from __future__ import annotations

from src.shared.analysis.domain.core_detection import CoreDetectionResult
from src.shared.analysis.domain.semantic_core import ExamResult, RequiredStructureSpec, ValidationStatus


def grade(required: list[RequiredStructureSpec], detected: CoreDetectionResult) -> ExamResult:
    missing = tuple(spec.type for spec in required if not detected.has(spec.type, spec.min_count))
    present = tuple(spec.type for spec in required if detected.has(spec.type, spec.min_count))
    status: ValidationStatus = "PASS" if not missing else "FAIL"
    return ExamResult(result=status, core=detected, missing=missing, present=present)
