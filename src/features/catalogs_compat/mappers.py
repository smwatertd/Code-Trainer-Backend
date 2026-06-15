from __future__ import annotations

from datetime import UTC, datetime

from src.features.assignment_sets.repos.assignment_set_repo import AssignmentSetDTO
from src.features.catalog.models import TaskModel
from src.features.catalog.mappers import _summary_languages
from src.features.catalogs_compat.schemas import CatalogResponse, LegacyTaskResponse


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


def catalog_from_set(dto: AssignmentSetDTO) -> CatalogResponse:
    return CatalogResponse(
        id=dto.id,
        title=dto.name,
        description=dto.description or None,
        created_at=dto.created_at,
        task_count=len(dto.items),
        visibility=dto.visibility,
        group_id=dto.group_id,
        deadline_at=dto.deadline_at,
    )


def task_to_legacy(
    model: TaskModel,
    *,
    catalog_ids: list[int] | None = None,
) -> LegacyTaskResponse:
    payload = dict(model.payload or {})
    languages = list(_summary_languages(payload))
    ids = catalog_ids or []
    return LegacyTaskResponse(
        id=model.id,
        title=model.title,
        content=model.description,
        type_id=model.task_type,
        created_at=_utc_now(),
        difficulty=model.difficulty,
        language=languages[0] if languages else None,
        languages=languages,
        catalog_ids=ids,
        is_assigned=bool(ids),
    )
