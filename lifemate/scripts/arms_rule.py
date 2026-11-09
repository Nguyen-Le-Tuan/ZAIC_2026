"""Apply the rule written before the 09-10/11 cloud arms (cloud/arms_2026-11-09_models_d2.txt header,
docs/RANKING_FINAL_WEEK_2026-11-08.md section 5) to their dev_lao scores, and write the decision that
scripts/brother_run.sh uses to choose what to train on all train samples (stage 2).

  .venv/bin/python scripts/arms_rule.py --arms cloud/arms_2026-11-09_models_d2.txt --json runs/arms_decision.json

Arm = TAG without its _s<seed> suffix. For every arm: mean over its finished seeds of runs/sft_<TAG>_score.json
(audio_text) and runs/sft_<TAG>_asr_score.json (PhoWhisper-ft text), and a paired bootstrap of its per-sample mean
against the parity arm (rows files, same 262 dev_lao ids).
Baseline = mean of the parity arm's seeds on this machine together with the earlier runs of the same recipe (--hist).
An arm wins when it has --min-seeds finished seeds, asr mean >= baseline asr + --margin-asr, and audio_text mean >=
baseline audio_text - --margin-clean. Several winners: the highest asr mean, except that a winner listed earlier in
--prefer (fewer changes to the submitted system) is taken when it is within --tie of the best.
fallback: when the winner uses another base model family than the submitted one (Qwen3.5, whose parameter count still
needs BTC's confirmation), the best other winner, if any.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path


def parse_arms(path: Path) -> dict[str, dict]:
    """{TAG: {KEY: value}} for the train lines of an arms file."""
    out = {}
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line.startswith("train "):
            continue
        kv = dict(x.split("=", 1) for x in line.split()[1:])
        out[kv["TAG"]] = kv
    return out


def arm_of(tag: str) -> str:
    return re.sub(r"_s\d+$", "", tag)


def load_score(runs: Path, tag: str) -> float | None:
    p = runs / f"sft_{tag}_score.json"
    return json.loads(p.read_text())["score"] if p.exists() else None


def load_rows(runs: Path, tag: str) -> dict[str, float] | None:
    p = runs / f"sft_{tag}_rows.jsonl"
    if not p.exists():
        return None
    return {r["id"]: 100 * r["score"] for r in map(json.loads, p.read_text().splitlines())}


def bootstrap(diffs: list[float], n: int = 10000, seed: int = 0) -> tuple[float, float]:
    rng = random.Random(seed)
    k = len(diffs)
    means = sorted(sum(diffs[rng.randrange(k)] for _ in range(k)) / k for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", required=True)
    ap.add_argument("--runs", default="runs")
    ap.add_argument("--parity", default="a0_q4b4_lao", help="arm name (TAG without _s<seed>) of the submitted recipe")
    ap.add_argument("--hist", default="53.40:41.30,53.73:40.81,49.37:41.18",
                    help="earlier runs of the parity recipe on other machines, audio_text:asr pairs")
    ap.add_argument("--margin-asr", type=float, default=3.0)
    ap.add_argument("--margin-clean", type=float, default=2.0)
    ap.add_argument("--min-seeds", type=int, default=2)
    ap.add_argument("--prefer", default="a3_q4b4_d2_lao,a2_q4bthink_d2_lao,a1_q35t_lao")
    ap.add_argument("--tie", type=float, default=1.0)
    ap.add_argument("--json")
    a = ap.parse_args()
    runs = Path(a.runs)
    cfg = parse_arms(Path(a.arms))
    arms: dict[str, dict] = {}
    for tag, kv in cfg.items():
        arms.setdefault(arm_of(tag), {"tags": [], "config": {k: v for k, v in kv.items() if k in ("MODEL", "THOUGHTS", "LORA_TARGETS")}})
        arms[arm_of(tag)]["tags"].append(tag)
    if a.parity not in arms:
        sys.exit(f"no parity arm {a.parity!r} in {a.arms}")

    def summary(name: str) -> dict:
        tags = arms[name]["tags"]
        done = [t for t in tags if load_score(runs, t) is not None and load_score(runs, f"{t}_asr") is not None]
        clean = [load_score(runs, t) for t in done]
        asr = [load_score(runs, f"{t}_asr") for t in done]
        return {"tags": tags, "finished": done, "clean": clean, "asr": asr,
                "clean_mean": sum(clean) / len(clean) if clean else None,
                "asr_mean": sum(asr) / len(asr) if asr else None, "config": arms[name]["config"]}

    par = summary(a.parity)
    if not par["finished"]:
        sys.exit("the parity arm has no finished seed: nothing to compare with")
    hist = [tuple(map(float, x.split(":"))) for x in a.hist.split(",") if x]
    base_clean = (sum(par["clean"]) + sum(h[0] for h in hist)) / (len(par["clean"]) + len(hist))
    base_asr = (sum(par["asr"]) + sum(h[1] for h in hist)) / (len(par["asr"]) + len(hist))
    par_rows = [load_rows(runs, f"{t}_asr") for t in par["finished"]]
    par_rows = [r for r in par_rows if r]
    out = {"baseline": {"clean": round(base_clean, 2), "asr": round(base_asr, 2), "parity_runs": par["finished"],
                        "hist": hist}, "rule": vars(a), "arms": {}, "winner": None, "fallback": None}
    winners = []
    print(f"baseline (parity {par['finished']} + {len(hist)} earlier runs): audio_text {base_clean:.2f} | "
          f"PhoWhisper-ft {base_asr:.2f}; win: asr >= {base_asr + a.margin_asr:.2f} and audio_text >= "
          f"{base_clean - a.margin_clean:.2f}, {a.min_seeds} seeds")
    print(f"{'arm':<22} {'seeds':>5} {'audio_text':>11} {'ASR text':>9} {'d_asr vs parity [95% CI]':>28}  verdict")
    for name in arms:
        s = summary(name)
        ci = None
        rows = [load_rows(runs, f"{t}_asr") for t in s["finished"]]
        rows = [r for r in rows if r]
        if name != a.parity and rows and par_rows:
            ids = sorted(set.intersection(*(set(r) for r in rows + par_rows)))
            diffs = [sum(r[i] for r in rows) / len(rows) - sum(p[i] for p in par_rows) / len(par_rows) for i in ids]
            if diffs:
                ci = (sum(diffs) / len(diffs), *bootstrap(diffs))
        passes = (name != a.parity and len(s["finished"]) >= a.min_seeds and s["asr_mean"] is not None
                  and s["asr_mean"] >= base_asr + a.margin_asr and s["clean_mean"] >= base_clean - a.margin_clean)
        verdict = "parity" if name == a.parity else ("WIN" if passes else
                  ("not enough seeds" if len(s["finished"]) < a.min_seeds else "no"))
        if passes:
            winners.append(name)
        cm = f"{s['clean_mean']:.2f}" if s["clean_mean"] is not None else "-"
        am = f"{s['asr_mean']:.2f}" if s["asr_mean"] is not None else "-"
        cs = f"{ci[0]:+.2f} [{ci[1]:+.2f}; {ci[2]:+.2f}]" if ci else "-"
        print(f"{name:<22} {len(s['finished']):>5} {cm:>11} {am:>9} {cs:>28}  {verdict}")
        out["arms"][name] = {**s, "delta_asr_vs_parity": ci, "passes": passes, "verdict": verdict}
    if winners:
        best = max(winners, key=lambda n: out["arms"][n]["asr_mean"])
        top = out["arms"][best]["asr_mean"]
        order = [p for p in a.prefer.split(",") if p in winners and out["arms"][p]["asr_mean"] >= top - a.tie]
        winner = order[0] if order else best
        out["winner"] = winner
        fam = lambda n: "qwen3.5" if "Qwen3.5" in out["arms"][n]["config"].get("MODEL", "") else "qwen3"  # noqa: E731
        if fam(winner) != "qwen3":
            others = [n for n in winners if fam(n) == "qwen3"]
            out["fallback"] = max(others, key=lambda n: out["arms"][n]["asr_mean"]) if others else None
    print(f"winner: {out['winner']} | fallback: {out['fallback']}")
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
