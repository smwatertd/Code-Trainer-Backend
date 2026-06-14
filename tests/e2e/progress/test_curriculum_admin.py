from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_admin__teacher_forbidden(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/curriculum/python/validate", headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_admin__admin_can_validate_and_debug(
    admin_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = admin_client
    headers = await auth_headers(client, auth_user)

    validate = await client.get("/api/curriculum/python/validate", headers=headers)
    assert validate.status_code == 200
    body = validate.json()
    assert body["language"] == "python"
    assert body["valid"] is True
    assert body["stats"]["learning_concepts"] >= 1

    debug = await client.get("/api/curriculum/pascal/debug", headers=headers)
    assert debug.status_code == 200
    payload = debug.json()
    assert payload["summary"]["language"] == "pascal"
    assert payload["validation"]["valid"] is True
    assert payload["chapters"]


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_admin__unknown_language_returns_404(
    admin_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = admin_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/curriculum/rust/validate", headers=headers)

    assert response.status_code == 404
