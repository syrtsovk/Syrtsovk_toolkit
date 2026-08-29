#!/usr/bin/env python3
"""vibecheck: сканер мёртвого и брошенного кода.

Чистый python3 без зависимостей. Только читает, ничего не меняет.
Находит: файлы-сироты, заглушки, закомментированные блоки, файлы-копии,
недостижимый код, неиспользуемые зависимости.

Запуск:
    python3 scan_dead.py /путь/к/проекту
    python3 scan_dead.py . --json
    python3 scan_dead.py . --report dead.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", "vendor", "target", ".idea", ".vscode",
    "coverage", ".turbo", ".cache", "site-packages", ".mypy_cache", ".tox", "migrations",
    ".claude", ".cursor", ".github", ".husky",
}
# Эти запускают вручную или дёргает инструментарий — импорта на них не бывает по определению.
STANDALONE = re.compile(r"(?i)(^|/)(scripts?|bin|tools?|hooks|cli|jobs|tasks|seeds?|fixtures?)/")
CODE_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".vue", ".svelte", ".go", ".rb"}
MAX_FILE_BYTES = 1_500_000

# Файлы, которые подключаются фреймворком по имени, а не импортом.
FRAMEWORK_ENTRY = re.compile(
    r"(?i)(^|/)(page|layout|route|loading|error|not-found|template|default|middleware|"
    r"index|main|app|__init__|conftest|settings|urls|wsgi|asgi|manage|setup|robots|sitemap|manifest|"
    r"opengraph-image|twitter-image|icon|apple-icon|favicon|instrumentation|proxy)\.[a-z]+$"
)
CONFIG_LIKE = re.compile(r"(?i)(\.config\.[a-z]+$|\.d\.ts$|(^|/)\.[a-z]|(^|/)(next|vite|tailwind|jest|vitest|"
                         r"webpack|rollup|babel|eslint|prettier|postcss|commitlint|lintstaged)[.\-])")
TEST_LIKE = re.compile(r"(?i)(\.test\.|\.spec\.|(^|/)tests?/|(^|/)__tests__/|(^|/)test_)")
BACKUP_LIKE = re.compile(r"(?i)(_v\d|_old|_new|_final|_fixed|_backup|_copy|[- ]copy|\.bak$|\.orig$|\.save$|"
                         r"[- ]?\(\d\)\.|old\.[a-z]+$)")

STUB = re.compile(
    r"(?i)(raise NotImplementedError|NotImplementedError\(|throw new Error\(\s*[\"'](not implemented|todo|unimplemented)|"
    r"@abstractmethod|def \w+\([^)]*\):\s*\n\s*pass\s*(\n|$)|=>\s*\{\s*\}\s*[;,)]|function \w+\([^)]*\)\s*\{\s*\}\s*)"
)
TODO_MARK = re.compile(r"(?i)(^|\s)(#|//|/\*|\*)\s*(TODO|FIXME|HACK|XXX|KOSTYL|КОСТЫЛЬ)[\s:!]")
UNREACHABLE = re.compile(r"(?m)^([ \t]*)(return\b[^\n]*|raise\b[^\n]*|throw\b[^\n]*|break|continue)\s*\n\1(?!\s*[}\])#/])"
                         r"(?!\s*(else|elif|except|finally|catch|case|default)\b)\S[^\n]*")
COMMENTED_CODE = re.compile(
    r"(?m)^(?:[ \t]*(?://|#)[^\n]*\n){5,}"
)
CODE_SIGNAL = re.compile(r"(?i)(function |def |class |return |import |const |let |var |if \(|for \(|=>|\{|\}|;$)")

JS_IMPORT = re.compile(r"""(?:from\s+["'`]([^"'`]+)["'`]|require\(\s*["'`]([^"'`]+)["'`]\s*\)|"""
                       r"""import\s*\(\s*["'`]([^"'`]+)["'`]\s*\))""")
# from pkg.sub import a, b  →  (модуль, имена).  Ведущие точки покрывают from .leads import
PY_FROM = re.compile(r"(?m)^\s*from\s+([.\w]+)\s+import\s+([^\n#]+)")
# import pkg.sub as alias, other
PY_IMPORT = re.compile(r"(?m)^\s*import\s+([^\n#]+)")


def iter_code_paths(root: Path):
    """Пути к файлам с кодом. В пропускаемые каталоги не спускаемся вовсе —
    иначе обход материализует всё содержимое node_modules и ест память."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.suffix.lower() in CODE_EXT:
                yield path


def iter_code_files(root: Path):
    for path in iter_code_paths(root):
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            yield path, path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue


class LazyFiles:
    """Ведёт себя как словарь «путь → текст», но держит в памяти только пути.

    Текст каждого файла читается на время одной проверки и сразу отпускается.
    На проекте в несколько тысяч файлов это разница между полугигабайтом
    и единицами мегабайт.
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.names = [str(p.relative_to(root)) for p in iter_code_paths(root)]

    def items(self):
        for path, text in iter_code_files(self.root):
            yield str(path.relative_to(self.root)), text

    def values(self):
        for _, text in self.items():
            yield text

    def __iter__(self):
        return iter(self.names)

    def __len__(self) -> int:
        return len(self.names)


def line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def is_pattern_declaration(text: str, pos: int) -> bool:
    """Совпало объявление регулярного выражения, а не настоящий код."""
    # окно: текущая строка и две предыдущие — объявление часто многострочное
    start = pos
    for _ in range(3):
        prev = text.rfind("\n", 0, start)
        if prev == -1:
            start = 0
            break
        start = prev
    end = text.find("\n", pos)
    window = text[start: end if end != -1 else len(text)]
    return bool(re.search(r"(re\.compile|regex|_PATTERNS?\s*=|_RULES?\s*=|new RegExp)", window))


def add(findings, *, id, severity, title, where, what, why, fix):
    findings.append({
        "id": id, "severity": severity, "title": title,
        "where": where, "what": what, "why": why, "fix": fix,
        "area": "dead-code",
    })


def check_orphan_files(root: Path, findings: list, files: dict[str, str]) -> None:
    """Файл, на который никто не ссылается импортом."""
    referenced: set[str] = set()
    for rel, text in files.items():
        for m in JS_IMPORT.finditer(text):
            target = next(g for g in m.groups() if g)
            referenced.add(Path(target).stem)
            referenced.add(Path(target).name)
        for m in PY_FROM.finditer(text):
            for part in m.group(1).split("."):          # путь модуля
                referenced.add(part.strip())
            for name in m.group(2).replace("(", "").replace(")", "").split(","):
                referenced.add(name.split(" as ")[0].strip().strip("*"))   # from api import auth, leads
        for m in PY_IMPORT.finditer(text):
            for chunk in m.group(1).split(","):
                for part in chunk.split(" as ")[0].strip().split("."):
                    referenced.add(part.strip())

    orphans = []
    for rel in files:
        path = Path(rel)
        if (FRAMEWORK_ENTRY.search(rel) or CONFIG_LIKE.search(rel)
                or TEST_LIKE.search(rel) or STANDALONE.search(rel)):
            continue
        if path.stem in referenced or path.name in referenced:
            continue
        orphans.append(rel)

    for rel in orphans[:25]:
        add(findings,
            id="orphan_file", severity="low",
            title="На файл никто не ссылается",
            where=rel,
            what="Ни один другой файл проекта не импортирует его. Это подсказка, а не приговор: "
                 "файл может подключаться фреймворком по соглашению об именах или вызываться из скрипта.",
            why="Брошенный файл продолжает жить в репозитории: в нём может остаться старый ключ, отключённая "
                "проверка прав или маршрут, про который забыли. Такой код никто не поддерживает, но он "
                "попадает в сборку и в глаза следующему разработчику как рабочий.",
            fix="Проверьте, зовут ли файл снаружи (grep по имени, поиск в конфигах и скриптах запуска). "
                "Если нет — удалите, история останется в git.")
    if len(orphans) > 25:
        add(findings,
            id="orphan_many", severity="medium",
            title=f"Файлов без ссылок много: {len(orphans)}",
            where="проект целиком",
            what=f"Перечислены первые 25 из {len(orphans)}.",
            why="Такой объём обычно значит, что в проекте лежат целые куски заброшенных экспериментов.",
            fix="Пройдите папками по очереди: удалите то, что точно не нужно, и вынесите спорное в отдельную ветку.")


def check_backup_copies(root: Path, findings: list, files: dict[str, str]) -> None:
    for rel in files:
        if BACKUP_LIKE.search(Path(rel).name):
            add(findings,
                id="backup_file", severity="medium",
                title="Файл-копия рядом с рабочим",
                where=rel,
                what="Имя выглядит как ручная копия: версия, old, final, fixed, backup, bak.",
                why="Копии живут своей жизнью. Правку вносят в один файл, а собирается другой — так возвращаются "
                    "уже исправленные ошибки. В старой копии часто остаётся код без проверок прав, который "
                    "убрали из основного файла.",
                fix="Оставьте одну рабочую версию, остальные удалите — история изменений уже хранится в git.")


def check_stubs_and_todo(root: Path, findings: list, files: dict[str, str]) -> None:
    todo_count = 0
    todo_places: list[str] = []
    for rel, text in files.items():
        for m in STUB.finditer(text):
            if is_pattern_declaration(text, m.start()):
                continue
            add(findings,
                id="stub_code", severity="medium",
                title="Функция-заглушка",
                where=f"{rel}:{line_no(text, m.start())}",
                what=f"Найдено `{m.group(0).strip().splitlines()[0][:60]}` — тело не написано.",
                why="Заглушка выглядит как готовая функция и вызывается как готовая. Если её зовут на проверке "
                    "прав или на валидации ввода, проверка молча не происходит, а тесты остаются зелёными.",
                fix="Либо допишите тело, либо удалите вызовы и саму функцию. Промежуточное состояние опаснее обоих.")
            break
        for m in TODO_MARK.finditer(text):
            todo_count += 1
            if len(todo_places) < 10:
                todo_places.append(f"{rel}:{line_no(text, m.start())}")
    if todo_count:
        add(findings,
            id="todo_marks", severity="low",
            title=f"Незакрытых пометок TODO / FIXME: {todo_count}",
            where=", ".join(todo_places) + (" …" if todo_count > len(todo_places) else ""),
            what="Пометки о недоделанном разбросаны по коду.",
            why="Часть таких пометок — это отложенная проверка прав или валидация «доделаю потом». "
                "Пока они висят, непонятно, какие куски кода можно считать готовыми.",
            fix="Пройдитесь по списку: закройте то, что делается за минуту, остальное вынесите в задачи и уберите из кода.")


def check_commented_blocks(root: Path, findings: list, files: dict[str, str]) -> None:
    for rel, text in files.items():
        for m in COMMENTED_CODE.finditer(text):
            block = m.group(0)
            if len(CODE_SIGNAL.findall(block)) < 3:
                continue  # это обычный текстовый комментарий, а не закомментированный код
            add(findings,
                id="commented_code", severity="low",
                title="Закомментированный блок кода",
                where=f"{rel}:{line_no(text, m.start())}",
                what=f"Подряд {block.count(chr(10))} строк кода спрятаны в комментарии.",
                why="Такой блок читается как «здесь было что-то важное» и мешает понять текущее поведение. "
                    "Иногда в нём остаются рабочие ключи и адреса внутренних сервисов.",
                fix="Удалите блок — если понадобится, он найдётся в истории git.")
            break


def check_unreachable(root: Path, findings: list, files: dict[str, str]) -> None:
    for rel, text in files.items():
        if Path(rel).suffix.lower() not in {".py", ".js", ".jsx", ".ts", ".tsx"}:
            continue
        for m in UNREACHABLE.finditer(text):
            add(findings,
                id="unreachable", severity="medium",
                title="Код после выхода из функции",
                where=f"{rel}:{line_no(text, m.start())}",
                what="Ниже return / raise / throw на том же уровне отступа есть ещё строки — они не выполнятся.",
                why="Обычно это след незаконченной правки: кусок логики выключили, а не удалили. "
                    "Если там была проверка прав или запись в журнал, они просто перестали работать, "
                    "и внешне всё выглядит нормально.",
                fix="Проверьте, что должно выполняться, и уберите лишнее или перенесите выше.")
            break


def check_unused_deps(root: Path, findings: list, files: dict[str, str]) -> None:
    package = root / "package.json"
    if not package.exists():
        return
    try:
        data = json.loads(package.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, json.JSONDecodeError, ValueError):
        return
    deps = list((data.get("dependencies") or {}).keys())
    if not deps:
        return
    config_text = ""
    for name in ("next.config.js", "next.config.mjs", "vite.config.ts", "vite.config.js",
                 "tailwind.config.js", "tailwind.config.ts", "postcss.config.js"):
        candidate = root / name
        if candidate.exists():
            config_text += candidate.read_text(encoding="utf-8", errors="ignore")

    # Ищем упоминания пакетов за один проход, не склеивая проект в одну строку.
    seen: set[str] = set()
    for _, text in files.items():
        for dep in deps:
            if dep in seen:
                continue
            if dep in text or dep.split("/")[-1] in text:
                seen.add(dep)
    unused = [d for d in deps if d not in seen and d not in config_text]
    if unused:
        add(findings,
            id="unused_deps", severity="low",
            title=f"Похоже, неиспользуемых зависимостей: {len(unused)}",
            where="package.json",
            what="Пакеты не встречаются в коде: " + ", ".join(unused[:12]) + ("…" if len(unused) > 12 else ""),
            why="Каждая лишняя зависимость — это чужой код в вашей сборке и ещё одна строка, по которой "
                "к вам могут прийти через известную уязвимость. Проверять и обновлять приходится и то, чем не пользуетесь.",
            fix="Удостоверьтесь, что пакет не нужен сборщику или конфигу, и удалите: npm uninstall <пакет>.")


# Типы и интерфейсы намеренно не проверяем: их экспортируют для читаемости,
# и «неиспользуемый» тип — норма, а не мусор.
JS_EXPORT = re.compile(r"(?m)^export\s+(?:const|function|class)\s+(\w+)")
JS_REEXPORT = re.compile(r"(?m)^export\s*\{([^}]+)\}")
PY_DEF = re.compile(r"(?m)^(?:def|class)\s+(\w+)")
ROUTE_PATH = re.compile(r"""(?i)(?:app|router|api)\.(?:get|post|put|patch|delete)\s*\(\s*["'`]([^"'`]{2,60})["'`]"""
                        r"""|@(?:app|router)\.(?:get|post|put|patch|delete)\s*\(\s*["'`]([^"'`]{2,60})["'`]""")
TRPC_PROC = re.compile(r"(?m)^\s*(\w+)\s*:\s*\w*[Pp]rocedure[\s.\n]")
DEBUG_PRINT = re.compile(r"(?m)^\s*(console\.(log|debug|dir)|print)\s*\(")


def check_unused_exports(root: Path, findings: list, files: dict[str, str]) -> None:
    """Экспорт объявлен, но никто снаружи его не импортирует."""
    exported: dict[str, str] = {}          # имя → где объявлено
    for rel, text in files.items():
        if TEST_LIKE.search(rel) or STANDALONE.search(rel) or CONFIG_LIKE.search(rel):
            continue
        suffix = Path(rel).suffix.lower()
        if suffix in {".ts", ".tsx", ".js", ".jsx", ".mjs"}:
            for m in JS_EXPORT.finditer(text):
                exported.setdefault(m.group(1), f"{rel}:{line_no(text, m.start())}")
            for m in JS_REEXPORT.finditer(text):
                for name in m.group(1).split(","):
                    clean = name.split(" as ")[-1].strip()
                    if clean:
                        exported.setdefault(clean, f"{rel}:{line_no(text, m.start())}")

    # Второй проход: один раз по файлам, отмечаем имена, которые где-то зовут.
    # Перебирать файлы заново на каждое имя нельзя — это чтение диска в квадрате.
    candidates = {n: w for n, w in exported.items() if len(n) >= 3}
    used: set[str] = set()
    for rel, text in files.items():
        for name in candidates:
            if name in used or candidates[name].split(":")[0] == rel:
                continue
            if name in text and re.search(rf"\b{re.escape(name)}\b", text):
                used.add(name)

    unused = [(n, w) for n, w in candidates.items() if n not in used]

    for name, where in unused[:20]:
        add(findings,
            id="unused_export", severity="low",
            title=f"Экспорт `{name}` никем не используется",
            where=where,
            what="Значение объявлено как экспортируемое, но ни один другой файл проекта на него не ссылается.",
            why="Экспорт — это обещание, что снаружи этим пользуются. Пока обещание висит, код нельзя ни удалить "
                "спокойно, ни изменить: непонятно, кого сломаешь. Такие хвосты накапливаются и превращают "
                "простую правку в исследование.",
            fix="Убедитесь, что имя не зовут динамически (по строке, через реестр), и уберите экспорт "
                "или сам код целиком. Для готовых наборов компонентов (shadcn и подобные) это нормально: "
                "их копируют целиком, и часть остаётся про запас — такие можно оставить осознанно.")
    if len(unused) > 20:
        add(findings,
            id="unused_export_many", severity="medium",
            title=f"Неиспользуемых экспортов много: {len(unused)}",
            where="проект целиком",
            what=f"Показаны первые 20 из {len(unused)}.",
            why="Такой объём означает, что публичная поверхность кода намного больше, чем реально нужно проекту.",
            fix="Пройдите по папкам и оставьте экспортируемым только то, что зовут снаружи.")


def check_orphan_routes(root: Path, findings: list, files: dict[str, str]) -> None:
    """Маршрут объявлен, но обращений к нему в проекте не видно."""
    routes: dict[str, str] = {}
    for rel, text in files.items():
        if TEST_LIKE.search(rel):
            continue
        for m in ROUTE_PATH.finditer(text):
            path_value = (m.group(1) or m.group(2) or "").strip()
            if len(path_value) > 2 and path_value not in {"/", "/*"}:
                routes.setdefault(path_value, f"{rel}:{line_no(text, m.start())}")
        for m in TRPC_PROC.finditer(text):
            routes.setdefault(f"trpc:{m.group(1)}", f"{rel}:{line_no(text, m.start())}")

    # Тот же приём: один проход по файлам вместо перебора файлов на каждый маршрут.
    checked = dict(list(routes.items())[:30])
    called: set[str] = set()
    for rel, text in files.items():
        for route, where in checked.items():
            if route in called or where.split(":")[0] == rel:
                continue
            needle = route.split(":", 1)[1] if route.startswith("trpc:") else route
            if needle in text:
                called.add(route)

    for route, where in checked.items():
        if route in called:
            continue
        add(findings,
            id="orphan_route", severity="medium",
            title=f"К маршруту `{route}` обращений не видно",
            where=where,
            what="Маршрут объявлен, но нигде в проекте нет вызова по этому адресу.",
            why="Забытый маршрут остаётся рабочей дверью: он отвечает на запросы, но его никто не проверяет "
                "и не помнит, какие проверки прав там были. Именно такие адреса находят перебором и используют "
                "в обход интерфейса.",
            fix="Проверьте, не зовут ли адрес снаружи — из мобильного приложения, чужого сервиса, вебхука. "
                "Если нет, удалите маршрут; если да, задокументируйте и проверьте на нём авторизацию.")


def check_debug_output(root: Path, findings: list, files: dict[str, str]) -> None:
    hits: list[str] = []
    for rel, text in files.items():
        if TEST_LIKE.search(rel) or STANDALONE.search(rel):
            continue
        for m in DEBUG_PRINT.finditer(text):
            hits.append(f"{rel}:{line_no(text, m.start())}")
    if len(hits) >= 5:
        add(findings,
            id="debug_output", severity="low",
            title=f"Отладочный вывод остался в коде: {len(hits)} мест",
            where=", ".join(hits[:8]) + (" …" if len(hits) > 8 else ""),
            what="Вызовы console.log и print разбросаны по рабочему коду.",
            why="Отладочный вывод пишет в журнал то, о чём не думали как о публичном: идентификаторы, куски "
                "запросов, иногда токены. Плюс он замедляет работу и мешает читать настоящие сообщения об ошибках.",
            fix="Уберите отладочные вызовы или замените на журналирование с уровнями, чтобы лишнее выключалось настройкой.")


def check_oversized(root: Path, findings: list, files: dict[str, str]) -> None:
    """Раздутые файлы и длинные функции — из наших лимитов размера."""
    for rel, text in files.items():
        if TEST_LIKE.search(rel):
            continue
        lines = text.count("\n") + 1
        if lines > 600:
            add(findings,
                id="oversized_file", severity="medium",
                title=f"Файл вырос до {lines} строк",
                where=rel,
                what="Превышен предел в 600 строк, за которым файл перестают читать целиком.",
                why="В таком файле правки делают вслепую, по поиску. Именно так рядом с рабочим кодом появляются "
                    "забытые куски и вторые реализации того же самого — а проверки прав теряются при переносе.",
                fix="Разделите по смыслу задач, а не по техническим слоям: отдельный файл на область ответственности.")


SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEV_LABEL = {"critical": "КРИТИЧНО", "high": "ВЫСОКИЙ", "medium": "СРЕДНИЙ", "low": "НИЗКИЙ"}


def build_markdown(findings: list, root: Path) -> str:
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEV_ORDER}
    lines = [
        "# Отчёт vibecheck — мёртвый код",
        "",
        f"Проект: `{root}`",
        f"**Найдено {len(findings)}: высоких {counts['high']}, средних {counts['medium']}, низких {counts['low']}**",
        "",
    ]
    if not findings:
        lines.append("Брошенного кода не нашлось.")
        return "\n".join(lines)
    for finding in sorted(findings, key=lambda f: SEV_ORDER[f["severity"]]):
        lines += [
            f"## [{SEV_LABEL[finding['severity']]}] {finding['title']}",
            "",
            f"**Где:** `{finding['where']}`",
            "",
            f"**Что нашли:** {finding['what']}",
            "",
            f"**Почему это мешает:** {finding['why']}",
            "",
            f"**Как исправить:** {finding['fix']}",
            "",
        ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="vibecheck — сканер мёртвого кода")
    parser.add_argument("path", nargs="?", default=".", help="папка проекта")
    parser.add_argument("--json", action="store_true", help="вывести находки в JSON")
    parser.add_argument("--report", metavar="FILE", help="записать markdown-отчёт в файл")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Не папка: {root}", file=sys.stderr)
        return 1

    files = LazyFiles(root)
    findings: list = []
    for check in (check_orphan_files, check_backup_copies, check_stubs_and_todo,
                  check_commented_blocks, check_unreachable, check_unused_deps,
                  check_unused_exports, check_orphan_routes, check_debug_output, check_oversized):
        try:
            check(root, findings, files)
        except Exception as exc:
            print(f"[warn] проверка {check.__name__} прервалась: {exc}", file=sys.stderr)

    findings.sort(key=lambda f: SEV_ORDER[f["severity"]])

    if args.json:
        json.dump(findings, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return 0

    if args.report:
        Path(args.report).write_text(build_markdown(findings, root), encoding="utf-8")

    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEV_ORDER}
    print(f"vibecheck / мёртвый код: {len(findings)} находок "
          f"(средних {counts['medium']}, низких {counts['low']}) в {len(files)} файлах")
    for finding in findings[:5]:
        print(f"  [{SEV_LABEL[finding['severity']]}] {finding['title']} — {finding['where']}")
    if args.report:
        print(f"Отчёт: {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
