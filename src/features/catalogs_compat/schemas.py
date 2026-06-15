from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CatalogResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    created_at: datetime | None = None
    task_count: int = 0
    visibility: str = "public"
    group_id: int | None = None
    deadline_at: datetime | None = None


class CreateCatalogRequest(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    description: str | None = None
    visibility: str = Field(default="public")
    group_id: int | None = None
    deadline_at: datetime | None = None


class LegacyTaskResponse(BaseModel):
    id: int
    title: str
    content: str
    topic_id: int | None = None
    type_id: str
    created_at: datetime
    difficulty: str | None = None
    language: str | None = None
    languages: list[str] = Field(default_factory=list)
    catalog_ids: list[int] = Field(default_factory=list)
    is_assigned: bool = False


class AssignTaskRequest(BaseModel):
    task_id: int


class CreateLegacyTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = ""
    topic_id: int | None = None
    type_id: str = Field(min_length=1, max_length=64)


class AssignCatalogToGroupRequest(BaseModel):
    catalog_id: int
    deadline_at: datetime | None = None
