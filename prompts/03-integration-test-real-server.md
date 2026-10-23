# Task: end-to-end test against the running HTTP server

Start `app.server` on an ephemeral port inside the test, seed data, then using
only `urllib` verify: list invoices, receive a signed webhook, list again and
see `paid`. Make sure the server shuts down cleanly even if the test fails.
Requires a small refactor so the server can be started with a custom Store and
port; keep `python -m app.server` working unchanged.
