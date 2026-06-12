# Deploy Handoff Template

Status: inactive until stack/profile approval

Use this template only after the selected profile is recorded in `STACK.md`, product/design/intake/reference gates are approved, implementation and audit evidence are complete, and final publish approval is recorded in `SITE_GATES.md`.

This file does not select a stack, install dependencies, configure credentials, or run deployment commands. Replace placeholders during a later DevOps/Release task.

## Common Handoff Fields

- Project: `<project-name>`
- Approved stack profile: `<profile>`
- Build artifact location: `<path-or-provider-output>`
- Deployment target: `<provider-or-vps>`
- Environment variable names: `<NAMES_ONLY>`
- Secret broker receipt: `<security secret-plan receipt or broker status>`
- Backup plan: `<backup-plan>`
- Rollback plan: `<rollback-plan>`
- Monitoring/checks: `<health-checks>`
- Residual risks: `<accepted-or-open-risks>`

## Profile: next-static

- Intended use: static or frontend-first Next.js site after approval.
- Build command placeholder: `cd frontend && npm run build`
- Publish placeholder: `<static-host-or-node-compatible-target>`
- Secret handling: use `security secret-plan` only when deployment provider variables are required.
- Operate handoff: document preview URL, production URL, cache behavior, rollback artifact, and frontend build verification.

## Profile: next-fullstack

- Intended use: Next.js with approved backend/data decisions.
- Build command placeholder: `cd frontend && npm run build`
- Publish placeholder: `<fullstack-host-or-vps-runtime>`
- Secret handling: record required environment variable names only; use `security secret-plan` for dry-run evidence before any broker action.
- Operate handoff: document runtime, database/auth/payment providers, migrations policy, backups, rollback, and health checks.

## Profile: astro-content

- Intended use: content-heavy static site after Astro scaffold approval.
- Build command placeholder: `npm run build`
- Publish placeholder: `<static-host-or-vps-static-root>`
- Secret handling: normally none unless an approved integration requires named variables.
- Operate handoff: document content update process, generated output path, redirects, cache policy, and rollback artifact.

## Profile: sveltekit

- Intended use: SvelteKit app after adapter/runtime approval.
- Build command placeholder: `npm run build`
- Publish placeholder: `<adapter-specific-runtime>`
- Secret handling: record adapter/provider variable names only; use `security secret-plan` before broker-backed configuration.
- Operate handoff: document adapter, runtime, server/static mode, health checks, backups, rollback, and dependency update policy.

## Profile: custom

- Intended use: user-approved custom stack.
- Build command placeholder: `<approved-build-command>`
- Publish placeholder: `<approved-deployment-target>`
- Secret handling: record variable names and provider metadata only; use `security secret-plan` before any secret-backed action.
- Operate handoff: document the selected runtime, install/build/test commands, backup, rollback, monitoring, and maintenance owner.

## Final Approval Reminder

Do not mark publish/operate handoff complete until final user approval and deployment evidence are recorded in task/checkpoint state and `SITE_GATES.md`.
