from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.features.languages.domain.language_config import (
    DockerConfig,
    ExecutionTestConfig,
    LanguageConfig,
    LanguageFeature,
    LocalCommandConfig,
    PatternsConfig,
)
from src.features.languages.services.language_registry import LanguageRegistry

_FEATURE_MAP = {
    "lint": LanguageFeature.LINT,
    "compile": LanguageFeature.COMPILE,
    "test": LanguageFeature.TEST,
}


def _parse_command(raw: Any) -> tuple[str, ...] | None:
    if not raw:
        return None
    if isinstance(raw, dict) and "command" in raw:
        raw = raw["command"]
    if isinstance(raw, list):
        return tuple(str(part) for part in raw)
    return None


def _parse_docker(raw: dict[str, Any] | None) -> DockerConfig | None:
    if not raw:
        return None
    image = str(raw.get("image") or "").strip()
    if not image:
        return None
    return DockerConfig(
        image=image,
        lint=raw.get("lint"),
        compile=raw.get("compile"),
        run=raw.get("run"),
        lint_container=raw.get("lint_container"),
    )


def _parse_test(raw: dict[str, Any] | None) -> ExecutionTestConfig:
    if not raw:
        return ExecutionTestConfig()
    return ExecutionTestConfig(
        strategy=str(raw.get("strategy") or "unsupported"),
        compile_once=bool(raw.get("compile_once", False)),
        batch_one_shot=bool(raw.get("batch_one_shot", False)),
        timeout_seconds=int(raw.get("timeout_seconds") or 2),
        compile=_parse_command(raw.get("compile")),
        run=_parse_command(raw.get("run")),
        docker_one_shot=raw.get("docker_one_shot"),
        local_one_shot=raw.get("local_one_shot"),
    )


def _parse_config(data: dict[str, Any], source: Path) -> LanguageConfig:
    lang_id = str(data.get("id") or "").strip().lower()
    if not lang_id:
        raise ValueError(f"Language config in {source} is missing 'id'")

    features_raw = data.get("features") or []
    features = frozenset(_FEATURE_MAP[str(item).lower()] for item in features_raw if str(item).lower() in _FEATURE_MAP)

    local = data.get("local") or {}
    patterns_raw = data.get("patterns") or {}
    grammar_raw = data.get("grammar") or {}
    tree_sitter = (
        str(grammar_raw.get("tree_sitter") or data.get("tree_sitter_grammar") or lang_id)
        if isinstance(grammar_raw, dict)
        else str(grammar_raw or lang_id)
    )

    return LanguageConfig(
        id=lang_id,
        label=str(data.get("label") or lang_id),
        file_extension=str(data.get("file_extension") or f".{lang_id}"),
        monaco_language=str(data.get("monaco_language") or lang_id),
        tree_sitter_grammar=tree_sitter,
        supported_features=features,
        local_lint=(
            LocalCommandConfig(command=cmd) if (cmd := _parse_command(local.get("lint"))) is not None else None
        ),
        local_compile=(
            LocalCommandConfig(command=cmd) if (cmd := _parse_command(local.get("compile"))) is not None else None
        ),
        docker=_parse_docker(data.get("docker")),
        test=_parse_test(data.get("test")),
        patterns=(
            PatternsConfig(normalization_key=patterns_raw.get("normalization_key"))
            if patterns_raw.get("normalization_key")
            else None
        ),
    )


class LanguageLoader:
    def __init__(self, registry: LanguageRegistry) -> None:
        self._registry = registry

    def load_from_directory(self, directory: Path) -> int:
        self._registry.clear()
        if not directory.is_dir():
            raise FileNotFoundError(f"Languages directory not found: {directory}")

        count = 0
        for path in sorted(directory.glob("*.yml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError(f"Invalid language config (expected mapping): {path}")
            self._registry.register(_parse_config(raw, path))
            count += 1

        if count == 0:
            raise RuntimeError(f"No language configs found in {directory}")
        return count
