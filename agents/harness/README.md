# Harness Execution Model

This directory defines the lightweight execution harness for agent work. It keeps implementation state in files so a fresh worker can resume from durable context instead of chat history.

HARNESS_88 is a stack-neutral autonomous core. The stack state lives in root `STACK.md`; profile descriptions live in `agents/harness/stack-options.md`, and CLI-readable profile metadata lives in `agents/harness/stack-profiles.json`.

## Operating Model

- Clean-context execution uses project files as the source of truth.
- Each real implementation starts from product, design, stack, spec, task, progress, checkpoint, and acceptance artifacts.
- Production implementation waits until `STACK.md` is selected or the user explicitly confirms a custom approach.
- Production implementation waits until `SITE_INTAKE.md` is `Status: approved` and its `references_status` is `approved`.
- Serious frontend implementation also waits until `SITE_REFERENCES.md` is approved with bounded crawl, desktop/mobile screenshots, UX/visual analysis, and Figma reference evidence.
- `PRODUCT.md` and `DESIGN.md` must use explicit statuses: `draft`, `approved`, or `needs-review`. Only `approved` unlocks implementation.
- The Conductor creates or assigns atomic task files before production implementation.
- Site-delivery worker tasks are created through `python tools/llm_wiki.py conductor delegate ...` so `Phase` and `Delegation packet` are machine-checkable.
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
assigned delegation packet
assigned progress file
assigned checkpoint file
```

## Artifact Roles

- `prd-template.md` captures the product problem, audience, requirements, and acceptance criteria.
- `site-intake-template.md` captures first-run site intake decisions before product/design/stack approval.
- `site-references-template.md` captures the strict pre-frontend reference analysis gate.
- `site-gates-template.md` captures machine-checkable delivery gates from frontend preview approval through publish/operate handoff.
- `spec-template.md` turns an approved product/design brief into implementation decisions.
- `task-template.md` defines one atomic unit of work with owner, scope, tooling, and evidence.
- `stack-options.md` summarizes selectable stack/fullstack profiles. `stack-profiles.json` defines the CLI-readable profile metadata, tradeoffs, selection questions, scaffold policy, and deployment options. Neither file scaffolds those stacks.
- `progress-template.md` records current state for clean handoff.
- `checkpoint-template.md` records preflight, implementation, verification, review, wiki/log updates, and risk.
- `acceptance-checklists.md` provides task-type checklists.
- `metrics.md` defines manual observations that can later become indexed metrics.

## Mechanical Checks

`python tools/llm_wiki.py lint --strict` checks both wiki health and harness structure. Harness lint verifies required root files, task statuses, required task sections, and verification evidence for `verified` or `done` task files.

Use `python tools/llm_wiki.py site doctor` for a unified readiness, stack, brief, task, wiki, optional scaffolded frontend, security, and generated-starter self-test report.

Use `python tools/llm_wiki.py site intake --json` for machine-readable first-run intake and reference approval state.

Use `python tools/llm_wiki.py site references --json` for machine-readable reference analysis readiness.

Use `python tools/llm_wiki.py site gates --json` for machine-readable delivery approval, audit, remediation, final approval, and publish handoff state.

Use `python tools/llm_wiki.py quality --skip-frontend` as the default core completion gate. It runs Python tests, wiki rebuild, and strict lint.

Use `python tools/llm_wiki.py site self-test` when generator changes need proof that a clean starter passes its own core checks.

Use `python tools/llm_wiki.py quality` when an approved scaffolded stack includes frontend lint checks. Use `python tools/llm_wiki.py quality --full` when a full scaffolded frontend build should be part of handoff evidence.

Use `python tools/llm_wiki.py security audit --json --no-record` for non-mutating dependency security review when a scaffolded frontend package manifest exists. Omit `--no-record` to record unresolved audit items in `wiki/review.md`; add `--blocking` only when a task or CI policy explicitly requires unresolved items to fail.

No frontend app is bundled. Stack is selected through dialogue, and deployment planning compares VPS/VDS vs hosting with pros and cons before recommending a publication target.
