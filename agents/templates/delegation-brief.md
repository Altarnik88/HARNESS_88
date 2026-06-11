# Delegation Brief Template

Use this shape when calling `multi_agent_v1.spawn_agent`.

```text
Role: <Role Agent>
Sub-agent: <Specific sub-agent>

Task file:
<Path to the assigned task file.>

Progress file:
<Path to the assigned progress file.>

Checkpoint file:
<Path to the assigned checkpoint file.>

Acceptance checklist:
<Checklist source, usually agents/harness/acceptance-checklists.md plus task-specific criteria.>

Objective:
<One clear task.>

Context to read:
- AGENTS.md
- agents/TEAM.md
- agents/tooling-matrix.md
- agents/roles/<role>.md
- <task-specific files>

Ownership / scope:
- Owned files: <exact files/directories, or "none; read-only">
- Do not edit: <files/directories>
- You are not alone in the codebase. Do not revert or overwrite changes made by others.

Required plugins/MCP/skills:
- <plugin/MCP/skill and when to use it, selected from agents/tooling-matrix.md>
- Default deny: all unlisted skills, plugins, MCP servers, and write scopes are forbidden.
- Conditional tools require the trigger named in the matrix and must be reported if unavailable.

Code permission:
- <none | docs-only | assigned files only | tests-only>

Expected output:
- <artifact, patch, report, or decision list>

Verification:
- <exact command or inspection>

Clean-context resume instructions:
- Read the task, progress, checkpoint, linked spec, and linked product/design decisions before continuing.
- Update progress and checkpoint files before reporting completion.
```

## Defaults

- If the task involves current framework/library behavior, include Context7 MCP.
- If the task involves design or UI direction, include Product Design skill guidance.
- If the task changes frontend UI, require Browser or Playwright verification.
- If the task touches GitHub, require GitHub plugin or `gh-cli` skill.
- If the task needs Supabase, Remotion, Sentry, Figma, Canva, or Creative Production, include the matrix trigger and whether writes are allowed.
- If the task creates durable project decisions, ask Knowledge Steward to update the wiki/log.
