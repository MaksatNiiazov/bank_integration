from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.models.platform import ActivityItem, DashboardResponse, DepartmentSummary, ServiceHealth


class PlatformService:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.client = client

    async def list_services(self) -> list[ServiceHealth]:
        services = [service for service in settings.services if service.visible]
        services.sort(key=lambda item: (item.sort_order, item.name))
        return [await self._check_service(service) for service in services]

    async def dashboard(self) -> DashboardResponse:
        service_health = await self.list_services()
        return DashboardResponse(
            generated_at=datetime.now(timezone.utc),
            services=service_health,
            departments=_department_summaries(service_health),
            activity=_activity(service_health),
        )

    async def _check_service(self, service) -> ServiceHealth:  # type: ignore[no-untyped-def]
        started = time.perf_counter()
        checked_at = datetime.now(timezone.utc)
        url = f"{service.base_url.rstrip('/')}/{service.health_path.lstrip('/')}"
        try:
            if self.client is None:
                async with httpx.AsyncClient(timeout=settings.service_timeout_seconds) as client:
                    response = await client.get(url)
            else:
                response = await self.client.get(url)
            latency_ms = int((time.perf_counter() - started) * 1000)
            if response.status_code < 400:
                status = "ok"
                error = None
            else:
                status = "unavailable"
                error = f"HTTP {response.status_code}"
        except (httpx.HTTPError, TimeoutError) as exc:
            latency_ms = int((time.perf_counter() - started) * 1000)
            status = "unavailable"
            error = str(exc) or exc.__class__.__name__

        return ServiceHealth(
            code=service.code,
            name=service.name,
            department=service.department,
            description=service.description,
            status=status,
            base_url=service.base_url,
            launch_url=service.launch_url,
            required_permission=service.required_permission,
            checked_at=checked_at,
            latency_ms=latency_ms,
            error=error,
        )


def _department_summaries(services: list[ServiceHealth]) -> list[DepartmentSummary]:
    grouped: dict[str, list[ServiceHealth]] = defaultdict(list)
    for service in services:
        grouped[service.department].append(service)

    summaries: list[DepartmentSummary] = []
    for department, items in sorted(grouped.items()):
        ok_count = sum(1 for item in items if item.status == "ok")
        unavailable_count = sum(1 for item in items if item.status == "unavailable")
        status = "ok" if unavailable_count == 0 else "unavailable"
        summaries.append(
            DepartmentSummary(
                department=department,
                services_total=len(items),
                services_ok=ok_count,
                services_unavailable=unavailable_count,
                status=status,
            )
        )
    return summaries


def _activity(services: list[ServiceHealth]) -> list[ActivityItem]:
    now = datetime.now(timezone.utc)
    unavailable = [service for service in services if service.status == "unavailable"]
    if unavailable:
        return [
            ActivityItem(
                id=f"{service.code}-unavailable",
                title=f"{service.name} недоступен: {service.error or 'нет ответа'}",
                service_code=service.code,
                tone="warning",
                created_at=now,
            )
            for service in unavailable
        ]
    return [
        ActivityItem(
            id="all-systems-ok",
            title="Все подключенные сервисы отвечают",
            service_code="platform",
            tone="success",
            created_at=now,
        )
    ]
