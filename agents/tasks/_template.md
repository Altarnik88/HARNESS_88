# Task: Short Action-Oriented Name

Status: planned
Role owner: Conductor
Created: YYYY-MM-DD
Phase: core-maintenance
Delegation packet: not-required

## Objective

Describe one atomic outcome.

## Context Files

- AGENTS.md
- agents/TEAM.md
- agents/tooling-matrix.md

## Ownership

- Owned files: none assigned yet
- Do not edit: raw/, data/wiki.sqlite

## Allowed Tooling

- Use only tooling granted by agents/tooling-matrix.md and this task file.
- For site-delivery worker phases, create this task with `python tools/llm_wiki.py conductor delegate ...` so `Phase` and `Delegation packet` are machine-checkable.

## Acceptance Checklist

- Scope is respected.
- Verification command is run.
- Completion evidence is recorded.

## Verification

Command:

```powershell
python tools/llm_wiki.py task validate --strict
```

Expected result:

```text
No task validation issues found.
```

## Progress

- No work has started.
