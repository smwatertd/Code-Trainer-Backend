from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__block_reorder_with_test_cases_success(client: AsyncClient) -> None:
    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": 5,
            "language": "python",
            "code": "print(1)\nprint(2)",
            "block_order": [0, 1],
        },
    )

    assert submit.status_code == 200
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "SUCCESS"
    assert body["success"] is True
    assert body["test_results"]
    assert body["test_results"][0]["status"] == "PASSED"
