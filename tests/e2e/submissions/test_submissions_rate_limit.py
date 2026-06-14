from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import E2EAuthUser
from tests.e2e.helpers.auth import auth_headers
from tests.e2e.helpers.http import assert_api_error
from tests.e2e.helpers.payloads import DEMO_CHECK_PAYLOAD, TASK1_HELLO_BLOCKS


@pytest.mark.asyncio(loop_scope="session")
async def test_submissions__concurrent_queued_jobs_hit_rate_limit(
    rate_limited_submissions_client: tuple[AsyncClient, E2EAuthUser],
) -> None:
    client, auth_user = rate_limited_submissions_client
    headers = await auth_headers(client, auth_user)
    first = await client.post("/api/submissions", headers=headers, json=TASK1_HELLO_BLOCKS)
    second = await client.post("/api/submissions", headers=headers, json=DEMO_CHECK_PAYLOAD)

    assert first.status_code == 200
    assert_api_error(second, status=429, code="RATE_LIMIT_EXCEEDED")
