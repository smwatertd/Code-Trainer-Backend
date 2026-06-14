from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.flowchart import valid_if_flowchart


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__flowchart_code_to_flowchart_success(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)
    nodes, edges = valid_if_flowchart()

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 3,
            "language": "python",
            "code": "if n > 0: print('pos')\nelse: print('nonpos')",
            "nodes": nodes,
            "edges": edges,
        },
    )

    assert submit.status_code == 200
    queued = submit.json()
    assert queued["status"] == "success"

    detail = await client.get(f"/api/submissions/{queued['id']}", headers=headers)

    assert detail.status_code == 200
    body = detail.json()
    assert body["success"] is True
    assert body["status"] == "success"
    assert body["pattern_errors"] == []


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__flowchart_records_progress(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)
    nodes, edges = valid_if_flowchart()

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 3,
            "language": "python",
            "code": "if n > 0: print('pos')\nelse: print('nonpos')",
            "nodes": nodes,
            "edges": edges,
        },
    )
    assert submit.status_code == 200

    progress = await client.get("/api/progress/tasks/3", headers=headers)

    assert progress.status_code == 200
    body = progress.json()
    assert body["progress_status"] == "passed"
    assert body["passed_count"] == 1
