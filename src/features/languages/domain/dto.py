from __future__ import annotations

from dataclasses import dataclass

from src.features.languages.domain.language_config import LanguageConfig


@dataclass(frozen=True)
class LanguageDTO:
    id: str
    label: str
    file_extension: str
    monaco_language: str
    supported_features: tuple[str, ...]

    @classmethod
    def from_config(cls, config: LanguageConfig) -> LanguageDTO:
        return cls(
            id=config.id,
            label=config.label,
            file_extension=config.file_extension,
            monaco_language=config.monaco_language,
            supported_features=tuple(f.value for f in sorted(config.supported_features, key=lambda x: x.value)),
        )
