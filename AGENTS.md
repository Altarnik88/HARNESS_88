# AGENTS.md

This file is the compact project contract for Codex agents. Keep `AGENTS.md` and `CLAUDE.md` files under 150 lines. Move detailed operating rules into linked protocol files instead of expanding this file.

## Project Role

HARNESS_88 is a stack-neutral autonomous core for site-development work.

New users start from `START_HERE.md`, complete `SITE_INTAKE.md`, compare stack/fullstack options, approve one option or a custom stack, and record it in `STACK.md`.

Do not assume Next.js, fullstack, VPS/VDS, or managed hosting has already been selected. No frontend app is bundled. Stack is selected through dialogue from the user's goals, site type, content model, backend/data needs, integrations, deployment expectations, and maintenance constraints.

Root `PRODUCT.md`, `DESIGN.md`, and `STACK.md` describe the site-project workflow gate. Their draft/unselected state blocks concrete site implementation, not core engineering work on HARNESS_88 itself.

## Read First

- `START_HERE.md` - first-run workflow for new users.
- `SITE_INTAKE.md` - first-run site intake and reference approval gate.
- `SITE_REFERENCES.md` - strict pre-frontend reference analysis gate.
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
- `agents/protocols/conversation-delegation.md` - user-language, reference-discovery, and agent-first delegation protocol.
- `agents/protocols/conductor-runtime.md` - executable Conductor bootstrap, routing, and delegation-packet gate.
- `agents/protocols/tooling-onboarding.md` - first-run tools/skills/plugins audit and permission flow.
- `agents/protocols/design-resources.md` - design resource grants for UX, visual, motion, and Canva work.
- `agents/TEAM.md` - multi-agent and one-agent fallback protocol.
- `agents/harness/README.md` - task/progress/checkpoint execution model.
- `agents/resources/tooling-sources.json` - source registry for GitHub-backed tools, skills, and MCP resources.
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
- Confirm `SITE_INTAKE.md` is approved and references are approved.
- Confirm `SITE_REFERENCES.md` is approved and `python tools/llm_wiki.py site references --json` reports complete reference analysis before serious frontend work.
- Confirm product/design direction is explicitly approved in `PRODUCT.md`, `DESIGN.md`, or equivalent wiki decisions.
- Create or update a concrete task file in `agents/tasks/`.
- Keep linked progress and checkpoint files current for clean handoff.

## Common Commands

```powershell
python tools/llm_wiki.py task readiness --json
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py site references --json
python tools/llm_wiki.py stack status
python tools/llm_wiki.py site doctor --skip-self-test
python tools/llm_wiki.py quality --skip-frontend
python tools/llm_wiki.py rebuild
python tools/llm_wiki.py lint
```
