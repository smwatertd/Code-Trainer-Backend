from src.shared.execution.checking.flow_public_response import (
    public_flowchart_check_result,
    sanitize_public_pattern_errors,
)


def test_sanitize_public_pattern_errors__strips_detail() -> None:
    errors = [
        {
            "type": "FLOW_SEQUENCE_MISMATCH",
            "text": "Проверьте порядок.",
            "detail": "Ожидаемый порядок: Начало → Цикл → Конец.",
        }
    ]

    sanitized = sanitize_public_pattern_errors(errors)

    assert sanitized == [{"type": "FLOW_SEQUENCE_MISMATCH", "text": "Проверьте порядок."}]
    assert "detail" not in sanitized[0]


def test_public_flowchart_check_result__removes_flow_debug() -> None:
    result = public_flowchart_check_result(
        {
            "success": False,
            "pattern_errors": [{"type": "FLOW_EMPTY", "text": "Пусто.", "detail": "internal"}],
            "flow_debug": {"expected_sequence": "Начало → Конец"},
        }
    )

    assert "flow_debug" not in result
    assert result["pattern_errors"] == [{"type": "FLOW_EMPTY", "text": "Пусто."}]
