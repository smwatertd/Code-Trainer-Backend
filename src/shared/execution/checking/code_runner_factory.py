from __future__ import annotations

from src.core.settings import ExecutionSettings
from src.features.languages.services.language_registry import LanguageRegistry
from src.shared.execution.checking.code_runner import CodeRunner
from src.shared.execution.checking.docker_code_runner import DockerCodeRunner
from src.shared.execution.checking.local_code_runner import LocalCodeRunner


def create_code_runner(
    registry: LanguageRegistry,
    *,
    prefer_docker: bool = True,
    execution_settings: ExecutionSettings | None = None,
) -> CodeRunner:
    if prefer_docker:
        docker_runner = DockerCodeRunner(registry, execution_settings=execution_settings)
        if docker_runner.is_available():
            return docker_runner
    return LocalCodeRunner(registry)
