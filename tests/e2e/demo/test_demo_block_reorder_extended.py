from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.demo import run_demo_check
from tests.e2e.helpers.payloads import TASK1_HELLO_BLOCKS, TASK2_AGE_PASCAL, TASK4_AREA_BLOCKS


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__block_reorder_wrong_order_fails_before_tests(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            **TASK1_HELLO_BLOCKS,
            "block_order": [0, 2, 1, 3],
        },
    )

    assert body["success"] is False
    assert body["test_results"] == []
    assert body["compiler_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__block_reorder_correct_order_passes(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK1_HELLO_BLOCKS)

    assert body["success"] is True


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__block_task4_wrong_order_fails_structurally(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            **TASK4_AREA_BLOCKS,
            "block_order": [0, 1, 2, 4, 3, 5, 6],
        },
    )

    assert body["success"] is False
    assert body["test_results"] == []
    assert body["compiler_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__fix_task2_age_success(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK2_AGE_PASCAL)

    assert body["success"] is True
