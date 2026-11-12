"""Score a run directory against train answers, by intent; write failures for reading.
    python scripts/eval_dev.py <train_split_dir> <run_dir> <ids.txt> [--fail fails.txt]"""
import argparse, json, os, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dm.score import load_jsonl, score_one

ap = argparse.ArgumentParser()
ap.add_argument("split"); ap.add_argument("run"); ap.add_argument("ids"); ap.add_argument("--fail")
a = ap.parse_args()
refs = load_jsonl(os.path.join(a.split, "answers.jsonl"))
preds = load_jsonl(os.path.join(a.run, "submission.jsonl"))
logs = {r["id"]: r for r in map(json.loads, open(os.path.join(a.run, "logs", "log.jsonl"), encoding="utf-8"))}
ids = [l.strip() for l in open(a.ids) if l.strip() and l.strip() in preds]
by = collections.defaultdict(list)
fails = []
for i in ids:
    s = score_one(preds.get(i), refs[i])
    lg = logs.get(i, {})
    qy = (lg.get("inputs") or {}).get("query") or {}
    it = qy.get("intent", "?")
    by[it].append(s)
    if s <= 0:
        fails.append((it, s, i, lg, refs[i], preds.get(i)))
tot = [score_one(preds.get(i), refs[i]) for i in ids]
print(f"PA {sum(tot)/len(tot):.4f} n={len(tot)} correct={tot.count(1)} wrong={tot.count(-1)} abstain={tot.count(0)}")
for it, v in sorted(by.items(), key=lambda kv: -len(kv[1])):
    print(f"  {it:26s} n={len(v):4d} PA={sum(v)/len(v):+.3f} ok={v.count(1):4d} wrong={v.count(-1):4d} abst={v.count(0):4d}")
if a.fail:
    with open(a.fail, "w", encoding="utf-8") as fh:
        for it, s, i, lg, r, p in sorted(fails, key=lambda x: (x[0], x[1])):
            q = (lg.get("inputs") or {})
            qy = q.get("query") or {}
            fh.write(f"[{it}] {s:+d} {i} {q.get('business')} {q.get('as_of_date')} | {q.get('question')}\n"
                     f"    gold={r['type']} {json.dumps(r.get('answer'), ensure_ascii=False)[:120]} | pred={json.dumps(p, ensure_ascii=False)[:160]} why={lg.get('why','')}\n"
                     f"    periods={qy.get('periods')} cmp={qy.get('compare')} out={qy.get('output')} f={qy.get('filters')} k={qy.get('k')} unit={qy.get('unit')} th={qy.get('threshold')} sd={qy.get('state_date')}\n")
