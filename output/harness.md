# Campus Customs Multi-Agent Operations — Agent Harness

Living spec for the Campus Customs multi-agent ticket shop (MCP server + FastAPI
multi-agent backend + React dashboard). Grows each problem (data → agents →
tools → delegation → safety → specs).

## 1. Database (`data/campus_customs.db`, working copy `data/campus_customs_new.db`)

SQLite, 9 tables. `campus_customs.db` is the untouched original used to reset
the shop; agents/tools only ever read or write `campus_customs_new.db`.

| Table | Rows (seed) | Purpose |
|---|---|---|
| `desk` | 1 | The shop's "today" — every overdue/due-soon check is relative to this, not the real calendar |
| `tickets` | 3 | The board — every request the agents work (orders, rent, discounts, etc.) |
| `inventory` | 10 | Stock on hand per SKU × size |
| `pricing` | 4 | Cost and list price per SKU — the source of margin |
| `vendors` | 3 | Who can restock what, and how fast |
| `leases` | 1 | The shop's physical space and rent obligation |
| `cash_accounts` | 1 | The shop's bank balance — the hard limit on any payment |
| `payments` | 0 | Ledger of money that has actually gone out (empty until something is paid) |
| `invoices` | 1 | Money the shop owes vendors — and what blocks a vendor from shipping |

### `desk`

| Field | Type | Why it matters for the agents |
|---|---|---|
| `date_today` | TEXT | Defines "today" for the whole shop; every agent compares dates (lease due date, invoice due date, vendor lead time) against this, not the system clock |
| `notes` | TEXT | Free-text context for the human/desk; not used in date logic |

### `tickets`

| Field | Type | Why it matters for the agents |
|---|---|---|
| `id` | INTEGER PK | Stable reference BOSS and other agents use when delegating or logging a decision about a specific ticket |
| `type` | TEXT | Tells BOSS who should own it (`customer_order`→CUSTOMER SERVICE/INVENTORY, `rent_notice`→FACILITIES, `price_override`→ACCOUNTING/CUSTOMER SERVICE) |
| `requester` | TEXT | Who asked — needed for CUSTOMER SERVICE's draft replies and for context in the dashboard |
| `subject` | TEXT | One-line human summary shown on the board |
| `sku` | TEXT (nullable) | Links an inventory-flavored ticket to `inventory`/`pricing` so INVENTORY/ACCOUNTING can look up stock and cost |
| `size` | TEXT (nullable) | Needed with `sku` to find the exact inventory row (PK is `sku`+`size`) |
| `qty` | INTEGER (nullable) | The amount requested — compared against `inventory.qty` to detect a shortfall |
| `lease_id` | INTEGER FK → leases (nullable) | Links a rent ticket to its lease so FACILITIES/ACCOUNTING can pull `monthly_rent` and `next_due` |
| `invoice_id` | INTEGER FK → invoices (nullable) | Links a ticket to a vendor invoice so ACCOUNTING can check if it's open/overdue before paying |
| `status` | TEXT | Tracks ticket progress (`open` → in-progress → resolved); agents should not re-work a resolved ticket |
| `notes` | TEXT | Extra free-text context for whoever picks up the ticket |
| `created_at` | TEXT | When the ticket landed — used with `desk.date_today` to judge urgency/age |

### `inventory`

| Field | Type | Why it matters for the agents |
|---|---|---|
| `sku` | TEXT (PK w/ size) | Product identifier INVENTORY uses to look up stock for a ticket |
| `name` | TEXT | Human-readable product name for dashboard/customer-facing drafts |
| `size` | TEXT (PK w/ sku) | Stock is tracked per size, not just per SKU — a ticket can be satisfiable in one size and not another |
| `qty` | INTEGER | The actual units on hand; comparing this to a ticket's `qty` is how INVENTORY spots a shortfall |
| `location` | TEXT | Where it sits in the shop; operational detail, not needed for restock decisions |

### `pricing`

| Field | Type | Why it matters for the agents |
|---|---|---|
| `sku` | TEXT PK | Links to `inventory`/`tickets` by SKU |
| `unit_cost` | REAL | What the shop pays per unit — ACCOUNTING needs this to compute margin on any discount request |
| `list_price` | REAL | What the shop charges — compared to `unit_cost` for margin, and is the starting point for any `price_override` negotiation |

### `vendors`

| Field | Type | Why it matters for the agents |
|---|---|---|
| `id` | INTEGER PK | Referenced by `invoices.vendor_id` — lets ACCOUNTING check "does this vendor have an open unpaid invoice" before INVENTORY can rely on them to restock |
| `name` | TEXT | Identifies the vendor in drafts/purchase orders (never actually contacted — drafts stay on the board) |
| `specialty` | TEXT | How INVENTORY matches a shortfall (apparel, mugs/small goods, courier) to the right vendor |
| `lead_days` | INTEGER | How long a restock would take — needed to judge whether a vendor can fix a shortfall in time |

### `leases`

| Field | Type | Why it matters for the agents |
|---|---|---|
| `id` | INTEGER PK | Referenced by `tickets.lease_id` |
| `space_name` | TEXT | Identifies which shop space the ticket concerns |
| `landlord` | TEXT | Who the rent is owed to; used in FACILITIES' notes/drafts |
| `monthly_rent` | REAL | The amount ACCOUNTING must check against `cash_accounts.balance` before proposing a rent payment |
| `next_due` | TEXT | Compared to `desk.date_today` to determine if rent is due soon/overdue |
| `notes` | TEXT | Extra lease context |

### `cash_accounts`

| Field | Type | Why it matters for the agents |
|---|---|---|
| `name` | TEXT PK | Account identifier (`checking`) referenced by `payments.account` |
| `balance` | REAL | The hard ceiling on every payment — ACCOUNTING's pay tool must refuse anything that would take this negative |
| `date` | TEXT | When the balance was last known-accurate |

### `payments`

| Field | Type | Why it matters for the agents |
|---|---|---|
| `id` | INTEGER PK | Ledger row identifier |
| `kind` | TEXT | What was paid for (e.g. rent, vendor invoice) — lets the dashboard/audit trail distinguish payment types |
| `ref_id` | INTEGER (nullable) | Points back to the `lease`/`invoice` row the payment settles, so that record can be marked paid |
| `amount` | REAL | Must be deducted from `cash_accounts.balance` when the payment is recorded |
| `account` | TEXT | Which cash account was debited |
| `paid_at` | TEXT | When the payment was recorded, relative to `desk.date_today` |
| `approved_by` | TEXT | Proof of the required human approval — a payment row must never be written without one |

### `invoices`

| Field | Type | Why it matters for the agents |
|---|---|---|
| `id` | INTEGER PK | Referenced by `tickets.invoice_id` and `payments.ref_id` |
| `vendor_id` | INTEGER FK → vendors | Ties the invoice to the vendor it would block from shipping while open |
| `amount` | REAL | What ACCOUNTING must check against `cash_accounts.balance` before proposing payment |
| `due_date` | TEXT | Compared to `desk.date_today` to flag it as overdue |
| `status` | TEXT | `open` invoices are unpaid and block that vendor from shipping new product; must flip to paid/closed once `payments` records settlement |
| `description` | TEXT | Human-readable reason for the charge |

## 2. Today's Open Tickets — Cross-Table Links

Shop "today" (`desk.date_today`) = **2026-08-31**. All three tickets are `open`.

### Ticket 101 — customer_order (Tauhid Zaman, "Bulldog tee")
- `sku=CC-TEE-WHITE`, `size=S`, `qty=1` → **`inventory` shows 0 units of `CC-TEE-WHITE` size S** — this order cannot be filled from stock, it's a real shortfall.
- `invoice_id=501` → **`invoices` row 501**: vendor `1`, $840, due 2026-08-28 (**already 3 days overdue** relative to desk date), status `open`, description "Rush reprint CC-TEE-WHITE S" — this is the invoice for the *previous* reprint of this exact item.
- Invoice 501's `vendor_id=1` → **`vendors` row 1 = Bulldog Print Co** (specialty "apparel reprint", 5-day lead time) — the natural restock vendor for `CC-TEE-WHITE`.
- Business rule collision: Bulldog Print Co has an **open unpaid invoice**, so per shop rules they **will not ship** a new restock until invoice 501 is paid. ACCOUNTING must check cash and get human approval to pay the $840 before INVENTORY can expect new stock (then +5 lead days).

### Ticket 102 — rent_notice (Elm City Properties, "Rent due")
- `lease_id=1` → **`leases` row 1**: Chapel Street shop, landlord Elm City Properties, `monthly_rent=$2400`, `next_due=2026-09-02` — exactly **2 days** after desk date, matching the ticket note "rent due in 2 days."
- No `sku`/`invoice_id` — this ticket doesn't touch inventory or vendor invoices at all, just the lease and cash.
- ACCOUNTING must check `cash_accounts.balance` ($3,400) against the $2,400 rent and get human approval before any payment is recorded.

### Ticket 103 — price_override (Yale AI Club, "Bulk hoodie discount")
- `sku=CC-HOOD-NAVY`, `size=M`, `qty=20` → **`inventory` shows only 8 units** of `CC-HOOD-NAVY` size M on hand — a **12-unit shortfall** against the requested 20.
- `pricing` for `CC-HOOD-NAVY`: `unit_cost=$22`, `list_price=$58` (margin $36/unit, ~62%) — ACCOUNTING needs this to judge how much discount the shop can give and still keep a reasonable margin.
- Restocking the shortfall would again route to **Bulldog Print Co** (apparel specialty) — the **same vendor blocked by invoice 501** in ticket 101. So tickets 101 and 103 compete for/depend on the same vendor relationship being unblocked.

## 3. MCP Tools (`mcp_server/server.py`, Problem 3)

Three read-only FastMCP tools, each grounded in one table and demonstrated against one of today's three open tickets:

| Tool | Table it reads | Ticket it unlocks | Why that tool is right for that ticket |
|---|---|---|---|
| `get_ticket(ticket_id)` | `tickets` | **101** | It's the only way to learn that ticket 101 is tied to `sku=CC-TEE-WHITE`, `size=S`, and `invoice_id=501` — the link that exposes this order as tangled up with an unpaid vendor invoice. |
| `check_inventory(sku, size)` | `inventory` | **103** | Returns the real on-hand count (8) for `CC-HOOD-NAVY` size M, turning Yale AI Club's request for 20 into a concrete, provable 12-unit shortfall instead of a guess. |
| `get_shop_today()` | `desk` | **102** | Supplies the shop's actual "today" (2026-08-31), the only way to compute that the lease's `next_due` (2026-09-02) is exactly 2 days away, matching the ticket's own urgency note. |

## 4. Agent Team ↔ MCP Tools ↔ Tables (Problem 5)

All 14 MCP tools in `mcp_server/server.py` (grown from the original 3 in Problem 5, plus one more in Problem 9 — see note below), each tied to the table(s) it touches:

| Tool | Read/Write | Table(s) |
|---|---|---|
| `get_ticket(ticket_id)` | read | `tickets` |
| `list_open_tickets()` | read | `tickets` |
| `check_inventory(sku, size)` | read | `inventory` |
| `get_pricing(sku)` | read | `pricing` |
| `list_vendors()` | read | `vendors` |
| `check_vendor_invoice_status(vendor_id)` | read | `vendors`, `invoices` |
| `get_invoice(invoice_id)` | read | `invoices` |
| `get_lease(lease_id)` | read | `leases` |
| `get_cash_balance(account)` | read | `cash_accounts` |
| `check_payment_history(kind, ref_id)` | read | `payments` |
| `get_shop_today()` | read | `desk` |
| `record_payment(kind, ref_id, amount, account, approved_by)` | **write** | `payments`, `cash_accounts`, `invoices` (only when `kind="invoice"`) |
| `update_ticket_status(ticket_id, status, notes)` | **write** | `tickets` |
| `save_draft(ticket_id, draft_text)` | **write** | `tickets` |

*Note added in Problem 9 (text above otherwise unchanged): `check_payment_history` didn't exist yet when this section was first written. A live run on ticket 102 showed ACCOUNTING correctly refusing to propose the rent payment because it had no tool to confirm rent hadn't already been paid (Shop Rule 2) — so this read tool was added, over the real `payments` table, no invented fields.*

*Also corrected (Problem 9): this section originally said "there's no code-level restriction on which agent can call which tool." That became false in Problem 7 — `record_payment` is filtered out of every agent's own toolset via `AbstractToolset.filtered(...)` in `backend/agents.py`, so no agent can call it at all; only the `/payments/approve` route (talking to the unfiltered server) can. See section 5 below. The ACCOUNTING row below is corrected to drop `record_payment` (it was never actually callable by agents after Problem 7) and add `check_payment_history`.*

| Agent | Tools its prompt calls out |
|---|---|
| BOSS | `get_ticket`, `list_open_tickets`, `update_ticket_status` |
| INVENTORY | `check_inventory`, `list_vendors`, `check_vendor_invoice_status`, `get_ticket` |
| ACCOUNTING | `get_cash_balance`, `get_invoice`, `get_pricing`, `get_lease`, `check_payment_history` |
| FACILITIES | `get_lease`, `get_shop_today` |
| CUSTOMER SERVICE | `save_draft`, `get_ticket`, `check_inventory` |

`get_shop_today()` is relevant to all five (everyone needs "today" for overdue checks). `delegate(to_agent, request)` is a separate, non-MCP PydanticAI tool every agent has — it calls a teammate's agent loop directly, not the database.

## 5. Safety & Guardrails

**The 8 Shop Rules** (Haby's rules, summarized here; each agent's prompt in `backend/prompts/` lists all 8 under "Shop Rules"):

1. The goal is to make a profit (P = R − C). No sale or discount may leave no profit.
2. Payments are made once. Check before paying, and flag any double-payment risk.
3. BOSS always has the final say.
4. A human (Haby) must approve before anything is paid.
5. No emails to customers or vendors. Drafts stay on the board.
6. Open tickets on the board can be anything the shop has to handle (orders, rent, unpaid bills, discount requests).
7. Never mark a ticket resolved if it's only partially resolved. Say Not Resolved and add a one-line Partial Fulfillment note.
8. No inventions (dates, amounts, requests, tools). If something isn't found, is wrong, or isn't there, say so.

**Already built in, not just prompted for:**

- **Human approval is enforced in code, not just asked for.** The agents' own MCP toolset has `record_payment` filtered out entirely (`backend/agents.py`, via `AbstractToolset.filtered`) — no agent can call it, no matter what the model decides. Only `backend/main.py`'s `/payments/approve` route (hit after a human clicks approve) talks to the unfiltered server and can call it. `record_payment` also refuses outright if `approved_by` is blank, as a second layer.
- **No negative balances, enforced in code.** `record_payment` checks `cash_accounts.balance` before writing anything and refuses if the payment would take it negative.
- **No double payment, enforced in code.** `record_payment` checks for an existing `payments` row with the same `(kind, ref_id)` and refuses if one exists.
- **No customer/vendor contact is even possible.** There is no "send email" or "call vendor" tool anywhere in the MCP server — `save_draft` only ever writes to a ticket's own `notes`. The guardrail here is omission: the capability to actually contact someone doesn't exist in this system, so no amount of prompt-following failure can cause it.
- **Bounded delegation chains.** `MAX_DELEGATION_DEPTH` (3, in `backend/deps.py`) stops a chain of agents delegating to each other from growing without limit.
- **Shared, capped token budget per ticket.** Every top-level `run_agent()` call sets a `UsageLimits(request_limit=...)`, and every delegated sub-run shares that same budget (`usage=ctx.usage`) instead of getting a fresh one — so a long delegation chain can't multiply cost by spinning up "free" sub-budgets. (This is also the limit that was hit and refused the work during live testing, exactly as intended.)
- **Append-only audit trail.** `output/audit_trail.json` records every agent run (top-level and delegated) — every tool call with its arguments and result, every thought/text step, and the final structured output — so a human can review after the fact exactly what was seen and decided, including refusals.
  *Note added after Problem 11:* entries 1–29 are the Problem 9 runs that every write-up in `output/` describes. Entries 30–37 (2026-10-15, 01:06–01:09 UTC) are one extra run on ticket 103. It was started from the dashboard after the submission, against a database that had been reset with Reset Desk. That run proposed no payment and ended Not Resolved. Its entries stay, because the trail is append-only. The committed `data/campus_customs_new.db` was then restored to the Problem 9 state ($2,560, one $840 payment), so it matches the Cash tab and `resolved_tickets.json`. Entries 38–42 (01:12–01:13 UTC) are a verification rerun of ticket 103 on that Problem 9 end state, requested by Haby. It reached the same outcome (Not Resolved, $22 floor, 8 of 20 in stock, no payment). Its only change to the database was one more customer draft appended to ticket 103's notes. Cash and payments are unchanged.
- **Shop-time consistency.** Writes (`record_payment`, `save_draft`) stamp dates using `desk.date_today`, not the real wall clock, so the working database never drifts from the shop's own sense of "today."

**Guardrails a real business would want beyond what this assignment builds:**

- A **per-payment dollar threshold** above which a second human (not just any approver) must sign off.
- **Rate limiting / per-ticket cooldown** so the same ticket can't be re-worked (and re-billed in model-cost terms) repeatedly in a short window.
- **Alerting on refusals**, not just logging them — insufficient funds, blocked vendors, and depth-limit cutoffs should actively notify a human, not just sit quietly in the audit trail.
- **Independent monitoring of the `resolved` field over time** — if an agent starts marking things resolved unusually often, that's a signal worth a human spot-check, since the field is self-reported by the same model it's meant to keep honest.
- **A hard kill switch** a human can flip to stop all agent activity immediately, independent of any in-conversation instruction.

## 6. Backend API Routes (`backend/main.py`, Problem 7)

Running at `http://localhost:8000` (`uvicorn main:app --reload --port 8000`, from `backend/`) for the dashboard to call:

| Route | Does |
|---|---|
| `GET /tickets` | Returns the 3 seed tickets (101, 102, 103) and whether each is open |
| `POST /tickets/{ticket_id}/run` | Runs the agent team (starting at BOSS) on that ticket — real `gpt-6-luna` calls, costs tokens |
| `GET /events?limit=` | Recent audit-trail entries, newest first: agent, what it said, tools used, resolved |
| `POST /payments/approve` | The only route that moves money — calls `record_payment` after a human approval, used for a prior `payment_proposal` |
| `GET /cash` | Current `checking` balance from `cash_accounts` |
| `POST /reset` | Re-copies `campus_customs.db` over `campus_customs_new.db` for a fresh run |

*Note added in Problem 9:* "open" means any status other than `resolved`/`closed`, so a `partial` ticket still counts as open work. The route originally used `status == "open"`, which wrongly showed `partial` tickets as closed.

## 7. The Five Agents (`backend/agents.py`, `backend/prompts/*.md`)

All five run on **`gpt-6-luna` via Portkey only** (hardcoded in `backend/agents.py`, never read from an environment variable), share the campus-customs MCP toolset (13 of 14 tools — `record_payment` is filtered out, see section 5), and return a structured `AgentReply` (`backend/models.py`): `summary`, `resolved`, `partial_fulfillment_note`, `needs_human_approval`, `delegated_to`, `payment_proposal`.

| Agent | Job | Prompt file |
|---|---|---|
| **BOSS** | Reads each ticket, decides who should work it, makes the final call, carries forward any `payment_proposal` from a delegate | `prompts/boss.md` |
| **INVENTORY** | Checks stock by SKU/size, spots shortfalls, matches a vendor by specialty, checks if that vendor is blocked by an open invoice | `prompts/inventory.md` |
| **ACCOUNTING** | Watches cash and invoices, checks margins, prepares (never executes) payments via `payment_proposal` | `prompts/accounting.md` |
| **FACILITIES** | Handles leases and rent | `prompts/facilities.md` |
| **CUSTOMER SERVICE** | Drafts customer-facing messages via `save_draft` — never sends anything | `prompts/customer_service.md` |

**Full connectivity:** every agent has one shared `delegate(to_agent, request)` tool (not an MCP tool — it calls a teammate's own agent loop directly) and can reach any of the other four, but not itself. Delegation depth is capped at 3 (`backend/deps.py`, `MAX_DELEGATION_DEPTH`) and the whole chain shares one token budget (`usage=ctx.usage`), not a fresh one per hop.

**What Problem 9's live run actually showed** (full detail in `output/desk_tickets.html`'s per-ticket Actual sections and `output/resolved_tickets.json`): delegation in practice was often less linear than the Expected plan predicted — e.g. ticket 102 saw BOSS ↔ ACCOUNTING ↔ FACILITIES hop back and forth several times without new information, and ACCOUNTING didn't call a tool (`check_payment_history`) that was specifically added so it could resolve its own stated blocker. These are genuine, observed limitations, not bugs that were hidden or smoothed over.

## 8. Dashboard (`frontend/`, Problem 8)

React + Vite + TypeScript, served at `http://localhost:5178` (`npm run dev`); talks only to the Problem 7 backend at `http://localhost:8000` (CORS on the backend is scoped to exactly this origin, not a wildcard — see `backend/main.py`). Full design rationale — layout, the 5 agent "characters," how resolved tickets and cash show up, and why — is in `output/design.md`; this section is the functional summary.

- **`TicketBoard`** — lists all 3 tickets with their real status pill (`open`/`partial`, from `GET /tickets`) and lets a human select exactly one at a time (disabled while a run is active).
- **`AgentStage`** — *(click filter added after Problem 11, at Haby's request: clicking an agent's card shows only that agent's messages in the feed, and clicking it again, or the button labeled "Click the Yellow Button Above to See Agents at Work and Status Below", clears the filter)* the 5 agent avatars (dim until they've spoken, glowing/pulsing when most recently active) plus a live feed that polls `GET /events` every 1.2s during a run and filters to events from the current run only (by timestamp, comparing real `Date` instants rather than raw strings — Python's and JS's ISO timestamp formats don't sort correctly against each other as plain strings).
- **`ResolutionPanel`** shows the run's real verdict and BOSS's summary, plus a "What each agent did" list. That list holds each agent's last statement and the tools it used, taken from that run's events (added in Problem 9, to cover requirement 5 directly). It also flags a mismatch if BOSS claims `resolved: true` while the ticket is still unresolved in the DB. That check never had cause to fire in Problem 9, because no run reported `resolved: true`.
- **`ApprovalPanel`** — appears only when a reply carries a `payment_proposal`; requires a typed name before `POST /payments/approve` can fire, mirroring Shop Rule 4 in the UI itself.
- The dashboard was verified visually for the first time during Problem 9 (`output/resolved_board.html`'s screenshots) — ticket selection, highlighting, and the status pills all render and behave correctly in a real browser.
