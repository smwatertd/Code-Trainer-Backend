from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.curriculum_links import delete_all_task_links


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__unauthenticated_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/curriculum/tasks/4/links")

    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__unlinked_task_has_no_links(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)
    await delete_all_task_links(client, headers, 25)

    response = await client.get("/api/curriculum/tasks/25/links", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["has_curriculum_link"] is False
    assert body["links"] == []


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__primary_swap_clears_old_primary(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)
    await delete_all_task_links(client, headers, 25)

    first = await client.post(
        "/api/curriculum/tasks/25/links",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "counted_loop",
            "exercise_pattern_id": "tr_pattern_translation",
            "is_primary": True,
        },
    )
    assert first.status_code == 201
    old_primary_id = first.json()["id"]

    create = await client.post(
        "/api/curriculum/tasks/25/links",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "pre_condition_loop",
            "exercise_pattern_id": "tr_python_snippet",
            "is_primary": True,
        },
    )
    assert create.status_code == 201
    new_primary_id = create.json()["id"]
    assert new_primary_id != old_primary_id

    metadata = await client.get("/api/curriculum/tasks/25/links", headers=headers)
    assert metadata.status_code == 200
    body = metadata.json()
    assert body["primary_link"]["id"] == new_primary_id
    assert body["primary_link"]["technical_concept_id"] == "pre_condition_loop"

    primary_flags = {link["id"]: link["is_primary"] for link in body["links"]}
    assert primary_flags[new_primary_id] is True
    assert primary_flags[old_primary_id] is False

    await client.delete(f"/api/curriculum/tasks/4/links/{new_primary_id}", headers=headers)


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__create_on_unknown_task_returns_404(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    response = await client.post(
        "/api/curriculum/tasks/999999/links",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "counted_loop",
            "exercise_pattern_id": "tr_pattern_translation",
            "is_primary": True,
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__patch_unknown_link_returns_404(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    response = await client.patch(
        "/api/curriculum/tasks/4/links/999999",
        headers=headers,
        json={"is_primary": True},
    )

    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__delete_unknown_link_returns_404(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    response = await client.delete("/api/curriculum/tasks/4/links/999999", headers=headers)

    assert response.status_code == 404
