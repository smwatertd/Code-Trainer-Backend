from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.payloads import TASK3_SUM_PASCAL
from tests.e2e.helpers.users import register_user


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_progress__aggregates_after_successful_submission(
    admin_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, admin_user = admin_client
    admin_headers = await auth_headers(client, admin_user)

    student = await register_user(client, name="E2E Student")
    student_headers = {"Authorization": f"Bearer {student['access_token']}"}

    link = await client.post(
        "/api/curriculum/tasks/3/links",
        headers=admin_headers,
        json={
            "language": "python",
            "technical_concept_id": "for_loop",
            "exercise_pattern_id": "tr_pattern_translation",
            "is_primary": True,
        },
    )
    assert link.status_code == 201

    submit = await client.post(
        "/api/submissions",
        headers=student_headers,
        json=TASK3_SUM_PASCAL,
    )
    assert submit.status_code == 200
    assert submit.json()["status"] == "success"

    progress = await client.get("/api/progress/curriculum/python/loops", headers=student_headers)

    assert progress.status_code == 200
    body = progress.json()
    assert body["total_tasks"] == 1
    assert body["passed_tasks"] == 1
    assert body["progress_percent"] == 100.0
    assert body["by_technical_concept"]["for_loop"]["passed_tasks"] == 1
    assert body["by_task_id"]["3"]["progress_status"] == "passed"
