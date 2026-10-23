# Task: pagination for invoice list

Context: read CLAUDE.md and docs/SPEC.md first.

Goal: `GET /clients/{id}/invoices` accepts `limit` (default 50, max 200) and
`offset` (default 0), and returns `{"invoices": [...], "total": N}` where
`total` is the count after the status filter, before paging.

Constraints:
- Change only `app/store.py`, `app/api.py`, tests, and `docs/API.md`.
- Invalid `limit`/`offset` (non-integer, negative, limit > 200) returns 400.

Acceptance: tests for default paging, last partial page, offset past the end
(empty list, correct total), invalid values, and paging combined with `status`.

Before coding, reply with a 5-line plan and any questions.
