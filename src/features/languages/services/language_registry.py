from __future__ import annotations

from src.features.languages.domain.language_config import LanguageConfig


class LanguageRegistry:
    def __init__(self) -> None:
        self._store: dict[str, LanguageConfig] = {}

    def clear(self) -> None:
        self._store.clear()

    def register(self, config: LanguageConfig) -> None:
        self._store[config.id] = config

    def get(self, language_id: str) -> LanguageConfig | None:
        return self._store.get(str(language_id).lower())

    def get_or_raise(self, language_id: str) -> LanguageConfig:
        cfg = self.get(language_id)
        if cfg is None:
            available = ", ".join(sorted(self._store))
            raise ValueError(f"Language '{language_id}' is not registered. Available: {available}")
        return cfg

    def all(self) -> list[LanguageConfig]:
        return list(self._store.values())

    def ids(self) -> list[str]:
        return list(self._store.keys())

    @property
    def is_loaded(self) -> bool:
        return bool(self._store)
