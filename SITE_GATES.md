# Site Delivery Gates

Status: draft

Allowed statuses: draft, approved, needs-review

This file records machine-checkable delivery approval gates after first-run intake. It gates publish/operate handoff together with approved intake, approved briefs, selected stack state, approved references, tracked tasks, audit evidence, remediation evidence, and final user approval.

Agents may update this file from accepted review evidence, but must not treat silence or missing evidence as approval. Keep secrets out of this file.

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
- Do not publish or provide final deployment instructions until final user approval is recorded and publish/operate handoff is complete.
- Secret values must not be stored here; record only variable names, redacted status, or broker receipts.
