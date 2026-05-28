from __future__ import annotations

from app.models import User


def build_user_claims(user: User) -> dict[str, object]:
    roles: set[str] = set()
    permissions: set[str] = set()
    branches: set[str] = set()
    branch_permissions: dict[str, set[str]] = {}

    for assignment in user.role_assignments:
        if not assignment.role.is_active or assignment.role.deleted_at is not None:
            continue
        roles.add(assignment.role.code)
        codes = {
            role_permission.permission.code
            for role_permission in assignment.role.role_permissions
        }
        if assignment.branch is not None:
            branches.add(assignment.branch.code)
            branch_permissions.setdefault(assignment.branch.code, set()).update(codes)
        else:
            permissions.update(codes)

    return {
        "sub": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "department": user.department.code if user.department else None,
        "roles": sorted(roles),
        "permissions": sorted(permissions),
        "branches": sorted(branches),
        "branch_permissions": {
            branch: sorted(values) for branch, values in sorted(branch_permissions.items())
        },
    }


def has_permission(claims: dict[str, object], permission: str) -> bool:
    permissions = claims.get("permissions")
    if isinstance(permissions, list) and permission in permissions:
        return True
    branch_permissions = claims.get("branch_permissions")
    if isinstance(branch_permissions, dict):
        return any(
            isinstance(values, list) and permission in values
            for values in branch_permissions.values()
        )
    return False
