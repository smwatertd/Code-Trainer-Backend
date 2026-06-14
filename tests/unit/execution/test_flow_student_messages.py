from __future__ import annotations

import pytest

from src.shared.execution.checking.flow_student_messages import (
    STUDENT_FLOW_ERROR_MESSAGES,
    student_flow_error_text,
)


@pytest.mark.parametrize("error_type", list(STUDENT_FLOW_ERROR_MESSAGES))
def test_student_flow_error_text__covers_all_known_types(error_type: str) -> None:
    text = student_flow_error_text(error_type)
    assert text
    assert text == STUDENT_FLOW_ERROR_MESSAGES[error_type]


def test_student_flow_error_text__fallback_for_unknown() -> None:
    assert student_flow_error_text("FLOW_UNKNOWN", fallback="custom") == "custom"


def test_student_flow_error_messages__source_mismatch_present() -> None:
    assert "FLOW_SOURCE_MISMATCH" in STUDENT_FLOW_ERROR_MESSAGES
