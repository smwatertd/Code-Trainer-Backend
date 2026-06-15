from __future__ import annotations

from httpx import AsyncClient


async def delete_all_task_links(
    client: AsyncClient,
    headers: dict[str, str],
    task_id: int,
) -> None:
    response = await client.get(f"/api/curriculum/tasks/{task_id}/links", headers=headers)
    response.raise_for_status()
    for link in response.json().get("links", []):
        await client.delete(
            f"/api/curriculum/tasks/{task_id}/links/{link['id']}",
            headers=headers,
        )
