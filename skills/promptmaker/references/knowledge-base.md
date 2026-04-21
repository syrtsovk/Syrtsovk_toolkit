<?xml version="1.0" encoding="UTF-8"?>

<!--
═══════════════════════════════════════════════════════════════════════════
PROMPTMAKER v2.0 — БАЗА ЗНАНИЙ
Компактная версия, организованная по нишам для быстрого извлечения
═══════════════════════════════════════════════════════════════════════════
-->

<knowledge_base version="2.0">

<!-- ═══════════════════════════════════════════════════════════════════
     ЧАСТЬ 1: УНИВЕРСАЛЬНЫЕ ПРИНЦИПЫ (применимы ко всем нишам)
     ═══════════════════════════════════════════════════════════════════ -->

<universal_principles>

<principle name="modular_architecture">
<description>
Любой профессиональный промпт состоит из чётко разделённых модулей с использованием XML-тегов для структурирования. Модули: роль → специализация → знания → поведение → примеры → мышление → выполнение → метрики → запреты.
</description>
</principle>

<principle name="positioning_optimization">
<description>
LLM демонстрируют U-образную кривую внимания: информация в первых 10% и последних 15% промпта получает максимальное внимание. Середина — "мёртвая зона" с деградацией внимания до 40%. Размещай критическую информацию (роль, ограничения, инструкции по выполнению) в начале и конце.
</description>
</principle>

<principle name="specificity_over_abstraction">
<description>
Всегда заменяй абстрактные формулировки конкретными с численными параметрами:
- ❌ "эксперт с опытом" → ✅ "эксперт с 12 годами опыта в сфере X"
- ❌ "используй лучшие практики" → ✅ "используй методологию STAR для поведенческих интервью"
- ❌ "детальный ответ" → ✅ "ответ с ≥3 конкретными рекомендациями, каждая с обоснованием"
</description>
</principle>

<principle name="examples_mandatory">
<description>
Для любого неочевидного элемента поведения включай минимум 2 развёрнутых примера (80-200 слов в зависимости от сложности задачи). Примеры должны демонстрировать разные сценарии: работа с новичком, решение продвинутой задачи, разоблачение мифа/ошибки, анализ спорной ситуации, структурирование сложной темы.
</description>
</principle>

<principle name="imperative_voice">
<description>
Инструкции формулируй в повелительном наклонении с активным залогом:
- ❌ "можно применить метод X" → ✅ "Примени метод X для задач типа Y"
- ❌ "следует учитывать фактор Z" → ✅ "Учитывай фактор Z при условии W"
</description>
</principle>

<principle name="measurable_metrics">
<description>
Всегда определяй измеримые критерии успеха с численными порогами (≥, ≤, =). Включай метрики в модуль quality_metrics с конкретными значениями.
</description>
</principle>

</universal_principles>

<!-- ═══════════════════════════════════════════════════════════════════
     ЧАСТЬ 2: МОДЕЛИ МЫШЛЕНИЯ (Thinking Models)
     7 ключевых моделей для разных типов задач
     ═══════════════════════════════════════════════════════════════════ -->

<thinking_models>

<model name="Chain of Thought v2">
<description>Пошаговое рассуждение с явной вербализацией промежуточных шагов и логических связей.</description>
<best_for>Сложные аналитические задачи, математические расчёты, многоступенчатые процессы, логический вывод.</best_for>
<prompt_integration>
"Для сложных аналитических задач используй Chain of Thought:
1. Разбей задачу на подзадачи с явными зависимостями
2. Вербализуй рассуждение на каждом шаге (объясняй ПОЧЕМУ делаешь этот шаг)
3. Покажи промежуточные результаты
4. Проверь логику перед финальным выводом
5. Убедись, что каждый шаг логически следует из предыдущего"
</prompt_integration>
</model>

<model name="ReAct++ (Reasoning + Acting)">
<description>Интеграция рассуждения и действия в едином цикле: думай → действуй → наблюдай → повтори.</description>
<best_for>Задачи, требующие взаимодействия с инструментами, API, базами данных, поиска информации.</best_for>
<prompt_integration>
"Используй ReAct++ для задач с инструментами:
- Thought (рассуждение): Объясни, что нужно сделать, почему и какой результат ожидается
- Action (действие): Выполни конкретное действие (вызов API, запрос данных, поиск)
- Observation (наблюдение): Проанализируй полученный результат
- Repeat (повтор): Продолжи цикл до достижения цели или максимум N итераций"
</prompt_integration>
</model>

<model name="Tree of Thoughts">
<description>Исследование множественных путей решения с оценкой и выбором оптимального варианта.</description>
<best_for>Творческие задачи, стратегическое планирование, задачи с множеством возможных решений, оптимизация.</best_for>
<prompt_integration>
"Для креативных и стратегических задач применяй Tree of Thoughts:
1. Сгенерируй 3-5 альтернативных подходов/решений
2. Для каждого подхода оцени: осуществимость, эффективность, риски, ресурсы
3. Сравни альтернативы по критериям [указать конкретные критерии]
4. Выбери оптимальный путь с обоснованием
5. Разверни выбранное решение детально"
</prompt_integration>
</model>

<model name="Self-Consistency">
<description>Генерация нескольких вариантов решения с последующей агрегацией или выбором наиболее согласованного.</description>
<best_for>Задачи, где критична стабильность и надёжность результата; задачи с высокими ставками; валидация решений.</best_for>
<prompt_integration>
"Для критически важных задач используй Self-Consistency:
1. Сгенерируй 3-5 независимых вариантов решения (с разными подходами)
2. Сравни результаты, найди общие элементы и различия
3. Если результаты согласуются — используй консенсусное решение
4. Если различаются — проанализируй причины и выбери наиболее обоснованный вариант
5. В финальном ответе упомяни степень уверенности"
</prompt_integration>
</model>

<model name="Meta-Reasoning">
<description>Рассуждение о собственном процессе мышления: выбор оптимальной стратегии решения перед началом работы.</description>
<best_for>Сложные нестандартные задачи; ситуации неопределённости; выбор методологии.</best_for>
<prompt_integration>
"Перед решением сложной или нестандартной задачи:
1. Проанализируй тип задачи (аналитическая? креативная? требует инструментов?)
2. Определи, какая модель мышления оптимальна (Chain of Thought? Tree of Thoughts? ReAct?)
3. Объясни выбор стратегии (почему именно эта модель подходит)
4. Примени выбранную стратегию
5. После решения оцени: была ли стратегия оптимальной? что можно улучшить?"
</prompt_integration>
</model>

<model name="Socratic Questioning">
<description>Метод обучения и анализа через серию целенаправленных вопросов, которые ведут к глубокому пониманию.</description>
<best_for>Обучающие задачи, консультирование, помощь в прояснении мыслей пользователя, анализ предпосылок.</best_for>
<prompt_integration>
"Для обучающих и консультационных задач применяй Socratic Questioning:
1. Задавай уточняющие вопросы для понимания контекста и целей
2. Помогай пользователю сформулировать проблему через вопросы
3. Используй последовательность вопросов: прояснение → предпосылки → причины → альтернативы → последствия
4. Не давай готовых решений сразу — веди к ним через вопросы
5. Подводи итоги: чему научились, что поняли"
</prompt_integration>
</model>

<model name="SWOT Analysis">
<description>Структурированный анализ по четырём измерениям: Strengths (сильные стороны), Weaknesses (слабости), Opportunities (возможности), Threats (угрозы).</description>
<best_for>Стратегическое планирование, оценка бизнес-идей, анализ конкурентов, принятие решений.</best_for>
<prompt_integration>
"Для стратегических и бизнес-задач используй SWOT Analysis:
1. Strengths: Определи сильные стороны (внутренние преимущества)
2. Weaknesses: Выяви слабости (внутренние ограничения)
3. Opportunities: Найди возможности (внешние благоприятные факторы)
4. Threats: Проанализируй угрозы (внешние риски)
5. Сформулируй стратегию на основе SWOT: как использовать сильные стороны для возможностей, как компенсировать слабости, как защититься от угроз"
</prompt_integration>
</model>

</thinking_models>

<!-- ═══════════════════════════════════════════════════════════════════
     ЧАСТЬ 3: ДОМЕНЫ ЗНАНИЙ
     10 основных ниш с компетенциями, источниками и методологиями
     ═══════════════════════════════════════════════════════════════════ -->

<domains>

<!-- МАРКЕТИНГ -->
<domain name="marketing">
<competencies>
- Разработка маркетинговых стратегий (4P/7P, SOSTAC framework)
- Анализ целевой аудитории (Jobs To Be Done, Customer Journey Mapping, персоны)
- Digital-маркетинг (SEO, PPC, SMM, Content Marketing, Email Marketing, Influencer)
- Аналитика и метрики (Google Analytics, Amplitude, когортный анализ, LTV, CAC)
- Воронки продаж (AARRR Pirate Metrics, конверсионная оптимизация)
- Brand positioning, messaging, storytelling
- Growth hacking и viral loops
- Marketing automation и CRM
</competencies>
<key_sources>
- Филип Котлер: "Основы маркетинга", "Marketing 4.0", "Маркетинг от А до Я"
- Сет Годин: "Это маркетинг", "Purple Cow", "Permission Marketing"
- Джон Янч: "Duct Tape Marketing"
- Дэн Кеннеди: "No B.S. Direct Marketing", "Ultimate Sales Letter"
- Райан Холидей: "Growth Hacker Marketing"
- Eugene Schwartz: "Breakthrough Advertising"
- Byron Sharp: "How Brands Grow"
- Исследования: McKinsey Marketing Insights, HubSpot State of Marketing, Gartner CMO reports
</key_sources>
<methodologies>
- SOSTAC: Situation → Objectives → Strategy → Tactics → Actions → Control
- Customer Journey Mapping: 5 этапов (Awareness → Consideration → Purchase → Retention → Advocacy)
- Jobs To Be Done (JTBD): фокус на "работу", которую продукт выполняет для клиента
- Pirate Metrics (AARRR): Acquisition → Activation → Retention → Referral → Revenue
- ICE Score: Impact × Confidence × Ease (для приоритизации экспериментов)
- North Star Metric: единая метрика, отражающая ценность для клиента
- Hook Model (Nir Eyal): Trigger → Action → Variable Reward → Investment
</methodologies>
</domain>

<!-- ПРОГРАММИРОВАНИЕ -->
<domain name="software_development">
<competencies>
- Архитектура ПО (MVC, MVVM, Clean Architecture, Hexagonal, Microservices, Event-Driven)
- Backend разработка (REST API, GraphQL, WebSockets, gRPC)
- Frontend разработка (React, Vue, Angular, state management, component architecture)
- Базы данных (SQL оптимизация, NoSQL patterns, индексирование, шардинг, репликация)
- DevOps (CI/CD, Docker, Kubernetes, Infrastructure as Code, мониторинг, логирование)
- Тестирование (Unit, Integration, E2E, TDD, BDD, Test Pyramid)
- Безопасность (OWASP Top 10, аутентификация, авторизация, шифрование)
- Code quality (рефакторинг, code review, статический анализ, tech debt management)
</competencies>
<key_sources>
- Robert C. Martin: "Clean Code", "Clean Architecture", "Agile Software Development"
- Martin Fowler: "Refactoring", "Patterns of Enterprise Application Architecture", "UML Distilled"
- Eric Evans: "Domain-Driven Design"
- Gang of Four: "Design Patterns: Elements of Reusable Object-Oriented Software"
- Michael Feathers: "Working Effectively with Legacy Code"
- Kent Beck: "Test-Driven Development By Example", "Extreme Programming Explained"
- Gene Kim: "The Phoenix Project", "The DevOps Handbook"
- Sam Newman: "Building Microservices"
</key_sources>
<methodologies>
- SOLID принципы: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- DRY (Don't Repeat Yourself) и противоположность — WET (Write Everything Twice)
- YAGNI (You Aren't Gonna Need It): не пиши код "на будущее"
- KISS (Keep It Simple, Stupid): простота важнее clever solutions
- Test-Driven Development (TDD): Red → Green → Refactor
- Behavior-Driven Development (BDD): Given → When → Then
- Domain-Driven Design: Ubiquitous Language, Bounded Contexts, Aggregates
- Trunk-Based Development: короткоживущие ветки, частые коммиты в main
- Twelve-Factor App: методология для cloud-native приложений
</methodologies>
</domain>

<!-- HR И РЕКРУТИНГ -->
<domain name="hr_recruitment">
<competencies>
- Подбор персонала (sourcing, скрининг, интервьюирование, оффер-менеджмент)
- Структурированные интервью (поведенческие, кейсовые, технические)
- Оценка компетенций (assessment centers, психометрические тесты, 360-degree feedback)
- Employer branding и кандидатский опыт
- Onboarding и адаптация новых сотрудников
- Performance management (постановка целей, обратная связь, PIP)
- Talent development (карьерные треки, succession planning)
- Компенсации и бенефиты (salary benchmarking, equity, benefits design)
</competencies>
<key_sources>
- Марк Мёрфи: "Interviewing по компетенциям", "Hiring for Attitude"
- Джефф Смарт, Рэнди Стрит: "Кто. Решите вашу проблему номер один" (Who: The A Method)
- Patty McCord: "Powerful: Building a Culture of Freedom and Responsibility" (Netflix culture)
- Laszlo Bock: "Work Rules!" (Google HR practices)
- Kim Scott: "Radical Candor"
- Marcus Buckingham: "First, Break All the Rules"
- Стандарты: SHRM (Society for Human Resource Management), HRCI certifications
</key_sources>
<methodologies>
- STAR метод: Situation → Task → Action → Result (для поведенческих интервью)
- SWOT анализ кандидата: Strengths, Weaknesses, Opportunities, Threats
- GROW модель (для коучинга): Goal → Reality → Options → Will
- OKR (Objectives and Key Results): для целеполагания и performance management
- 9-Box Grid: для talent review и succession planning
- Competency Framework: определение ключевых компетенций для ролей
- Assessment Center Method: комплексная оценка через симуляции и упражнения
</methodologies>
</domain>

<!-- ФИНАНСЫ И ИНВЕСТИЦИИ -->
<domain name="finance_investment">
<competencies>
- Финансовый анализ (отчётность, коэффициенты, DCF, NPV, IRR)
- Инвестиционная стратегия (value investing, growth investing, portfolio theory)
- Управление рисками (VaR, stress testing, hedging strategies)
- Корпоративные финансы (структура капитала, M&A, финмоделирование)
- Рынки капитала (акции, облигации, деривативы, альтернативные инвестиции)
- Behavioral finance (психология инвестора, cognitive biases)
- ESG investing (environmental, social, governance factors)
- Financial planning (бюджетирование, налоговое планирование, retirement planning)
</competencies>
<key_sources>
- Benjamin Graham: "The Intelligent Investor", "Security Analysis"
- Warren Buffett: годовые письма акционерам Berkshire Hathaway
- Burton Malkiel: "A Random Walk Down Wall Street"
- Aswath Damodaran: "Investment Valuation", "The Little Book of Valuation"
- Howard Marks: "The Most Important Thing", мемосы Oaktree Capital
- Daniel Kahneman: "Thinking, Fast and Slow" (behavioral finance)
- John Bogle: "The Little Book of Common Sense Investing"
- McKinsey Valuation (Koller, Goedhart, Wessels): "Valuation"
</key_sources>
<methodologies>
- DCF (Discounted Cash Flow): оценка через дисконтирование будущих денежных потоков
- Comparable Company Analysis: оценка через мультипликаторы (P/E, EV/EBITDA)
- Modern Portfolio Theory (Markowitz): оптимизация портфеля через диверсификацию
- Capital Asset Pricing Model (CAPM): расчёт ожидаемой доходности актива
- DuPont Analysis: декомпозиция ROE на операционную эффективность, asset efficiency, leverage
- Monte Carlo simulation: моделирование для оценки рисков
- Technical Analysis: price action, chart patterns, indicators
</methodologies>
</domain>

<!-- КОПИРАЙТИНГ И КОНТЕНТ -->
<domain name="copywriting_content">
<competencies>
- Persuasive writing (AIDA, PAS, FAB frameworks)
- SEO-копирайтинг (keyword research, on-page optimization, readability)
- Email-маркетинг (subject lines, body copy, CTAs, segmentation)
- Landing page copy (value propositions, headlines, social proof)
- Storytelling и narrative structures
- Brand voice development
- Content strategy (planning, creation, distribution, measurement)
- Conversion Rate Optimization (CRO) через копирайтинг
</competencies>
<key_sources>
- Eugene Schwartz: "Breakthrough Advertising" (классика persuasion)
- Robert Cialdini: "Influence: The Psychology of Persuasion"
- Ann Handley: "Everybody Writes", "Content Rules"
- Joe Sugarman: "The Adweek Copywriting Handbook"
- Gary Halbert: "The Boron Letters"
- Joseph Sugarman: "Triggers"
- Donald Miller: "Building a StoryBrand"
- Joanna Wiebe (Copyhackers): обучающие материалы по conversion copywriting
</key_sources>
<methodologies>
- AIDA: Attention → Interest → Desire → Action (классическая воронка)
- PAS: Problem → Agitate → Solve (усиливаем боль, затем предлагаем решение)
- FAB: Features → Advantages → Benefits (от характеристик к выгодам)
- 4 C's of Copywriting: Clear, Concise, Compelling, Credible
- Bucket Brigade: техника удержания внимания через коннекторы
- PASTOR: Problem → Amplify → Story → Transformation → Offer → Response
- The Hero's Journey: структура сторителлинга (12-этапный путь героя)
</methodologies>
</domain>

<!-- ПРОДАЖИ -->
<domain name="sales">
<competencies>
- Консультативные продажи (SPIN Selling, Solution Selling)
- B2B продажи (enterprise sales, account management, deal structuring)
- Управление воронкой продаж (pipeline management, forecasting)
- Переговоры и работа с возражениями
- Презентации и демонстрации продукта
- Closing techniques
- Relationship building и networking
- Sales enablement (инструменты, процессы, обучение)
</competencies>
<key_sources>
- Neil Rackham: "SPIN Selling" (ключевая методология для B2B)
- Jeffrey Gitomer: "The Sales Bible", "Little Red Book of Selling"
- Jill Konrath: "SNAP Selling", "Agile Selling"
- Matthew Dixon, Brent Adamson: "The Challenger Sale"
- Mike Weinberg: "New Sales. Simplified."
- Chet Holmes: "The Ultimate Sales Machine"
- Grant Cardone: "Sell or Be Sold"
- Aaron Ross: "Predictable Revenue" (о создании sales machine)
</key_sources>
<methodologies>
- SPIN Selling: Situation → Problem → Implication → Need-Payoff questions
- MEDDIC: Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion
- Sandler Selling System: Pain → Budget → Decision → строительство доверия
- Challenger Sale: Teach → Tailor → Take Control
- Solution Selling: understand buyer's journey и align с этапами
- BANT: Budget, Authority, Need, Timeline (квалификация лидов)
- ABC (Always Be Closing): техники закрытия на каждом этапе
</methodologies>
</domain>

<!-- УПРАВЛЕНИЕ ПРОЕКТАМИ -->
<domain name="project_management">
<competencies>
- Методологии управления проектами (Waterfall, Agile, Scrum, Kanban, Hybrid)
- Планирование проектов (WBS, Gantt charts, Critical Path Method)
- Управление рисками (идентификация, оценка, митигация)
- Управление стейкхолдерами и коммуникациями
- Бюджетирование и контроль затрат
- Quality management
- Resource allocation и team management
- Change management
</competencies>
<key_sources>
- PMBOK Guide (Project Management Body of Knowledge) — стандарт PMI
- Scrum Guide (Jeff Sutherland, Ken Schwaber) — официальная документация Scrum
- Henrik Kniberg: "Scrum and XP from the Trenches"
- Mike Cohn: "User Stories Applied", "Agile Estimating and Planning"
- Jeff Sutherland: "Scrum: The Art of Doing Twice the Work in Half the Time"
- Eliyahu Goldratt: "Critical Chain" (Theory of Constraints для PM)
- Rita Mulcahy: "PMP Exam Prep" (для сертификации PMP)
- Kanban Guide (David Anderson)
</key_sources>
<methodologies>
- Waterfall: последовательные фазы (Initiation → Planning → Execution → Monitoring → Closing)
- Scrum: спринты 1-4 недели, роли (PO, SM, Team), церемонии (Planning, Daily, Review, Retro)
- Kanban: визуализация потока, WIP limits, continuous flow
- Critical Path Method (CPM): определение критического пути через сетевой график
- Earned Value Management (EVM): интеграция scope, schedule, cost для контроля
- Risk Matrix: вероятность × impact для приоритизации рисков
- RACI Matrix: Responsible, Accountable, Consulted, Informed
- Agile ceremonies: Sprint Planning, Daily Standup, Sprint Review, Retrospective
</methodologies>
</domain>

<!-- ДИЗАЙН И UX/UI -->
<domain name="design_ux_ui">
<competencies>
- User Research (интервью, surveys, usability testing, persona development)
- Information Architecture (структура, навигация, taxonomy)
- Interaction Design (flows, wireframes, prototypes)
- Visual Design (типографика, цвет, композиция, брендинг)
- Usability principles (Nielsen's heuristics, accessibility, WCAG)
- Design Systems (компоненты, patterns, guidelines)
- Mobile-first и responsive design
- Conversion-focused design (CRO)
</competencies>
<key_sources>
- Don Norman: "The Design of Everyday Things" (основы UX)
- Steve Krug: "Don't Make Me Think" (usability)
- Jakob Nielsen: статьи Nielsen Norman Group, "Usability Engineering"
- Alan Cooper: "About Face: The Essentials of Interaction Design"
- Luke Wroblewski: "Mobile First"
- Jared Spool: статьи UIE (User Interface Engineering)
- Refactoring UI (Adam Wathan, Steve Schoger): практические советы
- Material Design Guidelines (Google), Human Interface Guidelines (Apple)
</key_sources>
<methodologies>
- Design Thinking: Empathize → Define → Ideate → Prototype → Test
- Double Diamond: Discover → Define → Develop → Deliver
- Jobs To Be Done (JTBD): фокус на "работу" пользователя
- Nielsen's 10 Usability Heuristics: visibility, match system/world, user control, consistency, error prevention, recognition vs recall, flexibility, aesthetic, help users with errors, documentation
- F-Pattern и Z-Pattern: паттерны сканирования контента
- Atomic Design (Brad Frost): atoms → molecules → organisms → templates → pages
- 8pt Grid System: для консистентности spacing и sizing
- Accessibility standards: WCAG 2.1 (A, AA, AAA levels)
</methodologies>
</domain>

<!-- ЮРИСПРУДЕНЦИЯ -->
<domain name="legal">
<competencies>
- Договорное право (составление, анализ, переговоры по договорам)
- Корпоративное право (структурирование, governance, M&A)
- Интеллектуальная собственность (патенты, авторские права, товарные знаки)
- Трудовое право (контракты, увольнения, dispute resolution)
- Защита данных (GDPR, CCPA, privacy policies)
- Litigation и dispute resolution
- Compliance и regulatory matters
- Legal research и case law analysis
</competencies>
<key_sources>
- Законодательство: гражданский кодекс, трудовой кодекс, налоговый кодекс (зависит от юрисдикции)
- Richard Susskind: "Tomorrow's Lawyers", "The End of Lawyers?"
- Bryan Garner: "Legal Writing in Plain English"
- Practitioner guides: "Drafting Contracts" (Tina Stark), "Model Business Corporation Act"
- Case law databases: LexisNexis, Westlaw, Google Scholar
- Стандарты: ABA (American Bar Association), Law Society standards
- GDPR text и official guidance (для data protection)
</key_sources>
<methodologies>
- IRAC: Issue → Rule → Application → Conclusion (для legal analysis)
- Due Diligence Checklist: систематическая проверка при M&A
- Contract Drafting Best Practices: clarity, completeness, consistency, consideration
- Legal Risk Matrix: вероятность × impact × controllability
- Alternative Dispute Resolution (ADR): mediation, arbitration (вместо litigation)
- Privacy by Design: встраивание защиты данных на этапе проектирования
- Compliance Framework: policies → procedures → monitoring → enforcement
</methodologies>
</domain>

<!-- МЕДИЦИНА И ЗДОРОВЬЕ -->
<domain name="healthcare_medicine">
<competencies>
- Клиническая диагностика (анамнез, physical examination, differential diagnosis)
- Evidence-based medicine (систематические обзоры, meta-analyses, clinical guidelines)
- Фармакология (механизмы действия, показания, противопоказания, взаимодействия)
- Patient care и communication
- Medical ethics (автономия, благодеяние, непричинение вреда, справедливость)
- Healthcare systems и public health
- Preventive medicine и wellness
- Telemedicine и digital health
</competencies>
<key_sources>
- Harrison's Principles of Internal Medicine (стандарт для врачей)
- UpToDate (evidence-based clinical decision support)
- The Cochrane Library (систематические обзоры)
- Clinical Practice Guidelines: NICE (UK), CDC (US), WHO
- Atul Gawande: "The Checklist Manifesto", "Being Mortal"
- Jerome Groopman: "How Doctors Think"
- Eric Topol: "Deep Medicine", "The Patient Will See You Now"
- Medical journals: NEJM, Lancet, JAMA, BMJ
</key_sources>
<methodologies>
- SOAP Notes: Subjective → Objective → Assessment → Plan (для документации)
- Differential Diagnosis: systematic approach через symptom clusters
- Evidence Pyramid: case reports → case-control → cohort → RCTs → systematic reviews
- PICO Framework: Patient/Problem → Intervention → Comparison → Outcome (для research questions)
- Shared Decision Making: информирование пациента + учёт предпочтений
- Quality Improvement: Plan-Do-Study-Act (PDSA) cycles
- Risk Stratification: для preventive medicine и screening
- Four Principles of Medical Ethics: autonomy, beneficence, non-maleficence, justice
</methodologies>
</domain>

<!-- ПСИХОЛОГИЯ И КОУЧИНГ -->
<domain name="psychology_coaching">
<competencies>
- Психологическая оценка (интервью, тестирование, наблюдение)
- Терапевтические подходы (CBT, ACT, psychodynamic, humanistic)
- Коучинговые техники (goal-setting, powerful questions, accountability)
- Мотивация и behavior change
- Эмоциональный интеллект
- Конфликт-менеджмент
- Групповая динамика и team coaching
- Wellness и stress management
</competencies>
<key_sources>
- Daniel Kahneman: "Thinking, Fast and Slow" (cognitive psychology)
- Carol Dweck: "Mindset: The New Psychology of Success"
- Martin Seligman: "Learned Optimism", "Authentic Happiness" (positive psychology)
- Brene Brown: "Dare to Lead", "The Gifts of Imperfection"
- Marshall Goldsmith: "What Got You Here Won't Get You There"
- Timothy Gallwey: "The Inner Game of Tennis" (performance coaching)
- John Whitmore: "Coaching for Performance" (GROW model)
- ICF (International Coach Federation): Core Competencies
</key_sources>
<methodologies>
- GROW Model: Goal → Reality → Options → Will (структура коучинговой сессии)
- Cognitive Behavioral Therapy (CBT): мысли → эмоции → поведение
- Acceptance and Commitment Therapy (ACT): psychological flexibility через acceptance + values
- Motivational Interviewing: evoke intrinsic motivation через открытые вопросы
- SMART Goals: Specific, Measurable, Achievable, Relevant, Time-bound
- Wheel of Life: оценка баланса по 8-10 сферам жизни
- Johari Window: self-awareness через 4 квадранта (open, blind, hidden, unknown)
- Stages of Change (Prochaska): precontemplation → contemplation → preparation → action → maintenance
</methodologies>
</domain>

</domains>

<!-- ═══════════════════════════════════════════════════════════════════
     ЧАСТЬ 4: ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ
     ═══════════════════════════════════════════════════════════════════ -->

<additional_resources>

<cross_domain_principles>
<principle name="first_principles_thinking">
Разбивай сложные проблемы на фундаментальные истины и строй решение снизу вверх. Применимо во всех доменах для инноваций и нестандартных решений.
</principle>

<principle name="pareto_principle">
80/20 rule: 80% результатов приходят из 20% усилий. Используй для приоритизации задач, фокусировки на ключевых факторах.
</principle>

<principle name="occams_razor">
Простейшее объяснение/решение обычно правильное. При множественных гипотезах выбирай наименее сложную.
</principle>

<principle name="feedback_loops">
Устанавливай быстрые циклы обратной связи для continuous improvement во всех доменах. Применимо от продуктовой разработки до личного развития.
</principle>
</cross_domain_principles>

<format_examples>
<simple_task_example>
Пример структуры для ПРОСТОЙ задачи (копирайтер для социальных сетей):
- core_role: 1-2 абзаца
- specialization: 3 компетенции
- behavioral_logic: краткие правила стиля
- execution_instructions: 5 шагов
- quality_metrics: 3-4 метрики
Итого: ~2500-3500 символов
</simple_task_example>

<complex_task_example>
Пример структуры для СЛОЖНОЙ задачи (стратегический бизнес-консультант):
- core_role: 4-5 абзацев с контекстом индустрии
- specialization: 10 детальных компетенций
- knowledge_base: глобальный + локальный + микро уровни (15+ источников)
- behavioral_logic: детальная с коммуникационным стилем
- behavior_examples: 7 развёрнутых примеров по 200+ слов
- thinking_models: 5 моделей с кейсами применения
- execution_instructions: 12+ шагов с подшагами
- quality_metrics: 8-10 детальных метрик
- prohibited_patterns: развёрнутый список с объяснениями
- internal_memory: контекст, цели, термины
Итого: ~12000-18000 символов
</complex_task_example>
</format_examples>

</additional_resources>

</knowledge_base>
