from __future__ import annotations

from migrations.seeds.basic_program_catalog import (
    BASIC_PROGRAM_CATALOG,
    build_basic_program_catalog,
)
from migrations.seeds.course_batch_25_74_catalog import (
    COURSE_BATCH_25_74_SIZE,
    build_course_batch_25_74_catalog,
)
from migrations.seeds.course_batch_75_124_catalog import (
    COURSE_BATCH_75_124_SIZE,
    build_course_batch_75_124_catalog,
)
from migrations.seeds.course_batch_125_174_catalog import (
    COURSE_BATCH_125_174_SIZE,
    build_course_batch_125_174_catalog,
)
from migrations.seeds.course_batch_175_224_catalog import (
    COURSE_BATCH_175_224_SIZE,
    build_course_batch_175_224_catalog,
)
from migrations.seeds.course_batch_225_270_catalog import (
    COURSE_BATCH_225_270_SIZE,
    build_course_batch_225_270_catalog,
)
from migrations.seeds.input_output_catalog import (
    INPUT_OUTPUT_CATALOG_SIZE,
    build_input_output_catalog,
)

TaskRow = dict

BASIC_PROGRAM_SIZE = len(BASIC_PROGRAM_CATALOG)
COURSE_BATCH_PREV_SIZE = 224
CATALOG_SIZE = 270
FULL_CATALOG_SIZE = CATALOG_SIZE


def _row(
    task_id: int,
    title: str,
    description: str,
    difficulty: str,
    task_type: str,
    payload: dict,
) -> TaskRow:
    return {
        "id": task_id,
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "task_type": task_type,
        "visibility": "public",
        "workflow_status": "active",
        "is_deleted": False,
        "payload": payload,
    }


def _translation(
    *,
    topics: list[str],
    source_code: str | None = None,
    target_language: str = "pascal",
    test_cases: list[dict] | None = None,
    constructions: list[str] | None = None,
    kind: str | None = None,
    template: str = "",
) -> dict:
    payload: dict = {"topics": topics}
    if source_code is not None:
        payload["source_language"] = "python"
        payload["source_code"] = source_code
    if target_language:
        payload["target_language"] = target_language
    if template:
        payload["template"] = template
    if test_cases:
        payload["test_cases"] = test_cases
    if constructions:
        payload["constructions"] = constructions
    if kind:
        payload["kind"] = kind
    return payload


def build_task_catalog() -> list[TaskRow]:
    basic = build_basic_program_catalog()
    io_tasks = build_input_output_catalog()
    batch_25_74 = build_course_batch_25_74_catalog()
    batch_75_124 = build_course_batch_75_124_catalog()
    batch_125_174 = build_course_batch_125_174_catalog()
    batch_175_224 = build_course_batch_175_224_catalog()
    batch_225_270 = build_course_batch_225_270_catalog()
    if len(basic) != BASIC_PROGRAM_SIZE:
        raise RuntimeError(f"Expected {BASIC_PROGRAM_SIZE} basic tasks, got {len(basic)}")
    if len(io_tasks) != INPUT_OUTPUT_CATALOG_SIZE:
        raise RuntimeError(
            f"Expected {INPUT_OUTPUT_CATALOG_SIZE} input/output tasks, got {len(io_tasks)}"
        )
    if len(batch_25_74) != COURSE_BATCH_25_74_SIZE:
        raise RuntimeError(
            f"Expected {COURSE_BATCH_25_74_SIZE} course batch 25-74 tasks, got {len(batch_25_74)}"
        )
    if len(batch_75_124) != COURSE_BATCH_75_124_SIZE:
        raise RuntimeError(
            f"Expected {COURSE_BATCH_75_124_SIZE} course batch 75-124 tasks, got {len(batch_75_124)}"
        )
    if len(batch_125_174) != COURSE_BATCH_125_174_SIZE:
        raise RuntimeError(
            f"Expected {COURSE_BATCH_125_174_SIZE} course batch 125-174 tasks, got {len(batch_125_174)}"
        )
    if len(batch_175_224) != COURSE_BATCH_175_224_SIZE:
        raise RuntimeError(
            f"Expected {COURSE_BATCH_175_224_SIZE} course batch 175-224 tasks, got {len(batch_175_224)}"
        )
    if len(batch_225_270) != COURSE_BATCH_225_270_SIZE:
        raise RuntimeError(
            f"Expected {COURSE_BATCH_225_270_SIZE} course batch 225-270 tasks, got {len(batch_225_270)}"
        )
    tasks = (
        basic
        + io_tasks
        + batch_25_74
        + batch_75_124
        + batch_125_174
        + batch_175_224
        + batch_225_270
    )
    if len(tasks) != CATALOG_SIZE:
        raise RuntimeError(f"Expected {CATALOG_SIZE} tasks, got {len(tasks)}")
    return tasks


CURRICULUM_LINKS: list[dict] = []

# Legacy export for historical Alembic revisions (flowchart patch migrations).
FLOWCHART_TEST_CASES: dict[int, list[dict[str, str]]] = {}

TASK_CATALOG_SEED = build_task_catalog()
