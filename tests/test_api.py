import json
import unittest
from datetime import date

from app.api import handle, sign
from app.store import Store, compute_status

TODAY = date(2026, 10, 24)
SECRET = "s3cret"


def make_store():
    s = Store()
    s.add_client("acme", "Acme", "key-acme")
    s.add_client("globex", "Globex", "key-globex")
    s.add_invoice("A1", "acme", 1000, "INR", "2026-10-01")   # overdue
    s.add_invoice("A2", "acme", 2000, "INR", "2026-11-01")   # sent
    s.add_invoice("G1", "globex", 3000, "INR", "2026-11-01")
    return s


def call(s, method, path, key=None, query=None, body=b"", sig=None):
    h = {}
    if key:
        h["X-Api-Key"] = key
    if sig is not None:
        h["X-Signature"] = sig
    return handle(s, method, path, query or {}, h, body, TODAY, SECRET)


class StatusRules(unittest.TestCase):
    def test_due_today_is_not_overdue(self):
        self.assertEqual(compute_status("2026-10-24", None, TODAY), "sent")

    def test_past_due_is_overdue(self):
        self.assertEqual(compute_status("2026-10-23", None, TODAY), "overdue")

    def test_paid_beats_overdue(self):
        self.assertEqual(compute_status("2026-01-01", "2026-10-01", TODAY), "paid")


class ClientReads(unittest.TestCase):
    def setUp(self):
        self.s = make_store()

    def test_requires_api_key(self):
        self.assertEqual(call(self.s, "GET", "/clients/acme/invoices")[0], 401)
        self.assertEqual(call(self.s, "GET", "/clients/acme/invoices", key="nope")[0], 401)

    def test_list_own_invoices(self):
        code, body = call(self.s, "GET", "/clients/acme/invoices", key="key-acme")
        self.assertEqual(code, 200)
        self.assertEqual([i["id"] for i in body["invoices"]], ["A1", "A2"])

    def test_filter_by_status(self):
        _, body = call(self.s, "GET", "/clients/acme/invoices", key="key-acme", query={"status": "overdue"})
        self.assertEqual([i["id"] for i in body["invoices"]], ["A1"])

    def test_bad_status_filter(self):
        self.assertEqual(call(self.s, "GET", "/clients/acme/invoices", key="key-acme",
                              query={"status": "banana"})[0], 400)

    def test_cannot_read_other_clients_list(self):
        self.assertEqual(call(self.s, "GET", "/clients/globex/invoices", key="key-acme")[0], 403)

    def test_other_clients_invoice_looks_missing(self):
        self.assertEqual(call(self.s, "GET", "/clients/acme/invoices/G1", key="key-acme")[0], 404)


class PaymentWebhook(unittest.TestCase):
    def setUp(self):
        self.s = make_store()

    def pay(self, invoice_id="A1", paid_at="2026-10-20", secret=SECRET):
        body = json.dumps({"invoice_id": invoice_id, "paid_at": paid_at}).encode()
        return call(self.s, "POST", "/webhooks/payment", body=body, sig=sign(secret, body))

    def test_bad_signature_rejected(self):
        self.assertEqual(self.pay(secret="wrong")[0], 401)

    def test_marks_paid(self):
        self.assertEqual(self.pay()[0], 200)
        _, inv = call(self.s, "GET", "/clients/acme/invoices/A1", key="key-acme")
        self.assertEqual(inv["status"], "paid")

    def test_idempotent_first_date_wins(self):
        self.pay(paid_at="2026-10-20")
        self.pay(paid_at="2026-10-22")
        _, inv = call(self.s, "GET", "/clients/acme/invoices/A1", key="key-acme")
        self.assertEqual(inv["paid_at"], "2026-10-20")

    def test_unknown_invoice(self):
        self.assertEqual(self.pay(invoice_id="NOPE")[0], 404)

    def test_malformed_payload(self):
        body = b"not json"
        self.assertEqual(call(self.s, "POST", "/webhooks/payment", body=body, sig=sign(SECRET, body))[0], 400)

    def test_bad_date(self):
        self.assertEqual(self.pay(paid_at="yesterday")[0], 400)


if __name__ == "__main__":
    unittest.main()
