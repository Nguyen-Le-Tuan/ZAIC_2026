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
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import runinfo
from .agent import Agent, HFBackend, OpenAICompletionsBackend, OracleBackend, PrefixBackend, VLLMBackend
from .data import DEFAULT_ROOT, catalog_tools, load_catalog, load_jsonl, load_split, write_jsonl, zaic_tools
from .prompt import build_messages, to_chatml
from .seeding import seed_everything

WARMUP_TEXT = "Xin chào."


def warmup_prompt(item: dict, tools: dict, apps: dict) -> str:
    """A full-length prompt for the untimed warm-up generation: the system prompt (rules, profile, calendar, tools)
    built from the sample's `context` only, plus a fixed greeting. No audio, text, history or label of the sample
    is used, and no ToolEnv is created, so the one-environment-per-sample rule is untouched."""
    return to_chatml(build_messages({"context": item["context"], "history": []}, WARMUP_TEXT, [], tools, apps))


def texts_for(item: dict, source: str, asr: dict | None) -> tuple[str, list[str]]:
    users = [h for h in item.get("history", []) if h["role"] == "user"]
    if source == "oracle":
        return item["audio_text"], [h["audio_text"] for h in users]
    return asr[item["audio"]], [asr[h["audio"]] for h in users]


def asr_seconds_for(item: dict, secs: dict) -> float:
    """ASR decode seconds of every wav of the sample (final turn + user turns of the history)."""
    return sum(secs.get(p, 0.0) for p in [item["audio"]] + [h["audio"] for h in item.get("history", []) if h["role"] == "user"])


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
    ap.add_argument("--time-budget", type=float, default=25.0,
                    help="seconds per sample, ASR included (with --text asr, the ASR file's per-wav seconds count)")
    ap.add_argument("--max-tokens", type=int, default=512, help="cap on generated tokens per step (gold steps: max 200)")
    ap.add_argument("--no-id-guard", action="store_true", help="do not block write calls with IDs never shown")
    ap.add_argument("--search-guard", action="store_true",
                    help="retry an empty filtered read once with looser arguments, and stop after 3 steps in a row that "
                         "only repeat answered reads (lifemate.agent docstring; off = the 05/11 system)")
    ap.add_argument("--arg-rules", action="store_true",
                    help="rewrite each call's arguments with lifemate.agent.safe_args (R0-R3: drop args outside the schema, "
                         "ISO/HH:MM time formats as the schema says, ask only required or one-of params) before it runs")
    ap.add_argument("--no-warmup", action="store_true",
                    help="skip the untimed warm-up generation after loading (hf/vllm backends)")
    ap.add_argument("--out", default="runs/submission.jsonl")
    ap.add_argument("--trace")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--overwrite", action="store_true", help="allow replacing an existing --out/--trace")
    a = ap.parse_args()

    meta_path = Path(a.out).with_suffix(".meta.json")
    runinfo.refuse_existing(a.out, a.trace, meta_path, overwrite=a.overwrite)
    seed_everything(a.seed)
    started = runinfo.now()
    zt = zaic_tools(a.split, a.root)
    cat = load_catalog(a.split, a.root)
    tools, apps = catalog_tools(cat), {x["id"]: x for x in cat["apps"]}
    items = load_split(a.split, a.root)
    if a.ids:
        keep = set(Path(a.ids).read_text().split())
        items = [s for s in items if s["id"] in keep]
    items = items[: a.limit] if a.limit else items
    asr_rows = load_jsonl(a.asr_file) if a.text == "asr" else []
    asr = {r["audio"]: r["text"] for r in asr_rows} if a.text == "asr" else None
    asr_secs = {r["audio"]: float(r.get("seconds", 0.0)) for r in asr_rows}

    shared = None
    tl = time.monotonic()
    if a.backend == "openai":
        shared = OpenAICompletionsBackend(a.model, a.base_url, max_tokens=a.max_tokens)
    elif a.backend == "vllm":
        shared = VLLMBackend(a.model, max_tokens=a.max_tokens)
    elif a.backend == "hf":
        shared = HFBackend(a.model, a.adapter, max_tokens=a.max_tokens, load_4bit=a.load_4bit)
    if shared is not None and a.assistant_prefix:
        shared = PrefixBackend(shared, a.assistant_prefix.encode().decode("unicode_escape"))
    load_s = round(time.monotonic() - tl, 3) if shared is not None else None
    if load_s is not None:
        print(json.dumps({"load_s": load_s}), flush=True)
    warmup_s = None
    if shared is not None and hasattr(shared, "warmup") and items and not a.no_warmup:
        tw = time.monotonic()
        shared.warmup(warmup_prompt(items[0], tools, apps))
        warmup_s = round(time.monotonic() - tw, 3)
        print(json.dumps({"warmup_s": warmup_s}), flush=True)

    def infer(item):
        t0 = time.monotonic()
        env = zt.ToolEnv(a.split, item["id"], root=str(a.root))  # exactly one environment per sample
        llm = OracleBackend(item["label"]["tool_calls"]) if a.backend == "oracle" else shared
        user_text, hist = texts_for(item, a.text, asr)
        spent = asr_seconds_for(item, asr_secs) if a.text == "asr" else 0.0
        agent = Agent(llm, tools, apps, time_budget=a.time_budget, id_guard=not a.no_id_guard,
                      search_relax=a.search_guard, max_repeat_steps=3 if a.search_guard else 0,
                      arg_rules=a.arg_rules)
        trace = agent.run(item, env, user_text, hist, t0=t0, spent=spent)
        row = {"id": item["id"], "tool_calls": env.get_tool_calls(), "state_hash": env.get_state_hash()}
        # organisers' `time` (guide p. 6-7): integer ms of the sample, before its audio is read to its result;
        # here the sample's ASR seconds (from the ASR file) plus this process's seconds from t0 to now
        row["time"] = int((spent + time.monotonic() - t0) * 1000)
        extra = {"asr_seconds": round(spent, 3)} if a.text == "asr" else {}
        return row, {"id": item["id"], "text": user_text, **extra, **trace}

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
    timing = {"mean_s": round(sum(secs) / max(len(secs), 1), 3), "p50_s": round(runinfo.percentile(secs, .5), 3),
              "p95_s": round(runinfo.percentile(secs, .95), 3), "max_s": max(secs, default=0)}
    adapter = None
    if a.adapter:
        adapter = {"path": a.adapter, "sha256": runinfo.sha256_dir(a.adapter)}
    runinfo.write_json(meta_path, {
        "kind": "infer", "started": started, "finished": runinfo.now(), "args": vars(a),
        "ids": runinfo.ids_digest(s["id"] for s in items), "ids_file_sha256": runinfo.sha256_file(a.ids) if a.ids else None,
        "model": a.model if a.backend != "oracle" else None, "adapter": adapter, "backend": a.backend,
        "code_sha256": runinfo.code_digest(), "git": runinfo.git_state(), "env": runinfo.env_info(),
        "timing": timing, "load_s": load_s, "warmup_s": warmup_s, "stops": dict(Counter(t["stop"] for _, t in out)),
        "id_guard_blocked": sum(len(s.get("blocked", [])) for _, t in out for s in t["steps"]),
        "search_relaxed": sum(len(s.get("relaxed", [])) for _, t in out for s in t["steps"]),
        "note": "seconds are wall time per sample on this machine (agent only, no ASR); not the A30 limit. "
                "With --text asr the sample's ASR seconds (trace asr_seconds) also count against --time-budget. "
                "warmup_s: the one untimed generation after loading, counted in no sample. load_s: building the "
                "backend (model load). Rows carry time = int ms of ASR seconds + this process's seconds per sample"})
    print(json.dumps({"n": len(out), "out": a.out, **timing}))


if __name__ == "__main__":
    main()
