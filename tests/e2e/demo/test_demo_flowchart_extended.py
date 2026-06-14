from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.demo import run_demo_check
from tests.e2e.helpers.flowchart import hello_flowchart


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__flowchart_task6_semantic_success(client: AsyncClient) -> None:
    nodes, edges = hello_flowchart()

    body = await run_demo_check(
        client,
        {
            "task_id": 6,
            "language": "python",
            "code": "print('hello')",
            "nodes": nodes,
            "edges": edges,
        },
    )

    assert body["success"] is True


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__flowchart_task6_wrong_block_text_fails(client: AsyncClient) -> None:
    nodes, edges = hello_flowchart()
    nodes[1]["text"] = "print('wrong')"

    body = await run_demo_check(
        client,
        {
            "task_id": 6,
            "language": "python",
            "code": "print('hello')",
            "nodes": nodes,
            "edges": edges,
        },
    )

    assert body["success"] is False
    assert any(item.get("type") == "FLOW_SOURCE_MISMATCH" for item in body.get("pattern_errors") or [])


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__flowchart_task3_missing_decision_branch_fails(client: AsyncClient) -> None:
    nodes = [
        {"id": "1", "type": "start", "x": 0, "y": 0},
        {"id": "2", "type": "output", "x": 0, "y": 100, "text": "print('pos')"},
        {"id": "3", "type": "end", "x": 0, "y": 200},
    ]
    edges = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
    ]

    body = await run_demo_check(
        client,
        {
            "task_id": 3,
            "language": "python",
            "code": "if n > 0: print('pos')\nelse: print('nonpos')",
            "nodes": nodes,
            "edges": edges,
        },
    )

    assert body["success"] is False
    assert body["pattern_errors"]
