"""Scoring as in the DataMate Evaluation tab: +1 correct, 0 abstain (or missing), -1 wrong; PA = mean.

Reference lines come from answers.jsonl ({"id","type","answer","alias"}). Aliases: string -> [str]; list -> [[str] per
element]; table -> [[str] per row] (accepted forms of the row's name cell).

    python -m dm.score answers.jsonl submission.jsonl [--ids ids.txt] [--by-type]
"""
from __future__ import annotations

import argparse
import json
import math

from .textnorm import score_norm

TYPES = {"number", "percent", "string", "date", "boolean", "list", "table", "unanswerable", "abstain"}


def _num_eq(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return False
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if math.isnan(a) or math.isnan(b):
        return False
    return abs(a - b) <= 1e-6 * max(1.0, abs(b))


def _pct_eq(a, b) -> bool:
    try:
        return round(float(a) + 0.0, 2) == round(float(b) + 0.0, 2) or abs(float(a) - float(b)) < 5e-7
    except (TypeError, ValueError):
        return False


def _str_eq(a, ref, aliases=()) -> bool:
    if not isinstance(a, str):
        return False
    na = score_norm(a)
    return any(na == score_norm(x) for x in [ref, *aliases] if isinstance(x, str))


def _elem_eq(a, ref, aliases=()) -> bool:
    if isinstance(ref, str):
        return _str_eq(a, ref, aliases)
    if isinstance(ref, bool):
        return a is ref
    if isinstance(ref, (int, float)):
        return _num_eq(a, ref)
    return a == ref


def score_one(pred: dict | None, ref: dict) -> int:
    if pred is None or pred.get("type") in (None, "abstain") or pred.get("type") not in TYPES:
        return 0
    rt, pt = ref["type"], pred["type"]
    if pt == "unanswerable":
        return 1 if rt == "unanswerable" else -1
    if rt == "unanswerable" or pt != rt:
        return -1
    a, r, al = pred.get("answer"), ref.get("answer"), ref.get("alias") or []
    ok = False
    if rt == "number":
        ok = _num_eq(a, r)
    elif rt == "percent":
        ok = _pct_eq(a, r)
    elif rt in ("date", "boolean"):
        ok = a == r and type(a) is type(r)
    elif rt == "string":
        ok = _str_eq(a, r, al)
    elif rt == "list":
        ok = isinstance(a, list) and len(a) == len(r) and all(
            _elem_eq(x, y, al[i] if i < len(al) and isinstance(al[i], list) else ()) for i, (x, y) in enumerate(zip(a, r)))
    elif rt == "table":
        ok = _table_eq(a, r, al)
    return 1 if ok else -1


def _table_eq(a, r, al) -> bool:
    if not isinstance(a, dict) or not isinstance(a.get("columns"), list) or not isinstance(a.get("rows"), list):
        return False
    rc, pc = r["columns"], a["columns"]
    if len(rc) != len(pc) or len(a["rows"]) != len(r["rows"]):
        return False
    # columns by normalised name, else by position
    pos = {score_norm(c): i for i, c in enumerate(pc)}
    perm = []
    for j, c in enumerate(rc):
        perm.append(pos.get(score_norm(c), j))
    if len(set(perm)) != len(perm):
        perm = list(range(len(rc)))
    rows_left = list(range(len(r["rows"])))
    for prow in a["rows"]:
        if not isinstance(prow, list) or len(prow) != len(rc):
            return False
        hit = None
        for k in rows_left:
            rrow = r["rows"][k]
            aliases = al[k] if k < len(al) and isinstance(al[k], list) else []
            if all(_elem_eq(prow[perm[j]], rrow[j], aliases if j == 0 else ()) for j in range(len(rc))):
                hit = k
                break
        if hit is None:
            return False
        rows_left.remove(hit)
    return not rows_left


def load_jsonl(path: str) -> dict:
    out = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            r = json.loads(line)
            out[r["id"]] = r
    return out


def score(refs: dict, preds: dict, ids=None) -> dict:
    ids = list(ids) if ids is not None else list(refs)
    s = [score_one(preds.get(i), refs[i]) for i in ids]
    n = len(s)
    return {"n": n, "pa": sum(s) / n if n else 0.0, "correct": s.count(1), "wrong": s.count(-1), "abstain": s.count(0),
            "precision": s.count(1) / max(1, s.count(1) + s.count(-1)), "scores": dict(zip(ids, s))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("answers")
    ap.add_argument("submission")
    ap.add_argument("--ids")
    ap.add_argument("--by-type", action="store_true")
    a = ap.parse_args()
    refs, preds = load_jsonl(a.answers), load_jsonl(a.submission)
    ids = [l.strip() for l in open(a.ids)] if a.ids else None
    r = score(refs, preds, ids)
    print(f"PA {r['pa']:.4f}  n={r['n']} correct={r['correct']} wrong={r['wrong']} abstain={r['abstain']} "
          f"precision={r['precision']:.3f}")
    if a.by_type:
        from collections import defaultdict
        g = defaultdict(list)
        for i, s in r["scores"].items():
            g[refs[i]["type"]].append(s)
        for t, v in sorted(g.items(), key=lambda kv: -len(kv[1])):
            print(f"  {t:13s} n={len(v):4d} PA={sum(v) / len(v):+.3f} correct={v.count(1)} wrong={v.count(-1)}")


if __name__ == "__main__":
    main()
