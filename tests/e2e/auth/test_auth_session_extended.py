from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import login


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_me__still_works_after_logout_with_access_token(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    tokens = await login(client, email=auth_user.email, password=auth_user.password)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    logout = await client.post(
        "/api/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert logout.status_code == 204

    me = await client.get("/api/auth/me", headers=headers)

    assert me.status_code == 200
    assert me.json()["email"] == auth_user.email


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_refresh__access_token_rejected(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    tokens = await login(client, email=auth_user.email, password=auth_user.password)

    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["access_token"]},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_logout__invalid_refresh_token_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/logout",
        json={"refresh_token": "not-a-valid-token"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_me__invalid_bearer_token_returns_401(client: AsyncClient) -> None:
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not-a-jwt"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_register__validation_error_on_short_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/register",
        json={
            "name": "Short Password",
            "email": "short-password@example.com",
            "password": "123",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
