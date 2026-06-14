from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.http import assert_api_error
from tests.e2e.helpers.payloads import DEMO_CHECK_PAYLOAD
from tests.e2e.helpers.users import register_user

PROTECTED_ENDPOINTS: list[tuple[str, str, dict | None]] = [
    ("GET", "/api/auth/me", None),
    ("GET", "/api/progress/tasks/1", None),
    ("GET", "/api/progress/curriculum/python/loops", None),
    ("POST", "/api/submissions", {"task_id": 1, "language": "python", "code": "print(1)"}),
    ("GET", "/api/submissions/1", None),
    ("POST", "/api/submissions/1/abandon", None),
    ("GET", "/api/submissions/pending/latest?task_id=2", None),
    ("POST", "/api/groups", {"name": "Hack"}),
    ("GET", "/api/groups/mine", None),
    ("GET", "/api/groups/joined", None),
    ("POST", "/api/groups/join", {"code": "ABCDEF"}),
    ("GET", "/api/assignment-sets", None),
    ("POST", "/api/assignment-sets", {"name": "Hack"}),
    ("GET", "/api/assignment-sets/mine", None),
    ("GET", "/api/curriculum/python/debug", None),
    ("GET", "/api/curriculum/python/validate", None),
    (
        "POST",
        "/api/curriculum/tasks/validate-link",
        {
            "language": "python",
            "technical_concept_id": "function_definition",
            "exercise_pattern_id": "tr_pattern_translation",
        },
    ),
]


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(("method", "path", "json_body"), PROTECTED_ENDPOINTS)
async def test_anonymous__protected_endpoints_return_401(
    client: AsyncClient,
    method: str,
    path: str,
    json_body: dict | None,
) -> None:
    response = await client.request(method, path, json=json_body)

    assert response.status_code == 401, f"{method} {path}: {response.text}"
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio(loop_scope="session")
async def test_anonymous__public_catalog_languages_and_demo_check_work(client: AsyncClient) -> None:
    catalog = await client.get("/api/catalog/tasks")
    task = await client.get("/api/catalog/tasks/2")
    languages = await client.get("/api/languages")
    demo = await client.post("/api/demo/check", json=DEMO_CHECK_PAYLOAD)

    assert catalog.status_code == 200
    assert task.status_code == 200
    assert languages.status_code == 200
    assert demo.status_code == 200
    assert demo.json()["job_id"]


@pytest.mark.asyncio(loop_scope="session")
async def test_anonymous__demo_check_works_with_invalid_bearer_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/demo/check",
        json=DEMO_CHECK_PAYLOAD,
        headers={"Authorization": "Bearer totally-invalid-token"},
    )

    assert response.status_code == 200
    assert response.json()["job_id"]


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_register__ignores_role_privilege_escalation(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/register",
        json={
            "name": "Escalation Attempt",
            "email": f"escalation-{uuid4().hex[:8]}@example.com",
            "password": "password123",
            "role": "admin",
        },
    )

    assert response.status_code == 201
    token = response.json()["access_token"]

    me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert me.status_code == 200
    assert me.json()["role"] == "student"


@pytest.mark.asyncio(loop_scope="session")
async def test_anonymous__submission_id_not_pollable_as_demo_job(client: AsyncClient) -> None:
    user = await register_user(client)
    headers = {"Authorization": f"Bearer {user['access_token']}"}

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 2,
            "language": "pascal",
            "code": "var age: integer;\nbegin\n  readln(age);\n  writeln(age);\nend.",
        },
    )
    assert submit.status_code == 200
    submission_id = submit.json()["id"]

    poll = await client.get(f"/api/demo/check/{submission_id}")

    assert poll.status_code == 404
    assert poll.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio(loop_scope="session")
async def test_anonymous__demo_job_not_readable_via_submissions_api(client: AsyncClient) -> None:
    queued = await client.post("/api/demo/check", json=DEMO_CHECK_PAYLOAD)
    assert queued.status_code == 200
    job_id = queued.json()["job_id"]

    user = await register_user(client)
    headers = {"Authorization": f"Bearer {user['access_token']}"}
    response = await client.get(f"/api/submissions/{job_id}", headers=headers)

    assert response.status_code == 422


@pytest.mark.asyncio(loop_scope="session")
async def test_anonymous__cannot_read_other_users_submission_without_auth(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, owner = auth_client
    headers = await auth_headers(client, owner)

    created = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 2,
            "language": "pascal",
            "code": "var age: integer;\nbegin\n  readln(age);\n  writeln(age);\nend.",
        },
    )
    assert created.status_code == 200
    submission_id = created.json()["id"]

    response = await client.get(f"/api/submissions/{submission_id}")

    assert_api_error(response, status=401, code="UNAUTHORIZED")
