"""Where the agent loses points on ASR text: per-sample score drop (oracle text run vs ASR text run of the same
checkpoint) bucketed by the word error rate of the final turn, plus Whisper-style hallucinations. Read-only, train only.

  .venv/bin/python scripts/asr_loss.py --asr turbo --json runs/asr_loss_turbo.json

Needs asr/train_<dev>_<asr>.jsonl, runs/sft_<ckpt>_rows.jsonl and runs/sft_<ckpt>_asr<asr>_rows.jsonl for each pair below.
lost_pts = points of the dev total (100 scale) lost inside the bucket; the buckets add up to the whole drop.
"""
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from asr_quality import edit_distance, words  # noqa: E402
from lifemate.data import load_jsonl, load_split  # noqa: E402
from lifemate.runinfo import read_ids, write_json  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PAIRS = (("dev_random", "q17b_fit_random"), ("dev_lao", "q17b_fit_lao"))
BUCKETS = ((0.10, "<10%"), (0.25, "10-25%"), (0.50, "25-50%"), (9e9, ">=50%"))
# phrases Whisper emits on silence or noise (YouTube outros); none occurs in audio_text of train
HALLUCINATION = re.compile(r"cảm ơn các bạn|theo dõi|đăng ký kênh|subscribe|ghiền mì gõ|hẹn gặp lại các bạn", re.I)


def wer(ref: str, hyp: str) -> float:
    r = words(ref)
    return edit_distance(r, words(hyp)) / max(1, len(r))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--asr", required=True, help="tag of asr/train_<dev>_<tag>.jsonl, e.g. turbo")
    ap.add_argument("--public", help="optional public ASR file, only to count hallucinations")
    ap.add_argument("--json")
    a = ap.parse_args()
    S = {s["id"]: s for s in load_split("train")}
    out = {"asr": a.asr, "devs": {}}
    for dev, ck in PAIRS:
        ids = read_ids(ROOT / "splits" / f"{dev}.txt")
        asr = {r["audio"]: r["text"] for r in load_jsonl(ROOT / "asr" / f"train_{dev}_{a.asr}.jsonl")}
        ref = {r["id"]: r["score"] for r in load_jsonl(ROOT / "runs" / f"sft_{ck}_rows.jsonl")}
        run = {r["id"]: r["score"] for r in load_jsonl(ROOT / "runs" / f"sft_{ck}_asr{a.asr}_rows.jsonl")}
        groups = defaultdict(list)
        hall_final = hall_any = 0
        for i in ids:
            s = S[i]
            w = wer(s["audio_text"], asr[s["audio"]])
            groups[next(name for top, name in BUCKETS if w < top)].append((ref[i], run[i]))
            turns = [s["audio"]] + [h["audio"] for h in s["history"] if h.get("role") == "user" and "audio" in h]
            hall_final += bool(HALLUCINATION.search(asr[s["audio"]]))
            hall_any += any(HALLUCINATION.search(asr[t]) for t in turns)
        n = len(ids)
        out["devs"][dev] = {
            "n": n,
            "drop": round(100 * sum(ref[i] - run[i] for i in ids) / n, 2),
            "final_wer_buckets": {name: {
                "n": len(g),
                "oracle_text": round(100 * sum(x for x, _ in g) / len(g), 1),
                "asr_text": round(100 * sum(y for _, y in g) / len(g), 1),
                "lost_pts": round(100 * sum(x - y for x, y in g) / n, 2),
            } for _, name in BUCKETS if (g := groups.get(name))},
            "hallucinated_final": hall_final,
            "hallucinated_any_turn": hall_any,
        }
    if a.public:
        rows = load_jsonl(ROOT / a.public)
        out["public_wavs_hallucinated"] = [sum(bool(HALLUCINATION.search(r["text"])) for r in rows), len(rows)]
    for dev, d in out["devs"].items():
        print(f"{dev}: drop {d['drop']:.2f}; hallucinated final {d['hallucinated_final']}, any turn {d['hallucinated_any_turn']}")
        for name, b in d["final_wer_buckets"].items():
            print(f"  final WER {name:7s} n {b['n']:3d}  oracle {b['oracle_text']:5.1f}  asr {b['asr_text']:5.1f}  lost {b['lost_pts']:5.2f}")
    if "public_wavs_hallucinated" in out:
        print("public wavs hallucinated:", out["public_wavs_hallucinated"])
    if a.json:
        write_json(ROOT / a.json, out)


if __name__ == "__main__":
    main()
