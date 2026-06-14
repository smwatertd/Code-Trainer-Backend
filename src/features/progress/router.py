from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.containers import Container
from src.core.policies.permissions import Permission
from src.features.auth.dependencies import AuthenticatedUser, require_permission
from src.features.progress.commands import GetLearningConceptProgressCommand, GetTaskProgressCommand
from src.features.progress.schemas import LearningConceptProgressResponse, TaskProgressResponse
from src.features.progress.usecases import GetLearningConceptProgressUseCase, GetTaskProgressUseCase
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/tasks/{task_id}", response_model=TaskProgressResponse)
@inject
async def get_task_progress(
    task_id: int,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_OWN_PROGRESS)),
    use_case: GetTaskProgressUseCase = Depends(Provide[Container.progress.get_task_progress_use_case]),
) -> TaskProgressResponse:
    result = await use_case.execute(
        GetTaskProgressCommand(user_id=current_user.user_id, task_id=task_id),
    )
    progress = unwrap_ok_or_http_exc(result)
    return TaskProgressResponse(**progress.__dict__)


@router.get(
    "/curriculum/{language}/{learning_concept_id}",
    response_model=LearningConceptProgressResponse,
)
@inject
async def get_learning_concept_progress(
    language: str,
    learning_concept_id: str,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_OWN_PROGRESS)),
    use_case: GetLearningConceptProgressUseCase = Depends(
        Provide[Container.progress.get_learning_concept_progress_use_case],
    ),
) -> LearningConceptProgressResponse:
    result = await use_case.execute(
        GetLearningConceptProgressCommand(
            user_id=current_user.user_id,
            language=language,
            learning_concept_id=learning_concept_id,
        ),
    )
    progress = unwrap_ok_or_http_exc(result)
    return LearningConceptProgressResponse(
        language=progress.language,
        learning_concept_id=progress.learning_concept_id,
        total_tasks=progress.total_tasks,
        passed_tasks=progress.passed_tasks,
        progress_percent=progress.progress_percent,
        by_technical_concept={key: value.__dict__ for key, value in progress.by_technical_concept.items()},
        by_task_id={key: value.__dict__ for key, value in progress.by_task_id.items()},
    )
