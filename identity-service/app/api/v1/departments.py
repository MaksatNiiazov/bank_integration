from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.deps import require_permission
from app.db.session import get_db
from app.models import Department
from app.repositories.identity import IdentityRepository, normalize_code
from app.schemas.identity import DepartmentCreate, DepartmentResponse, DepartmentUpdate

router = APIRouter()


@router.get(
    "",
    response_model=list[DepartmentResponse],
    dependencies=[Depends(require_permission("identity.departments.read"))],
)
def list_departments(db: Annotated[Session, Depends(get_db)]) -> list[Department]:
    return IdentityRepository(db).list_departments()


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("identity.departments.manage"))],
)
def create_department(
    payload: DepartmentCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Department:
    department = Department(
        code=normalize_code(payload.code),
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(department)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department already exists",
        ) from exc
    db.refresh(department)
    return department


@router.patch(
    "/{department_code}",
    response_model=DepartmentResponse,
    dependencies=[Depends(require_permission("identity.departments.manage"))],
)
def update_department(
    department_code: str,
    payload: DepartmentUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Department:
    department = IdentityRepository(db).get_department_by_code(department_code)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    if payload.name is not None:
        department.name = payload.name
    if payload.description is not None:
        department.description = payload.description
    if payload.is_active is not None:
        department.is_active = payload.is_active
    db.commit()
    db.refresh(department)
    return department
