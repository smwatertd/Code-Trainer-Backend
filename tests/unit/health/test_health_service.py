from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.settings import AppSettings, RedisSettings
from src.features.health.services.health_service import HealthService


class _FakeDatabase:
    def __init__(self, *, fail: bool = False) -> None:
        self._fail = fail
        connection = AsyncMock()
        connection.execute = AsyncMock()
        self._connect_cm = AsyncMock()
        self._connect_cm.__aenter__.return_value = connection
        self._connect_cm.__aexit__.return_value = None
        self.engine = MagicMock()
        if fail:
            self.engine.connect.side_effect = OSError("database unavailable")
        else:
            self.engine.connect.return_value = self._connect_cm


@pytest.mark.asyncio
async def test_check_readiness__reports_database_up() -> None:
    settings = AppSettings(redis=RedisSettings(url=""))
    service = HealthService(settings=settings, database=_FakeDatabase())

    result = await service.check_readiness()

    assert result.checks["database"].status == "up"
    assert result.checks["database"].latency_ms is not None
    assert result.status == "ok"


@pytest.mark.asyncio
async def test_check_readiness__reports_database_down_on_connection_error() -> None:
    settings = AppSettings(redis=RedisSettings(url=""))
    service = HealthService(settings=settings, database=_FakeDatabase(fail=True))

    result = await service.check_readiness()

    assert result.checks["database"].status == "down"
    assert "database unavailable" in (result.checks["database"].message or "")
    assert result.status == "down"


@pytest.mark.asyncio
async def test_check_readiness__skips_redis_when_url_empty() -> None:
    settings = AppSettings(redis=RedisSettings(url="   "))
    service = HealthService(settings=settings, database=_FakeDatabase())

    result = await service.check_readiness()

    assert result.checks["redis"].status == "skipped"
    assert result.status == "ok"


@pytest.mark.asyncio
async def test_check_readiness__reports_redis_up_when_ping_succeeds() -> None:
    settings = AppSettings(redis=RedisSettings(url="redis://localhost:6379/0"))
    service = HealthService(settings=settings, database=_FakeDatabase())

    with patch("src.features.health.services.health_service.redis_lib.from_url") as from_url:
        client = MagicMock()
        from_url.return_value = client

        result = await service.check_readiness()

    client.ping.assert_called_once()
    client.close.assert_called_once()
    assert result.checks["redis"].status == "up"


@pytest.mark.asyncio
async def test_check_readiness__reports_redis_down_on_ping_error() -> None:
    settings = AppSettings(redis=RedisSettings(url="redis://localhost:6379/0"))
    service = HealthService(settings=settings, database=_FakeDatabase())

    with patch("src.features.health.services.health_service.redis_lib.from_url") as from_url:
        client = MagicMock()
        client.ping.side_effect = ConnectionError("redis refused")
        from_url.return_value = client

        result = await service.check_readiness()

    assert result.checks["redis"].status == "down"
    assert result.status == "down"
