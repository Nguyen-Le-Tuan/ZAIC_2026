"""Why are wrong write calls wrong? Split by parameter type, and size each type with an oracle fix.

CPU only, no model, train data only. For every sample of a finished run:
  1. predicted write calls that match a gold call are set aside (scorer rules: exact, fuzzy token-F1 > 0.6);
  2. each remaining predicted write call is paired with the closest remaining gold write call of the same tool
     (most equal arguments); the arguments that differ are classified by their schema type:
       id (x-ref), datetime, number, enum, bool, fuzzy_text, phone, text_exact, array,
       extra_arg (an optional argument the gold call does not have), missing_arg;
  3. a predicted write with no gold write of that tool left is "wrong_tool"; a gold write left over is
     "missing_write" (never made, e.g. asked or stopped instead).
Oracle fix for a cause C: correct only the C errors with the gold values (set the argument, drop the extra
argument, add the missing one, drop the wrong-tool call, append the missing write), replay the whole call list on
a fresh ToolEnv and score. The gain is what fixing C perfectly would be worth with everything else unchanged.
Datetime, number, enum and fuzzy-text differences get a finer split.

  .venv/bin/python scripts/param_errors.py --run runs/sft_q17b_fit_random --run runs/sft_q17b_fit_lao \
      --json runs/param_errors.json
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from datetime import datetime, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate.data import DEFAULT_ROOT, catalog_tools, fuzzy_params, load_catalog, load_jsonl, load_split, zaic_tools  # noqa: E402
from lifemate.runinfo import refuse_existing, write_json  # noqa: E402
from lifemate.scorer import calls_match, category, score_sample, token_f1  # noqa: E402

PARAM_TYPES = ["id", "datetime", "number", "enum", "bool", "fuzzy_text", "phone", "text_exact", "array",
               "extra_arg", "missing_arg"]
CAUSES = PARAM_TYPES + ["wrong_tool", "missing_write"]


def ptype(name: str, spec: dict) -> str:
    if "x-ref" in spec:
        return "id"
    if "enum" in spec:
        return "enum"
    t = spec.get("type")
    if t == "string":
        d = spec.get("description", "")
        if spec.get("format") in ("date-time", "date", "time") or "ISO" in d:
            return "datetime"
        if spec.get("x-match") == "fuzzy":
            return "fuzzy_text"
        if "phone" in name or "điện thoại" in d.lower():
            return "phone"
        return "text_exact"
    if t in ("integer", "number"):
        return "number"
    if t == "boolean":
        return "bool"
    if t == "array":
        it = spec.get("items", {})
        return "id" if "x-ref" in it else "enum" if "enum" in it else "array"
    return "other"


def arg_equal(tool_name: str, k: str, a, b, fuzzy) -> bool:
    if k in fuzzy.get(tool_name, set()) and isinstance(a, str) and isinstance(b, str):
        return token_f1(a, b) > 0.6
    return a == b


def diffs(p: dict, g: dict, tool: dict, fuzzy) -> list[tuple[str, str]]:
    """[(argument, cause)] where the predicted call differs from the gold call of the same tool."""
    props = tool.get("parameters", {}).get("properties", {})
    pa, ga = p.get("arguments") or {}, g.get("arguments") or {}
    out = []
    for k in sorted(set(pa) | set(ga)):
        if k not in ga:
            out.append((k, "extra_arg"))
        elif k not in pa:
            out.append((k, "missing_arg"))
        elif not arg_equal(g["name"], k, pa[k], ga[k], fuzzy):
            out.append((k, ptype(k, props.get(k, {}))))
    return out


def n_equal(p, g, fuzzy) -> int:
    pa, ga = p.get("arguments") or {}, g.get("arguments") or {}
    return sum(k in ga and arg_equal(g["name"], k, pa[k], ga[k], fuzzy) for k in pa)


def pair_writes(pred_w, gold_w, fuzzy):
    """pred_w, gold_w: lists of calls. -> (pairs [(i, j)], wrong_tool [i], missing [j])."""
    left = list(range(len(gold_w)))
    wrong = []
    for i, p in enumerate(pred_w):
        j = next((j for j in left if calls_match(p, gold_w[j], fuzzy)), None)
        if j is None:
            wrong.append(i)
        else:
            left.remove(j)
    pairs, wrong_tool = [], []
    for i in wrong:
        cands = [j for j in left if gold_w[j]["name"] == pred_w[i]["name"]]
        if not cands:
            wrong_tool.append(i)
            continue
        j = max(cands, key=lambda j: n_equal(pred_w[i], gold_w[j], fuzzy))
        left.remove(j)
        pairs.append((i, j))
    return pairs, wrong_tool, left


def _parse(s):
    if not isinstance(s, str):
        return None
    for f in (datetime.fromisoformat, time.fromisoformat):
        try:
            return f(s)
        except ValueError:
            pass
    return None


def datetime_kind(p, g) -> tuple[str, str | None]:
    a, b = _parse(p), _parse(g)
    if a is None or b is None or type(a) is not type(b):
        return "unparsable_or_mixed", None
    if isinstance(a, time):
        mins = (a.hour * 60 + a.minute) - (b.hour * 60 + b.minute)
        return ("format" if mins == 0 else "time_of_day"), (f"{mins:+d} min" if mins else None)
    if (a.utcoffset() is None) != (b.utcoffset() is None) or (a.utcoffset() and a.utcoffset() != b.utcoffset()):
        return "timezone", None
    a, b = a.replace(tzinfo=None), b.replace(tzinfo=None)
    if a == b:
        return "format", None
    if a.date() == b.date():
        return "time_of_day", f"{round((a - b).total_seconds() / 60):+d} min"
    if a.time() == b.time():
        return "date", f"{(a.date() - b.date()).days:+d} d"
    return "date_and_time", f"{(a - b).total_seconds() / 3600:+.1f} h"


def number_kind(p, g) -> str:
    if not isinstance(p, (int, float)) or not isinstance(g, (int, float)) or isinstance(p, bool):
        return "not_a_number"
    if g and p == g * 1000:
        return "x1000"
    if p and g == p * 1000:
        return "/1000"
    return "off_by_le_60" if abs(p - g) <= 60 else "other"


def fixed_calls(calls, write_pos, gold_w, pairs, wrong_tool, missing, cause_set, tools, fuzzy):
    """The run's call list with the errors of the given causes corrected from gold."""
    out = copy.deepcopy(calls)
    drop = set()
    for i, j in pairs:
        p, g = out[write_pos[i]], gold_w[j]
        for k, c in diffs(p, g, tools[g["name"]], fuzzy):
            if c not in cause_set:
                continue
            if c == "extra_arg":
                del p["arguments"][k]
            else:
                p["arguments"][k] = copy.deepcopy(g["arguments"][k])
    if "wrong_tool" in cause_set:
        drop = {write_pos[i] for i in wrong_tool}
    out = [c for n, c in enumerate(out) if n not in drop]
    if "missing_write" in cause_set:
        out += [copy.deepcopy(gold_w[j]) for j in missing]
    return out


def replay(zt, root, sid, calls):
    env = zt.ToolEnv("train", sid, root=str(root))
    for c in calls:
        env.call(c["name"], c["arguments"])
    return env.get_tool_calls(), env.get_state_hash()


def analyse_run(zt, root, run, items, tools, fuzzy, n_examples: int = 6) -> dict:
    preds = load_jsonl(f"{run}.jsonl")
    trace_path = Path(f"{run}_trace.jsonl")
    stops = {t["id"]: t["stop"] for t in load_jsonl(trace_path)} if trace_path.exists() else {}
    missing_why = Counter()       # samples with a missing write: did the run ask, or stop for another reason?
    calls_by = Counter()          # wrong write calls with at least one error of this cause
    args_by = Counter()           # differing arguments by type
    where = {c: Counter() for c in CAUSES}
    detail = {"datetime": Counter(), "datetime_delta": Counter(), "number": Counter(), "enum": Counter(),
              "fuzzy_text_f1": Counter()}
    examples = {c: [] for c in CAUSES}
    gain = {c: Counter() for c in CAUSES + ["all_params", "all"]}
    writes, replay_mismatch, n_by_cat = Counter(), 0, Counter()
    for r in preds:
        sid, item = r["id"], items[r["id"]]
        gold = item["label"]["tool_calls"]
        cat = category(gold)
        n_by_cat[cat] += 1
        _, gold_hash = replay(zt, root, sid, gold)
        calls = r["tool_calls"]
        if replay(zt, root, sid, calls)[1] != r["state_hash"]:
            replay_mismatch += 1
        orig = score_sample(calls, r["state_hash"], gold, gold_hash, fuzzy)
        write_pos = [n for n, c in enumerate(calls) if tools.get(c["name"], {}).get("kind") == "write"]
        pred_w = [calls[n] for n in write_pos]
        gold_w = [c for c in gold if tools.get(c["name"], {}).get("kind") == "write"]
        pairs, wrong_tool, missing = pair_writes(pred_w, gold_w, fuzzy)
        writes["right"] += len(pred_w) - len(pairs) - len(wrong_tool)
        writes["wrong"] += len(pairs) + len(wrong_tool)
        for i, j in pairs:
            p, g = pred_w[i], gold_w[j]
            ds = diffs(p, g, tools[g["name"]], fuzzy)
            for c in {c for _, c in ds}:
                calls_by[c] += 1
            for k, c in ds:
                args_by[c] += 1
                where[c][f"{g['name']}.{k}"] += 1
                pv, gv = (p["arguments"] or {}).get(k), (g["arguments"] or {}).get(k)
                if len(examples[c]) < n_examples:
                    examples[c].append({"id": sid, "call": f"{g['name']}.{k}", "pred": pv, "gold": gv})
                if c == "datetime":
                    kind, delta = datetime_kind(pv, gv)
                    detail["datetime"][kind] += 1
                    if delta:
                        detail["datetime_delta"][delta] += 1
                elif c == "number":
                    detail["number"][number_kind(pv, gv)] += 1
                elif c == "enum":
                    detail["enum"][f"{k}: {pv} -> {gv}"] += 1
                elif c == "fuzzy_text":
                    f1 = token_f1(pv, gv) if isinstance(pv, str) and isinstance(gv, str) else 0.0
                    detail["fuzzy_text_f1"]["<0.3" if f1 < 0.3 else "0.3-0.6"] += 1
        for i in wrong_tool:
            calls_by["wrong_tool"] += 1
            where["wrong_tool"][f"{cat}|{pred_w[i]['name']}"] += 1
        for j in missing:
            calls_by["missing_write"] += 1
            where["missing_write"][f"{cat}|{gold_w[j]['name']}"] += 1
        if missing:
            asked = any(c["name"] == "sys.ask_missing_info" for c in calls)
            missing_why[f"{cat}|" + ("asked" if asked else f"stop={stops.get(sid, '?')}")] += 1
        fixes = {c: {c} for c in CAUSES}
        fixes["all_params"] = set(PARAM_TYPES)
        fixes["all"] = set(CAUSES)
        for name, cause_set in fixes.items():
            new = orig
            if pairs or wrong_tool or missing:
                fc = fixed_calls(calls, write_pos, gold_w, pairs, wrong_tool, missing, cause_set, tools, fuzzy)
                new = score_sample(*replay(zt, root, sid, fc), gold, gold_hash, fuzzy)
            gain[name][cat] += new - orig
            gain[name]["_samples_up"] += new > orig + 1e-9
            gain[name]["_samples_down"] += new < orig - 1e-9
    n = sum(n_by_cat.values())
    oracle = {}
    for name, g in gain.items():
        oracle[name] = {"points": round(100 * sum(v for k, v in g.items() if not k.startswith("_")) / n, 2),
                        "samples_up": g["_samples_up"], "samples_down": g["_samples_down"],
                        "by_category_points": {c: round(100 * g[c] / n, 2) for c in sorted(n_by_cat) if g[c]}}
    return {"n": n, "n_by_category": dict(n_by_cat), "replay_mismatch": replay_mismatch, "writes": dict(writes),
            "wrong_calls_by_cause": dict(calls_by.most_common()), "wrong_args_by_type": dict(args_by.most_common()),
            "oracle_fix": oracle, "missing_write_samples_why": dict(missing_why.most_common()),
            "where": {c: dict(v.most_common(8)) for c, v in where.items() if v},
            "detail": {k: dict(v.most_common(12)) for k, v in detail.items()},
            "examples": {c: v for c, v in examples.items() if v}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--run", action="append", required=True,
                    help="run prefix, e.g. runs/sft_q17b_fit_lao (needs <run>.jsonl, run on train ids)")
    ap.add_argument("--json", required=True)
    a = ap.parse_args()
    refuse_existing(a.json)
    root = Path(a.root)
    zt = zaic_tools("train", root)
    cat = load_catalog("train", root)
    tools, fuzzy = catalog_tools(cat), fuzzy_params(cat)
    items = {s["id"]: s for s in load_split("train", root)}
    out = {"runs": {}}
    for r in a.run:
        res = analyse_run(zt, root, r, items, tools, fuzzy)
        out["runs"][Path(r).name] = res
        print(Path(r).name, json.dumps({"n": res["n"], "replay_mismatch": res["replay_mismatch"],
                                        "writes": res["writes"], "wrong_calls_by_cause": res["wrong_calls_by_cause"]}))
        print("   oracle points:", json.dumps({k: v["points"] for k, v in res["oracle_fix"].items() if v["points"]}))
    write_json(a.json, out)


if __name__ == "__main__":
    main()
