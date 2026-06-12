# HARNESS_88

[English](README.md) | [Русский](README.ru.md)

HARNESS_88 - это stack-neutral автономное ядро для агентной разработки сайтов. Это не готовый сайт, не встроенное frontend-приложение и не выбранный по умолчанию Next.js/fullstack/hosting вариант. Задача ядра - превратить расплывчатый запрос на сайт в управляемую систему доставки: задать правильные вопросы, сохранить решения, рекомендовать стек, скоординировать профильных агентов, проверить работу и не выпускать сайт до явного одобрения пользователя.

Начинайте свежие копии проекта с [START_HERE.md](START_HERE.md).

## Какие проблемы решает

- Не дает агентам начинать код раньше времени, пока не утверждены цель сайта, стек, продуктовый контракт, дизайн, референсы и reference analysis.
- Превращает запрос в стиле "сделай сайт" в повторяемый workflow с видимыми решениями, approval gates и понятными точками handoff.
- Убирает хаос выбора стека: агент обязан предложить 2-4 конкретных варианта, объяснить плюсы, минусы, сложность поддержки и дождаться явного решения пользователя.
- Сохраняет решения по продукту, дизайну, стеку, референсам, задачам, аудиту и публикации в файлах проекта, которые переживают сброс контекста и передачу между агентами.
- Заменяет перегруженного "одного ассистента на все" профильными ролями: продукт, референсы, UX, визуальный дизайн, frontend, backend/data, QA, SEO, release и проектная память.
- Усиливает работу с референсами: перед серьезной frontend-разработкой нужны утвержденные примеры, bounded page inventory, desktop/mobile screenshot evidence, UX/visual analysis и Figma reference artifact.
- Делает большие сайты управляемыми через task-файлы, progress, checkpoints, review evidence, verification evidence и отдельные remediation-задачи.
- Держит публикацию под контролем: frontend preview approval, audit evidence, final user approval и handoff по VPS/VDS или managed hosting.
- Держит секреты вне файлов проекта, а runtime outputs считает generated state.

## Как работает

HARNESS_88 разделяет работу над ядром и реализацию конкретного сайта.

- Core-разработка может продолжаться, пока корневые `PRODUCT.md`, `DESIGN.md` и `STACK.md` остаются в draft/unselected состоянии.
- Реализация сайта начинается только после готовности `SITE_INTAKE.md`, `SITE_REFERENCES.md`, `PRODUCT.md`, `DESIGN.md`, выбранного стека и task ownership.
- Скачанная копия может проверить локальные tools, Codex skills, plugins и MCP-related capabilities до начала серьезной работы.
- Доставка отслеживается через `SITE_GATES.md`: approval frontend-превью, backend/data readiness, total audit, remediation, финальное одобрение пользователя и publish handoff.
- Агенты задают вопросы на языке пользователя, а поле `language` в `SITE_INTAKE.md` описывает основной язык сайта.
- Если у пользователя нет референсов, Reference Research предлагает варианты из Dribbble, Behance, Awwwards и релевантных конкурентов до начала frontend-работ.

## Что делает ядро по шагам

1. Проводит read-only аудит локальных tools, Codex skills, plugins и MCP-related capabilities. Оно показывает, что доступно, чего не хватает, и спрашивает разрешение перед любой установкой, загрузкой или подключением.
2. Проводит site intake: цель, аудитория, страна, язык сайта, тип сайта, модель контента, catalog/ecommerce/payment/request потребности, backend/data/admin/integration потребности и launch constraints.
3. Рекомендует 2-4 stack/fullstack варианта с языками, frameworks, сервисами, плюсами, минусами, операционной сложностью, scaffold policy и best-fit сценариями. `STACK.md` обновляется только после явного approval или custom stack.
4. Записывает принятые продуктовые и дизайн-решения в `PRODUCT.md` и `DESIGN.md`, затем ждет approval перед реализацией.
5. Получает approval пользовательских референсов или делегирует reference discovery. Утвержденные референсы должны пройти bounded analysis со screenshots, UX/visual findings и Figma reference artifact до серьезной frontend-работы.
6. Создает tracked task files, progress files и checkpoints, чтобы каждый implementation slice имел владельца, evidence, review, verification и handoff trail.
7. Scaffold и сборка stack-specific frontend/backend-файлов начинаются только после approved intake, selected stack, approved product/design briefs, approved references и task ownership.
8. Проводит previews, quality checks, audit/remediation loops, final user approval и publish/operate handoff: объясняет VPS/VDS vs managed hosting и рекомендует подходящий target по ответам пользователя.

## Агентная команда

HARNESS_88 использует agent-first модель:

- **Conductor:** планирует, делегирует, ревьюит, проверяет и координирует handoff.
- **Product Strategist:** цели, аудитория, пользовательские задачи, acceptance criteria.
- **Reference Research:** поиск референсов, shortlist, bounded crawl evidence, screenshot/Figma handoff и поддержка analysis gate.
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
- `python tools/llm_wiki.py site intake --json` - first-run intake и статус reference approval.
- `python tools/llm_wiki.py site references --json` - строгий pre-frontend reference analysis gate.
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
- **Design resources:** huashu-design, impeccable, ui-ux-pro-max, GSAP и Canva выдаются через `agents/protocols/design-resources.md` и фиксируются в `agents/resources/tooling-sources.json`.
- **Optional specialist plugins:** Figma, Canva, Creative Production, imagegen, Sentry, Supabase, Data Analytics, Documents, Spreadsheets и Remotion, когда задача и tooling matrix это разрешают.

Tooling audit работает read-only. Он показывает, что доступно, чего не хватает, и на что агент должен спросить разрешение: установка локальных tools, скачивание skills из GitHub или подключение Codex plugins/skills. HARNESS_88 не должен ничего устанавливать или подключать автоматически.

Ссылки на GitHub-ресурсы фиксируются в `agents/resources/tooling-sources.json`. Перед любой загрузкой из GitHub точный URL репозитория должен быть записан там и одобрен пользователем. Если URL пустой, агент должен спросить правильную ссылку, а не угадывать ее.

## Контракты репозитория

- `START_HERE.md`: first-chat инструкции для нового пользователя.
- `SITE_INTAKE.md`: machine-checkable first-run intake и reference approval gate.
- `SITE_REFERENCES.md`: machine-checkable bounded crawl, screenshots, Figma artifact, UX/visual analysis и user reference approval gate.
- `SITE_GATES.md`: machine-checkable delivery gate state.
- `STACK.md`: контролируемое состояние выбора стека.
- `PRODUCT.md` и `DESIGN.md`: durable product/design contracts.
- `agents/`: role docs, delegation protocol, workflows и harness templates.
- `agents/resources/tooling-sources.json`: реестр источников для GitHub-backed tools, skills и MCP resources.
- `wiki/`: Markdown-база знаний, поддерживаемая агентами.
- `src/llm_wiki/` и `tools/llm_wiki.py`: локальный CLI для wiki, task, stack, site и quality workflows.
- Frontend-приложение не поставляется в составе ядра. Stack выбирается через диалог из целей сайта, типа проекта, content model, backend/data needs, integrations, deployment expectations и maintenance constraints.

## Окружение

- Python >= 3.11.
- Node.js/npm нужны только после того, как пользователь утвердит JavaScript/TypeScript стек, а approved scaffold task создаст соответствующий проект.

## Первый запуск

```powershell
python tools/llm_wiki.py tools audit --json
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site references --json
python tools/llm_wiki.py site gates --json
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor --skip-self-test
python tools/llm_wiki.py quality --skip-frontend
```

## Рабочий процесс

1. Откройте чат в корне репозитория и следуйте `START_HERE.md`.
2. Проведите first-run intake и запишите принятые ответы в `SITE_INTAKE.md`.
3. Получите 2-4 stack/fullstack рекомендации с языками, frameworks, сервисами, плюсами, минусами, операционной сложностью и best-fit сценариями; дождитесь approval или custom stack перед записью в `STACK.md`.
4. Заполните `PRODUCT.md` и `DESIGN.md`, затем поставьте `Status: approved`, когда решения приняты.
5. Утвердите пользовательские или агентские референсы и поставьте `references_status: approved`.
6. Заполните `SITE_REFERENCES.md`: bounded crawl, desktop/mobile screenshots, Figma reference artifact, UX/visual analysis и explicit user approval.
7. Спросите, публикация планируется на VPS/VDS или managed hosting; объясните плюсы/минусы и рекомендуйте вариант по операционным, бюджетным, traffic, backend и maintenance ответам пользователя.
8. Создайте атомарные task-файлы через `python tools/llm_wiki.py task create ...`.
9. Реализуйте только из approved intake, approved briefs, selected stack state, approved reference analysis, selected deployment direction и task ownership.
10. Покажите frontend previews, проведите total audit, исправьте findings через tracked tasks и получите финальное одобрение пользователя до publish instructions.

SQLite-файлы в `data/` являются generated state. Их можно удалить и пересобрать через `python tools/llm_wiki.py rebuild`.
