from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__forbidden_without_solve_permission(
    auth_guest_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_guest_client
    headers = await auth_headers(client, auth_user)

    response = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 2,
            "language": "python",
            "code": "print(1)",
        },
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
