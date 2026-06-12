# Task: Short Action-Oriented Name

Task id: YYYY-MM-DD-short-slug
Status: planned
Role owner: Conductor
Phase: core-maintenance
Delegation packet: not-required

Allowed statuses: planned, ready, in_progress, blocked, review, verified, done

## Objective

Describe one atomic outcome.

## Owned Files

- List exact files or directories this task may change.

## Do-Not-Edit Files

- List files, directories, generated state, or external systems outside this task.

## Allowed Tooling

- Use only tooling granted by `agents/tooling-matrix.md` and this task file.
- For site-delivery worker phases, create this task with `python tools/llm_wiki.py conductor delegate ...` so `Phase` and `Delegation packet` are machine-checkable.

## Acceptance Checklist

- Scope is respected.
- Assigned files only are changed.
- Relevant verification is run.
- No secrets are stored.
- Durable decisions are logged when needed.

## Verification Command

```powershell
<command>
```

## Completion Evidence

- Record command output summaries, changed files, review notes, and remaining risks.
