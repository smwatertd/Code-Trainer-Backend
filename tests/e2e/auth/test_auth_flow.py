from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers, login


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_login__invalid_credentials(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_login__success_returns_tokens(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    tokens = await login(client, email=auth_user.email, password=auth_user.password)

    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"
    assert tokens["expires_in"] > 0


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_me__requires_bearer_token(client: AsyncClient) -> None:
    response = await client.get("/api/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_me__returns_current_user(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == auth_user.user_id
    assert body["email"] == auth_user.email
    assert body["role"] == "student"


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_refresh__rotates_tokens(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    tokens = await login(client, email=auth_user.email, password=auth_user.password)

    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert response.status_code == 200
    refreshed = response.json()
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]
    assert refreshed["refresh_token"] != tokens["refresh_token"]


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_logout__revokes_refresh_token(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    tokens = await login(client, email=auth_user.email, password=auth_user.password)

    logout = await client.post(
        "/api/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert logout.status_code == 204

    refresh = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert refresh.status_code == 401
