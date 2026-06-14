from __future__ import annotations

import pytest

from src.core.either import Ok
from src.features.languages.usecases import ListLanguagesUseCase


@pytest.mark.asyncio
async def test_list_languages_usecase__delegates_to_service(languages_service) -> None:
    use_case = ListLanguagesUseCase(languages_service=languages_service)

    result = await use_case.execute()

    assert isinstance(result, Ok)
    assert len(result.value) == 5
    assert all(item.id != "javascript" for item in result.value)
