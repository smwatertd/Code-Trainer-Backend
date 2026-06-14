from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TaskSummaryResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    task_type: str
    topics: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    progress_status: str | None = None


class TeacherTaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=5000)
    difficulty: str = Field(default="easy")
    task_type: str = Field(min_length=1, max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)


class TaskDetailResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    task_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
