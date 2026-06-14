from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.containers import Container
from src.features.languages.schemas import LanguageResponse
from src.features.languages.usecases import ListLanguagesUseCase
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc

router = APIRouter(prefix="/languages", tags=["languages"])


@router.get("", response_model=list[LanguageResponse])
@inject
async def list_languages(
    use_case: ListLanguagesUseCase = Depends(Provide[Container.languages.list_languages_use_case]),
) -> list[LanguageResponse]:
    result = await use_case.execute()
    items = unwrap_ok_or_http_exc(result)
    return [LanguageResponse(**item.__dict__) for item in items]
