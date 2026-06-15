from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__curriculum_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/progress/curriculum/python/chapter_1")

    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__curriculum_guest_forbidden(
    auth_guest_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_guest_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/progress/curriculum/python/chapter_1", headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__task_not_started_before_any_submission(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/progress/tasks/1", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["task_id"] == 1
    assert body["progress_status"] == "not_started"
    assert body["attempts_count"] == 0
    assert body["passed_count"] == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_progress__curriculum_normalizes_language_case(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/progress/curriculum/Python/chapter_1", headers=headers)

    assert response.status_code == 200
    assert response.json()["language"] == "python"
