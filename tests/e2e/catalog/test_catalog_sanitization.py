from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    ("task_id", "hidden_keys"),
    [
        (5, {"correct_order", "expected_code", "test_cases"}),
        (9, {"test_cases", "constructions", "patterns"}),
        (10, {"test_cases", "constructions", "patterns"}),
    ],
)
async def test_catalog__detail_hides_execution_answers(
    client: AsyncClient,
    task_id: int,
    hidden_keys: set[str],
) -> None:
    response = await client.get(f"/api/catalog/tasks/{task_id}")

    assert response.status_code == 200
    payload = response.json()["payload"]
    for key in hidden_keys:
        assert key not in payload


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__flowchart_task6_hides_validation_spec(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/6")

    assert response.status_code == 200
    payload = response.json()["payload"]
    assert payload["flowchart_mode"] == "code_to_flowchart"
    assert "flow_spec" not in payload
    assert "test_cases" not in payload
    assert "constructions" not in payload
    assert "source_code" in payload


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__block_reorder_exposes_blocks_not_raw_strings(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/catalog/tasks/5")

    assert response.status_code == 200
    payload = response.json()["payload"]
    assert payload["blocks_count"] == 2
    assert all("id" in block and "content" in block for block in payload["blocks"])


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__summary_never_includes_payload(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks")

    assert response.status_code == 200
    for item in response.json():
        assert "payload" not in item
        assert {"id", "title", "description", "difficulty", "task_type"} <= set(item.keys())
