from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__abandon_queued_submission(
    auth_queued_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_queued_client
    headers = await auth_headers(client, auth_user)

    create = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 2,
            "language": "python",
            "code": "print('pending')",
            "block_order": [0, 1],
        },
    )
    assert create.status_code == 200
    submission_id = create.json()["id"]
    assert create.json()["status"] == "queued"

    abandon = await client.post(f"/api/submissions/{submission_id}/abandon", headers=headers)

    assert abandon.status_code == 200
    body = abandon.json()
    assert body["released"] is True
    assert body["status"] == "failed"

    detail = await client.get(f"/api/submissions/{submission_id}", headers=headers)
    assert detail.json()["status"] == "failed"
