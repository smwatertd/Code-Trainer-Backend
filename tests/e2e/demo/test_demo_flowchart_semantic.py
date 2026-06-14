from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.flowchart import FC_HELLO, hello_flowchart


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__flowchart_semantic_after_structural(client: AsyncClient) -> None:
    nodes, edges = hello_flowchart()
    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": FC_HELLO,
            "language": "python",
            "code": "print('hello')",
            "nodes": nodes,
            "edges": edges,
        },
    )

    assert submit.status_code == 200
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "SUCCESS"
    assert body["success"] is True
