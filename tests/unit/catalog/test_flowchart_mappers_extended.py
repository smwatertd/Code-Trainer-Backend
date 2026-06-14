from __future__ import annotations

import pytest

from src.features.catalog.mappers import _public_flowchart_payload


def test_public_flowchart_payload__exposes_student_metadata_hides_flow_spec() -> None:
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

    assert "test_cases" in payload
    assert payload["test_cases"] == [{"inputs": "", "output": "hello"}]
    assert "constructions" in payload
    assert payload["constructions"] == ["for_loop"]
    assert "flow_spec" not in payload
    assert payload["flowchart_mode"] == "code_to_flowchart"
    assert payload["source_code"] == "print('hello')"
    assert "source_code_by_language" in payload
    assert "python" in payload["source_code_by_language"]
    assert "cpp" in payload["source_code_by_language"]


def test_public_flowchart_payload__synthesizes_all_languages() -> None:
    payload = _public_flowchart_payload(
        {
            "flowchart_mode": "code_to_flowchart",
            "source_code": "for i in range(3):\n    print(i)",
            "flow_spec": {"required_sequence": ["start", "loop", "output", "end"]},
            "test_cases": [{"inputs": "", "output": "0\n1\n2\n"}],
        }
    )

    variants = payload["source_code_by_language"]
    assert set(variants) >= {"python", "cpp", "pascal", "java", "csharp"}
    assert "range(3)" in variants["python"] or "range(3)" in variants["cpp"]


def test_public_flowchart_payload__preserves_topics_and_mode() -> None:
    payload = _public_flowchart_payload(
        {
            "flowchart_mode": "code_to_flowchart",
            "topics": ["flowchart", "loops"],
            "source_code": "print('x')",
            "flow_spec": {"required_sequence": ["start", "output", "end"]},
        }
    )

    assert payload["flowchart_mode"] == "code_to_flowchart"
    assert payload["topics"] == ["flowchart", "loops"]
