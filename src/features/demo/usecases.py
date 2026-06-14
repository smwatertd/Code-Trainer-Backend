from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult
from src.features.demo.commands import GetDemoCheckCommand, SubmitDemoCheckCommand
from src.features.demo.domain.dto import DemoCheckQueuedDTO, DemoCheckResultDTO
from src.features.demo.services.demo_service import DemoService
from src.features.tasks.domain.vo.task_id import TaskId


@dataclass
class SubmitDemoCheckUseCase:
    demo_service: DemoService

    async def execute(self, command: SubmitDemoCheckCommand) -> AppResult[DemoCheckQueuedDTO]:
        task_id_result = TaskId.create(command.task_id)
        if task_id_result.is_err():
            return task_id_result  # type: ignore[return-value]
        return await self.demo_service.submit_check(command)


@dataclass
class GetDemoCheckResultUseCase:
    demo_service: DemoService

    def execute(self, command: GetDemoCheckCommand) -> AppResult[DemoCheckResultDTO]:
        return self.demo_service.get_check_result(command)
