"""Experiment D phase 2: dev_lao and contrast-set numbers of each arm against B0 and the control, and the keep/drop
criteria of docs/REVIEW_D_2026-10-30.md section 5. Read-only over runs/.

  .venv/bin/python scripts/phase2_report.py --b0 q17b_fit_lao --control q17b_lao_up --arms q17b_lao_d1 q17b_lao_d3 \
      --json runs/phase2_report.json

Ask behaviour on dev_lao, from the predictions and the gold labels:
  gold ask    asked = the prediction calls the ask tool; right = same tool and param as the gold ask
  gold other  over-ask = the prediction calls the ask tool although the gold label does not ask
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate.askpolicy import ASK, ask_type  # noqa: E402
from lifemate.compare import load_run, paired  # noqa: E402
from lifemate.data import catalog_tools, load_catalog, load_jsonl, load_split  # noqa: E402
from lifemate.runinfo import read_ids, write_json  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
HELDOUT = set(json.loads((ROOT / "splits" / "heldout_apps.json").read_text()))
LEAK = "train_1140"  # D-eval-24 item whose label prefix still names a removed word (docs/D_PHASE1B section 4)


def ask_behaviour(tag, ids, S, tools) -> dict:
    pred = {p["id"]: p for p in load_jsonl(ROOT / "runs" / f"sft_{tag}.jsonl")}
    c = Counter()
    for i in ids:
        s, calls = S[i], pred.get(i, {}).get("tool_calls", [])
        asks = [x for x in calls if x["name"] == ASK]
        gold = s["label"]["tool_calls"]
        if gold and gold[-1]["name"] == ASK:
            a = gold[-1]["arguments"]
            grp = f"{ask_type(s, tools) or '?'}/{'held' if a['tool_name'].split('.')[0] in HELDOUT else 'seen'}"
            c[f"ask {grp} n"] += 1
            if asks:
                c[f"ask {grp} asked"] += 1
                pa = asks[-1]["arguments"]
                if pa.get("tool_name") == a["tool_name"] and list(pa.get("params", [])) == list(a["params"]):
                    c[f"ask {grp} right"] += 1
        else:
            kind = "execute" if gold else "out_of_scope"
            c[f"{kind} n"] += 1
            c[f"{kind} over_ask"] += bool(asks)
    return dict(sorted(c.items()))


def contrast(tag, name) -> dict | None:
    p = ROOT / "runs" / f"contrast_{tag}_{name}.jsonl"
    if not p.exists():
        return None
    rows = load_jsonl(p)
    out = {}
    for label, keep in (("all", lambda r: True), ("no_leak", lambda r: not r["id"].startswith(LEAK))):
        rs = [r for r in rows if keep(r)]
        syn = [r for r in rs if r["side"] == "synthetic"]
        by = {}
        for r in rs:
            by.setdefault(r["id"].split("#")[0], []).append(r["behaviour_ok"])
        kinds = Counter(r["kind"] for r in syn)
        out[label] = {"n": len(syn), "synthetic_ok": sum(r["behaviour_ok"] for r in syn),
                      "synthetic_ok_by_kind": {k: f"{sum(r['behaviour_ok'] for r in syn if r['kind'] == k)}/{n}"
                                               for k, n in sorted(kinds.items())},
                      "origin_ok": sum(r["behaviour_ok"] for r in rs if r["side"] == "origin"),
                      "flip_correct": sum(len(v) == 2 and all(v) for v in by.values())}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--b0", default="q17b_fit_lao")
    ap.add_argument("--control", default="q17b_lao_up")
    ap.add_argument("--arms", nargs="+", default=["q17b_lao_d1", "q17b_lao_d3"])
    ap.add_argument("--json")
    a = ap.parse_args()
    S = {s["id"]: s for s in load_split("train")}
    tools = catalog_tools(load_catalog("train"))
    ids = read_ids(ROOT / "splits" / "dev_lao.txt")
    tags = [t for t in [a.b0, a.control, *a.arms] if (ROOT / "runs" / f"sft_{t}_rows.jsonl").exists()]
    runs = {t: load_run(str(ROOT / "runs" / f"sft_{t}")) for t in tags}
    ask_ids = [i for i in ids if runs[a.b0]["rows"][i]["category"] == "ask_missing"]
    res = {"ids": len(ids), "ask_ids": len(ask_ids), "runs": {}}
    for t in tags:
        score = json.loads((ROOT / "runs" / f"sft_{t}_score.json").read_text())
        r = {"score": score["score"], "by_category": score["by_category"], "ask": ask_behaviour(t, ids, S, tools),
             "contrast": {n: contrast(t, n) for n in ("dv1eval", "pilot")}}
        for ref in (a.b0, a.control):
            if ref in runs and ref != t:
                r[f"vs_{ref}"] = {"all": paired(runs[ref], runs[t], ids), "ask": paired(runs[ref], runs[t], ask_ids)}
        res["runs"][t] = r
    b0 = res["runs"][a.b0]
    for t in a.arms:
        if t not in res["runs"]:
            continue
        r = res["runs"][t]
        ask_d = r["by_category"]["ask_missing"]["score"] - b0["by_category"]["ask_missing"]["score"]
        ctl = res["runs"].get(a.control)
        ask_c = r["by_category"]["ask_missing"]["score"] - ctl["by_category"]["ask_missing"]["score"] if ctl else None
        over = r["ask"].get("execute over_ask", 0) + r["ask"].get("out_of_scope over_ask", 0)
        over0 = b0["ask"].get("execute over_ask", 0) + b0["ask"].get("out_of_scope over_ask", 0)
        dv = (r["contrast"]["dv1eval"] or {}).get("all")
        r["criteria"] = {
            "ask_vs_b0_ge_10": [round(ask_d, 2), ask_d >= 10],
            "ask_vs_control_ge_5": [round(ask_c, 2) if ask_c is not None else None, ask_c is not None and ask_c >= 5],
            "dev_lao_ci_excludes_0": [[round(x, 2) for x in r[f"vs_{a.b0}"]["all"]["ci95"]], r[f"vs_{a.b0}"]["all"]["ci95"][0] > 0],
            "over_ask_increase_le_3": [over - over0, over - over0 <= 3],
            "d_eval_flip_ge_50pct": [f"{dv['flip_correct']}/{dv['n']}" if dv else None, bool(dv) and dv["flip_correct"] >= dv["n"] / 2],
        }
        r["keep_D"] = all(v[1] for v in r["criteria"].values())
    print(json.dumps(res, ensure_ascii=False, indent=1))
    if a.json:
        write_json(a.json, res)


if __name__ == "__main__":
    main()
