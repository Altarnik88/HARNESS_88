# Task: Core Maintainability Security Tooling DB Delivery Adapters

Status: verified
Role owner: Conductor
Created: 2026-06-12

## Objective

Improve core HARNESS_88 maintainability, security dry-run contracts, tooling readiness flow, read-only DB boundaries, and stack-neutral delivery adapter templates without starting site implementation.

## Context Files

- AGENTS.md
- agents/tasks/README.md

## Ownership

Owned files:

- src/llm_wiki/
- tests/
- agents/tasks/
- agents/harness/
- agents/protocols/
- wiki/log.md

Do not edit:

- STACK.md
- PRODUCT.md
- DESIGN.md
- SITE_INTAKE.md
- SITE_REFERENCES.md
- SITE_GATES.md
- raw/
- data/wiki.sqlite
- frontend/

## Allowed Tooling

- Use only tooling granted by agents/tooling-matrix.md and this task file.

## Acceptance Checklist

- Scope is respected.
- Verification command is run.
- Completion evidence is recorded.

## Verification

Command:

```powershell
python tools/llm_wiki.py quality --skip-frontend
```

Expected result:

- exits 0.

## Progress

- Core-only maintainability/security/tooling/DB/deploy-adapter work is complete and verified.
- CLI behavior was preserved while extracting command handlers into focused modules.
- Secret planning is now an executable redacted dry-run contract.
- Tooling readiness output now includes additive grouped next actions without mutation.
- Read-only DB search/event helpers were extracted without schema changes.
- Inactive stack-neutral deploy handoff templates were added without selecting a stack.

## Verification Evidence

- `python tools/llm_wiki.py quality --skip-frontend` passed.
- `python tools/llm_wiki.py site self-test` passed.
- `python tools/llm_wiki.py task validate --strict` passed after evidence was recorded.
- `python tools/llm_wiki.py task evidence --json` passed with no task evidence issues.
- `npm run lint` and `npm run build` passed in `frontend/`.
- `python -m unittest tests.test_security -v` passed after review hardening for uppercase token-shaped secret values.
