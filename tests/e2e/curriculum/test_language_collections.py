from __future__ import annotations

import pytest
from httpx import AsyncClient

from src.dev.seed_curriculum_links import clear_dev_curriculum_links, seed_dev_curriculum_links


@pytest.mark.asyncio(loop_scope="session")
async def test_language_collections__python_track_has_tasks(client: AsyncClient) -> None:
    await seed_dev_curriculum_links()
    try:
        response = await client.get("/api/curriculum/python/collections")
        assert response.status_code == 200
        body = response.json()

        assert body["language"] == "python"
        assert body["progress"]["total_tasks"] == 128

        collections = body["collections"]
        assert len(collections) == 16

        chapter_1 = next(item for item in collections if item["collection_id"] == "chapter_1")
        chapter_16 = next(item for item in collections if item["collection_id"] == "chapter_16")

        assert chapter_1["progress"]["total_tasks"] == 8
        assert chapter_16["progress"]["total_tasks"] == 8
        assert chapter_1["button_label"] != "Нет задач"
    finally:
        await seed_dev_curriculum_links()


@pytest.mark.asyncio(loop_scope="session")
async def test_language_collections__without_links_shows_zero_tasks(client: AsyncClient) -> None:
    """Regression: /learn/python shows 0/0 when task_curriculum_link table is empty."""
    await clear_dev_curriculum_links()
    try:
        response = await client.get("/api/curriculum/python/collections")
        assert response.status_code == 200
        body = response.json()

        assert body["progress"]["total_tasks"] == 0
        chapter_1 = next(item for item in body["collections"] if item["collection_id"] == "chapter_1")
        assert chapter_1["progress"]["total_tasks"] == 0
        assert chapter_1["button_label"] == "Нет задач"
    finally:
        await seed_dev_curriculum_links()


@pytest.mark.asyncio(loop_scope="session")
async def test_language_collections__cpp_track_has_tasks(client: AsyncClient) -> None:
    await seed_dev_curriculum_links()
    try:
        response = await client.get("/api/curriculum/cpp/collections")
        assert response.status_code == 200
        body = response.json()

        assert body["language"] == "cpp"
        assert body["progress"]["total_tasks"] == 128
        assert len(body["collections"]) == 16
        chapter_1 = next(item for item in body["collections"] if item["collection_id"] == "chapter_1")
        assert chapter_1["progress"]["total_tasks"] == 8
        assert chapter_1["button_label"] != "Нет задач"
    finally:
        await seed_dev_curriculum_links()


@pytest.mark.asyncio(loop_scope="session")
async def test_language_collections__java_and_csharp_tracks_have_tasks(client: AsyncClient) -> None:
    await seed_dev_curriculum_links()
    try:
        for language in ("java", "csharp"):
            response = await client.get(f"/api/curriculum/{language}/collections")
            assert response.status_code == 200
            body = response.json()

            assert body["language"] == language
            assert body["progress"]["total_tasks"] == 128
            assert len(body["collections"]) == 16
            chapter = next(item for item in body["collections"] if item["collection_id"] == "chapter_1")
            assert chapter["progress"]["total_tasks"] == 8
            assert chapter["button_label"] != "Нет задач"
    finally:
        await seed_dev_curriculum_links()


@pytest.mark.asyncio(loop_scope="session")
async def test_language_collections__pascal_track_has_tasks(client: AsyncClient) -> None:
    await seed_dev_curriculum_links()
    try:
        response = await client.get("/api/curriculum/pascal/collections")
        assert response.status_code == 200
        body = response.json()

        assert body["language"] == "pascal"
        assert body["progress"]["total_tasks"] == 128
        chapter_1 = next(item for item in body["collections"] if item["collection_id"] == "chapter_1")
        assert chapter_1["progress"]["total_tasks"] == 8
        assert chapter_1["button_label"] != "Нет задач"
        assert all(item["progress"]["total_tasks"] > 0 for item in body["collections"])
        assert any(item["collection_id"] == "chapter_16" for item in body["collections"])
    finally:
        await seed_dev_curriculum_links()
