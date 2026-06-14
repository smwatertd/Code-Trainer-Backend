from __future__ import annotations

import pytest

from src.features.tasks.domain.enums import TaskFamily, task_family_from_legacy_type


@pytest.mark.parametrize(
    ("legacy", "expected"),
    [
        ("translation", TaskFamily.TRANSLATION),
        ("task_write_from_description", TaskFamily.TRANSLATION),
        ("algorithm", TaskFamily.TRANSLATION),
        ("task_build_from_blocks", TaskFamily.BLOCK_REORDER),
        ("task_flowchart_to_code", TaskFamily.FLOWCHART),
        ("unknown", None),
    ],
)
def test_task_family_from_legacy_type(legacy: str, expected: TaskFamily | None) -> None:
    assert task_family_from_legacy_type(legacy) is expected
