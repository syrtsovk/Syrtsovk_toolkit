#!/usr/bin/env python3
"""vibecheck: карта проекта.

Делит проект на участки и расставляет их по важности, чтобы обход шёл
от горячего к холодному, а не по алфавиту. Нужна на больших проектах:
модель не прочитает три тысячи файлов за раз, но пройдёт двадцать участков
по одному, отмечая сделанное.

Запуск:
    python3 scan_map.py /путь/к/проекту
    python3 scan_map.py . --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", "vendor", "target", ".idea", ".vscode",
    "coverage", ".turbo", ".cache", "site-packages", ".mypy_cache", ".tox",
    ".claude", ".cursor", ".husky",
}
CODE_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".vue", ".svelte",
            ".go", ".rb", ".php", ".java", ".kt", ".rs", ".cs", ".swift"}

MAX_ZONES = 25          # больше человек всё равно не удержит
MIN_ZONE_FILES = 3      # мельче — сливаем в родителя

# Чем выше в списке, тем раньше идёт участок. Смотрим и путь, и содержимое.
ZONE_KINDS = [
    ("тесты", 10, re.compile(r"(?i)(^|/)(tests?|__tests__|spec|e2e|fixtures?|mocks?)(/|$)")),
    ("замороженное", 11, re.compile(r"(?i)(^|/)(archive|legacy|deprecated|old|backup)s?(/|$)")),
    ("оплата", 1, re.compile(r"(?i)(payment|billing|invoice|checkout|subscription|tariff|price|"
                             r"оплат|платеж|счет|тариф|stripe|yookassa|cloudpayment)")),
    ("вход и права", 2, re.compile(r"(?i)(auth|login|signin|signup|session|password|token|permission|"
                                   r"role|access|jwt|oauth|middleware)")),
    ("данные", 3, re.compile(r"(?i)(^|/)(db|database|models?|schema|migrations?|repositor|queries|"
                             r"prisma|orm|storage)")),
    ("приём извне", 4, re.compile(r"(?i)(^|/)(api|routes?|endpoints?|handlers?|controllers?|"
                                  r"webhooks?|upload|import|parser)")),
    ("фон и очереди", 5, re.compile(r"(?i)(^|/)(worker|queue|task|job|cron|scheduler|consumer|celery)")),
    ("внешние сервисы", 6, re.compile(r"(?i)(client|integration|connector|adapter|provider|sdk|"
                                      r"telegram|bitrix|amocrm|openai|anthropic)")),
    ("интерфейс", 8, re.compile(r"(?i)(^|/)(components?|ui|views?|pages?|screens?|design-system|"
                                r"widgets?|features?)")),
    ("вспомогательное", 9, re.compile(r"(?i)(^|/)(utils?|helpers?|lib|common|shared|types?|constants?|config)")),
]
DEFAULT_KIND = ("прочее", 7)

# Содержимое тоже голосует: папка без говорящего имени, но с работой с деньгами,
# должна попасть наверх.
CONTENT_SIGNALS = [
    (1, re.compile(r"(?i)(stripe\.|yookassa|cloudpayments|createInvoice|\.charge\(|\.refund\(|payout)")),
    (2, re.compile(r"(?i)(bcrypt|argon2|jwt\.(sign|encode|verify)|set_cookie|hash_password|verify_password)")),
    (4, re.compile(r"(?i)(app\.(get|post|put|delete)\(|router\.(get|post)\(|@app\.(get|post)\(|"
                   r"export async function (GET|POST))")),
]


def iter_code_paths(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.suffix.lower() in CODE_EXT:
                yield path


def zone_of(rel: str) -> str:
    """Участок — это папка файла, но не глубже трёх уровней от корня."""
    parts = Path(rel).parts[:-1]
    if not parts:
        return "."
    return "/".join(parts[:3])


def classify(zone: str, sample_text: str) -> tuple[str, int]:
    """Сначала спрашиваем путь: имя папки говорит о назначении честнее всего.

    Содержимое голосует только там, где путь ничего не сказал — папка
    без говорящего имени, но с работой с деньгами, должна попасть наверх.
    """
    for name, rank, pattern in ZONE_KINDS:
        if pattern.search(zone):
            return name, rank
    for rank, pattern in CONTENT_SIGNALS:
        if pattern.search(sample_text):
            return next(n for n, r, _ in ZONE_KINDS if r == rank), rank
    return DEFAULT_KIND


def build_zones(root: Path) -> list[dict]:
    by_zone: dict[str, list[str]] = defaultdict(list)
    for path in iter_code_paths(root):
        by_zone[zone_of(str(path.relative_to(root)))].append(str(path.relative_to(root)))

    # Мелкие участки поднимаем к родителю, пока список не станет обозримым.
    # Верхнеуровневые не трогаем: выше них подниматься некуда.
    while len(by_zone) > MAX_ZONES:
        mergeable = [z for z in by_zone if "/" in z]
        if not mergeable:
            break
        smallest = min(mergeable, key=lambda z: len(by_zone[z]))
        parent = "/".join(smallest.split("/")[:-1])
        by_zone[parent].extend(by_zone.pop(smallest))

    zones = []
    for zone, files in by_zone.items():
        sample = ""
        for rel in files[:6]:
            try:
                sample += (root / rel).read_text(encoding="utf-8", errors="ignore")[:4000]
            except OSError:
                continue
        kind, rank = classify(zone, sample)
        zones.append({
            "zone": zone,
            "kind": kind,
            "rank": rank,
            "files": len(files),
            "sample": files[:3],
        })
    merged: list[dict] = []
    collapsed: dict[str, dict] = {}
    for z in zones:
        if z["rank"] in (10, 11):
            head = collapsed.get(z["kind"])
            if head is None:
                collapsed[z["kind"]] = dict(z, zone=f"всё {z['kind']}", parts=[z["zone"]])
            else:
                head["files"] += z["files"]
                head["parts"].append(z["zone"])
            continue
        merged.append(z)
    merged.extend(collapsed.values())
    merged.sort(key=lambda z: (z["rank"], -z["files"]))
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description="vibecheck — карта проекта по участкам")
    parser.add_argument("path", nargs="?", default=".", help="папка проекта")
    parser.add_argument("--json", action="store_true", help="машинный вывод")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Не папка: {root}", file=sys.stderr)
        return 1

    zones = build_zones(root)
    total = sum(z["files"] for z in zones)

    if args.json:
        json.dump({"total_files": total, "zones": zones}, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return 0

    print(f"Карта проекта: {total} файлов, {len(zones)} участков\n")
    print(f"{'#':<4}{'участок':<42}{'что это':<18}{'файлов':>7}")
    print("-" * 71)
    for i, z in enumerate(zones, 1):
        print(f"{i:<4}{z['zone'][:41]:<42}{z['kind']:<18}{z['files']:>7}")
    print("\nПорядок обхода — сверху вниз: сначала деньги и доступы, в конце оформление.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
