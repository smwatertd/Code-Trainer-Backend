from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sqlalchemy.exc import IntegrityError

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import NotFoundFailure, ValidationFailure
from src.core.interfaces import UnitOfWork
from src.features.catalog.repos.task_repo import TaskRepo
from src.features.progress.models import TaskCurriculumLinkModel
from src.features.progress.repos.task_curriculum_link_repo import TaskCurriculumLinkRepo
from src.shared.curriculum.exceptions import CurriculumLinkValidationError
from src.shared.curriculum.link_validator import CurriculumLinkMetadata, validate_task_curriculum_link_metadata


@dataclass(frozen=True)
class TaskCurriculumLinkDTO:
    id: int
    task_id: int
    language: str
    learning_concept_id: str
    technical_concept_id: str
    exercise_pattern_id: str
    action: str
    is_primary: bool
    created_at: datetime | None


@dataclass(frozen=True)
class TaskCurriculumMetadataDTO:
    task_id: int
    has_curriculum_link: bool
    primary_link: TaskCurriculumLinkDTO | None
    links: tuple[TaskCurriculumLinkDTO, ...]


@dataclass
class TaskCurriculumLinkService:
    uow: UnitOfWork
    curriculum_root: Path

    async def validate_link_metadata(
        self,
        *,
        language: str,
        technical_concept_id: str,
        exercise_pattern_id: str,
    ) -> AppResult[CurriculumLinkMetadata]:
        try:
            metadata = validate_task_curriculum_link_metadata(
                self.curriculum_root,
                language=language,
                technical_concept_id=technical_concept_id,
                exercise_pattern_id=exercise_pattern_id,
            )
        except CurriculumLinkValidationError as exc:
            return Err(ValidationFailure(str(exc)))
        return Ok(metadata)

    async def get_task_metadata(self, task_id: int) -> AppResult[TaskCurriculumMetadataDTO]:
        async with self.uow() as uow:
            if await TaskRepo(uow.session).get_by_id(task_id) is None:
                return Err(NotFoundFailure("Task", str(task_id)))

            repo = TaskCurriculumLinkRepo(uow.session)
            links = await repo.list_by_task_id(task_id)
            dto_links = tuple(_to_link_dto(link) for link in links)
            primary = next((item for item in dto_links if item.is_primary), None)
            return Ok(
                TaskCurriculumMetadataDTO(
                    task_id=task_id,
                    has_curriculum_link=bool(dto_links),
                    primary_link=primary,
                    links=dto_links,
                ),
            )

    async def create_link(
        self,
        *,
        task_id: int,
        language: str,
        technical_concept_id: str,
        exercise_pattern_id: str,
        is_primary: bool = False,
    ) -> AppResult[TaskCurriculumLinkDTO]:
        validation = await self.validate_link_metadata(
            language=language,
            technical_concept_id=technical_concept_id,
            exercise_pattern_id=exercise_pattern_id,
        )
        if validation.is_err():
            return validation  # type: ignore[return-value]
        metadata = validation.value

        async with self.uow(autocommit=True) as uow:
            if await TaskRepo(uow.session).get_by_id(task_id) is None:
                return Err(NotFoundFailure("Task", str(task_id)))

            repo = TaskCurriculumLinkRepo(uow.session)
            existing = await repo.get_by_task_and_pattern(
                task_id,
                metadata.exercise_pattern_id,
                language=metadata.language,
            )
            if existing is not None:
                return Err(
                    ValidationFailure(
                        f"Task {task_id} is already linked to pattern {metadata.exercise_pattern_id}",
                    ),
                )

            if is_primary:
                await repo.clear_primary_for_task(task_id, metadata.language)

            row = TaskCurriculumLinkModel(
                task_id=task_id,
                language=metadata.language,
                learning_concept_id=metadata.learning_concept_id,
                technical_concept_id=metadata.technical_concept_id,
                exercise_pattern_id=metadata.exercise_pattern_id,
                action=metadata.action,
                is_primary=is_primary,
            )
            try:
                created = await repo.add(row)
            except IntegrityError:
                return Err(
                    ValidationFailure(
                        "Task already linked to this exercise pattern or primary link conflict",
                    ),
                )
            return Ok(_to_link_dto(created))

    async def update_link(
        self,
        *,
        task_id: int,
        link_id: int,
        language: str | None = None,
        technical_concept_id: str | None = None,
        exercise_pattern_id: str | None = None,
        is_primary: bool | None = None,
    ) -> AppResult[TaskCurriculumLinkDTO]:
        async with self.uow(autocommit=True) as uow:
            if await TaskRepo(uow.session).get_by_id(task_id) is None:
                return Err(NotFoundFailure("Task", str(task_id)))

            repo = TaskCurriculumLinkRepo(uow.session)
            existing = await repo.get_by_id(link_id)
            if existing is None or existing.task_id != task_id:
                return Err(NotFoundFailure("Curriculum link", str(link_id)))

            next_language = language or existing.language
            next_tc = technical_concept_id or existing.technical_concept_id
            next_pattern = exercise_pattern_id or existing.exercise_pattern_id

            if technical_concept_id is not None or exercise_pattern_id is not None or language is not None:
                validation = await self.validate_link_metadata(
                    language=next_language,
                    technical_concept_id=next_tc,
                    exercise_pattern_id=next_pattern,
                )
                if validation.is_err():
                    return validation  # type: ignore[return-value]
                metadata = validation.value
                if exercise_pattern_id and exercise_pattern_id != existing.exercise_pattern_id:
                    duplicate = await repo.get_by_task_and_pattern(
                        task_id,
                        next_pattern,
                        language=metadata.language,
                    )
                    if duplicate is not None and duplicate.id != link_id:
                        return Err(
                            ValidationFailure(
                                f"Task {task_id} is already linked to pattern {next_pattern}",
                            ),
                        )
                if is_primary is True:
                    await repo.clear_primary_for_task(task_id, metadata.language)
                try:
                    updated = await repo.update(
                        link_id,
                        is_primary=is_primary,
                        language=metadata.language,
                        learning_concept_id=metadata.learning_concept_id,
                        technical_concept_id=metadata.technical_concept_id,
                        exercise_pattern_id=metadata.exercise_pattern_id,
                        action=metadata.action,
                    )
                except IntegrityError:
                    return Err(
                        ValidationFailure(
                            "Task already linked to this exercise pattern or primary link conflict",
                        ),
                    )
            else:
                if is_primary is True:
                    await repo.clear_primary_for_task(task_id, next_language)
                try:
                    updated = await repo.update(link_id, is_primary=is_primary)
                except IntegrityError:
                    return Err(
                        ValidationFailure(
                            "Task already linked to this exercise pattern or primary link conflict",
                        ),
                    )

            if updated is None:
                return Err(NotFoundFailure("Curriculum link", str(link_id)))
            return Ok(_to_link_dto(updated))

    async def delete_link(self, *, task_id: int, link_id: int) -> AppResult[None]:
        async with self.uow(autocommit=True) as uow:
            if await TaskRepo(uow.session).get_by_id(task_id) is None:
                return Err(NotFoundFailure("Task", str(task_id)))

            repo = TaskCurriculumLinkRepo(uow.session)
            existing = await repo.get_by_id(link_id)
            if existing is None or existing.task_id != task_id:
                return Err(NotFoundFailure("Curriculum link", str(link_id)))

            await repo.delete(link_id)
            return Ok(None)


def _to_link_dto(row: TaskCurriculumLinkModel) -> TaskCurriculumLinkDTO:
    return TaskCurriculumLinkDTO(
        id=row.id,
        task_id=row.task_id,
        language=row.language,
        learning_concept_id=row.learning_concept_id,
        technical_concept_id=row.technical_concept_id,
        exercise_pattern_id=row.exercise_pattern_id,
        action=row.action,
        is_primary=row.is_primary,
        created_at=row.created_at,
    )
