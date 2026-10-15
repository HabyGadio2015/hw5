"""Shared run-time state threaded through every agent run in a delegation chain."""

from __future__ import annotations

from dataclasses import dataclass, field

from models import AgentRole

# Caps how many hops a single delegation chain can take (BOSS -> INVENTORY ->
# ACCOUNTING -> ...) before an agent is told to stop delegating and answer
# with what it already knows. Full connectivity between 5 agents can
# otherwise spiral into a long, expensive chain of model calls.
MAX_DELEGATION_DEPTH = 3


@dataclass
class TeamDeps:
    """Deps for every agent run: who's currently answering, and how deep
    the current delegation chain already is."""

    current_role: AgentRole
    delegation_depth: int = 0
    delegation_trail: list[str] = field(default_factory=list)
