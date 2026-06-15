from __future__ import annotations

from src.features.catalog.mappers import (
    _attach_student_metadata,
    _code_examples_from_blocks,
    _public_block_reorder_payload,
    _public_constructions,
    _public_payload,
    _public_placeholder_payload,
    _public_test_cases,
    _public_translation_payload,
)


def test_public_test_cases__normalizes_legacy_field_names() -> None:
    cases = _public_test_cases(
        {
            "test_cases": [
                {"input": "1\n", "expected_output": "1\n"},
                {"inputs": "2\n", "output": "2\n"},
                {"inputs": "", "expected": "ok"},
                "broken",
                None,
            ]
        }
    )

    assert cases == [
        {"inputs": "1\n", "output": "1\n"},
        {"inputs": "2\n", "output": "2\n"},
        {"inputs": "", "output": "ok"},
    ]


def test_public_test_cases__returns_empty_when_missing_or_invalid() -> None:
    assert _public_test_cases({}) == []
    assert _public_test_cases({"test_cases": "nope"}) == []
    assert _public_test_cases({"test_cases": []}) == []


def test_public_constructions__filters_empty_values() -> None:
    assert _public_constructions({"constructions": ["for_loop", "", None, "if_statement"]}) == [
        "for_loop",
        "if_statement",
    ]
    assert _public_constructions({}) == []


def test_code_examples_from_blocks__joins_block_contents() -> None:
    examples = _code_examples_from_blocks(
        {
            "python": [{"id": 0, "content": "print('a')"}, {"id": 1, "content": "print('b')"}],
            "cpp": [{"id": 0, "content": 'cout << "a";'}, {"id": 1, "content": ""}],
        }
    )

    assert examples["python"] == "print('a')\nprint('b')"
    assert examples["cpp"] == 'cout << "a";'
    assert "pascal" not in examples


def test_attach_student_metadata__adds_hints_when_present() -> None:
    public = _attach_student_metadata(
        {"language": "python"},
        {
            "test_cases": [{"inputs": "", "output": "42"}],
            "constructions": ["for_loop"],
            "construction_hints": {"for_loop": {"title": "Цикл"}},
            "flow_spec": {"secret": True},
        },
    )

    assert public["test_cases"] == [{"inputs": "", "output": "42"}]
    assert public["constructions"] == ["for_loop"]
    assert public["construction_hints"] == {"for_loop": {"title": "Цикл"}}
    assert "flow_spec" not in public


def test_public_translation_payload__exposes_student_fields_hides_secrets() -> None:
    payload = _public_translation_payload(
        {
            "source_language": "python",
            "target_language": "cpp",
            "source_code": "print('Hello')",
            "template": "int main() {}",
            "test_cases": [{"inputs": "", "output": "Hello"}],
            "constructions": ["io"],
            "kind": "snippet",
            "patterns": ["secret"],
            "expected_code": "cout << Hello;",
        }
    )

    assert payload["code_examples"] == {"python": "print('Hello')"}
    assert payload["test_cases"] == [{"inputs": "", "output": "Hello"}]
    assert payload["constructions"] == ["io"]
    assert "kind" not in payload
    assert "patterns" not in payload
    assert "expected_code" not in payload


def test_public_translation_payload__exposes_all_code_examples_for_parallel_languages() -> None:
    payload = _public_translation_payload(
        {
            "source_language": "python",
            "target_language": "pascal",
            "source_code": "w = int(input())\nh = int(input())\nprint(2 * (w + h))",
            "code_examples": {
                "python": "w = int(input())\nh = int(input())\nprint(2 * (w + h))",
                "pascal": "var w,h,p: integer;\nbegin\n  readln(w,h);\n  p:=2*(w+h);\n  writeln(p);\nend.",
                "cpp": "int w,h,p;\nstd::cin>>w>>h;\np=2*(w+h);\nstd::cout<<p;",
                "csharp": "var p=Console.ReadLine().Split();\nint w=int.Parse(p[0]),h=int.Parse(p[1]);\nConsole.WriteLine(2*(w+h));",
                "java": "Scanner sc=new Scanner(System.in);\nint w=sc.nextInt(),h=sc.nextInt();\nSystem.out.println(2*(w+h));",
            },
            "test_cases": [{"inputs": "4\n6\n", "output": "20"}],
        }
    )

    assert set(payload["code_examples"]) == {"python", "pascal", "cpp", "csharp", "java"}
    assert payload["code_examples"]["python"].startswith("w = int(input())")
    assert "readln(w,h)" in payload["code_examples"]["pascal"]


def test_public_block_reorder_payload__exposes_test_cases_and_code_examples() -> None:
    payload = _public_block_reorder_payload(
        {
            "blocks": ["print('a')", "print('b')"],
            "correct_order": [1, 0],
            "expected_code": "print('b')\nprint('a')",
            "language": "python",
            "test_cases": [{"inputs": "", "output": "b\na"}],
            "constructions": ["io"],
        }
    )

    assert "correct_order" not in payload
    assert "expected_code" not in payload
    assert payload["test_cases"] == [{"inputs": "", "output": "b\na"}]
    assert payload["constructions"] == ["io"]
    assert payload["code_examples"]["python"] == "print('a')\nprint('b')"
    assert payload["source_language"] == "python"


def test_public_block_reorder_payload__preserves_seed_code_examples() -> None:
    payload = _public_block_reorder_payload(
        {
            "blocks": ["program Main;", "begin", "writeln('Hello');", "end."],
            "language": "pascal",
            "code_examples": {
                "python": "print('Hello')",
                "pascal": "program Main;\nbegin\n  writeln('Hello');\nend.",
            },
            "constructions": ["program_entry", "stdout_write"],
        }
    )

    assert payload["code_examples"]["python"] == "print('Hello')"
    assert payload["code_examples"]["pascal"].startswith("program Main;")
    assert payload["constructions"] == ["program_entry", "stdout_write"]


def test_public_block_reorder_payload__exposes_template_for_fragment_assembly() -> None:
    payload = _public_block_reorder_payload(
        {
            "blocks": ["=", "print", "input"],
            "template": "x {0} 1\ny {1} 2\n{2}(x)",
            "correct_order": [0, 0, 1],
            "language": "python",
        }
    )

    assert payload["template"] == "x {0} 1\ny {1} 2\n{2}(x)"
    assert "correct_order" not in payload


def test_public_placeholder_payload__exposes_template_and_bank() -> None:
    payload = _public_placeholder_payload(
        {
            "language": "python",
            "target_language": "python",
            "placeholder_template": "name = ___()\nif total ___ 0:\n    print(name, total)",
            "placeholder_bank": ["input", "int", ">=", "print"],
            "code_examples": {"python": "name = input()"},
            "test_cases": [{"input": "a\n1\n1\n", "output": "a 1"}],
            "constructions": ["stdin_read", "if_statement"],
        }
    )

    assert payload["placeholder_template"].startswith("name = ___()")
    assert payload["placeholder_bank"] == ["input", "int", ">=", "print"]
    assert payload["code_examples"]["python"] == "name = input()"
    assert payload["test_cases"] == [{"inputs": "a\n1\n1\n", "output": "a 1"}]
    assert payload["constructions"] == ["stdin_read", "if_statement"]


def test_public_payload__routes_placeholder_tasks() -> None:
    payload = _public_payload(
        "task_fill_placeholders",
        {
            "language": "python",
            "placeholder_template": "print(___)",
            "placeholder_bank": ["input"],
        },
    )

    assert payload["placeholder_template"] == "print(___)"
    assert payload["placeholder_bank"] == ["input"]


def test_public_payload__translation_via_router_strips_internal_keys() -> None:
    payload = _public_payload(
        "translation",
        {
            "source_language": "python",
            "source_code": "print('x')",
            "target_language": "pascal",
            "test_cases": [{"inputs": "", "output": "x"}],
            "kind": "full_program",
            "patterns": ["hidden"],
        },
    )

    assert payload["test_cases"] == [{"inputs": "", "output": "x"}]
    assert payload["code_examples"] == {"python": "print('x')"}
    assert "kind" not in payload
    assert "patterns" not in payload
