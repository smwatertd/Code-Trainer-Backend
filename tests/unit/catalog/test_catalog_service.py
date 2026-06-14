from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.core.either import Err, Ok
from src.core.either.failures import NotFoundFailure
from src.features.catalog.models import TaskModel
from src.features.catalog.services.catalog_service import CatalogService
from tests.unit.conftest import FakeUoW


@pytest.fixture
def catalog_service() -> CatalogService:
    return CatalogService(uow=FakeUoW(session=AsyncMock()))


@pytest.mark.asyncio
async def test_catalog_service__list_public_tasks(catalog_service: CatalogService) -> None:
    task = TaskModel(
        id=2,
        title="Public task",
        description="desc",
        task_type="task_build_from_blocks",
        visibility="public",
        payload={"blocks": []},
        is_deleted=False,
    )

    with patch("src.features.catalog.services.catalog_service.TaskRepo") as repo_cls:
        repo_cls.return_value.list_public = AsyncMock(return_value=[task])

        result = await catalog_service.list_public_tasks()

    assert isinstance(result, Ok)
    assert len(result.value) == 1
    assert result.value[0].id == 2
    assert result.value[0].title == "Public task"


@pytest.mark.asyncio
async def test_catalog_service__get_public_task_not_found(catalog_service: CatalogService) -> None:
    with patch("src.features.catalog.services.catalog_service.TaskRepo") as repo_cls:
        repo_cls.return_value.get_public = AsyncMock(return_value=None)

        result = await catalog_service.get_public_task(404)

    assert isinstance(result, Err)
    assert isinstance(result.error, NotFoundFailure)


@pytest.mark.asyncio
async def test_catalog_service__get_internal_task_rejects_deleted(catalog_service: CatalogService) -> None:
    deleted = TaskModel(
        id=3,
        title="Deleted",
        description="desc",
        task_type="translation",
        visibility="public",
        payload={},
        is_deleted=True,
    )

    with patch("src.features.catalog.services.catalog_service.TaskRepo") as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=deleted)

        result = await catalog_service.get_internal_task(3)

    assert isinstance(result, Err)
    assert isinstance(result.error, NotFoundFailure)


@pytest.mark.asyncio
async def test_catalog_service__get_internal_task_success(catalog_service: CatalogService) -> None:
    task = TaskModel(
        id=2,
        title="Reorder",
        description="desc",
        task_type="task_build_from_blocks",
        visibility="public",
        payload={"correct_order": [1, 0]},
        is_deleted=False,
    )

    with patch("src.features.catalog.services.catalog_service.TaskRepo") as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=task)

        result = await catalog_service.get_internal_task(2)

    assert isinstance(result, Ok)
    assert result.value.task_type == "task_build_from_blocks"
    assert result.value.payload == {"correct_order": [1, 0]}
