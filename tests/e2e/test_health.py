from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_liveness_check(client: AsyncClient) -> None:
    response = await client.get("/api/health")

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio(loop_scope="session")
async def test_readiness_check_reports_database_and_redis(client: AsyncClient) -> None:
    response = await client.get("/api/health/ready")

    payload = response.json()
    assert payload["checks"]["database"]["status"] == "up"
    assert isinstance(payload["checks"]["database"]["latency_ms"], int)
    assert payload["checks"]["redis"]["status"] in {"up", "skipped", "down"}

    if payload["checks"]["redis"]["status"] == "down":
        assert response.status_code == 503, response.text
    else:
        assert response.status_code == 200, response.text
        assert payload["status"] == "ok"
