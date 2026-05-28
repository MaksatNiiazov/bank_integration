from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.platform import PlatformService


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_dashboard_tolerates_unavailable_services() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if "localhost:8020" in str(request.url):
            return httpx.Response(200, json={"status": "ok"})
        raise httpx.ConnectError("service down", request=request)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, timeout=1) as client:
        dashboard = await PlatformService(client=client).dashboard()

    assert dashboard.services
    assert any(service.status == "ok" for service in dashboard.services)
    assert any(service.status == "unavailable" for service in dashboard.services)
    assert dashboard.departments
    assert dashboard.activity
