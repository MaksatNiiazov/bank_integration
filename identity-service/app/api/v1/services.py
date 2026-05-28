from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.deps import require_permission
from app.db.session import get_db
from app.models import ServiceApp
from app.repositories.identity import IdentityRepository, normalize_code
from app.schemas.identity import (
    PermissionCreate,
    PermissionResponse,
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)

router = APIRouter()


@router.get(
    "",
    response_model=list[ServiceResponse],
    dependencies=[Depends(require_permission("identity.services.read"))],
)
def list_services(db: Annotated[Session, Depends(get_db)]) -> list[ServiceApp]:
    return IdentityRepository(db).list_services()


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("identity.services.manage"))],
)
def create_service(payload: ServiceCreate, db: Annotated[Session, Depends(get_db)]) -> ServiceApp:
    service = ServiceApp(
        code=normalize_code(payload.code),
        name=payload.name,
        description=payload.description,
        base_url=payload.base_url,
        is_active=payload.is_active,
    )
    db.add(service)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Service already exists") from exc
    db.refresh(service)
    return service


@router.patch(
    "/{service_code}",
    response_model=ServiceResponse,
    dependencies=[Depends(require_permission("identity.services.manage"))],
)
def update_service(
    service_code: str,
    payload: ServiceUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> ServiceApp:
    service = IdentityRepository(db).get_service_by_code(service_code)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    if payload.name is not None:
        service.name = payload.name
    if payload.description is not None:
        service.description = payload.description
    if payload.base_url is not None:
        service.base_url = payload.base_url
    if payload.is_active is not None:
        service.is_active = payload.is_active
    db.commit()
    db.refresh(service)
    return service


@router.post(
    "/{service_code}/permissions",
    response_model=list[PermissionResponse],
    dependencies=[Depends(require_permission("identity.services.manage"))],
)
def register_permissions(
    service_code: str,
    payload: list[PermissionCreate],
    db: Annotated[Session, Depends(get_db)],
) -> list[PermissionResponse]:
    repo = IdentityRepository(db)
    service = repo.get_service_by_code(service_code)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    permissions = [
        repo.upsert_permission(
            code=item.code,
            name=item.name,
            description=item.description,
            service=service,
        )
        for item in payload
    ]
    db.commit()
    return list(permissions)
