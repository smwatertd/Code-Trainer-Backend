from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.http import assert_api_error
from tests.e2e.helpers.payloads import TASK2_BLOCK_REORDER_OK


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__unknown_task_returns_404(client: AsyncClient) -> None:
    response = await client.post(
        "/api/demo/check",
        json={
            "task_id": 999999,
            "language": "python",
            "code": "print(1)",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__rate_limit_returns_429(strict_guest_client: AsyncClient) -> None:
    first = await strict_guest_client.post("/api/demo/check", json=TASK2_BLOCK_REORDER_OK)
    second = await strict_guest_client.post("/api/demo/check", json=TASK2_BLOCK_REORDER_OK)

    assert first.status_code == 200
    assert_api_error(second, status=429, code="RATE_LIMIT_EXCEEDED")


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__guest_disabled_returns_404(guest_disabled_client: AsyncClient) -> None:
    response = await guest_disabled_client.post(
        "/api/demo/check",
        json={
            "task_id": 2,
            "language": "python",
            "code": "print(1)",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__duplicate_submit_returns_same_job_id(dedup_client: AsyncClient) -> None:
    first = await dedup_client.post("/api/demo/check", json=TASK2_BLOCK_REORDER_OK)
    second = await dedup_client.post("/api/demo/check", json=TASK2_BLOCK_REORDER_OK)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["job_id"] == second.json()["job_id"]
