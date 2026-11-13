"""Quality metrics of the experiment-D generator (the D-M* metrics of docs/REVIEW_D_2026-10-30.md). Read-only.

  .venv/bin/python scripts/d_quality.py --tasks gen/tasks_fit_lao.jsonl --rewrites gen/rewrites_fit_lao.jsonl \
      --mutations gen/mutations_fit_lao.jsonl --runs runs/sft_q17b_fit_random_rerun:splits/dev_random.txt \
      runs/sft_q17b_fit_lao:splits/dev_lao.txt [--json out.json]

  D-M1  natural ask/execute neighbour pairs (text similarity >= 0.6): how many, and how many labels agree
  D-M2  generated labels whose (type, tool, param) a real fit ask attests
  D-M3  among those, read-prefix signature also seen in real asks
  D-M4  fixed adversarial rewrites (--mutations) that the text checks reject
  D-M5  accepted pilot rewrites (--rewrites) that the text checks would now reject (false rejects)
  D-M6/7 source prefilter vs the writer's skip decisions (in-sample on the pilot)
  D-M9..11 source pool size, top-3 tool share (raw and capped), distinct tools
  D-M12 coverage of the model's B/C ask misses on dev by generator sources (aggregate only)
  D-M6v2 source filter v2 vs the writer's / judge's decisions (--report: the build report, for judge rejects)
  D-M10/11 on kept samples (--samples): tools, top-3 share, real-ask precedent share
  D-M14 (rough) per kept (type, tool, param): real asks vs fit executes whose slot the request does not give
"""
import argparse
import collections
import difflib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate import counterfactual as cf  # noqa: E402
from lifemate.askpolicy import ASK, ask_type, attested_plain_params, is_ask_sample, norm  # noqa: E402
from lifemate.data import catalog_tools, load_catalog, load_jsonl, load_split  # noqa: E402
from lifemate.runinfo import read_ids, sha256_file, write_json  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
HELDOUT = set(json.loads((ROOT / "splits" / "heldout_apps.json").read_text()))


def pool(S):
    ids = lambda p: set(read_ids(ROOT / p))  # noqa: E731
    keep = (ids("splits/fit_random.txt") | ids("splits/fit_lao.txt")) - ids("splits/dev_random.txt") - ids("splits/dev_lao.txt")
    return [S[i] for i in sorted(keep)]


def all_candidates(P, tools, att, prefilter):
    rng = random.Random(0)
    for e in P:
        for t in cf.candidates_c(e, tools, att, prefilter) + cf.candidates_b_vague(e, tools, prefilter) + \
                cf.candidates_b_specific(e, tools, rng, prefilter):
            yield e, t


def sig(calls, tool, tools):
    app = tool.split(".")[0]
    return tuple(sorted({c["name"] for c in calls[:-1] if tools.get(c["name"], {}).get("kind") == "read"
                         and c["name"].split(".")[0] in (app, "contacts")}))


def label_fidelity(P, tools, att, prefilter) -> dict:
    real = collections.defaultdict(set)
    for s in P:
        if is_ask_sample(s) and ask_type(s, tools) in ("B", "C"):
            a = s["label"]["tool_calls"][-1]["arguments"]
            real[(ask_type(s, tools), a["tool_name"], a["params"][0])].add(sig(s["label"]["tool_calls"], a["tool_name"], tools))
    n = prec = agree = 0
    for e, t in all_candidates(P, tools, att, prefilter):
        if t["kind"] == "B-specific":
            continue
        k = ("C" if t["kind"] == "C" else "B", t["tool"], t["param"])
        n += 1
        if k in real:
            prec += 1
            agree += sig(cf.make_label(t, e), t["tool"], tools) in real[k]
    return {"labels": n, "with_precedent": prec, "prefix_agrees": agree}


def natural_pairs(P, tools, att, th=0.6) -> dict:
    idx = collections.defaultdict(list)
    for e, t in all_candidates(P, tools, att, False):
        if t["kind"] != "B-specific":
            idx[("C" if t["kind"] == "C" else "B", t["tool"], t["param"])].append((e, t))
    pairs = agree = 0
    for r in P:
        k = ask_type(r, tools)
        if k not in ("B", "C"):
            continue
        a = r["label"]["tool_calls"][-1]["arguments"]
        cands = idx.get((k, a["tool_name"], a["params"][0]), [])
        best = max(cands, key=lambda et: difflib.SequenceMatcher(None, norm(r["audio_text"]), norm(et[0]["audio_text"])).ratio(), default=None)
        if best and difflib.SequenceMatcher(None, norm(r["audio_text"]), norm(best[0]["audio_text"])).ratio() >= th:
            pairs += 1
            agree += [c["name"] for c in cf.make_label(best[1], best[0])] == [c["name"] for c in r["label"]["tool_calls"]]
    return {"pairs": pairs, "label_names_agree": agree, "similarity_threshold": th}


def validators(tasks, rewrites, mutations) -> dict:
    T = {t["task_id"]: t for t in tasks}
    out = {}
    if mutations:
        rej = collections.Counter()
        for m in mutations:
            rej[(T[m["task_id"]]["kind"], bool(cf.check_rewrite(T[m["task_id"]], m)))] += 1
        out["mutations_rejected"] = sum(v for (k, r), v in rej.items() if r)
        out["mutations_total"] = len(mutations)
        out["mutations_by_kind"] = {f"{k}/{'rejected' if r else 'missed'}": v for (k, r), v in sorted(rej.items())}
    if rewrites:
        good = [r for r in rewrites if "new_text" in r]
        out["false_rejects"] = [r["task_id"] for r in good if cf.check_rewrite(T[r["task_id"]], r)]
        out["good_rewrites"] = len(good)
    return out


def prefilter_vs_writer(tasks, rewrites, S, tools) -> dict:
    rw = {r["task_id"]: r for r in rewrites}
    conf = collections.Counter()
    for t in tasks:
        s = S[t["origin_id"]]
        if t["kind"] == "C":
            drop = cf.c_filter_reason(s, t, tools) is not None
        elif t["kind"] == "B-vague":
            drop = not any(x["param"] == t["param"] for x in cf.candidates_b_vague(s, tools))
        else:
            drop = not cf.candidates_b_specific(s, tools, random.Random(0))
        conf[f"{'writer_skipped' if 'skip' in rw.get(t['task_id'], {}) else 'writer_rewrote'}/{'dropped' if drop else 'kept'}"] += 1
    return dict(sorted(conf.items()))


def filter_v2_vs_writer(tasks, rewrites, report, S, tools) -> dict:
    """Confusion of filter_v2_reason (drop/keep) against the outcome: good = kept by build; bad = writer skip or
    judge / text-check reject. Hits per rule. In-sample when the rules were written after reading these decisions."""
    rw = {r["task_id"]: r for r in rewrites}
    out_by = {r["task_id"]: r for r in report} if report else {}
    conf, per = collections.Counter(), collections.defaultdict(collections.Counter)
    for t in tasks:
        if t["kind"] == "B-specific":
            continue
        s = S[t["origin_id"]]
        if t["kind"] == "C" and cf.c_filter_reason(s, t, tools):
            conf["dropped_by_v1_prefilter"] += 1
            continue
        r = cf.filter_v2_reason(s, t, tools)
        row = out_by.get(t["task_id"])
        o = "good" if (row["kept"] if row else "skip" not in rw.get(t["task_id"], {})) else \
            "writer_skip" if "skip" in rw.get(t["task_id"], {}) else "rejected"
        conf[f"{'good' if o == 'good' else 'bad'}/{'dropped' if r else 'kept'}"] += 1
        if r:
            per[r][o] += 1
    return {"confusion": dict(sorted(conf.items())), "per_rule": {k: dict(v) for k, v in sorted(per.items())}}


def kept_stats(samples, tasks, P, tools) -> dict:
    T = {t["task_id"]: t for t in tasks}
    prec = cf.precedents(P, tools)
    keys = collections.Counter()
    for d in samples:
        t = T[f"{d['_origin']}#{d['_kind']}"]
        keys[("C" if t["kind"] == "C" else "B", t["tool"], t["param"])] += 1
    tl = collections.Counter()
    for (_, tool, _), n in keys.items():
        tl[tool] += n
    n = sum(keys.values())
    return {"samples": n, "by_kind": dict(collections.Counter(d["_kind"] for d in samples)), "tools": len(tl),
            "top3_tools": tl.most_common(3), "top3_share": round(sum(x for _, x in tl.most_common(3)) / n, 2) if n else None,
            "with_precedent": sum(v for k, v in keys.items() if k in prec), "keys": keys}


def counter_precedent(P, tools, keys) -> list[dict]:
    """Rough: per (type, tool, param), fit executes where the request (or user history) does not give the slot and
    the value is not copied from a tool result (C), or the picked list entity has no unique word in the request (B).
    Counts include computed values and "all/each" requests, so read them as a flag for manual checking only."""
    asks, cnt = collections.Counter(), collections.Counter()
    for s in P:
        t = ask_type(s, tools)
        if t in ("B", "C"):
            a = s["label"]["tool_calls"][-1]["arguments"]
            asks[(t, a["tool_name"], a["params"][0])] += 1
        if is_ask_sample(s):
            continue
        calls, res = s["label"]["tool_calls"], s["label"]["tool_results"]
        hist = " ".join(h["audio_text"] for h in s.get("history", []) if h["role"] == "user")
        seen = cf._atoms(res) | cf._history_atoms(s)
        for i, c in enumerate(calls):
            spec = tools.get(c["name"], {})
            if spec.get("kind") != "write":
                continue
            for p in cf.required(spec):
                v = c["arguments"].get(p)
                if (("C", c["name"], p) not in keys and ("B", c["name"], p) not in keys) or v is None or isinstance(v, bool):
                    continue
                if cf.is_xref(spec, p):
                    pick = cf._list_pick(calls, res, i, v)
                    if pick and not (cf._unique_words(*pick) & cf.words(s["audio_text"] + " " + hist)):
                        cnt[("B", c["name"], p)] += 1
                elif "enum" not in spec["parameters"]["properties"].get(p, {}):
                    ps = spec["parameters"]["properties"].get(p, {})
                    said = cf.spoken_in(s["audio_text"], v, ps) or cf.spoken_in(hist, v, ps)
                    copied = all(str(x) in seen for x in v) if isinstance(v, list) else str(v) in seen
                    if not said and not copied:
                        cnt[("C", c["name"], p)] += 1
    return [{"key": list(k), "kept": n, "real_asks": asks[k], "counter": cnt[k], "flag": cnt[k] > asks[k]}
            for k, n in sorted(keys.items(), key=lambda x: (asks[x[0]] > 0, -cnt[x[0]]))]


def pool_stats(P, tools, att, prefilter, cap=8) -> dict:
    tl = collections.defaultdict(collections.Counter)
    for _, t in all_candidates(P, tools, att, prefilter):
        tl[t["kind"]][t["tool"]] += 1
    out = {}
    for k, v in sorted(tl.items()):
        capped = collections.Counter({x: min(n, cap) for x, n in v.items()})
        tot, ctot = sum(v.values()), sum(capped.values())
        out[k] = {"sources": tot, "tools": len(v), "top3_share": round(sum(n for _, n in v.most_common(3)) / tot, 2),
                  f"capped_{cap}": ctot, "capped_top3_share": round(sum(n for _, n in capped.most_common(3)) / ctot, 2)}
    return out


def coverage(prefix, ids_file, S, tools, P, att) -> dict:
    keys, params = collections.Counter(), collections.Counter()
    for _, t in all_candidates(P, tools, att, True):
        k = "C" if t["kind"] == "C" else "B"
        keys[(k, t["tool"], t["param"])] += 1
        params[(k, t["param"])] += 1
    Pr = {p["id"]: p for p in load_jsonl(f"{prefix}.jsonl")}
    c = collections.Counter()
    for i in read_ids(ids_file):
        s = S[i]
        t = ask_type(s, tools)
        if t not in ("B", "C") or any(x["name"] == ASK for x in Pr[i]["tool_calls"]):
            continue
        a = s["label"]["tool_calls"][-1]["arguments"]
        k = "C" if t == "C" else "B"
        held = "held-out" if a["tool_name"].split(".")[0] in HELDOUT else "seen"
        cov = "exact" if keys[(k, a["tool_name"], a["params"][0])] else "param_name" if params[(k, a["params"][0])] else "none"
        c[f"{held}/{cov}"] += 1
    return dict(sorted(c.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks")
    ap.add_argument("--rewrites")
    ap.add_argument("--mutations")
    ap.add_argument("--runs", nargs="*", default=[])
    ap.add_argument("--report", help="build report json (rows with kept/reason), for D-M6v2")
    ap.add_argument("--samples", nargs="*", default=[], help="kept D samples, for D-M10/11 and D-M14")
    ap.add_argument("--json")
    a = ap.parse_args()
    S = {s["id"]: s for s in load_split("train")}
    tools = catalog_tools(load_catalog("train"))
    P = pool(S)
    att = attested_plain_params(P, tools)
    tasks = load_jsonl(a.tasks) if a.tasks else []
    rewrites = load_jsonl(a.rewrites) if a.rewrites else []
    mutations = load_jsonl(a.mutations) if a.mutations else []
    res = {
        "inputs_sha256": {k: sha256_file(getattr(a, k)) for k in ("tasks", "rewrites", "mutations") if getattr(a, k)},
        "D-M1_natural_pairs": natural_pairs(P, tools, att),
        "D-M2_M3_label_fidelity": {"no_prefilter": label_fidelity(P, tools, att, False), "prefilter": label_fidelity(P, tools, att, True)},
        "D-M4_M5_validators": validators(tasks, rewrites, mutations) if tasks else None,
        "D-M6_M7_prefilter_vs_writer": prefilter_vs_writer(tasks, rewrites, S, tools) if tasks and rewrites else None,
        "D-M9_M11_pool": {"no_prefilter": pool_stats(P, tools, att, False), "prefilter": pool_stats(P, tools, att, True)},
        "D-M12_coverage_of_dev_misses": {p.split(":")[0]: coverage(*p.split(":"), S, tools, P, att) for p in a.runs},
    }
    if tasks and rewrites:
        rep = json.loads(Path(a.report).read_text())["rows"] if a.report else None
        res["D-M6v2_filter_v2_vs_outcome"] = filter_v2_vs_writer(tasks, rewrites, rep, S, tools)
    if a.samples:
        kept = [x for f in a.samples for x in load_jsonl(f)]
        ks = kept_stats(kept, tasks, P, tools)
        res["inputs_sha256"].update({f: sha256_file(f) for f in a.samples})
        res["D-M14_counter_precedent"] = counter_precedent(P, tools, ks.pop("keys"))
        res["D-M10_M11_kept"] = ks
    print(json.dumps(res, ensure_ascii=False, indent=1))
    if a.json:
        write_json(a.json, res)


if __name__ == "__main__":
    main()
