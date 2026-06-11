# Agent Site Tooling

HARNESS_88 starts as a portable, stack-neutral autonomous core. New users should begin with `START_HERE.md`.

## Current Project State

- Workspace: `<project-root>`
- Stack state: `STACK.md` starts unselected and must be updated before production implementation.
- Intake state: `SITE_INTAKE.md` starts draft and must record accepted first-run intake decisions before production implementation.
- Optional frontend template: `frontend/` contains a bundled Next.js starter/template.
- Canonical LLM Wiki: `wiki/`
- Generated SQLite state: `data/wiki.sqlite`

## Hard Rules

- Do not begin website implementation until `STACK.md` has a selected profile or the user explicitly confirms a custom approach.
- Do not begin website implementation until `SITE_INTAKE.md` has `Status: approved`.
- Do not begin website implementation until `PRODUCT.md` and `DESIGN.md` have `Status: approved`, or equivalent approved wiki decisions define the product and design direction.
- Do not begin serious frontend implementation until reference sites, screenshots, or approved agent-proposed reference examples are recorded and `references_status: approved` is set in `SITE_INTAKE.md`.
- Do not publish or provide final deployment instructions until total audit findings are resolved or residual risks are explicitly accepted, and the user has approved the final preview.
- Keep secrets in environment variables only.
- Never ask the user to paste secrets into chat. Follow `agents/workflows/secret-broker.md` for secret-backed backend/deployment setup.
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
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor --skip-self-test
python tools/llm_wiki.py quality --skip-frontend
```

Optional frontend checks:

```powershell
cd frontend
npm ci
npm run lint
npm run build
```

Optional frontend security review:

```powershell
python tools/llm_wiki.py security audit --json --no-record
```
