from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.core.containers import Container
from src.core.policies.permissions import Permission
from src.features.auth.dependencies import require_permission
from src.features.progress.commands import (
    CreateTaskCurriculumLinkCommand,
    DeleteTaskCurriculumLinkCommand,
    GetCurriculumDebugCommand,
    GetCurriculumValidationCommand,
    GetTaskCurriculumLinksCommand,
    UpdateTaskCurriculumLinkCommand,
    ValidateTaskCurriculumLinkCommand,
)
from src.features.progress.curriculum_link_schemas import (
    CurriculumDebugResponse,
    CurriculumValidationResponse,
    TaskCurriculumLinkCreateRequest,
    TaskCurriculumLinkResponse,
    TaskCurriculumLinkUpdateRequest,
    TaskCurriculumLinkValidateRequest,
    TaskCurriculumLinkValidateResponse,
    TaskCurriculumMetadataResponse,
)
from src.features.progress.services.task_curriculum_link_service import TaskCurriculumLinkDTO
from src.features.progress.usecases import (
    CreateTaskCurriculumLinkUseCase,
    DeleteTaskCurriculumLinkUseCase,
    GetCurriculumDebugUseCase,
    GetCurriculumValidationUseCase,
    GetTaskCurriculumLinksUseCase,
    UpdateTaskCurriculumLinkUseCase,
    ValidateTaskCurriculumLinkUseCase,
)
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


def _link_response(link: TaskCurriculumLinkDTO) -> TaskCurriculumLinkResponse:
    return TaskCurriculumLinkResponse(
        id=link.id,
        task_id=link.task_id,
        language=link.language,
        learning_concept_id=link.learning_concept_id,
        technical_concept_id=link.technical_concept_id,
        exercise_pattern_id=link.exercise_pattern_id,
        action=link.action,
        is_primary=link.is_primary,
        created_at=link.created_at.isoformat() if link.created_at else None,
    )


@router.post("/tasks/validate-link", response_model=TaskCurriculumLinkValidateResponse)
@inject
async def validate_task_curriculum_link(
    body: TaskCurriculumLinkValidateRequest,
    _: object = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    use_case: ValidateTaskCurriculumLinkUseCase = Depends(
        Provide[Container.progress.validate_task_curriculum_link_use_case],
    ),
) -> TaskCurriculumLinkValidateResponse:
    metadata = unwrap_ok_or_http_exc(
        await use_case.execute(
            ValidateTaskCurriculumLinkCommand(
                language=body.language,
                technical_concept_id=body.technical_concept_id,
                exercise_pattern_id=body.exercise_pattern_id,
            ),
        ),
    )
    return TaskCurriculumLinkValidateResponse(
        language=metadata.language,
        learning_concept_id=metadata.learning_concept_id,
        technical_concept_id=metadata.technical_concept_id,
        exercise_pattern_id=metadata.exercise_pattern_id,
        action=metadata.action,
    )


@router.get("/tasks/{task_id}/links", response_model=TaskCurriculumMetadataResponse)
@inject
async def get_task_curriculum_links(
    task_id: int,
    _: object = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    use_case: GetTaskCurriculumLinksUseCase = Depends(
        Provide[Container.progress.get_task_curriculum_links_use_case],
    ),
) -> TaskCurriculumMetadataResponse:
    metadata = unwrap_ok_or_http_exc(
        await use_case.execute(GetTaskCurriculumLinksCommand(task_id=task_id)),
    )
    return TaskCurriculumMetadataResponse(
        task_id=metadata.task_id,
        has_curriculum_link=metadata.has_curriculum_link,
        primary_link=_link_response(metadata.primary_link) if metadata.primary_link else None,
        links=[_link_response(item) for item in metadata.links],
    )


@router.post(
    "/tasks/{task_id}/links",
    response_model=TaskCurriculumLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_task_curriculum_link(
    task_id: int,
    body: TaskCurriculumLinkCreateRequest,
    _: object = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    use_case: CreateTaskCurriculumLinkUseCase = Depends(
        Provide[Container.progress.create_task_curriculum_link_use_case],
    ),
) -> TaskCurriculumLinkResponse:
    link = unwrap_ok_or_http_exc(
        await use_case.execute(
            CreateTaskCurriculumLinkCommand(
                task_id=task_id,
                language=body.language,
                technical_concept_id=body.technical_concept_id,
                exercise_pattern_id=body.exercise_pattern_id,
                is_primary=body.is_primary,
            ),
        ),
    )
    return _link_response(link)


@router.patch("/tasks/{task_id}/links/{link_id}", response_model=TaskCurriculumLinkResponse)
@inject
async def update_task_curriculum_link(
    task_id: int,
    link_id: int,
    body: TaskCurriculumLinkUpdateRequest,
    _: object = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    use_case: UpdateTaskCurriculumLinkUseCase = Depends(
        Provide[Container.progress.update_task_curriculum_link_use_case],
    ),
) -> TaskCurriculumLinkResponse:
    link = unwrap_ok_or_http_exc(
        await use_case.execute(
            UpdateTaskCurriculumLinkCommand(
                task_id=task_id,
                link_id=link_id,
                language=body.language,
                technical_concept_id=body.technical_concept_id,
                exercise_pattern_id=body.exercise_pattern_id,
                is_primary=body.is_primary,
            ),
        ),
    )
    return _link_response(link)


@router.delete("/tasks/{task_id}/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_task_curriculum_link(
    task_id: int,
    link_id: int,
    _: object = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    use_case: DeleteTaskCurriculumLinkUseCase = Depends(
        Provide[Container.progress.delete_task_curriculum_link_use_case],
    ),
) -> None:
    unwrap_ok_or_http_exc(
        await use_case.execute(DeleteTaskCurriculumLinkCommand(task_id=task_id, link_id=link_id)),
    )


@router.get("/{language}/validate", response_model=CurriculumValidationResponse)
@inject
async def validate_curriculum(
    language: str,
    _: object = Depends(require_permission(Permission.MANAGE_USERS)),
    use_case: GetCurriculumValidationUseCase = Depends(
        Provide[Container.progress.get_curriculum_validation_use_case],
    ),
) -> CurriculumValidationResponse:
    payload = unwrap_ok_or_http_exc(
        await use_case.execute(GetCurriculumValidationCommand(language=language)),
    )
    return CurriculumValidationResponse(**payload)


@router.get("/{language}/debug", response_model=CurriculumDebugResponse)
@inject
async def get_curriculum_debug(
    language: str,
    _: object = Depends(require_permission(Permission.MANAGE_USERS)),
    use_case: GetCurriculumDebugUseCase = Depends(
        Provide[Container.progress.get_curriculum_debug_use_case],
    ),
) -> CurriculumDebugResponse:
    payload = unwrap_ok_or_http_exc(
        await use_case.execute(GetCurriculumDebugCommand(language=language)),
    )
    return CurriculumDebugResponse(**payload)
