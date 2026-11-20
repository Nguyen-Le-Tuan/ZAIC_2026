"""Read-only numbers behind docs/EXPERIMENT_D.md: the gold ask policy on fit splits, how the model behaves on each
ask type, an offline replay of the "same-name lookup -> ask" guardrail, and how many fit samples can seed
counterfactual pairs. Writes nothing unless --json is given.

  .venv/bin/python scripts/ask_policy_stats.py --fit splits/fit_random.txt splits/fit_lao.txt \
      --runs runs/sft_q17b_fit_random_rerun:splits/dev_random.txt runs/sft_q17b_fit_lao:splits/dev_lao.txt \
             runs/sft_q17b_fit_random_probefit:splits/probe_fit_random_233.txt
Runs need <prefix>.jsonl, <prefix>_rows.jsonl and, for the guardrail replay, <prefix>_trace.jsonl with tool results.
"""
import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate import counterfactual as cf  # noqa: E402
from lifemate.askpolicy import ASK, ambiguous_ids, ask_type, attested_plain_params, is_ask_sample, is_xref  # noqa: E402
from lifemate.data import DEFAULT_ROOT, catalog_tools, fuzzy_params, load_catalog, load_jsonl, load_split, zaic_tools  # noqa: E402
from lifemate.runinfo import read_ids, write_json  # noqa: E402
from lifemate.scorer import gold_from_train, score_sample  # noqa: E402

HELDOUT = set(json.loads((Path(__file__).resolve().parents[1] / "splits" / "heldout_apps.json").read_text()))


def policy(samples, tools) -> dict:
    asks = [s for s in samples if is_ask_sample(s)]
    tgt = [s["label"]["tool_calls"][-1]["arguments"] for s in asks]
    writes_before = sum(any(tools.get(c["name"], {}).get("kind") == "write" for c in s["label"]["tool_calls"][:-1]) for s in asks)
    rule = Counter()
    fp = []
    for s in samples:
        calls, res = s["label"]["tool_calls"], s["label"]["tool_results"]
        if not calls:
            continue
        amb, fired = set(), False
        for c, r in zip(calls, res):
            amb |= set(ambiguous_ids(c, r, s["audio_text"]))
            if tools.get(c["name"], {}).get("kind") == "write" and any(
                    is_xref(tools[c["name"]], k) and str(v) in amb for k, v in c["arguments"].items()):
                fired = True
        gold_ask = calls[-1]["name"] == ASK
        fired = fired or (gold_ask and bool(amb))
        rule[f"{'ask' if gold_ask else 'execute'}/{'fires' if fired else 'silent'}"] += 1
        if fired and not gold_ask:
            fp.append(s["id"])
    return {
        "samples": len(samples), "asks": len(asks),
        "distinct_target_tools": len({a["tool_name"] for a in tgt}),
        "distinct_target_apps": len({a["tool_name"].split(".")[0] for a in tgt}),
        "params_per_ask": dict(Counter(len(a.get("params", [])) for a in tgt)),
        "asks_after_a_write": writes_before,
        "asked_param_xref": sum(is_xref(tools.get(a["tool_name"], {}), a["params"][0]) for a in tgt),
        "types": dict(Counter(ask_type(s, tools) for s in asks)),
        "top_plain_params": Counter(a["params"][0] for s, a in zip(asks, tgt) if ask_type(s, tools) == "C").most_common(8),
        "attested_plain_params": sorted(attested_plain_params(samples, tools)),
        "same_name_rule": dict(rule), "same_name_rule_false_positives": fp,
    }


def behaviour(prefix, ids_file, S, tools) -> dict:
    P = {p["id"]: p for p in load_jsonl(f"{prefix}.jsonl")}
    R = {r["id"]: r for r in load_jsonl(f"{prefix}_rows.jsonl")}
    tab = Counter()
    for i in read_ids(ids_file):
        s = S[i]
        if not is_ask_sample(s):
            continue
        t = ask_type(s, tools)
        held = s["label"]["tool_calls"][-1]["arguments"]["tool_name"].split(".")[0] in HELDOUT
        asked = any(c["name"] == ASK for c in P[i]["tool_calls"])
        tab[f"{t}/{'held-out' if held else 'seen'}/{'asked' if asked else 'NOT asked'}{'/score=1' if R[i]['score'] == 1 else ''}"] += 1
    over = sum(1 for i in read_ids(ids_file) if R[i]["category"] == "execute" and any(c["name"] == ASK for c in P[i]["tool_calls"]))
    return {"by_type": dict(sorted(tab.items())), "execute_samples_that_asked": over}


def guardrail(prefix, ids_file, S, tools, fz, zt) -> dict:
    """Replay the rollout with the rule: the first write that uses an id from an ambiguous same-name lookup becomes
    an ask; later calls are dropped (the agent stops after an ask)."""
    T = {t["id"]: t for t in load_jsonl(f"{prefix}_trace.jsonl")}
    if not any("results" in st for t in T.values() for st in t["steps"]):
        return {"skipped": "trace has no tool results"}
    R = {r["id"]: r for r in load_jsonl(f"{prefix}_rows.jsonl")}
    ids = read_ids(ids_file)
    gold = gold_from_train("train", DEFAULT_ROOT, set(ids))
    out, delta = Counter(), 0.0
    for i in ids:
        amb, new = set(), None
        calls = []
        for st in T[i]["steps"]:
            for c, r in zip(st["calls"], st.get("results", [])):
                hit = [k for k, v in c["arguments"].items() if is_xref(tools.get(c["name"], {}), k) and str(v) in amb] \
                    if tools.get(c["name"], {}).get("kind") == "write" else []
                if hit and new is None:
                    new = calls + [{"name": ASK, "arguments": {"tool_name": c["name"], "params": hit[:1]}}]
                calls.append(c)
                amb |= set(ambiguous_ids(c, r, T[i]["text"]))
        if new is None:
            continue
        env = zt.ToolEnv("train", i)
        for c in new:
            env.call(c["name"], c["arguments"])
        s_new = score_sample(env.get_tool_calls(), env.get_state_hash(), gold[i]["tool_calls"], gold[i]["state_hash"], fz)
        d = s_new - R[i]["score"]
        delta += d
        out["better" if d > 0 else "worse" if d < 0 else "same"] += 1
    return {"fires": sum(out.values()), "of": len(ids), "outcome": dict(out), "delta_points": round(100 * delta / len(ids), 2)}


def sources(samples, tools) -> dict:
    attested = attested_plain_params(samples, tools)
    rng = random.Random(0)
    c = [t for s in samples for t in cf.candidates_c(s, tools, attested)]
    bv = [t for s in samples for t in cf.candidates_b_vague(s, tools)]
    bs = [t for s in samples for t in cf.candidates_b_specific(s, tools, rng)]
    return {"C": len(c), "C_tools": len({t["tool"] for t in c}), "B_vague": len(bv), "B_vague_tools": len({t["tool"] for t in bv}),
            "B_specific": len(bs), "B_specific_tools": len({t["tool"] for t in bs})}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fit", nargs="+", required=True)
    ap.add_argument("--exclude", nargs="*", default=["splits/dev_random.txt", "splits/dev_lao.txt"],
                    help="ids left out of the generator-source counts")
    ap.add_argument("--runs", nargs="*", default=[], help="prefix:ids_file")
    ap.add_argument("--json")
    a = ap.parse_args()
    S = {s["id"]: s for s in load_split("train")}
    cat = load_catalog("train")
    tools, fz, zt = catalog_tools(cat), fuzzy_params(cat), zaic_tools("train")
    excl = set().union(*[set(read_ids(p)) for p in a.exclude] or [set()])
    res = {"fit": {}, "runs": {}}
    for f in a.fit:
        samples = [S[i] for i in sorted(set(read_ids(f)))]
        src_samples = [s for s in samples if s["id"] not in excl]
        res["fit"][f] = {"policy": policy(samples, tools), "generator_sources_excluding_dev": sources(src_samples, tools)}
    for spec in a.runs:
        prefix, ids_file = spec.split(":")
        res["runs"][prefix] = {"behaviour": behaviour(prefix, ids_file, S, tools),
                               "same_name_guardrail": guardrail(prefix, ids_file, S, tools, fz, zt)}
    print(json.dumps(res, ensure_ascii=False, indent=1))
    if a.json:
        write_json(a.json, res)


if __name__ == "__main__":
    main()
