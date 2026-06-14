"""Curriculum links for the 12-task basic program (ids 1–10 used in e2e)."""

from __future__ import annotations

BASIC_PROGRAM_CURRICULUM_LINKS: list[dict] = [
    {
        "task_id": 1,
        "language": "python",
        "learning_concept_id": "loops",
        "technical_concept_id": "for_loop",
        "exercise_pattern_id": "tr_pattern_translation",
        "action": "assemble",
        "is_primary": True,
    },
    {
        "task_id": 3,
        "language": "python",
        "learning_concept_id": "loops",
        "technical_concept_id": "for_loop",
        "exercise_pattern_id": "tr_python_snippet",
        "action": "translate",
        "is_primary": True,
    },
    {
        "task_id": 7,
        "language": "python",
        "learning_concept_id": "loops",
        "technical_concept_id": "while_loop",
        "exercise_pattern_id": "tr_pattern_translation",
        "action": "assemble",
        "is_primary": True,
    },
    {
        "task_id": 2,
        "language": "python",
        "learning_concept_id": "conditions",
        "technical_concept_id": "if_else",
        "exercise_pattern_id": "tr_pattern_translation",
        "action": "debug",
        "is_primary": True,
    },
    {
        "task_id": 5,
        "language": "python",
        "learning_concept_id": "conditions",
        "technical_concept_id": "if_else",
        "exercise_pattern_id": "tr_pattern_translation",
        "action": "debug",
        "is_primary": True,
    },
    {
        "task_id": 8,
        "language": "python",
        "learning_concept_id": "conditions",
        "technical_concept_id": "nested_branch",
        "exercise_pattern_id": "tr_pattern_translation",
        "action": "debug",
        "is_primary": True,
    },
    {
        "task_id": 4,
        "language": "python",
        "learning_concept_id": "functions",
        "technical_concept_id": "function_definition",
        "exercise_pattern_id": "tr_pattern_translation",
        "action": "assemble",
        "is_primary": True,
    },
    {
        "task_id": 6,
        "language": "python",
        "learning_concept_id": "functions",
        "technical_concept_id": "function_call",
        "exercise_pattern_id": "tr_python_snippet",
        "action": "translate",
        "is_primary": True,
    },
    {
        "task_id": 9,
        "language": "python",
        "learning_concept_id": "functions",
        "technical_concept_id": "return_value",
        "exercise_pattern_id": "tr_python_snippet",
        "action": "translate",
        "is_primary": True,
    },
]

CURRICULUM_LINKS_SEED: list[dict] = list(BASIC_PROGRAM_CURRICULUM_LINKS)
