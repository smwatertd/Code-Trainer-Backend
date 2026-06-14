from __future__ import annotations

from pathlib import Path

import pytest

from src.shared.curriculum.exceptions import CurriculumLinkValidationError
from src.shared.curriculum.link_validator import validate_task_curriculum_link_metadata

_CURRICULUM_ROOT = Path(__file__).resolve().parents[3] / "resources" / "curriculum"


def test_validate_task_curriculum_link_metadata__python_for_loop_implement() -> None:
    metadata = validate_task_curriculum_link_metadata(
        _CURRICULUM_ROOT,
        language="python",
        technical_concept_id="for_loop",
        exercise_pattern_id="tr_pattern_translation",
    )

    assert metadata.language == "python"
    assert metadata.learning_concept_id == "loops"
    assert metadata.technical_concept_id == "for_loop"
    assert metadata.action == "implement"


def test_validate_task_curriculum_link_metadata__pascal_counted_loop_translate() -> None:
    metadata = validate_task_curriculum_link_metadata(
        _CURRICULUM_ROOT,
        language="pascal",
        technical_concept_id="counted_loop",
        exercise_pattern_id="tr_python_to_pascal_code",
    )

    assert metadata.action == "translate"
    assert metadata.learning_concept_id == "loops"


def test_validate_task_curriculum_link_metadata__rejects_unknown_pattern() -> None:
    with pytest.raises(CurriculumLinkValidationError, match="Unknown exercise pattern"):
        validate_task_curriculum_link_metadata(
            _CURRICULUM_ROOT,
            language="python",
            technical_concept_id="for_loop",
            exercise_pattern_id="tr_does_not_exist",
        )


def test_validate_task_curriculum_link_metadata__python_if_else_implement() -> None:
    metadata = validate_task_curriculum_link_metadata(
        _CURRICULUM_ROOT,
        language="python",
        technical_concept_id="if_else",
        exercise_pattern_id="tr_pattern_translation",
    )

    assert metadata.learning_concept_id == "conditions"
    assert metadata.action == "implement"


def test_validate_task_curriculum_link_metadata__python_function_definition() -> None:
    metadata = validate_task_curriculum_link_metadata(
        _CURRICULUM_ROOT,
        language="python",
        technical_concept_id="function_definition",
        exercise_pattern_id="tr_pattern_translation",
    )

    assert metadata.learning_concept_id == "functions"


def test_validate_task_curriculum_link_metadata__rejects_disabled_action_pattern() -> None:
    with pytest.raises(CurriculumLinkValidationError, match="disabled|not allowed"):
        validate_task_curriculum_link_metadata(
            _CURRICULUM_ROOT,
            language="pascal",
            technical_concept_id="loop_control",
            exercise_pattern_id="asm_flowchart_to_blocks",
        )
