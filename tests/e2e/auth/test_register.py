from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_register__creates_user_and_returns_tokens(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/register",
        json={
            "name": "New Student",
            "email": "new-student@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_register__duplicate_email_returns_409(client: AsyncClient) -> None:
    payload = {
        "name": "Duplicate",
        "email": "duplicate@example.com",
        "password": "password123",
    }

    first = await client.post("/api/auth/register", json=payload)
    second = await client.post("/api/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
