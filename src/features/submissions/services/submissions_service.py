from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ForbiddenFailure, NotFoundFailure, RateLimitFailure
from src.core.interfaces import UnitOfWork
from src.core.settings import ExecutionSettings
from src.features.catalog.services.catalog_service import CatalogService
from src.features.submissions.domain.dto import (
    SubmissionAbandonedDTO,
    SubmissionDetailDTO,
    SubmissionHistoryItemDTO,
    SubmissionQueuedDTO,
)
from src.features.submissions.mappers import to_detail
from src.features.submissions.repos.submission_repo import SubmissionRepo
from src.features.submissions.services.submission_result_persister import SubmissionResultPersister
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.services.execution_rate_limiter import (
    ExecutionRateLimiterProtocol,
    ExecutionRateLimitError,
)
from src.shared.execution.services.execution_service import ExecutionService


@dataclass
class SubmissionsService:
    uow: UnitOfWork
    catalog_service: CatalogService
    execution_service: ExecutionService
    result_persister: SubmissionResultPersister
    execution_settings: ExecutionSettings
    execution_rate_limiter: ExecutionRateLimiterProtocol

    async def submit(
        self,
        *,
        user_id: int,
        task_id: int,
        language: str,
        code: str,
        block_order: list[int] | None = None,
        nodes: list[dict[str, Any]] | None = None,
        edges: list[dict[str, Any]] | None = None,
        flow: list[dict[str, Any]] | None = None,
    ) -> AppResult[SubmissionQueuedDTO]:
        task_result = await self.catalog_service.get_internal_task(task_id)
        if task_result.is_err():
            return task_result  # type: ignore[return-value]

        task = task_result.value
        submission_id: int | None = None
        user_key = str(user_id)
        input_payload: dict[str, Any] = {}
        if block_order is not None:
            input_payload["block_order"] = block_order
        if nodes is not None:
            input_payload["nodes"] = nodes
        if edges is not None:
            input_payload["edges"] = edges
        if flow is not None:
            input_payload["flow"] = flow

        try:
            try:
                self.execution_rate_limiter.check_submit(
                    user_key,
                    queue_depth=self.execution_service.queue_depth(),
                )
            except ExecutionRateLimitError as exc:
                return Err(RateLimitFailure(str(exc)))

            async with self.uow(autocommit=True):
                submission = await SubmissionRepo(self.uow.session).create(
                    user_id=user_id,
                    task_id=task_id,
                    language=language,
                    code=code,
                    input_payload=input_payload or None,
                )
                submission_id = submission.id

            payload: dict[str, Any] = {
                "submission_id": submission_id,
                "persist": True,
                "task_snapshot": {
                    "task_type": task.task_type,
                    "payload": task.payload,
                },
            }
            if block_order is not None:
                payload["block_order"] = block_order
            if nodes is not None:
                payload["nodes"] = nodes
            if edges is not None:
                payload["edges"] = edges
            if flow is not None:
                payload["flow"] = flow

            submit_result = self.execution_service.submit(
                user_id=str(user_id),
                language_id=language,
                code=code,
                op="process_submission",
                task_id=task_id,
                payload=payload,
            )
            if submit_result.is_err():
                await self.result_persister.mark_failed(submission_id, "Failed to enqueue submission check")
                return submit_result  # type: ignore[return-value]

            self.execution_rate_limiter.on_job_queued(user_key)

            if not self.execution_settings.use_redis_store:
                await self._finalize_processed_submission(
                    submission_id=submission_id,
                    job_id=submit_result.value.job_id,
                )
                self.execution_rate_limiter.on_job_finished(user_key)

            async with self.uow(autocommit=False):
                model = await SubmissionRepo(self.uow.session).get_by_id(submission_id)
                status = model.status if model is not None else "queued"

            return Ok(SubmissionQueuedDTO(id=submission_id, status=status))
        except Exception as exc:
            if submission_id is not None:
                await self.result_persister.mark_failed(submission_id, str(exc))
            raise

    async def get_submission(self, *, submission_id: int, user_id: int) -> AppResult[SubmissionDetailDTO]:
        async with self.uow(autocommit=False):
            model = await SubmissionRepo(self.uow.session).get_by_id(submission_id)
            if model is None:
                return Err(NotFoundFailure("Submission", str(submission_id)))
            if model.user_id != user_id:
                return Err(ForbiddenFailure())
            return Ok(to_detail(model))

    async def list_history(
        self,
        *,
        user_id: int,
        task_id: int,
        limit: int = 20,
    ) -> AppResult[list[SubmissionHistoryItemDTO]]:
        from src.features.submissions.mappers import to_history_item

        async with self.uow(autocommit=False):
            models = await SubmissionRepo(self.uow.session).list_for_user_task(
                user_id=user_id,
                task_id=task_id,
                limit=limit,
            )
            return Ok([to_history_item(model) for model in models])

    async def abandon(
        self,
        *,
        submission_id: int,
        user_id: int,
    ) -> AppResult[SubmissionAbandonedDTO]:
        async with self.uow(autocommit=True):
            model = await SubmissionRepo(self.uow.session).get_by_id(submission_id)
            if model is None:
                return Err(NotFoundFailure("Submission", str(submission_id)))
            if model.user_id != user_id:
                return Err(ForbiddenFailure())
            if model.status not in {"queued", "running"}:
                return Ok(SubmissionAbandonedDTO(released=False, status=model.status))

            model.status = "failed"
            model.success = False

        self.execution_rate_limiter.on_job_finished(str(user_id))
        return Ok(SubmissionAbandonedDTO(released=True, status="failed"))

    async def get_latest_pending(
        self,
        *,
        user_id: int,
        task_id: int,
    ) -> AppResult[SubmissionDetailDTO | None]:
        async with self.uow(autocommit=False):
            model = await SubmissionRepo(self.uow.session).get_latest_pending(
                user_id=user_id,
                task_id=task_id,
            )
            if model is None:
                return Ok(None)
            return Ok(to_detail(model))

    async def _finalize_processed_submission(self, *, submission_id: int, job_id: str) -> None:
        job = self.execution_service.get_job(job_id)
        if job is None:
            await self.result_persister.mark_failed(submission_id, "Submission job not found")
            return

        if not job.status.is_terminal():
            return

        stored = self.execution_service.get_result(job_id)
        if job.status == JobStatus.FAILED:
            error = None
            if stored.is_ok() and stored.value.errors:
                error = stored.value.errors
            await self.result_persister.mark_failed(submission_id, error or "Submission check failed")
            return

        output: dict[str, Any] = {}
        if stored.is_ok() and isinstance(stored.value.output, dict):
            output = stored.value.output
        await self.result_persister.persist_check_output(submission_id, output)
