from __future__ import annotations

from fastapi import APIRouter

from app.models.platform import DashboardResponse, ServiceHealth
from app.services.platform import PlatformService

router = APIRouter()


@router.get("/services", response_model=list[ServiceHealth])
async def list_services() -> list[ServiceHealth]:
    return await PlatformService().list_services()


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard() -> DashboardResponse:
    return await PlatformService().dashboard()
