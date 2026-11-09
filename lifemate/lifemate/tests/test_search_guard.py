"""Tests for the agent's search guard (lifemate.agent: empty_listing, relaxed_args, Agent(search_relax,
max_repeat_steps)). CPU only, no model.

Run:  .venv/bin/python -m lifemate.tests.test_search_guard     (also works under pytest)
The replay test needs the train split and is skipped when data/ is absent.
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

from lifemate.agent import Agent, OracleBackend, empty_listing, relaxed_args
from lifemate.data import DEFAULT_ROOT, catalog_tools, fuzzy_params, load_catalog, load_split, zaic_tools
from lifemate.prompt import render_calls
from lifemate.scorer import score_sample
from lifemate.tests.test_scorer import Skip, _skip

SEARCH = {"name": "ev.search", "kind": "read", "description": "tìm sự kiện",
          "parameters": {"properties": {"query": {"type": "string"}, "city": {"type": "string"}}, "required": []}}
FIND = {"name": "ev.find", "kind": "read", "description": "tìm theo tên",
        "parameters": {"properties": {"query": {"type": "string"}}, "required": ["query"]}}
BOOK = {"name": "ev.book", "kind": "write", "description": "đặt vé",
        "parameters": {"properties": {"event_id": {"type": "string", "x-ref": "ev.events"}}, "required": ["event_id"]}}
TOOLS = {t["name"]: t for t in (SEARCH, FIND, BOOK)}
APPS = {"ev": {"id": "ev", "name_vi": "Vé", "description": "vé sự kiện"}}
ITEM = {"id": "t1", "history": [], "context": {
    "current_time": "2026-11-08T10:00:00+07:00", "timezone": "Asia/Ho_Chi_Minh", "user_profile": {"name": "A"},
    "installed_apps": {"ev": {"tools": ["ev.search", "ev.find", "ev.book"]}}}}
EVENTS = [{"id": "e1", "name": "Đêm nhạc Mùa Thu"}, {"id": "e2", "name": "Kịch Tấm Cám"}]


class FakeEnv:
    """ToolEnv stand-in: ev.search / ev.find match the whole query as a substring of the name; every call is logged."""

    def __init__(self):
        self.log = []

    def validate(self, name, args):
        return {"ok": name in TOOLS}

    def call(self, name, args):
        self.log.append({"name": name, "arguments": dict(args)})
        if name in ("ev.search", "ev.find"):
            q = (args.get("query") or "").lower()
            if args.get("city"):
                return {"ok": True, "events": []}  # the city filter matches nothing
            return {"ok": True, "events": [e for e in EVENTS if q in e["name"].lower()]}
        return {"ok": True, "id": "b1"}


class Script:
    """Backend that emits the given call lists one step at a time, then a short final answer."""

    def __init__(self, steps):
        self.steps, self.i = steps, 0

    def generate(self, prompt, deadline=None):
        self.i += 1
        return render_calls(self.steps[self.i - 1]) if self.i <= len(self.steps) else "Đã xong."


def _run(steps, **kw):
    env = FakeEnv()
    trace = Agent(Script(steps), TOOLS, APPS, **kw).run(ITEM, env, "đặt vé đêm nhạc mùa thu", [])
    return env, trace


# ------------------------------------------------------------------ the rules

def test_empty_listing():
    assert empty_listing({"ok": True, "events": []})
    assert empty_listing({"ok": True, "events": [], "tickets": []})
    assert not empty_listing({"ok": True, "events": [{"id": "e1"}]})
    assert not empty_listing({"ok": True, "events": [], "tickets": [1]})
    assert not empty_listing({"ok": False, "events": []})
    assert not empty_listing({"ok": True, "balance": 5})
    assert not empty_listing([])


def test_relax_drops_optional_arguments_first():
    assert relaxed_args(SEARCH, {"query": "đêm nhạc", "city": "Huế"}) == {}
    assert relaxed_args(FIND, {"query": "x"}) is None  # only required, one word: nothing to loosen


def test_relax_strips_filler_words_from_a_required_query():
    assert relaxed_args(FIND, {"query": "vé đêm nhạc Mùa Thu"}) == {"query": "đêm nhạc Mùa Thu"}
    assert relaxed_args(FIND, {"query": "chị Lan"}) == {"query": "Lan"}
    assert relaxed_args(FIND, {"query": "Đêm nhạc Mùa Thu"}) is None  # no filler: no guessing
    assert relaxed_args(FIND, {"query": "anh"}) is None  # never empties the query


def test_relax_leaves_enums_alone():
    tool = {"parameters": {"properties": {"query": {"type": "string", "enum": ["vé xe", "vé tàu"]}}, "required": ["query"]}}
    assert relaxed_args(tool, {"query": "vé xe"}) is None


# ------------------------------------------------------------------ the loop

def test_empty_search_is_retried_once_and_shown_to_the_model():
    steps = [[{"name": "ev.search", "arguments": {"query": "đêm nhạc mùa thu", "city": "Huế"}}],
             [{"name": "ev.book", "arguments": {"event_id": "e1"}}]]
    env, trace = _run(steps, search_relax=True)
    assert [c["arguments"] for c in env.log] == [{"query": "đêm nhạc mùa thu", "city": "Huế"}, {}, {"event_id": "e1"}]
    s0 = trace["steps"][0]
    assert s0["relaxed"] == [{"from": {"query": "đêm nhạc mùa thu", "city": "Huế"}, "to": {}, "found": 2}]
    assert len(s0["calls"]) == 2 and len(s0["results"]) == 2
    assert not trace["steps"][1]["errors"]  # e1 came from the retry's result, so the ID guard lets the booking pass


def test_guard_off_keeps_the_old_behaviour():
    steps = [[{"name": "ev.search", "arguments": {"query": "đêm nhạc mùa thu", "city": "Huế"}}]]
    env, trace = _run(steps)
    assert env.log == [{"name": "ev.search", "arguments": {"query": "đêm nhạc mùa thu", "city": "Huế"}}]
    assert "relaxed" not in trace["steps"][0]


def test_no_retry_when_the_search_found_something_or_is_a_write():
    env, _ = _run([[{"name": "ev.search", "arguments": {"query": "mùa thu"}}]], search_relax=True)
    assert len(env.log) == 1
    env, _ = _run([[{"name": "ev.book", "arguments": {"event_id": "zz"}}]], search_relax=True, id_guard=False)
    assert len(env.log) == 1


def test_at_most_max_relax_retries_per_sample():
    steps = [[{"name": "ev.search", "arguments": {"query": f"q{i}", "city": "Huế"}}] for i in range(4)]
    env, trace = _run(steps, search_relax=True, max_relax=2)
    assert sum(len(s.get("relaxed", [])) for s in trace["steps"]) == 1  # the second retry would repeat {} (seen)
    assert len(env.log) == 4 + 1


def test_repeated_reads_stop_the_loop_without_changing_the_calls():
    steps = [[{"name": "ev.search", "arguments": {"query": "mùa thu"}}]] * 8
    env, trace = _run(steps, max_repeat_steps=3)
    assert trace["stop"] == "repeat" and len(trace["steps"]) == 4  # 1 real + 3 repeated
    assert len(env.log) == 1
    env2, trace2 = _run(steps)  # off: runs to max_steps, same single env call
    assert trace2["stop"] == "max_steps" and env2.log == env.log


def test_two_repeats_then_progress_is_not_cut():
    steps = [[{"name": "ev.search", "arguments": {"query": "mùa thu"}}]] * 3 + [[{"name": "ev.book", "arguments": {"event_id": "e1"}}]]
    env, trace = _run(steps, max_repeat_steps=3)
    assert env.log[-1]["name"] == "ev.book" and trace["stop"] == "done"


# ------------------------------------------------------------------ cost on gold (train)

@lru_cache(maxsize=1)
def _train():
    if not (Path(DEFAULT_ROOT) / "train" / "train.jsonl").exists():
        return None
    cat = load_catalog("train")
    return load_split("train"), catalog_tools(cat), {x["id"]: x for x in cat["apps"]}, fuzzy_params(cat)


def test_gold_replay_with_the_guard_barely_changes():
    """Replaying gold with the guard on: only samples whose gold itself has an empty filtered read can change (4 calls
    in train), so the replay must stay at about 100."""
    data = _train()
    if data is None:
        _skip("no train split")
    samples, tools, apps, fuzzy = data
    zt = zaic_tools("train")
    scores, changed = [], 0
    for s in samples:
        gold = s["label"]["tool_calls"]
        g_env = zt.ToolEnv("train", s["id"], root=str(DEFAULT_ROOT))
        for c in gold:
            g_env.call(c["name"], c["arguments"])
        env = zt.ToolEnv("train", s["id"], root=str(DEFAULT_ROOT))
        Agent(OracleBackend(gold), tools, apps, max_steps=12, time_budget=1e9, search_relax=True,
              max_repeat_steps=3).run(s, env, s["audio_text"], [h["audio_text"] for h in s["history"] if h["role"] == "user"])
        sub = env.get_tool_calls()
        changed += len(sub) != len(gold)
        scores.append(score_sample(sub, env.get_state_hash(), gold, g_env.get_state_hash(), fuzzy))
    mean = 100 * sum(scores) / len(scores)
    print(f"    gold replay with the guard: {mean:.2f} on {len(scores)} samples, {changed} with extra calls")
    assert changed <= 6 and mean >= 99.5


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
