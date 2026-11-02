"""ID guard: a write call may only use an ID the model has been shown.

Rule (fixed from the catalog before looking at dev; measured in docs/ID_GUARD_2026-10-30.md): a WRITE call is blocked
when a parameter whose schema has `x-ref` (an ID that has to come from a tool result) holds a value that appears nowhere
in what the model has been shown so far in the sample: system prompt (user context, tool list), history, the user turn,
and the tool results returned earlier in this turn. The model's own calls do not count, so an ID it invented in an
earlier step does not become "seen". The rule only reads `x-ref` from the catalog, so it also covers unseen apps.

Used by the agent loop (lifemate.agent) and by the offline analysis (scripts/id_guard_check.py).
"""
from __future__ import annotations

import re


def _is_id(x) -> bool:
    return isinstance(x, (str, int)) and not isinstance(x, bool)


def _vals(name: str, spec: dict, v) -> list[tuple[str, object]]:
    if "x-ref" in spec:
        return [(name, x) for x in (v if isinstance(v, list) else [v]) if _is_id(x)]
    if spec.get("type") == "array" and isinstance(v, list):
        it = spec.get("items", {})
        if "x-ref" in it:
            return [(name, x) for x in v if _is_id(x)]
        if it.get("type") == "object":
            return [(name, val) for x in v if isinstance(x, dict)
                    for k2, s2 in it.get("properties", {}).items() if k2 in x for _, val in _vals(k2, s2, x[k2])]
    if spec.get("type") == "object" and isinstance(v, dict):
        return [(name, val) for k2, s2 in spec.get("properties", {}).items() if k2 in v for _, val in _vals(k2, s2, v[k2])]
    return []


def guarded_values(tool: dict, args: dict) -> list[tuple[str, object]]:
    """[(top-level param name, value)] for every x-ref value of a call."""
    props = tool.get("parameters", {}).get("properties", {})
    return [kv for k, spec in props.items() if k in args for kv in _vals(k, spec, args[k])]


def seen(value, text: str) -> bool:
    s = str(value)
    return bool(s) and re.search(r"(?<!\w)" + re.escape(s) + r"(?!\w)", text) is not None


def unseen_ids(tool: dict, args: dict, visible: str) -> list[tuple[str, object]]:
    """x-ref values of a WRITE call that are not in `visible`; [] for reads and for calls that pass."""
    if tool.get("kind") != "write":
        return []
    return [(k, v) for k, v in guarded_values(tool, args) if not seen(v, visible)]


def block_message(unseen: list[tuple[str, object]]) -> str:
    """Error shown to the model, in the style of ToolEnv.validate errors."""
    vals = ", ".join(f"{k}={v}" for k, v in unseen)
    return f"ID chưa có trong lịch sử hay kết quả tool: {vals}. Không bịa ID: lấy ID từ kết quả tool hoặc từ lịch sử hội thoại."
