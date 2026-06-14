from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__submit_requires_auth(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, _ = auth_client
    response = await client.post(
        "/api/submissions",
        json={
            "task_id": 2,
            "language": "python",
            "code": "print('b')\nprint('a')",
            "block_order": [1, 0],
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__submit_block_reorder_success(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 2,
            "language": "python",
            "code": "print('b')\nprint('a')",
            "block_order": [1, 0],
        },
    )

    assert submit.status_code == 200
    queued = submit.json()
    assert queued["id"] > 0
    assert queued["status"] == "success"

    detail = await client.get(f"/api/submissions/{queued['id']}", headers=headers)

    assert detail.status_code == 200
    body = detail.json()
    assert body["success"] is True
    assert body["status"] == "success"


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__submit_wrong_order_fails(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 2,
            "language": "python",
            "code": "print('a')\nprint('b')",
            "block_order": [0, 1],
        },
    )

    assert submit.status_code == 200
    submission_id = submit.json()["id"]

    detail = await client.get(f"/api/submissions/{submission_id}", headers=headers)

    assert detail.status_code == 200
    body = detail.json()
    assert body["success"] is False
    assert body["status"] == "failed"
