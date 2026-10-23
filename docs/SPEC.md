# InvoiceLens: Spec

## Business need
Clients email our finance team to ask "has this been paid?". Let clients check
invoice status themselves, and update status automatically when a payment lands.

## Users
- **Client**: reads only their own invoices.
- **Payment provider** (system): notifies us when an invoice is paid.

## In scope
1. `GET /clients/{client_id}/invoices[?status=sent|paid|overdue]`
2. `GET /clients/{client_id}/invoices/{invoice_id}`
3. `POST /webhooks/payment` (HMAC-signed) marks an invoice paid.

## Out of scope (v1)
Creating invoices over the API, PDFs, email notifications, partial payments, UI.

## Rules
- Status is **derived**, never stored: `paid` if `paid_at` is set, else `overdue`
  if `due_date` < today, else `sent`. Due *today* is not overdue.
- Money is integer minor units (`amount_cents`) plus a currency code.
- Webhook is idempotent: repeats succeed, and the first `paid_at` wins.
- A client requesting another client's list gets `403`; requesting another
  client's single invoice gets `404` (no existence leak).

## Acceptance criteria
- [ ] No API key or an unknown key returns 401.
- [ ] Client A can never see client B's data.
- [ ] Invalid `status` filter returns 400 with allowed values.
- [ ] Webhook with a bad signature returns 401 and changes nothing.
- [ ] Malformed webhook body or date returns 400.
- [ ] Unknown invoice in webhook returns 404.
- [ ] All of the above covered by automated tests; `python -m unittest` passes.

## Open questions (for the real client)
- Should `draft` invoices exist and be hidden from clients?
- Do we need pagination? (Assume no until a client has 500+ invoices.)
