# Site Intake

Status: draft

Allowed statuses: draft, approved, needs-review

This file records the first-run website intake. It gates concrete site implementation together with `PRODUCT.md`, `DESIGN.md`, `STACK.md`, approved references, and a concrete task file.

Agents may update this file from user answers, but must not treat unknown answers as approval. Keep secrets out of this file.

## Required Fields

goal: unknown
audience: unknown
country: unknown
language: unknown
site_type: unknown
catalog_mode: unknown
payment_request_mode: unknown
design_style: unknown
reference_mode: unknown
references_status: pending
content_sources: unknown
stack_expectations: unknown
deploy_expectations: unknown
backend: unknown
data: unknown
auth: unknown
admin: unknown
integrations: unknown
product_catalog_document: unknown

## Notes

- `site_type`: landing, multipage, catalog, ecommerce, app, or custom.
- `catalog_mode`: none, catalog-only, product-catalog, service-catalog, mixed, or custom.
- `payment_request_mode`: no-commerce, online-payment, offline-payment, request-to-manager, mixed, or custom.
- `reference_mode`: user-provided, agent-suggested, mixed, or none-yet.
- `references_status`: pending, approved, rejected, or needs-review.
- `product_catalog_document`: not-required, needed, provided, or unknown.
- If references are missing, agents propose suitable examples and wait for approval before serious frontend implementation.
