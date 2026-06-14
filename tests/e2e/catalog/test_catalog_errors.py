from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__get_missing_task_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/999999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__list_contains_seeded_block_reorder_task(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks")

    assert response.status_code == 200
    tasks = response.json()
    ids = {task["id"] for task in tasks}
    assert 1 in ids


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__task_detail_has_payload(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/2")

    assert response.status_code == 200
    body = response.json()
    assert body["task_type"] == "translation"
    assert "payload" in body
