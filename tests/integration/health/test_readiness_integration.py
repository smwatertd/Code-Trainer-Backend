from __future__ import annotations

import pytest

from src.core.settings import AppSettings, RedisSettings
from src.features.health.services.health_service import HealthService
from src.shared.database.database import SqlAlchemyDatabase


@pytest.mark.asyncio
async def test_readiness_integration__database_is_reachable(settings: AppSettings) -> None:
    database = SqlAlchemyDatabase(settings.db)
    service = HealthService(
        settings=AppSettings(redis=RedisSettings(url="")),
        database=database,
    )

    result = await service.check_readiness()

    if result.checks["database"].status == "down":
        pytest.fail("PostgreSQL is not available for integration test")

    assert result.checks["database"].status == "up"
    assert isinstance(result.checks["database"].latency_ms, int)
    assert result.checks["redis"].status == "skipped"
    assert result.status == "ok"
