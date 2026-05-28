from __future__ import annotations

import os
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)

IDENTITY_SECRET_KEY = os.getenv("IDENTITY_SECRET_KEY", "dev-change-me")
IDENTITY_ALGORITHM = os.getenv("IDENTITY_ALGORITHM", "HS256")


def get_identity_claims(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        return jwt.decode(
            credentials.credentials,
            IDENTITY_SECRET_KEY,
            algorithms=[IDENTITY_ALGORITHM],
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def require_permission(permission: str, branch_code: str | None = None):
    def dependency(claims: Annotated[dict[str, Any], Depends(get_identity_claims)]) -> dict[str, Any]:
        global_permissions = claims.get("permissions", [])
        if permission in global_permissions:
            return claims

        branch_permissions = claims.get("branch_permissions", {})
        if branch_code is not None and permission in branch_permissions.get(branch_code, []):
            return claims

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing permission: {permission}",
        )

    return dependency
