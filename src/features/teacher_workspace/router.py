from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.core.containers import Container
from src.core.policies.permissions import Permission, can
from src.features.auth.dependencies import AuthenticatedUser, require_permission
from src.features.auth.repos.user_repo import UserRepo
from src.features.groups.commands import ListTeacherGroupsCommand
from src.features.groups.usecases import ListTeacherGroupsUseCase
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc
from src.core.interfaces import UnitOfWork

router = APIRouter(prefix="/teacher", tags=["teacher"])


class TeacherPermissionsResponse(BaseModel):
    edit_tasks: bool = True
    manage_groups: bool = True
    manage_catalogs: bool = True


class TeacherProfileResponse(BaseModel):
    user_id: int
    email: str
    display_name: str
    full_name: str
    role_label: str = "teacher"
    role: str = "Teacher"
    total_tasks: int = 0
    groups: list[dict[str, int | str]] = Field(default_factory=list)
    collections: list[dict[str, int | str]] = Field(default_factory=list)
    permissions: TeacherPermissionsResponse = Field(default_factory=TeacherPermissionsResponse)


class TeacherAnalyticsOverview(BaseModel):
    total_tasks: int = 0
    total_submissions: int = 0
    active_groups: int = 0


class TeacherAnalyticsResponse(BaseModel):
    overview: TeacherAnalyticsOverview = Field(default_factory=TeacherAnalyticsOverview)
    groups: list[dict] = Field(default_factory=list)
    assignments: list[dict] = Field(default_factory=list)


class TeacherSubmissionsListResponse(BaseModel):
    items: list[dict] = Field(default_factory=list)
    total: int = 0


@router.get("/profile", response_model=TeacherProfileResponse)
@inject
async def get_my_teacher_profile(
    current_user: AuthenticatedUser = Depends(require_permission(Permission.CREATE_ASSIGNMENTS)),
    groups_use_case: ListTeacherGroupsUseCase = Depends(
        Provide[Container.groups.list_teacher_groups_use_case],
    ),
    uow: UnitOfWork = Depends(Provide[Container.db.uow]),
) -> TeacherProfileResponse:
    async with uow(autocommit=False):
        user = await UserRepo(uow.session).get_by_id(current_user.user_id)
    if user is None:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    groups = unwrap_ok_or_http_exc(
        await groups_use_case.execute(ListTeacherGroupsCommand(teacher_id=current_user.user_id)),
    )
    role = current_user.role
    permissions = TeacherPermissionsResponse(
        edit_tasks=can(role, Permission.CREATE_ASSIGNMENTS),
        manage_groups=can(role, Permission.MANAGE_GROUPS),
        manage_catalogs=can(role, Permission.MANAGE_ASSIGNMENT_SETS),
    )
    return TeacherProfileResponse(
        user_id=user.id,
        email=user.email,
        display_name=user.name,
        full_name=user.name,
        groups=[{"id": group.id, "name": group.name} for group in groups],
        permissions=permissions,
    )


@router.get("/analytics", response_model=TeacherAnalyticsResponse)
async def get_teacher_analytics(
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_STUDENT_RESULTS)),
) -> TeacherAnalyticsResponse:
    return TeacherAnalyticsResponse()


@router.get("/submissions", response_model=TeacherSubmissionsListResponse)
async def get_teacher_submissions(
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_STUDENT_RESULTS)),
) -> TeacherSubmissionsListResponse:
    return TeacherSubmissionsListResponse()
