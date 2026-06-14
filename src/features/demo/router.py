from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request

from src.core.containers import Container
from src.features.demo.commands import GetDemoCheckCommand, SubmitDemoCheckCommand
from src.features.demo.schemas import (
    DemoCheckQueuedResponse,
    DemoCheckRequest,
    DemoCheckResultResponse,
)
from src.features.demo.usecases import GetDemoCheckResultUseCase, SubmitDemoCheckUseCase
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc

router = APIRouter(prefix="/demo", tags=["demo"])


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


@router.post("/check", response_model=DemoCheckQueuedResponse)
@inject
async def submit_demo_check(
    body: DemoCheckRequest,
    request: Request,
    use_case: SubmitDemoCheckUseCase = Depends(Provide[Container.demo.submit_demo_check_use_case]),
) -> DemoCheckQueuedResponse:
    result = await use_case.execute(
        SubmitDemoCheckCommand(
            task_id=body.task_id,
            language=body.language,
            code=body.code,
            client_ip=_client_ip(request),
            block_order=body.block_order,
            nodes=body.nodes,
            edges=body.edges,
            flow=body.flow,
        )
    )
    dto = unwrap_ok_or_http_exc(result)
    return DemoCheckQueuedResponse(job_id=dto.job_id, status=dto.status)


@router.get("/check/{job_id}", response_model=DemoCheckResultResponse)
@inject
async def get_demo_check_result(
    job_id: str,
    request: Request,
    use_case: GetDemoCheckResultUseCase = Depends(Provide[Container.demo.get_demo_check_result_use_case]),
) -> DemoCheckResultResponse:
    result = use_case.execute(
        GetDemoCheckCommand(
            job_id=job_id,
            client_ip=_client_ip(request),
        )
    )
    dto = unwrap_ok_or_http_exc(result)
    return DemoCheckResultResponse(
        job_id=dto.job_id,
        status=dto.status,
        success=dto.success,
        compiler_errors=dto.compiler_errors or [],
        linter_errors=dto.linter_errors or [],
        pattern_errors=dto.pattern_errors or [],
        test_results=dto.test_results or [],
        errors=dto.errors,
    )
