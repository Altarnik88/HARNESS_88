# Design Resources Protocol

Use this protocol when a delegated task involves site visual direction, UI/UX design, hi-fi prototypes, design critique, motion, campaign assets, or design handoff.

## Source Registry

All external design resources must be checked against `agents/resources/tooling-sources.json` before use. Do not install, download, connect, or add a dependency automatically. Ask user approval first.

Required design resources:

- `huashu-design`: `https://github.com/alchaincyf/huashu-design` for HTML-native high-fidelity prototypes, design directions, demos, animation concepts, and design review.
- `impeccable`: `https://github.com/pbakaus/impeccable` for design-language critique, UI audit, polish, responsive/a11y/performance design checks, and stronger visual judgment.
- `ui-ux-pro-max`: `https://github.com/nextlevelbuilder/ui-ux-pro-max-skill` for UI/UX design intelligence, design-system reasoning, multi-platform UX specs, and product-interface structure.
- `GSAP`: `https://github.com/greensock/GSAP/` for approved motion systems and assigned frontend animation implementation.
- `Canva`: `plugin://canva@openai-curated-remote` for editable design assets, mood boards, handoff decks, social/campaign visuals, and presentation outputs.

## Role Rules

- Reference Research may cite these as design-method or inspiration resources, but still needs project-specific references and user approval.
- Product Strategist and IA & Content may use `ui-ux-pro-max` for product/UI structure and acceptance criteria.
- UX/Product Design may use `ui-ux-pro-max` and `huashu-design` for flows, interaction models, variants, and high-fidelity prototype direction.
- Visual Design may use `huashu-design`, `impeccable`, Canva, and Creative Production for visual systems, critique, mood boards, asset direction, and presentation-ready design output.
- Frontend Implementation may use GSAP only after the layout, motion intent, ownership, and verification command are approved.
- QA & Accessibility and Performance/SEO may use `impeccable` and GSAP guidance for visual polish, accessibility, responsive behavior, and motion/performance checks.

## Delegation Contract

Every design delegation brief must name:

- which design resources are granted;
- why each resource is relevant to the task;
- whether the resource is read-only inspiration, a Codex skill/plugin, or a production dependency;
- whether user approval is required before download, plugin connection, or dependency addition;
- fallback behavior when the resource is unavailable.

Default fallback: use existing project context, approved references, Product Design plugin guidance, and local Browser/Playwright checks. Do not silently replace one design resource with another.
