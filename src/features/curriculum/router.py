from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.containers import Container
from src.features.auth.dependencies import get_optional_authenticated_user, AuthenticatedUser
from src.features.curriculum.schemas import CollectionShowcaseResponse, LanguageTrackResponse
from src.features.curriculum.services.collection_showcase_service import CollectionShowcaseService
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


@router.get("/{language}/collections", response_model=LanguageTrackResponse)
@inject
async def get_language_collections(
    language: str,
    current_user: AuthenticatedUser | None = Depends(get_optional_authenticated_user),
    service: CollectionShowcaseService = Depends(
        Provide[Container.curriculum.collection_showcase_service],
    ),
) -> LanguageTrackResponse:
    user_id = current_user.user_id if current_user else None
    payload = unwrap_ok_or_http_exc(await service.build_collections_view(language, user_id))
    return LanguageTrackResponse(**payload)


@router.get(
    "/{language}/collections/{learning_concept_id}",
    response_model=CollectionShowcaseResponse,
)
@inject
async def get_collection_showcase(
    language: str,
    learning_concept_id: str,
    current_user: AuthenticatedUser | None = Depends(get_optional_authenticated_user),
    service: CollectionShowcaseService = Depends(
        Provide[Container.curriculum.collection_showcase_service],
    ),
) -> CollectionShowcaseResponse:
    user_id = current_user.user_id if current_user else None
    payload = unwrap_ok_or_http_exc(
        await service.build_collection_showcase(language, learning_concept_id, user_id),
    )
    return CollectionShowcaseResponse(**payload)
