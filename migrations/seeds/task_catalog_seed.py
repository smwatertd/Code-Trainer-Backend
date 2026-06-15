from __future__ import annotations

from migrations.seeds.tc42_course_catalog_generated import (
    TC42_CATALOG_SIZE,
    build_tc42_course_catalog,
)
from migrations.seeds.tc42_curriculum_links import CURRICULUM_LINKS_SEED

TaskRow = dict

CATALOG_SIZE = TC42_CATALOG_SIZE
FULL_CATALOG_SIZE = CATALOG_SIZE

# Legacy constants for historical Alembic revisions (already applied in existing DBs).
BASIC_PROGRAM_SIZE = 12
COURSE_BATCH_PREV_SIZE = 24


def build_task_catalog() -> list[TaskRow]:
    tasks = build_tc42_course_catalog()
    if len(tasks) != CATALOG_SIZE:
        raise RuntimeError(f"Expected {CATALOG_SIZE} TC42 tasks, got {len(tasks)}")
    return tasks


# Historical Alembic revision r8s9t0u1v2 runs before the multilang constraint migration;
# keep python-only links so (task_id, exercise_pattern_id) uniqueness still holds.
CURRICULUM_LINKS: list[dict] = [
    row for row in CURRICULUM_LINKS_SEED if row["language"] == "python"
]

FLOWCHART_TEST_CASES: dict[int, list[dict[str, str]]] = {}

TASK_CATALOG_SEED = build_task_catalog()
