from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import redis as redis_lib
from sqlalchemy import text

from src.core.interfaces import Database
from src.core.settings import AppSettings
from src.features.health.schemas import HealthCheckResult, ReadinessStatus, ReadinessStatusValue

HEALTH_CHECK_TIMEOUT_SECONDS = 3.0


@dataclass
class HealthService:
    settings: AppSettings
    database: Database

    async def check_readiness(self) -> ReadinessStatus:
        database_task = asyncio.create_task(self._run_check(self._check_database))
        redis_task = asyncio.create_task(self._run_check(self._check_redis))

        results = await asyncio.gather(database_task, redis_task)
        checks = {
            "database": results[0],
            "redis": results[1],
        }
        overall_status: ReadinessStatusValue = (
            "ok" if all(check.status in {"up", "skipped"} for check in checks.values()) else "down"
        )
        return ReadinessStatus(status=overall_status, checks=checks)

    async def _run_check(self, check: Callable[[], Awaitable[HealthCheckResult]]) -> HealthCheckResult:
        try:
            return await asyncio.wait_for(check(), timeout=HEALTH_CHECK_TIMEOUT_SECONDS)
        except TimeoutError:
            return HealthCheckResult(status="down", message="Health check timed out")
        except Exception as exc:
            return HealthCheckResult(status="down", message=str(exc))

    async def _check_database(self) -> HealthCheckResult:
        started = time.perf_counter()
        async with self.database.engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        latency_ms = int((time.perf_counter() - started) * 1000)
        return HealthCheckResult(status="up", latency_ms=latency_ms)

    async def _check_redis(self) -> HealthCheckResult:
        redis_url = self.settings.redis.url.strip()
        if not redis_url:
            return HealthCheckResult(status="skipped", message="Redis is not configured")

        started = time.perf_counter()

        def ping() -> None:
            client = redis_lib.from_url(redis_url, socket_connect_timeout=2)
            try:
                client.ping()
            finally:
                client.close()

        await asyncio.to_thread(ping)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return HealthCheckResult(status="up", latency_ms=latency_ms)
