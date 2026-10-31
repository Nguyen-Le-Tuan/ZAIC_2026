"""Off-the-shelf Whisper-family ASR over every wav of a split, written in the ASR-file contract that infer.py reads.

  python -m lifemate.asr --split train --ids splits/dev_random.txt --model openai/whisper-large-v3-turbo \
      --revision 41f01f3fe87f28c78e2fbf8b568835947dd65ed9 --out asr/train_dev_random_turbo.jsonl

One row per wav: {"audio": "audio/<id>/<file>.wav", "text": ..., "seconds": ...}. Covers the final turn and every user
turn of the history (test history turns are audio-only). "seconds" is decode wall time; with --batch-size > 1 it is the
batch time shared equally, so use --batch-size 1 to measure latency.

Reads only <split>.jsonl and <split>/audio/, never <split>_environment/. Greedy decoding, Vietnamese, transcribe. The text
is the raw model output (stripped): no number normalisation. Never overwrites an earlier file.
"""
from __future__ import annotations

import argparse
import json
import time
import wave
from pathlib import Path

import numpy as np

from . import runinfo
from .data import DEFAULT_ROOT, load_split, write_jsonl

SR = 16000
MAX_S = 30.0  # Whisper's window; the data's longest wav is 17.1 s, so no long-form decoding is needed
MAX_NEW_TOKENS = 440  # Whisper decoders have 448 positions, minus the forced prompt tokens


def wav_paths(items) -> list[str]:
    """Unique audio paths (relative to the split folder): each sample's final turn, then its user history turns."""
    seen, out = set(), []
    for s in items:
        for p in [s["audio"]] + [h["audio"] for h in s.get("history", []) if h["role"] == "user"]:
            if p not in seen:
                seen.add(p)
                out.append(p)
    return out


def read_wav(path) -> np.ndarray:
    """16 kHz mono 16-bit PCM wav as float32 in [-1, 1]; anything else is an error, not a silent resample."""
    if any(part.endswith("_environment") for part in Path(path).parts):
        raise ValueError(f"{path}: agent code must not read <split>_environment/")
    with wave.open(str(path), "rb") as w:
        fmt = (w.getnchannels(), w.getsampwidth(), w.getframerate())
        if fmt != (1, 2, SR):
            raise ValueError(f"{path}: expected 16 kHz mono 16-bit PCM, got {fmt[0]} ch, {8 * fmt[1]} bit, {fmt[2]} Hz")
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
    if len(x) / SR > MAX_S:
        raise ValueError(f"{path}: {len(x) / SR:.1f} s is longer than {MAX_S:.0f} s")
    return x


class Whisper:
    """Whisper-architecture model (openai/whisper-*, vinai/PhoWhisper-*) with greedy Vietnamese transcription."""

    def __init__(self, model: str, revision: str | None = None, device: str | None = None, dtype: str | None = None):
        import torch
        from transformers import WhisperForConditionalGeneration, WhisperProcessor

        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype_name = dtype or ("fp16" if self.device == "cuda" else "fp32")
        self.dtype = {"fp16": torch.float16, "bf16": torch.bfloat16, "fp32": torch.float32}[self.dtype_name]
        self.processor = WhisperProcessor.from_pretrained(model, revision=revision)
        self.model = WhisperForConditionalGeneration.from_pretrained(model, revision=revision, dtype=self.dtype)
        self.model.to(self.device).eval()
        self.commit = getattr(self.model.config, "_commit_hash", None)

    def __call__(self, audios: list[np.ndarray]) -> list[str]:
        feats = self.processor.feature_extractor(audios, sampling_rate=SR, return_tensors="pt")
        x = feats.input_features.to(self.device, self.dtype)
        with self.torch.inference_mode():
            ids = self.model.generate(x, language="vi", task="transcribe", num_beams=1, do_sample=False,
                                      max_new_tokens=MAX_NEW_TOKENS)
        if self.device == "cuda":
            self.torch.cuda.synchronize()
        return [t.strip() for t in self.processor.batch_decode(ids, skip_special_tokens=True)]


def transcribe(asr, root_split: Path, paths: list[str], batch_size: int) -> list[dict]:
    """Rows in the order of `paths`. Batches group wavs of similar length so short ones do not wait for long ones."""
    audio = {p: read_wav(root_split / p) for p in paths}
    order = sorted(paths, key=lambda p: len(audio[p]))
    rows = {}
    for i in range(0, len(order), batch_size):
        batch = order[i:i + batch_size]
        t0 = time.monotonic()
        texts = asr([audio[p] for p in batch])
        dt = (time.monotonic() - t0) / len(batch)
        for p, t in zip(batch, texts):
            rows[p] = {"audio": p, "text": t, "seconds": round(dt, 4), "audio_s": round(len(audio[p]) / SR, 3)}
    return [rows[p] for p in paths]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="train")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--ids", help="file with sample ids (default: every sample of the split)")
    ap.add_argument("--limit", type=int, help="first N samples only")
    ap.add_argument("--max-wavs", type=int, help="first N wavs only (smoke and reproducibility checks)")
    ap.add_argument("--model", default="openai/whisper-large-v3-turbo")
    ap.add_argument("--revision")
    ap.add_argument("--device")
    ap.add_argument("--dtype", choices=["fp16", "bf16", "fp32"])
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--out", required=True)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()

    meta_path = Path(a.out).with_suffix(".meta.json")
    runinfo.refuse_existing(a.out, meta_path, overwrite=a.overwrite)
    started = runinfo.now()
    items = load_split(a.split, a.root)
    if a.ids:
        keep = set(runinfo.read_ids(a.ids))
        items = [s for s in items if s["id"] in keep]
    items = items[: a.limit] if a.limit else items
    paths = wav_paths(items)[: a.max_wavs] if a.max_wavs else wav_paths(items)

    t0 = time.monotonic()
    asr = Whisper(a.model, a.revision, a.device, a.dtype)
    load_s = time.monotonic() - t0
    rows = transcribe(asr, Path(a.root) / a.split, paths, a.batch_size)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(a.out, rows)

    secs = [r["seconds"] for r in rows]
    audio_s = sum(r["audio_s"] for r in rows)
    timing = {"load_s": round(load_s, 1), "decode_s": round(sum(secs), 1), "audio_s": round(audio_s, 1),
              "rtf": round(sum(secs) / max(audio_s, 1e-9), 4), "mean_s": round(sum(secs) / max(len(secs), 1), 4),
              "p95_s": round(runinfo.percentile(secs, .95), 4), "max_s": max(secs, default=0)}
    runinfo.write_json(meta_path, {
        "kind": "asr", "started": started, "finished": runinfo.now(), "args": vars(a),
        "model": a.model, "revision": a.revision, "commit": asr.commit, "device": asr.device, "dtype": asr.dtype_name,
        "samples": runinfo.ids_digest(s["id"] for s in items), "ids_file_sha256": runinfo.sha256_file(a.ids) if a.ids else None,
        "wavs": len(rows), "empty": sum(not r["text"] for r in rows), "timing": timing,
        "git": runinfo.git_state(), "env": runinfo.env_info(),
        "note": "seconds = decode wall time on this machine; shared equally within a batch when --batch-size > 1"})
    print(json.dumps({"wavs": len(rows), "out": a.out, **timing}))


if __name__ == "__main__":
    main()
