from __future__ import annotations

import typer

app = typer.Typer(help="Code Trainer backend management CLI")


@app.command("api")
def run_api(
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(8000, help="Bind port"),
    reload: bool = typer.Option(False, help="Enable auto-reload (dev)"),
) -> None:
    import uvicorn

    uvicorn.run(
        "src.core.rest:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
    )


@app.command("worker")
def run_worker() -> None:
    from src.workers.execution_worker import run_worker

    run_worker()


@app.command("seed-dev")
def seed_dev() -> None:
    """Create local dev accounts (student/teacher/admin) if missing."""
    import asyncio

    from src.dev.seed_users import seed_dev_users

    asyncio.run(seed_dev_users())


if __name__ == "__main__":
    app()
