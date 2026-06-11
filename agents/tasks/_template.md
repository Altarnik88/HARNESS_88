# Task: Short Action-Oriented Name

Status: planned
Role owner: Conductor
Created: 2026-06-11

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
