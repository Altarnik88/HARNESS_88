# Task: Agentic Site Delivery Workflow

Status: verified
Role owner: Conductor
Created: 2026-06-11

## Objective

Record the approved HARNESS_88 site-delivery route so generated starters guide agents through first-run intake, commerce/payment/request decisions, reference approval, frontend approval, backend/data work, product ingest, total audit, remediation, final user approval, and VPS handoff without turning the HARNESS_88 root into a concrete site.

## Context Files

- AGENTS.md
- START_HERE.md
- README.md
- AGENT_SITE_TOOLING.md
- agents/TEAM.md
- agents/workflows/multipage-site.md
- agents/tooling-matrix.md

## Ownership

Owned files:

- START_HERE.md
- README.md
- AGENT_SITE_TOOLING.md
- agents/TEAM.md
- agents/roles/product-strategist.md
- agents/roles/backend-data.md
- agents/roles/qa-accessibility.md
- agents/workflows/
- agents/tasks/2026-06-11-agentic-site-delivery-workflow.md
- agents/tasks/progress/2026-06-11-agentic-site-delivery-workflow.md
- agents/tasks/checkpoints/2026-06-11-agentic-site-delivery-workflow.md
- src/llm_wiki/templates/site_starter/
- tests/test_site_generator.py
- wiki/log.md

Do not edit:

- raw/
- data/wiki.sqlite

## Allowed Tooling

- Use only tooling granted by agents/tooling-matrix.md and this task file.
- No new runtime dependencies.
- No secrets may be recorded.

## Acceptance Checklist

- HARNESS_88 root remains a core/starter, not a concrete website.
- First-run intake includes ecommerce/catalog and online/offline/payment/request-to-manager decisions.
- Reference approval is required before serious frontend implementation.
- Frontend preview approval precedes backend expansion when possible.
- Backend/data/catalog work follows the selected stack and approved commerce mode.
- Total audit, remediation, final user approval, and publish handoff are recorded as required workflow gates.
- Secret handling is documented as an opaque broker contract without storing or exposing secrets.
- Generated starters include the workflow and hard rules.
- Verification command is run and evidence is recorded.

## Verification

Command:

```powershell
python -m unittest tests.test_site_generator
python tools/llm_wiki.py task validate --strict
python tools/llm_wiki.py quality --skip-frontend
```

Expected result:

- exits 0.

## Progress

- Added canonical agentic site delivery workflow, secret-broker protocol, onboarding/hard-rule/role updates, starter template updates, and generated-starter regression coverage.
- Verification evidence: `python -m unittest tests.test_site_generator` exited 0 with 8 tests OK.
- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0 with no task validation issues.
- Verification evidence: `python tools/llm_wiki.py quality --skip-frontend` exited 0 with 77 tests OK, wiki rebuild OK, and strict lint OK.
