from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class LanguageFeature(str, Enum):
    LINT = "lint"
    COMPILE = "compile"
    TEST = "test"


@dataclass(frozen=True)
class LocalCommandConfig:
    command: tuple[str, ...]


@dataclass(frozen=True)
class DockerConfig:
    image: str
    lint: str | None = None
    compile: str | None = None
    run: str | None = None
    lint_container: str | None = None


@dataclass(frozen=True)
class ExecutionTestConfig:
    strategy: str = "unsupported"
    compile_once: bool = False
    batch_one_shot: bool = False
    timeout_seconds: int = 2
    compile: tuple[str, ...] | None = None
    run: tuple[str, ...] | None = None
    docker_one_shot: str | None = None
    local_one_shot: str | None = None


@dataclass(frozen=True)
class PatternsConfig:
    normalization_key: str | None = None


@dataclass(frozen=True)
class LanguageConfig:
    id: str
    label: str
    file_extension: str
    monaco_language: str = ""
    tree_sitter_grammar: str = ""
    supported_features: frozenset[LanguageFeature] = field(default_factory=frozenset)
    local_lint: LocalCommandConfig | None = None
    local_compile: LocalCommandConfig | None = None
    docker: DockerConfig | None = None
    test: ExecutionTestConfig = field(default_factory=ExecutionTestConfig)
    patterns: PatternsConfig | None = None

    def __post_init__(self) -> None:
        if not self.monaco_language:
            object.__setattr__(self, "monaco_language", self.id)
        if not self.tree_sitter_grammar:
            object.__setattr__(self, "tree_sitter_grammar", self.id)

    def supports(self, feature: LanguageFeature) -> bool:
        return feature in self.supported_features
