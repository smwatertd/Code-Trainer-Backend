from __future__ import annotations

import pytest

from migrations.seeds.task_catalog_seed import build_task_catalog
from src.features.catalog.mappers import _public_flowchart_payload, _public_payload

FLOWCHART_TASK_IDS = [3, 6, *range(39, 51)]

HIDDEN_FLOWCHART_KEYS = {
    "test_cases",
    "constructions",
    "flow_spec",
    "correct_order",
    "expected_code",
}


@pytest.mark.parametrize("task_id", FLOWCHART_TASK_IDS)
def test_public_flowchart_payload__hides_grading_secrets_for_seed_tasks(task_id: int) -> None:
    catalog = {item["id"]: item for item in build_task_catalog()}
    payload = _public_flowchart_payload(dict(catalog[task_id]["payload"]))

    for key in HIDDEN_FLOWCHART_KEYS:
        assert key not in payload, f"task {task_id} leaked {key}"


@pytest.mark.parametrize("task_id", FLOWCHART_TASK_IDS)
def test_public_payload__flowchart_tasks_expose_reference_code(task_id: int) -> None:
    catalog = {item["id"]: item for item in build_task_catalog()}
    task = catalog[task_id]
    payload = _public_payload(task["task_type"], dict(task["payload"]))

    assert payload.get("flowchart_mode") == "code_to_flowchart"
    assert payload.get("source_code")


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
