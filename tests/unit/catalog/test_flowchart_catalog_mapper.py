from src.features.catalog.mappers import _public_flowchart_payload


def test_public_flowchart_payload__hides_test_cases_and_answer_patterns() -> None:
    payload = _public_flowchart_payload(
        {
            "flowchart_mode": "code_to_flowchart",
            "source_code": "print('hello')",
            "test_cases": [{"inputs": "", "output": "hello"}],
            "constructions": ["for_loop"],
            "flow_spec": {
                "required_sequence": ["start", "output", "end"],
                "required_text_checks": [{"type": "output", "contains_any": ["hello"]}],
            },
        }
    )

    assert "test_cases" not in payload
    assert "constructions" not in payload
    assert "flow_spec" not in payload
    assert payload["flowchart_mode"] == "code_to_flowchart"
    assert payload["source_code"] == "print('hello')"
    assert "source_code_by_language" in payload
    assert "python" in payload["source_code_by_language"]
    assert "cpp" in payload["source_code_by_language"]
