from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ServiceStatus = Literal["ok", "unavailable", "unknown"]


class ServiceConfig(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str
    department: str
    description: str | None = None
    base_url: str
    health_path: str = "/health"
    launch_url: str | None = None
    required_permission: str | None = None
    visible: bool = True
    sort_order: int = 100


class ServiceHealth(BaseModel):
    code: str
    name: str
    department: str
    description: str | None
    status: ServiceStatus
    base_url: str
    launch_url: str | None
    required_permission: str | None
    checked_at: datetime
    latency_ms: int | None = None
    error: str | None = None


class DepartmentSummary(BaseModel):
    department: str
    services_total: int
    services_ok: int
    services_unavailable: int
    status: ServiceStatus


class ActivityItem(BaseModel):
    id: str
    title: str
    service_code: str
    tone: Literal["info", "success", "warning", "danger"] = "info"
    created_at: datetime


class DashboardResponse(BaseModel):
    generated_at: datetime
    services: list[ServiceHealth]
    departments: list[DepartmentSummary]
    activity: list[ActivityItem]
