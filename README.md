# HARNESS_88

[English](README.md) | [Русский](README.ru.md)

HARNESS_88 is a stack-neutral autonomous core for agent-driven website delivery. It is not a finished website, not a bundled frontend app, and not a default Next.js/fullstack/hosting choice. Its job is to turn a vague website request into a controlled delivery system: ask the right questions, preserve decisions, recommend a stack, coordinate specialist agents, verify work, and keep publication gated until the user approves it.

Start fresh clones with [START_HERE.md](START_HERE.md).

## What It Solves

- Stops agents from coding too early, before the site goal, stack, product contract, design direction, references, and reference analysis are approved.
- Turns a vague request like "build me a site" into a repeatable workflow with visible decisions, approval gates, and handoff points.
- Prevents stack chaos by forcing a recommendation step with 2-4 concrete options, tradeoffs, operational complexity, and explicit user approval.
- Preserves product, design, stack, reference analysis, task, audit, and publish decisions in files that survive context resets and agent handoffs.
- Replaces one overloaded assistant with specialist roles for product, references, UX, visual design, frontend, backend/data, QA, SEO, release, and project memory.
- Reduces weak reference work by requiring approved examples, bounded page inventory, desktop/mobile screenshot evidence, UX/visual analysis, and a Figma reference artifact before serious frontend work.
- Gives larger sites clear ownership through tracked task files, progress files, checkpoints, review evidence, and remediation tasks.
- Keeps publish work gated by preview approval, audit evidence, final user approval, and a VPS/VDS or managed-hosting handoff.
- Keeps secrets out of project files and treats runtime outputs as generated state.

## How It Works

HARNESS_88 separates core engineering from concrete site implementation.

- Core work can continue while root `PRODUCT.md`, `DESIGN.md`, and `STACK.md` are still draft or unselected.
- Site implementation starts only after `SITE_INTAKE.md`, `SITE_REFERENCES.md`, `PRODUCT.md`, `DESIGN.md`, selected stack, and task ownership are ready.
- A downloaded copy can audit the user's local tools, Codex skills, plugins, and MCP-related capabilities before serious work starts.
- Delivery is tracked through `SITE_GATES.md`: frontend preview approval, backend/data readiness, total audit, remediation, final user approval, and publish handoff.
- Agents ask questions in the user's language, while `SITE_INTAKE.md` `language` records the site's primary language.
- If the user has no references, Reference Research proposes examples from Dribbble, Behance, Awwwards, and relevant competitors before frontend work starts.

## What The Core Does Step By Step

1. Audits local tools, Codex skills, plugins, and MCP-related capabilities in read-only mode with `python tools/llm_wiki.py tools audit --json`. It reports gaps through `next_actions`; the agent asks permission before installing local tools, downloading GitHub-backed skills/resources, connecting Codex plugins/MCP, or adding frontend dependencies.
2. Runs site intake: goal, audience, country, site language, site type, content model, catalog/ecommerce/payment/request needs, backend/data/admin/integration needs, and launch constraints.
3. Recommends 2-4 stack or fullstack options with languages, frameworks, services, pros, cons, operational complexity, scaffold policy, and best-fit use cases. It waits for explicit approval or a custom stack before updating `STACK.md`.
4. Records accepted product and design decisions in `PRODUCT.md` and `DESIGN.md`, then waits for approval before implementation.
5. Gets user approval for reference sites or delegates reference discovery. Approved references must pass bounded analysis with screenshots, UX/visual findings, and a Figma reference artifact before serious frontend work.
6. Creates tracked task files, progress files, and checkpoints so each implementation slice has an owner, evidence, review, verification, and handoff trail.
7. Scaffolds and builds stack-specific frontend/backend files only after intake, stack, product, design, references, and task ownership are approved.
8. Runs previews, quality checks, audit/remediation loops, final user approval, and a publish/operate handoff that explains VPS/VDS versus managed hosting and recommends the better target from the user's answers.

## Agent Team

HARNESS_88 uses an agent-first operating model:

- **Conductor:** plans, delegates, reviews, verifies, and coordinates handoff.
- **Product Strategist:** goals, audience, user jobs, acceptance criteria.
- **Reference Research:** reference discovery, shortlist approval, bounded crawl evidence, screenshot/Figma handoff, and analysis gate support.
- **IA & Content:** sitemap, slugs, page models, content and metadata briefs.
- **UX/Product Design:** divergent flow/interaction exploration, responsive behavior, states, and convergence handoff.
- **Visual Design:** named visual territories, visual system, tokens, imagery direction, asset guidance, and rejected-direction rationale.
- **Design Artifact:** Figma reference boards, exploration boards, evidence organization, and artifact handoff.
- **Frontend Architecture:** routing, component boundaries, implementation slices.
- **Frontend Implementation:** assigned pages, components, styling, interactions.
- **Backend/Data:** APIs, catalog/ecommerce/payment/request flows, data models.
- **QA & Accessibility:** functional checks, accessibility findings, verified flows.
- **Performance/SEO:** performance, metadata, SEO, and discovery checks.
- **DevOps/Release:** build, deploy, rollback, backup, monitoring, and maintenance handoff.
- **Knowledge Steward:** durable wiki decisions, logs, and closeout notes.

## Tools And Skills

Core local tools:

- `python tools/llm_wiki.py task readiness --json` - readiness and pending decisions.
- `python tools/llm_wiki.py site intake --json` - first-run intake and reference approval status.
- `python tools/llm_wiki.py site references --json` - strict pre-frontend reference analysis gate status.
- `python tools/llm_wiki.py site gates --json` - delivery, audit, remediation, approval, and publish handoff status.
- `python tools/llm_wiki.py stack list/status/select` - stack profile discovery and selection.
- `python tools/llm_wiki.py site doctor --skip-self-test` - fast unified diagnostics for readiness, wiki, task graph, frontend, security, and tooling.
- `python tools/llm_wiki.py quality --skip-frontend` - stack-neutral core quality gate.
- `python tools/llm_wiki.py rebuild` and `python tools/llm_wiki.py lint` - wiki index and Markdown quality checks.
- `python tools/llm_wiki.py tools audit --json` - local tools, Codex skills, plugins, and MCP capability audit.
- `python tools/llm_wiki.py conductor start/route/delegate` - Conductor bootstrap, phase routing, and delegation-packet creation.

Agent routing supports:

- **Serena MCP:** focused symbol-level code discovery.
- **Context7 MCP:** current framework, SDK, CLI, and cloud documentation.
- **Browser plugin / Playwright skill:** local UI previews, screenshots, flow checks, responsive and accessibility verification.
- **Product Design plugin:** product/UI context, design variants, image-to-code when a mockup or reference is selected.
- **GitHub plugin / `gh-cli` skill:** repository, pull request, issue, and CI workflows.
- **Reference discovery:** Dribbble, Behance, Awwwards, competitors, and market examples.
- **Design resources:** huashu-design, impeccable, ui-ux-pro-max, GSAP, Canva, and Creative Production are granted through `agents/protocols/design-resources.md` and tracked in `agents/resources/tooling-sources.json`.
- **Optional specialist plugins:** Figma, Canva, Creative Production, imagegen, Sentry, Supabase, Data Analytics, Documents, Spreadsheets, and Remotion when the task and tooling matrix allow them.

The tooling audit is read-only. `python tools/llm_wiki.py tools audit --json` reports what appears available, what is missing, and `next_actions`; the agent must ask permission before installing local tools, downloading GitHub-backed skills/resources, connecting Codex plugins/MCP, or adding frontend dependencies. HARNESS_88 must not install or connect anything automatically.

GitHub-backed resource links live in `agents/resources/tooling-sources.json`. Before any GitHub download, the exact repository URL must be recorded there and approved by the user. If the URL is blank, the agent must ask for the correct link instead of guessing.

## Repository Contracts

- `START_HERE.md`: first-chat instructions for a new user.
- `SITE_INTAKE.md`: machine-checkable first-run intake and reference approval gate.
- `SITE_REFERENCES.md`: machine-checkable bounded crawl, screenshots, Figma artifact, UX/visual analysis, and user reference approval gate.
- `SITE_GATES.md`: machine-checkable delivery gate state.
- `STACK.md`: controlled stack selection state.
- `PRODUCT.md` and `DESIGN.md`: durable product and design contracts.
- `agents/`: role docs, delegation protocol, workflows, and harness templates.
- `agents/resources/tooling-sources.json`: source registry for GitHub-backed tools, skills, and MCP resources.
- `wiki/`: LLM-maintained Markdown knowledge base.
- `src/llm_wiki/` and `tools/llm_wiki.py`: local CLI for wiki, task, stack, site, and quality workflows.
- No frontend app is bundled. Stack is selected through dialogue from the user's goals, site type, content model, backend/data needs, integrations, deployment expectations, and maintenance constraints.

## Environment

- Python >= 3.11.
- Node.js/npm are required only after the user approves a JavaScript/TypeScript stack and an approved scaffold task creates that project.

## First Run

```powershell
python tools/llm_wiki.py conductor start
python tools/llm_wiki.py tools audit --json
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site references --json
python tools/llm_wiki.py site gates --json
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py conductor route --phase reference-analysis
python tools/llm_wiki.py site doctor --skip-self-test
python tools/llm_wiki.py quality --skip-frontend
```

Reserve `python tools/llm_wiki.py site self-test` for generator or starter-template changes.

## Development Flow

1. Open a chat in the repository root and follow `START_HERE.md`.
2. Run first-run intake and record accepted answers in `SITE_INTAKE.md`.
3. Recommend 2-4 stack/fullstack options with languages, frameworks, services, pros, cons, operational complexity, and best-fit use cases; wait for user approval or a custom stack before recording the choice in `STACK.md`.
4. Fill `PRODUCT.md` and `DESIGN.md`, then set them to `Status: approved` when accepted.
5. Approve user-provided or agent-proposed references and set `references_status: approved`.
6. Complete `SITE_REFERENCES.md`: bounded crawl, desktop/mobile screenshots, Figma reference artifact, UX/visual analysis, and explicit user approval.
7. Ask whether publication should target VPS/VDS or managed hosting, explain pros and cons of each, and recommend the better option from the user's operational, budget, traffic, backend, and maintenance answers.
8. Create atomic task files with `python tools/llm_wiki.py task create ...`.
9. Scaffold and implement only from approved intake, approved briefs, selected stack state, approved reference analysis, selected deployment direction, and task ownership.
10. Show frontend previews, run total audit, fix findings through tracked tasks, and get final user approval before publish instructions.

SQLite files under `data/` are generated state. Delete and rebuild them with `python tools/llm_wiki.py rebuild` whenever needed.
