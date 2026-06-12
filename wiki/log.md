# Operation Log

Append durable project events using:

```markdown
## [YYYY-MM-DD] kind | Summary
- Path: `path/to/file`
```

## [2026-06-11] maintenance | Recorded stack-neutral onboarding and known Next/postcss review item
- Path: `START_HERE.md`
- Path: `STACK.md`
- Path: `wiki/review.md`

## [2026-06-11] maintenance | Added core doctor, self-test, templates, task validation, CI, and security audit workflow
- Path: `src/llm_wiki/`
- Path: `agents/harness/stack-profiles.json`
- Path: `agents/tasks/2026-06-11-core-cli-self-test-doctor-templates-ci.md`
- Path: `.github/workflows/quality.yml`

## [2026-06-11] maintenance | Clarified core readiness versus site implementation readiness
- Path: `src/llm_wiki/tasks.py`
- Path: `src/llm_wiki/cli.py`
- Path: `README.md`
- Path: `AGENTS.md`

## [2026-06-11] maintenance | Recorded agentic site delivery workflow gates
- Path: `agents/workflows/agentic-site-delivery.md`
- Path: `agents/workflows/secret-broker.md`
- Path: `START_HERE.md`
- Path: `README.md`

## [2026-06-11] maintenance | Added machine-checkable site intake and reference gates
- Path: `SITE_INTAKE.md`
- Path: `src/llm_wiki/intake.py`
- Path: `agents/harness/site-intake-template.md`
- Path: `src/llm_wiki/templates/site_starter/SITE_INTAKE.md`

## [2026-06-11] maintenance | Added machine-checkable site delivery gates
- Path: `SITE_GATES.md`
- Path: `src/llm_wiki/gates.py`
- Path: `agents/harness/site-gates-template.md`
- Path: `src/llm_wiki/templates/site_starter/SITE_GATES.md`

## [2026-06-11] maintenance | Added task evidence summaries for audit and remediation gates
- Path: `src/llm_wiki/evidence.py`
- Path: `src/llm_wiki/cli.py`
- Path: `agents/tasks/README.md`

## [2026-06-12] maintenance | Added strict reference analysis gate
- Path: `SITE_REFERENCES.md`
- Path: `src/llm_wiki/references.py`
- Path: `agents/workflows/agentic-site-delivery.md`
- Path: `raw/assets/references/manifest.json`
- Path: `agents/tasks/2026-06-11-task-evidence-summaries.md`

## [2026-06-12] maintenance | Refactored core diagnostics, gate parsing, evidence, tooling, and security audit reporting
- Path: `src/llm_wiki/status_fields.py`
- Path: `src/llm_wiki/evidence.py`
- Path: `src/llm_wiki/capabilities.py`
- Path: `src/llm_wiki/security.py`
- Path: `src/llm_wiki/cli.py`
- Path: `agents/tasks/2026-06-12-core-harness-refactor-diagnostics-evidence-semantics.md`

## [2026-06-12] maintenance | Improved core CLI split, secret planning, tooling readiness, DB read helpers, and deploy handoff templates
- Path: `src/llm_wiki/cli.py`
- Path: `src/llm_wiki/cli_tasks.py`
- Path: `src/llm_wiki/security.py`
- Path: `src/llm_wiki/capabilities.py`
- Path: `src/llm_wiki/db_search.py`
- Path: `agents/harness/deploy-handoff-template.md`
- Path: `agents/tasks/2026-06-12-core-maintainability-security-tooling-db-delivery-adapters.md`

## [2026-06-12] release | Blocked HARNESS_88 v0.1.0 full-repo release prep
- Path: `RELEASE_NOTES.md`
- Path: `agents/tasks/2026-06-12-github-core-engine-release.md`
- Path: `wiki/review.md`

## [2026-06-12] decision | Removed bundled frontend starter and added stack/deployment selection flow
- Path: `frontend/`
- Path: `src/llm_wiki/templates/site_starter/frontend/`
- Path: `agents/harness/stack-profiles.json`
- Path: `START_HERE.md`
- Path: `wiki/review.md`

## [2026-06-12] maintenance | Hardened delegation packet validation and synced tooling docs
- Path: `src/llm_wiki/harness.py`
- Path: `tests/test_conductor_runtime.py`
- Path: `agents/protocols/conductor-runtime.md`
- Path: `agents/protocols/tooling-onboarding.md`
- Path: `README.md`
- Path: `README.ru.md`
- Path: `src/llm_wiki/templates/site_starter/`
