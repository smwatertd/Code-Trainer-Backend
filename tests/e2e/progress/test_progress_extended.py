from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.payloads import TASK2_AGE_BROKEN, TASK2_AGE_PASCAL
from tests.e2e.helpers.submissions import submit_and_get
from tests.e2e.helpers.users import register_user


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__curriculum_empty_before_any_submission(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/progress/curriculum/python/chapter_2", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total_tasks"] == 8
    assert body["passed_tasks"] == 0
    assert body["progress_percent"] == 0.0


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__curriculum_records_failed_attempt_on_linked_task(
    client: AsyncClient,
) -> None:
    student = await register_user(client, name="E2E Student")
    student_headers = {"Authorization": f"Bearer {student['access_token']}"}

    await submit_and_get(client, student_headers, TASK2_AGE_BROKEN)

    progress = await client.get("/api/progress/curriculum/python/chapter_1", headers=student_headers)

    assert progress.status_code == 200
    body = progress.json()
    assert body["total_tasks"] == 8
    assert body["passed_tasks"] == 0
    assert body["by_task_id"]["4"]["progress_status"] == "failed"
    assert body["by_task_id"]["4"]["attempts_count"] == 1


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__task_progress_increments_attempts(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    await submit_and_get(client, headers, TASK2_AGE_BROKEN)
    await submit_and_get(client, headers, TASK2_AGE_PASCAL)

    progress = await client.get("/api/progress/tasks/4", headers=headers)

    assert progress.status_code == 200
    body = progress.json()
    assert body["attempts_count"] == 2
    assert body["passed_count"] == 1
    assert body["progress_status"] == "passed"


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__unknown_learning_concept_returns_empty_aggregate(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/progress/curriculum/python/nonexistent_lc", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["learning_concept_id"] == "nonexistent_lc"
    assert body["total_tasks"] == 0
