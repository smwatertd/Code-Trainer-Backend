from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__translation_compile_success(client: AsyncClient) -> None:
    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": 1,
            "language": "python",
            "code": "print('Hello')\n",
        },
    )

    assert submit.status_code == 200
    queued = submit.json()
    assert "job_id" in queued

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "SUCCESS"
    assert body["success"] is True


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__translation_syntax_error_fails(client: AsyncClient) -> None:
    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": 1,
            "language": "python",
            "code": "print('Hello'\n",
        },
    )
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "SUCCESS"
    assert body["success"] is False
    assert body["compiler_errors"]
