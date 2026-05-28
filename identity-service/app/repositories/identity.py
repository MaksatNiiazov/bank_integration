from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.security import get_password_hash
from app.models import (
    Branch,
    Department,
    Permission,
    Role,
    RolePermission,
    ServiceApp,
    User,
    UserRoleAssignment,
)


class IdentityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user(self, user_id: int) -> User | None:
        return self.db.scalar(
            select(User)
            .options(
                joinedload(User.department),
                selectinload(User.role_assignments)
                .joinedload(UserRoleAssignment.role)
                .selectinload(Role.role_permissions)
                .joinedload(RolePermission.permission),
                selectinload(User.role_assignments).joinedload(UserRoleAssignment.branch),
                selectinload(User.role_assignments).joinedload(UserRoleAssignment.department),
            )
            .where(User.id == user_id, User.deleted_at.is_(None))
        )

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.scalar(
            select(User)
            .options(
                joinedload(User.department),
                selectinload(User.role_assignments)
                .joinedload(UserRoleAssignment.role)
                .selectinload(Role.role_permissions)
                .joinedload(RolePermission.permission),
                selectinload(User.role_assignments).joinedload(UserRoleAssignment.branch),
                selectinload(User.role_assignments).joinedload(UserRoleAssignment.department),
            )
            .where(User.email == email.casefold(), User.deleted_at.is_(None))
        )

    def list_users(self) -> list[User]:
        return list(
            self.db.scalars(
                select(User)
                .options(
                    joinedload(User.department),
                    selectinload(User.role_assignments).joinedload(UserRoleAssignment.role),
                    selectinload(User.role_assignments).joinedload(UserRoleAssignment.branch),
                    selectinload(User.role_assignments).joinedload(UserRoleAssignment.department),
                )
                .where(User.deleted_at.is_(None))
                .order_by(User.email)
            )
        )

    def create_user(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
        department: Department | None = None,
        is_active: bool = True,
    ) -> User:
        user = User(
            email=email.casefold(),
            hashed_password=get_password_hash(password),
            full_name=full_name,
            department=department,
            is_active=is_active,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def get_branch_by_code(self, code: str) -> Branch | None:
        return self.db.scalar(
            select(Branch).where(Branch.code == normalize_code(code), Branch.deleted_at.is_(None))
        )

    def get_department_by_code(self, code: str) -> Department | None:
        return self.db.scalar(
            select(Department).where(
                Department.code == normalize_code(code),
                Department.deleted_at.is_(None),
            )
        )

    def get_service_by_code(self, code: str) -> ServiceApp | None:
        return self.db.scalar(
            select(ServiceApp).where(
                ServiceApp.code == normalize_code(code),
                ServiceApp.deleted_at.is_(None),
            )
        )

    def get_role_by_code(self, code: str) -> Role | None:
        return self.db.scalar(
            select(Role)
            .options(selectinload(Role.role_permissions).joinedload(RolePermission.permission))
            .where(Role.code == normalize_code(code), Role.deleted_at.is_(None))
        )

    def get_permission_by_code(self, code: str) -> Permission | None:
        return self.db.scalar(select(Permission).where(Permission.code == normalize_code(code)))

    def list_branches(self) -> list[Branch]:
        return list(
            self.db.scalars(
                select(Branch).where(Branch.deleted_at.is_(None)).order_by(Branch.name)
            )
        )

    def list_departments(self) -> list[Department]:
        return list(
            self.db.scalars(
                select(Department).where(Department.deleted_at.is_(None)).order_by(Department.name)
            )
        )

    def list_services(self) -> list[ServiceApp]:
        return list(
            self.db.scalars(
                select(ServiceApp).where(ServiceApp.deleted_at.is_(None)).order_by(ServiceApp.name)
            )
        )

    def list_permissions(self) -> list[Permission]:
        return list(self.db.scalars(select(Permission).order_by(Permission.code)))

    def list_roles(self) -> list[Role]:
        return list(
            self.db.scalars(
                select(Role)
                .options(selectinload(Role.role_permissions).joinedload(RolePermission.permission))
                .where(Role.deleted_at.is_(None))
                .order_by(Role.name)
            )
        )

    def upsert_permission(
        self,
        *,
        code: str,
        name: str,
        description: str | None = None,
        service: ServiceApp | None = None,
    ) -> Permission:
        permission = self.get_permission_by_code(code)
        if permission is None:
            permission = Permission(code=normalize_code(code), name=name, service=service)
            self.db.add(permission)
        permission.name = name
        permission.description = description
        if service is not None:
            permission.service = service
        self.db.flush()
        return permission

    def set_role_permissions(self, role: Role, permission_codes: list[str]) -> None:
        normalized_codes = list(dict.fromkeys(normalize_code(code) for code in permission_codes))
        permissions = [
            permission
            for code in normalized_codes
            if (permission := self.get_permission_by_code(code)) is not None
        ]
        self.db.query(RolePermission).filter(RolePermission.role_id == role.id).delete(
            synchronize_session=False
        )
        self.db.flush()
        role.role_permissions = [
            RolePermission(role=role, permission=permission) for permission in permissions
        ]
        self.db.flush()

    def assign_role(
        self,
        *,
        user: User,
        role: Role,
        branch: Branch | None = None,
        department: Department | None = None,
    ) -> UserRoleAssignment:
        assignment = UserRoleAssignment(
            user=user,
            role=role,
            branch=branch,
            department=department,
        )
        self.db.add(assignment)
        self.db.flush()
        return assignment


def normalize_code(value: str) -> str:
    return value.strip().casefold().replace(" ", "_")
