from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult
from src.features.groups.commands import (
    CreateGroupCommand,
    CreateInvitationCommand,
    GetGroupDashboardCommand,
    JoinGroupCommand,
    ListStudentGroupsCommand,
    ListTeacherGroupsCommand,
)
from src.features.groups.repos.group_repo import GroupDTO, InvitationCodeDTO
from src.features.groups.services.group_dashboard_service import GroupDashboardDTO, GroupDashboardService
from src.features.groups.services.group_service import GroupService


@dataclass
class CreateGroupUseCase:
    group_service: GroupService

    async def execute(self, command: CreateGroupCommand) -> AppResult[GroupDTO]:
        return await self.group_service.create_group(
            teacher_id=command.teacher_id,
            name=command.name,
        )


@dataclass
class ListTeacherGroupsUseCase:
    group_service: GroupService

    async def execute(self, command: ListTeacherGroupsCommand) -> AppResult[list[GroupDTO]]:
        return await self.group_service.list_teacher_groups(command.teacher_id)


@dataclass
class ListStudentGroupsUseCase:
    group_service: GroupService

    async def execute(self, command: ListStudentGroupsCommand) -> AppResult[list[GroupDTO]]:
        return await self.group_service.list_student_groups(command.student_id)


@dataclass
class CreateInvitationUseCase:
    group_service: GroupService

    async def execute(self, command: CreateInvitationCommand) -> AppResult[InvitationCodeDTO]:
        return await self.group_service.create_invitation(
            teacher_id=command.teacher_id,
            group_id=command.group_id,
            max_uses=command.max_uses,
            expires_in_days=command.expires_in_days,
        )


@dataclass
class JoinGroupUseCase:
    group_service: GroupService

    async def execute(self, command: JoinGroupCommand) -> AppResult[GroupDTO]:
        return await self.group_service.join_by_code(
            student_id=command.student_id,
            code=command.code,
        )


@dataclass
class GetGroupDashboardUseCase:
    dashboard_service: GroupDashboardService

    async def execute(self, command: GetGroupDashboardCommand) -> AppResult[GroupDashboardDTO]:
        return await self.dashboard_service.get_dashboard(
            teacher_id=command.teacher_id,
            group_id=command.group_id,
            viewer_role=command.viewer_role,
        )
