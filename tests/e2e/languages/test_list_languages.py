from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_list_languages__returns_public_catalog(client: AsyncClient) -> None:
    response = await client.get("/api/languages")

    assert response.status_code == 200, response.text
    payload = response.json()
    ids = {item["id"] for item in payload}

    assert "python" in ids
    assert "pascal" in ids
    assert "javascript" not in ids


@pytest.mark.asyncio(loop_scope="session")
async def test_list_languages__response_shape_matches_schema(client: AsyncClient) -> None:
    response = await client.get("/api/languages")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 5

    for item in payload:
        assert set(item) == {
            "id",
            "label",
            "file_extension",
            "monaco_language",
            "supported_features",
        }
        assert isinstance(item["supported_features"], list)


@pytest.mark.asyncio(loop_scope="session")
async def test_list_languages__python_entry_example(client: AsyncClient) -> None:
    response = await client.get("/api/languages")
    payload = response.json()

    python = next(item for item in payload if item["id"] == "python")
    assert python == {
        "id": "python",
        "label": "Python",
        "file_extension": ".py",
        "monaco_language": "python",
        "supported_features": ["compile", "lint", "test"],
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_list_languages__sorted_by_id(client: AsyncClient) -> None:
    response = await client.get("/api/languages")
    ids = [item["id"] for item in response.json()]

    assert ids == sorted(ids)


@pytest.mark.asyncio(loop_scope="session")
async def test_list_languages__unknown_route_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/languages/unknown")

    assert response.status_code == 404
