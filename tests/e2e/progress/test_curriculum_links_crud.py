from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__teacher_crud_lifecycle(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    empty = await client.get("/api/curriculum/tasks/3/links", headers=headers)
    assert empty.status_code == 200
    assert empty.json()["has_curriculum_link"] is False

    create = await client.post(
        "/api/curriculum/tasks/3/links",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "if_else",
            "exercise_pattern_id": "tr_pattern_translation",
            "is_primary": True,
        },
    )
    assert create.status_code == 201
    link_id = create.json()["id"]
    assert create.json()["learning_concept_id"] == "conditions"

    update = await client.patch(
        f"/api/curriculum/tasks/3/links/{link_id}",
        headers=headers,
        json={"is_primary": True},
    )
    assert update.status_code == 200
    assert update.json()["is_primary"] is True

    metadata = await client.get("/api/curriculum/tasks/3/links", headers=headers)
    assert metadata.json()["primary_link"]["technical_concept_id"] == "if_else"

    delete = await client.delete(f"/api/curriculum/tasks/3/links/{link_id}", headers=headers)
    assert delete.status_code == 204

    after = await client.get("/api/curriculum/tasks/3/links", headers=headers)
    assert after.json()["has_curriculum_link"] is False


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__duplicate_pattern_rejected(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    first = await client.post(
        "/api/curriculum/tasks/5/links",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "for_loop",
            "exercise_pattern_id": "tr_pattern_translation",
            "is_primary": True,
        },
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/curriculum/tasks/5/links",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "while_loop",
            "exercise_pattern_id": "tr_pattern_translation",
            "is_primary": False,
        },
    )

    assert second.status_code == 422


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__unknown_task_returns_404(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    response = await client.get("/api/curriculum/tasks/999999/links", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__pascal_counted_loop_validate(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    response = await client.post(
        "/api/curriculum/tasks/validate-link",
        headers=headers,
        json={
            "language": "pascal",
            "technical_concept_id": "counted_loop",
            "exercise_pattern_id": "tr_python_to_pascal_code",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["action"] == "translate"
    assert body["learning_concept_id"] == "loops"
