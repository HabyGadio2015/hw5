# Campus Customs MCP Server

A FastMCP server that exposes tools over the Campus Customs shop database.
Every agent in the multi-agent team (BOSS, INVENTORY, ACCOUNTING,
FACILITIES, CUSTOMER SERVICE) calls these tools instead of touching the
database directly — this is the single source of shop facts, with no
second shop-tools layer anywhere else in the codebase. Every tool returns
only what's actually stored or computed from what's stored — nothing is
invented.

## Database

Reads and writes `data/campus_customs_new.db` — the **working copy** of the
shop database. `data/campus_customs.db` (the original) is never touched, so
the shop can always be reset by re-copying it. Read tools open a read-only
connection (`mode=ro`); only the 3 write tools below use a read-write
connection.

## Tools (14)

**Read tools:**

- `get_ticket(ticket_id)` — one ticket from `tickets`, every field.
- `list_open_tickets()` — every `tickets` row with `status = 'open'`.
- `check_inventory(sku, size)` — on-hand qty + location from `inventory`
  (case-insensitive).
- `get_pricing(sku)` — `unit_cost` / `list_price` from `pricing`.
- `list_vendors()` — every `vendors` row.
- `check_vendor_invoice_status(vendor_id)` — whether a vendor (`vendors` +
  `invoices`) has an open invoice; includes a `can_ship` flag.
- `get_invoice(invoice_id)` — one `invoices` row.
- `get_lease(lease_id)` — one `leases` row.
- `get_cash_balance(account="checking")` — one `cash_accounts` row.
- `check_payment_history(kind, ref_id)` — whether a `payments` row already
  exists for this kind/ref_id (added in Problem 9, after a live run showed
  ACCOUNTING correctly refusing to propose rent because it had no way to
  confirm rent hadn't already been paid).
- `get_shop_today()` — `desk.date_today` + notes, the only valid "today"
  for judging overdue leases/invoices.

**Write tools** (the only ones allowed to change the working copy):

- `record_payment(kind, ref_id, amount, account, approved_by)` — the only
  way money leaves the shop. Writes `payments`, debits `cash_accounts`,
  and (for `kind="invoice"`) marks that invoice `paid`. Refuses outright —
  no exceptions — if `approved_by` is blank, if it would take the balance
  negative, or if a payment already exists for that `(kind, ref_id)`.
- `update_ticket_status(ticket_id, status, notes=None)` — updates a
  ticket's status (and optionally its notes) in `tickets`.
- `save_draft(ticket_id, draft_text)` — appends a timestamped draft to a
  ticket's `notes` in `tickets`. Never sends anything anywhere — there is
  no email/call tool in this server, by design.

Every tool returns `{"found": False, ...}` (or `{"success": False,
"reason": ...}` for writes) instead of guessing when something doesn't
exist or a rule would be broken.

## Running

```bash
python mcp_server/server.py          # stdio
python mcp_server/server.py --http   # Streamable HTTP on :8001
```

## Registered with the vibe coder

Added to the project-root `.mcp.json` (`AI Foundations/.mcp.json`) as
`campus-customs`, pointing at this folder's own `.venv/bin/python` and
`server.py`. New `.mcp.json` entries only take effect in Claude Code
sessions started after the edit.

## Testing

`mcp_server/test_tools.py` connects to the server over the real stdio MCP
protocol (the same way the vibe coder does) and calls the original 3 tools
from Problem 3 (`get_ticket`, `check_inventory`, `get_shop_today`):

```bash
python mcp_server/test_tools.py
```

The 10 tools added in Problem 5 were verified by direct call against the
real working database (all read tools matched ground truth; `record_payment`
was verified to pay successfully, refuse with no approval, refuse on
insufficient funds, and refuse a duplicate payment; `update_ticket_status`
and `save_draft` were verified to update/append correctly) — the working
copy was then reset to the original database so the test writes don't
linger.

`check_payment_history` (added in Problem 9) was checked by calling it directly against the real working database. For invoice 501, paid during Problem 9, it returned `already_paid: true` with that payment row. For rent on lease 1, never paid, and for a nonexistent invoice, it returned `already_paid: false`.
