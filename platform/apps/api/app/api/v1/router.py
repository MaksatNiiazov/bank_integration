from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import health, platform

api_router = APIRouter()
api_router.include_router(health.router, tags=["system"])
api_router.include_router(platform.router, prefix="/platform", tags=["platform"])
