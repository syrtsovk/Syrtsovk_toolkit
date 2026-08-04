---
title: pluginmaker v1 — Output Structure Spec
created: 2026-05-16
updated: 16-32-2026
tags:
  - pluginmaker
  - spec
  - output
provenance: llm-generated
confidence: 0.85
lifecycle: draft
sources:
  - internal design guide (не входит в поставку)
---

# pluginmaker v1 — Output Structure

> Точная спецификация того, что pluginmaker записывает на диск после прохождения интервью и валидации. Этот документ — единственный источник истины для **Сборщика-агента**: он не импровизирует, а сверяется со схемами ниже.

Канонический источник: `guide.md` §1.2 (структура директорий), §2.1 (skill structure), §5.2 (progressive disclosure), §13.6 (output for pluginmaker).

---

## 1. Output mode

v1 поддерживает **только skill-mode** (default и единственный). Bundle-mode — заглушка для v2.

### 1.1 Skill-mode (v1, default)

Pluginmaker выдаёт **одну самодостаточную папку** `<skill-name>/`, содержащую только то, что нужно для работы skill'а (без `plugin.json`, без `marketplace.json`, без `LICENSE`).

Эта папка совместима с тремя точками установки:

| Точка установки | Путь | Когда |
|---|---|---|
| Project-level | `<project>/.claude/skills/<skill-name>/` | Skill нужен в одном проекте |
| User-level | `~/.claude/skills/<skill-name>/` | Skill нужен везде у этого пользователя |
| Inside plugin | `<plugin-root>/skills/<skill-name>/` | Skill добавляется к существующему плагину |

Папка переносится между точками простым `mv` — никаких изменений внутри не требуется.

### 1.2 Bundle-mode (v2, заглушка)

В v2 pluginmaker сможет генерировать полный bundle:

```
<plugin-name>/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json    # опц., для дистрибуции
├── skills/
│   └── <skill-name>/       # ← то же что v1 выдаёт
├── README.md               # plugin-level
├── LICENSE
└── CHANGELOG.md
```

**В v1 это НЕ генерируется.** Если юзер просит «сделай мне плагин с несколькими skill'ами» — pluginmaker отвечает: «v1 делает один skill за раз; bundle планируется на v2; пока генерирую первый skill».

---

## 2. Структура файлов skill-mode

### 2.1 Канонический layout

```
<skill-name>/
├── SKILL.md                        ← обязательно (тело skill'а)
├── references/                     ← опционально, lazy load
│   └── <subtopic>.md
├── scripts/                        ← опционально, UV single-file
│   └── <name>.py
├── assets/                         ← опционально, templates/fonts
│   └── <file>
├── test-cases.json                 ← обязательно (test suite от L2 валидации)
└── .pluginmaker-meta.json          ← обязательно (audit trail)
```

### 2.2 Когда какая папка нужна

| Папка | Условие включения | Откуда решение |
|---|---|---|
| `references/` | SKILL.md приближается к 500 строкам (guide §5.2 hard limit), или есть «тяжёлые» edge-cases / lookup-таблицы | Сборщик прикидывает финальный размер SKILL.md; если >400 строк — выносит детали в `references/<topic>.md` и ссылается `For detailed X, see references/x.md` |
| `scripts/` | Skill вызывает детерминистические команды (lint, sanitize, parse) | Только UV single-file Python (с inline `# /// script` блоком), либо `.sh`. Никаких `requirements.txt` рядом |
| `assets/` | Есть шаблоны (Markdown/HTML), иконки, шрифты, статические configs | Каждый asset ссылается из SKILL.md явным путём `assets/<file>` |

**Жёсткое правило (guide §1.2):** внутри `<skill-name>/` **НЕТ `README.md`**. README уходит на уровень плагина (bundle-mode, v2). В skill-mode README не создаётся вовсе — документация живёт в SKILL.md и `references/`.

### 2.3 Обязательный минимум

Минимально валидный output:

```
<skill-name>/
├── SKILL.md
├── test-cases.json
└── .pluginmaker-meta.json
```

Три файла. Папки `references/`, `scripts/`, `assets/` появляются только если нужны.

---

## 3. SKILL.md канонический шаблон

Layout, который Сборщик заполняет:

```markdown
---
name: <kebab-case-name>
description: <80-1024 chars; [What it does] + [When trigger phrases / situations] + [When NOT to use]>
allowed-tools: <comma-separated list, e.g. Read, Grep, Glob>
model: <optional: sonnet | haiku | opus>
argument-hint: <optional: "[arg-name]">
---

# <Skill Display Name>

<Outcome-first opening: 1-2 предложения. «Your goal is to ...».>

## When to use

- <Trigger situation 1, mirrors a phrase from description>
- <Trigger situation 2>
- <...>

## When NOT to use

- <Negative case 1: близкая по словам задача, но другая цель>
- <Negative case 2>
- <...>

## Workflow

1. <Step — positive imperative, начинается с глагола>
2. <Step>
3. <...>

## Output format

<Что skill возвращает / производит / куда пишет. Конкретный формат: текстовый ответ, файл, JSON-блок, etc.>

## References

<Только если есть references/. Формат: «For detailed X, see references/x.md».>
```

### 3.1 Жёсткие правила (из guide §2.1, §5.1, §5.3)

| Поле | Правило |
|---|---|
| `name` | kebab-case, lowercase. Регекс `^[a-z][a-z0-9-]*[a-z0-9]$`. Совпадает с именем папки |
| `description` | 80–1024 символов. Без CAPSLOCK, без `MUST`/`NEVER`. Без XML-тегов (security) |
| `allowed-tools` | Минимальный набор. Comma- или space-separated. Default — пусто (все доступны) — но pluginmaker всегда явно проставляет |
| Body длина | ≤500 строк / ~5000 слов. Если приближаемся — split в `references/` |
| Стиль body | Outcome-first opening, positive imperatives, без CAPSLOCK |

### 3.2 Обязательные секции в body

`When to use`, `When NOT to use`, `Workflow`, `Output format` — обязательны для всех scaffold'ов. `References` появляется только если есть `references/`.

---

## 4. test-cases.json формат

Файл генерируется автоматически на этапе **L2-валидации (dry-run)**. Сборщик создаёт positive/negative промпты, прогоняет их через decision-only model call, заполняет `validation_result`.

```json
{
  "skill_name": "<kebab-case-name>",
  "generated_by": "pluginmaker/v1",
  "generated_at": "2026-05-16T14:23:45Z",
  "positive_cases": [
    {
      "id": "p1",
      "prompt": "Пользовательский промт, который ДОЛЖЕН триггерить skill",
      "expected_trigger": true,
      "rationale": "Матчит trigger phrase 'review code' из description"
    },
    {
      "id": "p2",
      "prompt": "...",
      "expected_trigger": true,
      "rationale": "..."
    }
  ],
  "negative_cases": [
    {
      "id": "n1",
      "prompt": "Близкая по словам задача, которую skill НЕ должен брать",
      "expected_trigger": false,
      "rationale": "Близко лексически ('review'), но речь про PR-ревью людьми, не код-аудит"
    }
  ],
  "validation_result": {
    "level_1_lint": "PASS",
    "level_2_dry_run": {
      "positive_accuracy": 0.8,
      "negative_accuracy": 1.0,
      "overall": "PASS"
    },
    "level_3_content_audit": "PASS"
  }
}
```

### 4.1 Минимальный объём

| Сложность skill | Positive cases | Negative cases |
|---|---|---|
| simple | 3 | 2 |
| standard | 5 | 3 |
| complex | 8 | 5 |

### 4.2 Семантика `overall`

- `PASS` — `positive_accuracy ≥ 0.8` и `negative_accuracy ≥ 0.9`.
- `WARN` — один из показателей ниже порога, но не критично; в meta фиксируется warning.
- `FAIL` — `positive_accuracy < 0.6` или `negative_accuracy < 0.7`; pluginmaker предлагает доработать description.

---

## 5. .pluginmaker-meta.json формат

Полный audit trail генерации. Нужен для:
- Воспроизводимости (видно какие вопросы задавались и что юзер ответил).
- Диагностики (если skill плохо триггерится — смотрим `inferred_type` и `validation`).
- Будущего batch-анализа эффективности pluginmaker'а (v2 roadmap).

```json
{
  "generated_by": "pluginmaker/v1.0",
  "generated_at": "2026-05-16T14:23:45Z",
  "interview": {
    "questions_asked": [
      {
        "q": "Опиши одной фразой какую задачу решает skill",
        "a": "Анализ конкурентов на B2B-рынке"
      },
      {
        "q": "В каких ситуациях ты хочешь чтобы он триггерился сам?",
        "a": "Когда я говорю 'разбери конкурента X' или 'сравни нас с Y'"
      }
    ],
    "inferred_type": "research-agent",
    "inferred_complexity": "standard",
    "language": "ru"
  },
  "scaffold_used": "research-agent",
  "validation": {
    "L1_lint_passed": true,
    "L1_warnings": [],
    "L2_dry_run_score": 0.9,
    "L2_dry_run_details": {
      "positive_accuracy": 0.8,
      "negative_accuracy": 1.0
    },
    "L3_audit_passed": true,
    "L3_warnings": []
  },
  "user_overrides": [
    {
      "field": "allowed-tools",
      "from": "Read, Grep",
      "to": "Read, Grep, WebFetch",
      "reason": "Юзер попросил веб-поиск"
    }
  ],
  "bootstrap_self_test": null
}
```

### 5.1 Поля

| Поле | Что |
|---|---|
| `interview.questions_asked` | Полный список Q/A из adaptive interview (см. §13.2 guide) |
| `interview.inferred_type` | Один из шести scaffold'ов v1 (см. §13.3 guide) |
| `interview.inferred_complexity` | `simple` / `standard` / `complex` |
| `interview.language` | `ru` / `en` — определяется по языку ответов |
| `scaffold_used` | Какой scaffold реально применён (может отличаться от inferred, если юзер переопределил) |
| `validation.*` | Результаты L1/L2/L3 (см. §13.4 guide) |
| `user_overrides` | Список ручных правок, которые юзер внёс поверх предложенного pluginmaker'ом |
| `bootstrap_self_test` | `null` в обычном режиме. Объект с метриками — если pluginmaker генерил сам себя (см. §13.7 guide) |

---

## 6. Naming & path conventions

### 6.1 Имя папки skill'а

- **kebab-case**, lowercase, ASCII.
- Регекс: `^[a-z][a-z0-9-]*[a-z0-9]$`.
- Без пробелов, без `_`, без CamelCase.
- Совпадает с `name:` в frontmatter SKILL.md (это **жёсткое** требование Claude Code runtime).

Примеры:
- ✅ `code-reviewer`, `pdf-processor`, `release-check`
- ❌ `Code-Reviewer`, `code_reviewer`, `CodeReviewer`, `my plugin`

### 6.2 SKILL.md — точное имя

- **`SKILL.md`** — case-sensitive: заглавные `S`, `K`, `I`, `L`, `L`, далее точка-md в нижнем регистре.
- Не `skill.md`, не `Skill.md`, не `SKILL.MD`.
- Runtime ищет именно `SKILL.md`; всё остальное игнорируется и skill не активируется.

### 6.3 references/

- Имена файлов — **kebab-case .md**: `output-structure.md`, `edge-cases.md`, `scaffold-types.md`.
- Один файл — одна тема (single responsibility).
- Каждый файл из `references/` упомянут хотя бы один раз в SKILL.md (иначе зачем он там — мёртвый код).

### 6.4 scripts/

- UV single-file Python: имя файла `<purpose>.py`, kebab-case в имени (без подчёркиваний кроме внутренних имён).
- Inline shebang `# /// script` блок с зависимостями.

### 6.5 Запрещено

- README.md внутри `<skill-name>/` (guide §1.2 жёсткое правило).
- Файлы с расширением `.MD`, `.Md` — только `.md`.
- Имя skill'а из reserved-list: `default`, `system`, `claude`, `anthropic` (см. guide §4.4).

---

## 7. Где складывать output

После прохождения L3-валидации pluginmaker создаёт папку под:

```
<cwd>/<skill-name>/
```

(временно, как draft), и спрашивает юзера через **AskUserQuestion** с 4 опциями:

| Опция | Действие | Куда переезжает |
|---|---|---|
| **Deploy user-level** | Доступен во всех проектах текущего пользователя | `~/.claude/skills/<skill-name>/` |
| **Deploy project-level** | Доступен только в текущем проекте | `<cwd>/.claude/skills/<skill-name>/` |
| **Keep as draft** | Не переносит. Юзер сам решит позже | Остаётся `<cwd>/<skill-name>/` |
| **Inside existing plugin** | Добавить в существующий плагин | `<plugin-root>/skills/<skill-name>/` (юзер указывает `<plugin-root>` отдельным вопросом) |

### 7.1 Псевдокод вопроса

```json
{
  "question": "Skill готов. Куда задеплоить?",
  "options": [
    { "label": "User-level (везде)", "value": "user" },
    { "label": "Project-level (только тут)", "value": "project" },
    { "label": "Draft (оставить как есть)", "value": "draft" },
    { "label": "Внутрь существующего плагина", "value": "plugin" }
  ]
}
```

При выборе `plugin` — follow-up: «Укажи путь к корню плагина».

### 7.2 Что делать после деплоя

После `mv` папки pluginmaker:
1. Сообщает финальный путь.
2. Подсказывает команду активации: `/plugins reload` (или эквивалент).
3. Предлагает запустить первый позитивный test-case из `test-cases.json` для smoke-проверки.

---

## 8. Что НЕ генерируется в v1

Список заглушек — это **сознательное «нет»** в v1. Если юзер просит — pluginmaker честно отвечает «v1 не умеет, в roadmap на vX». Не пытается имитировать.

| Фича | Где было бы | Версия |
|---|---|---|
| Hooks конфигурация | `hooks/hooks.json` | v2 |
| MCP server bundling | `.mcp.json` + код сервера | v2 |
| LSP server | `.lsp.json` | v2 |
| Subagents | `agents/<name>.md` | v2 |
| Commands (slash-команды) | `commands/<name>.md` | v2 (сейчас skill покрывает большинство кейсов) |
| Output styles / themes | `output-styles/`, `themes/` | v3 |
| Bundle с `plugin.json` | `.claude-plugin/plugin.json` | v2 |
| Marketplace manifest | `.claude-plugin/marketplace.json` | v2 |
| Auto-publishing на GitHub/npm | — | v3 |
| Multi-skill bundle за один прогон | — | v2 |
| Точная self-reproduction (pluginmaker, генерящий идентичного себя) | — | открытый вопрос, см. §13.7 guide |

### 8.1 Что делать при запросе «v2-фичи»

Шаблон ответа:

> «v1 делает только skill (одна папка с SKILL.md). \[Hooks/MCP/bundle\] на roadmap для v2.
> Если хочешь — могу сейчас сделать skill, а к \[нужной фиче\] вернёмся когда v2 выйдет.»

Никогда не генерировать заглушку файла, который выглядит как рабочий, но не работает. Лучше явный «нет».

---

## Связано

- `guide.md §1.2` — canonical directory structure.
- `guide.md §2.1` — SKILL.md frontmatter spec.
- `guide.md §5.1` — description engineering.
- `guide.md §5.2` — progressive disclosure (5-tier loading).
- `guide.md §5.3` — body structure best practices.
- `guide.md §13.3` — six scaffolds для v1.
- `guide.md §13.4` — validation pipeline (L1/L2/L3).
- `guide.md §13.6` — output structure (исходник для этого файла).
- `guide.md §13.7` — bootstrap / self-hosting.
