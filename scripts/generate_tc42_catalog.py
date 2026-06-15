#!/usr/bin/env python3
"""Generate TC42 course catalog seed module from the reworked PDF."""

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import pdfplumber
except ImportError:
    print("pdfplumber is required: pip install pdfplumber", file=sys.stderr)
    sys.exit(1)

DEFAULT_PDF = (
    Path(__file__).resolve().parents[3]
    / "algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED_1.pdf"
)
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parents[1] / "migrations/seeds/tc42_course_catalog_generated.py"
)

LANG_MAP = {
    "Pascal": "pascal",
    "Python": "python",
    "C++": "cpp",
    "C#": "csharp",
    "Java": "java",
}
LANG_PRIORITY = ("python", "pascal", "cpp", "csharp", "java")
IMPL_MAP = {
    "Сборка по блокам полностью": "block_full",
    "Сборка с плейсхолдерами": "placeholder",
    "Перевод кода": "translation",
    "Исправление ошибок": "debug",
}
DIFF_MAP = {
    "легкий": "easy",
    "лёгкий": "easy",
    "средний": "medium",
    "сложный": "hard",
}

logger = logging.getLogger("generate_tc42_catalog")


@dataclass
class ParsedTask:
    task_id: int
    title: str
    brief: str
    description: str
    difficulty: str
    impl_type: str
    test_cases: list[dict[str, str]] = field(default_factory=list)
    concepts: dict[str, list[str]] = field(default_factory=dict)
    blocks_by_lang: dict[str, list[str]] = field(default_factory=dict)
    placeholder_by_lang: dict[str, str] = field(default_factory=dict)
    placeholder_bank_by_lang: dict[str, list[str]] = field(default_factory=dict)
    placeholder_fills_by_lang: dict[str, list[str]] = field(default_factory=dict)
    code_by_lang: dict[str, str] = field(default_factory=dict)
    buggy_by_lang: dict[str, str] = field(default_factory=dict)
    chapter_id: str = ""
    is_full: bool = False
    warnings: list[str] = field(default_factory=list)


def extract_pdf_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join((page.extract_text() or "") for page in pdf.pages)


def parse_chapters(text: str) -> dict[int, tuple[str, str]]:
    chapters: dict[int, tuple[str, str]] = {}
    for match in re.finditer(r"Глава (\d+)\. (.+?)(?=\nЗадача|\nГлава|$)", text):
        num = int(match.group(1))
        title = match.group(2).strip()
        chapters[num] = (f"chapter_{num}", title)
    return chapters


def split_langs(section: str) -> dict[str, str]:
    section = section.strip()
    parts = re.split(r"(?:^|\n)(Pascal|Python|C\+\+|C#|Java):\s*\n", section)
    result: dict[str, str] = {}
    for index in range(1, len(parts), 2):
        lang_name = parts[index]
        body = parts[index + 1]
        body = re.split(r"(?:^|\n)(?:Pascal|Python|C\+\+|C#|Java):\s*\n", body)[0]
        body = body.split("Задача ")[0]
        result[lang_name] = body.strip()
    return result


def parse_numbered_blocks(text: str) -> list[str]:
    blocks: dict[int, str] = {}
    marker = re.compile(r"(?:^|\n)\[(\d+)\]\s*", re.M)
    matches = list(marker.finditer(text))
    if not matches:
        return []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[int(match.group(1))] = text[start:end].strip()
    return [blocks[num] for num in sorted(blocks)]


def blocks_to_code(blocks: list[str]) -> str:
    return "\n".join(block.strip() for block in blocks if block.strip())


def parse_test_cases(text: str) -> list[dict[str, str]]:
    match = re.search(
        r"Тест-кейсы:\s*\n№ Вход / данные Ожидаемый вывод / результат\s*\n"
        r"(.*?)(?=Expected Concepts|Материал задания|$)",
        text,
        re.S,
    )
    if not match:
        return []
    cases: list[dict[str, str]] = []
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        output = parts[-1]
        inputs_raw = " ".join(parts[1:-1])
        inputs = "\n".join(inputs_raw.split()) + "\n"
        cases.append({"inputs": inputs, "output": output})
    return cases


def parse_concepts(text: str) -> dict[str, list[str]]:
    match = re.search(
        r"Expected Concepts по языкам:\s*\nЯзык expected_concept_ids\s*\n(.*?)(?=Материал задания|$)",
        text,
        re.S,
    )
    concepts: dict[str, list[str]] = {}
    if not match:
        return concepts
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line:
            continue
        for lang_name, key in LANG_MAP.items():
            if line.startswith(lang_name + " "):
                concepts[key] = [part.strip() for part in line[len(lang_name) :].strip().split(",") if part.strip()]
                break
    return concepts


def parse_placeholder_bank(body: str) -> list[str]:
    match = re.search(
        r"Недостающие блоки:\s*\n(?:id что пропущено answer options\s*\n)?(.*)",
        body,
        re.S,
    )
    if not match:
        return []
    raw = match.group(1).split("Задача ")[0]
    bank: list[str] = []

    for line in raw.splitlines():
        line = " ".join(line.split())
        if not line or line.startswith("id ") or ";" not in line or not re.match(r"^p\d+\s", line):
            continue
        before, after = line.split(";", 1)
        placeholder = before.split()[-1]
        options = [placeholder] + [part.strip() for part in after.split(";") if part.strip()]
        for option in options:
            option = re.sub(r"\s+(?:найденного товара|совпадения)$", "", option).strip()
            if option and option not in bank:
                bank.append(option)

    merged = " ".join(
        line.strip()
        for line in raw.splitlines()
        if line.strip() and not line.startswith("id ")
    )
    for entry in re.findall(r"p\d+\s+.*?(?=p\d+\s|$)", merged, re.S):
        repeat = re.search(r"((?:\S+(?: \S+){0,4})) \1((?:; [^;]+)+)", entry)
        if repeat:
            for option in [repeat.group(1)] + [part.strip() for part in repeat.group(2).split(";") if part.strip()]:
                if option and option not in bank:
                    bank.append(option)
    return bank


def parse_placeholder_correct_fills(body: str) -> list[str]:
    match = re.search(
        r"Недостающие блоки:\s*\n(?:id что пропущено answer options\s*\n)?(.*)",
        body,
        re.S,
    )
    if not match:
        return []
    raw = match.group(1).split("Задача ")[0]
    merged = " ".join(
        line.strip()
        for line in raw.splitlines()
        if line.strip() and not line.startswith("id ")
    )
    fills: list[str] = []
    for entry in re.findall(r"p\d+\s+.*?(?=p\d+\s|$)", merged + " ", re.S):
        repeat = re.search(r"(\S+)\s+\1((?:;\s*\S+)+)", entry)
        if repeat:
            fills.append(repeat.group(1))
    return fills


def assemble_placeholder_reference(template: str, fills: list[str]) -> str:
    result = template
    for fill in fills:
        if "___" not in result:
            break
        result = result.replace("___", fill, 1)
    return result


def normalize_python_indentation(code: str) -> str:
    """Restore block indentation stripped by PDF extraction."""
    lines = code.splitlines()
    result: list[str] = []
    indent = 0
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            result.append("")
            continue
        if stripped.startswith(("elif ", "else:", "except", "finally:")):
            indent = max(0, indent - 1)
        result.append(("    " * indent) + stripped)
        if stripped.endswith(":") and not stripped.startswith("#"):
            indent += 1
    return "\n".join(result)


def format_pascal_placeholder(code: str) -> str:
    """Split compressed Pascal placeholder templates into readable lines."""
    text = code.strip()
    if not text:
        return text
    if text.count("\n") >= 3:
        return text
    text = re.sub(r"\s+\bbegin\b", "\nbegin", text, flags=re.I)
    text = re.sub(r"\bbegin\b", "begin\n  ", text, count=1, flags=re.I)
    text = re.sub(r"\s+\bend\.", "\nend.", text, flags=re.I)
    text = re.sub(r";\s*", ";\n  ", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    return text.strip()


def maybe_normalize_code(language: str, code: str) -> str:
    if language == "python" and code.strip():
        return normalize_python_indentation(code)
    if language == "pascal" and code.strip() and "___" in code:
        return format_pascal_placeholder(code)
    return code


TEST_CASE_OVERRIDES: dict[int, list[dict[str, str]]] = {
    9: [
        {"inputs": "3 7 2\n", "output": "7"},
        {"inputs": "10 5 8\n", "output": "10"},
        {"inputs": "1 1 1\n", "output": "1"},
    ],
    11: [
        {"inputs": "3 4 5\n", "output": "scalene"},
        {"inputs": "5 5 5\n", "output": "equilateral"},
        {"inputs": "3 3 4\n", "output": "isosceles"},
    ],
    12: [
        {"inputs": "15 6\n", "output": "valid"},
        {"inputs": "32 6\n", "output": "invalid"},
        {"inputs": "15 13\n", "output": "invalid"},
    ],
    13: [
        {"inputs": "95\n", "output": "excellent"},
        {"inputs": "80\n", "output": "good"},
        {"inputs": "40\n", "output": "retry"},
    ],
}

TASK18_PYTHON_TEMPLATE = (
    "n, target = map(int, input().split())\n"
    "position = 0\n"
    "for i in range(1, n + 1):\n"
    "    value = int(input())\n"
    "    if value == ___ and position == 0:\n"
    "        position = ___\n"
    "print(position)"
)

TASK18_PYTHON_REFERENCE = (
    "n, target = map(int, input().split())\n"
    "position = 0\n"
    "for i in range(1, n + 1):\n"
    "    value = int(input())\n"
    "    if value == target and position == 0:\n"
    "        position = i\n"
    "print(position)"
)

TASK18_PASCAL_REFERENCE = (
    "var i, n, target, value, position: integer;\n"
    "begin\n"
    "  readln(n, target);\n"
    "  position := 0;\n"
    "  for i := 1 to n do\n"
    "  begin\n"
    "    readln(value);\n"
    "    if (value = target) and (position = 0) then position := i;\n"
    "  end;\n"
    "  writeln(position);\n"
    "end."
)

TASK_PLACEHOLDER_OVERRIDES: dict[int, dict[str, Any]] = {
    18: {
        "language": "python",
        "target_language": "python",
        "source_language": "python",
        "placeholder_template": TASK18_PYTHON_TEMPLATE,
        "placeholder_bank": ["target", "value", "i", "position", "0", "n"],
        "test_cases": [
            {"inputs": "5 9\n2\n9\n1\n7\n4\n", "output": "2"},
            {"inputs": "5 3\n1\n2\n3\n4\n5\n", "output": "3"},
            {"inputs": "1 7\n7\n", "output": "1"},
        ],
        "code_examples": {
            "python": TASK18_PYTHON_REFERENCE,
            "pascal": TASK18_PASCAL_REFERENCE,
            "cpp": (
                "#include <iostream>\n"
                "int main(){\n"
                "int n,target; std::cin>>n>>target;\n"
                "int position=0;\n"
                "for(int i=1;i<=n;i++){\n"
                "int value; std::cin>>value;\n"
                "if(value==target && position==0) position=i;\n"
                "}\n"
                "std::cout<<position;\n"
                "}"
            ),
            "csharp": (
                "using System;\n"
                "class Program{static void Main(){\n"
                "var p=Console.ReadLine().Split(); int n=int.Parse(p[0]), target=int.Parse(p[1]);\n"
                "int position=0;\n"
                "for(int i=1;i<=n;i++){int value=int.Parse(Console.ReadLine());\n"
                "if(value==target && position==0) position=i;}\n"
                "Console.WriteLine(position);}}"
            ),
            "java": (
                "import java.util.*;\n"
                "class Main{public static void main(String[] args){\n"
                "Scanner sc=new Scanner(System.in);\n"
                "int n=sc.nextInt(), target=sc.nextInt(), position=0;\n"
                "for(int i=1;i<=n;i++){int value=sc.nextInt();\n"
                "if(value==target && position==0) position=i;}\n"
                "System.out.println(position);}}"
            ),
        },
    },
}


def parse_code_section(body: str, label: str) -> str:
    match = re.search(
        rf"{re.escape(label)}:\s*\n(.*?)(?=Правильный вариант:|Ошибки для внутренней проверки:|"
        r"Код с ошибками:|Код с плейсхолдерами:|Недостающие блоки:|$)",
        body,
        re.S,
    )
    return match.group(1).strip() if match else ""


def parse_plain_code(body: str) -> str:
    code = body.strip()
    code = re.split(r"Ошибки для внутренней проверки:", code)[0].strip()
    return code


def expected_from_pascal_blocks(blocks: list[str]) -> str:
    lines: list[str] = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith("program") or block == "begin":
            lines.append(block)
        elif block in {"end.", "end;"}:
            lines.append("end.")
        else:
            for subline in block.splitlines():
                subline = subline.strip()
                if subline:
                    lines.append(f"  {subline}")
    if lines and lines[-1] != "end.":
        lines.append("end.")
    return "\n".join(lines)


def pick_language(data: dict[str, Any], *, require_placeholder: bool = False) -> str | None:
    for lang in LANG_PRIORITY:
        value = data.get(lang)
        if not value:
            continue
        if require_placeholder and "___" not in value:
            continue
        return lang
    if require_placeholder:
        for lang, value in data.items():
            if value and "___" in value:
                return lang
    return next(iter(data), None) if data else None


def chapter_for_task(task_id: int, chapters: dict[int, tuple[str, str]]) -> str:
    chapter_num = (task_id - 1) // 8 + 1
    return chapters.get(chapter_num, (f"chapter_{chapter_num}", ""))[0]


def parse_tasks(text: str) -> list[ParsedTask]:
    chapters = parse_chapters(text)
    sections = [part for part in re.split(r"(?=Задача \d+\. )", text) if re.match(r"Задача \d+\. ", part)]
    tasks: list[ParsedTask] = []

    for section in sections:
        task_id = int(re.match(r"Задача (\d+)", section).group(1))
        title = re.search(r"Задача \d+\. (.+)", section).group(1).split("\n")[0].strip()
        brief_match = re.search(r"Краткое условие: (.+)", section)
        desc_match = re.search(r"Подробное условие: (.+?)(?=Тип реализации:|$)", section, re.S)
        impl_match = re.search(r"Тип реализации: (.+)", section)
        diff_match = re.search(r"Сложность: (.+)", section)

        brief = brief_match.group(1).strip() if brief_match else title
        description = " ".join(desc_match.group(1).split()) if desc_match else brief
        impl_raw = impl_match.group(1).strip() if impl_match else ""
        impl_type = IMPL_MAP.get(impl_raw, "unknown")
        difficulty = DIFF_MAP.get(diff_match.group(1).strip() if diff_match else "", "medium")

        task = ParsedTask(
            task_id=task_id,
            title=title,
            brief=brief,
            description=description,
            difficulty=difficulty,
            impl_type=impl_type,
            test_cases=parse_test_cases(section),
            concepts=parse_concepts(section),
            chapter_id=chapter_for_task(task_id, chapters),
        )
        if task_id in TEST_CASE_OVERRIDES:
            task.test_cases = TEST_CASE_OVERRIDES[task_id]

        if impl_type == "unknown":
            task.warnings.append(f"unknown impl type: {impl_raw!r}")

        if impl_type == "block_full":
            material = re.search(r"Материал задания: блоки для сборки\s*\n(.*)", section, re.S)
            if material:
                for lang_name, body in split_langs(material.group(1)).items():
                    key = LANG_MAP.get(lang_name)
                    if key:
                        task.blocks_by_lang[key] = parse_numbered_blocks(body)
            if not task.blocks_by_lang.get("pascal"):
                task.warnings.append("missing pascal blocks")
            task.is_full = bool(task.test_cases and task.concepts and task.blocks_by_lang.get("pascal"))

        elif impl_type == "placeholder":
            material = re.search(r"Материал задания: код с плейсхолдерами.*?\n(.*)", section, re.S)
            if material:
                for lang_name, body in split_langs(material.group(1)).items():
                    key = LANG_MAP.get(lang_name)
                    if not key:
                        continue
                    template_match = re.search(
                        r"Код с плейсхолдерами:\s*\n(.*?)(?=Недостающие блоки:|$)",
                        body,
                        re.S,
                    )
                    if template_match:
                        task.placeholder_by_lang[key] = template_match.group(1).strip()
                    task.placeholder_bank_by_lang[key] = parse_placeholder_bank(body)
                    task.placeholder_fills_by_lang[key] = parse_placeholder_correct_fills(body)
            template_lang = pick_language(task.placeholder_by_lang, require_placeholder=True)
            bank_lang = template_lang or pick_language(
                {k: v for k, v in task.placeholder_bank_by_lang.items() if v}
            )
            if not template_lang:
                task.warnings.append("no placeholder template with ___")
            if not bank_lang or not task.placeholder_bank_by_lang.get(bank_lang or "", []):
                task.warnings.append("missing placeholder bank")
            task.is_full = bool(
                task.test_cases
                and task.concepts
                and template_lang
                and bank_lang
                and task.placeholder_bank_by_lang.get(bank_lang, [])
            )

        elif impl_type == "translation":
            material = re.search(r"Материал задания: перевод кода\s*\n(.*)", section, re.S)
            if material:
                body = material.group(1)
                if "Pascal:" in body:
                    lang_section = body[body.index("Pascal:") :]
                else:
                    lang_section = body.split("Для интерфейса")[-1]
                for lang_name, lang_body in split_langs(lang_section).items():
                    key = LANG_MAP.get(lang_name)
                    if key:
                        task.code_by_lang[key] = parse_plain_code(lang_body)
            if len(task.code_by_lang) < 3:
                task.warnings.append(f"only {len(task.code_by_lang)} reference codes")
            task.is_full = bool(task.test_cases and task.concepts and len(task.code_by_lang) >= 3)

        elif impl_type == "debug":
            material = re.search(r"Материал задания: исправление ошибок\s*\n(.*)", section, re.S)
            if material:
                for lang_name, body in split_langs(material.group(1)).items():
                    key = LANG_MAP.get(lang_name)
                    if not key:
                        continue
                    buggy = parse_code_section(body, "Код с ошибками")
                    correct = parse_code_section(body, "Правильный вариант")
                    if buggy:
                        task.buggy_by_lang[key] = buggy
                    if correct:
                        task.code_by_lang[key] = correct
            if not task.buggy_by_lang:
                task.warnings.append("missing buggy code")
            if len(task.code_by_lang) < 3:
                task.warnings.append(f"only {len(task.code_by_lang)} correct codes")
            task.is_full = bool(
                task.test_cases and task.concepts and task.buggy_by_lang and len(task.code_by_lang) >= 3
            )

        else:
            task.warnings.append("unsupported impl type")

        if not task.test_cases:
            task.warnings.append("missing test cases")
            task.test_cases = [{"inputs": "\n", "output": "0"}]
        if not task.concepts:
            task.warnings.append("missing concepts")
            task.concepts = {"python": ["program_entry"]}

        tasks.append(task)

    return tasks


def py_repr(value: Any, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, list):
        if not value:
            return "[]"
        if all(isinstance(item, dict) for item in value):
            parts = ["["]
            for item in value:
                parts.append(f"{pad}    {py_repr(item, indent + 4)},")
            parts.append(f"{pad}]")
            return "\n".join(parts)
        inner = ", ".join(py_repr(item) for item in value)
        return f"[{inner}]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        parts = ["{"]
        for key, item in value.items():
            parts.append(f"{pad}    {repr(key)}: {py_repr(item, indent + 4)},")
        parts.append(f"{pad}}}")
        return "\n".join(parts)
    return repr(value)


def render_task(task: ParsedTask) -> str:
    topics = [f"tc42_{task.chapter_id}"]
    constructions = task.concepts.get("python") or next(iter(task.concepts.values()), ["program_entry"])
    code_examples = {lang: maybe_normalize_code(lang, text) for lang, text in task.code_by_lang.items()}

    if task.impl_type == "block_full":
        pascal_blocks = task.blocks_by_lang.get("pascal") or ["program Main;", "begin", "end."]
        if not code_examples:
            code_examples = {
                lang: maybe_normalize_code(lang, blocks_to_code(blocks))
                for lang, blocks in task.blocks_by_lang.items()
                if blocks
            }
        else:
            code_examples = {
                lang: maybe_normalize_code(lang, text) for lang, text in code_examples.items()
            }
        expected = expected_from_pascal_blocks(pascal_blocks)
        order = list(range(len(pascal_blocks)))
        return (
            f"        block_task(\n"
            f"            {task.task_id},\n"
            f"            {py_repr(task.title)},\n"
            f"            {py_repr(task.description)},\n"
            f"            {py_repr(task.difficulty)},\n"
            f"            topics={py_repr(topics)},\n"
            f"            constructions={py_repr(constructions)},\n"
            f"            code_examples={py_repr(code_examples)},\n"
            f"            pascal_blocks={py_repr(pascal_blocks)},\n"
            f"            correct_order={py_repr(order)},\n"
            f"            expected_pascal={py_repr(expected)},\n"
            f"            test_cases={py_repr(task.test_cases)},\n"
            f"        )"
        )

    if task.impl_type == "placeholder":
        override = TASK_PLACEHOLDER_OVERRIDES.get(task.task_id, {})
        template_lang = pick_language(task.placeholder_by_lang, require_placeholder=True) or "python"
        if override.get("language"):
            template_lang = str(override["language"])
        template = maybe_normalize_code(
            template_lang,
            override.get("placeholder_template")
            or task.placeholder_by_lang.get(template_lang)
            or "print(___)",
        )
        bank = override.get("placeholder_bank") or task.placeholder_bank_by_lang.get(template_lang) or task.placeholder_bank_by_lang.get("pascal") or ["___"]
        fills = task.placeholder_fills_by_lang.get(template_lang) or []
        code_examples = dict(override.get("code_examples") or task.code_by_lang)
        for lang, lang_template in task.placeholder_by_lang.items():
            if override.get("code_examples"):
                continue
            lang_fills = task.placeholder_fills_by_lang.get(lang) or []
            reference = task.code_by_lang.get(lang) or assemble_placeholder_reference(lang_template, lang_fills)
            if reference.strip():
                code_examples[lang] = maybe_normalize_code(lang, reference)
        reference = code_examples.get(template_lang) or assemble_placeholder_reference(template, fills)
        if reference.strip():
            code_examples[template_lang] = maybe_normalize_code(template_lang, reference)
        elif not code_examples:
            code_examples = {"python": "# placeholder task"}
        test_cases = override.get("test_cases") or task.test_cases
        payload = {
            "language": template_lang,
            "target_language": override.get("target_language", template_lang),
            "source_language": override.get("source_language", "python"),
            "placeholder_template": template,
            "placeholder_bank": bank,
            "test_cases": test_cases,
            "constructions": task.concepts.get(template_lang) or constructions,
            "code_examples": code_examples,
            "topics": topics,
        }
        return (
            f"        row(\n"
            f"            {task.task_id},\n"
            f"            {py_repr(task.title)},\n"
            f"            {py_repr(task.description)},\n"
            f"            {py_repr(task.difficulty)},\n"
            f"            \"task_fill_placeholders\",\n"
            f"            {py_repr(payload)},\n"
            f"        )"
        )

    if task.impl_type == "translation":
        if not code_examples:
            code_examples = {"python": "pass"}
        return (
            f"        translate_task(\n"
            f"            {task.task_id},\n"
            f"            {py_repr(task.title)},\n"
            f"            {py_repr(task.description)},\n"
            f"            {py_repr(task.difficulty)},\n"
            f"            topics={py_repr(topics)},\n"
            f"            constructions={py_repr(constructions)},\n"
            f"            code_examples={py_repr(code_examples)},\n"
            f"            test_cases={py_repr(task.test_cases)},\n"
            f"        )"
        )

    if task.impl_type == "debug":
        template_lang = pick_language(task.buggy_by_lang) or "pascal"
        template = maybe_normalize_code(
            template_lang,
            task.buggy_by_lang.get(template_lang) or task.buggy_by_lang.get("pascal") or "(* fix me *)",
        )
        if not code_examples:
            code_examples = {"python": "pass"}
        return (
            f"        translate_task(\n"
            f"            {task.task_id},\n"
            f"            {py_repr(task.title)},\n"
            f"            {py_repr(task.description)},\n"
            f"            {py_repr(task.difficulty)},\n"
            f"            topics={py_repr(topics)},\n"
            f"            constructions={py_repr(constructions)},\n"
            f"            code_examples={py_repr(code_examples)},\n"
            f"            test_cases={py_repr(task.test_cases)},\n"
            f"            template={py_repr(template)},\n"
            f"        )"
        )

    payload = {
        "topics": topics,
        "test_cases": task.test_cases,
        "constructions": constructions,
    }
    return (
        f"        row(\n"
        f"            {task.task_id},\n"
        f"            {py_repr(task.title)},\n"
        f"            {py_repr(task.description)},\n"
        f"            {py_repr(task.difficulty)},\n"
        f"            \"translation\",\n"
        f"            {py_repr(payload)},\n"
        f"        )"
    )


def render_module(tasks: list[ParsedTask], chapters: dict[int, tuple[str, str]]) -> str:
    chapter_plans = {
        chapters[num][0]: list(range((num - 1) * 8 + 1, num * 8 + 1))
        for num in sorted(chapters)
    }
    task_calls = ",\n".join(render_task(task) for task in tasks)
    return (
        '"""Auto-generated TC42 course catalog from PDF."""\n'
        "from __future__ import annotations\n\n"
        "from migrations.seeds.catalog_common import block_task, row, translate_task\n\n"
        "TaskRow = dict\n\n"
        f"TC42_CATALOG_SIZE = {len(tasks)}\n\n"
        f"CHAPTER_PLANS: dict[str, list[int]] = {py_repr(chapter_plans)}\n\n\n"
        "def build_tc42_course_catalog() -> list[TaskRow]:\n"
        "    return [\n"
        f"{task_calls},\n"
        "    ]\n"
    )


def validate_generated_module(module_path: Path) -> list[TaskRow]:
    import importlib.util

    spec = importlib.util.spec_from_file_location("tc42_course_catalog_generated", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import generated module at {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(module_path.parents[2]))
    spec.loader.exec_module(module)
    catalog = module.build_tc42_course_catalog()
    return catalog


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")

    if not args.pdf.exists():
        logger.error("PDF not found: %s", args.pdf)
        return 1

    text = extract_pdf_text(args.pdf)
    tasks = parse_tasks(text)
    chapters = parse_chapters(text)

    if len(tasks) != 128:
        logger.warning("expected 128 tasks, parsed %s", len(tasks))

    module_source = render_module(tasks, chapters)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(module_source, encoding="utf-8")
    logger.info("Wrote %s", args.output)

    catalog = validate_generated_module(args.output)
    if len(catalog) != 128:
        logger.error("generated catalog has %s tasks, expected 128", len(catalog))
        return 1

    full = sum(1 for task in tasks if task.is_full)
    stub = len(tasks) - full
    by_type: dict[str, dict[str, int]] = {}
    for task in tasks:
        bucket = by_type.setdefault(task.impl_type, {"full": 0, "stub": 0})
        bucket["full" if task.is_full else "stub"] += 1

    print("\n=== TC42 catalog generation summary ===")
    print(f"PDF: {args.pdf}")
    print(f"Output: {args.output}")
    print(f"Tasks parsed: {len(tasks)}")
    print(f"Catalog rows: {len(catalog)}")
    print(f"Full data: {full}")
    print(f"Stubs/minimal: {stub}")
    print("By impl type:")
    for impl_type, counts in sorted(by_type.items()):
        print(f"  {impl_type}: full={counts['full']}, stub={counts['stub']}")

    warned = [task for task in tasks if task.warnings]
    if warned:
        print(f"\nParsing warnings ({len(warned)} tasks):")
        for task in warned[:30]:
            print(f"  task {task.task_id}: {', '.join(task.warnings)}")
        if len(warned) > 30:
            print(f"  ... and {len(warned) - 30} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
