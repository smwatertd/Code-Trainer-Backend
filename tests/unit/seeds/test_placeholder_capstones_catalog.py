from __future__ import annotations

from migrations.seeds.placeholder_capstones_catalog import (
    PLACEHOLDER_CAPSTONES_CATALOG,
    PLACEHOLDER_CAPSTONES_SIZE,
    build_placeholder_capstones_catalog,
)
from migrations.seeds.task_catalog_seed import CATALOG_SIZE, build_task_catalog


def test_placeholder_capstones_catalog__size_and_ids() -> None:
    tasks = build_placeholder_capstones_catalog()

    assert PLACEHOLDER_CAPSTONES_SIZE == 3
    assert len(tasks) == 3
    assert [task["id"] for task in tasks] == [331, 332, 333]


def test_placeholder_capstones_catalog__task_shape() -> None:
    task = PLACEHOLDER_CAPSTONES_CATALOG[0]

    assert task["task_type"] == "task_fill_placeholders"
    assert task["payload"]["placeholder_template"]
    assert task["payload"]["placeholder_bank"]
    assert task["payload"]["test_cases"]


def test_main_catalog__does_not_overlap_placeholder_ids() -> None:
    main_ids = {task["id"] for task in build_task_catalog()}

    assert CATALOG_SIZE == 128
    assert 331 not in main_ids
    assert 332 not in main_ids
    assert 333 not in main_ids
