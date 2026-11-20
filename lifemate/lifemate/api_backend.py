"""Agent backend on a hosted chat API (Meta Model API, OpenAI-compatible /chat/completions). Reference runs only.

Why: the public leaderboard also lists an "APIs/Others" column (reference only; ranking uses small models). A run
with a hosted model on the same pipeline (same ASR text, same prompt, same agent loop and guards) shows how much of
the gap to the top is the 4B model and how much is the rest. Never part of the Docker image: the private test runs
offline. Outputs on public_test are never used for training (no pseudo-labels).

The agent builds Qwen ChatML strings; this backend turns them back into chat messages, sends them, and returns the
reply text, which the agent parses for <tool_call> blocks as usual.

Money: every request is appended to a usage ledger in gen/ (git-ignored). A request is refused (empty reply, which
ends the sample) once this run's ledger reached `max_usd` or all ledgers in that folder together reached
`total_usd` (Anh's limit: 30 USD for all API use; more only after asking him). Replies are cached by request, so a
rerun after a crash costs nothing for steps already done and gives the same text.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from . import runinfo

# USD per million tokens (input, output); reasoning tokens are billed as output. Meta Model API, standard tier
# (content not used for training). Same table as lifemate.synth; the contributor tier is refused.
PRICES = {"muse-spark-1.3": (1.25, 4.25), "muse-wonder-1.0": (4.0, 20.0)}
DEFAULT_BASE_URL = "https://api.meta.ai/v1"

_BLOCK = re.compile(r"<\|im_start\|>(system|user|assistant)\n(.*?)<\|im_end\|>\n", re.S)


def chatml_to_messages(prompt: str) -> list[dict]:
    """Inverse of prompt.to_chatml for a prompt ending in the generation prompt '<|im_start|>assistant\\n'."""
    tail = "<|im_start|>assistant\n"
    if not prompt.endswith(tail):
        raise ValueError("prompt must end with the assistant generation prompt")
    body = prompt[: -len(tail)]
    msgs = [{"role": r, "content": c} for r, c in _BLOCK.findall(body)]
    if "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in msgs) != body:
        raise ValueError("prompt is not plain ChatML")
    return msgs


def ledger_usd(path: Path) -> float:
    if not path.exists():
        return 0.0
    return sum(json.loads(line)["usd"] for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def total_spent(folder: Path) -> float:
    """All API ledgers in the folder (synthetic data and agent runs): what the API has cost so far."""
    return sum(ledger_usd(p) for p in sorted(folder.glob("*_usage.jsonl")))


class ChatAPIBackend:
    def __init__(self, model: str, ledger: str | Path, cache: str | Path, max_usd: float, total_usd: float = 30.0,
                 effort: str = "minimal", base_url: str = DEFAULT_BASE_URL, timeout: float = 300, purpose: str = ""):
        if "contributor" in model:
            raise SystemExit("contributor-tier models may train on prompts; prompts here carry competition files")
        if model not in PRICES:
            raise SystemExit(f"no price for {model!r}; add it to PRICES first (the budget cap needs it)")
        self.key = os.environ.get("MODEL_API_KEY") or os.environ.get("META_API_KEY")
        if not self.key:
            raise SystemExit("no API key: `set -a; source ~/.zac_meta_env; set +a` first")
        self.model, self.effort, self.price = model, effort, PRICES[model]
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.ledger, self.cache_path = Path(ledger), Path(cache)
        self.max_usd, self.total_usd, self.timeout, self.purpose = max_usd, total_usd, timeout, purpose
        self.lock = threading.Lock()
        self.cache: dict[str, str] = {}
        if self.cache_path.exists():
            for line in self.cache_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.cache[r["key"]] = r["text"]
        self.run_usd = ledger_usd(self.ledger)  # this run's ledger, rebuilt on resume
        self.all_usd = total_spent(self.ledger.parent) if self.ledger.parent.exists() else 0.0
        self.stats = {"requests": 0, "cache_hits": 0, "refused": 0, "failed": 0}

    def _key(self, messages: list[dict]) -> str:
        blob = json.dumps([self.model, self.effort, messages], ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def generate(self, prompt: str, deadline: float | None = None) -> str:
        """Reply text. With a deadline (time.monotonic()), stops waiting at it and returns "". Returns "" when the
        budget is used up or the request keeps failing (the agent then ends the sample)."""
        messages = chatml_to_messages(prompt)
        key = self._key(messages)
        with self.lock:
            if key in self.cache:
                self.stats["cache_hits"] += 1
                return self.cache[key]
            if self.run_usd >= self.max_usd or self.all_usd >= self.total_usd:
                self.stats["refused"] += 1
                return ""
        body = {"model": self.model, "messages": messages, "reasoning_effort": self.effort, "temperature": 0, "seed": 0}
        req = urllib.request.Request(self.url, json.dumps(body).encode(), {
            "Content-Type": "application/json", "Authorization": f"Bearer {self.key}"})
        delay, resp, t0 = 2.0, None, time.time()
        for attempt in range(6):
            timeout = self.timeout if deadline is None else deadline - time.monotonic()
            if timeout <= 0.05:
                return ""
            try:
                with urllib.request.urlopen(req, timeout=min(self.timeout, timeout)) as r:
                    resp = json.loads(r.read())
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < 5:
                    time.sleep(float(e.headers.get("Retry-After") or delay) + random.random())
                    delay *= 2
                    continue
                with self.lock:
                    self.stats["failed"] += 1
                print(json.dumps({"api_error": e.code, "body": e.read().decode(errors="replace")[:300]}), flush=True)
                return ""
            except (TimeoutError, urllib.error.URLError, ConnectionError) as e:
                if attempt < 5 and (deadline is None or deadline - time.monotonic() > delay):
                    time.sleep(delay)
                    delay *= 2
                    continue
                with self.lock:
                    self.stats["failed"] += 1
                print(json.dumps({"api_error": "network", "detail": str(e)[:200]}), flush=True)
                return ""
        u = resp.get("usage") or {}
        pin, pout = u.get("prompt_tokens", 0), u.get("completion_tokens", 0)
        usd = (pin * self.price[0] + pout * self.price[1]) / 1e6
        text = resp["choices"][0]["message"].get("content") or ""
        with self.lock:
            self.stats["requests"] += 1
            self.run_usd += usd
            self.all_usd += usd
            self.ledger.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ledger, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "time": runinfo.now(), "purpose": self.purpose, "model": self.model, "effort": self.effort,
                    "prompt_tokens": pin, "cached_tokens": (u.get("prompt_tokens_details") or {}).get("cached_tokens"),
                    "completion_tokens": pout,
                    "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                    "finish": resp["choices"][0].get("finish_reason"),
                    "seconds": round(time.time() - t0, 1), "usd": round(usd, 6)}) + "\n")
            self.cache[key] = text
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"key": key, "text": text}, ensure_ascii=False) + "\n")
        return text

    def summary(self) -> dict:
        return {"model": self.model, "effort": self.effort, "run_usd": round(self.run_usd, 4),
                "all_ledgers_usd": round(self.all_usd, 4), "max_usd": self.max_usd, "total_usd": self.total_usd,
                **self.stats}
