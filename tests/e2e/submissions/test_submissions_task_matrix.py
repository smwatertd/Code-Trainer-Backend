from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.flowchart import hello_flowchart, valid_if_flowchart
from tests.e2e.helpers.payloads import CPP_FOR_LOOP, PASCAL_FOR_LOOP
from tests.e2e.helpers.submissions import submit_and_get
from tests.e2e.helpers.users import register_user


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__translation_task1_success(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {"task_id": 1, "language": "python", "code": "print('Hello')\n"},
    )

    assert body["success"] is True
    assert body["status"] == "success"
    assert body["test_results"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__translation_task1_wrong_output_fails(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {"task_id": 1, "language": "python", "code": "print('Wrong')\n"},
    )

    assert body["success"] is False
    assert body["test_results"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__translation_task4_curriculum_link_updates_progress(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await submit_and_get(
        client,
        headers,
        {
            "task_id": 4,
            "language": "python",
            "code": "for i in range(3):\n    print(i)\n",
        },
    )
    assert submit["success"] is True

    progress = await client.get("/api/progress/curriculum/python/loops", headers=headers)
    assert progress.status_code == 200
    assert progress.json()["passed_tasks"] >= 1


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__block_reorder_task5_semantic_success(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {
            "task_id": 5,
            "language": "python",
            "code": "print(1)\nprint(2)",
            "block_order": [0, 1],
        },
    )

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__flowchart_task6_semantic_success(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)
    nodes, edges = hello_flowchart()

    body = await submit_and_get(
        client,
        headers,
        {
            "task_id": 6,
            "language": "python",
            "code": "print('hello')",
            "nodes": nodes,
            "edges": edges,
        },
    )

    assert body["success"] is True


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__cpp_task9_compiled_success(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {"task_id": 9, "language": "cpp", "code": CPP_FOR_LOOP},
    )

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__pascal_task10_compiled_success(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {"task_id": 10, "language": "pascal", "code": PASCAL_FOR_LOOP},
    )

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__cpp_snippet_task7_pattern_success(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {
            "task_id": 7,
            "language": "cpp",
            "code": "int main(){ for(int i=0;i<3;++i){} return 0; }",
        },
    )

    assert body["success"] is True


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__flowchart_task3_success(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)
    nodes, edges = valid_if_flowchart()

    body = await submit_and_get(
        client,
        headers,
        {
            "task_id": 3,
            "language": "python",
            "code": "if n > 0: print('pos')\nelse: print('nonpos')",
            "nodes": nodes,
            "edges": edges,
        },
    )

    assert body["success"] is True


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__unknown_task_returns_404(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.post(
        "/api/submissions",
        headers=headers,
        json={"task_id": 999999, "language": "python", "code": "print(1)"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__cannot_read_other_users_submission(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, owner = auth_client
    owner_headers = await auth_headers(client, owner)

    created = await submit_and_get(
        client,
        owner_headers,
        {
            "task_id": 2,
            "language": "python",
            "code": "print('b')\nprint('a')",
            "block_order": [1, 0],
        },
    )

    other = await register_user(client)
    other_headers = {"Authorization": f"Bearer {other['access_token']}"}

    response = await client.get(f"/api/submissions/{created['id']}", headers=other_headers)

    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__pending_latest_returns_queued_submission(
    auth_queued_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_queued_client
    headers = await auth_headers(client, auth_user)

    created = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 1,
            "language": "python",
            "code": "print('queued')",
        },
    )
    assert created.status_code == 200
    submission_id = created.json()["id"]
    assert created.json()["status"] == "queued"

    pending = await client.get("/api/submissions/pending/latest?task_id=1", headers=headers)

    assert pending.status_code == 200
    body = pending.json()
    assert body is not None
    assert body["id"] == submission_id
    assert body["status"] == "queued"


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__validation_error_on_empty_code(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    response = await client.post(
        "/api/submissions",
        headers=headers,
        json={"task_id": 1, "language": "python", "code": ""},
    )

    assert response.status_code == 422


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__unknown_job_id_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/demo/check/does-not-exist")

    assert response.status_code == 404
