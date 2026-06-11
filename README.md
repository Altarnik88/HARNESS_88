# HARNESS_88

HARNESS_88 is a stack-neutral autonomous core for site-development work. It gives a coding agent durable briefs, task files, progress/checkpoint files, wiki memory, approval gates, audit/remediation loops, and release handoff before any production implementation ships.

Start fresh clones with [START_HERE.md](START_HERE.md).

## Working On The Core

This repository is the reusable core, not a concrete site project. It is expected for root `PRODUCT.md` and `DESIGN.md` to remain `Status: draft`, and for root `STACK.md` to remain unselected, while core CLI, generator, template, CI, task, and wiki workflow work continues through `agents/tasks/`.

In readiness and doctor output, `core_development_ready` means the HARNESS_88 core workflow is healthy enough to work on. `site_implementation_ready` means a concrete site has approved briefs and a selected stack.

## What Is Included

- `START_HERE.md`: first-chat instructions for a new user.
- `SITE_INTAKE.md`: machine-checkable first-run intake and reference approval gate.
- `STACK.md`: the controlled stack selection state. It starts as `status: unselected`.
- `PRODUCT.md` and `DESIGN.md`: durable product and design contracts with explicit `draft`, `approved`, or `needs-review` statuses.
- `agents/`: role docs, delegation protocol, and harness templates.
- `agents/workflows/agentic-site-delivery.md`: canonical agentic site delivery workflow from intake to final audit, user approval, and VPS handoff.
- `agents/workflows/secret-broker.md`: contract for secret-safe backend/deployment configuration without exposing secret values to agents.
- `wiki/`: LLM-maintained Markdown knowledge base.
- `src/llm_wiki/` and `tools/llm_wiki.py`: local CLI for wiki, task, stack, and quality workflows.
- `frontend/`: optional bundled Next.js starter/template, not the default selected stack.

## Environment

- Python >= 3.11.
- Node.js/npm are only required for the optional bundled frontend template. The current template uses Next.js 16 and expects Node >= 20.9.0.

## First Run

```powershell
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py stack list
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor --skip-self-test
python tools/llm_wiki.py quality --skip-frontend
```

If you plan to use or verify the optional frontend template after a fresh clone:

```powershell
cd frontend
npm ci
npm run lint
npm run build
```

## Development Flow

1. Open a chat in the repository root and follow `START_HERE.md`.
2. Run the first-run intake and record accepted answers in `SITE_INTAKE.md`.
3. Choose a stack/fullstack profile and record it in `STACK.md`.
4. Fill in `PRODUCT.md` with the website goal, audience, scope, and acceptance criteria, then set `Status: approved` when accepted.
5. Include commerce mode in the brief: no commerce, catalog only, online payment, offline payment, request to manager, or mixed.
6. Fill in `DESIGN.md` with visual direction, UX constraints, reference expectations, and component rules, then set `Status: approved` when accepted.
7. Approve user-provided or agent-proposed reference sites and set `references_status: approved` in `SITE_INTAKE.md` before serious frontend implementation.
8. Create atomic task files with `python tools/llm_wiki.py task create ...`.
9. Implement only from approved intake, approved briefs, selected stack state, approved references, and task ownership.
10. Show frontend previews for approval, then implement backend/data/payment/request flows as approved.
11. Run total agent audit, fix findings through tracked tasks, and show the final site for user approval before publish instructions.
12. Run `python tools/llm_wiki.py quality --skip-frontend` for core checks, and frontend checks only when the optional frontend is in scope.

## Core Diagnostics

- `python tools/llm_wiki.py site doctor` reports readiness, stack, briefs, task graph, wiki health, frontend state, security state, and generated-project self-test.
- `python tools/llm_wiki.py site self-test` creates a temporary clean starter and runs its core quality gate.
- `python tools/llm_wiki.py security audit --json --no-record` runs optional frontend `npm audit` when available. Security audit is non-blocking by default; add `--blocking` to make unresolved findings fail.
- Core CI is stack-neutral. Optional frontend CI runs separately when `frontend/package.json` is present.

SQLite files under `data/` are generated state. Delete and rebuild them with `python tools/llm_wiki.py rebuild` whenever needed.
