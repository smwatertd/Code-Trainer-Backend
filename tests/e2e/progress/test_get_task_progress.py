from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__get_task_progress_requires_auth(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, _ = auth_client

    response = await client.get("/api/progress/tasks/2")

    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__records_pass_after_successful_submission(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 2,
            "language": "python",
            "code": "print('b')\nprint('a')",
            "block_order": [1, 0],
        },
    )
    assert submit.status_code == 200
    assert submit.json()["status"] == "success"

    progress = await client.get("/api/progress/tasks/2", headers=headers)

    assert progress.status_code == 200
    body = progress.json()
    assert body["task_id"] == 2
    assert body["progress_status"] == "passed"
    assert body["attempts_count"] == 1
    assert body["passed_count"] == 1
    assert body["last_status"] == "passed"


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__records_failed_attempt(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 2,
            "language": "python",
            "code": "print('a')\nprint('b')",
            "block_order": [0, 1],
        },
    )
    assert submit.status_code == 200
    assert submit.json()["status"] == "failed"

    progress = await client.get("/api/progress/tasks/2", headers=headers)

    assert progress.status_code == 200
    body = progress.json()
    assert body["progress_status"] == "failed"
    assert body["attempts_count"] == 1
    assert body["passed_count"] == 0
    assert body["last_status"] == "failed"
