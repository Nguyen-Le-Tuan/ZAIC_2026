"""Off-the-shelf Whisper-family ASR over every wav of a split, written in the ASR-file contract that infer.py reads.

  python -m lifemate.asr --split train --ids splits/dev_random.txt --model openai/whisper-large-v3-turbo \
      --revision 41f01f3fe87f28c78e2fbf8b568835947dd65ed9 --out asr/train_dev_random_turbo.jsonl

One row per wav: {"audio": "audio/<id>/<file>.wav", "text": ..., "seconds": ...}. Covers the final turn and every user
turn of the history (test history turns are audio-only). "seconds" is decode wall time; with --batch-size > 1 it is the
batch time shared equally, so use --batch-size 1 to measure latency.

Reads only <split>.jsonl and <split>/audio/, never <split>_environment/. Greedy decoding, Vietnamese, transcribe. The text
is the raw model output (stripped): no number normalisation. Never overwrites an earlier file.

--beams N (N > 1): beam search with N beams on each sample's final turn only (the sample's own `audio`, final_paths);
the user turns of the history stay greedy. Final-turn wavs are batched among themselves, batch-size // N at a time
(at least 1), so a batch holds about as many decoder sequences as a greedy one. --beams 1 (default) is the greedy run,
with the same batches and the same generate() call as before the option existed.
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
from .seeding import DEFAULT_SEED, seed_everything

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


def final_paths(items) -> set[str]:
    """The final user turn of each sample: its own `audio` (the scored request). `history[*].audio` are earlier user
    turns and are not in the set."""
    return {s["audio"] for s in items}


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
    """Whisper-architecture model (openai/whisper-*, vinai/PhoWhisper-*): Vietnamese transcription, greedy unless a
    call asks for beams."""

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

    def __call__(self, audios: list[np.ndarray], num_beams: int = 1) -> list[str]:
        """One transcript per wav: greedy (num_beams=1) or beam search, the best beam."""
        feats = self.processor.feature_extractor(audios, sampling_rate=SR, return_tensors="pt")
        x = feats.input_features.to(self.device, self.dtype)
        with self.torch.inference_mode():
            ids = self.model.generate(x, language="vi", task="transcribe", num_beams=num_beams, do_sample=False,
                                      max_new_tokens=MAX_NEW_TOKENS)
        if self.device == "cuda":
            self.torch.cuda.synchronize()
        return [t.strip() for t in self.processor.batch_decode(ids, skip_special_tokens=True)]

    def warmup(self, seconds: float = 1.0, max_new_tokens: int = 8, num_beams: int = 1) -> None:
        """One untimed decode of silence right after loading, so the first wav does not pay one-off GPU setup in
        its timed seconds. Whisper pads every input to 30 s, so the encoder runs at full size; output is discarded.
        num_beams > 1 warms up the beam-search path the same way."""
        x = self.processor.feature_extractor([np.zeros(int(SR * seconds), dtype=np.float32)], sampling_rate=SR,
                                             return_tensors="pt").input_features.to(self.device, self.dtype)
        with self.torch.inference_mode():
            self.model.generate(x, language="vi", task="transcribe", num_beams=num_beams, do_sample=False,
                                max_new_tokens=max_new_tokens)
        if self.device == "cuda":
            self.torch.cuda.synchronize()


def decode_passes(paths: list[str], batch_size: int, beams: int = 1, final: set[str] | None = None):
    """[(num_beams, wavs, batch size)]: the decoding passes of a run. beams = 1: one greedy pass over every wav.
    beams > 1: a greedy pass over the wavs not in `final`, then a beam pass over those in `final` (each sample's own
    final turn, final_paths), batch_size // beams at a time (at least 1); no batch mixes the two."""
    if beams < 1:
        raise ValueError(f"beams must be at least 1, got {beams}")
    if beams == 1:
        return [(1, list(paths), batch_size)]
    if final is None:
        raise ValueError("beams > 1 needs the final-turn wavs (final_paths(items))")
    return [(1, [p for p in paths if p not in final], batch_size),
            (beams, [p for p in paths if p in final], max(1, batch_size // beams))]


def transcribe(asr, root_split: Path, paths: list[str], batch_size: int, beams: int = 1,
               final: set[str] | None = None) -> list[dict]:
    """Rows in the order of `paths`. Batches group wavs of similar length so short ones do not wait for long ones.
    With beams > 1 the wavs in `final` are decoded with that many beams and the others greedily (decode_passes);
    the greedy calls are asr(batch), exactly as without beams."""
    audio = {p: read_wav(root_split / p) for p in paths}
    rows = {}
    for num_beams, group, size in decode_passes(paths, batch_size, beams, final):
        order = sorted(group, key=lambda p: len(audio[p]))
        for i in range(0, len(order), size):
            batch = order[i:i + size]
            t0 = time.monotonic()
            x = [audio[p] for p in batch]
            texts = asr(x) if num_beams == 1 else asr(x, num_beams=num_beams)
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
    ap.add_argument("--beams", type=int, default=1,
                    help="beam search with this many beams on each sample's final turn (its own `audio`); history "
                         "turns stay greedy; final-turn batches hold batch-size // beams wavs (at least 1). "
                         "1 (default) = greedy everywhere, the run as before this option")
    ap.add_argument("--no-warmup", action="store_true", help="skip the untimed decode of silence after loading")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--out", required=True)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    if a.beams < 1:
        ap.error("--beams must be at least 1")

    meta_path = Path(a.out).with_suffix(".meta.json")
    runinfo.refuse_existing(a.out, meta_path, overwrite=a.overwrite)
    seed_everything(a.seed)
    started = runinfo.now()
    items = load_split(a.split, a.root)
    if a.ids:
        keep = set(runinfo.read_ids(a.ids))
        items = [s for s in items if s["id"] in keep]
    items = items[: a.limit] if a.limit else items
    paths = wav_paths(items)[: a.max_wavs] if a.max_wavs else wav_paths(items)
    final = final_paths(items)

    t0 = time.monotonic()
    asr = Whisper(a.model, a.revision, a.device, a.dtype)
    load_s = time.monotonic() - t0
    warmup_s = None
    if not a.no_warmup:
        tw = time.monotonic()
        asr.warmup()
        if a.beams > 1:
            asr.warmup(num_beams=a.beams)
        warmup_s = round(time.monotonic() - tw, 3)
    rows = transcribe(asr, Path(a.root) / a.split, paths, a.batch_size, beams=a.beams, final=final)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(a.out, rows)

    secs = [r["seconds"] for r in rows]
    audio_s = sum(r["audio_s"] for r in rows)
    timing = {"load_s": round(load_s, 1), "warmup_s": warmup_s, "decode_s": round(sum(secs), 1), "audio_s": round(audio_s, 1),
              "rtf": round(sum(secs) / max(audio_s, 1e-9), 4), "mean_s": round(sum(secs) / max(len(secs), 1), 4),
              "p95_s": round(runinfo.percentile(secs, .95), 4), "max_s": max(secs, default=0)}
    fin = [r["seconds"] for r in rows if r["audio"] in final]
    timing_final = {"wavs": len(fin), "mean_s": round(sum(fin) / max(len(fin), 1), 4),
                    "p95_s": round(runinfo.percentile(fin, .95), 4), "max_s": max(fin, default=0)}
    runinfo.write_json(meta_path, {
        "kind": "asr", "started": started, "finished": runinfo.now(), "args": vars(a),
        "model": a.model, "revision": a.revision, "commit": asr.commit, "device": asr.device, "dtype": asr.dtype_name,
        "samples": runinfo.ids_digest(s["id"] for s in items), "ids_file_sha256": runinfo.sha256_file(a.ids) if a.ids else None,
        "wavs": len(rows), "empty": sum(not r["text"] for r in rows), "timing": timing,
        "beams": a.beams, "final_wavs": len(fin), "timing_final": timing_final,
        "git": runinfo.git_state(), "env": runinfo.env_info(),
        "note": "seconds = decode wall time on this machine; shared equally within a batch when --batch-size > 1; "
                "beams applies to the final_wavs (each sample's own audio) only, the history turns are greedy"})
    print(json.dumps({"wavs": len(rows), "out": a.out, **timing}))


if __name__ == "__main__":
    main()
