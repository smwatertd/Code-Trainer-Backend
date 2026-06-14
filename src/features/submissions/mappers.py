from __future__ import annotations

from typing import Any

from src.features.submissions.domain.dto import SubmissionDetailDTO, SubmissionHistoryItemDTO
from src.features.submissions.models import SubmissionModel

_LINTER_ERROR_TYPES = frozenset({"LINTER", "LINT"})


def _solver_input(model: SubmissionModel) -> dict[str, Any]:
    payload = model.input_payload if isinstance(model.input_payload, dict) else {}
    block_order = payload.get("block_order")
    nodes = payload.get("nodes")
    edges = payload.get("edges")
    flow = payload.get("flow")
    return {
        "code": model.code,
        "block_order": block_order if isinstance(block_order, list) else None,
        "nodes": nodes if isinstance(nodes, list) else None,
        "edges": edges if isinstance(edges, list) else None,
        "flow": flow if isinstance(flow, list) else None,
    }


def to_detail(model: SubmissionModel) -> SubmissionDetailDTO:
    compiler_errors = [
        {"type": item.error_type, "text": item.text}
        for item in model.linter_errors
        if item.error_type.upper() not in _LINTER_ERROR_TYPES
    ]
    linter_errors = [
        {"type": item.error_type, "text": item.text}
        for item in model.linter_errors
        if item.error_type.upper() in _LINTER_ERROR_TYPES
    ]
    solver_input = _solver_input(model)
    return SubmissionDetailDTO(
        id=model.id,
        user_id=model.user_id,
        task_id=model.task_id,
        language=model.language,
        status=model.status,
        success=model.success,
        created_at=model.created_at.isoformat() if model.created_at else None,
        updated_at=model.updated_at.isoformat() if model.updated_at else None,
        compiler_errors=compiler_errors,
        linter_errors=linter_errors,
        pattern_errors=[{"type": item.error_type, "text": item.text} for item in model.pattern_errors],
        test_results=[
            {
                "case": item.case_number,
                "status": item.status,
                "inputs": item.inputs,
                "expected": item.expected,
                "actual": item.actual,
                "message": item.message,
                "duration_ms": item.duration_ms,
            }
            for item in model.test_results
        ],
        duration_ms=model.duration_ms,
        code=solver_input["code"],
        block_order=solver_input["block_order"],
        nodes=solver_input["nodes"],
        edges=solver_input["edges"],
        flow=solver_input["flow"],
    )


def to_history_item(model: SubmissionModel) -> SubmissionHistoryItemDTO:
    return SubmissionHistoryItemDTO(
        id=model.id,
        task_id=model.task_id,
        language=model.language,
        status=model.status,
        success=model.success,
        created_at=model.created_at.isoformat() if model.created_at else None,
        duration_ms=model.duration_ms,
    )
