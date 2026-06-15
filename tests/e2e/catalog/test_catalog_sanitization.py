from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    ("task_id", "hidden_keys"),
    [
        (1, {"correct_order", "expected_code"}),
        (4, {"correct_order", "expected_code"}),
        (2, {"kind"}),
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
async def test_catalog__block_reorder_exposes_blocks_not_raw_strings(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/catalog/tasks/1")

    assert response.status_code == 200
    payload = response.json()["payload"]
    assert payload["blocks_count"] == 8
    assert all("id" in block and "content" in block for block in payload["blocks"])


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__summary_never_includes_payload(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks")

    assert response.status_code == 200
    for item in response.json():
        assert "payload" not in item
        assert {"id", "title", "description", "difficulty", "task_type"} <= set(item.keys())
