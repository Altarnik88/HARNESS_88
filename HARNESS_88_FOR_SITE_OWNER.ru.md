# HARNESS_88 для владельца сайта

Этот документ объясняет HARNESS_88 простым языком: зачем нужно ядро, какие шаги пройдет человек при создании сайта, какие функции уже есть в проекте, какие агенты и инструменты могут понадобиться, и почему любые внешние ресурсы подключаются только после отдельного разрешения.

## Коротко

HARNESS_88 - это не готовый сайт и не шаблон с уже выбранным frontend. Это автономное ядро для управляемой разработки сайта вместе с агентами.

Обычный запрос "сделай мне сайт" слишком расплывчатый. Если агент сразу начинает писать код, часто появляются проблемы: выбран не тот стек, не согласован дизайн, не понятна аудитория, забыты страницы, формы, каталог, оплата, SEO, публикация, безопасность и поддержка. HARNESS_88 нужен, чтобы не прыгать сразу в код, а сначала превратить идею сайта в проверяемый план доставки.

Ядро помогает:

- задать правильные вопросы о будущем сайте;
- сохранить ответы и решения в файлах проекта;
- выбрать подходящий стек только после обсуждения;
- собрать продуктовый и дизайн-контракт;
- проверить референсы до серьезной frontend-разработки;
- разбить работу на задачи с владельцами, прогрессом и checkpoints;
- показать preview, провести аудит, исправить замечания и получить финальное одобрение;
- подготовить публикацию на VPS/VDS или managed hosting без хранения секретов в проекте.

В текущем состоянии HARNESS_88 v0.1.0 является stack-neutral core: стек не выбран, готовый frontend не поставляется, а файлы `PRODUCT.md`, `DESIGN.md`, `SITE_INTAKE.md`, `SITE_REFERENCES.md` и `SITE_GATES.md` находятся в draft-состоянии. Это нормально для свежей копии: ядро сначала ждет решений пользователя.

## Зачем это владельцу сайта

Если вы хотите "просто сайт", HARNESS_88 может показаться лишним слоем. На деле это слой защиты от хаоса.

Сайт почти никогда не является только набором красивых блоков. Даже простой лендинг требует решений: кому он продает, какое действие должен выполнить посетитель, какие доказательства доверия нужны, какой язык сайта, какие формы использовать, где хранить заявки, кто будет поддерживать проект, где сайт будет опубликован, как проверять качество и кто принимает финальный результат.

HARNESS_88 делает эти решения явными. Он не позволяет агентам молча выбрать Next.js, fullstack, базу данных, платежи, VPS или хостинг "по привычке". Вместо этого ядро сначала спрашивает, сравнивает варианты, объясняет плюсы и минусы, а потом фиксирует принятое решение в проекте.

Главная польза для владельца сайта:

- меньше случайных технических решений;
- больше контроля над тем, что именно будет сделано;
- понятные точки одобрения;
- возможность передать проект другому агенту или разработчику без потери контекста;
- меньше риска получить красивую, но непригодную к запуску страницу;
- прозрачная подготовка к публикации, обновлениям, резервным копиям и поддержке.

## Какой путь пройдет человек

### 1. Первый запуск и аудит инструментов

Сначала агент читает проектные правила и запускает read-only аудит:

```powershell
python tools/llm_wiki.py tools audit --json
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site references --json
python tools/llm_wiki.py site gates --json
python tools/llm_wiki.py stack status
```

Этот аудит ничего не устанавливает и не подключает. Он только показывает, какие локальные tools, Codex plugins, MCP servers и skills доступны, чего не хватает, и где нужно спросить разрешение.

### 2. Site intake

Дальше агент задает вопросы на языке пользователя. Важно: язык общения и язык будущего сайта - разные вещи. Например, обсуждать проект можно на русском, а сайт делать на польском или английском.

На intake собираются:

- цель сайта;
- аудитория;
- страна или рынок;
- основной язык сайта;
- тип сайта: landing, multipage, catalog, ecommerce, app или custom;
- нужны ли каталог, товары, услуги, заявки, онлайн-оплата, офлайн-оплата или запрос менеджеру;
- желаемый стиль;
- референсы;
- источники контента;
- требования к backend, данным, auth, admin, integrations;
- ожидания по запуску, поддержке и публикации.

Принятые ответы записываются в `SITE_INTAKE.md`. Пока этот файл не утвержден, серьезная реализация сайта не начинается.

### 3. Выбор стека

HARNESS_88 не выбирает стек по умолчанию. Агент должен предложить 2-4 подходящих варианта и объяснить их человеческим языком: языки, frameworks, сервисы, плюсы, минусы, сложность поддержки и лучшие сценарии.

В проекте есть такие профили:

- `next-static` - Next.js App Router + TypeScript + Tailwind для лендингов, маркетинговых и frontend-first сайтов;
- `next-fullstack` - Next.js App Router + TypeScript + Tailwind для SaaS, кабинетов, форм, auth и будущей backend-логики;
- `astro-content` - Astro для быстрых SEO/content-heavy сайтов, блогов и документации;
- `sveltekit` - SvelteKit для интерактивных приложений;
- `custom` - пользовательский стек, если у проекта уже есть технические ограничения или предпочтения.

Выбор фиксируется в `STACK.md` только после явного approval пользователя. Команда выбора стека записывает решение, но сама не устанавливает зависимости и не создает frontend:

```powershell
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py stack select next-static
```

### 4. Product brief

После intake агент помогает сформулировать продуктовый контракт в `PRODUCT.md`: зачем сайт существует, для кого он, какие задачи пользователя решает, что входит в scope, что не входит, и по каким критериям результат считается успешным.

Пока `PRODUCT.md` имеет `Status: draft`, production implementation заблокирован.

### 5. Design brief

Затем фиксируется дизайн-направление в `DESIGN.md`: визуальный стиль, UX-принципы, доступность, компоненты, layout, typography, colors, imagery и motion policy.

Это нужно не для бюрократии, а чтобы агенты не рисовали сайт каждый раз заново и не спорили между собой о вкусе без опоры на принятое решение.

### 6. Референсы и reference analysis gate

Перед серьезной frontend-разработкой нужны утвержденные референсы. Это могут быть сайты, screenshots, бренды, конкуренты или agent-proposed examples.

Если у пользователя нет референсов, Reference Research должен предложить варианты. По правилам проекта поиск должен включать:

- `https://dribbble.com/`
- `https://www.behance.net/`
- `https://www.awwwards.com/`

Можно добавлять конкурентов и рыночные примеры, но нельзя заменять ими эти источники.

После выбора референсов HARNESS_88 требует строгую проверку:

- bounded crawl публичных страниц;
- inventory страниц;
- desktop/mobile screenshots;
- manifest `raw/assets/references/manifest.json`;
- UX/visual analysis;
- Figma reference artifact;
- явное approval пользователя.

Все это записывается в `SITE_REFERENCES.md`. Serious frontend implementation начинается только когда:

```powershell
python tools/llm_wiki.py site references --json
```

показывает, что reference analysis готов.

### 7. Sitemap, content model и user journeys

После продукта, дизайна, стека и референсов агентная команда описывает структуру сайта:

- страницы и slugs;
- navigation и footer;
- цель каждой страницы;
- content blocks;
- формы и conversion paths;
- metadata и SEO;
- catalog/ecommerce/request model, если он нужен.

### 8. Задачи, progress и checkpoints

HARNESS_88 не любит работу "где-то в чате". Для реальной реализации создаются task files в `agents/tasks/`, progress files и checkpoints.

Это помогает ответить на вопросы:

- кто отвечает за задачу;
- какие файлы можно менять;
- какие tools/skills/plugins разрешены;
- чем подтверждается результат;
- какая команда проверки должна пройти;
- что осталось рискованным или незавершенным.

Пример создания задачи:

```powershell
python tools/llm_wiki.py task create --title "First Implementation Slice" --objective "Build the first approved site slice from PRODUCT.md, DESIGN.md, and STACK.md."
```

### 9. Frontend preview и approval loop

После approved gates начинается frontend build. Агент показывает видимый preview, пользователь дает feedback, замечания превращаются в задачи, исправления снова показываются.

`SITE_GATES.md` получает `frontend_preview_approval: approved` только после явного одобрения. Молчание не считается согласием.

### 10. Backend, data, forms, catalog, ecommerce

Backend/Data подключается только если это нужно по intake и выбранному стеку.

Возможные варианты:

- static-only сайт без backend;
- forms-only сайт;
- catalog;
- ecommerce;
- auth/admin;
- CMS;
- custom integrations.

Для оплаты, каталога или заявок агент обязан следовать выбранному режиму: online payment, offline payment, request-to-manager или mixed mode. Секреты не записываются в проект. В файлах можно хранить только имена переменных окружения, redacted status или broker receipts.

### 11. Total audit и remediation

Перед финальной публикацией проводится аудит:

- functional bugs;
- accessibility;
- responsive behavior;
- performance;
- SEO/metadata;
- security/dependency audit;
- backend/data correctness;
- code quality;
- maintainability.

Найденные проблемы не прячутся в общем тексте. Они записываются как findings, превращаются в remediation tasks и проверяются повторно.

### 12. Финальное одобрение

Финальный сайт снова показывается пользователю. Если есть замечания, они фиксируются и исправляются. Только после явного approval можно переходить к publish/operate handoff.

### 13. Публикация и поддержка

HARNESS_88 должен объяснить разницу между VPS/VDS и managed hosting.

VPS/VDS дает больше контроля над runtime, logs, backups, reverse proxy и custom services, но требует администрирования, обновлений, мониторинга, security patches и реакции на incidents.

Managed hosting быстрее запускается, обычно дает previews, CDN/HTTPS и rollback, но меньше дает низкоуровневого контроля, может иметь provider limits, vendor lock-in и свои pricing constraints.

Агент должен спросить про бюджет, ожидаемый traffic, backend/runtime needs, uptime, backups и владельца техподдержки, а затем рекомендовать подходящий вариант.

Публикационные инструкции нельзя выдавать как финальный handoff, пока `SITE_GATES.md` не подтверждает audit, remediation, final user approval и publish/operate handoff.

## Что умеет ядро

### LLM Wiki

`wiki/` - это долговременная память проекта. Markdown остается источником истины, а `data/wiki.sqlite` является rebuildable index для поиска, graph, events и inspection.

Основные команды:

```powershell
python tools/llm_wiki.py rebuild
python tools/llm_wiki.py lint
```

### Readiness и gates

Ядро умеет проверять, готов ли проект к следующему этапу:

```powershell
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site references --json
python tools/llm_wiki.py site gates --json
```

На текущий момент для свежего проекта ожидаемы блокеры: не утверждены product/design, не выбран stack, не заполнен intake, не утверждены references, не завершены delivery gates.

### Stack profiles

Стек выбирается через диалог, а не через предположение агента. Профили живут в `agents/harness/stack-options.md` и `agents/harness/stack-profiles.json`.

### Site doctor

`site doctor` дает единый диагностический отчет по readiness, wiki, task graph, frontend, security и starter checks:

```powershell
python tools/llm_wiki.py site doctor --skip-self-test
```

### Quality и security checks

Для ядра используется stack-neutral quality gate:

```powershell
python tools/llm_wiki.py quality --skip-frontend
```

Когда позже появится approved scaffolded frontend/backend, добавятся stack-specific checks и dependency/security audit:

```powershell
python tools/llm_wiki.py quality
python tools/llm_wiki.py security audit --json --no-record
```

### Secret policy

Секреты нельзя хранить в `AGENTS.md`, wiki, task files, Codex config, MCP arguments или обычных project files. Tokens, API keys, database URLs и payment secrets должны жить в environment variables или проходить через `agents/workflows/secret-broker.md`.

## Агентная команда

HARNESS_88 устроен как conductor-led команда. Один агент не должен молча делать все роли сразу, особенно в большом сайте.

- **Conductor** - планирует, делегирует, проверяет, координирует handoff.
- **Product Strategist** - формулирует цель сайта, аудиторию, user jobs, acceptance criteria.
- **Reference Research** - ищет и анализирует референсы, готовит shortlist, screenshots, Figma handoff.
- **IA & Content** - отвечает за sitemap, slugs, page models, content и metadata.
- **UX/Product Design** - проектирует flows, responsive behavior, interactions и states.
- **Visual Design** - отвечает за visual system, tokens, imagery direction и polish.
- **Frontend Architecture** - определяет routing, component boundaries и implementation slices.
- **Frontend Implementation** - собирает страницы, компоненты, стили и интеракции в назначенных файлах.
- **Backend/Data** - проектирует API, data models, catalog, ecommerce, auth/admin, request flows.
- **QA & Accessibility** - проверяет функциональность, accessibility и user flows.
- **Performance/SEO** - проверяет скорость, metadata, SEO и discovery.
- **DevOps/Release** - отвечает за build, deploy, rollback, backups, monitoring и maintenance handoff.
- **Knowledge Steward** - записывает durable decisions в wiki, log и closeout notes.

## MCP, plugins и skills

Инструменты подключаются по принципу progressive discovery: только когда текущая задача действительно нуждается в них. По умолчанию доступ denied, а delegation brief должен явно назвать разрешенные tools/skills/plugins/MCP.

### MCP servers

- **Serena MCP** - точечное symbol-level code discovery, чтобы не читать весь код целиком.
- **Context7 MCP** - актуальная документация libraries, frameworks, SDK, CLI и cloud services.
- **Filesystem MCP** - scoped file access внутри проекта, если host поддерживает.
- **SQLite MCP** - read-only inspection локального SQLite state.

### Plugins

- **Browser plugin** - локальные preview, screenshots, responsive/browser checks.
- **GitHub plugin** - repository, PR, issues, CI; по умолчанию read-only, write только по явному запросу.
- **Figma plugin/MCP** - Figma files, FigJam, Slides, design system, reference artifacts.
- **Product Design plugin** - product/UI context, ideation, image-to-code после утверждения mockup/reference.
- **Canva plugin** - mood boards, editable assets, decks, campaign/social visuals.
- **Creative Production plugin** - visual directions, mood boards, ads, logos, scene exploration.
- **Supabase plugin** - database, auth, storage, realtime, edge functions, если Supabase выбран.
- **Sentry plugin/skill** - read-only production error inspection при configured environment auth.
- **Documents plugin** - Word/document artifacts, comments, render verification.
- **Spreadsheets plugin** - spreadsheets, CSV/XLSX, formulas, charts, exports.
- **Data Analytics plugin** - source-backed analysis, dashboards, reports, KPI work.
- **Remotion plugin** - video/render/export tasks, не обычная website UI-разработка.

### Skills

- **Playwright skill** - browser automation, screenshots, flow QA, responsive checks.
- **gh-cli skill** - GitHub workflows через authenticated GitHub CLI.
- **imagegen skill** - bitmap assets, mockups, textures, sprites, visual variants.
- **Product Design skills** - get-context, ideate, image-to-code для UI/product задач.
- **Design resources** - `ui-ux-pro-max`, `huashu-design`, `impeccable`, GSAP и Canva для advanced UI/UX, visual direction, critique, motion и editable design handoff.

## Подключение внешних бесплатных и публичных ресурсов

HARNESS_88 не должен автоматически устанавливать local tools, скачивать skills с GitHub, подключать MCP servers, подключать Codex plugins или добавлять frontend dependencies.

Даже если ресурс бесплатный, публичный или open-source, агент должен спросить разрешение. Для GitHub-backed resources точный URL должен быть записан в `agents/resources/tooling-sources.json`. Если URL пустой или отсутствует, агент не должен угадывать ссылку; он должен попросить пользователя дать или подтвердить правильный repository URL.

Текущий tooling audit показывает, что обязательные Python и Git доступны, Node.js/npm доступны, а GitHub CLI и некоторые design skills могут потребовать отдельного разрешения перед установкой или скачиванием.

### Готовые тексты запросов на разрешение

Эти формулировки можно использовать в первом запуске или перед конкретной задачей.

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

## Что пользователь должен одобрить до разработки

До production implementation пользователь должен явно одобрить:

- intake в `SITE_INTAKE.md`;
- product direction в `PRODUCT.md`;
- design direction в `DESIGN.md`;
- stack profile или custom stack в `STACK.md`;
- references и `SITE_REFERENCES.md`;
- deployment direction: VPS/VDS или managed hosting;
- concrete task file для первого implementation slice.

До publication handoff пользователь должен явно одобрить:

- frontend preview;
- backend/data readiness или `not-required`;
- total audit;
- remediation или accepted residual risk;
- final user approval;
- publish/operate handoff.

## Практический старт

Если вы только скачали HARNESS_88, начните с такого запроса агенту:

```text
Прочитай START_HERE.md, AGENTS.md, SITE_INTAKE.md, SITE_REFERENCES.md, SITE_GATES.md, PRODUCT.md, DESIGN.md, STACK.md, agents/protocols/tooling-onboarding.md, agents/harness/stack-options.md и agents/workflows/agentic-site-delivery.md.
Проверь tools/skills/plugins/MCP и readiness командами из START_HERE.md.
Проведи первый intake для моего сайта на русском языке.
Не выбирай стек, не обновляй PRODUCT.md, DESIGN.md и STACK.md, не начинай implementation и не подключай внешние ресурсы без моего явного approval.
```

После этого HARNESS_88 поведет проект не как случайный чат "сделай сайт", а как управляемый процесс: вопросы, решения, референсы, стек, задачи, preview, аудит, исправления, финальное approval и понятная публикация.
