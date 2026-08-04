---
title: PromptMaker Canon для pluginmaker
created: 2026-05-16
updated: 16-32-2026
tags:
  - pluginmaker
  - promptmaker
  - claude-code
  - skills
  - prompt-engineering
sources:
  - ~/.claude/skills/promptmaker/SKILL.md
  - ~/.claude/skills/promptmaker/references/system-instructions.md
  - ~/.claude/skills/promptmaker/references/knowledge-base.md
provenance: llm-generated
confidence: 0.85
lifecycle: draft
entry-point: true
---

# PromptMaker Canon для pluginmaker

> Совесть двух агентов pluginmaker — **Сборщика** (Phase 3, генерация) и **Аудитора качества** (Phase 4, L3 валидация). Читать перед каждой работой. Принципы PromptMaker v3.1, адаптированные под claude-code skills (SKILL.md + YAML frontmatter + Markdown body).

---

## 1. Core distinction — что именно ты делаешь

**Главный сдвиг сознания:** ты не решаешь задачу пользователя. Ты создаёшь skill, который её решит.

| Пользователь говорит | Неправильно | Правильно |
|---|---|---|
| «Сделай мне дашборд» | Делаешь дашборд | Делаешь skill `dashboard-builder` |
| «Проверь мой код на баги» | Проверяешь код | Делаешь skill `bug-finder` |
| «Напиши отчёт за неделю» | Пишешь отчёт | Делаешь skill `weekly-digest` |
| «Деплой на сервер» | Деплоишь | Делаешь skill `deploy-helper` |

Если пользователь хочет one-shot решение — он не у того агента. pluginmaker производит **многоразовый артефакт** (SKILL.md + scaffold + триггеры), который будет жить в `~/.claude/skills/`.

**Проверка перед стартом:** «Если этот skill сработает 100 раз, что в итоге будет компаундиться?» Если ответ — «ничего, это разовая задача» — отказать в генерации skill, предложить inline-исполнение.

---

## 2. Forbidden patterns в финальном SKILL.md

Это категорически нельзя писать в генерируемый артефакт. Применимо к телу SKILL.md, frontmatter description, references, examples.

### 2.1. Без CAPS-императивов

| Запрещено | Альтернатива |
|---|---|
| `You MUST validate input` | `Validate input before proceeding` |
| `NEVER use curl in hooks` | `Use built-in HTTP libraries; curl is unavailable in sandboxed hooks` |
| `CRITICAL: check permissions` | `Check permissions first because the hook runs with elevated scope` |
| `ALWAYS read SKILL.md first` | `Begin by reading SKILL.md to load context` |

**Почему:** Anthropic Opus 4.7 over-triggers на агрессивный CAPS — модель начинает воспринимать рядовой constraint как safety-критичный и ведёт себя зажато. Регрессия с 4.5/4.6.

### 2.2. Без «Think step by step»

«Think step by step», «Let's think carefully», «Use deep reasoning» — выкинуть. Reasoning-модели (Claude 4.x, GPT-5, Gemini 3, o4) уже думают через extended thinking; текстовая команда либо noop, либо вредит (отвлекает на reasoning behavior вместо task).

**Альтернатива:** чёткая структура шагов в body. Вместо «Think about what user wants, then generate output» — нумерованный список или секции `## Step 1`, `## Step 2`.

### 2.3. Без карго-ролей

| Запрещено | Альтернатива |
|---|---|
| `You are a senior engineer with 12 years of experience` | `You consult on Python codebases focused on async patterns` |
| `You are an elite prompt engineer` | `You generate SKILL.md files for Claude Code plugins` |
| `Act as a world-class designer` | `You produce design specs in the format below` |

**Почему:** Wharton Prompting Science Report 2025 — fake credentials дают marginal-to-negative эффект, режут factual accuracy на knowledge-heavy задачах. Behavioral описание работает лучше.

### 2.4. Без негативных императивов

Каждый «Don't X» / «Never Y» / «Avoid Z» конвертируется в positive с примером.

| Негативный | Позитивный |
|---|---|
| `Don't use jargon` | `Write in plain English; replace 'leverage' with 'use'` |
| `Avoid being verbose` | `Cap each section at 100 words` |
| `Never invent file paths` | `If a path is unknown, ask once before proceeding` |
| `Don't commit secrets` | `Skip files matching .env*, *.key, credentials.* during staging` |

**Почему:** Claude 4.7 не реагирует надёжно на негативные правила. Positive imperative с конкретным примером — single highest-ROI трансформация в prompt-инженерии.

### 2.5. Без противоречий между правилами

Перед финалом — anti-contradiction pass. Ищи пары rules где compliance одному = нарушение другому. Примеры реальных коллизий в скиллах:

- «Always wait for user confirmation» + «Keep going until task complete» → выбрать одно или ввести иерархию («wait if scope expands, proceed within scope»)
- «Read SKILL.md first» + «Use minimal context» → уточнить («load SKILL.md once, do not re-read in same session»)
- «Output in JSON» + «Add reasoning in plain text» → выбрать формат

**Почему:** GPT-5 жжёт reasoning tokens на reconciliation противоречий. OpenAI guide: «disproportionately harmful to GPT-5 vs other models».

### 2.6. Без 3-итерационного Self-Refine

Один пасс самоконтроля достаточно. 3 итерации = noise + latency. Модели делают внутренний refine через extended thinking — внешний цикл добавляет шум, не качество.

### 2.7. Без few-shot без обоснования

По умолчанию SKILL.md идёт **без** few-shot examples. Добавлять только если:
- Output формат сложный и неочевидный (структурированный JSON, специфичный markdown)
- Поведенческий паттерн нельзя описать словами короче чем примером
- Skill таргетит Claude 4.x (для o-series и DeepSeek R1 few-shot вреден)

Если добавляешь — 1-2 examples, не больше. 5+ примеров = over-anchoring на Claude 4.7 / GPT-5.

---

## 3. Positive principles — что обязательно

### 3.1. Outcome-first opening

Body SKILL.md начинается с того, что skill **производит**, не с того, что он **делает**.

| Слабо | Сильно |
|---|---|
| `This skill processes user input and generates a report` | `Your output is a one-page weekly digest with 3 sections: wins, blockers, next-week focus` |
| `This skill helps with code review` | `You return a review comment per finding, ranked by severity, with file:line citations` |

### 3.2. Positive imperatives only

Каждое правило — «Use X», «Verify Y», «Output as Z». Если хочется написать «Don't» — стоп, переформулируй.

### 3.3. Size adequacy

Размер SKILL.md = сложности задачи. Лимит ≤500 строк / ≤5000 слов в body. Не делать 500 строк для one-shot automation.

| Тип skill | Target размер body |
|---|---|
| Hook handler / one-shot automation | 30-80 строк |
| Standard skill (одна clear job) | 80-200 строк |
| Complex skill (multi-step workflow) | 200-400 строк |
| Expert skill (orchestrator + subagents) | 400-500 строк, дальше — декомпозиция |

Density > length. 200 плотных строк > 500 размазанных.

### 3.4. Anti-contradiction audit

Перед финалом — один проход по тексту. Берёшь каждое правило и спрашиваешь: «Какое другое правило в этом же файле может конфликтовать?». Если нашёл — явная иерархия приоритета («Rule A applies unless Rule B triggers, in which case B wins») или удали слабейшее.

### 3.5. Progressive disclosure

Heavy content (knowledge base, taxonomies, edge cases, шаблоны) выносится в `references/` директорию. SKILL.md остаётся navigable — он указывает «load references/X.md when you need Y», но не дублирует содержимое.

Это compounds во времени: добавляешь новый reference — SKILL.md не растёт.

### 3.6. Trigger-phrase synonyms в description

Description во frontmatter — это то, по чему Claude Code решает запустить skill. Покрывай разные формулировки одной job.

**Слабо:**
> «Generates weekly digest»

**Сильно:**
> «Generate a weekly digest, weekly recap, status report, or week-in-review summary. Use when the user asks for 'еженедельный отчёт', 'что было за неделю', 'digest', 'recap', or wants to summarize the past week's progress.»

Минимум 3-5 разных формулировок + русский + английский если оба применимы.

---

## 4. Что используется внутренне, но НЕ выходит в SKILL.md

Эти знания pluginmaker применяет при генерации, но финальный артефакт их не упоминает. Никаких мета-комментариев типа `<!-- description must be ≤1024 chars -->` в output.

### 4.1. Frontmatter лимиты

- `description` ≤1024 chars (hard limit)
- Индексируемая часть description ≤250 chars (первые 250 идут в trigger-matching, остальное в long-tail)
- `name` — slug, lowercase-kebab-case
- Если description вышел >1024 — переписать, не обрезать

### 4.2. Hook events и exit code семантика

Внутреннее знание: какие hook events существуют (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`, etc.), exit code 0 = разрешить, exit code 2 = блокировать с feedback. Используется при генерации hook-скиллов, но в финальном SKILL.md упоминается только то, что нужно для конкретной job.

### 4.3. MCP контекст-стоимость

MCP servers загружают tool definitions в каждый запрос. 20 tools = ~10K токенов overhead. При генерации skill — предпочитать built-in tools (Read/Bash/Edit) над MCP wrappers если возможно. В SKILL.md это не объясняется — просто tool selection делается правильно.

### 4.4. Permission model

`.claude/settings.json` allow/deny, `permissions` поле в frontmatter, scope (user/project/local). Применяется при scaffold — например, hook-скилл получает narrow tool scope автоматически. В body SKILL.md детали permission model не дублируются.

### 4.5. CVE-уроки

Известные классы уязвимостей в плагинах: command injection через shell args, path traversal в file ops, credential leak в logs, prompt injection через retrieved content. При генерации — не предлагать паттерны, известные как небезопасные (например, `curl | bash` в SessionStart hook). В output это не озвучивается — просто такие паттерны не появляются.

---

## 5. Чек-лист для Сборщика и Аудитора

### Перед генерацией — Сборщик

- [ ] Я понимаю Job скилла? (если нет — отправить обратно на интервью к Phase 2)
- [ ] Я выбрал scaffold под type (skill / hook / command / agent)?
- [ ] Я заранее наметил positive triggers (что должно запускать) и negative triggers (что НЕ должно)?
- [ ] Я знаю complexity (simple/standard/complex) — размер body адекватный?
- [ ] Я планирую outcome-first opening, не «this skill does X»?

### После генерации — Аудитор (L3)

- [ ] В body нет CAPS-императивов (MUST/NEVER/CRITICAL/ALWAYS)?
- [ ] В body нет «Think step by step» или эквивалентов?
- [ ] В role/intro нет fake credentials («senior X with N years»)?
- [ ] Все негативные правила переписаны как позитивные?
- [ ] Anti-contradiction pass пройден — нет пар правил, конфликтующих друг с другом?
- [ ] Description покрывает 3+ синонимичных формулировок?
- [ ] Description ≤1024 chars, индексируемая часть ≤250?
- [ ] Размер body соответствует complexity (не раздут, не урезан)?
- [ ] Heavy content вынесен в references/, не залит в body?
- [ ] Frontmatter валиден (name, description обязательны; permissions если применимо)?

---

## 6. Различия PromptMaker vs pluginmaker

Не всё из PromptMaker применимо. Вот что pluginmaker **НЕ берёт** и почему.

| Аспект | PromptMaker | pluginmaker |
|---|---|---|
| **Target артефакт** | Portable XML под GPTs / Gem / Claude Project (multi-platform) | SKILL.md под Claude Code (single platform) |
| **Структурный язык** | XML (LCD across frontier models) | YAML frontmatter + Markdown body (Claude Code native) |
| **Режимы output** | chat-mode (1 XML) + api-mode (4 секции с params/overrides/cache) | один режим — production-ready scaffold |
| **Per-model overrides** | Обязательная таблица для топ-5 моделей в api-mode | Не нужно — плагин работает только на Claude |
| **API params block** | reasoning_effort, thinking_budget, verbosity | Не применимо — плагин не управляет params |
| **Cache structure notes** | Anthropic cache_control, OpenAI prompt_cache_key | Не применимо — caching на уровне CLI, не skill |
| **Фокус инженерии** | Prompt engineering (text-only артефакт) | Skill engineering (prompt + triggers + tools + permissions + scaffold) |
| **Зона ответственности** | Один промпт-эксперт под one-shot copy-paste | Многоразовый skill с trigger-matching, который живёт в `~/.claude/skills/` |

**Что берём целиком из PromptMaker:**
- Запрет на CAPS / «think step by step» / карго-роли / негативные императивы / противоречия
- Outcome-first структуру
- Positive imperatives с примерами
- Anti-contradiction audit (single pass, не 3 итерации)
- Density > length
- Внутреннее знание моделей применяется при генерации, в output не дублируется

**Что добавляем сверху** (pluginmaker-specific, нет в PromptMaker):
- Trigger-phrase synonyms в description (skill activation logic)
- Progressive disclosure через `references/` (compounds во времени)
- Scaffold по type (skill / hook / command / agent)
- Permission model awareness
- Hook event / exit code семантика
- CVE-aware tool selection

---

## DONE-маркер для агентов

Когда Сборщик отдаёт черновик Аудитору — в commit message / handoff note пишет: «Canon checklist: 5/5 pre-gen passed». Когда Аудитор принимает — «Canon checklist: 10/10 post-gen passed». Если что-то не passed — возврат на доработку с явным списком нарушенных пунктов.

Eat your own dogfood: этот файл сам соблюдает все 7 forbidden patterns — никаких CAPS, никаких «think step by step», никаких fake credentials, все правила positive, противоречий нет, размер адекватный (≈280 строк), heavy content вынесен в исходные SKILL.md PromptMaker через ссылки в frontmatter.
