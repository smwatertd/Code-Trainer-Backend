from __future__ import annotations

from uuid import uuid4

from httpx import AsyncClient


async def register_user(
    client: AsyncClient,
    *,
    name: str = "E2E User",
    password: str = "password123",
    email: str | None = None,
) -> dict:
    resolved_email = email or f"e2e-{uuid4().hex[:10]}@example.com"
    response = await client.post(
        "/api/auth/register",
        json={
            "name": name,
            "email": resolved_email,
            "password": password,
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    body["email"] = resolved_email
    body["password"] = password
    return body
