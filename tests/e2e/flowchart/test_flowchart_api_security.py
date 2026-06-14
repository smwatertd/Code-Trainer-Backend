from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.flowchart import hello_flowchart, valid_if_flowchart

FLOWCHART_TASK_IDS = [3, 6, *range(39, 51)]


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("task_id", FLOWCHART_TASK_IDS)
async def test_catalog__flowchart_tasks_hide_flow_spec(client: AsyncClient, task_id: int) -> None:
    response = await client.get(f"/api/catalog/tasks/{task_id}")

    assert response.status_code == 200
    payload = response.json()["payload"]
    assert payload.get("flowchart_mode") == "code_to_flowchart"
    assert "flow_spec" not in payload
    assert "test_cases" not in payload
    assert "constructions" not in payload


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__flowchart_failure_has_no_flow_debug(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)
    nodes, edges = hello_flowchart()
    nodes[1]["text"] = "print('wrong')"

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 6,
            "language": "python",
            "code": "print('hello')",
            "nodes": nodes,
            "edges": edges,
        },
    )

    assert submit.status_code == 200
    body = await client.get(f"/api/submissions/{submit.json()['id']}", headers=headers)
    result = body.json()

    assert result["success"] is False
    assert "flow_debug" not in result
    assert any(item.get("type") == "FLOW_SOURCE_MISMATCH" for item in result.get("pattern_errors") or [])


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__flowchart_wrong_for_range_fails(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)
    nodes = [
        {"id": "1", "type": "start", "x": 0, "y": 0},
        {"id": "2", "type": "loop", "x": 0, "y": 100, "text": "for i in range(2)"},
        {"id": "3", "type": "output", "x": 0, "y": 200, "text": "print(i)"},
        {"id": "4", "type": "end", "x": 0, "y": 300},
    ]
    edges = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
        {"source": "3", "target": "2"},
        {"source": "2", "target": "4"},
    ]

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 40,
            "language": "python",
            "code": "for i in range(3):\n    print(i)",
            "nodes": nodes,
            "edges": edges,
        },
    )

    assert submit.status_code == 200
    detail = await client.get(f"/api/submissions/{submit.json()['id']}", headers=headers)
    result = detail.json()

    assert result["success"] is False
    assert any(item.get("type") == "FLOW_SOURCE_MISMATCH" for item in result.get("pattern_errors") or [])


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__flowchart_check_has_no_flow_debug(client: AsyncClient) -> None:
    nodes, edges = valid_if_flowchart()

    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": 3,
            "language": "python",
            "code": "n = int(input())\nif n > 0:\n    print('pos')\nelse:\n    print('nonpos')",
            "nodes": nodes,
            "edges": edges,
        },
    )
    assert submit.status_code == 200
    job_id = submit.json()["job_id"]

    result = await client.get(f"/api/demo/check/{job_id}")
    assert result.status_code == 200
    body = result.json()
    assert "flow_debug" not in body
