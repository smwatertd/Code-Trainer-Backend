from __future__ import annotations

import pytest
from httpx import AsyncClient

from migrations.seeds.task_catalog_seed import CATALOG_SIZE

_IMPL_TYPES = (
    "task_build_from_blocks",
    "task_fill_placeholders",
    "translation",
    "translation",
)


def _expected_type(task_id: int) -> str:
    return _IMPL_TYPES[(task_id - 1) % 4]


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("task_id", list(range(1, 13)))
async def test_catalog__get_each_seeded_task(client: AsyncClient, task_id: int) -> None:
    response = await client.get(f"/api/catalog/tasks/{task_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == task_id
    assert body["task_type"] == _expected_type(task_id)
    assert "title" in body
    assert "payload" in body


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__list_contains_all_seeded_ids(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks")

    assert response.status_code == 200
    ids = {item["id"] for item in response.json()}
    assert len([task_id for task_id in ids if task_id <= CATALOG_SIZE]) == CATALOG_SIZE
    assert ids >= set(range(1, CATALOG_SIZE + 1))
    assert 129 not in ids
    assert 331 not in ids


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__block_task_exposes_student_metadata(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/1")

    assert response.status_code == 200
    body = response.json()
    assert body["task_type"] == "task_build_from_blocks"
    assert body["title"] == "Поиск максимума в массиве"
    payload = body["payload"]
    assert payload["language"] == "pascal"
    assert "test_cases" in payload
    assert "constructions" in payload
    assert "code_examples" in payload


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__translation_task_exposes_reference_and_tests(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/3")

    assert response.status_code == 200
    payload = response.json()["payload"]
    assert payload["target_language"] == "pascal"
    assert payload["source_language"] == "python"
    assert "test_cases" in payload
    assert "code_examples" in payload
    assert "kind" not in payload


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__debug_translation_exposes_template(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/4")

    assert response.status_code == 200
    payload = response.json()["payload"]
    assert payload["template"]
    assert payload["target_language"] == "python"
    assert "count = 1" in payload["template"]
    assert "count = 0" in payload["code_examples"]["python"]


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__placeholder_task_exposes_bank(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/2")

    assert response.status_code == 200
    body = response.json()
    assert body["task_type"] == "task_fill_placeholders"
    payload = body["payload"]
    assert payload["placeholder_template"]
    assert payload["placeholder_bank"]
    assert payload["language"] == "python"
    assert "if code == target" in payload["code_examples"]["python"]


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__get_unknown_task_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/999999")

    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__legacy_task_ids_are_removed(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/129")

    assert response.status_code == 404
