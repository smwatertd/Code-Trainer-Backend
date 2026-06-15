"""Fix task 12 date-validation test cases in TC42 catalog."""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "j8k9l0m1_fix_task12_test_cases"
down_revision: Union[str, Sequence[str], None] = "i7j8k9l0_tc42_128_catalog"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TASK12_TEST_CASES = [
    {"inputs": "15 6\n", "output": "valid"},
    {"inputs": "32 6\n", "output": "invalid"},
    {"inputs": "15 13\n", "output": "invalid"},
]

_TASK9_TEST_CASES = [
    {"inputs": "3 7 2\n", "output": "7"},
    {"inputs": "10 5 8\n", "output": "10"},
    {"inputs": "1 1 1\n", "output": "1"},
]

_TASK11_TEST_CASES = [
    {"inputs": "3 4 5\n", "output": "scalene"},
    {"inputs": "5 5 5\n", "output": "equilateral"},
    {"inputs": "3 3 4\n", "output": "isosceles"},
]


def _patch_task_test_cases(connection, schema: str, task_id: int, test_cases: list[dict[str, str]]) -> None:
    row = connection.execute(
        sa.text(f'SELECT payload FROM "{schema}"."tasks" WHERE id = :task_id'),
        {"task_id": task_id},
    ).fetchone()
    if row is None:
        return
    payload = dict(row[0])
    payload["test_cases"] = test_cases
    connection.execute(
        sa.text(f'UPDATE "{schema}"."tasks" SET payload = :payload WHERE id = :task_id'),
        {"payload": json.dumps(payload), "task_id": task_id},
    )


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()
    _patch_task_test_cases(connection, schema, 9, _TASK9_TEST_CASES)
    _patch_task_test_cases(connection, schema, 11, _TASK11_TEST_CASES)
    _patch_task_test_cases(connection, schema, 12, _TASK12_TEST_CASES)


def downgrade() -> None:
    pass
