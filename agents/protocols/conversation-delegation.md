# Conversation and Delegation Protocol

Use this protocol for user-facing questions, reference discovery, and Conductor delegation.

## User Language

- Ask questions, clarifications, and user decisions in the user language inferred from the latest user message.
- Do not confuse conversation language with `SITE_INTAKE.md` `language`; the intake field records the site's primary language, not necessarily the chat language.
- Keep commands, file paths, API names, package names, quoted source text, and technical terms in their original language when translation would reduce precision.
- If the user's language is unclear, use the language of the current conversation and keep the question short.

## Agent-First Delegation

- The Conductor works agent-first: it coordinates substantial research, product/design decisions, frontend implementation, backend/data work, QA, performance/SEO, release, and wiki closeout through role agents.
- Micro-actions may stay local, including reading a short file, running a verification command, or editing a small protocol note.
- If a suitable role, tool grant, skill, plugin, or MCP server is missing, the Conductor first adds or updates the role/tooling contract, then delegates the work.
- Delegation briefs must name the user language, owned scope, denied scope, allowed tools/skills/plugins/MCP servers, why each is granted, and the fallback if a required resource is unavailable.
- When `multi_agent_v1` is unavailable, use the one-agent fallback from `agents/TEAM.md` and `agents/conductor.md` before production-code changes.

## Reference Discovery

- If the user has no references, cannot choose references, or asks the agent to propose them, the Conductor delegates reference discovery to Reference Research with UX/Product Design and Visual Design support as needed.
- Agent-proposed reference discovery must include these sources:
  - `https://dribbble.com/`
  - `https://www.behance.net/`
  - `https://www.awwwards.com/`
- Add relevant competitor, market, or domain examples when useful, but do not replace the required sources above.
- Return a short shortlist with URL, reason for inclusion, style tags, applicability to the project, and any visual or implementation cautions.
- Separate user-provided preferences from agent suggestions, then wait for explicit user approval before setting `references_status: approved` or starting serious frontend implementation.
