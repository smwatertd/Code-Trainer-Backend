from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateGroupCommand:
    teacher_id: int
    name: str


@dataclass(frozen=True)
class ListTeacherGroupsCommand:
    teacher_id: int


@dataclass(frozen=True)
class ListStudentGroupsCommand:
    student_id: int


@dataclass(frozen=True)
class CreateInvitationCommand:
    teacher_id: int
    group_id: int
    max_uses: int | None = None
    expires_in_days: int | None = 30


@dataclass(frozen=True)
class JoinGroupCommand:
    student_id: int
    code: str


@dataclass(frozen=True)
class GetGroupDashboardCommand:
    teacher_id: int
    group_id: int
