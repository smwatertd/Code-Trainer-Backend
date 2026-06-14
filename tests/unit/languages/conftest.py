from __future__ import annotations

import pytest

from src.features.languages.services.language_loader import LanguageLoader
from src.features.languages.services.language_registry import LanguageRegistry
from src.features.languages.services.languages_service import LanguagesService
from tests.helpers.languages import LANGUAGES_DIR


@pytest.fixture
def language_registry() -> LanguageRegistry:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(LANGUAGES_DIR)
    return registry


@pytest.fixture
def languages_service(language_registry: LanguageRegistry) -> LanguagesService:
    return LanguagesService(language_registry)
