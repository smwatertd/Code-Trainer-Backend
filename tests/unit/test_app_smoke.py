from __future__ import annotations

from src.core.rest import create_app


def test_create_app_returns_fastapi_instance() -> None:
    app = create_app()
    assert app.title == "Code Trainer API"
