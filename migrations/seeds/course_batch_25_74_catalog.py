"""Разделы «Простое ветвление», «Множественное ветвление», «Циклы», «Вложенные циклы» — задачи 25–74."""
from __future__ import annotations

from migrations.seeds.catalog_common import (
    block_task,
    pascal_blocks_from_body,
    row,
    tc,
    translate_task,
    wrap_pascal,
)

TaskRow = dict

_SIMPLE_BRANCH_TOPICS = ["branching", "simple_branch"]
_SIMPLE_BRANCH_CONSTRUCTIONS = [
    "typed_declaration",
    "stdin_read",
    "simple_branch",
    "conditional_expression",
    "assignment",
    "stdout_write",
]

_MULTI_BRANCH_TOPICS = ["branching", "multi_branch"]
_MULTI_BRANCH_CONSTRUCTIONS = [
    "typed_declaration",
    "stdin_read",
    "multi_branch",
    "switch_selection",
    "simple_branch",
    "assignment",
    "stdout_write",
]

_LOOPS_TOPICS = ["loops", "counted_loop"]
_LOOPS_CONSTRUCTIONS = [
    "typed_declaration",
    "stdin_read",
    "counted_loop",
    "pre_condition_loop",
    "post_condition_loop",
    "assignment",
    "stdout_write",
]

_NESTED_LOOPS_TOPICS = ["loops", "nested_iteration"]
_NESTED_LOOPS_CONSTRUCTIONS = [
    "nested_iteration",
    "loop_control",
    "counted_loop",
    "stdin_read",
    "assignment",
    "stdout_write",
]


def _stub(py: str, pascal: str) -> dict[str, str]:
    return {
        "python": py,
        "pascal": pascal,
        "cpp": "/* stub */",
        "csharp": "// stub",
        "java": "// stub",
    }


def _block_from_body(
    task_id: int,
    title: str,
    description: str,
    difficulty: str,
    body: str,
    *,
    topics: list[str],
    constructions: list[str],
    examples: dict[str, str],
    test_cases: list[dict[str, str]],
) -> TaskRow:
    blocks, expected = pascal_blocks_from_body(body)
    return block_task(
        task_id,
        title,
        description,
        difficulty,
        topics=topics,
        constructions=constructions,
        code_examples=examples,
        pascal_blocks=blocks,
        correct_order=list(range(len(blocks))),
        expected_pascal=expected,
        test_cases=test_cases,
    )


# --- code examples (python + pascal) ---

_EX_SIGN = _stub(
    "x = int(input())\nif x > 0:\n    print('yes')\nelse:\n    print('no')",
    "var x: integer;\nbegin\n  readln(x);\n  if x>0 then writeln('yes') else writeln('no');\nend.",
)

_EX_EVEN = _stub(
    "x = int(input())\nif x % 2 == 0:\n    print('even')\nelse:\n    print('odd')",
    "var x: integer;\nbegin\n  readln(x);\n  if x mod 2=0 then writeln('even') else writeln('odd');\nend.",
)

_EX_MAX = _stub(
    "a, b = map(int, input().split())\nif a > b:\n    print(a)\nelse:\n    print(b)",
    "var a,b: integer;\nbegin\n  readln(a,b);\n  if a>b then writeln(a) else writeln(b);\nend.",
)

_EX_ABS = _stub(
    "x = int(input())\nif x < 0:\n    print(-x)\nelse:\n    print(x)",
    "var x: integer;\nbegin\n  readln(x);\n  if x<0 then writeln(-x) else writeln(x);\nend.",
)

_EX_RANGE = _stub(
    "x = int(input())\nif 10 <= x <= 20:\n    print('yes')\nelse:\n    print('no')",
    "var x: integer;\nbegin\n  readln(x);\n  if (x>=10) and (x<=20) then writeln('yes') else writeln('no');\nend.",
)

_EX_AGE18 = _stub(
    "age = int(input())\nif age >= 18:\n    print('allow')\nelse:\n    print('deny')",
    "var age: integer;\nbegin\n  readln(age);\n  if age>=18 then writeln('allow') else writeln('deny');\nend.",
)

_EX_PASSWORD = _stub(
    "password = input()\nif password == 'qwerty':\n    print('ok')\nelse:\n    print('fail')",
    "var password: string;\nbegin\n  readln(password);\n  if password='qwerty' then writeln('ok') else writeln('fail');\nend.",
)

_EX_DISCOUNT = _stub(
    "total = float(input())\nif total > 1000:\n    total *= 0.9\nprint(f'{total:.2f}')",
    "var total: real;\nbegin\n  readln(total);\n  if total>1000 then total:=total*0.9;\n  writeln(total:0:2);\nend.",
)

_EX_SAFE_DIV = _stub(
    "a, b = map(int, input().split())\nif b == 0:\n    print('error')\nelse:\n    print(a // b)",
    "var a,b: integer;\nbegin\n  readln(a,b);\n  if b=0 then writeln('error') else writeln(a div b);\nend.",
)

_EX_STATUS = _stub(
    "x = int(input())\nif x > 0:\n    print('active')\nelse:\n    print('blocked')",
    "var x: integer;\nbegin\n  readln(x);\n  if x>0 then writeln('active') else writeln('blocked');\nend.",
)

_EX_GRADE = _stub(
    "g = int(input())\nif 1 <= g <= 5:\n    print('valid')\nelse:\n    print('invalid')",
    "var g: integer;\nbegin\n  readln(g);\n  if (g>=1) and (g<=5) then writeln('valid') else writeln('invalid');\nend.",
)

_EX_AGE_TICKET = _stub(
    "age = int(input())\nticket = input()\nif age >= 18 and ticket == 'yes':\n    print('allow')\nelse:\n    print('deny')",
    "var age: integer; ticket: string;\nbegin\n  readln(age);\n  readln(ticket);\n  if (age>=18) and (ticket='yes') then writeln('allow') else writeln('deny');\nend.",
)

_EX_PRODUCT_SIGN = _stub(
    "a, b = map(int, input().split())\nif a == 0 or b == 0:\n    print('zero')\nelif a * b > 0:\n    print('positive')\nelse:\n    print('negative')",
    "var a,b: integer;\nbegin\n  readln(a,b);\n  if (a=0) or (b=0) then writeln('zero')\n  else if a*b>0 then writeln('positive') else writeln('negative');\nend.",
)

_EX_EXAM_ADMIT = _stub(
    "theory, practice, absent = map(int, input().split())\n"
    "if theory >= 70 and practice > 60 and absent == 0:\n"
    "    print('admit')\nelse:\n    print('deny')",
    "var theory,practice,absent: integer;\nbegin\n"
    "  readln(theory,practice,absent);\n"
    "  if (theory>=70) and (practice>60) and (absent=0) then writeln('admit') else writeln('deny');\nend.",
)

_EX_SCORE_GRADE = _stub(
    "score = int(input())\n"
    "if score >= 90:\n    print(5)\n"
    "elif score >= 75:\n    print(4)\n"
    "elif score >= 55:\n    print(3)\n"
    "elif score >= 30:\n    print(2)\n"
    "else:\n    print(1)",
    "var score: integer;\nbegin\n  readln(score);\n"
    "  if score>=90 then writeln(5)\n"
    "  else if score>=75 then writeln(4)\n"
    "  else if score>=55 then writeln(3)\n"
    "  else if score>=30 then writeln(2)\n"
    "  else writeln(1);\nend.",
)

_EX_DAY = _stub(
    "d = int(input())\n"
    "if d == 1:\n    print('Mon')\n"
    "elif d == 2:\n    print('Tue')\n"
    "elif d == 3:\n    print('Wed')\n"
    "elif d == 4:\n    print('Thu')\n"
    "elif d == 5:\n    print('Fri')\n"
    "elif d == 6:\n    print('Sat')\n"
    "else:\n    print('Sun')",
    "var d: integer;\nbegin\n  readln(d);\n"
    "  case d of\n"
    "    1: writeln('Mon');\n"
    "    2: writeln('Tue');\n"
    "    3: writeln('Wed');\n"
    "    4: writeln('Thu');\n"
    "    5: writeln('Fri');\n"
    "    6: writeln('Sat');\n"
    "    else writeln('Sun');\n"
    "  end;\nend.",
)

_EX_SEASON = _stub(
    "m = int(input())\n"
    "if m in (12, 1, 2):\n    print('winter')\n"
    "elif m in (3, 4, 5):\n    print('spring')\n"
    "elif m in (6, 7, 8):\n    print('summer')\n"
    "else:\n    print('autumn')",
    "var m: integer;\nbegin\n  readln(m);\n"
    "  if (m=12) or (m=1) or (m=2) then writeln('winter')\n"
    "  else if (m>=3) and (m<=5) then writeln('spring')\n"
    "  else if (m>=6) and (m<=8) then writeln('summer')\n"
    "  else writeln('autumn');\nend.",
)

_EX_TARIFF = _stub(
    "code = input().strip()\n"
    "if code == 'A':\n    print(100)\n"
    "elif code == 'B':\n    print(200)\n"
    "elif code == 'C':\n    print(300)\n"
    "else:\n    print(0)",
    "var code: string;\nbegin\n  readln(code);\n"
    "  if code='A' then writeln(100)\n"
    "  else if code='B' then writeln(200)\n"
    "  else if code='C' then writeln(300)\n"
    "  else writeln(0);\nend.",
)

_EX_DISCOUNT_TIER = _stub(
    "score = int(input())\n"
    "if score >= 90:\n    print(30)\n"
    "elif score >= 70:\n    print(20)\n"
    "elif score >= 50:\n    print(10)\n"
    "else:\n    print(0)",
    "var score: integer;\nbegin\n  readln(score);\n"
    "  if score>=90 then writeln(30)\n"
    "  else if score>=70 then writeln(20)\n"
    "  else if score>=50 then writeln(10)\n"
    "  else writeln(0);\nend.",
)

_EX_CALC = _stub(
    "op, a, b = map(int, input().split())\n"
    "if op == 1:\n    print(a + b)\n"
    "elif op == 2:\n    print(a - b)\n"
    "elif op == 3:\n    print(a * b)\n"
    "else:\n    print('error')",
    "var op,a,b: integer;\nbegin\n  readln(op,a,b);\n"
    "  if op=1 then writeln(a+b)\n"
    "  else if op=2 then writeln(a-b)\n"
    "  else if op=3 then writeln(a*b)\n"
    "  else writeln('error');\nend.",
)

_EX_ORDER_STATUS = _stub(
    "code = int(input())\n"
    "if code == 1:\n    print('new')\n"
    "elif code == 2:\n    print('processing')\n"
    "elif code == 3:\n    print('shipped')\n"
    "elif code == 4:\n    print('delivered')\n"
    "else:\n    print('unknown')",
    "var code: integer;\nbegin\n  readln(code);\n"
    "  if code=1 then writeln('new')\n"
    "  else if code=2 then writeln('processing')\n"
    "  else if code=3 then writeln('shipped')\n"
    "  else if code=4 then writeln('delivered')\n"
    "  else writeln('unknown');\nend.",
)

_EX_AGE_CAT = _stub(
    "age = int(input())\n"
    "if age <= 12:\n    print('child')\n"
    "elif age <= 17:\n    print('teen')\n"
    "elif age <= 64:\n    print('adult')\n"
    "else:\n    print('senior')",
    "var age: integer;\nbegin\n  readln(age);\n"
    "  if age<=12 then writeln('child')\n"
    "  else if age<=17 then writeln('teen')\n"
    "  else if age<=64 then writeln('adult')\n"
    "  else writeln('senior');\nend.",
)

_EX_RATING = _stub(
    "score = int(input())\n"
    "if score >= 90:\n    print('A')\n"
    "elif score >= 75:\n    print('B')\n"
    "elif score >= 60:\n    print('C')\n"
    "else:\n    print('D')",
    "var score: integer;\nbegin\n  readln(score);\n"
    "  if score>=90 then writeln('A')\n"
    "  else if score>=75 then writeln('B')\n"
    "  else if score>=60 then writeln('C')\n"
    "  else writeln('D');\nend.",
)

_EX_TRIANGLE = _stub(
    "a, b, c = map(int, input().split())\n"
    "if a + b <= c or a + c <= b or b + c <= a:\n    print('invalid')\n"
    "elif a == b == c:\n    print('equilateral')\n"
    "elif a == b or b == c or a == c:\n    print('isosceles')\n"
    "else:\n    print('scalene')",
    "var a,b,c: integer;\nbegin\n  readln(a,b,c);\n"
    "  if (a+b<=c) or (a+c<=b) or (b+c<=a) then writeln('invalid')\n"
    "  else if (a=b) and (b=c) then writeln('equilateral')\n"
    "  else if (a=b) or (b=c) or (a=c) then writeln('isosceles')\n"
    "  else writeln('scalene');\nend.",
)

_EX_CATEGORY = _stub(
    "code = int(input())\n"
    "if code == 1:\n    print('food')\n"
    "elif code == 2:\n    print('electronics')\n"
    "elif code == 3:\n    print('clothing')\n"
    "else:\n    print('other')",
    "var code: integer;\nbegin\n  readln(code);\n"
    "  if code=1 then writeln('food')\n"
    "  else if code=2 then writeln('electronics')\n"
    "  else if code=3 then writeln('clothing')\n"
    "  else writeln('other');\nend.",
)

_EX_ATM = _stub(
    "choice = int(input())\n"
    "if choice == 1:\n    print('balance')\n"
    "elif choice == 2:\n    print('deposit')\n"
    "elif choice == 3:\n    print('withdraw')\n"
    "elif choice == 4:\n    print('exit')\n"
    "else:\n    print('error')",
    "var choice: integer;\nbegin\n  readln(choice);\n"
    "  if choice=1 then writeln('balance')\n"
    "  else if choice=2 then writeln('deposit')\n"
    "  else if choice=3 then writeln('withdraw')\n"
    "  else if choice=4 then writeln('exit')\n"
    "  else writeln('error');\nend.",
)

_EX_PRINT_1_N = _stub(
    "n = int(input())\nprint(' '.join(str(i) for i in range(1, n + 1)))",
    "var n,i: integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do if i<n then write(i,' ') else write(i);\n  writeln;\nend.",
)

_EX_PRINT_N_1 = _stub(
    "n = int(input())\nprint(' '.join(str(i) for i in range(n, 0, -1)))",
    "var n,i: integer;\nbegin\n  readln(n);\n"
    "  for i:=n downto 1 do if i>1 then write(i,' ') else write(i);\n  writeln;\nend.",
)

_EX_SUM_1_N = _stub(
    "n = int(input())\ns = 0\nfor i in range(1, n + 1):\n    s += i\nprint(s)",
    "var n,i,s: integer;\nbegin\n  readln(n);\n  s:=0;\n"
    "  for i:=1 to n do s:=s+i;\n  writeln(s);\nend.",
)

_EX_PROD_1_N = _stub(
    "n = int(input())\np = 1\nfor i in range(1, n + 1):\n    p *= i\nprint(p)",
    "var n,i,p: integer;\nbegin\n  readln(n);\n  p:=1;\n"
    "  for i:=1 to n do p:=p*i;\n  writeln(p);\nend.",
)

_EX_COUNT_EVENS = _stub(
    "n = int(input())\nc = 0\nfor i in range(1, n + 1):\n    if i % 2 == 0:\n        c += 1\nprint(c)",
    "var n,i,c: integer;\nbegin\n  readln(n);\n  c:=0;\n"
    "  for i:=1 to n do if i mod 2=0 then c:=c+1;\n  writeln(c);\nend.",
)

_EX_MULT_TABLE = _stub(
    "n = int(input())\nif n > 0:\n    print(' '.join(str(n * i) for i in range(1, n + 1)))",
    "var n,i: integer;\nbegin\n  readln(n);\n"
    "  if n>0 then for i:=1 to n do if i<n then write(n*i,' ') else write(n*i);\n  writeln;\nend.",
)

_EX_SUM_SQUARES = _stub(
    "n = int(input())\ns = 0\nfor i in range(1, n + 1):\n    s += i * i\nprint(s)",
    "var n,i,s: integer;\nbegin\n  readln(n);\n  s:=0;\n"
    "  for i:=1 to n do s:=s+i*i;\n  writeln(s);\nend.",
)

_EX_MAX_N = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(max(nums))",
    "var n,i,maxv,x: integer;\nbegin\n  readln(n);\n  read(maxv);\n"
    "  for i:=2 to n do begin read(x); if x>maxv then maxv:=x; end;\n  writeln(maxv);\nend.",
)

_EX_MIN_N = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(min(nums))",
    "var n,i,minv,x: integer;\nbegin\n  readln(n);\n  read(minv);\n"
    "  for i:=2 to n do begin read(x); if x<minv then minv:=x; end;\n  writeln(minv);\nend.",
)

_EX_COUNT_POS = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nc = sum(1 for x in nums if x > 0)\nprint(c)",
    "var n,i,c,x: integer;\nbegin\n  readln(n);\n  c:=0;\n"
    "  for i:=1 to n do begin read(x); if x>0 then c:=c+1; end;\n  writeln(c);\nend.",
)

_EX_SUM_PRICES = _stub(
    "n = int(input())\nif n == 0:\n    print(0)\nelse:\n"
    "    prices = list(map(int, input().split()))\n    print(sum(prices))",
    "var n,i,s,price: integer;\nbegin\n  readln(n);\n  s:=0;\n"
    "  for i:=1 to n do begin read(price); s:=s+price; end;\n  writeln(s);\nend.",
)

_EX_AVG_N = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(f'{sum(nums) / n:.1f}')",
    "var n,i,s,x: integer; avg: real;\nbegin\n  readln(n);\n  s:=0;\n"
    "  for i:=1 to n do begin read(x); s:=s+x; end;\n  avg:=s/n;\n  writeln(avg:0:1);\nend.",
)

_EX_READ_UNTIL0 = _stub(
    "s = 0\nwhile True:\n    x = int(input())\n    if x == 0:\n        break\n    s += x\nprint(s)",
    "var x,s: integer;\nbegin\n  s:=0;\n"
    "  readln(x);\n  while x<>0 do begin s:=s+x; readln(x); end;\n  writeln(s);\nend.",
)

_EX_PWD_CHECK = _stub(
    "while True:\n    p = input()\n    if p == 'admin':\n        print('ok')\n        break",
    "var p: string;\nbegin\n"
    "  repeat\n    readln(p);\n  until p='admin';\n  writeln('ok');\nend.",
)

_EX_BONUS = _stub(
    "s = 0\nwhile True:\n    b = int(input())\n    if b == 0:\n        break\n    s += b\nprint(s)",
    "var b,s: integer;\nbegin\n  s:=0;\n"
    "  readln(b);\n  while b<>0 do begin s:=s+b; readln(b); end;\n  writeln(s);\nend.",
)

_EX_EXAM_COUNT = _stub(
    "n = int(input())\nc = 0\nfor _ in range(n):\n    score = int(input())\n    if score >= 60:\n        c += 1\nprint(c)",
    "var n,i,score,c: integer;\nbegin\n  readln(n);\n  c:=0;\n"
    "  for i:=1 to n do begin readln(score); if score>=60 then c:=c+1; end;\n  writeln(c);\nend.",
)

_EX_SQUARE_STARS = _stub(
    "n = int(input())\nfor i in range(n):\n    print('*' * n)",
    "var n,i,j: integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do begin for j:=1 to n do write('*'); writeln; end;\nend.",
)

_EX_RECT_STARS = _stub(
    "w, h = map(int, input().split())\nfor i in range(h):\n    print('*' * w)",
    "var w,h,i,j: integer;\nbegin\n  readln(w,h);\n"
    "  for i:=1 to h do begin for j:=1 to w do write('*'); writeln; end;\nend.",
)

_EX_RIGHT_TRI = _stub(
    "n = int(input())\nfor i in range(1, n + 1):\n    print('*' * i)",
    "var n,i,j: integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do begin for j:=1 to i do write('*'); writeln; end;\nend.",
)

_EX_FULL_MULT = _stub(
    "n = int(input())\nfor i in range(1, n + 1):\n    print(' '.join(str(i * j) for j in range(1, n + 1)))",
    "var n,i,j: integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do begin\n"
    "    for j:=1 to n do if j<n then write(i*j,' ') else write(i*j);\n"
    "    writeln;\n  end;\nend.",
)

_EX_CHESS = _stub(
    "n = int(input())\nfor i in range(n):\n    row = ''.join('#' if (i + j) % 2 == 0 else '.' for j in range(n))\n    print(row)",
    "var n,i,j: integer;\nbegin\n  readln(n);\n"
    "  for i:=0 to n-1 do begin\n"
    "    for j:=0 to n-1 do if (i+j) mod 2=0 then write('#') else write('.');\n"
    "    writeln;\n  end;\nend.",
)

_EX_COORD_GRID = _stub(
    "n = int(input())\nfor i in range(n):\n    print(' '.join(f'{i},{j}' for j in range(n)))",
    "var n,i,j: integer;\nbegin\n  readln(n);\n"
    "  for i:=0 to n-1 do begin\n"
    "    for j:=0 to n-1 do if j<n-1 then write(i,',',j,' ') else write(i,',',j);\n"
    "    writeln;\n  end;\nend.",
)

_EX_PAIR_SUM = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nt = int(input())\n"
    "for i in range(n):\n    for j in range(i + 1, n):\n"
    "        if nums[i] + nums[j] == t:\n            print(nums[i], nums[j])\n            break\n    else:\n        continue\n    break",
    "var n,i,j,t: integer; nums: array[1..100] of integer;\nbegin\n"
    "  readln(n);\n  for i:=1 to n do read(nums[i]);\n  readln(t);\n"
    "  for i:=1 to n do for j:=i+1 to n do\n"
    "    if nums[i]+nums[j]=t then writeln(nums[i],' ',nums[j]);\nend.",
)

_EX_SKIP_MULT3 = _stub(
    "n = int(input())\nprint(' '.join(str(i) for i in range(1, n + 1) if i % 3 != 0 or (i == n and n > 3)))",
    "var n,i,c: integer;\nbegin\n  readln(n);\n  c:=0;\n"
    "  for i:=1 to n do if (i mod 3<>0) or (i=n and n>3) then begin if c>0 then write(' '); write(i); c:=c+1; end;\n"
    "  writeln;\nend.",
)


def build_course_batch_25_74_catalog() -> list[TaskRow]:
  """Tasks 25-74: branching, multi-branch, loops, nested loops."""
  return [
    # --- 25-38 simple branching (block, fix, translate cycle) ---
    _block_from_body(
      25, "Проверить знак числа",
      "Прочитайте целое число. Если оно положительное — выведите yes, иначе no. Соберите программу из блоков.",
      "easy",
      "var x: integer;\nbegin\n  readln(x);\n  if x>0 then writeln('yes') else writeln('no');\nend.",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      examples=_EX_SIGN,
      test_cases=[tc("5\n", "yes"), tc("0\n", "no"), tc("-1\n", "no"), tc("100\n", "yes"), tc("-20\n", "no")],
    ),
    translate_task(
      26, "Проверить чётность числа",
      "Прочитайте целое число и выведите even или odd. Исправьте ошибки в программе на Pascal.",
      "medium",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      code_examples=_EX_EVEN,
      test_cases=[tc("4\n", "even"), tc("7\n", "odd"), tc("0\n", "even"), tc("-2\n", "even"), tc("-3\n", "odd")],
      template="var x: integer;\nbegin\n  readln(x);\n  if x mod 2=1 then writeln('even') else writeln('odd');\nend.",
    ),
    translate_task(
      27, "Найти максимум из двух чисел",
      "Прочитайте два числа и выведите большее. Переведите программу с Python на Pascal.",
      "hard",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      code_examples=_EX_MAX,
      test_cases=[tc("3 8\n", "8"), tc("9 1\n", "9"), tc("7 7\n", "7"), tc("0 10\n", "10"), tc("-1 -5\n", "-1")],
    ),
    _block_from_body(
      28, "Вычислить модуль числа",
      "Прочитайте целое число и выведите его абсолютное значение. Соберите программу из блоков.",
      "easy",
      "var x: integer;\nbegin\n  readln(x);\n  if x<0 then writeln(-x) else writeln(x);\nend.",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      examples=_EX_ABS,
      test_cases=[tc("-5\n", "5"), tc("5\n", "5"), tc("0\n", "0"), tc("-123\n", "123"), tc("42\n", "42")],
    ),
    translate_task(
      29, "Проверить число в диапазоне [10, 20]",
      "Прочитайте число и выведите yes, если оно от 10 до 20 включительно, иначе no. Исправьте ошибки.",
      "medium",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      code_examples=_EX_RANGE,
      test_cases=[tc("10\n", "yes"), tc("20\n", "yes"), tc("15\n", "yes"), tc("9\n", "no"), tc("21\n", "no")],
      template="var x: integer;\nbegin\n  readln(x);\n  if (x>10) and (x<20) then writeln('yes') else writeln('no');\nend.",
    ),
    translate_task(
      30, "Проверить возраст (>= 18)",
      "Прочитайте возраст. Если >= 18 — allow, иначе deny. Переведите программу на Pascal.",
      "hard",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      code_examples=_EX_AGE18,
      test_cases=[tc("18\n", "allow"), tc("17\n", "deny"), tc("25\n", "allow"), tc("0\n", "deny"), tc("65\n", "allow")],
    ),
    _block_from_body(
      31, "Проверить пароль qwerty",
      "Прочитайте пароль. Если он равен qwerty — ok, иначе fail. Соберите программу из блоков.",
      "easy",
      "var password: string;\nbegin\n  readln(password);\n  if password='qwerty' then writeln('ok') else writeln('fail');\nend.",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      examples=_EX_PASSWORD,
      test_cases=[tc("qwerty\n", "ok"), tc("admin\n", "fail"), tc("\n", "fail"), tc("qwerty1\n", "fail"), tc("secret\n", "fail")],
    ),
    translate_task(
      32, "Скидка при сумме > 1000",
      "Прочитайте сумму. Если > 1000 — скидка 10%. Выведите итог с двумя знаками после запятой. Исправьте ошибки.",
      "medium",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      code_examples=_EX_DISCOUNT,
      test_cases=[tc("1200\n", "1080.00"), tc("1000\n", "1000.00"), tc("999\n", "999.00"), tc("2000\n", "1800.00"), tc("0\n", "0.00")],
      template="var total: real;\nbegin\n  readln(total);\n  if total>1000 then total:=total*0.1;\n  writeln(total:0:2);\nend.",
    ),
    translate_task(
      33, "Безопасное деление",
      "Прочитайте a и b. Если b=0 — error, иначе целочисленное деление. Переведите на Pascal.",
      "hard",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      code_examples=_EX_SAFE_DIV,
      test_cases=[tc("10 2\n", "5"), tc("10 0\n", "error"), tc("9 3\n", "3"), tc("-8 2\n", "-4"), tc("0 5\n", "0")],
    ),
    _block_from_body(
      34, "Статус аккаунта",
      "Прочитайте код. Если > 0 — active, иначе blocked. Соберите программу из блоков.",
      "easy",
      "var x: integer;\nbegin\n  readln(x);\n  if x>0 then writeln('active') else writeln('blocked');\nend.",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      examples=_EX_STATUS,
      test_cases=[tc("1\n", "active"), tc("0\n", "blocked"), tc("5\n", "active"), tc("-1\n", "blocked"), tc("10\n", "active")],
    ),
    translate_task(
      35, "Проверить оценку 1–5",
      "Прочитайте оценку. Если от 1 до 5 — valid, иначе invalid. Исправьте ошибки.",
      "medium",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      code_examples=_EX_GRADE,
      test_cases=[tc("1\n", "valid"), tc("5\n", "valid"), tc("3\n", "valid"), tc("0\n", "invalid"), tc("6\n", "invalid")],
      template="var g: integer;\nbegin\n  readln(g);\n  if (g>1) and (g<5) then writeln('valid') else writeln('invalid');\nend.",
    ),
    translate_task(
      36, "Возраст и билет",
      "Прочитайте возраст и yes/no. allow только если >=18 и yes. Переведите на Pascal.",
      "hard",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      code_examples=_EX_AGE_TICKET,
      test_cases=[tc("18\nyes\n", "allow"), tc("17\nyes\n", "deny"), tc("20\nno\n", "deny"), tc("30\nyes\n", "allow"), tc("10\nno\n", "deny")],
    ),
    _block_from_body(
      37, "Знак произведения",
      "Прочитайте a и b. Выведите positive, negative или zero. Соберите программу из блоков.",
      "easy",
      "var a,b: integer;\nbegin\n  readln(a,b);\n  if (a=0) or (b=0) then writeln('zero')\n  else if a*b>0 then writeln('positive') else writeln('negative');\nend.",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      examples=_EX_PRODUCT_SIGN,
      test_cases=[tc("2 3\n", "positive"), tc("-2 3\n", "negative"), tc("-2 -3\n", "positive"), tc("0 5\n", "zero"), tc("5 0\n", "zero")],
    ),
    translate_task(
      38, "Зачисление на экзамен",
      "Прочитайте теорию, практику и пропуски. admit если теория>=70, практика>60, пропусков=0. Исправьте ошибки.",
      "medium",
      topics=_SIMPLE_BRANCH_TOPICS,
      constructions=_SIMPLE_BRANCH_CONSTRUCTIONS,
      code_examples=_EX_EXAM_ADMIT,
      test_cases=[tc("80 90 0\n", "admit"), tc("50 90 0\n", "deny"), tc("80 60 0\n", "deny"), tc("80 90 1\n", "deny"), tc("70 75 0\n", "admit")],
      template="var theory,practice,absent: integer;\nbegin\n  readln(theory,practice,absent);\n  if (theory>=70) or (practice>=60) then writeln('admit') else writeln('deny');\nend.",
    ),
    # --- 39-50 multi branching ---
    translate_task(
        39, "Оценка по баллам",
        "Прочитайте балл и выведите оценку 1–5 по шкале. Переведите программу на Pascal.",
        "hard",
        topics=_MULTI_BRANCH_TOPICS,
        constructions=_MULTI_BRANCH_CONSTRUCTIONS,
        code_examples=_EX_SCORE_GRADE,
        test_cases=[tc("95\n", "5"), tc("75\n", "4"), tc("55\n", "3"), tc("30\n", "2"), tc("90\n", "5")],
    ),
    _block_from_body(
        40, "День недели",
        "Прочитайте число 1–7 и выведите Mon–Sun. Соберите программу из блоков.",
        "easy",
        "var d: integer;\nbegin\n  readln(d);\n"
        "  case d of\n"
        "    1: writeln('Mon');\n"
        "    2: writeln('Tue');\n"
        "    3: writeln('Wed');\n"
        "    4: writeln('Thu');\n"
        "    5: writeln('Fri');\n"
        "    6: writeln('Sat');\n"
        "    else writeln('Sun');\n"
        "  end;\nend.",
        topics=_MULTI_BRANCH_TOPICS,
        constructions=_MULTI_BRANCH_CONSTRUCTIONS,
        examples=_EX_DAY,
        test_cases=[tc("1\n", "Mon"), tc("2\n", "Tue"), tc("3\n", "Wed"), tc("4\n", "Thu"), tc("5\n", "Fri")],
    ),
    translate_task(
        41, "Сезон по месяцу",
        "Прочитайте месяц и выведите winter/spring/summer/autumn. Исправьте ошибки.",
        "medium",
        topics=_MULTI_BRANCH_TOPICS,
        constructions=_MULTI_BRANCH_CONSTRUCTIONS,
        code_examples=_EX_SEASON,
        test_cases=[tc("12\n", "winter"), tc("3\n", "spring"), tc("6\n", "summer"), tc("9\n", "autumn"), tc("1\n", "winter")],
        template="var m: integer;\nbegin\n  readln(m);\n  if (m>=3) and (m<=5) then writeln('winter')\n  else if (m>=6) and (m<=8) then writeln('spring')\n  else writeln('summer');\nend.",
    ),
    translate_task(
        42, "Тариф по коду",
        "Прочитайте код A/B/C и выведите 100/200/300, иначе 0. Переведите на Pascal.",
        "hard",
        topics=_MULTI_BRANCH_TOPICS,
        constructions=_MULTI_BRANCH_CONSTRUCTIONS,
        code_examples=_EX_TARIFF,
        test_cases=[tc("A\n", "100"), tc("B\n", "200"), tc("C\n", "300"), tc("X\n", "0"), tc("a\n", "0")],
    ),
    _block_from_body(
        43, "Скидка по баллам",
        "Прочитайте балл: >=90→30, >=70→20, >=50→10, иначе 0. Соберите программу из блоков.",
        "easy",
        "var score: integer;\nbegin\n  readln(score);\n"
        "  if score>=90 then writeln(30)\n"
        "  else if score>=70 then writeln(20)\n"
        "  else if score>=50 then writeln(10)\n"
        "  else writeln(0);\nend.",
        topics=_MULTI_BRANCH_TOPICS,
        constructions=_MULTI_BRANCH_CONSTRUCTIONS,
        examples=_EX_DISCOUNT_TIER,
        test_cases=[tc("95\n", "30"), tc("75\n", "20"), tc("55\n", "10"), tc("30\n", "0"), tc("90\n", "30")],
    ),
    translate_task(
        44, "Мини-калькулятор",
        "Прочитайте операцию (1=+, 2=-, 3=*) и a, b. Исправьте ошибки в программе.",
        "medium",
        topics=_MULTI_BRANCH_TOPICS,
        constructions=_MULTI_BRANCH_CONSTRUCTIONS,
        code_examples=_EX_CALC,
        test_cases=[tc("1 2 3\n", "5"), tc("2 10 3\n", "7"), tc("3 4 5\n", "20"), tc("4 1 1\n", "error"), tc("1 0 0\n", "0")],
        template="var op,a,b: integer;\nbegin\n  readln(op,a,b);\n  if op=1 then writeln(a-b)\n  else if op=2 then writeln(a+b)\n  else writeln(a*b);\nend.",
    ),
    translate_task(
        45, "Статус заказа",
        "Прочитайте код: 1→new, 2→processing, 3→shipped, 4→delivered, иначе unknown. Переведите на Pascal.",
        "hard",
        topics=_MULTI_BRANCH_TOPICS,
        constructions=_MULTI_BRANCH_CONSTRUCTIONS,
        code_examples=_EX_ORDER_STATUS,
        test_cases=[tc("1\n", "new"), tc("2\n", "processing"), tc("3\n", "shipped"), tc("4\n", "delivered"), tc("5\n", "unknown")],
    ),
    _block_from_body(
        46, "Возрастная категория",
        "Прочитайте возраст: 0–12 child, 13–17 teen, 18–64 adult, 65+ senior. Соберите из блоков.",
        "easy",
        "var age: integer;\nbegin\n  readln(age);\n"
        "  if age<=12 then writeln('child')\n"
        "  else if age<=17 then writeln('teen')\n"
        "  else if age<=64 then writeln('adult')\n"
        "  else writeln('senior');\nend.",
        topics=_MULTI_BRANCH_TOPICS,
        constructions=_MULTI_BRANCH_CONSTRUCTIONS,
        examples=_EX_AGE_CAT,
        test_cases=[tc("5\n", "child"), tc("15\n", "teen"), tc("30\n", "adult"), tc("70\n", "senior"), tc("12\n", "child")],
    ),
    translate_task(
        47, "Буквенный рейтинг игрока",
        "Прочитайте балл: >=90 A, >=75 B, >=60 C, иначе D. Исправьте ошибки.",
        "medium",
        topics=_MULTI_BRANCH_TOPICS,
        constructions=_MULTI_BRANCH_CONSTRUCTIONS,
        code_examples=_EX_RATING,
        test_cases=[tc("95\n", "A"), tc("80\n", "B"), tc("65\n", "C"), tc("50\n", "D"), tc("90\n", "A")],
        template="var score: integer;\nbegin\n  readln(score);\n  if score>=90 then writeln('B')\n  else if score>=75 then writeln('C')\n  else writeln('D');\nend.",
    ),
    translate_task(
        48, "Тип треугольника",
        "Прочитайте три стороны. Выведите equilateral/isosceles/scalene/invalid. Переведите на Pascal.",
        "hard",
        topics=_MULTI_BRANCH_TOPICS,
        constructions=_MULTI_BRANCH_CONSTRUCTIONS,
        code_examples=_EX_TRIANGLE,
        test_cases=[tc("3 3 3\n", "equilateral"), tc("3 3 5\n", "isosceles"), tc("3 4 5\n", "scalene"), tc("1 2 5\n", "invalid"), tc("5 5 5\n", "equilateral")],
    ),
    _block_from_body(
        49, "Категория товара",
        "Прочитайте код: 1→food, 2→electronics, 3→clothing, иначе other. Соберите из блоков.",
        "easy",
        "var code: integer;\nbegin\n  readln(code);\n"
        "  if code=1 then writeln('food')\n"
        "  else if code=2 then writeln('electronics')\n"
        "  else if code=3 then writeln('clothing')\n"
        "  else writeln('other');\nend.",
        topics=_MULTI_BRANCH_TOPICS,
        constructions=_MULTI_BRANCH_CONSTRUCTIONS,
        examples=_EX_CATEGORY,
        test_cases=[tc("1\n", "food"), tc("2\n", "electronics"), tc("3\n", "clothing"), tc("0\n", "other"), tc("9\n", "other")],
    ),
    translate_task(
        50, "Меню банкомата",
        "Прочитайте пункт: 1→balance, 2→deposit, 3→withdraw, 4→exit, иначе error. Исправьте ошибки.",
        "medium",
        topics=_MULTI_BRANCH_TOPICS,
        constructions=_MULTI_BRANCH_CONSTRUCTIONS,
        code_examples=_EX_ATM,
        test_cases=[tc("1\n", "balance"), tc("2\n", "deposit"), tc("3\n", "withdraw"), tc("4\n", "exit"), tc("5\n", "error")],
        template="var choice: integer;\nbegin\n  readln(choice);\n  if choice=1 then writeln('deposit')\n  else if choice=2 then writeln('balance')\n  else writeln('exit');\nend.",
    ),
    # --- 51-66 loops ---
    translate_task(
        51, "Вывести числа 1..N",
        "Прочитайте N и выведите числа от 1 до N через пробел. Переведите на Pascal.",
        "hard",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_PRINT_1_N,
        test_cases=[tc("3\n", "1 2 3"), tc("1\n", "1"), tc("5\n", "1 2 3 4 5"), tc("0\n", ""), tc("2\n", "1 2")],
    ),
    _block_from_body(
        52, "Вывести числа N..1",
        "Прочитайте N и выведите числа от N до 1 через пробел. Соберите из блоков.",
        "easy",
        "var n,i: integer;\nbegin\n  readln(n);\n  for i:=n downto 1 do if i>1 then write(i,' ') else write(i);\n  writeln;\nend.",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        examples=_EX_PRINT_N_1,
        test_cases=[tc("3\n", "3 2 1"), tc("1\n", "1"), tc("5\n", "5 4 3 2 1"), tc("0\n", ""), tc("2\n", "2 1")],
    ),
    translate_task(
        53, "Сумма чисел 1..N",
        "Прочитайте N и выведите сумму 1+2+…+N. Исправьте ошибки.",
        "medium",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_SUM_1_N,
        test_cases=[tc("5\n", "15"), tc("1\n", "1"), tc("0\n", "0"), tc("10\n", "55"), tc("3\n", "6")],
        template="var n,i,s: integer;\nbegin\n  readln(n);\n  s:=0;\n  for i:=1 to n do s:=s-i;\n  writeln(s);\nend.",
    ),
    translate_task(
        54, "Произведение чисел 1..N",
        "Прочитайте N и выведите произведение 1×2×…×N. Переведите на Pascal.",
        "hard",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_PROD_1_N,
        test_cases=[tc("5\n", "120"), tc("1\n", "1"), tc("0\n", "1"), tc("4\n", "24"), tc("3\n", "6")],
    ),
    _block_from_body(
        55, "Счёт чётных от 1 до N",
        "Прочитайте N и выведите количество чётных чисел от 1 до N. Соберите из блоков.",
        "easy",
        "var n,i,c: integer;\nbegin\n  readln(n);\n  c:=0;\n  for i:=1 to n do if i mod 2=0 then c:=c+1;\n  writeln(c);\nend.",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        examples=_EX_COUNT_EVENS,
        test_cases=[tc("5\n", "2"), tc("1\n", "0"), tc("10\n", "5"), tc("0\n", "0"), tc("6\n", "3")],
    ),
    translate_task(
        56, "Таблица умножения для n",
        "Прочитайте n и выведите n, 2n, 3n, 4n через пробел. Исправьте ошибки.",
        "medium",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_MULT_TABLE,
        test_cases=[tc("2\n", "2 4"), tc("3\n", "3 6 9"), tc("1\n", "1"), tc("4\n", "4 8 12 16"), tc("0\n", "")],
        template="var n,i: integer;\nbegin\n  readln(n);\n  for i:=1 to n do if i<n then write(n*i,' ') else write(n*i);\n  writeln;\nend.",
    ),
    translate_task(
        57, "Сумма квадратов 1..N",
        "Прочитайте N и выведите сумму квадратов от 1 до N. Переведите на Pascal.",
        "hard",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_SUM_SQUARES,
        test_cases=[tc("3\n", "14"), tc("1\n", "1"), tc("0\n", "0"), tc("5\n", "55"), tc("2\n", "5")],
    ),
    _block_from_body(
        58, "Максимум из N чисел",
        "Прочитайте N и N чисел, выведите максимум. Соберите из блоков.",
        "easy",
        "var n,i,maxv,x: integer;\nbegin\n  readln(n);\n  read(maxv);\n  for i:=2 to n do begin read(x); if x>maxv then maxv:=x; end;\n  writeln(maxv);\nend.",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        examples=_EX_MAX_N,
        test_cases=[tc("5\n1 2 3 4 5\n", "5"), tc("3\n-1 -5 -2\n", "-1"), tc("4\n0 10 2 7\n", "10"), tc("1\n42\n", "42"), tc("2\n5 5\n", "5")],
    ),
    translate_task(
        59, "Минимум из N чисел",
        "Прочитайте N и N чисел, выведите минимум. Исправьте ошибки.",
        "medium",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_MIN_N,
        test_cases=[tc("3\n-1 -5 -2\n", "-5"), tc("5\n1 2 3 4 5\n", "1"), tc("4\n0 10 2 7\n", "0"), tc("1\n42\n", "42"), tc("2\n5 5\n", "5")],
        template="var n,i,minv,x: integer;\nbegin\n  readln(n);\n  readln(minv);\n  for i:=2 to n do begin readln(x); if x>minv then minv:=x; end;\n  writeln(minv);\nend.",
    ),
    translate_task(
        60, "Счёт положительных из N чисел",
        "Прочитайте N и N чисел, выведите количество положительных. Переведите на Pascal.",
        "hard",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_COUNT_POS,
        test_cases=[tc("5\n1 -2 3 0 5\n", "3"), tc("3\n0 0 0\n", "0"), tc("1\n-1\n", "0"), tc("4\n1 2 3 4\n", "4"), tc("2\n-5 10\n", "1")],
    ),
    _block_from_body(
        61, "Сумма N цен",
        "Прочитайте N и N цен, выведите сумму. Соберите из блоков.",
        "easy",
        "var n,i,s,price: integer;\nbegin\n  readln(n);\n  s:=0;\n  for i:=1 to n do begin read(price); s:=s+price; end;\n  writeln(s);\nend.",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        examples=_EX_SUM_PRICES,
        test_cases=[tc("3\n100 200 50\n", "350"), tc("1\n99\n", "99"), tc("0\n", "0"), tc("2\n10 20\n", "30"), tc("5\n1 1 1 1 1\n", "5")],
    ),
    translate_task(
        62, "Среднее N чисел",
        "Прочитайте N и N чисел, выведите среднее с одним знаком после запятой. Исправьте ошибки.",
        "medium",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_AVG_N,
        test_cases=[tc("3\n3 6 9\n", "6.0"), tc("2\n10 20\n", "15.0"), tc("1\n5\n", "5.0"), tc("4\n1 2 3 4\n", "2.5"), tc("2\n0 10\n", "5.0")],
        template="var n,i,s,x: integer;\nbegin\n  readln(n);\n  s:=0;\n  for i:=1 to n do begin readln(x); s:=s+x; end;\n  writeln(s);\nend.",
    ),
    translate_task(
        63, "Сумма до нуля",
        "Читайте числа до 0, суммируйте все до нуля. Переведите на Pascal.",
        "hard",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_READ_UNTIL0,
        test_cases=[tc("1\n2\n3\n0\n", "6"), tc("5\n0\n", "5"), tc("0\n", "0"), tc("-1\n2\n0\n", "1"), tc("10\n-3\n0\n", "7")],
    ),
    _block_from_body(
        64, "Проверка пароля",
        "Читайте пароль до совпадения с admin, затем выведите ok. Соберите из блоков.",
        "easy",
        "var p: string;\nbegin\n  repeat\n    readln(p);\n  until p='admin';\n  writeln('ok');\nend.",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        examples=_EX_PWD_CHECK,
        test_cases=[tc("wrong\nadmin\n", "ok"), tc("admin\n", "ok"), tc("x\ny\nadmin\n", "ok"), tc("no\nno\nadmin\n", "ok"), tc("a\nadmin\n", "ok")],
    ),
    translate_task(
        65, "Накопление бонусов",
        "Читайте бонусы до 0, суммируйте. Исправьте ошибки.",
        "medium",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_BONUS,
        test_cases=[tc("10\n20\n30\n0\n", "60"), tc("5\n0\n", "5"), tc("0\n", "0"), tc("1\n2\n3\n0\n", "6"), tc("100\n-50\n0\n", "50")],
        template="var b,s: integer;\nbegin\n  s:=0;\n  readln(b);\n  while b>0 do begin s:=s+b; readln(b); end;\n  writeln(s);\nend.",
    ),
    translate_task(
        66, "Анализ экзамена",
        "Прочитайте N и N баллов, выведите число с баллом >= 60. Переведите на Pascal.",
        "hard",
        topics=_LOOPS_TOPICS,
        constructions=_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_EXAM_COUNT,
        test_cases=[tc("3\n80\n50\n70\n", "2"), tc("2\n40\n80\n", "1"), tc("1\n30\n", "0"), tc("4\n60\n60\n60\n60\n", "4"), tc("0\n", "0")],
    ),
    # --- 67-74 nested loops ---
    _block_from_body(
        67, "Квадрат из звёздочек",
        "Прочитайте n и выведите квадрат n×n из *. Соберите из блоков.",
        "easy",
        "var n,i,j: integer;\nbegin\n  readln(n);\n"
        "  for i:=1 to n do begin\n"
        "    for j:=1 to n do write('*');\n"
        "    writeln;\n"
        "  end;\nend.",
        topics=_NESTED_LOOPS_TOPICS,
        constructions=_NESTED_LOOPS_CONSTRUCTIONS,
        examples=_EX_SQUARE_STARS,
        test_cases=[tc("2\n", "**\n**"), tc("3\n", "***\n***\n***"), tc("0\n", ""), tc("1\n", "*"), tc("4\n", "****\n****\n****\n****")],
    ),
    translate_task(
        68, "Прямоугольник из звёздочек",
        "Прочитайте ширину и высоту, выведите прямоугольник из *. Исправьте ошибки.",
        "medium",
        topics=_NESTED_LOOPS_TOPICS,
        constructions=_NESTED_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_RECT_STARS,
        test_cases=[tc("3 2\n", "***\n***"), tc("2 3\n", "**\n**\n**"), tc("1 1\n", "*"), tc("0 2\n", ""), tc("4 0\n", "")],
        template="var w,h,i,j: integer;\nbegin\n  readln(w,h);\n  for i:=1 to w do for j:=1 to h do write('*'); writeln;\nend.",
    ),
    translate_task(
        69, "Прямоугольный треугольник из *",
        "Прочитайте n, выведите треугольник: 1 строка — 1 *, 2 — 2 *, … Переведите на Pascal.",
        "hard",
        topics=_NESTED_LOOPS_TOPICS,
        constructions=_NESTED_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_RIGHT_TRI,
        test_cases=[tc("3\n", "*\n**\n***"), tc("1\n", "*"), tc("2\n", "*\n**"), tc("0\n", ""), tc("4\n", "*\n**\n***\n****")],
    ),
    _block_from_body(
        70, "Таблица умножения до n",
        "Прочитайте n и выведите таблицу умножения n×n. Соберите из блоков.",
        "easy",
        "var n,i,j: integer;\nbegin\n  readln(n);\n"
        "  for i:=1 to n do begin\n"
        "    for j:=1 to n do if j<n then write(i*j,' ') else write(i*j);\n"
        "    writeln;\n"
        "  end;\nend.",
        topics=_NESTED_LOOPS_TOPICS,
        constructions=_NESTED_LOOPS_CONSTRUCTIONS,
        examples=_EX_FULL_MULT,
        test_cases=[tc("2\n", "1 2\n2 4"), tc("1\n", "1"), tc("3\n", "1 2 3\n2 4 6\n3 6 9"), tc("0\n", ""), tc("4\n", "1 2 3 4\n2 4 6 8\n3 6 9 12\n4 8 12 16")],
    ),
    translate_task(
        71, "Шахматная доска",
        "Прочитайте n, выведите доску n×n из # и . Исправьте ошибки.",
        "medium",
        topics=_NESTED_LOOPS_TOPICS,
        constructions=_NESTED_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_CHESS,
        test_cases=[tc("2\n", "#.\n.#"), tc("1\n", "#"), tc("3\n", "#.#\n.#.\n#.#"), tc("0\n", ""), tc("4\n", "#.#.\n.#.#\n#.#.\n.#.#")],
        template="var n,i,j: integer;\nbegin\n  readln(n);\n  for i:=1 to n do for j:=1 to n do write('#'); writeln;\nend.",
    ),
    translate_task(
        72, "Сетка координат",
        "Прочитайте n, выведите координаты i,j для i,j от 0 до n-1. Переведите на Pascal.",
        "hard",
        topics=_NESTED_LOOPS_TOPICS,
        constructions=_NESTED_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_COORD_GRID,
        test_cases=[tc("2\n", "0,0 0,1\n1,0 1,1"), tc("1\n", "0,0"), tc("3\n", "0,0 0,1 0,2\n1,0 1,1 1,2\n2,0 2,1 2,2"), tc("0\n", ""), tc("2\n", "0,0 0,1\n1,0 1,1")],
    ),
    _block_from_body(
        73, "Первая пара с суммой target",
        "Прочитайте N, N чисел и target. Выведите первую пару с суммой target. Соберите из блоков.",
        "easy",
        "var n,i,j,t: integer; nums: array[1..100] of integer;\nbegin\n"
        "  readln(n);\n  for i:=1 to n do read(nums[i]);\n  readln(t);\n"
        "  for i:=1 to n do for j:=i+1 to n do\n"
        "    if nums[i]+nums[j]=t then writeln(nums[i],' ',nums[j]);\nend.",
        topics=_NESTED_LOOPS_TOPICS,
        constructions=_NESTED_LOOPS_CONSTRUCTIONS,
        examples=_EX_PAIR_SUM,
        test_cases=[tc("4\n1 2 3 4\n5\n", "1 4"), tc("3\n1 2 4\n5\n", "1 4"), tc("2\n5 5\n10\n", "5 5"), tc("5\n1 -1 2 3 4\n4\n", "1 3"), tc("3\n2 2 2\n4\n", "2 2")],
    ),
    translate_task(
        74, "Пропуск запрещенных значений",
        "Прочитайте n, выведите числа 1..n, пропуская кратные 3. Исправьте ошибки.",
        "medium",
        topics=_NESTED_LOOPS_TOPICS,
        constructions=_NESTED_LOOPS_CONSTRUCTIONS,
        code_examples=_EX_SKIP_MULT3,
        test_cases=[tc("5\n", "1 2 4 5"), tc("6\n", "1 2 4 5 6"), tc("3\n", "1 2"), tc("1\n", "1"), tc("0\n", "")],
        template="var n,i: integer;\nbegin\n  readln(n);\n  for i:=1 to n do write(i,' ');\n  writeln;\nend.",
    ),
  ]


COURSE_BATCH_25_74_CATALOG = build_course_batch_25_74_catalog()
COURSE_BATCH_25_74_SIZE = len(COURSE_BATCH_25_74_CATALOG)
