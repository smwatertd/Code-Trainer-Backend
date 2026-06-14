from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.demo import run_demo_check
from tests.e2e.helpers.payloads import TASK1_HELLO_PYTHON, TASK2_BLOCK_REORDER_OK


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__block_reorder_wrong_order_fails_before_tests(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            **TASK2_BLOCK_REORDER_OK,
            "block_order": [0, 1],
        },
    )

    assert body["success"] is False
    assert body["test_results"] == []
    assert body["compiler_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__block_reorder_correct_order_passes(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK2_BLOCK_REORDER_OK)

    assert body["success"] is True


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__block_reorder_task5_wrong_order_fails_structurally(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            "task_id": 5,
            "language": "python",
            "code": "print(2)\nprint(1)",
            "block_order": [1, 0],
        },
    )

    assert body["success"] is False
    assert body["test_results"] == []
    assert body["compiler_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__translation_task1_hello_success(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK1_HELLO_PYTHON)

    assert body["success"] is True
