# AGENTS.md

This file is the compact project contract for Codex agents. Keep `AGENTS.md` and `CLAUDE.md` files under 150 lines. Move detailed operating rules into linked protocol files instead of expanding this file.

## Project Role

HARNESS_88 is a stack-neutral autonomous core for site-development work.

New users start from `START_HERE.md`, choose a stack/fullstack profile, and record it in `STACK.md`.

Do not assume Next.js or fullstack has already been selected. The `frontend/` directory is an optional bundled Next.js starter/template, not the default stack.

## Read First

- `START_HERE.md` - first-run workflow for new users.
- `STACK.md` - selected stack state; implementation waits until selected or custom is explicitly confirmed.
- `PRODUCT.md` - durable product contract.
- `DESIGN.md` - durable design contract.
- `purpose.md` - directional contract.
- `schema.md` - wiki structure contract.
- `wiki/index.md` and recent `wiki/log.md` entries - durable project memory.

## Detailed Protocols

- `agents/protocols/mcp-policy.md` - MCP/tool-surface policy and secret handling.
- `agents/protocols/wiki-operations.md` - wiki invariants, ingest, query, and lint workflow.
- `agents/protocols/skill-capture.md` - when repeated behavior should become a reusable Codex skill.
- `agents/TEAM.md` - multi-agent and one-agent fallback protocol.
- `agents/harness/README.md` - task/progress/checkpoint execution model.
- `agents/tooling-matrix.md` - allowed tools by role.

## Core Rules

- Preserve user edits. Never revert or overwrite unrelated changes.
- Keep `raw/` source files immutable during ingest.
- Treat `data/wiki.sqlite` and other runtime outputs as generated state.
- Keep secrets out of `AGENTS.md`, project files, skill resources, MCP arguments, and Codex config; use environment variables.
- Search existing pages and files before creating new ones.
- Prefer small, linked wiki pages over one large note.
- Update `wiki/index.md` and append to `wiki/log.md` for durable wiki changes.
- Run the relevant verification command before claiming completion.

## Implementation Gate

Before production implementation:

- Confirm `STACK.md` is selected, or the user explicitly confirmed a custom approach.
- Confirm product/design direction is approved in `PRODUCT.md`, `DESIGN.md`, or equivalent wiki decisions.
- Create or update a concrete task file in `agents/tasks/`.
- Keep linked progress and checkpoint files current for clean handoff.

## Common Commands

```powershell
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py stack status
python tools/llm_wiki.py quality --skip-frontend
python tools/llm_wiki.py rebuild
python tools/llm_wiki.py lint
```
