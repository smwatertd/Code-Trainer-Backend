from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.submissions import submit_and_get
from tests.e2e.helpers.payloads import (
    TASK1_HELLO_BLOCKS,
    TASK2_AGE_BROKEN,
    TASK3_SUM_PASCAL,
    TASK5_PERIMETER_BROKEN,
    TASK8_LAST_DIGIT_BROKEN,
)


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
            **TASK1_HELLO_BLOCKS,
            "block_order": [0, 2, 1, 3],
        },
    )

    assert body["success"] is False
    assert body["status"] == "failed"
    assert body["compiler_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__translation_task3_wrong_formula_fails(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {
            "task_id": 3,
            "language": "pascal",
            "code": "var a,b,s: integer;\nbegin\n  readln(a,b);\n  s:=a*b;\n  writeln(s);\nend.",
        },
    )

    assert body["success"] is False
    assert body["test_results"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__pascal_translation_syntax_error(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        {
            "task_id": 3,
            "language": "pascal",
            "code": "var a,b,s: integer;\nbegin\n  readln(a,b;\n  s:=a+b;\n  writeln(s);\nend.",
        },
    )

    assert body["success"] is False
    assert body["compiler_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__fix_task8_wrong_formula_fails(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        TASK8_LAST_DIGIT_BROKEN,
    )

    assert body["success"] is False
    assert body["test_results"]


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
            "task_id": 1,
            "language": "pascal",
            "code": TASK1_HELLO_BLOCKS["code"],
        },
    )

    assert body["success"] is False
    assert body["status"] == "failed"


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__fix_task2_broken_template_fails(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        TASK2_AGE_BROKEN,
    )

    assert body["success"] is False
    assert body["test_results"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__fix_task5_broken_perimeter_fails(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        TASK5_PERIMETER_BROKEN,
    )

    assert body["success"] is False
    assert body["test_results"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__translation_task3_passes(
    auth_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    body = await submit_and_get(
        client,
        headers,
        TASK3_SUM_PASCAL,
    )

    assert body["success"] is True
    assert body["test_results"]
