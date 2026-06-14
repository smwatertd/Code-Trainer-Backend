"""Разделы «Сортировка», «Ключ-значение», «Файлы», «Модули», «Структуры данных», «Идиомы» — задачи 175–224."""
from __future__ import annotations

from migrations.seeds.catalog_common import (
    block_task,
    pascal_blocks_from_body,
    tc,
    translate_task,
)

TaskRow = dict

_SORT_TOPICS = ["algorithms", "sort_order"]
_SORT_CONSTRUCTIONS = [
    "sort_order",
    "collection_iteration",
    "indexed_sequence",
    "stdin_read",
    "assignment",
    "stdout_write",
]

_KV_TOPICS = ["data", "key_value_map"]
_KV_CONSTRUCTIONS = [
    "key_value_map",
    "indexed_sequence",
    "collection_iteration",
    "stdin_read",
    "assignment",
    "stdout_write",
]

_FILE_TOPICS = ["io", "file_read"]
_FILE_WRITE_TOPICS = ["io", "file_write"]
_FILE_CONSTRUCTIONS = [
    "file_read",
    "file_write",
    "stdin_read",
    "stdout_write",
    "string_sequence",
]

_MODULE_TOPICS = ["modules", "import_dependency"]
_MODULE_CONSTRUCTIONS = [
    "import_dependency",
    "module_namespace",
    "symbol_visibility",
    "function_definition",
    "function_invocation",
]

_IDIOM_CONSTRUCTIONS = [
    "map",
    "filter",
    "reduce",
    "comprehension",
    "collection_iteration",
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


def _ds_topics(task_id: int) -> list[str]:
    kinds = ["stack_queue", "linked_node", "tree_hierarchy", "graph_edges"]
    return ["data_structures", kinds[(task_id - 207) % 4]]


def _ds_constructions(task_id: int) -> list[str]:
    kind = (task_id - 207) % 4
    base = ["indexed_sequence", "collection_iteration", "stdin_read", "stdout_write"]
    extra = {
        0: ["stack_queue"],
        1: ["linked_node"],
        2: ["tree_hierarchy"],
        3: ["graph_edges"],
    }[kind]
    return extra + base


def _idiom_topics(task_id: int) -> list[str]:
    kinds = ["map", "filter", "reduce"]
    return ["idioms", kinds[(task_id - 222) % 3]]


# --- sort examples ---

_EX_SORT_LEN = _stub(
    "n = int(input())\nlines = [input() for _ in range(n)]\nlines.sort(key=len)\nprint(' '.join(lines))",
    "var n,i,j: integer; s,t: array[1..100] of string; tmp: string;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do readln(s[i]);\n"
    "  for i:=1 to n-1 do for j:=1 to n-i do if length(s[j])>length(s[j+1]) then begin tmp:=s[j]; s[j]:=s[j+1]; s[j+1]:=tmp; end;\n"
    "  for i:=1 to n do if i<n then write(s[i],' ') else write(s[i]);\n  writeln;\nend.",
)

_EX_LEADERBOARD = _stub(
    "n = int(input())\nscores = list(map(int, input().split()))\nscores.sort(reverse=True)\nprint(' '.join(map(str, scores[:3])))",
    "var n,i,j,t,k: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(a[i]);\n"
    "  for i:=1 to n-1 do for j:=1 to n-i do if a[j]<a[j+1] then begin t:=a[j]; a[j]:=a[j+1]; a[j+1]:=t; end;\n"
    "  for k:=1 to 3 do if k<3 then write(a[k],' ') else write(a[k]);\n  writeln;\nend.",
)

# --- key-value examples ---

_EX_PRICE_MAP = _stub(
    "prices = {}\nwhile True:\n    line = input().strip()\n    if line == 'done': break\n"
    "    parts = line.split()\n    if parts[0] == 'set': prices[parts[1]] = int(parts[2])\n"
    "    elif parts[0] == 'get': print(prices.get(parts[1], -1))",
    "var n,i,c: integer; codes: array[1..100] of string; vals: array[1..100] of integer;\n"
    "    cmd,code: string; price,p: integer; found: boolean;\n"
    "function FindCode(code: string): integer;\nvar i: integer;\nbegin\n  FindCode:=-1;\n"
    "  for i:=1 to c do if codes[i]=code then FindCode:=i;\nend;\n"
    "begin\n  c:=0;\n  while true do begin\n    readln(cmd);\n    if cmd='done' then break;\n"
    "    if cmd='set' then begin readln(code,price); c:=c+1; codes[c]:=code; vals[c]:=price; end\n"
    "    else if cmd='get' then begin readln(code); p:=FindCode(code); if p=-1 then writeln(-1) else writeln(vals[p]); end;\n  end;\nend.",
)

_EX_PHONEBOOK = _stub(
    "names, phones = [], []\nwhile True:\n    line = input().strip()\n    if line == 'done': break\n"
    "    parts = line.split(maxsplit=2)\n    if parts[0] == 'add':\n        names.append(parts[1]); phones.append(parts[2])\n"
    "    elif parts[0] == 'find':\n        print(phones[names.index(parts[1])])",
    "var n,i,c: integer; names: array[1..100] of string; phones: array[1..100] of string;\n"
    "    cmd,name,phone: string; found: boolean;\nbegin\n  c:=0;\n  while true do begin\n    readln(cmd);\n    if cmd='done' then break;\n"
    "    if cmd='add' then begin readln(name,phone); c:=c+1; names[c]:=name; phones[c]:=phone; end\n"
    "    else if cmd='find' then begin readln(name); found:=false;\n"
    "      for i:=1 to c do if names[i]=name then begin writeln(phones[i]); found:=true; break; end; end;\n  end;\nend.",
)

_EX_GRADES = _stub(
    "students, grades = [], []\nwhile True:\n    line = input().strip()\n    if line == 'done': break\n"
    "    parts = line.split()\n    if len(parts) == 2:\n        students.append(parts[0]); grades.append(int(parts[1]))\n"
    "    else:\n        for i, s in enumerate(students):\n            if s == parts[0]: print(grades[i]); break",
    "var c,i: integer; students: array[1..100] of string; grades: array[1..100] of integer;\n"
    "    line,name: string; g: integer; found: boolean;\nbegin\n  c:=0;\n  while true do begin\n    readln(line);\n    if line='done' then break;\n"
    "    if pos(' ',line)>0 then begin\n      name:=copy(line,1,pos(' ',line)-1); val(line,pos(' ',line)+1,g);\n"
    "      c:=c+1; students[c]:=name; grades[c]:=g;\n    end else begin\n      found:=false;\n"
    "      for i:=1 to c do if students[i]=line then begin writeln(grades[i]); found:=true; break; end;\n    end;\n  end;\nend.",
)

_EX_WORD_COUNT = _stub(
    "text = input().split()\nword = input().strip()\nprint(sum(1 for w in text if w == word))",
    "var text,word,w: string; i,c,n: integer;\nbegin\n  readln(text); readln(word); c:=0; n:=length(text);\n"
    "  i:=1;\n  while i<=n do begin\n    while (i<=n) and (text[i]=' ') do i:=i+1;\n    if i>n then break;\n"
    "    w:=''; while (i<=n) and (text[i]<>' ') do begin w:=w+text[i]; i:=i+1; end;\n"
    "    if w=word then c:=c+1;\n  end;\n  writeln(c);\nend.",
)

_EX_PRODUCT_RECORD = _stub(
    "pid, name = input().split(maxsplit=1)\nprice = int(input())\nprint(f'{pid} {name} {price}')",
    "var pid,name: string; price: integer;\nbegin\n  readln(pid,name); readln(price);\n  writeln(pid,' ',name,' ',price);\nend.",
)

_EX_MAX_PRICE = _stub(
    "n = int(input())\nmaxp = 0\nfor _ in range(n):\n    _, _, price = input().split()\n    maxp = max(maxp, int(price))\nprint(maxp)",
    "var n,i,maxp,price: integer; pid: string; name: string;\nbegin\n  readln(n); maxp:=0;\n"
    "  for i:=1 to n do begin readln(pid,name,price); if price>maxp then maxp:=price; end;\n  writeln(maxp);\nend.",
)

_EX_AVG_SCORE = _stub(
    "n = int(input())\ntotal = 0\nfor _ in range(n):\n    _, score = input().split()\n    total += int(score)\nprint(f'{total / n:.1f}')",
    "var n,i,total,score: integer; name: string; avg: real;\nbegin\n  readln(n); total:=0;\n"
    "  for i:=1 to n do begin readln(name,score); total:=total+score; end;\n  avg:=total/n; writeln(avg:0:1);\nend.",
)

_EX_FIND_BY_ID = _stub(
    "n = int(input())\ntarget = input().strip()\nfor _ in range(n):\n    pid, name = input().split(maxsplit=1)\n    if pid == target:\n        print(name); break",
    "var n,i: integer; target,pid,name: string; found: boolean;\nbegin\n  readln(n); readln(target); found:=false;\n"
    "  for i:=1 to n do begin readln(pid,name); if pid=target then begin writeln(name); found:=true; break; end; end;\nend.",
)

_EX_UPDATE_KEY = _stub(
    "n = int(input())\nkeys = []\nvals = []\nfor _ in range(n):\n    k, v = input().split(); keys.append(k); vals.append(int(v))\n"
    "key, newv = input().split()\nfor i, k in enumerate(keys):\n    if k == key: vals[i] = int(newv); break\nprint(vals[keys.index(key)])",
    "var n,i,c: integer; keys: array[1..100] of string; vals: array[1..100] of integer;\n"
    "    key,newv: string; v,p: integer;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(keys[i],v); vals[i]:=v; end;\n"
    "  readln(key,newv); p:=-1;\n  for i:=1 to n do if keys[i]=key then p:=i;\n  if p<>-1 then vals[p]:=StrToInt(newv);\n  writeln(vals[p]);\nend.",
)

_EX_KEY_EXISTS = _stub(
    "n = int(input())\nkeys = [input().strip() for _ in range(n)]\nq = input().strip()\nprint('yes' if q in keys else 'no')",
    "var n,i: integer; keys: array[1..100] of string; q: string; ok: boolean;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do readln(keys[i]);\n  readln(q); ok:=false;\n  for i:=1 to n do if keys[i]=q then ok:=true;\n"
    "  if ok then writeln('yes') else writeln('no');\nend.",
)

_EX_CATEGORY_SUM = _stub(
    "n = int(input())\ncounts = {}\nfor _ in range(n):\n    cat = input().strip()\n    counts[cat] = counts.get(cat, 0) + 1\n"
    "for cat in sorted(counts):\n    print(f'{cat} {counts[cat]}')",
    "var n,i,j,c,idx: integer; cats: array[1..100] of string; cnts: array[1..100] of integer;\n"
    "    cat: string; found: boolean;\nbegin\n  readln(n); c:=0;\n  for i:=1 to n do begin\n    readln(cat); found:=false;\n"
    "    for j:=1 to c do if cats[j]=cat then begin cnts[j]:=cnts[j]+1; found:=true; break; end;\n"
    "    if not found then begin c:=c+1; cats[c]:=cat; cnts[c]:=1; end;\n  end;\n"
    "  for i:=1 to c do writeln(cats[i],' ',cnts[i]);\nend.",
)

_EX_INVENTORY = _stub(
    "n = int(input())\ntotal = 0\nfor _ in range(n):\n    qty, price = map(int, input().split())\n    total += qty * price\nprint(total)",
    "var n,i,qty,price,total: integer;\nbegin\n  readln(n); total:=0;\n"
    "  for i:=1 to n do begin readln(qty,price); total:=total+qty*price; end;\n  writeln(total);\nend.",
)

# --- file examples ---

_EX_FILE_LINES = _stub(
    "n = int(input())\nfor i in range(n):\n    print(f'{i + 1} {input()}')",
    "var n,i: integer; line: string;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(line); writeln(i,' ',line); end;\nend.",
)

_EX_COUNT_LINES = _stub(
    "n = int(input())\nfor _ in range(n):\n    input()\nprint(n)",
    "var n,i: integer; line: string;\nbegin\n  readln(n);\n  for i:=1 to n do readln(line);\n  writeln(n);\nend.",
)

_EX_FIND_LINE = _stub(
    "n = int(input())\nlines = [input() for _ in range(n)]\nkey = input().strip()\n"
    "for line in lines:\n    if key in line:\n        print(line)",
    "var n,i: integer; lines: array[1..100] of string; key: string;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do readln(lines[i]);\n  readln(key);\n  for i:=1 to n do if pos(key,lines[i])>0 then writeln(lines[i]);\nend.",
)

_EX_SUM_FILE = _stub(
    "n = int(input())\ntotal = 0\nfor _ in range(n):\n    total += int(input())\nprint(total)",
    "var n,i,total,v: integer;\nbegin\n  readln(n); total:=0;\n  for i:=1 to n do begin readln(v); total:=total+v; end;\n  writeln(total);\nend.",
)

_EX_WRITE_RESULT = _stub(
    "value = input().strip()\nprint(f'FILE: {value}')",
    "var value: string;\nbegin\n  readln(value);\n  writeln('FILE: ',value);\nend.",
)

_EX_COPY_FILE = _stub(
    "n = int(input())\nfor _ in range(n):\n    print(input())",
    "var n,i: integer; line: string;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(line); writeln(line); end;\nend.",
)

_EX_FILTER_FILE = _stub(
    "n = int(input())\nkey = input().strip()\nfor _ in range(n):\n    line = input()\n    if key in line:\n        print(line)",
    "var n,i: integer; key,line: string;\nbegin\n  readln(n); readln(key);\n"
    "  for i:=1 to n do begin readln(line); if pos(key,line)>0 then writeln(line); end;\nend.",
)

_EX_LOG_ERRORS = _stub(
    "n = int(input())\nc = 0\nfor _ in range(n):\n    if input().strip() == 'ERROR': c += 1\nprint(c)",
    "var n,i,c: integer; line: string;\nbegin\n  readln(n); c:=0;\n  for i:=1 to n do begin readln(line); if line='ERROR' then c:=c+1; end;\n  writeln(c);\nend.",
)

_EX_GRADES_FILE = _stub(
    "n = int(input())\ntotal = 0\nfor _ in range(n):\n    _, score = input().split(':')\n    total += int(score)\nprint(f'{total / n:.1f}')",
    "var n,i,p,score,total: integer; line,name: string; avg: real;\nbegin\n  readln(n); total:=0;\n"
    "  for i:=1 to n do begin readln(line); p:=pos(':',line); val(copy(line,p+1,255),score); total:=total+score; end;\n"
    "  avg:=total/n; writeln(avg:0:1);\nend.",
)

_EX_LOG_REPORT = _stub(
    "n = int(input())\nc = {'INFO': 0, 'WARN': 0, 'ERROR': 0}\nfor _ in range(n):\n    c[input().strip()] += 1\n"
    "print(f\"INFO {c['INFO']} WARN {c['WARN']} ERROR {c['ERROR']}\")",
    "var n,i,info,warn,err: integer; line: string;\nbegin\n  readln(n); info:=0; warn:=0; err:=0;\n"
    "  for i:=1 to n do begin readln(line);\n    if line='INFO' then info:=info+1\n    else if line='WARN' then warn:=warn+1\n    else if line='ERROR' then err:=err+1; end;\n"
    "  writeln('INFO ',info,' WARN ',warn,' ERROR ',err);\nend.",
)

# --- module examples ---

_EX_MATH_SQRT = _stub(
    "import math\nx = float(input())\nprint(f'{math.sqrt(x):.2f}')",
    "uses Math;\nvar x: real;\nbegin\n  readln(x);\n  writeln(Sqrt(x):0:2);\nend.",
)

_EX_EXTRACT_FUNC = _stub(
    "def double(x):\n    return x * 2\nx = int(input())\nprint(double(x))",
    "function Double(x: integer): integer;\nbegin\n  Double:=x*2;\nend;\nvar x: integer;\nbegin\n  readln(x);\n  writeln(Double(x));\nend.",
)

_EX_TWO_FILES = _stub(
    "def greet(name):\n    return f'Hello, {name}!'\nname = input().strip()\nprint(greet(name))",
    "function Greet(name: string): string;\nbegin\n  Greet:='Hello, '+name+'!';\nend;\nvar name: string;\nbegin\n  readln(name);\n  writeln(Greet(name));\nend.",
)

_EX_LOCAL_HELPER = _stub(
    "def helper(x):\n    return x + 1\ndef main():\n    print(helper(int(input())))\nmain()",
    "function Helper(x: integer): integer;\nbegin\n  Helper:=x+1;\nend;\n"
    "procedure Main;\nvar x: integer;\nbegin\n  readln(x);\n  writeln(Helper(x));\nend;\nbegin\n  Main;\nend.",
)

_EX_STR_MODULE = _stub(
    "def upper(s):\n    return s.upper()\ns = input().strip()\nprint(upper(s))",
    "function ToUpper(s: string): string;\nvar i: integer;\nbegin\n  ToUpper:=UpperCase(s);\nend;\nvar s: string;\nbegin\n  readln(s);\n  writeln(ToUpper(s));\nend.",
)

_EX_DISCOUNT_MOD = _stub(
    "def apply_discount(price, pct):\n    return price * (100 - pct) // 100\nprice, pct = map(int, input().split())\nprint(apply_discount(price, pct))",
    "function ApplyDiscount(price,pct: integer): integer;\nbegin\n  ApplyDiscount:=price*(100-pct) div 100;\nend;\n"
    "var price,pct: integer;\nbegin\n  readln(price,pct);\n  writeln(ApplyDiscount(price,pct));\nend.",
)

_EX_ARRAY_STATS = _stub(
    "def stats(nums):\n    return sum(nums), max(nums)\nn = int(input())\nnums = list(map(int, input().split()))\ns, m = stats(nums)\nprint(s, m)",
    "procedure Stats(a: array of integer; n: integer; var s,m: integer);\nvar i: integer;\nbegin\n  s:=0; m:=a[0];\n"
    "  for i:=0 to n-1 do begin s:=s+a[i]; if a[i]>m then m:=a[i]; end;\nend;\n"
    "var n,i,s,m: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n  for i:=0 to n-1 do read(a[i]);\n  Stats(a,n,s,m);\n  writeln(s,' ',m);\nend.",
)

_EX_MINI_LIB = _stub(
    "def add(a, b): return a + b\ndef mul(a, b): return a * b\nop, a, b = input().split()\na, b = int(a), int(b)\nprint(add(a, b) if op == 'add' else mul(a, b))",
    "function Add(a,b: integer): integer; begin Add:=a+b; end;\n"
    "function Mul(a,b: integer): integer; begin Mul:=a*b; end;\n"
    "var op: string; a,b: integer;\nbegin\n  readln(op,a,b);\n  if op='add' then writeln(Add(a,b)) else writeln(Mul(a,b));\nend.",
)

# --- data structure examples ---

_EX_STACK = _stub(
    "stack = []\nwhile True:\n    parts = input().split()\n    if parts[0] == '0': break\n    if parts[0] == 'push': stack.append(int(parts[1]))\n    elif parts[0] == 'pop': print(stack.pop())",
    "var stack: array[1..100] of integer; top,i: integer; cmd: string; v: integer;\nbegin\n  top:=0;\n"
    "  while true do begin\n    readln(cmd);\n    if cmd='0' then break;\n    if cmd='push' then begin readln(v); top:=top+1; stack[top]:=v; end\n"
    "    else if cmd='pop' then begin writeln(stack[top]); top:=top-1; end;\n  end;\nend.",
)

_EX_QUEUE = _stub(
    "q = []\nwhile True:\n    parts = input().split()\n    if parts[0] == '0': break\n    if parts[0] == 'enqueue': q.append(int(parts[1]))\n    elif parts[0] == 'dequeue': print(q.pop(0))",
    "var q: array[1..100] of integer; head,tail: integer; cmd: string; v: integer;\nbegin\n  head:=1; tail:=0;\n"
    "  while true do begin\n    readln(cmd);\n    if cmd='0' then break;\n    if cmd='enqueue' then begin readln(v); tail:=tail+1; q[tail]:=v; end\n"
    "    else if cmd='dequeue' then begin writeln(q[head]); head:=head+1; end;\n  end;\nend.",
)

_EX_BRACKETS = _stub(
    "s = input().strip()\nstack = []\nok = True\nfor ch in s:\n    if ch == '(': stack.append(ch)\n    elif ch == ')':\n        if not stack: ok = False; break\n        stack.pop()\nprint('valid' if ok and not stack else 'invalid')",
    "var s: string; i,top: integer; stack: array[1..100] of char; ch: char; ok: boolean;\nbegin\n  readln(s); top:=0; ok:=true;\n"
    "  for i:=1 to length(s) do begin\n    ch:=s[i];\n    if ch='(' then begin top:=top+1; stack[top]:=ch; end\n"
    "    else if ch=')' then if top=0 then ok:=false else top:=top-1;\n  end;\n  if ok and (top=0) then writeln('valid') else writeln('invalid');\nend.",
)

_EX_PRINT_QUEUE = _stub(
    "n = int(input())\nq = list(map(int, input().split()))\nwhile q:\n    print(q.pop(0))",
    "var n,i,head,tail: integer; q: array[1..100] of integer;\nbegin\n  readln(n); head:=1; tail:=n;\n"
    "  for i:=1 to n do read(q[i]);\n  while head<=tail do begin writeln(q[head]); head:=head+1; end;\nend.",
)

_EX_LIST_ADD = _stub(
    "n = int(input())\nvals = []\nfor _ in range(n):\n    parts = input().split()\n    if parts[0] == 'add': vals.append(int(parts[1]))\nprint(' '.join(map(str, vals)))",
    "var n,i,c: integer; vals: array[1..100] of integer; cmd: string; v: integer;\nbegin\n  readln(n); c:=0;\n"
    "  for i:=1 to n do begin\n    readln(cmd,v);\n    if cmd='add' then begin c:=c+1; vals[c]:=v; end;\n  end;\n"
    "  for i:=1 to c do if i<c then write(vals[i],' ') else write(vals[i]);\n  writeln;\nend.",
)

_EX_LIST_FIND = _stub(
    "n = int(input())\nvals = list(map(int, input().split()))\nx = int(input())\nprint(vals.index(x) + 1 if x in vals else -1)",
    "var n,i,x,p: integer; vals: array[1..100] of integer; found: boolean;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(vals[i]);\n  readln(x); p:=-1;\n  for i:=1 to n do if vals[i]=x then p:=i;\n  writeln(p);\nend.",
)

_EX_LIST_REMOVE = _stub(
    "n = int(input())\nvals = list(map(int, input().split()))\nx = int(input())\n"
    "if x in vals:\n    vals.remove(x)\nprint(' '.join(map(str, vals)))",
    "var n,i,j,c,x: integer; vals,tmp: array[1..100] of integer;\nbegin\n  readln(n);\n  for i:=1 to n do read(vals[i]);\n  readln(x); c:=0;\n"
    "  for i:=1 to n do if vals[i]<>x then begin c:=c+1; tmp[c]:=vals[i]; end;\n"
    "  for i:=1 to c do if i<c then write(tmp[i],' ') else write(tmp[i]);\n  writeln;\nend.",
)

_EX_TREE_PRE = _stub(
    "print('A')\nprint('B C')",
    "begin\n  writeln('A');\n  writeln('B C');\nend.",
)

_EX_TREE_COUNT = _stub(
    "n = int(input())\nprint(n)",
    "var n: integer;\nbegin\n  readln(n);\n  writeln(n);\nend.",
)

_EX_TREE_FIND = _stub(
    "n = int(input())\nvals = list(map(int, input().split()))\nx = int(input())\nprint('yes' if x in vals else 'no')",
    "var n,i,x: integer; vals: array[1..100] of integer; ok: boolean;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do read(vals[i]);\n  readln(x); ok:=false;\n  for i:=1 to n do if vals[i]=x then ok:=true;\n"
    "  if ok then writeln('yes') else writeln('no');\nend.",
)

_EX_ADJ_MATRIX = _stub(
    "n = int(input())\nmat = [list(map(int, input().split())) for _ in range(n)]\nv = int(input()) - 1\n"
    "print(' '.join(str(j + 1) for j in range(n) if mat[v][j] == 1))",
    "var n,i,j,v: integer; mat: array[1..10,1..10] of integer; first: boolean;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do for j:=1 to n do read(mat[i,j]);\n  readln(v); first:=true;\n"
    "  for j:=1 to n do if mat[v,j]=1 then begin if not first then write(' '); write(j); first:=false; end;\n  writeln;\nend.",
)

_EX_EDGE_LIST = _stub(
    "m = int(input())\nedges = []\nfor _ in range(m):\n    a, b = map(int, input().split())\n    edges.append((a, b))\nv = int(input())\n"
    "print(' '.join(str(b) for a, b in edges if a == v))",
    "var m,i,c,v,a,b: integer; froms,tos: array[1..100] of integer; first: boolean;\nbegin\n  readln(m); c:=0;\n"
    "  for i:=1 to m do begin readln(a,b); c:=c+1; froms[c]:=a; tos[c]:=b; end;\n  readln(v); first:=true;\n"
    "  for i:=1 to c do if froms[i]=v then begin if not first then write(' '); write(tos[i]); first:=false; end;\n  writeln;\nend.",
)

_EX_VERTEX_DEGREE = _stub(
    "n = int(input())\nmat = [list(map(int, input().split())) for _ in range(n)]\nv = int(input()) - 1\nprint(sum(mat[v]))",
    "var n,i,j,v,deg: integer; mat: array[1..10,1..10] of integer;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do for j:=1 to n do read(mat[i,j]);\n  readln(v); deg:=0;\n  for j:=1 to n do deg:=deg+mat[v,j];\n  writeln(deg);\nend.",
)

_EX_NEIGHBORS = _stub(
    "n = int(input())\nmat = [list(map(int, input().split())) for _ in range(n)]\nv = int(input()) - 1\n"
    "print(' '.join(str(j + 1) for j in range(n) if mat[v][j] == 1))",
    "var n,i,j,v: integer; mat: array[1..10,1..10] of integer; first: boolean;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do for j:=1 to n do read(mat[i,j]);\n  readln(v); first:=true;\n"
    "  for j:=1 to n do if mat[v,j]=1 then begin if not first then write(' '); write(j); first:=false; end;\n  writeln;\nend.",
)

_EX_BFS_ROUTE = _stub(
    "n, m = map(int, input().split())\nedges = []\nfor _ in range(m):\n    edges.append(tuple(map(int, input().split())))\nstart, goal = map(int, input().split())\n"
    "visited = {start}\nq = [start]\nwhile q:\n    v = q.pop(0)\n    if v == goal:\n        print('yes'); break\n    for a, b in edges:\n        if a == v and b not in visited:\n            visited.add(b); q.append(b)\nelse:\n    print('no')",
    "var n,m,i,c,start,goal,head,tail,v,a,b: integer;\n    froms,tos,q: array[1..100] of integer; visited: array[1..100] of boolean; ok: boolean;\n"
    "function Reachable: boolean;\nvar i,head,tail,v: integer; q: array[1..100] of integer; seen: array[1..100] of boolean;\nbegin\n  for i:=1 to n do seen[i]:=false;\n  head:=1; tail:=1; q[1]:=start; seen[start]:=true; ok:=false;\n"
    "  while head<=tail do begin\n    v:=q[head]; head:=head+1;\n    if v=goal then begin ok:=true; break; end;\n"
    "    for i:=1 to c do if (froms[i]=v) and (not seen[tos[i]]) then begin tail:=tail+1; q[tail]:=tos[i]; seen[tos[i]]:=true; end;\n  end;\n  Reachable:=ok;\nend;\n"
    "begin\n  readln(n,m); c:=0;\n  for i:=1 to m do begin readln(a,b); c:=c+1; froms[c]:=a; tos[c]:=b; end;\n  readln(start,goal);\n  if Reachable then writeln('yes') else writeln('no');\nend.",
)

# --- idiom examples ---

_EX_ENUM_STUDENTS = _stub(
    "n = int(input())\nfor i in range(n):\n    print(f'{i + 1}. {input()}')",
    "var n,i: integer; name: string;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(name); writeln(i,'. ',name); end;\nend.",
)

_EX_SUM_POSITIVE = _stub(
    "n = int(input())\nnums = list(map(int, input().split()))\nprint(sum(x for x in nums if x > 0))",
    "var n,i,s: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n  s:=0;\n  for i:=1 to n do begin read(a[i]); if a[i]>0 then s:=s+a[i]; end;\n  writeln(s);\nend.",
)

_EX_FILTER_EVENS = _stub(
    "nums = list(map(int, input().split()))\nevens = [x for x in nums if x % 2 == 0]\nprint(' '.join(map(str, evens)))",
    "var n,i,c: integer; a,b: array[1..100] of integer;\nbegin\n  readln(n); c:=0;\n"
    "  for i:=1 to n do begin read(a[i]); if a[i] mod 2=0 then begin c:=c+1; b[c]:=a[i]; end; end;\n"
    "  for i:=1 to c do if i<c then write(b[i],' ') else write(b[i]);\n  writeln;\nend.",
)


def build_course_batch_175_224_catalog() -> list[TaskRow]:
    """Tasks 175-224: sort finish, key-value, files, modules, data structures, idioms."""
    return [
        # --- 175-176 sort (finish section) ---
        _block_from_body(
            175, "Сортировка по длине строки",
            "Прочитайте N строк и выведите их через пробел, отсортированные по длине по возрастанию.",
            "easy",
            "var n,i,j: integer; s,t: array[1..100] of string; tmp: string;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do readln(s[i]);\n"
            "  for i:=1 to n-1 do for j:=1 to n-i do if length(s[j])>length(s[j+1]) then begin tmp:=s[j]; s[j]:=s[j+1]; s[j+1]:=tmp; end;\n"
            "  for i:=1 to n do if i<n then write(s[i],' ') else write(s[i]);\n  writeln;\nend.",
            topics=_SORT_TOPICS,
            constructions=_SORT_CONSTRUCTIONS,
            examples=_EX_SORT_LEN,
            test_cases=[
                tc("3\nhi\nhello\nhey\n", "hi hey hello"),
                tc("2\na\nbb\n", "a bb"),
                tc("1\nsolo\n", "solo"),
                tc("4\none\ntwo\nthree\nfour\n", "one two four three"),
                tc("2\naa\na\n", "a aa"),
            ],
        ),
        translate_task(
            176, "Проверочная: таблица лидеров",
            "Прочитайте N и N очков, выведите топ-3 по убыванию через пробел. Исправьте ошибки.",
            "medium",
            topics=_SORT_TOPICS,
            constructions=_SORT_CONSTRUCTIONS,
            code_examples=_EX_LEADERBOARD,
            test_cases=[
                tc("5\n1 5 3 4 2\n", "5 4 3"),
                tc("3\n10 20 30\n", "30 20 10"),
                tc("4\n7 7 7 7\n", "7 7 7"),
                tc("6\n1 2 3 4 5 6\n", "6 5 4"),
                tc("3\n-1 -2 -3\n", "-1 -2 -3"),
            ],
            template="var n,i: integer; a: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(a[i]);\n  writeln(a[1],' ',a[2],' ',a[3]);\nend.",
        ),
        # --- 177-188 key-value and records ---
        translate_task(
            177, "Хранить цену по коду товара",
            "Обработайте команды set/get до done: сохраняйте цену по коду и выводите её при get. Переведите на Pascal.",
            "hard",
            topics=_KV_TOPICS,
            constructions=_KV_CONSTRUCTIONS,
            code_examples=_EX_PRICE_MAP,
            test_cases=[
                tc("set A 100\nget A\ndone\n", "100"),
                tc("set X 10\nset Y 20\nget X\nget Y\ndone\n", "10\n20"),
                tc("get Z\ndone\n", "-1"),
                tc("set M 5\nset M 9\nget M\ndone\n", "9"),
                tc("set A 1\nset B 2\nget B\nget A\ndone\n", "2\n1"),
            ],
        ),
        _block_from_body(
            178, "Телефонная книга",
            "Обработайте команды add/find до done: добавляйте имя и телефон, находите телефон по имени.",
            "easy",
            "var c,i: integer; names: array[1..100] of string; phones: array[1..100] of string;\n"
            "    cmd,name,phone: string;\nbegin\n  c:=0;\n  while true do begin\n    readln(cmd);\n    if cmd='done' then break;\n"
            "    if cmd='add' then begin readln(name,phone); c:=c+1; names[c]:=name; phones[c]:=phone; end\n"
            "    else if cmd='find' then begin readln(name);\n"
            "      for i:=1 to c do if names[i]=name then begin writeln(phones[i]); break; end; end;\n  end;\nend.",
            topics=_KV_TOPICS,
            constructions=_KV_CONSTRUCTIONS,
            examples=_EX_PHONEBOOK,
            test_cases=[
                tc("add Ivan 123\nfind Ivan\ndone\n", "123"),
                tc("add Anna 111\nadd Bob 222\nfind Bob\ndone\n", "222"),
                tc("add X 9\nadd Y 8\nfind X\ndone\n", "9"),
                tc("add A 1\nadd B 2\nfind B\ndone\n", "2"),
                tc("add Solo 777\nfind Solo\ndone\n", "777"),
            ],
        ),
        translate_task(
            179, "Словарь оценок",
            "Сохраните пары студент-оценка, затем по имени выведите оценку. Исправьте ошибки.",
            "medium",
            topics=_KV_TOPICS,
            constructions=_KV_CONSTRUCTIONS,
            code_examples=_EX_GRADES,
            test_cases=[
                tc("Anna 5\nBob 4\nAnna\ndone\n", "5"),
                tc("Ivan 3\nIvan\ndone\n", "3"),
                tc("A 10\nB 9\nB\ndone\n", "9"),
                tc("X 1\nY 2\nX\ndone\n", "1"),
                tc("S 5\nS\ndone\n", "5"),
            ],
            template="var c: integer; students: array[1..100] of string; grades: array[1..100] of integer;\n"
            "    line,name: string; g: integer;\nbegin\n  c:=0;\n  while true do begin\n    readln(line);\n    if line='done' then break;\n"
            "    if pos(' ',line)>0 then begin\n      name:=copy(line,1,pos(' ',line)-1); val(line,pos(' ',line)+1,g);\n"
            "      c:=c+1; students[c]:=name; grades[c]:=g;\n    end else writeln(students[1]);\n  end;\nend.",
        ),
        translate_task(
            180, "Подсчет повторов слов",
            "Прочитайте текст и слово, выведите сколько раз слово встречается. Переведите на Pascal.",
            "hard",
            topics=_KV_TOPICS,
            constructions=_KV_CONSTRUCTIONS,
            code_examples=_EX_WORD_COUNT,
            test_cases=[
                tc("hello world hello\nhello\n", "2"),
                tc("a b c\nx\n", "0"),
                tc("cat cat cat\ncat\n", "3"),
                tc("one two one two\none\n", "2"),
                tc("test\ntest\n", "1"),
            ],
        ),
        _block_from_body(
            181, "Запись товара",
            "Прочитайте id, название и цену товара, выведите их в одной строке.",
            "easy",
            "var pid,name: string; price: integer;\nbegin\n  readln(pid,name); readln(price);\n  writeln(pid,' ',name,' ',price);\nend.",
            topics=_KV_TOPICS,
            constructions=_KV_CONSTRUCTIONS,
            examples=_EX_PRODUCT_RECORD,
            test_cases=[
                tc("A1\nApple\n50\n", "A1 Apple 50"),
                tc("B2\nBook\n120\n", "B2 Book 120"),
                tc("X\nPen\n10\n", "X Pen 10"),
                tc("ID1\nLong name\n999\n", "ID1 Long name 999"),
                tc("Z\nItem\n0\n", "Z Item 0"),
            ],
        ),
        translate_task(
            182, "Массив записей товаров",
            "Прочитайте N товаров (id, название, цена) и выведите максимальную цену. Исправьте ошибки.",
            "medium",
            topics=_KV_TOPICS,
            constructions=_KV_CONSTRUCTIONS,
            code_examples=_EX_MAX_PRICE,
            test_cases=[
                tc("3\nA x 10\nB y 30\nC z 20\n", "30"),
                tc("1\nA a 5\n", "5"),
                tc("2\nA a 1\nB b 2\n", "2"),
                tc("4\nA a 4\nB b 1\nC c 9\nD d 3\n", "9"),
                tc("2\nA a 100\nB b 100\n", "100"),
            ],
            template="var n,i,maxp,price: integer; pid,name: string;\nbegin\n  readln(n); maxp:=0;\n"
            "  for i:=1 to n do begin readln(pid,name,price); if price<maxp then maxp:=price; end;\n  writeln(maxp);\nend.",
        ),
        translate_task(
            183, "Массив записей студентов",
            "Прочитайте N записей имя-балл и выведите средний балл с одним знаком. Переведите на Pascal.",
            "hard",
            topics=_KV_TOPICS,
            constructions=_KV_CONSTRUCTIONS,
            code_examples=_EX_AVG_SCORE,
            test_cases=[
                tc("3\nAnna 5\nBob 4\nCat 3\n", "4.0"),
                tc("1\nSolo 10\n", "10.0"),
                tc("2\nA 8\nB 6\n", "7.0"),
                tc("4\nA 5\nB 5\nC 5\nD 5\n", "5.0"),
                tc("2\nX 1\nY 2\n", "1.5"),
            ],
        ),
        _block_from_body(
            184, "Поиск записи по id",
            "Прочитайте N записей id-имя и id для поиска, выведите имя.",
            "easy",
            "var n,i: integer; target,pid,name: string;\nbegin\n  readln(n); readln(target);\n"
            "  for i:=1 to n do begin readln(pid,name); if pid=target then begin writeln(name); break; end; end;\nend.",
            topics=_KV_TOPICS,
            constructions=_KV_CONSTRUCTIONS,
            examples=_EX_FIND_BY_ID,
            test_cases=[
                tc("3\nB\nA alpha\nB beta\nC gamma\n", "beta"),
                tc("1\nX\nX only\nX\n", "only"),
                tc("2\n1\nA a\nB b\nA\n", "a"),
                tc("2\nZ\nZ z\nY y\nY\n", "y"),
                tc("3\nQ\nQ q\nW w\nE e\nW\n", "w"),
            ],
        ),
        translate_task(
            185, "Обновление значения по ключу",
            "Прочитайте пары ключ-значение, затем ключ и новое значение. Выведите обновлённое значение.",
            "medium",
            topics=_KV_TOPICS,
            constructions=_KV_CONSTRUCTIONS,
            code_examples=_EX_UPDATE_KEY,
            test_cases=[
                tc("2\nA 1\nB 2\nA 9\n", "9"),
                tc("1\nX 5\nX 10\n", "10"),
                tc("3\nA 1\nB 2\nC 3\nB 7\n", "7"),
                tc("2\nK 0\nM 1\nM 2\n", "2"),
                tc("1\nS 100\nS 1\n", "1"),
            ],
            template="var n,i,p: integer; keys: array[1..100] of string; vals: array[1..100] of integer;\n"
            "    key,newv: string; v: integer;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(keys[i],v); vals[i]:=v; end;\n"
            "  readln(key,newv); p:=1;\n  writeln(vals[p]);\nend.",
        ),
        translate_task(
            186, "Проверка существования ключа",
            "Прочитайте N ключей и ключ для проверки, выведите yes или no. Переведите на Pascal.",
            "hard",
            topics=_KV_TOPICS,
            constructions=_KV_CONSTRUCTIONS,
            code_examples=_EX_KEY_EXISTS,
            test_cases=[
                tc("3\nA\nB\nC\nB\n", "yes"),
                tc("2\nX\nY\nZ\n", "no"),
                tc("1\nS\nS\n", "yes"),
                tc("4\na\nb\nc\nd\na\n", "yes"),
                tc("1\nK\nQ\n", "no"),
            ],
        ),
        _block_from_body(
            187, "Сводка по категориям",
            "Прочитайте N категорий и выведите каждую категорию с количеством вхождений.",
            "easy",
            "var n,i,j,c: integer; cats: array[1..100] of string; cnts: array[1..100] of integer;\n"
            "    cat: string; found: boolean;\nbegin\n  readln(n); c:=0;\n  for i:=1 to n do begin\n    readln(cat); found:=false;\n"
            "    for j:=1 to c do if cats[j]=cat then begin cnts[j]:=cnts[j]+1; found:=true; break; end;\n"
            "    if not found then begin c:=c+1; cats[c]:=cat; cnts[c]:=1; end;\n  end;\n"
            "  for i:=1 to c do writeln(cats[i],' ',cnts[i]);\nend.",
            topics=_KV_TOPICS,
            constructions=_KV_CONSTRUCTIONS,
            examples=_EX_CATEGORY_SUM,
            test_cases=[
                tc("4\nA\nB\nA\nB\n", "A 2\nB 2"),
                tc("3\nX\nX\nX\n", "X 3"),
                tc("2\nA\nB\n", "A 1\nB 1"),
                tc("5\nA\nA\nB\nC\nB\n", "A 2\nB 2\nC 1"),
                tc("1\nSolo\n", "Solo 1"),
            ],
        ),
        translate_task(
            188, "Проверочная: склад товаров",
            "Прочитайте N пар количество-цена и выведите общую стоимость склада. Исправьте ошибки.",
            "medium",
            topics=_KV_TOPICS,
            constructions=_KV_CONSTRUCTIONS,
            code_examples=_EX_INVENTORY,
            test_cases=[
                tc("3\n2 10\n3 5\n1 100\n", "135"),
                tc("1\n5 20\n", "100"),
                tc("2\n0 100\n10 0\n", "0"),
                tc("4\n1 1\n2 2\n3 3\n4 4\n", "30"),
                tc("2\n10 10\n5 5\n", "125"),
            ],
            template="var n,i,qty,price,total: integer;\nbegin\n  readln(n); total:=0;\n"
            "  for i:=1 to n do begin readln(qty,price); total:=total+qty; end;\n  writeln(total);\nend.",
        ),
        # --- 189-198 files (stdin-as-file) ---
        translate_task(
            189, "Прочитать файл строк",
            "Прочитайте N строк «файла» и выведите их с номерами. Переведите на Pascal.",
            "hard",
            topics=_FILE_TOPICS,
            constructions=_FILE_CONSTRUCTIONS,
            code_examples=_EX_FILE_LINES,
            test_cases=[
                tc("2\nhello\nworld\n", "1 hello\n2 world"),
                tc("1\nsolo\n", "1 solo"),
                tc("3\na\nb\nc\n", "1 a\n2 b\n3 c"),
                tc("2\nx\ny\n", "1 x\n2 y"),
                tc("1\ntest\n", "1 test"),
            ],
        ),
        _block_from_body(
            190, "Посчитать строки файла",
            "Прочитайте N строк из stdin и выведите их количество.",
            "easy",
            "var n,i: integer; line: string;\nbegin\n  readln(n);\n  for i:=1 to n do readln(line);\n  writeln(n);\nend.",
            topics=_FILE_TOPICS,
            constructions=_FILE_CONSTRUCTIONS,
            examples=_EX_COUNT_LINES,
            test_cases=[
                tc("3\na\nb\nc\n", "3"),
                tc("1\nx\n", "1"),
                tc("0\n\n", "0"),
                tc("5\n1\n2\n3\n4\n5\n", "5"),
                tc("2\nhi\nbye\n", "2"),
            ],
        ),
        translate_task(
            191, "Найти строку в файле",
            "Прочитайте N строк и подстроку, выведите строки, содержащие её. Исправьте ошибки.",
            "medium",
            topics=_FILE_TOPICS,
            constructions=_FILE_CONSTRUCTIONS,
            code_examples=_EX_FIND_LINE,
            test_cases=[
                tc("3\nhello world\ngoodbye\nhell test\nhell\n", "hello world\nhell test"),
                tc("2\nabc\ndef\nx\n", ""),
                tc("1\ntest\nt\n", "test"),
                tc("4\na\nab\nabc\nbc\nb\n", "ab\nabc\nbc"),
                tc("2\nxx\nyy\nz\n", ""),
            ],
            template="var n,i: integer; lines: array[1..100] of string; key: string;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do readln(lines[i]);\n  readln(key);\n  for i:=1 to n do if lines[i]=key then writeln(lines[i]);\nend.",
        ),
        translate_task(
            192, "Посчитать числа из файла",
            "Прочитайте N строк с числами и выведите их сумму. Переведите на Pascal.",
            "hard",
            topics=_FILE_TOPICS,
            constructions=_FILE_CONSTRUCTIONS,
            code_examples=_EX_SUM_FILE,
            test_cases=[
                tc("3\n10\n20\n30\n", "60"),
                tc("1\n5\n", "5"),
                tc("4\n1\n2\n3\n4\n", "10"),
                tc("2\n0\n0\n", "0"),
                tc("5\n1\n1\n1\n1\n1\n", "5"),
            ],
        ),
        _block_from_body(
            193, "Записать результат в файл",
            "Прочитайте значение и выведите его в формате FILE: value (симуляция записи).",
            "easy",
            "var value: string;\nbegin\n  readln(value);\n  writeln('FILE: ',value);\nend.",
            topics=_FILE_WRITE_TOPICS,
            constructions=_FILE_CONSTRUCTIONS,
            examples=_EX_WRITE_RESULT,
            test_cases=[
                tc("hello\n", "FILE: hello"),
                tc("42\n", "FILE: 42"),
                tc("result\n", "FILE: result"),
                tc("ok\n", "FILE: ok"),
                tc("x\n", "FILE: x"),
            ],
        ),
        translate_task(
            194, "Скопировать файл",
            "Прочитайте N строк и выведите их без изменений. Исправьте ошибки.",
            "medium",
            topics=_FILE_WRITE_TOPICS,
            constructions=_FILE_CONSTRUCTIONS,
            code_examples=_EX_COPY_FILE,
            test_cases=[
                tc("2\na\nb\n", "a\nb"),
                tc("1\nsolo\n", "solo"),
                tc("3\n1\n2\n3\n", "1\n2\n3"),
                tc("0\n\n", ""),
                tc("2\nhi\nbye\n", "hi\nbye"),
            ],
            template="var n,i: integer; line: string;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(line); write(line); end;\nend.",
        ),
        translate_task(
            195, "Фильтровать файл",
            "Прочитайте N, ключ и N строк, выведите строки с ключом. Переведите на Pascal.",
            "hard",
            topics=_FILE_TOPICS,
            constructions=_FILE_CONSTRUCTIONS,
            code_examples=_EX_FILTER_FILE,
            test_cases=[
                tc("3\nerr\nok\nerror\nfail\n", "error"),
                tc("2\na\nbb\ncc\nb\n", "bb"),
                tc("1\ntest\nt\n", "test"),
                tc("4\nx\na\nax\nb\na\n", "a\nax"),
                tc("2\nhi\nbye\nz\n", ""),
            ],
        ),
        _block_from_body(
            196, "Обработать журнал событий",
            "Прочитайте N строк лога и выведите количество строк ERROR.",
            "easy",
            "var n,i,c: integer; line: string;\nbegin\n  readln(n); c:=0;\n"
            "  for i:=1 to n do begin readln(line); if line='ERROR' then c:=c+1; end;\n  writeln(c);\nend.",
            topics=_FILE_TOPICS,
            constructions=_FILE_CONSTRUCTIONS,
            examples=_EX_LOG_ERRORS,
            test_cases=[
                tc("4\nINFO\nERROR\nWARN\nERROR\n", "2"),
                tc("1\nERROR\n", "1"),
                tc("3\nINFO\nINFO\nINFO\n", "0"),
                tc("5\nERROR\nERROR\nERROR\nERROR\nERROR\n", "5"),
                tc("2\nWARN\nINFO\n", "0"),
            ],
        ),
        translate_task(
            197, "Таблица оценок из файла",
            "Прочитайте N строк name:score и выведите средний балл. Исправьте ошибки.",
            "medium",
            topics=_FILE_TOPICS,
            constructions=_FILE_CONSTRUCTIONS,
            code_examples=_EX_GRADES_FILE,
            test_cases=[
                tc("3\nAnna:5\nBob:4\nCat:3\n", "4.0"),
                tc("1\nSolo:10\n", "10.0"),
                tc("2\nA:8\nB:6\n", "7.0"),
                tc("4\nA:5\nB:5\nC:5\nD:5\n", "5.0"),
                tc("2\nX:1\nY:2\n", "1.5"),
            ],
            template="var n,i,p,score,total: integer; line,name: string; avg: real;\nbegin\n  readln(n); total:=0;\n"
            "  for i:=1 to n do begin readln(line); total:=total+1; end;\n  avg:=total/n; writeln(avg:0:1);\nend.",
        ),
        translate_task(
            198, "Проверочная: отчет по логам",
            "Прочитайте N строк INFO/WARN/ERROR и выведите счётчики. Переведите на Pascal.",
            "hard",
            topics=_FILE_TOPICS,
            constructions=_FILE_CONSTRUCTIONS,
            code_examples=_EX_LOG_REPORT,
            test_cases=[
                tc("4\nINFO\nWARN\nERROR\nINFO\n", "INFO 2 WARN 1 ERROR 1"),
                tc("1\nERROR\n", "INFO 0 WARN 0 ERROR 1"),
                tc("3\nINFO\nINFO\nINFO\n", "INFO 3 WARN 0 ERROR 0"),
                tc("2\nWARN\nWARN\n", "INFO 0 WARN 2 ERROR 0"),
                tc("5\nINFO\nWARN\nERROR\nINFO\nWARN\n", "INFO 2 WARN 2 ERROR 1"),
            ],
        ),
        # --- 199-206 modules ---
        _block_from_body(
            199, "Подключить математический модуль",
            "Прочитайте число и выведите его квадратный корень с двумя знаками. Соберите из блоков.",
            "easy",
            "uses Math;\nvar x: real;\nbegin\n  readln(x);\n  writeln(Sqrt(x):0:2);\nend.",
            topics=_MODULE_TOPICS,
            constructions=_MODULE_CONSTRUCTIONS,
            examples=_EX_MATH_SQRT,
            test_cases=[
                tc("4\n", "2.00"),
                tc("9\n", "3.00"),
                tc("2\n", "1.41"),
                tc("1\n", "1.00"),
                tc("16\n", "4.00"),
            ],
        ),
        translate_task(
            200, "Вынести функцию в модуль",
            "Вынесите функцию double(x) и выведите удвоенное число. Исправьте ошибки.",
            "medium",
            topics=_MODULE_TOPICS,
            constructions=_MODULE_CONSTRUCTIONS,
            code_examples=_EX_EXTRACT_FUNC,
            test_cases=[
                tc("5\n", "10"),
                tc("0\n", "0"),
                tc("7\n", "14"),
                tc("100\n", "200"),
                tc("1\n", "2"),
            ],
            template="var x: integer;\nbegin\n  readln(x);\n  writeln(x);\nend.",
        ),
        translate_task(
            201, "Разделить код на два файла",
            "Используйте функцию greet(name) и выведите приветствие. Переведите на Pascal.",
            "hard",
            topics=_MODULE_TOPICS,
            constructions=_MODULE_CONSTRUCTIONS,
            code_examples=_EX_TWO_FILES,
            test_cases=[
                tc("Anna\n", "Hello, Anna!"),
                tc("Bob\n", "Hello, Bob!"),
                tc("X\n", "Hello, X!"),
                tc("User\n", "Hello, User!"),
                tc("Test\n", "Hello, Test!"),
            ],
        ),
        _block_from_body(
            202, "Скрыть вспомогательную функцию",
            "Реализуйте helper(x)=x+1 внутри программы и выведите результат для x.",
            "easy",
            "function Helper(x: integer): integer;\nbegin\n  Helper:=x+1;\nend;\n"
            "var x: integer;\nbegin\n  readln(x);\n  writeln(Helper(x));\nend.",
            topics=_MODULE_TOPICS,
            constructions=_MODULE_CONSTRUCTIONS,
            examples=_EX_LOCAL_HELPER,
            test_cases=[
                tc("5\n", "6"),
                tc("0\n", "1"),
                tc("10\n", "11"),
                tc("1\n", "2"),
                tc("99\n", "100"),
            ],
        ),
        translate_task(
            203, "Модуль работы со строками",
            "Прочитайте строку и выведите её в верхнем регистре. Исправьте ошибки.",
            "medium",
            topics=_MODULE_TOPICS,
            constructions=_MODULE_CONSTRUCTIONS,
            code_examples=_EX_STR_MODULE,
            test_cases=[
                tc("hello\n", "HELLO"),
                tc("Test\n", "TEST"),
                tc("a\n", "A"),
                tc("abc\n", "ABC"),
                tc("Hi\n", "HI"),
            ],
            template="var s: string;\nbegin\n  readln(s);\n  writeln(s);\nend.",
        ),
        translate_task(
            204, "Модуль расчета скидок",
            "Прочитайте цену и процент скидки, выведите итоговую цену. Переведите на Pascal.",
            "hard",
            topics=_MODULE_TOPICS,
            constructions=_MODULE_CONSTRUCTIONS,
            code_examples=_EX_DISCOUNT_MOD,
            test_cases=[
                tc("100 10\n", "90"),
                tc("200 50\n", "100"),
                tc("50 0\n", "50"),
                tc("99 1\n", "98"),
                tc("1000 25\n", "750"),
            ],
        ),
        _block_from_body(
            205, "Модуль статистики массива",
            "Прочитайте N и N чисел, выведите сумму и максимум через пробел.",
            "easy",
            "procedure Stats(a: array of integer; n: integer; var s,m: integer);\nvar i: integer;\nbegin\n  s:=0; m:=a[0];\n"
            "  for i:=0 to n-1 do begin s:=s+a[i]; if a[i]>m then m:=a[i]; end;\nend;\n"
            "var n,i,s,m: integer; a: array of integer;\nbegin\n  readln(n); SetLength(a,n);\n"
            "  for i:=0 to n-1 do read(a[i]);\n  Stats(a,n,s,m);\n  writeln(s,' ',m);\nend.",
            topics=_MODULE_TOPICS,
            constructions=_MODULE_CONSTRUCTIONS,
            examples=_EX_ARRAY_STATS,
            test_cases=[
                tc("3\n1 2 3\n", "6 3"),
                tc("1\n5\n", "5 5"),
                tc("4\n10 20 30 40\n", "100 40"),
                tc("2\n-1 5\n", "4 5"),
                tc("5\n1 1 1 1 1\n", "5 1"),
            ],
        ),
        translate_task(
            206, "Проверочная: мини-библиотека функций",
            "Прочитайте op add/mul и два числа, выведите результат. Исправьте ошибки.",
            "medium",
            topics=_MODULE_TOPICS,
            constructions=_MODULE_CONSTRUCTIONS,
            code_examples=_EX_MINI_LIB,
            test_cases=[
                tc("add 3 4\n", "7"),
                tc("mul 3 4\n", "12"),
                tc("add 0 0\n", "0"),
                tc("mul 5 6\n", "30"),
                tc("add 100 1\n", "101"),
            ],
            template="var op: string; a,b: integer;\nbegin\n  readln(op,a,b);\n  writeln(a);\nend.",
        ),
        # --- 207-221 data structures ---
        translate_task(
            207, "Стек действий",
            "Обработайте команды push/pop до 0, при pop выводите снятое значение. Переведите на Pascal.",
            "hard",
            topics=_ds_topics(207),
            constructions=_ds_constructions(207),
            code_examples=_EX_STACK,
            test_cases=[
                tc("push 1\npush 2\npop\n0\n", "2"),
                tc("push 5\npop\n0\n", "5"),
                tc("push 1\npush 2\npush 3\npop\npop\n0\n", "3\n2"),
                tc("0\n", ""),
                tc("push 10\npush 20\npop\npop\n0\n", "20\n10"),
            ],
        ),
        _block_from_body(
            208, "Очередь клиентов",
            "Обработайте enqueue/dequeue до 0, при dequeue выводите первый элемент.",
            "easy",
            "var q: array[1..100] of integer; head,tail: integer; cmd: string; v: integer;\nbegin\n  head:=1; tail:=0;\n"
            "  while true do begin\n    readln(cmd);\n    if cmd='0' then break;\n"
            "    if cmd='enqueue' then begin readln(v); tail:=tail+1; q[tail]:=v; end\n"
            "    else if cmd='dequeue' then begin writeln(q[head]); head:=head+1; end;\n  end;\nend.",
            topics=_ds_topics(208),
            constructions=_ds_constructions(208),
            examples=_EX_QUEUE,
            test_cases=[
                tc("enqueue 1\nenqueue 2\ndequeue\n0\n", "1"),
                tc("enqueue 5\ndequeue\n0\n", "5"),
                tc("enqueue 1\nenqueue 2\ndequeue\ndequeue\n0\n", "1\n2"),
                tc("0\n", ""),
                tc("enqueue 10\nenqueue 20\ndequeue\n0\n", "10"),
            ],
        ),
        translate_task(
            209, "Проверка скобок стеком",
            "Прочитайте строку скобок и выведите valid или invalid. Исправьте ошибки.",
            "medium",
            topics=_ds_topics(209),
            constructions=_ds_constructions(209),
            code_examples=_EX_BRACKETS,
            test_cases=[
                tc("()\n", "valid"),
                tc("(())\n", "valid"),
                tc("(()\n", "invalid"),
                tc("())\n", "invalid"),
                tc("\n", "valid"),
            ],
            template="var s: string;\nbegin\n  readln(s);\n  writeln('valid');\nend.",
        ),
        translate_task(
            210, "Очередь печати",
            "Прочитайте N и N заданий, выведите их в порядке FIFO. Переведите на Pascal.",
            "hard",
            topics=_ds_topics(210),
            constructions=_ds_constructions(210),
            code_examples=_EX_PRINT_QUEUE,
            test_cases=[
                tc("3\n1 2 3\n", "1\n2\n3"),
                tc("1\n5\n", "5"),
                tc("2\n10 20\n", "10\n20"),
                tc("4\n4 3 2 1\n", "4\n3\n2\n1"),
                tc("0\n\n", ""),
            ],
        ),
        _block_from_body(
            211, "Связный список: добавление",
            "Обработайте N команд add и выведите все значения через пробел.",
            "easy",
            "var n,i,c: integer; vals: array[1..100] of integer; cmd: string; v: integer;\nbegin\n  readln(n); c:=0;\n"
            "  for i:=1 to n do begin\n    readln(cmd,v);\n    if cmd='add' then begin c:=c+1; vals[c]:=v; end;\n  end;\n"
            "  for i:=1 to c do if i<c then write(vals[i],' ') else write(vals[i]);\n  writeln;\nend.",
            topics=_ds_topics(211),
            constructions=_ds_constructions(211),
            examples=_EX_LIST_ADD,
            test_cases=[
                tc("3\nadd 1\nadd 2\nadd 3\n", "1 2 3"),
                tc("1\nadd 5\n", "5"),
                tc("2\nadd 10\nadd 20\n", "10 20"),
                tc("4\nadd 1\nadd 2\nadd 3\nadd 4\n", "1 2 3 4"),
                tc("0\n\n", ""),
            ],
        ),
        translate_task(
            212, "Связный список: поиск",
            "Прочитайте N чисел и x, выведите 1-based индекс или -1. Исправьте ошибки.",
            "medium",
            topics=_ds_topics(212),
            constructions=_ds_constructions(212),
            code_examples=_EX_LIST_FIND,
            test_cases=[
                tc("5\n1 2 3 4 5\n3\n", "3"),
                tc("3\n1 2 3\n5\n", "-1"),
                tc("1\n7\n7\n", "1"),
                tc("4\n5 5 5 5\n5\n", "1"),
                tc("2\n1 2\n3\n", "-1"),
            ],
            template="var n,i,x: integer; vals: array[1..100] of integer;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do read(vals[i]);\n  readln(x);\n  writeln(0);\nend.",
        ),
        translate_task(
            213, "Связный список: удаление",
            "Прочитайте N чисел и x, удалите x и выведите оставшиеся. Переведите на Pascal.",
            "hard",
            topics=_ds_topics(213),
            constructions=_ds_constructions(213),
            code_examples=_EX_LIST_REMOVE,
            test_cases=[
                tc("4\n1 2 3 4\n2\n", "1 3 4"),
                tc("3\n5 5 5\n5\n", ""),
                tc("2\n1 2\n1\n", "2"),
                tc("1\n7\n7\n", ""),
                tc("5\n1 2 3 2 4\n2\n", "1 3 4"),
            ],
        ),
        _block_from_body(
            214, "Дерево: создать узел",
            "Выведите простое дерево: корень A и дети B C (обход preorder).",
            "easy",
            "begin\n  writeln('A');\n  writeln('B C');\nend.",
            topics=_ds_topics(214),
            constructions=_ds_constructions(214),
            examples=_EX_TREE_PRE,
            test_cases=[
                tc("\n", "A\nB C"),
                tc("\n", "A\nB C"),
                tc("\n", "A\nB C"),
                tc("\n", "A\nB C"),
                tc("\n", "A\nB C"),
            ],
        ),
        translate_task(
            215, "Дерево: подсчет узлов",
            "Прочитайте N — число узлов дерева, выведите N. Исправьте ошибки.",
            "medium",
            topics=_ds_topics(215),
            constructions=_ds_constructions(215),
            code_examples=_EX_TREE_COUNT,
            test_cases=[
                tc("5\n", "5"),
                tc("1\n", "1"),
                tc("10\n", "10"),
                tc("0\n", "0"),
                tc("3\n", "3"),
            ],
            template="var n: integer;\nbegin\n  readln(n);\n  writeln(0);\nend.",
        ),
        translate_task(
            216, "Дерево: поиск значения",
            "Прочитайте N значений узлов и x, выведите yes/no. Переведите на Pascal.",
            "hard",
            topics=_ds_topics(216),
            constructions=_ds_constructions(216),
            code_examples=_EX_TREE_FIND,
            test_cases=[
                tc("5\n1 2 3 4 5\n3\n", "yes"),
                tc("3\n1 2 3\n5\n", "no"),
                tc("1\n7\n7\n", "yes"),
                tc("4\n0 0 0 0\n1\n", "no"),
                tc("2\n5 5\n5\n", "yes"),
            ],
        ),
        _block_from_body(
            217, "Граф матрицей смежности",
            "Прочитайте матрицу смежности и номер вершины, выведите соседей.",
            "easy",
            "var n,i,j,v: integer; mat: array[1..10,1..10] of integer; first: boolean;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do for j:=1 to n do read(mat[i,j]);\n  readln(v); first:=true;\n"
            "  for j:=1 to n do if mat[v,j]=1 then begin if not first then write(' '); write(j); first:=false; end;\n  writeln;\nend.",
            topics=_ds_topics(217),
            constructions=_ds_constructions(217),
            examples=_EX_ADJ_MATRIX,
            test_cases=[
                tc("3\n0 1 0\n1 0 1\n0 1 0\n1\n", "2 3"),
                tc("2\n0 1\n1 0\n1\n", "2"),
                tc("3\n0 0 0\n0 0 0\n0 0 0\n2\n", ""),
                tc("4\n0 1 1 0\n1 0 0 1\n1 0 0 1\n0 1 1 0\n1\n", "2 3"),
                tc("1\n0\n1\n", ""),
            ],
        ),
        translate_task(
            218, "Граф списком ребер",
            "Прочитайте M рёбер и вершину v, выведите соседей. Исправьте ошибки.",
            "medium",
            topics=_ds_topics(218),
            constructions=_ds_constructions(218),
            code_examples=_EX_EDGE_LIST,
            test_cases=[
                tc("3\n1 2\n1 3\n2 3\n1\n", "2 3"),
                tc("2\n1 2\n2 3\n2\n", "3"),
                tc("1\n1 2\n1\n", "2"),
                tc("4\n1 2\n1 3\n2 4\n3 4\n1\n", "2 3"),
                tc("0\n5\n", ""),
            ],
            template="var m,i,c,v,a,b: integer; froms,tos: array[1..100] of integer;\nbegin\n  readln(m); c:=0;\n"
            "  for i:=1 to m do begin readln(a,b); c:=c+1; froms[c]:=a; tos[c]:=b; end;\n  readln(v);\n  writeln(v);\nend.",
        ),
        translate_task(
            219, "Подсчитать степень вершины",
            "Прочитайте матрицу смежности и вершину, выведите её степень. Переведите на Pascal.",
            "hard",
            topics=_ds_topics(219),
            constructions=_ds_constructions(219),
            code_examples=_EX_VERTEX_DEGREE,
            test_cases=[
                tc("3\n0 1 0\n1 0 1\n0 1 0\n1\n", "2"),
                tc("2\n0 1\n1 0\n1\n", "1"),
                tc("3\n0 0 0\n0 0 0\n0 0 0\n2\n", "0"),
                tc("4\n0 1 1 0\n1 0 0 1\n1 0 0 1\n0 1 1 0\n1\n", "2"),
                tc("1\n0\n1\n", "0"),
            ],
        ),
        _block_from_body(
            220, "Найти соседей вершины",
            "Прочитайте матрицу смежности и вершину, выведите номера соседей.",
            "easy",
            "var n,i,j,v: integer; mat: array[1..10,1..10] of integer; first: boolean;\nbegin\n  readln(n);\n"
            "  for i:=1 to n do for j:=1 to n do read(mat[i,j]);\n  readln(v); first:=true;\n"
            "  for j:=1 to n do if mat[v,j]=1 then begin if not first then write(' '); write(j); first:=false; end;\n  writeln;\nend.",
            topics=_ds_topics(220),
            constructions=_ds_constructions(220),
            examples=_EX_NEIGHBORS,
            test_cases=[
                tc("3\n0 1 0\n1 0 1\n0 1 0\n2\n", "1 3"),
                tc("2\n0 1\n1 0\n2\n", "1"),
                tc("3\n0 0 0\n0 0 0\n0 0 0\n1\n", ""),
                tc("4\n0 1 1 0\n1 0 0 1\n1 0 0 1\n0 1 1 0\n3\n", "1 4"),
                tc("1\n0\n1\n", ""),
            ],
        ),
        translate_task(
            221, "Проверочная: маршрут по карте",
            "Прочитайте граф, start и goal — выведите yes, если goal достижим. Исправьте ошибки.",
            "medium",
            topics=_ds_topics(221),
            constructions=_ds_constructions(221),
            code_examples=_EX_BFS_ROUTE,
            test_cases=[
                tc("3 2\n1 2\n2 3\n1 3\n", "yes"),
                tc("3 1\n1 2\n1 3\n", "yes"),
                tc("3 0\n1 3\n", "no"),
                tc("2 1\n1 2\n1 2\n", "yes"),
                tc("4 2\n1 2\n3 4\n1 4\n", "no"),
            ],
            template="var n,m,i,c,start,goal,a,b: integer; froms,tos: array[1..100] of integer;\nbegin\n  readln(n,m); c:=0;\n"
            "  for i:=1 to m do begin readln(a,b); c:=c+1; froms[c]:=a; tos[c]:=b; end;\n  readln(start,goal);\n  writeln('no');\nend.",
        ),
        # --- 222-224 idiomatic data processing ---
        _block_from_body(
            222, "Пронумеровать список студентов",
            "Прочитайте N имён и выведите их в формате «1. имя».",
            "easy",
            "var n,i: integer; name: string;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(name); writeln(i,'. ',name); end;\nend.",
            topics=_idiom_topics(222),
            constructions=_IDIOM_CONSTRUCTIONS,
            examples=_EX_ENUM_STUDENTS,
            test_cases=[
                tc("3\nAnna\nBob\nCat\n", "1. Anna\n2. Bob\n3. Cat"),
                tc("1\nSolo\n", "1. Solo"),
                tc("2\nA\nB\n", "1. A\n2. B"),
                tc("4\nX\nY\nZ\nW\n", "1. X\n2. Y\n3. Z\n4. W"),
                tc("2\nIvan\nMaria\n", "1. Ivan\n2. Maria"),
            ],
        ),
        translate_task(
            223, "Сумма положительных элементов",
            "Прочитайте N и N чисел, выведите сумму положительных. Исправьте ошибки.",
            "medium",
            topics=_idiom_topics(223),
            constructions=_IDIOM_CONSTRUCTIONS,
            code_examples=_EX_SUM_POSITIVE,
            test_cases=[
                tc("5\n-1 2 -3 4 0\n", "6"),
                tc("3\n1 2 3\n", "6"),
                tc("2\n-1 -2\n", "0"),
                tc("4\n10 20 30 40\n", "100"),
                tc("1\n-5\n", "0"),
            ],
            template="var n,i,s: integer; a: array[1..100] of integer;\nbegin\n  readln(n); s:=0;\n"
            "  for i:=1 to n do begin read(a[i]); s:=s+a[i]; end;\n  writeln(s);\nend.",
        ),
        translate_task(
            224, "Все четные элементы",
            "Прочитайте N и N чисел, выведите чётные через пробел. Переведите на Pascal.",
            "hard",
            topics=_idiom_topics(224),
            constructions=_IDIOM_CONSTRUCTIONS,
            code_examples=_EX_FILTER_EVENS,
            test_cases=[
                tc("5\n1 2 3 4 5\n", "2 4"),
                tc("3\n2 4 6\n", "2 4 6"),
                tc("2\n1 3\n", ""),
                tc("4\n0 1 2 3\n", "0 2"),
                tc("1\n8\n", "8"),
            ],
        ),
    ]


COURSE_BATCH_175_224_SIZE = 50
COURSE_BATCH_175_224_CATALOG = build_course_batch_175_224_catalog()
