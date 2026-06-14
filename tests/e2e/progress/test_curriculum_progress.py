from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_progress__aggregates_after_successful_submission(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 4,
            "language": "python",
            "code": "for i in range(3):\n    print(i)\n",
        },
    )
    assert submit.status_code == 200
    assert submit.json()["status"] == "success"

    progress = await client.get("/api/progress/curriculum/python/loops", headers=headers)

    assert progress.status_code == 200
    body = progress.json()
    assert body["total_tasks"] == 1
    assert body["passed_tasks"] == 1
    assert body["progress_percent"] == 100.0
    assert body["by_technical_concept"]["for_loop"]["passed_tasks"] == 1
    assert body["by_task_id"]["4"]["progress_status"] == "passed"
