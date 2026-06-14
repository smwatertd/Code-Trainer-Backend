from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__cpp_pattern_requires_for_loop(client: AsyncClient) -> None:
    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": 7,
            "language": "cpp",
            "code": "int main(){ return 0; }",
        },
    )
    assert submit.status_code == 200
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["success"] is False
    assert body["pattern_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__cpp_pattern_passes_with_for_loop(client: AsyncClient) -> None:
    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": 7,
            "language": "cpp",
            "code": "int main(){ for(int i=0;i<3;++i){} return 0; }",
        },
    )
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["success"] is True
    assert body["pattern_errors"] == []


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__pascal_pattern_requires_for_loop(client: AsyncClient) -> None:
    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": 8,
            "language": "pascal",
            "code": "program T; begin writeln(0); end.",
        },
    )
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["success"] is False
    assert body["pattern_errors"]


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__pascal_pattern_passes_with_for_loop(client: AsyncClient) -> None:
    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": 8,
            "language": "pascal",
            "code": "program T; var i: integer; begin for i := 1 to 3 do writeln(i); end.",
        },
    )
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["success"] is True
    assert body["pattern_errors"] == []
