from __future__ import annotations

from pydantic import BaseModel, Field


class LanguageResponse(BaseModel):
    id: str
    label: str
    file_extension: str
    monaco_language: str
    supported_features: list[str] = Field(default_factory=list)
