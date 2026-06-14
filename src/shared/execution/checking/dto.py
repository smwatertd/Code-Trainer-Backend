from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestCaseResult:
    case: int
    status: str
    inputs: str = ""
    expected: str = ""
    actual: str = ""
    message: str = ""
    duration_ms: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "case": self.case,
            "status": self.status,
            "inputs": self.inputs,
            "expected": self.expected,
            "actual": self.actual,
            "message": self.message,
            "duration_ms": self.duration_ms,
        }
