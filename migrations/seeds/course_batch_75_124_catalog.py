"""Разделы «Вложенные циклы», «Массивы», «Динамические массивы», «Строки», «Функции» — задачи 75–124."""
from __future__ import annotations

from migrations.seeds.catalog_common import (
    block_task,
    pascal_blocks_from_body,
    tc,
    translate_task,
)

TaskRow = dict

_NESTED_LOOPS_TOPICS = ["loops", "nested_iteration"]
_NESTED_LOOPS_CONSTRUCTIONS = [
    "nested_iteration",
    "loop_control",
    "counted_loop",
    "stdin_read",
    "assignment",
    "stdout_write",
]

_ARRAYS_TOPICS = ["arrays", "indexed_sequence"]
_ARRAYS_CONSTRUCTIONS = [
    "indexed_sequence",
    "collection_iteration",
    "typed_declaration",
    "stdin_read",
    "assignment",
    "stdout_write",
]

_DYNAMIC_TOPICS = ["arrays", "dynamic_array"]
_DYNAMIC_CONSTRUCTIONS = [
    "dynamic_array",
    "collection_iteration",
    "typed_declaration",
    "stdin_read",
    "assignment",
    "stdout_write",
]

_STRINGS_TOPICS = ["strings", "string_sequence"]
_STRINGS_CONSTRUCTIONS = [
    "string_sequence",
    "assignment",
    "stdin_read",
    "stdout_write",
    "collection_iteration",
]

_FUNCTIONS_TOPICS = ["functions", "function_definition"]
_FUNCTIONS_CONSTRUCTIONS = [
    "function_definition",
    "function_invocation",
    "return_flow",
    "typed_declaration",
    "stdin_read",
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


# --- nested loops examples ---

_EX_SEARCH = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\ntarget = int(input())\n"
    "for i in range(n):\n    if nums[i] == target:\n        print(i + 1)\n        break\n"
    "else:\n    print(-1)",
    "var n,i,target: integer; nums: array[1..100] of integer;\nbegin\n"
    "  readln(n);\n  for i:=1 to n do read(nums[i]);\n  readln(target);\n"
    "  for i:=1 to n do if nums[i]=target then begin writeln(i); halt; end;\n"
    "  writeln(-1);\nend.",
)

_EX_SEATS = _stub(
    "rows, cols = map(int, input().split())\nprint(rows * cols)",
    "var rows,cols: integer;\nbegin\n  readln(rows,cols);\n  writeln(rows*cols);\nend.",
)

_EX_DIST_MATRIX = _stub(
    "n = int(input())\nfor i in range(n):\n    print(' '.join(str(abs(i - j)) for j in range(n)))",
    "var n,i,j: integer;\nbegin\n  readln(n);\n"
    "  for i:=0 to n-1 do begin\n"
    "    for j:=0 to n-1 do if j<n-1 then write(abs(i-j),' ') else write(abs(i-j));\n"
    "    writeln;\n  end;\nend.",
)

_EX_SEAT_CHECK = _stub(
    "rows, cols, row, col = map(int, input().split())\n"
    "if 1 <= row <= rows and 1 <= col <= cols:\n    print('yes')\nelse:\n    print('no')",
    "var rows,cols,row,col: integer;\nbegin\n  readln(rows,cols,row,col);\n"
    "  if (row>=1) and (row<=rows) and (col>=1) and (col<=cols) then writeln('yes')\n"
    "  else writeln('no');\nend.",
)

# --- array examples ---

_EX_FILL_ARRAY = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(' '.join(map(str, nums)))",
    "var n,i: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n"
    "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_ARRAY_SUM = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(sum(nums))",
    "var n,i,s: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n  s:=0;\n"
    "  for i:=1 to n do begin read(a[i]); s:=s+a[i]; end;\n  writeln(s);\nend.",
)

_EX_ARRAY_MAX = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(max(nums))",
    "var n,i,maxv: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n  maxv:=a[1];\n"
    "  for i:=2 to n do if a[i]>maxv then maxv:=a[i];\n  writeln(maxv);\nend.",
)

_EX_ARRAY_MIN = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(min(nums))",
    "var n,i,minv: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n  minv:=a[1];\n"
    "  for i:=2 to n do if a[i]<minv then minv:=a[i];\n  writeln(minv);\nend.",
)

_EX_MAX_INDEX = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(nums.index(max(nums)) + 1)",
    "var n,i,idx,maxv: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n  maxv:=a[1]; idx:=1;\n"
    "  for i:=2 to n do if a[i]>maxv then begin maxv:=a[i]; idx:=i; end;\n  writeln(idx);\nend.",
)

_EX_COUNT_EVEN = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(sum(1 for x in nums if x % 2 == 0))",
    "var n,i,c: integer; a: array[1..100] of integer;\nbegin\n  readln(n); c:=0;\n"
    "  for i:=1 to n do begin read(a[i]); if a[i] mod 2=0 then c:=c+1; end;\n  writeln(c);\nend.",
)

_EX_SUM_POS = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(sum(x for x in nums if x > 0))",
    "var n,i,s: integer; a: array[1..100] of integer;\nbegin\n  readln(n); s:=0;\n"
    "  for i:=1 to n do begin read(a[i]); if a[i]>0 then s:=s+a[i]; end;\n  writeln(s);\nend.",
)

_EX_ZERO_NEG = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\n"
    "nums = [0 if x < 0 else x for x in nums]\nprint(' '.join(map(str, nums)))",
    "var n,i: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do begin read(a[i]); if a[i]<0 then a[i]:=0; end;\n"
    "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_CONTAINS = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nx = int(input())\n"
    "print('yes' if x in nums else 'no')",
    "var n,i,x: integer; a: array[1..100] of integer; found: boolean;\nbegin\n"
    "  readln(n);\n  for i:=1 to n do read(a[i]);\n  readln(x);\n  found:=false;\n"
    "  for i:=1 to n do if a[i]=x then found:=true;\n"
    "  if found then writeln('yes') else writeln('no');\nend.",
)

_EX_FIRST_INDEX = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nx = int(input())\n"
    "print(next((i + 1 for i, v in enumerate(nums) if v == x), -1))",
    "var n,i,x,idx: integer; a: array[1..100] of integer; found: boolean;\nbegin\n"
    "  readln(n);\n  for i:=1 to n do read(a[i]);\n  readln(x);\n"
    "  found:=false; idx:=-1;\n"
    "  for i:=1 to n do if (not found) and (a[i]=x) then begin found:=true; idx:=i; end;\n"
    "  writeln(idx);\nend.",
)

_EX_COPY_ARRAY = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\ncopy = nums[:]\nprint(' '.join(map(str, copy)))",
    "var n,i: integer; a,b: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n  for i:=1 to n do b[i]:=a[i];\n"
    "  for i:=1 to n do if i<n then write(b[i],' ') else write(b[i]);\n  writeln;\nend.",
)

_EX_REVERSE_ARRAY = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(' '.join(map(str, reversed(nums))))",
    "var n,i: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n"
    "  for i:=n downto 1 do if i>1 then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_ROTATE_RIGHT = _stub(
    "n = int(input())\na = list(map(int, input().split()))\nk = int(input())\n"
    "if n:\n    k %= n\n    a = a[-k:] + a[:-k]\nprint(' '.join(map(str, a)))",
    "var n,i,k,tmp: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n  readln(k);\n  k:=k mod n;\n"
    "  for i:=1 to k do begin tmp:=a[n]; for i:=n downto 2 do a[i]:=a[i-1]; a[1]:=tmp; end;\n"
    "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_COMPARE_ARRAYS = _stub(
    "n = int(input())\na = list(map(int, input().split()))\nb = list(map(int, input().split()))\n"
    "print('equal' if a == b else 'different')",
    "var n,i: integer; a,b: array[1..100] of integer; same: boolean;\nbegin\n"
    "  readln(n);\n  for i:=1 to n do read(a[i]);\n  for i:=1 to n do read(b[i]);\n"
    "  same:=true;\n  for i:=1 to n do if a[i]<>b[i] then same:=false;\n"
    "  if same then writeln('equal') else writeln('different');\nend.",
)

_EX_MERGE_ARRAYS = _stub(
    "n = int(input())\na = list(map(int, input().split()))\nm = int(input())\nb = list(map(int, input().split()))\n"
    "print(' '.join(map(str, a + b)))",
    "var n,m,i: integer; a,b: array[1..100] of integer;\nbegin\n"
    "  readln(n);\n  for i:=1 to n do read(a[i]);\n  readln(m);\n  for i:=1 to m do read(b[i]);\n"
    "  for i:=1 to n do write(a[i],' ');\n"
    "  for i:=1 to m do if i<m then write(b[i],' ') else write(b[i]);\n  writeln;\nend.",
)

_EX_SALES_STATS = _stub(
    "n = int(input())\nsales = list(map(int, input().split()))\npos = [x for x in sales if x > 0]\n"
    "if pos:\n    print(sum(pos), max(pos), len(pos))\nelse:\n    print(0, 0, 0)",
    "var n,i,s,maxv,c: integer; sales: array[1..100] of integer;\nbegin\n  readln(n); s:=0; maxv:=0; c:=0;\n"
    "  for i:=1 to n do begin read(sales[i]);\n"
    "    if sales[i]>0 then begin s:=s+sales[i]; c:=c+1; if sales[i]>maxv then maxv:=sales[i]; end; end;\n"
    "  writeln(s,' ',maxv,' ',c);\nend.",
)

# --- dynamic array examples ---

_EX_DYN_FILL = _stub(
    "n = int(input())\nvals = list(map(int, input().split()))\nprint(' '.join(map(str, vals)))",
    "var n,i: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
    "  for i:=0 to n-1 do read(a[i]);\n"
    "  for i:=0 to n-1 do if i<n-1 then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_DYN_DROP_LAST = _stub(
    "n = int(input())\nvals = list(map(int, input().split()))\nprint(' '.join(map(str, vals[:-1])))",
    "var n,i: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
    "  for i:=0 to n-1 do read(a[i]);\n"
    "  for i:=0 to n-2 do if i<n-2 then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_POSITIVES = _stub(
    "pos = []\nwhile True:\n    x = int(input())\n    if x == 0:\n        break\n    if x > 0:\n        pos.append(x)\nprint(' '.join(map(str, pos)))",
    "var x: integer; a: array of integer; n,i: integer;\nbegin\n  n:=0; SetLength(a,0);\n"
    "  readln(x);\n  while x<>0 do begin\n"
    "    if x>0 then begin SetLength(a,n+1); a[n]:=x; n:=n+1; end;\n    readln(x);\n  end;\n"
    "  for i:=0 to n-1 do if i<n-1 then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_SHOPPING = _stub(
    "total = 0\nwhile True:\n    price = int(input())\n    if price == 0:\n        break\n    total += price\nprint(total)",
    "var price,total: integer;\nbegin\n  total:=0;\n  readln(price);\n"
    "  while price<>0 do begin total:=total+price; readln(price); end;\n  writeln(total);\nend.",
)

_EX_GRADES_AVG = _stub(
    "n = int(input())\ngrades = list(map(int, input().split()))\nprint(f'{sum(grades) / n:.1f}')",
    "var n,i,s: integer; g: array of integer; avg: real;\nbegin\n  readln(n); SetLength(g,n); s:=0;\n"
    "  for i:=0 to n-1 do begin read(g[i]); s:=s+g[i]; end;\n"
    "  avg:=s/n; writeln(avg:0:1);\nend.",
)

_EX_FIND_LIST = _stub(
    "n = int(input())\nvals = list(map(int, input().split()))\nx = int(input())\n"
    "print('yes' if x in vals else 'no')",
    "var n,i,x: integer; a: array of integer; found: boolean;\nbegin\n"
    "  readln(n); SetLength(a,n);\n  for i:=0 to n-1 do read(a[i]);\n  readln(x);\n"
    "  found:=false;\n  for i:=0 to n-1 do if a[i]=x then found:=true;\n"
    "  if found then writeln('yes') else writeln('no');\nend.",
)

_EX_FILTER_ZEROS = _stub(
    "n = int(input())\nvals = [x for x in map(int, input().split()) if x != 0]\nprint(' '.join(map(str, vals)))",
    "var n,i,c: integer; a,b: array of integer;\nbegin\n  readln(n); SetLength(a,n); c:=0;\n"
    "  for i:=0 to n-1 do read(a[i]);\n  for i:=0 to n-1 do if a[i]<>0 then begin SetLength(b,c+1); b[c]:=a[i]; c:=c+1; end;\n"
    "  for i:=0 to c-1 do if i<c-1 then write(b[i],' ') else write(b[i]);\n  writeln;\nend.",
)

_EX_SPLIT_LIST = _stub(
    "n = int(input())\nvals = list(map(int, input().split()))\nth = int(input())\n"
    "low = [x for x in vals if x <= th]\nhigh = [x for x in vals if x > th]\n"
    "print(' '.join(map(str, low)))\nprint(' '.join(map(str, high)))",
    "var n,i,th: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
    "  for i:=0 to n-1 do read(a[i]);\n  readln(th);\n"
    "  for i:=0 to n-1 do if a[i]<=th then write(a[i],' '); writeln;\n"
    "  for i:=0 to n-1 do if a[i]>th then write(a[i],' '); writeln;\nend.",
)

_EX_UNIQUE = _stub(
    "n = int(input())\nvals = list(map(int, input().split()))\nseen = set()\nuniq = []\n"
    "for x in vals:\n    if x not in seen:\n        seen.add(x)\n        uniq.append(x)\nprint(' '.join(map(str, uniq)))",
    "var n,i,j,c: integer; a,b: array of integer; dup: boolean;\nbegin\n  readln(n); SetLength(a,n); c:=0;\n"
    "  for i:=0 to n-1 do read(a[i]);\n"
    "  for i:=0 to n-1 do begin dup:=false;\n"
    "    for j:=0 to c-1 do if b[j]=a[i] then dup:=true;\n"
    "    if not dup then begin SetLength(b,c+1); b[c]:=a[i]; c:=c+1; end; end;\n"
    "  for i:=0 to c-1 do if i<c-1 then write(b[i],' ') else write(b[i]);\n  writeln;\nend.",
)

_EX_LIMIT5 = _stub(
    "vals = []\nwhile True:\n    x = int(input())\n    if x == -1:\n        break\n    if len(vals) < 5:\n        vals.append(x)\nprint(' '.join(map(str, vals)))",
    "var x: integer; a: array of integer; n,i: integer;\nbegin\n  n:=0; SetLength(a,0);\n"
    "  readln(x);\n  while x<>-1 do begin\n"
    "    if n<5 then begin SetLength(a,n+1); a[n]:=x; n:=n+1; end;\n    readln(x);\n  end;\n"
    "  for i:=0 to n-1 do if i<n-1 then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_APPEND_LISTS = _stub(
    "n = int(input())\na = list(map(int, input().split()))\nm = int(input())\nb = list(map(int, input().split()))\n"
    "a.extend(b)\nprint(' '.join(map(str, a)))",
    "var n,m,i: integer; a,b: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
    "  for i:=0 to n-1 do read(a[i]);\n  readln(m); SetLength(b,m);\n"
    "  for i:=0 to m-1 do read(b[i]);\n"
    "  SetLength(a,n+m);\n  for i:=0 to m-1 do a[n+i]:=b[i];\n"
    "  for i:=0 to n+m-1 do if i<n+m-1 then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
)

_EX_QUEUE = _stub(
    "from collections import deque\nq = deque()\nwhile True:\n    cmd = int(input())\n    if cmd == 0:\n        break\n    if cmd == 1:\n        q.append(int(input()))\n    elif cmd == 2:\n        print(q.popleft() if q else -1)",
    "var cmd,x: integer; q: array of integer; head,tail: integer;\nbegin\n  SetLength(q,100); head:=0; tail:=0;\n"
    "  readln(cmd);\n  while cmd<>0 do begin\n"
    "    if cmd=1 then begin readln(x); q[tail]:=x; tail:=tail+1; end\n"
    "    else if cmd=2 then if head<tail then begin writeln(q[head]); head:=head+1; end else writeln(-1);\n"
    "    readln(cmd);\n  end;\nend.",
)

_EX_REVERSE_STRINGS = _stub(
    "n = int(input())\nlines = [input() for _ in range(n)]\nfor s in reversed(lines):\n    print(s)",
    "var n,i: integer; s: array[1..100] of string;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do readln(s[i]);\n"
    "  for i:=n downto 1 do writeln(s[i]);\nend.",
)

_EX_CART = _stub(
    "count = 0\ntotal = 0\nwhile True:\n    price = int(input())\n    if price == 0:\n        break\n    count += 1\n    total += price\nprint(count, total)",
    "var price,count,total: integer;\nbegin\n  count:=0; total:=0;\n  readln(price);\n"
    "  while price<>0 do begin count:=count+1; total:=total+price; readln(price); end;\n"
    "  writeln(count,' ',total);\nend.",
)

# --- string examples ---

_EX_STRLEN = _stub(
    "s = input()\nprint(len(s))",
    "var s: string;\nbegin\n  readln(s);\n  writeln(length(s));\nend.",
)

_EX_FIRST_LAST = _stub(
    "s = input()\nprint(s[0], s[-1])",
    "var s: string;\nbegin\n  readln(s);\n  if length(s)>0 then writeln(s[1],' ',s[length(s)]);\nend.",
)

_EX_COUNT_CHAR = _stub(
    "s = input()\nch = input().strip()\nc = sum(1 for c in s if c == ch)\nprint(c)",
    "var s,ch: string; i,c: integer;\nbegin\n  readln(s); readln(ch);\n  c:=0;\n  for i:=1 to length(s) do if s[i]=ch then c:=c+1;\n  writeln(c);\nend.",
)

_EX_CHAR_PRESENT = _stub(
    "s = input()\nch = input().strip()\nprint('yes' if ch in s else 'no')",
    "var s,ch: string; i: integer; found: boolean;\nbegin\n  readln(s); readln(ch);\n  found:=false;\n  for i:=1 to length(s) do if s[i]=ch then found:=true;\n  if found then writeln('yes') else writeln('no');\nend.",
)

_EX_COUNT_DIGITS = _stub(
    "s = input()\nprint(sum(1 for c in s if c.isdigit()))",
    "var s: string; i,c: integer;\nbegin\n  readln(s); c:=0;\n"
    "  for i:=1 to length(s) do if (s[i]>='0') and (s[i]<='9') then c:=c+1;\n  writeln(c);\nend.",
)

_EX_NO_SPACES = _stub(
    "s = input()\nprint(s.replace(' ', ''))",
    "var s: string; i: integer; r: string;\nbegin\n  readln(s); r:='';\n"
    "  for i:=1 to length(s) do if s[i]<>' ' then r:=r+s[i];\n  writeln(r);\nend.",
)

_EX_REVERSE_STR = _stub(
    "s = input()\nprint(s[::-1])",
    "var s: string; i: integer; r: string;\nbegin\n  readln(s); r:='';\n"
    "  for i:=length(s) downto 1 do r:=r+s[i];\n  writeln(r);\nend.",
)

_EX_PALINDROME = _stub(
    "s = input()\nprint('yes' if s == s[::-1] else 'no')",
    "var s: string; i: integer; ok: boolean;\nbegin\n  readln(s); ok:=true;\n"
    "  for i:=1 to length(s) div 2 do if s[i]<>s[length(s)-i+1] then ok:=false;\n"
    "  if ok then writeln('yes') else writeln('no');\nend.",
)

_EX_PASSWORD = _stub(
    "p = input()\nhas_digit = any(c.isdigit() for c in p)\n"
    "print('strong' if len(p) >= 8 and has_digit else 'weak')",
    "var p: string; i: integer; has_digit: boolean;\nbegin\n  readln(p); has_digit:=false;\n"
    "  for i:=1 to length(p) do if (p[i]>='0') and (p[i]<='9') then has_digit:=true;\n"
    "  if (length(p)>=8) and has_digit then writeln('strong') else writeln('weak');\nend.",
)

_EX_WORD_COUNT = _stub(
    "s = input().strip()\nprint(len(s.split()) if s else 0)",
    "var s: string; i,c: integer; in_word: boolean;\nbegin\n  readln(s); c:=0; in_word:=false;\n"
    "  for i:=1 to length(s) do\n"
    "    if s[i]<>' ' then begin if not in_word then begin c:=c+1; in_word:=true; end; end\n"
    "    else in_word:=false;\n  writeln(c);\nend.",
)

_EX_LONGEST_WORD = _stub(
    "words = input().split()\nprint(max(words, key=len) if words else '')",
    "var s,word,best: string; i: integer; len,best_len: integer;\nbegin\n  readln(s); best:=''; best_len:=0;\n"
    "  word:='';\n  for i:=1 to length(s)+1 do begin\n"
    "    if (i<=length(s)) and (s[i]<>' ') then word:=word+s[i]\n"
    "    else begin len:=length(word); if len>best_len then begin best:=word; best_len:=len; end; word:=''; end; end;\n"
    "  writeln(best);\nend.",
)

_EX_REPLACE = _stub(
    "s = input()\nold = input().strip()\nnew = input().strip()\nprint(s.replace(old, new))",
    "var s,old,new,r: string; i: integer;\nbegin\n  readln(s); readln(old); readln(new); r:='';\n"
    "  i:=1;\n  while i<=length(s) do if copy(s,i,length(old))=old then begin r:=r+new; i:=i+length(old); end\n"
    "  else begin r:=r+s[i]; i:=i+1; end;\n  writeln(r);\nend.",
)

_EX_LOGIN = _stub(
    "first, last = input().split()\nprint((first[0] + last).lower())",
    "var first,last,login: string;\nbegin\n  readln(first,last);\n"
    "  login:=lower(first[1])+lower(last);\n  writeln(login);\nend.",
)

_EX_FORM_VALID = _stub(
    "name = input().strip()\nage = int(input())\n"
    "print('valid' if name and 1 <= age <= 120 else 'invalid')",
    "var name: string; age: integer;\nbegin\n  readln(name); readln(age);\n"
    "  if (length(name)>0) and (age>=1) and (age<=120) then writeln('valid') else writeln('invalid');\nend.",
)

# --- function examples ---

_EX_FUNC_SUM = _stub(
    "def sum_ab(a, b):\n    return a + b\na, b = map(int, input().split())\nprint(sum_ab(a, b))",
    "function Sum(a,b: integer): integer;\nbegin\n  Sum:=a+b;\nend;\n"
    "var a,b: integer;\nbegin\n  readln(a,b);\n  writeln(Sum(a,b));\nend.",
)

_EX_FUNC_MAX = _stub(
    "def max_ab(a, b):\n    return a if a > b else b\na, b = map(int, input().split())\nprint(max_ab(a, b))",
    "function Max(a,b: integer): integer;\nbegin\n  if a>b then Max:=a else Max:=b;\nend;\n"
    "var a,b: integer;\nbegin\n  readln(a,b);\n  writeln(Max(a,b));\nend.",
)


def build_course_batch_75_124_catalog() -> list[TaskRow]:
    """Tasks 75-124: nested loops, arrays, dynamic arrays, strings, functions."""
    return [
        # --- 75-78 nested loops (translate, block, fix, translate) ---
        translate_task(
            75, "Ранний выход из поиска",
            "Прочитайте N, N чисел и target. Выведите 1-based индекс первого вхождения target или -1. Переведите на Pascal.",
            "hard",
            topics=_NESTED_LOOPS_TOPICS,
            constructions=_NESTED_LOOPS_CONSTRUCTIONS,
            code_examples=_EX_SEARCH,
            test_cases=[
                tc("5\n1 2 3 4 5\n4\n", "4"),
                tc("3\n2 4 6\n5\n", "-1"),
                tc("4\n7 7 7 7\n7\n", "1"),
                tc("1\n10\n10\n", "1"),
                tc("3\n1 2 3\n1\n", "1"),
            ],
        ),
        _block_from_body(
            76, "Подсчёт мест в зале",
            "Прочитайте число рядов и мест в ряду, выведите общее количество мест. Соберите из блоков.",
            "easy",
            "var rows,cols: integer;\nbegin\n  readln(rows,cols);\n  writeln(rows*cols);\nend.",
            topics=_NESTED_LOOPS_TOPICS,
            constructions=_NESTED_LOOPS_CONSTRUCTIONS,
            examples=_EX_SEATS,
            test_cases=[tc("5 10\n", "50"), tc("3 4\n", "12"), tc("1 1\n", "1"), tc("10 20\n", "200"), tc("2 5\n", "10")],
        ),
        translate_task(
            77, "Матрица расстояний",
            "Прочитайте n и выведите n×n матрицу |i-j| для i,j от 0 до n-1. Исправьте ошибки.",
            "medium",
            topics=_NESTED_LOOPS_TOPICS,
            constructions=_NESTED_LOOPS_CONSTRUCTIONS,
            code_examples=_EX_DIST_MATRIX,
            test_cases=[
                tc("3\n", "0 1 2\n1 0 1\n2 1 0"),
                tc("1\n", "0"),
                tc("2\n", "0 1\n1 0"),
                tc("4\n", "0 1 2 3\n1 0 1 2\n2 1 0 1\n3 2 1 0"),
                tc("0\n", ""),
            ],
            template="var n,i,j: integer;\nbegin\n  readln(n);\n"
            "  for i:=0 to n-1 do begin\n"
            "    for j:=0 to n-1 do if j<n-1 then write(i+j,' ') else write(i+j);\n"
            "    writeln;\n  end;\nend.",
        ),
        translate_task(
            78, "Проверка схемы рассадки",
            "Прочитайте rows, cols, row, col. Выведите yes, если место существует, иначе no. Переведите на Pascal.",
            "hard",
            topics=_NESTED_LOOPS_TOPICS,
            constructions=_NESTED_LOOPS_CONSTRUCTIONS,
            code_examples=_EX_SEAT_CHECK,
            test_cases=[
                tc("5 10\n3 7\n", "yes"),
                tc("5 10\n6 1\n", "no"),
                tc("3 3\n1 1\n", "yes"),
                tc("2 4\n2 5\n", "no"),
                tc("1 1\n1 1\n", "yes"),
            ],
        ),
        # --- 79-94 arrays (block, fix, translate cycle) ---
        _block_from_body(
            79, "Заполнить массив числами",
            "Прочитайте N и N целых чисел, выведите их через пробел. Соберите из блоков.",
            "easy",
            "var n,i: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n"
            "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            examples=_EX_FILL_ARRAY,
            test_cases=[
                tc("3\n1 2 3\n", "1 2 3"),
                tc("1\n42\n", "42"),
                tc("5\n10 20 30 40 50\n", "10 20 30 40 50"),
                tc("2\n-1 1\n", "-1 1"),
                tc("4\n0 0 0 0\n", "0 0 0 0"),
            ],
        ),
        translate_task(
            80, "Сумма массива",
            "Прочитайте N и N чисел, выведите их сумму. Исправьте ошибки.",
            "medium",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            code_examples=_EX_ARRAY_SUM,
            test_cases=[
                tc("3\n1 2 3\n", "6"),
                tc("5\n1 2 3 4 5\n", "15"),
                tc("1\n10\n", "10"),
                tc("4\n-1 -2 3 4\n", "4"),
                tc("0\n", "0"),
            ],
            template="var n,i,s: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n  s:=0;\n"
            "  for i:=1 to n do begin read(a[i]); s:=s-a[i]; end;\n  writeln(s);\nend.",
        ),
        translate_task(
            81, "Максимум массива",
            "Прочитайте N и N чисел, выведите максимальный элемент. Переведите на Pascal.",
            "hard",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            code_examples=_EX_ARRAY_MAX,
            test_cases=[
                tc("5\n1 9 3 4 2\n", "9"),
                tc("3\n-1 -5 -2\n", "-1"),
                tc("1\n42\n", "42"),
                tc("4\n0 10 2 7\n", "10"),
                tc("2\n5 5\n", "5"),
            ],
        ),
        _block_from_body(
            82, "Минимум массива",
            "Прочитайте N и N чисел, выведите минимальный элемент. Соберите из блоков.",
            "easy",
            "var n,i,minv: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n  minv:=a[1];\n"
            "  for i:=2 to n do if a[i]<minv then minv:=a[i];\n  writeln(minv);\nend.",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            examples=_EX_ARRAY_MIN,
            test_cases=[
                tc("3\n-1 -5 -2\n", "-5"),
                tc("5\n1 2 3 4 5\n", "1"),
                tc("1\n7\n", "7"),
                tc("4\n0 10 2 7\n", "0"),
                tc("2\n5 5\n", "5"),
            ],
        ),
        translate_task(
            83, "Индекс максимума",
            "Прочитайте N и N чисел, выведите 1-based индекс максимального элемента. Исправьте ошибки.",
            "medium",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            code_examples=_EX_MAX_INDEX,
            test_cases=[
                tc("5\n1 9 3 4 2\n", "2"),
                tc("3\n5 5 1\n", "1"),
                tc("1\n10\n", "1"),
                tc("4\n0 10 2 7\n", "2"),
                tc("3\n-1 -5 -2\n", "1"),
            ],
            template="var n,i,idx,maxv: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n  maxv:=a[1]; idx:=0;\n"
            "  for i:=2 to n do if a[i]>maxv then begin maxv:=a[i]; idx:=i; end;\n  writeln(idx);\nend.",
        ),
        translate_task(
            84, "Количество чётных элементов",
            "Прочитайте N и N чисел, выведите количество чётных. Переведите на Pascal.",
            "hard",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            code_examples=_EX_COUNT_EVEN,
            test_cases=[
                tc("5\n1 2 3 4 5\n", "2"),
                tc("3\n2 4 6\n", "3"),
                tc("4\n1 3 5 7\n", "0"),
                tc("1\n0\n", "1"),
                tc("6\n1 2 3 4 5 6\n", "3"),
            ],
        ),
        _block_from_body(
            85, "Сумма положительных элементов",
            "Прочитайте N и N чисел, выведите сумму положительных. Соберите из блоков.",
            "easy",
            "var n,i,s: integer; a: array[1..100] of integer;\nbegin\n  readln(n); s:=0;\n"
            "  for i:=1 to n do begin read(a[i]); if a[i]>0 then s:=s+a[i]; end;\n  writeln(s);\nend.",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            examples=_EX_SUM_POS,
            test_cases=[
                tc("5\n1 -2 3 0 5\n", "9"),
                tc("3\n0 0 0\n", "0"),
                tc("1\n-1\n", "0"),
                tc("4\n1 2 3 4\n", "10"),
                tc("2\n-5 10\n", "10"),
            ],
        ),
        translate_task(
            86, "Замена отрицательных на ноль",
            "Прочитайте N и N чисел, замените отрицательные на 0 и выведите массив. Исправьте ошибки.",
            "medium",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            code_examples=_EX_ZERO_NEG,
            test_cases=[
                tc("4\n-1 2 -3 4\n", "0 2 0 4"),
                tc("3\n1 2 3\n", "1 2 3"),
                tc("2\n-5 -10\n", "0 0"),
                tc("1\n0\n", "0"),
                tc("5\n-1 -2 0 3 -4\n", "0 0 0 3 0"),
            ],
            template="var n,i: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do begin read(a[i]); if a[i]<0 then a[i]:=1; end;\n"
            "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
        ),
        translate_task(
            87, "Проверить наличие числа",
            "Прочитайте N, массив и x. Выведите yes или no. Переведите на Pascal.",
            "hard",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            code_examples=_EX_CONTAINS,
            test_cases=[
                tc("5\n1 2 3 4 5\n3\n", "yes"),
                tc("3\n2 4 6\n5\n", "no"),
                tc("1\n10\n10\n", "yes"),
                tc("4\n0 0 0 0\n1\n", "no"),
                tc("2\n5 5\n5\n", "yes"),
            ],
        ),
        _block_from_body(
            88, "Найти первое вхождение",
            "Прочитайте N, массив и x. Выведите 1-based индекс или -1. Соберите из блоков.",
            "easy",
            "var n,i,x,idx: integer; a: array[1..100] of integer; found: boolean;\nbegin\n"
            "  readln(n);\n  for i:=1 to n do read(a[i]);\n  readln(x);\n"
            "  found:=false; idx:=-1;\n"
            "  for i:=1 to n do if (not found) and (a[i]=x) then begin found:=true; idx:=i; end;\n"
            "  writeln(idx);\nend.",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            examples=_EX_FIRST_INDEX,
            test_cases=[
                tc("5\n1 2 3 4 5\n4\n", "4"),
                tc("3\n2 4 6\n5\n", "-1"),
                tc("4\n7 7 7 7\n7\n", "1"),
                tc("1\n10\n5\n", "-1"),
                tc("3\n1 2 3\n2\n", "2"),
            ],
        ),
        translate_task(
            89, "Скопировать массив",
            "Прочитайте N и N чисел, выведите копию массива. Исправьте ошибки.",
            "medium",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            code_examples=_EX_COPY_ARRAY,
            test_cases=[
                tc("3\n1 2 3\n", "1 2 3"),
                tc("1\n42\n", "42"),
                tc("4\n10 20 30 40\n", "10 20 30 40"),
                tc("2\n-1 1\n", "-1 1"),
                tc("5\n1 1 1 1 1\n", "1 1 1 1 1"),
            ],
            template="var n,i: integer; a,b: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n  for i:=1 to n do b[i]:=a[n-i+1];\n"
            "  for i:=1 to n do if i<n then write(b[i],' ') else write(b[i]);\n  writeln;\nend.",
        ),
        translate_task(
            90, "Развернуть массив",
            "Прочитайте N и N чисел, выведите элементы в обратном порядке. Переведите на Pascal.",
            "hard",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            code_examples=_EX_REVERSE_ARRAY,
            test_cases=[
                tc("3\n1 2 3\n", "3 2 1"),
                tc("1\n42\n", "42"),
                tc("4\n10 20 30 40\n", "40 30 20 10"),
                tc("2\n-1 1\n", "1 -1"),
                tc("5\n1 2 3 4 5\n", "5 4 3 2 1"),
            ],
        ),
        _block_from_body(
            91, "Сдвиг массива вправо",
            "Прочитайте N, массив и k. Сдвиньте массив вправо на k и выведите результат. Соберите из блоков.",
            "easy",
            "var n,i,k,tmp: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n  readln(k);\n  k:=k mod n;\n"
            "  for i:=1 to k do begin tmp:=a[n]; for i:=n downto 2 do a[i]:=a[i-1]; a[1]:=tmp; end;\n"
            "  for i:=1 to n do if i<n then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            examples=_EX_ROTATE_RIGHT,
            test_cases=[
                tc("5\n1 2 3 4 5\n2\n", "4 5 1 2 3"),
                tc("3\n1 2 3\n1\n", "3 1 2"),
                tc("4\n10 20 30 40\n4\n", "10 20 30 40"),
                tc("1\n7\n3\n", "7"),
                tc("3\n1 2 3\n0\n", "1 2 3"),
            ],
        ),
        translate_task(
            92, "Сравнить два массива",
            "Прочитайте N и два массива по N элементов. Выведите equal или different. Исправьте ошибки.",
            "medium",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            code_examples=_EX_COMPARE_ARRAYS,
            test_cases=[
                tc("3\n1 2 3\n1 2 3\n", "equal"),
                tc("3\n1 2 3\n1 2 4\n", "different"),
                tc("1\n5\n1 5\n", "different"),
                tc("2\n0 0\n0 0\n", "equal"),
                tc("4\n1 1 1 1\n1 1 1 2\n", "different"),
            ],
            template="var n,i: integer; a,b: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n  for i:=1 to n do read(b[i]);\n"
            "  if a[1]=b[1] then writeln('equal') else writeln('different');\nend.",
        ),
        translate_task(
            93, "Объединить два массива",
            "Прочитайте N, первый массив, M и второй массив. Выведите объединение. Переведите на Pascal.",
            "hard",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            code_examples=_EX_MERGE_ARRAYS,
            test_cases=[
                tc("2\n1 2\n3\n3 4 5\n", "1 2 3 4 5"),
                tc("1\n10\n1\n20\n", "10 20"),
                tc("0\n1\n5\n", "5"),
                tc("3\n1 2 3\n0\n", "1 2 3"),
                tc("2\n-1 1\n2\n0 0\n", "-1 1 0 0"),
            ],
        ),
        _block_from_body(
            94, "Проверочная: статистика продаж",
            "Прочитайте N и массив продаж. Выведите сумму, максимум и количество продаж > 0 через пробел. Соберите из блоков.",
            "easy",
            "var n,i,s,maxv,c: integer; sales: array[1..100] of integer;\nbegin\n  readln(n); s:=0; maxv:=0; c:=0;\n"
            "  for i:=1 to n do begin read(sales[i]);\n"
            "    if sales[i]>0 then begin s:=s+sales[i]; c:=c+1; if sales[i]>maxv then maxv:=sales[i]; end; end;\n"
            "  writeln(s,' ',maxv,' ',c);\nend.",
            topics=_ARRAYS_TOPICS,
            constructions=_ARRAYS_CONSTRUCTIONS,
            examples=_EX_SALES_STATS,
            test_cases=[
                tc("5\n100 0 -50 200 150\n", "450 200 3"),
                tc("3\n0 0 0\n", "0 0 0"),
                tc("1\n50\n", "50 50 1"),
                tc("4\n10 20 30 40\n", "100 40 4"),
                tc("2\n-1 -2\n", "0 0 0"),
            ],
        ),
        # --- 95-108 dynamic arrays (fix, translate, block cycle) ---
        translate_task(
            95, "Добавить элементы в список",
            "Прочитайте N и N значений, выведите их через пробел. Исправьте ошибки.",
            "medium",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            code_examples=_EX_DYN_FILL,
            test_cases=[
                tc("3\n1 2 3\n", "1 2 3"),
                tc("1\n42\n", "42"),
                tc("5\n10 20 30 40 50\n", "10 20 30 40 50"),
                tc("2\n-1 1\n", "-1 1"),
                tc("4\n0 0 0 0\n", "0 0 0 0"),
            ],
            template="var n,i: integer; a: array of integer;\nbegin\n  readln(n);\n"
            "  for i:=0 to n-1 do read(a[i]);\n"
            "  for i:=0 to n-1 do if i<n-1 then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
        ),
        translate_task(
            96, "Удалить последнее значение",
            "Прочитайте N и N значений, выведите первые N-1 через пробел. Переведите на Pascal.",
            "hard",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            code_examples=_EX_DYN_DROP_LAST,
            test_cases=[
                tc("3\n1 2 3\n", "1 2"),
                tc("1\n42\n", ""),
                tc("5\n10 20 30 40 50\n", "10 20 30 40"),
                tc("2\n-1 1\n", "-1"),
                tc("4\n0 0 0 0\n", "0 0 0"),
            ],
        ),
        _block_from_body(
            97, "Добавить только положительные",
            "Читайте числа до 0, выведите только положительные через пробел. Соберите из блоков.",
            "easy",
            "var x: integer; a: array of integer; n,i: integer;\nbegin\n  n:=0; SetLength(a,0);\n"
            "  readln(x);\n  while x<>0 do begin\n"
            "    if x>0 then begin SetLength(a,n+1); a[n]:=x; n:=n+1; end;\n    readln(x);\n  end;\n"
            "  for i:=0 to n-1 do if i<n-1 then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            examples=_EX_POSITIVES,
            test_cases=[
                tc("1\n2\n-1\n0\n", "1 2"),
                tc("5\n0\n", "5"),
                tc("-1\n0\n", ""),
                tc("3\n-2\n4\n0\n", "3 4"),
                tc("0\n", ""),
            ],
        ),
        translate_task(
            98, "Список покупок",
            "Читайте цены до 0, выведите общую сумму. Исправьте ошибки.",
            "medium",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            code_examples=_EX_SHOPPING,
            test_cases=[
                tc("100\n200\n50\n0\n", "350"),
                tc("99\n0\n", "99"),
                tc("0\n", "0"),
                tc("10\n20\n30\n0\n", "60"),
                tc("5\n5\n5\n0\n", "15"),
            ],
            template="var price,total: integer;\nbegin\n  total:=0;\n  readln(price);\n"
            "  while price>0 do begin total:=total+price; readln(price); end;\n  writeln(total);\nend.",
        ),
        translate_task(
            99, "Список оценок",
            "Прочитайте N и N оценок, выведите среднее с одним знаком после запятой. Переведите на Pascal.",
            "hard",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            code_examples=_EX_GRADES_AVG,
            test_cases=[
                tc("3\n3 4 5\n", "4.0"),
                tc("2\n10 20\n", "15.0"),
                tc("1\n5\n", "5.0"),
                tc("4\n2 3 4 5\n", "3.5"),
                tc("5\n5 5 5 5 5\n", "5.0"),
            ],
        ),
        _block_from_body(
            100, "Найти элемент в списке",
            "Прочитайте N, список и x. Выведите yes или no. Соберите из блоков.",
            "easy",
            "var n,i,x: integer; a: array of integer; found: boolean;\nbegin\n"
            "  readln(n); SetLength(a,n);\n  for i:=0 to n-1 do read(a[i]);\n  readln(x);\n"
            "  found:=false;\n  for i:=0 to n-1 do if a[i]=x then found:=true;\n"
            "  if found then writeln('yes') else writeln('no');\nend.",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            examples=_EX_FIND_LIST,
            test_cases=[
                tc("5\n1 2 3 4 5\n3\n", "yes"),
                tc("3\n2 4 6\n5\n", "no"),
                tc("1\n10\n10\n", "yes"),
                tc("4\n0 0 0 0\n1\n", "no"),
                tc("2\n5 5\n5\n", "yes"),
            ],
        ),
        translate_task(
            101, "Удалить все нули",
            "Прочитайте N и N значений, удалите нули и выведите остальные. Исправьте ошибки.",
            "medium",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            code_examples=_EX_FILTER_ZEROS,
            test_cases=[
                tc("5\n1 0 2 0 3\n", "1 2 3"),
                tc("3\n0 0 0\n", ""),
                tc("1\n5\n", "5"),
                tc("4\n0 1 0 2\n", "1 2"),
                tc("2\n0 0\n", ""),
            ],
            template="var n,i: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
            "  for i:=0 to n-1 do read(a[i]);\n"
            "  for i:=0 to n-1 do if a[i]=0 then write(a[i],' ');\n  writeln;\nend.",
        ),
        translate_task(
            102, "Разделить список",
            "Прочитайте N, значения и порог. Выведите элементы <= порога, затем > порога. Переведите на Pascal.",
            "hard",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            code_examples=_EX_SPLIT_LIST,
            test_cases=[
                tc("5\n1 2 3 4 5\n3\n", "1 2 3\n4 5"),
                tc("3\n10 20 30\n25\n", "10 20\n30"),
                tc("1\n5\n5\n", "5\n"),
                tc("4\n1 1 1 1\n0\n", "1 1 1 1\n"),
                tc("2\n-1 1\n0\n", "-1\n1"),
            ],
        ),
        _block_from_body(
            103, "Список уникальных значений",
            "Прочитайте N и N значений, выведите уникальные в порядке появления. Соберите из блоков.",
            "easy",
            "var n,i,j,c: integer; a,b: array of integer; dup: boolean;\nbegin\n  readln(n); SetLength(a,n); c:=0;\n"
            "  for i:=0 to n-1 do read(a[i]);\n"
            "  for i:=0 to n-1 do begin dup:=false;\n"
            "    for j:=0 to c-1 do if b[j]=a[i] then dup:=true;\n"
            "    if not dup then begin SetLength(b,c+1); b[c]:=a[i]; c:=c+1; end; end;\n"
            "  for i:=0 to c-1 do if i<c-1 then write(b[i],' ') else write(b[i]);\n  writeln;\nend.",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            examples=_EX_UNIQUE,
            test_cases=[
                tc("5\n1 2 1 3 2\n", "1 2 3"),
                tc("3\n5 5 5\n", "5"),
                tc("1\n42\n", "42"),
                tc("4\n1 2 3 4\n", "1 2 3 4"),
                tc("6\n1 1 2 2 3 3\n", "1 2 3"),
            ],
        ),
        translate_task(
            104, "Ограничить размер списка",
            "Читайте значения до -1, сохраните не более 5, выведите их. Исправьте ошибки.",
            "medium",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            code_examples=_EX_LIMIT5,
            test_cases=[
                tc("1\n2\n3\n4\n5\n6\n-1\n", "1 2 3 4 5"),
                tc("10\n-1\n", "10"),
                tc("-1\n", ""),
                tc("1\n2\n-1\n", "1 2"),
                tc("1\n2\n3\n4\n5\n-1\n", "1 2 3 4 5"),
            ],
            template="var x: integer; a: array of integer; n,i: integer;\nbegin\n  n:=0;\n"
            "  readln(x);\n  while x<>-1 do begin SetLength(a,n+1); a[n]:=x; n:=n+1; readln(x); end;\n"
            "  for i:=0 to n-1 do if i<n-1 then write(a[i],' ') else write(a[i]);\n  writeln;\nend.",
        ),
        translate_task(
            105, "Перенести элементы между списками",
            "Прочитайте N, список A, M, список B. Добавьте B к A и выведите A. Переведите на Pascal.",
            "hard",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            code_examples=_EX_APPEND_LISTS,
            test_cases=[
                tc("2\n1 2\n3\n3 4 5\n", "1 2 3 4 5"),
                tc("1\n10\n1\n20\n", "10 20"),
                tc("0\n1\n5\n", "5"),
                tc("3\n1 2 3\n0\n", "1 2 3"),
                tc("2\n-1 1\n2\n0 0\n", "-1 1 0 0"),
            ],
        ),
        _block_from_body(
            106, "Очередь заявок",
            "Читайте команды: 1 x — добавить, 2 — извлечь и вывести, 0 — завершить. Соберите из блоков.",
            "easy",
            "var cmd,x: integer; q: array of integer; head,tail: integer;\nbegin\n  SetLength(q,100); head:=0; tail:=0;\n"
            "  readln(cmd);\n  while cmd<>0 do begin\n"
            "    if cmd=1 then begin readln(x); q[tail]:=x; tail:=tail+1; end\n"
            "    else if cmd=2 then if head<tail then begin writeln(q[head]); head:=head+1; end else writeln(-1);\n"
            "    readln(cmd);\n  end;\nend.",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            examples=_EX_QUEUE,
            test_cases=[
                tc("1\n10\n1\n20\n2\n2\n0\n", "10\n20"),
                tc("2\n0\n", "-1"),
                tc("1\n5\n2\n0\n", "5"),
                tc("1\n1\n1\n2\n1\n3\n2\n2\n0\n", "1\n2"),
                tc("1\n99\n2\n2\n0\n", "99\n-1"),
            ],
        ),
        translate_task(
            107, "История действий",
            "Прочитайте N строк и выведите их в обратном порядке. Исправьте ошибки.",
            "medium",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            code_examples=_EX_REVERSE_STRINGS,
            test_cases=[
                tc("3\nopen\nedit\nsave\n", "save\nedit\nopen"),
                tc("1\nhello\n", "hello"),
                tc("2\na\nb\n", "b\na"),
                tc("4\n1\n2\n3\n4\n", "4\n3\n2\n1"),
                tc("0\n", ""),
            ],
            template="var n,i: integer; s: array[1..100] of string;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do readln(s[i]);\n"
            "  for i:=1 to n do writeln(s[i]);\nend.",
        ),
        translate_task(
            108, "Проверочная: корзина покупателя",
            "Читайте цены товаров до 0. Выведите количество и общую сумму через пробел. Переведите на Pascal.",
            "hard",
            topics=_DYNAMIC_TOPICS,
            constructions=_DYNAMIC_CONSTRUCTIONS,
            code_examples=_EX_CART,
            test_cases=[
                tc("100\n200\n0\n", "2 300"),
                tc("50\n0\n", "1 50"),
                tc("0\n", "0 0"),
                tc("10\n20\n30\n0\n", "3 60"),
                tc("5\n5\n5\n0\n", "3 15"),
            ],
        ),
        # --- 109-122 strings (block, fix, translate cycle) ---
        _block_from_body(
            109, "Длина строки",
            "Прочитайте строку и выведите её длину. Соберите из блоков.",
            "easy",
            "var s: string;\nbegin\n  readln(s);\n  writeln(length(s));\nend.",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            examples=_EX_STRLEN,
            test_cases=[tc("hello\n", "5"), tc("a\n", "1"), tc("\n", "0"), tc("level\n", "5"), tc("12345\n", "5")],
        ),
        translate_task(
            110, "Первый и последний символ",
            "Прочитайте строку, выведите первый и последний символ через пробел. Исправьте ошибки.",
            "medium",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            code_examples=_EX_FIRST_LAST,
            test_cases=[
                tc("hello\n", "h o"),
                tc("a\n", "a a"),
                tc("ab\n", "a b"),
                tc("test\n", "t t"),
                tc("123\n", "1 3"),
            ],
            template="var s: string;\nbegin\n  readln(s);\n  writeln(s[2],' ',s[1]);\nend.",
        ),
        translate_task(
            111, "Подсчет символа",
            "Прочитайте строку и символ, выведите количество вхождений. Переведите на Pascal.",
            "hard",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            code_examples=_EX_COUNT_CHAR,
            test_cases=[
                tc("hello\nl\n", "2"),
                tc("aaa\na\n", "3"),
                tc("test\nx\n", "0"),
                tc("abc\nb\n", "1"),
                tc("mississippi\ns\n", "4"),
            ],
        ),
        _block_from_body(
            112, "Проверить наличие символа",
            "Прочитайте строку и символ, выведите yes или no. Соберите из блоков.",
            "easy",
            "var s,ch: string; i: integer; found: boolean;\nbegin\n  readln(s); readln(ch);\n  found:=false;\n"
            "  for i:=1 to length(s) do if s[i]=ch then found:=true;\n"
            "  if found then writeln('yes') else writeln('no');\nend.",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            examples=_EX_CHAR_PRESENT,
            test_cases=[
                tc("hello\nl\n", "yes"),
                tc("hello\nx\n", "no"),
                tc("aaa\na\n", "yes"),
                tc("test\nT\n", "no"),
                tc("abc\nz\n", "no"),
            ],
        ),
        translate_task(
            113, "Подсчитать цифры в строке",
            "Прочитайте строку и выведите количество цифр. Исправьте ошибки.",
            "medium",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            code_examples=_EX_COUNT_DIGITS,
            test_cases=[
                tc("abc123\n", "3"),
                tc("hello\n", "0"),
                tc("2024\n", "4"),
                tc("a1b2c3\n", "3"),
                tc("999\n", "3"),
            ],
            template="var s: string; i,c: integer;\nbegin\n  readln(s); c:=0;\n"
            "  for i:=1 to length(s) do if s[i]='0' then c:=c+1;\n  writeln(c);\nend.",
        ),
        translate_task(
            114, "Удалить пробелы",
            "Прочитайте строку и выведите её без пробелов. Переведите на Pascal.",
            "hard",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            code_examples=_EX_NO_SPACES,
            test_cases=[
                tc("a b c\n", "abc"),
                tc("hello world\n", "helloworld"),
                tc("no spaces\n", "nospaces"),
                tc("  x  \n", "x"),
                tc("abc\n", "abc"),
            ],
        ),
        _block_from_body(
            115, "Развернуть строку",
            "Прочитайте строку и выведите её в обратном порядке. Соберите из блоков.",
            "easy",
            "var s: string; i: integer; r: string;\nbegin\n  readln(s); r:='';\n"
            "  for i:=length(s) downto 1 do r:=r+s[i];\n  writeln(r);\nend.",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            examples=_EX_REVERSE_STR,
            test_cases=[
                tc("hello\n", "olleh"),
                tc("a\n", "a"),
                tc("ab\n", "ba"),
                tc("123\n", "321"),
                tc("race\n", "ecar"),
            ],
        ),
        translate_task(
            116, "Проверить палиндром",
            "Прочитайте строку, выведите yes если палиндром, иначе no. Исправьте ошибки.",
            "medium",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            code_examples=_EX_PALINDROME,
            test_cases=[
                tc("level\n", "yes"),
                tc("hello\n", "no"),
                tc("a\n", "yes"),
                tc("abba\n", "yes"),
                tc("abc\n", "no"),
            ],
            template="var s: string; i: integer; ok: boolean;\nbegin\n  readln(s); ok:=true;\n"
            "  for i:=1 to length(s) do if s[i]<>s[i] then ok:=false;\n"
            "  if ok then writeln('yes') else writeln('no');\nend.",
        ),
        translate_task(
            117, "Проверить пароль",
            "Прочитайте пароль. strong если длина >= 8 и есть цифра, иначе weak. Переведите на Pascal.",
            "hard",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            code_examples=_EX_PASSWORD,
            test_cases=[
                tc("password1\n", "strong"),
                tc("short1\n", "weak"),
                tc("longenough\n", "weak"),
                tc("12345678\n", "strong"),
                tc("abc\n", "weak"),
            ],
        ),
        _block_from_body(
            118, "Разбить строку на слова",
            "Прочитайте строку и выведите количество слов. Соберите из блоков.",
            "easy",
            "var s: string; i,c: integer; in_word: boolean;\nbegin\n  readln(s); c:=0; in_word:=false;\n"
            "  for i:=1 to length(s) do\n"
            "    if s[i]<>' ' then begin if not in_word then begin c:=c+1; in_word:=true; end; end\n"
            "    else in_word:=false;\n  writeln(c);\nend.",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            examples=_EX_WORD_COUNT,
            test_cases=[
                tc("hello world\n", "2"),
                tc("one\n", "1"),
                tc("  a  b  c  \n", "3"),
                tc("\n", "0"),
                tc("a b c d e\n", "5"),
            ],
        ),
        translate_task(
            119, "Найти самое длинное слово",
            "Прочитайте строку и выведите самое длинное слово. Исправьте ошибки.",
            "medium",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            code_examples=_EX_LONGEST_WORD,
            test_cases=[
                tc("hello world\n", "world"),
                tc("a bb ccc\n", "ccc"),
                tc("test\n", "test"),
                tc("one two three four\n", "three"),
                tc("x y z\n", "x"),
            ],
            template="var s,word,best: string; i: integer; len,best_len: integer;\nbegin\n  readln(s); best:=''; best_len:=999;\n"
            "  word:='';\n  for i:=1 to length(s)+1 do begin\n"
            "    if (i<=length(s)) and (s[i]<>' ') then word:=word+s[i]\n"
            "    else begin len:=length(word); if len<best_len then begin best:=word; best_len:=len; end; word:=''; end; end;\n"
            "  writeln(best);\nend.",
        ),
        translate_task(
            120, "Заменить символы",
            "Прочитайте строку, старый и новый символ. Замените все вхождения. Переведите на Pascal.",
            "hard",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            code_examples=_EX_REPLACE,
            test_cases=[
                tc("hello\nl\nL\n", "heLLo"),
                tc("aaa\na\nb\n", "bbb"),
                tc("test\nx\ny\n", "test"),
                tc("abcabc\na\n1\n", "1bc1bc"),
                tc("mississippi\ns\nz\n", "mizzizzippi"),
            ],
        ),
        _block_from_body(
            121, "Сформировать логин",
            "Прочитайте имя и фамилию, выведите логин: первая буква имени + фамилия в нижнем регистре. Соберите из блоков.",
            "easy",
            "var first,last,login: string;\nbegin\n  readln(first,last);\n"
            "  login:=lower(first[1])+lower(last);\n  writeln(login);\nend.",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            examples=_EX_LOGIN,
            test_cases=[
                tc("Ivan Petrov\n", "ipetrov"),
                tc("Anna Smith\n", "asmith"),
                tc("A B\n", "ab"),
                tc("John Doe\n", "jdoe"),
                tc("X YZ\n", "xyz"),
            ],
        ),
        translate_task(
            122, "Проверочная: валидация анкеты",
            "Прочитайте имя и возраст. valid если имя непустое и возраст 1–120, иначе invalid. Исправьте ошибки.",
            "medium",
            topics=_STRINGS_TOPICS,
            constructions=_STRINGS_CONSTRUCTIONS,
            code_examples=_EX_FORM_VALID,
            test_cases=[
                tc("Ivan\n25\n", "valid"),
                tc("\n30\n", "invalid"),
                tc("Anna\n0\n", "invalid"),
                tc("Bob\n121\n", "invalid"),
                tc("Eve\n1\n", "valid"),
            ],
            template="var name: string; age: integer;\nbegin\n  readln(name); readln(age);\n"
            "  if (length(name)>0) or (age>=1) then writeln('valid') else writeln('invalid');\nend.",
        ),
        # --- 123-124 functions ---
        translate_task(
            123, "Функция Sum",
            "Напишите функцию Sum(a,b), возвращающую a+b. Переведите программу на Pascal.",
            "hard",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            code_examples=_EX_FUNC_SUM,
            test_cases=[
                tc("2 3\n", "5"),
                tc("0 0\n", "0"),
                tc("-1 1\n", "0"),
                tc("10 20\n", "30"),
                tc("100 200\n", "300"),
            ],
        ),
        _block_from_body(
            124, "Функция Max",
            "Реализуйте функцию Max(a,b), возвращающую большее из двух чисел. Соберите из блоков.",
            "easy",
            "function Max(a,b: integer): integer;\nbegin\n  if a>b then Max:=a else Max:=b;\nend;\n"
            "var a,b: integer;\nbegin\n  readln(a,b);\n  writeln(Max(a,b));\nend.",
            topics=_FUNCTIONS_TOPICS,
            constructions=_FUNCTIONS_CONSTRUCTIONS,
            examples=_EX_FUNC_MAX,
            test_cases=[
                tc("3 8\n", "8"),
                tc("9 1\n", "9"),
                tc("7 7\n", "7"),
                tc("0 10\n", "10"),
                tc("-1 -5\n", "-1"),
            ],
        ),
    ]


COURSE_BATCH_75_124_CATALOG = build_course_batch_75_124_catalog()
COURSE_BATCH_75_124_SIZE = 50
