from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TaskProgressDTO:
    task_id: int
    progress_status: str
    attempts_count: int
    passed_count: int
    failed_count: int = 0
    last_status: str | None = None
    last_submission_id: int | None = None
    last_attempt_at: datetime | None = None
    first_passed_at: datetime | None = None


@dataclass(frozen=True)
class TechnicalConceptProgressDTO:
    technical_concept_id: str
    total_tasks: int
    passed_tasks: int
    progress_percent: float


@dataclass(frozen=True)
class TaskCurriculumProgressItemDTO:
    task_id: int
    progress_status: str
    attempts_count: int
    passed_count: int


@dataclass(frozen=True)
class LearningConceptProgressDTO:
    language: str
    learning_concept_id: str
    total_tasks: int
    passed_tasks: int
    progress_percent: float
    by_technical_concept: dict[str, TechnicalConceptProgressDTO]
    by_task_id: dict[int, TaskCurriculumProgressItemDTO]
