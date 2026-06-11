# Agent Site Tooling

This clean project starts with the portable, stack-neutral site-development harness only.

## Current Project State

- Workspace: `<project-root>`
- Stack state: `STACK.md` starts unselected and must be updated before production implementation.
- Optional frontend template: `frontend/` contains a bundled Next.js starter/template.
- Canonical LLM Wiki: `wiki/`
- Generated SQLite state: `data/wiki.sqlite`

## Hard Rules

- Do not begin website implementation until `STACK.md` has a selected profile or the user explicitly confirms a custom approach.
- Do not begin website implementation until `PRODUCT.md` and `DESIGN.md` have `Status: approved`, or equivalent approved wiki decisions define the product and design direction.
- Keep secrets in environment variables only.
- Treat `data/wiki.sqlite` as generated state.
- Preserve files under `raw/` during ingest.
- For multi-agent website work, read `agents/TEAM.md` before delegation.
- Real implementation requires a concrete task file in `agents/tasks/` or an equivalent approved plan.

## Optional Resources

Project-local design and AI skill packs are intentionally not bundled in this generated starter. Install or copy them only when a task explicitly needs them, then record the decision in the wiki.

## Default Checks

```powershell
python -m unittest discover -s tests
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor
python tools/llm_wiki.py quality --skip-frontend
```
