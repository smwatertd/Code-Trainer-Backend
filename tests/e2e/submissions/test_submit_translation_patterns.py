from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.payloads import TASK3_SUM_PASCAL


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__translation_wrong_formula_fails(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json={
            "task_id": 3,
            "language": "pascal",
            "code": "var a,b,s: integer;\nbegin\n  readln(a,b);\n  s:=a*b;\n  writeln(s);\nend.",
        },
    )

    assert submit.status_code == 200
    queued = submit.json()
    assert queued["status"] == "failed"

    detail = await client.get(f"/api/submissions/{queued['id']}", headers=headers)

    assert detail.status_code == 200
    body = detail.json()
    assert body["success"] is False
    assert body["test_results"]


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__translation_with_correct_sum_passes(
    auth_client: tuple[AsyncClient, object],
) -> None:
    client, auth_user = auth_client
    headers = await auth_headers(client, auth_user)

    submit = await client.post(
        "/api/submissions",
        headers=headers,
        json=TASK3_SUM_PASCAL,
    )

    assert submit.status_code == 200
    queued = submit.json()
    assert queued["status"] == "success"

    detail = await client.get(f"/api/submissions/{queued['id']}", headers=headers)

    assert detail.status_code == 200
    body = detail.json()
    assert body["success"] is True
    assert body["test_results"]
