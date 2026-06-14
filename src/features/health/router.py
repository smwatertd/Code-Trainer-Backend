from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.core.containers import Container
from src.features.health.schemas import LivenessStatus
from src.features.health.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=LivenessStatus)
async def liveness_check() -> LivenessStatus:
    return LivenessStatus()


@router.get("/ready")
@inject
async def readiness_check(
    health_service: HealthService = Depends(Provide[Container.health.health_service]),
) -> JSONResponse:
    payload = await health_service.check_readiness()
    status_code = 200 if payload.status == "ok" else 503
    return JSONResponse(status_code=status_code, content=payload.model_dump())
