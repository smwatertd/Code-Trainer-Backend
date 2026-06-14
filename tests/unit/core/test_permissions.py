from __future__ import annotations

from src.core.policies.permissions import Permission, can, can_any, normalize_role, permissions_for_role


def test_permissions__student_can_solve_assignments() -> None:
    assert can("student", Permission.SOLVE_ASSIGNMENTS) is True


def test_permissions__student_cannot_manage_users() -> None:
    assert can("student", Permission.MANAGE_USERS) is False


def test_permissions__admin_has_all_permissions() -> None:
    assert can("admin", Permission.MANAGE_USERS) is True
    assert can("admin", Permission.SOLVE_ASSIGNMENTS) is True


def test_permissions__teacher_can_view_student_results() -> None:
    assert can("teacher", Permission.VIEW_STUDENT_RESULTS) is True


def test_permissions__unknown_role_has_no_permissions() -> None:
    assert permissions_for_role("guest") == frozenset()
    assert can("guest", Permission.SOLVE_ASSIGNMENTS) is False


def test_permissions__normalize_role_aliases() -> None:
    assert normalize_role("Administrator") == "admin"
    assert can("Administrator", Permission.MANAGE_USERS) is True


def test_permissions__can_any() -> None:
    assert can_any("student", Permission.MANAGE_USERS, Permission.SOLVE_ASSIGNMENTS) is True
    assert can_any("guest", Permission.MANAGE_USERS, Permission.SOLVE_ASSIGNMENTS) is False
