from __future__ import annotations

from typing import Any

from src.features.catalog.domain.dto import TaskDetailDTO, TaskSummaryDTO
from src.features.catalog.models import TaskModel
from src.features.tasks.domain.block_reorder_language import (
    BLOCK_REORDER_LANGUAGES,
    block_reorder_statements,
    synthesize_blocks_by_language,
)
from src.features.tasks.domain.enums import (
    TaskFamily,
    is_write_from_description_task,
    task_family_from_legacy_type,
)
from src.features.tasks.domain.flowchart_reference_code import synthesize_flowchart_source_by_language


def _format_block_items(raw: list[Any]) -> list[dict[str, Any]]:
    return [{"id": index, "content": content} for index, content in enumerate(raw)]


def _public_test_cases(payload: dict[str, Any]) -> list[dict[str, str]]:
    raw = payload.get("test_cases")
    if not isinstance(raw, list):
        return []
    cases: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        cases.append(
            {
                "inputs": str(item.get("inputs", item.get("input", ""))),
                "output": str(item.get("output", item.get("expected_output", item.get("expected", "")))),
            }
        )
    return cases


def _public_constructions(payload: dict[str, Any]) -> list[str]:
    raw = payload.get("constructions")
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if item]


def _code_examples_from_blocks(blocks_by_language: dict[str, list[dict[str, Any]]]) -> dict[str, str]:
    examples: dict[str, str] = {}
    for language_id, blocks in blocks_by_language.items():
        if not blocks:
            continue
        lines = [str(block.get("content", "")) for block in blocks if str(block.get("content", "")).strip()]
        if lines:
            examples[str(language_id)] = "\n".join(lines)
    return examples


def _attach_student_metadata(public: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    test_cases = _public_test_cases(payload)
    if test_cases:
        public["test_cases"] = test_cases
    constructions = _public_constructions(payload)
    if constructions:
        public["constructions"] = constructions
    hints = payload.get("construction_hints")
    if isinstance(hints, dict) and hints:
        public["construction_hints"] = hints
    return public


def _public_block_reorder_payload(payload: dict[str, Any]) -> dict[str, Any]:
    default_language = str(payload.get("language") or "python")
    variants = payload.get("blocks_by_language")
    blocks_by_language: dict[str, list[dict[str, Any]]] = {}

    if isinstance(variants, dict):
        for language_id, lines in variants.items():
            if isinstance(lines, list):
                blocks_by_language[str(language_id)] = _format_block_items(lines)

    if not blocks_by_language:
        blocks = payload.get("blocks") or []
        if isinstance(blocks, list) and blocks:
            blocks_by_language[default_language] = _format_block_items(blocks)

    default_blocks = blocks_by_language.get(default_language) or next(iter(blocks_by_language.values()), [])
    source_statements = [str(block["content"]) for block in default_blocks]
    if source_statements:
        for language_id, lines in synthesize_blocks_by_language(source_statements).items():
            if language_id not in blocks_by_language:
                blocks_by_language[language_id] = _format_block_items(lines)

    existing_examples = payload.get("code_examples")
    if isinstance(existing_examples, dict) and existing_examples:
        for language_id in BLOCK_REORDER_LANGUAGES:
            statements = block_reorder_statements(payload, language_id)
            if statements:
                blocks_by_language[language_id] = _format_block_items(statements)

    default_blocks = blocks_by_language.get(default_language) or default_blocks

    public = {
        "blocks": default_blocks,
        "blocks_by_language": blocks_by_language,
        "blocks_count": len(default_blocks),
        "language": default_language,
    }
    template = payload.get("template")
    if isinstance(template, str) and template.strip():
        public["template"] = template
    language_variants = payload.get("language_variants")
    if isinstance(language_variants, dict) and language_variants:
        public["language_variants"] = language_variants
    existing_examples = payload.get("code_examples")
    if isinstance(existing_examples, dict) and existing_examples:
        public["code_examples"] = {
            str(key): str(value) for key, value in existing_examples.items() if str(value).strip()
        }
    else:
        code_examples = _code_examples_from_blocks(blocks_by_language)
        if code_examples:
            public["code_examples"] = code_examples
    if payload.get("source_language"):
        public["source_language"] = str(payload["source_language"])
    elif public.get("code_examples"):
        public["source_language"] = "python"
    return _attach_student_metadata(public, payload)


def _public_flowchart_payload(payload: dict[str, Any]) -> dict[str, Any]:
    public: dict[str, Any] = {
        key: value
        for key, value in payload.items()
        if not key.startswith("_")
        and key
        not in {
            "test_cases",
            "constructions",
            "construction_hints",
            "flow_spec",
        }
    }
    if payload.get("flowchart_mode"):
        public["flowchart_mode"] = payload.get("flowchart_mode")
    source_code = payload.get("source_code")
    if isinstance(source_code, str) and source_code.strip():
        variants = payload.get("source_code_by_language")
        if not isinstance(variants, dict) or not variants:
            public["source_code_by_language"] = synthesize_flowchart_source_by_language(source_code)
        elif "source_code_by_language" not in public:
            public["source_code_by_language"] = variants
        public["source_language"] = payload.get("source_language") or "python"
        public["source_code"] = source_code
    return _attach_student_metadata(public, payload)


def _public_translation_payload(payload: dict[str, Any]) -> dict[str, Any]:
    public: dict[str, Any] = {
        "source_language": payload.get("source_language"),
        "target_language": payload.get("target_language"),
        "source_code": payload.get("source_code"),
        "template": payload.get("template"),
    }
    kind = payload.get("kind")
    if isinstance(kind, str) and kind.strip().lower() == "debug":
        public["kind"] = "debug"
    source_code = payload.get("source_code")
    source_language = str(payload.get("source_language") or "python").strip().lower()

    code_examples: dict[str, str] = {}
    seed_examples = payload.get("code_examples")
    if isinstance(seed_examples, dict) and seed_examples:
        code_examples = {
            str(key).strip().lower(): str(value)
            for key, value in seed_examples.items()
            if str(value or "").strip()
        }
    if isinstance(source_code, str) and source_code.strip():
        code_examples.setdefault(source_language, source_code)
    if code_examples:
        public["code_examples"] = code_examples

    return _attach_student_metadata(public, payload)


def _public_write_from_description_payload(payload: dict[str, Any]) -> dict[str, Any]:
    public: dict[str, Any] = {
        "target_language": payload.get("target_language"),
    }
    template = payload.get("template")
    if isinstance(template, str) and template.strip():
        public["template"] = template
    problem_statement = payload.get("problem_statement")
    if isinstance(problem_statement, str) and problem_statement.strip():
        public["problem_statement"] = problem_statement
    return _attach_student_metadata(public, payload)


def _public_placeholder_payload(payload: dict[str, Any]) -> dict[str, Any]:
    public: dict[str, Any] = {
        "language": payload.get("language") or "python",
        "target_language": payload.get("target_language") or "python",
        "placeholder_template": payload.get("placeholder_template"),
        "placeholder_bank": payload.get("placeholder_bank"),
    }
    code_examples = payload.get("code_examples")
    if isinstance(code_examples, dict) and code_examples:
        public["code_examples"] = code_examples
        public["source_language"] = payload.get("source_language") or "python"
    return _attach_student_metadata(public, payload)


def _public_payload(task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    if task_type == "task_fill_placeholders":
        return _public_placeholder_payload(payload)
    family = task_family_from_legacy_type(task_type)
    if family is TaskFamily.BLOCK_REORDER:
        return _public_block_reorder_payload(payload)
    if is_write_from_description_task(task_type):
        return _public_write_from_description_payload(payload)
    if family is TaskFamily.TRANSLATION:
        return _public_translation_payload(payload)
    if family is TaskFamily.FLOWCHART:
        return _public_flowchart_payload(payload)
    return {key: value for key, value in payload.items() if not key.startswith("_")}


def _task_topics(payload: dict[str, Any]) -> tuple[str, ...]:
    raw = payload.get("topics")
    if not isinstance(raw, list):
        return ()
    return tuple(str(item) for item in raw if item)


def _summary_languages(payload: dict[str, Any]) -> tuple[str, ...]:
    languages: set[str] = set()
    for key in ("source_language", "target_language", "language"):
        raw = payload.get(key)
        if raw:
            languages.add(str(raw).strip().lower())
    blocks_by_language = payload.get("blocks_by_language")
    if isinstance(blocks_by_language, dict):
        languages.update(str(key).strip().lower() for key in blocks_by_language if key)
    code_examples = payload.get("code_examples")
    if isinstance(code_examples, dict):
        languages.update(str(key).strip().lower() for key in code_examples if key)
    return tuple(sorted(languages))


def to_summary(model: TaskModel) -> TaskSummaryDTO:
    payload = dict(model.payload or {})
    return TaskSummaryDTO(
        id=model.id,
        title=model.title,
        description=model.description,
        difficulty=model.difficulty,
        task_type=model.task_type,
        topics=_task_topics(payload),
        languages=_summary_languages(payload),
    )


def to_detail(model: TaskModel) -> TaskDetailDTO:
    return TaskDetailDTO(
        id=model.id,
        title=model.title,
        description=model.description,
        difficulty=model.difficulty,
        task_type=model.task_type,
        payload=_public_payload(model.task_type, dict(model.payload or {})),
    )


def to_internal_detail(model: TaskModel) -> TaskDetailDTO:
    """Full payload for execution — includes answers hidden from public API."""
    return TaskDetailDTO(
        id=model.id,
        title=model.title,
        description=model.description,
        difficulty=model.difficulty,
        task_type=model.task_type,
        payload=dict(model.payload or {}),
    )
