from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.demo import run_demo_check
from tests.e2e.helpers.payloads import TASK2_AGE_BROKEN, TASK2_AGE_PASCAL, TASK5_PERIMETER_BROKEN, TASK5_PERIMETER_OK


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__fix_task2_broken_template_fails(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK2_AGE_BROKEN)

    assert body["success"] is False
    assert body["test_results"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__fix_task2_correct_solution_passes(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK2_AGE_PASCAL)

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__fix_task5_broken_perimeter_fails(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK5_PERIMETER_BROKEN)

    assert body["success"] is False
    assert body["test_results"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__fix_task5_correct_perimeter_passes(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK5_PERIMETER_OK)

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"
