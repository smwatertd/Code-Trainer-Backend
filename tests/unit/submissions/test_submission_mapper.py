from __future__ import annotations

from src.features.submissions.mappers import to_detail
from src.features.submissions.models import (
    SubmissionLintErrorModel,
    SubmissionModel,
    SubmissionPatternErrorModel,
    SubmissionTestResultModel,
)


def test_to_detail__splits_compiler_and_linter_errors() -> None:
    model = SubmissionModel(
        id=1,
        user_id=7,
        task_id=2,
        language="python",
        code="print(1)",
        status="success",
        success=True,
    )
    model.linter_errors = [
        SubmissionLintErrorModel(id=1, submission_id=1, error_type="COMPILER", text="syntax"),
        SubmissionLintErrorModel(id=2, submission_id=1, error_type="LINT", text="style"),
    ]
    model.pattern_errors = [
        SubmissionPatternErrorModel(id=1, submission_id=1, error_type="PATTERN", text="missing for"),
    ]
    model.test_results = [
        SubmissionTestResultModel(
            id=1,
            submission_id=1,
            case_number=1,
            status="passed",
            inputs="",
            expected="1",
            actual="1",
            message="",
        ),
    ]

    dto = to_detail(model)

    assert dto.compiler_errors == [{"type": "COMPILER", "text": "syntax"}]
    assert dto.linter_errors == [{"type": "LINT", "text": "style"}]
    assert dto.pattern_errors == [{"type": "PATTERN", "text": "missing for"}]
    assert dto.test_results[0]["case"] == 1
    assert dto.code == "print(1)"


def test_to_detail__restores_solver_input_from_payload() -> None:
    model = SubmissionModel(
        id=2,
        user_id=7,
        task_id=2,
        language="cpp",
        code="int main() { return 0; }",
        input_payload={
            "block_order": [1, 0],
            "nodes": [{"id": "n1", "type": "start", "x": 0, "y": 0, "text": "start"}],
            "edges": [{"source": "n1", "target": "n2"}],
            "flow": [{"id": "n1", "type": "start"}],
        },
        status="failed",
        success=False,
    )

    dto = to_detail(model)

    assert dto.code == "int main() { return 0; }"
    assert dto.block_order == [1, 0]
    assert dto.nodes == [{"id": "n1", "type": "start", "x": 0, "y": 0, "text": "start"}]
    assert dto.edges == [{"source": "n1", "target": "n2"}]
    assert dto.flow == [{"id": "n1", "type": "start"}]


def test_to_detail__routes_validation_errors_to_compiler_bucket() -> None:
    model = SubmissionModel(
        id=3,
        user_id=7,
        task_id=2,
        language="python",
        code="print(1)",
        status="failed",
        success=False,
    )
    model.linter_errors = [
        SubmissionLintErrorModel(
            id=1,
            submission_id=3,
            error_type="VALIDATION",
            text="Блоки расставлены в неверном порядке.",
        ),
        SubmissionLintErrorModel(id=2, submission_id=3, error_type="LINT", text="style"),
    ]

    dto = to_detail(model)

    assert dto.compiler_errors == [{"type": "VALIDATION", "text": "Блоки расставлены в неверном порядке."}]
    assert dto.linter_errors == [{"type": "LINT", "text": "style"}]
