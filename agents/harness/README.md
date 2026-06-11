# Harness Execution Model

This directory defines the lightweight execution harness for agent work. It keeps implementation state in files so a fresh worker can resume from durable context instead of chat history.

HARNESS_88 is a stack-neutral autonomous core. The stack state lives in root `STACK.md`; profile descriptions live in `agents/harness/stack-options.md`.

## Operating Model

- Clean-context execution uses project files as the source of truth.
- Each real implementation starts from product, design, stack, spec, task, progress, checkpoint, and acceptance artifacts.
- Production implementation waits until `STACK.md` is selected or the user explicitly confirms a custom approach.
- The Conductor creates or assigns atomic task files before production implementation.
- Workers update progress and checkpoint files as work moves through preflight, implementation, verification, and review.
- The Knowledge Steward records durable decisions, outcomes, and unresolved issues in the LLM Wiki.
- Default-deny tooling from `agents/tooling-matrix.md` still applies to every role and task.

## Fresh Worker Read Order

```text
AGENTS.md
agents/TEAM.md
agents/tooling-matrix.md
role file
PRODUCT.md and DESIGN.md or equivalent wiki decisions
STACK.md
assigned spec file
assigned task file
assigned progress file
assigned checkpoint file
```

## Artifact Roles

- `prd-template.md` captures the product problem, audience, requirements, and acceptance criteria.
- `spec-template.md` turns an approved product/design brief into implementation decisions.
- `task-template.md` defines one atomic unit of work with owner, scope, tooling, and evidence.
- `stack-options.md` defines the selectable stack/fullstack profiles. It does not scaffold those stacks.
- `progress-template.md` records current state for clean handoff.
- `checkpoint-template.md` records preflight, implementation, verification, review, wiki/log updates, and risk.
- `acceptance-checklists.md` provides task-type checklists.
- `metrics.md` defines manual observations that can later become indexed metrics.

## Mechanical Checks

`python tools/llm_wiki.py lint --strict` checks both wiki health and harness structure. Harness lint verifies required root files, task statuses, required task sections, and verification evidence for `verified` or `done` task files.

Use `python tools/llm_wiki.py quality --skip-frontend` as the default core completion gate. It runs Python tests, wiki rebuild, and strict lint.

Use `python tools/llm_wiki.py quality` when optional frontend lint should be included. Use `python tools/llm_wiki.py quality --full` when a full optional frontend build should be part of handoff evidence. If frontend dependencies are missing, install them with `cd frontend && npm ci`.
