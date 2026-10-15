# Campus Customs Multi-Agent Operations

Campus Customs runs on an agentic team: open tickets land on a board
(customer orders, rent, unpaid bills, discount requests, whatever the shop
has to handle), and five connected agents — BOSS, INVENTORY, ACCOUNTING,
FACILITIES, CUSTOMER SERVICE — work them, with a human approving anything
that spends money.

## Shop Rules

These are enforced in every agent's system prompt (`backend/prompts/`) and,
where possible, structurally in the agent output type (`backend/models.py`).

1. The goal is to make a profit (**P = R − C**). No sale or discount is
   ever approved if it leaves no profit.
2. Payments are made **once**. Agents must check before recommending or
   reporting a payment, and flag any double-payment risk or mistake.
3. **BOSS always has the final say** on a ticket, even after delegating.
4. A **human** (Haby) must approve before anything is actually paid — no
   exceptions.
5. **No emails to customers, no calls/emails to vendors.** Everything
   customer- or vendor-facing is a draft that stays on the board.
6. Tickets on the board can be customer orders, rent, unpaid bills,
   discount requests, or anything else the shop has to handle.
7. **Nothing is marked resolved if only partially resolved.** Agents set
   `resolved=false` and add a one-line `partial_fulfillment_note`
   explaining what's missing (`AgentReply`/`DelegationResult` in
   `backend/models.py` make this a required structured field, not just a
   prompt instruction).
8. **No inventions** — dates, amounts, requests, tools, anything. If a tool
   says something isn't found, the agent says so. If something looks
   wrong, the agent says so.

## MCP Tools

**Implemented in Problem 3** (`mcp_server/server.py`), read-only, against
`data/campus_customs_new.db`:

| Tool | Reads | Does |
|---|---|---|
| `get_ticket(ticket_id)` | `tickets` | Fetch one ticket by id, every field |
| `check_inventory(sku, size)` | `inventory` | On-hand qty for a SKU + size |
| `get_shop_today()` | `desk` | The shop's current date |

**Suggested in Problem 5** (what each agent needed to work the 3 open
tickets). The Status column was added in Problem 9 to show what actually
got built:

| # | Tool | For | Why it's needed | Status |
|---|---|---|---|---|
| 4 | `get_vendor(specialty)` / `list_vendors()` | INVENTORY | Match a shortfall to the right vendor and get `lead_days` | Built as `list_vendors()` only (just 3 vendors, so the agent matches specialty itself) |
| 5 | `check_vendor_invoice_status(vendor_id)` | INVENTORY | A vendor with an open unpaid invoice won't ship — must check before promising a restock | Built |
| 6 | `get_cash_balance()` | ACCOUNTING | Read `cash_accounts` before recommending any payment | Built |
| 7 | `get_invoice(invoice_id)` | ACCOUNTING | Amount, status, due date, vendor for a specific invoice | Built |
| 8 | `get_pricing(sku)` | ACCOUNTING | Unit cost / list price for margin and no-loss checks (Shop Rule 1) | Built |
| 9 | `record_payment(...)` | ACCOUNTING | **Write** tool: insert into `payments`, debit `cash_accounts`, mark invoice/lease paid — must require an approval flag (Shop Rule 4) | Built. Refuses a blank `approved_by`, a negative balance, or a duplicate payment. Agents cannot call it at all (it is filtered out of their toolset). Only the human-approval route `POST /payments/approve` can. |
| 10 | `get_lease(lease_id)` | FACILITIES | Lease terms, rent, next due date | Built |
| 11 | `list_open_tickets()` | BOSS | See the whole board, not one ticket at a time | Built |
| 12 | `update_ticket_status(ticket_id, status, notes)` | BOSS | **Write** tool to close out a ticket once genuinely resolved (Shop Rule 7) | Built |
| 13 | `save_draft(ticket_id, draft_text)` | CUSTOMER SERVICE | Persist a draft without ever sending it (Shop Rule 5) | Built |
| 14 | *(reset step)* | all | Re-copy `campus_customs.db` → `campus_customs_new.db` before a full ticket-resolution run | Built as the backend route `POST /reset`, not as an MCP tool (it resets the desk; it is not a shop fact) |
| — | `check_payment_history(kind, ref_id)` | ACCOUNTING | Confirm a bill isn't already paid before proposing payment (Shop Rule 2) | Added in Problem 9, after the live run on ticket 102 showed it was missing |

That gives 14 MCP tools in total. 13 are visible to the agents; `record_payment` is reserved for the approval route.

## Agent Team (`backend/`)

Five PydanticAI agents (model: `gpt-6-luna` via Portkey, no other model
used anywhere in this code), fully connected through a shared `delegate`
tool (any agent can ask any other for help, with a depth limit to bound
cost), each attached in-process to the `campus-customs` MCP server:

- `backend/prompts/{boss,inventory,accounting,facilities,customer_service}.md`
- `backend/models.py` — `AgentRole`, `AgentReply`, `DelegationResult`, `PaymentProposal`, plus the API request/response types
- `backend/deps.py` — `TeamDeps` (current role + delegation depth guard)
- `backend/agents.py` — builds the team and the `delegate` tool, and filters `record_payment` out of the agents' toolset
- `backend/audit.py` — append-only `output/audit_trail.json`
- `backend/main.py` — the FastAPI routes the dashboard calls (see `output/harness.md` section 6)
- `frontend/` — the React + Vite dashboard (see `output/design.md`)

## Run it

All commands start from the repo root (`hw5/`). You need Python 3.11+ (required by pydantic-ai) and Node 20.19+ or 22.12+ (required by Vite).

**1. Set up once**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then put your PORTKEY_API_KEY in .env
```

**2. Copy the original database to the working copy (for a clean run)**

`data/campus_customs.db` is the untouched original. Everything the app does
reads and writes `data/campus_customs_new.db`. As committed, the working copy
holds the state *after* the Problem 9 run: checking at $2,560, invoice #501
paid. To start clean:

```bash
cp data/campus_customs.db data/campus_customs_new.db
```

**3. Start the MCP server (optional)**

```bash
python mcp_server/server.py          # stdio, e.g. for an MCP client / vibe coder
python mcp_server/server.py --http   # or Streamable HTTP on http://127.0.0.1:8001/mcp
```

You don't have to start this yourself for the app. The backend loads the same
server in-process. The repo's `.mcp.json` registers it as `campus-customs` for
a vibe coder opened in this folder.

**4. Start the FastAPI backend (port 8000)**

```bash
cd backend
uvicorn main:app --reload --port 8000
```

**5. Start the React board (port 5178)**

In a second terminal:

```bash
cd frontend
npm install
npm run dev                  # open http://localhost:5178
```

The board uses port 5178, not Vite's default 5173, and the backend's CORS
only allows that origin.

**6. Reset the database before a full 3-ticket run**

Click **↺ Reset Desk** on the board, or:

```bash
curl -X POST http://localhost:8000/reset
```

This re-copies the original database over the working copy, so checking goes
back to $3,400 and all 3 tickets reopen. Then pick a ticket and click
**Start the Team**. Each run makes real `gpt-6-luna` calls and costs tokens.
