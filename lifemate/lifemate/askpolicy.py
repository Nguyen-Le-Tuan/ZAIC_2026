"""What the gold labels do around sys.ask_missing_info, as reusable functions (analysis and data generation only;
the agent never imports this).

Ask types observed on fit (184 asks in fit_random, always exactly one param, always the last call):
  A  a lookup by name returns >=2 entities with exactly that name and the request does not single one out
     (e.g. two contacts called "Lan") -> ask for the id
  B  any other ask for an x-ref id: vague pick out of a listed collection ("cancel one order") or from history
  C  ask for a plain (non x-ref) slot the request does not give (amount, time, start, steps, ...)
"""
from __future__ import annotations

import re
import unicodedata

NAME_KEYS = ("name", "title", "full_name", "display_name")
QUERY_KEYS = ("query", "name", "keyword")
SKIP_ATTR_KEYS = set(NAME_KEYS) | {"id", "phone", "email", "phone_number"}
ASK = "sys.ask_missing_info"


def norm(s, strip_accents: bool = False) -> str:
    s = unicodedata.normalize("NFC", str(s)).lower().strip()
    if strip_accents:
        s = "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn").replace("đ", "d")
    return " ".join(s.split())


def words(s) -> set[str]:
    return {w for w in re.split(r"[^\w]+", norm(s)) if len(w) >= 2}


def entities(result) -> list[dict]:
    """First list of dict entities in a tool result (contacts, orders, chats, ...)."""
    if isinstance(result, dict):
        for v in result.values():
            if isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
                return v
    return []


def ent_name(e: dict):
    return next((e[k] for k in NAME_KEYS if k in e), None)


def _attr_words(e: dict) -> set[str]:
    return set().union(*[words(v) for k, v in e.items() if k not in SKIP_ATTR_KEYS and isinstance(v, str)] or [set()])


def ambiguous_ids(call: dict, result, user_text: str) -> list[str]:
    """Ask type A trigger. For a lookup with a free-text query: ids of the >=2 entities whose name equals the query
    (accent-insensitive), unless exactly one of them is singled out by a word of its other attributes (relation,
    ...) that appears in the request and in none of the others (e.g. "anh Quân bên kho" vs relation "bộ phận kho").
    Returns [] when the lookup is not ambiguous."""
    q = next((v for k, v in (call.get("arguments") or {}).items() if k in QUERY_KEYS and isinstance(v, str)), None)
    if not q:
        return []
    same = [e for e in entities(result) if ent_name(e) is not None and norm(ent_name(e), True) == norm(q, True)]
    if len(same) < 2:
        return []
    text = words(user_text)
    attrs = [_attr_words(e) for e in same]
    singled = [e for i, e in enumerate(same)
               if (attrs[i] - set().union(*[a for j, a in enumerate(attrs) if j != i])) & text]
    if len(singled) == 1:
        return []
    return [str(e.get("id")) for e in same]


def params_spec(tool: dict) -> dict:
    return (tool.get("parameters") or {}).get("properties", {})


def required(tool: dict) -> list[str]:
    return list((tool.get("parameters") or {}).get("required", []))


def is_xref(tool: dict, param: str) -> bool:
    return "x-ref" in params_spec(tool).get(param, {})


def is_ask_sample(s: dict) -> bool:
    calls = s["label"]["tool_calls"]
    return bool(calls) and calls[-1]["name"] == ASK


def ask_type(s: dict, tools: dict) -> str | None:
    """'A' / 'B' / 'C' for a gold ask sample, None otherwise."""
    if not is_ask_sample(s):
        return None
    calls, results = s["label"]["tool_calls"], s["label"]["tool_results"]
    if any(ambiguous_ids(c, r, s["audio_text"]) for c, r in zip(calls, results)):
        return "A"
    a = calls[-1]["arguments"]
    return "B" if is_xref(tools.get(a["tool_name"], {}), a["params"][0]) else "C"


def attested_plain_params(samples, tools) -> set[str]:
    """Plain (non x-ref) params that gold actually asks for in these samples: only these get counterfactual asks,
    since the policy for other missing slots (content, title, ...) is not attested."""
    out = set()
    for s in samples:
        if ask_type(s, tools) == "C":
            out.add(s["label"]["tool_calls"][-1]["arguments"]["params"][0])
    return out
