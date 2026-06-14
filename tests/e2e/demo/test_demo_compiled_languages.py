from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.payloads import TASK3_SUM_PASCAL, TASK9_DIGIT_SUM_PASCAL, TASK10_MINUTES_BLOCKS


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__pascal_translation_compile_and_run_passes(client: AsyncClient) -> None:
    submit = await client.post("/api/demo/check", json=TASK9_DIGIT_SUM_PASCAL)
    assert submit.status_code == 200
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__pascal_block_compile_and_run_passes(client: AsyncClient) -> None:
    submit = await client.post("/api/demo/check", json=TASK10_MINUTES_BLOCKS)
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__pascal_translation_compile_and_run_passes(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json=TASK3_SUM_PASCAL,
    )

    assert submit.status_code == 200
    assert submit.json()["status"] == "success"
