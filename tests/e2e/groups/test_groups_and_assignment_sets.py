from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.users import register_user


async def _register_student(client: AsyncClient) -> dict[str, str]:
    body = await register_user(client, name="Groups Student")
    return {"Authorization": f"Bearer {body['access_token']}"}


@pytest.mark.asyncio(loop_scope="session")
async def test_groups__teacher_creates_and_student_joins(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    teacher_http, teacher = teacher_client
    teacher_headers = await auth_headers(teacher_http, teacher)
    student_headers = await _register_student(teacher_http)

    create_group = await teacher_http.post(
        "/api/groups",
        headers=teacher_headers,
        json={"name": "E2E Group"},
    )
    assert create_group.status_code == 201
    group_id = create_group.json()["id"]

    invite = await teacher_http.post(
        f"/api/groups/{group_id}/invitations",
        headers=teacher_headers,
        json={"max_uses": 5, "expires_in_days": 7},
    )
    assert invite.status_code == 200
    code = invite.json()["code"]

    join = await teacher_http.post(
        "/api/groups/join",
        headers=student_headers,
        json={"code": code},
    )
    assert join.status_code == 200
    assert join.json()["id"] == group_id

    joined = await teacher_http.get("/api/groups/joined", headers=student_headers)
    assert joined.status_code == 200
    assert any(item["id"] == group_id for item in joined.json())


@pytest.mark.asyncio(loop_scope="session")
async def test_assignment_sets__teacher_crud_and_student_access(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    teacher_http, teacher = teacher_client
    teacher_headers = await auth_headers(teacher_http, teacher)
    student_headers = await _register_student(teacher_http)

    group = await teacher_http.post(
        "/api/groups",
        headers=teacher_headers,
        json={"name": "Sets Group"},
    )
    group_id = group.json()["id"]
    invite = await teacher_http.post(
        f"/api/groups/{group_id}/invitations",
        headers=teacher_headers,
        json={},
    )
    await teacher_http.post(
        "/api/groups/join",
        headers=student_headers,
        json={"code": invite.json()["code"]},
    )

    create_set = await teacher_http.post(
        "/api/assignment-sets",
        headers=teacher_headers,
        json={
            "name": "Week 1",
            "description": "Loops practice",
            "visibility": "private",
            "group_id": group_id,
        },
    )
    assert create_set.status_code == 201
    set_id = create_set.json()["id"]

    add_item = await teacher_http.post(
        f"/api/assignment-sets/{set_id}/items",
        headers=teacher_headers,
        json={"task_id": 4, "sort_order": 0},
    )
    assert add_item.status_code == 204

    mine = await teacher_http.get("/api/assignment-sets/mine", headers=teacher_headers)
    assert mine.status_code == 200
    assert any(item["id"] == set_id for item in mine.json())

    accessible = await teacher_http.get("/api/assignment-sets", headers=student_headers)
    assert accessible.status_code == 200
    assert any(item["id"] == set_id for item in accessible.json())

    detail = await teacher_http.get(f"/api/assignment-sets/{set_id}", headers=student_headers)
    assert detail.status_code == 200
    assert detail.json()["items"][0]["task_id"] == 4


@pytest.mark.asyncio(loop_scope="session")
async def test_groups__dashboard_returns_members_and_progress(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    teacher_http, teacher = teacher_client
    teacher_headers = await auth_headers(teacher_http, teacher)
    student_headers = await _register_student(teacher_http)

    group = await teacher_http.post(
        "/api/groups",
        headers=teacher_headers,
        json={"name": "Dashboard Group"},
    )
    assert group.status_code == 201
    group_id = group.json()["id"]

    invite = await teacher_http.post(
        f"/api/groups/{group_id}/invitations",
        headers=teacher_headers,
        json={},
    )
    await teacher_http.post(
        "/api/groups/join",
        headers=student_headers,
        json={"code": invite.json()["code"]},
    )

    create_set = await teacher_http.post(
        "/api/assignment-sets",
        headers=teacher_headers,
        json={
            "name": "Dashboard Set",
            "description": "",
            "visibility": "private",
            "group_id": group_id,
        },
    )
    set_id = create_set.json()["id"]
    await teacher_http.post(
        f"/api/assignment-sets/{set_id}/items",
        headers=teacher_headers,
        json={"task_id": 4, "sort_order": 0},
    )

    dashboard = await teacher_http.get(
        f"/api/groups/{group_id}/dashboard",
        headers=teacher_headers,
    )
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["group"]["id"] == group_id
    assert len(body["members"]) == 1
    assert len(body["assignment_sets"]) == 1
    assert body["assignment_sets"][0]["task_count"] == 1
    assert len(body["student_summaries"]) == 1
    assert body["student_summaries"][0]["total_tasks"] == 1
    assert len(body["task_progress"]) == 1
    assert body["task_progress"][0]["task_id"] == 4
    assert body["task_progress"][0]["progress_status"] == "not_started"
