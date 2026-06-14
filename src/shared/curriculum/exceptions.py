from __future__ import annotations


class CurriculumError(Exception):
    pass


class CurriculumNotFoundError(CurriculumError):
    pass


class CurriculumLinkValidationError(CurriculumError):
    pass


class CurriculumValidationError(CurriculumError):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        message = "; ".join(errors) if errors else "Curriculum validation failed"
        super().__init__(message)
