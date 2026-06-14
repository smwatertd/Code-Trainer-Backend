from __future__ import annotations

from httpx import AsyncClient


async def submit_demo_check(client: AsyncClient, payload: dict) -> dict:
    response = await client.post("/api/demo/check", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


async def poll_demo_check(client: AsyncClient, job_id: str) -> dict:
    response = await client.get(f"/api/demo/check/{job_id}")
    assert response.status_code == 200, response.text
    return response.json()


async def run_demo_check(client: AsyncClient, payload: dict) -> dict:
    queued = await submit_demo_check(client, payload)
    return await poll_demo_check(client, queued["job_id"])
