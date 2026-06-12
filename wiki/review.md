---
title: Review
type: overview
status: draft
confidence: medium
sources: []
tags: []
summary: Human-in-the-loop decisions and unresolved review items.
---

# Review

## [2026-06-11] Known npm audit issue: Next internal postcss

- Found: `npm audit` previously reported a moderate vulnerability path through `next@16.2.9` to its internal `postcss@8.4.31` dependency.
- Prior auto-fix policy: do not apply `npm audit fix` automatically if it requires a breaking Next.js or dependency change.
- Resolution: closed for `v0.1.0` by removing the bundled `frontend/` starter. No npm audit target remains in the core repository; future scaffolded frontends must run their own audit after stack approval.

## [2026-06-12] Release gate: v0.1.0 stack-neutral core

- Status: verified for release preparation.
- Decision: HARNESS_88 ships as stack-neutral core engine/template infrastructure, not as a completed site and not with a preselected frontend.
- Stack selection: agents recommend 2-4 stack options with languages, frameworks, services, pros, cons, operational complexity, and best-fit use cases, then wait for user approval or a custom stack.
- Deployment selection: agents ask about VPS/VDS vs hosting, explain pros and cons of each, and recommend a publication target from the client's budget, traffic, backend/runtime, operations, backup, and maintenance answers.
- Verification: `python -m unittest discover -s tests`, `python tools/llm_wiki.py quality --skip-frontend`, `python tools/llm_wiki.py security audit --json --no-record --blocking`, and `python tools/llm_wiki.py task validate --strict` exited 0 during release preparation.
