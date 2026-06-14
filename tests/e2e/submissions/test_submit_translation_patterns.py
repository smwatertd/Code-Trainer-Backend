from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__translation_requires_for_loop(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 4,
            "language": "python",
            "code": "print(0)\nprint(1)\nprint(2)\n",
        },
    )

    assert submit.status_code == 200
    queued = submit.json()
    assert queued["status"] == "failed"

    detail = await client.get(f"/api/submissions/{queued['id']}", headers=headers)

    assert detail.status_code == 200
    body = detail.json()
    assert body["success"] is False
    assert body["pattern_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__translation_with_for_loop_passes(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 4,
            "language": "python",
            "code": "for i in range(3):\n    print(i)\n",
        },
    )

    assert submit.status_code == 200
    queued = submit.json()
    assert queued["status"] == "success"

    detail = await client.get(f"/api/submissions/{queued['id']}", headers=headers)

    assert detail.status_code == 200
    body = detail.json()
    assert body["success"] is True
    assert body["test_results"]
