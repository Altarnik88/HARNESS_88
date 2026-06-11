# Harness Metrics

These lightweight metrics start as manual observations in task, progress, and checkpoint files. They may later become SQLite-backed metrics after repeated tasks reveal stable structure.

## Cycle Time

Elapsed time from task status `ready` to `done`.

## Blocked Time

Time spent in `blocked` status, with the blocker reason recorded in the progress file.

## First-Pass Verification Rate

Share of tasks whose required verification passes on the first completed run.

## Rework Count

Number of review or verification loops needed after the first implementation pass.

## QA Escape Count

Number of issues found after a task was marked `verified` or `done`.

## Handoff Quality

Manual rating of whether a fresh worker could resume from the task, progress, checkpoint, spec, and linked context files alone.

## Task Throughput

Number of tasks moved to `done` during a selected period, grouped by role or task type when useful.
