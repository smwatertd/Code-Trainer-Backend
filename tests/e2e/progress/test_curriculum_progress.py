from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.payloads import TASK3_SUM_PASCAL
from tests.e2e.helpers.users import register_user


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_progress__aggregates_after_successful_submission(
    client: AsyncClient,
) -> None:
    student = await register_user(client, name="E2E Student")
    student_headers = {"Authorization": f"Bearer {student['access_token']}"}

    submit = await client.post(
        "/api/submissions",
        headers=student_headers,
        json=TASK3_SUM_PASCAL,
    )
    assert submit.status_code == 200
    assert submit.json()["status"] == "success"

    progress = await client.get("/api/progress/curriculum/python/chapter_1", headers=student_headers)

    assert progress.status_code == 200
    body = progress.json()
    assert body["total_tasks"] == 8
    assert body["passed_tasks"] == 1
    assert body["progress_percent"] == 12.5
    assert body["by_task_id"]["3"]["progress_status"] == "passed"
