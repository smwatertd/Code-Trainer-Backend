from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SkillProgressResponse(BaseModel):
    id: str
    label: str
    percent: int
    solved: int
    total: int


class RecentSubmissionResponse(BaseModel):
    id: int
    task_id: int
    task_title: str
    language: str
    status: str
    attempt: int
    created_at: datetime


class MyProfileResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role: str
    handle: str
    level: str
    solved_tasks_count: int
    total_tasks_attempted: int
    success_rate: int
    streak_days: int
    groups_count: int
    activity_by_date: dict[str, int] = Field(default_factory=dict)
    recent_submissions: list[RecentSubmissionResponse] = Field(default_factory=list)
    skills: list[SkillProgressResponse] = Field(default_factory=list)


class TeacherGroupSummaryResponse(BaseModel):
    id: int
    name: str
    member_count: int


class TeacherStatsResponse(BaseModel):
    tasks_count: int
    groups_count: int
    students_count: int
    assignment_sets_count: int


class TeacherPublicProfileResponse(BaseModel):
    kind: Literal["teacher"] = "teacher"
    user_id: int
    name: str
    email: str
    handle: str
    initials: str
    bio: str = ""
    groups: list[TeacherGroupSummaryResponse] = Field(default_factory=list)
    stats: TeacherStatsResponse
    is_own_profile: bool = False


class StudentGroupSummaryResponse(BaseModel):
    id: int
    name: str
    teacher_id: int
    teacher_name: str


class StudentSummaryResponse(BaseModel):
    solved_count: int
    success_rate: int
    streak_days: int
    attempts_count: int
    last_activity_at: datetime | None = None


class StudentTeacherRefResponse(BaseModel):
    id: int
    name: str


class StudentPublicProfileResponse(BaseModel):
    kind: Literal["student"] = "student"
    user_id: int
    name: str
    email: str
    handle: str
    initials: str
    level: str
    summary: StudentSummaryResponse
    groups: list[StudentGroupSummaryResponse] = Field(default_factory=list)
    skills: list[SkillProgressResponse] = Field(default_factory=list)
    recent_submissions: list[RecentSubmissionResponse] = Field(default_factory=list)
    teacher: StudentTeacherRefResponse | None = None
    is_own_profile: bool = False
