from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.demo import run_demo_check
from tests.e2e.helpers.payloads import (
    TASK10_MINUTES_BLOCKS,
    TASK3_SUM_PASCAL,
    TASK4_AREA_BLOCKS,
    TASK5_PERIMETER_BROKEN,
    TASK5_PERIMETER_OK,
    TASK8_LAST_DIGIT_BROKEN,
    TASK8_LAST_DIGIT_OK,
    TASK9_DIGIT_SUM_PASCAL,
)


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__translation_task3_wrong_sum_fails(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            "task_id": 3,
            "language": "pascal",
            "code": "var a,b,s: integer;\nbegin\n  readln(a,b);\n  s:=a*b;\n  writeln(s);\nend.",
        },
    )

    assert body["success"] is False
    assert body["test_results"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__translation_task3_passes_with_sum(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK3_SUM_PASCAL)

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__block_task4_wrong_order_fails(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            **TASK4_AREA_BLOCKS,
            "block_order": [0, 1, 3, 2, 4, 5, 6],
        },
    )

    assert body["success"] is False
    assert body["test_results"] == []
    assert body["compiler_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__fix_task5_wrong_perimeter_fails(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK5_PERIMETER_BROKEN)

    assert body["success"] is False
    assert body["test_results"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__fix_task5_correct_perimeter_passes(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK5_PERIMETER_OK)

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__block_task7_wrong_order_fails(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            "task_id": 7,
            "language": "pascal",
            "code": (
                "program Main;\nvar a,b: integer; avg: real;\n"
                "begin\n  readln(a,b);\n  avg:=(a+b)/2;\n  writeln(avg:0:1);\nend."
            ),
            "block_order": [0, 1, 2, 4, 3, 5, 6],
        },
    )

    assert body["success"] is False
    assert body["compiler_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__fix_task8_wrong_last_digit_fails(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK8_LAST_DIGIT_BROKEN)

    assert body["success"] is False
    assert body["test_results"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__translation_task9_passes(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK9_DIGIT_SUM_PASCAL)

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__block_task10_passes(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK10_MINUTES_BLOCKS)

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__fix_task8_correct_last_digit_passes(client: AsyncClient) -> None:
    body = await run_demo_check(client, TASK8_LAST_DIGIT_OK)

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"
