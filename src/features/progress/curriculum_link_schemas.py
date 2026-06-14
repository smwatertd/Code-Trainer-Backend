from __future__ import annotations

from pydantic import BaseModel, Field


class TaskCurriculumLinkResponse(BaseModel):
    id: int
    task_id: int
    language: str
    learning_concept_id: str
    technical_concept_id: str
    exercise_pattern_id: str
    action: str
    is_primary: bool
    created_at: str | None = None


class TaskCurriculumMetadataResponse(BaseModel):
    task_id: int
    has_curriculum_link: bool
    primary_link: TaskCurriculumLinkResponse | None = None
    links: list[TaskCurriculumLinkResponse] = Field(default_factory=list)


class TaskCurriculumLinkCreateRequest(BaseModel):
    language: str = "python"
    technical_concept_id: str
    exercise_pattern_id: str
    is_primary: bool = False


class TaskCurriculumLinkUpdateRequest(BaseModel):
    language: str | None = None
    technical_concept_id: str | None = None
    exercise_pattern_id: str | None = None
    is_primary: bool | None = None


class TaskCurriculumLinkValidateRequest(BaseModel):
    language: str = "python"
    technical_concept_id: str
    exercise_pattern_id: str


class TaskCurriculumLinkValidateResponse(BaseModel):
    language: str
    learning_concept_id: str
    technical_concept_id: str
    exercise_pattern_id: str
    action: str


class CurriculumValidationResponse(BaseModel):
    language: str
    valid: bool
    errors: list[str] = Field(default_factory=list)
    stats: dict[str, int]


class CurriculumDebugResponse(BaseModel):
    summary: dict[str, int | str]
    validation: CurriculumValidationResponse
    chapters: list[dict[str, object]]
