from __future__ import annotations

import pytest
from httpx import AsyncClient

from migrations.seeds.task_catalog_seed import CATALOG_SIZE


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    ("task_id", "hidden_keys"),
    [
        (1, {"correct_order", "expected_code"}),
        (2, {"kind"}),
        (3, {"kind"}),
    ],
)
async def test_catalog__public_detail_hides_grading_secrets(
    client: AsyncClient,
    task_id: int,
    hidden_keys: set[str],
) -> None:
    response = await client.get(f"/api/catalog/tasks/{task_id}")

    assert response.status_code == 200
    payload = response.json()["payload"]
    for key in hidden_keys:
        assert key not in payload, f"task {task_id} leaked {key}"


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__anonymous_can_read_public_tasks_without_auth(client: AsyncClient) -> None:
    listing = await client.get("/api/catalog/tasks")
    detail = await client.get("/api/catalog/tasks/1")

    assert listing.status_code == 200
    product_tasks = [item for item in listing.json() if item["id"] <= CATALOG_SIZE]
    assert len(product_tasks) == CATALOG_SIZE
    assert detail.status_code == 200
    assert detail.json()["id"] == 1


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__unknown_task_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/999999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
