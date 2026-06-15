from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.containers import Container
from src.core.policies.permissions import Permission
from src.features.auth.dependencies import AuthenticatedUser, get_optional_authenticated_user, require_permission
from src.features.catalog.commands import (
    CreateTeacherTaskCommand,
    GetTaskCommand,
    GetTeacherTaskCommand,
    ListTasksCommand,
    ListTeacherTasksCommand,
    UpdateTeacherTaskCommand,
)
from src.features.catalog.schemas import (
    TaskDetailResponse,
    TaskSummaryResponse,
    TeacherTaskCreateRequest,
    TeacherTaskUpdateRequest,
)
from src.features.catalog.usecases import (
    CreateTeacherTaskUseCase,
    GetPublicTaskUseCase,
    GetTeacherTaskUseCase,
    ListPublicTasksUseCase,
    ListTeacherTasksUseCase,
    UpdateTeacherTaskUseCase,
)
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc

router = APIRouter(prefix="/catalog", tags=["catalog"])
teacher_router = APIRouter(prefix="/teacher/tasks", tags=["teacher-tasks"])


@router.get("/tasks", response_model=list[TaskSummaryResponse])
@inject
async def list_public_tasks(
    difficulty: str | None = Query(default=None),
    task_type: str | None = Query(default=None),
    topic: str | None = Query(default=None),
    current_user: AuthenticatedUser | None = Depends(get_optional_authenticated_user),
    use_case: ListPublicTasksUseCase = Depends(Provide[Container.catalog.list_public_tasks_use_case]),
) -> list[TaskSummaryResponse]:
    result = await use_case.execute(
        ListTasksCommand(
            difficulty=difficulty,
            task_type=task_type,
            topic=topic,
            user_id=current_user.user_id if current_user else None,
        ),
    )
    items = unwrap_ok_or_http_exc(result)
    return [TaskSummaryResponse(**item.__dict__) for item in items]


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
@inject
async def get_public_task(
    task_id: int,
    use_case: GetPublicTaskUseCase = Depends(Provide[Container.catalog.get_public_task_use_case]),
) -> TaskDetailResponse:
    result = await use_case.execute(GetTaskCommand(task_id=task_id))
    item = unwrap_ok_or_http_exc(result)
    return TaskDetailResponse(**item.__dict__)


@teacher_router.get("/mine", response_model=list[TaskSummaryResponse])
@inject
async def list_teacher_tasks(
    current_user: AuthenticatedUser = Depends(require_permission(Permission.CREATE_ASSIGNMENTS)),
    use_case: ListTeacherTasksUseCase = Depends(Provide[Container.catalog.list_teacher_tasks_use_case]),
) -> list[TaskSummaryResponse]:
    result = await use_case.execute(ListTeacherTasksCommand(owner_user_id=current_user.user_id))
    items = unwrap_ok_or_http_exc(result)
    return [TaskSummaryResponse(**item.__dict__) for item in items]


@teacher_router.get("/{task_id}", response_model=TaskDetailResponse)
@inject
async def get_teacher_task(
    task_id: int,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.CREATE_ASSIGNMENTS)),
    use_case: GetTeacherTaskUseCase = Depends(Provide[Container.catalog.get_teacher_task_use_case]),
) -> TaskDetailResponse:
    result = await use_case.execute(
        GetTeacherTaskCommand(
            task_id=task_id,
            user_id=current_user.user_id,
            is_admin=current_user.role == "admin",
        ),
    )
    item = unwrap_ok_or_http_exc(result)
    return TaskDetailResponse(**item.__dict__)


@teacher_router.post("", response_model=TaskDetailResponse)
@inject
async def create_teacher_task(
    body: TeacherTaskCreateRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.CREATE_ASSIGNMENTS)),
    use_case: CreateTeacherTaskUseCase = Depends(Provide[Container.catalog.create_teacher_task_use_case]),
) -> TaskDetailResponse:
    result = await use_case.execute(
        CreateTeacherTaskCommand(
            owner_user_id=current_user.user_id,
            title=body.title,
            description=body.description,
            difficulty=body.difficulty,
            task_type=body.task_type,
            payload=body.payload,
        )
    )
    item = unwrap_ok_or_http_exc(result)
    return TaskDetailResponse(**item.__dict__)


@teacher_router.patch("/{task_id}", response_model=TaskDetailResponse)
@inject
async def update_teacher_task(
    task_id: int,
    body: TeacherTaskUpdateRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    use_case: UpdateTeacherTaskUseCase = Depends(Provide[Container.catalog.update_teacher_task_use_case]),
) -> TaskDetailResponse:
    result = await use_case.execute(
        UpdateTeacherTaskCommand(
            task_id=task_id,
            user_id=current_user.user_id,
            is_admin=current_user.role == "admin",
            title=body.title,
            description=body.description,
            difficulty=body.difficulty,
            payload=body.payload,
        ),
    )
    item = unwrap_ok_or_http_exc(result)
    return TaskDetailResponse(**item.__dict__)
