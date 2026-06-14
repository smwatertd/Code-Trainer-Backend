from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AssignmentSetItemResponse(BaseModel):
    task_id: int
    sort_order: int


class AssignmentSetResponse(BaseModel):
    id: int
    name: str
    description: str
    teacher_id: int
    visibility: str
    group_id: int | None
    is_archived: bool
    items: list[AssignmentSetItemResponse]
    created_at: datetime | None = None
    deadline_at: datetime | None = None


class CreateAssignmentSetRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str = ""
    visibility: str = "private"
    group_id: int | None = None
    deadline_at: datetime | None = None


class UpdateAssignmentSetRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    visibility: str | None = None
    group_id: int | None = None
    clear_group: bool = False
    deadline_at: datetime | None = None
    is_archived: bool | None = None


class AddAssignmentSetItemRequest(BaseModel):
    task_id: int
    sort_order: int | None = None
