from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_admin__student_forbidden_debug(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/curriculum/python/debug", headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_admin__teacher_forbidden_validate_bundle(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/curriculum/python/validate", headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_admin__debug_includes_python_chapters(
    admin_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = admin_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/curriculum/python/debug", headers=headers)

    assert response.status_code == 200
    body = response.json()
    chapter_ids = {item["learning_concept"]["id"] for item in body["chapters"]}
    assert chapter_ids.issuperset({"chapter_1", "chapter_2", "chapter_16"})
    assert body["validation"]["valid"] is True


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_admin__pascal_validate_reports_stats(
    admin_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = admin_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/curriculum/pascal/validate", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["stats"]["exercise_patterns"] > 20
    assert body["stats"]["technical_concepts"] > 20
