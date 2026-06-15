from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.core.containers import Container
from src.core.policies.permissions import Permission
from src.features.auth.dependencies import AuthenticatedUser, require_permission
from src.features.groups.commands import (
    CreateGroupCommand,
    CreateInvitationCommand,
    GetGroupDashboardCommand,
    JoinGroupCommand,
    ListStudentGroupsCommand,
    ListTeacherGroupsCommand,
)
from src.features.groups.schemas import (
    AssignCatalogToGroupRequest,
    CreateGroupRequest,
    GenerateInvitationRequest,
    GroupAssignmentSetSummaryResponse,
    GroupDashboardResponse,
    GroupMemberResponse,
    GroupResponse,
    GroupStudentSummaryResponse,
    InvitationCodeResponse,
    JoinGroupRequest,
    StudentTaskProgressResponse,
)
from src.features.assignment_sets.commands import UpdateAssignmentSetCommand
from src.features.assignment_sets.usecases import UpdateAssignmentSetUseCase
from src.features.groups.usecases import (
    CreateGroupUseCase,
    CreateInvitationUseCase,
    GetGroupDashboardUseCase,
    JoinGroupUseCase,
    ListStudentGroupsUseCase,
    ListTeacherGroupsUseCase,
)
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc

router = APIRouter(prefix="/groups", tags=["groups"])


def _group_response(dto) -> GroupResponse:
    return GroupResponse(
        id=dto.id,
        name=dto.name,
        teacher_id=dto.teacher_id,
        created_at=dto.created_at,
        member_count=dto.member_count,
    )


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_group(
    body: CreateGroupRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_GROUPS)),
    use_case: CreateGroupUseCase = Depends(Provide[Container.groups.create_group_use_case]),
) -> GroupResponse:
    result = await use_case.execute(
        CreateGroupCommand(teacher_id=current_user.user_id, name=body.name),
    )
    return _group_response(unwrap_ok_or_http_exc(result))


@router.get("/mine", response_model=list[GroupResponse])
@inject
async def list_teacher_groups(
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_GROUPS)),
    use_case: ListTeacherGroupsUseCase = Depends(Provide[Container.groups.list_teacher_groups_use_case]),
) -> list[GroupResponse]:
    result = await use_case.execute(ListTeacherGroupsCommand(teacher_id=current_user.user_id))
    return [_group_response(item) for item in unwrap_ok_or_http_exc(result)]


@router.get("/joined", response_model=list[GroupResponse])
@inject
async def list_joined_groups(
    current_user: AuthenticatedUser = Depends(require_permission(Permission.JOIN_GROUPS)),
    use_case: ListStudentGroupsUseCase = Depends(Provide[Container.groups.list_student_groups_use_case]),
) -> list[GroupResponse]:
    result = await use_case.execute(ListStudentGroupsCommand(student_id=current_user.user_id))
    return [_group_response(item) for item in unwrap_ok_or_http_exc(result)]


@router.post("/join", response_model=GroupResponse)
@inject
async def join_group(
    body: JoinGroupRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.JOIN_GROUPS)),
    use_case: JoinGroupUseCase = Depends(Provide[Container.groups.join_group_use_case]),
) -> GroupResponse:
    result = await use_case.execute(
        JoinGroupCommand(student_id=current_user.user_id, code=body.code),
    )
    return _group_response(unwrap_ok_or_http_exc(result))


@router.post("/{group_id}/invitations", response_model=InvitationCodeResponse)
@inject
async def create_group_invitation(
    group_id: int,
    body: GenerateInvitationRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_GROUPS)),
    use_case: CreateInvitationUseCase = Depends(Provide[Container.groups.create_invitation_use_case]),
) -> InvitationCodeResponse:
    result = await use_case.execute(
        CreateInvitationCommand(
            teacher_id=current_user.user_id,
            group_id=group_id,
            max_uses=body.max_uses,
            expires_in_days=body.expires_in_days,
        ),
    )
    dto = unwrap_ok_or_http_exc(result)
    return InvitationCodeResponse(
        id=dto.id,
        code=dto.code,
        group_id=dto.group_id,
        max_uses=dto.max_uses,
        use_count=dto.use_count,
        expires_at=dto.expires_at,
        is_active=dto.is_active,
    )


@router.post("/{group_id}/catalogs", status_code=status.HTTP_200_OK)
@inject
async def assign_group_catalog(
    group_id: int,
    body: AssignCatalogToGroupRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_GROUPS)),
    use_case: UpdateAssignmentSetUseCase = Depends(
        Provide[Container.assignment_sets.update_assignment_set_use_case],
    ),
) -> dict[str, int | None]:
    dto = unwrap_ok_or_http_exc(
        await use_case.execute(
            UpdateAssignmentSetCommand(
                teacher_id=current_user.user_id,
                set_id=body.catalog_id,
                group_id=group_id,
                deadline_at=body.deadline_at,
            ),
        ),
    )
    return {"catalog_id": dto.id, "group_id": dto.group_id}


@router.get("/{group_id}/dashboard", response_model=GroupDashboardResponse)
@inject
async def get_group_dashboard(
    group_id: int,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_STUDENT_RESULTS)),
    use_case: GetGroupDashboardUseCase = Depends(Provide[Container.groups.get_group_dashboard_use_case]),
) -> GroupDashboardResponse:
    result = await use_case.execute(
        GetGroupDashboardCommand(
            teacher_id=current_user.user_id,
            group_id=group_id,
            viewer_role=current_user.role,
        ),
    )
    dashboard = unwrap_ok_or_http_exc(result)
    return GroupDashboardResponse(
        group=_group_response(dashboard.group),
        members=[
            GroupMemberResponse(id=member.id, name=member.name, email=member.email) for member in dashboard.members
        ],
        assignment_sets=[
            GroupAssignmentSetSummaryResponse(
                id=item.id,
                name=item.name,
                task_count=item.task_count,
                deadline_at=item.deadline_at,
            )
            for item in dashboard.assignment_sets
        ],
        student_summaries=[
            GroupStudentSummaryResponse(
                student_id=item.student_id,
                student_name=item.student_name,
                solved_count=item.solved_count,
                total_tasks=item.total_tasks,
                progress_percent=item.progress_percent,
            )
            for item in dashboard.student_summaries
        ],
        task_progress=[
            StudentTaskProgressResponse(
                student_id=item.student_id,
                task_id=item.task_id,
                progress_status=item.progress_status,
                attempts_count=item.attempts_count,
            )
            for item in dashboard.task_progress
        ],
    )
