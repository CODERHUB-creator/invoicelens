"""SQLite-backed storage and business rules for invoices."""
import sqlite3
from datetime import date


def compute_status(due_date: str, paid_at: str | None, today: date) -> str:
    """paid beats overdue; overdue means due_date is strictly before today."""
    if paid_at:
        return "paid"
    return "overdue" if date.fromisoformat(due_date) < today else "sent"


class Store:
    def __init__(self, path: str = ":memory:"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS clients(
                id TEXT PRIMARY KEY, name TEXT NOT NULL, api_key TEXT UNIQUE NOT NULL);
            CREATE TABLE IF NOT EXISTS invoices(
                id TEXT PRIMARY KEY,
                client_id TEXT NOT NULL REFERENCES clients(id),
                amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
                currency TEXT NOT NULL,
                due_date TEXT NOT NULL,
                paid_at TEXT);
        """)

    def add_client(self, id: str, name: str, api_key: str) -> None:
        self.db.execute("INSERT INTO clients VALUES (?,?,?)", (id, name, api_key))
        self.db.commit()

    def client_for_key(self, api_key: str | None) -> str | None:
        if not api_key:
            return None
        row = self.db.execute("SELECT id FROM clients WHERE api_key=?", (api_key,)).fetchone()
        return row["id"] if row else None

    def add_invoice(self, id, client_id, amount_cents, currency, due_date) -> None:
        date.fromisoformat(due_date)  # raises ValueError on bad input
        self.db.execute(
            "INSERT INTO invoices(id,client_id,amount_cents,currency,due_date) VALUES (?,?,?,?,?)",
            (id, client_id, amount_cents, currency, due_date))
        self.db.commit()

    def _row(self, row, today: date) -> dict:
        return {
            "id": row["id"], "client_id": row["client_id"],
            "amount_cents": row["amount_cents"], "currency": row["currency"],
            "due_date": row["due_date"], "paid_at": row["paid_at"],
            "status": compute_status(row["due_date"], row["paid_at"], today),
        }

    def get_invoice(self, invoice_id: str, today: date) -> dict | None:
        row = self.db.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone()
        return self._row(row, today) if row else None

    def list_invoices(self, client_id: str, today: date, status: str | None = None) -> list[dict]:
        rows = self.db.execute(
            "SELECT * FROM invoices WHERE client_id=? ORDER BY due_date, id", (client_id,)).fetchall()
        items = [self._row(r, today) for r in rows]
        return [i for i in items if status is None or i["status"] == status]

    def mark_paid(self, invoice_id: str, paid_at: str) -> bool:
        """Idempotent: first payment date wins. Returns False if invoice unknown."""
        date.fromisoformat(paid_at)
        cur = self.db.execute(
            "UPDATE invoices SET paid_at=COALESCE(paid_at, ?) WHERE id=?", (paid_at, invoice_id))
        self.db.commit()
        return cur.rowcount == 1
