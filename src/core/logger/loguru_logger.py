from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger as _logger

from src.core.logger.app_logger import AppLogger
from src.core.logger.pii_redactor import redact_pii_text


class LoguruLogger(AppLogger):
    _configured = False
    _logger_levels: dict[str, int] = {}

    @staticmethod
    def _redact_record(record: Any) -> None:
        record["message"] = redact_pii_text(str(record.get("message", "")))
        extra = record.get("extra", {})
        for key, value in list(extra.items()):
            if isinstance(value, str):
                extra[key] = redact_pii_text(value)

    def __init__(
        self,
        name: str,
        *,
        level: str = "INFO",
        log_dir: str | Path | None = None,
        rotation: str = "10 MB",
        retention: str = "14 days",
        compression: str = "zip",
        enqueue: bool = True,
    ) -> None:
        LoguruLogger._logger_levels[name] = _logger.level(level).no
        if not LoguruLogger._configured:
            self._setup_sinks(
                name=name,
                level=level,
                log_dir=log_dir,
                rotation=rotation,
                retention=retention,
                compression=compression,
                enqueue=enqueue,
            )
            LoguruLogger._configured = True

        self._logger = _logger.patch(self._redact_record).bind(logger=name)

    @staticmethod
    def _setup_sinks(
        *,
        name: str,
        level: str,
        log_dir: str | Path | None,
        rotation: str,
        retention: str,
        compression: str,
        enqueue: bool,
    ) -> None:
        if log_dir is None:
            log_dir = Path(__file__).resolve().parents[3] / "logs"
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        _logger.remove()

        _logger.add(
            log_dir / "app.log",
            level="TRACE",
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=enqueue,
            filter=lambda record: record["extra"].get("logger") is not None,
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[logger]: <12} | "
                "{file.name}:{line}:{function} | {message}"
            ),
        )

        _logger.add(
            lambda msg: (log_dir / f"{msg.record['extra'].get('logger', 'default')}.log").open("a").write(msg),  # type: ignore
            level="TRACE",
            filter=lambda record: (
                record["extra"].get("logger") is not None
                and record["level"].no >= LoguruLogger._logger_levels.get(record["extra"].get("logger"), 0)  # type: ignore
            ),
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[logger]: <12} | "
                "{file.name}:{line}:{function} | {message}"
            ),
        )

    def bind(self, **kwargs: Any) -> LoguruLogger:
        return LoguruLogger.__new_with_logger(self._logger.bind(**kwargs))

    @classmethod
    def __new_with_logger(cls, logger_obj: Any) -> LoguruLogger:
        obj = cls.__new__(cls)
        obj._logger = logger_obj
        return obj

    def debug(self, message: str) -> None:
        self._logger.opt(depth=1).debug(message)

    def info(self, message: str) -> None:
        self._logger.opt(depth=1).info(message)

    def warning(self, message: str) -> None:
        self._logger.opt(depth=1).warning(message)

    def error(self, message: str) -> None:
        self._logger.opt(depth=1).error(message)

    def critical(self, message: str) -> None:
        self._logger.opt(depth=1).critical(message)
