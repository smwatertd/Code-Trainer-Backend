from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.payloads import TASK3_SUM_PASCAL


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__flowchart_code_to_flowchart_success(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json=TASK3_SUM_PASCAL,
    )

    assert submit.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__flowchart_records_progress(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json=TASK3_SUM_PASCAL,
    )
    assert submit.status_code == 200

    progress = await client.get("/api/progress/tasks/3", headers=headers)

    assert progress.status_code == 200
