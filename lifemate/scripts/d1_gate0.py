"""Gate 0 of D1: does the catalog-only label policy (lifemate/d1_policy.py) reproduce the read calls of the train labels?

  cd lifemate && PYTHONPATH=. python3 scripts/d1_gate0.py [--show 15] [--json runs/d1_gate0.json]

CPU, stdlib only, train labels only (label.tool_calls and label.tool_results); never reads *_environment/.

Replay, per train sample: the scenario is what a generator would know before writing the label: the gold write calls,
the gold sys.ask_missing_info call, and the objects they refer to. The policy must add the reads that fetch the IDs.
A gold read is then one of:
  id-read    predicted by the policy for an ID of a write (tool and arguments must match the gold call);
  scenario   not an ID fetch: a condition, a question, or the look-up before a clarification. The generator decides
             these per scenario; here they are only checked for the "minimal arguments" convention.
Policy errors: `args` (right tool, other arguments), `tool` (gold fetched the ID with another tool), `over-read`
(the policy reads, gold has no read giving that ID), `reread-known` (gold reads an ID the policy took as known).

Rule written before the run (JOURNAL entry 118): samples whose gold uses one of the 6 apps held out in dev_lao
(splits/heldout_apps.json), share with no policy error: >= 80% go on with D1, < 60% stop D1.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

from lifemate.d1_policy import (QUERY_KEYS, atoms, call_key, canonical_readers, read_args, reader_index, xref_values)
from lifemate.data import catalog_tools, fuzzy_params, load_catalog, load_split
from lifemate.scorer import calls_match

C = collections.Counter
ASK = "sys.ask_missing_info"


def find_entity(results: list, value) -> dict | None:
    """The object with this id in the gold results (what the scenario targets)."""
    def walk(x):
        if isinstance(x, dict):
            if x.get("id") == value:
                return x
            for v in x.values():
                r = walk(v)
                if r is not None:
                    return r
        elif isinstance(x, list):
            for v in x:
                r = walk(v)
                if r is not None:
                    return r
        return None
    return walk(results)


def replay(s: dict, tools: dict, idx: dict, fuzzy: dict) -> dict:
    calls, res = s["label"]["tool_calls"], s["label"]["tool_results"]
    known = set()
    for h in s.get("history", []):
        if h["role"] != "user":
            atoms(h.get("tool_results") or [], known)
            atoms(h.get("tool_calls") or [], known)
    kind = [tools.get(c["name"], {}).get("kind", "meta") for c in calls]
    matched: dict[int, str] = {}       # gold read index -> how it was explained
    errors, id_reads, skipped, slot_from_gold = [], [], 0, 0
    for i, c in enumerate(calls):
        if kind[i] != "write":
            continue
        for path, col, v in xref_values(tools[c["name"]], c["arguments"]):
            sv = str(v)
            if sv in known:
                skipped += 1
                continue
            readers = canonical_readers(col, tools, idx)
            earlier = [j for j in range(i) if kind[j] == "read" and j not in matched]
            holds = [j for j in earlier if sv in atoms(res[j])]
            rec = {"col": col, "value": sv, "write": c["name"], "ok": False}
            if not readers:
                errors.append(("no-reader", c["name"], col))
                known.add(sv)
                continue
            tool = tools[readers[0]]
            entity = find_entity(res[:i], v) or find_entity(res, v)
            slots = None
            need = [k for k in tool["parameters"].get("required", []) if k not in QUERY_KEYS]
            if need:   # values only the scenario knows: taken from the gold call of that tool
                src = next((j for j in holds if calls[j]["name"] == tool["name"]), None)
                if src is not None:
                    slots = {k: calls[src]["arguments"][k] for k in need if k in calls[src]["arguments"]}
                    slot_from_gold += 1
            args = read_args(tool, entity, slots)
            pred = {"name": tool["name"], "arguments": args if args is not None else {}}
            rec["pred"] = pred
            hit = next((j for j in earlier if calls_match(pred, calls[j], fuzzy)), None) if args is not None else None
            if hit is not None:
                matched[hit] = "id-read"
                atoms(res[hit], known)
                rec["ok"] = True
            else:
                same = next((j for j in holds if calls[j]["name"] == tool["name"]), None)
                if same is not None:
                    errors.append(("args", json.dumps(pred, ensure_ascii=False), json.dumps(calls[same], ensure_ascii=False)))
                    matched[same] = "id-read(args)"
                    atoms(res[same], known)
                    rec["gold"] = calls[same]
                elif holds:
                    errors.append(("tool", tool["name"], calls[holds[-1]]["name"]))
                    matched[holds[-1]] = "id-read(tool)"
                    atoms(res[holds[-1]], known)
                    rec["gold"] = calls[holds[-1]]
                else:
                    errors.append(("over-read", json.dumps(pred, ensure_ascii=False), c["name"]))
            known.add(sv)
            rec["app"] = tool["name"].split(".")[0]
            id_reads.append(rec)
        atoms(res[i], known)
    # gold reads the policy did not predict
    ask = next((c for c in calls if c["name"] == ASK), None)
    ask_readers = set()
    if ask is not None:
        t = tools.get(ask["arguments"].get("tool_name", ""), {})
        for spec in t.get("parameters", {}).get("properties", {}).values():
            cols = [spec["x-ref"]] if "x-ref" in spec else ([spec["items"]["x-ref"]] if "x-ref" in spec.get("items", {}) else [])
            for col in cols:
                ask_readers.update(canonical_readers(col, tools, idx))
    later_ids = [(i, str(v)) for i, c in enumerate(calls) if kind[i] == "write"
                 for _, _, v in xref_values(tools[c["name"]], c["arguments"])]
    scenario = []
    for j, c in enumerate(calls):
        if kind[j] != "read" or j in matched:
            continue
        got = atoms(res[j])
        if any(i > j and v in got for i, v in later_ids):
            errors.append(("reread-known", json.dumps(c, ensure_ascii=False), ""))
            continue
        t = tools[c["name"]]
        minimal = set(c["arguments"]) <= set(t["parameters"].get("required", [])) | set(QUERY_KEYS)
        scenario.append({"name": c["name"], "args": c["arguments"], "minimal": minimal,
                         "role": "ask-lookup" if c["name"] in ask_readers else "condition/question"})
    return {"errors": errors, "id_reads": id_reads, "scenario": scenario, "skipped_known": skipped,
            "slot_from_gold": slot_from_gold, "n_reads": sum(k == "read" for k in kind),
            "apps": {c["name"].split(".")[0] for c in calls}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", type=int, default=12, help="examples of each error kind to print")
    ap.add_argument("--json")
    a = ap.parse_args()
    tools = catalog_tools(load_catalog("train"))
    fuzzy = fuzzy_params(load_catalog("train"))
    idx = reader_index(tools)
    held = set(json.loads(Path("splits/heldout_apps.json").read_text()))
    samples = load_split("train")
    out = {}
    rows = [(s, replay(s, tools, idx, fuzzy)) for s in samples]

    def report(name, sel):
        n = len(sel)
        ok = sum(not r["errors"] for _, r in sel)
        strict = sum(not r["errors"] and not r["scenario"] for _, r in sel)
        ids = [x for _, r in sel for x in r["id_reads"]]
        sc = [x for _, r in sel for x in r["scenario"]]
        err = C(e[0] for _, r in sel for e in r["errors"])
        reads = sum(r["n_reads"] for _, r in sel)
        print(f"\n== {name}: {n} samples, {reads} gold reads")
        print(f"  samples with no policy error: {ok}/{n} = {100 * ok / max(n, 1):.1f}%"
              f" | of which the policy explains every read: {strict}/{n} = {100 * strict / max(n, 1):.1f}%")
        print(f"  ID reads predicted: {len(ids)}, matching a gold call exactly: {sum(x['ok'] for x in ids)}"
              f" = {100 * sum(x['ok'] for x in ids) / max(len(ids), 1):.1f}% | IDs taken as known (no read): "
              f"{sum(r['skipped_known'] for _, r in sel)} | scenario slots copied from gold: {sum(r['slot_from_gold'] for _, r in sel)}")
        print(f"  policy errors: {dict(err)}")
        roles = C(x["role"] for x in sc)
        print(f"  scenario reads: {len(sc)} {dict(roles)}; minimal arguments: {sum(x['minimal'] for x in sc)}"
              f" = {100 * sum(x['minimal'] for x in sc) / max(len(sc), 1):.1f}%")
        out[name] = {"n": n, "no_policy_error": ok, "policy_explains_all_reads": strict, "id_reads": len(ids),
                     "id_reads_exact": sum(x["ok"] for x in ids), "errors": dict(err), "scenario_reads": len(sc),
                     "scenario_minimal": sum(x["minimal"] for x in sc), "gold_reads": reads}
        return ok / max(n, 1)

    report("all train", rows)
    report("gold uses no held-out app", [(s, r) for s, r in rows if not (r["apps"] & held)])
    share = report("gold uses a held-out app (dev_lao apps)", [(s, r) for s, r in rows if r["apps"] & held])
    # the same, counting only the calls of the held-out apps
    hid = [x for _, r in rows for x in r["id_reads"] if x["app"] in held]
    print(f"\nID reads done with a held-out app's tool: {len(hid)}, exact: {sum(x['ok'] for x in hid)}"
          f" = {100 * sum(x['ok'] for x in hid) / max(len(hid), 1):.1f}%")
    by = collections.defaultdict(C)
    for _, r in rows:
        for x in r["id_reads"]:
            by[x["pred"]["name"]]["ok" if x["ok"] else "miss"] += 1
    print("\nper predicted reader (ok / miss):")
    for n, v in sorted(by.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"  {n:38s} {v['ok']:4d} / {v['miss']:3d} {'HELD' if n.split('.')[0] in held else ''}")
    nonmin = C((x["name"], json.dumps(sorted(x["args"]))) for _, r in rows for x in r["scenario"] if not x["minimal"])
    print("\nscenario reads with extra optional arguments (top):", nonmin.most_common(15))
    for k in ("args", "tool", "over-read", "reread-known", "no-reader"):
        ex = [(s["id"], e) for s, r in rows for e in r["errors"] if e[0] == k]
        print(f"\n-- {k}: {len(ex)}")
        for sid, e in ex[:a.show]:
            print(f"   {sid}: {e[1]}  ||  {e[2]}")
    verdict = "GO" if share >= 0.80 else ("STOP" if share < 0.60 else "GREY")
    print(f"\nGATE 0: held-out-app samples with no policy error = {100 * share:.1f}% -> {verdict} (>= 80 go, < 60 stop)")
    out["gate"] = {"share": share, "verdict": verdict}
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
