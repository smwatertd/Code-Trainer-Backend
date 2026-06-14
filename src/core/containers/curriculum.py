from __future__ import annotations

from dependency_injector import containers, providers

from src.features.curriculum.services.collection_showcase_service import CollectionShowcaseService


class CurriculumContainer(containers.DeclarativeContainer):
    uow = providers.Dependency()
    config = providers.Dependency()

    collection_showcase_service = providers.Factory(
        CollectionShowcaseService,
        curriculum_root=config.provided.curriculum_dir,
        uow=uow,
    )
