from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateAssignmentSetCommand:
    teacher_id: int
    name: str
    description: str
    visibility: str
    group_id: int | None
    deadline_at: datetime | None = None


@dataclass(frozen=True)
class ListTeacherAssignmentSetsCommand:
    teacher_id: int
    include_archived: bool = False


@dataclass(frozen=True)
class ListAccessibleAssignmentSetsCommand:
    user_id: int


@dataclass(frozen=True)
class GetAssignmentSetCommand:
    user_id: int
    role: str
    set_id: int


@dataclass(frozen=True)
class UpdateAssignmentSetCommand:
    teacher_id: int
    set_id: int
    name: str | None = None
    description: str | None = None
    visibility: str | None = None
    group_id: int | None = None
    clear_group: bool = False
    deadline_at: datetime | None = None
    is_archived: bool | None = None


@dataclass(frozen=True)
class AddAssignmentSetItemCommand:
    teacher_id: int
    set_id: int
    task_id: int
    sort_order: int | None = None


@dataclass(frozen=True)
class RemoveAssignmentSetItemCommand:
    teacher_id: int
    set_id: int
    task_id: int
