from __future__ import annotations

from dependency_injector import containers, providers

from src.core.logger import LoguruLogger
from src.features.languages.services.language_loader import LanguageLoader
from src.features.languages.services.language_registry import LanguageRegistry
from src.features.languages.services.languages_service import LanguagesService
from src.features.languages.usecases import ListLanguagesUseCase


class LanguagesContainer(containers.DeclarativeContainer):
    logger = providers.Singleton(LoguruLogger, name="languages")

    registry = providers.Singleton(LanguageRegistry)

    loader = providers.Singleton(LanguageLoader, registry=registry)

    languages_service = providers.Singleton(LanguagesService, registry=registry)

    list_languages_use_case = providers.Factory(
        ListLanguagesUseCase,
        languages_service=languages_service,
    )
