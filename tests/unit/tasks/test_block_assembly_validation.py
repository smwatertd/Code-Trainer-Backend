from __future__ import annotations

from src.core.either import Err, Ok
from src.features.catalog.mappers import _public_block_reorder_payload
from src.features.tasks.services.block_reorder_validator import validate_block_order_structure


def test_public_block_reorder_payload__exposes_language_variants_for_fragment_tasks() -> None:
    payload = _public_block_reorder_payload(
        {
            "blocks": ["=", "print"],
            "template": "x {0} 1",
            "language": "python",
            "language_variants": {
                "cpp": {
                    "template": "int x {0} 1;",
                    "blocks": ["=", "cout << x;"],
                }
            },
        }
    )

    assert payload["template"] == "x {0} 1"
    assert payload["language_variants"]["cpp"]["template"] == "int x {0} 1;"
    assert payload["language_variants"]["cpp"]["blocks"] == ["=", "cout << x;"]


def test_validate_block_order_structure__accepts_fragment_assembled_code() -> None:
    expected = "x = 1\ny = 2\nprint(x)"

    result = validate_block_order_structure(
        submitted_order=[0, 0, 1],
        correct_order=[0, 0, 1],
        assembled_code=expected,
        expected_code=expected,
    )

    assert isinstance(result, Ok)


def test_validate_block_order_structure__rejects_fragment_code_mismatch() -> None:
    result = validate_block_order_structure(
        submitted_order=[0, 0, 1],
        correct_order=[0, 0, 1],
        assembled_code="x = 1\ny = 2\nprint(y)",
        expected_code="x = 1\ny = 2\nprint(x)",
    )

    assert isinstance(result, Err)
    assert result.error.code == "VALIDATION_ERROR"


def test_validate_block_order_structure__requires_assembled_code_for_freeform_python() -> None:
    result = validate_block_order_structure(
        submitted_order=[0, 1, 2, 3],
        correct_order=[3, 2, 0, 1],
        assembled_code="",
        expected_code="total=135\nh=total//60\nm=total%60\nprint(h, m)",
    )

    assert isinstance(result, Err)
    assert result.error.code == "VALIDATION_ERROR"
