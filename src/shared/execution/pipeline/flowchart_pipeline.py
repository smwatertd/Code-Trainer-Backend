from __future__ import annotations

from typing import Any

from src.shared.execution.checking.code_runner import CodeRunner
from src.shared.execution.checking.flow_public_response import public_flowchart_check_result
from src.shared.execution.checking.flow_validation_service import FlowValidationService
from src.shared.execution.pipeline.translation_pipeline import TranslationPipeline


def resolve_flowchart_mode(task_payload: dict[str, Any], job_payload: dict[str, Any]) -> str:
    explicit = str(task_payload.get("flowchart_mode") or "").strip()
    if explicit:
        return explicit
    if job_payload.get("nodes") or job_payload.get("edges") or job_payload.get("flow"):
        return "code_to_flowchart"
    return "flowchart_to_code"


class FlowchartPipeline:
    def __init__(
        self,
        translation_pipeline: TranslationPipeline,
        flow_validator: FlowValidationService | None = None,
        code_runner: CodeRunner | None = None,
    ) -> None:
        self._translation_pipeline = translation_pipeline
        self._flow_validator = flow_validator or FlowValidationService()
        self._code_runner = code_runner

    def run(
        self,
        *,
        language_id: str,
        code: str,
        task_type: str,
        task_payload: dict[str, Any],
        job_payload: dict[str, Any],
    ) -> dict[str, object]:
        mode = resolve_flowchart_mode(task_payload, job_payload)
        if mode == "code_to_flowchart":
            return self._run_code_to_flowchart(
                language_id=language_id,
                code=code,
                task_payload=task_payload,
                job_payload=job_payload,
            )
        return self._run_flowchart_to_code(
            language_id=language_id,
            code=code,
            task_type=task_type,
            task_payload=task_payload,
        )

    def _run_flowchart_to_code(
        self,
        *,
        language_id: str,
        code: str,
        task_type: str,
        task_payload: dict[str, Any],
    ) -> dict[str, object]:
        return self._translation_pipeline.run(
            language_id=language_id,
            code=code,
            task_type=task_type,
            task_payload=task_payload,
            mode="full",
        )

    def _run_code_to_flowchart(
        self,
        *,
        language_id: str,
        code: str,
        task_payload: dict[str, Any],
        job_payload: dict[str, Any],
    ) -> dict[str, object]:
        flow_spec = dict(task_payload.get("flow_spec") or {})
        if not flow_spec.get("allowed_blocks"):
            from src.shared.execution.checking.flow_block_constructions import DEFAULT_ALLOWED_BLOCKS

            flow_spec["allowed_blocks"] = list(DEFAULT_ALLOWED_BLOCKS)

        nodes = list(job_payload.get("nodes") or [])
        edges = list(job_payload.get("edges") or [])
        flow = list(job_payload.get("flow") or [])
        constructions = task_payload.get("required_structures") or task_payload.get("constructions") or []
        task = {
            "constructions": constructions,
            "source_code": task_payload.get("source_code"),
        }

        details = self._flow_validator.validate_with_details(
            flow=flow,
            flow_spec=flow_spec,
            task=task,
            nodes=nodes or None,
            edges=edges or None,
        )
        errors = list(details.get("errors") or [])
        debug = details.get("debug")
        if errors:
            from src.shared.execution.checking.flow_error_hints import enrich_flow_pattern_errors

            pattern_errors = enrich_flow_pattern_errors(
                [{"type": item["type"], "text": item["text"]} for item in errors],
                debug if isinstance(debug, dict) else None,
            )
            return public_flowchart_check_result(
                {
                    "success": False,
                    "semantic_checked": False,
                    "compiler_errors": [],
                    "linter_errors": [],
                    "pattern_errors": pattern_errors,
                    "test_results": [],
                    "flow_debug": debug,
                }
            )

        return public_flowchart_check_result(
            {
                "success": True,
                "semantic_checked": False,
                "compiler_errors": [],
                "linter_errors": [],
                "pattern_errors": [],
                "test_results": list(details.get("execution_results") or []),
                "flow_debug": details.get("debug"),
            }
        )
