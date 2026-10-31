"""Agent loop: LLM proposes tool calls -> guardrails -> env.call -> results back to the LLM -> ...

Guardrails (pure code, no model):
  * env.validate() before every call: schema errors go back to the model as a tool_response but are NOT sent
    to env.call, so they never appear in the submission (rejected calls would count as unmatched).
  * identical repeated READ calls are answered from the earlier result instead of being called again.
  * stop right after sys.ask_missing_info (always the last call in train gold), after max_steps, or when the
    time budget runs out.
"""
from __future__ import annotations

import json
import re
import time
import urllib.request

from .prompt import build_messages, render_calls, render_results, to_chatml

_TOOL_CALL = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.S)
_THINK = re.compile(r"<think>.*?</think>", re.S)


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

    def generate(self, prompt: str) -> str:
        body = {"model": self.model, "prompt": prompt, "max_tokens": self.max_tokens, "temperature": 0,
                "seed": 0, "stop": ["<|im_end|>"], "skip_special_tokens": False}
        req = urllib.request.Request(self.url, json.dumps(body).encode(), {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read())["choices"][0]["text"]


class VLLMBackend:
    """In-process vLLM engine (what the Docker image will use)."""

    def __init__(self, model: str, max_model_len: int = 16384, gpu_memory_utilization: float = 0.80, max_tokens: int = 512):
        from vllm import LLM, SamplingParams
        self.llm = LLM(model=model, max_model_len=max_model_len, dtype="bfloat16", seed=0,
                       enable_prefix_caching=True, gpu_memory_utilization=gpu_memory_utilization)
        self.params = SamplingParams(temperature=0, max_tokens=max_tokens, stop=["<|im_end|>"], seed=0)

    def generate(self, prompt: str) -> str:
        return self.llm.generate([prompt], self.params, use_tqdm=False)[0].outputs[0].text


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

    def generate(self, prompt: str) -> str:
        torch = self.torch
        ids = self.tok(prompt, return_tensors="pt", add_special_tokens=False).input_ids.to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(ids, max_new_tokens=self.max_tokens, do_sample=False, eos_token_id=self.eos,
                                      pad_token_id=self.eos)
        return self.tok.decode(out[0, ids.shape[1]:], skip_special_tokens=False).split("<|im_end|>")[0]


class PrefixBackend:
    """Forces the start of every assistant turn, e.g. an empty '<think>\\n\\n</think>\\n\\n' so hybrid Qwen3
    models answer without thinking in zero-shot runs. SFT models need no prefix."""

    def __init__(self, inner, prefix: str):
        self.inner, self.prefix = inner, prefix

    def generate(self, prompt: str) -> str:
        return self.prefix + self.inner.generate(prompt + self.prefix)


class OracleBackend:
    """Replays known calls one per step, then stops. Used to test the loop end to end without a model."""

    def __init__(self, calls: list[dict]):
        self.calls, self.i = calls, 0

    def generate(self, prompt: str) -> str:
        if self.i < len(self.calls):
            self.i += 1
            return render_calls([self.calls[self.i - 1]])
        return "Xong."


# ---------------------------------------------------------------- loop

class Agent:
    def __init__(self, llm, tools_by_name: dict, apps_by_id: dict, max_steps: int = 8, max_retries: int = 2, time_budget: float = 25.0):
        self.llm, self.tools, self.apps = llm, tools_by_name, apps_by_id
        self.max_steps, self.max_retries, self.time_budget = max_steps, max_retries, time_budget

    def run(self, item: dict, env, user_text: str, history_texts: list[str], t0: float | None = None) -> dict:
        """Runs the loop on `env` (one ToolEnv per sample, created by the caller). Returns a trace for debugging."""
        t0 = time.monotonic() if t0 is None else t0
        msgs = build_messages(item, user_text, history_texts, self.tools, self.apps)
        trace = {"steps": [], "stop": "max_steps"}
        seen: dict[str, dict] = {}
        retries = 0
        for _ in range(self.max_steps):
            if time.monotonic() - t0 > self.time_budget:
                trace["stop"] = "time"
                break
            out = self.llm.generate(to_chatml(msgs))
            calls, errors = parse_tool_calls(out)
            step = {"output": out, "calls": [], "errors": list(errors)}
            trace["steps"].append(step)
            if not calls and not errors:
                trace["stop"] = "done"
                break
            results, processed, stop = [], [], False
            for c in calls:
                processed.append(c)
                # only reads are de-duplicated: repeating a write can be intended (redeem twice = two tickets)
                is_read = self.tools.get(c["name"], {}).get("kind") == "read"
                key = json.dumps([c["name"], c["arguments"]], sort_keys=True, ensure_ascii=False) if is_read else None
                if key in seen:
                    results.append(seen[key])
                    continue
                v = env.validate(c["name"], c["arguments"])
                if not v["ok"]:
                    results.append({"ok": False, "error": v["error"]})
                    step["errors"].append(f"{c['name']}: {v['error']}")
                    continue
                r = env.call(c["name"], c["arguments"])
                if key:
                    seen[key] = r
                results.append(r)
                step["calls"].append(c)
                if c["name"] == "sys.ask_missing_info":
                    stop = True
                    break
            results += [{"ok": False, "error": e} for e in errors]
            msgs.append({"role": "assistant", "content": render_calls(processed) if processed else out})
            msgs.append({"role": "user", "content": render_results(results)})
            if stop:
                trace["stop"] = "ask_missing"
                break
            if step["errors"]:
                retries += 1
                if retries > self.max_retries:
                    trace["stop"] = "retries"
                    break
        trace["seconds"] = round(time.monotonic() - t0, 3)
        return trace
