from __future__ import annotations

from enum import Enum


class Permission(str, Enum):
    SOLVE_ASSIGNMENTS = "solve_assignments"
    VIEW_OWN_PROGRESS = "view_own_progress"
    BROWSE_TEACHERS = "browse_teachers"
    JOIN_GROUPS = "join_groups"
    CREATE_ASSIGNMENTS = "create_assignments"
    EDIT_ASSIGNMENTS = "edit_assignments"
    MANAGE_ASSIGNMENT_SETS = "manage_assignment_sets"
    MANAGE_GROUPS = "manage_groups"
    VIEW_STUDENT_RESULTS = "view_student_results"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_SYSTEM_STATISTICS = "view_system_statistics"
    REVIEW_TEACHER_REQUESTS = "review_teacher_requests"
    SUBMIT_SUPPORT_REQUEST = "submit_support_request"
    MANAGE_SUPPORT_TICKETS = "manage_support_tickets"


_ROLE_ALIASES: dict[str, str] = {
    "student": "student",
    "teacher": "teacher",
    "admin": "admin",
    "administrator": "admin",
}


ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "student": frozenset(
        {
            Permission.SOLVE_ASSIGNMENTS,
            Permission.VIEW_OWN_PROGRESS,
            Permission.BROWSE_TEACHERS,
            Permission.JOIN_GROUPS,
            Permission.SUBMIT_SUPPORT_REQUEST,
        }
    ),
    "teacher": frozenset(
        {
            Permission.SOLVE_ASSIGNMENTS,
            Permission.VIEW_OWN_PROGRESS,
            Permission.BROWSE_TEACHERS,
            Permission.JOIN_GROUPS,
            Permission.CREATE_ASSIGNMENTS,
            Permission.EDIT_ASSIGNMENTS,
            Permission.MANAGE_ASSIGNMENT_SETS,
            Permission.MANAGE_GROUPS,
            Permission.VIEW_STUDENT_RESULTS,
            Permission.SUBMIT_SUPPORT_REQUEST,
        }
    ),
    "admin": frozenset(Permission),
}


def normalize_role(role: str) -> str:
    return _ROLE_ALIASES.get(role.strip().lower(), role.strip().lower())


def permissions_for_role(role: str) -> frozenset[Permission]:
    return ROLE_PERMISSIONS.get(normalize_role(role), frozenset())


def can(role: str, permission: Permission) -> bool:
    return permission in permissions_for_role(role)


def can_any(role: str, *permissions: Permission) -> bool:
    granted = permissions_for_role(role)
    return any(item in granted for item in permissions)
