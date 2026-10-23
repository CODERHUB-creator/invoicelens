"""Transport-independent request handler. Easy to test without sockets."""
import hashlib
import hmac
import json
import re
from datetime import date

from .store import Store

VALID_STATUSES = {"sent", "paid", "overdue"}


def sign(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def handle(store: Store, method: str, path: str, query: dict, headers: dict,
           body: bytes, today: date, webhook_secret: str):
    """Returns (status_code, json_serialisable_body)."""
    headers = {k.lower(): v for k, v in headers.items()}

    if method == "POST" and path == "/webhooks/payment":
        expected = sign(webhook_secret, body)
        if not hmac.compare_digest(expected, headers.get("x-signature", "")):
            return 401, {"error": "invalid signature"}
        try:
            data = json.loads(body)
            invoice_id, paid_at = data["invoice_id"], data["paid_at"]
            ok = store.mark_paid(invoice_id, paid_at)
        except (ValueError, KeyError, TypeError):
            return 400, {"error": "malformed payload"}
        return (200, {"ok": True}) if ok else (404, {"error": "unknown invoice"})

    client_id = store.client_for_key(headers.get("x-api-key"))
    if client_id is None:
        return 401, {"error": "missing or invalid api key"}

    m = re.fullmatch(r"/clients/([^/]+)/invoices(?:/([^/]+))?", path)
    if method != "GET" or not m:
        return 404, {"error": "not found"}
    if m.group(1) != client_id:
        return 403, {"error": "forbidden"}

    if m.group(2):
        inv = store.get_invoice(m.group(2), today)
        # Other clients' invoices look identical to missing ones: no leaking.
        if not inv or inv["client_id"] != client_id:
            return 404, {"error": "not found"}
        return 200, inv

    status = query.get("status")
    if status is not None and status not in VALID_STATUSES:
        return 400, {"error": f"status must be one of {sorted(VALID_STATUSES)}"}
    return 200, {"invoices": store.list_invoices(client_id, today, status)}
