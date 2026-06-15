from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.containers import Container
from src.core.policies.permissions import Permission
from src.features.assignment_sets.commands import (
    AddAssignmentSetItemCommand,
    CreateAssignmentSetCommand,
    GetAssignmentSetCommand,
    ListTeacherAssignmentSetsCommand,
    RemoveAssignmentSetItemCommand,
    UpdateAssignmentSetCommand,
)
from src.features.assignment_sets.repos.assignment_set_repo import AssignmentSetRepo
from src.features.assignment_sets.usecases import (
    AddAssignmentSetItemUseCase,
    CreateAssignmentSetUseCase,
    GetAssignmentSetUseCase,
    ListTeacherAssignmentSetsUseCase,
    RemoveAssignmentSetItemUseCase,
    UpdateAssignmentSetUseCase,
)
from src.features.auth.dependencies import AuthenticatedUser, require_permission
from src.features.catalog.commands import CreateTeacherTaskCommand, ListTasksCommand
from src.features.catalog.repos.task_repo import TaskRepo
from src.features.catalog.usecases import CreateTeacherTaskUseCase, ListPublicTasksUseCase
from src.features.catalogs_compat.mappers import catalog_from_set, task_to_legacy
from src.features.catalogs_compat.schemas import (
    AssignTaskRequest,
    CatalogResponse,
    CreateCatalogRequest,
    CreateLegacyTaskRequest,
    LegacyTaskResponse,
)
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc
from src.core.interfaces import UnitOfWork

router = APIRouter(prefix="/catalogs", tags=["catalogs-compat"])


async def _catalog_ids_by_task(uow: UnitOfWork, teacher_id: int) -> dict[int, list[int]]:
    async with uow(autocommit=False):
        sets = await AssignmentSetRepo(uow.session).list_for_teacher(teacher_id)
    mapping: dict[int, list[int]] = {}
    for assignment_set in sets:
        for item in assignment_set.items:
            mapping.setdefault(item.task_id, []).append(assignment_set.id)
    return mapping


@router.get("/mine", response_model=list[CatalogResponse])
@inject
async def list_my_catalogs(
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: ListTeacherAssignmentSetsUseCase = Depends(
        Provide[Container.assignment_sets.list_teacher_assignment_sets_use_case],
    ),
) -> list[CatalogResponse]:
    result = await use_case.execute(
        ListTeacherAssignmentSetsCommand(teacher_id=current_user.user_id),
    )
    return [catalog_from_set(item) for item in unwrap_ok_or_http_exc(result)]


@router.post("", response_model=CatalogResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_catalog(
    body: CreateCatalogRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: CreateAssignmentSetUseCase = Depends(
        Provide[Container.assignment_sets.create_assignment_set_use_case],
    ),
) -> CatalogResponse:
    visibility = body.visibility if body.visibility in {"public", "private"} else "public"
    result = await use_case.execute(
        CreateAssignmentSetCommand(
            teacher_id=current_user.user_id,
            name=body.title.strip(),
            description=body.description or "",
            visibility=visibility,
            group_id=body.group_id,
            deadline_at=body.deadline_at,
        ),
    )
    return catalog_from_set(unwrap_ok_or_http_exc(result))


@router.get("/tasks", response_model=list[LegacyTaskResponse])
@inject
async def list_catalog_tasks(
    current_user: AuthenticatedUser = Depends(require_permission(Permission.CREATE_ASSIGNMENTS)),
    list_use_case: ListPublicTasksUseCase = Depends(Provide[Container.catalog.list_public_tasks_use_case]),
    uow: UnitOfWork = Depends(Provide[Container.db.uow]),
) -> list[LegacyTaskResponse]:
    summaries = unwrap_ok_or_http_exc(
        await list_use_case.execute(ListTasksCommand()),
    )
    catalog_map = await _catalog_ids_by_task(uow, current_user.user_id)
    async with uow(autocommit=False):
        repo = TaskRepo(uow.session)
        models = {model.id: model for model in await repo.list_public()}
    return [
        task_to_legacy(
            models[item.id],
            catalog_ids=catalog_map.get(item.id, []),
        )
        for item in summaries
        if item.id in models
    ]


@router.post("/tasks", response_model=LegacyTaskResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_catalog_task(
    body: CreateLegacyTaskRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.CREATE_ASSIGNMENTS)),
    use_case: CreateTeacherTaskUseCase = Depends(Provide[Container.catalog.create_teacher_task_use_case]),
    uow: UnitOfWork = Depends(Provide[Container.db.uow]),
) -> LegacyTaskResponse:
    payload: dict = {}
    if body.topic_id is not None:
        payload["topic_id"] = body.topic_id
    result = await use_case.execute(
        CreateTeacherTaskCommand(
            owner_user_id=current_user.user_id,
            title=body.title,
            description=body.content,
            difficulty="easy",
            task_type=body.type_id,
            payload=payload,
        ),
    )
    detail = unwrap_ok_or_http_exc(result)
    async with uow(autocommit=False):
        model = await TaskRepo(uow.session).get_by_id(detail.id)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task_to_legacy(model, catalog_ids=[])


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_catalog_task(
    task_id: int,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    uow: UnitOfWork = Depends(Provide[Container.db.uow]),
) -> None:
    async with uow(autocommit=True):
        repo = TaskRepo(uow.session)
        model = await repo.get_by_id(task_id)
        if model is None or model.owner_user_id != current_user.user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        model.is_deleted = True


@router.get("/{catalog_id}", response_model=CatalogResponse)
@inject
async def get_catalog(
    catalog_id: int,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: GetAssignmentSetUseCase = Depends(
        Provide[Container.assignment_sets.get_assignment_set_use_case],
    ),
) -> CatalogResponse:
    result = await use_case.execute(
        GetAssignmentSetCommand(
            user_id=current_user.user_id,
            role=current_user.role,
            set_id=catalog_id,
        ),
    )
    dto = unwrap_ok_or_http_exc(result)
    if dto.teacher_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog not found")
    return catalog_from_set(dto)


@router.delete("/{catalog_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_catalog(
    catalog_id: int,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: UpdateAssignmentSetUseCase = Depends(
        Provide[Container.assignment_sets.update_assignment_set_use_case],
    ),
) -> None:
    unwrap_ok_or_http_exc(
        await use_case.execute(
            UpdateAssignmentSetCommand(
                teacher_id=current_user.user_id,
                set_id=catalog_id,
                is_archived=True,
            ),
        ),
    )


@router.get("/{catalog_id}/tasks", response_model=list[LegacyTaskResponse])
@inject
async def get_catalog_tasks(
    catalog_id: int,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: GetAssignmentSetUseCase = Depends(
        Provide[Container.assignment_sets.get_assignment_set_use_case],
    ),
    uow: UnitOfWork = Depends(Provide[Container.db.uow]),
) -> list[LegacyTaskResponse]:
    dto = unwrap_ok_or_http_exc(
        await use_case.execute(
            GetAssignmentSetCommand(
                user_id=current_user.user_id,
                role=current_user.role,
                set_id=catalog_id,
            ),
        ),
    )
    if dto.teacher_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog not found")
    task_ids = [item.task_id for item in dto.items]
    async with uow(autocommit=False):
        repo = TaskRepo(uow.session)
        models = []
        for task_id in task_ids:
            model = await repo.get_by_id(task_id)
            if model and not model.is_deleted:
                models.append(model)
    return [task_to_legacy(model, catalog_ids=[catalog_id]) for model in models]


@router.post("/{catalog_id}/assignments", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def assign_existing_task(
    catalog_id: int,
    body: AssignTaskRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: AddAssignmentSetItemUseCase = Depends(
        Provide[Container.assignment_sets.add_assignment_set_item_use_case],
    ),
) -> None:
    unwrap_ok_or_http_exc(
        await use_case.execute(
            AddAssignmentSetItemCommand(
                teacher_id=current_user.user_id,
                set_id=catalog_id,
                task_id=body.task_id,
            ),
        ),
    )


@router.delete("/{catalog_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def remove_task_from_catalog(
    catalog_id: int,
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
                set_id=catalog_id,
                task_id=task_id,
            ),
        ),
    )


@router.post("/{catalog_id}/tasks", response_model=LegacyTaskResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_task_in_catalog(
    catalog_id: int,
    body: CreateLegacyTaskRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.CREATE_ASSIGNMENTS)),
    create_use_case: CreateTeacherTaskUseCase = Depends(Provide[Container.catalog.create_teacher_task_use_case]),
    add_use_case: AddAssignmentSetItemUseCase = Depends(
        Provide[Container.assignment_sets.add_assignment_set_item_use_case],
    ),
    uow: UnitOfWork = Depends(Provide[Container.db.uow]),
) -> LegacyTaskResponse:
    payload: dict = {}
    if body.topic_id is not None:
        payload["topic_id"] = body.topic_id
    detail = unwrap_ok_or_http_exc(
        await create_use_case.execute(
            CreateTeacherTaskCommand(
                owner_user_id=current_user.user_id,
                title=body.title,
                description=body.content,
                difficulty="easy",
                task_type=body.type_id,
                payload=payload,
            ),
        ),
    )
    unwrap_ok_or_http_exc(
        await add_use_case.execute(
            AddAssignmentSetItemCommand(
                teacher_id=current_user.user_id,
                set_id=catalog_id,
                task_id=detail.id,
            ),
        ),
    )
    async with uow(autocommit=False):
        model = await TaskRepo(uow.session).get_by_id(detail.id)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task_to_legacy(model, catalog_ids=[catalog_id])
