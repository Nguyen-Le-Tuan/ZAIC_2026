"""Where each arm's score change against a base run comes from: gold-ask samples, new over-asks, everything else.
Read-only over runs/. Uses the gold labels, so the "ceiling" is an upper bound, not a deployable number.

  .venv/bin/python scripts/overask_cost.py --base q17b_fit_lao --arms q17b_lao_up q17b_lao_d1 q17b_lao_d3 \
      --ids splits/dev_lao.txt --json runs/overask_cost.json

For each arm, the dev samples split into three parts and the total change (points on the 100 scale) is their sum:
  ask        the gold label asks
  new_over   the gold label does not ask, the arm calls the ask tool and the base run does not
  rest       every other sample
ceiling = the arm's score if each new over-ask got the base run's result instead (a perfect filter for new over-asks).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate.askpolicy import ASK  # noqa: E402
from lifemate.data import load_jsonl  # noqa: E402
from lifemate.runinfo import read_ids, write_json  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def load(tag):
    rows = {r["id"]: r for r in load_jsonl(ROOT / "runs" / f"sft_{tag}_rows.jsonl")}
    pred = {p["id"]: p for p in load_jsonl(ROOT / "runs" / f"sft_{tag}.jsonl")}
    asked = {i for i, p in pred.items() if any(c["name"] == ASK for c in p.get("tool_calls", []))}
    return rows, asked


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--arms", nargs="+", required=True)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--json")
    a = ap.parse_args()
    ids = read_ids(ROOT / a.ids)
    n = len(ids)
    rows0, asked0 = load(a.base)
    gold_ask = {i for i in ids if rows0[i]["category"] == "ask_missing"}
    out = {"base": a.base, "ids": n, "gold_ask": len(gold_ask), "arms": {}}
    for tag in a.arms:
        rows, asked = load(tag)
        over = {i for i in ids if i not in gold_ask and i in asked}
        new = {i for i in over if i not in asked0}
        d = {i: rows[i]["score"] - rows0[i]["score"] for i in ids}
        part = {
            "ask": sum(d[i] for i in gold_ask),
            "new_over": sum(d[i] for i in new),
            "rest": sum(d[i] for i in ids if i not in gold_ask and i not in new),
        }
        score = sum(rows[i]["score"] for i in ids)
        out["arms"][tag] = {
            "score": round(score / n * 100, 2),
            "delta": round(sum(d.values()) / n * 100, 2),
            "delta_parts": {k: round(v / n * 100, 2) for k, v in part.items()},
            "over_ask": len(over),
            "over_ask_shared_with_base": len(over - new),
            "new_over_ask": len(new),
            "base_score_on_new_over_ask": round(sum(rows0[i]["score"] for i in new), 2),
            "ceiling_without_new_over_ask": round((score - part["new_over"]) / n * 100, 2),
        }
    for tag, r in out["arms"].items():
        p = r["delta_parts"]
        print(f"{tag:22s} score {r['score']:6.2f}  delta {r['delta']:+6.2f} = ask {p['ask']:+6.2f}"
              f" + new over-ask {p['new_over']:+6.2f} + rest {p['rest']:+6.2f}  |  over-ask {r['over_ask']}"
              f" (new {r['new_over_ask']}, base got {r['base_score_on_new_over_ask']} of them)"
              f"  ceiling {r['ceiling_without_new_over_ask']:.2f}")
    if a.json:
        write_json(ROOT / a.json, out)


if __name__ == "__main__":
    main()
