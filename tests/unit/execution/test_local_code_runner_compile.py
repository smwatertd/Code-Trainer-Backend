from __future__ import annotations

from pathlib import Path

import pytest

from src.features.languages.services.language_loader import LanguageLoader
from src.features.languages.services.language_registry import LanguageRegistry
from src.shared.execution.checking.local_code_runner import LocalCodeRunner
from tests.helpers.toolchain import require_fpc

_LANGUAGES_DIR = Path(__file__).resolve().parents[3] / "languages"


@pytest.fixture
def local_runner() -> LocalCodeRunner:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(_LANGUAGES_DIR)
    return LocalCodeRunner(registry)


def test_local_code_runner__cpp_compile_and_run_passes(local_runner: LocalCodeRunner) -> None:
    code = (
        "#include <iostream>\n"
        "int main() {\n"
        "  for (int i = 0; i < 3; ++i) std::cout << i << '\\n';\n"
        "  return 0;\n"
        "}\n"
    )
    results = local_runner.run_tests(
        "cpp",
        code,
        [{"inputs": "", "output": "0\n1\n2"}],
    )

    assert len(results) == 1
    assert results[0].status == "PASSED"


def test_local_code_runner__pascal_compile_and_run_passes(local_runner: LocalCodeRunner) -> None:
    require_fpc()
    code = "program T;\n" "var i: integer;\n" "begin\n" "  for i := 1 to 3 do\n" "    writeln(i);\n" "end.\n"
    results = local_runner.run_tests(
        "pascal",
        code,
        [{"inputs": "", "output": "1\n2\n3"}],
    )

    assert len(results) == 1
    assert results[0].status == "PASSED"
