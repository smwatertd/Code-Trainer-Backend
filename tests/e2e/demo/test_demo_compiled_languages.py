from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.auth import auth_headers


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__cpp_compile_and_run_passes(client: AsyncClient) -> None:
    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": 9,
            "language": "cpp",
            "code": (
                "#include <iostream>\n"
                "int main() {\n"
                "  for (int i = 0; i < 3; ++i) std::cout << i << '\\n';\n"
                "  return 0;\n"
                "}\n"
            ),
        },
    )
    assert submit.status_code == 200
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_demo_check__pascal_compile_and_run_passes(client: AsyncClient) -> None:
    submit = await client.post(
        "/api/demo/check",
        json={
            "task_id": 10,
            "language": "pascal",
            "code": (
                "program T;\n" "var i: integer;\n" "begin\n" "  for i := 1 to 3 do\n" "    writeln(i);\n" "end.\n"
            ),
        },
    )
    queued = submit.json()

    result = await client.get(f"/api/demo/check/{queued['job_id']}")

    assert result.status_code == 200
    body = result.json()
    assert body["success"] is True
    assert body["test_results"][0]["status"] == "PASSED"


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__cpp_compile_and_run_passes(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 9,
            "language": "cpp",
            "code": (
                "#include <iostream>\n"
                "int main() {\n"
                "  for (int i = 0; i < 3; ++i) std::cout << i << '\\n';\n"
                "  return 0;\n"
                "}\n"
            ),
        },
    )

    assert submit.status_code == 200
    assert submit.json()["status"] == "success"
