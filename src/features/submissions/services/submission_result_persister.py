from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.core.interfaces import UnitOfWork
from src.features.progress.services.curriculum_progress_service import CurriculumProgressService
from src.features.progress.services.task_progress_service import TaskProgressService
from src.features.submissions.models import SubmissionModel
from src.features.submissions.repos.submission_repo import SubmissionRepo
from src.shared.execution.checking.student_execution_errors import redact_infrastructure_error

_TERMINAL_STATUSES = frozenset({"success", "failed"})


@dataclass
class SubmissionResultPersister:
    uow: UnitOfWork
    progress_service: TaskProgressService | None = None
    curriculum_progress_service: CurriculumProgressService | None = None

    async def mark_running(self, submission_id: int) -> None:
        async with self.uow(autocommit=True):
            await self._update_status(submission_id, status="running")

    async def mark_failed(self, submission_id: int, message: str) -> None:
        async with self.uow(autocommit=True):
            repo = SubmissionRepo(self.uow.session)
            model = await repo.get_by_id(submission_id)
            if model is None or model.status in _TERMINAL_STATUSES:
                return
            await repo.clear_check_results(submission_id)
            repo.add_lint_error(
                submission_id=submission_id,
                error_type="INTERNAL_ERROR",
                text=redact_infrastructure_error(message),
            )
            model.status = "failed"
            model.success = False
            await self._record_progress(model, submission_id=submission_id, passed=False)

    async def persist_check_output(self, submission_id: int, output: dict[str, Any]) -> None:
        async with self.uow(autocommit=True):
            repo = SubmissionRepo(self.uow.session)
            model = await repo.get_by_id(submission_id)
            if model is None:
                return

            success = bool(output.get("success"))
            model.status = "success" if success else "failed"
            model.success = success
            model.duration_ms = self._total_duration_ms(output)

            await repo.clear_check_results(submission_id)
            self._store_output(repo, submission_id, output)
            await self._record_progress(model, submission_id=submission_id, passed=success)

    async def _record_progress(
        self,
        model: SubmissionModel,
        *,
        submission_id: int,
        passed: bool,
    ) -> None:
        if self.progress_service is None or model.user_id is None:
            return
        await self.progress_service.record_submission_result(
            self.uow.session,
            user_id=model.user_id,
            submission_id=submission_id,
            task_id=model.task_id,
            passed=passed,
        )
        if self.curriculum_progress_service is None:
            return
        await self.curriculum_progress_service.record_submission_result(
            self.uow.session,
            user_id=model.user_id,
            submission_id=submission_id,
            task_id=model.task_id,
            language=model.language,
            passed=passed,
        )

    async def _update_status(self, submission_id: int, *, status: str) -> None:
        repo = SubmissionRepo(self.uow.session)
        model = await repo.get_by_id(submission_id)
        if model is None or model.status in _TERMINAL_STATUSES:
            return
        model.status = status

    def _store_output(self, repo: SubmissionRepo, submission_id: int, output: dict[str, Any]) -> None:
        for error in output.get("compiler_errors") or []:
            if isinstance(error, dict):
                repo.add_lint_error(
                    submission_id=submission_id,
                    error_type=str(error.get("type") or "COMPILER"),
                    text=str(error.get("text") or ""),
                )

        for error in output.get("linter_errors") or []:
            if isinstance(error, dict):
                repo.add_lint_error(
                    submission_id=submission_id,
                    error_type=str(error.get("type") or "LINTER"),
                    text=str(error.get("text") or ""),
                )

        for error in output.get("pattern_errors") or []:
            if isinstance(error, dict):
                repo.add_pattern_error(
                    submission_id=submission_id,
                    error_type=str(error.get("type") or "PATTERN"),
                    text=str(error.get("text") or ""),
                )

        for test in output.get("test_results") or []:
            if isinstance(test, dict):
                repo.add_test_result(
                    submission_id=submission_id,
                    case_number=int(test.get("case") or 0),
                    status=str(test.get("status") or "ERROR"),
                    inputs=str(test.get("inputs") or ""),
                    expected=str(test.get("expected") or ""),
                    actual=str(test.get("actual") or ""),
                    message=str(test.get("message") or ""),
                    duration_ms=int(test.get("duration_ms") or 0),
                )

    @staticmethod
    def _total_duration_ms(output: dict[str, Any]) -> int:
        total = 0
        for test in output.get("test_results") or []:
            if isinstance(test, dict):
                total += int(test.get("duration_ms") or 0)
        return total
