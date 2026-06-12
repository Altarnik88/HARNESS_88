# Task: No Bundled Frontend Stack Selection

Status: planned
Role owner: Conductor
Created: 2026-06-12

## Objective

Remove bundled frontend starters and make stack/deployment selection dialog-driven before stack-specific scaffolding.

## Context Files

- AGENTS.md
- agents/tasks/README.md

## Ownership

Owned files:

- frontend/
- src/llm_wiki/templates/site_starter/frontend/
- src/llm_wiki/site_generator.py
- src/llm_wiki/stack.py
- src/llm_wiki/cli.py
- agents/harness/stack-profiles.json
- agents/harness/stack-options.md
- README.md
- AGENTS.md
- AGENT_SITE_TOOLING.md
- START_HERE.md
- DESIGN.md
- llms.txt
- agents/conductor.md
- agents/harness/README.md
- agents/harness/deploy-handoff-template.md
- src/llm_wiki/templates/site_starter/
- tests/test_site_generator.py
- tests/test_stack_neutral.py
- tests/test_stack_cli.py
- tests/test_frontend_build_config.py
- tests/test_quality.py
- tests/test_security.py
- RELEASE_NOTES.md
- wiki/review.md
- wiki/log.md
- docs/superpowers/plans/2026-06-12-no-bundled-frontend-stack-selection.md
- docs/superpowers/specs/2026-06-12-no-bundled-frontend-stack-selection-design.md

Do not edit:

- raw/
- data/wiki.sqlite
- PRODUCT.md
- SITE_INTAKE.md
- SITE_REFERENCES.md
- SITE_GATES.md
- STACK.md

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

- No work has started.
