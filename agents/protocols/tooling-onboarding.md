# Tooling Onboarding Protocol

Use this protocol after a fresh download/clone of HARNESS_88 and after meaningful environment changes.

## Audit First

Run:

```powershell
python tools/llm_wiki.py tools audit --json
```

The audit inspects local commands, Codex skills, Codex plugins, and MCP-related capabilities. It does not install, download, connect, or mutate anything.

## Permission Flow

- Read `summary`, `items`, and `next_actions`.
- Ask the user for permission before every install, GitHub download, Codex plugin connection, MCP connection, or frontend dependency addition.
- Ask permission in the user language from the latest user message.
- For GitHub-backed resources, use the URL recorded in `agents/resources/tooling-sources.json`.
- If a GitHub `resource_url` is blank or missing, ask the user to provide or approve the exact repository URL before download.
- For Codex plugin resources, use the recorded plugin URI when available, such as `plugin://canva@openai-curated-remote`, and ask the user to connect the Codex plugin.
- Do not substitute one skill, plugin, MCP server, or repository for another without explicit user approval.

## Design Resources

Design resources are part of the same onboarding flow:

- `huashu-design`
- `impeccable`
- `ui-ux-pro-max`
- GSAP
- Canva

Use `agents/protocols/design-resources.md` for role grants and `agents/resources/tooling-sources.json` for source links.

## Evidence

Record approved install/connect/download decisions in the active task, checkpoint, or wiki log when they affect durable project setup.
