"""Token length of the full agent prompt per sample (Qwen3 tokenizer), to check the 16K context limit.

train: system + history + request + gold calls/results (the longest the context gets).
public_test: no transcripts, so each user turn is replaced by a typical 60-char sentence.
"""
import argparse
import statistics as st
import sys
from pathlib import Path

from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate.data import DEFAULT_ROOT, catalog_tools, load_catalog, load_split  # noqa: E402
from lifemate.prompt import build_messages, render_calls, render_results, to_chatml  # noqa: E402

PLACEHOLDER = "Nhắn Zalo cho vợ là chiều nay anh đón con muộn một chút nha em."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B-Instruct-2507")
    a = ap.parse_args()
    tok = Tokenizer.from_file(hf_hub_download(a.model, "tokenizer.json"))
    for split in ["train", "public_test"]:
        cat = load_catalog(split)
        tools, apps = catalog_tools(cat), {x["id"]: x for x in cat["apps"]}
        lens, sys_lens, worst = [], [], None
        for s in load_split(split):
            labelled = "label" in s
            hist_texts = [h.get("audio_text") or PLACEHOLDER for h in s["history"] if h["role"] == "user"]
            msgs = build_messages(s, s.get("audio_text") or PLACEHOLDER, hist_texts, tools, apps)
            text = to_chatml(msgs)
            if labelled:
                for c, r in zip(s["label"]["tool_calls"], s["label"]["tool_results"]):
                    text += render_calls([c]) + "<|im_end|>\n<|im_start|>user\n" + render_results([r]) + "<|im_end|>\n<|im_start|>assistant\n"
            n = len(tok.encode(text).ids)
            lens.append(n)
            sys_lens.append(len(tok.encode(msgs[0]["content"]).ids))
            if worst is None or n > worst[0]:
                worst = (n, s["id"])
        lens.sort()
        q = lambda p: lens[int(p * (len(lens) - 1))]  # noqa: E731
        print(f"{split}: system mean {st.mean(sys_lens):.0f} max {max(sys_lens)} | full mean {st.mean(lens):.0f} "
              f"p50 {q(.5)} p95 {q(.95)} p99 {q(.99)} max {worst[0]} ({worst[1]}) | >12K: {sum(x > 12000 for x in lens)} >16K: {sum(x > 16384 for x in lens)}")


if __name__ == "__main__":
    main()
