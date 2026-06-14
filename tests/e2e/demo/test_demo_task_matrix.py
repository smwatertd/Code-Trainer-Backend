from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.demo import run_demo_check
from tests.e2e.helpers.flowchart import valid_if_flowchart
from tests.e2e.helpers.payloads import CPP_FOR_LOOP, PASCAL_FOR_LOOP


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__translation_task4_requires_for_loop(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            "task_id": 4,
            "language": "python",
            "code": "print(0)\nprint(1)\nprint(2)\n",
        },
    )

    assert body["success"] is False
    assert body["pattern_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__translation_task4_passes_with_for_loop(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            "task_id": 4,
            "language": "python",
            "code": "for i in range(3):\n    print(i)\n",
        },
    )

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__block_reorder_task5_wrong_output_fails(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            "task_id": 5,
            "language": "python",
            "code": "print(2)\nprint(1)",
            "block_order": [0, 1],
        },
    )

    assert body["success"] is False
    assert body["test_results"] == []
    assert body["compiler_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__flowchart_task3_invalid_structure_fails(client: AsyncClient) -> None:
    nodes = [
        {"id": "1", "type": "start", "x": 0, "y": 0},
        {"id": "2", "type": "end", "x": 0, "y": 100},
    ]
    edges = [{"source": "1", "target": "2"}]

    body = await run_demo_check(
        client,
        {
            "task_id": 3,
            "language": "python",
            "code": "if n > 0: print('pos')\nelse: print('nonpos')",
            "nodes": nodes,
            "edges": edges,
        },
    )

    assert body["success"] is False


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__flowchart_task3_valid_structure_passes(client: AsyncClient) -> None:
    nodes, edges = valid_if_flowchart()

    body = await run_demo_check(
        client,
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
async def test_demo__cpp_snippet_task7_pattern_only(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            "task_id": 7,
            "language": "cpp",
            "code": "int main(){ for(int i=0;i<3;++i){} return 0; }",
        },
    )

    assert body["success"] is True
    assert body["test_results"] == []


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__pascal_snippet_task8_without_loop_fails(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            "task_id": 8,
            "language": "pascal",
            "code": "program T; begin writeln(0); end.",
        },
    )

    assert body["success"] is False
    assert body["pattern_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__cpp_compiled_task9_passes(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            "task_id": 9,
            "language": "cpp",
            "code": CPP_FOR_LOOP,
        },
    )

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__pascal_compiled_task10_passes(client: AsyncClient) -> None:
    body = await run_demo_check(
        client,
        {
            "task_id": 10,
            "language": "pascal",
            "code": PASCAL_FOR_LOOP,
        },
    )

    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"
