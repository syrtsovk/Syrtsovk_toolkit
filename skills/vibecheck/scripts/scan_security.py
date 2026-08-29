#!/usr/bin/env python3
"""vibecheck: сканер секретов и типовых дыр безопасности.

Чистый python3 без зависимостей. Читает проект, ничего не меняет.
Найденные секреты маскируются — целиком в отчёт не попадают никогда.

Запуск:
    python3 scan_security.py /путь/к/проекту
    python3 scan_security.py . --json          # машинный вывод для скилла
    python3 scan_security.py . --report out.md # markdown-отчёт
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", "vendor", "target", ".idea", ".vscode",
    "coverage", ".turbo", ".cache", "site-packages", ".mypy_cache", ".tox",
    ".claude", ".cursor",
}
TEXT_EXT = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".rb", ".php", ".go",
    ".java", ".kt", ".cs", ".rs", ".swift", ".sh", ".bash", ".zsh", ".sql",
    ".env", ".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".conf",
    ".vue", ".svelte", ".astro", ".tf", ".tfvars", ".properties", ".xml",
}
MAX_FILE_BYTES = 1_500_000

# Файлы, где строка, похожая на ключ, почти всегда пример или лок-файл.
EXAMPLE_FILE = re.compile(
    r"(\.example|\.sample|\.template|\.dist|\.test\.|_test\.|test_|\.spec\.|"
    r"\.lock$|lock\.json$|\.md$|\.snap$|fixtures?/|mocks?/|__tests__/)"
)
CLIENT_DIR = re.compile(r"(^|/)(src|app|pages|components|public|client|frontend|www)(/|$)")
SERVER_HINT = re.compile(r"(^|/)(api|server|backend|routes?|handlers?|functions?|lambda|worker)s?(/|$)")

# ─────────────────────────── секреты ───────────────────────────
# (id, severity, человеческое имя, regex)
SECRETS = [
    ("anthropic_key", "critical", "ключ Anthropic", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("openrouter_key", "critical", "ключ OpenRouter", re.compile(r"\bsk-or-v1-[A-Za-z0-9]{32,}")),
    ("openai_key", "critical", "ключ OpenAI", re.compile(r"\bsk-(?!ant-|or-)[A-Za-z0-9_-]{20,}")),
    ("stripe_live", "critical", "боевой ключ Stripe", re.compile(r"\b[sr]k_live_[A-Za-z0-9]{20,}")),
    ("aws_key", "critical", "ключ доступа AWS", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github_token", "critical", "токен GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}")),
    ("slack_token", "critical", "токен Slack", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("telegram_bot", "critical", "токен Telegram-бота", re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_-]{32,}")),
    ("google_api", "critical", "ключ Google API", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("sendgrid", "critical", "ключ SendGrid", re.compile(r"\bSG\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}")),
    ("twilio", "critical", "SID аккаунта Twilio", re.compile(r"\bAC[0-9a-f]{32}\b")),
    ("supabase_service", "critical", "сервисный ключ Supabase (service_role)",
     re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]*c2VydmljZV9yb2xl[A-Za-z0-9_-]*\.[A-Za-z0-9_-]{10,}")),
    ("private_key", "critical", "приватный ключ (PEM)",
     re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("db_url_pass", "critical", "строка подключения к базе с паролем",
     re.compile(r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://[^\s:@/\"']{2,}:[^\s:@/\"']{4,}@")),
    ("generic_secret", "high", "похоже на захардкоженный секрет",
     re.compile(r"""(?i)\b(api[_-]?key|apikey|secret|password|passwd|token|access[_-]?key)\b\s*[:=]\s*["'][^"'\s${}]{16,}["']""")),
]

# Для этих правил строка в комментарии — почти всегда пример из документации,
# а не утечка. Настоящий ключ остаётся утечкой даже закомментированным.
SKIP_IN_COMMENT = {"generic_secret", "db_url_pass"}

# Признак того, что данные почистили перед вставкой в разметку.
SANITIZED = re.compile(r"(?i)(sanitiz|dompurify|purify|escapeHtml|clean_?html|bleach|xss|"
                       r"\\\\u003c|replace\(\s*/</|encodeURI|htmlspecialchars)")

# Локальные и контейнерные адреса в строке подключения — это среда разработки,
# а не боевой пароль: postgres://user:pass@localhost.
LOCAL_HOST = re.compile(r"(?i)@(localhost|127\.0\.0\.1|0\.0\.0\.0|host\.docker\.internal|db|database|"
                        r"postgres|mysql|mongo|redis)[:/]")
CI_PATH = re.compile(r"(?i)(^|/)(\.github|\.gitlab|\.circleci|ci|\.devcontainer)/")

# Значения-пустышки, на которые не стоит ругаться.
PLACEHOLDER = re.compile(
    r"(?i)(your[_-]?|my[_-]?|example|placeholder|changeme|xxx+|\.\.\.|<[^>]+>|\$\{|process\.env|os\.environ|"
    r"dummy|fake|sample|test[_-]?key|insert[_-]?here|todo)"
)

# ─────────────────────── дыры в конфигурации и коде ───────────────────────
# (id, severity, заголовок, regex, почему это дыра, как чинить, применимые расширения)
CODE_RULES = [
    ("cors_star", "high", "CORS открыт для всех доменов",
     re.compile(r"""(?i)(Access-Control-Allow-Origin["'\s:,=>]+\*|origin\s*:\s*["']\*["']|CORS_ORIGINS?\s*=\s*["']?\*)"""),
     "Любой сайт может слать запросы к вашему API от имени залогиненного пользователя и читать ответы. "
     "Вместе с куками это даёт чужой странице доступ к данным ваших клиентов.",
     "Перечислите свои домены явным списком вместо звёздочки.",
     None),
    ("debug_prod", "high", "Отладочный режим включён в коде",
     re.compile(r"(?i)(DEBUG\s*=\s*True|debug\s*:\s*true|app\.run\([^)]*debug\s*=\s*True|FLASK_DEBUG\s*=\s*1)"),
     "В отладочном режиме сервер показывает трассировку ошибки с кусками вашего кода, путями на диске и "
     "переменными окружения. У Flask и Django это ещё и интерактивная консоль — то есть чужое выполнение кода.",
     "Читайте флаг из переменной окружения и держите его выключенным по умолчанию.",
     None),
    ("eval_use", "high", "eval / exec на данных",
     re.compile(r"""(?<![\w.'"])(eval|exec)\s*\(\s*(?!["'])"""),
     "Если в eval попадёт хоть что-то от пользователя — он выполнит свой код на вашем сервере. "
     "Это полный захват процесса: чтение файлов, кража переменных окружения, исходящие запросы.",
     "Замените на разбор конкретного формата: json.loads, ast.literal_eval, явный маппинг допустимых значений.",
     {".py", ".js", ".jsx", ".ts", ".tsx"}),
    ("sql_fstring", "critical", "SQL собирается f-строкой или склейкой",
     re.compile(r"""(?i)(execute|executemany|query|raw|\$queryRawUnsafe)\s*\(\s*(f["']|["'][^"'\n]{0,200}["']\s*[+%]\s*\w)"""),
     "Пользователь может дописать в поле ввода свой кусок SQL и прочитать всю базу целиком — включая таблицу "
     "пользователей с почтами и хешами паролей. Это самый частый способ увода базы.",
     "Передавайте значения параметрами: execute('... WHERE id = %s', (user_id,)). Строку запроса не склеивайте.",
     None),
    ("sql_template", "medium", "В шаблон SQL подставляется выражение",
     re.compile(r"""(?is)(query|execute|raw|\$queryRawUnsafe)\s*\(\s*`[^`]{0,400}?\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE)\b[^`]{0,400}?\$\{"""),
     "Если внутрь подстановки попадёт значение от пользователя, он допишет свой запрос и прочитает чужие данные. "
     "Когда подставляется имя таблицы или готовый фрагмент из константы — это безопасно, но отличить одно от другого "
     "может только человек.",
     "Посмотрите, что именно подставляется. Значения передавайте параметрами ($1, $2), а через подстановку "
     "пропускайте только имена из своего заранее заданного списка.",
     None),
    ("jwt_none", "critical", "JWT принимается без проверки подписи",
     re.compile(r"""(?i)(["']alg["']\s*:\s*["']none["']|verify\s*[=:]\s*False|verify_signature["']?\s*[:=]\s*False|algorithms\s*=\s*\[\s*["']none["'])"""),
     "Токен без проверки подписи можно подделать вручную: подставить чужой id или роль администратора. "
     "Атакующий заходит под любым пользователем, ничего не взламывая.",
     "Проверяйте подпись всегда и задавайте список разрешённых алгоритмов явно.",
     None),
    ("jwt_no_expiry", "medium", "JWT выдаётся без срока жизни",
     re.compile(r"""(?i)(jwt\.sign\((?![^)]*expiresIn)[^)]{0,200}\)|jwt\.encode\((?![^)]*"exp")[^)]{0,200}\))"""),
     "Токен без срока действует вечно. Один раз утёк из логов, истории браузера или чужого ноутбука — "
     "и доступ у чужого человека остаётся навсегда, отозвать нечем.",
     "Ставьте срок жизни (expiresIn / exp) и делайте отдельный refresh-токен.",
     None),
    ("tls_off", "high", "Проверка TLS-сертификата отключена",
     re.compile(r"(?i)(verify\s*=\s*False|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0|InsecureSkipVerify\s*:\s*true)"),
     "Отключённая проверка сертификата означает, что любой в сети между вами и сервисом может встать посередине, "
     "прочитать и подменить трафик — вместе с ключами и данными клиентов, которые в нём едут.",
     "Верните проверку. Если мешает самоподписанный сертификат — добавьте именно его в доверенные, а не выключайте проверку целиком.",
     None),
    ("weak_hash_password", "high", "Пароли хешируются слабым алгоритмом",
     re.compile(r"(?i)(md5|sha1)\s*\(\s*[^)]{0,60}(password|passwd|pwd)"),
     "MD5 и SHA1 перебираются на видеокарте миллиардами вариантов в секунду. Если база утечёт, "
     "пароли ваших пользователей восстановят за часы — а люди используют их и на других сайтах.",
     "Используйте bcrypt, argon2 или scrypt — они специально сделаны медленными.",
     None),
    ("shell_injection", "critical", "Команда оболочки собирается из переменных",
     re.compile(r"""(?i)(os\.system\s*\(\s*f?["'][^"']*[+{]|subprocess\.[a-z]+\([^)]*shell\s*=\s*True|child_process\.exec\(\s*[`"'][^`"']*\$\{)"""),
     "Пользователь может дописать в строку свою команду через точку с запятой и выполнить что угодно от имени "
     "вашего процесса — скачать базу, прочитать .env, открыть себе доступ.",
     "Передавайте аргументы списком без shell=True: subprocess.run(['git', 'log', ref]).",
     None),
    ("pickle_load", "high", "Небезопасная десериализация",
     re.compile(r"(?i)(pickle\.loads?|yaml\.load\s*\((?![^)]*SafeLoader)|marshal\.loads)\s*\("),
     "Такой формат при чтении может запускать код. Если данные пришли снаружи — это выполнение чужого кода у вас.",
     "Для данных извне используйте json, а для YAML — yaml.safe_load.",
     None),
    ("path_traversal", "high", "Путь к файлу собирается из пользовательских данных",
     re.compile(r"""(?i)(open|readFile|readFileSync|sendFile|createReadStream)\s*\(\s*[^)]{0,40}(req\.(query|params|body)|request\.(args|form|json)|params\[)"""),
     "Подставив в имя файла ../../ пользователь выйдет за пределы папки и прочитает системные файлы или ваш .env с ключами.",
     "Сверяйте запрошенное имя со списком разрешённых или приводите путь к абсолютному и проверяйте, что он внутри нужной папки.",
     None),
    ("secret_in_log", "medium", "Секрет попадает в логи",
     re.compile(r"""(?i)(console\.log|print|logger?\.(info|debug|warn|error))\s*\([^)]{0,80}\b(token|password|passwd|secret|api[_-]?key|authorization)\b"""),
     "Логи читают шире, чем код: они уходят в облачные сервисы, попадают в скриншоты и остаются в истории. "
     "Ключ, попавший в лог, считается утёкшим.",
     "Логируйте факт события без значения, либо маскируйте: token[:4] + '…'.",
     None),
    ("role_from_client", "high", "Роль или права приходят с клиента",
     re.compile(r"""(?i)(req\.body\.(role|is_?admin|isAdmin|permissions?)|request\.(json|form)\[["'](role|is_?admin)|body\.role\b)"""),
     "Клиент может отправить в запросе что угодно, включая role: admin. Если сервер этому верит, "
     "любой пользователь делает себя администратором одной правкой запроса.",
     "Берите роль из базы по идентификатору сессии, а поле роли из тела запроса игнорируйте.",
     None),
    ("idor_suspect", "medium", "Объект берётся по id из запроса без проверки владельца",
     re.compile(r"""(?i)(findById|findOne|get_object_or_404|findUnique)\s*\(\s*[^)]{0,60}(req\.params|req\.query|request\.args|params\[)"""),
     "Если рядом нет проверки, что объект принадлежит текущему пользователю, достаточно поменять цифру в адресе — "
     "и человек читает чужой заказ, чужую переписку, чужие документы.",
     "После загрузки объекта сверяйте его владельца с текущим пользователем и отдавайте 404 при несовпадении.",
     None),
    ("xss_html", "high", "Пользовательские данные вставляются как разметка",
     re.compile(r"""(?i)(dangerouslySetInnerHTML|\.innerHTML\s*=|v-html\s*=|\.html\s*\(\s*[^)'"]|"""
                r"""insertAdjacentHTML|document\.write\s*\()"""),
     "Браузер выполнит то, что вставили. Если в эти данные попадёт чужой текст с кодом, он запустится у каждого "
     "посетителя страницы: утекут сессионные куки, а с ними и вход в аккаунт.",
     "Выводите текст обычной вставкой (children в React, textContent в JS). Когда разметка действительно нужна, "
     "прогоняйте её через очистку — DOMPurify или аналог.",
     {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}),
    ("prisma_unsafe", "high", "Небезопасный вызов запроса в Prisma",
     re.compile(r"\$(?:query|execute)RawUnsafe\s*\("),
     "Методы с Unsafe в названии не экранируют подставленное значение — это прямая дорога к тому, что пользователь "
     "допишет свой запрос и прочитает чужие данные.",
     "Замените на $queryRaw с тегированным шаблоном — там значения уходят параметрами.",
     None),
    ("swallowed_error", "medium", "Ошибка перехватывается и молча теряется",
     re.compile(r"(?m)(except[^:\n]*:\s*\n\s*pass\s*$|catch\s*\([^)]*\)\s*\{\s*\}|\.catch\s*\(\s*\(\s*\)\s*=>\s*\{\s*\}\s*\))"),
     "Пустой перехват означает, что упавшая проверка выглядит как успешная. Если так обёрнута проверка прав или "
     "платёж, отказ превращается в разрешение, и в журнале не остаётся следа.",
     "Запишите ошибку в журнал и верните отказ. Молча продолжать можно только там, где сбой действительно ничего не значит.",
     None),
    ("upload_unbounded", "medium", "Загрузка файлов без ограничений",
     re.compile(r"(?i)(multer\s*\(\s*\{\s*(?![^}]*limits)|upload\.(single|array|any)\(|request\.files\[)"),
     "Без лимита размера и списка разрешённых типов диск забивают одним запросом, а исполняемый файл, "
     "положенный в публичную папку, может быть запущен через веб.",
     "Задайте максимальный размер, белый список типов и храните загруженное вне публичной папки.",
     None),
]

# ─────────────────────── проверки по конкретным файлам ───────────────────────
PUBLIC_ENV_PREFIX = re.compile(r"\b(NEXT_PUBLIC_|VITE_|REACT_APP_|PUBLIC_|EXPO_PUBLIC_|GATSBY_)[A-Z0-9_]*"
                               r"(KEY|SECRET|TOKEN|PASSWORD|PRIVATE|CREDENTIAL)")
PAID_API_FROM_CLIENT = re.compile(r"https?://api\.(openai|anthropic|stripe|openrouter)\.(com|ai)")
LLM_CALL = re.compile(r"(?i)(openai|anthropic|\.chat\.completions|messages\.create|generateContent|openrouter)")
ROUTE_DEF = re.compile(r"(?i)(app\.(post|get|put|patch|delete)|router\.(post|get|put|patch|delete)|"
                       r"@(app|router)\.(post|get)|export (async )?function (POST|GET)|def \w+\(request)")
AUTH_HINT = re.compile(r"(?i)(auth|verifyToken|requireUser|getSession|getServerSession|middleware|authorize|"
                       r"jwt|current_user|login_required|Depends\()")
SENSITIVE_ROUTE = re.compile(r"""(?i)["'`/](login|signin|sign-in|signup|sign-up|register|reset-password|"""
                             r"""forgot|verify|otp|token)["'`/]""")
RATE_LIMIT_LIB = ("express-rate-limit", "ratelimit", "rate_limit", "slowapi", "@upstash/ratelimit",
                  "limiter", "throttle", "flask-limiter", "django-ratelimit", "bottleneck")


def mask(value: str) -> str:
    value = value.strip()
    if len(value) <= 10:
        return "…"
    return f"{value[:5]}…{value[-3:]}"


def line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def is_commented(text: str, pos: int) -> bool:
    start = text.rfind("\n", 0, pos) + 1
    prefix = text[start:pos].lstrip()
    return prefix.startswith(("#", "//", "*", "/*", "<!--"))


def is_pattern_declaration(text: str, pos: int) -> bool:
    """Строка объявляет регулярное выражение — совпало определение правила, а не код.

    Так устроены линтеры, тесты и сам этот сканер: слово из паттерна лежит
    в объявлении, а не в рабочем вызове.
    """
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


def iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_EXT and path.name not in {".env", "Dockerfile", "docker-compose.yml"}:
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            yield path, path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue


def add(findings, *, id, severity, title, where, what, why, fix):
    findings.append({
        "id": id, "severity": severity, "title": title,
        "where": where, "what": what, "why": why, "fix": fix,
        "area": "security",
    })


def git_tracked(root: Path) -> set[str]:
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files"],
                             capture_output=True, text=True, timeout=20)
        return set(out.stdout.splitlines()) if out.returncode == 0 else set()
    except (OSError, subprocess.SubprocessError):
        return set()


def check_secrets(root: Path, findings: list) -> None:
    for path, text in iter_files(root):
        rel = str(path.relative_to(root))
        if EXAMPLE_FILE.search(rel):
            continue
        for sid, severity, name, pattern in SECRETS:
            for m in pattern.finditer(text):
                value = m.group(0)
                if PLACEHOLDER.search(value):
                    continue
                if sid in SKIP_IN_COMMENT and is_commented(text, m.start()):
                    continue
                if sid == "db_url_pass" and (LOCAL_HOST.search(value) or CI_PATH.search(rel)):
                    continue
                add(findings,
                    id=sid, severity=severity,
                    title=f"В коде лежит {name}",
                    where=f"{rel}:{line_no(text, m.start())}",
                    what=f"Найдено значение вида `{mask(value)}` прямо в файле.",
                    why="Ключ в коде утекает вместе с репозиторием: его видят все, у кого есть доступ, он остаётся "
                        "в истории git навсегда, и боты круглосуточно сканируют публичные репозитории именно на такие "
                        "строки. Чужой человек получит доступ к сервису и потратит ваши деньги от вашего имени.",
                    fix="1) Перевыпустите ключ в консоли сервиса прямо сейчас — если он был в git, считайте его "
                        "скомпрометированным. 2) Вынесите значение в переменную окружения. 3) Убедитесь, что .env "
                        "в .gitignore. 4) Историю можно почистить git filter-repo, но перевыпуск обязателен в любом случае.")
                break  # одна находка на файл и тип — не спамим


def check_env_and_git(root: Path, findings: list) -> None:
    tracked = git_tracked(root)
    for name in tracked:
        base = Path(name).name
        if base == ".env" or (base.startswith(".env.") and not EXAMPLE_FILE.search(base)):
            add(findings,
                id="env_in_git", severity="critical",
                title=".env лежит в git",
                where=name,
                what="Файл с переменными окружения отслеживается системой контроля версий.",
                why="Всё, что попало в историю git, остаётся там навсегда и уезжает вместе с каждой копией "
                    "репозитория. Даже если файл удалить сейчас, старые коммиты сохранят все ключи.",
                fix="Уберите файл из отслеживания: git rm --cached .env, добавьте .env в .gitignore, "
                    "перевыпустите все ключи, которые в нём были.")

    gitignore = root / ".gitignore"
    if (root / ".git").exists():
        content = gitignore.read_text(encoding="utf-8", errors="ignore") if gitignore.exists() else ""
        if ".env" not in content:
            add(findings,
                id="env_not_ignored", severity="high",
                title=".env не защищён от коммита",
                where=".gitignore",
                what="В .gitignore нет строки .env — файл с ключами может уехать в репозиторий случайно.",
                why="Достаточно одного git add . в спешке, чтобы ключи оказались в истории. "
                    "Это самый частый способ утечки в небольших проектах.",
                fix="Добавьте в .gitignore строки: .env и .env.*.local")


def check_client_exposure(root: Path, findings: list) -> None:
    for path, text in iter_files(root):
        rel = str(path.relative_to(root))
        if EXAMPLE_FILE.search(rel):
            continue
        m = PUBLIC_ENV_PREFIX.search(text)
        if m:
            add(findings,
                id="public_env_secret", severity="critical",
                title="Секрет положен в публичную переменную окружения",
                where=f"{rel}:{line_no(text, m.start())}",
                what=f"Переменная `{m.group(0)}` с публичным префиксом содержит слово ключ/секрет/токен.",
                why="Префиксы NEXT_PUBLIC_, VITE_, REACT_APP_ означают «положить значение прямо в файлы, которые "
                    "скачивает браузер». Ключ будет виден любому через инструменты разработчика за десять секунд.",
                fix="Уберите публичный префикс и обращайтесь к платному сервису только с сервера — "
                    "через свой эндпоинт, который проверяет пользователя.")
        if CLIENT_DIR.search(rel) and not SERVER_HINT.search(rel):
            mm = PAID_API_FROM_CLIENT.search(text)
            if mm:
                add(findings,
                    id="paid_api_from_client", severity="critical",
                    title="Платный API вызывается прямо из браузера",
                    where=f"{rel}:{line_no(text, mm.start())}",
                    what=f"Обращение к {mm.group(0)} находится в клиентской части приложения.",
                    why="Чтобы браузер сделал такой запрос, ключ должен попасть в код страницы. Значит, его видно "
                        "в исходниках вкладки. Дальше по вашему ключу генерируют что угодно, а счёт приходит вам.",
                    fix="Перенесите вызов на сервер: браузер зовёт ваш эндпоинт, эндпоинт проверяет пользователя "
                        "и уже сам ходит в платный сервис своим ключом.")


def check_code_rules(root: Path, findings: list) -> None:
    for path, text in iter_files(root):
        rel = str(path.relative_to(root))
        if EXAMPLE_FILE.search(rel):
            continue
        for rid, severity, title, pattern, why, fix, exts in CODE_RULES:
            if exts and path.suffix.lower() not in exts:
                continue
            for m in pattern.finditer(text):
                if is_commented(text, m.start()) or is_pattern_declaration(text, m.start()):
                    continue
                if rid == "xss_html" and SANITIZED.search(text[max(0, m.start() - 500): m.end() + 200]):
                    continue        # данные прогнали через очистку — вставка безопасна
                snippet = m.group(0).strip().replace("\n", " ")[:70]
                add(findings,
                    id=rid, severity=severity, title=title,
                    where=f"{rel}:{line_no(text, m.start())}",
                    what=f"Сработало на `{snippet}`.",
                    why=why, fix=fix)
                break


def check_auth_and_cost(root: Path, findings: list) -> None:
    files: dict[str, str] = {}
    for path, text in iter_files(root):
        if path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".py", ".go", ".rb"}:
            files[str(path.relative_to(root))] = text
    if not files:
        return
    corpus = "\n".join(files.values()).lower()
    has_rate_limit = any(lib in corpus for lib in RATE_LIMIT_LIB)

    for rel, text in files.items():
        if EXAMPLE_FILE.search(rel):
            continue
        m = SENSITIVE_ROUTE.search(text)
        if m and ROUTE_DEF.search(text) and not has_rate_limit:
            add(findings,
                id="no_rate_limit", severity="high",
                title="Вход и регистрация без ограничения частоты запросов",
                where=f"{rel}:{line_no(text, m.start())}",
                what="В проекте не найдено ни одной библиотеки ограничения частоты, а роут входа есть.",
                why="Без лимита пароль подбирают перебором миллионами попыток, а форму восстановления используют "
                    "для рассылки спама с вашего домена — за ваш счёт и с ударом по репутации отправителя.",
                fix="Подключите ограничитель: express-rate-limit, slowapi, flask-limiter или @upstash/ratelimit. "
                    "Порог на вход — порядка 5 попыток в минуту на адрес.")
            break

    for rel, text in files.items():
        if EXAMPLE_FILE.search(rel) or not LLM_CALL.search(text):
            continue
        m = LLM_CALL.search(text)
        if is_pattern_declaration(text, m.start()):
            continue
        window = text[max(0, m.start() - 400): m.end() + 400].lower()
        if "max_tokens" not in window and "maxtokens" not in window and "max_output" not in window:
            add(findings,
                id="llm_no_limit", severity="medium",
                title="Обращение к платной модели без лимита длины ответа",
                where=f"{rel}:{line_no(text, m.start())}",
                what="Рядом с вызовом нет max_tokens или аналога.",
                why="Длину ответа задаёт модель, а платите вы. Одна кривая подсказка от пользователя — и один "
                    "запрос стоит как тысяча обычных.",
                fix="Задайте max_tokens, ограничьте длину входного текста и поставьте потолок трат в консоли сервиса.")
        if ROUTE_DEF.search(text) and not AUTH_HINT.search(text):
            add(findings,
                id="llm_open_endpoint", severity="critical",
                title="Эндпоинт с платной моделью открыт без проверки пользователя",
                where=rel,
                what="Файл одновременно объявляет маршрут и зовёт платную модель, проверки авторизации не видно.",
                why="Такой адрес находят автоматическим перебором за часы. Дальше ваш ключ используют как бесплатный "
                    "прокси к модели: счёт растёт, лимиты выбираются, сервис отключают за нарушение правил.",
                fix="Закройте маршрут проверкой сессии и ограничением числа запросов на пользователя, "
                    "а не только общим лимитом.")
        break


def check_infra_configs(root: Path, findings: list) -> None:
    for path, text in iter_files(root):
        rel = str(path.relative_to(root))
        name = path.name.lower()

        if name.startswith("docker-compose"):
            m = re.search(r"(?i)(POSTGRES_PASSWORD|MYSQL_ROOT_PASSWORD|MONGO_INITDB_ROOT_PASSWORD)\s*:\s*"
                          r"(postgres|mysql|root|admin|password|123456|test)\b", text)
            if m:
                add(findings,
                    id="default_db_password", severity="critical",
                    title="У базы данных пароль по умолчанию",
                    where=f"{rel}:{line_no(text, m.start())}",
                    what=f"Найдено `{m.group(0).strip()}`.",
                    why="Такие пары логин-пароль перебираются первыми же строчками любого автоматического сканера. "
                        "Если порт базы виден снаружи — базу выкачают и оставят записку с требованием выкупа.",
                    fix="Сгенерируйте длинный пароль, положите его в переменную окружения и подставляйте оттуда.")
            m = re.search(r"(?m)^\s*-\s*[\"']?(?:0\.0\.0\.0:)?(5432|3306|27017|6379|9200):\1", text)
            if m:
                add(findings,
                    id="db_port_exposed", severity="high",
                    title="Порт базы данных проброшен наружу",
                    where=f"{rel}:{line_no(text, m.start())}",
                    what=f"Проброс `{m.group(0).strip()}` открывает базу на внешнем адресе машины.",
                    why="База становится доступна из интернета напрямую, минуя приложение. Сканеры находят открытые "
                        "порты за считаные часы после запуска.",
                    fix="Уберите проброс наружу — контейнеры общаются между собой по внутренней сети. "
                        "Если доступ нужен вам лично, привяжите порт к 127.0.0.1 и ходите через SSH-туннель.")

        if name in {"firebase.rules", "firestore.rules", "storage.rules"} or "rules" in name and path.suffix == ".rules":
            m = re.search(r"(?i)allow\s+(read|write|read,\s*write)\s*:\s*if\s+true", text)
            if m:
                add(findings,
                    id="firebase_open", severity="critical",
                    title="База Firebase открыта на чтение и запись всем",
                    where=f"{rel}:{line_no(text, m.start())}",
                    what="Правило разрешает операции без каких-либо условий.",
                    why="Любой человек, открывший ваш сайт, видит адрес базы в коде страницы и может прочитать "
                        "или стереть все данные напрямую, минуя приложение.",
                    fix="Опишите правила: доступ только авторизованному пользователю и только к своим документам.")

        if name == "dockerfile":
            m = re.search(r"(?im)^\s*(ENV|ARG)\s+\w*(KEY|SECRET|TOKEN|PASSWORD)\w*\s*=?\s*\S{8,}", text)
            if m:
                add(findings,
                    id="secret_in_dockerfile", severity="high",
                    title="Секрет зашит в образ контейнера",
                    where=f"{rel}:{line_no(text, m.start())}",
                    what="Переменная с ключом задана прямо в Dockerfile.",
                    why="Значение остаётся в слоях образа. Любой, кто скачает образ, достанет его командой "
                        "docker history — даже если в финальном контейнере переменной уже нет.",
                    fix="Передавайте секреты при запуске контейнера через переменные окружения или secret-механизм сборки.")


def check_dependencies(root: Path, findings: list) -> None:
    if (root / "package.json").exists() and (root / "package-lock.json").exists():
        try:
            out = subprocess.run(["npm", "audit", "--json", "--audit-level=high"],
                                 cwd=root, capture_output=True, text=True, timeout=120)
            data = json.loads(out.stdout or "{}")
            vulns = data.get("metadata", {}).get("vulnerabilities", {})
            crit, high = vulns.get("critical", 0), vulns.get("high", 0)
            if crit or high:
                add(findings,
                    id="vulnerable_deps", severity="critical" if crit else "high",
                    title=f"Уязвимые зависимости: {crit} критичных, {high} высоких",
                    where="package.json",
                    what="Отчёт npm audit нашёл известные уязвимости в установленных пакетах.",
                    why="Это опубликованные дыры с готовыми примерами атаки. Их проверяют автоматически по версиям "
                        "из вашего lock-файла — искать вручную никому не нужно.",
                    fix="Запустите npm audit fix. Если не помогает — npm audit покажет, какие пакеты обновить вручную.")
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError, ValueError):
            add(findings,
                id="deps_not_checked", severity="low",
                title="Зависимости на уязвимости не проверены",
                where="package.json",
                what="Не удалось запустить npm audit (нет npm, нет сети или другая ошибка).",
                why="Известные дыры в чужих пакетах — самый дешёвый способ попасть в ваш проект, и проверка занимает минуту.",
                fix="Запустите вручную: npm audit")
    if (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
        add(findings,
            id="pip_audit_hint", severity="low",
            title="Python-зависимости стоит проверить на уязвимости",
            where="requirements.txt" if (root / "requirements.txt").exists() else "pyproject.toml",
            what="Автоматическая проверка для python в этот сканер не встроена.",
            why="В библиотеках регулярно находят дыры, и обновление обычно занимает одну команду.",
            fix="Установите и запустите: pip install pip-audit && pip-audit")


SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEV_LABEL = {"critical": "КРИТИЧНО", "high": "ВЫСОКИЙ", "medium": "СРЕДНИЙ", "low": "НИЗКИЙ"}


def build_markdown(findings: list, root: Path) -> str:
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEV_ORDER}
    lines = [
        "# Отчёт vibecheck — безопасность",
        "",
        f"Проект: `{root}`",
        f"**Найдено {len(findings)}: критичных {counts['critical']}, высоких {counts['high']}, "
        f"средних {counts['medium']}, низких {counts['low']}**",
        "",
    ]
    if not findings:
        lines.append("Сканер типовых дыр не нашёл. Это не гарантия безопасности — "
                     "логику авторизации и настройки в облачных консолях он не проверяет.")
        return "\n".join(lines)
    for finding in sorted(findings, key=lambda f: SEV_ORDER[f["severity"]]):
        lines += [
            f"## [{SEV_LABEL[finding['severity']]}] {finding['title']}",
            "",
            f"**Где:** `{finding['where']}`",
            "",
            f"**Что нашли:** {finding['what']}",
            "",
            f"**Почему это опасно:** {finding['why']}",
            "",
            f"**Как исправить:** {finding['fix']}",
            "",
        ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="vibecheck — сканер секретов и дыр безопасности")
    parser.add_argument("path", nargs="?", default=".", help="папка проекта")
    parser.add_argument("--json", action="store_true", help="вывести находки в JSON")
    parser.add_argument("--report", metavar="FILE", help="записать markdown-отчёт в файл")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Не папка: {root}", file=sys.stderr)
        return 1

    findings: list = []
    for check in (check_secrets, check_env_and_git, check_client_exposure,
                  check_code_rules, check_auth_and_cost, check_infra_configs, check_dependencies):
        try:
            check(root, findings)
        except Exception as exc:  # одна упавшая проверка не роняет весь скан
            print(f"[warn] проверка {check.__name__} прервалась: {exc}", file=sys.stderr)

    findings.sort(key=lambda f: SEV_ORDER[f["severity"]])

    if args.json:
        json.dump(findings, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return 0

    if args.report:
        Path(args.report).write_text(build_markdown(findings, root), encoding="utf-8")

    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEV_ORDER}
    print(f"vibecheck / безопасность: {len(findings)} находок "
          f"(критичных {counts['critical']}, высоких {counts['high']}, "
          f"средних {counts['medium']}, низких {counts['low']})")
    for finding in findings[:5]:
        print(f"  [{SEV_LABEL[finding['severity']]}] {finding['title']} — {finding['where']}")
    if args.report:
        print(f"Отчёт: {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
