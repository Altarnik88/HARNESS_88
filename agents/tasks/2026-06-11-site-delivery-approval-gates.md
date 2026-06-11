# Task: Site Delivery Approval Gates

Status: verified
Role owner: Conductor
Created: 2026-06-11

## Objective

Add core-level, machine-checkable delivery approval and publish handoff gates without creating a concrete site or selecting a stack.

## Context Files

- AGENTS.md
- START_HERE.md
- README.md
- SITE_INTAKE.md
- SITE_GATES.md
- AGENT_SITE_TOOLING.md
- agents/workflows/agentic-site-delivery.md
- agents/harness/README.md
- agents/harness/acceptance-checklists.md

## Ownership

Owned files:

- SITE_GATES.md
- agents/harness/site-gates-template.md
- src/llm_wiki/gates.py
- src/llm_wiki/tasks.py
- src/llm_wiki/cli.py
- src/llm_wiki/doctor.py
- src/llm_wiki/harness.py
- src/llm_wiki/site_generator.py
- src/llm_wiki/templates/site_starter/
- tests/test_gates.py
- tests/test_tasks.py
- tests/test_task_cli.py
- tests/test_doctor.py
- tests/test_site_generator.py
- tests/test_harness.py
- START_HERE.md
- README.md
- AGENT_SITE_TOOLING.md
- agents/workflows/agentic-site-delivery.md
- agents/harness/README.md
- agents/harness/acceptance-checklists.md
- wiki/log.md
- agents/tasks/2026-06-11-site-delivery-approval-gates.md
- agents/tasks/progress/2026-06-11-site-delivery-approval-gates.md
- agents/tasks/checkpoints/2026-06-11-site-delivery-approval-gates.md

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
- `SITE_GATES.md` and the generated-starter template cover delivery approval and publish handoff decisions.
- `site gates` is read-only and supports `--json`.
- `task readiness` and `site doctor` report delivery gates and publish readiness without changing `site_implementation_ready` semantics.
- Generated starters receive the same delivery gates workflow.
- Task/progress/checkpoint and wiki log are updated.
- Verification commands are run and evidence is recorded.

## Verification

Command:

```powershell
python -m unittest tests.test_gates
python -m unittest tests.test_site_generator tests.test_harness tests.test_tasks tests.test_task_cli tests.test_doctor
python tools/llm_wiki.py site gates --json
python tools/llm_wiki.py quality --skip-frontend
python tools/llm_wiki.py task validate --strict
```

Expected result:

- exits 0.

## Progress

- Wrote failing tests for delivery gate parsing, CLI JSON, readiness, doctor output, harness required files, and generated starter propagation.
- Implemented `SITE_GATES.md`, gate parsing, readiness/doctor wiring, and starter propagation.
- Verification evidence: `python -m unittest tests.test_gates` exited 0 with 6 tests OK.
- Verification evidence: `python -m unittest tests.test_site_generator tests.test_harness tests.test_tasks tests.test_task_cli tests.test_doctor` exited 0 with 38 tests OK.
- Verification evidence: `python tools/llm_wiki.py site gates --json` exited 0 and reported root `SITE_GATES.md` as draft with pending delivery/publish gates.
- Verification evidence: `python tools/llm_wiki.py quality --skip-frontend` exited 0 with 88 tests OK, wiki rebuild OK, and strict lint OK.
- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0 with no task validation issues.
