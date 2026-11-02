"""Copies of the real ask samples of a fit split, to rebalance SFT data towards asking (the B-up arm of phase 2).

Selection: gold samples whose label asks (sys.ask_missing_info) and whose ask kind (lifemate.askpolicy.ask_type) is
B or C; kind A (several entities share a name) is left out, as in gen/up_real_asks_232.jsonl. On fit_lao this
selects exactly the 112 source samples of that file. Every selected sample gets --copies copies; extra copies go to
the first samples of a seeded shuffle until --rows rows. Ids are <id>~u1, ~u2, ...; _origin/_src/_kind as in the
B-up file. Feed the output to lifemate.sft --extra-samples (scripts/train_local.sh EXTRA_SAMPLES=...).

  .venv/bin/python scripts/make_upsample.py --fit splits/fit_random.txt --ratio 2.0714 --out gen/up_real_asks_random.jsonl

--ratio is rows per selected sample (B-up on fit_lao: 232 / 112 = 2.0714); --rows sets the count directly.
The output holds train data: keep it under gen/ (gitignored), never in git.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate.askpolicy import ask_type  # noqa: E402
from lifemate.data import DEFAULT_ROOT, catalog_tools, load_catalog, load_split, write_jsonl  # noqa: E402
from lifemate.runinfo import read_ids, refuse_existing  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--fit", required=True, help="ids file, e.g. splits/fit_random.txt")
    ap.add_argument("--kinds", default="B,C")
    ap.add_argument("--copies", type=int, default=2)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--rows", type=int)
    g.add_argument("--ratio", type=float)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    refuse_existing(a.out)
    tools = catalog_tools(load_catalog("train", a.root))
    keep = set(read_ids(a.fit))
    kinds = set(a.kinds.split(","))
    sel = [s for s in load_split("train", a.root) if s["id"] in keep and ask_type(s, tools) in kinds]
    rows = a.rows if a.rows is not None else round(a.ratio * len(sel))
    if rows < a.copies * len(sel):
        sys.exit(f"--rows {rows} < {a.copies} copies x {len(sel)} samples")
    order = sel[:]
    random.Random(a.seed).shuffle(order)
    n_copies = {s["id"]: a.copies for s in sel}
    for i in range(rows - a.copies * len(sel)):
        n_copies[order[i % len(order)]["id"]] += 1
    out = []
    for s in order:
        k = ask_type(s, tools)
        for c in range(1, n_copies[s["id"]] + 1):
            out.append({"id": f"{s['id']}~u{c}", "audio": s["audio"], "audio_text": s["audio_text"],
                        "context": s["context"], "history": s.get("history", []), "label": s["label"],
                        "_origin": s["id"], "_src": "upsample-real-ask", "_kind": k})
    write_jsonl(a.out, out)
    print(json.dumps({"fit": a.fit, "selected": len(sel), "rows": len(out),
                      "kinds": dict(Counter(ask_type(s, tools) for s in sel)),
                      "copies": dict(Counter(n_copies.values()))}))


if __name__ == "__main__":
    main()
