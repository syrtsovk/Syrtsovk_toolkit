#!/usr/bin/env python3
"""vibecheck: не дать записать ключ в файл проекта.

Срабатывает перед записью (Write / Edit) и останавливает её, если в тексте
видно настоящий ключ от платного сервиса или приватный ключ. Отчёт находит
утечку после того, как она случилась; этот крючок не даёт ей случиться.

Работает только на явных форматах ключей — то, что ни с чем не спутать.
Подозрительные строки вроде `password = "..."` пропускаются: блокировать
работу из-за догадки нельзя.

Выход 2 останавливает запись и показывает причину.
"""

from __future__ import annotations

import json
import re
import sys

# Только однозначные форматы. Каждая строка — это ключ, а не похожая на ключ.
HARD_SECRETS = [
    ("ключ Anthropic", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("ключ OpenRouter", re.compile(r"\bsk-or-v1-[A-Za-z0-9]{32,}")),
    ("ключ OpenAI", re.compile(r"\bsk-(?!ant-|or-)[A-Za-z0-9_-]{32,}")),
    ("боевой ключ Stripe", re.compile(r"\b[sr]k_live_[A-Za-z0-9]{20,}")),
    ("ключ доступа AWS", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("токен GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}")),
    ("токен Slack", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("токен Telegram-бота", re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_-]{32,}")),
    ("ключ Google API", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("ключ SendGrid", re.compile(r"\bSG\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}")),
    ("приватный ключ (PEM)", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
]

# Значения-пустышки из примеров и документации.
PLACEHOLDER = re.compile(r"(?i)(your[_-]?|example|placeholder|changeme|xxxx|dummy|fake|<[^>]+>)")

# Файлы, куда ключам класть можно и нужно.
ALLOWED_FILES = re.compile(r"(?i)(^|/)\.env(\.[a-z]+)?$|\.example$|\.sample$|\.template$")


def mask(value: str) -> str:
    return f"{value[:5]}…{value[-3:]}" if len(value) > 10 else "…"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0        # не разобрали — пропускаем, ломать работу нельзя

    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or ""
    content = " ".join(str(tool_input.get(field) or "")
                       for field in ("content", "new_string", "new_str"))
    if not content or ALLOWED_FILES.search(path):
        return 0

    for name, pattern in HARD_SECRETS:
        match = pattern.search(content)
        if match and not PLACEHOLDER.search(match.group(0)):
            print(
                f"vibecheck остановил запись: в тексте {name} — {mask(match.group(0))}\n"
                f"Файл: {path or '—'}\n\n"
                "Ключ в коде уезжает вместе с репозиторием и остаётся в истории навсегда.\n"
                "Положите значение в .env и читайте оттуда, а .env держите в .gitignore.\n"
                "Если это пример для документации — замените значение на заглушку "
                "вроде sk-ant-YOUR-KEY-HERE.",
                file=sys.stderr,
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
