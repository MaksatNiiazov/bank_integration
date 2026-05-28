from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import require_permission
from app.db.session import get_db
from app.repositories.identity import IdentityRepository
from app.schemas.identity import PermissionResponse

router = APIRouter()


@router.get(
    "",
    response_model=list[PermissionResponse],
    dependencies=[Depends(require_permission("identity.roles.read"))],
)
def list_permissions(db: Annotated[Session, Depends(get_db)]) -> list[PermissionResponse]:
    return list(IdentityRepository(db).list_permissions())
