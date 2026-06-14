from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TaskProgressResponse(BaseModel):
    task_id: int
    progress_status: str
    attempts_count: int = Field(ge=0)
    passed_count: int = Field(ge=0)
    failed_count: int = Field(ge=0, default=0)
    last_status: str | None = None
    last_submission_id: int | None = None
    last_attempt_at: datetime | None = None
    first_passed_at: datetime | None = None


class TechnicalConceptProgressResponse(BaseModel):
    technical_concept_id: str
    total_tasks: int = Field(ge=0)
    passed_tasks: int = Field(ge=0)
    progress_percent: float = Field(ge=0)


class TaskCurriculumProgressItemResponse(BaseModel):
    task_id: int
    progress_status: str
    attempts_count: int = Field(ge=0)
    passed_count: int = Field(ge=0)


class LearningConceptProgressResponse(BaseModel):
    language: str
    learning_concept_id: str
    total_tasks: int = Field(ge=0)
    passed_tasks: int = Field(ge=0)
    progress_percent: float = Field(ge=0)
    by_technical_concept: dict[str, TechnicalConceptProgressResponse]
    by_task_id: dict[int, TaskCurriculumProgressItemResponse]
