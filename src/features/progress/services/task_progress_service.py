from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.interfaces import UnitOfWork
from src.features.progress.domain.dto import TaskProgressDTO
from src.features.progress.models import TaskProgressModel
from src.features.progress.repos.task_progress_repo import TaskProgressRepo
from src.shared.database.base import utc_now

PROGRESS_STATUS_NOT_STARTED = "not_started"
PROGRESS_STATUS_FAILED = "failed"
PROGRESS_STATUS_PASSED = "passed"


def progress_status_from_row(row: TaskProgressModel | None) -> str:
    if row is None:
        return PROGRESS_STATUS_NOT_STARTED
    if row.passed_count > 0:
        return PROGRESS_STATUS_PASSED
    if row.attempts_count > 0:
        return PROGRESS_STATUS_FAILED
    return PROGRESS_STATUS_NOT_STARTED


@dataclass
class TaskProgressService:
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
        repo = TaskProgressRepo(session)
        now = utc_now()
        row = await repo.get_by_user_and_task(user_id, task_id)
        if row is None:
            row = TaskProgressModel(
                user_id=user_id,
                task_id=task_id,
                attempts_count=0,
                passed_count=0,
            )
            await repo.add(row)

        row.attempts_count += 1
        row.last_submission_id = submission_id
        row.last_attempt_at = now
        row.updated_at = now
        row.last_status = "passed" if passed else "failed"

        if passed:
            row.passed_count += 1
            if row.first_passed_at is None:
                row.first_passed_at = now

    async def get_progress_for_task(self, user_id: int, task_id: int) -> TaskProgressDTO:
        async with self.uow():
            repo = TaskProgressRepo(self.uow.session)
            row = await repo.get_by_user_and_task(user_id, task_id)
            return self._to_dto(task_id, row)

    @staticmethod
    def _to_dto(task_id: int, row: TaskProgressModel | None) -> TaskProgressDTO:
        if row is None:
            return TaskProgressDTO(
                task_id=task_id,
                progress_status=PROGRESS_STATUS_NOT_STARTED,
                attempts_count=0,
                passed_count=0,
                failed_count=0,
            )
        return TaskProgressDTO(
            task_id=task_id,
            progress_status=progress_status_from_row(row),
            attempts_count=row.attempts_count,
            passed_count=row.passed_count,
            failed_count=max(row.attempts_count - row.passed_count, 0),
            last_status=row.last_status,
            last_submission_id=row.last_submission_id,
            last_attempt_at=row.last_attempt_at,
            first_passed_at=row.first_passed_at,
        )
