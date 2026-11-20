"""Where do the points go? For each prediction file on train ids: score, points lost by reason, unmatched calls
and argument mismatches (by parameter, fuzzy or exact). Read-only; train split only (needs labels).

  .venv/bin/python scripts/loss_breakdown.py runs/sft_x.jsonl@splits/dev_random.txt runs/api_y.jsonl@ids.txt

Reasons (points on the 0-100 scale of that file):
  out_of_scope: called tools     gold is empty, the prediction is not
  no calls (gold had some)
  hash wrong, F1=0               final state wrong and no call matched
  hash wrong (F1>0 lost)         final state wrong although some calls matched: the F1 that the hash threw away
  F1 shortfall                   ... and the part of F1 that was missing anyway
  F1 shortfall, hash ok          final state right, but calls missing or extra (reads, extra arguments)
First written for JOURNAL entry 78 (04/11).
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lifemate.data import DEFAULT_ROOT, catalog_tools, fuzzy_params, load_catalog  # noqa: E402
from lifemate.scorer import call_f1, calls_match, gold_from_train, load_predictions  # noqa: E402


def analyse(pred_path: str, ids: list[str], root, tools: dict, fuzzy: dict) -> dict:
    gold = gold_from_train("train", root, ids)
    pred = load_predictions(pred_path)
    kind = lambda n: tools.get(n, {}).get("kind", "?")  # noqa: E731
    lost, params, missing, extra = Counter(), Counter(), Counter(), Counter()
    examples, total = defaultdict(list), 0.0
    for i in ids:
        g, p = gold[i], pred.get(i, {"tool_calls": [], "state_hash": None})
        gc, pc = g["tool_calls"], p["tool_calls"]
        hok = p["state_hash"] == g["state_hash"]
        if not gc:
            s = 1.0 if not pc else 0.0
            total += s
            lost["out_of_scope: called tools"] += 1 - s
            continue
        f1 = call_f1(pc, gc, fuzzy) if pc else 0.0
        s = f1 if hok and f1 > 0 else 0.0
        total += s
        if s == 1.0:
            continue
        if not pc:
            lost["no calls (gold had some)"] += 1
            continue
        if not hok and f1 > 0:
            lost["hash wrong (F1>0 lost)"] += f1
            lost["F1 shortfall"] += 1 - f1
        elif not hok:
            lost["hash wrong, F1=0"] += 1
        else:
            lost["F1 shortfall, hash ok"] += 1 - f1
        used = set()
        for gcall in gc:
            hit = next((j for j, c in enumerate(pc) if j not in used and calls_match(c, gcall, fuzzy)), None)
            if hit is not None:
                used.add(hit)
                continue
            same = [j for j, c in enumerate(pc) if j not in used and c["name"] == gcall["name"]]
            if not same:
                missing[kind(gcall["name"])] += 1
                continue
            c = pc[same[0]]
            used.add(same[0])
            ga, pa = gcall["arguments"], c["arguments"]
            for k in sorted(set(ga) | set(pa)):
                if ga.get(k) != pa.get(k):
                    how = "absent" if k not in pa else ("extra" if k not in ga else "diff")
                    key = (gcall["name"], k, "fuzzy" if k in fuzzy.get(gcall["name"], set()) else "exact", how)
                    params[key] += 1
                    if len(examples[key]) < 3:
                        examples[key].append(i)
        for j, c in enumerate(pc):
            if j not in used:
                extra[kind(c["name"])] += 1
    n = len(ids)
    return {"file": pred_path, "n": n, "score": round(100 * total / n, 2),
            "lost": {k: round(100 * v / n, 2) for k, v in lost.most_common()},
            "missing_calls_by_kind": dict(missing), "extra_calls_by_kind": dict(extra),
            "arg_mismatches": [{"tool": t, "param": k, "match": m, "how": h, "n": c, "ids": examples[(t, k, m, h)]}
                               for (t, k, m, h), c in params.most_common()]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", help="prediction.jsonl@ids.txt")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--top", type=int, default=12, help="argument mismatches printed per file")
    ap.add_argument("--json", help="write every result here")
    a = ap.parse_args()
    cat = load_catalog("train", a.root)
    tools, fuzzy = catalog_tools(cat), fuzzy_params(cat)
    out = []
    for spec in a.runs:
        path, idf = spec.split("@")
        r = analyse(path, Path(idf).read_text().split(), a.root, tools, fuzzy)
        out.append(r)
        print(f"\n=== {Path(path).name}  n={r['n']}  score={r['score']}")
        print("  points lost:", r["lost"])
        print("  gold calls with no same-name prediction, by kind:", r["missing_calls_by_kind"],
              "| extra predicted calls, by kind:", r["extra_calls_by_kind"])
        for m in r["arg_mismatches"][: a.top]:
            print(f"    {m['tool']}.{m['param']} ({m['match']}, {m['how']}): {m['n']}  e.g. {m['ids']}")
    if a.json:
        import json
        Path(a.json).write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
