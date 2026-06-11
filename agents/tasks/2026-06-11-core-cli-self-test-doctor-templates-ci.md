# Task: Core CLI Self Test Doctor Templates CI

Status: verified
Role owner: Conductor
Created: 2026-06-11

## Objective

Implement generated-project self-tests, site doctor, explicit brief statuses, data-driven templates/profiles, stronger task validation, split CI, and non-blocking frontend security audit for the HARNESS_88 core.

## Context Files

- AGENTS.md
- agents/tasks/README.md

## Ownership

Owned files:

- src/llm_wiki/
- tests/
- agents/harness/
- agents/tasks/
- README.md
- START_HERE.md
- PRODUCT.md
- DESIGN.md
- STACK.md
- AGENT_SITE_TOOLING.md
- .github/workflows/quality.yml
- wiki/log.md
- wiki/review.md

Do not edit:

- raw/
- data/wiki.sqlite

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

- Implemented generated-project self-tests, `site doctor`, explicit brief statuses, data-driven starter templates and stack profiles, stronger task validation, split CI, and non-blocking frontend security audit.
- Clarified readiness semantics: root draft briefs and unselected stack block concrete site implementation, not core engineering on HARNESS_88 itself.
- Verification evidence: `python -m unittest discover -s tests` exited 0 with 74 tests OK.
- Verification evidence: `python tools/llm_wiki.py quality --skip-frontend` exited 0.
- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0 with no task validation issues.
- Verification evidence: `python tools/llm_wiki.py site self-test` exited 0.
- Verification evidence: `python tools/llm_wiki.py site init C:\tmp\harness88-selftest-20260611-impl --self-test` exited 0.
- Verification evidence: `python tools/llm_wiki.py site doctor --json --skip-self-test` exited 0.
- Verification evidence: `python tools/llm_wiki.py security audit --json --no-record` exited 0; escalated network run reported unresolved optional frontend audit items non-blockingly.
- Verification evidence: `npm run lint` in `frontend/` exited 0.
- Verification evidence: `npm run build` in `frontend/` exited 0.
