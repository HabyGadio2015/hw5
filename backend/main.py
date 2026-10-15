"""Campus Customs FastAPI backend — the API the React dashboard (next
problem) calls. Every shop fact still goes through the campus-customs MCP
server (via backend/mcp_client.py or the agent team in backend/agents.py);
this file adds no second, parallel way of touching the database.

Run from this folder:  uvicorn main:app --reload --port 8013
"""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents import run_agent
from mcp_client import call_tool
from models import (
    AgentEvent,
    AgentRole,
    ApprovePaymentRequest,
    ApprovePaymentResult,
    CashBalanceResponse,
    ResetResult,
    RunTicketRequest,
    TicketSummary,
)
from audit import AUDIT_PATH
import json

ROOT = Path(__file__).resolve().parent.parent  # "HW 5"
ORIGINAL_DB = ROOT / "data" / "campus_customs.db"
WORKING_DB = ROOT / "data" / "campus_customs_new.db"

# Fixed seed ticket ids for this assignment — see output/harness.md.
TICKET_IDS = (101, 102, 103)

app = FastAPI(title="Campus Customs Multi-Agent Operations")

# The dashboard is a separate Vite dev server and needs to call this API
# cross-origin. Port 5178, not Vite's default 5173 — ports 5173-5177 are
# already used by other projects in this workspace (see vite.config.ts).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5178"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/tickets", response_model=list[TicketSummary])
async def get_tickets() -> list[TicketSummary]:
    """(1) Return the 3 tickets and whether each is open."""
    tickets = []
    for ticket_id in TICKET_IDS:
        data = await call_tool("get_ticket", {"ticket_id": ticket_id})
        if not data.get("found"):
            continue
        tickets.append(
            TicketSummary(
                id=data["id"],
                type=data["type"],
                subject=data["subject"],
                requester=data["requester"],
                status=data["status"],
                # "partial" is still unresolved work, so it counts as open.
                is_open=data["status"] not in ("resolved", "closed"),
            )
        )
    return tickets


@app.post("/tickets/{ticket_id}/run")
async def run_ticket(ticket_id: int, body: RunTicketRequest | None = None):
    """(2) Run the agent team on a ticket. Starts with BOSS, who reads the
    ticket and delegates from there. This calls the real gpt-6-luna model —
    it costs real tokens every time it's hit."""
    message = (body.message if body else None) or (
        f"Work ticket {ticket_id}: read it with get_ticket, figure out what "
        "it needs, delegate to whichever teammates can help, and report "
        "back with your decision."
    )
    reply = await run_agent(AgentRole.BOSS, message)
    return reply.model_dump(mode="json")


@app.get("/events", response_model=list[AgentEvent])
async def get_events(limit: int = 20) -> list[AgentEvent]:
    """(3) Return recent agent events (what each agent said and which
    tools it used) from the append-only audit trail, newest first, so the
    dashboard board can refresh."""
    if not AUDIT_PATH.exists() or AUDIT_PATH.stat().st_size == 0:
        return []
    rows = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    events: list[AgentEvent] = []
    for row in reversed(rows):
        tools_used = list(
            dict.fromkeys(
                step["tool"] for step in row.get("steps", []) if step.get("type") == "tool_call"
            )
        )
        events.append(
            AgentEvent(
                time=row["time"],
                agent=row["agent"],
                delegation_trail=row.get("delegation_trail", []),
                input=row["input"],
                said=row.get("output", {}).get("summary", ""),
                tools_used=tools_used,
                resolved=row.get("output", {}).get("resolved", False),
            )
        )
        if len(events) >= limit:
            break
    return events


@app.post("/payments/approve", response_model=ApprovePaymentResult)
async def approve_payment(body: ApprovePaymentRequest) -> ApprovePaymentResult:
    """(4) Approve a payment or purchase after a human clicks approve.
    Agents only ever *prepare* a payment_proposal — this route is the only
    thing that actually changes cash, by calling the MCP record_payment
    tool (which itself refuses without a real approved_by, on insufficient
    funds, or on a duplicate payment)."""
    if not body.approved_by.strip():
        raise HTTPException(status_code=400, detail="approved_by is required")
    result = await call_tool(
        "record_payment",
        {
            "kind": body.kind,
            "ref_id": body.ref_id,
            "amount": body.amount,
            "account": body.account,
            "approved_by": body.approved_by,
        },
    )
    return ApprovePaymentResult(**result)


@app.get("/cash", response_model=CashBalanceResponse)
async def get_cash() -> CashBalanceResponse:
    """(5) Return the current checking balance from cash_accounts."""
    data = await call_tool("get_cash_balance", {"account": "checking"})
    if not data.get("found"):
        raise HTTPException(status_code=404, detail="checking account not found")
    return CashBalanceResponse(account=data["name"], balance=data["balance"], date=data["date"])


@app.post("/reset", response_model=ResetResult)
async def reset_database() -> ResetResult:
    """(6) Reset the working database copy to the original seed values, for
    a fresh run. Copies the file directly — this is shop-ops ("reset the
    desk"), not a shop fact, so it doesn't need an MCP tool."""
    shutil.copy(ORIGINAL_DB, WORKING_DB)
    return ResetResult(reset=True, message=f"{WORKING_DB.name} reset from {ORIGINAL_DB.name}")
