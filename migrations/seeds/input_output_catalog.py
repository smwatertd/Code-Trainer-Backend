"""Раздел «Ввод и вывод» — задачи 13–24 из final_course_270.pdf."""
from __future__ import annotations

from migrations.seeds.block_helpers import block_reorder_payload

TaskRow = dict

_IO_CONSTRUCTIONS = [
    "typed_declaration",
    "stdin_read",
    "assignment",
    "arithmetic_ops",
    "stdout_write",
]

_IO_TOPICS = ["io", "stdin_read"]

_PY_SQUARE = "x = int(input())\nprint(x * x)"

_PY_GREETING = 'name = input()\nprint("Hello, " + name)'

_PY_SUM_TWO = "a, b = map(int, input().split())\nprint(a + b)"

_PY_AREA = "w, h = map(int, input().split())\nprint(w * h)"

_PY_MINUTES = (
    "total = int(input())\n"
    "h = total // 60\n"
    "m = total % 60\n"
    "print(h, m)"
)

_PY_PURCHASE = (
    "price, count = map(int, input().split())\n"
    "total = price * count\n"
    "print(total)"
)

_PY_LAST_DIGIT = "x = int(input())\nprint(x % 10)"

_PY_DIGIT_SUM = "x = int(input())\nprint(x // 10 + x % 10)"

_PY_CELSIUS = (
    "c = float(input())\n"
    "f = c * 9 / 5 + 32\n"
    'print(f"{f:.1f}")'
)

_PY_STR_TO_INT = "s = input()\nx = int(s)\nprint(x + 1)"

_PY_AVG_THREE = (
    "a, b, c = map(int, input().split())\n"
    'print(f"{(a + b + c) / 3:.1f}")'
)

_PY_DELIVERY = (
    "price, weight, rate = map(float, input().split())\n"
    "total = price + weight * rate\n"
    'print(f"{total:.2f}")'
)

_CODE_EXAMPLES: dict[str, dict[str, str]] = {
    "square": {
        "python": _PY_SQUARE,
        "pascal": "var x: integer;\nbegin\n  readln(x);\n  writeln(x*x);\nend.",
        "cpp": "int x; std::cin>>x;\nstd::cout << x*x;",
        "csharp": "int x=int.Parse(Console.ReadLine());\nConsole.WriteLine(x*x);",
        "java": "Scanner sc=new Scanner(System.in);\nint x=sc.nextInt();\nSystem.out.println(x*x);",
    },
    "greeting": {
        "python": _PY_GREETING,
        "pascal": "var name: string;\nbegin\n  readln(name);\n  writeln('Hello, ', name);\nend.",
        "cpp": 'std::string name;\nstd::cin >> name;\nstd::cout << "Hello, " << name;',
        "csharp": 'string name=Console.ReadLine();\nConsole.WriteLine($"Hello, {name}");',
        "java": 'Scanner sc=new Scanner(System.in);\nString name=sc.next();\nSystem.out.println("Hello, "+name);',
    },
    "sum_two": {
        "python": _PY_SUM_TWO,
        "pascal": "var a,b: integer;\nbegin\n  readln(a,b);\n  writeln(a+b);\nend.",
        "cpp": "int a,b; std::cin>>a>>b;\nstd::cout << a+b;",
        "csharp": "var p=Console.ReadLine().Split();\nint a=int.Parse(p[0]), b=int.Parse(p[1]);\nConsole.WriteLine(a+b);",
        "java": "Scanner sc=new Scanner(System.in);\nint a=sc.nextInt(), b=sc.nextInt();\nSystem.out.println(a+b);",
    },
    "area": {
        "python": _PY_AREA,
        "pascal": "var w,h: integer;\nbegin\n  readln(w,h);\n  writeln(w*h);\nend.",
        "cpp": "int w,h;\nstd::cin >> w >> h;\nstd::cout << w*h;",
        "csharp": "var p=Console.ReadLine().Split();\nint w=int.Parse(p[0]), h=int.Parse(p[1]);\nConsole.WriteLine(w*h);",
        "java": "Scanner sc=new Scanner(System.in);\nint w=sc.nextInt(), h=sc.nextInt();\nSystem.out.println(w*h);",
    },
    "minutes": {
        "python": _PY_MINUTES,
        "pascal": (
            "var total,h,m: integer;\n"
            "begin\n"
            "  readln(total);\n"
            "  h:=total div 60;\n"
            "  m:=total mod 60;\n"
            "  writeln(h,' ',m);\n"
            "end."
        ),
        "cpp": "int total; std::cin>>total;\nint h=total/60, m=total%60;\nstd::cout << h << ' ' << m;",
        "csharp": "int total=int.Parse(Console.ReadLine());\nint h=total/60, m=total%60;\nConsole.WriteLine($\"{h} {m}\");",
        "java": "Scanner sc=new Scanner(System.in);\nint total=sc.nextInt();\nint h=total/60, m=total%60;\nSystem.out.println(h+\" \"+m);",
    },
    "purchase": {
        "python": _PY_PURCHASE,
        "pascal": (
            "var price,count,total: integer;\n"
            "begin\n"
            "  readln(price,count);\n"
            "  total:=price*count;\n"
            "  writeln(total);\n"
            "end."
        ),
        "cpp": "int price,count; std::cin>>price>>count;\nint total=price*count;\nstd::cout << total;",
        "csharp": "var p=Console.ReadLine().Split();\nint price=int.Parse(p[0]), count=int.Parse(p[1]);\nint total=price*count;\nConsole.WriteLine(total);",
        "java": "Scanner sc=new Scanner(System.in);\nint price=sc.nextInt(), count=sc.nextInt();\nint total=price*count;\nSystem.out.println(total);",
    },
    "last_digit": {
        "python": _PY_LAST_DIGIT,
        "pascal": "var x,last: integer;\nbegin\n  readln(x);\n  last:=x mod 10;\n  writeln(last);\nend.",
        "cpp": "int x; std::cin>>x;\nint last=x%10;\nstd::cout << last;",
        "csharp": "int x=int.Parse(Console.ReadLine());\nint last=x%10;\nConsole.WriteLine(last);",
        "java": "Scanner sc=new Scanner(System.in);\nint x=sc.nextInt();\nint last=x%10;\nSystem.out.println(last);",
    },
    "digit_sum": {
        "python": _PY_DIGIT_SUM,
        "pascal": "var x,s: integer;\nbegin\n  readln(x);\n  s:=x div 10 + x mod 10;\n  writeln(s);\nend.",
        "cpp": "int x,s; std::cin>>x;\ns=x/10+x%10;\nstd::cout << s;",
        "csharp": "int x=int.Parse(Console.ReadLine());\nConsole.WriteLine(x/10+x%10);",
        "java": "Scanner sc=new Scanner(System.in);\nint x=sc.nextInt();\nSystem.out.println(x/10+x%10);",
    },
    "celsius": {
        "python": _PY_CELSIUS,
        "pascal": "var c,f: real;\nbegin\n  readln(c);\n  f:=c*9/5+32;\n  writeln(f:0:1);\nend.",
        "cpp": "double c; std::cin>>c;\ndouble f=c*9/5+32;\nstd::cout << f;",
        "csharp": "double c=double.Parse(Console.ReadLine());\ndouble f=c*9/5+32;\nConsole.WriteLine(f);",
        "java": "Scanner sc=new Scanner(System.in);\ndouble c=sc.nextDouble();\ndouble f=c*9/5+32;\nSystem.out.println(f);",
    },
    "str_to_int": {
        "python": _PY_STR_TO_INT,
        "pascal": (
            "var s: string; x,code: integer;\n"
            "begin\n"
            "  readln(s);\n"
            "  val(s,x,code);\n"
            "  writeln(x+1);\n"
            "end."
        ),
        "cpp": "std::string s;\nstd::cin >> s;\nint x=std::stoi(s);\nstd::cout << x+1;",
        "csharp": "string s=Console.ReadLine();\nint x=int.Parse(s);\nConsole.WriteLine(x+1);",
        "java": "Scanner sc=new Scanner(System.in);\nString s=sc.next();\nint x=Integer.parseInt(s);\nSystem.out.println(x+1);",
    },
    "avg_three": {
        "python": _PY_AVG_THREE,
        "pascal": (
            "var a,b,c: integer;\n"
            "begin\n"
            "  readln(a,b,c);\n"
            "  writeln((a+b+c)/3:0:1);\n"
            "end."
        ),
        "cpp": "int a,b,c; std::cin>>a>>b>>c;\nstd::cout << (a+b+c)/3.0;",
        "csharp": "var p=Console.ReadLine().Split();\nint a=int.Parse(p[0]),b=int.Parse(p[1]),c=int.Parse(p[2]);\nConsole.WriteLine((a+b+c)/3.0);",
        "java": "Scanner sc=new Scanner(System.in);\nint a=sc.nextInt(),b=sc.nextInt(),c=sc.nextInt();\nSystem.out.println((a+b+c)/3.0);",
    },
    "delivery": {
        "python": _PY_DELIVERY,
        "pascal": (
            "var price,weight,rate,total: real;\n"
            "begin\n"
            "  readln(price,weight,rate);\n"
            "  total:=price+weight*rate;\n"
            "  writeln(total:0:2);\n"
            "end."
        ),
        "cpp": "double price,weight,rate;\nstd::cin>>price>>weight>>rate;\nstd::cout << price+weight*rate;",
        "csharp": "var p=Console.ReadLine().Split();\ndouble price=double.Parse(p[0]), weight=double.Parse(p[1]), rate=double.Parse(p[2]);\nConsole.WriteLine(price+weight*rate);",
        "java": "Scanner sc=new Scanner(System.in);\ndouble price=sc.nextDouble(), weight=sc.nextDouble(), rate=sc.nextDouble();\nSystem.out.println(price+weight*rate);",
    },
}


def _row(
    task_id: int,
    title: str,
    description: str,
    difficulty: str,
    task_type: str,
    payload: dict,
) -> TaskRow:
    return {
        "id": task_id,
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "task_type": task_type,
        "visibility": "public",
        "workflow_status": "active",
        "is_deleted": False,
        "payload": payload,
    }


def _translation(
    *,
    topics: list[str],
    source_code: str | None = None,
    target_language: str = "pascal",
    test_cases: list[dict] | None = None,
    constructions: list[str] | None = None,
    kind: str | None = None,
    template: str = "",
) -> dict:
    payload: dict = {"topics": topics}
    if source_code is not None:
        payload["source_language"] = "python"
        payload["source_code"] = source_code
    if target_language:
        payload["target_language"] = target_language
    if template:
        payload["template"] = template
    if test_cases:
        payload["test_cases"] = test_cases
    if constructions:
        payload["constructions"] = constructions
    if kind:
        payload["kind"] = kind
    return payload


def _examples(key: str) -> dict[str, str]:
    return dict(_CODE_EXAMPLES[key])


def _tc(inputs: str, output: str) -> dict[str, str]:
    return {"inputs": inputs, "output": output}


def _block_task(
    task_id: int,
    title: str,
    description: str,
    difficulty: str,
    *,
    pascal_blocks: list[str],
    correct_order: list[int],
    expected_pascal: str,
    test_cases: list[dict[str, str]],
    examples_key: str,
) -> TaskRow:
    payload = block_reorder_payload(
        blocks=pascal_blocks,
        correct_order=correct_order,
        expected_code=expected_pascal,
        output=test_cases[0]["output"],
        topics=_IO_TOPICS,
        language="pascal",
    )
    payload["test_cases"] = test_cases
    payload["constructions"] = list(_IO_CONSTRUCTIONS)
    payload["code_examples"] = _examples(examples_key)
    payload["source_language"] = "python"
    return _row(task_id, title, description, difficulty, "task_build_from_blocks", payload)


def _translate_task(
    task_id: int,
    title: str,
    description: str,
    difficulty: str,
    *,
    examples_key: str,
    test_cases: list[dict[str, str]],
    template: str = "",
) -> TaskRow:
    payload = _translation(
        topics=_IO_TOPICS,
        source_code=_examples(examples_key)["python"],
        target_language="pascal",
        test_cases=test_cases,
        constructions=list(_IO_CONSTRUCTIONS),
        template=template,
        kind="debug" if template else None,
    )
    payload["code_examples"] = _examples(examples_key)
    return _row(task_id, title, description, difficulty, "translation", payload)


def build_input_output_catalog() -> list[TaskRow]:
    return [
        _block_task(
            13,
            "Прочитать число и вывести квадрат",
            (
                "Пользователь вводит число; программа выводит квадрат. "
                "Входные данные читаются в указанном порядке, результат выводится без лишнего текста. "
                "Соберите программу из блоков на Pascal."
            ),
            "easy",
            pascal_blocks=[
                "program Main;",
                "var x: integer;",
                "begin",
                "readln(x);",
                "writeln(x*x);",
                "end.",
            ],
            correct_order=[0, 1, 2, 3, 4, 5],
            expected_pascal=(
                "program Main;\nvar x: integer;\n"
                "begin\n  readln(x);\n  writeln(x*x);\nend."
            ),
            test_cases=[
                _tc("5\n", "25"),
                _tc("0\n", "0"),
                _tc("-3\n", "9"),
                _tc("12\n", "144"),
                _tc("1\n", "1"),
            ],
            examples_key="square",
        ),
        _translate_task(
            14,
            "Прочитать имя и вывести приветствие",
            (
                "Пользователь вводит имя; программа выводит приветствие в формате Hello, <имя>. "
                "Исправьте ошибки в программе на Pascal, ориентируясь на эталон слева."
            ),
            "medium",
            examples_key="greeting",
            test_cases=[
                _tc("Ann\n", "Hello, Ann"),
                _tc("Ivan\n", "Hello, Ivan"),
                _tc("Mia\n", "Hello, Mia"),
                _tc("Bob\n", "Hello, Bob"),
                _tc("Ada\n", "Hello, Ada"),
            ],
            template=(
                "var name: string;\n"
                "begin\n"
                "  readln(name);\n"
                "  writeln('Hello, name');\n"
                "end."
            ),
        ),
        _translate_task(
            15,
            "Прочитать два числа и вывести сумму",
            (
                "Введите два числа и выведите их сумму без лишнего текста. "
                "Переведите программу с Python на Pascal."
            ),
            "hard",
            examples_key="sum_two",
            test_cases=[
                _tc("2\n3\n", "5"),
                _tc("-2\n5\n", "3"),
                _tc("0\n0\n", "0"),
                _tc("100\n250\n", "350"),
                _tc("-7\n-8\n", "-15"),
            ],
        ),
        _block_task(
            16,
            "Прочитать стороны прямоугольника",
            (
                "На вход подаются ширина и высота. Вычислите площадь и выведите одно число. "
                "Соберите программу из блоков на Pascal."
            ),
            "easy",
            pascal_blocks=[
                "program Main;",
                "var w,h: integer;",
                "begin",
                "readln(w,h);",
                "writeln(w*h);",
                "end.",
            ],
            correct_order=[0, 1, 2, 3, 4, 5],
            expected_pascal=(
                "program Main;\nvar w,h: integer;\n"
                "begin\n  readln(w,h);\n  writeln(w*h);\nend."
            ),
            test_cases=[
                _tc("4\n6\n", "24"),
                _tc("1\n10\n", "10"),
                _tc("7\n7\n", "49"),
                _tc("0\n5\n", "0"),
                _tc("12\n3\n", "36"),
            ],
            examples_key="area",
        ),
        _translate_task(
            17,
            "Прочитать минуты",
            (
                "На вход подаётся целое количество минут. Выведите два числа: полные часы и остаток минут. "
                "Исправьте ошибки в программе на Pascal."
            ),
            "medium",
            examples_key="minutes",
            test_cases=[
                _tc("135\n", "2 15"),
                _tc("60\n", "1 0"),
                _tc("59\n", "0 59"),
                _tc("0\n", "0 0"),
                _tc("245\n", "4 5"),
            ],
            template=(
                "var total,h,m: integer;\n"
                "begin\n"
                "  readln(total);\n"
                "  h:=total mod 60;\n"
                "  m:=total div 60;\n"
                "  writeln(h,' ',m);\n"
                "end."
            ),
        ),
        _translate_task(
            18,
            "Прочитать цену и количество",
            (
                "Прочитайте цену и количество, выведите итоговую стоимость покупки. "
                "Переведите программу на Pascal."
            ),
            "hard",
            examples_key="purchase",
            test_cases=[
                _tc("120\n3\n", "360"),
                _tc("10\n0\n", "0"),
                _tc("5\n8\n", "40"),
                _tc("99\n2\n", "198"),
                _tc("7\n7\n", "49"),
            ],
        ),
        _block_task(
            19,
            "Прочитать число и вывести последнюю цифру",
            (
                "Прочитайте целое число и выведите его последнюю цифру, используя mod. "
                "Соберите программу из блоков."
            ),
            "easy",
            pascal_blocks=[
                "program Main;",
                "var x,last: integer;",
                "begin",
                "readln(x);",
                "last:=x mod 10;",
                "writeln(last);",
                "end.",
            ],
            correct_order=[0, 1, 2, 3, 4, 5, 6],
            expected_pascal=(
                "program Main;\nvar x,last: integer;\n"
                "begin\n  readln(x);\n  last:=x mod 10;\n  writeln(last);\nend."
            ),
            test_cases=[
                _tc("127\n", "7"),
                _tc("10\n", "0"),
                _tc("5\n", "5"),
                _tc("999\n", "9"),
                _tc("1204\n", "4"),
            ],
            examples_key="last_digit",
        ),
        _translate_task(
            20,
            "Прочитать двузначное число",
            (
                "Прочитайте двузначное число и выведите сумму его цифр, используя div и mod. "
                "Исправьте ошибки в программе на Pascal."
            ),
            "medium",
            examples_key="digit_sum",
            test_cases=[
                _tc("47\n", "11"),
                _tc("10\n", "1"),
                _tc("99\n", "18"),
                _tc("35\n", "8"),
                _tc("80\n", "8"),
            ],
            template=(
                "var a,b: integer;\n"
                "begin\n"
                "  readln(a,b);\n"
                "  writeln(a+b);\n"
                "end."
            ),
        ),
        _translate_task(
            21,
            "Прочитать температуру Celsius",
            (
                "Прочитайте температуру в градусах Celsius и выведите Fahrenheit "
                "с одним знаком после запятой. Переведите программу на Pascal."
            ),
            "hard",
            examples_key="celsius",
            test_cases=[
                _tc("0\n", "32.0"),
                _tc("100\n", "212.0"),
                _tc("25\n", "77.0"),
                _tc("-40\n", "-40.0"),
                _tc("10\n", "50.0"),
            ],
        ),
        _block_task(
            22,
            "Прочитать строку с числом",
            (
                "Прочитайте строку, преобразуйте её в число и увеличьте на 1. "
                "Соберите программу из блоков на Pascal."
            ),
            "easy",
            pascal_blocks=[
                "program Main;",
                "var s: string; x,code: integer;",
                "begin",
                "readln(s);",
                "val(s,x,code);",
                "writeln(x+1);",
                "end.",
            ],
            correct_order=[0, 1, 2, 3, 4, 5, 6],
            expected_pascal=(
                "program Main;\nvar s: string; x,code: integer;\n"
                "begin\n  readln(s);\n  val(s,x,code);\n  writeln(x+1);\nend."
            ),
            test_cases=[
                _tc("41\n", "42"),
                _tc("0\n", "1"),
                _tc("-2\n", "-1"),
                _tc("99\n", "100"),
                _tc("7\n", "8"),
            ],
            examples_key="str_to_int",
        ),
        _translate_task(
            23,
            "Прочитать три числа",
            (
                "Прочитайте три числа и выведите их среднее арифметическое с одним знаком после запятой. "
                "Исправьте ошибки в программе на Pascal."
            ),
            "medium",
            examples_key="avg_three",
            test_cases=[
                _tc("9 6 7.5\n", "7.5"),
                _tc("1 2 1.5\n", "1.5"),
                _tc("0 0 0\n", "0.0"),
                _tc("-2 4 1\n", "1.0"),
                _tc("10 20 15\n", "15.0"),
            ],
            template=(
                "var a,b,c: integer;\n"
                "begin\n"
                "  readln(a,b,c);\n"
                "  writeln((a+b+c) div 3);\n"
                "end."
            ),
        ),
        _translate_task(
            24,
            "Проверочная: стоимость доставки",
            (
                "Прочитайте цену товара, вес и тариф за единицу веса. "
                "Итог: price + weight × rate, вывод с двумя знаками после запятой. "
                "Переведите программу на Pascal."
            ),
            "hard",
            examples_key="delivery",
            test_cases=[
                _tc("100\n2\n10\n", "120.00"),
                _tc("0\n5\n3\n", "15.00"),
                _tc("50\n0\n7\n", "50.00"),
                _tc("200\n3\n20\n", "260.00"),
                _tc("75\n4\n5\n", "95.00"),
            ],
        ),
    ]


INPUT_OUTPUT_CATALOG = build_input_output_catalog()
INPUT_OUTPUT_CATALOG_SIZE = len(INPUT_OUTPUT_CATALOG)
