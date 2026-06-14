from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult
from src.features.submissions.commands import (
    AbandonSubmissionCommand,
    GetLatestPendingSubmissionCommand,
    GetSubmissionCommand,
    ListSubmissionHistoryCommand,
    SubmitSubmissionCommand,
)
from src.features.submissions.domain.dto import (
    SubmissionAbandonedDTO,
    SubmissionDetailDTO,
    SubmissionHistoryItemDTO,
    SubmissionQueuedDTO,
)
from src.features.submissions.services.submissions_service import SubmissionsService


@dataclass
class GetSubmissionUseCase:
    submissions_service: SubmissionsService

    async def execute(self, command: GetSubmissionCommand) -> AppResult[SubmissionDetailDTO]:
        return await self.submissions_service.get_submission(
            submission_id=command.submission_id,
            user_id=command.user_id,
        )


@dataclass
class GetLatestPendingSubmissionUseCase:
    submissions_service: SubmissionsService

    async def execute(
        self,
        command: GetLatestPendingSubmissionCommand,
    ) -> AppResult[SubmissionDetailDTO | None]:
        return await self.submissions_service.get_latest_pending(
            user_id=command.user_id,
            task_id=command.task_id,
        )


@dataclass
class SubmitSubmissionUseCase:
    submissions_service: SubmissionsService

    async def execute(self, command: SubmitSubmissionCommand) -> AppResult[SubmissionQueuedDTO]:
        return await self.submissions_service.submit(
            user_id=command.user_id,
            task_id=command.task_id,
            language=command.language,
            code=command.code,
            block_order=command.block_order,
            nodes=command.nodes,
            edges=command.edges,
            flow=command.flow,
        )


@dataclass
class ListSubmissionHistoryUseCase:
    submissions_service: SubmissionsService

    async def execute(self, command: ListSubmissionHistoryCommand) -> AppResult[list[SubmissionHistoryItemDTO]]:
        return await self.submissions_service.list_history(
            user_id=command.user_id,
            task_id=command.task_id,
            limit=command.limit,
        )


@dataclass
class AbandonSubmissionUseCase:
    submissions_service: SubmissionsService

    async def execute(self, command: AbandonSubmissionCommand) -> AppResult[SubmissionAbandonedDTO]:
        return await self.submissions_service.abandon(
            submission_id=command.submission_id,
            user_id=command.user_id,
        )
