from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_api_contract__public_endpoints_are_available(client: AsyncClient) -> None:
    cases = [
        ("/api/health", 200),
        ("/api/health/ready", {200, 503}),
        ("/api/languages", 200),
        ("/api/catalog/tasks", 200),
        ("/api/catalog/tasks/2", 200),
    ]

    for path, expected in cases:
        response = await client.get(path)
        if isinstance(expected, set):
            assert response.status_code in expected, f"{path}: {response.text}"
        else:
            assert response.status_code == expected, f"{path}: {response.text}"


@pytest.mark.asyncio(loop_scope="session")
async def test_api_contract__protected_endpoints_require_auth(client: AsyncClient) -> None:
    cases = [
        ("GET", "/api/auth/me", None),
        ("POST", "/api/submissions", {"task_id": 2, "language": "python", "code": "print(1)"}),
        ("GET", "/api/submissions/1", None),
        ("GET", "/api/submissions/pending/latest?task_id=2", None),
    ]

    for method, path, json_body in cases:
        response = await client.request(method, path, json=json_body)
        assert response.status_code == 401, f"{method} {path}: {response.text}"
        assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio(loop_scope="session")
async def test_readiness__response_documents_dependency_checks(client: AsyncClient) -> None:
    response = await client.get("/api/health/ready")
    payload = response.json()

    assert "status" in payload
    assert "checks" in payload
    assert set(payload["checks"]) == {"database", "redis"}
    assert payload["checks"]["database"]["status"] == "up"
