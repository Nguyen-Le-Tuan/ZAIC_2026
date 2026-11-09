"""Tests for D2 thoughts: lifemate.sft --thoughts (think blocks in the SFT data) and the agent keeping a model's own
<think> block in its next prompts, so training and inference sequences stay identical. CPU only, no model, no API.

Run:  .venv/bin/python -m lifemate.tests.test_thoughts     (also works under pytest)
Tests that need the train split are skipped when data/ is absent.
"""
from __future__ import annotations

import random
import sys
from functools import lru_cache
from pathlib import Path

from lifemate.agent import Agent
from lifemate.data import DEFAULT_ROOT, catalog_tools, load_catalog, load_split, zaic_tools
from lifemate.rationale import brief, check
from lifemate.sft import (FINAL_DONE, FINAL_NONE, THOUGHT_FALLBACK_STEP, THOUGHT_REMOVED, apply_rename, build_all,
                          build_example, clean_thought, group_steps, make_rename, think_block)
from lifemate.tests.test_scorer import Skip, _skip


@lru_cache(maxsize=1)
def _data():
    if not (Path(DEFAULT_ROOT) / "train" / "train.jsonl").exists():
        return None
    cat = load_catalog("train")
    return {s["id"]: s for s in load_split("train")}, catalog_tools(cat), {x["id"]: x for x in cat["apps"]}


def _need():
    d = _data()
    if d is None:
        _skip("no train split")
    return d


def _fake_thoughts(s, tools):
    calls, results = s["label"]["tool_calls"], s["label"]["tool_results"]
    n = len(group_steps(calls, results, tools)) if calls else 0
    names = [calls[st[0]]["name"] for st in group_steps(calls, results, tools)] if calls else []
    return {"thoughts": [f"- bước tới: gọi {nm}​" for nm in names][:n], "final": "Xong."}


# ------------------------------------------------------------------ text helpers

def test_clean_thought():
    assert clean_thought("- ​cần device_id -> smart_home.get_status ") == "cần device_id -> smart_home.get_status"
    assert clean_thought("gọi smart_home.get_status", {"smart_home.get_status": "home_iot.fetch_status"}) == \
        "gọi home_iot.fetch_status"
    assert think_block("A") == "<think>\nA\n</think>\n\n"


def test_check_rejects_bad_teacher_output():
    assert check({"thoughts": ["a", "b"], "final": "c"}, 2) is None
    assert "need 2" in check({"thoughts": ["a"], "final": "c"}, 2)
    assert "banned" in check({"thoughts": ["theo đáp án thì gọi x"], "final": "c"}, 1)
    assert "too long" in check({"thoughts": ["từ " * 60], "final": "c"}, 1)


# ------------------------------------------------------------------ SFT segments

def test_thoughts_lead_every_assistant_turn():
    samples, tools, apps = _need()
    s = next(x for x in samples.values() if len(x["label"]["tool_calls"]) >= 3 and
             not any(c["name"] == "sys.ask_missing_info" for c in x["label"]["tool_calls"]))
    th = _fake_thoughts(s, tools)
    segs = build_example(s, s["audio_text"], [h["audio_text"] for h in s["history"] if h["role"] == "user"],
                         s["label"]["tool_calls"], s["label"]["tool_results"], tools, apps, thoughts=th)
    loss = [t for t, l in segs if l]
    assert len(loss) == len(th["thoughts"]) + 1
    for text, thought in zip(loss, th["thoughts"]):
        assert text.startswith(think_block(clean_thought(thought))) and "<tool_call>" in text
    assert loss[-1] == think_block("Xong.") + FINAL_DONE + "<|im_end|>"
    plain = build_example(s, s["audio_text"], [h["audio_text"] for h in s["history"] if h["role"] == "user"],
                          s["label"]["tool_calls"], s["label"]["tool_results"], tools, apps)
    assert [t for t, l in plain if not l] == [t for t, l in segs if not l]  # prompts are unchanged


def test_renamed_variant_renames_the_thoughts_too():
    samples, tools, apps = _need()
    s = next(x for x in samples.values() if x["label"]["tool_calls"] and x["label"]["tool_calls"][0]["name"] != "sys.ask_missing_info")
    th = _fake_thoughts(s, tools)
    mapping = make_rename(s, random.Random(1))
    it, cl, tb, ab = apply_rename(s, s["label"]["tool_calls"], tools, apps, mapping)
    segs = build_example(it, s["audio_text"], [h["audio_text"] for h in s["history"] if h["role"] == "user"], cl,
                         s["label"]["tool_results"], tb, ab, thoughts=th, mapping=mapping)
    first = next(t for t, l in segs if l)
    old = s["label"]["tool_calls"][0]["name"]
    assert mapping[old] in first.split("</think>")[0] and old not in first.split("</think>")[0]


def test_build_all_fallback_and_removal_thoughts():
    samples, tools, apps = _need()
    pick = [s for s in samples.values() if s["label"]["tool_calls"]][:40]
    stats = {}
    rows = build_all(pick, tools, apps, {}, rename=0, p_remove=1.0, p_distract=0.0, p_lower=0.0, thoughts={},
                     stats=stats)
    assert stats["no_thoughts"] == len(pick)
    removed = [r for r in rows if r["aug"] == ["remove"]]
    assert removed and all(r["segments"][-1][0] == think_block(THOUGHT_REMOVED) + FINAL_NONE + "<|im_end|>"
                           for r in removed)
    normal = [r for r in rows if r["aug"] != ["remove"]]
    assert all(r["segments"][1][0].startswith(think_block(THOUGHT_FALLBACK_STEP)) for r in normal)


def test_build_all_without_thoughts_has_no_think_blocks():
    samples, tools, apps = _need()
    pick = list(samples.values())[:30]
    rows = build_all(pick, tools, apps, {}, rename=1, p_remove=0.3, p_distract=0.0, p_lower=0.3)
    assert not any("<think>" in t for r in rows for t, _ in r["segments"])


# ------------------------------------------------------------------ inference = training

class Replay:
    """Backend that writes exactly the SFT loss texts (minus <|im_end|>), one per step, recording every prompt."""

    def __init__(self, texts):
        self.texts, self.prompts = texts, []

    def generate(self, prompt, deadline=None):
        self.prompts.append(prompt)
        i = len(self.prompts) - 1
        return self.texts[i] if i < len(self.texts) else ""


def test_agent_prompts_equal_sft_text_with_thoughts():
    """For train samples, the agent's prompt before each step equals the SFT sequence up to that loss segment, with
    think blocks in place (the property scripts/check_sft.py checks for the plain format)."""
    samples, tools, apps = _need()
    zt = zaic_tools("train")
    pick = [s for s in samples.values() if s["id"] != "train_1696"][:: max(1, len(samples) // 120)]
    for s in pick:
        hist = [h["audio_text"] for h in s["history"] if h["role"] == "user"]
        segs = build_example(s, s["audio_text"], hist, s["label"]["tool_calls"], s["label"]["tool_results"], tools,
                             apps, thoughts=_fake_thoughts(s, tools))
        loss_idx = [i for i, (_, l) in enumerate(segs) if l]
        texts = [segs[i][0].removesuffix("<|im_end|>") for i in loss_idx]
        llm = Replay(texts)
        env = zt.ToolEnv("train", s["id"], root=str(DEFAULT_ROOT))
        Agent(llm, tools, apps, max_steps=12, time_budget=1e9).run(s, env, s["audio_text"], hist)
        for k, i in enumerate(loss_idx[: len(llm.prompts)]):
            want = "".join(t for t, _ in segs[:i])
            assert llm.prompts[k] == want, f"{s['id']} step {k}: prompt differs from the SFT text"


def test_teacher_brief_counts_the_sft_steps():
    samples, tools, apps = _need()
    for s in list(samples.values())[:50]:
        text, n = brief(s, tools, apps)
        calls = s["label"]["tool_calls"]
        assert n == (len(group_steps(calls, s["label"]["tool_results"], tools)) if calls else 0)
        assert s["audio_text"] in text and "_environment" not in text


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
