"""Append-only audit trail for every agent run (top-level or delegated).

Writes to output/audit_trail.json as a growing JSON array — existing
entries are read back and kept, never wiped, each new run just appends.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic_ai.messages import (
    BaseToolCallPart,
    BaseToolReturnPart,
    ModelRequest,
    ModelResponse,
    RetryPromptPart,
    TextPart,
    ThinkingPart,
)
from pydantic_core import to_json

AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"
_PREVIEW_CHARS = 400

_lock = threading.Lock()


def _preview(value: Any) -> str:
    text = value if isinstance(value, str) else to_json(value).decode("utf-8", "replace")
    text = " ".join(text.split())
    return text if len(text) <= _PREVIEW_CHARS else text[: _PREVIEW_CHARS - 1] + "…"


def summarize_steps(messages: list[Any]) -> tuple[list[dict[str, Any]], str | None]:
    """Turn one agent run's messages into a step-by-step list: thoughts,
    text, and each tool call paired with its result (includes `delegate`
    calls and every MCP tool call)."""
    steps: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    finish_reason: str | None = None

    for message in messages:
        if isinstance(message, ModelResponse):
            finish_reason = message.finish_reason
            for part in message.parts:
                if isinstance(part, ThinkingPart) and part.content:
                    steps.append({"type": "thought", "content": part.content})
                elif isinstance(part, TextPart) and part.content:
                    steps.append({"type": "text", "content": part.content})
                elif isinstance(part, BaseToolCallPart):
                    entry = {
                        "type": "tool_call",
                        "tool": part.tool_name,
                        "args": part.args_as_dict(),
                        "result": None,
                    }
                    steps.append(entry)
                    by_id[part.tool_call_id] = entry
        elif isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, (BaseToolReturnPart, RetryPromptPart)):
                    entry = by_id.get(part.tool_call_id)
                    if entry is not None:
                        entry["result"] = _preview(part.content)

    return steps, finish_reason


def append_run(
    *,
    agent: str,
    delegation_trail: list[str],
    delegation_depth: int,
    input_message: str,
    messages: list[Any],
    output: dict[str, Any],
) -> None:
    """Append one audit entry for a completed agent run (append-only —
    reads the existing file, adds this entry, writes it back)."""
    steps, finish_reason = summarize_steps(messages)
    entry = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "agent": agent,
        "delegation_trail": delegation_trail,
        "delegation_depth": delegation_depth,
        "input": input_message,
        "steps": steps,
        "output": output,
        "stopped": f"finish_reason={finish_reason or 'stop'}",
    }
    with _lock:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        rows: list[Any] = []
        if AUDIT_PATH.exists() and AUDIT_PATH.stat().st_size > 0:
            try:
                loaded = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
                rows = loaded if isinstance(loaded, list) else [loaded]
            except json.JSONDecodeError:
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                AUDIT_PATH.replace(AUDIT_PATH.with_name(f"audit_trail.corrupt-{stamp}.json"))
        rows.append(entry)
        tmp = AUDIT_PATH.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(rows, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        tmp.replace(AUDIT_PATH)
