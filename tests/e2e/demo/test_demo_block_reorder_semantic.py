from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.payloads import TASK4_AREA_BLOCKS


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__block_reorder_with_test_cases_success(client: AsyncClient) -> None:
    submit = await client.post("/api/demo/check", json=TASK4_AREA_BLOCKS)

    assert submit.status_code == 200
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "SUCCESS"
    assert body["success"] is True
    assert body["test_results"]
    assert body["test_results"][0]["status"] == "PASSED"
