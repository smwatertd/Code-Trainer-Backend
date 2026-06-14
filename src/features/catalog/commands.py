from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ListTasksCommand:
    difficulty: str | None = None
    task_type: str | None = None
    topic: str | None = None
    user_id: int | None = None


@dataclass(frozen=True)
class CreateTeacherTaskCommand:
    owner_user_id: int
    title: str
    description: str
    difficulty: str
    task_type: str
    payload: dict


@dataclass(frozen=True)
class GetTaskCommand:
    task_id: int
