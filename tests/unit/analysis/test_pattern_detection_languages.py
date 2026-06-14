from __future__ import annotations

import pytest

from src.shared.analysis.educational_validator import EducationalValidator
from src.shared.execution.checking.pattern_checker import PatternChecker

_validator = EducationalValidator()
_checker = PatternChecker()


@pytest.mark.parametrize(
    ("language", "code", "expected_missing"),
    [
        (
            "cpp",
            "int main(){ for(int i=0;i<3;++i) std::cout<<i; return 0; }",
            False,
        ),
        (
            "cpp",
            "int main(){ std::cout<<0; return 0; }",
            True,
        ),
        (
            "pascal",
            "program T; var i: integer; begin for i := 1 to 3 do writeln(i); end.",
            False,
        ),
        (
            "pascal",
            "program T; begin writeln(0); end.",
            True,
        ),
    ],
)
def test_pattern_detection__for_loop_in_cpp_and_pascal(
    language: str,
    code: str,
    expected_missing: bool,
) -> None:
    missing = _validator.missing_structure_labels(code, language, ["for_loop"])

    if expected_missing:
        assert missing
        assert "Цикл" in missing[0]
    else:
        assert missing == []


def test_pattern_checker__cpp_if_statement_detection() -> None:
    code = "int main(){ if(1) return 0; return 1; }"
    missing = _checker.check(code, "cpp", ["if_statement"])
    assert missing == []


def test_pattern_checker__pascal_if_statement_detection() -> None:
    code = "program T; begin if 1 > 0 then writeln('yes'); end."
    missing = _checker.check(code, "pascal", ["if_statement"])
    assert missing == []
