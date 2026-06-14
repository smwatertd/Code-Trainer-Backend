from __future__ import annotations

from httpx import AsyncClient


async def submit_submission(
    client: AsyncClient,
    headers: dict[str, str],
    payload: dict,
) -> dict:
    response = await client.post("/api/submissions", headers=headers, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


async def get_submission(
    client: AsyncClient,
    headers: dict[str, str],
    submission_id: int,
) -> dict:
    response = await client.get(f"/api/submissions/{submission_id}", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


async def submit_and_get(
    client: AsyncClient,
    headers: dict[str, str],
    payload: dict,
) -> dict:
    queued = await submit_submission(client, headers, payload)
    return await get_submission(client, headers, queued["id"])
