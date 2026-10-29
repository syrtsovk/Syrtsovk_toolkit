#!/usr/bin/env python3
"""Проверка добавляемых строк на секреты и ПДн перед коммитом бэкапа (/backup).

Три слоя (скан только по шаблонам ключей пропускает пароли, написанные словами):
  1. жёсткие шаблоны ключей/токенов/вебхуков;
  2. слова «пароль/password/token/секрет/api key» + значение;
  3. длинные смешанные строки (буквы+цифры) вне ссылок и путей — только как «подозрение».

Печатает ТОЛЬКО файл, номер строки, тип и длину значения. Значение не выводится никогда
(маска не ловит спецсимволы, поэтому не показываем даже начало).

Использование:
  secret_scan.py --staged                 # то, что в git add (дифф)
  secret_scan.py --diff REF1..REF2        # дифф между коммитами
  secret_scan.py путь [путь …]            # файлы целиком
  secret_scan.py --known-values FILE ...  # + обратный поиск значений из FILE (по одному на строку)
Код возврата: 0 — чисто, 1 — есть находки уровня HARD/WORD, 2 — только подозрения.
"""
import re
import subprocess
import sys

HARD = re.compile(
    r"sk-[A-Za-z0-9_-]{16,}|sk-ant|ghp_[A-Za-z0-9]{20,}|github_pat_|xox[bap]-"
    r"|AIza[0-9A-Za-z_-]{20,}|AKIA[0-9A-Z]{12,}|BEGIN [A-Z ]*PRIVATE KEY"
    r"|\b\d{8,10}:[A-Za-z0-9_-]{35}\b|://[^/\s:@]+:[^/\s@]+@"
    r"|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}|sb_secret|sb_publishable"
    r"|hooks\.slack\.com/services/\S+"
    r"|discord(?:app)?\.com/api/webhooks/\S+"
    r"|AGE-SECRET-KEY-1[0-9A-Z]{20,}"

)
SSHPASS = re.compile(r"sshpass\s+-p\s+'([^']{4,})'")
WORDS = re.compile(
    r"(парол[ьяюе]|password|passwd|passphrase|парольная фраза|token|токен|секрет|secret|api[_ -]?key)"
    r"\W{0,6}[:=]\s*[`'\"]?([A-Za-z0-9_\-!@#$%^&*./+=]{8,})",
    re.I,
)
MIXED = re.compile(r"(?<![A-Za-z0-9/_.\-=:])(?=[A-Za-z0-9_\-]*[0-9])(?=[A-Za-z0-9_\-]*[A-Za-z])[A-Za-z0-9_\-]{32,}(?![A-Za-z0-9/_.\-])")
PLACEHOLDER = re.compile(r"(<.*>|REDACTED|ПАРОЛЬ|XXX+|\*+|…+|example|your.*|\$\{?\w+\}?|none|null|true|false)", re.I)
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def lines_from_diff(diff: str):
    """Возвращает (файл, номер_строки_в_новой_версии, текст) только для добавленных строк."""
    f, n = None, 0
    for raw in diff.splitlines():
        if raw.startswith("+++ b/"):
            f = raw[6:]
        elif raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            n = int(m.group(1)) - 1 if m else 0
        elif raw.startswith("+") and not raw.startswith("+++"):
            n += 1
            yield f, n, raw[1:]
        elif not raw.startswith("-"):
            n += 1


def lines_from_files(paths):
    for p in paths:
        try:
            for i, l in enumerate(open(p, encoding="utf-8", errors="ignore").read().splitlines(), 1):
                yield p, i, l
        except OSError:
            continue


def scan(items, known):
    hard, word, susp = [], [], []
    for f, i, l in items:
        if f and f.endswith('secret_scan.py'):   # шаблоны в самом сканере — не секреты
            continue
        if HARD.search(l):
            hard.append((f, i, "шаблон ключа/вебхука", len(HARD.search(l).group(0))))
        sp = SSHPASS.search(l)
        if sp and not PLACEHOLDER.fullmatch(sp.group(1)) and not sp.group(1).startswith('<'):
            hard.append((f, i, "sshpass с реальным паролем", len(sp.group(1))))
        m = WORDS.search(l)
        if m and not PLACEHOLDER.fullmatch(m.group(2)) and '...' not in m.group(2) and '…' not in m.group(2):
            word.append((f, i, f"«{m.group(1).lower()}» + значение", len(m.group(2))))
        for mm in MIXED.finditer(l):
            s = mm.group(0)
            if UUID.match(s) or re.fullmatch(r"[0-9a-f]{40,64}", s):
                continue
            susp.append((f, i, "длинная смешанная строка", len(s)))
            break
        for v in known:
            if v and v in l:
                hard.append((f, i, "ИЗВЕСТНОЕ значение секрета", len(v)))
    return hard, word, susp


def main(argv):
    known, items = [], []
    args = argv[1:]
    if "--known-values" in args:
        k = args.index("--known-values")
        known = [x.strip() for x in open(args[k + 1], encoding="utf-8").read().splitlines() if len(x.strip()) >= 6]
        del args[k:k + 2]
    if not args:
        print(__doc__)
        return 0
    if args[0] == "--staged":
        d = subprocess.run(["git", "diff", "--cached", "-U0"], capture_output=True).stdout.decode("utf-8", "ignore")
        items = list(lines_from_diff(d))
    elif args[0] == "--diff":
        d = subprocess.run(["git", "diff", "-U0", args[1]], capture_output=True).stdout.decode("utf-8", "ignore")
        items = list(lines_from_diff(d))
    else:
        items = list(lines_from_files(args))
    hard, word, susp = scan(items, known)
    for title, rows in (("HARD (шаблон ключа)", hard), ("WORD (слово+значение)", word), ("ПОДОЗРЕНИЕ", susp)):
        print(f"{title}: {len(rows)}")
        for f, i, t, n in rows[:25]:
            print(f"   {f}:{i}  {t}, длина {n}")
    if hard or word:
        return 1
    return 2 if susp else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
