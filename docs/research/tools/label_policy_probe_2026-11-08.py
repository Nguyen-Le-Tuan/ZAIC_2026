"""Label-policy probe (CPU, stdlib only). Claude, 08/11/2026. Numbers quoted in docs/SYNTH_DATA_PLAN_2026-11-08.md.

Part A uses train labels only: how deterministic is the gold policy given catalog metadata (kind, x-ref, returns)?
Part B (optional) reads OUR OWN public run trace and counts behaviour only (empty searches, read loops, no-op
writes). It never uses or infers public labels. Never reads *_environment/.

Run from lifemate/:
  PYTHONPATH=. python3 ../docs/research/tools/label_policy_probe_2026-11-08.py \
      [--trace runs/e2e_public_q4b_all_phoft_trace.jsonl]
"""
from __future__ import annotations

import argparse
import collections
import json

from lifemate.data import catalog_tools, load_catalog, load_split

C = collections.Counter


def atoms(x, out: set) -> set:
    """Scalar values that could carry information from a tool result into a later call."""
    if isinstance(x, dict):
        for v in x.values():
            atoms(v, out)
    elif isinstance(x, list):
        for v in x:
            atoms(v, out)
    elif isinstance(x, bool) or x is None:
        pass
    elif isinstance(x, (int, float)):
        out.add(str(x))
    elif isinstance(x, str) and len(x) >= 2:
        out.add(x)
    return out


def list_fields(r) -> list:
    return [v for v in r.values() if isinstance(v, list)] if isinstance(r, dict) else []


def part_a() -> None:
    tools = catalog_tools(load_catalog("train"))
    samples = load_split("train")

    # x-ref collection -> read tools whose `returns` names it
    ret = collections.defaultdict(list)
    for n, t in tools.items():
        if t["kind"] == "read" and t.get("returns"):
            app = n.split(".")[0]
            for part in str(t["returns"]).replace(",", " ").split():
                col = part.strip("[]{}").split(".")[0]
                if col:
                    ret[f"{app}.{col}"].append(n)
    xref_cols = {v["x-ref"] for t in tools.values() for v in t.get("parameters", {}).get("properties", {}).values()
                 if "x-ref" in v}
    print("== A. Train labels ==")
    print(f"x-ref collections: {len(xref_cols)}; exactly one read tool returns it: "
          f"{sum(len(ret.get(c, [])) == 1 for c in xref_cols)}; none: {sum(not ret.get(c) for c in xref_cols)}")

    src, canon, read_use, read_next, read_args, w_args = C(), C(), C(), C(), C(), C()
    opt_fill, opt_slots, empty, empty_next, contacts = C(), C(), C(), C(), C()
    for s in samples:
        calls, res = s["label"]["tool_calls"], s["label"]["tool_results"]
        hist = set()
        for h in s.get("history", []):
            if h["role"] != "user":
                atoms(h.get("tool_results") or [], hist)
                atoms(h.get("tool_calls") or [], hist)
        for i, (c, r) in enumerate(zip(calls, res)):
            t = tools.get(c["name"], {})
            kind = t.get("kind", "meta")
            args = c.get("arguments") or {}
            req = set(t.get("parameters", {}).get("required", []))
            props = set(t.get("parameters", {}).get("properties", {}))
            if kind in ("read", "write"):
                tag = "exactly required" if set(args) == req else "required + optional"
                (read_args if kind == "read" else w_args)[tag] += 1
                opt_slots[kind] += len(props - req)
                opt_fill[kind] += len(set(args) & (props - req))
            nxt = calls[i + 1]["name"] if i + 1 < len(calls) else None
            if kind == "read":
                later = set()
                for c2 in calls[i + 1:]:
                    atoms(c2.get("arguments") or {}, later)
                if atoms(r, set()) & later:
                    read_use["result used later"] += 1
                elif nxt is None:
                    read_use["last call"] += 1
                else:
                    read_use["not used later"] += 1
                    read_next["ask" if nxt == "sys.ask_missing_info" else tools.get(nxt, {}).get("kind", "?")] += 1
                lists = list_fields(r)
                if lists:
                    empty[("with args" if args else "{}", "total")] += 1
                    if all(len(v) == 0 for v in lists):
                        empty[("with args" if args else "{}", "empty")] += 1
                        empty_next["ask" if nxt == "sys.ask_missing_info" else
                                   ("end" if nxt is None else tools.get(nxt, {}).get("kind", "?"))] += 1
                if c["name"] == "contacts.search" and lists:
                    n = len(lists[0])
                    b = "1" if n == 1 else (">=2" if n >= 2 else "0")
                    contacts[(b, "ask" if nxt == "sys.ask_missing_info" else ("end" if nxt is None else "other"))] += 1
            if kind == "write":
                for p, spec in t.get("parameters", {}).get("properties", {}).items():
                    if "x-ref" not in spec or p not in args:
                        continue
                    for val in (args[p] if isinstance(args[p], list) else [args[p]]):
                        sv = str(val)
                        prev = [j for j in range(i) if sv in atoms(res[j], set())]
                        if prev:
                            src["earlier call in turn"] += 1
                            canon["canonical read tool" if calls[prev[-1]]["name"] in ret.get(spec["x-ref"], [])
                                  else "other tool"] += 1
                        elif sv in hist:
                            src["history"] += 1
                        else:
                            src["no source"] += 1
    print("x-ref ID source in writes:", dict(src))
    print("  of those from an earlier call:", dict(canon))
    print("read args:", dict(read_args), "| write args:", dict(w_args))
    for k in ("read", "write"):
        print(f"  {k}: optional slots filled {opt_fill[k]}/{opt_slots[k]} = {100 * opt_fill[k] / max(1, opt_slots[k]):.1f}%")
    print("read result reused:", dict(read_use), "| unused read -> next call kind:", dict(read_next))
    for a in ("with args", "{}"):
        print(f"list-returning reads {a}: empty {empty[(a, 'empty')]}/{empty[(a, 'total')]}")
    print("after an empty gold read:", dict(empty_next))
    print("contacts.search results -> next:", dict(sorted(contacts.items())))


def part_b(trace_path: str) -> None:
    pt = catalog_tools(load_catalog("public_test"))
    tr = [json.loads(line) for line in open(trace_path, encoding="utf-8")]
    print(f"\n== B. Behaviour of our own run ({len(tr)} samples; no labels) ==")
    print("stop reasons:", dict(C(t["stop"] for t in tr)))
    empty, after, samples, nodone, loops = C(), C(), set(), C(), 0
    for t in tr:
        steps = t["steps"]
        if t["stop"] == "max_steps" and any("<tool_call>" in st["output"] and not st["calls"] and not st["errors"]
                                            for st in steps):
            loops += 1
        for si, st in enumerate(steps):
            res, calls = st.get("results", []), st["calls"]
            if len(res) != len(calls):
                continue
            for c, r in zip(calls, res):
                if isinstance(r, dict) and r.get("ok") is True and r.get("done") is False:
                    nodone[c["name"].split(".")[0]] += 1
                lists = list_fields(r)
                if pt.get(c["name"], {}).get("kind") == "read" and c.get("arguments") and lists \
                        and all(len(v) == 0 for v in lists):
                    empty[c["name"]] += 1
                    samples.add(t["id"])
                    nxt = [c2["name"] for st2 in steps[si + 1:] for c2 in st2["calls"]]
                    after["ask" if "sys.ask_missing_info" in nxt else
                          ("write" if any(pt.get(n, {}).get("kind") == "write" for n in nxt) else
                           ("read again" if nxt else "stop"))] += 1
    print(f"filtered reads returning empty: {sum(empty.values())} in {len(samples)} samples;", empty.most_common(8))
    print("after empty:", dict(after))
    print("max-step samples stuck re-issuing an answered read:", loops)
    print("no-op writes (ok but done=false) by app:", dict(nodone))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", help="our own run trace (optional)")
    a = ap.parse_args()
    part_a()
    if a.trace:
        part_b(a.trace)
