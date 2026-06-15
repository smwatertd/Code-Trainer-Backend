from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.curriculum_links import delete_all_task_links


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__update_technical_concept_and_pattern(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)
    await delete_all_task_links(client, headers, 25)

    create = await client.post(
        "/api/curriculum/tasks/25/links",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "counted_loop",
            "exercise_pattern_id": "tr_pattern_translation",
            "is_primary": True,
        },
    )
    assert create.status_code == 201
    link_id = create.json()["id"]
    assert create.json()["learning_concept_id"] == "chapter_3"
    assert create.json()["action"] == "implement"

    update = await client.patch(
        f"/api/curriculum/tasks/25/links/{link_id}",
        headers=headers,
        json={
            "technical_concept_id": "pre_condition_loop",
            "exercise_pattern_id": "tr_python_snippet",
        },
    )
    assert update.status_code == 200
    body = update.json()
    assert body["technical_concept_id"] == "pre_condition_loop"
    assert body["exercise_pattern_id"] == "tr_python_snippet"
    assert body["learning_concept_id"] == "chapter_3"
    assert body["action"] == "translate"

    await client.delete(f"/api/curriculum/tasks/25/links/{link_id}", headers=headers)


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__invalid_pattern_returns_422(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    response = await client.post(
        "/api/curriculum/tasks/validate-link",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "counted_loop",
            "exercise_pattern_id": "does_not_exist",
        },
    )

    assert response.status_code == 422
