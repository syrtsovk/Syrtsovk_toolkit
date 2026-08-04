---
name: pluginmaker
description: Generates production-ready Claude Code skills through a short adaptive interview (4-6 questions) plus three-level validation. Use when the user asks to create a skill, build a new Claude Code plugin, make a slash command, design a subagent, scaffold a skill, generate SKILL.md, or wants help structuring a new automation as a reusable Claude Code artifact. Stay out when the user already has a skill and wants only minor edits to existing files, or wants to run an existing skill, or asks general questions about how Claude Code works.
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
argument-hint: "[brief description of the skill, optional]"
version: 1.0
---

# pluginmaker

Your goal is to take a fuzzy user idea ("I want a skill that does X") and turn it into a working Claude Code skill — directory + SKILL.md + tests + audit trail — that the user can drop into `~/.claude/skills/` and use today.

You do not solve the user's underlying task. You build the skill that will solve it. If the user asks for a competitor-analysis skill, you do not analyze competitors — you produce a `competitor-analysis/` skill folder.

## When this skill fires

- "Сделай скилл для X" / "Создай скилл" / "Хочу плагин"
- "Make a Claude Code skill" / "Scaffold a SKILL.md" / "Build a slash command"
- "Сделай мне ассистента/агента под задачу Y" (если речь про Claude Code, не GPTs — для GPTs/Gems используй promptmaker)
- User describes a recurring workflow and wants it reusable

## When to stay silent

- User wants to edit an existing skill (use `Edit` directly, no interview)
- User wants to run an existing skill (just run it)
- User asks "how does Claude Code work" (answer directly, no scaffolding)
- User wants a portable XML prompt for GPTs/Gems/Projects (route to `promptmaker`)
- User wants a non-skill artifact (Obsidian template, blog post, etc.)

## Workflow — 5 phases

### Phase 1 — Adaptive interview (Интервьюер role, inline)

Read `references/interview-flow.md` in full before the first question. Follow M1-M4 framework:

- **Q1 (M1)** — open low-barrier: "Опиши задачу скилла — какую работу он должен делать?"
- **Q2 (M2)** — auto-classify type from Q1 keywords against the 6 scaffold types; confirm if ambiguous.
- **Q3 (M3)** — Most Impactful Axis (trigger / tools / source-target) chosen by type.
- **Q4-6 (M4)** — type-specific follow-ups (exact texts in `interview-flow.md` §4).
- **Final Q** — negative triggers: "Когда скилл НЕ должен срабатывать?"

Pause-points: minimum 3 questions, maximum 6. If Q1 answer is already detailed and unambiguous, skip Q4-5 and go straight to negative-triggers Q.

Use `AskUserQuestion` for every question. Output of this phase = a structured brief (schema in `interview-flow.md` §8).

### Phase 2 — Scaffold selection (Сборщик role, inline)

Read `references/scaffolds.md` once before this phase. The brief from Phase 1 names the scaffold type. Load that section (one of: `research-agent`, `code-reviewer`, `workflow-orchestrator`, `doc-generator`, `knowledge-curator`, `simple-automation`).

If brief is ambiguous between two types — ask one disambiguating question before picking.

### Phase 3 — Generation (Сборщик role, inline)

Before writing anything, read `references/promptmaker-canon.md` — these are the principles every generated SKILL.md must obey (positive imperatives, outcome-first opening, size adequacy, no CAPS MUST, no contradictions, trigger-phrase synonyms).

Fill the chosen scaffold:

1. Substitute placeholders with brief values.
2. Write a description that:
   - Opens with what the skill does (verb-led, third-person)
   - Names 3+ trigger synonyms drawn from how real users phrase the task
   - Closes with a "Stay out when..." negative clause (compulsory if the skill domain overlaps with anything else)
   - Stays inside 80-1024 characters
3. Write the body as outcome-first prose. Use positive imperatives. Keep it under 500 lines / 5000 words.
4. If any section grows past one screen, split it into `references/<topic>.md` and link from the body.
5. Create `test-cases.json` (5 positive prompts + 5 negative prompts) — schema in `references/output-structure.md` §4.
6. Create `.pluginmaker-meta.json` with the audit trail — schema in `references/output-structure.md` §5.

### Phase 4 — Validation (three parallel subagent roles)

Read `references/validation-rules.md` for the full ruleset before this phase. Spawn three workers in parallel via the Task tool:

**🎯 Triggertester** — runs Level 2 dry-run:
- Generates 5 positive + 5 negative prompts grounded in the description
- For each prompt, judges whether the skill should fire given the description
- Returns `positive_accuracy` and `negative_accuracy` scores
- If positive_accuracy < 0.8 → description is too narrow, suggest expanding synonyms
- If negative_accuracy < 0.8 → description is too broad, suggest sharpening negative clause

**🔍 Quality-Auditor** — runs Level 3 content audit:
- Scans the generated SKILL.md against CHECK-L3-01 through CHECK-L3-15
- Reports blockers, warnings, and suggestions with line numbers
- Proposes concrete rewrites for each finding

**📏 Linter** — runs Level 1 deterministic checks via Bash/regex:
- 15 RULE-L1-XX checks on frontmatter, file structure, naming
- Pure deterministic — no LLM judgment
- Returns PASS/FAIL per rule

Aggregate the three reports per the scoring lattice in `validation-rules.md` §5. Possible verdicts: `PASS`, `PASS-with-warnings`, `FAIL`.

If `FAIL` — return to Phase 3 with a fix list. One refinement pass. If still `FAIL` — surface to the user with the issues, do not loop indefinitely.

### Phase 5 — Output and deploy (inline)

When validation returns `PASS` or `PASS-with-warnings`:

1. Show the user the generated SKILL.md (full text) and the validation report summary.
2. Ask via `AskUserQuestion` where to deploy (four options from `output-structure.md` §7):
   - User-level (`~/.claude/skills/<name>/`)
   - Project-level (`<project>/.claude/skills/<name>/`)
   - Keep as draft (current cwd)
   - Inside an existing plugin (`<plugin>/skills/<name>/`)
3. Write the files: `SKILL.md`, `test-cases.json`, `.pluginmaker-meta.json`, plus any `references/<topic>.md` you split out.
4. Confirm: print the absolute path, a one-line how-to-use, and the next-step suggestion (test the skill in a real session, then refine the description if triggering misses).

## Six scaffold types — pick the right one

| Type | Use when | Reference section |
|---|---|---|
| `research-agent` | Multi-step search → synthesis → cite | `scaffolds.md` §2 |
| `code-reviewer` | Diff-aware bug/security/style review | `scaffolds.md` §3 |
| `workflow-orchestrator` | Multi-phase process with state | `scaffolds.md` §4 |
| `doc-generator` | README, JSDoc, structured docs | `scaffolds.md` §5 |
| `knowledge-curator` | Vault / RAG / source-attributed lookup | `scaffolds.md` §6 |
| `simple-automation` | One-shot trigger → action | `scaffolds.md` §7 |

If brief matches none of these — pick the closest and document the deviation in `.pluginmaker-meta.json` under `user_overrides`.

## Hard limits (apply to every generated skill)

- Description: 80-1024 chars, third-person, with synonyms and negative clause
- SKILL.md body: ≤500 lines, ≤5000 words
- No README.md inside the skill folder (it belongs at plugin level)
- No `_v2.md` / `_final.md` / `_fixed.md` files — overwrite the version, don't fork
- No hardcoded user paths (`/Users/<name>/` etc.) — use `${CLAUDE_SKILL_DIR}` or relative
- No CAPS imperatives (`MUST`, `NEVER`, `CRITICAL`) in the body — rewrite as "You should X, because Y"
- No "Think step by step" anywhere
- No cargo-cult role claims ("senior engineer with 12 years of experience")
- Every tool mentioned in the body must appear in `allowed-tools`

## Bundle mode (v2, not active in v1)

If the user asks for a full plugin bundle (with `.claude-plugin/plugin.json` and `marketplace.json`), tell them v1 generates a single skill only. Offer two paths:

1. Generate the skill now, then wrap it in a bundle manually following the plugin spec at https://code.claude.com/docs/en/plugins.
2. Wait for pluginmaker v2 — same workflow, full bundle output.

## Roles cheat-sheet

| Role | Realised as | Phase | Output |
|---|---|---|---|
| 🎤 Интервьюер | Inline (main skill) | 1 | brief.yaml |
| 🧱 Сборщик | Inline (main skill) | 2-3 | draft SKILL.md + tests + meta |
| 🎯 Триггер-тестер | Subagent via Task | 4 | L2 score + diagnosis |
| 🔍 Аудитор качества | Subagent via Task | 4 | L3 findings list |
| 📏 Линтер | Bash + regex inline | 4 | L1 PASS/FAIL per rule |

## References (lazy-load — read only when you reach that phase)

- `references/interview-flow.md` — exact question texts, M1-M4, brief schema
- `references/scaffolds.md` — six SKILL.md templates with placeholders
- `references/validation-rules.md` — three validation levels, every rule, prompt templates
- `references/promptmaker-canon.md` — generation principles (positive imperatives, outcome-first, etc.)
- `references/output-structure.md` — file layout, naming, JSON schemas, deploy targets

The references cite an internal `guide.md` (Claude Code Plugins Building Guide) as their provenance. That file ships separately and is not part of this skill — treat those `guide.md §X` mentions as source credits, not as files to open.

## When stuck

- User refuses to answer enough questions → after 3 questions, generate with sensible defaults and flag low-confidence sections in `.pluginmaker-meta.json`.
- Brief is contradictory (e.g. "auto-invoke" + "only when I type /command") → ask one clarifying question, default to `auto-invoke` since it covers both.
- Validation loops more than once → surface findings to the user, let them decide whether to ship with warnings.
- User asks for a feature not in the six scaffolds → use `simple-automation` as the base and document the gap.

## Notes for self-improvement

- Every generated skill leaves an audit trail in `.pluginmaker-meta.json` — questions asked, scaffold used, validation scores. Over time these become a dataset for tuning interview depth and scaffold defaults.
- If a generated skill comes back with the same lint failure twice, that's a signal to refine the scaffold, not the validator.
