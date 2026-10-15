"""Campus Customs agent team: BOSS, INVENTORY, ACCOUNTING, FACILITIES,
CUSTOMER SERVICE — built with PydanticAI, wired to the campus-customs MCP
server, and fully connected via a shared `delegate` tool.

Model: gpt-6-luna through Portkey only, for every agent in this file. Do not
add any other model here.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Final

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.toolsets import AbstractToolset
from pydantic_ai.usage import UsageLimits

from audit import append_run
from deps import MAX_DELEGATION_DEPTH, TeamDeps
from models import AgentRole, DelegationResult, AgentReply

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # "HW 5"
PROMPTS_DIR = HERE / "prompts"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")  # hw5/.env (graders: copy .env.example)
load_dotenv(ROOT.parent / ".env")  # fallback: AI Foundations root .env

# HW5 rule: ONLY this model, for every agent. Not read from the environment
# on purpose, so it can't be silently swapped.
MODEL_NAME: Final = "gpt-6-luna"
PORTKEY_BASE_URL: Final = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1").rstrip("/")

_PROMPT_FILES: Final[dict[AgentRole, str]] = {
    AgentRole.BOSS: "boss.md",
    AgentRole.INVENTORY: "inventory.md",
    AgentRole.ACCOUNTING: "accounting.md",
    AgentRole.FACILITIES: "facilities.md",
    AgentRole.CUSTOMER_SERVICE: "customer_service.md",
}

AGENTS: dict[AgentRole, Agent[TeamDeps, AgentReply]] = {}

# record_payment is the ONLY thing that moves money — agents may prepare a
# payment_proposal, never execute one. Filtered out of the agents' own
# toolset below so this is a structural guarantee, not just a prompt rule;
# only backend/main.py's /payments/approve route (via mcp_client.py, which
# talks to the unfiltered server) can actually call it.
_AGENT_BLOCKED_TOOLS: Final[frozenset[str]] = frozenset({"record_payment"})

_toolset: AbstractToolset[TeamDeps] | None = None
_model: OpenAIResponsesModel | None = None


def _mcp_toolset() -> AbstractToolset[TeamDeps]:
    """Attach the campus-customs FastMCP server in-process (tools over
    data/campus_customs_new.db), with record_payment filtered out."""
    global _toolset
    if _toolset is None:
        from mcp_server.server import mcp as campus_mcp

        full_toolset = MCPToolset(campus_mcp)
        _toolset = full_toolset.filtered(
            lambda ctx, tool_def: tool_def.name not in _AGENT_BLOCKED_TOOLS
        )
    return _toolset


def _shared_model() -> OpenAIResponsesModel:
    global _model
    if _model is None:
        api_key = os.getenv("PORTKEY_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("PORTKEY_API_KEY is not set (put it in the root .env file).")
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=PORTKEY_BASE_URL,
            default_headers={"x-portkey-api-key": api_key},
        )
        _model = OpenAIResponsesModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))
    return _model


async def delegate(ctx: RunContext[TeamDeps], to_agent: AgentRole, request: str) -> DelegationResult:
    """Ask a teammate on the Campus Customs team for help with part of a
    ticket. Full connectivity: any agent can delegate to any other agent
    (but not to itself) as many times as genuinely needed.
    """
    if to_agent == ctx.deps.current_role:
        raise ModelRetry(
            f"You are {ctx.deps.current_role.value} — delegate to a teammate, not yourself."
        )
    if ctx.deps.delegation_depth >= MAX_DELEGATION_DEPTH:
        return DelegationResult(
            from_agent=to_agent,
            reply=(
                "Delegation depth limit reached for this ticket — "
                "proceed with what the team already knows instead of delegating further."
            ),
            resolved=False,
            partial_fulfillment_note="Delegation depth limit reached before this teammate could weigh in.",
        )
    target = AGENTS[to_agent]
    sub_deps = TeamDeps(
        current_role=to_agent,
        delegation_depth=ctx.deps.delegation_depth + 1,
        delegation_trail=[*ctx.deps.delegation_trail, f"{ctx.deps.current_role.value}->{to_agent.value}"],
    )
    result = await target.run(request, deps=sub_deps, usage=ctx.usage)
    append_run(
        agent=to_agent.value,
        delegation_trail=sub_deps.delegation_trail,
        delegation_depth=sub_deps.delegation_depth,
        input_message=request,
        messages=result.new_messages(),
        output=result.output.model_dump(mode="json"),
    )
    return DelegationResult(
        from_agent=to_agent,
        reply=result.output.summary,
        resolved=result.output.resolved,
        partial_fulfillment_note=result.output.partial_fulfillment_note,
        payment_proposal=result.output.payment_proposal,
    )


def _build_agent(role: AgentRole) -> Agent[TeamDeps, AgentReply]:
    prompt_path = PROMPTS_DIR / _PROMPT_FILES[role]
    agent = Agent(
        _shared_model(),
        deps_type=TeamDeps,
        output_type=AgentReply,
        instructions=prompt_path.read_text(encoding="utf-8"),
        toolsets=[_mcp_toolset()],
        model_settings=OpenAIResponsesModelSettings(openai_reasoning_summary="auto"),
    )
    agent.tool(delegate)
    return agent


def _build_team() -> None:
    for role in AgentRole:
        AGENTS[role] = _build_agent(role)


_build_team()


async def run_agent(role: AgentRole, message: str, *, request_limit: int = 40) -> AgentReply:
    """Entry point: start a fresh run with the given agent (delegation depth
    0) and log the full step trail (including every delegated sub-run) to
    output/audit_trail.json."""
    deps = TeamDeps(current_role=role)
    agent = AGENTS[role]
    result = await agent.run(
        message, deps=deps, usage_limits=UsageLimits(request_limit=request_limit)
    )
    append_run(
        agent=role.value,
        delegation_trail=deps.delegation_trail,
        delegation_depth=deps.delegation_depth,
        input_message=message,
        messages=result.new_messages(),
        output=result.output.model_dump(mode="json"),
    )
    return result.output
