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
- Auto-fix policy: do not apply `npm audit fix` automatically if it requires a breaking Next.js or dependency change.
- Recommendation: monitor Next.js and postcss releases, then upgrade the optional bundled Next.js starter/template when a compatible fix is available.
