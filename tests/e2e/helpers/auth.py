from __future__ import annotations

from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser


async def login(client: AsyncClient, *, email: str, password: str) -> dict[str, object]:
    response = await client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()


async def auth_headers(client: AsyncClient, auth_user: E2EAuthUser) -> dict[str, str]:
    tokens = await login(client, email=auth_user.email, password=auth_user.password)
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def blocked_auth_headers(auth_user: E2EAuthUser) -> dict[str, str]:
    assert auth_user.access_token is not None
    return {"Authorization": f"Bearer {auth_user.access_token}"}
