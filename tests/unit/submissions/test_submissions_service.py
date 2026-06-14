from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.either import Err, Ok
from src.core.either.failures import ForbiddenFailure, NotFoundFailure
from src.core.settings import ExecutionSettings
from src.features.submissions.models import SubmissionModel
from src.features.submissions.services.submission_result_persister import SubmissionResultPersister
from src.features.submissions.services.submissions_service import SubmissionsService
from tests.unit.conftest import FakeUoW


@pytest.fixture
def submissions_service() -> SubmissionsService:
    rate_limiter = MagicMock()
    rate_limiter.check_submit = MagicMock()
    rate_limiter.on_job_queued = MagicMock()
    rate_limiter.on_job_finished = MagicMock()
    execution = MagicMock()
    execution.queue_depth.return_value = 0
    return SubmissionsService(
        uow=FakeUoW(session=AsyncMock()),
        catalog_service=MagicMock(),
        execution_service=execution,
        result_persister=MagicMock(spec=SubmissionResultPersister),
        execution_settings=ExecutionSettings(use_redis_store=True),
        execution_rate_limiter=rate_limiter,
    )


def _submission(*, user_id: int = 1, submission_id: int = 10) -> SubmissionModel:
    now = datetime.now(UTC)
    model = SubmissionModel(
        id=submission_id,
        user_id=user_id,
        task_id=2,
        language="python",
        code="print(1)",
        status="success",
        success=True,
        created_at=now,
        updated_at=now,
    )
    model.linter_errors = []
    model.pattern_errors = []
    model.test_results = []
    return model


@pytest.mark.asyncio
async def test_submissions_service__get_submission_not_found(submissions_service: SubmissionsService) -> None:
    with patch("src.features.submissions.services.submissions_service.SubmissionRepo") as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        result = await submissions_service.get_submission(submission_id=99, user_id=1)

    assert isinstance(result, Err)
    assert isinstance(result.error, NotFoundFailure)


@pytest.mark.asyncio
async def test_submissions_service__get_submission_forbidden(submissions_service: SubmissionsService) -> None:
    model = _submission(user_id=2)

    with patch("src.features.submissions.services.submissions_service.SubmissionRepo") as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=model)

        result = await submissions_service.get_submission(submission_id=model.id, user_id=1)

    assert isinstance(result, Err)
    assert isinstance(result.error, ForbiddenFailure)


@pytest.mark.asyncio
async def test_submissions_service__get_submission_success(submissions_service: SubmissionsService) -> None:
    model = _submission(user_id=7)

    with patch("src.features.submissions.services.submissions_service.SubmissionRepo") as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=model)

        result = await submissions_service.get_submission(submission_id=model.id, user_id=7)

    assert isinstance(result, Ok)
    assert result.value.id == model.id
    assert result.value.task_id == 2


@pytest.mark.asyncio
async def test_submissions_service__get_latest_pending_none(submissions_service: SubmissionsService) -> None:
    with patch("src.features.submissions.services.submissions_service.SubmissionRepo") as repo_cls:
        repo_cls.return_value.get_latest_pending = AsyncMock(return_value=None)

        result = await submissions_service.get_latest_pending(user_id=1, task_id=2)

    assert isinstance(result, Ok)
    assert result.value is None


@pytest.mark.asyncio
async def test_submissions_service__get_latest_pending_found(submissions_service: SubmissionsService) -> None:
    model = _submission(user_id=3)
    model.status = "queued"

    with patch("src.features.submissions.services.submissions_service.SubmissionRepo") as repo_cls:
        repo_cls.return_value.get_latest_pending = AsyncMock(return_value=model)

        result = await submissions_service.get_latest_pending(user_id=3, task_id=2)

    assert isinstance(result, Ok)
    assert result.value is not None
    assert result.value.status == "queued"
