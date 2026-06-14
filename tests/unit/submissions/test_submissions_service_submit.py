from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.either import Err, Ok
from src.core.either.failures import NotFoundFailure
from src.core.settings import ExecutionSettings
from src.features.catalog.domain.dto import TaskDetailDTO
from src.features.submissions.models import SubmissionModel
from src.features.submissions.services.submission_result_persister import SubmissionResultPersister
from src.features.submissions.services.submissions_service import SubmissionsService
from src.shared.execution.domain.dto import JobQueuedDTO
from tests.unit.conftest import FakeUoW


@pytest.fixture
def submissions_service() -> SubmissionsService:
    catalog = MagicMock()
    catalog.get_internal_task = AsyncMock(
        return_value=Ok(
            TaskDetailDTO(
                id=2,
                title="Reorder",
                description="desc",
                difficulty="easy",
                task_type="task_build_from_blocks",
                payload={
                    "correct_order": [1, 0],
                    "expected_code": "print('b')\nprint('a')",
                },
            )
        )
    )

    execution = MagicMock()
    execution.submit.return_value = Ok(JobQueuedDTO(job_id="job-1", status="QUEUED"))
    execution.get_job.return_value = None
    execution.queue_depth.return_value = 0

    rate_limiter = MagicMock()
    rate_limiter.check_submit = MagicMock()
    rate_limiter.on_job_queued = MagicMock()
    rate_limiter.on_job_finished = MagicMock()

    return SubmissionsService(
        uow=FakeUoW(session=AsyncMock()),
        catalog_service=catalog,
        execution_service=execution,
        result_persister=MagicMock(spec=SubmissionResultPersister),
        execution_settings=ExecutionSettings(use_redis_store=True),
        execution_rate_limiter=rate_limiter,
    )


@pytest.mark.asyncio
async def test_submissions_service__submit_unknown_task(submissions_service: SubmissionsService) -> None:
    submissions_service.catalog_service.get_internal_task = AsyncMock(
        return_value=Err(NotFoundFailure("Task", "404")),
    )

    result = await submissions_service.submit(
        user_id=1,
        task_id=404,
        language="python",
        code="print(1)",
    )

    assert isinstance(result, Err)


@pytest.mark.asyncio
async def test_submissions_service__submit_creates_row_and_enqueues(submissions_service: SubmissionsService) -> None:
    created = SubmissionModel(
        id=15,
        user_id=1,
        task_id=2,
        language="python",
        code="print('b')\nprint('a')",
        status="queued",
    )

    with patch("src.features.submissions.services.submissions_service.SubmissionRepo") as repo_cls:
        repo_cls.return_value.create = AsyncMock(return_value=created)
        repo_cls.return_value.get_by_id = AsyncMock(return_value=created)

        result = await submissions_service.submit(
            user_id=1,
            task_id=2,
            language="python",
            code="print('b')\nprint('a')",
            block_order=[1, 0],
        )

    assert isinstance(result, Ok)
    assert result.value.id == 15
    assert result.value.status == "queued"

    submissions_service.execution_service.submit.assert_called_once()
    call_kwargs = submissions_service.execution_service.submit.call_args.kwargs
    assert call_kwargs["op"] == "process_submission"
    assert call_kwargs["payload"]["submission_id"] == 15
    assert call_kwargs["payload"]["block_order"] == [1, 0]


@pytest.mark.asyncio
async def test_submissions_service__submit_passes_flowchart_payload(submissions_service: SubmissionsService) -> None:
    submissions_service.catalog_service.get_internal_task = AsyncMock(
        return_value=Ok(
            TaskDetailDTO(
                id=3,
                title="Flowchart",
                description="desc",
                difficulty="easy",
                task_type="task_flowchart_to_code",
                payload={"flowchart_mode": "code_to_flowchart", "flow_spec": {}},
            )
        )
    )
    created = SubmissionModel(
        id=16,
        user_id=1,
        task_id=3,
        language="python",
        code=".",
        status="queued",
    )
    nodes = [{"id": "1", "type": "start"}]
    edges = [{"source": "1", "target": "2"}]

    with patch("src.features.submissions.services.submissions_service.SubmissionRepo") as repo_cls:
        repo_cls.return_value.create = AsyncMock(return_value=created)
        repo_cls.return_value.get_by_id = AsyncMock(return_value=created)

        result = await submissions_service.submit(
            user_id=1,
            task_id=3,
            language="python",
            code=".",
            nodes=nodes,
            edges=edges,
        )

    assert isinstance(result, Ok)
    payload = submissions_service.execution_service.submit.call_args.kwargs["payload"]
    assert payload["nodes"] == nodes
    assert payload["edges"] == edges


@pytest.mark.asyncio
async def test_submissions_service__submit_finalizes_when_in_memory_store() -> None:
    catalog = MagicMock()
    catalog.get_public_task = AsyncMock(
        return_value=Ok(
            TaskDetailDTO(
                id=2,
                title="Reorder",
                description="desc",
                difficulty="easy",
                task_type="task_build_from_blocks",
                payload={"correct_order": [1, 0], "expected_code": "x"},
            )
        )
    )
    catalog.get_internal_task = AsyncMock(
        return_value=Ok(
            TaskDetailDTO(
                id=2,
                title="Reorder",
                description="desc",
                difficulty="easy",
                task_type="task_build_from_blocks",
                payload={"correct_order": [1, 0], "expected_code": "x"},
            )
        )
    )

    execution = MagicMock()
    execution.submit.return_value = Ok(JobQueuedDTO(job_id="job-99", status="QUEUED"))

    from src.shared.execution.domain.execution_job import ExecutionJob
    from src.shared.execution.domain.job_status import JobStatus

    job = ExecutionJob.create(
        user_id="1",
        language_id="python",
        code="print(1)",
        op="process_submission",
        task_id=2,
    )
    job.status = JobStatus.SUCCESS
    execution.get_job.return_value = job
    execution.get_result.return_value = Ok(
        MagicMock(
            output={"success": True, "compiler_errors": [], "linter_errors": [], "pattern_errors": []},
            errors=None,
        )
    )
    execution.queue_depth.return_value = 0

    rate_limiter = MagicMock()
    rate_limiter.check_submit = MagicMock()
    rate_limiter.on_job_queued = MagicMock()
    rate_limiter.on_job_finished = MagicMock()

    persister = MagicMock(spec=SubmissionResultPersister)
    persister.persist_check_output = AsyncMock()

    service = SubmissionsService(
        uow=FakeUoW(session=AsyncMock()),
        catalog_service=catalog,
        execution_service=execution,
        result_persister=persister,
        execution_settings=ExecutionSettings(use_redis_store=False),
        execution_rate_limiter=rate_limiter,
    )

    created = SubmissionModel(id=20, user_id=1, task_id=2, language="python", code="print(1)", status="success")
    with patch("src.features.submissions.services.submissions_service.SubmissionRepo") as repo_cls:
        repo_cls.return_value.create = AsyncMock(
            return_value=SubmissionModel(
                id=20, user_id=1, task_id=2, language="python", code="print(1)", status="queued"
            )
        )
        repo_cls.return_value.get_by_id = AsyncMock(return_value=created)

        result = await service.submit(user_id=1, task_id=2, language="python", code="print(1)")

    assert isinstance(result, Ok)
    assert result.value.status == "success"
    persister.persist_check_output.assert_awaited_once()
