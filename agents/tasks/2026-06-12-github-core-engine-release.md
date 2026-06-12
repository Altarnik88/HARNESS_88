# Task: GitHub Core Engine Release

Status: verified
Role owner: Conductor
Created: 2026-06-12

## Objective

Prepare HARNESS_88 v0.1.0 as a GitHub release for the stack-neutral site-development core engine, without selecting a stack or starting site implementation.

## Context Files

- AGENTS.md
- RELEASE_NOTES.md
- wiki/review.md
- agents/tasks/README.md

## Ownership

Owned files:

- RELEASE_NOTES.md
- agents/tasks/2026-06-12-github-core-engine-release.md
- agents/tasks/progress/2026-06-12-github-core-engine-release.md
- agents/tasks/checkpoints/2026-06-12-github-core-engine-release.md
- wiki/review.md
- wiki/log.md

Do not edit:

- STACK.md
- PRODUCT.md
- DESIGN.md
- SITE_INTAKE.md
- SITE_REFERENCES.md
- SITE_GATES.md
- raw/
- data/wiki.sqlite

## Allowed Tooling

- Use only tooling granted by agents/tooling-matrix.md and this task file.
- No networked npm checks are required for the core release because no frontend package manifest remains in the repository.
- Future scaffolded frontend/backend projects must run their own dependency audits after stack approval.

## Acceptance Checklist

- Local prompt dumps are removed from the worktree.
- Release notes explain that HARNESS_88 is a core engine/template release, not a completed site.
- Release notes state that no stack is selected and no site approvals are advanced.
- Release notes state that no secrets are included or requested.
- Core security audit skips cleanly because no frontend package manifest exists.
- Verification evidence is recorded.

## Verification

Command:

```powershell
python tools/llm_wiki.py quality --skip-frontend
python tools/llm_wiki.py security audit --json --no-record --blocking
python tools/llm_wiki.py task validate --strict
python tools/llm_wiki.py task evidence --json
```

Expected result:

- Core verification commands exit 0.
- Security audit exits 0 with `status: "skipped"` and `unresolved_count: 0` while no frontend package manifest exists.

## Progress

- Release preparation is verified after removing the bundled frontend starter and confirming no core npm audit target remains.
- Do not tag or publish `v0.1.0` until the verified branch is merged to `main` and release publication checks are rerun.
