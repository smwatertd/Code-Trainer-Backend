from __future__ import annotations

from abc import ABC, abstractmethod

from src.shared.execution.domain.execution_job import ExecutionJob


class JobProcessor(ABC):
    @abstractmethod
    def process(self, job: ExecutionJob) -> dict[str, object]: ...
