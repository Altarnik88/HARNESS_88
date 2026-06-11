# Codex-Native Agents Team

This team is for building websites with Codex on top of the HARNESS_88 autonomous core. It is inspired by `peterfei/ai-agent-team`, but adapted to this project, Codex sub-agents, the local LLM Wiki, and the available plugins/MCP servers.

## Operating Rule

The Conductor does not make serious production-code changes in multi-agent mode. The Conductor plans, delegates, coordinates, reviews, runs verification, and updates durable project knowledge. Production implementation belongs to worker agents with explicit ownership.

The project is stack-neutral until `STACK.md` is selected. The optional bundled Next.js starter/template in `frontend/` is not the default stack.

## Read Order

For every multi-agent website task, the Conductor reads:

1. `AGENTS.md`
2. `START_HERE.md`
3. `STACK.md`
4. `agents/TEAM.md`
5. `agents/tooling-matrix.md`
6. `agents/harness/README.md` when implementation tasks are delegated
7. `agents/conductor.md`
8. `purpose.md`
9. `schema.md`
10. `wiki/index.md`
11. Recent `wiki/log.md` entries

Role agents read `agents/tooling-matrix.md`, their own role file, and the delegation brief they receive.

## Team Map

| Role | File | Main Output | Code Permission |
| --- | --- | --- | --- |
| Conductor | `agents/conductor.md` | Plan, delegation, review, final integration notes | No major production code |
| Product Strategist | `agents/roles/product-strategist.md` | Goals, audience, user journeys, acceptance criteria | No code |
| IA & Content | `agents/roles/ia-content.md` | Sitemap, page model, slugs, metadata/content briefs | No code unless docs-only |
| UX/Product Design | `agents/roles/ux-product-design.md` | Flows, responsive behavior, interaction design | No production code |
| Visual Design | `agents/roles/visual-design.md` | Visual system, tokens, imagery direction | No production code unless asset specs |
| Frontend Architecture | `agents/roles/frontend-architecture.md` | Routing, component boundaries, implementation slices | Architecture docs/config only if delegated |
| Frontend Implementation | `agents/roles/frontend-implementation.md` | Frontend pages/components/interactions | Assigned files only |
| Backend/Data | `agents/roles/backend-data.md` | API/data/schema integration | Assigned backend/data files only |
| QA & Accessibility | `agents/roles/qa-accessibility.md` | Test plan, bug list, verified flows, a11y findings | Test files only if delegated |
| Performance/SEO | `agents/roles/performance-seo.md` | Performance and SEO audit/remediation plan | Assigned metadata/config only if delegated |
| DevOps/Release | `agents/roles/devops-release.md` | Build/deploy checklist, CI/deploy fixes | Assigned infra files only |
| Knowledge Steward | `agents/roles/knowledge-steward.md` | Wiki/log/index updates and decisions | Wiki/docs only |

## Sub-Agent Invocation

Use `multi_agent_v1.spawn_agent` only when the user asks for sub-agents, delegation, or parallel agent work. A delegation prompt must include:

- Role and sub-agent name.
- Objective and success criteria.
- Task file path, progress file path, checkpoint file path, and acceptance checklist source.
- Exact ownership or read-only scope.
- Code-change permission.
- Required plugins, MCP servers, and skills.
- Required local context files.
- Expected output.
- Verification command.

Use `agents/templates/delegation-brief.md` as the default prompt shape.

## One-Agent Fallback

If `multi_agent_v1` is unavailable, the current agent may temporarily take the needed worker role. The agent must state the worker role it is assuming before making changes.

Fallback production-code changes are allowed only when the agent follows the harness protocol:

- Confirm `STACK.md` is selected and `PRODUCT.md`/`DESIGN.md` are `Status: approved`, or record the remaining blocker.
- Create or update the task file for the work.
- Create or update the linked progress and checkpoint files.
- Respect ownership and do-not-edit scopes from the task.
- Run the required quality gates and record verification evidence.
- Return to Conductor-style review after the worker-role work is complete.

## Plugin, MCP, and Skill Policy

- Default deny: agents may use only the skills, plugins, MCP servers, and write scopes listed in `agents/tooling-matrix.md` or explicitly granted in a delegation brief.
- Delegation briefs may narrow access. They may broaden access only when the user request clearly requires it.
- `Serena MCP`: Use for symbol-level code discovery and focused repo navigation.
- `Context7 MCP`: Use only for current library/framework/SDK/CLI/cloud docs.
- `Browser plugin`: Use for local UI opening, visual checks, screenshots, and interactions.
- `Playwright skill`: Use for browser automation, screenshots, flow QA, and canvas/visual checks.
- `Product Design plugin`: Use for product UI work, design briefs, ideation, image-to-code, and design QA.
- `Figma MCP`: Use only when the user provides a Figma URL, asks for Figma, or a design task explicitly needs Figma.
- `GitHub plugin` and `gh-cli skill`: Use for GitHub PR/issues/CI/release work. Keep GitHub read-only unless write operations are requested.
- `Sentry skill/plugin`: Use for read-only production error inspection when `SENTRY_AUTH_TOKEN` is set in the environment.
- `Supabase`: Backend/Data only, conditional on an available MCP/plugin or Context7 documentation; no schema/data mutation unless explicitly delegated.
- `Remotion`: Visual/video agents only for explicit render/export work, not ordinary website UI.
- `Data Analytics plugin`: Use for source-backed dashboards/reports/data visuals, not ordinary website coding.
- `Documents` and `Spreadsheets` plugins: Use only when those artifact types are provided or requested.
- `imagegen skill`: Use for bitmap assets and visual variants, not for repo-native SVG/icon systems.
- Local LLM Wiki CLI: Use `python tools/llm_wiki.py search/events/rebuild/lint` for project memory and health.

## Escalation Rules

- Conductor escalates to Product Strategist when goals, audience, or acceptance criteria are unclear.
- Conductor escalates to UX/Product Design before implementing unclear flows or UI interactions.
- Conductor escalates to Frontend Architecture before splitting large implementation work.
- Conductor escalates to QA & Accessibility after significant frontend implementation.
- Conductor escalates to Performance/SEO before release or when pages include marketing/discovery goals.
- Conductor escalates to DevOps/Release when build/deploy/CI/environment behavior matters.
- Conductor escalates to Knowledge Steward after durable decisions or completed website milestones.
- Conductor escalates to Backend/Data when intake selects ecommerce, catalog, online/offline payment, manager-request flow, auth, database, CMS, or integrations.
- Conductor must run the total audit and remediation loop in `agents/workflows/agentic-site-delivery.md` before final publish handoff.

## Required Verification

For website work, final verification should include the relevant subset of:

- Repo-specific tests/builds.
- `python tools/llm_wiki.py stack status`
- `python tools/llm_wiki.py rebuild`
- `python tools/llm_wiki.py lint`
- Browser/Playwright local UI check after frontend changes.
- QA/accessibility review for new or changed user flows.
- Performance/SEO audit before release.
- Security/dependency audit when frontend/backend dependencies are present.
- Final user approval after remediation and before VPS publication instructions.

## References

- `agents/workflows/agentic-site-delivery.md`
- `agents/workflows/multipage-site.md`
- `agents/workflows/secret-broker.md`
- `agents/templates/delegation-brief.md`
- `https://github.com/peterfei/ai-agent-team`
