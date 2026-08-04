---
title: Validation Rules — 3 уровня проверки сгенерированного skill'а
aliases:
  - validation-rules
  - pluginmaker-validation
  - lint-trigger-audit
created: 2026-05-16
updated: 16-32-2026
tags:
  - pluginmaker
  - validation
  - skills
  - claude-code
sources:
  - internal design guide (не входит в поставку)
provenance: llm-generated
confidence: 0.9
lifecycle: draft
entry-point: true
---

# Validation Rules — 3 уровня

> Операционный reference для трёх агентов-валидаторов pluginmaker'а: **Линтер** (Level 1), **Триггер-тестер** (Level 2), **Аудитор качества** (Level 3). По этому документу агенты реально работают — он определяет правила, regex'ы, пороги и формат отчёта.

## Зачем 3 уровня

Чем дальше уровень — тем дороже и неопределённее проверка. Принцип fail-fast:

| Level | Тип | Стоимость | Что ловит | Кто запускает |
|---|---|---|---|---|
| **L1 — Lint** | Детерминистический (bash/regex/jq) | Дёшево (<1s) | Структурные ошибки: невалидный frontmatter, hardcoded paths, antipattern-имена файлов | Агент **Линтер** |
| **L2 — Trigger test** | LLM dry-run (10 промтов) | Средне (~30s, ~5K токенов) | Семантика description: under/over-triggering, weak synonym coverage | Агент **Триггер-тестер** |
| **L3 — Content audit** | LLM семантический разбор | Дорого (~60s, ~10K токенов) | Антипаттерны §7: CAPSLOCK, карго-роли, hypothetical bloat, противоречия | Агент **Аудитор качества** |

**Правило прогона:** L1 → если PASS → L2 → если PASS-with-warnings и выше → L3. Если L1 FAIL — L2/L3 не запускаем (нет смысла оценивать семантику структурно сломанного файла).

---

## Level 1 — Lint (детерминистические правила)

15 правил. Каждое — конкретная bash/regex/jq проверка. Запускается на `SKILL.md` + папке skill'а.

### RULE-L1-01: YAML frontmatter parses

- **Check:** `head -50 SKILL.md | awk '/^---$/{c++; if(c==2) exit} c==1 && NR>1' | python3 -c "import sys, yaml; yaml.safe_load(sys.stdin)"` — exit code 0
- **Severity:** blocker
- **Auto-fix:** none (syntax error требует ручной правки)
- **Error message:** `Frontmatter не парсится как YAML. Проверь отступы, кавычки, двоеточия. Строка: <line из ошибки>.`

### RULE-L1-02: `name:` присутствует и kebab-case

- **Check:** frontmatter содержит `name:` И значение матчит regex `^[a-z][a-z0-9-]*[a-z0-9]$`
- **Severity:** blocker
- **Auto-fix:** если есть `name: My_Skill Name` → нормализуем в `my-skill-name`
- **Error message:** `name должен быть в kebab-case (lowercase, цифры и дефисы, начинается с буквы, не заканчивается дефисом). Получено: '<value>'.`

### RULE-L1-03: `description:` присутствует и непустой

- **Check:** frontmatter содержит ключ `description:` со значением длиной ≥1
- **Severity:** blocker
- **Auto-fix:** none
- **Error message:** `description обязателен. Без него Claude не сможет триггерить skill — это единственное что грузится в metadata-tier (Layer 1, 50–150 токенов).`

### RULE-L1-04: `description:` длина 80–1024 символов

- **Check:** `python3 -c "import yaml,sys; d=yaml.safe_load(open('SKILL.md').read().split('---')[1]); l=len(d['description']); print(l); sys.exit(0 if 80<=l<=1024 else 1)"`
- **Severity:** blocker если >1024; warning если <80
- **Auto-fix:** none — но в error message предложить шаблон `[What] + [When] + [Triggers] + [Not when]`
- **Error message:**
  - `>1024`: `description слишком длинный (<N> симв.). Anthropic hard limit — 1024. Перенеси детали в body или references/.`
  - `<80`: `description подозрительно короткий (<N> симв.). Минимум для покрытия trigger phrases — ~80. Похоже на 'helps with X' антипаттерн (§7.6).`

### RULE-L1-05: `description:` не содержит XML-тегов

- **Check:** `grep -E '<[a-zA-Z][^>]*>' <(yq -r '.description' SKILL.md)` → пустой вывод
- **Severity:** blocker
- **Auto-fix:** strip tags через `sed -E 's/<[^>]+>//g'`
- **Error message:** `description содержит XML-теги (<X>). Запрещено спецификацией Anthropic — metadata-tier парсится как plain text.`

### RULE-L1-06: `description:` третье лицо, не от первого

- **Check:** description **не начинается** с `I `, `My `, `We `, `This skill `, `The skill `. Допустимо: начинается с глагола (Reviews, Generates, Analyzes...) или существительного-функции (Code reviewer that...).
- **Severity:** warning
- **Auto-fix:** если начинается с `This skill performs X` → suggest `Performs X`
- **Error message:** `description должен быть в третьем лице, без "I"/"This skill". Канон Anthropic-плагинов: глагол первым ("Reviews code...", "Generates tests..."). Текущее начало: '<first_8_words>'.`

### RULE-L1-07: `allowed-tools:` валиден (если присутствует)

- **Check:** если ключ есть — это comma-separated list из {Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, Task, TodoWrite, NotebookEdit, AskUserQuestion} или MCP-tool name (`mcp__<server>__<tool>`). Отсутствие ключа = inherit defaults (легально).
- **Severity:** blocker (если значение невалидно)
- **Auto-fix:** удалить неизвестные tools со списка, оставить остальное
- **Error message:** `allowed-tools содержит неизвестный инструмент: '<tool>'. Допустимы стандартные tool names или mcp__<server>__<tool>.`

### RULE-L1-08: SKILL.md ≤500 строк

- **Check:** `wc -l SKILL.md | awk '{print $1}'` ≤ 500
- **Severity:** blocker если >500; warning если 400–500
- **Auto-fix:** none (требует декомпозиции в references/)
- **Error message:**
  - `>500`: `SKILL.md = <N> строк. Anthropic hard limit — 500. Вынеси детали в references/<topic>.md и сошлись из body: "For X, see references/x.md".`
  - `400–500`: `SKILL.md приближается к лимиту (<N>/500). Подумай о декомпозиции в references/ заранее.`

### RULE-L1-09: Нет README.md в папке skill'а

- **Check:** `test ! -f <skill_dir>/README.md`
- **Severity:** blocker
- **Auto-fix:** переименовать в `references/overview.md` если контент полезный; иначе удалить
- **Error message:** `README.md внутри skill folder запрещён (§7.3). Token-tax + breaks progressive disclosure. Перенеси в references/ или удали.`

### RULE-L1-10: Нет файлов с антипаттерн-суффиксами

- **Check:** `find <skill_dir> -type f \( -name '*_v2*' -o -name '*_final*' -o -name '*_fixed*' -o -name '*_new*' -o -name '*_old*' -o -name '*.bak' \)` → пустой
- **Severity:** blocker
- **Auto-fix:** none (требует ручного решения — какую версию оставить)
- **Error message:** `Найдены файлы с антипаттерн-суффиксами: <list>. Это патч-спираль (§7.8). Сделай rebuild from baseline или удали устаревшие версии.`

### RULE-L1-11: `.claude-plugin/` содержит только манифесты

- **Check:** `ls <plugin_root>/.claude-plugin/` возвращает только из {`plugin.json`, `marketplace.json`}. Любые другие файлы — нарушение.
- **Severity:** blocker
- **Auto-fix:** переместить компоненты на корень плагина
- **Error message:** `В .claude-plugin/ находятся компоненты: <list>. Спецификация Anthropic — там только plugin.json/marketplace.json. Skills/agents/commands/hooks — на уровне корня плагина (§7.5).`

### RULE-L1-12: Компоненты на корне плагина, не вложены

- **Check:** `test -d <plugin_root>/skills` (либо agents/commands/hooks) И NOT `test -d <plugin_root>/.claude-plugin/skills`
- **Severity:** blocker
- **Auto-fix:** `mv .claude-plugin/skills/ skills/` etc.
- **Error message:** `Папка <component>/ должна быть на корне плагина, не внутри .claude-plugin/.`

### RULE-L1-13: Нет hardcoded абсолютных путей

- **Check:** `grep -rE '(/Users/[a-zA-Z][a-zA-Z0-9_.-]+/|/home/[a-zA-Z][a-zA-Z0-9_.-]+/|C:\\\\Users\\\\)' <skill_dir>` → пустой
- **Severity:** blocker
- **Auto-fix:** suggest замену на `${CLAUDE_SKILL_DIR}` / `${CLAUDE_PLUGIN_ROOT}` / relative
- **Error message:** `Найден hardcoded path: '<path>' в <file:line>. Используй переменные ${CLAUDE_SKILL_DIR}, ${CLAUDE_PLUGIN_ROOT} или relative paths (§7.4).`

### RULE-L1-14: Trigger phrases — ≥3 синонима в description

- **Check:** heuristic. В description ищем секцию после «Use when» / «Use this skill when» (case-insensitive). Считаем количество glagol/verb-фраз, разделённых через `,` или `or`. Должно быть ≥3.
- **Severity:** warning
- **Auto-fix:** none (LLM-fix в L3)
- **Error message:** `В description найдено <N> trigger phrases. Рекомендуется ≥3 синонима для покрытия variation (e.g., 'review code, audit changes, check a PR, scan for bugs'). Иначе высокий under-triggering risk (§5.1).`

### RULE-L1-15: Если skill потенциально многозначен — есть negative clause

- **Check:** если в description встречается ≥2 из ключевых терминов из общих доменов (code, test, review, generate, fix, deploy, docs, prompt) — требуем наличие фразы `Do not use` / `Not for` / `Skip if` / `Не используй когда`.
- **Severity:** warning
- **Auto-fix:** none
- **Error message:** `Skill касается широкого домена ('<keywords>') без negative clause. Высокий risk over-triggering. Добавь: "Do not use when <X>" (§5.1).`

---

## Level 2 — Trigger test (dry-run, LLM-driven)

### 2.1 Workflow

1. Распарсить description из frontmatter.
2. Сгенерировать 10 тестовых промтов (5 positive + 5 negative) через LLM по шаблону ниже.
3. Для каждого промта — отдельный LLM-call: «сработал бы skill на этом промте?» (binary).
4. Подсчитать accuracy.
5. Сравнить с порогом, выдать diagnosis.

### 2.2 Шаблон промта — генерация тестовых запросов

```
You are a test generator for a Claude Code skill. Your job is to produce 10 user prompts that probe whether the skill's description triggers correctly.

Skill name: <NAME>
Skill description:
<DESCRIPTION>

Generate exactly 10 prompts, divided into two groups:

POSITIVE (5 prompts): user phrasings that SHOULD trigger this skill. Vary:
  - 1 direct (uses exact terms from description)
  - 1 indirect (synonym or different phrasing for the same job)
  - 1 contextual (user describes a situation that implies this skill, without naming it)
  - 1 elliptical (short, casual: "do X for me")
  - 1 mixed-language or non-canonical phrasing

NEGATIVE (5 prompts): user phrasings that are SIMILAR but should NOT trigger. Aim to expose over-triggering:
  - 1 adjacent domain (close topic but wrong job — e.g., "run tests" if skill is "write tests")
  - 1 opposite intent (asking to undo / disable the thing the skill builds)
  - 1 generic ask that could match many skills ("help me with my code")
  - 1 negation of the skill's job ("don't review, just commit")
  - 1 explicit user override ("skip this skill, just do X")

Output STRICT JSON:
{
  "positives": [
    {"prompt": "...", "category": "direct|indirect|contextual|elliptical|non-canonical", "reason": "<why should trigger>"},
    ...
  ],
  "negatives": [
    {"prompt": "...", "category": "adjacent|opposite|generic|negation|override", "reason": "<why should NOT trigger>"},
    ...
  ]
}
```

### 2.3 Шаблон промта — self-check (срабатывание)

```
You simulate Claude Code's skill routing. Your only job: given a skill's description and a user prompt, decide whether Claude Code would invoke this skill.

Apply Claude Code routing rules:
- A skill triggers when the user's intent matches the "Use when..." trigger phrases (literal or synonym).
- A skill does NOT trigger when negative clauses match, or when intent belongs to an adjacent but distinct job.
- Be strict — Anthropic's default bias is under-triggering. If uncertain, answer "no".

Skill description:
<DESCRIPTION>

User prompt:
<PROMPT>

Answer STRICT JSON, no prose:
{"would_trigger": true|false, "confidence": 0.0-1.0, "reason": "<one sentence>"}
```

Запускается 10 раз (по одному на каждый prompt).

### 2.4 Scoring и threshold

Подсчёт:
- `positives_correct` = число positives где `would_trigger == true`
- `negatives_correct` = число negatives где `would_trigger == false`
- `accuracy = (positives_correct + negatives_correct) / 10`

Пороги:

| accuracy | Verdict | Действие |
|---|---|---|
| ≥0.9 | PASS | Переход к L3 |
| 0.8–0.89 | PASS-with-warnings | Переход к L3, в отчёт — конкретные failed prompts |
| <0.8 | FAIL | Остановиться, отдать diagnosis |

### 2.5 Diagnosis при FAIL

Декомпозиция причин:

| Условие | Диагноз | Конкретное предложение |
|---|---|---|
| `positives_correct < 3` (≤60%) | Description слишком узкое → under-triggering | «Добавь синонимы для trigger phrases. Сейчас не сработали: <failed_positive_prompts>. Расширь "Use when..." покрытием X, Y, Z.» |
| `negatives_correct < 3` (≤60%) | Description слишком широкое → over-triggering | «Добавь negative clause "Do not use when...". Сейчас ложно сработали: <failed_negative_prompts>. Эти зоны нужно явно исключить.» |
| `positives_correct == 5` и `negatives_correct < 3` | Только over-triggering | «Триггерится корректно, но слишком жадно. Сократи общие термины, добавь negative.» |
| `positives_correct < 3` и `negatives_correct == 5` | Только under-triggering | «Не триггерится даже на прямых формулировках. Добавь pushy clause: "Make sure to use this skill whenever..."» |
| Split confidence (LLM uncertain ≥3 раза, `confidence < 0.6`) | Description неоднозначен | «LLM не уверен в маршрутизации. Конкретизируй job через outcome ("Your goal is X"), не через describe ("Helps with X").» |

### 2.6 Variance & cost

- Stochastic — повторный прогон может дать другой результат. Для PASS-with-warnings — opt-in повтор (×3 → median).
- ~5K input + ~3K output токенов на full L2 (1 generation + 10 self-checks).
- Запускать на final draft, не на каждой итерации.

---

## Level 3 — Content audit (антипаттерны §7)

15 проверок. Каждая — что искать в тексте SKILL.md (и references/* если декларированы). Часть детерминистична (regex), часть требует LLM-judgment.

### CHECK-L3-01: No CAPSLOCK MUST/NEVER в body

- **Pattern:** regex `\b(MUST|NEVER|ALWAYS|CRITICAL|FORBIDDEN|IMPORTANT)\b` в теле SKILL.md (после frontmatter)
- **Severity:** suggest (warning если ≥5 совпадений)
- **Fix suggestion:** «Reframe в positive imperative с объяснением reasoning. Вместо "NEVER do X" → "Avoid X because <reason>". Anthropic skill-creator flag это yellow (§5.3, §7.10).»

### CHECK-L3-02: No "Think step by step" cargo-cult

- **Pattern:** grep -i `'think step by step'` или `'let.s think step'` или `'step-by-step thinking'`
- **Severity:** suggest
- **Fix suggestion:** «Удали — это устаревший паттерн для GPT-3.x, для Claude 4.x пустой токен-tax. Если нужна декомпозиция — задай явный workflow секциями.»

### CHECK-L3-03: No карго-роли в опeнинге

- **Pattern:** semantic check. LLM-prompt: «Содержит ли текст карго-роль вида "You are a senior X with Y years of experience" / "As an elite expert in Z" в первых 5 строках body?»
- **Severity:** suggest
- **Fix suggestion:** «Удали роль. Anthropic Opus 4.5 не реагирует на cargo prompts. Замени outcome-first opening: "Your goal is <X>."»

### CHECK-L3-04: Outcome-first opening

- **Pattern:** semantic. Первый параграф body должен начинаться с user-goal-формулировки: «Your goal is...», «You will...», «You help users...». **НЕ** начинаться с «This skill...», «The skill performs...», «I am...».
- **Severity:** warning
- **Fix suggestion:** «Перепиши первый параграф outcome-first (§5.3). Bad: "This skill performs code review...". Good: "Your goal is to identify bugs, security issues, and perf bottlenecks so devs fix them before prod."»

### CHECK-L3-05: No contradictions между правилами

- **Pattern:** LLM-judgment. Промпт: «Найди пары правил в этом SKILL.md которые противоречат друг другу. Например: "Always commit after edit" vs "Never commit without user approval". Выведи список пар с line refs.»
- **Severity:** blocker если найдено ≥1; warning если LLM uncertain
- **Fix suggestion:** «Выстрой явную иерархию приоритета или удали слабейшее правило. Anti-contradiction audit — §5.5.»

### CHECK-L3-06: Description начинается с глагола/существительного-функции

- **Pattern:** semantic + regex. Первое слово description должно быть verb (Reviews, Generates, Analyzes, Audits, Builds, Tests, ...) ИЛИ noun-функцией (Code reviewer that..., Test generator that...). НЕ «I», «This», «The skill», «My».
- **Severity:** warning (дубль RULE-L1-06, но семантически глубже — ловит «A skill that helps with»)
- **Fix suggestion:** «Замени начало на активный глагол. "A skill that helps with code review" → "Reviews code for bugs and security issues."»

### CHECK-L3-07: Third-person tone везде в description

- **Pattern:** LLM tone analysis. Проверка что description не сваливается в second-person посередине ("Use when you want...") — допустимо, но первая половина должна быть third-person о skill'е.
- **Severity:** suggest
- **Fix suggestion:** «Канон Anthropic-плагинов — описывать skill в третьем лице. "Reviews code" not "I review code".»

### CHECK-L3-08: Hardcoded paths в body или references

- **Pattern:** regex `(/Users/[a-zA-Z][a-zA-Z0-9_-]+/|/home/[a-zA-Z][a-zA-Z0-9_-]+/|C:\\Users\\)` — расширение L1-13 на references/*
- **Severity:** blocker
- **Fix suggestion:** «Замени на `${CLAUDE_SKILL_DIR}` / `${CLAUDE_PLUGIN_ROOT}` / relative path.»

### CHECK-L3-09: No "helps with X" generic description

- **Pattern:** LLM-judgment. Промпт: «Является ли description настолько общим, что может описывать ≥5 разных skills? (e.g., "Helps with content creation", "Assists with code")»
- **Severity:** blocker
- **Fix suggestion:** «Description слишком общий — самый частый failure (Alex McFarland, §7.6). Замени job-specific формулировкой: "Extracts content ideas from session transcripts" вместо "helps with content".»

### CHECK-L3-10: Hypothetical edge cases bloat

- **Pattern:** считаем параграфы в body начинающиеся с «If X happens...», «In case of Y...», «When the user does Z...». Если >3 — flag.
- **Severity:** suggest
- **Fix suggestion:** «<N> hypothetical edge cases в body — антипаттерн §7.7. Вынеси в `references/edge-cases.md` и сошлись одной строкой. Body должен покрывать happy path + 1–2 ключевых развилки.»

### CHECK-L3-11: Tools cross-check (упоминание ↔ allowed-tools)

- **Pattern:** найти в body упоминания tools (`Read`, `Bash`, `WebFetch`, `mcp__...`). Сверить с `allowed-tools:` во frontmatter. Любой mentioned-but-not-allowed → flag.
- **Severity:** blocker
- **Fix suggestion:** «Body использует tool '<X>' но он не в allowed-tools. Добавь во frontmatter или убери упоминание.»

### CHECK-L3-12: Stop-хуки с `stop_hook_active` check (если хуки декларированы)

- **Pattern:** если у плагина есть hooks, найти все `Stop` hooks. В их скрипте должна быть проверка `stop_hook_active` (e.g., `if [ "$stop_hook_active" = "true" ]; then exit 0; fi` или эквивалент в python/JSON output)
- **Severity:** blocker
- **Fix suggestion:** «Stop-hook без stop_hook_active → infinite loop (§6.2, §7.15). Добавь early-exit: если флаг `true` — exit 0 без re-trigger.»

### CHECK-L3-13: No curl/wget в SessionStart hooks

- **Pattern:** в hooks/*.json или hooks/*.sh найти SessionStart matchers. В их command — regex `\b(curl|wget|http\s+GET|fetch\s+https?)\b`. Любое совпадение — blocker.
- **Severity:** blocker (CVE-уровень)
- **Fix suggestion:** «curl/wget в SessionStart запрещён (§6.2, §7.14, CVE-уровень). Anthropic явно запрещает external network в SessionStart. Перенеси в on-demand command или используй cached local artifact.»

### CHECK-L3-14: References declared but not loaded

- **Pattern:** в body grep на упоминания `references/<file>.md` (regex `references/[a-zA-Z0-9_-]+\.md`). Для каждого — `test -f <skill_dir>/<path>`. Missing → flag.
- **Severity:** blocker
- **Fix suggestion:** «Body ссылается на `references/<X>.md` но файла нет. Создай файл или удали ссылку.»

### CHECK-L3-15: References лежат, но в body на них нет ссылок (orphan refs)

- **Pattern:** для каждого файла в `references/` — `grep -rn "<filename>" SKILL.md`. Если 0 совпадений — orphan.
- **Severity:** suggest
- **Fix suggestion:** «`references/<X>.md` существует, но в SKILL.md нет ссылок на него — Claude не загрузит. Добавь в body: "For X, see references/<X>.md" или удали файл.»

---

## Итоговый scoring

Каждый level возвращает свой verdict; общий verdict — самый строгий из трёх.

### Per-level verdicts

| Level | PASS | PASS-with-warnings | FAIL |
|---|---|---|---|
| L1 | 0 blockers, 0 warnings | 0 blockers, ≥1 warning | ≥1 blocker |
| L2 | accuracy ≥0.9 | 0.8 ≤ accuracy < 0.9 | accuracy <0.8 |
| L3 | 0 blockers, ≤2 warnings, suggest допустимы | 0 blockers, 3–5 warnings | ≥1 blocker ИЛИ ≥6 warnings |

### Aggregate verdict (lattice)

```
FAIL                       — если любой level вернул FAIL
PASS-with-warnings         — если все ≥PASS-with-warnings и хотя бы один PASS-with-warnings
PASS                       — если все три PASS
```

### Действия по verdict

- **PASS** → ship. Можно `claude plugin validate .` и публиковать.
- **PASS-with-warnings** → ship опционально. Отчёт показывает что улучшить в v1.1.
- **FAIL** → блок. Pluginmaker возвращает контроль user'у с конкретным fix-листом. Re-run только после правок.

---

## Output format — JSON-отчёт валидации

Все три агента пишут в один файл `validation-report.json` (overwrite разрешён — это не historical report, а текущий снапшот):

```json
{
  "schema_version": "1.0",
  "skill_name": "<name from frontmatter>",
  "skill_path": "<absolute path to SKILL.md>",
  "timestamp": "2026-05-16T14:30:00Z",
  "aggregate_verdict": "PASS | PASS-with-warnings | FAIL",
  "levels": {
    "L1_lint": {
      "verdict": "PASS | PASS-with-warnings | FAIL",
      "duration_ms": 420,
      "rules_checked": 15,
      "violations": [
        {
          "rule_id": "RULE-L1-04",
          "rule_name": "description length 80–1024",
          "severity": "blocker",
          "location": "SKILL.md frontmatter",
          "details": "description = 1247 chars, exceeds 1024",
          "auto_fix_available": false,
          "error_message": "..."
        }
      ]
    },
    "L2_trigger_test": {
      "verdict": "PASS | PASS-with-warnings | FAIL | SKIPPED",
      "duration_ms": 28400,
      "tokens_used": {"input": 4820, "output": 2910},
      "accuracy": 0.7,
      "positives_correct": 3,
      "negatives_correct": 4,
      "diagnosis": "under-triggering: description слишком узкое",
      "failed_prompts": [
        {"prompt": "...", "expected": true, "actual": false, "category": "indirect", "llm_reason": "..."}
      ],
      "fix_suggestions": [
        "Добавь синонимы X, Y, Z в trigger phrases"
      ]
    },
    "L3_content_audit": {
      "verdict": "PASS | PASS-with-warnings | FAIL | SKIPPED",
      "duration_ms": 54200,
      "tokens_used": {"input": 9300, "output": 4100},
      "checks_run": 15,
      "violations": [
        {
          "check_id": "CHECK-L3-01",
          "check_name": "No CAPSLOCK MUST/NEVER",
          "severity": "suggest",
          "location": "SKILL.md:42, :58, :91",
          "matches_count": 7,
          "details": "Found 7 CAPSLOCK directives in body",
          "fix_suggestion": "Reframe to positive imperative with reasoning"
        }
      ]
    }
  },
  "summary": {
    "total_blockers": 1,
    "total_warnings": 3,
    "total_suggests": 5,
    "next_action": "FIX_BLOCKERS | REVIEW_WARNINGS | SHIP",
    "blocker_summary": ["RULE-L1-04: description too long"]
  }
}
```

### Производные текстовые форматы

Помимо JSON, агенты пишут human-readable summary в `validation-report.md` для прямого чтения user'ом. Формат:

```markdown
# Validation Report — <skill-name>

**Verdict:** ❌ FAIL / ⚠️ PASS-with-warnings / ✅ PASS

## Blockers (must fix)
- [RULE-L1-04] description = 1247 chars, exceeds 1024 → ...

## Warnings (should fix)
- [CHECK-L3-04] Body не outcome-first → ...

## Suggestions (nice to have)
- [CHECK-L3-01] 7× CAPSLOCK MUST → reframe ...

## Trigger test (L2)
- Accuracy: 70% (FAIL, threshold 80%)
- Under-triggering detected: 2 indirect prompts not matched
- Fix: расширь синонимы X, Y, Z

## Next steps
1. Fix blockers
2. Re-run validation
3. If PASS — `claude plugin validate .` → publish
```

---

## Operational notes для агентов

- **Линтер (L1)** работает локально через bash/jq/python yaml — никакого LLM-вызова. Должен быть детерминистичным и быстрым. Если skill валиден — выход < 2 сек.
- **Триггер-тестер (L2)** делает 1 LLM-call для генерации промтов и 10 LLM-call'ов для self-check. Промты должны быть детерминистичны (temperature=0 при генерации, чтобы повторный прогон давал тот же результат на том же description).
- **Аудитор качества (L3)** делает один большой LLM-call со всем SKILL.md + промтом со списком всех 15 CHECK-L3-XX правил, просит вернуть JSON-массив violations. Так дешевле чем 15 отдельных вызовов.
- **Re-run policy:** validation-report.json **перезаписывается** при каждом прогоне (это снапшот, не история). Если нужна история — повышение версии skill'а через `version: X.Y.Z` создаст новую папку.
- **Cost budget:** полный прогон L1+L2+L3 — ~15K input + ~7K output токенов + ~90 секунд. Если pluginmaker генерирует n итераций — запускать L2/L3 только на финальном кандидате, L1 на каждой.

---

**Источники:**
- Внутренний гайд `guide.md` (Claude Code Plugins Building Guide 2026) §5, §6, §7, §12 — не входит в поставку
- Anthropic skill-creator (Tier 1) — baseline-build-refine loop
- Trail of Bits `testing-handbook-generator` — `validate-skills.py` паттерн
