"""Run the agent on a split and write submission.jsonl (+ optional traces).

Text sources:
  --text oracle   use audio_text (train only): measures the agent alone
  --text asr      use an ASR file (jsonl lines {"audio": "audio/<id>/<file>.wav", "text": ...}) from the ASR stage

Examples:
  python -m lifemate.infer --split train --ids splits/dev_random.txt --text oracle --backend oracle
  python -m lifemate.infer --split train --ids splits/dev_random.txt --text oracle --backend openai \
      --model Qwen/Qwen3-4B-Instruct-2507 --workers 16 --out runs/zs_dev.jsonl
"""
from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .agent import Agent, HFBackend, OpenAICompletionsBackend, OracleBackend, PrefixBackend, VLLMBackend
from .data import DEFAULT_ROOT, catalog_tools, load_catalog, load_jsonl, load_split, write_jsonl, zaic_tools


def texts_for(item: dict, source: str, asr: dict | None) -> tuple[str, list[str]]:
    users = [h for h in item.get("history", []) if h["role"] == "user"]
    if source == "oracle":
        return item["audio_text"], [h["audio_text"] for h in users]
    return asr[item["audio"]], [asr[h["audio"]] for h in users]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="train")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--ids", help="file with sample ids to run (default: all)")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--text", choices=["oracle", "asr"], default="oracle")
    ap.add_argument("--asr-file")
    ap.add_argument("--backend", choices=["oracle", "openai", "vllm", "hf"], default="oracle")
    ap.add_argument("--model", default="Qwen/Qwen3-4B-Instruct-2507")
    ap.add_argument("--adapter", help="LoRA adapter dir (hf backend)")
    ap.add_argument("--load-4bit", action="store_true", help="hf backend: load the base model in 4-bit")
    ap.add_argument("--assistant-prefix", default="", help=r"forced start of each assistant turn, e.g. '<think>\n\n</think>\n\n' for zero-shot hybrid Qwen3")
    ap.add_argument("--base-url", default="http://localhost:8000/v1")
    ap.add_argument("--workers", type=int, default=1, help=">1 only with --backend openai (dev runs; final runs use 1)")
    ap.add_argument("--time-budget", type=float, default=25.0)
    ap.add_argument("--out", default="runs/submission.jsonl")
    ap.add_argument("--trace")
    a = ap.parse_args()

    zt = zaic_tools(a.split, a.root)
    cat = load_catalog(a.split, a.root)
    tools, apps = catalog_tools(cat), {x["id"]: x for x in cat["apps"]}
    items = load_split(a.split, a.root)
    if a.ids:
        keep = set(Path(a.ids).read_text().split())
        items = [s for s in items if s["id"] in keep]
    items = items[: a.limit] if a.limit else items
    asr = {r["audio"]: r["text"] for r in load_jsonl(a.asr_file)} if a.text == "asr" else None

    shared = None
    if a.backend == "openai":
        shared = OpenAICompletionsBackend(a.model, a.base_url)
    elif a.backend == "vllm":
        shared = VLLMBackend(a.model)
    elif a.backend == "hf":
        shared = HFBackend(a.model, a.adapter, load_4bit=a.load_4bit)
    if shared is not None and a.assistant_prefix:
        shared = PrefixBackend(shared, a.assistant_prefix.encode().decode("unicode_escape"))

    def infer(item):
        t0 = time.monotonic()
        env = zt.ToolEnv(a.split, item["id"], root=str(a.root))  # exactly one environment per sample
        llm = OracleBackend(item["label"]["tool_calls"]) if a.backend == "oracle" else shared
        user_text, hist = texts_for(item, a.text, asr)
        trace = Agent(llm, tools, apps, time_budget=a.time_budget).run(item, env, user_text, hist, t0=t0)
        row = {"id": item["id"], "tool_calls": env.get_tool_calls(), "state_hash": env.get_state_hash()}
        return row, {"id": item["id"], "text": user_text, **trace}

    if a.workers > 1:
        with ThreadPoolExecutor(a.workers) as pool:
            out = list(pool.map(infer, items))
    else:
        out = [infer(s) for s in items]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(a.out, [r for r, _ in out])
    if a.trace:
        write_jsonl(a.trace, [t for _, t in out])
    secs = [t["seconds"] for _, t in out]
    print(json.dumps({"n": len(out), "out": a.out, "mean_s": round(sum(secs) / max(len(secs), 1), 3), "max_s": max(secs, default=0)}))


if __name__ == "__main__":
    main()
