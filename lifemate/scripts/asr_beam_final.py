"""Beam-search transcripts of each sample's final turn, merged into a copy of an existing greedy ASR file.

  .venv/bin/python scripts/asr_beam_final.py --greedy asr/train_dev_union_phoft_v8.jsonl --ids <ids file> \
      --model ckpt/asr_phoft/merged --beams 4 --out asr/train_dev_union_phoft_v8_beam4.jsonl

The final turns (each sample's own `audio`, lifemate.asr.final_paths) are decoded by lifemate.asr's Whisper through
transcribe(..., beams=N), --batch-size at a time (default 1, so "seconds" is that wav's latency, as in docker/predict.sh).
Every other row of --greedy (the user history turns) is copied unchanged, in the greedy file's order. The output has
the greedy file's rows and record format ({"audio", "text", "seconds", "audio_s"}) and differs only in the final-turn
records: the file `lifemate.asr --beams N` writes, without decoding the history turns a second time.

Reads only <split>.jsonl and <split>/audio/, never <split>_environment/. Never overwrites an earlier file.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate import runinfo  # noqa: E402
from lifemate.asr import Whisper, final_paths, transcribe, wav_paths  # noqa: E402
from lifemate.data import DEFAULT_ROOT, load_jsonl, load_split, write_jsonl  # noqa: E402
from lifemate.seeding import DEFAULT_SEED, seed_everything  # noqa: E402


def merge(greedy_rows: list[dict], beam_rows: list[dict]) -> list[dict]:
    """The greedy rows in their order, each final-turn row replaced by its beam row (same keys)."""
    beam = {r["audio"]: r for r in beam_rows}
    out = []
    for g in greedy_rows:
        b = beam.get(g["audio"])
        if b is not None and set(b) != set(g):
            raise ValueError(f"{g['audio']}: beam row keys {sorted(b)} differ from the greedy row's {sorted(g)}")
        out.append(b if b is not None else g)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--greedy", required=True, help="greedy lifemate.asr file of the same samples (history rows source)")
    ap.add_argument("--split", default="train")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--ids", required=True, help="file with sample ids (the greedy run's)")
    ap.add_argument("--model", required=True)
    ap.add_argument("--revision")
    ap.add_argument("--device")
    ap.add_argument("--dtype", choices=["fp16", "bf16", "fp32"])
    ap.add_argument("--batch-size", type=int, default=1)
    ap.add_argument("--beams", type=int, default=4)
    ap.add_argument("--no-warmup", action="store_true", help="skip the untimed decodes of silence after loading")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--out", required=True)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    if a.beams < 2:
        ap.error("--beams must be at least 2 (1 is the greedy file itself)")

    meta_path = Path(a.out).with_suffix(".meta.json")
    runinfo.refuse_existing(a.out, meta_path, overwrite=a.overwrite)
    seed_everything(a.seed)
    started = runinfo.now()
    keep = set(runinfo.read_ids(a.ids))
    items = [s for s in load_split(a.split, a.root) if s["id"] in keep]
    greedy_rows = load_jsonl(a.greedy)
    greedy_meta_path = Path(a.greedy).with_suffix(".meta.json")
    greedy_meta = json.loads(greedy_meta_path.read_text()) if greedy_meta_path.exists() else {}
    if greedy_meta.get("beams", 1) != 1:
        sys.exit(f"{a.greedy}: not a greedy file (beams {greedy_meta['beams']})")
    want = wav_paths(items)
    got = [r["audio"] for r in greedy_rows]
    if sorted(got) != sorted(want):
        sys.exit(f"{a.greedy}: its {len(got)} wavs are not the {len(want)} wavs of the {len(items)} selected samples")
    final = final_paths(items)
    final_list = [p for p in got if p in final]

    t0 = time.monotonic()
    asr = Whisper(a.model, a.revision, a.device, a.dtype)
    load_s = time.monotonic() - t0
    warmup_s = None
    if not a.no_warmup:
        tw = time.monotonic()
        asr.warmup()
        asr.warmup(num_beams=a.beams)
        warmup_s = round(time.monotonic() - tw, 3)
    beam_rows = transcribe(asr, Path(a.root) / a.split, final_list, a.batch_size, beams=a.beams, final=final)
    greedy_by = {r["audio"]: r for r in greedy_rows}
    bad = [r["audio"] for r in beam_rows if r["audio_s"] != greedy_by[r["audio"]]["audio_s"]]
    if bad:
        sys.exit(f"audio_s differs from {a.greedy} for {len(bad)} wavs (first {bad[0]})")
    rows = merge(greedy_rows, beam_rows)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(a.out, rows)

    secs = [r["seconds"] for r in beam_rows]
    audio_s = sum(r["audio_s"] for r in beam_rows)
    timing = {"load_s": round(load_s, 1), "warmup_s": warmup_s, "decode_s": round(sum(secs), 1),
              "audio_s": round(audio_s, 1), "rtf": round(sum(secs) / max(audio_s, 1e-9), 4),
              "mean_s": round(sum(secs) / max(len(secs), 1), 4), "p95_s": round(runinfo.percentile(secs, .95), 4),
              "max_s": max(secs, default=0)}
    changed = sum(r["text"] != greedy_by[r["audio"]]["text"] for r in beam_rows)
    runinfo.write_json(meta_path, {
        "kind": "asr", "started": started, "finished": runinfo.now(), "args": vars(a),
        "model": a.model, "revision": a.revision, "commit": asr.commit, "device": asr.device, "dtype": asr.dtype_name,
        "samples": runinfo.ids_digest(s["id"] for s in items), "ids_file_sha256": runinfo.sha256_file(a.ids),
        "wavs": len(rows), "empty": sum(not r["text"] for r in rows), "beams": a.beams,
        "final_wavs": len(beam_rows), "final_changed_vs_greedy": changed, "timing": timing, "timing_final": timing,
        "history_rows_from": {"file": str(a.greedy), "sha256": runinfo.sha256_file(a.greedy),
                              "rows_copied": len(rows) - len(beam_rows),
                              "meta_git": greedy_meta.get("git"), "meta_args": greedy_meta.get("args")},
        "git": runinfo.git_state(), "env": runinfo.env_info(),
        "note": f"final-turn rows decoded here with {a.beams} beams, --batch-size {a.batch_size} (seconds = that "
                f"wav's decode wall time when 1); every other row copied unchanged from the greedy file; timing "
                f"covers the decoded final-turn wavs only"})
    print(json.dumps({"final_wavs": len(beam_rows), "changed_vs_greedy": changed, "rows": len(rows), "out": a.out,
                      **timing}))


if __name__ == "__main__":
    main()
