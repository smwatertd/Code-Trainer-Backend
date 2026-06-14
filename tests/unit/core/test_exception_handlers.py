from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.core.either.failures import ApplicationError, NotFoundFailure
from src.core.rest import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.mark.asyncio
async def test_application_error_handler__returns_structured_json(app) -> None:
    @app.get("/test-not-found")
    async def _raise_not_found() -> None:
        raise ApplicationError(NotFoundFailure("Task", "42"))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/test-not-found")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "Task with id 42 not found",
            "details": None,
        }
    }
