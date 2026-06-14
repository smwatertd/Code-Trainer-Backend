from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.submissions import submit_and_get


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__block_reorder_wrong_order_fails(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {
            "task_id": 2,
            "language": "python",
            "code": "print('b')\nprint('a')",
            "block_order": [0, 1],
        },
    )

    assert body["success"] is False
    assert body["status"] == "failed"
    assert any(item["type"] == "VALIDATION" for item in body["compiler_errors"]) or body["pattern_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__translation_task4_pattern_failure(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {
            "task_id": 4,
            "language": "python",
            "code": "print(0)\nprint(1)\nprint(2)\n",
        },
    )

    assert body["success"] is False
    assert body["pattern_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__cpp_compiled_task9_syntax_error(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {
            "task_id": 1,
            "language": "cpp",
            "code": "int main() { return 0",
        },
    )

    assert body["success"] is False
    assert body["compiler_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__pascal_snippet_task8_missing_loop_fails(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {
            "task_id": 8,
            "language": "pascal",
            "code": "program T; begin writeln(0); end.",
        },
    )

    assert body["success"] is False
    assert body["pattern_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__block_reorder_missing_order_fails(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {
            "task_id": 2,
            "language": "python",
            "code": "print('b')\nprint('a')",
        },
    )

    assert body["success"] is False
    assert body["status"] == "failed"
