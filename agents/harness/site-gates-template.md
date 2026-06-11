# Site Delivery Gates Template

This template becomes the concrete post-intake delivery gate tracker for a generated site project.

Status: draft

Allowed statuses: draft, approved, needs-review

## Required Fields

frontend_preview_approval: pending
backend_data_readiness: pending
total_audit: pending
remediation: pending
final_user_approval: pending
publish_operate_handoff: pending

## Notes

- `frontend_preview_approval`: approved, pending, needs-review, or rejected.
- `backend_data_readiness`: complete, not-required, pending, or needs-review.
- `total_audit`: complete, pending, or needs-review.
- `remediation`: complete, not-required, residual-risk-accepted, pending, or needs-review.
- `final_user_approval`: approved, pending, needs-review, or rejected.
- `publish_operate_handoff`: complete, pending, or needs-review.
- Keep secrets out of this file. Use `agents/workflows/secret-broker.md` for secret-backed backend or deployment setup.
