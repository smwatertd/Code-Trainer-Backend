from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__block_reorder_happy_path(client: AsyncClient) -> None:
    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": 2,
            "language": "python",
            "code": "print('b')\nprint('a')",
            "block_order": [1, 0],
        },
    )

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
            "task_id": 2,
            "language": "python",
            "code": "print('a')\nprint('b')",
            "block_order": [0, 1],
        },
    )
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "SUCCESS"
    assert body["success"] is False
