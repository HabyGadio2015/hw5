"""Shared Pydantic types for the Campus Customs agent team."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """The five agent roles on the Campus Customs team."""

    BOSS = "boss"
    INVENTORY = "inventory"
    ACCOUNTING = "accounting"
    FACILITIES = "facilities"
    CUSTOMER_SERVICE = "customer_service"


class PaymentProposal(BaseModel):
    """A payment ACCOUNTING recommends but cannot execute itself — the
    human-approval route (backend/main.py) needs this structured data,
    not just prose, to actually call `record_payment`."""

    kind: str = Field(..., description='e.g. "invoice" or "rent".')
    ref_id: int = Field(..., description="The invoices.id or leases.id this payment settles.")
    amount: float
    account: str = Field("checking", description="Which cash_accounts row to debit.")
    reason: str | None = Field(None, description="One-liner on why this payment is recommended.")


class DelegationResult(BaseModel):
    """What a delegated-to agent reports back to whoever asked for help."""

    from_agent: AgentRole
    reply: str
    resolved: bool = Field(
        ..., description="Shop Rule 7: false if the delegate's part was only partially handled."
    )
    partial_fulfillment_note: str | None = Field(
        None,
        description="One-liner explaining what's missing, required when resolved is false.",
    )
    payment_proposal: PaymentProposal | None = Field(
        None, description="Carried forward from the delegate's AgentReply, if any."
    )


class AgentReply(BaseModel):
    """Structured final output every agent in the team returns."""

    summary: str = Field(
        ..., description="Plain-language summary of what was found or decided."
    )
    resolved: bool = Field(
        ...,
        description=(
            "Shop Rule 7: must be false unless the ticket (or the piece you were "
            "asked to help with) is FULLY resolved. Any partial progress is false, "
            "never true — never mark something resolved that only got partway done."
        ),
    )
    partial_fulfillment_note: str | None = Field(
        None,
        description=(
            "Required one-liner when resolved is false: explain exactly what's "
            "missing or still outstanding (Shop Rule 7)."
        ),
    )
    needs_human_approval: bool = Field(
        False,
        description=(
            "True if this reply proposes a payment or any other action that "
            "a human must approve before it can happen (Shop Rule 4)."
        ),
    )
    delegated_to: list[AgentRole] = Field(
        default_factory=list,
        description="Which teammates (if any) this agent delegated to while answering.",
    )
    payment_proposal: PaymentProposal | None = Field(
        None,
        description=(
            "Required whenever needs_human_approval is true because of a payment: "
            "the exact kind/ref_id/amount/account a human would approve. Never set "
            "this AND report the payment as already made in the same reply."
        ),
    )


# ---------------------------------------------------------------------------
# API request/response types (backend/main.py, Problem 7)
# ---------------------------------------------------------------------------


class TicketSummary(BaseModel):
    """One row for the dashboard's ticket list."""

    id: int
    type: str
    subject: str
    requester: str
    status: str
    is_open: bool


class RunTicketRequest(BaseModel):
    message: str | None = Field(
        None,
        description="Optional override instruction. Defaults to a generic 'work this ticket'.",
    )


class ApprovePaymentRequest(BaseModel):
    """What the dashboard sends when a human clicks Approve on a
    payment_proposal."""

    kind: str
    ref_id: int
    amount: float
    account: str = "checking"
    approved_by: str = Field(..., description="The human's name — required, never blank.")


class ApprovePaymentResult(BaseModel):
    success: bool
    reason: str | None = None
    payment_id: int | None = None
    new_balance: float | None = None


class CashBalanceResponse(BaseModel):
    account: str
    balance: float
    date: str


class ResetResult(BaseModel):
    reset: bool
    message: str


class AgentEvent(BaseModel):
    """One row for the dashboard's live event feed — a condensed view of
    one audit_trail.json entry: what the agent said and which tools it
    used, not the full step-by-step detail."""

    time: str
    agent: str
    delegation_trail: list[str]
    input: str
    said: str
    tools_used: list[str]
    resolved: bool
