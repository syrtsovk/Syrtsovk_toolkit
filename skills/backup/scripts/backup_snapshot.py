#!/usr/bin/env python3
"""Бэкап настроек ИИ-инструментов (Claude Code, Codex, любая другая папка настроек) в ваш приватный git-репозиторий.

Что делает:
  1. Для каждой «цели» копирует белый список файлов из её папки в клон бэкап-репозитория <имя>-home/:
       claude  ~/.claude  {skills,commands,hooks,agents,scripts,CLAUDE.md,settings.json} + память проектов
                          + ~/.claude.json → claude.json.sanitized (список MCP-серверов, ключи <REDACTED>)
       codex   ~/.codex   {AGENTS.md,skills,agents,hooks,hooks.json} + config.toml → config.toml.sanitized
       своя    любая папка из custom_targets в config.json
     Ссылки разыменованы в обычные файлы, библиотеки и файлы с секретами исключены (EXCLUDES).
     Берётся только то, что в белом списке: входы в аккаунт (auth.json), история чатов и кэши не попадают никогда.
  2. Показывает, какие ваши git-репозитории не отправлены в облако (что пропадёт, если Mac умрёт).
  3. Проверяет, что репозиторий бэкапа приватный (через gh). Публичный — стоп, ничего не пишет.

Использование:
  backup_snapshot.py            # сухой прогон: что изменится + отчёт, ничего не пишет
  backup_snapshot.py --apply    # обновить снимок, git add, скан на секреты (коммит и пуш делает агент по SKILL.md)
  backup_snapshot.py --all      # в отчёте по репозиториям показать все, а не первые 25

Настройки (config.json рядом со скриптом, образец config.example.json; переменная BACKUP_REPO главнее):
  repo            — путь к клону бэкап-репозитория (по умолчанию ~/ai-backup)
  targets         — какие встроенные цели брать: ["claude", "codex"]; не задано = все, чья папка существует
  custom_targets  — свои цели: [{"name": "...", "home": "~/.папка", "items": [...], "sanitize_files": [...]}]
  extra_excludes  — что ещё не брать (шаблоны rsync)
  scan_dirs       — где искать ваши репозитории для отчёта «что не в облаке»
  include_memory  — брать ли память проектов Claude Code (true по умолчанию)

Код возврата при --apply: 0 чисто · 1 находки секретов, стоп · 2 подозрения, проверь · 3 нечего сохранять ·
4 репозиторий бэкапа публичный, стоп. Значения секретов не печатаются никогда.
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

HOME = Path.home()
HERE = Path(os.path.abspath(__file__)).parent
SKILL_DIR = HERE.parent
SCAN = HERE / "secret_scan.py"
EXCLUDES = [".venv", "venv", "node_modules", "__pycache__", "*.pyc", ".DS_Store", ".git", "ms-playwright",
            ".trash", ".env", ".env.*", "*.pem", "*.key", "secret_*", "*credential*"]
BUILTIN = {
    "claude": {"home": "~/.claude",
               "items": ["skills", "commands", "hooks", "agents", "scripts", "CLAUDE.md", "settings.json"],
               "memory": True,
               "sanitized": [("~/.claude.json", "claude.json.sanitized", "claude_json")]},
    "codex": {"home": "~/.codex",
              "items": ["AGENTS.md", "skills", "agents", "hooks", "hooks.json"],
              "sanitized": [("~/.codex/config.toml", "config.toml.sanitized", "toml")]},
}
SECRET_KEY = re.compile(r"key|token|secret|passw|auth|bearer|cookie|credential", re.I)
MIXED = re.compile(r"^(?=.*\d)(?=.*[A-Za-z])[A-Za-z0-9_\-.]{24,}$")
R = "<REDACTED>"
STUB = "<REDACTED: взять из менеджера паролей>"
QUOTED = re.compile(r"""((?:key|token|secret|passw\w*|api_?key)\w*["']?\s*[:=]\s*)(["'])([^"'\s]{8,})\2""", re.I)


def expand(p):
    return Path(os.path.expanduser(str(p)))


def load_config():
    cfg = {"repo": "~/ai-backup", "targets": None, "custom_targets": [], "extra_excludes": [],
           "scan_dirs": None, "include_memory": True}
    for p in (os.environ.get("BACKUP_CONFIG"), SKILL_DIR / "config.json", HOME / ".claude/skills/backup/config.json",
              HOME / ".codex/skills/backup/config.json"):
        if p and Path(p).is_file():
            cfg.update(json.loads(Path(p).read_text()))
            break
    if os.environ.get("BACKUP_REPO"):
        cfg["repo"] = os.environ["BACKUP_REPO"]
    return cfg


CFG = load_config()
REPO = expand(CFG["repo"])


def sh(*cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def active_targets():
    """Список целей: {name, home, items, memory, sanitized:[(src, dst_name, kind)]}."""
    out, wanted = [], CFG.get("targets")
    for name, t in BUILTIN.items():
        if (wanted is None and expand(t["home"]).is_dir()) or (wanted is not None and name in wanted):
            out.append({"name": name, **t})
    for c in CFG.get("custom_targets") or []:
        san = []
        for rel in c.get("sanitize_files") or []:
            kind = "toml" if rel.endswith(".toml") else "json" if rel.endswith(".json") else None
            if kind:
                san.append((f"{c['home']}/{rel}", f"{rel}.sanitized", kind))
            else:
                print(f"  ! {c['name']}: не умею чистить {rel} (только .json и .toml), файл не беру")
        skip = {rel for rel in c.get("sanitize_files") or []}
        out.append({"name": c["name"], "home": c["home"], "items": [i for i in c.get("items") or [] if i not in skip],
                    "sanitized": san})
    return [t for t in out if expand(t["home"]).is_dir()]


def _scan_module():
    spec = importlib.util.spec_from_file_location("secret_scan", SCAN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def scrub(path):
    """Ключи, зашитые прямо в скрипты, в снимок не берём: значение → заглушка."""
    try:
        text = path.read_text()
    except (UnicodeDecodeError, OSError):
        return
    hard = _scan_module().HARD
    new = QUOTED.sub(lambda m: m.group(0) if m.group(3).startswith("<") else f"{m.group(1)}{m.group(2)}{STUB}{m.group(2)}", text)
    new = hard.sub(STUB, new)
    if new != text:
        path.write_text(new)


def rsync(src, dst, apply):
    excludes = EXCLUDES + list(CFG.get("extra_excludes") or [])
    args = ["rsync", "-aL", "--delete", "--itemize-changes"] + [f"--exclude={e}" for e in excludes]
    if not apply:
        args.append("-n")
    if src.is_dir():
        if apply:
            dst.mkdir(parents=True, exist_ok=True)
        out = sh(*args, f"{src}/", f"{dst}/")
    else:
        if apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
        out = sh(*args, str(src), str(dst))
    lines = [l for l in out.stdout.splitlines() if l.startswith((">f", "*deleting"))]
    if apply:
        for l in lines:
            if l.startswith(">f"):
                scrub(dst / l.split(" ", 1)[1] if src.is_dir() else dst)
    return lines, out.stderr.strip()


def clean_value(k, v):
    if isinstance(v, str) and (SECRET_KEY.search(k) or MIXED.match(v)):
        return R
    return v


def clean_server(s):
    s = dict(s)
    for k in ("env", "headers"):
        if isinstance(s.get(k), dict):
            s[k] = {name: R for name in s[k]}
    if isinstance(s.get("url"), str) and "?" in s["url"]:
        s["url"] = s["url"].split("?", 1)[0] + "?" + R
    if isinstance(s.get("args"), list):
        out, hide = [], False  # hide: прошлый аргумент — флаг вида --api-key, значит этот — значение
        for a in map(str, s["args"]):
            name = a.split("=", 1)[0]
            if hide or MIXED.match(a):
                a = R
            elif "=" in a and SECRET_KEY.search(name):
                a = f"{name}={R}"
            hide = a.startswith("-") and "=" not in a and bool(SECRET_KEY.search(a))
            out.append(a)
        s["args"] = out
    return {k: (clean_value(k, v) if k not in ("env", "headers", "args", "url") else v) for k, v in s.items()}


def sanitized_claude_json(src):
    d = json.loads(src.read_text())
    out = {"_comment": f"Только структура MCP-серверов из ~/.claude.json, ключи заменены на {R}. Аккаунт, кэши, история не берутся. "
                       "Ключи — см. SECRETS-NEEDED.md. Этот файл НЕ ставится автоматически.",
           "_snapshot_date": date.today().isoformat(),
           "mcpServers": {n: clean_server(s) for n, s in (d.get("mcpServers") or {}).items()},
           "projectMcpServers": {}}
    for path, p in (d.get("projects") or {}).items():
        if p.get("mcpServers"):
            out["projectMcpServers"][path] = {n: clean_server(s) for n, s in p["mcpServers"].items()}
    return json.dumps(out, ensure_ascii=False, indent=2) + "\n"


def redact(obj, key=""):
    if isinstance(obj, dict):
        if key in ("env", "headers", "http_headers"):
            return {k: R for k in obj}
        return {k: redact(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(v, key) for v in obj]
    return clean_value(key, obj)


def sanitized_json(src):
    return json.dumps(redact(json.loads(src.read_text())), ensure_ascii=False, indent=2) + "\n"


def sanitized_toml(src):
    text = src.read_text()
    try:
        import tomllib  # Python 3.11+; на старом системном python проверку пропускаем
        tomllib.loads(text)  # битый файл — пусть упадёт, а не уйдёт криво
    except ImportError:
        pass
    out, table = [], ""
    for line in text.splitlines():
        m = re.match(r"\s*\[+([^\]]+)\]+", line)
        if m:
            table = m.group(1)
        kv = re.match(r"(\s*)([\w\"'.-]+)(\s*=\s*)(.+)", line)
        if kv and not m:
            key, val = kv.group(2), kv.group(4).strip()
            secret_table = re.search(r"(^|\.)(env|headers|http_headers)$", table)
            if secret_table or SECRET_KEY.search(key) or MIXED.match(val.strip("\"'")):
                line = f'{kv.group(1)}{key}{kv.group(3)}"{R}"'
        out.append(line)
    return "\n".join(out) + "\n"


SANITIZERS = {"claude_json": sanitized_claude_json, "json": sanitized_json, "toml": sanitized_toml}


def write_if_changed(path, text, apply):
    if text is None:
        return []
    old = path.read_text() if path.exists() else None
    strip = lambda t: re.sub(r'"_snapshot_date": "[^"]*"', "", t or "")  # дата меняется каждый день — сравниваем без неё
    if strip(old) == strip(text):
        return []
    if apply:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return [f">f {path.relative_to(REPO)}"]


def snapshot(apply):
    changes, manifest = {}, {}
    for t in active_targets():
        name, home, out = t["name"], expand(t["home"]), REPO / f"{t['name']}-home"
        manifest[name] = {"home": t["home"]}
        for it in t["items"]:
            src = home / it
            if src.exists():
                lines, err = rsync(src, out / it, apply)
                if err:
                    print(f"  ! rsync {name}/{it}: {err}")
                if lines:
                    changes[f"{name}/{it}"] = lines
        if t.get("memory") and CFG.get("include_memory", True):
            lines = []
            for mem in sorted(home.glob("projects/*/memory")):
                if mem.resolve().is_dir():
                    got, _ = rsync(mem.resolve(), out / "projects-memory" / mem.parent.name, apply)
                    lines += got
            if lines:
                changes[f"{name}/память проектов"] = lines
        for src_p, dst_name, kind in t.get("sanitized") or []:
            src = expand(src_p)
            if src.is_file():
                lines = write_if_changed(out / dst_name, SANITIZERS[kind](src), apply)
                if lines:
                    changes[f"{name}/{dst_name}"] = lines
    # какая цель в какую папку ставится при восстановлении
    lines = write_if_changed(REPO / "backup-manifest.json", json.dumps({"targets": manifest}, indent=2) + "\n", apply)
    if lines:
        changes["backup-manifest.json"] = lines
    return changes


def scan_dirs():
    if CFG.get("scan_dirs"):
        dirs = [expand(d) for d in CFG["scan_dirs"]]
    else:
        dirs = [HOME / d for d in ("Developer", "Projects", "Code", "dev", "src", "Documents/GitHub")]
    return [d for d in dirs if d.is_dir()]


def repo_status():
    """Что пропадёт, если Mac умрёт: репозитории без облака, коммиты только здесь, несохранённые файлы."""
    found = {REPO} if (REPO / ".git").exists() else set()
    for base in scan_dirs():
        for g in base.glob("**/.git"):
            if len(g.relative_to(base).parts) <= 4 and "node_modules" not in g.parts:
                found.add(g.parent)
    rows = []
    for r in sorted(found):
        st = sh("git", "status", "--porcelain=v1", cwd=r)
        if st.returncode:
            continue
        dirty = len([l for l in st.stdout.splitlines() if not l.endswith(".DS_Store")])
        has_remote = bool(sh("git", "remote", cwd=r).stdout.strip())
        local = sh("git", "rev-list", "--count", "HEAD", "--not", "--remotes", cwd=r).stdout.strip()
        local = int(local) if local.isdigit() else 0
        if not has_remote:
            sev, what = 0, f"НЕТ ОБЛАКА вообще (коммитов: {sh('git', 'rev-list', '--count', '--all', cwd=r).stdout.strip() or 0})"
        elif local:
            sev, what = 1, f"коммитов только здесь: {local}"
        elif dirty:
            sev, what = 2, ""
        else:
            continue
        if dirty:
            what = f"{what}; " if what else ""
            what += f"несохранённых файлов: {dirty}"
        rows.append((sev, -dirty, f"  {str(r).replace(str(HOME), '~')} — {what}"))
    rows.sort()
    limit = None if "--all" in sys.argv else 25
    out = [x[2] for x in rows[:limit]]
    if limit and len(rows) > limit:
        out.append(f"  …и ещё {len(rows) - 25} (полный список: --all)")
    return out


def private_state():
    """True — приватный, False — публичный, None — проверить не удалось (текст — почему)."""
    remote = sh("git", "remote", "get-url", "origin", cwd=REPO).stdout.strip()
    if not remote:
        return None, "у клона нет remote origin — пуша в облако не будет"
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", remote)
    if not m:
        return None, "remote не на GitHub — приватность проверь сам"
    if not shutil.which("gh"):
        return None, "не установлен gh — приватность не проверил"
    r = sh("gh", "repo", "view", m.group(1), "--json", "isPrivate", "-q", ".isPrivate")
    if r.returncode:
        return None, "gh не смог посмотреть репозиторий (войди: gh auth login)"
    return r.stdout.strip() == "true", m.group(1)


def _public_stop(slug):
    print(f"СТОП: репозиторий {slug} ПУБЛИЧНЫЙ. В бэкапе ваши скиллы, команды и память — отправлять их в открытый репозиторий нельзя.\n"
          f"Сделайте приватным: gh repo edit {slug} --visibility private --accept-visibility-change-consequences\n"
          "и запустите бэкап снова. Ничего не записано.")
    sys.exit(4)


def main():
    apply = "--apply" in sys.argv
    if not (REPO / ".git").exists():
        sys.exit(f"Нет клона бэкап-репозитория {REPO}. Создай приватный и склонируй:\n"
                 f"  gh repo create ai-backup --private --clone   (в папке {REPO.parent})\n"
                 "Подробно — INSTALL.md скилла.")
    priv, info = private_state()
    if priv is False:
        _public_stop(info)
    if priv is None:
        print(f"!! Приватность не подтверждена: {info}")
    targets = active_targets()
    if not targets:
        sys.exit("Нет ни одной цели: не нашёл ~/.claude, ~/.codex и своих папок из custom_targets. Проверь config.json.")
    print(f"== {'БЭКАП' if apply else 'СУХОЙ ПРОГОН (ничего не пишу; для записи --apply)'}")
    print("   цели: " + ", ".join(f"{t['name']} ({t['home']})" for t in targets))
    changes = snapshot(apply)
    total = sum(len(v) for v in changes.values())
    print(f"\n1. Снимок настроек: изменений {total}")
    for k, v in changes.items():
        print(f"  {k}: {len(v)}")
    for p in REPO.glob("*-home/**/*"):
        if p.is_file() and p.stat().st_size > 5_000_000:
            print(f"  ! файл больше 5 МБ: {p.relative_to(REPO)}")
    print("\n2. Репозитории, где что-то не в облаке (пропадёт, если Mac умрёт):")
    print("\n".join(repo_status()) or "  всё отправлено")
    if not apply:
        return 0
    if changes and (REPO / "README.md").exists():
        txt = (REPO / "README.md").read_text()
        (REPO / "README.md").write_text(re.sub(r"\*\*Дата снимка:\*\* [0-9-]+", f"**Дата снимка:** {date.today()}", txt))
    paths = sorted(p.name for p in REPO.glob("*-home") if p.is_dir()) + [f for f in ("backup-manifest.json", "README.md") if (REPO / f).exists()]
    sh("git", "add", "-A", "--", *paths, cwd=REPO)
    if not sh("git", "diff", "--cached", "--name-only", cwd=REPO).stdout.strip():
        print("\nНечего сохранять: снимок совпадает с прошлым.")
        return 3
    print("\n3. Скан на секреты (добавленные строки):", flush=True)
    return subprocess.run([sys.executable, str(SCAN), "--staged"], cwd=REPO).returncode


if __name__ == "__main__":
    sys.exit(main())
