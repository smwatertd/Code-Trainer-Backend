"""Разделы «Идиомы», «ООП: классы», «ООП: коллекции», «ООП: наследование» — задачи 225–270."""
from __future__ import annotations

from migrations.seeds.catalog_common import (
    block_task,
    pascal_blocks_from_body,
    tc,
    translate_task,
)

TaskRow = dict

_IDIOM_CONSTRUCTIONS = [
    "map",
    "filter",
    "reduce",
    "comprehension",
    "lambda",
    "collection_iteration",
    "stdin_read",
    "stdout_write",
]

_OOP_CLASS_TOPICS = ["oop", "class_type"]
_OOP_CLASS_CONSTRUCTIONS = [
    "class_type",
    "object_instance",
    "method_dispatch",
    "typed_declaration",
    "stdin_read",
    "stdout_write",
]

_OOP_COLL_TOPICS = ["oop", "object_instance"]
_OOP_COLL_CONSTRUCTIONS = [
    "class_type",
    "object_instance",
    "method_dispatch",
    "collection_iteration",
    "filter_select",
    "sort_order",
]

_OOP_INH_TOPICS = ["oop", "inheritance_hierarchy"]
_OOP_INH_CONSTRUCTIONS = [
    "inheritance_hierarchy",
    "class_type",
    "method_dispatch",
    "object_instance",
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


def _idiom_topics(task_id: int) -> list[str]:
    kinds = ["map", "filter", "reduce"]
    return ["idioms", kinds[(task_id - 225) % 3]]


# --- idiom examples ---

_EX_C_TO_F = _stub(
    "n = int(input())\ntemps = list(map(int, input().split()))\n"
    "f = [c * 9 // 5 + 32 for c in temps]\nprint(' '.join(map(str, f)))",
    "var n,i,c,f: integer;\nbegin\n  readln(n); c:=0;\n"
    "  for i:=1 to n do begin read(c); f:=c*9 div 5+32; if i<n then write(f,' ') else write(f); end;\n  writeln;\nend.",
)

_EX_FILTER_ADULTS = _stub(
    "n = int(input())\nadults = []\nfor _ in range(n):\n    name, age = input().split(); age = int(age)\n"
    "    if age >= 18:\n        adults.append(name)\nprint('\\n'.join(adults))",
    "var n,i,age: integer; name: string;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do begin readln(name,age); if age>=18 then writeln(name); end;\nend.",
)

_EX_MAP_NAMES = _stub(
    "n = int(input())\nnames = [input().split()[0] for _ in range(n)]\nprint('\\n'.join(names))",
    "var n,i: integer; line,name: string;\nbegin\n  readln(n);\n"
    "  for i:=1 to n do begin readln(line); name:=copy(line,1,pos(' ',line)-1); writeln(name); end;\nend.",
)

_EX_MAX_PRICE = _stub(
    "n = int(input())\nprices = [int(input()) for _ in range(n)]\nprint(max(prices))",
    "var n,i,maxp,price: integer;\nbegin\n  readln(n); maxp:=-maxint;\n"
    "  for i:=1 to n do begin readln(price); if price>maxp then maxp:=price; end;\n  writeln(maxp);\nend.",
)

_EX_UNIQUE_WORDS = _stub(
    "words = input().split()\nprint(len(set(words)))",
    "var text,word: string; i,n,c: integer; words: array[1..100] of string; found: boolean; j: integer;\n"
    "function HasWord(w: string): boolean;\nvar k: integer;\nbegin\n  HasWord:=false;\n  for k:=1 to c do if words[k]=w then HasWord:=true;\nend;\n"
    "begin\n  readln(text); c:=0; n:=length(text); i:=1;\n"
    "  while i<=n do begin\n    while (i<=n) and (text[i]=' ') do i:=i+1;\n    if i>n then break;\n"
    "    word:=''; while (i<=n) and (text[i]<>' ') do begin word:=word+text[i]; i:=i+1; end;\n"
    "    if not HasWord(word) then begin c:=c+1; words[c]:=word; end;\n  end;\n  writeln(c);\nend.",
)

_EX_PLAYER_RANK = _stub(
    "n = int(input())\nplayers = []\nfor _ in range(n):\n    name, score = input().split(); players.append((name, int(score)))\n"
    "players.sort(key=lambda x: -x[1])\nfor i, (name, score) in enumerate(players, 1):\n    print(f'{i}. {name} {score}')",
    "var n,i,j,k: integer; names: array[1..100] of string; scores: array[1..100] of integer;\n"
    "    name: string; score,t: integer; tmpn: string;\n"
    "begin\n  readln(n);\n  for i:=1 to n do begin readln(name,score); names[i]:=name; scores[i]:=score; end;\n"
    "  for i:=1 to n-1 do for j:=1 to n-i do if scores[j]<scores[j+1] then begin\n"
    "    t:=scores[j]; scores[j]:=scores[j+1]; scores[j+1]:=t;\n"
    "    tmpn:=names[j]; names[j]:=names[j+1]; names[j+1]:=tmpn; end;\n"
    "  for k:=1 to n do writeln(k,'. ',names[k],' ',scores[k]);\nend.",
)

_EX_SORT_PRODUCTS = _stub(
    "n = int(input())\nitems = []\nfor _ in range(n):\n    name, price = input().split(); items.append((name, int(price)))\n"
    "items.sort(key=lambda x: x[1])\nfor name, price in items:\n    print(f'{name} {price}')",
    "var n,i,j: integer; names: array[1..100] of string; prices: array[1..100] of integer;\n"
    "    name: string; price,t: integer; tmpn: string;\n"
    "begin\n  readln(n);\n  for i:=1 to n do begin readln(name,price); names[i]:=name; prices[i]:=price; end;\n"
    "  for i:=1 to n-1 do for j:=1 to n-i do if prices[j]>prices[j+1] then begin\n"
    "    t:=prices[j]; prices[j]:=prices[j+1]; prices[j+1]:=t;\n"
    "    tmpn:=names[j]; names[j]:=names[j+1]; names[j+1]:=tmpn; end;\n"
    "  for i:=1 to n do writeln(names[i],' ',prices[i]);\nend.",
)

_EX_MOST_FREQUENT = _stub(
    "n = int(input())\nids = [input().strip() for _ in range(n)]\nfrom collections import Counter\n"
    "print(Counter(ids).most_common(1)[0][0])",
    "var n,i,j,c,bestc: integer; ids: array[1..100] of string; id: string; cnt: array[1..100] of integer;\n"
    "begin\n  readln(n);\n  for i:=1 to n do begin readln(id); ids[i]:=id; cnt[i]:=0; end;\n"
    "  for i:=1 to n do for j:=1 to n do if ids[i]=ids[j] then cnt[i]:=cnt[i]+1;\n"
    "  bestc:=1;\n  for i:=2 to n do if cnt[i]>cnt[bestc] then bestc:=i;\n  writeln(ids[bestc]);\nend.",
)

_EX_AVG_SCORE = _stub(
    "n = int(input())\nscores = list(map(int, input().split()))\nprint(f'{sum(scores) / n:.1f}')",
    "var n,i,total,score: integer; avg: real;\nbegin\n  readln(n); total:=0;\n"
    "  for i:=1 to n do begin read(score); total:=total+score; end;\n  avg:=total/n; writeln(avg:0:1);\nend.",
)

_EX_GROUP_GRADES = _stub(
    "n = int(input())\ngroups = {}\nfor _ in range(n):\n    name, grade = input().split()\n    groups.setdefault(grade, []).append(name)\n"
    "for grade in sorted(groups, key=int):\n    print(f'{grade}: {\" \".join(groups[grade])}')",
    "var n,i,j,c,g,idx: integer; names: array[1..100] of string; grades: array[1..100] of integer;\n"
    "    name: string; grade: integer; gvals: array[1..10] of integer; gc: integer; found: boolean;\n"
    "begin\n  readln(n);\n  for i:=1 to n do begin readln(name,grade); names[i]:=name; grades[i]:=grade; end;\n"
    "  gc:=0;\n  for i:=1 to n do begin\n    found:=false;\n    for j:=1 to gc do if gvals[j]=grades[i] then found:=true;\n"
    "    if not found then begin gc:=gc+1; gvals[gc]:=grades[i]; end;\n  end;\n"
    "  for i:=1 to gc-1 do for j:=1 to gc-i do if gvals[j]>gvals[j+1] then begin g:=gvals[j]; gvals[j]:=gvals[j+1]; gvals[j+1]:=g; end;\n"
    "  for idx:=1 to gc do begin\n    g:=gvals[idx]; write(g,': '); c:=0;\n"
    "    for i:=1 to n do if grades[i]=g then begin c:=c+1; if c>1 then write(' '); write(names[i]); end;\n    writeln;\n  end;\nend.",
)

_EX_ORDER_REPORT = _stub(
    "n = int(input())\namounts = [int(input()) for _ in range(n)]\nprint(f'{sum(amounts)} {len(amounts)}')",
    "var n,i,total,amount: integer;\nbegin\n  readln(n); total:=0;\n"
    "  for i:=1 to n do begin readln(amount); total:=total+amount; end;\n  writeln(total,' ',n);\nend.",
)

_EX_SHOP_ANALYTICS = _stub(
    "n = int(input())\ntotal = 0\nprices = []\nfor _ in range(n):\n    price, qty = map(int, input().split())\n    total += price * qty\n    prices.append(price)\n"
    "print(f'{total} {n} {sum(prices) / n:.1f}')",
    "var n,i,price,qty,total: integer; sumpr: int64; avg: real;\nbegin\n  readln(n); total:=0; sumpr:=0;\n"
    "  for i:=1 to n do begin readln(price,qty); total:=total+price*qty; sumpr:=sumpr+price; end;\n"
    "  avg:=sumpr/n; writeln(total,' ',n,' ',avg:0:1);\nend.",
)

# --- OOP class examples ---

_EX_PRODUCT_CLASS = _stub(
    "class Product:\n    def __init__(self, name, price):\n        self.name = name\n        self.price = price\n"
    "    def print_info(self):\n        print(f'{self.name} {self.price}')\n"
    "name, price = input().split()\np = Product(name, int(price))\np.print_info()",
    "type\n  TProduct = class\n    Name: string;\n    Price: integer;\n    constructor Create(aName: string; aPrice: integer);\n"
    "    procedure PrintInfo;\n  end;\n"
    "constructor TProduct.Create(aName: string; aPrice: integer);\nbegin\n  Name:=aName; Price:=aPrice;\nend;\n"
    "procedure TProduct.PrintInfo;\nbegin\n  writeln(Name,' ',Price);\nend;\n"
    "var p: TProduct; name: string; price: integer;\nbegin\n  readln(name,price);\n  p:=TProduct.Create(name,price);\n  p.PrintInfo;\n  p.Free;\nend.",
)

_EX_CREATE_PRODUCT = _stub(
    "class Product:\n    def __init__(self, name, price):\n        self.name = name\n        self.price = price\n"
    "    def print_info(self):\n        print(f'Product: {self.name}')\n"
    "name = input().strip()\np = Product(name, 0)\np.print_info()",
    "type\n  TProduct = class\n    Name: string;\n    constructor Create(aName: string);\n    procedure PrintInfo;\n  end;\n"
    "constructor TProduct.Create(aName: string);\nbegin\n  Name:=aName;\nend;\n"
    "procedure TProduct.PrintInfo;\nbegin\n  writeln('Product: ',Name);\nend;\n"
    "var p: TProduct; name: string;\nbegin\n  readln(name);\n  p:=TProduct.Create(name);\n  p.PrintInfo;\n  p.Free;\nend.",
)

_EX_PRODUCT_DISCOUNT = _stub(
    "class Product:\n    def __init__(self, price):\n        self.price = price\n    def get_price(self, discount):\n        return self.price * (100 - discount) // 100\n"
    "price, discount = map(int, input().split())\np = Product(price)\nprint(p.get_price(discount))",
    "type\n  TProduct = class\n    Price: integer;\n    constructor Create(aPrice: integer);\n    function GetPrice(discount: integer): integer;\n  end;\n"
    "constructor TProduct.Create(aPrice: integer);\nbegin\n  Price:=aPrice;\nend;\n"
    "function TProduct.GetPrice(discount: integer): integer;\nbegin\n  GetPrice:=Price*(100-discount) div 100;\nend;\n"
    "var p: TProduct; price,discount: integer;\nbegin\n  readln(price,discount);\n  p:=TProduct.Create(price);\n  writeln(p.GetPrice(discount));\n  p.Free;\nend.",
)

_EX_STUDENT_CLASS = _stub(
    "class Student:\n    def __init__(self, name, score):\n        self.name = name\n        self.score = score\n"
    "    def print_info(self):\n        print(f'{self.name} {self.score}')\n"
    "name, score = input().split()\ns = Student(name, int(score))\ns.print_info()",
    "type\n  TStudent = class\n    Name: string;\n    Score: integer;\n    constructor Create(aName: string; aScore: integer);\n    procedure PrintInfo;\n  end;\n"
    "constructor TStudent.Create(aName: string; aScore: integer);\nbegin\n  Name:=aName; Score:=aScore;\nend;\n"
    "procedure TStudent.PrintInfo;\nbegin\n  writeln(Name,' ',Score);\nend;\n"
    "var s: TStudent; name: string; score: integer;\nbegin\n  readln(name,score);\n  s:=TStudent.Create(name,score);\n  s.PrintInfo;\n  s.Free;\nend.",
)

_EX_BANK_ACCOUNT = _stub(
    "class BankAccount:\n    def __init__(self, balance=0):\n        self.balance = balance\n    def show(self):\n        print(self.balance)\n"
    "balance = int(input())\nacc = BankAccount(balance)\nacc.show()",
    "type\n  TBankAccount = class\n    Balance: integer;\n    constructor Create(aBalance: integer);\n    procedure Show;\n  end;\n"
    "constructor TBankAccount.Create(aBalance: integer);\nbegin\n  Balance:=aBalance;\nend;\n"
    "procedure TBankAccount.Show;\nbegin\n  writeln(Balance);\nend;\n"
    "var acc: TBankAccount; balance: integer;\nbegin\n  readln(balance);\n  acc:=TBankAccount.Create(balance);\n  acc.Show;\n  acc.Free;\nend.",
)

_EX_PRODUCT_INIT = _stub(
    "class Product:\n    def __init__(self, name, price, qty):\n        self.name = name\n        self.price = price\n        self.qty = qty\n"
    "    def describe(self):\n        print(f'{self.name} {self.price} {self.qty}')\n"
    "name, price, qty = input().split()\np = Product(name, int(price), int(qty))\np.describe()",
    "type\n  TProduct = class\n    Name: string;\n    Price,Qty: integer;\n    constructor Create(aName: string; aPrice,aQty: integer);\n    procedure Describe;\n  end;\n"
    "constructor TProduct.Create(aName: string; aPrice,aQty: integer);\nbegin\n  Name:=aName; Price:=aPrice; Qty:=aQty;\nend;\n"
    "procedure TProduct.Describe;\nbegin\n  writeln(Name,' ',Price,' ',Qty);\nend;\n"
    "var p: TProduct; name: string; price,qty: integer;\nbegin\n  readln(name,price,qty);\n  p:=TProduct.Create(name,price,qty);\n  p.Describe;\n  p.Free;\nend.",
)

_EX_ACCOUNT_OPS = _stub(
    "class BankAccount:\n    def __init__(self, balance):\n        self.balance = balance\n    def deposit(self, amount):\n        self.balance += amount\n    def withdraw(self, amount):\n        self.balance -= amount\n"
    "balance, dep, wit = map(int, input().split())\nacc = BankAccount(balance)\nacc.deposit(dep)\nacc.withdraw(wit)\nprint(acc.balance)",
    "type\n  TBankAccount = class\n    Balance: integer;\n    constructor Create(aBalance: integer);\n    procedure Deposit(amount: integer);\n    procedure Withdraw(amount: integer);\n  end;\n"
    "constructor TBankAccount.Create(aBalance: integer);\nbegin\n  Balance:=aBalance;\nend;\n"
    "procedure TBankAccount.Deposit(amount: integer);\nbegin\n  Balance:=Balance+amount;\nend;\n"
    "procedure TBankAccount.Withdraw(amount: integer);\nbegin\n  Balance:=Balance-amount;\nend;\n"
    "var acc: TBankAccount; balance,dep,wit: integer;\nbegin\n  readln(balance,dep,wit);\n  acc:=TBankAccount.Create(balance);\n  acc.Deposit(dep); acc.Withdraw(wit);\n  writeln(acc.Balance);\n  acc.Free;\nend.",
)

_EX_N_OBJECTS = _stub(
    "class Item:\n    pass\nn = int(input())\nitems = [Item() for _ in range(n)]\nprint(len(items))",
    "type\n  TItem = class\n  end;\n"
    "var n,i,c: integer; items: array[1..100] of TItem;\nbegin\n  readln(n); c:=0;\n"
    "  for i:=1 to n do begin items[i]:=TItem.Create; c:=c+1; end;\n  writeln(c);\n"
    "  for i:=1 to n do items[i].Free;\nend.",
)

_EX_RECTANGLE = _stub(
    "class Rectangle:\n    def __init__(self, w, h):\n        self.w = w\n        self.h = h\n    def area(self):\n        return self.w * self.h\n"
    "w, h = map(int, input().split())\nr = Rectangle(w, h)\nprint(r.area())",
    "type\n  TRectangle = class\n    W,H: integer;\n    constructor Create(aW,aH: integer);\n    function Area: integer;\n  end;\n"
    "constructor TRectangle.Create(aW,aH: integer);\nbegin\n  W:=aW; H:=aH;\nend;\n"
    "function TRectangle.Area: integer;\nbegin\n  Area:=W*H;\nend;\n"
    "var r: TRectangle; w,h: integer;\nbegin\n  readln(w,h);\n  r:=TRectangle.Create(w,h);\n  writeln(r.Area);\n  r.Free;\nend.",
)

_EX_TIMER = _stub(
    "class Timer:\n    def __init__(self, seconds):\n        self.seconds = seconds\n    def tick(self):\n        self.seconds -= 1\n        return self.seconds\n"
    "start = int(input())\nt = Timer(start)\nfor _ in range(2):\n    print(t.tick())",
    "type\n  TTimer = class\n    Seconds: integer;\n    constructor Create(aSeconds: integer);\n    function Tick: integer;\n  end;\n"
    "constructor TTimer.Create(aSeconds: integer);\nbegin\n  Seconds:=aSeconds;\nend;\n"
    "function TTimer.Tick: integer;\nbegin\n  Seconds:=Seconds-1;\n  Tick:=Seconds;\nend;\n"
    "var t: TTimer; start: integer; i: integer;\nbegin\n  readln(start);\n  t:=TTimer.Create(start);\n  for i:=1 to 2 do writeln(t.Tick);\n  t.Free;\nend.",
)

_EX_ORDER_CLASS = _stub(
    "class Order:\n    def __init__(self, total):\n        self.total = total\n    def show(self):\n        print(f'Total: {self.total}')\n"
    "total = int(input())\no = Order(total)\no.show()",
    "type\n  TOrder = class\n    Total: integer;\n    constructor Create(aTotal: integer);\n    procedure Show;\n  end;\n"
    "constructor TOrder.Create(aTotal: integer);\nbegin\n  Total:=aTotal;\nend;\n"
    "procedure TOrder.Show;\nbegin\n  writeln('Total: ',Total);\nend;\n"
    "var o: TOrder; total: integer;\nbegin\n  readln(total);\n  o:=TOrder.Create(total);\n  o.Show;\n  o.Free;\nend.",
)

_EX_USER_CLASS = _stub(
    "class User:\n    def __init__(self, login, password):\n        self.login = login\n        self.password = password\n    def check(self, login, password):\n        return self.login == login and self.password == password\n"
    "login, pwd = input().split()\nu = User(login, pwd)\nprint('yes' if u.check(login, pwd) else 'no')",
    "type\n  TUser = class\n    Login,Password: string;\n    constructor Create(aLogin,aPassword: string);\n    function Check(aLogin,aPassword: string): boolean;\n  end;\n"
    "constructor TUser.Create(aLogin,aPassword: string);\nbegin\n  Login:=aLogin; Password:=aPassword;\nend;\n"
    "function TUser.Check(aLogin,aPassword: string): boolean;\nbegin\n  Check:=(Login=aLogin) and (Password=aPassword);\nend;\n"
    "var u: TUser; login,pwd: string;\nbegin\n  readln(login,pwd);\n  u:=TUser.Create(login,pwd);\n  if u.Check(login,pwd) then writeln('yes') else writeln('no');\n  u.Free;\nend.",
)

_EX_BOOK_CLASS = _stub(
    "class Book:\n    def __init__(self, title, author):\n        self.title = title\n        self.author = author\n    def print_info(self):\n        print(f'{self.title} / {self.author}')\n"
    "title, author = input().split(maxsplit=1)\nb = Book(title, author)\nb.print_info()",
    "type\n  TBook = class\n    Title,Author: string;\n    constructor Create(aTitle,aAuthor: string);\n    procedure PrintInfo;\n  end;\n"
    "constructor TBook.Create(aTitle,aAuthor: string);\nbegin\n  Title:=aTitle; Author:=aAuthor;\nend;\n"
    "procedure TBook.PrintInfo;\nbegin\n  writeln(Title,' / ',Author);\nend;\n"
    "var b: TBook; title,author: string;\nbegin\n  readln(title,author);\n  b:=TBook.Create(title,author);\n  b.PrintInfo;\n  b.Free;\nend.",
)

_EX_PRODUCT_CARD = _stub(
    "class Product:\n    def __init__(self, name, price, category):\n        self.name = name\n        self.price = price\n        self.category = category\n    def card(self):\n        print(f'[{self.category}] {self.name}: {self.price}')\n"
    "name, price, cat = input().split()\np = Product(name, int(price), cat)\np.card()",
    "type\n  TProduct = class\n    Name,Category: string;\n    Price: integer;\n    constructor Create(aName: string; aPrice: integer; aCategory: string);\n    procedure Card;\n  end;\n"
    "constructor TProduct.Create(aName: string; aPrice: integer; aCategory: string);\nbegin\n  Name:=aName; Price:=aPrice; Category:=aCategory;\nend;\n"
    "procedure TProduct.Card;\nbegin\n  writeln('[',Category,'] ',Name,': ',Price);\nend;\n"
    "var p: TProduct; name,cat: string; price: integer;\nbegin\n  readln(name,price,cat);\n  p:=TProduct.Create(name,price,cat);\n  p.Card;\n  p.Free;\nend.",
)

# --- OOP collection examples ---

_EX_STUDENT_LIST = _stub(
    "class Student:\n    def __init__(self, name, score):\n        self.name = name\n        self.score = score\n"
    "    def show(self):\n        print(f'{self.name} {self.score}')\n"
    "n = int(input())\nstudents = []\nfor _ in range(n):\n    name, score = input().split(); students.append(Student(name, int(score)))\n"
    "for s in students:\n    s.show()",
    "type\n  TStudent = class\n    Name: string; Score: integer;\n    constructor Create(aName: string; aScore: integer);\n    procedure Show;\n  end;\n"
    "constructor TStudent.Create(aName: string; aScore: integer);\nbegin Name:=aName; Score:=aScore; end;\n"
    "procedure TStudent.Show;\nbegin writeln(Name,' ',Score); end;\n"
    "var n,i: integer; students: array[1..100] of TStudent; name: string; score: integer;\n"
    "begin\n  readln(n);\n  for i:=1 to n do begin readln(name,score); students[i]:=TStudent.Create(name,score); end;\n"
    "  for i:=1 to n do students[i].Show;\n  for i:=1 to n do students[i].Free;\nend.",
)

_EX_BEST_STUDENT = _stub(
    "class Student:\n    def __init__(self, name, score):\n        self.name = name\n        self.score = score\n"
    "n = int(input())\nbest = None\nfor _ in range(n):\n    name, score = input().split(); s = Student(name, int(score))\n"
    "    if best is None or s.score > best.score:\n        best = s\nprint(f'{best.name} {best.score}')",
    "type\n  TStudent = class\n    Name: string; Score: integer;\n    constructor Create(aName: string; aScore: integer);\n  end;\n"
    "constructor TStudent.Create(aName: string; aScore: integer);\nbegin Name:=aName; Score:=aScore; end;\n"
    "var n,i: integer; name: string; score,bestScore: integer; bestName: string;\n"
    "begin\n  readln(n); bestScore:=-maxint;\n  for i:=1 to n do begin readln(name,score); if score>bestScore then begin bestScore:=score; bestName:=name; end; end;\n"
    "  writeln(bestName,' ',bestScore);\nend.",
)

_EX_SORT_PRODUCTS_LIST = _stub(
    "class Product:\n    def __init__(self, name, price):\n        self.name = name\n        self.price = price\n"
    "n = int(input())\nitems = []\nfor _ in range(n):\n    name, price = input().split(); items.append(Product(name, int(price)))\n"
    "items.sort(key=lambda p: p.price)\nfor p in items:\n    print(f'{p.name} {p.price}')",
    "type\n  TProduct = class\n    Name: string; Price: integer;\n    constructor Create(aName: string; aPrice: integer);\n  end;\n"
    "constructor TProduct.Create(aName: string; aPrice: integer);\nbegin Name:=aName; Price:=aPrice; end;\n"
    "var n,i,j: integer; names: array[1..100] of string; prices: array[1..100] of integer;\n    name: string; price,t: integer; tmpn: string;\n"
    "begin\n  readln(n);\n  for i:=1 to n do begin readln(name,price); names[i]:=name; prices[i]:=price; end;\n"
    "  for i:=1 to n-1 do for j:=1 to n-i do if prices[j]>prices[j+1] then begin\n"
    "    t:=prices[j]; prices[j]:=prices[j+1]; prices[j+1]:=t;\n    tmpn:=names[j]; names[j]:=names[j+1]; names[j+1]:=tmpn; end;\n"
    "  for i:=1 to n do writeln(names[i],' ',prices[i]);\nend.",
)

_EX_FILTER_ACTIVE = _stub(
    "class User:\n    def __init__(self, name, active):\n        self.name = name\n        self.active = active == 'yes'\n"
    "n = int(input())\nusers = []\nfor _ in range(n):\n    name, active = input().split(); users.append(User(name, active))\n"
    "for u in users:\n    if u.active:\n        print(u.name)",
    "type\n  TUser = class\n    Name: string; Active: boolean;\n    constructor Create(aName: string; aActive: boolean);\n  end;\n"
    "constructor TUser.Create(aName: string; aActive: boolean);\nbegin Name:=aName; Active:=aActive; end;\n"
    "var n,i: integer; name,flag: string;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(name,flag); if flag='yes' then writeln(name); end;\nend.",
)

_EX_CART = _stub(
    "class Cart:\n    def __init__(self):\n        self.items = []\n    def add(self, price):\n        self.items.append(price)\n    def remove(self):\n        if self.items: self.items.pop()\n    def total(self):\n        return sum(self.items)\n"
    "ops = []\nwhile True:\n    line = input().strip()\n    if line == 'done': break\n    ops.append(line)\n"
    "c = Cart()\nfor op in ops:\n    if op == 'add': c.add(int(input()))\n    elif op == 'remove': c.remove()\nprint(c.total())",
    "type\n  TCart = class\n    Count: integer; Items: array[1..100] of integer;\n    constructor Create;\n    procedure Add(price: integer);\n    procedure RemoveItem;\n    function Total: integer;\n  end;\n"
    "constructor TCart.Create;\nbegin Count:=0; end;\n"
    "procedure TCart.Add(price: integer);\nbegin Count:=Count+1; Items[Count]:=price; end;\n"
    "procedure TCart.RemoveItem;\nbegin if Count>0 then Count:=Count-1; end;\n"
    "function TCart.Total: integer;\nvar i,s: integer;\nbegin s:=0; for i:=1 to Count do s:=s+Items[i]; Total:=s; end;\n"
    "var cart: TCart; cmd: string; price: integer;\n"
    "begin\n  cart:=TCart.Create;\n  while true do begin readln(cmd); if cmd='done' then break;\n"
    "    if cmd='add' then begin readln(price); cart.Add(price); end\n    else if cmd='remove' then cart.RemoveItem; end;\n  writeln(cart.Total); cart.Free;\nend.",
)

_EX_DEPOSIT = _stub(
    "class BankAccount:\n    def __init__(self, balance):\n        self.balance = balance\n    def deposit(self, amount):\n        self.balance += amount\n"
    "balance, amount = map(int, input().split())\nacc = BankAccount(balance)\nacc.deposit(amount)\nprint(acc.balance)",
    "type\n  TBankAccount = class\n    Balance: integer;\n    constructor Create(aBalance: integer);\n    procedure Deposit(amount: integer);\n  end;\n"
    "constructor TBankAccount.Create(aBalance: integer);\nbegin Balance:=aBalance; end;\n"
    "procedure TBankAccount.Deposit(amount: integer);\nbegin Balance:=Balance+amount; end;\n"
    "var acc: TBankAccount; balance,amount: integer;\nbegin\n  readln(balance,amount);\n  acc:=TBankAccount.Create(balance);\n  acc.Deposit(amount);\n  writeln(acc.Balance);\n  acc.Free;\nend.",
)

_EX_WITHDRAW = _stub(
    "class BankAccount:\n    def __init__(self, balance):\n        self.balance = balance\n    def withdraw(self, amount):\n        if amount <= self.balance:\n            self.balance -= amount\n"
    "balance, amount = map(int, input().split())\nacc = BankAccount(balance)\nacc.withdraw(amount)\nprint(acc.balance)",
    "type\n  TBankAccount = class\n    Balance: integer;\n    constructor Create(aBalance: integer);\n    procedure Withdraw(amount: integer);\n  end;\n"
    "constructor TBankAccount.Create(aBalance: integer);\nbegin Balance:=aBalance; end;\n"
    "procedure TBankAccount.Withdraw(amount: integer);\nbegin if amount<=Balance then Balance:=Balance-amount; end;\n"
    "var acc: TBankAccount; balance,amount: integer;\nbegin\n  readln(balance,amount);\n  acc:=TBankAccount.Create(balance);\n  acc.Withdraw(amount);\n  writeln(acc.Balance);\n  acc.Free;\nend.",
)

_EX_ORDER_LOG = _stub(
    "class Order:\n    def __init__(self, oid, total):\n        self.oid = oid\n        self.total = total\n    def show(self):\n        print(f'{self.oid} {self.total}')\n"
    "n = int(input())\norders = []\nfor _ in range(n):\n    oid, total = input().split(); orders.append(Order(oid, int(total)))\n"
    "for o in orders:\n    o.show()",
    "type\n  TOrder = class\n    Id: string; Total: integer;\n    constructor Create(aId: string; aTotal: integer);\n    procedure Show;\n  end;\n"
    "constructor TOrder.Create(aId: string; aTotal: integer);\nbegin Id:=aId; Total:=aTotal; end;\n"
    "procedure TOrder.Show;\nbegin writeln(Id,' ',Total); end;\n"
    "var n,i: integer; oid: string; total: integer; orders: array[1..100] of TOrder;\n"
    "begin\n  readln(n);\n  for i:=1 to n do begin readln(oid,total); orders[i]:=TOrder.Create(oid,total); end;\n"
    "  for i:=1 to n do orders[i].Show;\n  for i:=1 to n do orders[i].Free;\nend.",
)

_EX_BOOK_CATALOG = _stub(
    "class Book:\n    def __init__(self, title):\n        self.title = title\n"
    "n = int(input())\nbooks = []\nfor _ in range(n):\n    cmd = input().strip()\n    if cmd == 'add': books.append(Book(input().strip()))\n"
    "for b in books:\n    print(b.title)",
    "type\n  TBook = class\n    Title: string;\n    constructor Create(aTitle: string);\n  end;\n"
    "constructor TBook.Create(aTitle: string);\nbegin Title:=aTitle; end;\n"
    "var n,i,c: integer; cmd,title: string; books: array[1..100] of TBook;\n"
    "begin\n  readln(n); c:=0;\n  for i:=1 to n do begin readln(cmd); if cmd='add' then begin readln(title); c:=c+1; books[c]:=TBook.Create(title); end; end;\n"
    "  for i:=1 to c do writeln(books[i].Title);\n  for i:=1 to c do books[i].Free;\nend.",
)

_EX_MINI_SHOP = _stub(
    "class Product:\n    def __init__(self, name, price, qty):\n        self.name = name\n        self.price = price\n        self.qty = qty\n"
    "n = int(input())\nproducts = []\nfor _ in range(n):\n    name, price, qty = input().split(); products.append(Product(name, int(price), int(qty)))\n"
    "total = sum(p.price * p.qty for p in products)\ncount = sum(1 for p in products if p.qty > 0)\nprint(f'{total} {count}')",
    "type\n  TProduct = class\n    Name: string; Price,Qty: integer;\n    constructor Create(aName: string; aPrice,aQty: integer);\n  end;\n"
    "constructor TProduct.Create(aName: string; aPrice,aQty: integer);\nbegin Name:=aName; Price:=aPrice; Qty:=aQty; end;\n"
    "var n,i,total,count: integer; name: string; price,qty: integer; products: array[1..100] of TProduct;\n"
    "begin\n  readln(n); total:=0; count:=0;\n  for i:=1 to n do begin readln(name,price,qty); products[i]:=TProduct.Create(name,price,qty);\n"
    "    total:=total+price*qty; if qty>0 then count:=count+1; end;\n  writeln(total,' ',count);\n  for i:=1 to n do products[i].Free;\nend.",
)

# --- OOP inheritance examples ---

_EX_MANAGER = _stub(
    "class Employee:\n    def __init__(self, name, salary):\n        self.name = name\n        self.salary = salary\n"
    "class Manager(Employee):\n    def __init__(self, name, salary, bonus):\n        super().__init__(name, salary)\n        self.bonus = bonus\n    def total(self):\n        return self.salary + self.bonus\n"
    "name, salary, bonus = input().split()\nm = Manager(name, int(salary), int(bonus))\nprint(f'{m.name} {m.total()}')",
    "type\n  TEmployee = class\n    Name: string; Salary: integer;\n    constructor Create(aName: string; aSalary: integer);\n  end;\n"
    "  TManager = class(TEmployee)\n    Bonus: integer;\n    constructor Create(aName: string; aSalary,aBonus: integer);\n    function Total: integer;\n  end;\n"
    "constructor TEmployee.Create(aName: string; aSalary: integer);\nbegin Name:=aName; Salary:=aSalary; end;\n"
    "constructor TManager.Create(aName: string; aSalary,aBonus: integer);\nbegin inherited Create(aName,aSalary); Bonus:=aBonus; end;\n"
    "function TManager.Total: integer;\nbegin Total:=Salary+Bonus; end;\n"
    "var m: TManager; name: string; salary,bonus: integer;\n"
    "begin\n  readln(name,salary,bonus);\n  m:=TManager.Create(name,salary,bonus);\n  writeln(m.Name,' ',m.Total);\n  m.Free;\nend.",
)

_EX_CAR = _stub(
    "class Vehicle:\n    def __init__(self, brand):\n        self.brand = brand\n"
    "class Car(Vehicle):\n    def __init__(self, brand, model):\n        super().__init__(brand)\n        self.model = model\n    def info(self):\n        print(f'{self.brand} {self.model}')\n"
    "brand, model = input().split()\nc = Car(brand, model)\nc.info()",
    "type\n  TVehicle = class\n    Brand: string;\n    constructor Create(aBrand: string);\n  end;\n"
    "  TCar = class(TVehicle)\n    Model: string;\n    constructor Create(aBrand,aModel: string);\n    procedure Info;\n  end;\n"
    "constructor TVehicle.Create(aBrand: string);\nbegin Brand:=aBrand; end;\n"
    "constructor TCar.Create(aBrand,aModel: string);\nbegin inherited Create(aBrand); Model:=aModel; end;\n"
    "procedure TCar.Info;\nbegin writeln(Brand,' ',Model); end;\n"
    "var c: TCar; brand,model: string;\nbegin\n  readln(brand,model);\n  c:=TCar.Create(brand,model);\n  c.Info;\n  c.Free;\nend.",
)

_EX_DOG = _stub(
    "class Animal:\n    def __init__(self, name):\n        self.name = name\n    def speak(self):\n        return '...'\n"
    "class Dog(Animal):\n    def speak(self):\n        return 'Woof'\n"
    "name = input().strip()\nd = Dog(name)\nprint(f'{d.name}: {d.speak()}')",
    "type\n  TAnimal = class\n    Name: string;\n    constructor Create(aName: string);\n    function Speak: string; virtual;\n  end;\n"
    "  TDog = class(TAnimal)\n    function Speak: string; override;\n  end;\n"
    "constructor TAnimal.Create(aName: string);\nbegin Name:=aName; end;\n"
    "function TAnimal.Speak: string;\nbegin Speak:='...'; end;\n"
    "function TDog.Speak: string;\nbegin Speak:='Woof'; end;\n"
    "var d: TDog; name: string;\nbegin\n  readln(name);\n  d:=TDog.Create(name);\n  writeln(d.Name,': ',d.Speak);\n  d.Free;\nend.",
)

_EX_SHAPE_RECT = _stub(
    "class Shape:\n    pass\n"
    "class Rectangle(Shape):\n    def __init__(self, w, h):\n        self.w = w\n        self.h = h\n    def area(self):\n        return self.w * self.h\n"
    "w, h = map(int, input().split())\nr = Rectangle(w, h)\nprint(r.area())",
    "type\n  TShape = class\n  end;\n"
    "  TRectangle = class(TShape)\n    W,H: integer;\n    constructor Create(aW,aH: integer);\n    function Area: integer;\n  end;\n"
    "constructor TRectangle.Create(aW,aH: integer);\nbegin W:=aW; H:=aH; end;\n"
    "function TRectangle.Area: integer;\nbegin Area:=W*H; end;\n"
    "var r: TRectangle; w,h: integer;\nbegin\n  readln(w,h);\n  r:=TRectangle.Create(w,h);\n  writeln(r.Area);\n  r.Free;\nend.",
)

_EX_CARD_PAYMENT = _stub(
    "class Payment:\n    def __init__(self, amount):\n        self.amount = amount\n"
    "class CardPayment(Payment):\n    def __init__(self, amount, card):\n        super().__init__(amount)\n        self.card = card\n    def pay(self):\n        print(f'Card {self.card}: {self.amount}')\n"
    "amount, card = input().split()\np = CardPayment(int(amount), card)\np.pay()",
    "type\n  TPayment = class\n    Amount: integer;\n    constructor Create(aAmount: integer);\n  end;\n"
    "  TCardPayment = class(TPayment)\n    Card: string;\n    constructor Create(aAmount: integer; aCard: string);\n    procedure Pay;\n  end;\n"
    "constructor TPayment.Create(aAmount: integer);\nbegin Amount:=aAmount; end;\n"
    "constructor TCardPayment.Create(aAmount: integer; aCard: string);\nbegin inherited Create(aAmount); Card:=aCard; end;\n"
    "procedure TCardPayment.Pay;\nbegin writeln('Card ',Card,': ',Amount); end;\n"
    "var p: TCardPayment; amount: integer; card: string;\n"
    "begin\n  readln(amount,card);\n  p:=TCardPayment.Create(amount,card);\n  p.Pay;\n  p.Free;\nend.",
)

_EX_DELIVERY = _stub(
    "class Delivery:\n    def deliver(self):\n        return 'Delivery'\n"
    "class Courier(Delivery):\n    def deliver(self):\n        return 'Courier'\n"
    "class Post(Delivery):\n    def deliver(self):\n        return 'Post'\n"
    "kind = input().strip()\nd = Courier() if kind == 'courier' else Post()\nprint(d.deliver())",
    "type\n  TDelivery = class\n    function Deliver: string; virtual;\n  end;\n"
    "  TCourier = class(TDelivery)\n    function Deliver: string; override;\n  end;\n"
    "  TPost = class(TDelivery)\n    function Deliver: string; override;\n  end;\n"
    "function TDelivery.Deliver: string;\nbegin Deliver:='Delivery'; end;\n"
    "function TCourier.Deliver: string;\nbegin Deliver:='Courier'; end;\n"
    "function TPost.Deliver: string;\nbegin Deliver:='Post'; end;\n"
    "var kind: string; d: TDelivery;\n"
    "begin\n  readln(kind);\n  if kind='courier' then d:=TCourier.Create else d:=TPost.Create;\n  writeln(d.Deliver);\n  d.Free;\nend.",
)

_EX_SHAPE_LIST = _stub(
    "class Shape:\n    def area(self):\n        return 0\n"
    "class Rectangle(Shape):\n    def __init__(self, w, h):\n        self.w = w\n        self.h = h\n    def area(self):\n        return self.w * self.h\n"
    "n = int(input())\nshapes = []\nfor _ in range(n):\n    w, h = map(int, input().split()); shapes.append(Rectangle(w, h))\nprint(sum(s.area() for s in shapes))",
    "type\n  TShape = class\n    function Area: integer; virtual;\n  end;\n"
    "  TRectangle = class(TShape)\n    W,H: integer;\n    constructor Create(aW,aH: integer);\n    function Area: integer; override;\n  end;\n"
    "function TShape.Area: integer;\nbegin Area:=0; end;\n"
    "constructor TRectangle.Create(aW,aH: integer);\nbegin W:=aW; H:=aH; end;\n"
    "function TRectangle.Area: integer;\nbegin Area:=W*H; end;\n"
    "var n,i,total,w,h: integer;\nbegin\n  readln(n); total:=0;\n  for i:=1 to n do begin readln(w,h); total:=total+w*h; end;\n  writeln(total);\nend.",
)

_EX_OVERRIDE_DESC = _stub(
    "class Item:\n    def __init__(self, name):\n        self.name = name\n    def describe(self):\n        return self.name\n"
    "class FancyItem(Item):\n    def describe(self):\n        return f'*{self.name}*'\n"
    "name = input().strip()\nkind = input().strip()\nobj = FancyItem(name) if kind == 'fancy' else Item(name)\nprint(obj.describe())",
    "type\n  TItem = class\n    Name: string;\n    constructor Create(aName: string);\n    function Describe: string; virtual;\n  end;\n"
    "  TFancyItem = class(TItem)\n    function Describe: string; override;\n  end;\n"
    "constructor TItem.Create(aName: string);\nbegin Name:=aName; end;\n"
    "function TItem.Describe: string;\nbegin Describe:=Name; end;\n"
    "function TFancyItem.Describe: string;\nbegin Describe:='*'+Name+'*'; end;\n"
    "var kind: string; obj: TItem;\n"
    "begin\n  readln(obj.Name); readln(kind);\n  if kind='fancy' then writeln('*',obj.Name,'*') else writeln(obj.Name);\nend.",
)

_EX_VALIDATABLE = _stub(
    "class Validator:\n    def validate(self, value):\n        return len(value) >= 3\n"
    "v = Validator()\nvalue = input().strip()\nprint('yes' if v.validate(value) else 'no')",
    "type\n  IValidatable = interface\n    function Validate(value: string): boolean;\n  end;\n"
    "  TValidator = class(TInterfacedObject, IValidatable)\n    function Validate(value: string): boolean;\n  end;\n"
    "function TValidator.Validate(value: string): boolean;\nbegin Validate:=length(value)>=3; end;\n"
    "var v: IValidatable; value: string;\n"
    "begin\n  v:=TValidator.Create;\n  readln(value);\n  if v.Validate(value) then writeln('yes') else writeln('no');\nend.",
)

_EX_SHOP_SYSTEM = _stub(
    "class Employee:\n    def __init__(self, name):\n        self.name = name\n"
    "class Product:\n    def __init__(self, name, price):\n        self.name = name\n        self.price = price\n"
    "class Order:\n    def __init__(self, emp, product, qty):\n        self.total = product.price * qty\n        self.emp = emp.name\n        self.product = product.name\n    def receipt(self):\n        print(f'{self.emp} sold {self.product} for {self.total}')\n"
    "emp_name, prod_name, price, qty = input().split()\ne = Employee(emp_name)\np = Product(prod_name, int(price))\no = Order(e, p, int(qty))\no.receipt()",
    "type\n  TEmployee = class\n    Name: string;\n    constructor Create(aName: string);\n  end;\n"
    "  TProduct = class\n    Name: string; Price: integer;\n    constructor Create(aName: string; aPrice: integer);\n  end;\n"
    "  TOrder = class\n    EmpName,ProdName: string; Total: integer;\n    constructor Create(aEmp,aProd: string; aTotal: integer);\n    procedure Receipt;\n  end;\n"
    "constructor TEmployee.Create(aName: string);\nbegin Name:=aName; end;\n"
    "constructor TProduct.Create(aName: string; aPrice: integer);\nbegin Name:=aName; Price:=aPrice; end;\n"
    "constructor TOrder.Create(aEmp,aProd: string; aTotal: integer);\nbegin EmpName:=aEmp; ProdName:=aProd; Total:=aTotal; end;\n"
    "procedure TOrder.Receipt;\nbegin writeln(EmpName,' sold ',ProdName,' for ',Total); end;\n"
    "var emp,prod: string; price,qty,total: integer; order: TOrder;\n"
    "begin\n  readln(emp,prod,price,qty);\n  total:=price*qty;\n  order:=TOrder.Create(emp,prod,total);\n  order.Receipt;\n  order.Free;\nend.",
)

def build_course_batch_225_270_catalog() -> list[TaskRow]:
    """Tasks 225-270: idioms finish, OOP classes, collections, inheritance."""
    return [
        translate_task(
            225, 'Преобразовать температуры',
            'Прочитайте N и N температур в °C, выведите значения в °F через пробел. Переведите на Pascal.',
            'hard',
            topics=_idiom_topics(225),
            constructions=_IDIOM_CONSTRUCTIONS,
            code_examples=_EX_C_TO_F,
            test_cases=[
                tc('3\n0 100 -40\n', '32 212 -40'),
                tc('1\n37\n', '98'),
                tc('2\n10 20\n', '50 68'),
                tc('4\n-10 0 10 20\n', '14 32 50 68'),
                tc('2\n100 0\n', '212 32'),
            ]
        ),
        _block_from_body(
            226, 'Отфильтровать совершеннолетних',
            'Прочитайте N пар имя-возраст, выведите имена людей с возрастом >= 18.',
            'easy',
            "var n,i,age: integer; name: string;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(name,age); if age>=18 then writeln(name); end;\nend.",
            topics=_idiom_topics(226),
            constructions=_IDIOM_CONSTRUCTIONS,
            examples=_EX_FILTER_ADULTS,
            test_cases=[
                tc('3\nAnna 20\nBob 15\nCat 18\n', 'Anna\nCat'),
                tc('2\nX 18\nY 17\n', 'X'),
                tc('1\nSolo 21\n', 'Solo'),
                tc('4\nA 10\nB 20\nC 30\nD 5\n', 'B\nC'),
                tc('2\nI 18\nJ 18\n', 'I\nJ'),
            ],
        ),
        translate_task(
            227, 'Получить список имен',
            'Прочитайте N строк «имя балл», выведите только имена по одному на строку. Исправьте ошибки.',
            'medium',
            topics=_idiom_topics(227),
            constructions=_IDIOM_CONSTRUCTIONS,
            code_examples=_EX_MAP_NAMES,
            test_cases=[
                tc('3\nAnna 5\nBob 4\nCat 3\n', 'Anna\nBob\nCat'),
                tc('1\nSolo 10\n', 'Solo'),
                tc('2\nA 1\nB 2\n', 'A\nB'),
                tc('4\nX 0\nY 1\nZ 2\nW 3\n', 'X\nY\nZ\nW'),
                tc('2\nIvan 5\nMaria 5\n', 'Ivan\nMaria'),
            ],
            template='var n,i: integer; line: string;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(line); writeln(line); end;\nend.'
        ),
        translate_task(
            228, 'Найти максимальную цену',
            'Прочитайте N цен, выведите максимальную. Переведите на Pascal.',
            'hard',
            topics=_idiom_topics(228),
            constructions=_IDIOM_CONSTRUCTIONS,
            code_examples=_EX_MAX_PRICE,
            test_cases=[
                tc('5\n10 30 5 20 25\n', '30'),
                tc('1\n7\n', '7'),
                tc('3\n1 2 3\n', '3'),
                tc('4\n100 50 75 50\n', '100'),
                tc('2\n-5 0\n', '0'),
            ]
        ),
        _block_from_body(
            229, 'Подсчитать уникальные слова',
            'Прочитайте строку текста, выведите число уникальных слов.',
            'easy',
            "var text,word: string; i,n,c: integer; words: array[1..100] of string; j: integer;\nfunction HasWord(w: string): boolean;\nvar k: integer;\nbegin\n  HasWord:=false;\n  for k:=1 to c do if words[k]=w then HasWord:=true;\nend;\nbegin\n  readln(text); c:=0; n:=length(text); i:=1;\n  while i<=n do begin\n    while (i<=n) and (text[i]=' ') do i:=i+1;\n    if i>n then break;\n    word:=''; while (i<=n) and (text[i]<>' ') do begin word:=word+text[i]; i:=i+1; end;\n    if not HasWord(word) then begin c:=c+1; words[c]:=word; end;\n  end;\n  writeln(c);\nend.",
            topics=_idiom_topics(229),
            constructions=_IDIOM_CONSTRUCTIONS,
            examples=_EX_UNIQUE_WORDS,
            test_cases=[
                tc('hello world hello\n', '2'),
                tc('a b c\n', '3'),
                tc('cat cat cat\n', '1'),
                tc('one two one two\n', '2'),
                tc('test\n', '1'),
            ],
        ),
        translate_task(
            230, 'Построить рейтинг игроков',
            'Прочитайте N пар имя-очки, выведите рейтинг по убыванию очков. Исправьте ошибки.',
            'medium',
            topics=_idiom_topics(230),
            constructions=_IDIOM_CONSTRUCTIONS,
            code_examples=_EX_PLAYER_RANK,
            test_cases=[
                tc('3\nAnna 10\nBob 20\nCat 15\n', '1. Bob 20\n2. Cat 15\n3. Anna 10'),
                tc('2\nA 5\nB 5\n', '1. A 5\n2. B 5'),
                tc('1\nSolo 100\n', '1. Solo 100'),
                tc('4\nD 1\nC 2\nB 3\nA 4\n', '1. A 4\n2. B 3\n3. C 2\n4. D 1'),
                tc('2\nX 0\nY 10\n', '1. Y 10\n2. X 0'),
            ],
            template="var n,i: integer; names: array[1..100] of string; scores: array[1..100] of integer; name: string; score: integer;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(name,score); names[i]:=name; scores[i]:=score; end;\n  for i:=1 to n do writeln(i,'. ',names[i],' ',scores[i]);\nend."
        ),
        translate_task(
            231, 'Отсортировать товары по цене',
            'Прочитайте N товаров (название цена), выведите отсортированные по цене. Переведите на Pascal.',
            'hard',
            topics=_idiom_topics(231),
            constructions=_IDIOM_CONSTRUCTIONS,
            code_examples=_EX_SORT_PRODUCTS,
            test_cases=[
                tc('3\nB 30\nA 10\nC 20\n', 'A 10\nB 30\nC 20'),
                tc('1\nX 5\n', 'X 5'),
                tc('2\nY 2\nZ 1\n', 'Z 1\nY 2'),
                tc('4\nD 4\nC 3\nB 2\nA 1\n', 'A 1\nB 2\nC 3\nD 4'),
                tc('2\nM 100\nN 50\n', 'N 50\nM 100'),
            ]
        ),
        _block_from_body(
            232, 'Найти популярный товар',
            'Прочитайте N идентификаторов товаров, выведите самый частый id.',
            'easy',
            "var n,i,j,c,bestc: integer; ids: array[1..100] of string; id: string; cnt: array[1..100] of integer;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(id); ids[i]:=id; cnt[i]:=0; end;\n  for i:=1 to n do for j:=1 to n do if ids[i]=ids[j] then cnt[i]:=cnt[i]+1;\n  bestc:=1;\n  for i:=2 to n do if cnt[i]>cnt[bestc] then bestc:=i;\n  writeln(ids[bestc]);\nend.",
            topics=_idiom_topics(232),
            constructions=_IDIOM_CONSTRUCTIONS,
            examples=_EX_MOST_FREQUENT,
            test_cases=[
                tc('5\nA B A C A\n', 'A'),
                tc('3\nX X Y\n', 'X'),
                tc('1\nZ\n', 'Z'),
                tc('4\nM N M O\n', 'M'),
                tc('6\n1 1 2 2 2 3\n', '2'),
            ],
        ),
        translate_task(
            233, 'Средний балл группы',
            'Прочитайте N и N баллов, выведите средний с одним знаком. Исправьте ошибки.',
            'medium',
            topics=_idiom_topics(233),
            constructions=_IDIOM_CONSTRUCTIONS,
            code_examples=_EX_AVG_SCORE,
            test_cases=[
                tc('3\n5 4 3\n', '4.0'),
                tc('1\n10\n', '10.0'),
                tc('2\n8 6\n', '7.0'),
                tc('4\n5 5 5 5\n', '5.0'),
                tc('2\n1 2\n', '1.5'),
            ],
            template='var n,i,score: integer; avg: real;\nbegin\n  readln(n);\n  for i:=1 to n do read(score);\n  avg:=score/n; writeln(avg:0:1);\nend.'
        ),
        translate_task(
            234, 'Сгруппировать студентов по оценке',
            'Прочитайте N пар имя-оценка, выведите группы «оценка: имена». Переведите на Pascal.',
            'hard',
            topics=_idiom_topics(234),
            constructions=_IDIOM_CONSTRUCTIONS,
            code_examples=_EX_GROUP_GRADES,
            test_cases=[
                tc('4\nAnna 5\nBob 4\nCat 5\nDan 4\n', '4: Bob Dan\n5: Anna Cat'),
                tc('2\nA 3\nB 3\n', '3: A B'),
                tc('1\nSolo 10\n', '10: Solo'),
                tc('3\nX 1\nY 2\nZ 1\n', '1: X Z\n2: Y'),
                tc('2\nM 5\nN 4\n', '4: N\n5: M'),
            ]
        ),
        _block_from_body(
            235, 'Сформировать отчет по заказам',
            'Прочитайте N сумм заказов, выведите общую сумму и количество.',
            'easy',
            "var n,i,total,amount: integer;\nbegin\n  readln(n); total:=0;\n  for i:=1 to n do begin readln(amount); total:=total+amount; end;\n  writeln(total,' ',n);\nend.",
            topics=_idiom_topics(235),
            constructions=_IDIOM_CONSTRUCTIONS,
            examples=_EX_ORDER_REPORT,
            test_cases=[
                tc('3\n100\n200\n50\n', '350 3'),
                tc('1\n10\n', '10 1'),
                tc('2\n5\n15\n', '20 2'),
                tc('4\n1\n2\n3\n4\n', '10 4'),
                tc('0\n', '0 0'),
            ],
        ),
        translate_task(
            236, 'Проверочная: аналитика магазина',
            'Прочитайте N пар цена-количество, выведите выручку, число позиций и среднюю цену. Исправьте ошибки.',
            'medium',
            topics=_idiom_topics(236),
            constructions=_IDIOM_CONSTRUCTIONS,
            code_examples=_EX_SHOP_ANALYTICS,
            test_cases=[
                tc('2\n10 2\n5 4\n', '40 2 7.5'),
                tc('1\n100 1\n', '100 1 100.0'),
                tc('3\n10 1\n20 1\n30 1\n', '60 3 20.0'),
                tc('2\n5 10\n15 2\n', '80 2 10.0'),
                tc('1\n0 5\n', '0 1 0.0'),
            ],
            template="var n,i,price,qty: integer; total: integer; avg: real;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(price,qty); total:=price; end;\n  avg:=price; writeln(total,' ',n,' ',avg:0:1);\nend."
        ),
        translate_task(
            237, 'Класс товара',
            'Реализуйте класс Product с полями name и price и методом вывода. Переведите на Pascal.',
            'hard',
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            code_examples=_EX_PRODUCT_CLASS,
            test_cases=[
                tc('Apple 50\n', 'Apple 50'),
                tc('Book 120\n', 'Book 120'),
                tc('Pen 10\n', 'Pen 10'),
                tc('X 0\n', 'X 0'),
                tc('Long 999\n', 'Long 999'),
            ]
        ),
        _block_from_body(
            238, 'Создать объект товара',
            'Прочитайте имя товара, создайте объект и выведите «Product: имя».',
            'easy',
            "var name: string;\nbegin\n  readln(name);\n  writeln('Product: ',name);\nend.",
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            examples=_EX_CREATE_PRODUCT,
            test_cases=[
                tc('Apple\n', 'Product: Apple'),
                tc('Book\n', 'Product: Book'),
                tc('X\n', 'Product: X'),
                tc('Pen\n', 'Product: Pen'),
                tc('Item\n', 'Product: Item'),
            ],
        ),
        translate_task(
            239, 'Метод расчета цены',
            'Класс Product с методом getPrice(discount). Исправьте ошибки.',
            'medium',
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            code_examples=_EX_PRODUCT_DISCOUNT,
            test_cases=[
                tc('100 10\n', '90'),
                tc('200 50\n', '100'),
                tc('50 0\n', '50'),
                tc('1000 25\n', '750'),
                tc('80 20\n', '64'),
            ],
            template='var price,discount: integer;\nbegin\n  readln(price,discount);\n  writeln(price);\nend.'
        ),
        translate_task(
            240, 'Класс студента',
            'Реализуйте класс Student с полями name и score. Переведите на Pascal.',
            'hard',
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            code_examples=_EX_STUDENT_CLASS,
            test_cases=[
                tc('Anna 5\n', 'Anna 5'),
                tc('Bob 4\n', 'Bob 4'),
                tc('Solo 10\n', 'Solo 10'),
                tc('X 0\n', 'X 0'),
                tc('Ivan 3\n', 'Ivan 3'),
            ]
        ),
        _block_from_body(
            241, 'Класс банковского счета',
            'Прочитайте начальный баланс, создайте счёт и выведите баланс.',
            'easy',
            "var balance: integer;\nbegin\n  readln(balance);\n  writeln(balance);\nend.",
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            examples=_EX_BANK_ACCOUNT,
            test_cases=[
                tc('100\n', '100'),
                tc('0\n', '0'),
                tc('500\n', '500'),
                tc('1\n', '1'),
                tc('999\n', '999'),
            ],
        ),
        translate_task(
            242, 'Конструктор товара',
            'Класс Product с конструктором name, price, qty. Исправьте ошибки.',
            'medium',
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            code_examples=_EX_PRODUCT_INIT,
            test_cases=[
                tc('Apple 50 3\n', 'Apple 50 3'),
                tc('Book 120 1\n', 'Book 120 1'),
                tc('Pen 10 5\n', 'Pen 10 5'),
                tc('X 0 0\n', 'X 0 0'),
                tc('Item 99 2\n', 'Item 99 2'),
            ],
            template="var name: string; price,qty: integer;\nbegin\n  readln(name,price,qty);\n  writeln(name,' ',qty);\nend."
        ),
        translate_task(
            243, 'Метод изменения состояния',
            'Класс BankAccount с deposit и withdraw. Переведите на Pascal.',
            'hard',
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            code_examples=_EX_ACCOUNT_OPS,
            test_cases=[
                tc('100 50 30\n', '120'),
                tc('0 10 5\n', '5'),
                tc('200 0 50\n', '150'),
                tc('50 50 50\n', '50'),
                tc('1000 100 200\n', '900'),
            ]
        ),
        _block_from_body(
            244, 'Несколько объектов',
            'Прочитайте N, создайте N объектов и выведите их количество.',
            'easy',
            "var n: integer;\nbegin\n  readln(n);\n  writeln(n);\nend.",
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            examples=_EX_N_OBJECTS,
            test_cases=[
                tc('3\n', '3'),
                tc('1\n', '1'),
                tc('5\n', '5'),
                tc('0\n', '0'),
                tc('10\n', '10'),
            ],
        ),
        translate_task(
            245, 'Класс прямоугольника',
            'Класс Rectangle с методом area. Исправьте ошибки.',
            'medium',
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            code_examples=_EX_RECTANGLE,
            test_cases=[
                tc('3 4\n', '12'),
                tc('1 1\n', '1'),
                tc('5 5\n', '25'),
                tc('10 2\n', '20'),
                tc('7 3\n', '21'),
            ],
            template='var w,h: integer;\nbegin\n  readln(w,h);\n  writeln(w+h);\nend.'
        ),
        translate_task(
            246, 'Класс таймера',
            'Класс Timer с tick/countdown. Переведите на Pascal.',
            'hard',
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            code_examples=_EX_TIMER,
            test_cases=[
                tc('5\n', '4\n3'),
                tc('3\n', '2\n1'),
                tc('10\n', '9\n8'),
                tc('1\n', '0\n-1'),
                tc('2\n', '1\n0'),
            ]
        ),
        _block_from_body(
            247, 'Класс заказа',
            'Прочитайте сумму заказа, создайте Order и выведите «Total: сумма».',
            'easy',
            "var total: integer;\nbegin\n  readln(total);\n  writeln('Total: ',total);\nend.",
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            examples=_EX_ORDER_CLASS,
            test_cases=[
                tc('100\n', 'Total: 100'),
                tc('0\n', 'Total: 0'),
                tc('50\n', 'Total: 50'),
                tc('999\n', 'Total: 999'),
                tc('1\n', 'Total: 1'),
            ],
        ),
        translate_task(
            248, 'Класс пользователя',
            'Класс User с проверкой login/password. Исправьте ошибки.',
            'medium',
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            code_examples=_EX_USER_CLASS,
            test_cases=[
                tc('admin secret\n', 'yes'),
                tc('user pass\n', 'yes'),
                tc('a b\n', 'yes'),
                tc('x y\n', 'yes'),
                tc('login pwd\n', 'yes'),
            ],
            template="var login,pwd: string;\nbegin\n  readln(login,pwd);\n  writeln('no');\nend."
        ),
        translate_task(
            249, 'Класс книги',
            'Класс Book с title и author. Переведите на Pascal.',
            'hard',
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            code_examples=_EX_BOOK_CLASS,
            test_cases=[
                tc('War and Peace Leo Tolstoy\n', 'War and Peace / Leo Tolstoy'),
                tc('1984 George Orwell\n', '1984 / George Orwell'),
                tc('A B\n', 'A / B'),
                tc('Title Author Name\n', 'Title / Author Name'),
                tc('X Y\n', 'X / Y'),
            ]
        ),
        translate_task(
            250, 'Проверочная: карточка товара',
            'Класс Product с card(): вывод «[категория] имя: цена». Исправьте ошибки.',
            'medium',
            topics=_OOP_CLASS_TOPICS,
            constructions=_OOP_CLASS_CONSTRUCTIONS,
            code_examples=_EX_PRODUCT_CARD,
            test_cases=[
                tc('Apple 50 fruit\n', '[fruit] Apple: 50'),
                tc('Book 120 books\n', '[books] Book: 120'),
                tc('Pen 10 office\n', '[office] Pen: 10'),
                tc('X 0 misc\n', '[misc] X: 0'),
                tc('Item 99 cat\n', '[cat] Item: 99'),
            ],
            template="var name,cat: string; price: integer;\nbegin\n  readln(name,price,cat);\n  writeln(name,' ',price);\nend."
        ),
        translate_task(
            251, 'Список студентов',
            'Прочитайте N студентов, сохраните в список объектов и выведите всех. Исправьте ошибки.',
            'medium',
            topics=_OOP_COLL_TOPICS,
            constructions=_OOP_COLL_CONSTRUCTIONS,
            code_examples=_EX_STUDENT_LIST,
            test_cases=[
                tc('2\nAnna 5\nBob 4\n', 'Anna 5\nBob 4'),
                tc('1\nSolo 10\n', 'Solo 10'),
                tc('3\nA 1\nB 2\nC 3\n', 'A 1\nB 2\nC 3'),
                tc('2\nX 0\nY 5\n', 'X 0\nY 5'),
                tc('4\nD 1\nC 2\nB 3\nA 4\n', 'D 1\nC 2\nB 3\nA 4'),
            ],
            template='var n,i: integer; name: string; score: integer;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(name,score); writeln(score); end;\nend.'
        ),
        translate_task(
            252, 'Найти лучшего студента',
            'Прочитайте N пар имя-балл, выведите студента с максимальным баллом. Переведите на Pascal.',
            'hard',
            topics=_OOP_COLL_TOPICS,
            constructions=_OOP_COLL_CONSTRUCTIONS,
            code_examples=_EX_BEST_STUDENT,
            test_cases=[
                tc('3\nAnna 5\nBob 4\nCat 5\n', 'Anna 5'),
                tc('2\nA 10\nB 9\n', 'A 10'),
                tc('1\nSolo 7\n', 'Solo 7'),
                tc('4\nD 1\nC 9\nB 5\nA 9\n', 'C 9'),
                tc('2\nX 0\nY 1\n', 'Y 1'),
            ]
        ),
        _block_from_body(
            253, 'Отсортировать товары',
            'Прочитайте N товаров (название цена), отсортируйте список по цене.',
            'easy',
            "var n,i,j: integer; names: array[1..100] of string; prices: array[1..100] of integer;\n    name: string; price,t: integer; tmpn: string;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(name,price); names[i]:=name; prices[i]:=price; end;\n  for i:=1 to n-1 do for j:=1 to n-i do if prices[j]>prices[j+1] then begin\n    t:=prices[j]; prices[j]:=prices[j+1]; prices[j+1]:=t;\n    tmpn:=names[j]; names[j]:=names[j+1]; names[j+1]:=tmpn; end;\n  for i:=1 to n do writeln(names[i],' ',prices[i]);\nend.",
            topics=_OOP_COLL_TOPICS,
            constructions=_OOP_COLL_CONSTRUCTIONS,
            examples=_EX_SORT_PRODUCTS_LIST,
            test_cases=[
                tc('3\nB 30\nA 10\nC 20\n', 'A 10\nB 30\nC 20'),
                tc('1\nX 5\n', 'X 5'),
                tc('2\nY 2\nZ 1\n', 'Z 1\nY 2'),
                tc('4\nD 4\nC 3\nB 2\nA 1\n', 'A 1\nB 2\nC 3\nD 4'),
                tc('2\nM 100\nN 50\n', 'N 50\nM 100'),
            ],
        ),
        translate_task(
            254, 'Фильтр активных пользователей',
            'Прочитайте N пользователей (имя yes/no), выведите активных. Исправьте ошибки.',
            'medium',
            topics=_OOP_COLL_TOPICS,
            constructions=_OOP_COLL_CONSTRUCTIONS,
            code_examples=_EX_FILTER_ACTIVE,
            test_cases=[
                tc('3\nAnna yes\nBob no\nCat yes\n', 'Anna\nCat'),
                tc('2\nA yes\nB yes\n', 'A\nB'),
                tc('1\nSolo no\n', ''),
                tc('4\nA yes\nB no\nC yes\nD no\n', 'A\nC'),
                tc('2\nX no\nY yes\n', 'Y'),
            ],
            template='var n,i: integer; name,flag: string;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(name,flag); writeln(name); end;\nend.'
        ),
        translate_task(
            255, 'Корзина объектов',
            'Реализуйте Cart: add/remove/total до команды done. Переведите на Pascal.',
            'hard',
            topics=_OOP_COLL_TOPICS,
            constructions=_OOP_COLL_CONSTRUCTIONS,
            code_examples=_EX_CART,
            test_cases=[
                tc('add\n10\nadd\n20\nremove\ndone\n', '10'),
                tc('add\n5\ndone\n', '5'),
                tc('add\n1\nadd\n2\nadd\n3\ndone\n', '6'),
                tc('remove\ndone\n', '0'),
                tc('add\n100\nadd\n50\nremove\nremove\ndone\n', '0'),
            ]
        ),
        _block_from_body(
            256, 'Банковский счет: пополнение',
            'Прочитайте баланс и сумму пополнения, выведите новый баланс.',
            'easy',
            "var balance,amount: integer;\nbegin\n  readln(balance,amount);\n  writeln(balance+amount);\nend.",
            topics=_OOP_COLL_TOPICS,
            constructions=_OOP_COLL_CONSTRUCTIONS,
            examples=_EX_DEPOSIT,
            test_cases=[
                tc('100 50\n', '150'),
                tc('0 10\n', '10'),
                tc('200 0\n', '200'),
                tc('50 50\n', '100'),
                tc('1000 1\n', '1001'),
            ],
        ),
        translate_task(
            257, 'Банковский счет: снятие',
            'Счёт с проверкой овердрафта при снятии. Исправьте ошибки.',
            'medium',
            topics=_OOP_COLL_TOPICS,
            constructions=_OOP_COLL_CONSTRUCTIONS,
            code_examples=_EX_WITHDRAW,
            test_cases=[
                tc('100 30\n', '70'),
                tc('50 50\n', '0'),
                tc('100 200\n', '100'),
                tc('0 0\n', '0'),
                tc('200 150\n', '50'),
            ],
            template='var balance,amount: integer;\nbegin\n  readln(balance,amount);\n  writeln(balance-amount);\nend.'
        ),
        translate_task(
            258, 'Журнал заказов',
            'Прочитайте N заказов (id сумма), выведите журнал. Переведите на Pascal.',
            'hard',
            topics=_OOP_COLL_TOPICS,
            constructions=_OOP_COLL_CONSTRUCTIONS,
            code_examples=_EX_ORDER_LOG,
            test_cases=[
                tc('2\nA 100\nB 200\n', 'A 100\nB 200'),
                tc('1\nX 50\n', 'X 50'),
                tc('3\n1 10\n2 20\n3 30\n', '1 10\n2 20\n3 30'),
                tc('2\nO1 0\nO2 1\n', 'O1 0\nO2 1'),
                tc('4\nA 1\nB 2\nC 3\nD 4\n', 'A 1\nB 2\nC 3\nD 4'),
            ]
        ),
        _block_from_body(
            259, 'Каталог книг',
            'Обработайте N команд add: добавьте книгу и выведите все названия.',
            'easy',
            "var n,i,c: integer; cmd,title: string; titles: array[1..100] of string;\nbegin\n  readln(n); c:=0;\n  for i:=1 to n do begin readln(cmd); if cmd='add' then begin readln(title); c:=c+1; titles[c]:=title; end; end;\n  for i:=1 to c do writeln(titles[i]);\nend.",
            topics=_OOP_COLL_TOPICS,
            constructions=_OOP_COLL_CONSTRUCTIONS,
            examples=_EX_BOOK_CATALOG,
            test_cases=[
                tc('2\nadd\nBook1\nadd\nBook2\n', 'Book1\nBook2'),
                tc('1\nadd\nSolo\n', 'Solo'),
                tc('3\nadd\nA\nadd\nB\nadd\nC\n', 'A\nB\nC'),
                tc('2\nadd\nX\nadd\nY\n', 'X\nY'),
                tc('1\nadd\nTest\n', 'Test'),
            ],
        ),
        translate_task(
            260, 'Проверочная: мини-магазин',
            'Прочитайте N товаров (имя цена кол-во), выведите выручку и число позиций с qty>0. Исправьте ошибки.',
            'medium',
            topics=_OOP_COLL_TOPICS,
            constructions=_OOP_COLL_CONSTRUCTIONS,
            code_examples=_EX_MINI_SHOP,
            test_cases=[
                tc('2\nA 10 2\nB 5 0\n', '20 1'),
                tc('1\nX 100 1\n', '100 1'),
                tc('3\nA 1 1\nB 2 2\nC 3 3\n', '14 3'),
                tc('1\nZ 0 5\n', '0 1'),
                tc('2\nM 10 0\nN 20 3\n', '60 1'),
            ],
            template='var n,i: integer; name: string; price,qty: integer;\nbegin\n  readln(n);\n  for i:=1 to n do begin readln(name,price,qty); writeln(price); end;\nend.'
        ),
        translate_task(
            261, 'Сотрудник и менеджер',
            'Manager extends Employee с bonus и total(). Переведите на Pascal.',
            'hard',
            topics=_OOP_INH_TOPICS,
            constructions=_OOP_INH_CONSTRUCTIONS,
            code_examples=_EX_MANAGER,
            test_cases=[
                tc('Ivan 1000 200\n', 'Ivan 1200'),
                tc('Anna 500 100\n', 'Anna 600'),
                tc('X 0 0\n', 'X 0'),
                tc('Boss 10000 5000\n', 'Boss 15000'),
                tc('A 100 50\n', 'A 150'),
            ]
        ),
        _block_from_body(
            262, 'Транспорт и автомобиль',
            'Car extends Vehicle: прочитайте brand model, выведите «brand model».',
            'easy',
            "var brand,model: string;\nbegin\n  readln(brand,model);\n  writeln(brand,' ',model);\nend.",
            topics=_OOP_INH_TOPICS,
            constructions=_OOP_INH_CONSTRUCTIONS,
            examples=_EX_CAR,
            test_cases=[
                tc('Toyota Camry\n', 'Toyota Camry'),
                tc('BMW X5\n', 'BMW X5'),
                tc('A B\n', 'A B'),
                tc('Ford Focus\n', 'Ford Focus'),
                tc('X Y\n', 'X Y'),
            ],
        ),
        translate_task(
            263, 'Животное и собака',
            'Dog extends Animal, переопределите speak. Исправьте ошибки.',
            'medium',
            topics=_OOP_INH_TOPICS,
            constructions=_OOP_INH_CONSTRUCTIONS,
            code_examples=_EX_DOG,
            test_cases=[
                tc('Rex\n', 'Rex: Woof'),
                tc('Buddy\n', 'Buddy: Woof'),
                tc('A\n', 'A: Woof'),
                tc('Dog\n', 'Dog: Woof'),
                tc('X\n', 'X: Woof'),
            ],
            template="var name: string;\nbegin\n  readln(name);\n  writeln(name,': ...');\nend."
        ),
        translate_task(
            264, 'Фигура и прямоугольник',
            'Rectangle extends Shape с area(). Переведите на Pascal.',
            'hard',
            topics=_OOP_INH_TOPICS,
            constructions=_OOP_INH_CONSTRUCTIONS,
            code_examples=_EX_SHAPE_RECT,
            test_cases=[
                tc('3 4\n', '12'),
                tc('1 1\n', '1'),
                tc('5 5\n', '25'),
                tc('10 2\n', '20'),
                tc('7 3\n', '21'),
            ]
        ),
        _block_from_body(
            265, 'Платеж и оплата картой',
            'CardPayment extends Payment: выведите «Card номер: сумма».',
            'easy',
            "var amount: integer; card: string;\nbegin\n  readln(amount,card);\n  writeln('Card ',card,': ',amount);\nend.",
            topics=_OOP_INH_TOPICS,
            constructions=_OOP_INH_CONSTRUCTIONS,
            examples=_EX_CARD_PAYMENT,
            test_cases=[
                tc('100 1234\n', 'Card 1234: 100'),
                tc('50 9999\n', 'Card 9999: 50'),
                tc('0 0\n', 'Card 0: 0'),
                tc('200 42\n', 'Card 42: 200'),
                tc('1 1\n', 'Card 1: 1'),
            ],
        ),
        translate_task(
            266, 'Доставка разными способами',
            'Полиморфный deliver() для courier/post. Исправьте ошибки.',
            'medium',
            topics=_OOP_INH_TOPICS,
            constructions=_OOP_INH_CONSTRUCTIONS,
            code_examples=_EX_DELIVERY,
            test_cases=[
                tc('courier\n', 'Courier'),
                tc('post\n', 'Post'),
                tc('courier\n', 'Courier'),
                tc('post\n', 'Post'),
                tc('courier\n', 'Courier'),
            ],
            template="var kind: string;\nbegin\n  readln(kind);\n  writeln('Delivery');\nend."
        ),
        translate_task(
            267, 'Список базового типа',
            'Список Shape (Rectangle), выведите суммарную площадь. Переведите на Pascal.',
            'hard',
            topics=_OOP_INH_TOPICS,
            constructions=_OOP_INH_CONSTRUCTIONS,
            code_examples=_EX_SHAPE_LIST,
            test_cases=[
                tc('2\n3 4\n5 5\n', '37'),
                tc('1\n1 1\n', '1'),
                tc('3\n1 2\n2 3\n3 4\n', '20'),
                tc('1\n10 10\n', '100'),
                tc('2\n0 5\n5 0\n', '0'),
            ]
        ),
        _block_from_body(
            268, 'Переопределение вывода',
            'Item/FancyItem: переопределите describe, выведите результат.',
            'easy',
            "var name,kind: string;\nbegin\n  readln(name); readln(kind);\n  if kind='fancy' then writeln('*',name,'*') else writeln(name);\nend.",
            topics=_OOP_INH_TOPICS,
            constructions=_OOP_INH_CONSTRUCTIONS,
            examples=_EX_OVERRIDE_DESC,
            test_cases=[
                tc('Apple\nfancy\n', '*Apple*'),
                tc('Book\nplain\n', 'Book'),
                tc('X\nfancy\n', '*X*'),
                tc('Y\nplain\n', 'Y'),
                tc('Z\nfancy\n', '*Z*'),
            ],
        ),
        translate_task(
            269, 'Интерфейс проверки',
            'IValidatable validate: длина >= 3. Исправьте ошибки.',
            'medium',
            topics=_OOP_INH_TOPICS,
            constructions=_OOP_INH_CONSTRUCTIONS,
            code_examples=_EX_VALIDATABLE,
            test_cases=[
                tc('abc\n', 'yes'),
                tc('ab\n', 'no'),
                tc('hello\n', 'yes'),
                tc('a\n', 'no'),
                tc('xyz\n', 'yes'),
            ],
            template="var value: string;\nbegin\n  readln(value);\n  writeln('yes');\nend."
        ),
        translate_task(
            270, 'Проверочная: мини-система магазина',
            'Employee + Product + Order: выведите чек продажи. Переведите на Pascal.',
            'hard',
            topics=_OOP_INH_TOPICS,
            constructions=_OOP_INH_CONSTRUCTIONS,
            code_examples=_EX_SHOP_SYSTEM,
            test_cases=[
                tc('Ivan Apple 50 2\n', 'Ivan sold Apple for 100'),
                tc('Anna Book 120 1\n', 'Anna sold Book for 120'),
                tc('X Y 10 3\n', 'X sold Y for 30'),
                tc('A B 0 5\n', 'A sold B for 0'),
                tc('Boss Item 99 1\n', 'Boss sold Item for 99'),
            ]
        ),
    ]


COURSE_BATCH_225_270_SIZE = 46
COURSE_BATCH_225_270_CATALOG = build_course_batch_225_270_catalog()
