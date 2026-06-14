from __future__ import annotations

TASK2_BLOCK_REORDER_OK: dict = {
    "task_id": 2,
    "language": "python",
    "code": "print('b')\nprint('a')",
    "block_order": [1, 0],
}

TASK1_HELLO_PYTHON: dict = {
    "task_id": 1,
    "language": "python",
    "code": "print('Hello')\n",
}

CPP_FOR_LOOP = (
    "#include <iostream>\n"
    "int main() {\n"
    "  for (int i = 0; i < 3; ++i) std::cout << i << '\\n';\n"
    "  return 0;\n"
    "}\n"
)

PASCAL_FOR_LOOP = "program T;\n" "var i: integer;\n" "begin\n" "  for i := 1 to 3 do\n" "    writeln(i);\n" "end.\n"
