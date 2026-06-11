# HARNESS_88

[English](README.md) | [Русский](README.ru.md)

HARNESS_88 is a stack-neutral autonomous core for agent-driven website delivery. It helps turn an ambiguous website request into coordinated agent-team work: intake, stack selection, product and design approval, reference discovery, task ownership, progress tracking, quality checks, remediation, final user approval, and publish/operate handoff.

Start fresh clones with [START_HERE.md](START_HERE.md).

## What It Solves

- Prevents agents from starting site implementation before stack, product, design, and references are approved.
- Turns one vague website request into a controlled workflow with durable decisions and approval gates.
- Splits work across specialist roles instead of letting one assistant design, build, test, and release everything alone.
- Keeps product, design, stack, reference, task, audit, and publish decisions in project files that survive context resets.
- Reduces chaotic frontend work by requiring approved references and disjoint implementation ownership.
- Supports catalog, ecommerce, online payment, offline payment, and manager-request flows through explicit intake decisions.
- Keeps secrets out of project files and treats runtime outputs as generated state.

## How It Works

HARNESS_88 separates core engineering from concrete site implementation.

- Core work can continue while root `PRODUCT.md`, `DESIGN.md`, and `STACK.md` are still draft or unselected.
- Site implementation starts only after `SITE_INTAKE.md`, `PRODUCT.md`, `DESIGN.md`, approved references, selected stack, and task ownership are ready.
- Delivery is tracked through `SITE_GATES.md`: frontend preview approval, backend/data readiness, total audit, remediation, final user approval, and publish handoff.
- Agents ask questions in the user's language, while `SITE_INTAKE.md` `language` records the site's primary language.
- If the user has no references, Reference Research proposes examples from Dribbble, Behance, Awwwards, and relevant competitors before frontend work starts.

## Agent Team

HARNESS_88 uses an agent-first operating model:

- **Conductor:** plans, delegates, reviews, verifies, and coordinates handoff.
- **Product Strategist:** goals, audience, user jobs, acceptance criteria.
- **Reference Research:** reference discovery and shortlist approval.
- **IA & Content:** sitemap, slugs, page models, content and metadata briefs.
- **UX/Product Design:** flows, responsive behavior, interactions, and states.
- **Visual Design:** visual system, tokens, imagery direction, asset guidance.
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
- `python tools/llm_wiki.py site intake --json` - first-run intake and reference gate status.
- `python tools/llm_wiki.py site gates --json` - delivery, audit, remediation, approval, and publish handoff status.
- `python tools/llm_wiki.py stack list/status/select` - stack profile discovery and selection.
- `python tools/llm_wiki.py site doctor` - unified diagnostics for readiness, wiki, task graph, frontend, security, and generated starter checks.
- `python tools/llm_wiki.py quality --skip-frontend` - stack-neutral core quality gate.
- `python tools/llm_wiki.py rebuild` and `python tools/llm_wiki.py lint` - wiki index and Markdown quality checks.

Agent routing supports:

- **Serena MCP:** focused symbol-level code discovery.
- **Context7 MCP:** current framework, SDK, CLI, and cloud documentation.
- **Browser plugin / Playwright skill:** local UI previews, screenshots, flow checks, responsive and accessibility verification.
- **Product Design plugin:** product/UI context, design variants, image-to-code when a mockup or reference is selected.
- **GitHub plugin / `gh-cli` skill:** repository, pull request, issue, and CI workflows.
- **Reference discovery:** Dribbble, Behance, Awwwards, competitors, and market examples.
- **Optional specialist plugins:** Figma, Canva, Creative Production, imagegen, Sentry, Supabase, Data Analytics, Documents, Spreadsheets, and Remotion when the task and tooling matrix allow them.

## Repository Contracts

- `START_HERE.md`: first-chat instructions for a new user.
- `SITE_INTAKE.md`: machine-checkable first-run intake and reference approval gate.
- `SITE_GATES.md`: machine-checkable delivery gate state.
- `STACK.md`: controlled stack selection state.
- `PRODUCT.md` and `DESIGN.md`: durable product and design contracts.
- `agents/`: role docs, delegation protocol, workflows, and harness templates.
- `wiki/`: LLM-maintained Markdown knowledge base.
- `src/llm_wiki/` and `tools/llm_wiki.py`: local CLI for wiki, task, stack, site, and quality workflows.
- `frontend/`: optional bundled Next.js starter/template, not the default selected stack.

## Environment

- Python >= 3.11.
- Node.js/npm are only required for the optional bundled frontend template. The current template uses Next.js 16 and expects Node >= 20.9.0.

## First Run

```powershell
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site gates --json
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor --skip-self-test
python tools/llm_wiki.py quality --skip-frontend
```

If you plan to use or verify the optional frontend template:

```powershell
cd frontend
npm ci
npm run lint
npm run build
```

## Development Flow

1. Open a chat in the repository root and follow `START_HERE.md`.
2. Run first-run intake and record accepted answers in `SITE_INTAKE.md`.
3. Choose a stack/fullstack profile and record it in `STACK.md`.
4. Fill `PRODUCT.md` and `DESIGN.md`, then set them to `Status: approved` when accepted.
5. Approve user-provided or agent-proposed references and set `references_status: approved`.
6. Create atomic task files with `python tools/llm_wiki.py task create ...`.
7. Implement only from approved intake, approved briefs, selected stack state, approved references, and task ownership.
8. Show frontend previews, run total audit, fix findings through tracked tasks, and get final user approval before publish instructions.

SQLite files under `data/` are generated state. Delete and rebuild them with `python tools/llm_wiki.py rebuild` whenever needed.
