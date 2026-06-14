from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.http import assert_api_error
from tests.e2e.helpers.payloads import DEMO_CHECK_PAYLOAD, TASK1_HELLO_BLOCKS


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__poll_job_from_different_ip_returns_403(client: AsyncClient) -> None:
    submit = await client.post(
        "/api/demo/check",
        json=DEMO_CHECK_PAYLOAD,
        headers={"X-Forwarded-For": "10.0.0.1"},
    )
    assert submit.status_code == 200
    job_id = submit.json()["job_id"]

    poll = await client.get(
        f"/api/demo/check/{job_id}",
        headers={"X-Forwarded-For": "10.0.0.2"},
    )

    assert_api_error(poll, status=403, code="FORBIDDEN")


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__poll_job_from_same_ip_succeeds(client: AsyncClient) -> None:
    headers = {"X-Forwarded-For": "10.0.0.99"}
    submit = await client.post(
        "/api/demo/check",
        json=TASK1_HELLO_BLOCKS,
        headers=headers,
    )
    assert submit.status_code == 200
    job_id = submit.json()["job_id"]

    poll = await client.get(f"/api/demo/check/{job_id}", headers=headers)

    assert poll.status_code == 200
    assert poll.json()["status"] in {"SUCCESS", "FAILED", "QUEUED", "RUNNING"}


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__guest_disabled_get_returns_404(guest_disabled_client: AsyncClient) -> None:
    response = await guest_disabled_client.get("/api/demo/check/any-job-id")

    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__empty_code_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/api/demo/check",
        json={"task_id": 1, "language": "python", "code": ""},
    )

    assert_api_error(response, status=422, code="VALIDATION_ERROR")


@pytest.mark.asyncio(loop_scope="session")
async def test_demo__concurrent_submit_while_job_running_returns_429(
    concurrent_guest_client: AsyncClient,
) -> None:
    first = await concurrent_guest_client.post("/api/demo/check", json=DEMO_CHECK_PAYLOAD)
    second = await concurrent_guest_client.post("/api/demo/check", json=DEMO_CHECK_PAYLOAD)

    assert first.status_code == 200
    body = assert_api_error(second, status=429, code="RATE_LIMIT_EXCEEDED")
    assert "already in progress" in body["error"]["message"].lower()
