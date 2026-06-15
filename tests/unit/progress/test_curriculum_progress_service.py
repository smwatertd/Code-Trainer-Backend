from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.features.progress.models import StudentCurriculumProgressModel, TaskCurriculumLinkModel
from src.features.progress.services.curriculum_progress_service import CurriculumProgressService
from tests.unit.conftest import FakeUoW


@pytest.mark.asyncio
async def test_curriculum_progress_service__skips_task_without_link() -> None:
    session = AsyncMock()
    service = CurriculumProgressService(uow=FakeUoW(session=session))
    link_repo = AsyncMock()
    link_repo.get_primary_by_task_and_language = AsyncMock(return_value=None)

    with patch(
        "src.features.progress.services.curriculum_progress_service.TaskCurriculumLinkRepo",
        return_value=link_repo,
    ):
        await service.record_submission_result(
            session,
            user_id=1,
            submission_id=10,
            task_id=99,
            language="python",
            passed=True,
        )

    link_repo.get_primary_by_task_and_language.assert_awaited_once_with(99, "python")


@pytest.mark.asyncio
async def test_curriculum_progress_service__records_first_pass() -> None:
    session = AsyncMock()
    service = CurriculumProgressService(uow=FakeUoW(session=session))
    link = TaskCurriculumLinkModel(
        id=1,
        task_id=4,
        language="python",
        learning_concept_id="loops",
        technical_concept_id="for_loop",
        exercise_pattern_id="tr_pattern_translation",
        action="implement",
        is_primary=True,
    )
    link_repo = AsyncMock()
    link_repo.get_primary_by_task_and_language = AsyncMock(return_value=link)
    progress_repo = AsyncMock()
    progress_repo.get_by_user_and_task = AsyncMock(return_value=None)
    progress_repo.add = AsyncMock(side_effect=lambda row: row)

    with (
        patch(
            "src.features.progress.services.curriculum_progress_service.TaskCurriculumLinkRepo",
            return_value=link_repo,
        ),
        patch(
            "src.features.progress.services.curriculum_progress_service.CurriculumProgressRepo",
            return_value=progress_repo,
        ),
    ):
        await service.record_submission_result(
            session,
            user_id=7,
            submission_id=20,
            task_id=4,
            language="python",
            passed=True,
        )

    created: StudentCurriculumProgressModel = progress_repo.add.await_args.args[0]
    assert created.passed_count == 1
    assert created.attempts_count == 1
    assert created.learning_concept_id == "loops"


@pytest.mark.asyncio
async def test_curriculum_progress_service__aggregates_learning_concept_progress() -> None:
    links = [
        TaskCurriculumLinkModel(
            id=1,
            task_id=4,
            language="python",
            learning_concept_id="loops",
            technical_concept_id="for_loop",
            exercise_pattern_id="tr_pattern_translation",
            action="implement",
            is_primary=True,
        ),
    ]
    rows = [
        StudentCurriculumProgressModel(
            user_id=1,
            task_id=4,
            language="python",
            learning_concept_id="loops",
            technical_concept_id="for_loop",
            action="implement",
            exercise_pattern_id="tr_pattern_translation",
            attempts_count=2,
            passed_count=1,
        ),
    ]
    session = AsyncMock()
    service = CurriculumProgressService(uow=FakeUoW(session=session))
    link_repo = AsyncMock()
    link_repo.list_for_learning_concept = AsyncMock(return_value=links)
    progress_repo = AsyncMock()
    progress_repo.list_for_user_tasks = AsyncMock(return_value=rows)

    with (
        patch(
            "src.features.progress.services.curriculum_progress_service.TaskCurriculumLinkRepo",
            return_value=link_repo,
        ),
        patch(
            "src.features.progress.services.curriculum_progress_service.CurriculumProgressRepo",
            return_value=progress_repo,
        ),
    ):
        result = await service.get_learning_concept_progress(
            user_id=1,
            language="python",
            learning_concept_id="loops",
        )

    assert result.total_tasks == 1
    assert result.passed_tasks == 1
    assert result.progress_percent == 100.0
    assert result.by_technical_concept["for_loop"].passed_tasks == 1
    assert result.by_task_id[4].progress_status == "passed"
