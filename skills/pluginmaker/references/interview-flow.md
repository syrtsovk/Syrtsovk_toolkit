---
title: pluginmaker — Interview Flow (M1-M4)
aliases:
  - interview-flow
  - pluginmaker-interview
created: 2026-05-16
updated: 16-31-2026
tags:
  - pluginmaker
  - reference
  - interview
  - skill-design
provenance: llm-generated
confidence: 0.9
lifecycle: draft
entry-point: true
---

# Interview Flow — операционный документ Интервьюера

Это reference, по которому работает sub-agent `Интервьюер` внутри `/pluginmaker`. На выходе — структурированный `brief.yaml`, который передаётся Сборщику. Цель — собрать **минимально достаточный** контекст за 3–6 вопросов без friction.

## 0. Зачем M1-M4

Источник: Modular AI Interviewer (arxiv:2601.11534). Идея: интервью разбивается на 4 функциональных модуля, каждый со своей целью. Это даёт adaptive flow вместо линейной анкеты.

| Модуль | Цель | Поведение в pluginmaker |
|---|---|---|
| **M1** | Low-barrier entry — снять страх «не знаю с чего начать» | Один открытый вопрос с 4 готовыми опциями + Other |
| **M2** | Профилирование — определить тип скилла и сложность | Авто-парс Q1 + (опц.) подтверждение типа |
| **M3** | Most Impactful Axis — самый информативный вопрос | Выбор из {trigger, tools, source-target} по типу |
| **M4** | Adaptive follow-up — reflection (<10 слов) + transition | 2-3 type-specific вопроса, можно сократить |

**Outcome:** заполненный `brief.yaml` (см. §8). Бриф читает Сборщик, генерирует SKILL.md.

**Принципы:**
- Минимум — 3 вопроса (Q1 + Q3 + negative-triggers). Максимум — 6.
- Каждый вопрос — `AskUserQuestion` с 2-4 опциями (или multiSelect для tools).
- Reflection перед новым вопросом: «Понял — это [type], срабатывает [trigger]. Теперь...» (< 10 слов).
- Если юзер в Q1 дал детальный ответ (≥3 сущности: задача + trigger + tools) — пропускаем Q4-5.

---

## 1. Q1 (M1) — открытый старт

**Header:** `Что делать`
**Question:** «Опиши задачу скилла: какую работу он должен делать?»
**multiSelect:** false

**Options:**

| Label | Description |
|---|---|
| Исследовать тему | Собрать информацию из web/файлов/vault, синтезировать выжимку или отчёт |
| Проверить код | Найти баги, security-проблемы, нарушения конвенций в diff/файлах |
| Автоматизировать процесс | Многошаговый workflow с состоянием (orchestration) или одношаговая автоматизация по триггеру |
| Сгенерировать документацию | Создать README, JSDoc, ADR, changelog или другой структурный текст |
| Other | Свой вариант — опиши свободным текстом |

**AskUserQuestion JSON:**

```json
{
  "questions": [{
    "header": "Что делать",
    "question": "Опиши задачу скилла: какую работу он должен делать?",
    "multiSelect": false,
    "options": [
      {"label": "Исследовать тему", "description": "Собрать info из web/vault/files, синтезировать"},
      {"label": "Проверить код", "description": "Bugs, security, convention violations"},
      {"label": "Автоматизировать процесс", "description": "Workflow или одношаговая автоматизация"},
      {"label": "Сгенерировать документацию", "description": "README, JSDoc, ADR, changelog"},
      {"label": "Other", "description": "Свой вариант текстом"}
    ]
  }]
}
```

**Если Other** → задаём один уточняющий open-ended текст: «Опиши в 1-2 предложениях что должен делать скилл».

---

## 2. Q2 (M2) — авто-профилирование + (опц.) подтверждение типа

**Парсинг ответа Q1 → scaffold type.** Делается без вопроса юзеру, если keyword'ы однозначны.

**Decision table (keyword → scaffold type):**

| Keywords / опция Q1 | Scaffold type | Q-count |
|---|---|---|
| исследовать, research, найти info, проанализировать, собрать данные, deep dive | **research-agent** | 6 |
| код, review, баги, security, audit, diff, lint, проверить PR | **code-reviewer** | 5 |
| workflow, orchestrate, multi-step, pipeline, цепочка, state machine, координация | **workflow-orchestrator** | 6 |
| docs, README, JSDoc, TSDoc, ADR, changelog, комментарии, документация | **doc-generator** | 5 |
| vault, knowledge base, curate, RAG, источники, синтез поверх корпуса, ingest | **knowledge-curator** | 5 |
| hook, trigger, одношаговое, автоматизация, на каждое событие, periodic | **simple-automation** | 4 |

**Логика:**
1. Распарсить ответ Q1 (выбранная опция + текст для Other).
2. Подсчитать матчи keyword'ов по каждому типу.
3. Если top-match ≥ 2× second-match → принять без подтверждения, перейти к Q3.
4. Если ambiguous (top ≈ second) → задать Q2 подтверждение.

**Q2 (only if ambiguous):**

**Header:** `Тип скилла`
**Question:** «Я понял задачу как [type-A]. Подтверди или выбери другое»

```json
{
  "questions": [{
    "header": "Тип скилла",
    "question": "Я понял задачу как research-agent (исследовать + синтез). Верно? Или другой тип?",
    "multiSelect": false,
    "options": [
      {"label": "Да, research-agent", "description": "Multi-step search + synthesis с цитатами"},
      {"label": "Скорее knowledge-curator", "description": "Работа поверх vault/KB, не web"},
      {"label": "Скорее workflow", "description": "Это многошаговый процесс, не research"},
      {"label": "Other", "description": "Опиши точнее"}
    ]
  }]
}
```

**Complexity** (определяется параллельно):
- Длина ответа Q1 < 10 слов + Other выбран → `simple`
- Q1 = одна из 4 готовых опций без Other → `standard`
- Other + ≥30 слов + упоминание ≥2 систем (vault + MCP, code + docs, etc.) → `complex`

---

## 3. Q3 (M3) — Most Impactful Axis

**Выбор axis по типу.** Один из трёх, какой больше всего повлияет на финальный SKILL.md.

| Scaffold type | Most impactful axis | Q-вариант |
|---|---|---|
| research-agent | source/target | Q3c |
| code-reviewer | trigger | Q3a |
| workflow-orchestrator | tools | Q3b |
| doc-generator | source/target | Q3c |
| knowledge-curator | trigger | Q3a |
| simple-automation | tools | Q3b |

### Q3a — Trigger mode

**Header:** `Когда срабатывает`
**Question:** «Auto-invoke (Claude сам решит по описанию) или manual `/command-name`?»

```json
{
  "questions": [{
    "header": "Когда срабатывает",
    "question": "Auto-invoke (Claude сам решит по описанию) или manual /command-name?",
    "multiSelect": false,
    "options": [
      {"label": "Auto", "description": "Claude триггерит сам — нужны pushy positive triggers"},
      {"label": "Manual", "description": "Только по /команде — точный контроль"},
      {"label": "Both", "description": "Auto + опционально /команда для явного вызова"},
      {"label": "Other", "description": "Гибрид или условие — опиши"}
    ]
  }]
}
```

### Q3b — Tools

**Header:** `Инструменты`
**Question:** «Какие tools нужны скиллу? Отметь все применимые»
**multiSelect:** true

```json
{
  "questions": [{
    "header": "Инструменты",
    "question": "Какие tools нужны скиллу? (multi-select)",
    "multiSelect": true,
    "options": [
      {"label": "Read/Edit/Write", "description": "Работа с файлами проекта"},
      {"label": "Bash", "description": "Shell-команды, git, npm, etc."},
      {"label": "Grep/Glob", "description": "Поиск по коду/файлам"},
      {"label": "WebSearch/WebFetch", "description": "Доступ к интернету"},
      {"label": "MCP-сервер", "description": "Внешний MCP (укажи какой — github, n8n, context7, etc.)"},
      {"label": "Только текст", "description": "Скиллу не нужны tools — он работает на reasoning'е"}
    ]
  }]
}
```

Если выбран `MCP-сервер` → follow-up open-ended: «Какой именно MCP? (имя сервера или URL)».

### Q3c — Source / Target

**Header:** `Откуда и куда`
**Question:** «Откуда брать input и куда писать output?»

```json
{
  "questions": [{
    "header": "Откуда и куда",
    "question": "Откуда брать input и куда писать output?",
    "multiSelect": false,
    "options": [
      {"label": "Web → отчёт в чат", "description": "Search в интернете, ответ в conversation"},
      {"label": "Локальные файлы → файл", "description": "Чтение проекта, запись в новый/существующий файл"},
      {"label": "Vault → wiki-страница", "description": "Источник — Obsidian vault, output — wiki/synthesis/*"},
      {"label": "Mixed", "description": "Комбинация — уточню в следующем вопросе"},
      {"label": "Other", "description": "Опиши свой паттерн"}
    ]
  }]
}
```

---

## 4. Q4-6 (M4) — adaptive follow-ups по типу

**Reflection format** перед каждым Q4-6: «Понял — [type], [axis-answer]. Теперь...»  (≤10 слов).

### research-agent (3 follow-ups)

**Q4 — Поиск:**
- Header: `Источники`
- Q: «Где искать информацию?»
- Options: Web only / Локальные файлы / Vault / MCP (context7, etc.) / Комбинация

**Q5 — Output format:**
- Header: `Формат`
- Q: «В каком виде давать результат?»
- Options: Краткая выжимка (5-10 строк) / Структурированный отчёт (sections) / Сравнительная таблица / Markdown-файл в проект / Other

**Q6 (optional) — Citation policy:**
- Header: `Цитаты`
- Q: «Указывать источники?»
- Options: Всегда с URL/file-path / Только по запросу / Inline footnotes / Не нужно

### code-reviewer (2-3 follow-ups)

**Q4 — Scope:**
- Header: `Что ревьюим`
- Q: «На какие категории смотреть?»
- multiSelect: true
- Options: Security / Bugs (logic errors) / Performance / Conventions (style) / Tests coverage / Architecture

**Q5 — Output:**
- Header: `Формат ревью`
- Q: «Как подавать findings?»
- Options: Inline comments per-line / Сводный отчёт с severity / GitHub PR comments via gh / Список TODO в файле

**Q6 (optional) — Severity policy:**
- Header: `Severity`
- Q: «Бить во все колокола или только critical?»
- Options: Только critical+high / Все уровни / По запросу threshold / Other

### workflow-orchestrator (3 follow-ups)

**Q4 — Steps:**
- Header: `Шаги`
- Q: «Сколько шагов и какие? Опиши последовательность (free-text)»
- (free-text — без options)

**Q5 — State:**
- Header: `Состояние`
- Q: «Нужно ли сохранять прогресс между шагами?»
- Options: Да, в файл (resume support) / Да, in-memory / Нет, stateless / Other

**Q6 — Sub-agents:**
- Header: `Параллелизм`
- Q: «Запускать sub-agents параллельно?»
- Options: Да, parallel fan-out / Sequential pipeline / Только Tech Lead-стиль (один coordinator) / Не знаю — реши сам

### doc-generator (2 follow-ups)

**Q4 — Template:**
- Header: `Шаблон`
- Q: «По какому шаблону писать?»
- Options: README (project overview) / API docs (JSDoc/TSDoc) / ADR (architecture decision) / Changelog / Custom (укажу позже)

**Q5 — Trigger source:**
- Header: `Что анализировать`
- Q: «Из чего генерировать docs?»
- Options: Git diff (changes only) / Весь проект / Конкретные файлы (manual list) / Symbols from index

### knowledge-curator (2-3 follow-ups)

**Q4 — Vault scope:**
- Header: `Зона vault'а`
- Q: «По каким папкам работаем?»
- Options: wiki/concepts/ / wiki/entities/ / wiki/sources/ / raw/inbox/ → wiki/ / Весь vault / Other

**Q5 — Action:**
- Header: `Действие`
- Q: «Что делаем с найденным?»
- Options: Создать synthesis-страницу / Обновить cross-refs / Найти orphan'ы / Suggest tag canonization / Other

**Q6 (optional) — Provenance:**
- Header: `Provenance`
- Q: «Как помечать AI-generated claims?»
- Options: Inline `^[inferred]` / Frontmatter breakdown / Both / Не нужно

### simple-automation (1-2 follow-ups)

**Q4 — Trigger event:**
- Header: `Событие`
- Q: «По чему срабатывает?»
- Options: Hook (PreToolUse/PostToolUse/Stop) / Slash-command manual / Cron/schedule / Other

**Q5 (optional) — Side effects:**
- Header: `Эффекты`
- Q: «Меняет файлы/git/внешние системы?»
- Options: Read-only (safe) / Меняет файлы / git operations / External API calls / Mixed

---

## 5. Negative triggers — обязательный последний вопрос

**Header:** `Когда НЕ срабатывать`
**Question:** «Когда скилл НЕ должен срабатывать? Что похоже на твою задачу, но это НЕ оно?»

```json
{
  "questions": [{
    "header": "Когда НЕ срабатывать",
    "question": "Когда скилл НЕ должен срабатывать? Назови 1-3 ситуации похожих на задачу, но НЕ её",
    "multiSelect": true,
    "options": [
      {"label": "Похожая задача в другом домене", "description": "Например: review кода ≠ review текста"},
      {"label": "Меньший масштаб", "description": "Однострочные правки vs полноценный workflow"},
      {"label": "Больший масштаб", "description": "Архитектурное решение vs быстрый ответ"},
      {"label": "Прямой запрос другого скилла", "description": "User явно зовёт другую команду"},
      {"label": "Other", "description": "Опиши свободно"}
    ]
  }]
}
```

**Why critical:** без negative triggers description становится over-triggering. Пример pushy формата для финального SKILL.md:
> Use when: X, Y, Z. **Do NOT use when:** A, B, C.

Negative triggers идут в YAML `description` как clause «Do NOT use when: ...». Это снижает false-positive rate на dry-run (см. validation pipeline §13.4).

---

## 6. Pause-points — когда остановиться раньше

| Сигнал | Действие |
|---|---|
| Q1-ответ ≥30 слов покрывает {task, trigger, tools/source} | Пропустить Q3, перейти к Q4 type-specific (1 вопрос) + negative-triggers. **Total: 3 Q.** |
| Q1-ответ покрывает {task, trigger} но не tools | Пропустить Q3a, задать Q3b/Q3c + 1 follow-up + negative. **Total: 4 Q.** |
| Q1 = выбор готовой опции без Other, ответ короткий | Полный flow: Q1 → Q3 → Q4 → Q5 → Q6 → negative. **Total: 5-6 Q.** |
| После Q3 юзер уточнил всё сам в свободной форме | Скип Q4-5, оставить negative-triggers. **Total: 3 Q.** |
| После любого Q юзер пишет «всё, хватит, собирай» | Stop, передать brief как есть, помечая `complexity: simple`. |

**Минимум:** 3 вопроса (Q1 + Q3 + negative). **Максимум:** 6 вопросов. Не выходить за этот диапазон — friction.

---

## 7. Reflection & Transition templates (M4)

Между вопросами Интервьюер вставляет **одну строку** reflection + transition:

| После | Template |
|---|---|
| Q1 | «Понял — это [type]. Теперь уточню [axis-name].» |
| Q3a | «Триггер [auto/manual]. Дальше — [Q4-topic].» |
| Q3b | «Инструменты записал. Теперь [Q4-topic].» |
| Q3c | «Источник [X] → output [Y]. Уточню [Q4-topic].» |
| Q4 | «Записал. Ещё [N] вопрос(ов).» |
| Q5 | «Почти всё. Последний — про negative.» |
| Negative | «Готово, собираю бриф.» |

**Лимит:** ≤10 слов на reflection. Без эмодзи, без воды.

---

## 8. Output — `brief.yaml`

Передаётся Сборщику. **Все поля обязательны** (если значение неизвестно — `null` или `[]`).

```yaml
skill_name: <kebab-case-derived-from-Q1-or-explicit>
skill_type: research-agent | code-reviewer | workflow-orchestrator | doc-generator | knowledge-curator | simple-automation
complexity: simple | standard | complex
trigger_mode: auto | manual | both
positive_triggers:
  - "<phrase-1 from Q1/Q4>"
  - "<phrase-2>"
  - "<phrase-3>"   # минимум 3 синонима для description
negative_triggers:
  - "<situation-1 from negative-Q>"
  - "<situation-2>"
tools_needed:
  - Read
  - Edit
  - Bash
  - Grep
  - WebSearch
  # точный список из allowed-tools whitelist
external_deps:
  - web                # если WebSearch/WebFetch
  - "mcp:context7"     # если MCP — с именем
  - none
source: <where input comes from — описать в 1 строке>
output: <where result goes — описать в 1 строке>
language: en | ru      # язык SKILL.md и сообщений
user_notes: |
  Free-text — всё что юзер сказал но не легло в поля выше.
  Сборщик использует для description'а и edge cases секции.
interview_meta:
  questions_asked: 3 | 4 | 5 | 6
  early_stop_reason: <null или причина pause-point>
  ambiguity_resolved: true | false   # был ли Q2 подтверждения
```

**Validation перед передачей Сборщику:**
- `skill_name` — kebab-case, ≤40 символов, не конфликтует с существующими в `~/.claude/skills/` и `./.claude/skills/`.
- `positive_triggers` — минимум 3, каждый ≥2 слов.
- `negative_triggers` — минимум 1.
- `tools_needed` — каждый из whitelist (Read, Edit, Write, Bash, Grep, Glob, WebSearch, WebFetch, AskUserQuestion, Task, mcp:<name>).
- Если `external_deps` содержит `mcp:*` — имя сервера резолвится (есть в `~/.claude/settings.json` или явно указано юзером).

Если хоть один пункт не прошёл — Интервьюер задаёт **точечный re-ask** на конкретное поле, не возвращается к началу.

---

## 9. Edge cases

| Случай | Поведение |
|---|---|
| Юзер отвечает «не знаю» на Q1 | Дать example-based fallback: показать 3 готовых skill'а (research-agent, doc-generator, simple-automation) с однострочным описанием. Спросить «какой ближе». |
| Юзер просит «сделай как [existing skill]» | Прочитать тот skill (Read), извлечь brief по шаблону §8, спросить «что меняем». Пропустить M1-M3. |
| Юзер пишет на английском | `language: en`, все опции в Q2+ — на английском. Перевести option labels на лету. |
| Конфликт имени с существующим skill | Re-ask только `skill_name` с suggestion'ом (`<name>-v2`, `<name>-custom`). |
| Юзер выбрал ≥4 типов в multi-select tools | Warn: «много tools = широкий blast radius. Точно нужны все?» — дать возможность сократить. |
| Q1 = Other и текст < 5 слов | Re-ask Q1 с подсказкой: «слишком коротко — опиши в 1-2 предложениях задачу скилла». |

---

## 10. Чеклист Интервьюера перед передачей Сборщику

- [ ] Задано 3–6 вопросов (не меньше, не больше)
- [ ] `skill_type` определён (auto-parsed или подтверждён через Q2)
- [ ] `positive_triggers` ≥ 3, `negative_triggers` ≥ 1
- [ ] `tools_needed` валидирован против whitelist
- [ ] `skill_name` уникален
- [ ] Reflection между Q вставлены (≤10 слов каждая)
- [ ] `user_notes` содержит всё что не легло в structured поля
- [ ] Юзер видел финальный summary брифа и подтвердил («Собираю — ок?»)

**Только после чеклиста** — передача брифа Сборщику.

---

## Источники

- `guide.md §13.2` — M1-M4 framework (Modular AI Interviewer, arxiv:2601.11534)
- `guide.md §13.3` — 6 scaffold types с Q-count
- `guide.md §13.4` — validation pipeline (использует `positive_triggers` / `negative_triggers` из брифа)
- Anthropic `/skill-creator` — 5-step workflow (Tier 1 baseline)
- nickwinder `skill-generator` — dynamic consultation pattern (для Сборщика, не Интервьюера)
