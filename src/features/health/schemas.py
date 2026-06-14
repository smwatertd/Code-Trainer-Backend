from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

HealthCheckStatus = Literal["up", "down", "skipped"]
ReadinessStatusValue = Literal["ok", "down"]


class HealthCheckResult(BaseModel):
    status: HealthCheckStatus
    latency_ms: int | None = None
    message: str | None = None


class LivenessStatus(BaseModel):
    status: Literal["ok"] = "ok"


class ReadinessStatus(BaseModel):
    status: ReadinessStatusValue
    checks: dict[str, HealthCheckResult] = Field(default_factory=dict)
