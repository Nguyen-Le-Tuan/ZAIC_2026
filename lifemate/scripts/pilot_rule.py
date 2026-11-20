"""Keep-or-drop rule of a pilot with several seeds per side, written before the results (JOURNAL entry 103).

  python scripts/pilot_rule.py --base runs/sft_q4b4_lao_base_s0 runs/sft_q4b4_lao_base_s1 \
      --new runs/sft_q4b4_lao_v2_s0 runs/sft_q4b4_lao_v2_s1 --ids splits/dev_lao.txt --json runs/pilot_v2_rule.json

For every run prefix P it reads P_score.json (oracle text) and P_asr_score.json (ASR text).
PASS when mean(new) - mean(base) >= --min-asr on ASR text AND >= --min-oracle on oracle text.
Also printed, for reading only: each seed, and the held-out-app / seen-app slices (apps in splits/heldout_apps.json).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate.data import load_jsonl, load_split  # noqa: E402


def score(prefix: str, text: str) -> float:
    p = Path(f"{prefix}{'_asr' if text == 'asr' else ''}_score.json")
    return float(json.loads(p.read_text())["score"])


def slice_scores(prefix: str, text: str, held_ids: set[str], ids: list[str]) -> dict:
    rows = {r["id"]: r["score"] for r in load_jsonl(f"{prefix}{'_asr' if text == 'asr' else ''}_rows.jsonl")}
    out = {}
    for name, keep in (("held_out_apps", [i for i in ids if i in held_ids]), ("seen_apps", [i for i in ids if i not in held_ids])):
        out[name] = round(100 * sum(rows.get(i, 0.0) for i in keep) / len(keep), 2) if keep else None
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", nargs="+", required=True)
    ap.add_argument("--new", nargs="+", required=True)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--heldout", default="splits/heldout_apps.json")
    ap.add_argument("--min-asr", type=float, default=2.0)
    ap.add_argument("--min-oracle", type=float, default=-2.0)
    ap.add_argument("--json")
    a = ap.parse_args()
    ids = Path(a.ids).read_text().split()
    held = set(json.loads(Path(a.heldout).read_text()))
    S = {s["id"]: s for s in load_split("train")}
    held_ids = {i for i in ids if {c["name"].split(".", 1)[0] for c in S[i]["label"]["tool_calls"]} & held}
    rep = {"rule": {"min_asr": a.min_asr, "min_oracle": a.min_oracle}, "texts": {}}
    ok = True
    for text, need in (("asr", a.min_asr), ("oracle", a.min_oracle)):
        b = [score(p, text) for p in a.base]
        n = [score(p, text) for p in a.new]
        d = mean(n) - mean(b)
        passed = d >= need
        ok &= passed
        rep["texts"][text] = {"base": b, "new": n, "mean_base": round(mean(b), 2), "mean_new": round(mean(n), 2),
                              "delta": round(d, 2), "needed": need, "pass": passed,
                              "slices_base": [slice_scores(p, text, held_ids, ids) for p in a.base],
                              "slices_new": [slice_scores(p, text, held_ids, ids) for p in a.new]}
        print(f"{text}: base {b} (mean {mean(b):.2f}) -> new {n} (mean {mean(n):.2f}): {d:+.2f}, "
              f"needed {need:+.1f} -> {'pass' if passed else 'FAIL'}")
    rep["result"] = "PASS" if ok else "FAIL"
    print(f"RULE {rep['result']}")
    if a.json:
        Path(a.json).write_text(json.dumps(rep, indent=1) + "\n")


if __name__ == "__main__":
    main()
