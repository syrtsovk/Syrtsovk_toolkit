---
title: "Scaffolds: 6 production-ready SKILL.md шаблонов для pluginmaker"
created: 2026-05-16
updated: 16-32-2026
tags:
  - pluginmaker
  - scaffold
  - skill
  - claude-code
  - reference
sources:
  - internal design guide (не входит в поставку)
  - ~/.claude/skills/promptmaker/SKILL.md
provenance: llm-generated
confidence: 0.88
lifecycle: draft
entry-point: true
---

# Scaffolds — 6 production-ready шаблонов SKILL.md

Этот файл — операционная библиотека `pluginmaker/v1`. После того как Interview-агент определил **тип скилла** через Q1 + профилирование Q2 (см. `guide.md §13.2`), Сборщик-агент берёт соответствующий шаблон ниже, подставляет placeholder'ы и пропускает через `validation pipeline` (`guide.md §13.4`).

Все шаблоны соответствуют:
- `guide.md §2.1` — frontmatter спека для Skills.
- `guide.md §5.1` — description engineering (третье лицо, ≤1024 chars, pushy, синонимы триггеров, negative clause).
- `guide.md §5.2` — progressive disclosure (≤500 строк SKILL.md, references/ для тяжёлого).
- `guide.md §5.3` — outcome-first opening, positive imperatives, без CAPS MUST.
- `~/.claude/skills/promptmaker/SKILL.md` — анти-противоречия, positive framing, объяснение «почему» вместо запретов.

---

## Decision helper — какой scaffold брать

Сборщик-агент использует эту таблицу как первый шаг. Колонка «когда» = критерии из Interview Q1-Q3. Колонка «следы» = что должен дать ответ пользователя, чтобы выбор был очевиден.

| # | Scaffold | Job (что нанимают делать) | Когда брать | Следы в интервью | Tier complexity |
|---|---|---|---|---|---|
| 1 | `research-agent` | Глубокое исследование темы → синтез с цитатами | Нужно сравнить варианты, изучить конкурентов, собрать SOTA | «исследуй», «найди что есть по теме», «сравни N подходов», «deep dive» | medium |
| 2 | `code-reviewer` | Прочитать diff/файлы → найти баги/security/style | Audit PR, прохождение по коду, security review | «проверь код», «найди баги», «audit PR», «security review» | medium |
| 3 | `workflow-orchestrator` | Многофазный процесс с состоянием | Setup-протоколы, multi-step генераторы, миграции | «проведи через шаги», «сначала спроси, потом сделай», «фаза 1, фаза 2» | high |
| 4 | `doc-generator` | По коду/API сгенерировать docs по шаблону | JSDoc/TSDoc, README, API reference, changelog | «напиши доку», «сгенерируй README», «JSDoc для функции» | low-medium |
| 5 | `knowledge-curator` | Поиск в локальной базе → ответ с attribution | Vault queries, RAG-стиль, FAQ-боты по корпоративной базе | «найди в моих заметках», «что я писал про X», «спроси нашу вики» | medium |
| 6 | `simple-automation` | Один триггер → одно действие | Form-filler, file-renamer, quick formatter | «когда вижу X — сделай Y», «один раз пройдись и…» | low |

**Правило выбора:** если интервью даёт неоднозначные следы — Сборщик-агент задаёт уточняющий Q «вам нужен **многошаговый процесс с состоянием** или **разовое действие**?». State → 3 или 1, no-state → 6 или 4.

---

# Scaffold 1 — research-agent

## Когда подходит

Скилл выполняет многоступенчатое исследование: разворачивает запрос в подзадачи, собирает источники (web/local), синтезирует ответ с **обязательной атрибуцией**. Подходит когда пользователь нанимает Claude вместо ручного googling + чтения 20 вкладок. Антипаттерн использования: разовый factual lookup (туда — `simple-automation`).

## YAML frontmatter

```yaml
---
name: {{name}}                                  # kebab-case, ≤40 chars; пример: deep-research, competitor-scan
description: |                                  # ≤1024 chars; третье лицо; pushy; синонимы + negative clause
  {{one-line-what}}. Use this skill whenever the user asks to
  {{trigger-verb-1}}, {{trigger-verb-2}}, {{trigger-verb-3}},
  {{trigger-verb-4}}, or mentions {{domain-keyword-1}},
  {{domain-keyword-2}}, {{domain-keyword-3}}. The skill produces
  a synthesis with explicit source citations for every claim.
  Do not use for quick factual lookups that fit in a single
  search query, or for tasks that require writing or modifying
  code.
allowed-tools: {{allowed-tools}}                # см. рекомендацию ниже
model: sonnet                                   # research выигрывает от sonnet/opus; haiku теряет nuance
effort: high                                    # многошаговый, нужен бюджет на reasoning
argument-hint: "[topic or question]"            # пример: "[topic-or-question]"
# disable-model-invocation: omit                # хотим auto-invoke
# user-invocable: omit                          # доступен из меню /skills
---
```

## Skeleton body

```markdown
# {{Title-Case-Name}}

Your goal is to produce a {{deliverable: "structured research brief" | "comparison matrix" | "competitive landscape"}} that the user can act on within {{time-budget: "10 minutes of reading"}}. Every claim links back to a concrete source so the user can verify and dig deeper.

## When this skill is the right fit

Use it when the user wants to:
- {{trigger-1: "compare three or more approaches"}}
- {{trigger-2: "understand the state of the art in <area>"}}
- {{trigger-3: "scout competitors before a strategic decision"}}
- {{trigger-4: "go from a vague question to a defensible answer"}}

Stay out of the way when the task is a one-shot factual lookup or pure code work — there are better tools for those.

## Workflow

### Phase 1 — Frame the question
1. Restate the user's question in one sentence.
2. List 3-5 sub-questions that, taken together, answer the main one.
3. Decide the minimum source diversity (e.g. 2 primary, 3 secondary).

### Phase 2 — Gather
For each sub-question, run targeted searches (web, local docs, vault). Capture per source: `url | one-line summary | the claim it supports`.

### Phase 3 — Synthesise
Group findings by sub-question. For each, write a 2-4 sentence answer with inline citations `[source-N]`. Mark contradictions explicitly — they are more valuable than smoothed-over consensus.

### Phase 4 — Deliver
Produce the brief in this order: TL;DR (5 lines) → answer per sub-question → contradictions/open questions → full source list.

## Quality bar
- Every non-obvious claim has a citation.
- Contradictions surface in their own section, not buried.
- If fewer than {{min-sources: 3}} sources support the synthesis, the brief says so explicitly.

## References (lazy-loaded)
- `references/search-strategies.md` — how to phrase queries by domain
- `references/citation-format.md` — exact citation style for this skill
```

## Positive trigger phrases (для description)

1. «исследуй тему X»
2. «сравни подходы / решения / библиотеки»
3. «что есть на рынке по X»
4. «scout конкурентов»
5. «deep dive в X»

## Negative triggers (что НЕ должно срабатывать)

1. «какая столица Франции» — разовый factual lookup → не нужен multi-phase.
2. «напиши код для X» — это `code-generator`, не research.
3. «найди в моих заметках про X» — это `knowledge-curator`, vault-specific.

## Рекомендуемый `allowed-tools`

```yaml
allowed-tools: Read, Glob, Grep, WebFetch, WebSearch, Bash
```
- `WebFetch` + `WebSearch` — обязательны для external research.
- `Bash` — для `gh search`, `curl`, локального ripgrep по большим папкам.
- `Edit/Write` **не** даём — research-агент пишет финальный output в чат, а не в файлы (если нужно writing — отдельная фаза).

## References / scripts — когда нужны

- `references/search-strategies.md` — обязательна, если домен специфичный (academic / patents / TG-каналы).
- `scripts/dedupe-sources.py` — опционально, если ожидается >30 источников за один прогон.

---

# Scaffold 2 — code-reviewer

## Когда подходит

Скилл анализирует **diff** или конкретные файлы и возвращает структурированный отчёт по категориям severity. Подходит для PR-аудита, pre-commit gate, security review. Антипаттерн: «напиши тесты» (это generator, не reviewer) и «почини баг» (это fixer).

## YAML frontmatter

```yaml
---
name: {{name}}                                  # пример: pr-review, security-audit, lint-on-steroids
description: |                                  # ≤1024 chars; третье лицо; pushy; синонимы + negative clause
  Reviews {{review-scope: "diff and changed files" | "the whole repo"}}
  for bugs, security vulnerabilities, performance regressions,
  and style violations. Use whenever the user asks to review
  code, check a PR, audit changes, scan for bugs, look for
  security issues, or mentions code review of any kind. Returns
  findings grouped by severity (blocker / major / minor / nit).
  Do not use to run existing tests, fix failing tests, or
  generate new code — this skill only reports, it does not edit.
allowed-tools: {{allowed-tools}}
model: sonnet                                   # достаточный для большинства repos
effort: medium
argument-hint: "[path-or-branch]"               # пример: HEAD~1 или src/api/
---
```

## Skeleton body

```markdown
# {{Title-Case-Name}}

Your goal is to give the developer a review they trust enough to merge or reject within {{decision-budget: "5 minutes"}}. Severity is honest — a nit is a nit, a blocker is a blocker — so the developer never wastes attention on the wrong thing.

## When this skill fires
- User asks to review {{scope: "a PR / diff / file / branch"}}.
- User mentions code review, audit, security scan, or pre-merge check.
- User wants a second opinion before pushing.

The skill stays silent for: running tests, fixing tests, generating code, refactoring proposals beyond review scope.

## Workflow

### Phase 1 — Scope the review
1. Detect the diff: `git diff {{base-ref: "main"}}...HEAD` or explicit paths from `$ARGUMENTS`.
2. Build the file list. If >{{file-limit: 40}} files, ask the user to narrow scope.
3. Read each changed file fully, not just the hunk — context matters.

### Phase 2 — Categorised findings

For every issue, attach one severity tag:

| Severity | Definition | Examples |
|---|---|---|
| **blocker** | Ship breaks production, security CVE, data loss | SQL injection, missing auth check, race condition on money |
| **major** | High chance of bug, perf regression, broken contract | N+1 query, swallowed exception, public API break |
| **minor** | Smell, fragile code, weak naming | Magic number, deeply nested if, inconsistent style |
| **nit** | Subjective, style, optional | Comment polish, import ordering |

For each finding produce:
```
[severity] path:line — title
  what:  one line
  why:   one line — why it matters
  fix:   one line — concrete suggestion
```

### Phase 3 — Summary block
- Counts per severity.
- Top-3 must-fix.
- One-line verdict: `ship / fix-then-ship / hold`.

## Quality bar
- No finding without `fix:` line — review without suggestions is noise.
- Severity calibrated against the project (not "everything is major").
- If diff is clean, the report says so in one line, no padding.

## References (lazy-loaded)
- `references/severity-rubric.md` — per-language calibration
- `references/security-checklist.md` — OWASP-style triggers
```

## Positive trigger phrases

1. «review my PR»
2. «найди баги в этих файлах»
3. «security audit этого модуля»
4. «scan for vulnerabilities»
5. «check changes before I merge»

## Negative triggers

1. «напиши тесты для этого» — не review, это test-generator.
2. «исправь баги» — review только репортит, не правит (если нужно править → отдельный skill).
3. «отрефактори файл» — refactoring выходит за scope review.

## Рекомендуемый `allowed-tools`

```yaml
allowed-tools: Read, Glob, Grep, Bash
```
- `Bash` — для `git diff`, `git log`, `gh pr view`.
- `Edit/Write` **не выдаём** — это критическая граница для review-only скиллов (см. `guide.md §5.4`).

## References / scripts

- `references/severity-rubric.md` — обязательна, иначе severity «плавает» от прогона к прогону.
- `references/security-checklist.md` — рекомендуется, если в Q3 user сказал «security важен».
- `scripts/collect-diff.sh` — опционально для нетривиальных diff-стратегий (worktree, stacked PRs).

---

# Scaffold 3 — workflow-orchestrator

## Когда подходит

Скилл ведёт пользователя через несколько фаз (обычно 3-7) с явным state между ними: interview → plan → execute → validate. Это паттерн `skill-creator`, `setup-docs`, `team-feature`. Антипаттерн: один шаг без зависимостей (`simple-automation`).

## YAML frontmatter

```yaml
---
name: {{name}}                                  # пример: setup-docs, migrate-to-vN, onboard-newbie
description: |                                  # ≤1024 chars
  Drives {{outcome: "a multi-phase X process"}} from start to
  finish: gathers context, proposes a plan, executes step by
  step, and validates the result. Use whenever the user asks
  to {{trigger-1}}, {{trigger-2}}, {{trigger-3}}, set up
  {{noun}}, migrate {{noun}}, or run the full {{noun}}
  workflow. The skill keeps state across phases and never
  jumps ahead without explicit confirmation. Do not use for
  single-step tasks or quick fixes — pick a simpler skill
  for those.
allowed-tools: {{allowed-tools}}
model: sonnet                                   # opus если фазы требуют сложного reasoning
effort: high
argument-hint: "[target-or-scope]"
context: fork                                   # рекомендуется: изоляция state-машины
---
```

## Skeleton body

```markdown
# {{Title-Case-Name}}

Your goal is to bring the user from {{start-state}} to {{end-state}} without losing their context between phases. The state machine is explicit: the user always knows which phase they are in and what the next gate is.

## State machine

```
[P0: Idle] → [P1: Discover] → [P2: Plan] → [P3: Execute] → [P4: Verify] → [P5: Done]
                  ↑                            ↓
                  └─── (re-discover on fail) ──┘
```

Each transition needs a clear signal from the user or from a deterministic check.

## Phase contracts

### P1 — Discover
- **Input:** user request, repo context.
- **Output:** `discovery.md` with `stack`, `constraints`, `existing-artefacts`.
- **Gate to P2:** user confirms the discovery is accurate.

### P2 — Plan
- **Input:** `discovery.md`.
- **Output:** numbered plan with risks, rollback points.
- **Gate to P3:** explicit "go" from user. No silent transitions.

### P3 — Execute
- **Input:** plan.
- **Output:** changes on disk, log of every step.
- **Gate to P4:** all steps marked done.

### P4 — Verify
- **Input:** plan + execution log.
- **Output:** verification report (each step → passed/failed/skipped + evidence).
- **Gate to P5:** verification clean OR user accepts known gaps.

### P5 — Done
- Print final summary, point to next-steps doc, close state.

## State persistence

Persist state to `${CLAUDE_PLUGIN_DATA}/{{name}}/state-${CLAUDE_SESSION_ID}.json` so the user can resume after a crash. Shape:
```json
{ "phase": "P3", "plan_id": "...", "completed_steps": [1,2,3], "started_at": "..." }
```

## Quality bar
- No phase skipped silently.
- Every gate has a visible prompt — user sees what they are confirming.
- State file is the single source of truth, not chat history.

## References (lazy-loaded)
- `references/phase-templates.md` — body templates per phase
- `references/recovery-playbook.md` — what to do if a phase fails mid-way
```

## Positive trigger phrases

1. «set up X в проекте»
2. «migrate с vN на vM»
3. «проведи меня через X-процесс»
4. «onboard меня в этот repo»
5. «давай сделаем X пошагово»

## Negative triggers

1. «быстрый фикс» — один шаг → `simple-automation`.
2. «просто посмотри код» — read-only → `code-reviewer`.
3. «найди ответ на вопрос» — research → `research-agent`.

## Рекомендуемый `allowed-tools`

```yaml
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
```
- Полный set, потому что orchestrator может затрагивать любую фазу.
- Если в Q3 user сказал «никаких внешних вызовов» — убрать `WebFetch`/`WebSearch`.

## References / scripts

- `references/phase-templates.md` — **обязательна**, иначе фазы расплываются.
- `references/recovery-playbook.md` — обязательна для production (state machine падает → recovery).
- `scripts/state-helper.py` — опционально, если state-файл становится сложным (validators, migrations).

---

# Scaffold 4 — doc-generator

## Когда подходит

Скилл по коду / API / changelog генерирует документацию по шаблону: JSDoc, TSDoc, READMEs, API reference, release notes. Подходит для «напиши доку, я лень». Антипаттерн: ad-hoc объяснение в чате (это не doc-generator, это просто Claude).

## YAML frontmatter

```yaml
---
name: {{name}}                                  # пример: jsdoc-writer, readme-bootstrap, api-docs
description: |                                  # ≤1024 chars
  Generates {{doc-type: "JSDoc / TSDoc / README / API reference"}}
  from existing source code by analysing signatures, types,
  and usage. Use whenever the user asks to write documentation,
  add JSDoc/TSDoc comments, bootstrap a README, generate API
  reference, document a module, or fill in missing docstrings.
  The skill follows the project's existing doc style if any is
  detected. Do not use for tutorial-style content, blog posts,
  or any docs that require new domain explanation rather than
  describing existing code.
allowed-tools: {{allowed-tools}}
model: sonnet                                   # haiku хватает для прямого JSDoc; sonnet для README
effort: medium
argument-hint: "[file-or-module-path]"
---
```

## Skeleton body

```markdown
# {{Title-Case-Name}}

Your goal is to ship documentation the developer can paste straight into the repo: structurally consistent, technically accurate, and matching the project's existing tone.

## When this skill fires
- User asks to document a file, module, function, or whole package.
- User mentions JSDoc, TSDoc, docstrings, API reference, README.
- User opens a fresh repo and wants a baseline README.

Stay out of: blog posts, tutorials, domain explanations beyond what the code shows.

## Workflow

### Phase 1 — Detect style
1. Glob for existing docs (`README*`, `docs/`, top of source files).
2. Detect framework: JSDoc / TSDoc / Sphinx / Rustdoc / MkDocs / plain.
3. If no style detected, default to `{{default-style: "TSDoc with @param @returns @example"}}` and tell the user.

### Phase 2 — Extract surface
For each target file:
- List exports (functions, classes, types).
- For each export: signature, parameters, return type, observable side-effects, thrown errors.
- Find call sites (use `Grep`) for usage examples.

### Phase 3 — Generate
Use the template from `references/templates/{{doc-type}}.md`. Fill placeholders. Prefer copying real types over inventing them.

Template anatomy (TSDoc example):
```typescript
/**
 * {{One-line purpose, imperative voice}}.
 *
 * @param name - {{what it represents, units if any}}
 * @returns {{shape and meaning}}
 * @throws {ErrorClass} {{when}}
 * @example
 * ```ts
 * {{minimal working snippet}}
 * ```
 */
```

### Phase 4 — Apply
- For inline doc (JSDoc/TSDoc): produce a patch with `Edit`, one function at a time.
- For README/API ref: write to the chosen path with `Write`.
- Always show the diff before committing — the developer is the gatekeeper.

## Quality bar
- No invented parameters or return types — only what the code actually exposes.
- Examples compile (or at minimum, type-check) against the real signature.
- Existing docs are extended, not overwritten — preserve human-written prose.

## References (lazy-loaded)
- `references/templates/jsdoc.md`
- `references/templates/tsdoc.md`
- `references/templates/readme.md`
- `references/templates/api-reference.md`
- `references/style-detection.md` — heuristics for detecting project style
```

## Positive trigger phrases

1. «напиши JSDoc для этой функции»
2. «сгенерируй README для проекта»
3. «document this module»
4. «добавь docstrings ко всем функциям»
5. «нужна API reference»

## Negative triggers

1. «напиши гайд по X с нуля» — это tutorial, не doc-generator.
2. «объясни мне как работает X» — это интерактивное объяснение, не файл.
3. «отрефактори комментарии» — refactor scope, не generation.

## Рекомендуемый `allowed-tools`

```yaml
allowed-tools: Read, Glob, Grep, Edit, Write
```
- `Bash` **не нужен** — doc-generator работает с файлами, не с runtime.
- `Edit` для inline JSDoc, `Write` для свежих README.

## References / scripts

- `references/templates/*.md` — **обязательны**, по одной на формат. Без них стиль плавает.
- `references/style-detection.md` — обязательна, иначе скилл навязывает свой стиль чужому проекту.
- `scripts/extract-exports.{ts,py}` — опционально, если AST-парсинг важен. Базово хватает Grep + Read.

---

# Scaffold 5 — knowledge-curator

## Когда подходит

RAG-стиль: скилл ищет в локальной базе (vault, docs/, internal wiki), синтезирует ответ **с обязательной atrribution на конкретные файлы и строки**. Подходит для work с Obsidian-vault'ом, корпоративной wiki, FAQ-ботами. Антипаттерн: external research (это `research-agent`), правка vault'а (это другой skill).

## YAML frontmatter

```yaml
---
name: {{name}}                                  # пример: vault-query, wiki-answer, kb-search
description: |                                  # ≤1024 chars
  Answers questions by searching {{base-name: "the user's vault / wiki / internal docs"}}
  and synthesising a response with explicit citations back to
  the source files. Use whenever the user asks what they wrote
  about X, what the team decided about Y, where in the docs Z
  lives, or mentions {{vault-keyword-1}}, {{vault-keyword-2}},
  internal knowledge base, wiki, notes, or memory. The skill
  never invents content — if the base is silent, the answer
  says so. Do not use for external research, web search, or
  general questions where the answer lives outside the base.
allowed-tools: {{allowed-tools}}
model: sonnet
effort: medium
argument-hint: "[question]"
---
```

## Skeleton body

```markdown
# {{Title-Case-Name}}

Your goal is to answer the user's question using only what lives in {{base-path: "the configured knowledge base"}}, and to make every claim traceable back to a specific file and line. Trust is the product.

## When this skill fires
- User asks «what did I write about X», «where is Y in our docs», «what did we decide about Z».
- User references the base by name (vault, wiki, notes, knowledge base, second brain).
- User wants a synthesis across multiple internal pages.

Stay silent for: external research, code review, generic Q&A unrelated to the base.

## Workflow

### Phase 1 — Resolve the base
1. Read the index/MOC if present (e.g. `index.md`, `overview.md`).
2. Honour the cheapest-primitive rule (`guide §5.3 / Kir CLAUDE.md`): metadata > frontmatter > grep > full read.

### Phase 2 — Retrieve
1. Translate the question into 2-4 search terms (synonyms included).
2. Run `Grep` against the base; cap results at {{retrieve-cap: 20}} hits.
3. For each hit, open the file just enough to confirm relevance (`-A 10 -B 2`).
4. Score each source by: recency, lifecycle (`verified` > `reviewed` > `draft`), provenance (`human-written` > `llm+human-reviewed` > `llm-generated`).

### Phase 3 — Synthesise with attribution
Compose the answer as paragraphs where every non-trivial claim ends with `[[source-page]]` or `path/to/file.md:line`. Contradictions inside the base get a dedicated subsection, not silent merging.

Output shape:
```
Answer in 5–10 sentences.

Sources:
- [[page-1]] — what it contributed
- [[page-2]] — what it contributed
- ...

Contradictions (if any):
- [[page-1]] says X, [[page-3]] says ¬X. Recency favours [[page-3]].
```

### Phase 4 — Offer to save
If the synthesis itself is reusable, offer to save it as `wiki/synthesis/{{slug}}.md` (vault rule) or equivalent for the project. Save only after explicit confirmation.

## Quality bar
- No claim without attribution. If unsourced, mark with `^[inferred]` (vault convention) or omit.
- If the base says nothing on the topic, the answer says so in one line — no padding.
- Lifecycle and provenance are respected when sources conflict.

## References (lazy-loaded)
- `references/retrieval-primitives.md` — cheap → expensive ordering
- `references/citation-style.md` — wikilinks vs path:line per base type
- `references/contradiction-handling.md` — how to surface conflicts
```

## Positive trigger phrases

1. «что я писал про X»
2. «найди в моих заметках Y»
3. «что в нашей wiki про Z»
4. «search internal docs for X»
5. «вспомни наше решение про X»

## Negative triggers

1. «найди в гугле» — это `research-agent`.
2. «обнови мою wiki» — write-операция, отдельный skill (`/ingest`, `/sync`).
3. «напиши новую страницу про X с нуля» — generation, не curation.

## Рекомендуемый `allowed-tools`

```yaml
allowed-tools: Read, Glob, Grep
```
- Read-only по дизайну. `Edit/Write` **не выдаём** — curator только читает и цитирует.
- `Bash` опционально, если базе нужен внешний индекс (например `rg` с custom-конфигом).

## References / scripts

- `references/retrieval-primitives.md` — обязательна для соблюдения cheap-first.
- `references/citation-style.md` — обязательна (per-vault style различается).
- `scripts/build-index.py` — опционально, если базе нужен предварительный индекс.

---

# Scaffold 6 — simple-automation

## Когда подходит

One-shot: пришёл триггер — выполнили одно действие — закончили. Никакого state между запусками. Подходит для form-filler, file-renamer, quick formatter, single-pass cleanup. Антипаттерн: задача требует памяти между фазами (`workflow-orchestrator`).

## YAML frontmatter

```yaml
---
name: {{name}}                                  # пример: rename-by-pattern, strip-trailing-ws, format-on-save
description: |                                  # ≤1024 chars; держим коротким
  {{One-line-what: "Performs <X> in a single pass"}}. Use
  whenever the user asks to {{trigger-verb-1}}, {{trigger-verb-2}},
  {{trigger-verb-3}}, or mentions {{keyword-1}}, {{keyword-2}}.
  The skill runs once, reports what it changed, and stops.
  Do not use for multi-step workflows, anything that requires
  confirmation between phases, or tasks where state must
  survive across runs.
allowed-tools: {{allowed-tools}}
model: haiku                                    # достаточно для one-shot
effort: low
argument-hint: "[target]"
---
```

## Skeleton body

```markdown
# {{Title-Case-Name}}

Your goal is to do exactly one thing well: {{one-thing: "rename files matching pattern X to pattern Y"}}, and then get out of the way. No state, no follow-up, no scope creep.

## When this skill fires
- User asks to {{trigger-1}}, {{trigger-2}}, {{trigger-3}}.
- The task fits in one pass — input → action → report.

Stay silent for: multi-phase tasks, anything requiring confirmation between steps, tasks needing memory across runs.

## Workflow

### Step 1 — Validate input
- Parse `$ARGUMENTS`. If required arg is missing, ask once and stop.
- Sanity-check target exists, scope is bounded.

### Step 2 — Dry-run preview
- Show what would change (files, lines, count).
- Wait for user's «go» — single confirmation, not multi-gate.

### Step 3 — Apply
- Execute the action. Cap blast radius at {{blast-radius: "the explicit target"}}.
- Capture before/after for the report.

### Step 4 — Report and stop
- One-screen report: what changed, what was skipped, any warnings.
- No follow-up suggestions, no "want me to also...". Done is done.

## Quality bar
- Single pass, no loops over phases.
- Dry-run is mandatory unless user explicitly said «just do it».
- Report fits on one screen.

## References (lazy-loaded)
- Usually none. If the skill needs >1 reference doc, it is probably the wrong scaffold — promote to `workflow-orchestrator`.
```

## Positive trigger phrases

1. «rename all files matching X»
2. «strip trailing whitespace»
3. «format this file»
4. «прогони formatter один раз»
5. «удали .DS_Store везде»

## Negative triggers

1. «сначала спроси меня, потом сделай, потом проверь» — это `workflow-orchestrator`.
2. «найди и исправь все баги» — review + fix, не one-shot (это `code-reviewer` + отдельный fixer).
3. «помни что я делал в прошлый раз» — state across runs → `workflow-orchestrator`.

## Рекомендуемый `allowed-tools`

```yaml
allowed-tools: Read, Glob, Edit, Bash
```
- Узкий set: ровно то, что нужно для одного действия.
- Если действие read-only (например «count lines») — убрать `Edit`.
- `Bash` для shell-операций (`mv`, `find -exec`), но фильтровать через `PreToolUse` hook если действие деструктивное.

## References / scripts

- References — как правило **не нужны**. Если возникают — пересмотри выбор scaffold.
- `scripts/{{action}}.sh` — опционально, если действие проще выразить shell-командой, чем серией tool calls.

---

# Общие правила для всех 6 scaffold'ов

Эти правила Сборщик-агент проверяет независимо от типа. Если шаблон нарушает что-то здесь — это блокер для деплоя (`guide.md §13.4`, уровень Lint).

## Description (frontmatter)

- **Длина:** ≥20 символов, ≤1024. Combined `description + when_to_use` truncate'ится на 1536 в marketplace (`guide.md §2.1`).
- **Лицо:** третье. «Reviews code», не «I review code», не «You should review».
- **Структура:** `[What it does] + [When to use] + [Trigger keywords/synonyms] + [Negative clause]` (`guide.md §5.1`).
- **Pushy:** включает фразы типа «whenever the user asks to», «mentions», «even if not explicitly named». Claude склонен к under-triggering — компенсируем.
- **Синонимы:** ≥3 trigger phrases в разных формулировках. Один канонический термин ловит ~30% реальных запросов, синонимы добирают остальное.
- **Negative clause:** одна фраза вида «Do not use for X, Y, Z» предотвращает over-triggering (`guide.md §5.1`).
- **Без XML-тегов:** запрещено спекой (security, `guide.md §2.1`).

## Body (SKILL.md)

- **≤500 строк.** Anthropic hard limit. Если приближаемся — выносим в `references/*.md` с ссылкой (`guide.md §5.2`).
- **Outcome-first opening:** «Your goal is to ...» — что должно получиться, не как это устроено внутри (`guide.md §5.3`).
- **Positive imperatives:** «Use this skill when ...» вместо «NEVER use for ...». Объясняем «почему», а не запрещаем.
- **Без CAPS MUST/NEVER/CRITICAL:** Anthropic skill-creator явно флагает yellow flag (`guide.md §5.3`). Заменяем на «You should, because ...».
- **Без «Think step by step»:** устаревший паттерн. Современные модели и так reason'ят; формулировка делает body хрупким.
- **Anti-contradiction audit:** если правило A конфликтует с правилом B — выставить явную иерархию приоритета (`guide.md §5.5`). Это требование PromptMaker'а и оно наследуется.

## Tools

- **Узкий allowlist:** даём ровно то, что нужно. Лишний `Bash` или `Write` — атак-серфэйс.
- **Read-only по дефолту:** если скилл репортит/исследует — без `Edit/Write`.
- **`Bash` — с осторожностью:** для деструктивных операций (rm, mv, force-push) использовать `PreToolUse` hook на уровне плагина (`guide.md §6`).

## References / scripts (progressive disclosure)

- `references/*.md` подгружаются по запросу Claude (`guide.md §5.2`, tier 3). Используем, чтобы не раздувать SKILL.md.
- `scripts/*` подгружаются при exec (tier 4). Хороший индикатор «вынести в скрипт»: одинаковый shell-snippet встречается в body ≥2 раз.
- В references держим: per-format templates, per-language rubrics, длинные таблицы, edge-case playbooks. Не держим: «что делает скилл» (это в SKILL.md).

## Validation handoff

После генерации скилла Сборщик-агент гонит результат через `guide.md §13.4`:
1. **Lint** — YAML parseable, description в пределах, ≥3 trigger synonyms, нет коллизий имён.
2. **Dry-run triggering** — 5 positive prompts должны триггерить, 5 negative не должны. >20% false positive → suggest narrower description.
3. **Content checks** — ≥2 шага в workflow (кроме `simple-automation`, там 4 шага jeden-pass), все упомянутые tools — в allowed-tools, нет undefined variable refs.

## Placeholder соглашения

Все шаблоны выше используют `{{kebab-or-snake-name}}` в местах подстановки. Сборщик-агент:
- Подставляет конкретные значения из interview Q1-Q6.
- Удаляет любые placeholder'ы, которые остались незаполненными (либо ставит sensible default из контекста).
- Никогда не оставляет `{{...}}` в финальном SKILL.md — это блокер.

---

## DONE

**Что сделано:** создан reference-файл с 6 production-ready SKILL.md scaffolds (research-agent, code-reviewer, workflow-orchestrator, doc-generator, knowledge-curator, simple-automation). Каждый: frontmatter по спеке §2.1, outcome-first body, 3-5 positive triggers, 2-3 negative triggers, рекомендованный allowed-tools, подсказки по references/scripts. В конце — раздел «Общие правила», в нём description-инварианты, body-инварианты, tools-инварианты, validation handoff на §13.4 и placeholder-соглашения.

**Проверки:**
- Cross-check: frontmatter поля соответствуют `guide.md §2.1` (name, description, allowed-tools, model, effort, argument-hint, context).
- Description ≤1024 chars во всех 6 — выдержано (длина шаблонов в коде ниже лимита).
- Outcome-first, без CAPS MUST, без «think step by step», positive imperatives — проверено по тексту.
- Все 6 scaffold'ов матчат таблицу из `guide.md §13.3` (типы, complexity, Q-count подразумевается интервью pluginmaker'а).

**Уверенность:** 88% — основа канонична. -7% за то, что не валидировал шаблоны через mock dry-run trigger (это работа Сборщика-агента, не моя). -5% за placeholder'ы — они унифицированы внутри файла, но Сборщик-агент может захотеть свои конвенции.
