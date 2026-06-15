from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.users import register_user
from tests.e2e.helpers.payloads import TASK2_AGE_BROKEN, TASK2_AGE_PASCAL


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
        json=TASK2_AGE_PASCAL,
    )
    assert submit.status_code == 200
    assert submit.json()["status"] == "success"

    progress = await client.get("/api/progress/tasks/4", headers=headers)

    assert progress.status_code == 200
    body = progress.json()
    assert body["task_id"] == 4
    assert body["progress_status"] == "passed"
    assert body["attempts_count"] == 1
    assert body["passed_count"] == 1
    assert body["last_status"] == "passed"


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__records_failed_attempt(
    client: AsyncClient,
) -> None:
    student = await register_user(client, name="E2E Progress Failed")
    headers = {"Authorization": f"Bearer {student['access_token']}"}

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json=TASK2_AGE_BROKEN,
    )
    assert submit.status_code == 200
    assert submit.json()["status"] == "failed"

    progress = await client.get("/api/progress/tasks/4", headers=headers)

    assert progress.status_code == 200
    body = progress.json()
    assert body["progress_status"] == "failed"
    assert body["attempts_count"] == 1
    assert body["passed_count"] == 0
    assert body["last_status"] == "failed"
