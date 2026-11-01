"""Would an ID-provenance guard help? Measured on existing runs: CPU only, no model, train data only.

Rule (fixed from the catalog before looking at dev): a WRITE call is blocked when a parameter whose schema has
`x-ref` (an ID that has to come from a tool result) holds a value that appears nowhere in what the model has been
shown so far in the sample: system prompt (user context, tool list), history (user turns, assistant calls, tool
results, replies), the user turn, and tool results returned earlier in this turn. The model's own calls in this
turn do not count, so an ID it invented in an earlier step does not become "seen".

1. gold check on fit ids (train minus dev_random and dev_lao): how often would the rule block a GOLD write call?
2. per run: replay the run's executed calls on fresh ToolEnvs (checked against its submission), list the write
   calls the rule would block and whether they match a gold call, sort every wrong write call by cause, and
   score two static counterfactuals per flagged sample:
     drop - the blocked calls are removed and the rest replayed
     ask  - calls before the first blocked call are kept, then sys.ask_missing_info(tool, [params]) and stop
   Neither is what the model would do after a block message (that needs a GPU rerun); they size the effect.

  .venv/bin/python scripts/id_guard_check.py --run runs/sft_q17b_fit_random --run runs/sft_q17b_fit_lao \
      --json runs/id_guard_check.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate.data import DEFAULT_ROOT, catalog_tools, fuzzy_params, load_catalog, load_jsonl, load_split, zaic_tools  # noqa: E402
from lifemate.guard import guarded_values, seen  # noqa: E402
from lifemate.prompt import build_messages, render_results  # noqa: E402
from lifemate.runinfo import read_ids, refuse_existing, write_json  # noqa: E402
from lifemate.scorer import calls_match, category, score_sample  # noqa: E402

SPLITS = Path(__file__).resolve().parents[1] / "splits"


def source_of(value, parts: dict[str, str]) -> str:
    for name in ("turn_results", "history", "user", "system"):
        if seen(value, parts[name]):
            return name
    return "unseen"


def prompt_parts(item, tools, apps) -> dict[str, str]:
    """The prompt the model gets (oracle text), split by source."""
    hist = [h["audio_text"] for h in item.get("history", []) if h["role"] == "user"]
    msgs = build_messages(item, item["audio_text"], hist, tools, apps)
    return {"system": msgs[0]["content"], "history": "\n".join(m["content"] for m in msgs[1:-1]),
            "user": msgs[-1]["content"], "turn_results": ""}


def replay(zt, root, sid, calls):
    env = zt.ToolEnv("train", sid, root=str(root))
    for c in calls:
        env.call(c["name"], c["arguments"])
    return env.get_tool_calls(), env.get_state_hash()


def gold_check(zt, root, items, ids, tools, apps) -> dict:
    """Where the x-ref values of gold write calls come from, replaying gold call by call (lenient: in a real
    run calls of one step do not see each other's results)."""
    src, blocked = Counter(), []
    for s in items:
        if s["id"] not in ids:
            continue
        parts = prompt_parts(s, tools, apps)
        env = zt.ToolEnv("train", s["id"], root=str(root))
        for c in s["label"]["tool_calls"]:
            t = tools.get(c["name"], {})
            if t.get("kind") == "write":
                for k, v in guarded_values(t, c["arguments"]):
                    where = source_of(v, parts)
                    src[where] += 1
                    if where == "unseen":
                        blocked.append({"id": s["id"], "tool": c["name"], "param": k})
            parts["turn_results"] += "\n" + render_results([env.call(c["name"], c["arguments"])])
    n = sum(src.values())
    return {"n_samples": len(ids), "n_values": n, "sources": dict(src),
            "false_block_rate": round(src["unseen"] / max(n, 1), 4), "blocked_gold": blocked}


def wrong_kind(c, unseen, srcs, gold_calls, tools) -> str:
    """Why a write call matches no gold call."""
    same = [g for g in gold_calls if g["name"] == c["name"]]
    if not same:
        return "tool_not_in_gold"
    if not srcs:
        return "no_id_param_wrong"
    mine = sorted(str(v) for _, v in guarded_values(tools[c["name"]], c["arguments"]))
    if any(sorted(str(v) for _, v in guarded_values(tools[g["name"]], g["arguments"])) == mine for g in same):
        return "id_right_other_param_wrong"
    return "id_wrong:" + "+".join(sorted(set(srcs)))


def wrong_id_params(c, gold_calls, tools) -> list[str]:
    """x-ref params whose value differs from the closest gold call of the same tool."""
    tool = tools[c["name"]]
    mine = {k: str(v) for k, v in guarded_values(tool, c["arguments"])}
    same = [g for g in gold_calls if g["name"] == c["name"]]
    best = max(same, key=lambda g: sum(mine.get(k) == str(v) for k, v in guarded_values(tool, g["arguments"])))
    theirs = {k: str(v) for k, v in guarded_values(tool, best["arguments"])}
    return [f"{c['name']}.{k}" for k in mine if theirs.get(k) != mine[k]]


def analyse_run(zt, root, run, items, tools, apps, fuzzy) -> dict:
    preds = {r["id"]: r for r in load_jsonl(f"{run}.jsonl")}
    res = {"n": 0, "replay_mismatch": 0, "flag_samples": 0, "flag_calls": 0, "flag_calls_gold": 0,
           "unseen_id_reads": 0, "writes": Counter(), "wrong_by_cause": Counter(), "wrong_id_params": Counter(),
           "orig": 0.0, "drop": 0.0, "ask": 0.0, "drop_better": 0, "drop_worse": 0, "ask_better": 0, "ask_worse": 0}
    by_cat, cases, wrong_id_samples = {}, [], set()
    for t in load_jsonl(f"{run}_trace.jsonl"):
        sid, item = t["id"], items[t["id"]]
        if t["text"] != item["audio_text"]:
            sys.exit(f"{run}: {sid} was not run on audio_text; this check assumes oracle text")
        gold_calls = item["label"]["tool_calls"]
        _, gold_hash = replay(zt, root, sid, gold_calls)
        parts = prompt_parts(item, tools, apps)
        env = zt.ToolEnv("train", sid, root=str(root))
        executed = []  # (call, unseen x-ref values, sources of its x-ref values) in execution order
        for step in t["steps"]:
            visible = "\n".join(parts.values())  # what the model had seen before generating this step
            replayed = []
            for c in step["calls"]:  # validated and executed calls only, in order
                tool = tools.get(c["name"], {})
                vals = guarded_values(tool, c["arguments"])
                unseen = [(k, v) for k, v in vals if not seen(v, visible)]
                if tool.get("kind") == "write":
                    executed.append((c, unseen, [source_of(v, parts) for _, v in vals]))
                else:
                    executed.append((c, [], []))
                    res["unseen_id_reads"] += bool(unseen)
                replayed.append(env.call(c["name"], c["arguments"]))
            parts["turn_results"] += "\n" + render_results(step.get("results", replayed))
        p = preds[sid]
        if env.get_tool_calls() != p["tool_calls"] or env.get_state_hash() != p["state_hash"]:
            res["replay_mismatch"] += 1
        cat = category(gold_calls)
        orig = score_sample(p["tool_calls"], p["state_hash"], gold_calls, gold_hash, fuzzy)
        for c, unseen, srcs in executed:
            if tools.get(c["name"], {}).get("kind") != "write":
                continue
            right = any(calls_match(c, g, fuzzy) for g in gold_calls)
            res["writes"]["right" if right else "wrong"] += 1
            if not right:
                kind = wrong_kind(c, unseen, srcs, gold_calls, tools)
                res["wrong_by_cause"][f"{cat}|{kind}"] += 1
                if kind.startswith("id_wrong"):
                    wrong_id_samples.add(sid)
                    res["wrong_id_params"].update(wrong_id_params(c, gold_calls, tools))
        drop = ask = orig
        flags = [(i, c, u) for i, (c, u, _) in enumerate(executed) if u]
        if flags:
            drop = score_sample(*replay(zt, root, sid, [c for c, u, _ in executed if not u]),
                                gold_calls, gold_hash, fuzzy)
            i0, c0, u0 = flags[0]
            ask_call = {"name": "sys.ask_missing_info",
                        "arguments": {"tool_name": c0["name"], "params": sorted({k for k, _ in u0})}}
            ask = score_sample(*replay(zt, root, sid, [c for c, _, _ in executed[:i0]] + [ask_call]),
                               gold_calls, gold_hash, fuzzy)
            hits = sum(any(calls_match(c, g, fuzzy) for g in gold_calls) for _, c, _ in flags)
            res["flag_samples"] += 1
            res["flag_calls"] += len(flags)
            res["flag_calls_gold"] += hits
            for k, v in (("drop", drop), ("ask", ask)):
                res[f"{k}_better"] += v > orig + 1e-9
                res[f"{k}_worse"] += v < orig - 1e-9
            cases.append({"id": sid, "category": cat, "orig": round(orig, 3), "drop": round(drop, 3),
                          "ask": round(ask, 3), "flagged_right_calls": hits,
                          "flagged": [{"tool": c["name"], "params": sorted({k for k, _ in u})} for _, c, u in flags]})
        res["n"] += 1
        b = by_cat.setdefault(cat, Counter())
        b["n"] += 1
        b["flag_samples"] += bool(flags)
        for k, v in (("orig", orig), ("drop", drop), ("ask", ask)):
            res[k] += v
            b[k] += v
    n = max(res["n"], 1)
    for k in ("orig", "drop", "ask"):
        res[k] = round(100 * res[k] / n, 2)
    res["writes"] = dict(res["writes"])
    res["wrong_by_cause"] = dict(sorted(res["wrong_by_cause"].items()))
    res["wrong_id_samples"] = len(wrong_id_samples)
    res["wrong_id_params"] = dict(res["wrong_id_params"].most_common())
    res["by_category"] = {c: {"n": v["n"], "flag_samples": v["flag_samples"],
                              **{k: round(100 * v[k] / v["n"], 2) for k in ("orig", "drop", "ask")}}
                          for c, v in sorted(by_cat.items())}
    res["cases"] = cases
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--splits", default=str(SPLITS), help="dir with dev_random.txt and dev_lao.txt")
    ap.add_argument("--run", action="append", required=True,
                    help="run prefix, e.g. runs/sft_q17b_fit_lao (needs <run>.jsonl and <run>_trace.jsonl)")
    ap.add_argument("--json", required=True)
    a = ap.parse_args()
    refuse_existing(a.json)
    root = Path(a.root)
    zt = zaic_tools("train", root)
    cat = load_catalog("train", root)
    tools, apps, fuzzy = catalog_tools(cat), {x["id"]: x for x in cat["apps"]}, fuzzy_params(cat)
    items_list = load_split("train", root)
    items = {s["id"]: s for s in items_list}
    dev = set(read_ids(Path(a.splits) / "dev_random.txt")) | set(read_ids(Path(a.splits) / "dev_lao.txt"))
    out = {"rule": "block a write call whose x-ref value is not in system/history/user/earlier tool results",
           "gold_check_fit": gold_check(zt, root, items_list, set(items) - dev, tools, apps), "runs": {}}
    g = out["gold_check_fit"]
    print(f"gold, fit ids: {g['n_values']} x-ref values in {g['n_samples']} samples, sources {g['sources']}")
    for r in a.run:
        res = analyse_run(zt, root, r, items, tools, apps, fuzzy)
        out["runs"][Path(r).name] = res
        print(Path(r).name, json.dumps({k: res[k] for k in ("n", "replay_mismatch", "flag_samples", "flag_calls",
                                                            "flag_calls_gold", "orig", "drop", "ask")}))
    write_json(a.json, out)


if __name__ == "__main__":
    main()
