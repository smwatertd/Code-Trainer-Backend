from __future__ import annotations

from src.features.demo.services.demo_service import DemoService
from src.shared.execution.domain.dto import JobResultDTO


def test_demo_service__maps_flowchart_failure_without_flow_debug() -> None:
    service = DemoService(
        catalog_service=None,  # type: ignore[arg-type]
        execution_service=None,  # type: ignore[arg-type]
        rate_limiter=None,  # type: ignore[arg-type]
        guest_settings=None,  # type: ignore[arg-type]
    )
    dto = JobResultDTO(
        job_id="job-flow",
        status="SUCCESS",
        success=True,
        output={
            "success": False,
            "pattern_errors": [
                {
                    "type": "FLOW_SOURCE_MISMATCH",
                    "text": "В блоке «Цикл» укажите условие range(3), как в программе.",
                }
            ],
            "flow_debug": {"expected_sequence": "Начало → Цикл → Конец"},
        },
    )

    mapped = service._map_result(dto)

    assert mapped.success is False
    assert mapped.pattern_errors


def test_demo_service__strips_detail_from_pattern_errors() -> None:
    service = DemoService(
        catalog_service=None,  # type: ignore[arg-type]
        execution_service=None,  # type: ignore[arg-type]
        rate_limiter=None,  # type: ignore[arg-type]
        guest_settings=None,  # type: ignore[arg-type]
    )
    dto = JobResultDTO(
        job_id="job-flow-2",
        status="SUCCESS",
        success=True,
        output={
            "success": False,
            "pattern_errors": [
                {
                    "type": "FLOW_SEQUENCE_MISMATCH",
                    "text": "Проверьте порядок.",
                    "detail": "Ожидаемый порядок: Начало → Конец",
                }
            ],
        },
    )

    mapped = service._map_result(dto)

    assert mapped.pattern_errors == [{"type": "FLOW_SEQUENCE_MISMATCH", "text": "Проверьте порядок."}]
