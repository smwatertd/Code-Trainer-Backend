from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__get_requires_auth(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    response = await client.get(f"/api/submissions/{auth_user.submission_id}")

    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__get_owned_submission(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.get(f"/api/submissions/{auth_user.submission_id}", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == auth_user.submission_id
    assert body["task_id"] == 2
    assert body["status"] == "success"
    assert body["success"] is True
    assert len(body["compiler_errors"]) == 1
    assert len(body["pattern_errors"]) == 1


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__not_found_for_missing_id(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/submissions/999999", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__pending_latest_returns_null_when_none(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/submissions/pending/latest?task_id=2", headers=headers)

    assert response.status_code == 200
    assert response.json() is None
