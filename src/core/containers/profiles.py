from __future__ import annotations

from dependency_injector import containers, providers

from src.features.profiles.services.profile_service import ProfileService


class ProfilesContainer(containers.DeclarativeContainer):
    uow = providers.Dependency()

    profile_service = providers.Factory(ProfileService, uow=uow)
