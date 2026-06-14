from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.containers import Container
from src.core.policies.permissions import Permission
from src.features.auth.dependencies import AuthenticatedUser, require_permission
from src.features.catalog.commands import CreateTeacherTaskCommand, GetTaskCommand, ListTasksCommand
from src.features.catalog.schemas import TaskDetailResponse, TaskSummaryResponse, TeacherTaskCreateRequest
from src.features.catalog.usecases import CreateTeacherTaskUseCase, GetPublicTaskUseCase, ListPublicTasksUseCase
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc

router = APIRouter(prefix="/catalog", tags=["catalog"])
teacher_router = APIRouter(prefix="/teacher/tasks", tags=["teacher-tasks"])


@router.get("/tasks", response_model=list[TaskSummaryResponse])
@inject
async def list_public_tasks(
    difficulty: str | None = Query(default=None),
    task_type: str | None = Query(default=None),
    topic: str | None = Query(default=None),
    use_case: ListPublicTasksUseCase = Depends(Provide[Container.catalog.list_public_tasks_use_case]),
) -> list[TaskSummaryResponse]:
    result = await use_case.execute(
        ListTasksCommand(difficulty=difficulty, task_type=task_type, topic=topic),
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
