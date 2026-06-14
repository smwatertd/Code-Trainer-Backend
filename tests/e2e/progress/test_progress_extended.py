from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.submissions import submit_and_get


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
async def test_progress__curriculum_records_failed_attempt_on_task4(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    await submit_and_get(
        client,
        headers,
        {
            "task_id": 4,
            "language": "python",
            "code": "print(0)\nprint(1)\nprint(2)\n",
        },
    )

    progress = await client.get("/api/progress/curriculum/python/loops", headers=headers)

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

    await submit_and_get(
        client,
        headers,
        {
            "task_id": 2,
            "language": "python",
            "code": "print('a')\nprint('b')",
            "block_order": [0, 1],
        },
    )
    await submit_and_get(
        client,
        headers,
        {
            "task_id": 2,
            "language": "python",
            "code": "print('b')\nprint('a')",
            "block_order": [1, 0],
        },
    )

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
