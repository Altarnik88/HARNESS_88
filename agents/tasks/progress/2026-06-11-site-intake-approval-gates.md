# Progress: Site Intake Approval Gates

Linked task: `agents/tasks/2026-06-11-site-intake-approval-gates.md`
Current status: verified

## Completed Steps

- Wrote failing tests for the new intake parser, readiness gates, doctor output, CLI output, harness required files, and generated starter propagation.
- Added `SITE_INTAKE.md` and `agents/harness/site-intake-template.md`.
- Added `src/llm_wiki/intake.py`.
- Wired intake/reference readiness into `task readiness`, `site doctor`, and read-only `site intake`.
- Updated root docs and generated-starter overlays.

## Current Blocker

- None.

## Next Action

- Run final verification and record evidence.

## Files Changed

- SITE_INTAKE.md
- AGENTS.md
- START_HERE.md
- README.md
- AGENT_SITE_TOOLING.md
- agents/workflows/agentic-site-delivery.md
- agents/harness/README.md
- agents/harness/acceptance-checklists.md
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
- wiki/log.md

## Verification Run

- Verification evidence: `python -m unittest tests.test_site_generator tests.test_harness tests.test_tasks tests.test_task_cli tests.test_doctor` exited 0 with 38 tests OK.
- Verification evidence: `python -m unittest tests.test_intake` exited 0 with 5 tests OK.
- Verification evidence: `python tools/llm_wiki.py site intake --json` exited 0 and reported root `SITE_INTAKE.md` as draft with pending intake/reference gates.
- Verification evidence: `python tools/llm_wiki.py quality --skip-frontend` exited 0 with 82 tests OK, wiki rebuild OK, and strict lint OK.
- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0 with no task validation issues.

## Clean-Context Handoff Notes

- This is a core workflow/CLI/templates/tests slice only.
- Root `PRODUCT.md` and `DESIGN.md` remain draft, and `STACK.md` remains unselected.
- The actual secret broker program remains a future task.
