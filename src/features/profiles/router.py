from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.containers import Container
from src.core.policies.permissions import Permission
from src.features.auth.dependencies import AuthenticatedUser, require_permission
from src.features.profiles.schemas import (
    MyProfileResponse,
    StudentPublicProfileResponse,
    TeacherPublicProfileResponse,
)
from src.features.profiles.services.profile_service import ProfileService
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=MyProfileResponse)
@inject
async def get_my_profile(
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_OWN_PROGRESS)),
    profile_service: ProfileService = Depends(Provide[Container.profiles.profile_service]),
) -> MyProfileResponse:
    result = await profile_service.get_my_profile(user_id=current_user.user_id)
    return unwrap_ok_or_http_exc(result)


@router.get(
    "/users/{user_id}",
    response_model=TeacherPublicProfileResponse | StudentPublicProfileResponse,
)
@inject
async def get_user_profile(
    user_id: int,
    teacher_id: int | None = Query(default=None, ge=1),
    current_user: AuthenticatedUser = Depends(require_permission(Permission.BROWSE_TEACHERS)),
    profile_service: ProfileService = Depends(Provide[Container.profiles.profile_service]),
) -> TeacherPublicProfileResponse | StudentPublicProfileResponse:
    result = await profile_service.get_user_profile(
        target_user_id=user_id,
        viewer_id=current_user.user_id,
        viewer_role=current_user.role,
        teacher_id=teacher_id,
    )
    return unwrap_ok_or_http_exc(result)
