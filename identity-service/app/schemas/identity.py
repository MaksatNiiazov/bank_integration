from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class IntrospectRequest(BaseModel):
    token: str


class PermissionRef(BaseModel):
    code: str
    name: str


class TokenClaimsResponse(BaseModel):
    active: bool
    sub: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    roles: list[str] = []
    permissions: list[str] = []
    branches: list[str] = []
    branch_permissions: dict[str, list[str]] = {}
    department: str | None = None


class CurrentUserResponse(TokenClaimsResponse):
    id: int


class BranchCreate(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    is_active: bool = True


class BranchUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_active: bool | None = None


class BranchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None
    is_active: bool


class DepartmentCreate(BranchCreate):
    pass


class DepartmentUpdate(BranchUpdate):
    pass


class DepartmentResponse(BranchResponse):
    pass


class ServiceCreate(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    base_url: str | None = None
    is_active: bool = True


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    base_url: str | None = None
    is_active: bool | None = None


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None
    base_url: str | None
    is_active: bool


class PermissionCreate(BaseModel):
    code: str = Field(min_length=3, max_length=128)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None
    service_id: int | None


class RoleCreate(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    permission_codes: list[str] = []
    is_active: bool = True


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    permission_codes: list[str] | None = None
    is_active: bool | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None
    is_system: bool
    is_active: bool
    permissions: list[str]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=1, max_length=255)
    department_code: str | None = None
    is_active: bool = True


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    department_code: str | None = None
    is_active: bool | None = None


class RoleAssignmentCreate(BaseModel):
    role_code: str
    branch_code: str | None = None
    department_code: str | None = None


class RoleAssignmentResponse(BaseModel):
    id: int
    role_code: str
    branch_code: str | None
    department_code: str | None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    department_code: str | None
    is_active: bool
    created_at: datetime
    role_assignments: list[RoleAssignmentResponse]
