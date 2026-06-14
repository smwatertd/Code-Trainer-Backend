from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.flowchart import valid_if_flowchart


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__flowchart_code_to_flowchart_success(client: AsyncClient) -> None:
    nodes, edges = valid_if_flowchart()
    submit = await client.post(
        "/api/demo/check",
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

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "SUCCESS"
    assert body["success"] is True


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__flowchart_missing_decision_fails(client: AsyncClient) -> None:
    nodes = [
        {"id": "1", "type": "start", "x": 0, "y": 0},
        {"id": "2", "type": "input", "x": 0, "y": 100, "text": "readln(n)"},
        {"id": "3", "type": "output", "x": 0, "y": 200, "text": "writeln('pos')"},
        {"id": "4", "type": "end", "x": 0, "y": 300},
    ]
    edges = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
        {"source": "3", "target": "4"},
    ]

    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": 3,
            "language": "python",
            "code": "print(1)",
            "nodes": nodes,
            "edges": edges,
        },
    )
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["success"] is False
    assert body["pattern_errors"]
