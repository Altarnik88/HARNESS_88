# HARNESS_88

[English](README.md) | [Русский](README.ru.md)

HARNESS_88 - это stack-neutral автономное ядро для агентной разработки сайтов. Проект помогает превратить неопределенный запрос на сайт в управляемую работу агентной команды: сбор вводных, выбор стека, согласование продукта и дизайна, поиск референсов, владение задачами, фиксация прогресса, проверки качества, исправление замечаний, финальное одобрение пользователя и handoff к публикации/поддержке.

Начинайте свежие копии проекта с [START_HERE.md](START_HERE.md).

## Какие проблемы решает

- Не дает агентам начинать разработку сайта без выбранного стека, утвержденного продукта, дизайна и референсов.
- Превращает расплывчатый запрос на сайт в контролируемый workflow с долговременными решениями и approval gates.
- Делит работу между профильными ролями вместо сценария, где один ассистент сам исследует, проектирует, пишет код, тестирует и выпускает сайт.
- Сохраняет решения по продукту, дизайну, стеку, референсам, задачам, аудиту и публикации в файлах проекта, которые переживают сброс контекста.
- Снижает хаос во frontend-разработке: референсы должны быть утверждены, а большие сайты режутся на задачи с раздельным владением файлами.
- Поддерживает каталоги, ecommerce, онлайн-оплату, офлайн-оплату и заявки менеджеру через явные решения в intake.
- Держит секреты вне файлов проекта, а runtime outputs считает generated state.

## Как работает

HARNESS_88 разделяет работу над ядром и реализацию конкретного сайта.

- Core-разработка может продолжаться, пока корневые `PRODUCT.md`, `DESIGN.md` и `STACK.md` остаются в draft/unselected состоянии.
- Реализация сайта начинается только после готовности `SITE_INTAKE.md`, `PRODUCT.md`, `DESIGN.md`, утвержденных референсов, выбранного стека и task ownership.
- Скачанная копия может проверить локальные tools, Codex skills, plugins и MCP-related capabilities до начала серьезной работы.
- Доставка отслеживается через `SITE_GATES.md`: approval frontend-превью, backend/data readiness, total audit, remediation, финальное одобрение пользователя и publish handoff.
- Агенты задают вопросы на языке пользователя, а поле `language` в `SITE_INTAKE.md` описывает основной язык сайта.
- Если у пользователя нет референсов, Reference Research предлагает варианты из Dribbble, Behance, Awwwards и релевантных конкурентов до начала frontend-работ.

## Агентная команда

HARNESS_88 использует agent-first модель:

- **Conductor:** планирует, делегирует, ревьюит, проверяет и координирует handoff.
- **Product Strategist:** цели, аудитория, пользовательские задачи, acceptance criteria.
- **Reference Research:** поиск референсов и shortlist для утверждения.
- **IA & Content:** sitemap, slugs, модели страниц, content/metadata briefs.
- **UX/Product Design:** пользовательские flow, responsive behavior, interactions и states.
- **Visual Design:** визуальная система, tokens, imagery direction, asset guidance.
- **Frontend Architecture:** routing, границы компонентов, implementation slices.
- **Frontend Implementation:** назначенные страницы, компоненты, стили и взаимодействия.
- **Backend/Data:** API, каталог/ecommerce/payment/request flows, модели данных.
- **QA & Accessibility:** функциональные проверки, accessibility findings, verified flows.
- **Performance/SEO:** производительность, metadata, SEO и discovery checks.
- **DevOps/Release:** build, deploy, rollback, backup, monitoring и maintenance handoff.
- **Knowledge Steward:** durable wiki decisions, logs и closeout notes.

## Tools и skills

Локальные инструменты ядра:

- `python tools/llm_wiki.py task readiness --json` - готовность и pending decisions.
- `python tools/llm_wiki.py site intake --json` - first-run intake и статус reference gate.
- `python tools/llm_wiki.py site gates --json` - delivery, audit, remediation, approval и publish handoff status.
- `python tools/llm_wiki.py stack list/status/select` - просмотр и выбор stack profiles.
- `python tools/llm_wiki.py site doctor` - единая диагностика readiness, wiki, task graph, frontend, security и generated starter checks.
- `python tools/llm_wiki.py quality --skip-frontend` - stack-neutral quality gate для ядра.
- `python tools/llm_wiki.py rebuild` и `python tools/llm_wiki.py lint` - индекс wiki и Markdown quality checks.
- `python tools/llm_wiki.py tools audit` - аудит локальных tools, Codex skills, plugins и MCP capabilities.

Маршрутизация tools/skills для агентов:

- **Serena MCP:** точечное symbol-level code discovery.
- **Context7 MCP:** актуальная документация framework/SDK/CLI/cloud.
- **Browser plugin / Playwright skill:** локальные UI previews, screenshots, flow checks, responsive и accessibility verification.
- **Product Design plugin:** product/UI context, design variants, image-to-code при выбранном mockup/reference.
- **GitHub plugin / `gh-cli` skill:** repository, pull request, issue и CI workflows.
- **Reference discovery:** Dribbble, Behance, Awwwards, конкуренты и market examples.
- **Optional specialist plugins:** Figma, Canva, Creative Production, imagegen, Sentry, Supabase, Data Analytics, Documents, Spreadsheets и Remotion, когда задача и tooling matrix это разрешают.

Tooling audit работает read-only. Он показывает, что доступно, чего не хватает, и на что агент должен спросить разрешение: установка локальных tools, скачивание skills из GitHub или подключение Codex plugins/skills. HARNESS_88 не должен ничего устанавливать или подключать автоматически.

## Контракты репозитория

- `START_HERE.md`: first-chat инструкции для нового пользователя.
- `SITE_INTAKE.md`: machine-checkable first-run intake и reference approval gate.
- `SITE_GATES.md`: machine-checkable delivery gate state.
- `STACK.md`: контролируемое состояние выбора стека.
- `PRODUCT.md` и `DESIGN.md`: durable product/design contracts.
- `agents/`: role docs, delegation protocol, workflows и harness templates.
- `wiki/`: Markdown-база знаний, поддерживаемая агентами.
- `src/llm_wiki/` и `tools/llm_wiki.py`: локальный CLI для wiki, task, stack, site и quality workflows.
- `frontend/`: optional bundled Next.js starter/template, не выбранный стек по умолчанию.

## Окружение

- Python >= 3.11.
- Node.js/npm нужны только для optional bundled frontend template. Текущий template использует Next.js 16 и ожидает Node >= 20.9.0.

## Первый запуск

```powershell
python tools/llm_wiki.py tools audit --json
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site gates --json
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor --skip-self-test
python tools/llm_wiki.py quality --skip-frontend
```

Если нужно использовать или проверить optional frontend template:

```powershell
cd frontend
npm ci
npm run lint
npm run build
```

## Рабочий процесс

1. Откройте чат в корне репозитория и следуйте `START_HERE.md`.
2. Проведите first-run intake и запишите принятые ответы в `SITE_INTAKE.md`.
3. Выберите stack/fullstack profile и запишите его в `STACK.md`.
4. Заполните `PRODUCT.md` и `DESIGN.md`, затем поставьте `Status: approved`, когда решения приняты.
5. Утвердите пользовательские или агентские референсы и поставьте `references_status: approved`.
6. Создайте атомарные task-файлы через `python tools/llm_wiki.py task create ...`.
7. Реализуйте только из approved intake, approved briefs, selected stack state, approved references и task ownership.
8. Покажите frontend previews, проведите total audit, исправьте findings через tracked tasks и получите финальное одобрение пользователя до publish instructions.

SQLite-файлы в `data/` являются generated state. Их можно удалить и пересобрать через `python tools/llm_wiki.py rebuild`.
