from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.shared.analysis.domain.core_detection import CoreDetectionResult

ValidationStatus = Literal["PASS", "FAIL"]


@dataclass(frozen=True)
class RequiredStructureSpec:
    type: str
    min_count: int = 1


@dataclass(frozen=True)
class ExamResult:
    result: ValidationStatus
    core: CoreDetectionResult
    missing: tuple[str, ...] = ()
    present: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.result == "PASS"
