from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    ("task_id", "task_type"),
    [
        (1, "translation"),
        (2, "task_build_from_blocks"),
        (3, "task_flowchart_to_code"),
        (4, "task_write_from_description"),
        (5, "task_build_from_blocks"),
        (6, "task_flowchart_to_code"),
        (7, "translation"),
        (8, "translation"),
        (9, "task_write_from_description"),
        (10, "task_write_from_description"),
    ],
)
async def test_catalog__get_each_seeded_task(
    client: AsyncClient,
    task_id: int,
    task_type: str,
) -> None:
    response = await client.get(f"/api/catalog/tasks/{task_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == task_id
    assert body["task_type"] == task_type
    assert "title" in body
    assert "payload" in body


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__list_contains_all_seeded_ids(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks")

    assert response.status_code == 200
    ids = {item["id"] for item in response.json()}
    assert len(ids) == 50
    assert ids == set(range(1, 51))


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__translation_task_hides_test_cases(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/4")

    assert response.status_code == 200
    body = response.json()
    assert body["task_type"] == "task_write_from_description"
    payload = body["payload"]
    assert "test_cases" not in payload
    assert "constructions" not in payload
    assert "source_code" not in payload
    assert payload["target_language"] == "python"


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__flowchart_task_exposes_mode_and_hides_answers(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/3")

    assert response.status_code == 200
    payload = response.json()["payload"]
    assert payload["flowchart_mode"] == "code_to_flowchart"
    assert "test_cases" not in payload


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__snippet_task_hides_internal_fields(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/7")

    assert response.status_code == 200
    payload = response.json()["payload"]
    assert "kind" not in payload
    assert "patterns" not in payload
    assert payload["target_language"] == "cpp"


@pytest.mark.asyncio(loop_scope="session")
async def test_catalog__get_unknown_task_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/catalog/tasks/999999")

    assert response.status_code == 404
