# Agent Resource Sources

`tooling-sources.json` is the project registry for external tool, skill, and MCP sources.

Rules:

- Do not install, download, or connect anything automatically.
- If a resource is taken from GitHub, record the exact repository URL in `tooling-sources.json` before download.
- If the URL is blank, ask the user to provide or approve the exact GitHub link first.
- Keep Codex plugin connections separate from GitHub downloads; plugin access still requires user approval.
- Record any approved install/connect decision in the project wiki or task evidence.

Design resource grants for `huashu-design`, `impeccable`, `ui-ux-pro-max`, GSAP, and Canva are defined in `agents/protocols/design-resources.md`.
