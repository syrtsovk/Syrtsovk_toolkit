#!/usr/bin/env bash
# Восстановление настроек Claude Code из бэкап-репозитория.
#
#   ./install.sh            — сухой прогон: только показывает, что будет сделано, ничего не пишет
#   ./install.sh --apply    — реально ставит файлы в $TARGET_HOME/.claude/
#   TARGET_HOME=/tmp/x ./install.sh --apply   — поставить в другую «домашнюю» папку (для проверки)
#
# Что делает:
#   * копирует claude-home/{skills,commands,hooks,agents,scripts,CLAUDE.md,settings.json} в $TARGET_HOME/.claude/
#   * файл, который уже есть и отличается, сначала сохраняет в $TARGET_HOME/.claude-restore-backup-<дата>/
#     (то, что успел настроить новый аккаунт, не пропадёт)
#   * одинаковые файлы не трогает — повторный запуск ничего не меняет
#   * лишние файлы в ~/.claude НЕ удаляет
#   * память проектов (claude-home/projects-memory) кладёт в ~/.claude/projects/<проект>/memory, существующие заметки не перезаписывает
#   * ~/.claude.json НЕ трогает — ключи MCP-серверов вводятся руками (см. SECRETS-NEEDED.md)
set -euo pipefail

APPLY=0
for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) echo "Неизвестный параметр: $arg (есть только --apply и --help)" >&2; exit 2 ;;
  esac
done

TARGET_HOME="${TARGET_HOME:-$HOME}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/claude-home"
DEST="$TARGET_HOME/.claude"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$TARGET_HOME/.claude-restore-backup-$STAMP"
ITEMS=(skills commands hooks agents scripts CLAUDE.md settings.json)

[ -d "$SRC" ] || { echo "Нет папки $SRC — запускай скрипт из корня бэкап-репозитория." >&2; exit 1; }
[ -d "$TARGET_HOME" ] || { echo "Нет папки TARGET_HOME=$TARGET_HOME" >&2; exit 1; }

if [ "$APPLY" -eq 1 ]; then MODE="УСТАНОВКА"; else MODE="СУХОЙ ПРОГОН (ничего не пишу; для установки добавь --apply)"; fi
echo "== $MODE"
echo "   откуда: $SRC"
echo "   куда:   $DEST"

n_new=0; n_upd=0; n_same=0; n_link=0; n_mem=0; backup_used=0

backup_path() {  # сохранить существующий путь (файл или ссылку) в бэкап, не следуя по ссылкам
  local rel="$1"
  mkdir -p "$BACKUP/$(dirname "$rel")"
  cp -pPR "$DEST/$rel" "$BACKUP/$rel"
  backup_used=1
}

seen=$'\n'      # уже показанные ссылки (чтобы в сухом прогоне не повторять)
under_link=0    # 1 = файл лежит под ссылкой, которую установка заменит папкой

ensure_real_dir() {  # каждая папка на пути должна быть настоящей папкой, а не ссылкой
  local rel="$1" acc="" part
  local IFS='/'
  under_link=0
  for part in $rel; do
    acc="${acc:+$acc/}$part"
    if [ -L "$DEST/$acc" ] || { [ -e "$DEST/$acc" ] && [ ! -d "$DEST/$acc" ]; }; then
      under_link=1
      case "$seen" in *$'\n'"$acc"$'\n'*) continue ;; esac
      seen="$seen$acc"$'\n'
      n_link=$((n_link + 1))
      echo "  ССЫЛКА/ФАЙЛ→ПАПКА  $acc  (старое уйдёт в бэкап)"
      if [ "$APPLY" -eq 1 ]; then backup_path "$acc"; rm "$DEST/$acc"; mkdir -p "$DEST/$acc"; under_link=0; fi
    elif [ ! -e "$DEST/$acc" ] && [ "$APPLY" -eq 1 ]; then
      mkdir -p "$DEST/$acc"
    fi
  done
}

[ "$APPLY" -eq 1 ] && mkdir -p "$DEST"

for item in "${ITEMS[@]}"; do
  [ -e "$SRC/$item" ] || { echo "  (в бэкапе нет $item — пропускаю)"; continue; }
  while IFS= read -r -d '' f; do
    rel="${f#"$SRC"/}"
    d="$(dirname "$rel")"
    under_link=0
    if [ "$d" != "." ]; then ensure_real_dir "$d"; fi
    target="$DEST/$rel"
    if [ "$under_link" -eq 1 ]; then
      n_new=$((n_new + 1))   # сухой прогон: папка-ссылка будет заменена, файл ляжет заново
    elif [ -L "$target" ]; then
      n_link=$((n_link + 1)); n_upd=$((n_upd + 1))
      echo "  ССЫЛКА→ФАЙЛ   $rel"
      if [ "$APPLY" -eq 1 ]; then backup_path "$rel"; rm "$target"; cp -p "$f" "$target"; fi
    elif [ -f "$target" ]; then
      if cmp -s "$f" "$target"; then
        n_same=$((n_same + 1))
      else
        n_upd=$((n_upd + 1))
        echo "  ОБНОВИТЬ      $rel"
        if [ "$APPLY" -eq 1 ]; then backup_path "$rel"; cp -p "$f" "$target"; fi
      fi
    elif [ -e "$target" ]; then
      echo "  ПРОПУСК       $rel — на этом месте папка, разберись руками" >&2
    else
      n_new=$((n_new + 1))
      [ "$n_new" -le 20 ] && echo "  НОВЫЙ         $rel"
      [ "$n_new" -eq 21 ] && echo "  … (остальные новые файлы не печатаю)"
      if [ "$APPLY" -eq 1 ]; then cp -p "$f" "$target"; fi
    fi
  done < <(find "$SRC/$item" -type f ! -name '.DS_Store' -print0)
done

# Память проектов: только то, чего ещё нет (cp -n), чужие заметки не трогаем.
MEM_SRC="$SRC/projects-memory"
if [ -d "$MEM_SRC" ]; then
  while IFS= read -r -d '' f; do
    rel="${f#"$MEM_SRC"/}"          # <проект>/<файл>
    proj="${rel%%/*}"; rest="${rel#*/}"
    target="$DEST/projects/$proj/memory/$rest"
    if [ ! -e "$target" ]; then
      n_mem=$((n_mem + 1))
      if [ "$APPLY" -eq 1 ]; then mkdir -p "$(dirname "$target")"; cp -p "$f" "$target"; fi
    fi
  done < <(find "$MEM_SRC" -type f ! -name '.DS_Store' -print0)
fi

echo
echo "== Итог: новых $n_new · обновить $n_upd · без изменений $n_same · ссылок заменить $n_link · заметок памяти $n_mem"
if [ "$APPLY" -eq 1 ]; then
  if [ "$backup_used" -eq 1 ]; then echo "   Старые версии изменённых файлов: $BACKUP"; else echo "   Бэкап не понадобился (ничего не перезаписано)."; fi
else
  echo "   Это был сухой прогон. Ничего не записано. Для установки: ./install.sh --apply"
fi

# Абсолютные пути в settings.json с чужим именем пользователя — предупредить.
if [ -f "$SRC/settings.json" ]; then
  bad="$(grep -o '/Users/[^/"]*' "$SRC/settings.json" 2>/dev/null | sort -u | grep -vx "$TARGET_HOME" || true)"
  if [ -n "$bad" ]; then
    echo
    echo "!! В settings.json зашиты пути другого пользователя:"
    echo "$bad" | sed 's/^/     /'
    echo "   Поправь их в $DEST/settings.json руками."
  fi
fi

echo
echo "Дальше: ключи и входы в сервисы — по SECRETS-NEEDED.md. ~/.claude.json этот скрипт не трогает."
