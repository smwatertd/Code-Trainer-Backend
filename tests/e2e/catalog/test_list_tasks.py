from __future__ import annotations

import pytest
from httpx import AsyncClient

from migrations.seeds.task_catalog_seed import CATALOG_SIZE


@pytest.mark.asyncio(loop_scope="session")
async def test_list_catalog_tasks__returns_seeded_public_tasks(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks")

    assert response.status_code == 200
    payload = response.json()
    product_tasks = [item for item in payload if item["id"] <= CATALOG_SIZE]
    assert len(product_tasks) == CATALOG_SIZE
    assert any(item["id"] == 1 and item["task_type"] == "task_build_from_blocks" for item in product_tasks)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_catalog_task__block_task_exposes_metadata(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert "correct_order" not in payload["payload"]
    assert "expected_code" not in payload["payload"]
    assert payload["payload"]["blocks_count"] == 4
    assert "test_cases" in payload["payload"]
    assert "code_examples" in payload["payload"]
