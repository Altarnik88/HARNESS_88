# Progress: GitHub Core Engine Release

Linked task: `agents/tasks/2026-06-12-github-core-engine-release.md`
Current status: blocked

## Completed Steps

- Confirmed `core_harness88_improvement_prompt.txt` was untracked and not referenced by repo files.
- Deleted `core_harness88_improvement_prompt.txt` after user approval because it did not affect core HARNESS_88 behavior.
- Ran real `npm audit --json` in `frontend/` with network approval.
- Queried `npm view next version` and `npm view eslint-config-next version` with network approval.
- Added draft release notes for `v0.1.0`.
- Recorded the release blocker in the task bundle and review queue.

## Verification Run

- `git status --short` no longer showed `core_harness88_improvement_prompt.txt` after deletion.
- `npm audit --json` reported 2 moderate unresolved vulnerabilities through `next` and nested `postcss`.
- `npm view next version` returned `16.2.9`.
- `npm view eslint-config-next version` returned `16.2.9`.
- No compatible safe patch/minor update was available from the npm registry during this run.
- `python tools/llm_wiki.py quality --skip-frontend` passed: 147 Python tests OK, wiki rebuild OK, strict lint OK.
- `python tools/llm_wiki.py task validate --strict` passed with no validation issues.
- `python tools/llm_wiki.py task evidence --json` passed with no evidence issues; this release task is intentionally `blocked`.
- `cd frontend; npm run lint` passed.
- `cd frontend; npm run build` passed.

## Residual Risk

- Unresolved moderate npm audit finding remains open for the optional bundled Next.js starter/template.
- The full-repo clean release gate is blocked until a compatible Next.js update removes nested `postcss@8.4.31`, or release scope changes explicitly.

## Next Action

- Monitor for a compatible Next.js release newer than `16.2.9`, then update `next` and `eslint-config-next`, rerun `npm audit --json`, `npm run lint`, and `npm run build`.
- Do not merge to `main`, create tag `v0.1.0`, or publish a GitHub release while `npm audit` reports unresolved findings.

## Files Changed

- Added `RELEASE_NOTES.md`.
- Added this release task bundle.
- Updated `wiki/review.md`.
- Updated `wiki/log.md`.

## Review Evidence

- Stack remains unselected.
- Site intake, site references, product, design, and site gates remain unapproved.
- Frontend/site implementation was not started.
- No secret values were requested, displayed, written, or stored.
