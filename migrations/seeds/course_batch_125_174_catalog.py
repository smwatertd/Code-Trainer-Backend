"""Разделы «Функции», «Рекурсия», «Поиск/фильтрация/свёртка», «Сортировка» — задачи 125–174."""
from __future__ import annotations

from migrations.seeds.catalog_common import (
    block_task,
    pascal_blocks_from_body,
    tc,
    translate_task,
)

TaskRow = dict

_FUNCTIONS_TOPICS = ["functions", "function_definition"]
_FUNCTIONS_CONSTRUCTIONS = [
    "function_definition",
    "function_invocation",
    "return_flow",
    "parameter_passing",
    "typed_declaration",
    "stdin_read",
    "stdout_write",
]

_RECURSION_TOPICS = ["functions", "recursion"]
_RECURSION_CONSTRUCTIONS = [
    "recursion",
    "function_definition",
    "function_invocation",
    "return_flow",
    "typed_declaration",
    "stdin_read",
    "stdout_write",
]

_SEARCH_BASE_CONSTRUCTIONS = [
    "search_find",
    "filter_select",
    "fold_aggregate",
    "collection_iteration",
    "stdin_read",
    "assignment",
    "stdout_write",
]

_SORT_TOPICS = ["algorithms", "sort_order"]
_SORT_CONSTRUCTIONS = [
    "sort_order",
    "collection_iteration",
    "indexed_sequence",
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


def _algo_topics(task_id: int) -> list[str]:
    kinds = ["search_find", "filter_select", "fold_aggregate"]
    return ["algorithms", kinds[(task_id - 149) % 3]]


# --- function examples ---

_EX_IS_EVEN = _stub(
    "def is_even(n):\n    return n % 2 == 0\nn = int(input())\nprint('yes' if is_even(n) else 'no')",
    "function IsEven(n: integer): boolean;\nbegin\n  IsEven:=n mod 2=0;\nend;\n"
    "var n: integer;\nbegin\n  readln(n);\n  if IsEven(n) then writeln('yes') else writeln('no');\nend.",
)

_EX_DISCOUNT = _stub(
    "def discount(price, pct):\n    return price * (100 - pct) // 100\n"
    "price, pct = map(int, input().split())\nprint(discount(price, pct))",
    "function Discount(price,pct: integer): integer;\nbegin\n  Discount:=price*(100-pct) div 100;\nend;\n"
    "var price,pct: integer;\nbegin\n  readln(price,pct);\n  writeln(Discount(price,pct));\nend.",
)

_EX_PRINT_MSG = _stub(
    "def print_msg(s):\n    print(s)\ns = input()\nprint_msg(s)",
    "procedure PrintMsg(s: string);\nbegin\n  writeln(s);\nend;\n"
    "var s: string;\nbegin\n  readln(s);\n  PrintMsg(s);\nend.",
)

_EX_SWAP = _stub(
    "def swap(a, b):\n    return b, a\na, b = map(int, input().split())\na, b = swap(a, b)\nprint(a, b)",
    "procedure Swap(var a,b: integer);\nvar t: integer;\nbegin\n  t:=a; a:=b; b:=t;\nend;\n"
    "var a,b: integer;\nbegin\n  readln(a,b);\n  Swap(a,b);\n  writeln(a,' ',b);\nend.",
)

_EX_AREA = _stub(
    "def area(w, h):\n    return w * h\nw, h = map(int, input().split())\nprint(area(w, h))",
    "function Area(w,h: integer): integer;\nbegin\n  Area:=w*h;\nend;\n"
    "var w,h: integer;\nbegin\n  readln(w,h);\n  writeln(Area(w,h));\nend.",
)

_EX_CTOF = _stub(
    "def c_to_f(c):\n    return c * 9 // 5 + 32\nc = int(input())\nprint(c_to_f(c))",
    "function CtoF(c: integer): integer;\nbegin\n  CtoF:=c*9 div 5+32;\nend;\n"
    "var c: integer;\nbegin\n  readln(c);\n  writeln(CtoF(c));\nend.",
)

_EX_TAX = _stub(
    "def tax(price, rate):\n    return price + price * rate // 100\n"
    "price, rate = map(int, input().split())\nprint(tax(price, rate))",
    "function Tax(price,rate: integer): integer;\nbegin\n  Tax:=price+price*rate div 100;\nend;\n"
    "var price,rate: integer;\nbegin\n  readln(price,rate);\n  writeln(Tax(price,rate));\nend.",
)

_EX_AVG_ARRAY = _stub(
    "def avg_array(nums):\n    return sum(nums) / len(nums)\n"
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(f'{avg_array(nums):.1f}')",
    "function AvgArray(a: array of integer; n: integer): real;\nvar i,s: integer;\nbegin\n  s:=0;\n"
    "  for i:=0 to n-1 do s:=s+a[i];\n  AvgArray:=s/n;\nend;\n"
    "var n,i: integer; a: array of integer; avg: real;\nbegin\n"
    "  readln(n); SetLength(a,n);\n  for i:=0 to n-1 do read(a[i]);\n"
    "  avg:=AvgArray(a,n);\n  writeln(avg:0:1);\nend.",
)

_EX_CONTAINS = _stub(
    "def contains(nums, x):\n    return x in nums\n"
    "n = int(input())\nnums = list(map(int, input().split()))\nx = int(input())\n"
    "print('yes' if contains(nums, x) else 'no')",
    "function Contains(a: array of integer; n,x: integer): boolean;\nvar i: integer;\nbegin\n"
    "  Contains:=false;\n  for i:=0 to n-1 do if a[i]=x then Contains:=true;\nend;\n"
    "var n,i,x: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
    "  for i:=0 to n-1 do read(a[i]);\n  readln(x);\n"
    "  if Contains(a,n,x) then writeln('yes') else writeln('no');\nend.",
)

_EX_INDEX_OF = _stub(
    "def index_of(nums, x):\n    return nums.index(x) + 1 if x in nums else -1\n"
    "n = int(input())\nnums = list(map(int, input().split()))\nx = int(input())\nprint(index_of(nums, x))",
    "function IndexOf(a: array of integer; n,x: integer): integer;\nvar i: integer;\nbegin\n"
    "  IndexOf:=-1;\n  for i:=0 to n-1 do if a[i]=x then IndexOf:=i+1;\nend;\n"
    "var n,i,x: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
    "  for i:=0 to n-1 do read(a[i]);\n  readln(x);\n  writeln(IndexOf(a,n,x));\nend.",
)

_EX_COUNT_IF = _stub(
    "def count_if(nums, t):\n    return sum(1 for x in nums if x > t)\n"
    "n = int(input())\nnums = list(map(int, input().split()))\nt = int(input())\nprint(count_if(nums, t))",
    "function CountIf(a: array of integer; n,t: integer): integer;\nvar i,c: integer;\nbegin\n  c:=0;\n"
    "  for i:=0 to n-1 do if a[i]>t then c:=c+1;\n  CountIf:=c;\nend;\n"
    "var n,i,t: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
    "  for i:=0 to n-1 do read(a[i]);\n  readln(t);\n  writeln(CountIf(a,n,t));\nend.",
)

_EX_VALIDATE_PWD = _stub(
    "def validate_password(p):\n    return len(p) >= 8 and any(c.isdigit() for c in p)\n"
    "p = input()\nprint('valid' if validate_password(p) else 'invalid')",
    "function ValidatePassword(p: string): boolean;\nvar i: integer; has_digit: boolean;\nbegin\n"
    "  has_digit:=false;\n  for i:=1 to length(p) do if (p[i]>='0') and (p[i]<='9') then has_digit:=true;\n"
    "  ValidatePassword:=(length(p)>=8) and has_digit;\nend;\n"
    "var p: string;\nbegin\n  readln(p);\n"
    "  if ValidatePassword(p) then writeln('valid') else writeln('invalid');\nend.",
)

_EX_FORMAT_NAME = _stub(
    "def format_name(first, last):\n    return f'{last}, {first}'\n"
    "first, last = input().split()\nprint(format_name(first, last))",
    "function FormatName(first,last: string): string;\nbegin\n  FormatName:=last+', '+first;\nend;\n"
    "var first,last: string;\nbegin\n  readln(first,last);\n  writeln(FormatName(first,last));\nend.",
)

_EX_GRADE_CAT = _stub(
    "def grade_category(score):\n"
    "    if score >= 90: return 'A'\n    if score >= 80: return 'B'\n"
    "    if score >= 70: return 'C'\n    if score >= 60: return 'D'\n    return 'F'\n"
    "score = int(input())\nprint(grade_category(score))",
    "function GradeCategory(score: integer): char;\nbegin\n"
    "  if score>=90 then GradeCategory:='A'\n  else if score>=80 then GradeCategory:='B'\n"
    "  else if score>=70 then GradeCategory:='C'\n  else if score>=60 then GradeCategory:='D'\n"
    "  else GradeCategory:='F';\nend;\nvar score: integer;\nbegin\n  readln(score);\n  writeln(GradeCategory(score));\nend.",
)

_EX_SALARY = _stub(
    "def salary(hours, rate):\n    return hours * rate\n"
    "hours, rate = map(int, input().split())\nprint(salary(hours, rate))",
    "function Salary(hours,rate: integer): integer;\nbegin\n  Salary:=hours*rate;\nend;\n"
    "var hours,rate: integer;\nbegin\n  readln(hours,rate);\n  writeln(Salary(hours,rate));\nend.",
)

_EX_FUNC_CALC = _stub(
    "def calc(op, a, b):\n    if op == 1: return a + b\n    if op == 2: return a - b\n    return a * b\n"
    "op, a, b = map(int, input().split())\nprint(calc(op, a, b))",
    "function Calc(op,a,b: integer): integer;\nbegin\n"
    "  if op=1 then Calc:=a+b\n  else if op=2 then Calc:=a-b\n  else Calc:=a*b;\nend;\n"
    "var op,a,b: integer;\nbegin\n  readln(op,a,b);\n  writeln(Calc(op,a,b));\nend.",
)


# --- recursion examples ---

_EX_FACTORIAL = _stub(
    "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\nn = int(input())\nprint(fact(n))",
    "function Fact(n: integer): integer;\nbegin\n  if n<=1 then Fact:=1 else Fact:=n*Fact(n-1);\nend;\n"
    "var n: integer;\nbegin\n  readln(n);\n  writeln(Fact(n));\nend.",
)

_EX_REC_SUM = _stub(
    "def rec_sum(n):\n    if n <= 0:\n        return 0\n    return n + rec_sum(n - 1)\nn = int(input())\nprint(rec_sum(n))",
    "function RecSum(n: integer): integer;\nbegin\n  if n<=0 then RecSum:=0 else RecSum:=n+RecSum(n-1);\nend;\n"
    "var n: integer;\nbegin\n  readln(n);\n  writeln(RecSum(n));\nend.",
)

_EX_FIB = _stub(
    "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n - 1) + fib(n - 2)\nn = int(input())\nprint(fib(n))",
    "function Fib(n: integer): integer;\nbegin\n"
    "  if n<=1 then Fib:=n else Fib:=Fib(n-1)+Fib(n-2);\nend;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(Fib(n));\nend.",
)

_EX_REC_PRINT = _stub(
    "def rec_print(n):\n    if n > 0:\n        print(n, end=' ')\n        rec_print(n - 1)\n"
    "n = int(input())\nrec_print(n)\nprint()",
    "procedure RecPrint(n: integer);\nbegin\n  if n>0 then begin write(n,' '); RecPrint(n-1); end;\nend;\n"
    "var n: integer;\nbegin\n  readln(n);\n  RecPrint(n);\n  writeln;\nend.",
)

_EX_DIGIT_SUM = _stub(
    "def digit_sum(n):\n    if n < 10:\n        return n\n    return n % 10 + digit_sum(n // 10)\nn = int(input())\nprint(digit_sum(n))",
    "function DigitSum(n: integer): integer;\nbegin\n"
    "  if n<10 then DigitSum:=n else DigitSum:=(n mod 10)+DigitSum(n div 10);\nend;\n"
    "var n: integer;\nbegin\n  readln(n);\n  writeln(DigitSum(n));\nend.",
)

_EX_REC_SEARCH = _stub(
    "def rec_search(nums, x, i):\n    if i >= len(nums):\n        return False\n    if nums[i] == x:\n        return True\n    return rec_search(nums, x, i + 1)\n"
    "n = int(input())\nnums = list(map(int, input().split()))\nx = int(input())\n"
    "print('yes' if rec_search(nums, x, 0) else 'no')",
    "function RecSearch(a: array of integer; n,x,i: integer): boolean;\nbegin\n"
    "  if i>=n then RecSearch:=false\n  else if a[i]=x then RecSearch:=true\n  else RecSearch:=RecSearch(a,n,x,i+1);\nend;\n"
    "var n,i,x: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
    "  for i:=0 to n-1 do read(a[i]);\n  readln(x);\n"
    "  if RecSearch(a,n,x,0) then writeln('yes') else writeln('no');\nend.",
)

_EX_REC_PAL = _stub(
    "def is_pal(s, l, r):\n    if l >= r:\n        return True\n    if s[l] != s[r]:\n        return False\n    return is_pal(s, l + 1, r - 1)\n"
    "s = input().strip()\nprint('yes' if is_pal(s, 0, len(s) - 1) else 'no')",
    "function IsPal(s: string; l,r: integer): boolean;\nbegin\n"
    "  if l>=r then IsPal:=true\n  else if s[l+1]<>s[r+1] then IsPal:=false\n  else IsPal:=IsPal(s,l+1,r-1);\nend;\n"
    "var s: string;\nbegin\n  readln(s);\n  if IsPal(s,0,length(s)-1) then writeln('yes') else writeln('no');\nend.",
)

_EX_FOLDER_TREE = _stub(
    "def print_tree(depth, n):\n    if depth <= n:\n        print('*' * depth)\n        print_tree(depth + 1, n)\n"
    "n = int(input())\nprint_tree(1, n)",
    "procedure PrintTree(depth,n: integer);\nbegin\n"
    "  if depth<=n then begin\n"
    "    writeln(StringOfChar('*',depth));\n    PrintTree(depth+1,n);\n  end;\nend;\n"
    "var n: integer;\nbegin\n  readln(n);\n  PrintTree(1,n);\nend.",
)

# --- search/filter/fold examples ---

_EX_LIN_SEARCH = _stub(
    "n = int(input())\nids = list(map(int, input().split()))\ntarget = int(input())\n"
    "for i in range(n):\n    if ids[i] == target:\n        print(i + 1)\n        break\nelse:\n    print(-1)",
    "var n,i,target: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n  readln(target);\n"
    "  for i:=1 to n do if a[i]=target then begin writeln(i); halt; end;\n  writeln(-1);\nend.",
)

_EX_FIRST_EXP = _stub(
    "n = int(input())\nprices = list(map(int, input().split()))\nth = int(input())\n"
    "for p in prices:\n    if p > th:\n        print(p)\n        break\nelse:\n    print(-1)",
    "var n,i,th,p: integer; a: array[1..100] of integer; found: boolean;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n  readln(th); found:=false;\n"
    "  for i:=1 to n do if a[i]>th then begin writeln(a[i]); found:=true; halt; end;\n"
    "  if not found then writeln(-1);\nend.",
)

_EX_FILTER_POS = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\n"
    "pos = [x for x in nums if x > 0]\nprint(' '.join(map(str, pos)))",
    "var n,i,c: integer; a,b: array[1..100] of integer;\nbegin\n  readln(n); c:=0;\n"
    "  for i:=1 to n do read(a[i]);\n  for i:=1 to n do if a[i]>0 then begin c:=c+1; b[c]:=a[i]; end;\n"
    "  for i:=1 to c do if i<c then write(b[i],' ') else write(b[i]);\n  writeln;\nend.",
)

_EX_FILTER_LEN = _stub(
    "n = int(input())\nlines = [input() for _ in range(n)]\nk = int(input())\n"
    "for s in lines:\n    if len(s) >= k:\n        print(s)",
    "var n,i,k: integer; s: array[1..100] of string;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do readln(s[i]);\n  readln(k);\n"
    "  for i:=1 to n do if length(s[i])>=k then writeln(s[i]);\nend.",
)

_EX_SUM_MATCH = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(sum(x for x in nums if x > 0))",
    "var n,i,s: integer; a: array[1..100] of integer;\nbegin\n  readln(n); s:=0;\n"
    "  for i:=1 to n do begin read(a[i]); if a[i]>0 then s:=s+a[i]; end;\n  writeln(s);\nend.",
)

_EX_COUNT_MATCH = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(sum(1 for x in nums if x > 0))",
    "var n,i,c: integer; a: array[1..100] of integer;\nbegin\n  readln(n); c:=0;\n"
    "  for i:=1 to n do begin read(a[i]); if a[i]>0 then c:=c+1; end;\n  writeln(c);\nend.",
)

_EX_ANY = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint('yes' if any(x > 0 for x in nums) else 'no')",
    "var n,i: integer; a: array[1..100] of integer; ok: boolean;\nbegin\n  readln(n); ok:=false;\n"
    "  for i:=1 to n do begin read(a[i]); if a[i]>0 then ok:=true; end;\n"
    "  if ok then writeln('yes') else writeln('no');\nend.",
)

_EX_ALL = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint('yes' if all(x > 0 for x in nums) else 'no')",
    "var n,i: integer; a: array[1..100] of integer; ok: boolean;\nbegin\n  readln(n); ok:=true;\n"
    "  for i:=1 to n do begin read(a[i]); if a[i]<=0 then ok:=false; end;\n"
    "  if ok then writeln('yes') else writeln('no');\nend.",
)

_EX_MUL_PRICES = _stub(
    "n = int(input())\nprices = list(map(int, input().split()))\nf = int(input())\n"
    "print(' '.join(str(p * f) for p in prices))",
    "var n,i,f: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n  readln(f);\n"
    "  for i:=1 to n do if i<n then write(a[i]*f,' ') else write(a[i]*f);\n  writeln;\nend.",
)

_EX_UPPER = _stub(
    "n = int(input())\nlines = [input() for _ in range(n)]\nfor s in lines:\n    print(s.upper())",
    "var n,i: integer; s: array[1..100] of string;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do readln(s[i]);\n  for i:=1 to n do writeln(upper(s[i]));\nend.",
)

_EX_ORDER_SUM = _stub(
    "n = int(input())\norders = list(map(int, input().split()))\nprint(sum(orders))",
    "var n,i,s: integer; a: array[1..100] of integer;\nbegin\n  readln(n); s:=0;\n"
    "  for i:=1 to n do begin read(a[i]); s:=s+a[i]; end;\n  writeln(s);\nend.",
)

_EX_AVG_RATING = _stub(
    "n = int(input())\nratings = list(map(int, input().split()))\nprint(f'{sum(ratings)/len(ratings):.1f}')",
    "var n,i,s: integer; a: array[1..100] of integer; avg: real;\nbegin\n  readln(n); s:=0;\n"
    "  for i:=1 to n do begin read(a[i]); s:=s+a[i]; end;\n  avg:=s/n;\n  writeln(avg:0:1);\nend.",
)

_EX_FILTER_STUDENTS = _stub(
    "n = int(input())\nscores = list(map(int, input().split()))\n"
    "passed = [s for s in scores if s >= 60]\nprint(' '.join(map(str, passed)))",
    "var n,i,c: integer; a,b: array[1..100] of integer;\nbegin\n  readln(n); c:=0;\n"
    "  for i:=1 to n do read(a[i]);\n  for i:=1 to n do if a[i]>=60 then begin c:=c+1; b[c]:=a[i]; end;\n"
    "  for i:=1 to c do if i<c then write(b[i],' ') else write(b[i]);\n  writeln;\nend.",
)

_EX_FILTER_TXT = _stub(
    "n = int(input())\nfiles = [input() for _ in range(n)]\n"
    "for f in files:\n    if f.endswith('.txt'):\n        print(f)",
    "var n,i: integer; f: array[1..100] of string;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do readln(f[i]);\n"
    "  for i:=1 to n do if copy(f[i],length(f[i])-3,4)='.txt' then writeln(f[i]);\nend.",
)

_EX_CTOF_LIST = _stub(
    "n = int(input())\ntemps = list(map(int, input().split()))\n"
    "print(' '.join(str(c * 9 // 5 + 32) for c in temps))",
    "var n,i: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n"
    "  for i:=1 to n do if i<n then write(a[i]*9 div 5+32,' ') else write(a[i]*9 div 5+32);\n  writeln;\nend.",
)

_EX_PASS_FAIL = _stub(
    "n = int(input())\nscores = list(map(int, input().split()))\n"
    "p = sum(1 for s in scores if s >= 60)\nprint(p, n - p)",
    "var n,i,p: integer; a: array[1..100] of integer;\nbegin\n  readln(n); p:=0;\n"
    "  for i:=1 to n do begin read(a[i]); if a[i]>=60 then p:=p+1; end;\n  writeln(p,' ',n-p);\nend.",
)

_EX_BEST_OFFER = _stub(
    "n = int(input())\nvalues = list(map(int, input().split()))\nprint(max(values))",
    "var n,i,maxv: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n  maxv:=a[1];\n"
    "  for i:=2 to n do if a[i]>maxv then maxv:=a[i];\n  writeln(maxv);\nend.",
)

_EX_STORE_REPORT = _stub(
    "n = int(input())\nsales = list(map(int, input().split()))\nprint(sum(sales), len(sales), max(sales))",
    "var n,i,s,maxv: integer; a: array[1..100] of integer;\nbegin\n  readln(n); s:=0; maxv:=0;\n"
    "  for i:=1 to n do begin read(a[i]); s:=s+a[i]; if a[i]>maxv then maxv:=a[i]; end;\n"
    "  writeln(s,' ',n,' ',maxv);\nend.",
)

# --- sort examples ---

_EX_SORT_ASC = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nnums.sort()\nprint(' '.join(map(str, nums)))",
    "var n,i,j,t: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n"
    "  for i:=1 to n-1 do for j:=1 to n-i do if a[j]>a[j+1] then begin t:=a[j]; a[j]:=a[j+1]; a[j+1]:=t; end;\n"
    "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_SORT_DESC = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nnums.sort(reverse=True)\nprint(' '.join(map(str, nums)))",
    "var n,i,j,t: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n"
    "  for i:=1 to n-1 do for j:=1 to n-i do if a[j]<a[j+1] then begin t:=a[j]; a[j]:=a[j+1]; a[j+1]:=t; end;\n"
    "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_SORT_STR = _stub(
    "n = int(input())\nlines = [input() for _ in range(n)]\nlines.sort()\nfor s in lines:\n    print(s)",
    "var n,i,j: integer; s,t: array[1..100] of string; tmp: string;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do readln(s[i]);\n"
    "  for i:=1 to n-1 do for j:=1 to n-i do if s[j]>s[j+1] then begin tmp:=s[j]; s[j]:=s[j+1]; s[j+1]:=tmp; end;\n"
    "  for i:=1 to n do writeln(s[i]);\nend.",
)

_EX_SORT_PRICE = _stub(
    "n = int(input())\nprices = list(map(int, input().split()))\nprices.sort()\nprint(' '.join(map(str, prices)))",
    "var n,i,j,t: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n"
    "  for i:=1 to n-1 do for j:=1 to n-i do if a[j]>a[j+1] then begin t:=a[j]; a[j]:=a[j+1]; a[j+1]:=t; end;\n"
    "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_SORT_SCORE = _stub(
    "n = int(input())\nscores = list(map(int, input().split()))\nscores.sort(reverse=True)\nprint(' '.join(map(str, scores)))",
    "var n,i,j,t: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n"
    "  for i:=1 to n-1 do for j:=1 to n-i do if a[j]<a[j+1] then begin t:=a[j]; a[j]:=a[j+1]; a[j+1]:=t; end;\n"
    "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_BUBBLE = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\n"
    "for i in range(n):\n    for j in range(n - i - 1):\n        if nums[j] > nums[j + 1]:\n            nums[j], nums[j + 1] = nums[j + 1], nums[j]\n"
    "print(' '.join(map(str, nums)))",
    "var n,i,j,t: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n"
    "  for i:=1 to n-1 do for j:=1 to n-i do if a[j]>a[j+1] then begin t:=a[j]; a[j]:=a[j+1]; a[j+1]:=t; end;\n"
    "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_EVENS_ODDS = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\n"
    "evens = [x for x in nums if x % 2 == 0]\nodds = [x for x in nums if x % 2 != 0]\n"
    "print(' '.join(map(str, evens + odds)))",
    "var n,i,c1,c2: integer; a,b1,b2: array[1..100] of integer;\nbegin\n  readln(n); c1:=0; c2:=0;\n"
    "  for i:=1 to n do read(a[i]);\n"
    "  for i:=1 to n do if a[i] mod 2=0 then begin c1:=c1+1; b1[c1]:=a[i]; end\n"
    "  else begin c2:=c2+1; b2[c2]:=a[i]; end;\n"
    "  for i:=1 to c1 do write(b1[i],' ');\n  for i:=1 to c2 do if i<c2 then write(b2[i],' ') else write(b2[i]);\n  writeln;\nend.",
)

_EX_TOP3 = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nnums.sort(reverse=True)\nprint(' '.join(map(str, nums[:3])))",
    "var n,i,j,t,k: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n"
    "  for i:=1 to n-1 do for j:=1 to n-i do if a[j]<a[j+1] then begin t:=a[j]; a[j]:=a[j+1]; a[j+1]:=t; end;\n"
    "  for k:=1 to 3 do if k<3 then write(a[k],' ') else write(a[k]);\n  writeln;\nend.",
)



def build_course_batch_125_174_catalog() -> list[TaskRow]:
    """Tasks 125-174: functions, recursion, search/filter/fold, sort."""
    return [
        # --- 125-140 functions (fix, translate, block cycle) ---
        translate_task(
            125, "Функция четности",
            "Напишите функцию IsEven(n), возвращающую true для чётных чисел. Исправьте ошибки в шаблоне.",
            "medium",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            code_examples=_EX_IS_EVEN,
            test_cases=[
                tc("4\n", "yes"),
                tc("7\n", "no"),
                tc("0\n", "yes"),
                tc("1\n", "no"),
                tc("100\n", "yes"),
            ],
            template="function IsEven(n: integer): boolean;\nbegin\n  IsEven:=n mod 2=1;\nend;\n"
            "var n: integer;\nbegin\n  readln(n);\n  if IsEven(n) then writeln('yes') else writeln('no');\nend.",
        ),
        translate_task(
            126, "Функция скидки",
            "Напишите функцию Discount(price, pct), возвращающую цену со скидкой. Переведите на Pascal.",
            "hard",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            code_examples=_EX_DISCOUNT,
            test_cases=[
                tc("100 10\n", "90"),
                tc("200 25\n", "150"),
                tc("50 0\n", "50"),
                tc("80 50\n", "40"),
                tc("99 1\n", "98"),
            ],
        ),
        _block_from_body(
            127, "Процедура вывода сообщения",
            "Реализуйте процедуру PrintMsg(s), выводящую строку. Соберите программу из блоков.",
            "easy",
            "procedure PrintMsg(s: string);\nbegin\n  writeln(s);\nend;\n"
            "var s: string;\nbegin\n  readln(s);\n  PrintMsg(s);\nend.",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            examples=_EX_PRINT_MSG,
            test_cases=[
                tc("hello\n", "hello"),
                tc("test\n", "test"),
                tc("123\n", "123"),
                tc("Привет\n", "Привет"),
                tc("a\n", "a"),
            ],
        ),
        translate_task(
            128, "Процедура обмена значений",
            "Напишите процедуру Swap с параметрами var для обмена двух чисел. Исправьте ошибки.",
            "medium",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            code_examples=_EX_SWAP,
            test_cases=[
                tc("3 7\n", "7 3"),
                tc("1 2\n", "2 1"),
                tc("0 0\n", "0 0"),
                tc("-1 5\n", "5 -1"),
                tc("10 10\n", "10 10"),
            ],
            template="procedure Swap(a,b: integer);\nvar t: integer;\nbegin\n  t:=a; a:=b; b:=t;\nend;\n"
            "var a,b: integer;\nbegin\n  readln(a,b);\n  Swap(a,b);\n  writeln(a,' ',b);\nend.",
        ),
        translate_task(
            129, "Функция площади",
            "Напишите функцию Area(w, h), возвращающую площадь прямоугольника. Переведите на Pascal.",
            "hard",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            code_examples=_EX_AREA,
            test_cases=[
                tc("3 4\n", "12"),
                tc("5 5\n", "25"),
                tc("1 10\n", "10"),
                tc("7 2\n", "14"),
                tc("0 5\n", "0"),
            ],
        ),
        _block_from_body(
            130, "Функция перевода температуры",
            "Реализуйте функцию CtoF(c), переводящую Цельсий в Фаренгейт. Соберите из блоков.",
            "easy",
            "function CtoF(c: integer): integer;\nbegin\n  CtoF:=c*9 div 5+32;\nend;\n"
            "var c: integer;\nbegin\n  readln(c);\n  writeln(CtoF(c));\nend.",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            examples=_EX_CTOF,
            test_cases=[
                tc("0\n", "32"),
                tc("100\n", "212"),
                tc("37\n", "99"),
                tc("-40\n", "-40"),
                tc("25\n", "77"),
            ],
        ),
        translate_task(
            131, "Функция налога",
            "Напишите функцию Tax(price, rate), возвращающую цену с налогом. Исправьте ошибки.",
            "medium",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            code_examples=_EX_TAX,
            test_cases=[
                tc("100 20\n", "120"),
                tc("50 10\n", "55"),
                tc("200 0\n", "200"),
                tc("80 25\n", "100"),
                tc("1000 5\n", "1050"),
            ],
            template="function Tax(price,rate: integer): integer;\nbegin\n  Tax:=price*rate div 100;\nend;\n"
            "var price,rate: integer;\nbegin\n  readln(price,rate);\n  writeln(Tax(price,rate));\nend.",
        ),
        translate_task(
            132, "Функция среднего массива",
            "Напишите функцию AvgArray для среднего массива чисел. Переведите на Pascal.",
            "hard",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            code_examples=_EX_AVG_ARRAY,
            test_cases=[
                tc("3\n10 20 30\n", "20.0"),
                tc("1\n5\n", "5.0"),
                tc("4\n2 3 4 5\n", "3.5"),
                tc("5\n5 5 5 5 5\n", "5.0"),
                tc("2\n1 2\n", "1.5"),
            ],
        ),
        _block_from_body(
            133, "Функция поиска элемента",
            "Реализуйте функцию Contains для проверки наличия элемента в массиве. Соберите из блоков.",
            "easy",
            "function Contains(a: array of integer; n,x: integer): boolean;\nvar i: integer;\nbegin\n"
            "  Contains:=false;\n  for i:=0 to n-1 do if a[i]=x then Contains:=true;\nend;\n"
            "var n,i,x: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
            "  for i:=0 to n-1 do read(a[i]);\n  readln(x);\n"
            "  if Contains(a,n,x) then writeln('yes') else writeln('no');\nend.",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            examples=_EX_CONTAINS,
            test_cases=[
                tc("5\n1 2 3 4 5\n3\n", "yes"),
                tc("3\n2 4 6\n5\n", "no"),
                tc("1\n10\n10\n", "yes"),
                tc("4\n0 0 0 0\n1\n", "no"),
                tc("2\n5 5\n5\n", "yes"),
            ],
        ),
        translate_task(
            134, "Функция индекса элемента",
            "Напишите функцию IndexOf, возвращающую 1-based индекс или -1. Исправьте ошибки.",
            "medium",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            code_examples=_EX_INDEX_OF,
            test_cases=[
                tc("5\n1 2 3 4 5\n4\n", "4"),
                tc("3\n2 4 6\n5\n", "-1"),
                tc("4\n7 7 7 7\n7\n", "1"),
                tc("1\n10\n10\n", "1"),
                tc("3\n1 2 3\n2\n", "2"),
            ],
            template="function IndexOf(a: array of integer; n,x: integer): integer;\nvar i: integer;\nbegin\n"
            "  IndexOf:=0;\n  for i:=0 to n-1 do if a[i]=x then IndexOf:=i;\nend;\n"
            "var n,i,x: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
            "  for i:=0 to n-1 do read(a[i]);\n  readln(x);\n  writeln(IndexOf(a,n,x));\nend.",
        ),
        translate_task(
            135, "Функция подсчета подходящих",
            "Напишите функцию CountIf, считающую элементы больше порога. Переведите на Pascal.",
            "hard",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            code_examples=_EX_COUNT_IF,
            test_cases=[
                tc("5\n1 2 3 4 5\n3\n", "2"),
                tc("3\n10 20 30\n25\n", "1"),
                tc("4\n1 1 1 1\n0\n", "4"),
                tc("2\n-1 1\n0\n", "1"),
                tc("6\n1 2 3 4 5 6\n6\n", "0"),
            ],
        ),
        _block_from_body(
            136, "Функция проверки пароля",
            "Реализуйте функцию ValidatePassword: длина >= 8 и есть цифра. Соберите из блоков.",
            "easy",
            "function ValidatePassword(p: string): boolean;\nvar i: integer; has_digit: boolean;\nbegin\n"
            "  has_digit:=false;\n  for i:=1 to length(p) do if (p[i]>='0') and (p[i]<='9') then has_digit:=true;\n"
            "  ValidatePassword:=(length(p)>=8) and has_digit;\nend;\n"
            "var p: string;\nbegin\n  readln(p);\n"
            "  if ValidatePassword(p) then writeln('valid') else writeln('invalid');\nend.",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            examples=_EX_VALIDATE_PWD,
            test_cases=[
                tc("password1\n", "valid"),
                tc("short1\n", "invalid"),
                tc("longenough\n", "invalid"),
                tc("12345678\n", "valid"),
                tc("abc\n", "invalid"),
            ],
        ),
        translate_task(
            137, "Функция форматирования имени",
            "Напишите функцию FormatName(first, last), возвращающую «Фамилия, Имя». Исправьте ошибки.",
            "medium",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            code_examples=_EX_FORMAT_NAME,
            test_cases=[
                tc("Ivan Petrov\n", "Petrov, Ivan"),
                tc("Anna Smith\n", "Smith, Anna"),
                tc("A B\n", "B, A"),
                tc("John Doe\n", "Doe, John"),
                tc("Eve Adams\n", "Adams, Eve"),
            ],
            template="function FormatName(first,last: string): string;\nbegin\n  FormatName:=first+', '+last;\nend;\n"
            "var first,last: string;\nbegin\n  readln(first,last);\n  writeln(FormatName(first,last));\nend.",
        ),
        translate_task(
            138, "Функция категории оценки",
            "Напишите функцию GradeCategory(score), возвращающую буквенную оценку. Переведите на Pascal.",
            "hard",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            code_examples=_EX_GRADE_CAT,
            test_cases=[
                tc("95\n", "A"),
                tc("85\n", "B"),
                tc("75\n", "C"),
                tc("65\n", "D"),
                tc("50\n", "F"),
            ],
        ),
        _block_from_body(
            139, "Функция расчета зарплаты",
            "Реализуйте функцию Salary(hours, rate). Соберите программу из блоков.",
            "easy",
            "function Salary(hours,rate: integer): integer;\nbegin\n  Salary:=hours*rate;\nend;\n"
            "var hours,rate: integer;\nbegin\n  readln(hours,rate);\n  writeln(Salary(hours,rate));\nend.",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            examples=_EX_SALARY,
            test_cases=[
                tc("40 100\n", "4000"),
                tc("10 50\n", "500"),
                tc("0 100\n", "0"),
                tc("8 75\n", "600"),
                tc("100 10\n", "1000"),
            ],
        ),
        translate_task(
            140, "Проверочная: калькулятор функций",
            "Напишите функцию Calc: 1 — сложение, 2 — вычитание, 3 — умножение. Исправьте ошибки.",
            "medium",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            code_examples=_EX_FUNC_CALC,
            test_cases=[
                tc("1 3 4\n", "7"),
                tc("2 10 3\n", "7"),
                tc("3 6 7\n", "42"),
                tc("1 0 0\n", "0"),
                tc("2 5 5\n", "0"),
            ],
            template="function Calc(op,a,b: integer): integer;\nbegin\n"
            "  if op=1 then Calc:=a-b\n  else if op=2 then Calc:=a+b\n  else Calc:=a*b;\nend;\n"
            "var op,a,b: integer;\nbegin\n  readln(op,a,b);\n  writeln(Calc(op,a,b));\nend.",
        ),
        # --- 141-148 recursion (translate, block, fix cycle) ---
        translate_task(
            141, "Рекурсивный факториал",
            "Напишите рекурсивную функцию Fact(n). Переведите программу на Pascal.",
            "hard",
            topics=_RECURSION_TOPICS,
            constructions=_RECURSION_CONSTRUCTIONS,
            code_examples=_EX_FACTORIAL,
            test_cases=[
                tc("5\n", "120"),
                tc("0\n", "1"),
                tc("1\n", "1"),
                tc("3\n", "6"),
                tc("7\n", "5040"),
            ],
        ),
        _block_from_body(
            142, "Рекурсивная сумма чисел",
            "Реализуйте рекурсивную функцию RecSum(n) — сумму чисел от 1 до n. Соберите из блоков.",
            "easy",
            "function RecSum(n: integer): integer;\nbegin\n  if n<=0 then RecSum:=0 else RecSum:=n+RecSum(n-1);\nend;\n"
            "var n: integer;\nbegin\n  readln(n);\n  writeln(RecSum(n));\nend.",
            topics=_RECURSION_TOPICS,
            constructions=_RECURSION_CONSTRUCTIONS,
            examples=_EX_REC_SUM,
            test_cases=[
                tc("5\n", "15"),
                tc("1\n", "1"),
                tc("0\n", "0"),
                tc("10\n", "55"),
                tc("3\n", "6"),
            ],
        ),
        translate_task(
            143, "Рекурсивный Fibonacci",
            "Напишите рекурсивную функцию Fib(n). Исправьте ошибки в шаблоне.",
            "medium",
            topics=_RECURSION_TOPICS,
            constructions=_RECURSION_CONSTRUCTIONS,
            code_examples=_EX_FIB,
            test_cases=[
                tc("5\n", "5"),
                tc("0\n", "0"),
                tc("1\n", "1"),
                tc("7\n", "13"),
                tc("10\n", "55"),
            ],
            template="function Fib(n: integer): integer;\nbegin\n"
            "  if n<=1 then Fib:=1 else Fib:=Fib(n-1)+Fib(n-2);\nend;\n"
            "var n: integer;\nbegin\n  readln(n);\n  writeln(Fib(n));\nend.",
        ),
        translate_task(
            144, "Рекурсивный обратный вывод",
            "Выведите числа от n до 1 рекурсивно через пробел. Переведите на Pascal.",
            "hard",
            topics=_RECURSION_TOPICS,
            constructions=_RECURSION_CONSTRUCTIONS,
            code_examples=_EX_REC_PRINT,
            test_cases=[
                tc("5\n", "5 4 3 2 1"),
                tc("1\n", "1"),
                tc("3\n", "3 2 1"),
                tc("7\n", "7 6 5 4 3 2 1"),
                tc("2\n", "2 1"),
            ],
        ),
        _block_from_body(
            145, "Рекурсивная сумма цифр",
            "Реализуйте рекурсивную функцию DigitSum(n). Соберите программу из блоков.",
            "easy",
            "function DigitSum(n: integer): integer;\nbegin\n"
            "  if n<10 then DigitSum:=n else DigitSum:=(n mod 10)+DigitSum(n div 10);\nend;\n"
            "var n: integer;\nbegin\n  readln(n);\n  writeln(DigitSum(n));\nend.",
            topics=_RECURSION_TOPICS,
            constructions=_RECURSION_CONSTRUCTIONS,
            examples=_EX_DIGIT_SUM,
            test_cases=[
                tc("123\n", "6"),
                tc("9\n", "9"),
                tc("1000\n", "1"),
                tc("456\n", "15"),
                tc("0\n", "0"),
            ],
        ),
        translate_task(
            146, "Рекурсивный поиск в массиве",
            "Напишите рекурсивную функцию RecSearch для поиска элемента. Исправьте ошибки.",
            "medium",
            topics=_RECURSION_TOPICS,
            constructions=_RECURSION_CONSTRUCTIONS,
            code_examples=_EX_REC_SEARCH,
            test_cases=[
                tc("5\n1 2 3 4 5\n3\n", "yes"),
                tc("3\n2 4 6\n5\n", "no"),
                tc("1\n10\n10\n", "yes"),
                tc("4\n0 0 0 0\n1\n", "no"),
                tc("2\n5 5\n5\n", "yes"),
            ],
            template="function RecSearch(a: array of integer; n,x,i: integer): boolean;\nbegin\n"
            "  if i>=n then RecSearch:=true\n  else if a[i]=x then RecSearch:=false\n  else RecSearch:=RecSearch(a,n,x,i+1);\nend;\n"
            "var n,i,x: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
            "  for i:=0 to n-1 do read(a[i]);\n  readln(x);\n"
            "  if RecSearch(a,n,x,0) then writeln('yes') else writeln('no');\nend.",
        ),
        translate_task(
            147, "Рекурсивная проверка палиндрома",
            "Проверьте палиндром рекурсивно. Переведите программу на Pascal.",
            "hard",
            topics=_RECURSION_TOPICS,
            constructions=_RECURSION_CONSTRUCTIONS,
            code_examples=_EX_REC_PAL,
            test_cases=[
                tc("level\n", "yes"),
                tc("hello\n", "no"),
                tc("a\n", "yes"),
                tc("abba\n", "yes"),
                tc("abc\n", "no"),
            ],
        ),
        _block_from_body(
            148, "Проверочная: дерево папок",
            "Рекурсивно выведите строки из 1..n звёздочек. Соберите программу из блоков.",
            "easy",
            "procedure PrintTree(depth,n: integer);\nbegin\n  if depth<=n then begin\n"
            "    writeln(StringOfChar('*',depth));\n    PrintTree(depth+1,n);\n  end;\nend;\n"
            "var n: integer;\nbegin\n  readln(n);\n  PrintTree(1,n);\nend.",
            topics=_RECURSION_TOPICS,
            constructions=_RECURSION_CONSTRUCTIONS,
            examples=_EX_FOLDER_TREE,
            test_cases=[
                tc("3\n", "*\n**\n***"),
                tc("1\n", "*"),
                tc("2\n", "*\n**"),
                tc("4\n", "*\n**\n***\n****"),
                tc("0\n", ""),
            ],
        ),
        # --- 149-166 search/filter/fold (fix, translate, block cycle) ---
        translate_task(
            149, "Линейный поиск товара",
            "Прочитайте N, список id и target. Выведите 1-based индекс или -1. Исправьте ошибки.",
            "medium",
            topics=_algo_topics(149),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            code_examples=_EX_LIN_SEARCH,
            test_cases=[
                tc("5\n10 20 30 40 50\n30\n", "3"),
                tc("3\n1 2 3\n5\n", "-1"),
                tc("1\n7\n7\n", "1"),
                tc("4\n5 5 5 5\n5\n", "1"),
                tc("2\n1 2\n3\n", "-1"),
            ],
            template="var n,i,target: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n  readln(target);\n"
            "  for i:=1 to n do if a[i]=target then begin writeln(i-1); halt; end;\n  writeln(-1);\nend.",
        ),
        translate_task(
            150, "Поиск первого дорогого товара",
            "Прочитайте N, цены и порог. Выведите первую цену > порога или -1. Переведите на Pascal.",
            "hard",
            topics=_algo_topics(150),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            code_examples=_EX_FIRST_EXP,
            test_cases=[
                tc("5\n10 20 30 40 50\n25\n", "30"),
                tc("3\n1 2 3\n10\n", "-1"),
                tc("1\n100\n50\n", "100"),
                tc("4\n5 5 5 5\n4\n", "5"),
                tc("2\n10 20\n15\n", "20"),
            ],
        ),
        _block_from_body(
            151, "Фильтрация положительных чисел",
            "Прочитайте N и N чисел, выведите только положительные. Соберите из блоков.",
            "easy",
            "var n,i,c: integer; a,b: array[1..100] of integer;\nbegin\n  readln(n); c:=0;\n"
            "  for i:=1 to n do read(a[i]);\n  for i:=1 to n do if a[i]>0 then begin c:=c+1; b[c]:=a[i]; end;\n"
            "  for i:=1 to c do if i<c then write(b[i],' ') else write(b[i]);\n  writeln;\nend.",
            topics=_algo_topics(151),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            examples=_EX_FILTER_POS,
            test_cases=[
                tc("5\n-1 2 -3 4 0\n", "2 4"),
                tc("3\n1 2 3\n", "1 2 3"),
                tc("2\n-1 -2\n", ""),
                tc("1\n0\n", ""),
                tc("4\n-5 0 7 8\n", "7 8"),
            ],
        ),
        translate_task(
            152, "Фильтрация строк по длине",
            "Прочитайте N строк и k, выведите строки длиной >= k. Исправьте ошибки.",
            "medium",
            topics=_algo_topics(152),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            code_examples=_EX_FILTER_LEN,
            test_cases=[
                tc("3\nhi\nhello\nworld\n4\n", "hello\nworld"),
                tc("2\na\nab\n2\n", "ab"),
                tc("1\ntest\n10\n", ""),
                tc("4\none\ntwo\nthree\nfour\n3\n", "one\ntwo\nthree\nfour"),
                tc("2\n\nx\n1\n", "x"),
            ],
            template="var n,i,k: integer; s: array[1..100] of string;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do readln(s[i]);\n  readln(k);\n"
            "  for i:=1 to n do if length(s[i])>k then writeln(s[i]);\nend.",
        ),
        translate_task(
            153, "Сумма подходящих элементов",
            "Прочитайте N и N чисел, выведите сумму положительных. Переведите на Pascal.",
            "hard",
            topics=_algo_topics(153),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            code_examples=_EX_SUM_MATCH,
            test_cases=[
                tc("5\n-1 2 -3 4 0\n", "6"),
                tc("3\n1 2 3\n", "6"),
                tc("2\n-1 -2\n", "0"),
                tc("4\n10 20 30 40\n", "100"),
                tc("1\n-5\n", "0"),
            ],
        ),
        _block_from_body(
            154, "Количество подходящих элементов",
            "Прочитайте N и N чисел, выведите количество положительных. Соберите из блоков.",
            "easy",
            "var n,i,c: integer; a: array[1..100] of integer;\nbegin\n  readln(n); c:=0;\n"
            "  for i:=1 to n do begin read(a[i]); if a[i]>0 then c:=c+1; end;\n  writeln(c);\nend.",
            topics=_algo_topics(154),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            examples=_EX_COUNT_MATCH,
            test_cases=[
                tc("5\n-1 2 -3 4 0\n", "2"),
                tc("3\n1 2 3\n", "3"),
                tc("2\n-1 -2\n", "0"),
                tc("4\n0 0 0 0\n", "0"),
                tc("6\n1 -1 2 -2 3 -3\n", "3"),
            ],
        ),
        translate_task(
            155, "Проверка хотя бы одного элемента",
            "Прочитайте N и N чисел. Выведите yes, если есть положительное. Исправьте ошибки.",
            "medium",
            topics=_algo_topics(155),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            code_examples=_EX_ANY,
            test_cases=[
                tc("3\n-1 0 5\n", "yes"),
                tc("2\n-1 -2\n", "no"),
                tc("1\n1\n", "yes"),
                tc("4\n0 0 0 0\n", "no"),
                tc("5\n-3 -2 -1 0 10\n", "yes"),
            ],
            template="var n,i: integer; a: array[1..100] of integer; ok: boolean;\nbegin\n  readln(n); ok:=true;\n"
            "  for i:=1 to n do begin read(a[i]); if a[i]<=0 then ok:=false; end;\n"
            "  if ok then writeln('yes') else writeln('no');\nend.",
        ),
        translate_task(
            156, "Проверка всех элементов",
            "Прочитайте N и N чисел. Выведите yes, если все положительные. Переведите на Pascal.",
            "hard",
            topics=_algo_topics(156),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            code_examples=_EX_ALL,
            test_cases=[
                tc("3\n1 2 3\n", "yes"),
                tc("2\n-1 2\n", "no"),
                tc("1\n5\n", "yes"),
                tc("4\n0 1 2 3\n", "no"),
                tc("0\n\n", "yes"),
            ],
        ),
        _block_from_body(
            157, "Преобразование цен",
            "Прочитайте N, цены и коэффициент. Умножьте все цены. Соберите из блоков.",
            "easy",
            "var n,i,f: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n  readln(f);\n"
            "  for i:=1 to n do if i<n then write(a[i]*f,' ') else write(a[i]*f);\n  writeln;\nend.",
            topics=_algo_topics(157),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            examples=_EX_MUL_PRICES,
            test_cases=[
                tc("3\n10 20 30\n2\n", "20 40 60"),
                tc("1\n5\n3\n", "15"),
                tc("2\n0 100\n1\n", "0 100"),
                tc("4\n1 2 3 4\n0\n", "0 0 0 0"),
                tc("2\n7 8\n5\n", "35 40"),
            ],
        ),
        translate_task(
            158, "Преобразование строк",
            "Прочитайте N строк и выведите каждую в верхнем регистре. Исправьте ошибки.",
            "medium",
            topics=_algo_topics(158),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            code_examples=_EX_UPPER,
            test_cases=[
                tc("2\nhello\nworld\n", "HELLO\nWORLD"),
                tc("1\nTest\n", "TEST"),
                tc("3\na\nb\nc\n", "A\nB\nC"),
                tc("1\nabc\n", "ABC"),
                tc("2\nHi\nBye\n", "HI\nBYE"),
            ],
            template="var n,i: integer; s: array[1..100] of string;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do readln(s[i]);\n  for i:=1 to n do writeln(lower(s[i]));\nend.",
        ),
        translate_task(
            159, "Сумма заказов клиента",
            "Прочитайте N и N сумм заказов, выведите общую сумму. Переведите на Pascal.",
            "hard",
            topics=_algo_topics(159),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            code_examples=_EX_ORDER_SUM,
            test_cases=[
                tc("3\n100 200 300\n", "600"),
                tc("1\n50\n", "50"),
                tc("5\n10 20 30 40 50\n", "150"),
                tc("0\n\n", "0"),
                tc("2\n0 0\n", "0"),
            ],
        ),
        _block_from_body(
            160, "Средний рейтинг",
            "Прочитайте N и N оценок, выведите среднее с одним знаком после запятой. Соберите из блоков.",
            "easy",
            "var n,i,s: integer; a: array[1..100] of integer; avg: real;\nbegin\n  readln(n); s:=0;\n"
            "  for i:=1 to n do begin read(a[i]); s:=s+a[i]; end;\n  avg:=s/n;\n  writeln(avg:0:1);\nend.",
            topics=_algo_topics(160),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            examples=_EX_AVG_RATING,
            test_cases=[
                tc("3\n5 4 3\n", "4.0"),
                tc("1\n10\n", "10.0"),
                tc("4\n2 3 4 5\n", "3.5"),
                tc("2\n1 2\n", "1.5"),
                tc("5\n5 5 5 5 5\n", "5.0"),
            ],
        ),
        translate_task(
            161, "Отбор студентов",
            "Прочитайте N и N баллов, выведите сдавших (>= 60). Исправьте ошибки.",
            "medium",
            topics=_algo_topics(161),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            code_examples=_EX_FILTER_STUDENTS,
            test_cases=[
                tc("5\n50 60 70 40 80\n", "60 70 80"),
                tc("3\n30 40 50\n", ""),
                tc("1\n60\n", "60"),
                tc("4\n100 0 60 59\n", "100 60"),
                tc("2\n61 62\n", "61 62"),
            ],
            template="var n,i,c: integer; a,b: array[1..100] of integer;\nbegin\n  readln(n); c:=0;\n"
            "  for i:=1 to n do read(a[i]);\n  for i:=1 to n do if a[i]>60 then begin c:=c+1; b[c]:=a[i]; end;\n"
            "  for i:=1 to c do if i<c then write(b[i],' ') else write(b[i]);\n  writeln;\nend.",
        ),
        translate_task(
            162, "Отбор файлов по расширению",
            "Прочитайте N имён файлов, выведите файлы с расширением .txt. Переведите на Pascal.",
            "hard",
            topics=_algo_topics(162),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            code_examples=_EX_FILTER_TXT,
            test_cases=[
                tc("3\na.txt\nb.doc\nc.txt\n", "a.txt\nc.txt"),
                tc("2\nx.txt\ny.txt\n", "x.txt\ny.txt"),
                tc("1\nreadme.md\n", ""),
                tc("4\n1.txt\n2.TXT\n3.txt\n4.doc\n", "1.txt\n3.txt"),
                tc("0\n\n", ""),
            ],
        ),
        _block_from_body(
            163, "Преобразование температур",
            "Прочитайте N температур в Цельсиях, выведите в Фаренгейтах. Соберите из блоков.",
            "easy",
            "var n,i: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n"
            "  for i:=1 to n do if i<n then write(a[i]*9 div 5+32,' ') else write(a[i]*9 div 5+32);\n  writeln;\nend.",
            topics=_algo_topics(163),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            examples=_EX_CTOF_LIST,
            test_cases=[
                tc("3\n0 100 37\n", "32 212 99"),
                tc("1\n25\n", "77"),
                tc("2\n-40 0\n", "-40 32"),
                tc("4\n1 2 3 4\n", "34 36 37 39"),
                tc("1\n100\n", "212"),
            ],
        ),
        translate_task(
            164, "Группировка результатов вручную",
            "Прочитайте N баллов, выведите количество сдавших и не сдавших через пробел. Исправьте ошибки.",
            "medium",
            topics=_algo_topics(164),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            code_examples=_EX_PASS_FAIL,
            test_cases=[
                tc("5\n50 60 70 40 80\n", "3 2"),
                tc("3\n30 40 50\n", "0 3"),
                tc("1\n60\n", "1 0"),
                tc("4\n100 0 60 59\n", "2 2"),
                tc("2\n61 62\n", "2 0"),
            ],
            template="var n,i,p: integer; a: array[1..100] of integer;\nbegin\n  readln(n); p:=0;\n"
            "  for i:=1 to n do begin read(a[i]); if a[i]>60 then p:=p+1; end;\n  writeln(p,' ',p);\nend.",
        ),
        translate_task(
            165, "Поиск лучшего предложения",
            "Прочитайте N и N значений, выведите максимальное. Переведите на Pascal.",
            "hard",
            topics=_algo_topics(165),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            code_examples=_EX_BEST_OFFER,
            test_cases=[
                tc("5\n10 20 30 40 50\n", "50"),
                tc("3\n-1 -5 -2\n", "-1"),
                tc("1\n7\n", "7"),
                tc("4\n5 5 5 5\n", "5"),
                tc("2\n100 1\n", "100"),
            ],
        ),
        _block_from_body(
            166, "Проверочная: отчет магазина",
            "Прочитайте N и N продаж. Выведите сумму, количество и максимум через пробел. Соберите из блоков.",
            "easy",
            "var n,i,s,maxv: integer; a: array[1..100] of integer;\nbegin\n  readln(n); s:=0; maxv:=0;\n"
            "  for i:=1 to n do begin read(a[i]); s:=s+a[i]; if a[i]>maxv then maxv:=a[i]; end;\n"
            "  writeln(s,' ',n,' ',maxv);\nend.",
            topics=_algo_topics(166),
            constructions=_SEARCH_BASE_CONSTRUCTIONS,
            examples=_EX_STORE_REPORT,
            test_cases=[
                tc("3\n100 200 300\n", "600 3 300"),
                tc("1\n50\n", "50 1 50"),
                tc("5\n10 20 30 40 50\n", "150 5 50"),
                tc("0\n\n", "0 0 0"),
                tc("2\n5 5\n", "10 2 5"),
            ],
        ),
        # --- 167-174 sort (fix, translate, block cycle) ---
        translate_task(
            167, "Сортировка чисел по возрастанию",
            "Прочитайте N и N чисел, отсортируйте по возрастанию пузырьком. Исправьте ошибки.",
            "medium",
            topics=_SORT_TOPICS,
            constructions=_SORT_CONSTRUCTIONS,
            code_examples=_EX_SORT_ASC,
            test_cases=[
                tc("5\n5 3 1 4 2\n", "1 2 3 4 5"),
                tc("3\n10 10 10\n", "10 10 10"),
                tc("1\n7\n", "7"),
                tc("4\n-1 0 1 2\n", "-1 0 1 2"),
                tc("2\n2 1\n", "1 2"),
            ],
            template="var n,i,j,t: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n"
            "  for i:=1 to n-1 do for j:=1 to n-i do if a[j]<a[j+1] then begin t:=a[j]; a[j]:=a[j+1]; a[j+1]:=t; end;\n"
            "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
        ),
        translate_task(
            168, "Сортировка чисел по убыванию",
            "Прочитайте N и N чисел, отсортируйте по убыванию. Переведите на Pascal.",
            "hard",
            topics=_SORT_TOPICS,
            constructions=_SORT_CONSTRUCTIONS,
            code_examples=_EX_SORT_DESC,
            test_cases=[
                tc("5\n5 3 1 4 2\n", "5 4 3 2 1"),
                tc("3\n1 2 3\n", "3 2 1"),
                tc("1\n7\n", "7"),
                tc("4\n-1 0 1 2\n", "2 1 0 -1"),
                tc("2\n2 1\n", "2 1"),
            ],
        ),
        _block_from_body(
            169, "Сортировка строк",
            "Прочитайте N строк и выведите их в лексикографическом порядке. Соберите из блоков.",
            "easy",
            "var n,i,j: integer; s,t: array[1..100] of string; tmp: string;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do readln(s[i]);\n"
            "  for i:=1 to n-1 do for j:=1 to n-i do if s[j]>s[j+1] then begin tmp:=s[j]; s[j]:=s[j+1]; s[j+1]:=tmp; end;\n"
            "  for i:=1 to n do writeln(s[i]);\nend.",
            topics=_SORT_TOPICS,
            constructions=_SORT_CONSTRUCTIONS,
            examples=_EX_SORT_STR,
            test_cases=[
                tc("3\nbanana\napple\ncherry\n", "apple\nbanana\ncherry"),
                tc("2\nb\na\n", "a\nb"),
                tc("1\nsolo\n", "solo"),
                tc("4\nd\nc\nb\na\n", "a\nb\nc\nd"),
                tc("2\naa\na\n", "a\naa"),
            ],
        ),
        translate_task(
            170, "Сортировка товаров по цене",
            "Прочитайте N и N цен, отсортируйте по возрастанию. Исправьте ошибки.",
            "medium",
            topics=_SORT_TOPICS,
            constructions=_SORT_CONSTRUCTIONS,
            code_examples=_EX_SORT_PRICE,
            test_cases=[
                tc("4\n300 100 200 50\n", "50 100 200 300"),
                tc("2\n10 5\n", "5 10"),
                tc("1\n99\n", "99"),
                tc("3\n1 1 1\n", "1 1 1"),
                tc("5\n9 8 7 6 5\n", "5 6 7 8 9"),
            ],
            template="var n,i: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n"
            "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
        ),
        translate_task(
            171, "Сортировка студентов по баллу",
            "Прочитайте N и N баллов, отсортируйте по убыванию. Переведите на Pascal.",
            "hard",
            topics=_SORT_TOPICS,
            constructions=_SORT_CONSTRUCTIONS,
            code_examples=_EX_SORT_SCORE,
            test_cases=[
                tc("4\n60 90 70 80\n", "90 80 70 60"),
                tc("3\n5 5 5\n", "5 5 5"),
                tc("1\n100\n", "100"),
                tc("2\n10 20\n", "20 10"),
                tc("5\n1 3 2 5 4\n", "5 4 3 2 1"),
            ],
        ),
        _block_from_body(
            172, "Ручная сортировка пузырьком",
            "Отсортируйте массив чисел пузырьковой сортировкой. Соберите программу из блоков.",
            "easy",
            "var n,i,j,t: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n"
            "  for i:=1 to n-1 do for j:=1 to n-i do if a[j]>a[j+1] then begin t:=a[j]; a[j]:=a[j+1]; a[j+1]:=t; end;\n"
            "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
            topics=_SORT_TOPICS,
            constructions=_SORT_CONSTRUCTIONS,
            examples=_EX_BUBBLE,
            test_cases=[
                tc("5\n5 3 1 4 2\n", "1 2 3 4 5"),
                tc("3\n10 10 10\n", "10 10 10"),
                tc("1\n7\n", "7"),
                tc("4\n-1 0 1 2\n", "-1 0 1 2"),
                tc("2\n2 1\n", "1 2"),
            ],
        ),
        translate_task(
            173, "Сортировка с условием",
            "Прочитайте N и N чисел. Сначала чётные, затем нечётные. Исправьте ошибки.",
            "medium",
            topics=_SORT_TOPICS,
            constructions=_SORT_CONSTRUCTIONS,
            code_examples=_EX_EVENS_ODDS,
            test_cases=[
                tc("5\n1 2 3 4 5\n", "2 4 1 3 5"),
                tc("4\n2 4 6 8\n", "2 4 6 8"),
                tc("3\n1 3 5\n", "1 3 5"),
                tc("2\n1 2\n", "2 1"),
                tc("6\n6 5 4 3 2 1\n", "6 4 2 5 3 1"),
            ],
            template="var n,i,c1,c2: integer; a,b1,b2: array[1..100] of integer;\nbegin\n  readln(n); c1:=0; c2:=0;\n"
            "  for i:=1 to n do read(a[i]);\n"
            "  for i:=1 to n do if a[i] mod 2=0 then begin c1:=c1+1; b1[c1]:=a[i]; end;\n"
            "  for i:=1 to c2 do if i<c2 then write(b2[i],' ') else write(b2[i]);\n  writeln;\nend.",
        ),
        translate_task(
            174, "Найти топ-3 значения",
            "Прочитайте N и N чисел, выведите 3 наибольших через пробел. Переведите на Pascal.",
            "hard",
            topics=_SORT_TOPICS,
            constructions=_SORT_CONSTRUCTIONS,
            code_examples=_EX_TOP3,
            test_cases=[
                tc("5\n1 5 3 4 2\n", "5 4 3"),
                tc("3\n10 20 30\n", "30 20 10"),
                tc("4\n7 7 7 7\n", "7 7 7"),
                tc("6\n1 2 3 4 5 6\n", "6 5 4"),
                tc("3\n-1 -2 -3\n", "-1 -2 -3"),
            ],
        ),
    ]


COURSE_BATCH_125_174_CATALOG = build_course_batch_125_174_catalog()
COURSE_BATCH_125_174_SIZE = 50
