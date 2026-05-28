from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Branch, Department, Role, ServiceApp
from app.repositories.identity import IdentityRepository, normalize_code

IDENTITY_PERMISSIONS = [
    ("identity.users.read", "Read users"),
    ("identity.users.manage", "Manage users"),
    ("identity.roles.read", "Read roles"),
    ("identity.roles.manage", "Manage roles"),
    ("identity.branches.read", "Read branches"),
    ("identity.branches.manage", "Manage branches"),
    ("identity.departments.read", "Read departments"),
    ("identity.departments.manage", "Manage departments"),
    ("identity.services.read", "Read service registry"),
    ("identity.services.manage", "Manage service registry"),
]

PLATFORM_ADMIN_PERMISSIONS = [code for code, _name in IDENTITY_PERMISSIONS]


def bootstrap_identity(db: Session) -> None:
    repo = IdentityRepository(db)
    service = repo.get_service_by_code("identity")
    if service is None:
        service = ServiceApp(
            code="identity",
            name="Identity",
            description="Users, roles, permissions, branches, and departments",
            is_active=True,
        )
        db.add(service)
        db.flush()

    for code, name in IDENTITY_PERMISSIONS:
        repo.upsert_permission(code=code, name=name, service=service)

    role = repo.get_role_by_code("platform_admin")
    if role is None:
        role = Role(
            code="platform_admin",
            name="Platform Admin",
            description="Full access to identity administration",
            is_system=True,
            is_active=True,
        )
        db.add(role)
        db.flush()
    repo.set_role_permissions(role, PLATFORM_ADMIN_PERMISSIONS)

    _ensure_default_org(db)

    if settings.auto_create_admin:
        admin = repo.get_user_by_email(settings.default_admin_email)
        if admin is None:
            admin = repo.create_user(
                email=settings.default_admin_email,
                password=settings.default_admin_password,
                full_name=settings.default_admin_full_name,
                is_active=True,
            )
        if not any(assignment.role.code == "platform_admin" for assignment in admin.role_assignments):
            repo.assign_role(user=admin, role=role)
    db.commit()


def _ensure_default_org(db: Session) -> None:
    for model, code, name in (
        (Department, "platform", "Platform"),
        (Branch, "head_office", "Head Office"),
    ):
        exists = db.query(model).filter(model.code == normalize_code(code)).first()
        if exists is None:
            db.add(model(code=normalize_code(code), name=name, is_active=True))
    db.flush()
