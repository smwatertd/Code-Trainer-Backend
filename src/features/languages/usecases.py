from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult
from src.features.languages.domain.dto import LanguageDTO
from src.features.languages.services.languages_service import LanguagesService


@dataclass
class ListLanguagesUseCase:
    languages_service: LanguagesService

    async def execute(self) -> AppResult[list[LanguageDTO]]:
        return await self.languages_service.list_public_languages()
