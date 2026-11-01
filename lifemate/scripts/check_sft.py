"""Checks that SFT sequences match inference exactly.

1. Prompt identity: for every train sample, run the real Agent on a ToolEnv with a backend that replays the SFT
   steps; every prompt the agent builds must equal the SFT text before the matching loss segment.
2. Scoring: the replayed submissions must score 100 (steps grouping loses no call). With the ID guard on (the
   default), train_1696 is the one expected exception: its gold write uses an ID never shown (data skew), so the
   guard blocks it: 1544/1545 prompts identical, score 99.99.
3. Token boundaries: tokenizing segments one by one gives the same ids as tokenizing the whole sequence.
"""
import random
import sys
from pathlib import Path

from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate.agent import Agent  # noqa: E402
from lifemate.data import DEFAULT_ROOT, catalog_tools, fuzzy_params, load_catalog, load_split, zaic_tools  # noqa: E402
from lifemate.prompt import render_calls  # noqa: E402
from lifemate.scorer import evaluate, gold_from_train  # noqa: E402
from lifemate.sft import FINAL_DONE, FINAL_NONE, build_example, group_steps  # noqa: E402


class StepReplay:
    def __init__(self, steps):
        self.steps, self.prompts = steps, []

    def generate(self, prompt, deadline=None):
        self.prompts.append(prompt)
        i = len(self.prompts) - 1
        if i < len(self.steps):
            return render_calls(self.steps[i])
        return FINAL_DONE if self.steps else FINAL_NONE


def main():
    zt = zaic_tools("train")
    cat = load_catalog("train")
    tools, apps = catalog_tools(cat), {a["id"]: a for a in cat["apps"]}
    samples = load_split("train")
    pred, mismatches, n_steps = {}, [], 0
    for s in samples:
        calls, results = s["label"]["tool_calls"], s["label"]["tool_results"]
        hist = [h["audio_text"] for h in s["history"] if h["role"] == "user"]
        segs = build_example(s, s["audio_text"], hist, calls, results, tools, apps)
        steps = [[calls[i] for i in g] for g in group_steps(calls, results, tools)]
        n_steps += len(steps)
        llm = StepReplay(steps)
        env = zt.ToolEnv("train", s["id"], root=str(DEFAULT_ROOT))
        Agent(llm, tools, apps).run(s, env, s["audio_text"], hist)
        pred[s["id"]] = {"tool_calls": env.get_tool_calls(), "state_hash": env.get_state_hash()}
        # prompt before the k-th loss segment
        prefix, expected = "", []
        for text, loss in segs:
            if loss:
                expected.append(prefix)
            prefix += text
        got = llm.prompts[: len(expected)]
        if got != expected:
            mismatches.append(s["id"])
    print(f"prompt identity: {len(samples) - len(mismatches)}/{len(samples)} ok; mean steps {n_steps / len(samples):.2f} "
          f"vs mean calls {sum(len(s['label']['tool_calls']) for s in samples) / len(samples):.2f}")
    if mismatches:
        print("  mismatches:", mismatches[:10])
    res = evaluate(pred, gold_from_train("train", DEFAULT_ROOT), fuzzy_params(cat))
    print(f"replayed steps score: {res['score']:.2f}")

    tok = Tokenizer.from_file(hf_hub_download("Qwen/Qwen3-4B-Instruct-2507", "tokenizer.json"))
    rng, bad = random.Random(0), 0
    for s in rng.sample(samples, 300):
        hist = [h["audio_text"] for h in s["history"] if h["role"] == "user"]
        segs = build_example(s, s["audio_text"], hist, s["label"]["tool_calls"], s["label"]["tool_results"], tools, apps)
        whole = tok.encode("".join(t for t, _ in segs), add_special_tokens=False).ids
        parts = [i for t, _ in segs for i in tok.encode(t, add_special_tokens=False).ids]
        bad += whole != parts
    print(f"token boundaries: {300 - bad}/300 identical")


if __name__ == "__main__":
    main()
