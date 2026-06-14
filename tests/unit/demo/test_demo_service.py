from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.either import Err, Ok
from src.core.either.failures import ForbiddenFailure, NotFoundFailure, RateLimitFailure
from src.core.settings import GuestSettings
from src.features.catalog.domain.dto import TaskDetailDTO
from src.features.demo.commands import GetDemoCheckCommand, SubmitDemoCheckCommand
from src.features.demo.services.demo_service import DemoService
from src.features.demo.services.guest_rate_limiter import GuestRateLimiter, GuestRateLimitError
from src.shared.execution.domain.dto import JobResultDTO
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.services.execution_service import ExecutionService
from src.shared.execution.stores.memory_job_store import MemoryJobStore


def _public_task() -> TaskDetailDTO:
    return TaskDetailDTO(
        id=2,
        title="Reorder blocks",
        description="desc",
        difficulty="easy",
        task_type="task_build_from_blocks",
        payload={
            "correct_order": [1, 0],
            "expected_code": "print('b')\nprint('a')",
        },
    )


@pytest.fixture
def demo_service() -> DemoService:
    catalog = MagicMock()
    catalog.get_internal_task = AsyncMock(return_value=Ok(_public_task()))

    store = MemoryJobStore()
    execution = ExecutionService(store=store, auto_process=False)
    rate_limiter = GuestRateLimiter(
        max_checks_per_minute=8,
        max_concurrent_checks=1,
    )

    return DemoService(
        catalog_service=catalog,
        execution_service=execution,
        rate_limiter=rate_limiter,
        guest_settings=GuestSettings(enabled=True),
    )


@pytest.mark.asyncio
async def test_demo_service__submit_disabled_guest_mode(demo_service: DemoService) -> None:
    demo_service.guest_settings = GuestSettings(enabled=False)

    result = await demo_service.submit_check(
        SubmitDemoCheckCommand(
            task_id=2,
            language="python",
            code="print(1)",
            client_ip="10.0.0.1",
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, NotFoundFailure)


@pytest.mark.asyncio
async def test_demo_service__submit_unknown_task(demo_service: DemoService) -> None:
    demo_service.catalog_service.get_internal_task = AsyncMock(
        return_value=Err(NotFoundFailure("Task", "999")),
    )

    result = await demo_service.submit_check(
        SubmitDemoCheckCommand(
            task_id=999,
            language="python",
            code="print(1)",
            client_ip="10.0.0.1",
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, NotFoundFailure)


@pytest.mark.asyncio
async def test_demo_service__submit_rate_limited(demo_service: DemoService) -> None:
    demo_service.rate_limiter.check_submit = MagicMock(
        side_effect=GuestRateLimitError("too many checks"),
    )

    result = await demo_service.submit_check(
        SubmitDemoCheckCommand(
            task_id=2,
            language="python",
            code="print(1)",
            client_ip="10.0.0.1",
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, RateLimitFailure)


@pytest.mark.asyncio
async def test_demo_service__submit_queues_job(demo_service: DemoService) -> None:
    result = await demo_service.submit_check(
        SubmitDemoCheckCommand(
            task_id=2,
            language="python",
            code="print('b')\nprint('a')",
            client_ip="10.0.0.8",
            block_order=[1, 0],
        )
    )

    assert isinstance(result, Ok)
    assert result.value.job_id
    assert result.value.status == JobStatus.QUEUED.value


def test_demo_service__get_result_forbidden_for_other_ip(demo_service: DemoService) -> None:
    submit = demo_service.execution_service.submit(
        user_id=demo_service.rate_limiter.guest_user_id("10.0.0.1"),
        language_id="python",
        code="print(1)",
        op="guest_full_check",
        task_id=2,
        payload={"client_ip": "10.0.0.1", "guest": True},
    )
    assert isinstance(submit, Ok)
    job_id = submit.value.job_id

    result = demo_service.get_check_result(
        GetDemoCheckCommand(job_id=job_id, client_ip="10.0.0.2"),
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, ForbiddenFailure)


def test_demo_service__maps_success_output(demo_service: DemoService) -> None:
    dto = JobResultDTO(
        job_id="job-1",
        status="SUCCESS",
        success=True,
        output={
            "success": True,
            "compiler_errors": [],
            "linter_errors": [{"type": "LINT", "text": "ok"}],
            "pattern_errors": [],
            "test_results": [{"case": 1, "status": "PASS"}],
        },
    )

    mapped = demo_service._map_result(dto)

    assert mapped.status == "SUCCESS"
    assert mapped.success is True
    assert mapped.linter_errors == [{"type": "LINT", "text": "ok"}]
    assert mapped.test_results == [{"case": 1, "status": "PASS"}]


def test_demo_service__maps_failed_execution(demo_service: DemoService) -> None:
    dto = JobResultDTO(
        job_id="job-2",
        status="FAILED",
        success=False,
        errors="boom",
    )

    mapped = demo_service._map_result(dto)

    assert mapped.status == "FAILED"
    assert mapped.success is False
    assert mapped.compiler_errors == [{"type": "EXECUTION", "text": "boom"}]


def test_demo_service__maps_non_terminal_status(demo_service: DemoService) -> None:
    dto = JobResultDTO(job_id="job-3", status="RUNNING", success=None)

    mapped = demo_service._map_result(dto)

    assert mapped.status == "RUNNING"
    assert mapped.success is None
