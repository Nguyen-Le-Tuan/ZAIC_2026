"""Optional tool parameters that the train labels (almost) never fill, as a JSON list for `infer --drop-params`.

Why: a call matches gold only when every non-fuzzy argument is identical, so an optional argument the labels leave
out (alarm.create.repeat: 0 of 193 gold calls) makes a call count as wrong even when the final state is right. A
zero-shot model fills such arguments; the SFT models learned to leave them out (JOURNAL entry 78). Only train labels
are read; tools never seen in train get no rule.

  python -m lifemate.rare_params --exclude splits/dev_random.txt splits/dev_lao.txt --out runs/rare_params_fit.json
  python -m lifemate.rare_params --out runs/rare_params_train.json        # all train, for public runs
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from .data import DEFAULT_ROOT, catalog_tools, load_catalog, load_split


def rare_params(items, tools: dict, max_rate: float = 0.05, min_calls: int = 5) -> list[dict]:
    seen, filled = Counter(), Counter()
    for s in items:
        for c in s["label"]["tool_calls"]:
            p = tools.get(c["name"], {}).get("parameters", {})
            for k in p.get("properties", {}):
                if k not in p.get("required", []):
                    seen[(c["name"], k)] += 1
                    filled[(c["name"], k)] += k in c["arguments"]
    return [{"tool": t, "param": k, "filled": filled[(t, k)], "calls": n}
            for (t, k), n in sorted(seen.items()) if n >= min_calls and filled[(t, k)] / n < max_rate]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--exclude", nargs="*", default=[], help="id files whose samples are left out (dev splits)")
    ap.add_argument("--max-rate", type=float, default=0.05)
    ap.add_argument("--min-calls", type=int, default=5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    drop = {i for f in a.exclude for i in Path(f).read_text().split()}
    items = [s for s in load_split("train", a.root) if s["id"] not in drop]
    rows = rare_params(items, catalog_tools(load_catalog("train", a.root)), a.max_rate, a.min_calls)
    Path(a.out).write_text(json.dumps({"samples": len(items), "excluded": sorted(a.exclude), "max_rate": a.max_rate,
                                       "min_calls": a.min_calls, "params": rows}, ensure_ascii=False, indent=1))
    print(json.dumps({"samples": len(items), "params": len(rows), "out": a.out}))


if __name__ == "__main__":
    main()
