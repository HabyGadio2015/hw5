"""Campus Customs MCP server.

The single source of shop facts for every agent, over the working database
copy (data/campus_customs_new.db). Agents must go through these tools —
never a second, parallel way of touching the database. Every tool queries
the database directly and returns exactly what's stored or computed from
what's stored — never invented values. If something isn't in the database,
the tool says so.

Read tools open a read-only connection. The three write tools
(record_payment, update_ticket_status, save_draft) are the only ones
allowed to change the working copy, and each enforces the shop's hard
rules itself (not just via agent prompts): record_payment refuses without
explicit human approval, refuses if it would take the balance negative,
and refuses a duplicate payment for the same (kind, ref_id).

Run from this folder (stdio):  python mcp_server/server.py
Run (HTTP):                    python mcp_server/server.py --http
HTTP URL:                      http://127.0.0.1:8001/mcp
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DB_PATH = ROOT / "data" / "campus_customs_new.db"

mcp = FastMCP("campus-customs")


def _connect() -> sqlite3.Connection:
    """Open a read-only connection to the working database copy."""
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _connect_rw() -> sqlite3.Connection:
    """Open a read-write connection to the working database copy (write tools only)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _shop_today() -> str:
    """The shop's own "today" (desk.date_today) — used to timestamp writes
    so the database stays internally consistent, instead of the real
    wall-clock date."""
    with _connect() as conn:
        row = conn.execute("SELECT date_today FROM desk LIMIT 1").fetchone()
    return row["date_today"] if row else ""


# ---------------------------------------------------------------------------
# Read tools
# ---------------------------------------------------------------------------


@mcp.tool
def get_ticket(ticket_id: int) -> dict[str, Any]:
    """Fetch one ticket from the board by id, with every stored field.

    Returns {"found": False, "ticket_id": ...} if no ticket with that id
    exists — never guess at a ticket's contents.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
        ).fetchone()
    if row is None:
        return {"found": False, "ticket_id": ticket_id}
    return {"found": True, **dict(row)}


@mcp.tool
def list_open_tickets() -> list[dict[str, Any]]:
    """List every ticket on the board with status = 'open', every field, lowest id first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM tickets WHERE status = 'open' ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]


@mcp.tool
def check_inventory(sku: str, size: str) -> dict[str, Any]:
    """Look up on-hand stock for a SKU + size from the inventory table.

    SKU and size are matched case-insensitively against stored values.
    Returns {"found": False, "sku": ..., "size": ...} if that exact
    SKU/size combination isn't in inventory — do not assume a quantity.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM inventory WHERE sku = ? COLLATE NOCASE "
            "AND size = ? COLLATE NOCASE",
            (sku, size),
        ).fetchone()
    if row is None:
        return {"found": False, "sku": sku, "size": size}
    return {"found": True, **dict(row)}


@mcp.tool
def get_pricing(sku: str) -> dict[str, Any]:
    """Look up unit cost and list price for a SKU, for margin/no-loss checks.

    Returns {"found": False, "sku": ...} if the SKU isn't in pricing.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM pricing WHERE sku = ? COLLATE NOCASE", (sku,)
        ).fetchone()
    if row is None:
        return {"found": False, "sku": sku}
    return {"found": True, **dict(row)}


@mcp.tool
def list_vendors() -> list[dict[str, Any]]:
    """List every vendor (id, name, specialty, lead_days). Only 3 vendors
    exist — match a shortfall to one by specialty yourself."""
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM vendors ORDER BY id").fetchall()
    return [dict(r) for r in rows]


@mcp.tool
def check_vendor_invoice_status(vendor_id: int) -> dict[str, Any]:
    """Check whether a vendor has any open (unpaid) invoice.

    A vendor with an open invoice will not ship new stock — use
    `can_ship` before promising a restock. Returns {"found": False,
    "vendor_id": ...} if no such vendor exists.
    """
    with _connect() as conn:
        vendor = conn.execute(
            "SELECT * FROM vendors WHERE id = ?", (vendor_id,)
        ).fetchone()
        if vendor is None:
            return {"found": False, "vendor_id": vendor_id}
        invoices = conn.execute(
            "SELECT * FROM invoices WHERE vendor_id = ? ORDER BY id", (vendor_id,)
        ).fetchall()
    open_invoices = [dict(r) for r in invoices if r["status"] == "open"]
    return {
        "found": True,
        "vendor": dict(vendor),
        "has_open_invoice": bool(open_invoices),
        "can_ship": not open_invoices,
        "open_invoices": open_invoices,
    }


@mcp.tool
def get_invoice(invoice_id: int) -> dict[str, Any]:
    """Fetch one invoice by id (vendor_id, amount, due_date, status, description).

    Returns {"found": False, "invoice_id": ...} if no such invoice exists.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
        ).fetchone()
    if row is None:
        return {"found": False, "invoice_id": invoice_id}
    return {"found": True, **dict(row)}


@mcp.tool
def get_lease(lease_id: int) -> dict[str, Any]:
    """Fetch one lease by id (space_name, landlord, monthly_rent, next_due, notes).

    Returns {"found": False, "lease_id": ...} if no such lease exists.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM leases WHERE id = ?", (lease_id,)
        ).fetchone()
    if row is None:
        return {"found": False, "lease_id": lease_id}
    return {"found": True, **dict(row)}


@mcp.tool
def get_cash_balance(account: str = "checking") -> dict[str, Any]:
    """Look up a cash account's current balance (default account: "checking").

    Returns {"found": False, "account": ...} if no such account exists.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM cash_accounts WHERE name = ? COLLATE NOCASE", (account,)
        ).fetchone()
    if row is None:
        return {"found": False, "account": account}
    return {"found": True, **dict(row)}


@mcp.tool
def check_payment_history(kind: str, ref_id: int) -> dict[str, Any]:
    """Check whether a payment already exists for this (kind, ref_id) —
    e.g. has this invoice, or this lease's rent, already been paid?

    Returns {"already_paid": False, "kind": ..., "ref_id": ...} if no
    matching row exists in `payments` yet, or {"already_paid": True,
    "payment": {...}} with the real payment record if one does. Check
    this before proposing a payment, to avoid a duplicate (Shop Rule 2) —
    don't assume something is unpaid just because a ticket doesn't say so.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM payments WHERE kind = ? AND ref_id = ? ORDER BY id DESC LIMIT 1",
            (kind, ref_id),
        ).fetchone()
    if row is None:
        return {"already_paid": False, "kind": kind, "ref_id": ref_id}
    return {"already_paid": True, "payment": dict(row)}


@mcp.tool
def get_shop_today() -> dict[str, Any]:
    """Return the shop's current date (desk.date_today) and desk notes.

    This is the only valid source of "today" for the shop — use it (not
    the real calendar) to judge whether a lease or invoice is overdue.
    """
    with _connect() as conn:
        row = conn.execute("SELECT * FROM desk LIMIT 1").fetchone()
    if row is None:
        return {"found": False}
    return {"found": True, **dict(row)}


# ---------------------------------------------------------------------------
# Write tools
# ---------------------------------------------------------------------------


@mcp.tool
def record_payment(kind: str, ref_id: int, amount: float, account: str, approved_by: str) -> dict[str, Any]:
    """Record a payment — the ONLY way money leaves the shop. Enforces the
    shop's hard rules itself, and refuses rather than bending them:

    - `approved_by` must be a real human's name — refuses if blank (Shop
      Rule 4: a human must approve before anything is paid).
    - Refuses if `account` doesn't have enough balance to cover `amount`
      (no negative balances, ever).
    - Refuses if a payment already exists for this exact (kind, ref_id) —
      no double payment (Shop Rule 2).

    On success: inserts into `payments`, debits `cash_accounts.balance`,
    and — if kind == "invoice" — marks that invoice's status "paid". (The
    `leases` table has no payment-status field, so a "rent" payment is
    recorded in `payments` but doesn't change the `leases` row.)
    """
    if not approved_by or not approved_by.strip():
        return {"success": False, "reason": "refused: no human approval (approved_by is empty)"}

    with _connect_rw() as conn:
        existing = conn.execute(
            "SELECT * FROM payments WHERE kind = ? AND ref_id = ?", (kind, ref_id)
        ).fetchone()
        if existing is not None:
            return {
                "success": False,
                "reason": "refused: already paid — a payment for this kind/ref_id already exists",
                "existing_payment": dict(existing),
            }

        cash_row = conn.execute(
            "SELECT * FROM cash_accounts WHERE name = ? COLLATE NOCASE", (account,)
        ).fetchone()
        if cash_row is None:
            return {"success": False, "reason": f"refused: no cash account named {account!r}"}
        if amount > cash_row["balance"]:
            return {
                "success": False,
                "reason": "refused: insufficient funds — this would take the balance negative",
                "balance": cash_row["balance"],
                "amount": amount,
            }

        today = _shop_today()
        cursor = conn.execute(
            "INSERT INTO payments (kind, ref_id, amount, account, paid_at, approved_by) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (kind, ref_id, amount, account, today, approved_by),
        )
        new_balance = cash_row["balance"] - amount
        conn.execute(
            "UPDATE cash_accounts SET balance = ?, date = ? WHERE name = ?",
            (new_balance, today, cash_row["name"]),
        )
        if kind == "invoice":
            conn.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (ref_id,))
        conn.commit()
        payment_id = cursor.lastrowid

    return {
        "success": True,
        "payment_id": payment_id,
        "paid_at": today,
        "new_balance": new_balance,
    }


@mcp.tool
def update_ticket_status(ticket_id: int, status: str, notes: str | None = None) -> dict[str, Any]:
    """Update a ticket's status (and optionally replace its notes).

    Only writes a status the agent genuinely means — e.g. never pass
    "resolved" for a ticket that's only partially handled (Shop Rule 7);
    use something like "open" or "partial" and record the
    partial_fulfillment_note in `notes` instead.

    Returns {"found": False, "ticket_id": ...} if no such ticket exists.
    """
    with _connect_rw() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if row is None:
            return {"found": False, "ticket_id": ticket_id}
        new_notes = notes if notes is not None else row["notes"]
        conn.execute(
            "UPDATE tickets SET status = ?, notes = ? WHERE id = ?",
            (status, new_notes, ticket_id),
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    return {"found": True, **dict(updated)}


@mcp.tool
def save_draft(ticket_id: int, draft_text: str) -> dict[str, Any]:
    """Save a customer/vendor-facing draft onto a ticket's notes — draft
    only, this never sends anything (Shop Rule 5). Appends to the
    ticket's existing notes with a timestamp, rather than overwriting them.

    Returns {"found": False, "ticket_id": ...} if no such ticket exists.
    """
    with _connect_rw() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if row is None:
            return {"found": False, "ticket_id": ticket_id}
        today = _shop_today()
        existing = row["notes"] or ""
        stamped = f"[DRAFT @ {today}] {draft_text}"
        new_notes = f"{existing}\n\n{stamped}" if existing else stamped
        conn.execute("UPDATE tickets SET notes = ? WHERE id = ?", (new_notes, ticket_id))
        conn.commit()
        updated = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    return {"found": True, **dict(updated)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Campus Customs MCP server")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Serve Streamable HTTP on port 8001 (keeps FastAPI free on 8000)",
    )
    args = parser.parse_args()
    if args.http:
        mcp.run(transport="http", host="127.0.0.1", port=8001)
    else:
        mcp.run()
