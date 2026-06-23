# Perplexity-пак под Gong — заполненный пример

> **Пример заполнения шаблонов [prompts/perplexity-external-pack.md](../../prompts/perplexity-external-pack.md) и [prompts/perplexity-ajtbd-pack.md](../../prompts/perplexity-ajtbd-pack.md) на реальной компании (Gong).**

**Что это и зачем.** Готовый-к-прогону набор запросов в Perplexity Deep Research, в котором плейсхолдеры из шаблонов уже подставлены под конкретного конкурента — Gong (gong.io, платформа revenue / conversation intelligence). Берите его как образец: видно, как абстрактные `{{КОНКУРЕНТ}}` / `{{НИША}}` / `{{САЙТ_URL}}` превращаются в живые формулировки. Хотите так же по своему конкуренту — копируйте шаблоны и подставляйте свои значения.

Запросы на английском — потому что Gong западная компания, и её отзывы, кейсы и аналитику Perplexity лучше находит на английском. Для русскоязычного конкурента пишите запросы по-русски.

---

## Как пользоваться

- Вставляйте по одному запросу в Perplexity в режиме **Deep Research**.
- Ответ помечайте кодом запроса (A1, B2 …), чтобы потом легко разнести по досье.
- Маркеры в ответах (`[SITE]` / `[CUSTOMER]` / `[INFERRED]` / `[BUZZWORD]` / `[OPAQUE]` / `[PSEUDO-BIG]`) **не стирайте** — это карта, где маркетинг, а где правда от клиента. Логику маркеров см. в [methodology/02-signal-rules.md](../../methodology/02-signal-rules.md).
- Куда какой ответ идёт в досье — указано в скобках у каждого запроса (ссылки на блоки структуры досье: см. [templates/source-breakdown.md](../../templates/source-breakdown.md) и каркас [examples/gong/dossier-skeleton.md](dossier-skeleton.md)).
- Два блока: **A — взгляд через AJTBD на бренд и сайт** (методика в [methodology/04-ajtbd-lens.md](../../methodology/04-ajtbd-lens.md)), **B — взгляд рынка через внешние источники** (методика в [methodology/03-external-signals.md](../../methodology/03-external-signals.md)).

> Важно: эти запросы дают **карту конкурента** — где у него сильные стороны, где слабые места, куда он движется. Что с этой картой делать дальше (свой заход, своё позиционирование) — отдельная работа, которую вы делаете уже под свой продукт. В этом примере таких выводов нет специально: тут только метод сбора.

---

# A. AJTBD: бренд + сайт (A1–A7)

> Все 7 запросов из шаблона, подставленные под Gong. Самые ценные под такого конкурента: **A1** (позиционирование), **A2** (монетизация — у Gong цена и есть главная слабость по отзывам), **A3** (timeline переключения). **A4–A7** (ICP / силы / ценность / карта работ) — для полноты картины.

В запросах ниже фигурирует строка «Our product (context): …». В реальной работе это короткий контекст вашего продукта, чтобы модель понимала угол сравнения. В этом публичном примере он заменён на нейтральный плейсхолдер `{{МОЙ_ПРОДУКТ}}` — подставьте описание своего продукта одним предложением.

## A1 — Positioning + Core Job + artifact-check (→ блоки «позиционирование», «ценность»)

```
Use Deep Research. Cite a source + date for every claim (prefer 2024-2026).

Our product (context): {{МОЙ_ПРОДУКТ}}. Target competitor: Gong (gong.io), a revenue / conversation intelligence platform. Goal: find the actual customer JOB Gong removes — not Gong's marketing.

TAGGING — label every fact:
- [SITE] = Gong's own claim on its website (marketing — what they want you to believe).
- [CUSTOMER] = the customer's own words (from reviews / case studies / forums — the truth).
- [INFERRED] = your own reconstruction/guess (say so honestly).
- [BUZZWORD] = vague marketing with no number behind it.

Sources: gong.io homepage, product / platform pages, H1/H2 headlines.

Collect:
1. Exact one-liner / pitch + URL.
2. Value verbs from headlines as a LEVEL HYPOTHESIS: Big ("grow revenue" = wrapper promise), Core ("control / see what happens in deals"), Small/commodity ("record / transcribe calls").
3. ARTIFACT CHECK: for each Big promise, find proof (a named case study with attribution; a number with a measurement method). A Big promise with no proof → [PSEUDO-BIG]; downgrade it to the actual job it removes.
4. OBSERVABLE (not a label): which customer job Gong fully REMOVES (the customer stops doing X by hand), which it SHORTENS, which it shifts onto itself — quote each.
5. If the site has only Big slogans and no Core job → that's a signal (selling on emotion, Core hidden); reconstruct the likely Core job from the features and mark it [INFERRED].

Compare everything to the customer's status quo (manual review, spreadsheets, "doing nothing") — NOT to my product.
Format: numbered list; each point = fact + tag + quote + URL + date.
Final (1 line): Gong's actual Core-job level, and how it differs from the customer's status quo.
```

## A2 — Monetization / pricing packaging (→ блоки «монетизация», «упаковка»)

```
Use Deep Research. Cite a source + date for every claim (prefer 2024-2026).

Our product (context): {{МОЙ_ПРОДУКТ}}. Target competitor: Gong (gong.io). Goal: their MONETIZATION MODEL and where the price barrier is — not just the sticker price.

TAGGING — label every fact:
- [SITE] = Gong's own claim (pricing page, marketing).
- [CUSTOMER] = the customer's own words about price (G2 / Capterra / Reddit reviews — the truth).
- [INFERRED] = your reconstruction.
- [OPAQUE] = "flexible pricing / contact us" with no numbers.

Sources: gong.io/pricing, billing FAQ, price-related reviews (G2 / Capterra / Reddit).

Collect:
1. Model: subscription / per-seat / per-volume (calls or minutes) / platform fee. What exactly is the price "meter" (what they charge per).
2. Tier packaging: which tiers exist, and what JOB each higher tier UNLOCKS for the customer (not "tier features", but what the customer becomes ABLE to do). What is hidden in the top tier / "contact us".
3. Anchor & upsell: where the price starts, what raises the bill (extra seats, modules, platform fee).
4. Price barrier as ANXIETY (not just "expensive"): for which buyer role is the price a personal stake (budget / quota / risk in front of leadership)? Prefer [CUSTOMER] quotes over [SITE].
5. Hidden cost: contract terms (length, auto-renewal, cancellation penalty), entry threshold (implementation, training), and what reviews call "overpaying / using only half of it".
6. Status-quo comparison: their price vs "doing nothing" ($0) vs manual review (a manager's salary) — how do they justify the gap?

Format: the model + a table "tier | job it unlocks | price | barrier/anxiety | quote + URL".
Final (1 line): where their monetization leaves an unmet job or a barrier.
```

## A3 — Switch-timeline + GTM motion (→ блоки «путь клиента», «каналы»)

```
Use Deep Research. Cite a source + date for every claim (prefer 2024-2026).

Our product (context): {{МОЙ_ПРОДУКТ}}. Target competitor: Gong (gong.io). Goal: the customer's SWITCHING PATH and which stage of it Gong's go-to-market is built for. NOTE: this timeline is not stated on the site — RECONSTRUCT it from case studies / reviews and mark guesses [INFERRED].

TAGGING — label every fact:
- [SITE] = Gong's own claim (marketing).
- [CUSTOMER] = the customer's own words (reviews / case studies).
- [INFERRED] = your reconstruction.

Sources: case studies (especially "how they came to the decision"), reviews, "why us" pages, demo / trial pages, FAQ.

Collect:
1. The switching timeline by stage (Bob Moesta's "forces of progress" model) — for each stage: what triggers it, and whether there is [CUSTOMER] evidence or it is [INFERRED]:
   - First Thought (the first "we should change something" moment)
   - Passive Looking (casually reading / searching)
   - Active Looking (actively comparing options; on what criteria)
   - Deciding (what finally tips them — demo / pilot / case study / price)
   - Onboarding (first weeks; what must work so they don't churn back)
2. Which stage Gong's motion is built for (from content / CTAs): self-serve + open pricing + "start now" = catches Active / Deciding (fast buyers); demo + ROI calculator + white paper + "request a demo" = pulls from Passive (slow buyers).
3. Where the HOLE in the timeline is: which stage is not served.
4. Who decides / influences at each stage (buyer role) and their personal stake.

Compare to the customer's status quo, not to my product.
Format: a table "stage | trigger | evidence [CUSTOMER]/[INFERRED] | Gong's focus | hole".
Final (1 line): the timeline stage where Gong is weakest.
```

## A4 — ICP / segments + customer language + fast-slow funnel (→ блоки «ICP», «сегменты»)

```
Use Deep Research. Cite a source + date for every claim (prefer 2024-2026).

Our product (context): {{МОЙ_ПРОДУКТ}}. Target competitor: Gong (gong.io). Goal: WHO they sell to and in WHAT LANGUAGE — the edges of their ICP.

TAGGING — label every fact:
- [SITE] = Gong's own claim (marketing).
- [CUSTOMER] = the customer's own words (reviews / case studies).
- [INFERRED] = your reconstruction.

Sources: segment / industry landing pages, "customers / case studies", logos, reviews, pricing (a size proxy).

Collect:
1. Buyer roles (VP Sales, Sales Director, RevOps, Enablement, CRO) — whom the headlines and cases are written for.
2. Company size (seats / number of reps, revenue, enterprise vs SMB) — from logos and case numbers.
3. Industries — where strong, where clearly absent.
4. ICP edges: who it's explicitly NOT for ("from N reps", "for large teams").
5. LANGUAGE ratio: the buyer's personal job ("stop reviewing calls by hand", "you get control") vs the org's business job ("conversion +X%", "revenue") — approx % with quotes. A marker of the real ICP.
6. Pain — SPLIT: [SITE] (copywriter) vs [CUSTOMER] (quote from a review/case). Only the latter count.
7. Funnel fast vs slow: self-serve / open price / "start now" = fast; demo / consult / ROI calculator / white paper = slow. Only-fast → the slow segment (who deliberates) is open = niche; only-slow → the reverse.

Format: table "segment | buyer role | size | industry | fast/slow | quote + URL + date".
Final (2 lines): the core of their ICP + the segment they DON'T cover.
```

## A5 — Triggers + 4 forces (seller→customer) + alternatives (→ блоки «путь клиента», «сегменты»)

```
Use Deep Research. Cite a source + date (2024-2026).

Our product (context): {{МОЙ_ПРОДУКТ}}. Target competitor: Gong (gong.io). Goal: the 4 switching forces, triggers, and ALTERNATIVES (incl. invisible ones). NOTE: a website is polished PULL — push/anxiety/habit are mostly absent, so RECONSTRUCT them and mark [INFERRED].

TAGGING — label every fact:
- [SITE] = Gong's own claim.
- [CUSTOMER] = the customer's own words.
- [INFERRED] = your reconstruction.
- [NOT FOUND] = no evidence.

Sources: case studies, "why us / the problem" pages, FAQ, objection pages, reviews.

Collect:
1. The 4 forces. For EACH mark the source: [CUSTOMER] / [INFERRED] / [NOT FOUND]:
   - PUSH (problems with the old way), PULL (value of the new), ANXIETY (adoption fears — price, integration, "the team will resist"), HABIT (the status quo).
   If you take a push/pain from a slogan ("you lose revenue on bad calls"), that's a SELLER push: mark it [SITE] and translate it into a CUSTOMER one — which role, and their personal stake (bonus / firing / status before the owner / a burning deadline).
2. Struggling moment — score it on 6 markers (place / time / role / event / emotion / date), X/6. On a site expect 0-1/6 — note "not revealed" and reconstruct.
3. Visible alternatives — whom they directly compare to.
4. Invisible alternatives (the main ones — mandatory): a spreadsheet / a checklist, manual review by a team lead, training, audit agencies, "do nothing" — which they attack, which they ignore.

Format: a block per force (with a seller→customer column), a "trigger X/6" block, an alternatives table.
Final (1 line): which invisible alternative they DON'T close.
```

## A6 — Value as outcome + 3 energies + packaging/aha (→ блоки «ценность», «упаковка»)

```
Use Deep Research. Cite a source + date (2024-2026).

Our product (context): {{МОЙ_ПРОДУКТ}}. Target competitor: Gong (gong.io). Goal: value as a MEASURABLE customer outcome (not a vendor feature), what it removes, and the aha packaging.

TAGGING — label every fact:
- [SITE] = Gong's own claim.
- [CUSTOMER] = the customer's own words.
- [INFERRED] = your reconstruction.
- [BUZZWORD] = vague claim with no number.

Sources: homepage, pricing, demo / onboarding, case studies with numbers.

Collect:
1. ROI numbers → REALITY-CHECK: whose, sample size, method. Discount the optimism: claimed /2-3 (selection bias) − implementation drag − regression to the mean ≈ 30-40% real. Unsupported → [BUZZWORD].
2. EACH promise → a customer desired outcome: [reduce / increase] + [metric] + [object] + [context]. Model: not "speeds up call review" but "reduce the time a team lead spends finding the un-followed script in one call". Doesn't reduce to that → [BUZZWORD].
3. Energy efficiency across 3 energies: functional (hours / money), social (what the team thinks; will the team revolt), emotional (the lead's fear of looking bad before the owner). Which they address, which they ignore.
4. OBSERVABLE (not a mechanic number): which customer job it removes fully / shortens / lifts a level — quote each.
5. Time-to-value: when the first result appears; which metric moves FIRST.
6. Packaging / aha: visual devices (dashboard, scoring, demo report) that show value in 5 seconds.

Format: table "promise | customer outcome | number | supported? | which energy".
Final (1 line): Gong's strongest value lever.
```

## A7 — Weaknesses + over/under-served + job-map coverage + vector (→ блоки «слабости», «вектор»)

> Заметка из реальной работы: слабости и вектор Gong во многом уже собираются внешкой (**B1**, **B7** и видео-разбор). Главная уникальная ценность A7 — **карта покрытия работы по шагам** (пункт 4). Если время ограничено — гоните этот запрос только ради пункта 4.

```
Use Deep Research. Cite a source + date (2024-2026). Reviews = [CUSTOMER], the main source of truth here.

Our product (context): {{МОЙ_ПРОДУКТ}}. Target competitor: Gong (gong.io). Goal: real weaknesses, uncovered work steps, and the vector (where they're heading).

TAGGING: [SITE] / [CUSTOMER] / [INFERRED].

Sources: reviews (G2, Capterra, TrustRadius, Reddit), blog, job posts, news / releases.

Collect:
1. Frequent COMPLAINTS (price, complexity, accuracy, support, onboarding) — real quotes + source + date.
2. From NEGATIVE reviews reconstruct the FAILED switch: what the customer expected (pull) → what they hit (a new push) → why they reverted (habit won).
3. OVER-/UNDER-served with frequency: over-served = high share of "too complex / overpaying / use only half" × low importance → a simplification niche. Under-served = high importance × low satisfaction. 1 review = noise; 30%+ = signal.
4. JOB MAP coverage: break the team lead's work into steps [decide which calls to review → find the problem ones → diagnose the cause → give feedback to the rep → check they fixed it → track team dynamics]. Score Gong's coverage of each 0/1/2. The uncovered step (often the "coaching loop" — getting the rep to actually fix it) = a candidate gap.
5. SIGNAL CONVERGENCE (vector): 3+ independent signals — new buyer personas in recent cases (up-migration); SMB-CRM integrations / a lower threshold (move into the lower segment); hiring (enterprise sales? ML? partnerships?); blog themes 2025-2026. Conclude only if 3+ converge.

Format: a "complaints" block, a "failed switches" block, a "job-map step | coverage 0/1/2" table, a "signal | direction | source + date" table.
Final: a list of Gong's uncovered work steps (3-5 items).
```

---

# B. Внешние источники (взгляд рынка)

> Девять запросов на внешние сигналы. Методика и приоритеты сигналов — в [methodology/03-external-signals.md](../../methodology/03-external-signals.md). Самые ценные под такого конкурента: **B7** (где проигрывает), **B9** (отток), **B2** (найм), **A2** (монетизация — выше).

## B1 — Reviews & weaknesses (→ блок «слабости / точки внимания»)

```
Use Deep Research. Cite every claim with a source + date; prefer 2024-2026.
Context: competitive intelligence on Gong (gong.io), a revenue/conversation intelligence platform. I need its REAL weaknesses.
Research user reviews on G2, TrustRadius, Capterra, and Reddit (r/sales, r/salesforce).
Collect: 1. Most common COMPLAINTS (pricing, complexity, accuracy, support, onboarding, false positives). 2. What users praise. 3. Sentiment shift 2024→2026. 4. Specific feature gaps users wish existed.
Prioritize criticisms. Quote real review snippets with source + date.
```

## B2 — Hiring / LinkedIn (→ блок «вектор», сигнал направления #1)

```
Use Deep Research. Cite sources + dates; focus on the last 6-12 months.
Context: competitive intelligence on Gong (gong.io). Hiring is the #1 leading indicator of product direction.
Analyze Gong's current/recent job openings (LinkedIn, careers page, job boards).
Collect: 1. Which functions/teams they hire into most (AI/ML, product, eng, GTM, vertical sales). 2. New SPECIALIZED roles signaling direction (AI agents, MCP/interoperability, security/governance, new verticals). 3. Geographic expansion. 4. Seniority mix.
For each pattern, infer the strategic/product direction. Cite sources.
```

## B3 — Funding / M&A / financials (→ блоки «обзор», «вектор»)

```
Use Deep Research. Cite Crunchbase, PitchBook, press releases with dates. Focus 2023-2026.
Context: competitive intelligence on Gong (gong.io).
Collect: 1. Funding history: total raised, last round, valuation, lead investors. 2. Reported revenue/ARR and growth rate. 3. Acquisitions by Gong (which, why). 4. Major partnerships.
For each acquisition/partnership, note the strategic signal.
```

## B4 — Blog / content agenda (→ блоки «контент», «вектор»)

```
Use Deep Research. Cite article titles + dates. Focus 2024-2026.
Context: competitive intelligence on Gong (gong.io/blog) and their thought-leadership (incl. "Gong Labs").
Collect: 1. Dominant TOPICS/themes they push most. 2. New categories/terms (vs a year earlier). 3. What the content agenda reveals about direction.
List themes with example article titles/dates.
```

## B5 — News / press / events (→ блоки «вектор», «контент»)

```
Use Deep Research. Cite with dates. Focus 2025-2026.
Context: competitive intelligence on Gong (gong.io).
Collect major news: product launches (Gong Missions / Mission Andromeda, MCP, AI agents), ARR milestones, leadership changes, conferences (Celebrate), regulatory/security moves.
For each event, note the strategic signal.
```

## B6 — Analysts & market position (→ блок «позиция на рынке»)

```
Use Deep Research. Cite analyst reports + dates. Focus 2024-2026.
Context: competitive intelligence on Gong (gong.io) in revenue / conversation intelligence / sales engagement.
How do analysts (Gartner, Forrester, G2 Grid) position Gong vs competitors (Clari, Chorus/ZoomInfo, Salesloft, Outreach, Salesforce)?
Collect: Magic Quadrant / Forrester Wave placements, G2 Grid leader status, market-share estimates, and how analysts describe Gong's strengths AND weaknesses.
```

## B7 — Head-to-head vs competitors (→ блок «где проигрывает»)

```
Use Deep Research. Cite sources + dates. Focus 2024-2026.
Context: Gong (gong.io) rarely names competitors itself, so I need the market's view.
Find head-to-head comparisons: Gong vs Clari, Gong vs Chorus (ZoomInfo), Gong vs Salesloft/Outreach, Gong vs AI-native (Sybill, Avoma, Fireflies, tl;dv).
For each: where Gong WINS, where it LOSES, and what buyers say when they pick a competitor OVER Gong. Prioritize the losses.
```

## B8 — Tech-stack / integrations (→ блоки «монетизация», «упаковка»)

```
Use Deep Research. Cite BuiltWith/Wappalyzer/official docs + dates. Focus 2025-2026.
Context: competitive intelligence on Gong (gong.io).
Collect: key integrations and partner ecosystem (which CRMs and tools), and any NEW integrations in 2025-2026.
What does the integration roadmap signal about platform strategy?
```

## B9 — Social tonality / churn / switching (→ блок «отток / тональность»)

```
Use Deep Research. Cite sources with quotes. Focus 2025-2026.
Context: competitive intelligence on Gong (gong.io).
Analyze market sentiment and switching dynamics from Reddit (r/sales, r/salesforce), X/Twitter, and communities. Who is switching AWAY from Gong and to what (tl;dv, Fireflies, Avoma, Chorus, Clari, Sybill)? What reasons do they cite? Overall tonality trend?
Quote real posts with source links.
```

---

**Куда складывать ответы.** У каждого запроса в скобках указан блок досье. Собирайте ответы в каркас из [examples/gong/dossier-skeleton.md](dossier-skeleton.md), а отдельные источники разбирайте по шаблону [templates/source-breakdown.md](../../templates/source-breakdown.md) и заносите в реестр [templates/source-registry.md](../../templates/source-registry.md).

**Дальше по комбайну:** видео-разбор конкурента — через [prompts/notebooklm-video-pack.md](../../prompts/notebooklm-video-pack.md) (заполненный пример: [examples/gong/notebooklm-pack-filled.md](notebooklm-pack-filled.md)); итоговая battlecard — [templates/battlecard.md](../../templates/battlecard.md).

> Что брать на свой счёт: эти запросы дают **факты и карту** конкурента. Решение, что с этой картой делать в вашем продукте, — отдельный шаг уже под ваш `{{МОЙ_ПРОДУКТ}}`, и он не входит в этот пример сбора.
