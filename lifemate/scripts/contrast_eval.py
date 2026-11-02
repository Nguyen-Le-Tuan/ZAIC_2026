"""Contrast-set evaluation for experiment D: run a checkpoint on each synthetic sample AND on its origin sample
(same context and history, only the request text differs) and check that the behaviour flips as the labels say.

  .venv/bin/python scripts/contrast_eval.py --samples gen/d_fit_lao.jsonl --adapter ckpt/q17b_fit_lao/final \
      --out runs/contrast_q17b_fit_lao_pilot.jsonl

Per item: score (official formula, gold hash from replaying the label) and behaviour:
  ask label      -> correct if the model asks for exactly that tool and param
  execute label  -> correct if the model makes the label's last call (B-specific write) and does not ask
A pair is "flip-correct" when both the synthetic item and its origin are behaviour-correct.
Never evaluate a checkpoint on synthetic samples it was trained on: keep a held-out part of D for this.
"""
import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate import runinfo  # noqa: E402
from lifemate.agent import Agent, HFBackend  # noqa: E402
from lifemate.askpolicy import ASK  # noqa: E402
from lifemate.data import DEFAULT_ROOT, catalog_tools, fuzzy_params, load_catalog, load_jsonl, load_split, write_jsonl, zaic_tools  # noqa: E402
from lifemate.scorer import score_sample  # noqa: E402


def behaviour_ok(pred_calls, label_calls) -> bool:
    last = label_calls[-1]
    asks = [c for c in pred_calls if c["name"] == ASK]
    if last["name"] == ASK:
        return any(a["arguments"].get("tool_name") == last["arguments"]["tool_name"]
                   and a["arguments"].get("params") == last["arguments"]["params"] for a in asks)
    return not asks and any(c["name"] == last["name"] and c["arguments"] == last["arguments"] for c in pred_calls)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-1.7B")
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    runinfo.refuse_existing(a.out, overwrite=a.overwrite)

    root = DEFAULT_ROOT
    S = {s["id"]: s for s in load_split("train", root)}
    cat = load_catalog("train", root)
    tools, apps, fz = catalog_tools(cat), {x["id"]: x for x in cat["apps"]}, fuzzy_params(cat)
    zt = zaic_tools("train", root)
    llm = HFBackend(a.model, a.adapter)
    rows = []
    for syn in load_jsonl(a.samples):
        origin = S[syn["_origin"]]
        for side, item in (("synthetic", syn), ("origin", origin)):
            label = item["label"]["tool_calls"]
            ref = zt.ToolEnv("train", origin["id"], root=str(root))  # gold hash: replay the label
            for c in label:
                ref.call(c["name"], c["arguments"])
            env = zt.ToolEnv("train", origin["id"], root=str(root))
            t0 = time.monotonic()
            hist = [h["audio_text"] for h in origin.get("history", []) if h["role"] == "user"]
            trace = Agent(llm, tools, apps).run(item, env, item["audio_text"], hist, t0=t0)
            pred = env.get_tool_calls()
            rows.append({"id": syn["id"], "kind": syn["_kind"], "side": side,
                         "label_asks": label[-1]["name"] == ASK,
                         "score": score_sample(pred, env.get_state_hash(), label, ref.get_state_hash(), fz),
                         "behaviour_ok": behaviour_ok(pred, label), "pred": pred, "seconds": trace["seconds"]})
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(a.out, rows)

    summ = defaultdict(lambda: Counter())
    pairs = defaultdict(dict)
    for r in rows:
        k = f"{r['kind']}/{r['side']}"
        summ[k]["n"] += 1
        summ[k]["behaviour_ok"] += r["behaviour_ok"]
        summ[k]["score_sum_x100"] += round(100 * r["score"])
        pairs[r["id"]][r["side"]] = r["behaviour_ok"]
    flip = Counter()
    for i, p in pairs.items():
        kind = i and next(r["kind"] for r in rows if r["id"] == i)
        flip[kind] += p.get("synthetic", False) and p.get("origin", False)
        flip["all"] += p.get("synthetic", False) and p.get("origin", False)
    out = {"by_kind_side": {k: {"n": v["n"], "behaviour_ok": v["behaviour_ok"], "mean_score": round(v["score_sum_x100"] / v["n"], 1)}
                            for k, v in sorted(summ.items())},
           "flip_correct_pairs": dict(flip), "pairs": len(pairs)}
    runinfo.write_json(Path(a.out).with_suffix(".summary.json"), {
        "created": runinfo.now(), "args": vars(a), "samples_sha256": runinfo.sha256_file(a.samples),
        "adapter_sha256": runinfo.sha256_dir(a.adapter), "git": runinfo.git_state(), "env": runinfo.env_info(), **out})
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
