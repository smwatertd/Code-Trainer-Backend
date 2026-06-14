from __future__ import annotations

from httpx import Response


def assert_api_error(
    response: Response,
    *,
    status: int,
    code: str,
    message: str | None = None,
) -> dict:
    assert response.status_code == status, response.text
    body = response.json()
    assert body["error"]["code"] == code
    if message is not None:
        assert body["error"]["message"] == message
    return body
