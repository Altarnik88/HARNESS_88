# Checkpoint: Core CLI Self Test Doctor Templates CI

Linked task: `agents/tasks/2026-06-11-core-cli-self-test-doctor-templates-ci.md`

## Preflight Checks

- Worktree state checked.
- Owned files and do-not-edit files confirmed.
- Required context reviewed.

## Implementation Evidence

- Source-specific Next/PostCSS audit assertion is skipped in generated starters, while source `wiki/review.md` preserves the audit item.
- Generated starter self-test commands now run core quality on clean output.
- Starter overlay files live under `src/llm_wiki/templates/site_starter/`, with drift tests comparing templates to generated output.
- Stack profile metadata lives in `agents/harness/stack-profiles.json` and is consumed by the stack CLI.
- Readiness uses explicit `draft`, `approved`, and `needs-review` brief statuses and reports blockers, files, next command, and suggested tasks.
- `site doctor` reports readiness, stack, briefs, task graph, wiki health, frontend state, security state, and generated-project self-test.
- Task validation checks linked progress/checkpoint files, open-task owned-file conflicts, and stronger verified/done evidence.
- Core CI is split from optional frontend CI; optional security audit is non-blocking by default.

## Verification Evidence

- Verification evidence: `python -m unittest discover -s tests` exited 0 with 74 tests OK.
- Verification evidence: `python tools/llm_wiki.py quality --skip-frontend` exited 0.
- Verification evidence: `python tools/llm_wiki.py task validate --strict` exited 0 with no task validation issues.
- Verification evidence: `python tools/llm_wiki.py site self-test` exited 0.
- Verification evidence: `python tools/llm_wiki.py site init C:\tmp\harness88-selftest-20260611-impl --self-test` exited 0.
- Verification evidence: `python tools/llm_wiki.py site doctor --json --skip-self-test` exited 0.
- Verification evidence: `python tools/llm_wiki.py security audit --json --no-record` exited 0; escalated network run reported unresolved optional frontend audit items non-blockingly.
- Verification evidence: `npm run lint` in `frontend/` exited 0.
- Verification evidence: `npm run build` in `frontend/` exited 0.

## Review Evidence

- Source review item for known Next/PostCSS audit issue remains in `wiki/review.md`.

## Wiki and Log Updates

- Added durable log entry in `wiki/log.md`.

## Residual Risk

- Optional frontend `npm audit` currently reports unresolved Next/PostCSS findings; default audit remains non-blocking and `wiki/review.md` retains the known review item.
