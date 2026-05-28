from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.deps import require_permission
from app.core.security import get_password_hash
from app.db.session import get_db
from app.repositories.identity import IdentityRepository
from app.schemas.identity import (
    RoleAssignmentCreate,
    RoleAssignmentResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter()


@router.get(
    "",
    response_model=list[UserResponse],
    dependencies=[Depends(require_permission("identity.users.read"))],
)
def list_users(db: Annotated[Session, Depends(get_db)]) -> list[UserResponse]:
    return [_user_response(user) for user in IdentityRepository(db).list_users()]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("identity.users.manage"))],
)
def create_user(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    repo = IdentityRepository(db)
    department = repo.get_department_by_code(payload.department_code) if payload.department_code else None
    if payload.department_code and department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    try:
        user = repo.create_user(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            department=department,
            is_active=payload.is_active,
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists") from exc
    return _user_response(repo.get_user(user.id) or user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("identity.users.read"))],
)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    user = IdentityRepository(db).get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _user_response(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("identity.users.manage"))],
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    repo = IdentityRepository(db)
    user = repo.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.email is not None:
        user.email = payload.email.casefold()
    if payload.password is not None:
        user.hashed_password = get_password_hash(payload.password)
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.department_code is not None:
        department = repo.get_department_by_code(payload.department_code)
        if department is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        user.department = department
    if payload.is_active is not None:
        user.is_active = payload.is_active

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists") from exc
    return _user_response(repo.get_user(user.id) or user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("identity.users.manage"))],
)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]) -> None:
    user = IdentityRepository(db).get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.deleted_at = datetime.now(timezone.utc)
    user.is_active = False
    db.commit()


@router.post(
    "/{user_id}/role-assignments",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("identity.users.manage"))],
)
def assign_role(
    user_id: int,
    payload: RoleAssignmentCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    repo = IdentityRepository(db)
    user = repo.get_user(user_id)
    role = repo.get_role_by_code(payload.role_code)
    branch = repo.get_branch_by_code(payload.branch_code) if payload.branch_code else None
    department = repo.get_department_by_code(payload.department_code) if payload.department_code else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if payload.branch_code and branch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
    if payload.department_code and department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    try:
        repo.assign_role(user=user, role=role, branch=branch, department=department)
        db.commit()
    except IntegrityError:
        db.rollback()
    return _user_response(repo.get_user(user_id) or user)


@router.delete(
    "/{user_id}/role-assignments/{assignment_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("identity.users.manage"))],
)
def delete_role_assignment(
    user_id: int,
    assignment_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    user = IdentityRepository(db).get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    assignment = next((item for item in user.role_assignments if item.id == assignment_id), None)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    db.delete(assignment)
    db.commit()
    return _user_response(IdentityRepository(db).get_user(user_id) or user)


def _user_response(user) -> UserResponse:  # type: ignore[no-untyped-def]
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        department_code=user.department.code if user.department else None,
        is_active=user.is_active,
        created_at=user.created_at,
        role_assignments=[
            RoleAssignmentResponse(
                id=assignment.id,
                role_code=assignment.role.code,
                branch_code=assignment.branch.code if assignment.branch else None,
                department_code=assignment.department.code if assignment.department else None,
            )
            for assignment in user.role_assignments
        ],
    )
