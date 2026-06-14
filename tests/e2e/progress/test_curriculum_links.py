from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__student_forbidden(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.post(
        "/api/curriculum/tasks/validate-link",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "for_loop",
            "exercise_pattern_id": "tr_pattern_translation",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__teacher_validates_and_creates_link(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    validate = await client.post(
        "/api/curriculum/tasks/validate-link",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "for_loop",
            "exercise_pattern_id": "tr_pattern_translation",
        },
    )
    assert validate.status_code == 200
    assert validate.json()["learning_concept_id"] == "loops"
    assert validate.json()["action"] == "implement"

    create = await client.post(
        "/api/curriculum/tasks/1/links",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "for_loop",
            "exercise_pattern_id": "tr_pattern_translation",
            "is_primary": True,
        },
    )
    assert create.status_code == 201
    body = create.json()
    assert body["task_id"] == 1
    assert body["is_primary"] is True

    metadata = await client.get("/api/curriculum/tasks/1/links", headers=headers)
    assert metadata.status_code == 200
    payload = metadata.json()
    assert payload["has_curriculum_link"] is True
    assert payload["primary_link"]["exercise_pattern_id"] == "tr_pattern_translation"


@pytest.mark.asyncio(loop_scope="session")
async def test_curriculum_links__teacher_rejects_invalid_pattern(
    teacher_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = teacher_client
    headers = await auth_headers(client, auth_user)

    response = await client.post(
        "/api/curriculum/tasks/validate-link",
        headers=headers,
        json={
            "language": "python",
            "technical_concept_id": "for_loop",
            "exercise_pattern_id": "tr_does_not_exist",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
