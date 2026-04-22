# База знаний: UX/UI и визуальный дизайн

> Справочник для формирования грамотных промптов и общения с дизайн-инструментами. Используется как второй источник знаний скилла.

## Оглавление

1. [Современные стили визуального дизайна](#1-современные-стили-визуального-дизайна)
2. [Типографика](#2-типографика)
3. [Цвет](#3-цвет)
4. [UX: методология и процессы](#4-ux-методология-и-процессы)
5. [UI: компоненты и паттерны](#5-ui-компоненты-и-паттерны)
6. [Дизайн-системы](#6-дизайн-системы)
7. [Инструменты](#7-инструменты)
8. [Accessibility](#8-accessibility)
9. [Профессиональный словарь](#9-профессиональный-словарь)
10. [Тренды 2024–2025](#10-тренды-20242025)
11. [Сетки и пространство](#11-сетки-и-пространство)
12. [Иконки и иллюстрации](#12-иконки-и-иллюстрации)
13. [UX Writing](#13-ux-writing)
14. [Метрики и KPI](#14-метрики-и-kpi)

---

## 1. Современные стили визуального дизайна

### Glassmorphism (матовое стекло)
Полупрозрачные слои с размытием фона, тонкой обводкой и тенью.
- `background: rgba(255,255,255,0.15)` + `backdrop-filter: blur(20px)`
- Поверх градиентных или фотографических фонов
- **Когда:** дашборды, мобильные приложения, презентационные сайты
- **Примеры:** iOS, macOS Ventura+, Microsoft Fluent Design

### Neumorphism
Элементы «выдавлены» или «вдавлены» в поверхность. Две тени — светлая и тёмная.
- Монохромный фон + двойная box-shadow
- Низкий контраст — провалил WCAG
- **Когда:** концепт-дизайн, умные устройства, аудио-плееры
- В реальных продуктах используется редко

### Neobrutalism
Антидизайн — грубые границы, жирные обводки, плоские тени со смещением, дерзкие цвета.
- `border: 2px-4px solid #000`
- `box-shadow: 4px 4px 0px #000`
- Смелые цвета: жёлтый, лайм, коралловый
- Grotesk-шрифты с большим весом
- **Когда:** стартапы, молодёжные продукты, лендинги
- **Примеры:** Gumroad, Framer (частично), Linear (частично)

### Claymorphism
3D-объекты с «глиняной» текстурой — раздутые, пастельные, с внутренними тенями.
- `inset shadow` для объёма
- Пастельные, насыщенные цвета
- Заоблённые до максимума формы
- **Когда:** детские приложения, геймификация, онбординг
- **Примеры:** Apple WWDC 2022, Duolingo

### Bento Grid
Сетка карточек разного размера в духе японского ланч-бокса.
- CSS Grid с явно заданными `grid-column span`
- Карточки разного размера (1×1, 2×1, 1×2, 2×2)
- Чаще тёмный фон, небольшой радиус
- **Когда:** фичер-секции лендингов, дашборды, портфолио
- **Примеры:** Apple.com, Linear, Vercel, Raycast

### Flat Design 2.0
Эволюция плоского дизайна с микро-тенями и тонкими градиентами.
- **Когда:** корпоративные продукты, B2B SaaS

### Material Design 3 (Material You)
Google, 2022. Динамическая цветовая система.
- **Dynamic Color** — цвета генерируются из обоев устройства
- **Color roles:** Primary, Secondary, Tertiary, Error + On-variants
- **Elevation** через цветные оверлеи
- **Shape scale:** Extra Small → Extra Large
- **Когда:** Android-приложения, Google-экосистема

### Apple HIG
Принципы Apple для iOS, macOS, watchOS, visionOS.
- **Clarity** — текст читаем, иконки точны
- **Deference** — UI помогает контенту
- **Depth** — реалистичное движение и слои
- **Маркеры:** SF Pro шрифт, системные компоненты, blur-эффекты

### Dark Mode Design
Принципы:
- Не `#000000`, а тёмно-серые (`#0F0F0F`, `#1A1A1A`, `#121212`)
- Поверхности повышаются в светлоте с elevation
- Цвета десатурированные
- Текст — `#E5E5E5` или `#F5F5F5`, не чистый белый
- Тени почти невидимы — используй цветные свечения

---

## 2. Типографика

### Терминология

| Термин | Значение |
|---|---|
| Кегль | Размер шрифта (px/pt) |
| Трекинг | Интервал между всеми буквами (letter-spacing) |
| Кернинг | Интервал между конкретной парой (AV, To) |
| Интерлиньяж | Расстояние между базовыми линиями (line-height) |
| Капитель | Заглавные буквы размером со строчные |
| Лигатура | Соединение двух букв в один глиф (fi, fl) |
| Базовая линия | Линия, на которой стоят буквы |
| Апрош | Горизонтальный пробел вокруг символа |
| Засечки | Маленькие штрихи на концах букв |
| Вес | Thin, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black |
| X-height | Высота строчной «x» — ключ к читаемости |
| Variable font | Шрифт с осями: weight, width, slant, optical size |

### Классификация

**Serif (с засечками):**
- Old Style: Garamond, Palatino — классика
- Transitional: Times New Roman, Baskerville — нейтрально
- Modern/Didone: Didot, Bodoni — люкс, мода
- Slab Serif: Rockwell, Courier — технический/ретро

**Sans-serif (без засечек):**
- Grotesque: Helvetica, Arial — промышленные
- Neo-grotesque: Inter, Neue Haas — оптимизированные
- Geometric: Futura, Circular, DM Sans — на основе геометрии
- Humanist: Gill Sans, Nunito — ближе к рукописному

**Display** — для заголовков (Bebas Neue, Clash Display)
**Monospace** — одной ширины (JetBrains Mono, Fira Code)
**Handwritten** — рукописные (Caveat, Satisfy)

### Шрифты для UI (2024–2025)

| Шрифт | Тип | Где |
|---|---|---|
| Inter | Neo-grotesque | Дефолт web UI, SaaS |
| Geist | Neo-grotesque | Vercel, современные продукты |
| Plus Jakarta Sans | Humanist | Стартапы, мягкий UI |
| DM Sans | Geometric | Приложения, дашборды |
| Syne | Display | Заголовки, агентства |
| Clash Display | Display | Лендинги, брендинг |
| Satoshi | Geometric | Современные стартапы |
| General Sans | Geometric | Корпоративный UI |
| JetBrains Mono | Monospace | Код |
| Cabinet Grotesk | Geometric | Брендинг |
| Bricolage Grotesque | Variable | Творческие проекты |

### Типографическая шкала (Major Third, 1.25)

```
xs:   12px    2xl:  30px
sm:   14px    3xl:  36px
base: 16px    4xl:  48px
lg:   20px    5xl:  60px
xl:   24px    6xl:  72px
```

### Интерлиньяж

- Основной текст: 1.5–1.6
- Заголовки: 1.1–1.3
- UI-элементы: 1.0–1.2

### Тренды 2024–2025

- Большие жирные заголовки (80–120px+)
- Variable fonts — анимированный вес при hover
- Serif revival — засечки в digital (NYT, Medium)
- Mixing typefaces — сочетание serif + sans-serif
- Text as texture — типографика как декор

---

## 3. Цвет

### Модели

| Модель | Где | Пример |
|---|---|---|
| HEX | Web, CSS | `#FF5733` |
| RGB | Экраны, CSS | `rgb(255, 87, 51)` |
| HSL | CSS, Figma | `hsl(10, 100%, 60%)` |
| HSB/HSV | Figma picker | H:10 S:80 B:100 |
| CMYK | Печать | C:0 M:66 Y:80 K:0 |
| OKLCH | Современный CSS | `oklch(65% 0.18 30)` |

**HSL интуитивнее RGB для дизайна.** OKLCH ещё лучше — перцептуально равномерный.

### Терминология

| Термин | Значение |
|---|---|
| Hue | Оттенок — угол на круге (0°=красный, 120°=зелёный, 240°=синий) |
| Saturation | Насыщенность (0%=серый, 100%=чистый) |
| Lightness | Светлота (0%=чёрный, 100%=белый) |
| Tint | Цвет + белый |
| Shade | Цвет + чёрный |
| Tone | Цвет + серый |
| Chroma | Яркость/живость (OKLCH) |
| Temperature | Тёплые vs холодные |

### Цветовые схемы

| Схема | Описание | Когда |
|---|---|---|
| Monochromatic | Один оттенок, разная светлота | Минимализм |
| Analogous | Соседние цвета (30–60°) | Гармоничный UI |
| Complementary | Противоположные (180°) | Акцент, CTA |
| Split-complementary | Цвет + два соседних с дополнительным | Менее напряжённый |
| Triadic | Три через 120° | Живой, энергичный |
| Tetradic | Четыре через 90° | Сложно, нужен баланс |

### Токены в дизайн-системе

```
Primitive:
  blue-50 → blue-950
  gray-50 → gray-950

Semantic:
  color-primary = blue-600
  color-background = gray-50
  color-text-primary = gray-900
  color-text-secondary = gray-500
  color-border = gray-200
  color-error = red-600
  color-success = green-600
  color-warning = amber-500

Component:
  button-primary-bg = color-primary
  button-primary-text = white
```

### Роли (Material Design 3)

Primary / Secondary / Tertiary / Error / Surface / Background / On-[color]

### WCAG — контраст

| Уровень | Мелкий текст (<18px) | Крупный (≥18px bold / ≥24px) |
|---|---|---|
| AA | 4.5:1 | 3:1 |
| AAA | 7:1 | 4.5:1 |

**Правило:** никогда не передавай информацию только цветом.

### Тренды цвета 2024–2025

- Neon на тёмном — cyberpunk/tech
- Earthy neutrals — бежевые, терракота, sage green
- Digital lavender — пастельный фиолетово-голубой
- Muted mauve — утончённый пост-Barbie
- Moss & Forest green — wellness
- Mesh gradients — сложные нелинейные
- Duotone — два цвета + маска

---

## 4. UX: методология и процессы

### Double Diamond

```
Discover → Define → Develop → Deliver
(расширить)(сузить)(расширить)(сузить)
```

Детально:
1. Discovery / Empathize — исследовать пользователей
2. Define — сформулировать проблему (Problem Statement, HMW)
3. Ideate — генерация идей, Crazy 8s
4. Prototype — Lo-fi → Hi-fi
5. Test — usability testing
6. Launch & Measure — метрики

### Методы User Research

**Качественные (почему):**
- User Interview — 1:1 на 60–90 мин
- Contextual Inquiry — наблюдение в среде
- Focus Group — групповая дискуссия
- Usability Testing — задания + наблюдение
- JTBD — выявление «работ» продукта
- Diary Study — дневник использования

**Количественные (сколько):**
- Survey — опрос
- A/B Test — сравнение двух вариантов
- Analytics — клики, конверсии, воронки
- Heatmaps — Hotjar, Clarity
- Session Recording
- Card Sorting — для IA
- Tree Testing — проверка навигации

### Законы UX

| Закон | Суть | Применение |
|---|---|---|
| Фиттса | Время достижения ∝ расстоянию / размеру | Крупные кнопки, близость CTA |
| Хика | Больше вариантов → больше времени | Меньше пунктов в меню |
| Миллера | Память = 7±2 элемента | Группировать |
| Якоба | Ждут привычных паттернов | Следовать стандартам |
| Зейгарник | Незавершённые задачи запоминаются | Прогресс-бары |
| Близости (Gestalt) | Близкие = группа | Группировать связанное |
| Прегнанц | Мозг видит простейшую форму | Упрощать |
| Сходства | Похожие = одна группа | Визуальные стили |
| Серийной позиции | Начало и конец запоминаются | Важное — первым/последним |
| Эстетики-юзабилити | Красивое = удобным | Инвестировать в визуал |
| Тесслера | Общая сложность неизменна | Скрывать сложность в продукт |

### UX Метрики

**Поведенческие:** Task Success Rate, Time on Task, Error Rate, Findability

**Опросные:**
- NPS (0–10, порекомендуете?)
- CSAT (удовлетворение)
- CES (усилие)
- SUS (0–100, >68 = выше среднего)

**Продуктовые:** Retention (D1/D7/D30), Activation, Churn, Feature Adoption

### Артефакты

- **Persona** — типичный пользователь с целями и болями
- **User Journey Map (CJM)** — этапы, действия, мысли, эмоции, точки боли
- **User Flow** — экраны и переходы для одной задачи
- **Service Blueprint** — CJM + бэкэнд-процессы
- **Problem Statement / HMW** — формулировка
- **Sitemap** — иерархия страниц
- **Information Architecture** — структура, навигация, таги, иерархия

### 10 эвристик Нильсена

1. Видимость статуса системы
2. Соответствие реальному миру
3. Контроль и свобода
4. Последовательность и стандарты
5. Предотвращение ошибок
6. Узнавание, а не воспоминание
7. Гибкость и эффективность
8. Эстетика и минимализм
9. Помощь при ошибках
10. Документация

---

## 5. UI: компоненты и паттерны

### Ввод данных

| Компонент | Описание |
|---|---|
| Button | Primary, Secondary, Ghost, Destructive, Icon |
| Input | Text Field, состояния: Default, Focus, Filled, Error, Disabled |
| Textarea | Многострочный ввод |
| Select / Dropdown | Выбор одного |
| Combobox | Select + поиск |
| Checkbox | Множественный выбор |
| Radio Button | Один из группы |
| Toggle / Switch | Вкл/выкл |
| Slider | Диапазон |
| Date Picker | Дата/время |
| File Upload | Drop Zone |
| Color Picker | Выбор цвета |
| Search | С иконкой и очисткой |

### Навигация

Navbar, Sidebar, Tab Bar, Tabs, Breadcrumb, Pagination, Stepper, Menu / Context Menu

### Отображение данных

Card, Table, List, Badge, Tag / Chip, Avatar, Progress Bar, Skeleton, Stat / Metric

### Обратная связь

Toast / Snackbar, Alert / Banner, Modal / Dialog, Drawer / Sheet, Tooltip, Popover, Spinner / Loader

### Контейнеры

Accordion, Collapsible, Carousel, Scroll Area, Separator / Divider

### Состояния любого интерактивного компонента

Default / Hover / Focus / Active / Disabled / Loading / Error / Success / Empty

### Паттерны состояний

**Empty State:** иллюстрация + заголовок + подпись + CTA

**Error State:** человекочитаемое сообщение + что делать + кнопка «попробовать снова»

**Loading State:** Skeleton (>1 сек) / Спиннер (<1 сек) / Progress bar (длительные)

### Atomic Design (Брэд Фрост)

```
Atoms — кнопка, input, label, иконка
  ↓
Molecules — поле поиска (input + кнопка + иконка)
  ↓
Organisms — header (logo + nav + search + avatar)
  ↓
Templates — wireframe-уровень
  ↓
Pages — реальный контент
```

### Брейкпоинты (Tailwind)

```
sm:  640px   (mobile landscape)
md:  768px   (tablet)
lg:  1024px  (laptop)
xl:  1280px  (desktop)
2xl: 1536px  (wide)
```

**Mobile First** — сначала мобильный, потом расширение.

---

## 6. Дизайн-системы

**Дизайн-система** = единый источник правды. Включает:
- Design Tokens (переменные)
- Component Library
- Style Guide
- Documentation
- Principles

### Известные системы

| Система | Компания | Технология |
|---|---|---|
| Material Design 3 | Google | Web, Android, Flutter |
| Apple HIG | Apple | iOS, macOS, visionOS |
| Fluent Design | Microsoft | Windows, Web |
| Carbon | IBM | React, Angular |
| Ant Design | Alibaba | React |
| Polaris | Shopify | React |
| Radix UI | WorkOS | React (headless) |
| Shadcn/ui | — | React + Tailwind |
| Chakra UI | — | React |

### Категории токенов

```yaml
Color:
  primitive: gray-100, blue-500...
  semantic: color-primary, color-background...

Typography:
  font-family-body: 'Inter'
  font-size-md: 16px
  font-weight-bold: 700
  line-height-normal: 1.5

Spacing (8pt Grid):
  space-1: 4px    space-8: 32px
  space-2: 8px    space-12: 48px
  space-4: 16px   space-16: 64px

Border Radius:
  radius-sm: 4px
  radius-md: 8px
  radius-lg: 16px
  radius-full: 9999px

Shadow:
  shadow-sm: 0 1px 3px rgba(0,0,0,0.1)
  shadow-md: 0 4px 6px rgba(0,0,0,0.1)
  shadow-lg: 0 10px 15px rgba(0,0,0,0.1)
```

### Figma-специфика

- **Auto Layout** — аналог CSS Flexbox
- **Variants** — группировка состояний (Default/Hover/Active + Size + Type)
- **Component Properties** — Boolean, Text, Instance swap, Variant
- **Variables (2023+)** — design tokens внутри Figma с поддержкой modes
- **Interactive Components** — прототипирование состояний
- **Dev Mode** — автогенерация CSS/iOS/Android

---

## 7. Инструменты

### Основные

| Инструмент | Назначение |
|---|---|
| Figma | UI/UX, дизайн-системы (стандарт индустрии) |
| FigJam | Воркшопы, диаграммы |
| Sketch | UI/UX только macOS |
| Framer | Интерактивные прототипы, сайты (код + дизайн) |
| Webflow | No-code веб-разработка |
| Spline | 3D для веба |
| ProtoPie | Сложные прототипы |
| Lottie | JSON-анимации |

### Figma-плагины

Unsplash, Iconify, Contrast, Figma to Code, Content Reel, Stark, Blobs, Remove BG, Noise & Texture, Tokens Studio

### AI-инструменты

Galileo AI, Uizard, Magician, Midjourney, DALL·E 3, Adobe Firefly, Framer AI, Relume, Spline AI, Claude/GPT

---

## 8. Accessibility

### WCAG — версии

WCAG 2.1 (2018), 2.2 (2023), 3.0 (в работе). Уровни: A / AA / AAA.

### Принципы POUR

| Принцип | Суть |
|---|---|
| Perceivable | Доступен органам чувств |
| Operable | Работает с клавиатурой |
| Understandable | Предсказуемый |
| Robust | Работает в разных браузерах |

### Требования

**Визуальные:**
- Контраст текста ≥ 4.5:1 (AA)
- Контраст UI ≥ 3:1
- Не только цветом
- Масштабирование до 200%

**Интерактивность:**
- Все функции с клавиатуры
- Видимый фокус (не `outline: none`)
- Touch-target: 44×44px (Apple) / 48×48dp (Material)
- Нет keyboard traps

**Семантика:**
- Правильные теги (`<button>`, `<nav>`, `<main>`, `<h1>`)
- ARIA: `aria-label`, `aria-describedby`, `aria-expanded`
- Alt-текст для изображений
- `<label>` для полей форм

**Когнитивная:**
- Понятный язык
- Последовательная навигация
- Предупреждения о таймаутах
- `prefers-reduced-motion`

---

## 9. Профессиональный словарь

### Базовые термины

| Термин | Перевод |
|---|---|
| Affordance | Подсказка способа взаимодействия |
| Hierarchy | Порядок важности элементов |
| White space | «Воздух» в макете |
| Alignment | Выравнивание |
| Proximity | Близость — связанность |
| Repetition | Единообразие стиля |
| Contrast | Различие |
| Visual weight | Визуальный вес |
| Balance | Баланс (симметричный/асимметричный) |
| Grid | Сетка |
| Gutter | Отступ между колонками |
| Margin / Padding | Внешний / внутренний отступ |
| Baseline grid | Сетка по базовым линиям |
| Truncation | Обрезка с многоточием |
| Overflow | Выход за границы |
| Clipping | Обрезка по краям |

### Продуктовые термины

| Термин | Значение |
|---|---|
| Wireframe | Схематичный макет без стилей (lo-fi) |
| Mockup | Статичный hi-fi макет |
| Prototype | Интерактивный макет |
| Lo-fi / Hi-fi | Низкая/высокая детализация |
| Flow / User Flow | Последовательность экранов |
| Handoff | Передача разработчикам |
| Redlines | Аннотации с размерами |
| Edge case | Редкий сценарий |
| Happy path | Идеальный сценарий |
| Pain point | Точка боли |
| Friction | Трение на пути пользователя |
| Onboarding | Знакомство нового пользователя |
| CTA | Call to Action, призыв к действию |
| Above the fold | Видно без прокрутки |
| Progressive disclosure | Показ информации постепенно |
| Gestalt | Целое больше суммы частей |
| Mental model | Ожидания пользователя |

### Технические (для дизайнера)

| Термин | Значение |
|---|---|
| px / rem / em | Единицы (rem от корня, em от родителя) |
| vh / vw | % от высоты/ширины экрана |
| Viewport | Видимая область браузера |
| Breakpoint | Точка смены layout |
| CSS Grid / Flexbox | Двумерная / одномерная сетка |
| z-index | Порядок наложения |
| opacity | Прозрачность |
| border-radius | Скругление |
| box-shadow | Тень |
| transition | Плавное изменение |
| SVG | Векторная графика |
| WebP / AVIF | Современные форматы |
| Retina / 2x | Удвоенная плотность |
| Safe area | Без notch на iPhone |

---

## 10. Тренды 2024–2025

### Визуальный дизайн

- Bento Grid layouts
- Dark mode first
- 3D в веб (Spline, Three.js)
- Maximalism возвращается
- Grain/noise текстуры
- Custom cursors
- Oversized typography
- Horizontal scrolling sections
- Aurora / mesh gradients
- Frosted glass on dark

### Motion

**Принципы:**
- Purpose — помогать, не развлекать
- Duration: 100–200ms — feedback, 200–500ms — переходы, 500+ — attention
- Easing: ease-in, ease-out, ease-in-out, spring

**Microinteractions:** кнопка «нравится», чекбокс, toggle, hover карточек, skeleton, pull-to-refresh

**Инструменты:** Lottie, CSS transitions, Framer Motion, GSAP, Motion.dev

### AI в дизайне

- Генерация вариантов UI (Galileo, Uizard)
- Автоматизация repetitive
- Генерация placeholder-контента
- Персонализация интерфейса
- Автоматические A/B тесты

**AI UX паттерны:** Transparency, Control, Confidence indicators, Progressive loading, Error recovery

### Voice и мультимодальность

- Voice UI (VUI) — Alexa, Siri, ChatGPT Voice
- Multimodal — голос + экран + жесты (Vision Pro)
- Conversational UI

### Spatial Design (Vision Pro)

- Depth layers
- Gaze + pinch interaction
- Shared vs Immersive spaces
- Ornament компоненты

---

## 11. Сетки и пространство

### Типы

| Тип | Описание |
|---|---|
| Column Grid | Колонки + gutters (стандарт 12) |
| Baseline Grid | Горизонтальная для типографики (8px) |
| Modular Grid | Пересечение колонок и строк |
| Hierarchical | Свободная под контент |

**Стандарты:**
- Desktop: 12 колонок, gutter 24–32px, margin 80–120px
- Tablet: 8 колонок, gutter 16–24px
- Mobile: 4 колонки, gutter 16px, margin 16–24px

### 8pt Grid

Все отступы кратны 4px или 8px:
```
4px — минимум (иконка + текст)
8px — xs       32px — xl
12px — sm      48px — 2xl
16px — md      64px — 3xl
24px — lg      96px — 4xl
```

---

## 12. Иконки и иллюстрации

### Типы иконок

| Тип | Stroke | Пример |
|---|---|---|
| Outline | 1.5–2px | Heroicons, Phosphor |
| Filled | — | Material Icons |
| Duotone | Два цвета | Phosphor Duotone |
| Thin | 1px | Feather Icons |
| Bold | Жирный | Heroicons Bold |
| Bulk | Заполненные + полупрозрачные | Solar Icons |

**Наборы:** Heroicons, Lucide, Phosphor, Tabler, Remix, Material Symbols, SF Symbols

### Правила

- Единый стиль в пределах продукта
- Стандартные размеры: 16, 20, 24, 32px
- aria-label для доступности
- Оптическое выравнивание (не математическое)

### Стили иллюстраций

- Flat 2D — плоские формы
- Isometric — 3D-иллюстрации
- Abstract / Geometric — формы + цвет
- Hand-drawn — рукописный стиль
- 3D Realistic — рендер, clay-style
- AI-generated — Midjourney, DALL·E

---

## 13. UX Writing

### Принципы

- **Ясность** — понятно сразу
- **Краткость** — минимум слов
- **Конкретность** — не «продолжить», а «создать проект»
- **Человечность** — разговорный тон
- **Консистентность** — одно и то же называется одинаково

### Типичные ошибки

- «Нажмите здесь» → «Создать аккаунт»
- «Ошибка 404» → «Страница не найдена»
- «Успешно!» → «Заявка отправлена, ответим за 2 часа»
- «Вы уверены?» → «Удалить проект? Это нельзя отменить»

### Tone of Voice (4 оси)

- Funny ↔ Serious
- Formal ↔ Casual
- Respectful ↔ Irreverent
- Enthusiastic ↔ Matter-of-fact

---

## 14. Метрики и KPI

| Метрика | Что измеряет |
|---|---|
| Conversion Rate | % целевого действия |
| Bounce Rate | % ушедших с первой страницы |
| Time on Task | Время выполнения |
| Task Completion Rate | % успеха |
| Error Rate | Количество ошибок |
| SUS Score | System Usability Scale (0–100) |
| NPS | Готовность рекомендовать |
| CSAT | Удовлетворённость |
| Retention D1/D7/D30 | Возврат |
| Feature Adoption | % использующих фичу |
| Rage Clicks | От фрустрации |
| Dead Clicks | На неинтерактивные элементы |
