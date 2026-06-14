from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.core.containers import Container
from src.core.policies.permissions import Permission
from src.features.assignment_sets.commands import (
    AddAssignmentSetItemCommand,
    CreateAssignmentSetCommand,
    GetAssignmentSetCommand,
    ListAccessibleAssignmentSetsCommand,
    ListTeacherAssignmentSetsCommand,
    RemoveAssignmentSetItemCommand,
    UpdateAssignmentSetCommand,
)
from src.features.assignment_sets.schemas import (
    AddAssignmentSetItemRequest,
    AssignmentSetItemResponse,
    AssignmentSetResponse,
    CreateAssignmentSetRequest,
    UpdateAssignmentSetRequest,
)
from src.features.assignment_sets.usecases import (
    AddAssignmentSetItemUseCase,
    CreateAssignmentSetUseCase,
    GetAssignmentSetUseCase,
    ListAccessibleAssignmentSetsUseCase,
    ListTeacherAssignmentSetsUseCase,
    RemoveAssignmentSetItemUseCase,
    UpdateAssignmentSetUseCase,
)
from src.features.auth.dependencies import AuthenticatedUser, require_permission
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc

router = APIRouter(prefix="/assignment-sets", tags=["assignment-sets"])


def _to_response(dto) -> AssignmentSetResponse:
    return AssignmentSetResponse(
        id=dto.id,
        name=dto.name,
        description=dto.description,
        teacher_id=dto.teacher_id,
        visibility=dto.visibility,
        group_id=dto.group_id,
        is_archived=dto.is_archived,
        created_at=dto.created_at,
        deadline_at=dto.deadline_at,
        items=[AssignmentSetItemResponse(task_id=item.task_id, sort_order=item.sort_order) for item in dto.items],
    )


@router.post("", response_model=AssignmentSetResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_assignment_set(
    body: CreateAssignmentSetRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: CreateAssignmentSetUseCase = Depends(
        Provide[Container.assignment_sets.create_assignment_set_use_case],
    ),
) -> AssignmentSetResponse:
    result = await use_case.execute(
        CreateAssignmentSetCommand(
            teacher_id=current_user.user_id,
            name=body.name,
            description=body.description,
            visibility=body.visibility,
            group_id=body.group_id,
            deadline_at=body.deadline_at,
        ),
    )
    return _to_response(unwrap_ok_or_http_exc(result))


@router.get("", response_model=list[AssignmentSetResponse])
@inject
async def list_accessible_assignment_sets(
    current_user: AuthenticatedUser = Depends(require_permission(Permission.SOLVE_ASSIGNMENTS)),
    use_case: ListAccessibleAssignmentSetsUseCase = Depends(
        Provide[Container.assignment_sets.list_accessible_assignment_sets_use_case],
    ),
) -> list[AssignmentSetResponse]:
    result = await use_case.execute(ListAccessibleAssignmentSetsCommand(user_id=current_user.user_id))
    return [_to_response(item) for item in unwrap_ok_or_http_exc(result)]


@router.get("/mine", response_model=list[AssignmentSetResponse])
@inject
async def list_teacher_assignment_sets(
    include_archived: bool = False,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: ListTeacherAssignmentSetsUseCase = Depends(
        Provide[Container.assignment_sets.list_teacher_assignment_sets_use_case],
    ),
) -> list[AssignmentSetResponse]:
    result = await use_case.execute(
        ListTeacherAssignmentSetsCommand(
            teacher_id=current_user.user_id,
            include_archived=include_archived,
        ),
    )
    return [_to_response(item) for item in unwrap_ok_or_http_exc(result)]


@router.get("/{set_id}", response_model=AssignmentSetResponse)
@inject
async def get_assignment_set(
    set_id: int,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.SOLVE_ASSIGNMENTS)),
    use_case: GetAssignmentSetUseCase = Depends(
        Provide[Container.assignment_sets.get_assignment_set_use_case],
    ),
) -> AssignmentSetResponse:
    result = await use_case.execute(
        GetAssignmentSetCommand(
            user_id=current_user.user_id,
            role=current_user.role,
            set_id=set_id,
        ),
    )
    return _to_response(unwrap_ok_or_http_exc(result))


@router.patch("/{set_id}", response_model=AssignmentSetResponse)
@inject
async def update_assignment_set(
    set_id: int,
    body: UpdateAssignmentSetRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: UpdateAssignmentSetUseCase = Depends(
        Provide[Container.assignment_sets.update_assignment_set_use_case],
    ),
) -> AssignmentSetResponse:
    result = await use_case.execute(
        UpdateAssignmentSetCommand(
            teacher_id=current_user.user_id,
            set_id=set_id,
            name=body.name,
            description=body.description,
            visibility=body.visibility,
            group_id=body.group_id,
            clear_group=body.clear_group,
            deadline_at=body.deadline_at,
            is_archived=body.is_archived,
        ),
    )
    return _to_response(unwrap_ok_or_http_exc(result))


@router.post("/{set_id}/items", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def add_assignment_set_item(
    set_id: int,
    body: AddAssignmentSetItemRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: AddAssignmentSetItemUseCase = Depends(
        Provide[Container.assignment_sets.add_assignment_set_item_use_case],
    ),
) -> None:
    unwrap_ok_or_http_exc(
        await use_case.execute(
            AddAssignmentSetItemCommand(
                teacher_id=current_user.user_id,
                set_id=set_id,
                task_id=body.task_id,
                sort_order=body.sort_order,
            ),
        ),
    )


@router.delete("/{set_id}/items/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def remove_assignment_set_item(
    set_id: int,
    task_id: int,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: RemoveAssignmentSetItemUseCase = Depends(
        Provide[Container.assignment_sets.remove_assignment_set_item_use_case],
    ),
) -> None:
    unwrap_ok_or_http_exc(
        await use_case.execute(
            RemoveAssignmentSetItemCommand(
                teacher_id=current_user.user_id,
                set_id=set_id,
                task_id=task_id,
            ),
        ),
    )
