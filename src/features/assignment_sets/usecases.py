from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult
from src.features.assignment_sets.commands import (
    AddAssignmentSetItemCommand,
    CreateAssignmentSetCommand,
    GetAssignmentSetCommand,
    ListAccessibleAssignmentSetsCommand,
    ListTeacherAssignmentSetsCommand,
    RemoveAssignmentSetItemCommand,
    UpdateAssignmentSetCommand,
)
from src.features.assignment_sets.repos.assignment_set_repo import AssignmentSetDTO
from src.features.assignment_sets.services.assignment_set_service import AssignmentSetService


@dataclass
class CreateAssignmentSetUseCase:
    service: AssignmentSetService

    async def execute(self, command: CreateAssignmentSetCommand) -> AppResult[AssignmentSetDTO]:
        return await self.service.create_set(
            teacher_id=command.teacher_id,
            name=command.name,
            description=command.description,
            visibility=command.visibility,
            group_id=command.group_id,
            deadline_at=command.deadline_at,
        )


@dataclass
class ListTeacherAssignmentSetsUseCase:
    service: AssignmentSetService

    async def execute(self, command: ListTeacherAssignmentSetsCommand) -> AppResult[list[AssignmentSetDTO]]:
        return await self.service.list_teacher_sets(
            command.teacher_id,
            include_archived=command.include_archived,
        )


@dataclass
class ListAccessibleAssignmentSetsUseCase:
    service: AssignmentSetService

    async def execute(self, command: ListAccessibleAssignmentSetsCommand) -> AppResult[list[AssignmentSetDTO]]:
        return await self.service.list_accessible_sets(user_id=command.user_id)


@dataclass
class GetAssignmentSetUseCase:
    service: AssignmentSetService

    async def execute(self, command: GetAssignmentSetCommand) -> AppResult[AssignmentSetDTO]:
        return await self.service.get_set(
            user_id=command.user_id,
            role=command.role,
            set_id=command.set_id,
        )


@dataclass
class UpdateAssignmentSetUseCase:
    service: AssignmentSetService

    async def execute(self, command: UpdateAssignmentSetCommand) -> AppResult[AssignmentSetDTO]:
        return await self.service.update_set(
            teacher_id=command.teacher_id,
            set_id=command.set_id,
            name=command.name,
            description=command.description,
            visibility=command.visibility,
            group_id=command.group_id,
            clear_group=command.clear_group,
            deadline_at=command.deadline_at,
            is_archived=command.is_archived,
        )


@dataclass
class AddAssignmentSetItemUseCase:
    service: AssignmentSetService

    async def execute(self, command: AddAssignmentSetItemCommand) -> AppResult[None]:
        return await self.service.add_item(
            teacher_id=command.teacher_id,
            set_id=command.set_id,
            task_id=command.task_id,
            sort_order=command.sort_order,
        )


@dataclass
class RemoveAssignmentSetItemUseCase:
    service: AssignmentSetService

    async def execute(self, command: RemoveAssignmentSetItemCommand) -> AppResult[None]:
        return await self.service.remove_item(
            teacher_id=command.teacher_id,
            set_id=command.set_id,
            task_id=command.task_id,
        )
