from __future__ import annotations

import pytest

from src.core.either import Err, Ok
from src.core.either.failures import ValidationFailure
from src.features.tasks.services.block_reorder_validator import (
    matches_correct_order,
    validate_block_order_answer,
    validate_block_order_structure,
)


class TestBlockReorderValidatorExamples:
    """Примеры доменной валидации block_reorder — как будет работать demo/catalog."""

    def test_example__correct_order_passes(self) -> None:
        result = validate_block_order_answer(
            submitted_order=[1, 0, 2],
            correct_order=[1, 0, 2],
            blocks_count=3,
        )

        assert isinstance(result, Ok)
        assert result.value.as_list() == [1, 0, 2]

    def test_example__wrong_order_fails_before_execution(self) -> None:
        result = validate_block_order_answer(
            submitted_order=[0, 1, 2],
            correct_order=[1, 0, 2],
            blocks_count=3,
        )

        assert isinstance(result, Err)
        assert result.error.code == "VALIDATION_ERROR"
        assert "неверном порядке" in result.error.message.lower()

    def test_example__structural_check_compares_assembled_code(self) -> None:
        blocks = ["print('a')", "print('b')"]
        expected = "\n".join(blocks[i] for i in [1, 0])

        result = validate_block_order_structure(
            submitted_order=[1, 0],
            correct_order=[1, 0],
            assembled_code=expected,
            expected_code=expected,
        )

        assert isinstance(result, Ok)

    def test_example__structural_check_rejects_mismatched_code(self) -> None:
        result = validate_block_order_structure(
            submitted_order=[1, 0],
            correct_order=[1, 0],
            assembled_code="print('wrong')",
            expected_code="print('b')\nprint('a')",
        )

        assert isinstance(result, Err)
        assert isinstance(result.error, ValidationFailure)

    @pytest.mark.parametrize(
        ("submitted", "correct", "expected"),
        [
            ([0, 1], [0, 1], True),
            ([1, 0], [0, 1], False),
            ([0, 1, 2], [0, 1], False),
        ],
    )
    def test_example__matches_correct_order_helper(
        self,
        submitted: list[int],
        correct: list[int],
        expected: bool,
    ) -> None:
        assert matches_correct_order(submitted, correct) is expected
