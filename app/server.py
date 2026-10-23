"""Thin HTTP wrapper. Run: WEBHOOK_SECRET=dev python -m app.server"""
import json
import os
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse

from .api import handle
from .store import Store

STORE = Store(os.environ.get("DB_PATH", ":memory:"))
SECRET = os.environ.get("WEBHOOK_SECRET", "dev")


class Handler(BaseHTTPRequestHandler):
    def _run(self):
        url = urlparse(self.path)
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""
        code, payload = handle(STORE, self.command, url.path, dict(parse_qsl(url.query)),
                               dict(self.headers), body, date.today(), SECRET)
        out = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    do_GET = do_POST = _run


def seed():
    STORE.add_client("acme", "Acme Ltd", "key-acme")
    STORE.add_client("globex", "Globex", "key-globex")
    STORE.add_invoice("INV-1", "acme", 150000, "INR", "2026-09-30")
    STORE.add_invoice("INV-2", "acme", 99900, "INR", "2026-12-01")


if __name__ == "__main__":
    seed()
    print("Listening on http://localhost:8000")
    HTTPServer(("", 8000), Handler).serve_forever()
