from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.deps import require_permission
from app.db.session import get_db
from app.models import Role
from app.repositories.identity import IdentityRepository, normalize_code
from app.schemas.identity import PermissionResponse, RoleCreate, RoleResponse, RoleUpdate

router = APIRouter()


@router.get(
    "",
    response_model=list[RoleResponse],
    dependencies=[Depends(require_permission("identity.roles.read"))],
)
def list_roles(db: Annotated[Session, Depends(get_db)]) -> list[RoleResponse]:
    return [_role_response(role) for role in IdentityRepository(db).list_roles()]


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("identity.roles.manage"))],
)
def create_role(payload: RoleCreate, db: Annotated[Session, Depends(get_db)]) -> RoleResponse:
    repo = IdentityRepository(db)
    role = Role(
        code=normalize_code(payload.code),
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(role)
    try:
        db.flush()
        repo.set_role_permissions(role, payload.permission_codes)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already exists") from exc
    return _role_response(repo.get_role_by_code(role.code) or role)


@router.patch(
    "/{role_code}",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission("identity.roles.manage"))],
)
def update_role(
    role_code: str,
    payload: RoleUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> RoleResponse:
    repo = IdentityRepository(db)
    role = repo.get_role_by_code(role_code)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if payload.name is not None:
        role.name = payload.name
    if payload.description is not None:
        role.description = payload.description
    if payload.is_active is not None:
        role.is_active = payload.is_active
    if payload.permission_codes is not None:
        repo.set_role_permissions(role, payload.permission_codes)
    db.commit()
    return _role_response(repo.get_role_by_code(role.code) or role)


@router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    dependencies=[Depends(require_permission("identity.roles.read"))],
)
def list_permissions(db: Annotated[Session, Depends(get_db)]) -> list[PermissionResponse]:
    return list(IdentityRepository(db).list_permissions())


def _role_response(role: Role) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        code=role.code,
        name=role.name,
        description=role.description,
        is_system=role.is_system,
        is_active=role.is_active,
        permissions=sorted(item.permission.code for item in role.role_permissions),
    )
