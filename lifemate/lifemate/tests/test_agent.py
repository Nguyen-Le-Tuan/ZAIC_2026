"""Tests for the agent loop's time budget and ID guard (lifemate.agent, lifemate.guard). CPU only, no model.

Run:  .venv/bin/python -m lifemate.tests.test_agent     (also works under pytest)
Tests that need the train split are skipped when data/ is absent.
"""
from __future__ import annotations

import http.server
import json
import sys
import threading
import time
from functools import lru_cache
from pathlib import Path

from lifemate.agent import Agent, OpenAICompletionsBackend, OracleBackend
from lifemate.data import DEFAULT_ROOT, catalog_tools, load_catalog, load_split, zaic_tools
from lifemate.guard import guarded_values, seen, unseen_ids
from lifemate.prompt import render_calls
from lifemate.tests.test_scorer import Skip, _skip

GUARD_SKEW = "train_1696"  # the one fit sample whose gold write uses an ID never shown (data skew; docs/ID_GUARD_2026-10-30.md)
INVENTED = "zz_invented_404"

WRITE = {"kind": "write", "parameters": {"properties": {
    "account_id": {"type": "string", "x-ref": "accounts"},
    "amount": {"type": "integer"},
    "items": {"type": "array", "items": {"type": "object", "properties": {"product_id": {"type": "string", "x-ref": "products"}}}},
}}}


# ------------------------------------------------------------------ the rule (no data)

def test_guard_passes_ids_that_were_shown():
    assert unseen_ids(WRITE, {"account_id": "acc_01", "amount": 5}, "kết quả: acc_01, acc_02") == []


def test_guard_blocks_ids_never_shown():
    assert unseen_ids(WRITE, {"account_id": "acc_99", "amount": 5}, "acc_01 acc_02") == [("account_id", "acc_99")]


def test_guard_needs_whole_word():
    assert not seen("acc_1", "acc_10 acc_11") and seen("acc_1", "[acc_1]")


def test_guard_checks_nested_ids():
    args = {"account_id": "acc_01", "items": [{"product_id": "p_2"}, {"product_id": "p_3"}]}
    assert guarded_values(WRITE, args) == [("account_id", "acc_01"), ("items", "p_2"), ("items", "p_3")]
    assert unseen_ids(WRITE, args, "acc_01 p_2") == [("items", "p_3")]


def test_guard_ignores_reads():
    assert unseen_ids({**WRITE, "kind": "read"}, {"account_id": "acc_99"}, "") == []


# ------------------------------------------------------------------ the loop on real samples

@lru_cache(maxsize=1)
def _data():
    if not (Path(DEFAULT_ROOT) / "train" / "train.jsonl").exists():
        _skip("train data not available")
    cat = load_catalog("train")
    items = {s["id"]: s for s in load_split("train")}
    return zaic_tools("train"), catalog_tools(cat), {a["id"]: a for a in cat["apps"]}, items


def _env(sid):
    zt = _data()[0]
    return zt.ToolEnv("train", sid, root=str(DEFAULT_ROOT))


def _hist(item):
    return [h["audio_text"] for h in item.get("history", []) if h["role"] == "user"]


def _run(item, llm, **kw):
    _, tools, apps, _ = _data()
    spent = kw.pop("spent", 0.0)
    env = _env(item["id"])
    trace = Agent(llm, tools, apps, **kw).run(item, env, item["audio_text"], _hist(item), spent=spent)
    return trace, env


def _xref_samples():
    """Samples (not the skew case) with a write call that has a top-level x-ref string, in id order."""
    _, tools, _, items = _data()
    out = []
    for sid in sorted(items):
        if sid == GUARD_SKEW:
            continue
        for i, c in enumerate(items[sid]["label"]["tool_calls"]):
            t = tools.get(c["name"], {})
            top = [(k, v) for k, v in guarded_values(t, c["arguments"]) if c["arguments"].get(k) == v and isinstance(v, str)]
            if t.get("kind") == "write" and top:
                out.append((items[sid], i, top[0][0]))
                break
    return out


def _first_read_sample():
    """A sample whose first two gold calls are reads."""
    _, tools, _, items = _data()
    for sid in sorted(items):
        calls = items[sid]["label"]["tool_calls"]
        if len(calls) >= 2 and all(tools.get(c["name"], {}).get("kind") == "read" for c in calls[:2]):
            return items[sid]
    raise AssertionError("no sample starts with two reads")


def test_gold_replay_passes_guard():
    samples = _xref_samples()[:40]
    assert len(samples) == 40
    for item, _, _ in samples:
        trace, env = _run(item, OracleBackend(item["label"]["tool_calls"]))
        assert not any(s.get("blocked") for s in trace["steps"]), item["id"]
        gold = _env(item["id"])
        for c in item["label"]["tool_calls"]:
            gold.call(c["name"], c["arguments"])
        assert env.get_state_hash() == gold.get_state_hash(), item["id"]


def test_invented_id_is_blocked_and_shown_to_the_model():
    item, i, k = _xref_samples()[0]
    calls = json.loads(json.dumps(item["label"]["tool_calls"]))
    calls[i]["arguments"][k] = INVENTED
    trace, env = _run(item, OracleBackend(calls))
    blocked = [c for s in trace["steps"] for c in s.get("blocked", [])]
    assert blocked == [calls[i]]
    assert calls[i] not in env.get_tool_calls()
    err = [e for s in trace["steps"] for e in s["errors"] if INVENTED in e]
    assert err and err[0].startswith(calls[i]["name"])
    res = [r for s in trace["steps"] for r in s.get("results", []) if INVENTED in str(r.get("error"))]
    assert res, "the model must see the block as a tool_response error"


def test_guard_off_executes_the_call():
    item, i, k = _xref_samples()[0]
    calls = json.loads(json.dumps(item["label"]["tool_calls"]))
    calls[i]["arguments"][k] = INVENTED
    trace, env = _run(item, OracleBackend(calls), id_guard=False)
    assert not any(s.get("blocked") for s in trace["steps"])
    assert calls[i] in env.get_tool_calls()


class SlowBackend:
    """Takes `step_s` seconds per generation and, like HFBackend, stops at the deadline with a cut output."""

    def __init__(self, outputs, step_s, cut=lambda out: out[: len(out) // 2]):
        self.outputs, self.step_s, self.cut, self.deadlines, self.i = outputs, step_s, cut, [], 0

    def generate(self, prompt, deadline=None):
        self.deadlines.append(deadline)
        out = self.outputs[min(self.i, len(self.outputs) - 1)]
        self.i += 1
        left = self.step_s if deadline is None else deadline - time.monotonic()
        if left >= self.step_s:
            time.sleep(self.step_s)
            return out
        time.sleep(max(0.0, left))
        return self.cut(out)


def test_deadline_bounds_the_sample():
    item = _first_read_sample()
    llm = SlowBackend([render_calls([item["label"]["tool_calls"][0]])], step_s=0.3)
    trace, _ = _run(item, llm, time_budget=1.0, min_step_seconds=0.1)
    assert trace["stop"] == "time" and trace["seconds"] <= 1.1, trace["seconds"]
    assert len(set(llm.deadlines)) == 1 and 3 <= len(trace["steps"]) <= 4, len(trace["steps"])


def test_asr_seconds_count_against_the_budget():
    item = _first_read_sample()
    llm = SlowBackend([render_calls([item["label"]["tool_calls"][0]])], step_s=0.3)
    t0 = time.monotonic()
    trace, _ = _run(item, llm, time_budget=1.0, min_step_seconds=0.1, spent=0.8)
    assert trace["stop"] == "time" and len(trace["steps"]) == 1
    assert trace["seconds"] <= 0.3, trace["seconds"]
    assert abs(llm.deadlines[0] - (t0 + 0.2)) < 0.05


def test_no_step_starts_with_too_little_time():
    item = _first_read_sample()
    llm = SlowBackend(["Xong."], step_s=0.3)
    trace, env = _run(item, llm, time_budget=1.0, min_step_seconds=0.1, spent=0.95)
    assert trace["stop"] == "time" and trace["steps"] == [] and env.get_tool_calls() == []


def test_complete_calls_before_the_cut_still_run():
    item = _first_read_sample()
    c1, c2 = item["label"]["tool_calls"][:2]
    first = lambda out: out[: out.index("</tool_call>") + len("</tool_call>")]  # noqa: E731
    llm = SlowBackend([render_calls([c1, c2])], step_s=0.5, cut=first)
    trace, env = _run(item, llm, time_budget=0.3, min_step_seconds=0.1)
    assert trace["stop"] == "time"
    assert env.get_tool_calls() == [c1]


# ------------------------------------------------------------------ OpenAI-compatible client

class _Slow(http.server.BaseHTTPRequestHandler):
    delay = 1.0

    def do_POST(self):  # noqa: N802
        self.rfile.read(int(self.headers["Content-Length"]))
        time.sleep(self.delay)
        body = json.dumps({"choices": [{"text": "Xong."}]}).encode()
        try:
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except BrokenPipeError:  # the client stopped waiting
            pass

    def log_message(self, *a):
        pass


def _server(delay):
    handler = type("H", (_Slow,), {"delay": delay})
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/v1"


def test_openai_client_stops_waiting_at_the_deadline():
    srv, url = _server(1.0)
    try:
        llm = OpenAICompletionsBackend("m", url)
        t = time.monotonic()
        assert llm.generate("x", deadline=t + 0.2) == ""
        assert time.monotonic() - t < 0.6
    finally:
        srv.shutdown()


def test_openai_client_without_deadline_waits_and_raises_on_timeout():
    srv, url = _server(0.3)
    try:
        assert OpenAICompletionsBackend("m", url).generate("x") == "Xong."
        try:
            OpenAICompletionsBackend("m", url, timeout=0.1).generate("x")
        except (TimeoutError, OSError):
            pass
        else:
            raise AssertionError("a timeout without a deadline must raise")
    finally:
        srv.shutdown()


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        try:
            fn()
            print(f"ok    {name}")
        except Skip as e:
            print(f"skip  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {name}: {type(e).__name__}: {e}")
    sys.exit(1 if failed else 0)
