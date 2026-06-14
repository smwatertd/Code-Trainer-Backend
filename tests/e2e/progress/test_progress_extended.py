from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.payloads import TASK2_AGE_BROKEN, TASK2_AGE_PASCAL, TASK4_AREA_BLOCKS
from tests.e2e.helpers.submissions import submit_and_get
from tests.e2e.helpers.users import register_user


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__curriculum_empty_before_any_submission(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/progress/curriculum/python/conditions", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total_tasks"] == 0
    assert body["passed_tasks"] == 0
    assert body["progress_percent"] == 0.0


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__curriculum_records_failed_attempt_on_linked_task(
    admin_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, admin_user = admin_client
    admin_headers = await auth_headers(client, admin_user)

    student = await register_user(client, name="E2E Student")
    student_headers = {"Authorization": f"Bearer {student['access_token']}"}

    link = await client.post(
        "/api/curriculum/tasks/4/links",
        headers=admin_headers,
        json={
            "language": "python",
            "technical_concept_id": "for_loop",
            "exercise_pattern_id": "tr_pattern_translation",
            "is_primary": True,
        },
    )
    assert link.status_code == 201

    await submit_and_get(
        client,
        student_headers,
        {
            **TASK4_AREA_BLOCKS,
            "block_order": [0, 1, 3, 2, 4, 5, 6],
        },
    )

    progress = await client.get("/api/progress/curriculum/python/loops", headers=student_headers)

    assert progress.status_code == 200
    body = progress.json()
    assert body["total_tasks"] == 1
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

    progress = await client.get("/api/progress/tasks/2", headers=headers)

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
