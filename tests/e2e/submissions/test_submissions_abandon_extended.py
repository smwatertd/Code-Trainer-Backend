from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.submissions import submit_and_get


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__abandon_twice_second_call_is_noop(
    auth_queued_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_queued_client
    headers = await auth_headers(client, auth_user)

    created = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 2,
            "language": "python",
            "code": "print('pending')",
            "block_order": [0, 1],
        },
    )
    assert created.status_code == 200
    submission_id = created.json()["id"]

    first = await client.post(f"/api/submissions/{submission_id}/abandon", headers=headers)
    second = await client.post(f"/api/submissions/{submission_id}/abandon", headers=headers)

    assert first.status_code == 200
    assert first.json()["released"] is True
    assert first.json()["status"] == "failed"

    assert second.status_code == 200
    assert second.json()["released"] is False
    assert second.json()["status"] == "failed"


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__abandon_terminal_submission_is_noop(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    finished = await submit_and_get(
        client,
        headers,
        {
            "task_id": 1,
            "language": "python",
            "code": "print('Hello')\n",
        },
    )
    assert finished["status"] == "success"

    abandon = await client.post(
        f"/api/submissions/{finished['id']}/abandon",
        headers=headers,
    )

    assert abandon.status_code == 200
    assert abandon.json()["released"] is False
    assert abandon.json()["status"] == "success"


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__abandon_other_users_submission_returns_403(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, owner = auth_client
    owner_headers = await auth_headers(client, owner)

    created = await client.post(
        "/api/submissions",
        headers=owner_headers,
        json={
            "task_id": 1,
            "language": "python",
            "code": "print('x')",
        },
    )
    assert created.status_code == 200
    submission_id = created.json()["id"]

    from tests.e2e.helpers.users import register_user

    other = await register_user(client)
    other_headers = {"Authorization": f"Bearer {other['access_token']}"}

    response = await client.post(
        f"/api/submissions/{submission_id}/abandon",
        headers=other_headers,
    )

    assert response.status_code == 403
