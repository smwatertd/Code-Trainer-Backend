from __future__ import annotations


class Failure:
    def __init__(self, code: str, message: str, status_code: int) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code}, message={self.message})"


class UnknownFailure(Failure):
    def __init__(self, message: str = "An unknown error occurred") -> None:
        super().__init__("UNKNOWN_ERROR", message, 500)


class ValidationFailure(Failure):
    def __init__(self, message: str) -> None:
        super().__init__("VALIDATION_ERROR", message, 422)


class NotFoundFailure(Failure):
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__("NOT_FOUND", f"{resource} with id {identifier} not found", 404)


class UnauthorizedFailure(Failure):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__("UNAUTHORIZED", message, 401)


class ConflictFailure(Failure):
    def __init__(self, message: str) -> None:
        super().__init__("CONFLICT", message, 409)


class ForbiddenFailure(Failure):
    def __init__(self, message: str = "Access denied") -> None:
        super().__init__("FORBIDDEN", message, 403)


class RateLimitFailure(Failure):
    def __init__(self, message: str) -> None:
        super().__init__("RATE_LIMIT_EXCEEDED", message, 429)


class InfrastructureFailure(Failure):
    def __init__(self, message: str, status_code: int = 503) -> None:
        super().__init__("INFRASTRUCTURE_ERROR", message, status_code)


class ApplicationError(Exception):
    def __init__(self, failure: Failure) -> None:
        self.failure = failure
