from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.core.containers import Container
from src.core.either.failures import ApplicationError
from src.core.logger import AppLogger
from src.features import get_routers


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[dict[str, str]] | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    container: Container = app.container  # type: ignore[attr-defined]
    settings = container.config()
    loader = container.languages.loader()
    loader.load_from_directory(settings.languages_dir)
    yield


def create_app(container: Container | None = None) -> FastAPI:
    container = container or Container()
    logger = container.logger()
    settings = container.config()

    app = FastAPI(
        title=settings.title,
        version=settings.version,
        debug=settings.debug,
        description="Educational platform for comparing programming languages",
        docs_url=settings.docs_url,
        openapi_url="/api/openapi.json",
        lifespan=_lifespan,
    )
    app.container = container  # type: ignore[attr-defined]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origin_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _add_exception_handlers(app, logger)

    for router in get_routers():
        app.include_router(router, prefix="/api")

    container.wire()
    return app


def _add_exception_handlers(app: FastAPI, logger: AppLogger) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
            message = error["msg"]
            error_type = error["type"]

            if error_type == "missing":
                friendly_message = f"Field '{field}' is required"
            elif error_type == "string_type":
                friendly_message = f"Field '{field}' must be a string"
            elif error_type == "value_error":
                friendly_message = message
            else:
                friendly_message = f"Field '{field}': {message}"

            errors.append(
                {
                    "field": field,
                    "message": friendly_message,
                }
            )

        logger.warning(
            f"Validation error: {len(errors)} field(s), errors={errors}, path={request.url.path}",
        )

        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error=ErrorBody(code="VALIDATION_ERROR", message="Validation error", details=errors),
            ).model_dump(),
        )

    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
        failure = exc.failure
        logger.warning(
            f"Application error: {failure.code}, message={failure.message}, path={request.url.path}",
        )
        return JSONResponse(
            status_code=failure.status_code,
            content=ErrorResponse(
                error=ErrorBody(code=failure.code, message=failure.message),
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            f"Unhandled exception, exception details: {exc}, path={request.url.path}",
        )
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error=ErrorBody(code="INTERNAL_ERROR", message="Internal server error"),
            ).model_dump(),
        )
