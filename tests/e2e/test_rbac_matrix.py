from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.users import register_user


@pytest.mark.asyncio(loop_scope="session")
async def test_rbac__teacher_can_validate_curriculum_link_but_not_admin_bundle(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    allowed = await client.post(
        "/api/curriculum/tasks/validate-link",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "function_definition",
            "exercise_pattern_id": "tr_pattern_translation",
        },
    )
    forbidden = await client.get("/api/curriculum/python/validate", headers=headers)

    assert allowed.status_code == 200
    assert forbidden.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_rbac__registered_student_can_submit_and_view_progress(client: AsyncClient) -> None:
    user = await register_user(client)
    headers = {"Authorization": f"Bearer {user['access_token']}"}

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={"task_id": 1, "language": "python", "code": "print('hi')\n"},
    )
    progress = await client.get("/api/progress/tasks/1", headers=headers)
    curriculum_admin = await client.get("/api/curriculum/python/debug", headers=headers)

    assert submit.status_code == 200
    assert progress.status_code == 200
    assert curriculum_admin.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_rbac__guest_cannot_access_submissions_or_progress(
    auth_guest_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_guest_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={"task_id": 1, "language": "python", "code": "print(1)"},
    )
    progress = await client.get("/api/progress/tasks/1", headers=headers)

    assert submit.status_code == 403
    assert progress.status_code == 403
