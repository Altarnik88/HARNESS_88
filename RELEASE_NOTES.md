# HARNESS_88 Release Notes

## v0.1.0 - Draft, blocked

Status: blocked pending frontend security remediation.

HARNESS_88 v0.1.0 is intended to publish the project as a stack-neutral core engine and template infrastructure for building sites from scratch. It is not a completed site, and it does not select a stack, approve a product brief, approve a design brief, or begin frontend/site implementation.

### Intended release contents

- Core HARNESS_88 workflow, task, wiki, gate, and diagnostics tooling.
- Stack-neutral onboarding and approval gates for new site projects.
- Optional bundled Next.js starter/template under `frontend/`.
- Secret handling guidance that records variable names and provider metadata only; no secret values are requested, stored, or committed.

### Required before publishing

- `git status --short` must be clean.
- `python tools/llm_wiki.py quality --skip-frontend` must pass.
- `python tools/llm_wiki.py task validate --strict` must pass.
- `python tools/llm_wiki.py task evidence --json` must report no evidence issues.
- `npm audit --json` in `frontend/` must report zero unresolved vulnerabilities.
- `npm run lint` and `npm run build` in `frontend/` must pass.

### Current blocker

The full-repo release gate is blocked by a moderate npm audit finding in the optional bundled Next.js starter/template:

- `next@16.2.9` includes nested `postcss@8.4.31`.
- The advisory requires `postcss >=8.5.10`.
- `npm audit` reports the path through `next` and suggests a downgrade to `next@9.3.3`, which is not acceptable for this release.
- `npm view next version` and `npm view eslint-config-next version` currently return `16.2.9`, so there is no compatible patch/minor update available in the npm registry at the time of this check.

Do not publish `v0.1.0` as a full-repo clean release until a compatible Next.js update removes the vulnerable nested PostCSS dependency, or until the release scope is changed explicitly.
