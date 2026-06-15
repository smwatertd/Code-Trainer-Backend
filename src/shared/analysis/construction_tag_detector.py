"""Regex-based detection for curriculum construction tags (program_entry, stdin_read, …)."""

from __future__ import annotations

import re

CONSTRUCTION_TAG_LABELS: dict[str, str] = {
    "program_entry": "Точка входа программы",
    "typed_declaration": "Объявление переменной",
    "assignment": "Присваивание",
    "arithmetic_ops": "Арифметические операции",
    "stdout_write": "Вывод в консоль",
    "stdin_read": "Ввод с клавиатуры",
    "if_statement": "Условие",
    "simple_branch": "Ветвление",
    "for_loop": "Цикл for",
    "while_loop": "Цикл while",
    "counted_loop": "Счётный цикл",
}

_CONSTRUCTION_TAG_PATTERNS: dict[str, dict[str, tuple[re.Pattern[str], ...]]] = {
    "program_entry": {
        "python": (
            re.compile(r"\bdef\s+main\s*\(", re.I),
            re.compile(r"\bif\s+__name__\s*==", re.I),
            re.compile(r"^\s*(?:print|input|def|class|\w+\s*=)", re.M),
        ),
        "pascal": (
            re.compile(r"\bprogram\b", re.I),
            re.compile(r"\bbegin\b[\s\S]*\bend\.", re.I),
        ),
        "cpp": (re.compile(r"\bint\s+main\s*\(", re.I), re.compile(r"\bmain\s*\(", re.I)),
        "java": (re.compile(r"\bpublic\s+static\s+void\s+main\s*\(", re.I),),
        "csharp": (re.compile(r"\bstatic\s+void\s+Main\s*\(", re.I),),
    },
    "typed_declaration": {
        "python": (
            re.compile(r"\b\w+\s*:\s*\w+"),
            re.compile(r"\b\w+\s*=\s*(?:int|float|str)\("),
        ),
        "pascal": (re.compile(r"\bvar\b", re.I),),
        "cpp": (re.compile(r"\b(?:int|float|double|char|bool|long|string|auto)\s+\w+"),),
        "java": (re.compile(r"\b(?:int|float|double|char|boolean|long|String)\s+\w+"),),
        "csharp": (re.compile(r"\b(?:int|float|double|char|bool|long|string|var)\s+\w+"),),
    },
    "assignment": {
        "python": (re.compile(r"\b\w+\s*=(?!=)"),),
        "pascal": (
            re.compile(r"\b\w+\s*:="),
            re.compile(r"\breadln\s*\(", re.I),
        ),
        "cpp": (re.compile(r"\b\w+\s*=(?!=)"),),
        "java": (re.compile(r"\b\w+\s*=(?!=)"),),
        "csharp": (re.compile(r"\b\w+\s*=(?!=)"),),
    },
    "arithmetic_ops": {
        "python": (re.compile(r"[+\-*/%](?!=)"),),
        "pascal": (
            re.compile(r"[+\-*/](?!=)"),
            re.compile(r"\b(?:mod|div)\b", re.I),
        ),
        "cpp": (re.compile(r"[+\-*/%](?!=)"),),
        "java": (re.compile(r"[+\-*/%](?!=)"),),
        "csharp": (re.compile(r"[+\-*/%](?!=)"),),
    },
    "stdout_write": {
        "python": (re.compile(r"\bprint\s*\(", re.I),),
        "pascal": (re.compile(r"\bwriteln\b", re.I), re.compile(r"\bwrite\b", re.I)),
        "cpp": (re.compile(r"\bcout\b"), re.compile(r"\bprintf\s*\(", re.I)),
        "java": (re.compile(r"\bSystem\.out\.(?:print|println)\b"),),
        "csharp": (re.compile(r"\bConsole\.(?:Write|WriteLine)\b"),),
    },
    "stdin_read": {
        "python": (re.compile(r"\binput\s*\(", re.I),),
        "pascal": (re.compile(r"\breadln\b", re.I), re.compile(r"\bread\b", re.I)),
        "cpp": (re.compile(r"\bcin\s*>>"),),
        "java": (re.compile(r"\bnext(?:Int|Line|Double)?\s*\(", re.I), re.compile(r"\bScanner\b"),),
        "csharp": (re.compile(r"\bConsole\.ReadLine\s*\(", re.I),),
    },
    "counted_loop": {
        "python": (re.compile(r"\bfor\s+\w+\s+in\s+range\s*\(", re.I),),
        "pascal": (
            re.compile(r"\bfor\s+\w+\s*:=\s*\d+\s+to\b", re.I),
            re.compile(r"\bfor\s+\w+\s*:=\s*\w+\s+downto\b", re.I),
        ),
        "cpp": (re.compile(r"\bfor\s*\(\s*int\s+\w+\s*=\s*\d+", re.I),),
        "java": (re.compile(r"\bfor\s*\(\s*int\s+\w+\s*=\s*\d+", re.I),),
        "csharp": (re.compile(r"\bfor\s*\(\s*int\s+\w+\s*=\s*\d+", re.I),),
    },
}

_TAGGED_CONSTRUCTIONS = frozenset(_CONSTRUCTION_TAG_PATTERNS)


def is_tagged_construction(tag: str) -> bool:
    return str(tag or "").strip().lower() in _TAGGED_CONSTRUCTIONS


def construction_tag_label(tag: str) -> str:
    normalized = str(tag or "").strip().lower()
    return CONSTRUCTION_TAG_LABELS.get(normalized, normalized or tag)


def detect_construction_tags(code: str, language_id: str, tags: list[str]) -> set[str]:
    if not code.strip() or not tags:
        return set()

    lang = str(language_id or "python").strip().lower()
    detected: set[str] = set()

    for raw in tags:
        tag = str(raw or "").strip().lower()
        patterns = _CONSTRUCTION_TAG_PATTERNS.get(tag, {}).get(lang)
        if not patterns:
            patterns = _CONSTRUCTION_TAG_PATTERNS.get(tag, {}).get("python", ())
        if any(pattern.search(code) for pattern in patterns):
            detected.add(tag)

    return detected


def missing_construction_tag_labels(code: str, language_id: str, tags: list[str]) -> list[str]:
    required = [str(item).strip().lower() for item in tags if is_tagged_construction(str(item))]
    if not required:
        return []

    detected = detect_construction_tags(code, language_id, required)
    messages: list[str] = []
    for tag in required:
        if tag not in detected:
            messages.append(f"Отсутствует конструкция: {construction_tag_label(tag)}")
    return messages
