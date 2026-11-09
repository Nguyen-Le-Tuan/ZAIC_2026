"""Agent loop: LLM proposes tool calls -> guardrails -> env.call -> results back to the LLM -> ...

Guardrails (pure code, no model):
  * env.validate() before every call: schema errors go back to the model as a tool_response but are NOT sent
    to env.call, so they never appear in the submission (rejected calls would count as unmatched).
  * ID guard (lifemate.guard): a write call with an x-ref ID the model has never been shown is not sent to env.call;
    the model gets an error instead, like a schema error. Off with id_guard=False.
  * identical repeated READ calls are answered from the earlier result instead of being called again.
  * time: a sample has `time_budget` seconds in total, including what it spent before the agent (its ASR, `spent`).
    Every generation gets the deadline: the HF backend stops generating at it (max_time) and the OpenAI-compatible
    client stops waiting. No step starts with less than `min_step_seconds` left. Complete calls of a step cut by the
    deadline still run, then the loop stops. The in-process vLLM backend cannot be stopped mid-generation, so there
    only the per-step token cap (max_tokens) bounds a step.
  * stop right after sys.ask_missing_info (always the last call in train gold), after max_steps, or when time runs out.
  * search guard (off by default; search_relax / max_repeat_steps, `--search-guard` in infer.py), measured on the
    05/11 public run (51,16; docs/SYNTH_DATA_PLAN_2026-11-08.md section 1):
      - a READ call with arguments that comes back empty is retried once with looser arguments (relaxed_args). Train
        gold filtered reads come back empty in 4/555 calls, so an empty result almost always means our own filter or
        query was wrong; the public run had 98 such calls in 55 samples, mostly optional filters the model added on
        unseen apps. The retry is a real env.call, so it is in the submission like any other call.
      - after max_repeat_steps steps in a row that only repeat already answered reads, the loop stops. Those steps
        reach no env.call, so the submission is unchanged; only the time is saved (18 public samples looped to
        max_steps this way; no sample that later wrote or asked repeated more than 2 steps in a row).
"""
from __future__ import annotations

import json
import re
import time
import unicodedata
import urllib.error
import urllib.request

from .guard import block_message, unseen_ids
from .prompt import build_messages, render_calls, render_results, to_chatml

_TOOL_CALL = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.S)
_THINK = re.compile(r"<think>.*?</think>", re.S)


def _fold(s: str) -> str:
    """lower-case, diacritics removed, spaces collapsed: the same folding zaic_tools search uses (utils._fold)."""
    t = unicodedata.normalize("NFD", str(s).lower()).replace("đ", "d")
    return " ".join("".join(c for c in t if not unicodedata.combining(c)).split())


# free-text argument names that the relaxer may shorten
_QUERY_KEYS = {"query", "keyword", "keywords", "q", "search", "term", "name", "title"}
# words dropped from the FRONT of a spoken query before retrying ("chị Lan" -> "Lan", "vé ca nhạc X" -> "ca nhạc X")
_QUERY_FILLER = {_fold(w) for w in (
    "tìm", "kiếm", "xem", "mua", "đặt", "vé", "cho", "tôi", "mình", "em", "anh", "chị", "cô", "chú", "bác", "ông",
    "bà", "bạn", "cậu", "dì", "các", "những", "một", "cái", "chiếc", "món", "loại", "sản", "phẩm", "sự", "kiện",
    "buổi", "the", "a", "an")}


def empty_listing(result) -> bool:
    """A read result that found nothing: not an error, at least one list field, and every list field empty."""
    if not isinstance(result, dict) or result.get("ok") is False:
        return False
    lists = [v for v in result.values() if isinstance(v, list)]
    return bool(lists) and all(len(v) == 0 for v in lists)


def relaxed_args(tool: dict, args: dict) -> dict | None:
    """Looser arguments for one retry of a read that came back empty, or None when there is nothing to loosen.
    1) optional arguments were given -> keep only the required ones. This is the gold convention: 1.212/1.599 train
       read calls carry exactly their required arguments.
    2) otherwise, for the first free-text argument (_QUERY_KEYS) with two or more words, drop filler words from its
       front. Nothing to drop -> None (no guessing which words matter)."""
    params = tool.get("parameters", {})
    required = set(params.get("required", []))
    if set(args) - required:
        return {k: v for k, v in args.items() if k in required}
    props = params.get("properties", {})
    for k, v in args.items():
        if k not in _QUERY_KEYS or not isinstance(v, str) or "enum" in props.get(k, {}):
            continue
        words = v.split()
        i = 0
        while i < len(words) - 1 and _fold(words[i]) in _QUERY_FILLER:
            i += 1
        if i:
            return {**args, k: " ".join(words[i:])}
    return None


def parse_tool_calls(text: str) -> tuple[list[dict], list[str]]:
    """-> (calls, errors). A call is {"name": str, "arguments": dict}."""
    text = _THINK.sub("", text)
    calls, errors = [], []
    for raw in _TOOL_CALL.findall(text):
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            errors.append(f"JSON không hợp lệ: {e}")
            continue
        if not isinstance(obj, dict) or not isinstance(obj.get("name"), str):
            errors.append("thiếu trường name")
            continue
        args = obj.get("arguments") or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                pass
        if not isinstance(args, dict):
            errors.append(f"{obj['name']}: arguments phải là object")
            continue
        calls.append({"name": obj["name"], "arguments": args})
    return calls, errors


# ---------------------------------------------------------------- LLM backends: generate(prompt) -> completion text

class OpenAICompletionsBackend:
    """Any OpenAI-compatible /v1/completions server (e.g. `vllm serve`). Greedy decoding."""

    def __init__(self, model: str, base_url: str = "http://localhost:8000/v1", max_tokens: int = 512, timeout: float = 60):
        self.model, self.url, self.max_tokens, self.timeout = model, base_url.rstrip("/") + "/completions", max_tokens, timeout

    def generate(self, prompt: str, deadline: float | None = None) -> str:
        """With a deadline (time.monotonic() value), stops waiting at it and returns "" (the server may keep going)."""
        timeout = self.timeout if deadline is None else max(0.05, min(self.timeout, deadline - time.monotonic()))
        body = {"model": self.model, "prompt": prompt, "max_tokens": self.max_tokens, "temperature": 0,
                "seed": 0, "stop": ["<|im_end|>"], "skip_special_tokens": False}
        req = urllib.request.Request(self.url, json.dumps(body).encode(), {"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())["choices"][0]["text"]
        except (TimeoutError, urllib.error.URLError) as e:
            timed_out = isinstance(e, TimeoutError) or isinstance(getattr(e, "reason", None), TimeoutError)
            if deadline is None or not timed_out:
                raise
            return ""


class VLLMBackend:
    """In-process vLLM engine (what the Docker image will use)."""

    def __init__(self, model: str, max_model_len: int = 16384, gpu_memory_utilization: float = 0.80, max_tokens: int = 512):
        from vllm import LLM, SamplingParams
        self.llm = LLM(model=model, max_model_len=max_model_len, dtype="bfloat16", seed=0,
                       enable_prefix_caching=True, gpu_memory_utilization=gpu_memory_utilization)
        self.params = SamplingParams(temperature=0, max_tokens=max_tokens, stop=["<|im_end|>"], seed=0)

    def generate(self, prompt: str, deadline: float | None = None) -> str:
        """`deadline` is not enforced here: an in-process generate cannot be stopped; max_tokens bounds it."""
        return self.llm.generate([prompt], self.params, use_tqdm=False)[0].outputs[0].text

    def warmup(self, prompt: str, max_new_tokens: int = 16) -> None:
        """One untimed generation before the first sample (see HFBackend.warmup)."""
        from vllm import SamplingParams
        self.llm.generate([prompt], SamplingParams(temperature=0, max_tokens=max_new_tokens, seed=0), use_tqdm=False)


class HFBackend:
    """transformers + optional LoRA adapter (merged). Slower than vLLM but runs anywhere; used for local evals."""

    def __init__(self, model: str, adapter: str | None = None, max_tokens: int = 512, load_4bit: bool = False):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        torch.manual_seed(0)
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(model)
        kw = {"dtype": torch.bfloat16, "attn_implementation": "sdpa", "device_map": {"": 0}}
        if load_4bit:
            kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                           bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
        self.model = AutoModelForCausalLM.from_pretrained(model, **kw)
        if adapter:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, adapter)
            if not load_4bit:
                self.model = self.model.merge_and_unload()
        self.model.eval()
        self.eos = self.tok.convert_tokens_to_ids("<|im_end|>")
        self.max_tokens = max_tokens

    def generate(self, prompt: str, deadline: float | None = None) -> str:
        """With a deadline (time.monotonic() value), generation stops at it (transformers max_time)."""
        torch = self.torch
        ids = self.tok(prompt, return_tensors="pt", add_special_tokens=False).input_ids.to(self.model.device)
        kw = {} if deadline is None else {"max_time": max(0.01, deadline - time.monotonic())}
        with torch.no_grad():
            out = self.model.generate(ids, max_new_tokens=self.max_tokens, do_sample=False, eos_token_id=self.eos,
                                      pad_token_id=self.eos, **kw)
        return self.tok.decode(out[0, ids.shape[1]:], skip_special_tokens=False).split("<|im_end|>")[0]

    def warmup(self, prompt: str, max_new_tokens: int = 16) -> None:
        """One untimed generation right after loading. The first generate call pays one-off GPU setup that the
        per-sample deadline cannot cut (max_time is only checked between tokens): in the 4-bit dev runs the first
        sample took 110 s and 62 s and stopped on time with one step (JOURNAL entry 58). Output is discarded."""
        ids = self.tok(prompt, return_tensors="pt", add_special_tokens=False).input_ids.to(self.model.device)
        with self.torch.no_grad():
            self.model.generate(ids, max_new_tokens=max_new_tokens, do_sample=False, eos_token_id=self.eos,
                                pad_token_id=self.eos)


class PrefixBackend:
    """Forces the start of every assistant turn, e.g. an empty '<think>\\n\\n</think>\\n\\n' so hybrid Qwen3
    models answer without thinking in zero-shot runs. SFT models need no prefix."""

    def __init__(self, inner, prefix: str):
        self.inner, self.prefix = inner, prefix

    def generate(self, prompt: str, deadline: float | None = None) -> str:
        return self.prefix + self.inner.generate(prompt + self.prefix, deadline=deadline)

    def warmup(self, prompt: str, max_new_tokens: int = 16) -> None:
        if hasattr(self.inner, "warmup"):
            self.inner.warmup(prompt + self.prefix, max_new_tokens)


class OracleBackend:
    """Replays known calls one per step, then stops. Used to test the loop end to end without a model."""

    def __init__(self, calls: list[dict]):
        self.calls, self.i = calls, 0

    def generate(self, prompt: str, deadline: float | None = None) -> str:
        if self.i < len(self.calls):
            self.i += 1
            return render_calls([self.calls[self.i - 1]])
        return "Xong."


# ---------------------------------------------------------------- loop

class Agent:
    def __init__(self, llm, tools_by_name: dict, apps_by_id: dict, max_steps: int = 8, max_retries: int = 2,
                 time_budget: float = 25.0, min_step_seconds: float = 1.0, id_guard: bool = True,
                 search_relax: bool = False, max_relax: int = 2, max_repeat_steps: int = 0):
        """search_relax: retry an empty filtered read once with relaxed_args (at most max_relax retries per sample).
        max_repeat_steps: stop after this many steps in a row that only repeat answered reads (0 = never)."""
        self.llm, self.tools, self.apps = llm, tools_by_name, apps_by_id
        self.max_steps, self.max_retries, self.time_budget = max_steps, max_retries, time_budget
        self.min_step_seconds, self.id_guard = min_step_seconds, id_guard
        self.search_relax, self.max_relax, self.max_repeat_steps = search_relax, max_relax, max_repeat_steps

    def _relax(self, env, c: dict, r, seen: dict, step: dict) -> tuple[dict, dict] | None:
        """One looser retry of read call `c` whose result `r` was empty; (call, result) or None."""
        tool = self.tools.get(c["name"], {})
        if tool.get("kind") != "read" or not c["arguments"] or not empty_listing(r):
            return None
        args = relaxed_args(tool, c["arguments"])
        if args is None or args == c["arguments"]:
            return None
        key = json.dumps([c["name"], args], sort_keys=True, ensure_ascii=False)
        if key in seen or not env.validate(c["name"], args)["ok"]:
            return None  # already shown to the model, or not a valid call on its own
        call = {"name": c["name"], "arguments": args}
        r2 = env.call(c["name"], args)
        seen[key] = r2
        found = sum(len(v) for v in r2.values() if isinstance(v, list)) if isinstance(r2, dict) else 0
        step.setdefault("relaxed", []).append({"from": c["arguments"], "to": args, "found": found})
        return call, r2

    def run(self, item: dict, env, user_text: str, history_texts: list[str], t0: float | None = None,
            spent: float = 0.0) -> dict:
        """Runs the loop on `env` (one ToolEnv per sample, created by the caller). Returns a trace for debugging.
        `spent`: seconds the sample used before the agent (its ASR); they count against time_budget.
        trace["seconds"] is the agent's own wall time from t0."""
        t0 = time.monotonic() if t0 is None else t0
        deadline = t0 + self.time_budget - spent
        msgs = build_messages(item, user_text, history_texts, self.tools, self.apps)
        visible = "\n".join(m["content"] for m in msgs)  # what the model has been shown; its own calls excluded
        trace = {"steps": [], "stop": "max_steps"}
        seen: dict[str, dict] = {}
        retries = relaxes = repeat_run = 0
        for _ in range(self.max_steps):
            if deadline - time.monotonic() < self.min_step_seconds:
                trace["stop"] = "time"
                break
            ts = time.monotonic()
            out = self.llm.generate(to_chatml(msgs), deadline=deadline)
            late = time.monotonic() >= deadline
            calls, errors = parse_tool_calls(out)
            step = {"output": out, "calls": [], "errors": list(errors), "seconds": round(time.monotonic() - ts, 3)}
            trace["steps"].append(step)
            if not calls and not errors:
                trace["stop"] = "time" if late else "done"
                break
            results, processed, stop = [], [], False
            repeats = 0  # calls of this step answered from `seen` (no env.call)
            for c in calls:
                processed.append(c)
                # only reads are de-duplicated: repeating a write can be intended (redeem twice = two tickets)
                is_read = self.tools.get(c["name"], {}).get("kind") == "read"
                key = json.dumps([c["name"], c["arguments"]], sort_keys=True, ensure_ascii=False) if is_read else None
                if key in seen:
                    results.append(seen[key])
                    repeats += 1
                    continue
                v = env.validate(c["name"], c["arguments"])
                if not v["ok"]:
                    results.append({"ok": False, "error": v["error"]})
                    step["errors"].append(f"{c['name']}: {v['error']}")
                    continue
                bad = unseen_ids(self.tools.get(c["name"], {}), c["arguments"], visible) if self.id_guard else []
                if bad:
                    err = block_message(bad)
                    results.append({"ok": False, "error": err})
                    step["errors"].append(f"{c['name']}: {err}")
                    step.setdefault("blocked", []).append(c)
                    continue
                r = env.call(c["name"], c["arguments"])
                if key:
                    seen[key] = r
                results.append(r)
                step["calls"].append(c)
                if c["name"] == "sys.ask_missing_info":
                    stop = True
                    break
                if self.search_relax and relaxes < self.max_relax:
                    retry = self._relax(env, c, r, seen, step)
                    if retry:  # shown to the model as its own next call, right after the empty one
                        relaxes += 1
                        processed.append(retry[0])
                        results.append(retry[1])
                        step["calls"].append(retry[0])
            results += [{"ok": False, "error": e} for e in errors]
            step["results"] = results  # what the model is shown next; kept so audits need no replay
            # a model trained with thoughts (lifemate.sft --thoughts) wrote "<think>...</think>\n\n" before its calls;
            # the training sequences keep that block in front of the step's calls, so the next prompts keep it too.
            # Models trained without thoughts write none, and an empty block (zero-shot prefix) is dropped as before.
            think = _THINK.search(out)
            kept = think.group(0) + "\n\n" if think and think.group(0)[7:-8].strip() else ""
            msgs.append({"role": "assistant", "content": kept + render_calls(processed) if processed else out})
            msgs.append({"role": "user", "content": render_results(results)})
            visible += "\n" + msgs[-1]["content"]
            if stop:
                trace["stop"] = "ask_missing"
                break
            if late:
                trace["stop"] = "time"
                break
            repeat_run = repeat_run + 1 if calls and repeats == len(calls) and not step["errors"] else 0
            if self.max_repeat_steps and repeat_run >= self.max_repeat_steps:
                trace["stop"] = "repeat"
                break
            if step["errors"]:
                retries += 1
                if retries > self.max_retries:
                    trace["stop"] = "retries"
                    break
        trace["seconds"] = round(time.monotonic() - t0, 3)
        return trace
