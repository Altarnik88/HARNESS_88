# Agent Site Tooling

HARNESS_88 starts as a portable, stack-neutral autonomous core. New users should begin with `START_HERE.md`.

## Current Project State

- Workspace: `<project-root>`
- Stack state: `STACK.md` starts unselected and must be updated before production implementation.
- Optional frontend template: `frontend/` contains a bundled Next.js starter/template.
- Canonical LLM Wiki: `wiki/`
- Generated SQLite state: `data/wiki.sqlite`

## Hard Rules

- Do not begin website implementation until `STACK.md` has a selected profile or the user explicitly confirms a custom approach.
- Do not begin website implementation until `PRODUCT.md`, `DESIGN.md`, or equivalent approved wiki decisions define the product and design direction.
- Keep secrets in environment variables only.
- Treat `data/wiki.sqlite` as generated state.
- Preserve files under `raw/` during ingest.
- For multi-agent website work, read `agents/TEAM.md` before delegation.
- Real implementation requires a concrete task file in `agents/tasks/` or an equivalent approved plan.

## Optional Frontend Template

The `frontend/` directory is provided as an optional bundled Next.js starter/template. It is useful when the selected profile is compatible with Next.js, but HARNESS_88 does not assume it is selected.

Install frontend dependencies only when frontend checks or implementation are in scope:

```powershell
cd frontend
npm ci
```

## Default Checks

Core checks:

```powershell
python -m unittest discover -s tests
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py stack status
python tools/llm_wiki.py quality --skip-frontend
```

Optional frontend checks:

```powershell
cd frontend
npm ci
npm run lint
npm run build
```
