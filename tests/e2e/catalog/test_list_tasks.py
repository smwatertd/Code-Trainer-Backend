from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_list_catalog_tasks__returns_seeded_public_tasks(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 50
    assert any(item["id"] == 2 and item["task_type"] == "task_build_from_blocks" for item in payload)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_catalog_task__hides_block_reorder_answers(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/2")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 2
    assert "correct_order" not in payload["payload"]
    assert "expected_code" not in payload["payload"]
    assert payload["payload"]["blocks_count"] == 2
