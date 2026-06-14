"""Общие хелперы для seed-каталогов задач."""
from __future__ import annotations

from migrations.seeds.block_helpers import block_reorder_payload

TaskRow = dict


def row(
    task_id: int,
    title: str,
    description: str,
    difficulty: str,
    task_type: str,
    payload: dict,
) -> TaskRow:
    return {
        "id": task_id,
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "task_type": task_type,
        "visibility": "public",
        "workflow_status": "active",
        "is_deleted": False,
        "payload": payload,
    }


def translation_payload(
    *,
    topics: list[str],
    source_code: str,
    test_cases: list[dict[str, str]],
    constructions: list[str],
    code_examples: dict[str, str],
    template: str = "",
) -> dict:
    payload: dict = {
        "topics": topics,
        "source_language": "python",
        "source_code": source_code,
        "target_language": "pascal",
        "test_cases": test_cases,
        "constructions": constructions,
        "code_examples": code_examples,
    }
    if template:
        payload["template"] = template
        payload["kind"] = "debug"
    return payload


def block_task(
    task_id: int,
    title: str,
    description: str,
    difficulty: str,
    *,
    topics: list[str],
    constructions: list[str],
    code_examples: dict[str, str],
    pascal_blocks: list[str],
    correct_order: list[int],
    expected_pascal: str,
    test_cases: list[dict[str, str]],
) -> TaskRow:
    payload = block_reorder_payload(
        blocks=pascal_blocks,
        correct_order=correct_order,
        expected_code=expected_pascal,
        output=test_cases[0]["output"],
        topics=topics,
        language="pascal",
    )
    payload["test_cases"] = test_cases
    payload["constructions"] = constructions
    payload["code_examples"] = code_examples
    payload["source_language"] = "python"
    return row(task_id, title, description, difficulty, "task_build_from_blocks", payload)


def translate_task(
    task_id: int,
    title: str,
    description: str,
    difficulty: str,
    *,
    topics: list[str],
    constructions: list[str],
    code_examples: dict[str, str],
    test_cases: list[dict[str, str]],
    template: str = "",
) -> TaskRow:
    payload = translation_payload(
        topics=topics,
        source_code=code_examples["python"],
        test_cases=test_cases,
        constructions=constructions,
        code_examples=code_examples,
        template=template,
    )
    return row(task_id, title, description, difficulty, "translation", payload)


def tc(inputs: str, output: str) -> dict[str, str]:
    return {"inputs": inputs, "output": output}


def wrap_pascal(body: str) -> str:
    text = body.strip()
    if text.lower().startswith("program"):
        return text
    return f"program Main;\n{text}"


def pascal_blocks_from_body(body: str) -> tuple[list[str], str]:
    wrapped = wrap_pascal(body)
    lines: list[str] = []
    for part in wrapped.splitlines():
        part = part.strip()
        if not part:
            continue
        if part.startswith("var ") and lines and lines[-1] != "begin":
            lines.append(part)
        elif part == "begin":
            lines.append(part)
        elif part in {"end.", "end;"}:
            lines.append("end.")
        elif part.startswith("program "):
            lines.append(part)
        else:
            if "begin" not in lines:
                if part.startswith("var "):
                    lines.append(part)
                    lines.append("begin")
                else:
                    lines.append("begin")
                    lines.append(part if part.endswith(";") else part + ";")
            else:
                lines.append(part if part.endswith(";") or part == "end." else part + ";")
    if lines and lines[0].startswith("program") and len(lines) == 1:
        lines.append("begin")
        lines.append("end.")
    if "end." not in lines:
        lines.append("end.")
    order = list(range(len(lines)))
    expected_lines = []
    for line in lines:
        if line.startswith("program"):
            expected_lines.append(line)
        elif line == "begin":
            expected_lines.append("begin")
        elif line == "end.":
            expected_lines.append("end.")
        else:
            expected_lines.append(f"  {line}")
    expected = "\n".join(expected_lines)
    return lines, expected
