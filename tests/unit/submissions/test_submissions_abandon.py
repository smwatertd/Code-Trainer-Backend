from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.core.either import Ok
from src.features.submissions.models import SubmissionModel
from src.features.submissions.services.submissions_service import SubmissionsService


@pytest.mark.asyncio
async def test_submissions_service__abandon_releases_stuck_submission(
    submissions_service: SubmissionsService,
) -> None:
    model = SubmissionModel(
        id=3,
        user_id=1,
        task_id=2,
        language="python",
        code="print(1)",
        status="queued",
    )

    with patch("src.features.submissions.services.submissions_service.SubmissionRepo") as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=model)

        result = await submissions_service.abandon(submission_id=3, user_id=1)

    assert isinstance(result, Ok)
    assert result.value.released is True
    assert result.value.status == "failed"
    submissions_service.execution_rate_limiter.on_job_finished.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_submissions_service__abandon_noop_for_terminal(
    submissions_service: SubmissionsService,
) -> None:
    model = SubmissionModel(
        id=4,
        user_id=1,
        task_id=2,
        language="python",
        code="print(1)",
        status="success",
        success=True,
    )

    with patch("src.features.submissions.services.submissions_service.SubmissionRepo") as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=model)

        result = await submissions_service.abandon(submission_id=4, user_id=1)

    assert isinstance(result, Ok)
    assert result.value.released is False
    submissions_service.execution_rate_limiter.on_job_finished.assert_not_called()
