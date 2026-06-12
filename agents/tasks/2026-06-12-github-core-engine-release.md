# Task: GitHub Core Engine Release

Status: blocked
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

Conditional files:

- frontend/package.json
- frontend/package-lock.json

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
- Networked npm checks require explicit approval.
- Dependency remediation is limited to safe compatible frontend dependency updates.
- Do not downgrade Next.js and do not add risky dependency overrides.

## Acceptance Checklist

- Local prompt dumps are removed from the worktree.
- Release notes explain that HARNESS_88 is a core engine/template release, not a completed site.
- Release notes state that no stack is selected and no site approvals are advanced.
- Release notes state that no secrets are included or requested.
- Frontend security audit is clean, or release is explicitly blocked.
- Verification evidence is recorded.

## Verification

Command:

```powershell
python tools/llm_wiki.py quality --skip-frontend
python tools/llm_wiki.py task validate --strict
python tools/llm_wiki.py task evidence --json
cd frontend
npm audit --json
npm run lint
npm run build
```

Expected result:

- Core verification commands exit 0.
- Frontend lint and build exit 0.
- `npm audit --json` reports zero unresolved vulnerabilities before release publication.

## Progress

- Release preparation is blocked because the full-repo frontend security audit is not clean.
- Do not tag or publish `v0.1.0` until the blocker is resolved or release scope changes explicitly.
