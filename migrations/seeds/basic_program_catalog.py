"""Раздел «Базовая программа» — 12 задач из final_course_270.pdf."""
from __future__ import annotations

from migrations.seeds.block_helpers import block_reorder_payload

TaskRow = dict


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


_BASICS_CONSTRUCTIONS = [
    "program_entry",
    "typed_declaration",
    "assignment",
    "arithmetic_ops",
    "stdout_write",
]

_PY_HELLO = "print('Hello')"

_PY_AGE = "age = int(input())\nprint(age)"

_PY_SUM = "a = int(input())\nb = int(input())\nprint(a + b)"

_PY_AREA = "w = int(input())\nh = int(input())\nprint(w * h)"

_PY_PERIMETER = "w = int(input())\nh = int(input())\nprint(2 * (w + h))"

_PY_SWAP = (
    "a = int(input())\n"
    "b = int(input())\n"
    "t = a\n"
    "a = b\n"
    "b = t\n"
    "print(a, b)"
)

_PY_AVG = (
    "a = int(input())\n"
    "b = int(input())\n"
    "avg = (a + b) / 2\n"
    "print(f'{avg:.1f}')"
)

_PY_LAST_DIGIT = "x = int(input())\nprint(x % 10)"

_PY_DIGIT_SUM = "x = int(input())\nprint(x // 10 + x % 10)"

_PY_MINUTES = (
    "total = int(input())\n"
    "h = total // 60\n"
    "m = total % 60\n"
    "print(h, m)"
)

_PY_PURCHASE = (
    "price = int(input())\n"
    "count = int(input())\n"
    "print(price * count)"
)

_PY_RECEIPT = (
    "price = float(input())\n"
    "tax_pct = float(input())\n"
    "discount_pct = float(input())\n"
    "total = price * (1 + tax_pct / 100) * (1 - discount_pct / 100)\n"
    "print(f'{total:.2f}')"
)

_CODE_EXAMPLES: dict[str, dict[str, str]] = {
    "hello": {
        "python": _PY_HELLO,
        "pascal": "program Main;\nbegin\n  writeln('Hello');\nend.",
        "cpp": '#include <iostream>\nint main() {\n  std::cout << "Hello\\n";\n  return 0;\n}',
        "csharp": 'using System;\nclass Program {\n  static void Main() {\n    Console.WriteLine("Hello");\n  }\n}',
        "java": 'class Main {\n  public static void main(String[] args) {\n    System.out.println("Hello");\n  }\n}',
    },
    "age": {
        "python": _PY_AGE,
        "pascal": "var age: integer;\nbegin\n  readln(age);\n  writeln(age);\nend.",
        "cpp": "int age;\nstd::cin >> age;\nstd::cout << age << \"\\n\";",
        "csharp": "int age = int.Parse(Console.ReadLine());\nConsole.WriteLine(age);",
        "java": "int age = Integer.parseInt(new Scanner(System.in).nextLine());\nSystem.out.println(age);",
    },
    "sum": {
        "python": _PY_SUM,
        "pascal": "var a,b,s: integer;\nbegin\n  readln(a,b);\n  s:=a+b;\n  writeln(s);\nend.",
        "cpp": "int a,b,s;\nstd::cin>>a>>b;\ns=a+b;\nstd::cout<<s;",
        "csharp": "var p=Console.ReadLine().Split();\nint a=int.Parse(p[0]),b=int.Parse(p[1]);\nConsole.WriteLine(a+b);",
        "java": "Scanner sc=new Scanner(System.in);\nint a=sc.nextInt(),b=sc.nextInt();\nSystem.out.println(a+b);",
    },
    "area": {
        "python": _PY_AREA,
        "pascal": "var w,h,area: integer;\nbegin\n  readln(w,h);\n  area:=w*h;\n  writeln(area);\nend.",
        "cpp": "int w,h,area;\nstd::cin>>w>>h;\narea=w*h;\nstd::cout<<area;",
        "csharp": "var p=Console.ReadLine().Split();\nint w=int.Parse(p[0]),h=int.Parse(p[1]);\nConsole.WriteLine(w*h);",
        "java": "Scanner sc=new Scanner(System.in);\nint w=sc.nextInt(),h=sc.nextInt();\nSystem.out.println(w*h);",
    },
    "perimeter": {
        "python": _PY_PERIMETER,
        "pascal": "var w,h,p: integer;\nbegin\n  readln(w,h);\n  p:=2*(w+h);\n  writeln(p);\nend.",
        "cpp": "int w,h,p;\nstd::cin>>w>>h;\np=2*(w+h);\nstd::cout<<p;",
        "csharp": "var p=Console.ReadLine().Split();\nint w=int.Parse(p[0]),h=int.Parse(p[1]);\nConsole.WriteLine(2*(w+h));",
        "java": "Scanner sc=new Scanner(System.in);\nint w=sc.nextInt(),h=sc.nextInt();\nSystem.out.println(2*(w+h));",
    },
    "swap": {
        "python": _PY_SWAP,
        "pascal": "var a,b,t: integer;\nbegin\n  readln(a,b);\n  t:=a; a:=b; b:=t;\n  writeln(a,' ',b);\nend.",
        "cpp": "int a,b,t;\nstd::cin>>a>>b;\nt=a; a=b; b=t;\nstd::cout<<a<<' '<<b;",
        "csharp": "var p=Console.ReadLine().Split();\nint a=int.Parse(p[0]),b=int.Parse(p[1]),t=a; a=b; b=t;\nConsole.WriteLine($\"{a} {b}\");",
        "java": "Scanner sc=new Scanner(System.in);\nint a=sc.nextInt(),b=sc.nextInt(),t=a; a=b; b=t;\nSystem.out.println(a+\" \"+b);",
    },
    "avg": {
        "python": _PY_AVG,
        "pascal": "var a,b: integer; avg: real;\nbegin\n  readln(a,b);\n  avg:=(a+b)/2;\n  writeln(avg:0:1);\nend.",
        "cpp": "int a,b;\ndouble avg;\nstd::cin>>a>>b;\navg=(a+b)/2.0;\nstd::cout<<avg;",
        "csharp": "var p=Console.ReadLine().Split();\nint a=int.Parse(p[0]),b=int.Parse(p[1]);\nConsole.WriteLine((a+b)/2.0);",
        "java": "Scanner sc=new Scanner(System.in);\nint a=sc.nextInt(),b=sc.nextInt();\nSystem.out.println((a+b)/2.0);",
    },
    "last_digit": {
        "python": _PY_LAST_DIGIT,
        "pascal": "var x,last: integer;\nbegin\n  readln(x);\n  last:=x mod 10;\n  writeln(last);\nend.",
        "cpp": "int x,last;\nstd::cin>>x;\nlast=x%10;\nstd::cout<<last;",
        "csharp": "int x=int.Parse(Console.ReadLine());\nConsole.WriteLine(x%10);",
        "java": "int x=Integer.parseInt(new Scanner(System.in).nextLine());\nSystem.out.println(x%10);",
    },
    "digit_sum": {
        "python": _PY_DIGIT_SUM,
        "pascal": "var x,s: integer;\nbegin\n  readln(x);\n  s:=x div 10 + x mod 10;\n  writeln(s);\nend.",
        "cpp": "int x,s;\nstd::cin>>x;\ns=x/10+x%10;\nstd::cout<<s;",
        "csharp": "int x=int.Parse(Console.ReadLine());\nConsole.WriteLine(x/10+x%10);",
        "java": "int x=Integer.parseInt(new Scanner(System.in).nextLine());\nSystem.out.println(x/10+x%10);",
    },
    "minutes": {
        "python": _PY_MINUTES,
        "pascal": "var total,h,m: integer;\nbegin\n  readln(total);\n  h:=total div 60;\n  m:=total mod 60;\n  writeln(h,' ',m);\nend.",
        "cpp": "int total,h,m;\nstd::cin>>total;\nh=total/60; m=total%60;\nstd::cout<<h<<' '<<m;",
        "csharp": "int total=int.Parse(Console.ReadLine());\nConsole.WriteLine($\"{total/60} {total%60}\");",
        "java": "int total=Integer.parseInt(new Scanner(System.in).nextLine());\nSystem.out.println(total/60+\" \"+total%60);",
    },
    "purchase": {
        "python": _PY_PURCHASE,
        "pascal": "var price,count,total: integer;\nbegin\n  readln(price,count);\n  total:=price*count;\n  writeln(total);\nend.",
        "cpp": "int price,count,total;\nstd::cin>>price>>count;\ntotal=price*count;\nstd::cout<<total;",
        "csharp": "var p=Console.ReadLine().Split();\nint price=int.Parse(p[0]),count=int.Parse(p[1]);\nConsole.WriteLine(price*count);",
        "java": "Scanner sc=new Scanner(System.in);\nint price=sc.nextInt(),count=sc.nextInt();\nSystem.out.println(price*count);",
    },
    "receipt": {
        "python": _PY_RECEIPT,
        "pascal": (
            "var price,tax,discount,total: real;\n"
            "begin\n"
            "  readln(price,tax,discount);\n"
            "  total:=price*(1+tax/100)*(1-discount/100);\n"
            "  writeln(total:0:2);\n"
            "end."
        ),
        "cpp": (
            "double price,tax,discount,total;\n"
            "std::cin>>price>>tax>>discount;\n"
            "total=price*(1+tax/100)*(1-discount/100);\n"
            "std::cout<<total;"
        ),
        "csharp": (
            "var p=Console.ReadLine().Split();\n"
            "double price=double.Parse(p[0]),tax=double.Parse(p[1]),discount=double.Parse(p[2]);\n"
            "Console.WriteLine(price*(1+tax/100)*(1-discount/100));"
        ),
        "java": (
            "Scanner sc=new Scanner(System.in);\n"
            "double price=sc.nextDouble(),tax=sc.nextDouble(),discount=sc.nextDouble();\n"
            "System.out.printf(\"%.2f\", price*(1+tax/100)*(1-discount/100));"
        ),
    },
}


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
        topics=["basics", "program"],
        language="pascal",
    )
    payload["test_cases"] = test_cases
    payload["constructions"] = list(_BASICS_CONSTRUCTIONS)
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
        topics=["basics", "program"],
        source_code=_examples(examples_key)["python"],
        target_language="pascal",
        test_cases=test_cases,
        constructions=list(_BASICS_CONSTRUCTIONS),
        template=template,
        kind="debug" if template else None,
    )
    payload["code_examples"] = _examples(examples_key)
    return _row(task_id, title, description, difficulty, "translation", payload)


def build_basic_program_catalog() -> list[TaskRow]:
    return [
        _block_task(
            1,
            "Вывести приветствие",
            (
                "Напишите программу для задачи «Вывести приветствие». Программа запускается без "
                "входных данных и выводит ровно строку Hello. Важно показать минимальную оболочку "
                "программы и консольный вывод."
            ),
            "easy",
            pascal_blocks=[
                "program Main;",
                "begin",
                "writeln('Hello');",
                "end.",
            ],
            correct_order=[0, 1, 2, 3],
            expected_pascal="program Main;\nbegin\n  writeln('Hello');\nend.",
            test_cases=[
                _tc("", "Hello"),
                _tc("", "Hello"),
                _tc("", "Hello"),
            ],
            examples_key="hello",
        ),
        _translate_task(
            2,
            "Сохранить возраст",
            (
                "Создайте переменную age, прочитайте её значение и выведите без лишнего текста. "
                "Исправьте ошибки в программе на Pascal, ориентируясь на эталон слева."
            ),
            "medium",
            examples_key="age",
            test_cases=[
                _tc("18\n", "18"),
                _tc("0\n", "0"),
                _tc("21\n", "21"),
                _tc("65\n", "65"),
                _tc("7\n", "7"),
            ],
            template=(
                "var age: integer;\n"
                "begin\n"
                "  age = 18;\n"
                "  writeln(age);\n"
                "end."
            ),
        ),
        _translate_task(
            3,
            "Посчитать сумму двух чисел",
            (
                "Прочитайте два числа и выведите их сумму без лишнего текста. "
                "Переведите программу с Python на Pascal."
            ),
            "hard",
            examples_key="sum",
            test_cases=[
                _tc("2\n3\n", "5"),
                _tc("-2\n5\n", "3"),
                _tc("0\n0\n", "0"),
                _tc("100\n250\n", "350"),
                _tc("-7\n-8\n", "-15"),
            ],
        ),
        _block_task(
            4,
            "Посчитать площадь прямоугольника",
            (
                "На вход подаются ширина и высота. Вычислите площадь и выведите одно число. "
                "Соберите программу из блоков на Pascal."
            ),
            "easy",
            pascal_blocks=[
                "program Main;",
                "var w,h,area: integer;",
                "begin",
                "readln(w,h);",
                "area:=w*h;",
                "writeln(area);",
                "end.",
            ],
            correct_order=[0, 1, 2, 3, 4, 5, 6],
            expected_pascal=(
                "program Main;\nvar w,h,area: integer;\n"
                "begin\n  readln(w,h);\n  area:=w*h;\n  writeln(area);\nend."
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
            5,
            "Посчитать периметр прямоугольника",
            (
                "На вход подаются ширина и высота. Вычислите периметр и выведите одно число. "
                "Исправьте ошибки в программе на Pascal."
            ),
            "medium",
            examples_key="perimeter",
            test_cases=[
                _tc("4\n6\n", "20"),
                _tc("1\n10\n", "22"),
                _tc("7\n7\n", "28"),
                _tc("0\n5\n", "10"),
                _tc("12\n3\n", "30"),
            ],
            template=(
                "var w,h,p: integer;\n"
                "begin\n"
                "  readln(w,h);\n"
                "  p:=w*h;\n"
                "  writeln(p);\n"
                "end."
            ),
        ),
        _translate_task(
            6,
            "Поменять две переменные местами",
            (
                "Прочитайте два числа, поменяйте их местами через временную переменную "
                "и выведите результат через пробел. Переведите программу на Pascal."
            ),
            "hard",
            examples_key="swap",
            test_cases=[
                _tc("3\n8\n", "8 3"),
                _tc("1\n2\n", "2 1"),
                _tc("0\n5\n", "5 0"),
                _tc("-1\n7\n", "7 -1"),
                _tc("10\n10\n", "10 10"),
            ],
        ),
        _block_task(
            7,
            "Найти среднее двух чисел",
            (
                "Прочитайте два числа и выведите их среднее арифметическое с одним знаком "
                "после запятой. Соберите программу из блоков."
            ),
            "easy",
            pascal_blocks=[
                "program Main;",
                "var a,b: integer; avg: real;",
                "begin",
                "readln(a,b);",
                "avg:=(a+b)/2;",
                "writeln(avg:0:1);",
                "end.",
            ],
            correct_order=[0, 1, 2, 3, 4, 5, 6],
            expected_pascal=(
                "program Main;\nvar a,b: integer; avg: real;\n"
                "begin\n  readln(a,b);\n  avg:=(a+b)/2;\n  writeln(avg:0:1);\nend."
            ),
            test_cases=[
                _tc("9\n6\n", "7.5"),
                _tc("1\n2\n", "1.5"),
                _tc("0\n0\n", "0"),
                _tc("-2\n4\n", "1"),
                _tc("10\n20\n", "15"),
            ],
            examples_key="avg",
        ),
        _translate_task(
            8,
            "Вывести последнюю цифру числа",
            (
                "Прочитайте целое число и выведите его последнюю цифру, используя mod. "
                "Исправьте ошибки в программе на Pascal."
            ),
            "medium",
            examples_key="last_digit",
            test_cases=[
                _tc("127\n", "7"),
                _tc("10\n", "0"),
                _tc("5\n", "5"),
                _tc("999\n", "9"),
                _tc("1204\n", "4"),
            ],
            template=(
                "var x,last: integer;\n"
                "begin\n"
                "  readln(x);\n"
                "  last:=x div 10;\n"
                "  writeln(last);\n"
                "end."
            ),
        ),
        _translate_task(
            9,
            "Найти сумму цифр двузначного числа",
            (
                "Прочитайте двузначное число и выведите сумму его цифр, используя div и mod. "
                "Переведите программу на Pascal."
            ),
            "hard",
            examples_key="digit_sum",
            test_cases=[
                _tc("47\n", "11"),
                _tc("10\n", "1"),
                _tc("99\n", "18"),
                _tc("35\n", "8"),
                _tc("80\n", "8"),
            ],
        ),
        _block_task(
            10,
            "Перевести минуты в часы и минуты",
            (
                "Прочитайте количество минут и выведите два числа: полные часы и остаток минут. "
                "Соберите программу из блоков."
            ),
            "easy",
            pascal_blocks=[
                "program Main;",
                "var total,h,m: integer;",
                "begin",
                "readln(total);",
                "h:=total div 60;",
                "m:=total mod 60;",
                "writeln(h,' ',m);",
                "end.",
            ],
            correct_order=[0, 1, 2, 3, 4, 5, 6, 7],
            expected_pascal=(
                "program Main;\nvar total,h,m: integer;\n"
                "begin\n  readln(total);\n  h:=total div 60;\n  m:=total mod 60;\n  writeln(h,' ',m);\nend."
            ),
            test_cases=[
                _tc("135\n", "2 15"),
                _tc("60\n", "1 0"),
                _tc("59\n", "0 59"),
                _tc("0\n", "0 0"),
                _tc("245\n", "4 5"),
            ],
            examples_key="minutes",
        ),
        _translate_task(
            11,
            "Рассчитать стоимость покупки",
            (
                "Прочитайте цену и количество, выведите итоговую стоимость. "
                "Исправьте ошибки в программе на Pascal."
            ),
            "medium",
            examples_key="purchase",
            test_cases=[
                _tc("120\n3\n", "360"),
                _tc("10\n0\n", "0"),
                _tc("5\n8\n", "40"),
                _tc("99\n2\n", "198"),
                _tc("7\n7\n", "49"),
            ],
            template=(
                "var price,count,total: integer;\n"
                "begin\n"
                "  readln(price,count);\n"
                "  total:=price+count;\n"
                "  writeln(total);\n"
                "end."
            ),
        ),
        _translate_task(
            12,
            "Проверочная: чек с налогом и скидкой",
            (
                "Прочитайте цену, процент налога и процент скидки. "
                "Итог: price × (1 + tax/100) × (1 − discount/100), вывод с двумя знаками после запятой. "
                "Переведите программу на Pascal."
            ),
            "hard",
            examples_key="receipt",
            test_cases=[
                _tc("1000\n20\n10\n", "1080.00"),
                _tc("100\n0\n0\n", "100.00"),
                _tc("200\n10\n0\n", "220.00"),
                _tc("500\n20\n50\n", "300.00"),
                _tc("120\n20\n5\n", "136.80"),
            ],
        ),
    ]


BASIC_PROGRAM_CATALOG = build_basic_program_catalog()
