# Task: Core Harness Refactor Diagnostics Evidence Semantics

Status: verified
Role owner: Conductor
Created: 2026-06-12

## Objective

Refactor core HARNESS_88 CLI diagnostics, gate parsing, task evidence semantics, tooling audit, and security audit reporting without starting site implementation.

## Context Files

- AGENTS.md
- agents/tasks/README.md

## Ownership

Owned files:

- src/llm_wiki/
- tests/
- agents/tasks/
- wiki/log.md

Do not edit:

- STACK.md
- PRODUCT.md
- DESIGN.md
- SITE_INTAKE.md
- SITE_REFERENCES.md
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

- Implementation completed for core diagnostics, gate parsing, task evidence semantics, tooling audit, and security audit reporting.
- Verification evidence: `python tools/llm_wiki.py quality --skip-frontend` exited 0 with 131 tests OK, wiki rebuild OK, and strict lint OK.
- Verification evidence: `python tools/llm_wiki.py site self-test` exited 0.
- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0 before status verification; final validation is rerun after this evidence entry.
- Verification evidence: `npm run lint` and `npm run build` in `frontend/` exited 0.
