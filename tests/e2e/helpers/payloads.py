from __future__ import annotations

TASK1_HELLO_BLOCKS: dict = {
    "task_id": 1,
    "language": "pascal",
    "code": "program Main;\nbegin\n  writeln('Hello');\nend.",
    "block_order": [0, 1, 2, 3],
}

TASK4_AREA_BLOCKS: dict = {
    "task_id": 4,
    "language": "pascal",
    "code": (
        "program Main;\nvar w,h,area: integer;\n"
        "begin\n  readln(w,h);\n  area:=w*h;\n  writeln(area);\nend."
    ),
    "block_order": [0, 1, 2, 3, 4, 5, 6],
}

TASK10_MINUTES_BLOCKS: dict = {
    "task_id": 10,
    "language": "pascal",
    "code": (
        "program Main;\nvar total,h,m: integer;\n"
        "begin\n  readln(total);\n  h:=total div 60;\n  m:=total mod 60;\n  writeln(h,' ',m);\nend."
    ),
    "block_order": [0, 1, 2, 3, 4, 5, 6, 7],
}

TASK3_SUM_PASCAL: dict = {
    "task_id": 3,
    "language": "pascal",
    "code": "var a,b,s: integer;\nbegin\n  readln(a,b);\n  s:=a+b;\n  writeln(s);\nend.",
}

TASK2_AGE_PASCAL: dict = {
    "task_id": 2,
    "language": "pascal",
    "code": "var age: integer;\nbegin\n  readln(age);\n  writeln(age);\nend.",
}

TASK2_AGE_BROKEN: dict = {
    "task_id": 2,
    "language": "pascal",
    "code": "var age: integer;\nbegin\n  age := 18;\n  writeln(age);\nend.",
}

TASK5_PERIMETER_OK: dict = {
    "task_id": 5,
    "language": "pascal",
    "code": "var w,h,p: integer;\nbegin\n  readln(w,h);\n  p:=2*(w+h);\n  writeln(p);\nend.",
}

TASK5_PERIMETER_BROKEN: dict = {
    "task_id": 5,
    "language": "pascal",
    "code": "var w,h,p: integer;\nbegin\n  readln(w,h);\n  p:=w*h;\n  writeln(p);\nend.",
}

TASK8_LAST_DIGIT_OK: dict = {
    "task_id": 8,
    "language": "pascal",
    "code": "var x,last: integer;\nbegin\n  readln(x);\n  last:=x mod 10;\n  writeln(last);\nend.",
}

TASK8_LAST_DIGIT_BROKEN: dict = {
    "task_id": 8,
    "language": "pascal",
    "code": "var x,last: integer;\nbegin\n  readln(x);\n  last:=x div 10;\n  writeln(last);\nend.",
}

TASK9_DIGIT_SUM_PASCAL: dict = {
    "task_id": 9,
    "language": "pascal",
    "code": "var x,s: integer;\nbegin\n  readln(x);\n  s:=x div 10 + x mod 10;\n  writeln(s);\nend.",
}

PASCAL_RECEIPT = (
    "var price,tax,discount,total: real;\n"
    "begin\n"
    "  readln(price,tax,discount);\n"
    "  total:=price*(1+tax/100)*(1-discount/100);\n"
    "  writeln(total:0:2);\n"
    "end."
)

TASK12_RECEIPT_PASCAL: dict = {
    "task_id": 12,
    "language": "pascal",
    "code": PASCAL_RECEIPT,
}

# Stable payloads for rate-limit / dedup / security smoke tests.
DEMO_CHECK_PAYLOAD = TASK1_HELLO_BLOCKS
