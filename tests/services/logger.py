from src.core.logger.app_logger import AppLogger


class TestLogger(AppLogger):
    def debug(self, message: str) -> None:
        return None

    def info(self, message: str) -> None:
        return None

    def warning(self, message: str) -> None:
        return None

    def error(self, message: str) -> None:
        return None

    def critical(self, message: str) -> None:
        return None
