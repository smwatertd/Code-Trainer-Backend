from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ForbiddenFailure, NotFoundFailure, RateLimitFailure
from src.core.settings import GuestSettings
from src.features.catalog.services.catalog_service import CatalogService
from src.features.demo.commands import GetDemoCheckCommand, SubmitDemoCheckCommand
from src.features.demo.domain.dto import DemoCheckQueuedDTO, DemoCheckResultDTO
from src.features.demo.services.guest_rate_limiter import GuestRateLimiter, GuestRateLimitError
from src.shared.execution.checking.flow_public_response import sanitize_public_pattern_errors
from src.shared.execution.domain.dto import JobResultDTO
from src.shared.execution.services.execution_service import ExecutionService


@dataclass
class DemoService:
    catalog_service: CatalogService
    execution_service: ExecutionService
    rate_limiter: GuestRateLimiter
    guest_settings: GuestSettings

    async def submit_check(self, command: SubmitDemoCheckCommand) -> AppResult[DemoCheckQueuedDTO]:
        if not self.guest_settings.enabled:
            return Err(NotFoundFailure("Guest mode", "disabled"))

        task_result = await self.catalog_service.get_internal_task(command.task_id)
        if task_result.is_err():
            return task_result  # type: ignore[return-value]

        task = task_result.value
        try:
            self.rate_limiter.check_submit(command.client_ip)
        except GuestRateLimitError as exc:
            return Err(RateLimitFailure(str(exc)))

        payload: dict[str, Any] = {
            "client_ip": command.client_ip,
            "guest": True,
            "task_snapshot": {
                "task_type": task.task_type,
                "payload": task.payload,
            },
        }
        if command.block_order is not None:
            payload["block_order"] = command.block_order
        if command.nodes is not None:
            payload["nodes"] = command.nodes
        if command.edges is not None:
            payload["edges"] = command.edges
        if command.flow is not None:
            payload["flow"] = command.flow

        submit_result = self.execution_service.submit(
            user_id=self.rate_limiter.guest_user_id(command.client_ip),
            language_id=command.language,
            code=command.code,
            op="guest_full_check",
            task_id=command.task_id,
            payload=payload,
        )
        if submit_result.is_err():
            return submit_result  # type: ignore[return-value]

        self.rate_limiter.on_job_queued(command.client_ip)
        queued = submit_result.value
        return Ok(DemoCheckQueuedDTO(job_id=queued.job_id, status=queued.status))

    def get_check_result(self, command: GetDemoCheckCommand) -> AppResult[DemoCheckResultDTO]:
        if not self.guest_settings.enabled:
            return Err(NotFoundFailure("Guest mode", "disabled"))

        status_result = self.execution_service.get_status(command.job_id)
        if status_result.is_err():
            return status_result  # type: ignore[return-value]

        job_status = status_result.value
        if job_status.op != "guest_full_check":
            return Err(NotFoundFailure("Job", command.job_id))

        job = self.execution_service.get_job(command.job_id)
        if not job:
            return Err(NotFoundFailure("Job", command.job_id))

        if job.payload.get("client_ip") != command.client_ip:
            return Err(ForbiddenFailure())
        if job.user_id != self.rate_limiter.guest_user_id(command.client_ip):
            return Err(ForbiddenFailure())

        result = self.execution_service.get_result(command.job_id)
        if result.is_err():
            return result  # type: ignore[return-value]

        dto = result.value
        self._release_active_if_terminal(command.client_ip, dto)
        return Ok(self._map_result(dto))

    def _release_active_if_terminal(self, client_ip: str, dto: JobResultDTO) -> None:
        if dto.status in {"SUCCESS", "FAILED", "TIMEOUT"}:
            self.rate_limiter.on_job_finished(client_ip)

    def _map_result(self, dto: JobResultDTO) -> DemoCheckResultDTO:
        if dto.status not in {"SUCCESS", "FAILED"}:
            return DemoCheckResultDTO(job_id=dto.job_id, status=dto.status)

        if dto.status == "FAILED":
            return DemoCheckResultDTO(
                job_id=dto.job_id,
                status="FAILED",
                success=False,
                errors=dto.errors,
                compiler_errors=[{"type": "EXECUTION", "text": dto.errors or "Check failed"}],
            )

        output = dto.output or {}
        return DemoCheckResultDTO(
            job_id=dto.job_id,
            status="SUCCESS",
            success=bool(output.get("success")),
            compiler_errors=output.get("compiler_errors") or [],
            linter_errors=output.get("linter_errors") or [],
            pattern_errors=sanitize_public_pattern_errors(output.get("pattern_errors") or []),
            test_results=output.get("test_results") or [],
        )
