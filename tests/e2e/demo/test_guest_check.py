from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.payloads import TASK1_HELLO_BLOCKS, TASK2_AGE_PASCAL


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__block_reorder_happy_path(client: AsyncClient) -> None:
    submit = await client.post("/api/demo/check", json=TASK1_HELLO_BLOCKS)

    assert submit.status_code == 200
    queued = submit.json()
    assert "job_id" in queued
    assert queued["status"] == "QUEUED"

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "SUCCESS"
    assert body["success"] is True


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__wrong_block_order_fails(client: AsyncClient) -> None:
    submit = await client.post(
        "/api/demo/check",
        json={
            **TASK1_HELLO_BLOCKS,
            "block_order": [0, 2, 1, 3],
        },
    )
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "SUCCESS"
    assert body["success"] is False


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__fix_task2_happy_path(client: AsyncClient) -> None:
    submit = await client.post("/api/demo/check", json=TASK2_AGE_PASCAL)
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["success"] is True
