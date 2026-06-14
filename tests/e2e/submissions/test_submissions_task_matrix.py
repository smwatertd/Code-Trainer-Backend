from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.payloads import TASK1_HELLO_BLOCKS, TASK3_SUM_PASCAL
from tests.e2e.helpers.submissions import submit_and_get


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__block_task1_hello_success(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(client, headers, TASK1_HELLO_BLOCKS)

    assert body["success"] is True
    assert body["status"] == "success"
    assert body["test_results"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__block_task1_wrong_order_fails(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {
            **TASK1_HELLO_BLOCKS,
            "block_order": [2, 1, 0, 3],
        },
    )

    assert body["success"] is False


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__translation_task3_sum_success(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(client, headers, TASK3_SUM_PASCAL)

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


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
