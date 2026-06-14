from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.catalog.repos.task_repo import TaskRepo


@pytest.mark.asyncio(loop_scope="session")
async def test_task_repo__list_public_returns_seeded_tasks(session: AsyncSession) -> None:
    repo = TaskRepo(session)
    tasks = await repo.list_public()

    assert len(tasks) >= 2
    assert {task.id for task in tasks} >= {1, 2}


@pytest.mark.asyncio(loop_scope="session")
async def test_task_repo__get_public_block_reorder(session: AsyncSession) -> None:
    repo = TaskRepo(session)
    task = await repo.get_public(2)

    assert task is not None
    assert task.task_type == "task_build_from_blocks"
    assert task.payload["correct_order"] == [1, 0]
