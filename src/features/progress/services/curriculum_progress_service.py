from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.interfaces import UnitOfWork
from src.features.progress.domain.dto import (
    LearningConceptProgressDTO,
    TaskCurriculumProgressItemDTO,
    TechnicalConceptProgressDTO,
)
from src.features.progress.models import StudentCurriculumProgressModel
from src.features.progress.repos.curriculum_progress_repo import CurriculumProgressRepo
from src.features.progress.repos.task_curriculum_link_repo import TaskCurriculumLinkRepo
from src.features.progress.services.task_progress_service import progress_status_from_row
from src.shared.database.base import utc_now


def _progress_percent(passed: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(100.0 * passed / total, 1)


@dataclass
class CurriculumProgressService:
    uow: UnitOfWork

    async def record_submission_result(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        submission_id: int,
        task_id: int,
        passed: bool,
    ) -> None:
        link_repo = TaskCurriculumLinkRepo(session)
        primary = await link_repo.get_primary_by_task_id(task_id)
        if primary is None:
            return

        repo = CurriculumProgressRepo(session)
        now = utc_now()
        row = await repo.get_by_user_and_task(user_id, task_id)
        if row is None:
            row = StudentCurriculumProgressModel(
                user_id=user_id,
                task_id=task_id,
                language=primary.language,
                learning_concept_id=primary.learning_concept_id,
                technical_concept_id=primary.technical_concept_id,
                action=primary.action,
                exercise_pattern_id=primary.exercise_pattern_id,
                attempts_count=0,
                passed_count=0,
            )
            await repo.add(row)

        row.attempts_count += 1
        row.last_submission_id = submission_id
        row.last_attempt_at = now
        row.updated_at = now
        row.last_status = "passed" if passed else "failed"

        if passed and row.passed_count == 0:
            row.passed_count = 1
            row.first_passed_at = now

    async def get_learning_concept_progress(
        self,
        *,
        user_id: int,
        language: str,
        learning_concept_id: str,
    ) -> LearningConceptProgressDTO:
        lang = language.strip().lower()
        async with self.uow():
            link_repo = TaskCurriculumLinkRepo(self.uow.session)
            links = await link_repo.list_for_learning_concept(
                language=lang,
                learning_concept_id=learning_concept_id,
            )
            task_ids = [link.task_id for link in links]
            rows = await CurriculumProgressRepo(self.uow.session).list_for_user_tasks(user_id, task_ids)
            by_task_id = {row.task_id: row for row in rows}

        passed_task_ids = {task_id for task_id, row in by_task_id.items() if row.passed_count > 0}
        total = len(task_ids)
        passed = len(passed_task_ids)

        tasks_by_tc: dict[str, list[int]] = {}
        for link in links:
            tasks_by_tc.setdefault(link.technical_concept_id, []).append(link.task_id)

        by_tc: dict[str, TechnicalConceptProgressDTO] = {}
        for tc_id, tc_task_ids in tasks_by_tc.items():
            tc_passed = sum(1 for task_id in tc_task_ids if task_id in passed_task_ids)
            by_tc[tc_id] = TechnicalConceptProgressDTO(
                technical_concept_id=tc_id,
                total_tasks=len(tc_task_ids),
                passed_tasks=tc_passed,
                progress_percent=_progress_percent(tc_passed, len(tc_task_ids)),
            )

        by_task_progress = {
            task_id: TaskCurriculumProgressItemDTO(
                task_id=task_id,
                progress_status=progress_status_from_row(by_task_id.get(task_id)),
                attempts_count=by_task_id[task_id].attempts_count if task_id in by_task_id else 0,
                passed_count=by_task_id[task_id].passed_count if task_id in by_task_id else 0,
            )
            for task_id in task_ids
        }

        return LearningConceptProgressDTO(
            language=lang,
            learning_concept_id=learning_concept_id,
            total_tasks=total,
            passed_tasks=passed,
            progress_percent=_progress_percent(passed, total),
            by_technical_concept=by_tc,
            by_task_id=by_task_progress,
        )
