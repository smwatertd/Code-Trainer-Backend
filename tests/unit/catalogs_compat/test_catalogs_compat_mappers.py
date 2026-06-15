from __future__ import annotations

from datetime import UTC, datetime

from src.features.assignment_sets.repos.assignment_set_repo import AssignmentSetDTO, AssignmentSetItemDTO
from src.features.catalog.models import TaskModel
from src.features.catalogs_compat.mappers import catalog_from_set, task_to_legacy


def test_catalog_from_set__maps_assignment_set_fields() -> None:
    created_at = datetime(2026, 6, 13, 12, 0, tzinfo=UTC)
    dto = AssignmentSetDTO(
        id=7,
        name="Week 1",
        description="Loops",
        teacher_id=2,
        visibility="private",
        group_id=11,
        is_archived=False,
        items=(AssignmentSetItemDTO(task_id=4, sort_order=0), AssignmentSetItemDTO(task_id=5, sort_order=1)),
        created_at=created_at,
        deadline_at=None,
    )

    catalog = catalog_from_set(dto)

    assert catalog.id == 7
    assert catalog.title == "Week 1"
    assert catalog.description == "Loops"
    assert catalog.task_count == 2
    assert catalog.visibility == "private"
    assert catalog.group_id == 11
    assert catalog.created_at == created_at


def test_task_to_legacy__maps_task_and_catalog_membership() -> None:
    model = TaskModel(
        id=4,
        title="Save age",
        description="Fix the program",
        difficulty="medium",
        task_type="translation",
        visibility="public",
        workflow_status="active",
        is_deleted=False,
        payload={"language": "pascal", "source_language": "python"},
    )

    legacy = task_to_legacy(model, catalog_ids=[7, 9])

    assert legacy.id == 4
    assert legacy.title == "Save age"
    assert legacy.content == "Fix the program"
    assert legacy.type_id == "translation"
    assert legacy.difficulty == "medium"
    assert legacy.language == "pascal"
    assert legacy.languages == ["pascal", "python"]
    assert legacy.catalog_ids == [7, 9]
    assert legacy.is_assigned is True


def test_task_to_legacy__marks_unassigned_tasks() -> None:
    model = TaskModel(
        id=1,
        title="Hello",
        description="",
        difficulty="easy",
        task_type="translation",
        visibility="public",
        workflow_status="active",
        is_deleted=False,
        payload={"language": "python"},
    )

    legacy = task_to_legacy(model)

    assert legacy.catalog_ids == []
    assert legacy.is_assigned is False
