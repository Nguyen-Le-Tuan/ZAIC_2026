"""What /code/predict.sh and /code/predict_notebook.ipynb share (organisers' Docker guide of 04/11/2026; summary with
page numbers in docs/BTC_DOCKER_GUIDE_2026-11-06.md on main).

- DEFAULTS: the submitted system. The organisers set no environment variables, so these values are the defaults of
  docker/predict.sh and of the notebook (tests/test_submit.py checks that the shell defaults agree).
- find_split: the split folder under /data, found as in the organisers' notebook (the subfolder that holds
  <name>_tools_catalog.json); /data/private_test at grading.
- Runner: one sample at a time, as the notebook must run it: read the sample's wavs, ASR, then the agent loop on the
  sample's one ToolEnv. predict.sh runs the same models and agent as two processes instead (lifemate.asr on every wav,
  then lifemate.infer), the path every scored run used.
- report: the stdout lines predict.sh ends with (model load time, prediction time), in the organisers' wording (p. 12).

  python -m lifemate.submit split --root /data            # prints the split name
  python -m lifemate.submit report --asr-meta W/submission_asr.meta.json --infer-meta W/submission.meta.json \
      --submission /result/submission.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from .agent import Agent
from .asr import read_wav
from .data import catalog_tools, load_catalog, load_jsonl
from .infer import texts_for, warmup_prompt
from .runinfo import percentile

DEFAULTS = {
    "ASR_MODEL": "ckpt/asr_phoft/merged",          # PhoWhisper-large fine-tuned on all train audio, merged
    "ADAPTER": "ckpt/v7q35_avg/final",             # average of the two v7q35 LoRA seeds (4-bit base, all train samples)
    "LLM": "principled-intelligence/Qwen3.5-4B-text-only",  # @efe91c59, from the image's Hugging Face cache (offline)
    "LOAD_4BIT": "1",                              # NF4 base + adapter not merged, as in every scored 4B run
    "TIME_BUDGET": "25",                           # seconds per sample, ASR included
    "WARMUP": "1",                                 # untimed warm-up generation after loading
    "SEED": "0",                                   # = training seed
    "SEARCH_GUARD": "1",                           # 1 = lifemate.infer --search-guard (D5), on in every Qwen3.5 file
}
MAX_TOKENS = 512  # per agent step; lifemate.infer --max-tokens default


def settings(env=None) -> dict:
    """DEFAULTS overridden by environment variables of the same name (empty counts as unset, like ${X:-default}),
    parsed and checked the way scripts/predict.sh checks them."""
    env = os.environ if env is None else env
    s = {k: env.get(k) or v for k, v in DEFAULTS.items()}
    for k in ("LOAD_4BIT", "WARMUP", "SEARCH_GUARD"):
        if s[k] not in ("0", "1"):
            raise ValueError(f"{k} must be 0 or 1, got {s[k]!r}")
    budget = float(s["TIME_BUDGET"])
    if not 0 < budget < 30:
        raise ValueError(f"TIME_BUDGET must be above 0 and below 30, got {budget}")
    return {"asr_model": s["ASR_MODEL"], "adapter": s["ADAPTER"], "llm": s["LLM"], "load_4bit": s["LOAD_4BIT"] == "1",
            "time_budget": budget, "warmup": s["WARMUP"] == "1", "seed": int(s["SEED"]),
            "search_guard": s["SEARCH_GUARD"] == "1"}


def split_candidates(root) -> list[str]:
    root = Path(root)
    return sorted(p.name for p in root.iterdir() if p.is_dir() and (p / f"{p.name}_tools_catalog.json").is_file())


def find_split(root, split: str | None = None) -> str:
    """The split under `root`: a subfolder <name>/ that holds <name>_tools_catalog.json. `split` picks one by name
    (the laptop's data/train+public_test holds two). Without it: private_test when present, else the only one."""
    found = split_candidates(root)
    if split:
        if split not in found:
            raise ValueError(f"{root}: no split {split!r} (found: {', '.join(found) or 'none'})")
        return split
    if "private_test" in found:
        return "private_test"
    if len(found) == 1:
        return found[0]
    raise ValueError(f"{root}: {len(found)} splits ({', '.join(found) or 'none'}); set SPLIT to pick one")


def sample_wavs(item: dict) -> list[str]:
    """The sample's wavs, relative to the split folder: the final turn, then the user turns of the history."""
    return [item["audio"]] + [h["audio"] for h in item.get("history", []) if h["role"] == "user"]


def model_path(lifemate_dir, name: str) -> str:
    """A model given relative to the lifemate folder (ckpt/...) when it exists there, else the name as given
    (absolute path or Hugging Face id)."""
    p = Path(lifemate_dir) / name
    return str(p) if p.exists() else name


class Runner:
    """Loaded ASR model + agent LLM; run() does one sample. Used by the notebook, which times each sample from
    before its ToolEnv and audio to its result (guide p. 17)."""

    def __init__(self, split: str, root, asr, llm, time_budget: float = 25.0, id_guard: bool = True,
                 search_guard: bool = False):
        cat = load_catalog(split, root)
        self.tools, self.apps = catalog_tools(cat), {x["id"]: x for x in cat["apps"]}
        self.split_dir = Path(root) / split
        self.asr, self.llm, self.time_budget, self.id_guard = asr, llm, time_budget, id_guard
        self.search_guard = search_guard  # same switch as lifemate.infer --search-guard

    def warmup(self, item: dict) -> float:
        """Untimed, before the first sample (as predict.sh does): a short ASR decode of silence, then one short
        generation with a full-length prompt built from `item`'s context only (no audio, text or ToolEnv)."""
        t = time.monotonic()
        if hasattr(self.asr, "warmup"):
            self.asr.warmup()
        if hasattr(self.llm, "warmup"):
            self.llm.warmup(warmup_prompt(item, self.tools, self.apps))
        return time.monotonic() - t

    def transcribe(self, item: dict) -> dict[str, str]:
        """{wav path: text} for the sample's wavs, one at a time (= lifemate.asr --batch-size 1)."""
        return {p: self.asr([read_wav(self.split_dir / p)])[0] for p in sample_wavs(item)}

    def run(self, item: dict, env, t1: float) -> dict:
        """One sample on `env`, the ToolEnv the caller created after t1 = time.perf_counter(). The time budget
        counts from t1, so the sample's wav reading and ASR are inside it (in predict.sh they enter as `spent`).
        Returns the trace; its "seconds" is the whole sample (ASR + agent), "asr_seconds" the ASR part."""
        t0 = time.monotonic() - (time.perf_counter() - t1)  # t1 on the agent's clock
        ta = time.monotonic()
        texts = self.transcribe(item)
        asr_s = time.monotonic() - ta
        user_text, hist = texts_for(item, "asr", texts)
        agent = Agent(self.llm, self.tools, self.apps, time_budget=self.time_budget, id_guard=self.id_guard,
                      search_relax=self.search_guard, max_repeat_steps=3 if self.search_guard else 0)
        trace = agent.run(item, env, user_text, hist, t0=t0)
        return {"id": item["id"], "text": user_text, "asr_seconds": round(asr_s, 3), **trace}


def report(asr_meta: dict, infer_meta: dict, rows: list[dict]) -> list[str]:
    """predict.sh's closing stdout lines, worded like the organisers' example (guide p. 12):
    'load model: 2 ms' and 'predict: 634 mẫu, 1128 ms, trung bình 1.8 ms/mẫu'."""
    asr_t = asr_meta.get("timing", {})
    parts = {"ASR": asr_t.get("load_s"), "ASR warm-up": asr_t.get("warmup_s"),
             "LLM": infer_meta.get("load_s"), "LLM warm-up": infer_meta.get("warmup_s")}
    parts = {k: int(v * 1000) for k, v in parts.items() if v is not None}
    detail = ", ".join(f"{k} {v} ms" for k, v in parts.items())
    lines = [f"load model: {sum(parts.values())} ms ({detail or 'no timing found'})"]
    ms = [r["time"] for r in rows if isinstance(r.get("time"), int)]
    n = len(rows)
    budget = (infer_meta.get("args") or {}).get("time_budget")
    over = f", over {budget:g} s: {sum(t > budget * 1000 for t in ms)}" if budget else ""
    lines.append(f"predict: {n} mẫu, {sum(ms)} ms, trung bình {sum(ms) / max(len(ms), 1):.1f} ms/mẫu "
                 f"(sum of the rows' time = ASR + agent of each sample; p50 {int(percentile(ms, .5))} ms, "
                 f"p95 {int(percentile(ms, .95))} ms, max {max(ms, default=0)} ms{over})")
    if len(ms) != n:
        lines.append(f"WARNING: {n - len(ms)} of {n} rows have no integer time")
    return lines


def _read_json(path) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("split", help="print the split folder name under --root")
    sp.add_argument("--root", default="/data")
    sp.add_argument("--split", help="pick this split (must exist under --root)")
    rp = sub.add_parser("report", help="print the model load and prediction times")
    rp.add_argument("--asr-meta", required=True)
    rp.add_argument("--infer-meta", required=True)
    rp.add_argument("--submission", required=True)
    a = ap.parse_args()
    if a.cmd == "split":
        try:
            print(find_split(a.root, a.split))
        except (OSError, ValueError) as e:
            raise SystemExit(f"lifemate.submit split: {e}") from None
    else:
        rows = load_jsonl(a.submission) if Path(a.submission).exists() else []
        print("\n".join(report(_read_json(a.asr_meta), _read_json(a.infer_meta), rows)), flush=True)


if __name__ == "__main__":
    main()
