from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_teacher_tasks__create_list_get_update(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    teacher_http, teacher = teacher_client
    headers = await auth_headers(teacher_http, teacher)

    create = await teacher_http.post(
        "/api/teacher/tasks",
        headers=headers,
        json={
            "title": "Teacher custom task",
            "description": "Print hello from teacher task",
            "difficulty": "easy",
            "task_type": "task_write_from_description",
            "payload": {
                "target_language": "python",
                "test_cases": [{"inputs": "", "output": "hello"}],
                "topics": ["custom"],
            },
        },
    )
    assert create.status_code == 200
    task_id = create.json()["id"]

    mine = await teacher_http.get("/api/teacher/tasks/mine", headers=headers)
    assert mine.status_code == 200
    assert any(item["id"] == task_id for item in mine.json())

    detail = await teacher_http.get(f"/api/teacher/tasks/{task_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["title"] == "Teacher custom task"

    update = await teacher_http.patch(
        f"/api/teacher/tasks/{task_id}",
        headers=headers,
        json={"title": "Teacher custom task updated"},
    )
    assert update.status_code == 200
    assert update.json()["title"] == "Teacher custom task updated"
