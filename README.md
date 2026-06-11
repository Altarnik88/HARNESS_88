# HARNESS_88

HARNESS_88 is a stack-neutral autonomous core for site-development work. It gives a coding agent durable briefs, task files, progress/checkpoint files, wiki memory, and quality gates before any production implementation starts.

Start fresh clones with [START_HERE.md](START_HERE.md).

## What Is Included

- `START_HERE.md`: first-chat instructions for a new user.
- `STACK.md`: the controlled stack selection state. It starts as `status: unselected`.
- `PRODUCT.md` and `DESIGN.md`: durable product and design contracts with explicit `draft`, `approved`, or `needs-review` statuses.
- `agents/`: role docs, delegation protocol, and harness templates.
- `wiki/`: LLM-maintained Markdown knowledge base.
- `src/llm_wiki/` and `tools/llm_wiki.py`: local CLI for wiki, task, stack, and quality workflows.
- `frontend/`: optional bundled Next.js starter/template, not the default selected stack.

## Environment

- Python >= 3.11.
- Node.js/npm are only required for the optional bundled frontend template. The current template uses Next.js 16 and expects Node >= 20.9.0.

## First Run

```powershell
python tools/llm_wiki.py task readiness --json
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
2. Choose a stack/fullstack profile and record it in `STACK.md`.
3. Fill in `PRODUCT.md` with the website goal, audience, scope, and acceptance criteria, then set `Status: approved` when accepted.
4. Fill in `DESIGN.md` with visual direction, UX constraints, and component rules, then set `Status: approved` when accepted.
5. Create atomic task files with `python tools/llm_wiki.py task create ...`.
6. Implement only from approved briefs, selected stack state, and task ownership.
7. Run `python tools/llm_wiki.py quality --skip-frontend` for core checks, and frontend checks only when the optional frontend is in scope.

## Core Diagnostics

- `python tools/llm_wiki.py site doctor` reports readiness, stack, briefs, task graph, wiki health, frontend state, security state, and generated-project self-test.
- `python tools/llm_wiki.py site self-test` creates a temporary clean starter and runs its core quality gate.
- `python tools/llm_wiki.py security audit --json --no-record` runs optional frontend `npm audit` when available. Security audit is non-blocking by default; add `--blocking` to make unresolved findings fail.
- Core CI is stack-neutral. Optional frontend CI runs separately when `frontend/package.json` is present.

SQLite files under `data/` are generated state. Delete and rebuild them with `python tools/llm_wiki.py rebuild` whenever needed.
