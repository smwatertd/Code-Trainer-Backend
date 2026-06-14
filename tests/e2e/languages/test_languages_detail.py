from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_languages__list_includes_python_cpp_pascal(client: AsyncClient) -> None:
    response = await client.get("/api/languages")

    assert response.status_code == 200
    languages = {item["id"]: item for item in response.json()}
    assert "python" in languages
    assert "cpp" in languages
    assert "pascal" in languages
    assert languages["python"]["label"] == "Python"
    assert languages["python"]["file_extension"] == ".py"


@pytest.mark.asyncio(loop_scope="session")
async def test_languages__each_entry_has_monaco_language(client: AsyncClient) -> None:
    response = await client.get("/api/languages")

    assert response.status_code == 200
    for item in response.json():
        assert item["monaco_language"]
        assert item["id"]
