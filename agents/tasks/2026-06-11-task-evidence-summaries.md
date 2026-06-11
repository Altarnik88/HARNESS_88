# Task: Task Evidence Summaries

Status: verified
Role owner: Conductor
Created: 2026-06-11

## Objective

Add read-only machine-checkable task, progress, and checkpoint evidence summaries for audit and remediation gates.

## Context Files

- AGENTS.md
- agents/tasks/README.md

## Ownership

Owned files:

- src/llm_wiki/evidence.py
- src/llm_wiki/cli.py
- tests/test_task_evidence.py
- tests/test_task_cli.py
- tests/test_site_generator.py
- agents/tasks/README.md
- src/llm_wiki/templates/site_starter/agents/tasks/README.md
- wiki/log.md
- agents/tasks/2026-06-11-task-evidence-summaries.md
- agents/tasks/progress/2026-06-11-task-evidence-summaries.md
- agents/tasks/checkpoints/2026-06-11-task-evidence-summaries.md

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
python -m unittest tests.test_task_evidence; python -m unittest tests.test_site_generator tests.test_harness tests.test_tasks tests.test_task_cli tests.test_doctor; python tools/llm_wiki.py task evidence --json; python tools/llm_wiki.py quality --skip-frontend; python tools/llm_wiki.py task validate --strict
```

Expected result:

- exits 0.

## Progress

- Wrote failing tests for `llm_wiki.evidence`, `task evidence --json`, missing support files, verified tasks without verification evidence, residual risk detection, and generated-starter task docs.
- Verification evidence: initial RED run failed because `llm_wiki.evidence` did not exist and starter task docs did not mention `task evidence --json`.
- Added read-only task evidence parsing and CLI output without raw evidence lines.
- Updated source and generated-starter task docs to include `task evidence --json`.
- Verification evidence: targeted GREEN run `python -m unittest tests.test_task_evidence` exited 0 with 5 tests OK.
- Verification evidence: targeted GREEN run `python -m unittest tests.test_site_generator` exited 0 with 8 tests OK.
- Verification evidence: `python -m unittest tests.test_task_evidence` exited 0 with 5 tests OK.
- Verification evidence: `python -m unittest tests.test_site_generator tests.test_harness tests.test_tasks tests.test_task_cli tests.test_doctor` exited 0 with 38 tests OK.
- Verification evidence: `python tools/llm_wiki.py task evidence --json` exited 0 with no evidence issues and 5 task bundles reported.
- Verification evidence: `python tools/llm_wiki.py quality --skip-frontend` exited 0 with 93 tests OK, wiki rebuild OK, and strict lint OK.
- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0 with no task validation issues.
