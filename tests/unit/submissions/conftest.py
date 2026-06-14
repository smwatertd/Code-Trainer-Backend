from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.settings import ExecutionSettings
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
