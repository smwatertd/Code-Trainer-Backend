from __future__ import annotations

from src.features.catalog.mappers import _public_payload, to_detail
from src.features.catalog.models import TaskModel


def test_public_payload__hides_block_reorder_answers() -> None:
    payload = _public_payload(
        "task_build_from_blocks",
        {
            "blocks": ["print('a')", "print('b')"],
            "correct_order": [1, 0],
            "expected_code": "print('b')\nprint('a')",
            "language": "python",
        },
    )

    assert "correct_order" not in payload
    assert "expected_code" not in payload
    assert "blocks_by_language" in payload
    assert "code_examples" in payload
    assert payload["blocks_by_language"]["cpp"][0]["content"] == 'cout << "a" << endl;'
    assert payload["blocks_count"] == 2


def test_public_payload__keeps_explicit_language_variants() -> None:
    payload = _public_payload(
        "task_build_from_blocks",
        {
            "blocks": ["print('a')", "print('b')"],
            "blocks_by_language": {
                "python": ["print('a')", "print('b')"],
                "cpp": ['cout << "a" << endl;', 'cout << "b" << endl;'],
            },
            "language": "python",
        },
    )

    assert payload["blocks_by_language"]["cpp"][0]["content"] == 'cout << "a" << endl;'


def test_public_payload__hides_write_from_description_answers() -> None:
    payload = _public_payload(
        "task_write_from_description",
        {
            "target_language": "python",
            "template": "print('')",
            "problem_statement": "Выведите 42.",
            "test_cases": [{"inputs": "", "output": "42"}],
            "constructions": ["for_loop"],
            "source_code": "secret",
        },
    )

    assert payload == {
        "target_language": "python",
        "template": "print('')",
        "problem_statement": "Выведите 42.",
        "test_cases": [{"inputs": "", "output": "42"}],
        "constructions": ["for_loop"],
    }


def test_to_detail__maps_model() -> None:
    model = TaskModel(
        id=2,
        title="Reorder",
        description="desc",
        difficulty="easy",
        task_type="task_build_from_blocks",
        visibility="public",
        workflow_status="active",
        is_deleted=False,
        payload={"blocks": ["a", "b"], "language": "python"},
    )

    dto = to_detail(model)

    assert dto.id == 2
    assert dto.task_type == "task_build_from_blocks"
    assert len(dto.payload["blocks"]) == 2
