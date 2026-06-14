from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GetTaskProgressCommand:
    user_id: int
    task_id: int


@dataclass(frozen=True)
class GetLearningConceptProgressCommand:
    user_id: int
    language: str
    learning_concept_id: str


@dataclass(frozen=True)
class ValidateTaskCurriculumLinkCommand:
    language: str
    technical_concept_id: str
    exercise_pattern_id: str


@dataclass(frozen=True)
class GetTaskCurriculumLinksCommand:
    task_id: int


@dataclass(frozen=True)
class CreateTaskCurriculumLinkCommand:
    task_id: int
    language: str
    technical_concept_id: str
    exercise_pattern_id: str
    is_primary: bool = False


@dataclass(frozen=True)
class UpdateTaskCurriculumLinkCommand:
    task_id: int
    link_id: int
    language: str | None = None
    technical_concept_id: str | None = None
    exercise_pattern_id: str | None = None
    is_primary: bool | None = None


@dataclass(frozen=True)
class DeleteTaskCurriculumLinkCommand:
    task_id: int
    link_id: int


@dataclass(frozen=True)
class GetCurriculumValidationCommand:
    language: str


@dataclass(frozen=True)
class GetCurriculumDebugCommand:
    language: str
