from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.containers import Container
from src.core.policies.permissions import Permission
from src.features.auth.dependencies import AuthenticatedUser, require_permission
from src.features.submissions.commands import (
    AbandonSubmissionCommand,
    GetLatestPendingSubmissionCommand,
    GetSubmissionCommand,
    ListSubmissionHistoryCommand,
    SubmitSubmissionCommand,
)
from src.features.submissions.schemas import (
    SubmissionAbandonedResponse,
    SubmissionCreateRequest,
    SubmissionHistoryItemResponse,
    SubmissionQueuedResponse,
    SubmissionResponse,
)
from src.features.submissions.usecases import (
    AbandonSubmissionUseCase,
    GetLatestPendingSubmissionUseCase,
    GetSubmissionUseCase,
    ListSubmissionHistoryUseCase,
    SubmitSubmissionUseCase,
)
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.get("/pending/latest", response_model=SubmissionResponse | None)
@inject
async def get_latest_pending_submission(
    task_id: int = Query(..., ge=1),
    current_user: AuthenticatedUser = Depends(require_permission(Permission.SOLVE_ASSIGNMENTS)),
    use_case: GetLatestPendingSubmissionUseCase = Depends(
        Provide[Container.submissions.get_latest_pending_submission_use_case]
    ),
) -> SubmissionResponse | None:
    result = await use_case.execute(
        GetLatestPendingSubmissionCommand(user_id=current_user.user_id, task_id=task_id),
    )
    dto = unwrap_ok_or_http_exc(result)
    if dto is None:
        return None
    return SubmissionResponse(**dto.__dict__)


@router.get("/history", response_model=list[SubmissionHistoryItemResponse])
@inject
async def list_submission_history(
    task_id: int = Query(..., ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(require_permission(Permission.SOLVE_ASSIGNMENTS)),
    use_case: ListSubmissionHistoryUseCase = Depends(Provide[Container.submissions.list_submission_history_use_case]),
) -> list[SubmissionHistoryItemResponse]:
    result = await use_case.execute(
        ListSubmissionHistoryCommand(user_id=current_user.user_id, task_id=task_id, limit=limit),
    )
    items = unwrap_ok_or_http_exc(result)
    return [SubmissionHistoryItemResponse(**item.__dict__) for item in items]


@router.post("", response_model=SubmissionQueuedResponse)
@inject
async def submit_submission(
    body: SubmissionCreateRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.SOLVE_ASSIGNMENTS)),
    use_case: SubmitSubmissionUseCase = Depends(Provide[Container.submissions.submit_submission_use_case]),
) -> SubmissionQueuedResponse:
    result = await use_case.execute(
        SubmitSubmissionCommand(
            user_id=current_user.user_id,
            task_id=body.task_id,
            language=body.language,
            code=body.code,
            block_order=body.block_order,
            nodes=body.nodes,
            edges=body.edges,
            flow=body.flow,
        )
    )
    queued = unwrap_ok_or_http_exc(result)
    return SubmissionQueuedResponse(id=queued.id, status=queued.status)


@router.post("/{submission_id}/abandon", response_model=SubmissionAbandonedResponse)
@inject
async def abandon_submission(
    submission_id: int,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.SOLVE_ASSIGNMENTS)),
    use_case: AbandonSubmissionUseCase = Depends(Provide[Container.submissions.abandon_submission_use_case]),
) -> SubmissionAbandonedResponse:
    result = await use_case.execute(
        AbandonSubmissionCommand(submission_id=submission_id, user_id=current_user.user_id),
    )
    abandoned = unwrap_ok_or_http_exc(result)
    return SubmissionAbandonedResponse(released=abandoned.released, status=abandoned.status)


@router.get("/{submission_id}", response_model=SubmissionResponse)
@inject
async def get_submission(
    submission_id: int,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.SOLVE_ASSIGNMENTS)),
    use_case: GetSubmissionUseCase = Depends(Provide[Container.submissions.get_submission_use_case]),
) -> SubmissionResponse:
    result = await use_case.execute(
        GetSubmissionCommand(submission_id=submission_id, user_id=current_user.user_id),
    )
    dto = unwrap_ok_or_http_exc(result)
    return SubmissionResponse(**dto.__dict__)
