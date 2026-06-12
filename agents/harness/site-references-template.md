# Site References Template

This template becomes the concrete pre-frontend reference analysis gate tracker for a generated site project.

Status: draft

Allowed statuses: draft, approved, needs-review

## Required Fields

reference_analysis_status: pending
crawl_policy: bounded-crawl
page_inventory: pending
screenshot_manifest: raw/assets/references/manifest.json
figma_policy: create-file
figma_reference: pending
ux_visual_analysis: pending
user_reference_approval: pending

## Notes

- `reference_analysis_status`: complete, pending, or needs-review.
- `crawl_policy`: bounded-crawl. Default crawl is same-origin public pages from sitemap, navigation, and footer links, max 50 normalized pages per approved reference.
- `page_inventory`: complete, pending, or needs-review.
- `screenshot_manifest`: must be `raw/assets/references/manifest.json`.
- `figma_policy`: create-file or existing-file. If no Figma file is provided, agents create a new Figma design file after confirming access/team.
- `figma_reference`: Figma design URL for the reference artifact.
- `ux_visual_analysis`: complete, pending, or needs-review.
- `user_reference_approval`: approved, pending, needs-review, or rejected.
- Exclude login, private, admin, account, checkout/cart, destructive, and form-submission flows unless explicitly approved.
- Skipped pages and unresolved blockers must be recorded in the manifest with reasons.
