# Syrtsovk Toolkit

Коллекция **скиллов** для [Claude](https://claude.com) — моя личная подборка, которую я использую в повседневной работе и постепенно выкладываю сюда.

Скиллы работают везде, где Claude поддерживает [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview):

- **Claude Code** (CLI) — файлы в `~/.claude/skills/`
- **Claude.ai** (web / desktop) — через Settings → Features → Skills
- **Claude Agent SDK / Anthropic API** — программно через Skills API

> Каждый скилл — это папка с `SKILL.md` (YAML frontmatter + инструкции) и опциональными `references/`. Claude сам подхватывает скилл по полю `description`, когда видит подходящий запрос.

---

## Содержание

### Skills

| Скилл | Для чего | Ссылка |
|-------|----------|--------|
| `promptmaker` | Элитный промпт-инженер: генерирует готовые XML-промпты для виртуальных AI-экспертов. Анализирует задачу, подбирает модули, прогоняет Self-Refine и Constitutional Principles. | [skills/promptmaker](skills/promptmaker/) |
| `design-expert` | Эксперт-ассистент по Claude Design: составляет промпты для генерации презентаций / лендингов / прототипов / инфографики, подбирает стили и настройки, решает задачи в продукте Claude Design. | [skills/design-expert](skills/design-expert/) |

### Prompts

| Промт | Для чего | Ссылка |
|-------|----------|--------|
| `promptscanner` | Промтсканнер — проверь чужой промт за 30 секунд: балл 0-100, что грамотно, что недоработано, что реально получишь на выходе. Защищён от prompt injection. | [prompts/promptscanner](prompts/promptscanner/) |

### Commands

_Slash-команды для Claude Code — скоро добавлю._

---

## Установка

### 1. Claude Code (CLI)

Самый простой способ — клонировать репо и симлинкнуть нужные скиллы:

```bash
# клонируем в удобное место
git clone https://github.com/syrtsovk/Syrtsovk_toolkit.git ~/syrtsovk-toolkit

# симлинкаем нужный скилл (user-level, доступен во всех проектах)
mkdir -p ~/.claude/skills
ln -s ~/syrtsovk-toolkit/skills/promptmaker ~/.claude/skills/promptmaker
```

Для project-level (только в одном проекте) — положи в `<project>/.claude/skills/` вместо `~/.claude/skills/`.

После этого скилл подхватится автоматически. Проверить можно так:
- Открой Claude Code в любом проекте
- Набери что-то, что триггерит описание скилла (например: «сделай мне промпт для эксперта по X»)
- Claude сам загрузит `SKILL.md` и применит его

Обновления — `cd ~/syrtsovk-toolkit && git pull`. Симлинки остаются валидными.

#### Альтернатива: только один скилл через sparse-checkout

```bash
git clone --filter=blob:none --sparse https://github.com/syrtsovk/Syrtsovk_toolkit.git
cd Syrtsovk_toolkit
git sparse-checkout set skills/promptmaker
cp -r skills/promptmaker ~/.claude/skills/
```

---

### 2. Claude.ai (web / desktop)

Доступно на **всех планах** (Free, Pro, Max, Team, Enterprise). Требование — включить «Code execution and file creation» в Settings.

1. Склонируй репо (или скачай нужный скилл архивом)
2. Запакуй папку скилла в ZIP:
   ```bash
   cd skills/
   zip -r promptmaker.zip promptmaker/
   ```
3. В Claude.ai открой: **Settings → Features → Skills → `+` → Create skill**
4. Загрузи `promptmaker.zip`
5. После активации Claude будет подхватывать скилл по триггерам

> Custom skills в Claude.ai приватны для твоего аккаунта и **не синкируются** с Claude Code / API.

Официальная инструкция: [Use Skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

---

### 3. Claude Agent SDK / Anthropic API

Подключается программно через Skills API. Нужны три beta-header'а:

```python
from anthropic import Anthropic

client = Anthropic(
    default_headers={
        "skills-2025-10-02": "true",
        "code-execution-2025-08-25": "true",
        "files-api-2025-04-14": "true",
    }
)

# 1. Загрузить скилл через POST /v1/skills (получишь skill_id)
# 2. Передать skill_id в container параметре сообщения
```

Подробности и актуальные примеры:
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Use Skills with Claude API](https://platform.claude.com/docs/en/build-with-claude/skills-guide)
- [Extend Claude with Skills (Claude Code)](https://code.claude.com/docs/en/skills)

> Skills через API — workspace-wide (синкируются внутри workspace), но **не синкируются с Claude.ai**.

---

## Как устроен скилл

Минимальная структура:

```
skills/<name>/
├── SKILL.md                 # YAML frontmatter + инструкция
└── references/              # опциональные материалы (knowledge base, примеры)
    └── ...
```

`SKILL.md` начинается с frontmatter:

```yaml
---
name: promptmaker
description: "Короткое описание + триггеры активации"
---
```

`description` — ключевое поле: Claude решает активировать скилл, анализируя его. Пиши чётко, с примерами триггеров.

---

## Обновления

- Репозиторий пополняется постепенно
- Breaking changes маркирую в описании скилла
- Issues и PR приветствуются

---

## Лицензия

[MIT](LICENSE) — используй как хочешь, форкай, адаптируй под свой workflow.

---

## Контакты

- [**Telegram**](https://t.me/+ygb6FUWDPDszNjQ6)
- [**MAX**](https://max.ru/join/LKkLyQX7Ite2p_17YKNYQpeqLtfpfe9i1MyAgvEHYxM)
- [**GitHub**](https://github.com/syrtsovk)
