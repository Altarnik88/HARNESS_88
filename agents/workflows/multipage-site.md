# Multi-Page Site Workflow

## Goal

Move from an ambiguous multi-page website request to verified implementation while keeping agent ownership clear and the Conductor out of serious production-code changes.

## Phase 1: Product Brief

Lead role: Product Strategist.

Outputs:

- Website goal and audience.
- Primary conversion or success action.
- Page list and user journeys.
- Acceptance criteria.
- New or updated `PRODUCT.md` or equivalent approved wiki decision.

Required skills/plugins/MCP:

- Product Design `get-context` when UI/product context is incomplete.
- LLM Wiki CLI search/events for existing decisions.

## Phase 2: Sitemap and Content Model

Lead role: IA & Content.

Outputs:

- Sitemap and URL slugs.
- Per-page purpose.
- Content blocks and metadata plan.
- Navigation/footer model.

Required skills/plugins/MCP:

- Documents/Data plugins only when source docs/data are provided.
- Context7 only when CMS or framework-specific routing docs are needed.

## Phase 3: UX and Visual Direction

Lead roles: UX/Product Design and Visual Design.

Outputs:

- Responsive flow and interaction notes.
- Visual language, design tokens, imagery direction.
- Component mood and layout rules.
- New or updated `DESIGN.md` or equivalent approved wiki decision.

Required skills/plugins/MCP:

- Product Design `get-context` mandatory for product UI work.
- Product Design `ideate` for variants.
- Figma MCP only with Figma URLs or explicit Figma requests.
- imagegen only for bitmap assets.

## Phase 4: Architecture Split

Lead role: Frontend Architecture.

Outputs:

- Framework/routing structure.
- Shared layout/component boundaries.
- Implementation slices with disjoint ownership.
- Test/build commands.
- Spec files and atomic task files for implementation work.

Required skills/plugins/MCP:

- Serena MCP for symbol-level repo discovery.
- Context7 MCP for current framework docs.

## Phase 5: Implementation

Lead role: Frontend Implementation.

Optional role: Backend/Data when dynamic data, API, auth, CMS, or persistence is required.

Outputs:

- Pages/components/interactions in assigned files.
- API/data integration if required.
- Local verification notes.
- Updated progress and checkpoint files for each assigned task.

Required skills/plugins/MCP:

- Context7 MCP for framework/library APIs.
- Browser plugin after significant UI changes.
- Playwright skill for flow checks.
- Product Design image-to-code only when implementing from a mockup/screenshot.

## Phase 6: QA, Performance, Release

Lead roles: QA & Accessibility, Performance/SEO, DevOps/Release.

Outputs:

- Functional and accessibility findings.
- Performance/SEO issues.
- Build/deploy handoff.
- Task-level acceptance checklist verification.

Required skills/plugins/MCP:

- Browser plugin and Playwright skill for local UI verification.
- Context7 only for framework-specific optimization docs.
- GitHub plugin/gh-cli for CI, PR, and release checks when needed.

## Phase 7: Knowledge Closeout

Lead role: Knowledge Steward.

Outputs:

- `wiki/log.md` entry.
- `wiki/index.md` update if a durable page is created.
- Durable decisions or unresolved follow-ups in wiki pages.
- Archived durable decisions and final task states in the wiki when they should compound.

Required skills/plugins/MCP:

- Local LLM Wiki CLI: rebuild, lint, search, events.
