from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.features.submissions.models import (
    SubmissionLintErrorModel,
    SubmissionModel,
    SubmissionPatternErrorModel,
    SubmissionTestResultModel,
)


class SubmissionRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: int,
        task_id: int,
        language: str,
        code: str,
        input_payload: dict | None = None,
    ) -> SubmissionModel:
        model = SubmissionModel(
            user_id=user_id,
            task_id=task_id,
            language=language,
            code=code,
            input_payload=input_payload,
            status="queued",
            success=None,
        )
        self._session.add(model)
        await self._session.flush()
        return model

    async def get_by_id(self, submission_id: int) -> SubmissionModel | None:
        stmt = (
            select(SubmissionModel)
            .where(SubmissionModel.id == submission_id)
            .options(
                selectinload(SubmissionModel.linter_errors),
                selectinload(SubmissionModel.pattern_errors),
                selectinload(SubmissionModel.test_results),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_pending(self, *, user_id: int, task_id: int) -> SubmissionModel | None:
        stmt = (
            select(SubmissionModel)
            .where(
                SubmissionModel.user_id == user_id,
                SubmissionModel.task_id == task_id,
                SubmissionModel.status.in_(("queued", "running", "pending")),
            )
            .order_by(SubmissionModel.id.desc())
            .limit(1)
            .options(
                selectinload(SubmissionModel.linter_errors),
                selectinload(SubmissionModel.pattern_errors),
                selectinload(SubmissionModel.test_results),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def clear_check_results(self, submission_id: int) -> None:
        await self._session.execute(
            delete(SubmissionLintErrorModel).where(
                SubmissionLintErrorModel.submission_id == submission_id,
            )
        )
        await self._session.execute(
            delete(SubmissionPatternErrorModel).where(
                SubmissionPatternErrorModel.submission_id == submission_id,
            )
        )
        await self._session.execute(
            delete(SubmissionTestResultModel).where(
                SubmissionTestResultModel.submission_id == submission_id,
            )
        )

    def add_lint_error(self, *, submission_id: int, error_type: str, text: str) -> None:
        self._session.add(
            SubmissionLintErrorModel(
                submission_id=submission_id,
                error_type=error_type,
                text=text,
            )
        )

    def add_pattern_error(self, *, submission_id: int, error_type: str, text: str) -> None:
        self._session.add(
            SubmissionPatternErrorModel(
                submission_id=submission_id,
                error_type=error_type,
                text=text,
            )
        )

    def add_test_result(
        self,
        *,
        submission_id: int,
        case_number: int,
        status: str,
        inputs: str,
        expected: str,
        actual: str,
        message: str,
        duration_ms: int = 0,
    ) -> None:
        self._session.add(
            SubmissionTestResultModel(
                submission_id=submission_id,
                case_number=case_number,
                status=status,
                inputs=inputs,
                expected=expected,
                actual=actual,
                message=message,
                duration_ms=duration_ms,
            )
        )

    async def list_for_user_task(
        self,
        *,
        user_id: int,
        task_id: int,
        limit: int = 20,
    ) -> list[SubmissionModel]:
        stmt = (
            select(SubmissionModel)
            .where(
                SubmissionModel.user_id == user_id,
                SubmissionModel.task_id == task_id,
                SubmissionModel.status.in_(("success", "failed")),
            )
            .order_by(SubmissionModel.id.desc())
            .limit(limit)
            .options(
                selectinload(SubmissionModel.linter_errors),
                selectinload(SubmissionModel.pattern_errors),
                selectinload(SubmissionModel.test_results),
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
