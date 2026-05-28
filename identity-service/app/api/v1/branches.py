from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.deps import require_permission
from app.db.session import get_db
from app.models import Branch
from app.repositories.identity import IdentityRepository, normalize_code
from app.schemas.identity import BranchCreate, BranchResponse, BranchUpdate

router = APIRouter()


@router.get(
    "",
    response_model=list[BranchResponse],
    dependencies=[Depends(require_permission("identity.branches.read"))],
)
def list_branches(db: Annotated[Session, Depends(get_db)]) -> list[Branch]:
    return IdentityRepository(db).list_branches()


@router.post(
    "",
    response_model=BranchResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("identity.branches.manage"))],
)
def create_branch(payload: BranchCreate, db: Annotated[Session, Depends(get_db)]) -> Branch:
    branch = Branch(
        code=normalize_code(payload.code),
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(branch)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Branch already exists") from exc
    db.refresh(branch)
    return branch


@router.patch(
    "/{branch_code}",
    response_model=BranchResponse,
    dependencies=[Depends(require_permission("identity.branches.manage"))],
)
def update_branch(
    branch_code: str,
    payload: BranchUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Branch:
    branch = IdentityRepository(db).get_branch_by_code(branch_code)
    if branch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
    if payload.name is not None:
        branch.name = payload.name
    if payload.description is not None:
        branch.description = payload.description
    if payload.is_active is not None:
        branch.is_active = payload.is_active
    db.commit()
    db.refresh(branch)
    return branch
