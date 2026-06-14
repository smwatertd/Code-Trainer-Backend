from __future__ import annotations

import pytest

from src.core.either import Ok
from src.features.languages.services.languages_service import LanguagesService


@pytest.mark.asyncio
async def test_list_public_languages__returns_sorted_stable_catalog(languages_service: LanguagesService) -> None:
    result = await languages_service.list_public_languages()

    assert isinstance(result, Ok)
    ids = [item.id for item in result.value]

    assert ids == sorted(ids)
    assert set(ids) == {"cpp", "csharp", "java", "pascal", "python"}


@pytest.mark.asyncio
async def test_list_public_languages__dto_has_only_public_fields(languages_service: LanguagesService) -> None:
    result = await languages_service.list_public_languages()

    assert isinstance(result, Ok)
    python = next(item for item in result.value if item.id == "python")
    payload = python.__dict__

    assert set(payload) == {
        "id",
        "label",
        "file_extension",
        "monaco_language",
        "supported_features",
    }
