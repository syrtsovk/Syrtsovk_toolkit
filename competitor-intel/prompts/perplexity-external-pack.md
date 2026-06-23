# Perplexity: пак запросов для взгляда снаружи

> Что это: готовый набор запросов к Perplexity, который собирает про конкурента то, чего нет в его собственном контенте — отзывы и жалобы, с кем его сравнивают и почему уходят, новости (инвестиции, поглощения, партнёрства, уход топов), найм под новые направления, цены и таймлайн событий.
> Зачем: сайт и видео конкурента показывают его «парадную» версию. Perplexity показывает версию рынка — что о нём реально думают, куда он вкладывается и где у него болит. Это половина досье, которую невозможно собрать из его собственных материалов.

Если нужен глубокий разбор мотивов клиентов и «работ» (Jobs) конкурента — см. [perplexity-ajtbd-pack.md](perplexity-ajtbd-pack.md).
Заполненный пример пака на реальном конкуренте — см. [examples/gong/perplexity-pack-filled.md](../examples/gong/perplexity-pack-filled.md).

---

## Как пользоваться (прочитай один раз)

1. **Замени плейсхолдеры** во всех запросах: `{{КОНКУРЕНТ}}` (название/бренд), `{{НИША}}` (твой рынок одним словом), `{{САЙТ_URL}}` (сайт конкурента, если знаешь).
2. **Включи режим Deep Research** (или Pro Search) в Perplexity. Каждый запрос внизу уже просит цитаты и даты — не убирай эту строку.
3. **Гоняй по одному запросу за раз.** Не вставляй весь пак сразу: один запрос → дождись ответа → скопируй результат в [шаблон разбора источника](../templates/source-breakdown.md) → следующий запрос. Так Perplexity глубже копает и не сваливает всё в кашу.
4. **Сохраняй цитату + дату + ссылку** на каждый факт. Нет источника — это не факт, а гипотеза. Поисковые AI иногда выдумывают или приписывают факт не тому источнику — проверяй ссылки.
5. **Для западного / иностранного конкурента** запускай EN-версию запроса (даю под каждым) — на нужном языке Perplexity вытащит в разы больше из локальных источников. Результат он же и переведёт.
6. **Один запрос — несколько подтем.** Если ответ слишком общий, разбей запрос на два и задай по очереди.

Как читать сигналы из ответов (опережающие vs запаздывающие, правило суммы весов) — см. [methodology/02-signal-rules.md](../methodology/02-signal-rules.md). Откуда вообще берутся внешние сигналы и как они ложатся в досье — см. [methodology/03-external-signals.md](../methodology/03-external-signals.md).

Концовка каждого запроса (копируй как есть):

```
Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

---

## Запрос 1 — Отзывы, жалобы, слабые места

**RU:**
```
Что пишут реальные пользователи про {{КОНКУРЕНТ}} в отзывах, обсуждениях и на форумах — и хорошее, и плохое. Сделай две части:
1. За что хвалят (плюсы, повторяющиеся похвалы).
2. На что жалуются и какие слабые места называют чаще всего (баги, поддержка, цена, сложность, чего не хватает).
Отдельно выпиши 3–5 самых частых претензий с цитатами и ссылками.

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

**EN (для западного конкурента):**
```
What do real users say about {{КОНКУРЕНТ}} in reviews, discussions and forums (G2, TrustRadius, Capterra, Reddit, Trustpilot, app stores)? Two parts:
1. What they praise (recurring positives).
2. What they complain about and the most frequently mentioned weaknesses (bugs, support, price, complexity, missing features).
List the 3–5 most common complaints with quotes and links.

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

> Зачем: жалобы клиентов — это карта слабых мест конкурента и одновременно карта спроса (за что люди готовы платить, но не получают). Главный приоритет внешней разведки.

---

## Запрос 2 — С кем сравнивают и почему уходят

**RU:**
```
С какими альтернативами и конкурентами сравнивают {{КОНКУРЕНТ}} в нише «{{НИША}}»? Найди:
1. Список альтернатив, с которыми его ставят рядом.
2. По каким причинам выбирают именно {{КОНКУРЕНТ}} (за что).
3. По каким причинам уходят к другим или жалеют о выборе (триггеры оттока: цена, функции, поддержка, сложность, надёжность).
Цитаты и ссылки на конкретные сравнения и отзывы об уходе.

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

**EN:**
```
What alternatives and competitors is {{КОНКУРЕНТ}} compared to in the "{{НИША}}" space? Find:
1. The list of alternatives it's benchmarked against.
2. Why people choose {{КОНКУРЕНТ}} over them.
3. Why people switch away or regret the choice (churn triggers: price, features, support, complexity, reliability).
Quotes and links to specific comparisons and switching/churn reviews.

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

> Зачем: причины ухода — это слабости глазами клиента, а список альтернатив показывает, как рынок реально воспринимает позиционирование конкурента (часто не так, как он сам себя описывает).

---

## Запрос 3 — Новости: инвестиции, поглощения, партнёрства, уход топов

**RU:**
```
Что писали СМИ и отраслевые медиа про {{КОНКУРЕНТ}} за последние 24 месяца? Собери:
1. Инвестиции и раунды финансирования (сумма, дата, инвесторы).
2. Поглощения и слияния (кого купили или кто купил их).
3. Стратегические партнёрства, крупные контракты, интеграции.
4. Кадровые перестановки в топ-менеджменте — приход или уход ключевых руководителей.
5. Ребрендинг, смена позиционирования, выход на новые рынки.
Каждый пункт — с датой и ссылкой на источник.

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

**EN:**
```
What did the press and industry media write about {{КОНКУРЕНТ}} in the last 24 months? Collect:
1. Funding rounds and investments (amount, date, investors).
2. Acquisitions and mergers (who they bought or who bought them).
3. Strategic partnerships, major contracts, integrations.
4. Executive changes — key leaders joining or leaving.
5. Rebranding, repositioning, expansion into new markets.
Each item with a date and a source link.

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

> Зачем: деньги и сделки — самые сильные сигналы намерения. Поглощение или раунд под конкретное направление говорит о стратегии громче любого блога. Уход топа часто предвещает смену курса.

---

## Запрос 4 — Найм под новые направления

**RU:**
```
Какие вакансии и роли открывал {{КОНКУРЕНТ}} за последний год (LinkedIn, careers-страница, job-площадки)? Меня интересует не текучка, а сигнал направления:
1. Какие НОВЫЕ роли или направления появились впервые (раньше таких не нанимали)?
2. Есть ли концентрация вакансий вокруг одной новой темы/продукта/рынка — это ставка.
3. Разрозненный найм на замену — это шум, его помечай отдельно.
Со ссылками на вакансии и датами публикации.

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

**EN:**
```
What roles has {{КОНКУРЕНТ}} been hiring for in the last year (LinkedIn, careers page, job boards)? I care about direction, not routine backfill:
1. What NEW roles or functions appeared for the first time (never hired before)?
2. Is there a concentration of openings around one new theme/product/market — that's a bet.
3. Scattered backfill hiring is noise — flag it separately.
With links to the postings and posting dates.

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

> Зачем: компания нанимает туда, куда вкладывает завтра. Кучка вакансий вокруг одной новой темы — самый ранний и честный сигнал нового направления (его ещё нет на сайте). Найм линейного персонала (продавцы, мастера, операторы) сигналом не считается — это просто восполнение текучки.

---

## Запрос 5 — Цены и предложение по открытым данным

**RU:**
```
Какие у {{КОНКУРЕНТ}} цены и из чего состоит предложение по открытым данным ({{САЙТ_URL}}, прайсы, отзывы, обзоры)? Собери:
1. Текущие тарифы / пакеты / вилки цен — что входит, кому адресован каждый уровень.
2. Что вынесено в премиум или платится отдельно.
3. Как менялись цены за последние 1–2 года — дорожали, дешевели, что переехало из бесплатного в платное.
Подкрепи ссылками; где есть — сравни с архивной версией сайта (web.archive.org).

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

**EN:**
```
What are {{КОНКУРЕНТ}}'s prices and what's in the offer, from public data ({{САЙТ_URL}}, pricing pages, reviews)? Collect:
1. Current plans / packages / price ranges — what's included, who each tier targets.
2. What's locked behind premium or charged separately.
3. How pricing changed over the last 1–2 years — up, down, what moved from free to paid.
Back it with links; where possible compare to the archived site (web.archive.org).

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

> Зачем: движение цен — это сигнал сдвига сегмента. Вверх (новые премиум-пакеты, что-то уехало в платное) — уход в более дорогой сегмент. Вниз (дешёвый вход) — заход в масс-сегмент. Запаздывающий сигнал, но дешёвый в сборе.

---

## Запрос 6 — Таймлайн ключевых событий за 24 месяца

**RU:**
```
Построй таймлайн ключевых событий {{КОНКУРЕНТ}} за последние 24 месяца, по датам: запуски продуктов/направлений, волны найма, сделки и партнёрства, инвестиции, смена цен, кадровые перестановки, ребрендинг. Таблицей: дата | событие | тип (продукт / найм / сделка / цена / коммуникация) | ссылка.
В конце ответь на один вопрос: ускоряется ли темп изменений в последние 6 месяцев по сравнению с предыдущими 18?

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

**EN:**
```
Build a timeline of key {{КОНКУРЕНТ}} events over the last 24 months, by date: product/line launches, hiring waves, deals and partnerships, funding, price changes, exec changes, rebranding. As a table: date | event | type (product / hiring / deal / price / comms) | link.
End with one answer: is the pace of change accelerating in the last 6 months vs the prior 18?

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

> Зачем: одно событие — шум, цепочка событий в одну сторону — манёвр. Таймлайн собирает разрозненные факты в линию и показывает темп: ускорение изменений за последние полгода — само по себе сильный сигнал.

---

## Для локального и офлайн-бизнеса — добавь эти источники

Если конкурент — кафе, барбершоп, клиника, локальный сервис, магазин, продавец на маркетплейсе, то у него почти не будет инвестиций, найма под направления и пресс-релизов. Зато будет гора отзывов. Смести фокус с «куда движется» на «что у них болит в сервисе и продукте» и добавь к запросу 1 эти площадки.

**RU:**
```
Что пишут клиенты про {{КОНКУРЕНТ}} на картах (2ГИС, Яндекс.Карты, Google Maps), маркетплейсах и отзовиках? Собери:
1. Средние оценки и динамику (растёт/падает рейтинг).
2. За что хвалят чаще всего.
3. На что жалуются чаще всего (сервис, качество, цена, сроки, ассортимент) — с цитатами.
4. Как компания отвечает на негатив — вообще отвечает или игнорирует?
Со ссылками на конкретные отзывы и датами.

Use Deep Research. Cite every claim with a source link + date. Prefer 2024–2026 sources. If a fact has no source — mark it as a hypothesis, do not state it as fact.
```

> Карты и отзовики для локального бизнеса — это то же, что G2 и Reddit для SaaS: главный источник реальных слабостей. Отсутствие «опережающих» сигналов (найм, сделки) у локального игрока — это норма, а не провал разведки.

---

## Куда дальше

- Разложи каждый ответ в [шаблон разбора источника](../templates/source-breakdown.md) и помечай вес сигналов по [правилам сигналов](../methodology/02-signal-rules.md).
- Сведённые слабости и точки отстройки — в [боевую карту](../templates/battlecard.md).
- Глубокий разбор мотивов клиентов и «работ» (Jobs) — [perplexity-ajtbd-pack.md](perplexity-ajtbd-pack.md) и [методология AJTBD-линзы](../methodology/04-ajtbd-lens.md).
- Внутренний голос конкурента (его видео и материалы) собирается отдельно — [notebooklm-video-pack.md](notebooklm-video-pack.md).
