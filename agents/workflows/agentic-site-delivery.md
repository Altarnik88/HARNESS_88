# Agentic Site Delivery Workflow

## Goal

Move from an ambiguous website request to a verified, user-approved, publishable site while keeping agent ownership clear and the Conductor out of serious production-code changes.

This workflow applies to landing pages, multi-page sites, catalog sites, and ecommerce projects. HARNESS_88 itself remains a stack-neutral core; concrete site implementation starts only after approved briefs, approved references, and a selected stack or explicitly approved custom stack.

The Conductor coordinates agent-first work. If no suitable role, skill, plugin, MCP server, or tooling grant exists for a needed task, update the role/tooling contract before delegating.

## Phase 1: First-Run Intake

Lead role: Product Strategist.

Conversation rule: ask intake questions, clarifications, and approval prompts in the user's language from the latest user message. This is separate from the `SITE_INTAKE.md` `language` field, which records the site's primary language.

Outputs:

- Website goal, audience, country/market, primary language, and constraints.
- Machine-checkable answers recorded in `SITE_INTAKE.md`.
- Site type: landing page, multi-page site, catalog, ecommerce, web app, or custom.
- Commerce decision:
  - no commerce;
  - catalog only;
  - ecommerce with online payment;
  - ecommerce with offline payment;
  - purchase request/lead form for a manager;
  - mixed mode.
- Primary conversion or success action.
- Required pages, integrations, content sources, and launch constraints.
- Open questions that block product or stack approval.
- Reference status recorded as `references_status` in `SITE_INTAKE.md`.

Required skills/plugins/MCP:

- Product Design `get-context` when UI/product context is incomplete.
- LLM Wiki CLI search/events for existing decisions.

## Phase 2: Brief Contracts

Lead role: Product Strategist, with UX/Product Design and Frontend Architecture review when needed.

Outputs:

- Updated `PRODUCT.md` with product goal, audience, scope, commerce mode, user jobs, and acceptance criteria.
- Updated `DESIGN.md` with design style, interaction direction, accessibility constraints, and visual reference expectations.
- Updated `SITE_INTAKE.md` with `Status: approved` and `references_status: approved` when accepted.
- Updated `STACK.md` with a selected profile or documented custom approach.
- Explicit statuses:
  - `PRODUCT.md`: `Status: approved` before implementation.
  - `DESIGN.md`: `Status: approved` before implementation.
  - `SITE_INTAKE.md`: `Status: approved` and approved references before implementation.
  - `STACK.md`: selected before implementation.
- First concrete task file, progress file, and checkpoint file.

Required skills/plugins/MCP:

- Product Design `get-context` for missing product/UI decisions.
- Context7 only when a stack decision depends on current framework/platform behavior.

## Phase 3: Reference Gate

Lead roles: Reference Research, UX/Product Design, and Visual Design.

Outputs:

- User-provided reference sites, screenshots, brand examples, or competitor examples.
- If the user has no references or cannot choose them, agent-proposed examples based on the intake answers.
- Documented approval or rejection notes for each selected reference.
- Visual direction summary carried into `DESIGN.md` or an approved wiki decision.

Rules:

- Do not start serious frontend implementation before references or reference substitutes are approved.
- When references are missing or undecided, Conductor delegates Reference Research instead of selecting examples alone.
- Agent-proposed reference discovery must include `https://dribbble.com/`, `https://www.behance.net/`, and `https://www.awwwards.com/`.
- Reference shortlists must include URL, reason for inclusion, style tags, project applicability, cautions, and an explicit user approval prompt.
- When examples are agent-proposed, clearly separate direct user preferences from agent suggestions.
- Record unresolved reference disagreements as blockers, not assumptions.

Required skills/plugins/MCP:

- Browser or web search only when current public references are needed.
- Product Design `ideate` for visual variants after the brief is clear.
- Design resources from `agents/protocols/design-resources.md` when reference research feeds UX, visual direction, critique, or motion decisions.
- Figma only when a Figma URL or explicit Figma workflow is requested.

## Phase 4: Sitemap, Content Model, and User Journeys

Lead role: IA & Content.

Outputs:

- Sitemap, URL slugs, navigation, footer model, and page ownership.
- Per-page purpose, content blocks, metadata, forms, and conversion paths.
- Commerce/catalog model when applicable: categories, product attributes, price/payment display, request flow, cart/checkout needs, and manager handoff.

Required skills/plugins/MCP:

- Documents/Data plugins only when source docs/data are provided.
- Context7 only when CMS or framework-specific routing docs are needed.

## Phase 5: Frontend Architecture

Lead role: Frontend Architecture.

Outputs:

- Framework/routing structure.
- Shared layout/component boundaries.
- Implementation slices with disjoint ownership.
- For large multi-page frontend work, a fan-out plan that splits UX, visual system, pages, components, animations, assets, QA, performance/SEO, and wiki closeout into disjoint agent tasks.
- Preview, animation, responsive, and browser-verification plan.
- Test/build commands.
- Spec files and atomic task files for implementation work.

Required skills/plugins/MCP:

- Serena MCP for symbol-level repo discovery.
- Context7 MCP for current framework docs.
- `agents/protocols/design-resources.md` for planning UX, visual, Canva, and GSAP specialist briefs.

## Phase 6: Frontend Build and Approval Loop

Lead role: Frontend Implementation.

Supporting roles: UX/Product Design, Visual Design, QA & Accessibility.

Outputs:

- Pages, components, interactions, animations, banners, and responsive states in assigned files.
- For large sites, many bounded frontend agents may run across page sections, product cards, posters/banners, motion, logo/image polish, responsive states, QA, performance/SEO, and knowledge updates, with disjoint ownership and explicit tools/skills in each brief.
- Browser-visible previews for user review.
- Progress/checkpoint updates for each assigned task.
- Recorded user approval, or recorded feedback items that become follow-up tasks.
- Updated `SITE_GATES.md` with `frontend_preview_approval: approved` only after explicit user approval.

Rules:

- Show meaningful frontend progress to the user before backend work begins unless the selected stack requires a small backend stub.
- If the user has remarks, record them as tasks, fix them, and show the updated result again.
- Do not treat silence as approval.
- The Conductor coordinates the fan-out and reviews outputs; it does not become the sole frontend builder.

Required skills/plugins/MCP:

- Context7 MCP for framework/library APIs.
- Design resources from `agents/protocols/design-resources.md` for UX/visual/motion specialists when their delegation brief grants them.
- Browser plugin after significant UI changes.
- Playwright skill for flow checks.
- Product Design image-to-code only when implementing from a mockup/screenshot.

## Phase 7: Backend/Data Build

Lead role: Backend/Data.

Supporting role: DevOps/Release when environment or deployment choices are involved.

Outputs:

- Backend necessity decision: static-only, forms-only, catalog, ecommerce, auth/admin, CMS, or custom.
- API contracts, data models, auth/session model, and integration plan.
- Payment/request mode implementation according to the intake decision:
  - online payment;
  - offline payment;
  - request to manager;
  - mixed mode.
- Environment variable names without secret values.
- Updated verification evidence.
- Updated `SITE_GATES.md` with `backend_data_readiness: complete` or `not-required`.

Required skills/plugins/MCP:

- Context7 MCP for backend/database/ORM/current platform docs.
- Supabase plugin/MCP only when Supabase is explicitly selected and available.
- SQLite MCP read-only for local DB inspection only.
- Secret handling follows `agents/workflows/secret-broker.md`.

## Phase 8: Catalog or Product Ingest

Lead role: Backend/Data.

Supporting roles: IA & Content, Frontend Implementation.

Outputs:

- Source document request when products are required: spreadsheet, CSV, ERP export, CMS export, or user-provided product document.
- Data mapping for names, descriptions, characteristics, categories, media, prices, availability, SKU, and manager/request fields.
- Import plan and validation report.
- Frontend product/card/category pages synchronized with the accepted data model.

Required skills/plugins/MCP:

- Spreadsheets/Documents plugins only when those source artifacts are provided.
- Data Analytics only for source-backed data profiling or reporting needs.
- Database tools only within selected backend rules and assigned scope.

## Phase 9: Total Agent Audit

Lead roles: QA & Accessibility, Performance/SEO, Backend/Data, DevOps/Release.

Output:

- Findings across:
  - functional bugs;
  - accessibility;
  - responsive behavior;
  - performance;
  - SEO/metadata;
  - security and dependency audit;
  - backend/data correctness;
  - code quality and maintainability;
  - weak architecture or unnecessary complexity.
- Severity, evidence, reproduction steps, affected files, and recommended fix for each issue.
- Explicit unresolved-risk list.
- Updated `SITE_GATES.md` with `total_audit: complete` after audit evidence is recorded.

Required skills/plugins/MCP:

- Browser plugin and Playwright skill for UI and flow checks.
- Repo-specific tests/builds.
- `python tools/llm_wiki.py security audit --json --no-record` for optional frontend security review when applicable.
- Sentry read-only only when production context exists and credentials are configured through environment variables.

## Phase 10: Remediation Plan and Fix Loop

Lead role: Conductor coordinates; worker roles fix assigned areas.

Outputs:

- Remediation plan from audit findings.
- Atomic tasks with ownership, status, verification command, and acceptance criteria.
- Fixed issues and updated verification evidence.
- Re-run audit subset proving the fix.
- Updated `SITE_GATES.md` with `remediation: complete`, `not-required`, or `residual-risk-accepted`.

Rules:

- Do not bury unresolved findings in summaries; record them in task/checkpoint/wiki review state.
- Verified/done task states require command-plus-success evidence.
- Rework continues until the user or task owner explicitly accepts residual risk.

## Phase 11: Final User Approval

Lead role: Conductor.

Supporting roles: Frontend Implementation, QA & Accessibility, UX/Product Design.

Outputs:

- Browser-visible final site preview.
- User feedback captured as concrete tasks or explicit approval.
- Fixed final corrections and re-shown preview until approved.
- Final approval note in the task/checkpoint or wiki.
- Updated `SITE_GATES.md` with `final_user_approval: approved`.

Required skills/plugins/MCP:

- Browser plugin for visible review.
- Playwright for smoke checks when flows matter.
- Product Design plugin only when final visual/interaction feedback needs design support.

## Phase 12: Publish and Operate

Lead role: DevOps/Release.

Outputs:

- Step-by-step VPS publication instructions for the selected stack.
- Required environment variable names and secret-broker invocation path without secret values.
- Build, deploy, rollback, backup, monitoring, and update instructions.
- Maintenance notes for dependency updates and versioned releases.
- Handoff checklist and residual risks.
- Updated `SITE_GATES.md` with `publish_operate_handoff: complete`.

Required skills/plugins/MCP:

- Context7 only for current platform/framework/deploy docs.
- GitHub/gh-cli only when repository/CI/release work is requested.
- Secret handling follows `agents/workflows/secret-broker.md`.

## Phase 13: Knowledge Closeout

Lead role: Knowledge Steward.

Outputs:

- `wiki/log.md` entry.
- `wiki/index.md` update if a durable page is created.
- Durable decisions or unresolved follow-ups in wiki pages.
- Archived durable decisions and final task states in the wiki when they should compound.

Required skills/plugins/MCP:

- Local LLM Wiki CLI: rebuild, lint, search, events.
