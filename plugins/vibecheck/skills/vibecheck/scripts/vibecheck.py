#!/usr/bin/env python3
"""vibecheck: сборщик единого отчёта.

Зовёт оба сканера, складывает повторы в одну запись и сортирует находки
по тому, чем они грозят приложению, а не по типу проверки.

Запуск:
    python3 vibecheck.py /путь/к/проекту
    python3 vibecheck.py . --report vibecheck-report.md
    python3 vibecheck.py . --json
    python3 vibecheck.py . --only money,data     # выборочно
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ─────────────── чем находка грозит приложению ───────────────
# Порядок здесь и есть порядок в отчёте: сначала деньги, в конце — развитие.
IMPACT_ORDER = ["money", "data", "downtime", "wrong", "growth"]

IMPACT_TITLE = {
    "money": "Утекут деньги",
    "data": "Заберут или сотрут данные",
    "downtime": "Ляжет под нагрузкой",
    "wrong": "Работает не так, как задумано",
    "growth": "Мешает развивать проект",
}

IMPACT_LEAD = {
    "money": "По этим местам платит владелец проекта, а пользуется кто-то другой.",
    "data": "Через эти места забирают данные пользователей или получают чужой доступ.",
    "downtime": "Эти места дают положить сервис простым перебором или потоком запросов.",
    "wrong": "Здесь код делает не то, что задумано, и внешне это незаметно.",
    "growth": "Это не ломает работу сегодня, но каждая следующая правка делается вслепую.",
}

# Какая находка к чему относится. Незнакомый идентификатор попадает в growth.
IMPACT_BY_ID = {
    # деньги — ключи от платных сервисов и всё, что жжёт баланс
    "anthropic_key": "money", "openrouter_key": "money", "openai_key": "money",
    "stripe_live": "money", "aws_key": "money", "sendgrid": "money", "twilio": "money",
    "google_api": "money", "paid_api_from_client": "money",
    "llm_open_endpoint": "money", "llm_no_limit": "money",

    # данные и доступ
    "github_token": "data", "slack_token": "data", "telegram_bot": "data",
    "supabase_service": "data", "private_key": "data", "db_url_pass": "data",
    "generic_secret": "data", "env_in_git": "data", "env_not_ignored": "data",
    "public_env_secret": "data", "secret_in_log": "data", "secret_in_dockerfile": "data",
    "sql_fstring": "data", "sql_template": "data", "prisma_unsafe": "data",
    "jwt_none": "data", "jwt_no_expiry": "data", "role_from_client": "data",
    "idor_suspect": "data", "xss_html": "data", "firebase_open": "data",
    "default_db_password": "data", "db_port_exposed": "data", "path_traversal": "data",
    "shell_injection": "data", "pickle_load": "data", "eval_use": "data",
    "tls_off": "data", "weak_hash_password": "data", "cors_star": "data",
    "debug_prod": "data", "vulnerable_deps": "data",

    # доступность
    "no_rate_limit": "downtime", "upload_unbounded": "downtime",

    # неверная работа
    "swallowed_error": "wrong", "stub_code": "wrong", "unreachable": "wrong",

    # развитие
    "orphan_file": "growth", "orphan_many": "growth", "orphan_route": "growth",
    "unused_export": "growth", "unused_export_many": "growth", "backup_file": "growth",
    "commented_code": "growth", "todo_marks": "growth", "unused_deps": "growth",
    "oversized_file": "growth", "debug_output": "growth",
    "deps_not_checked": "growth", "pip_audit_hint": "growth",
}


def places_word(n: int) -> str:
    """Правильная форма: 1 место, 2 места, 5 мест."""
    if 11 <= n % 100 <= 14:
        return "мест"
    return {1: "место", 2: "места", 3: "места", 4: "места"}.get(n % 10, "мест")


SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEV_LABEL = {"critical": "КРИТИЧНО", "high": "ВЫСОКИЙ", "medium": "СРЕДНИЙ", "low": "НИЗКИЙ"}

# Начиная с этого числа одинаковые находки складываются в одну запись.
GROUP_FROM = 3
# У этих находок цифры и текст разные, поэтому «одно и то же в N местах» —
# неправда. Их сводим в одну запись с перечнем, а не складываем как повторы.
# вид находки → (заголовок свода, единица для худшего случая)
SUMMARIZE = {
    "oversized_file": ("Файлы разрослись больше 600 строк", "строк"),
    "orphan_file": ("Файлы, на которые никто не ссылается", ""),
    "unused_export": ("Экспорты, которые никем не используются", ""),
}
# А эти уже сами по себе сводные — трогать нечего.
NEVER_GROUP = {"orphan_many", "unused_export_many", "todo_marks",
               "debug_output", "unused_deps", "vulnerable_deps"}
# Сколько мест показать внутри сложенной записи.
GROUP_SHOW = 5
# Потолок записей в теле отчёта; остальное уходит в приложение.
BODY_LIMIT = 30


BASELINE_FILE = ".vibecheck-baseline.json"
IGNORE_FILE = ".vibecheckignore"


def finding_key(f: dict) -> str:
    """Опознаём находку так, чтобы сдвиг строк её не «обновлял».

    Номер строки в ключ не входит: одна добавленная строка выше по файлу
    иначе превращала бы все находки в нём в новые.
    """
    return f"{f['id']}|{f['where'].split(':')[0].strip()}"


def load_ignore(root: Path) -> list[tuple[str | None, str | None]]:
    """Читает .vibecheckignore. Строка — это `id`, `путь`, либо `id:путь`.

    Пути сравниваются как шаблоны: src/components/ui/* закрывает всю папку.
    """
    path = root / IGNORE_FILE
    if not path.exists():
        return []
    rules: list[tuple[str | None, str | None]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        if ":" in line:
            fid, glob = line.split(":", 1)
            rules.append((fid.strip() or None, glob.strip() or None))
        elif "/" in line or "*" in line or "." in line:
            rules.append((None, line))
        else:
            rules.append((line, None))
    return rules


def is_ignored(f: dict, rules: list[tuple[str | None, str | None]]) -> bool:
    place = f["where"].split(":")[0].strip()
    for fid, glob in rules:
        if fid and f["id"] != fid:
            continue
        if glob and not (fnmatch(place, glob) or fnmatch(place, glob.rstrip("/") + "/*")):
            continue
        return True
    return False


def load_baseline(root: Path) -> set[str] | None:
    path = root / BASELINE_FILE
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return set(data.get("keys", []))
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def save_baseline(root: Path, findings: list[dict]) -> tuple[int, bool]:
    """Пишет отправную точку и сам прикрывает её от коммита.

    Файл служебный и у каждого свой: уехав в общую историю, он будет
    конфликтовать у всех подряд.
    """
    keys = sorted({finding_key(f) for f in findings})
    (root / BASELINE_FILE).write_text(
        json.dumps({"version": 1, "keys": keys}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    ignored = False
    if (root / ".git").exists():
        gitignore = root / ".gitignore"
        current = gitignore.read_text(encoding="utf-8", errors="ignore") if gitignore.exists() else ""
        if BASELINE_FILE not in current:
            with gitignore.open("a", encoding="utf-8") as fh:
                if current and not current.endswith("\n"):
                    fh.write("\n")
                fh.write(f"\n# служебные файлы vibecheck\n{BASELINE_FILE}\n")
            ignored = True
    return len(keys), ignored


def count_scanned(root: Path) -> dict:
    """Что и сколько реально просмотрено.

    Сканер секретов ходит шире, чем по коду: настройки, скрипты выкатки,
    docker-файлы. Считать только код — занижать охват и путать человека.
    """
    # тот же список, что у сканеров: две точки правды на один вопрос
    # рано или поздно расходятся
    skip = {".git", "node_modules", ".next", "dist", "build", ".venv", "venv", "env",
            "__pycache__", ".pytest_cache", "vendor", "target", ".idea", ".vscode",
            "coverage", ".turbo", ".cache", "site-packages", ".mypy_cache", ".tox",
            ".claude", ".cursor"}
    code_ext = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".vue",
                ".svelte", ".go", ".rb", ".php", ".java", ".kt", ".rs", ".cs", ".swift"}
    code = text = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for name in filenames:
            suffix = Path(name).suffix.lower()
            if suffix in code_ext:
                code += 1
                text += 1
            elif suffix in {".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".conf",
                            ".sh", ".bash", ".zsh", ".sql", ".tf", ".xml", ".properties"} \
                    or name.startswith((".env", "Dockerfile", "docker-compose")):
                text += 1

    def rule_count(script: str) -> int:
        """Виды находок сканера: и объявленные в таблицах, и заданные по месту."""
        try:
            src = (HERE / script).read_text(encoding="utf-8")
        except OSError:
            return 0
        ids = set(re.findall(r'id="(\w+)"', src))
        ids |= set(re.findall(r'\(\s*"(\w+)",\s*"(?:critical|high|medium|low)"', src))
        return len(ids)

    return {
        "code_files": code,
        "text_files": text,
        "security_rules": rule_count("scan_security.py"),
        "dead_rules": rule_count("scan_dead.py"),
    }


def run_scanner(script: str, root: Path) -> list[dict]:
    """Запускает сканер и забирает его находки."""
    try:
        out = subprocess.run(
            [sys.executable, str(HERE / script), str(root), "--json"],
            capture_output=True, text=True, timeout=900,
        )
        if out.returncode != 0:
            print(f"[warn] {script} завершился с кодом {out.returncode}", file=sys.stderr)
        return json.loads(out.stdout) if out.stdout.strip() else []
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, ValueError) as exc:
        print(f"[warn] {script} не отработал: {exc}", file=sys.stderr)
        return []


def group_repeats(findings: list[dict]) -> list[dict]:
    """Складывает одинаковые находки в одну запись.

    Сорок семь одинаковых пунктов — это не сорок семь проблем, а одна
    привычка в проекте. В отчёте она должна занимать одну запись.
    """
    by_id: dict[str, list[dict]] = {}
    for f in findings:
        by_id.setdefault(f["id"], []).append(f)

    result: list[dict] = []
    for fid, group in by_id.items():
        if len(group) < GROUP_FROM or fid in NEVER_GROUP:
            result.extend(group)
            continue
        group.sort(key=lambda f: SEV_ORDER.get(f["severity"], 9))
        head = dict(group[0])
        places = [f["where"] for f in group]

        if fid in SUMMARIZE:
            # каждая находка со своими цифрами — перечисляем, а не обобщаем.
            # В заголовок выносим худший случай: иначе туда попадает первый
            # попавшийся, и человек недооценивает масштаб.
            label, unit = SUMMARIZE[fid]
            numbers = [int(n) for f in group for n in re.findall(r"\b(\d{2,})\b", f["title"])]
            worst = f", самый крупный — {max(numbers)} {unit}".rstrip() if numbers and unit else ""
            head["title"] = f"{label} — таких {len(group)}{worst}"
            head["where"] = "; ".join(places[:GROUP_SHOW]) + (
                f" … и ещё {len(places) - GROUP_SHOW}" if len(places) > GROUP_SHOW else "")
            head["what"] = (f"Под это правило попало {len(group)} разных мест, "
                            f"у каждого свои цифры. Полный перечень — в приложении к отчёту.")
        else:
            head["title"] = f"{head['title']} — {len(group)} {places_word(len(group))}"
            head["where"] = "; ".join(places[:GROUP_SHOW]) + (
                f" … и ещё {len(places) - GROUP_SHOW}" if len(places) > GROUP_SHOW else "")
            head["what"] = (f"Одно и то же повторяется в {len(group)} местах проекта. "
                            f"{head['what']}")
        head["grouped"] = len(group)
        head["all_places"] = places
        result.append(head)
    return result


def enrich(findings: list[dict]) -> list[dict]:
    for f in findings:
        f["impact"] = IMPACT_BY_ID.get(f["id"], "growth")
    return findings


def sort_key(f: dict) -> tuple:
    return (IMPACT_ORDER.index(f["impact"]), SEV_ORDER.get(f["severity"], 9), f["id"])


def verdict(findings: list[dict]) -> str:
    """Состояние приложения одной строкой — по худшему из найденного."""
    money = [f for f in findings if f["impact"] == "money"]
    data = [f for f in findings if f["impact"] == "data"]
    crit = [f for f in findings if f["severity"] == "critical"]
    high = [f for f in findings if f["severity"] == "high"]

    if any(f["severity"] in {"critical", "high"} for f in money):
        return "ДЕНЬГИ ПОД УГРОЗОЙ — чинить сегодня"
    if any(f["severity"] == "critical" for f in data):
        return "ДАННЫЕ ПОД УГРОЗОЙ — чинить сегодня"
    if crit:
        return "ЕСТЬ КРИТИЧНОЕ — выкладывать рано"
    if high:
        return "РАБОТАТЬ МОЖНО, ПОЧИНИТЬ НА ЭТОЙ НЕДЕЛЕ"
    if findings:
        return "СЕРЬЁЗНОГО НЕ НАЙДЕНО — остальное когда дойдут руки"
    return "ТИПОВЫХ ОШИБОК НЕ НАЙДЕНО"


def render_finding(f: dict) -> list[str]:
    why_label = "Почему это мешает" if f["impact"] == "growth" else "Почему это опасно"
    return [
        f"### [{SEV_LABEL[f['severity']]}] {f['title']}",
        "",
        f"**Где:** `{f['where']}`",
        "",
        f"**Что нашли:** {f['what']}",
        "",
        f"**{why_label}:** {f['why']}",
        "",
        f"**Как исправить:** {f['fix']}",
        "",
    ]


def build_report(findings: list[dict], root: Path, scanned: dict,
                 fresh_count: int | None = None, ignored_count: int = 0) -> str:
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEV_ORDER}
    raw_total = sum(f.get("grouped", 1) for f in findings)

    lines = [
        "# Отчёт vibecheck",
        "",
        f"Проект: `{root}`",
        "",
        f"**Состояние: {verdict(findings)}**",
        "",
        f"Записей в отчёте: {len(findings)} (за ними {raw_total} {places_word(raw_total)}). "
        f"Критичных {counts['critical']}, высоких {counts['high']}, "
        f"средних {counts['medium']}, низких {counts['low']}.",
        "",
    ]
    if fresh_count is not None:
        lines += [
            f"**С прошлой проверки появилось: {fresh_count}.** "
            + ("Остальное было и раньше." if fresh_count else "Нового нет."),
            "",
        ]
    if ignored_count:
        lines += [f"Заглушено через `{IGNORE_FILE}`: {ignored_count}.", ""]

    urgent = [f for f in findings if f["severity"] in {"critical", "high"}][:3]
    if urgent:
        lines += ["## Чинить прямо сейчас", ""]
        for i, f in enumerate(urgent, 1):
            place = f["where"].split(";")[0].strip()
            lines.append(f"{i}. **{f['title']}** — `{place}`")
            lines.append(f"   → {f['why'].split('.')[0]}.")
        lines.append("")

    body, appendix = findings[:BODY_LIMIT], findings[BODY_LIMIT:]

    shown_impacts = []
    for impact in IMPACT_ORDER:
        group = [f for f in body if f["impact"] == impact]
        if not group:
            continue
        shown_impacts.append(impact)
        lines += [f"## {IMPACT_TITLE[impact]}", "", IMPACT_LEAD[impact], ""]
        for f in group:
            lines += render_finding(f)

    if appendix:
        lines += [
            "## Приложение — остальные находки",
            "",
            f"Ещё {len(appendix)} записей, вынесены сюда, чтобы не перегружать основной список. "
            "Они не срочные, но посмотреть стоит.",
            "",
        ]
        for f in appendix:
            place = f["where"].split(";")[0].strip()
            lines.append(f"- **[{SEV_LABEL[f['severity']]}]** {f['title']} — `{place}` · {f['fix'].split('.')[0]}.")
        lines.append("")

    detailed = [f for f in findings if f.get("all_places") and len(f["all_places"]) > GROUP_SHOW]
    if detailed:
        lines += ["## Полные перечни", "",
                  "Здесь целиком то, что выше показано первыми пятью местами.", ""]
        for f in detailed:
            lines.append(f"**{f['title']}**")
            lines.append("")
            for place in f["all_places"]:
                lines.append(f"- `{place}`")
            lines.append("")

    lines += [
        "## Что проверить руками",
        "",
        "Сканер не заглядывает в личные кабинеты сервисов, а деньги и данные теряют чаще именно там: "
        "потолок трат, двойная защита входа, правила доступа к базе, рабочие резервные копии, "
        "права служебных доступов, доступы бывших участников проекта.",
        "",
        "## Что проверено",
        "",
        f"- просмотрено файлов: {scanned.get('text_files', '—')} "
        f"(из них с кодом {scanned.get('code_files', '—')}; остальное — настройки, "
        f"скрипты выкатки, docker-файлы: ключи ищутся и там)",
        f"- видов находок: {scanned.get('security_rules', '—')} по безопасности, "
        f"{scanned.get('dead_rules', '—')} по неиспользуемому коду",
        "",
        "Это поиск известных ошибок, а не проверка на проникновение. Скорость работы не измеряется — "
        "для неё нужен профилировщик на живой нагрузке. "
        "Пустой отчёт означает «типовых ошибок не нашли», а не «приложение безопасно»: "
        "логику прав внутри приложения, настройки в облаке и инфраструктуру проверяет человек.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="vibecheck — единый отчёт по проекту")
    parser.add_argument("path", nargs="?", default=".", help="папка проекта")
    parser.add_argument("--report", metavar="FILE", nargs="?", const="",
                        help="записать отчёт (без значения — vibecheck-report.md в корень проекта)")
    parser.add_argument("--no-report", action="store_true",
                        help="не писать файл, только сводка в терминал")
    parser.add_argument("--json", action="store_true", help="машинный вывод для скилла")
    parser.add_argument("--only", metavar="LIST",
                        help="через запятую: money,data,downtime,wrong,growth")
    parser.add_argument("--save-baseline", action="store_true",
                        help="запомнить текущие находки как отправную точку")
    parser.add_argument("--new", action="store_true",
                        help="показать только то, чего не было при прошлой проверке")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Не папка: {root}", file=sys.stderr)
        return 1

    findings = enrich(run_scanner("scan_security.py", root) + run_scanner("scan_dead.py", root))

    if args.only:
        wanted = {x.strip() for x in args.only.split(",")}
        unknown = wanted - set(IMPACT_ORDER)
        if unknown:
            print(f"Неизвестные значения --only: {', '.join(sorted(unknown))}. "
                  f"Доступны: {', '.join(IMPACT_ORDER)}", file=sys.stderr)
            return 1
        findings = [f for f in findings if f["impact"] in wanted]

    ignore_rules = load_ignore(root)
    ignored = [f for f in findings if is_ignored(f, ignore_rules)]
    findings = [f for f in findings if f not in ignored]

    if args.save_baseline:
        saved, ignored = save_baseline(root, findings)
        print(f"Отправная точка записана: {saved} находок в {BASELINE_FILE}")
        if ignored:
            print(f"Файл служебный, поэтому добавлен в .gitignore — в коммит не уедет.")
        print("Дальше запускай с --new — покажет только то, что появилось после этого момента.")
        return 0

    baseline = load_baseline(root)
    fresh: list[dict] = []
    if baseline is not None:
        fresh = [f for f in findings if finding_key(f) not in baseline]
        if args.new:
            findings = fresh

    findings = group_repeats(findings)
    findings.sort(key=sort_key)

    scanned = count_scanned(root)

    if args.json:
        json.dump(findings, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return 0

    report = build_report(findings, root, scanned, len(fresh) if baseline is not None else None,
                          len(ignored))
    report_path = None
    if not args.no_report:
        # по умолчанию кладём в проверяемый проект: человек должен знать, где смотреть
        # относительный путь — от проверяемого проекта, а не от того места,
        # откуда запустили: иначе отчёт ложится внутрь папки скилла и стирается
        # при следующем обновлении плагина
        if args.report:
            given = Path(args.report)
            report_path = given if given.is_absolute() else root / given
        else:
            report_path = root / "vibecheck-report.md"
        report_path.write_text(report, encoding="utf-8")

    raw_total = sum(f.get("grouped", 1) for f in findings)
    print(f"vibecheck: {verdict(findings)}")
    if baseline is not None:
        print(f"С прошлой проверки появилось: {len(fresh)}")
    if ignored:
        print(f"Заглушено через {IGNORE_FILE}: {len(ignored)}")
    print(f"Записей: {len(findings)} (за ними {raw_total} {places_word(raw_total)})")
    for impact in IMPACT_ORDER:
        n = sum(1 for f in findings if f["impact"] == impact)
        if n:
            print(f"  {IMPACT_TITLE[impact]}: {n}")
    for f in findings[:3]:
        if f["severity"] in {"critical", "high"}:
            print(f"  → {f['title']} — {f['where'].split(';')[0].strip()}")
    if report_path:
        print(f"\nПолный отчёт: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
