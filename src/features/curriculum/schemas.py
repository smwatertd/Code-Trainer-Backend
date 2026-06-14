from __future__ import annotations

from pydantic import BaseModel, Field


class CollectionProgressResponse(BaseModel):
    total_tasks: int = Field(ge=0)
    passed_tasks: int = Field(ge=0)
    progress_percent: float = Field(ge=0)


class CollectionNextTaskResponse(BaseModel):
    task_id: int
    title: str
    progress_status: str | None = None


class CollectionSummaryResponse(BaseModel):
    collection_id: str
    title_ru: str
    description_ru: str
    route_path: str
    order: int
    progress: CollectionProgressResponse
    completed: bool
    button_label: str
    next_task: CollectionNextTaskResponse | None = None


class LanguageTrackResponse(BaseModel):
    language: str
    language_label: str
    progress: CollectionProgressResponse
    collections: list[CollectionSummaryResponse]


class ShowcaseTaskResponse(BaseModel):
    task_id: int
    title: str
    action: str
    action_label: str
    action_skill_label: str
    action_description_ru: str
    difficulty: str
    progress_status: str | None = None
    short_instruction: str
    subtopic_name_ru: str


class ShowcaseSectionResponse(BaseModel):
    id: str
    name_ru: str
    tasks: list[ShowcaseTaskResponse]
    progress: CollectionProgressResponse


class CollectionShowcaseResponse(BaseModel):
    collection_id: str
    title: str
    description: str
    total_tasks: int = Field(ge=0)
    progress: CollectionProgressResponse | None = None
    sections: list[ShowcaseSectionResponse]
    next_task: CollectionNextTaskResponse | None = None
    button_label: str
    completed: bool
