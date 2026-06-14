from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__abandon_unknown_id_returns_404(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.post("/api/submissions/999999/abandon", headers=headers)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__pending_latest_missing_task_id_returns_422(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/submissions/pending/latest", headers=headers)

    assert response.status_code == 422


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__pending_latest_invalid_task_id_returns_422(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/submissions/pending/latest?task_id=0", headers=headers)

    assert response.status_code == 422


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__guest_cannot_get_submission(
    auth_guest_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_guest_client
    headers = await auth_headers(client, auth_user)

    response = await client.get(f"/api/submissions/{auth_user.submission_id}", headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__guest_cannot_get_pending_latest(
    auth_guest_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_guest_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/submissions/pending/latest?task_id=1", headers=headers)

    assert response.status_code == 403
