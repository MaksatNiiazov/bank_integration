from __future__ import annotations

import json
from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.models.platform import ServiceConfig


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Turkuaz Platform API"
    environment: str = "development"
    service_timeout_seconds: float = 2.5
    platform_services_json: str | None = None
    backend_cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5174", "http://127.0.0.1:5174"]
    )
    backend_cors_origin_regex: str | None = r"https://.*\.ngrok-free\.dev"

    @cached_property
    def services(self) -> list[ServiceConfig]:
        if self.platform_services_json:
            raw = json.loads(self.platform_services_json)
            return [ServiceConfig.model_validate(item) for item in raw]
        return default_services()


def default_services() -> list[ServiceConfig]:
    return [
        ServiceConfig(
            code="identity",
            name="Identity",
            department="Platform",
            description="Users, roles, branches, permissions",
            base_url="http://localhost:8020",
            health_path="/api/v1/health",
            launch_url="http://localhost:8020/docs",
            required_permission="identity.users.read",
            sort_order=10,
        ),
        ServiceConfig(
            code="converter",
            name="Converter",
            department="Operations",
            description="Orders, clients, products, converter history",
            base_url="http://localhost:8000",
            health_path="/api/v1/health",
            launch_url="http://localhost:5173",
            required_permission="converter.orders.read",
            sort_order=20,
        ),
        ServiceConfig(
            code="payments",
            name="Payments",
            department="Finance",
            description="Transactions, QR, payment callbacks",
            base_url="http://localhost:8010",
            health_path="/health",
            launch_url="http://localhost:6750",
            required_permission="payments.transactions.read",
            sort_order=30,
        ),
        ServiceConfig(
            code="reports",
            name="Reports",
            department="Management",
            description="Company metrics and department reports",
            base_url="http://localhost:8040",
            health_path="/api/v1/health",
            launch_url="http://localhost:5175",
            required_permission="reports.read",
            sort_order=40,
        ),
        ServiceConfig(
            code="warehouse",
            name="Warehouse",
            department="Logistics",
            description="Stock, shipments, warehouse signals",
            base_url="http://localhost:8050",
            health_path="/api/v1/health",
            launch_url="http://localhost:5176",
            required_permission="warehouse.read",
            sort_order=50,
        ),
    ]


settings = Settings()
