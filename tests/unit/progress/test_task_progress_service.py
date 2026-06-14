from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.features.progress.models import TaskProgressModel
from src.features.progress.services.task_progress_service import (
    PROGRESS_STATUS_FAILED,
    PROGRESS_STATUS_NOT_STARTED,
    PROGRESS_STATUS_PASSED,
    TaskProgressService,
    progress_status_from_row,
)


def test_progress_status_from_row__not_started_when_missing() -> None:
    assert progress_status_from_row(None) == PROGRESS_STATUS_NOT_STARTED


def test_progress_status_from_row__failed_after_attempts() -> None:
    row = TaskProgressModel(
        user_id=1,
        task_id=2,
        attempts_count=1,
        passed_count=0,
    )

    assert progress_status_from_row(row) == PROGRESS_STATUS_FAILED


def test_progress_status_from_row__passed_when_solved() -> None:
    row = TaskProgressModel(
        user_id=1,
        task_id=2,
        attempts_count=3,
        passed_count=1,
    )

    assert progress_status_from_row(row) == PROGRESS_STATUS_PASSED


@pytest.mark.asyncio
async def test_task_progress_service__records_first_pass() -> None:
    class _Session:
        def __init__(self) -> None:
            self.added: list[TaskProgressModel] = []

        def add(self, row: TaskProgressModel) -> None:
            self.added.append(row)

        async def execute(self, _stmt: object) -> object:
            return type("Result", (), {"scalar_one_or_none": lambda self: None})()

        async def flush(self) -> None:
            return None

    session = _Session()
    uow = MagicMock()
    uow.session = session
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    service = TaskProgressService(uow=uow)

    await service.record_submission_result(
        session,  # type: ignore[arg-type]
        user_id=7,
        submission_id=11,
        task_id=2,
        passed=True,
    )

    added = session.added[0]
    assert isinstance(added, TaskProgressModel)
    assert added.attempts_count == 1
    assert added.passed_count == 1
    assert added.last_status == "passed"
    assert added.first_passed_at is not None


@pytest.mark.asyncio
async def test_task_progress_service__increments_passed_count_on_each_success() -> None:
    row = TaskProgressModel(
        user_id=1,
        task_id=2,
        attempts_count=2,
        passed_count=1,
    )
    repo = MagicMock()
    repo.get_by_user_and_task = AsyncMock(return_value=row)
    repo.add = AsyncMock()
    session = AsyncMock()

    with patch(
        "src.features.progress.services.task_progress_service.TaskProgressRepo",
        return_value=repo,
    ):
        service = TaskProgressService(uow=MagicMock())
        await service.record_submission_result(
            session,  # type: ignore[arg-type]
            user_id=1,
            submission_id=12,
            task_id=2,
            passed=True,
        )

    assert row.attempts_count == 3
    assert row.passed_count == 2


@pytest.mark.asyncio
async def test_task_progress_service__get_progress_for_task_returns_not_started() -> None:
    session = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
    uow = MagicMock()
    uow.session = session
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    service = TaskProgressService(uow=uow)

    progress = await service.get_progress_for_task(user_id=1, task_id=99)

    assert progress.task_id == 99
    assert progress.progress_status == PROGRESS_STATUS_NOT_STARTED
    assert progress.attempts_count == 0


@pytest.mark.asyncio
async def test_task_progress_service__get_progress_for_task_maps_existing_row() -> None:
    row = TaskProgressModel(
        user_id=1,
        task_id=2,
        attempts_count=2,
        passed_count=0,
        last_status="failed",
        last_submission_id=5,
        last_attempt_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    session = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=row)))
    uow = MagicMock()
    uow.session = session
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    service = TaskProgressService(uow=uow)

    progress = await service.get_progress_for_task(user_id=1, task_id=2)

    assert progress.progress_status == PROGRESS_STATUS_FAILED
    assert progress.attempts_count == 2
    assert progress.passed_count == 0
    assert progress.failed_count == 2
    assert progress.last_submission_id == 5
