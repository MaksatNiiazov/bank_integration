from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token, verify_password
from app.db.session import get_db
from app.models import User
from app.repositories.identity import IdentityRepository
from app.schemas.identity import (
    CurrentUserResponse,
    IntrospectRequest,
    LoginRequest,
    TokenClaimsResponse,
    TokenResponse,
)
from app.services.tokens import build_user_claims

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    user = IdentityRepository(db).get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    token = create_access_token(build_user_claims(user))
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=CurrentUserResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> CurrentUserResponse:
    claims = build_user_claims(current_user)
    return CurrentUserResponse(id=current_user.id, active=True, **claims)


@router.post("/introspect", response_model=TokenClaimsResponse)
def introspect(payload: IntrospectRequest) -> TokenClaimsResponse:
    try:
        claims = decode_access_token(payload.token)
    except jwt.PyJWTError:
        return TokenClaimsResponse(active=False)
    return TokenClaimsResponse(active=True, **claims)
