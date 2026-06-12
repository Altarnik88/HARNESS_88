# HARNESS_88 для владельца сайта

HARNESS_88 проще всего воспринимать не как шаблон сайта, а как рабочий штаб проекта. Он не приносит с собой готовую главную страницу, не выбирает за вас Next.js, базу данных, хостинг или платежную систему. Его задача другая: провести вас от фразы "мне нужен сайт" до понятного, проверенного и одобренного результата.

Если агент сразу начинает писать код, проект часто уезжает не туда. Сначала выбирается случайный стек, потом внезапно выясняется, что нужны каталог, заявки, другой язык, другие референсы, админка, SEO, форма оплаты или публикация на конкретном сервере. HARNESS_88 ставит между идеей и кодом несколько полезных остановок: вопросы, решения, референсы, выбор стека, preview, аудит, исправления и финальное одобрение.

Сейчас HARNESS_88 v0.1.0 находится в честном стартовом состоянии: стек не выбран, frontend не поставляется, а `PRODUCT.md`, `DESIGN.md`, `SITE_INTAKE.md`, `SITE_REFERENCES.md` и `SITE_GATES.md` находятся в статусе `draft`. Это не недоделка. Так и задумано: свежая копия ядра сначала ждет ваших решений, а уже потом превращается в конкретный сайт.

## Зачем это нужно, если хочется "просто сайт"

"Просто сайт" почти всегда оказывается не таким простым. Даже лендинг требует ответов на вопросы: кому он нужен, что посетитель должен сделать, какие страницы и блоки нужны, на каком языке говорить с аудиторией, где брать контент, куда отправлять заявки, как проверять качество, где публиковать сайт и кто потом будет его поддерживать.

HARNESS_88 помогает не держать все это в переписке. Он сохраняет решения в файлах проекта, поэтому контекст не теряется при смене агента, сбросе чата или передаче работы другому разработчику. Вы видите, что уже принято, что еще открыто, и почему агент пока не начинает реализацию.

Для владельца сайта это дает три вещи:

- контроль над решениями до того, как они превратятся в код;
- меньше технической самодеятельности со стороны агентов;
- понятную дорогу к запуску: от идеи до публикации и поддержки.

## Как проходит работа

### 1. Сначала ядро проверяет окружение

Агент начинает не с установки зависимостей, а с чтения правил проекта и read-only проверки окружения. Обычно запускаются такие команды:

```powershell
python tools/llm_wiki.py tools audit --json
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site references --json
python tools/llm_wiki.py site gates --json
python tools/llm_wiki.py stack status
```

Эти команды ничего не устанавливают и не подключают. Они только показывают, какие tools, plugins, MCP servers и skills уже доступны, чего не хватает, и где агент обязан спросить разрешение.

### 2. Потом идет разговор о будущем сайте

Этот этап называется `site intake`. Агент задает вопросы на вашем языке, но отдельно фиксирует язык будущего сайта. Например, обсуждать проект можно на русском, а сайт делать на польском или английском.

На этом этапе выясняется:

- цель сайта и аудитория;
- страна или рынок;
- основной язык сайта;
- тип проекта: landing, multipage, catalog, ecommerce, app или custom;
- нужны ли каталог, товары, услуги, заявки, онлайн-оплата, офлайн-оплата или запрос менеджеру;
- стиль, референсы и источники контента;
- нужны ли backend, база данных, auth, admin или integrations;
- как вы представляете запуск, поддержку и публикацию.

Принятые ответы записываются в `SITE_INTAKE.md`. Пока intake не утвержден, серьезная разработка сайта не начинается.

### 3. Стек выбирается после разговора, а не по привычке

HARNESS_88 не считает, что всем сайтам нужен один и тот же стек. Агент должен предложить несколько подходящих вариантов, объяснить плюсы, минусы, сложность поддержки и сценарии, где каждый вариант уместен.

В проекте уже описаны такие профили:

- `next-static` - Next.js App Router + TypeScript + Tailwind для лендингов, маркетинговых сайтов и frontend-first проектов;
- `next-fullstack` - Next.js App Router + TypeScript + Tailwind для SaaS, кабинетов, форм, auth и будущей backend-логики;
- `astro-content` - Astro для быстрых SEO/content-heavy сайтов, блогов и документации;
- `sveltekit` - SvelteKit для интерактивных приложений;
- `custom` - ваш собственный стек, если у проекта уже есть технические ограничения или предпочтения.

Решение фиксируется в `STACK.md` только после вашего явного approval. Команда выбора стека записывает выбор, но сама не создает frontend и не ставит зависимости:

```powershell
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py stack select next-static
```

### 4. Продукт и дизайн становятся контрактом

После intake агент помогает оформить два важных документа.

`PRODUCT.md` отвечает на вопросы: зачем существует сайт, для кого он, какие задачи решает, что входит в scope, что не входит, и как понять, что результат успешен.

`DESIGN.md` фиксирует визуальное направление: стиль, UX-принципы, доступность, компоненты, layout, typography, colors, imagery и motion policy.

Это не бюрократия ради бюрократии. Эти файлы защищают проект от ситуации, когда один агент рисует "дорого и минималистично", другой - "ярко и с анимациями", а владелец сайта в итоге получает смесь несогласованных решений.

### 5. Референсы проверяются до frontend-разработки

Перед серьезной frontend-работой HARNESS_88 требует утвержденные референсы. Это могут быть сайты, screenshots, бренды, конкуренты или примеры, которые предложил агент.

Если у вас нет референсов, Reference Research должен предложить варианты. По правилам проекта поиск включает:

- `https://dribbble.com/`
- `https://www.behance.net/`
- `https://www.awwwards.com/`

Можно добавить конкурентов и рыночные примеры, но эти три источника не заменяются чем-то другим.

После выбора референсов начинается `reference analysis gate`. Агент собирает bounded crawl публичных страниц, page inventory, desktop/mobile screenshots, UX/visual analysis и Figma reference artifact. Все это записывается в `SITE_REFERENCES.md`, а screenshots индексируются через `raw/assets/references/manifest.json`.

Frontend-разработка начинается только после того, как reference gate готов:

```powershell
python tools/llm_wiki.py site references --json
```

### 6. Работа разбивается на задачи

HARNESS_88 не держит реализацию только в чате. Для реальной работы создаются task files в `agents/tasks/`, progress files и checkpoints. В них видно, кто отвечает за задачу, какие файлы можно менять, какие tools разрешены и какой проверкой подтверждается результат.

Пример команды:

```powershell
python tools/llm_wiki.py task create --title "First Implementation Slice" --objective "Build the first approved site slice from PRODUCT.md, DESIGN.md, and STACK.md."
```

Так проект можно продолжать после паузы, передавать между агентами и проверять без угадывания, что имелось в виду в старом чате.

### 7. Сайт показывается, проверяется и дорабатывается

Когда gates пройдены, начинается сборка сайта. Сначала обычно показывается frontend preview. Вы смотрите, даете замечания, агент превращает их в конкретные задачи, исправляет и показывает результат снова.

После этого, если проект требует backend или data-слой, подключается Backend/Data роль. Она занимается API, data models, catalog, ecommerce, auth/admin, request flows и integrations. Если backend не нужен, это тоже фиксируется как решение, а не остается догадкой.

Перед публикацией проводится total audit: функциональность, accessibility, responsive behavior, performance, SEO/metadata, security, dependency audit, backend/data correctness, code quality и maintainability. Найденные проблемы идут в remediation tasks и проверяются повторно.

### 8. Публикация идет только после финального approval

Публикационные инструкции появляются в самом конце, когда preview одобрен, аудит пройден, замечания исправлены или осознанно приняты как residual risk, а `SITE_GATES.md` подтверждает готовность.

Перед этим агент должен обсудить с вами, где публиковать сайт: на VPS/VDS или managed hosting.

VPS/VDS дает больше контроля над runtime, logs, backups, reverse proxy и custom services, но требует администрирования, security patches, мониторинга и реакции на incidents.

Managed hosting обычно быстрее запускается, дает previews, CDN/HTTPS и rollback, но ограничивает низкоуровневый контроль, может иметь provider limits, vendor lock-in и свои pricing constraints.

Выбор зависит от бюджета, traffic, backend/runtime needs, требований к uptime, backups и того, кто будет заниматься поддержкой.

## Что уже умеет ядро

HARNESS_88 хранит долговременную память проекта в `wiki/`. Markdown остается источником истины, а `data/wiki.sqlite` считается generated state: его можно пересобрать.

Для wiki используются:

```powershell
python tools/llm_wiki.py rebuild
python tools/llm_wiki.py lint
```

Для проверки готовности проекта:

```powershell
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site references --json
python tools/llm_wiki.py site gates --json
```

Для общего health-check:

```powershell
python tools/llm_wiki.py site doctor --skip-self-test
```

Для core quality:

```powershell
python tools/llm_wiki.py quality --skip-frontend
```

Когда в проекте появится approved scaffolded frontend/backend, добавятся stack-specific проверки и security audit:

```powershell
python tools/llm_wiki.py quality
python tools/llm_wiki.py security audit --json --no-record
```

Секреты в проект не записываются. Tokens, API keys, database URLs и payment secrets должны жить в environment variables или проходить через `agents/workflows/secret-broker.md`.

## Кто участвует в работе

HARNESS_88 устроен как команда, которой управляет Conductor. В маленькой задаче часть ролей может выполнять один агент, но для большого сайта роли лучше разделять.

- **Conductor** планирует, делегирует, проверяет и координирует handoff.
- **Product Strategist** формулирует цель сайта, аудиторию, user jobs и acceptance criteria.
- **Reference Research** ищет и анализирует референсы, готовит shortlist, screenshots и Figma handoff.
- **IA & Content** отвечает за sitemap, slugs, page models, content и metadata.
- **UX/Product Design** проектирует flows, responsive behavior, interactions и states.
- **Visual Design** отвечает за visual system, tokens, imagery direction и polish.
- **Frontend Architecture** определяет routing, component boundaries и implementation slices.
- **Frontend Implementation** собирает страницы, компоненты, стили и интеракции.
- **Backend/Data** проектирует API, data models, catalog, ecommerce, auth/admin и request flows.
- **QA & Accessibility** проверяет функциональность, accessibility и user flows.
- **Performance/SEO** проверяет скорость, metadata, SEO и discovery.
- **DevOps/Release** отвечает за build, deploy, rollback, backups, monitoring и maintenance handoff.
- **Knowledge Steward** записывает durable decisions в wiki, log и closeout notes.

## Какие tools, MCP, plugins и skills могут понадобиться

Инструменты в HARNESS_88 подключаются по принципу progressive discovery: только когда они действительно нужны для текущей задачи. По умолчанию доступ ограничен, а delegation brief должен явно назвать разрешенные tools, skills, plugins и MCP.

Из MCP чаще всего полезны:

- **Serena MCP** - точечный symbol-level code discovery;
- **Context7 MCP** - актуальная документация libraries, frameworks, SDK, CLI и cloud services;
- **Filesystem MCP** - scoped file access внутри проекта;
- **SQLite MCP** - read-only inspection локального SQLite state.

Из plugins могут понадобиться:

- **Browser plugin** для preview, screenshots и responsive/browser checks;
- **GitHub plugin** для repository, PR, issues и CI, обычно read-only;
- **Figma plugin/MCP** для Figma files, FigJam, Slides, design system и reference artifacts;
- **Product Design plugin** для product/UI context, ideation и image-to-code;
- **Canva plugin** для mood boards, editable assets, decks и campaign/social visuals;
- **Creative Production plugin** для visual directions, mood boards, ads, logos и scene exploration;
- **Supabase plugin** для database, auth, storage, realtime и edge functions, если Supabase выбран;
- **Sentry plugin/skill** для read-only production error inspection;
- **Documents** и **Spreadsheets** для документов, таблиц, CSV/XLSX, charts и exports;
- **Data Analytics** для source-backed dashboards, reports и KPI work;
- **Remotion** только для video/render/export задач, не для обычной website UI-разработки.

Из skills чаще всего встречаются:

- **Playwright skill** для browser automation, screenshots, flow QA и responsive checks;
- **gh-cli skill** для GitHub workflows через authenticated GitHub CLI;
- **imagegen skill** для bitmap assets, mockups, textures, sprites и visual variants;
- **Product Design skills** вроде get-context, ideate и image-to-code;
- design resources: `ui-ux-pro-max`, `huashu-design`, `impeccable`, GSAP и Canva.

## Внешние ресурсы подключаются только с разрешения

Это важное правило. HARNESS_88 не устанавливает local tools, не скачивает skills с GitHub, не подключает MCP servers, не подключает Codex plugins и не добавляет frontend dependencies автоматически.

Даже если ресурс бесплатный, публичный или open-source, агент сначала спрашивает разрешение. Для GitHub-backed resources точный URL должен быть записан в `agents/resources/tooling-sources.json`. Если URL пустой или отсутствует, агент не угадывает ссылку, а просит вас дать или подтвердить правильный repository URL.

Текущий tooling audit показывает, что обязательные Python и Git доступны, Node.js/npm тоже доступны, а GitHub CLI и часть design skills могут потребовать отдельного разрешения перед установкой или скачиванием.

Ниже - готовые формулировки, которые агент может использовать перед подключением внешних ресурсов.

**GitHub CLI**

```text
Для работы с GitHub через authenticated CLI мне нужен GitHub CLI. Он поможет проверять PR, issues, CI и release workflows без ручного копирования больших данных. Разрешаете установить или подключить GitHub CLI, используя источник из реестра проекта: https://github.com/cli/cli?
```

**gh-cli skill**

```text
Для более строгой работы с GitHub CLI можно подключить Codex skill `gh-cli`. Сейчас в `agents/resources/tooling-sources.json` нет утвержденного URL для этого skill, поэтому я не буду ничего скачивать. Пришлите или подтвердите точную ссылку на репозиторий `gh-cli` skill, если хотите разрешить его установку.
```

**ui-ux-pro-max**

```text
Для более сильной UI/UX-структуры, design-system reasoning и UX specs можно скачать skill `ui-ux-pro-max`. Разрешаете использовать GitHub-источник из реестра проекта: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill?
```

**huashu-design**

```text
Для high-fidelity design directions, HTML-native prototypes, demos, animation concepts и design review можно скачать skill `huashu-design`. Разрешаете использовать GitHub-источник из реестра проекта: https://github.com/alchaincyf/huashu-design?
```

**impeccable**

```text
Для design-language critique, UI audit, polish, responsive/accessibility/performance design checks можно скачать ресурс `impeccable`. Разрешаете использовать GitHub-источник из реестра проекта: https://github.com/pbakaus/impeccable?
```

**GSAP**

```text
Для утвержденной motion-системы и production animation implementation можно добавить GSAP. Это optional frontend resource, и я не буду добавлять его без вашего решения. Разрешаете использовать источник из реестра проекта: https://github.com/greensock/GSAP/?
```

**Canva plugin**

```text
Для mood boards, editable design assets, decks, campaign/social visuals можно подключить Canva plugin. Это внешний Codex plugin, поэтому я подключу его только после вашего разрешения. Разрешаете использовать ресурс из реестра проекта: plugin://canva@openai-curated-remote?
```

**Figma plugin/MCP**

```text
Для reference artifact, design handoff или работы с Figma-файлом нужен Figma plugin/MCP. Разрешаете использовать Figma для этой задачи? Если нужно создать новый Figma file, я отдельно уточню workspace/team и scope записи.
```

**MCP capabilities**

```text
Для этой задачи может понадобиться MCP capability. Я буду использовать MCP только узко и по назначению: Serena для symbol-level code discovery, Context7 для актуальной документации, Filesystem только в пределах проекта, SQLite только read-only. Разрешаете использовать соответствующий MCP capability для этой задачи, если он доступен в Codex host?
```

**Frontend dependencies**

```text
Для выбранного frontend стека может понадобиться установка зависимостей через npm или другой package manager. Я не буду устанавливать зависимости автоматически. Разрешаете установить зависимости только для утвержденного stack/task scope и затем запустить проверочные команды?
```

## Что нужно одобрить до разработки и публикации

До production implementation нужно явно утвердить:

- intake в `SITE_INTAKE.md`;
- product direction в `PRODUCT.md`;
- design direction в `DESIGN.md`;
- stack profile или custom stack в `STACK.md`;
- references и `SITE_REFERENCES.md`;
- deployment direction: VPS/VDS или managed hosting;
- concrete task file для первого implementation slice.

Перед publication handoff также нужны:

- frontend preview approval;
- backend/data readiness или `not-required`;
- total audit;
- remediation или accepted residual risk;
- final user approval;
- publish/operate handoff.

## С чего начать

Если вы только скачали HARNESS_88, можно написать агенту так:

```text
Прочитай START_HERE.md, AGENTS.md, SITE_INTAKE.md, SITE_REFERENCES.md, SITE_GATES.md, PRODUCT.md, DESIGN.md, STACK.md, agents/protocols/tooling-onboarding.md, agents/harness/stack-options.md и agents/workflows/agentic-site-delivery.md.
Проверь tools/skills/plugins/MCP и readiness командами из START_HERE.md.
Проведи первый intake для моего сайта на русском языке.
Не выбирай стек, не обновляй PRODUCT.md, DESIGN.md и STACK.md, не начинай implementation и не подключай внешние ресурсы без моего явного approval.
```

После этого HARNESS_88 будет вести проект не как случайный чат "сделай сайт", а как нормальный рабочий процесс: сначала вопросы и решения, потом референсы и стек, затем задачи, preview, аудит, исправления, финальное approval и понятная публикация.
