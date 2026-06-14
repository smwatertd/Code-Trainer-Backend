from __future__ import annotations

from dependency_injector import containers, providers

from src.features.groups.services.group_dashboard_service import GroupDashboardService
from src.features.groups.services.group_service import GroupService
from src.features.groups.usecases import (
    CreateGroupUseCase,
    CreateInvitationUseCase,
    GetGroupDashboardUseCase,
    JoinGroupUseCase,
    ListStudentGroupsUseCase,
    ListTeacherGroupsUseCase,
)


class GroupsContainer(containers.DeclarativeContainer):
    uow = providers.Dependency()

    group_service = providers.Factory(GroupService, uow=uow)
    group_dashboard_service = providers.Factory(GroupDashboardService, uow=uow)

    create_group_use_case = providers.Factory(CreateGroupUseCase, group_service=group_service)
    list_teacher_groups_use_case = providers.Factory(
        ListTeacherGroupsUseCase,
        group_service=group_service,
    )
    list_student_groups_use_case = providers.Factory(
        ListStudentGroupsUseCase,
        group_service=group_service,
    )
    create_invitation_use_case = providers.Factory(
        CreateInvitationUseCase,
        group_service=group_service,
    )
    join_group_use_case = providers.Factory(JoinGroupUseCase, group_service=group_service)
    get_group_dashboard_use_case = providers.Factory(
        GetGroupDashboardUseCase,
        dashboard_service=group_dashboard_service,
    )
