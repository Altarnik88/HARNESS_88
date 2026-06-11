# Task: Site Intake Approval Gates

Status: verified
Role owner: Conductor
Created: 2026-06-11

## Objective

Add core-level, machine-checkable first-run site intake and reference approval gates without creating a concrete site or selecting a stack.

## Context Files

- AGENTS.md
- START_HERE.md
- README.md
- SITE_INTAKE.md
- AGENT_SITE_TOOLING.md
- agents/workflows/agentic-site-delivery.md
- agents/harness/README.md

## Ownership

Owned files:

- SITE_INTAKE.md
- agents/harness/site-intake-template.md
- src/llm_wiki/intake.py
- src/llm_wiki/tasks.py
- src/llm_wiki/cli.py
- src/llm_wiki/doctor.py
- src/llm_wiki/harness.py
- src/llm_wiki/site_generator.py
- src/llm_wiki/templates/site_starter/
- tests/test_intake.py
- tests/test_tasks.py
- tests/test_task_cli.py
- tests/test_doctor.py
- tests/test_site_generator.py
- tests/test_harness.py
- START_HERE.md
- README.md
- AGENTS.md
- AGENT_SITE_TOOLING.md
- agents/workflows/agentic-site-delivery.md
- agents/harness/README.md
- agents/harness/acceptance-checklists.md
- wiki/log.md
- agents/tasks/2026-06-11-site-intake-approval-gates.md
- agents/tasks/progress/2026-06-11-site-intake-approval-gates.md
- agents/tasks/checkpoints/2026-06-11-site-intake-approval-gates.md

Do not edit:

- raw/
- data/wiki.sqlite

## Allowed Tooling

- Local shell commands for tests and read-only inspection.
- Serena MCP for symbol-level code discovery.
- No new runtime dependencies.
- No secrets may be recorded.

## Acceptance Checklist

- HARNESS_88 remains a stack-neutral core and no concrete site is created in the root.
- `SITE_INTAKE.md` and the generated-starter template cover required intake decisions.
- `site intake` is read-only and supports `--json`.
- `task readiness` and `site doctor` report intake and reference gates.
- Generated starters receive the same intake workflow.
- Task/progress/checkpoint and wiki log are updated.
- Verification commands are run and evidence is recorded.

## Verification

Command:

```powershell
python -m unittest tests.test_site_generator tests.test_harness tests.test_tasks tests.test_task_cli tests.test_doctor
python -m unittest tests.test_intake
python tools/llm_wiki.py site intake --json
python tools/llm_wiki.py quality --skip-frontend
python tools/llm_wiki.py task validate --strict
```

Expected result:

- exits 0.

## Progress

- Added tests first for intake parsing, readiness, doctor, CLI, and generated starter behavior.
- Implemented `SITE_INTAKE.md`, intake parsing, readiness/doctor wiring, and starter propagation.
- Verification evidence: `python -m unittest tests.test_site_generator tests.test_harness tests.test_tasks tests.test_task_cli tests.test_doctor` exited 0 with 38 tests OK.
- Verification evidence: `python -m unittest tests.test_intake` exited 0 with 5 tests OK.
- Verification evidence: `python tools/llm_wiki.py site intake --json` exited 0 and reported root `SITE_INTAKE.md` as draft with pending intake/reference gates.
- Verification evidence: `python tools/llm_wiki.py quality --skip-frontend` exited 0 with 82 tests OK, wiki rebuild OK, and strict lint OK.
- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0 with no task validation issues.
