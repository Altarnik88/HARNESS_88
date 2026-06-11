# Agent Site Tooling

This clean project starts with the portable site-development harness only.

## Current Project State

- Workspace: `<project-root>`
- Frontend app: `frontend/`
- Frontend stack: Next.js App Router, TypeScript, Tailwind CSS, GSAP-ready package slots.
- Canonical LLM Wiki: `wiki/`
- Generated SQLite state: `data/wiki.sqlite`

## Hard Rules

- Do not begin website implementation until `PRODUCT.md`, `DESIGN.md`, or equivalent approved wiki decisions define the product and design direction.
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
python tools/llm_wiki.py task readiness
python tools/llm_wiki.py quality
```
