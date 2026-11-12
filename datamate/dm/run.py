"""Run DataMate on a split folder: /data-like layout (data/<biz>/, rulebook.md, calendar.csv, questions.jsonl).

    python -m dm.run --split /data --out /result [--ids ids.txt] [--biz biz_101,...] [--cache /tmp/dm_cache]

Writes one line per question to <out>/submission.jsonl as soon as it is answered, and one log line per question to
<out>/logs/log.jsonl (id, answer, elapsed_ms, thinking=null, code=function and inputs, output).
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import sys
import time
import traceback
from collections import defaultdict

from .assemble import build
from .canon import open_business
from .engine import Answer, Ctx, answer
from .qparse import parse


def load_questions(split: str):
    qs = []
    with open(os.path.join(split, "questions.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                qs.append(json.loads(line))
    return qs


def _jsonable(x):
    if dataclasses.is_dataclass(x):
        x = dataclasses.asdict(x)
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (dt.date, dt.datetime)):
        return x.isoformat()
    return x


def run(split: str, out: str, ids=None, bizs=None, cache=None, verbose=False):
    os.makedirs(os.path.join(out, "logs"), exist_ok=True)
    qs = load_questions(split)
    if ids is not None:
        qs = [q for q in qs if q["id"] in ids]
    if bizs:
        qs = [q for q in qs if q["business_id"] in bizs]
    by_biz = defaultdict(list)
    for q in qs:
        by_biz[q["business_id"]].append(q)
    cal = os.path.join(split, "calendar.csv")
    cal = cal if os.path.exists(cal) else None
    sub = open(os.path.join(out, "submission.jsonl"), "w", encoding="utf-8")
    log = open(os.path.join(out, "logs", "log.jsonl"), "w", encoding="utf-8")
    t_all = time.time()
    for biz, items in by_biz.items():
        t0 = time.time()
        ctx = None
        err = None
        try:
            b = open_business(os.path.join(split, "data", biz), cache_dir=cache)
            C = build(b)
            ctx = Ctx(C, cal)
        except Exception as e:  # a business we cannot read: abstain on its questions
            err = f"{type(e).__name__}: {e}"
            if verbose:
                traceback.print_exc()
        load_ms = int((time.time() - t0) * 1000)
        for q in items:
            t1 = time.time()
            asof = dt.date.fromisoformat(q["as_of_date"])
            if ctx is None:
                ans, qq = Answer("abstain", why=f"load error {err}"), None
            else:
                try:
                    qq = parse(q["question"], asof, ctx, cal)
                    ans = answer(qq, ctx, asof)
                except Exception as e:
                    qq = None
                    ans = Answer("abstain", why=f"{type(e).__name__}: {e}")
                    if verbose:
                        traceback.print_exc()
            rec = ans.to_json(q["id"])
            sub.write(json.dumps(rec, ensure_ascii=False) + "\n")
            sub.flush()
            el = int((time.time() - t1) * 1000)
            log.write(json.dumps({
                "id": q["id"], "answer": {k: v for k, v in rec.items() if k != "id"}, "elapsed_ms": el,
                "thinking": None, "code": "dm/engine.py::answer",
                "inputs": {"business": biz, "as_of_date": q["as_of_date"], "question": q["question"],
                           "query": _jsonable(qq) if qq is not None else None, "load_ms": load_ms},
                "output": rec.get("answer", rec.get("reason")), "why": ans.why}, ensure_ascii=False) + "\n")
            log.flush()
        if verbose:
            print(f"{biz}: {len(items)} q, load {load_ms} ms, total {time.time() - t0:.1f}s", file=sys.stderr, flush=True)
    sub.close()
    log.close()
    return time.time() - t_all


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ids")
    ap.add_argument("--biz")
    ap.add_argument("--cache")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    ids = set(l.strip() for l in open(a.ids)) if a.ids else None
    bizs = set(a.biz.split(",")) if a.biz else None
    secs = run(a.split, a.out, ids, bizs, a.cache, a.v)
    print(f"done in {secs:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
