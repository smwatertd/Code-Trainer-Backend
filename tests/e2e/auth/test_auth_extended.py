from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers, login


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_me__teacher_role(teacher_client: tuple[AsyncClient, E2EAuthUser]) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["role"] == "teacher"


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_me__admin_role(admin_client: tuple[AsyncClient, E2EAuthUser]) -> None:
    client, auth_user = admin_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_logout__idempotent_second_call_returns_204(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    tokens = await login(client, email=auth_user.email, password=auth_user.password)

    first = await client.post("/api/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    second = await client.post("/api/auth/logout", json={"refresh_token": tokens["refresh_token"]})

    assert first.status_code == 204
    assert second.status_code == 204


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_refresh__invalid_token_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": "not-a-valid-token"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_login__validation_error_on_empty_body(client: AsyncClient) -> None:
    response = await client.post("/api/auth/login", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
