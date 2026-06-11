# Reusable Skill Capture Protocol

Codex works in this project as a durable engineering agent, not as a one-off chat. When user preferences, workflows, checks, output formats, or repeated operations appear across sessions, the agent should consider whether they belong in a reusable Codex skill.

Do not create or edit global skills silently. First propose the concrete skill change, wait for explicit user approval, then make the change.

## When To Propose A Skill

If a user explains the same preference, process, format, or verification pattern repeatedly, pause and propose turning it into a skill.

When proposing a skill, include:

- working skill name;
- exact `description` that defines when the skill should activate;
- concise `SKILL.md` instructions;
- any deterministic `scripts/`;
- any focused `references/`, `assets/`, templates, or examples.

## Shape Skills Well

- Prefer several narrow composable skills over one large monolithic skill.
- If a skill grows to cover unrelated workflows, propose splitting it.
- Move repeatable mechanical work into scripts whenever possible.
- Keep creative, contextual, and judgment-heavy work in model instructions.

## Session Retrospective

After sessions that reveal a useful repeatable pattern, offer a short retrospective:

- what should become durable skill behavior;
- what was only a one-time project decision;
- which file, script, reference, or template should be updated.

Never store secrets in `AGENTS.md`, `SKILL.md`, skill resources, project files, or Codex config. Use environment variables for tokens and keys.
