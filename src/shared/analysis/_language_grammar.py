from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from src.features.languages.services.language_loader import LanguageLoader
from src.features.languages.services.language_registry import LanguageRegistry

_BACKEND_ROOT = Path(__file__).resolve().parents[3]


@lru_cache
def _registry() -> LanguageRegistry:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(_BACKEND_ROOT / "languages")
    return registry


def get_tree_sitter_grammar(language_id: str) -> str:
    cfg = _registry().get_or_raise(language_id)
    return cfg.tree_sitter_grammar or cfg.id
