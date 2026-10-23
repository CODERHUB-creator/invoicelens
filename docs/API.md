# API reference

Auth: clients send `X-Api-Key`. The webhook sends `X-Signature` =
hex HMAC-SHA256 of the raw body using `WEBHOOK_SECRET`.

| Method | Path | Success | Errors |
|---|---|---|---|
| GET | `/clients/{id}/invoices?status=` | 200 `{"invoices":[...]}` | 400, 401, 403 |
| GET | `/clients/{id}/invoices/{inv}` | 200 invoice | 401, 403, 404 |
| POST | `/webhooks/payment` | 200 `{"ok":true}` | 400, 401, 404 |

Invoice shape:
```json
{"id":"INV-1","client_id":"acme","amount_cents":150000,"currency":"INR",
 "due_date":"2026-09-30","paid_at":null,"status":"overdue"}
```

Try it:
```bash
WEBHOOK_SECRET=dev python -m app.server
curl -H "X-Api-Key: key-acme" "localhost:8000/clients/acme/invoices?status=overdue"
```
