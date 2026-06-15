from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_catalogs_compat__teacher_crud_and_legacy_task_shape(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    teacher_http, teacher = teacher_client
    headers = await auth_headers(teacher_http, teacher)

    create = await teacher_http.post(
        "/api/catalogs",
        headers=headers,
        json={"title": "Compat Catalog", "description": "Legacy UI", "visibility": "public"},
    )
    assert create.status_code == 201
    catalog = create.json()
    catalog_id = catalog["id"]
    assert catalog["title"] == "Compat Catalog"
    assert catalog["task_count"] == 0

    mine = await teacher_http.get("/api/catalogs/mine", headers=headers)
    assert mine.status_code == 200
    assert any(item["id"] == catalog_id for item in mine.json())

    assign = await teacher_http.post(
        f"/api/catalogs/{catalog_id}/assignments",
        headers=headers,
        json={"task_id": 4},
    )
    assert assign.status_code == 204

    detail = await teacher_http.get(f"/api/catalogs/{catalog_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["task_count"] == 1

    tasks = await teacher_http.get(f"/api/catalogs/{catalog_id}/tasks", headers=headers)
    assert tasks.status_code == 200
    body = tasks.json()
    assert len(body) == 1
    assert body[0]["id"] == 4
    assert body[0]["type_id"]
    assert body[0]["catalog_ids"] == [catalog_id]
    assert body[0]["is_assigned"] is True

    teacher_tasks = await teacher_http.get("/api/catalogs/tasks", headers=headers)
    assert teacher_tasks.status_code == 200
    assigned = next(item for item in teacher_tasks.json() if item["id"] == 4)
    assert catalog_id in assigned["catalog_ids"]


@pytest.mark.asyncio(loop_scope="session")
async def test_teacher_workspace__profile_returns_groups_and_permissions(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    teacher_http, teacher = teacher_client
    headers = await auth_headers(teacher_http, teacher)

    group = await teacher_http.post(
        "/api/groups",
        headers=headers,
        json={"name": "Compat Group"},
    )
    assert group.status_code == 201
    group_id = group.json()["id"]

    profile = await teacher_http.get("/api/teacher/profile", headers=headers)
    assert profile.status_code == 200
    body = profile.json()
    assert body["user_id"] == teacher.user_id
    assert body["email"] == teacher.email
    assert body["permissions"]["manage_catalogs"] is True
    assert any(item["id"] == group_id for item in body["groups"])

    analytics = await teacher_http.get("/api/teacher/analytics", headers=headers)
    assert analytics.status_code == 200
    assert "overview" in analytics.json()

    submissions = await teacher_http.get("/api/teacher/submissions", headers=headers)
    assert submissions.status_code == 200
    assert submissions.json()["items"] == []
