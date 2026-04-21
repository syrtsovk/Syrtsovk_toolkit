# Syrtsovk Toolkit

Коллекция **скиллов** и **команд** для [Claude Code](https://docs.claude.com/en/docs/claude-code) — моя личная подборка, которую я использую в повседневной работе и постепенно выкладываю сюда.

> Всё оформлено под стандарт Claude Code Skills: каждый скилл — это папка с `SKILL.md` и опциональными `references/`. Просто копируешь её в `~/.claude/skills/` и скилл готов к работе.

---

## Содержание

### Skills

| Скилл | Для чего | Ссылка |
|-------|----------|--------|
| `promptmaker` | Элитный промпт-инженер: генерирует готовые XML-промпты для виртуальных AI-экспертов. Анализирует задачу, подбирает модули, прогоняет Self-Refine и Constitutional Principles. | [skills/promptmaker](skills/promptmaker/) |

### Commands

_Команд пока нет — скоро добавлю._

---

## Установка

### Все скиллы разом

```bash
# клонируем в удобное место
git clone https://github.com/syrtsovk/Syrtsovk_toolkit.git ~/syrtsovk-toolkit

# симлинкаем нужные скиллы в ~/.claude/skills
mkdir -p ~/.claude/skills
ln -s ~/syrtsovk-toolkit/skills/promptmaker ~/.claude/skills/promptmaker
```

После этого в Claude Code скилл будет доступен как `/promptmaker` или по триггерам из описания.

### Один конкретный скилл

Если нужен только `promptmaker` — можно просто скопировать его папку:

```bash
# через git sparse-checkout (рекомендуется, можно обновляться)
git clone --filter=blob:none --sparse https://github.com/syrtsovk/Syrtsovk_toolkit.git
cd Syrtsovk_toolkit
git sparse-checkout set skills/promptmaker
cp -r skills/promptmaker ~/.claude/skills/
```

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

Claude Code сам подхватывает скилл по `description`, когда видит подходящий запрос пользователя.

---

## Обновления

- Репозиторий пополняется постепенно
- Breaking changes маркирую в описании скилла
- Issues и PR приветствуются

---

## Лицензия

[MIT](LICENSE) — используй как хочешь, форкай, адаптируй под свой workflow.

---

**Автор:** [@syrtsovk](https://github.com/syrtsovk)
