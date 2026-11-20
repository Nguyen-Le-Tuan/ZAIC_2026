"""Paired comparison of evaluation runs on the same samples.

A run is a path prefix P with P_rows.jsonl (from lifemate.scorer --rows), and optionally P_trace.jsonl (latency,
stop reasons) and P.meta.json. The first run is the reference. All runs must cover the same ids.

Example:
  python -m lifemate.compare runs/sft_q17b_fit_random runs/sft_q17b_fit_random_s100 runs/sft_q17b_fit_random_s200 --slices
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from . import runinfo
from .data import DEFAULT_ROOT, load_jsonl, load_split

CATS = ("ask_missing", "execute", "out_of_scope")


def load_run(prefix: str) -> dict:
    p = Path(prefix)
    rows = {r["id"]: r for r in load_jsonl(f"{p}_rows.jsonl")}
    trace_path = Path(f"{p}_trace.jsonl")
    trace = {t["id"]: t for t in load_jsonl(trace_path)} if trace_path.exists() else {}
    meta_path = p.with_name(p.name + ".meta.json")
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else None
    return {"name": p.name, "rows": rows, "trace": trace, "meta": meta}


def summarize(run: dict, ids: list[str]) -> dict:
    rows = [run["rows"][i] for i in ids]
    n = len(rows)
    s = {"n": n, "score": 100 * sum(r["score"] for r in rows) / n, "call_f1": 100 * sum(r["call_f1"] for r in rows) / n,
         "hash": 100 * sum(r["hash_ok"] for r in rows) / n,
         "full": sum(r["score"] == 1 for r in rows), "partial": sum(0 < r["score"] < 1 for r in rows),
         "zero": sum(r["score"] == 0 for r in rows)}
    for c in CATS:
        v = [r["score"] for r in rows if r["category"] == c]
        s[c] = 100 * sum(v) / len(v) if v else float("nan")
    secs = [run["trace"][i]["seconds"] for i in ids if i in run["trace"]]
    if secs:
        s.update(mean_s=sum(secs) / len(secs), p95_s=runinfo.percentile(secs, .95), max_s=max(secs))
        s["stops"] = dict(Counter(run["trace"][i]["stop"] for i in ids if i in run["trace"]))
    return s


def paired(ref: dict, run: dict, ids: list[str], n_boot: int = 10000, seed: int = 0) -> dict:
    d = [run["rows"][i]["score"] - ref["rows"][i]["score"] for i in ids]
    rng = random.Random(seed)
    means = sorted(sum(d[rng.randrange(len(d))] for _ in d) / len(d) for _ in range(n_boot))
    return {"delta": 100 * sum(d) / len(d), "ci95": (100 * means[int(.025 * n_boot)], 100 * means[int(.975 * n_boot) - 1]),
            "better": sum(x > 0 for x in d), "worse": sum(x < 0 for x in d), "same": sum(x == 0 for x in d)}


def slices(ids: list[str], root) -> dict[str, list[str]]:
    """Fixed slices of train-derived dev sets: history length and id range (train ids come in generation batches)."""
    S = {s["id"]: s for s in load_split("train", root)}
    out: dict[str, list[str]] = {}
    for i in ids:
        h = sum(x["role"] == "user" for x in S[i].get("history", []))
        hb = "hist 0" if h == 0 else "hist 1-2" if h <= 2 else "hist 3-5" if h <= 5 else "hist 6+"
        n = int(i.split("_")[1])
        ib = f"id {(n - 1) // 300 * 300 + 1:04d}-{(n - 1) // 300 * 300 + 300:04d}"
        out.setdefault(hb, []).append(i)
        out.setdefault(ib, []).append(i)
    return dict(sorted(out.items()))


def main():
    ap = argparse.ArgumentParser(description="paired comparison of evaluation runs (first = reference)")
    ap.add_argument("runs", nargs="+", help="run prefixes, e.g. runs/sft_q17b_fit_random")
    ap.add_argument("--ids", help="restrict to these ids (default: ids common to all runs, which must be identical)")
    ap.add_argument("--slices", action="store_true", help="also score by history length and id range")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--json", help="write the numbers here too")
    a = ap.parse_args()

    runs = [load_run(p) for p in a.runs]
    sets = [set(r["rows"]) for r in runs]
    if a.ids:
        ids = sorted(set(runinfo.read_ids(a.ids)))
        missing = {r["name"]: len(set(ids) - set(r["rows"])) for r in runs if set(ids) - set(r["rows"])}
        if missing:
            raise SystemExit(f"runs miss ids of {a.ids}: {missing}")
    else:
        if any(s != sets[0] for s in sets):
            raise SystemExit("runs cover different ids; pass --ids to compare on a common set")
        ids = sorted(sets[0])

    res = {"ids": runinfo.ids_digest(ids), "runs": []}
    print(f"{len(ids)} samples; reference = {runs[0]['name']}\n")
    print("| run | score | call-F1 | hash % | ask | execute | oos | full/part/zero | mean s | p95 s | max s |")
    print("|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|")
    for r in runs:
        s = summarize(r, ids)
        res["runs"].append({"name": r["name"], "summary": s})
        lat = f"{s['mean_s']:.2f} | {s['p95_s']:.2f} | {s['max_s']:.2f}" if "mean_s" in s else "- | - | -"
        print(f"| {r['name']} | {s['score']:.2f} | {s['call_f1']:.2f} | {s['hash']:.2f} | {s['ask_missing']:.1f} | "
              f"{s['execute']:.1f} | {s['out_of_scope']:.1f} | {s['full']}/{s['partial']}/{s['zero']} | {lat} |")

    if len(runs) > 1:
        print("\n| run vs reference | Δscore | paired bootstrap 95% CI | better | worse | same |")
        print("|---|---:|---|---:|---:|---:|")
        for r, out in zip(runs[1:], res["runs"][1:]):
            p = paired(runs[0], r, ids)
            out["vs_reference"] = p
            print(f"| {r['name']} | {p['delta']:+.2f} | [{p['ci95'][0]:+.2f}, {p['ci95'][1]:+.2f}] | {p['better']} | {p['worse']} | {p['same']} |")

    if a.slices:
        sl = slices(ids, a.root)
        print("\n| slice | n | " + " | ".join(r["name"] for r in runs) + " |")
        print("|---|---:|" + "---:|" * len(runs))
        res["slices"] = {}
        for k, v in sl.items():
            vals = [100 * sum(r["rows"][i]["score"] for i in v) / len(v) for r in runs]
            res["slices"][k] = {"n": len(v), "scores": vals}
            print(f"| {k} | {len(v)} | " + " | ".join(f"{x:.1f}" for x in vals) + " |")
    if a.json:
        runinfo.write_json(a.json, res)


if __name__ == "__main__":
    main()
