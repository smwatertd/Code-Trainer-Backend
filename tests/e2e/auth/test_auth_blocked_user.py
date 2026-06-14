from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import blocked_auth_headers, login
from tests.e2e.helpers.http import assert_api_error


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_login__blocked_user_returns_401(
    blocked_auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = blocked_auth_client

    response = await client.post(
        "/api/auth/login",
        json={"email": auth_user.email, "password": auth_user.password},
    )

    assert_api_error(response, status=401, code="UNAUTHORIZED", message="Account is disabled")


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_refresh__blocked_user_returns_401(
    blocked_auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = blocked_auth_client

    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": auth_user.refresh_token},
    )

    assert_api_error(response, status=401, code="UNAUTHORIZED", message="Account is disabled")


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_me__blocked_user_with_valid_access_token_returns_401(
    blocked_auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = blocked_auth_client

    response = await client.get("/api/auth/me", headers=blocked_auth_headers(auth_user))

    assert_api_error(response, status=401, code="UNAUTHORIZED", message="Account is disabled")


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_refresh__reused_token_after_rotation_returns_401(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    tokens = await login(client, email=auth_user.email, password=auth_user.password)

    refresh = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh.status_code == 200

    reuse = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert_api_error(
        reuse,
        status=401,
        code="UNAUTHORIZED",
        message="Refresh session is invalid",
    )


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_register__email_case_insensitive_duplicate_returns_409(
    client: AsyncClient,
) -> None:
    first = await client.post(
        "/api/auth/register",
        json={
            "name": "Case Test",
            "email": "CaseSensitive@Example.com",
            "password": "password123",
        },
    )
    second = await client.post(
        "/api/auth/register",
        json={
            "name": "Case Test 2",
            "email": "casesensitive@example.com",
            "password": "password123",
        },
    )

    assert first.status_code == 201
    assert_api_error(second, status=409, code="CONFLICT")
