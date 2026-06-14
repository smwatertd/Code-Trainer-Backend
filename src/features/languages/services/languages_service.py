from __future__ import annotations

from src.core.either import AppResult, Ok
from src.features.languages.domain.dto import LanguageDTO
from src.features.languages.services.language_registry import LanguageRegistry

_HIDDEN_LANGUAGE_IDS = frozenset({"javascript"})


class LanguagesService:
    def __init__(self, registry: LanguageRegistry) -> None:
        self._registry = registry

    async def list_public_languages(self) -> AppResult[list[LanguageDTO]]:
        items = [
            LanguageDTO.from_config(cfg)
            for cfg in sorted(self._registry.all(), key=lambda c: c.id)
            if cfg.id not in _HIDDEN_LANGUAGE_IDS
        ]
        return Ok(items)
