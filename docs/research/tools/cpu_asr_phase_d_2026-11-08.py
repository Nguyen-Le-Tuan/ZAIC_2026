"""CPU-only LifeMate dev_random ASR probe; never stores transcripts.

Usage (from repo root):
  python docs/research/tools/cpu_asr_phase_d_2026-11-08.py inspect
  CUDA_VISIBLE_DEVICES='' HF_HOME=/tmp/zac_phase_d_hf python \
      docs/research/tools/cpu_asr_phase_d_2026-11-08.py run moonshine

Reads only train.jsonl and final-turn WAV paths from 100 dev_random IDs.  Model
artifacts are pinned to the research CSV revision and cached under HF_HOME.
The caller must delete HF_HOME after all probes.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import threading
import time
import unicodedata
import wave

REPO_ROOT = Path(__file__).resolve().parents[3]
TRAIN_ROOT = REPO_ROOT / "data" / "train+public_test" / "train"
IDS_FILE = REPO_ROOT / "lifemate" / "splits" / "dev_random.txt"
CANDIDATES = REPO_ROOT / "docs" / "research" / "model_candidates_2026-11-08.csv"
LIMIT = 100
RSS_LIMIT = 1_850_000_000  # Leave margin below the brief's 2 GB RAM limit.

MODELS = {
    "gipformer": ("g-group-ai-lab/gipformer1.5-68M-rnnt", [
        "encoder.int8.onnx", "decoder.int8.onnx", "joiner.int8.onnx", "tokens.txt"]),
    "moonshine": ("moonshine-ai/moonshine-streaming-tiny-vi", [
        "model.safetensors", "config.json", "generation_config.json",
        "preprocessor_config.json", "processor_config.json", "special_tokens_map.json",
        "tokenizer.json", "tokenizer_config.json"]),
    "pho_tiny": ("vinai/PhoWhisper-tiny", [
        "pytorch_model.bin", "config.json", "generation_config.json", "added_tokens.json",
        "merges.txt", "normalizer.json", "preprocessor_config.json",
        "special_tokens_map.json", "tokenizer.json", "tokenizer_config.json", "vocab.json"]),
    "pho_base": ("vinai/PhoWhisper-base", [
        "pytorch_model.bin", "config.json", "generation_config.json", "added_tokens.json",
        "merges.txt", "normalizer.json", "preprocessor_config.json",
        "special_tokens_map.json", "tokenizer.json", "tokenizer_config.json", "vocab.json"]),
}


def samples() -> list[dict]:
    ids = IDS_FILE.read_text(encoding="utf-8").split()[:LIMIT]
    wanted = set(ids)
    found = {}
    with (TRAIN_ROOT / "train.jsonl").open(encoding="utf-8") as fp:
        for line in fp:
            row = json.loads(line)
            if str(row["id"]) in wanted:
                found[str(row["id"])] = row
    if len(found) != len(ids):
        raise RuntimeError(f"Only {len(found)}/{len(ids)} dev_random IDs in train.jsonl")
    return [found[i] for i in ids]


def wav_info(row: dict) -> tuple[Path, float]:
    rel = Path(row["audio"])
    if rel.is_absolute() or ".." in rel.parts or any(x.endswith("_environment") for x in rel.parts):
        raise ValueError("Forbidden audio path in train sample")
    root = TRAIN_ROOT.resolve()
    path = (root / rel).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Audio path escapes train root")
    with wave.open(str(path), "rb") as w:
        if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (1, 2, 16000):
            raise ValueError("Expected mono 16-bit 16 kHz PCM")
        return path, w.getnframes() / 16000


def read_wav(path: Path):
    import numpy as np
    with wave.open(str(path), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype("float32") / 32768.0


def revision(repo: str) -> str:
    import csv
    for row in csv.DictReader(CANDIDATES.open(encoding="utf-8")):
        if row["repo_id"] == repo:
            if not row["revision"]:
                raise RuntimeError(f"Missing revision for {repo}")
            return row["revision"]
    raise RuntimeError(f"Candidate missing: {repo}")


def download(model: str) -> Path:
    from huggingface_hub import HfApi, snapshot_download
    repo, files = MODELS[model]
    rev = revision(repo)
    entries = HfApi().list_repo_tree(repo, revision=rev, recursive=True)
    sizes = {x.path: x.size for x in entries if hasattr(x, "size")}
    if not all(name in sizes for name in files):
        raise RuntimeError("Model file manifest does not match pinned revision")
    weight_bytes = sum(sizes[name] for name in files if name.endswith((".bin", ".onnx", ".safetensors")))
    if weight_bytes >= 500_000_000:
        raise RuntimeError(f"Model weight budget exceeded: {weight_bytes}")
    all_weight_bytes = 151_099_049 + 290_458_785 + 108_079_716 + 73_218_466
    if all_weight_bytes >= 2_000_000_000:
        raise RuntimeError("Overall four-model budget exceeded")
    print(json.dumps({"model": model, "revision": rev, "weight_bytes": weight_bytes}), flush=True)
    return Path(snapshot_download(repo_id=repo, revision=rev, allow_patterns=files))


def memory_guard() -> dict:
    import psutil
    proc = psutil.Process()
    state = {"peak_rss": 0, "done": False}

    def loop():
        while not state["done"]:
            rss = proc.memory_info().rss
            state["peak_rss"] = max(state["peak_rss"], rss)
            if rss >= RSS_LIMIT:
                sys.stderr.write(f"RAM guard stopped process at {rss} bytes\n")
                sys.stderr.flush()
                os._exit(71)
            time.sleep(0.05)

    threading.Thread(target=loop, daemon=True).start()
    return state


def load_model(name: str, local: Path):
    if name == "gipformer":
        import sherpa_onnx
        recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=str(local / "encoder.int8.onnx"), decoder=str(local / "decoder.int8.onnx"),
            joiner=str(local / "joiner.int8.onnx"), tokens=str(local / "tokens.txt"),
            num_threads=1, sample_rate=16000, feature_dim=80, decoding_method="greedy_search")

        def infer(audio):
            stream = recognizer.create_stream()
            stream.accept_waveform(16000, audio)
            recognizer.decode_streams([stream])
            return stream.result.text.strip()

        return infer

    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    from transformers import AutoProcessor, MoonshineStreamingForConditionalGeneration, WhisperForConditionalGeneration, WhisperProcessor
    if name == "moonshine":
        processor = AutoProcessor.from_pretrained(local, local_files_only=True)
        model = MoonshineStreamingForConditionalGeneration.from_pretrained(local, local_files_only=True).eval()

        def infer(audio):
            inputs = processor(audio, return_tensors="pt", sampling_rate=16000)
            max_new = int(len(audio) * 6.5 / 16000) + 2
            with torch.inference_mode():
                ids = model.generate(**inputs, max_new_tokens=max_new, do_sample=False, num_beams=1)
            return processor.batch_decode(ids, skip_special_tokens=True)[0].strip()

        return infer

    processor = WhisperProcessor.from_pretrained(local, local_files_only=True)
    model = WhisperForConditionalGeneration.from_pretrained(local, local_files_only=True, use_safetensors=False).eval()
    model.generation_config.max_length = 224

    def infer(audio):
        features = processor.feature_extractor(audio, sampling_rate=16000, return_tensors="pt").input_features
        with torch.inference_mode():
            ids = model.generate(features, language="vi", task="transcribe", num_beams=1,
                                 do_sample=False, use_cache=True)
        return processor.batch_decode(ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()

    return infer


def norm(s: str) -> str:
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFC", s).lower()))


def name_proxy(ref: str) -> list[str]:
    """Capitalized words within a sentence: a limited proxy, not named-entity gold."""
    out = []
    for m in re.finditer(r"(?<!\w)[A-ZÀ-Ỹ][\w-]*", ref):
        prefix = ref[:m.start()].rstrip()
        if prefix and prefix[-1] not in ".!?\n":
            out.append(m.group())
    return out


def slot_counts(ref: str, hyp: str) -> dict[str, tuple[int, int]]:
    from lifemate.vinum import find_form, time_forms, value_forms
    times = []
    occupied = []
    for m in re.finditer(r"(?<!\d)(\d{1,2})\s*(?::|h|giờ)\s*(\d{2})?(?!\d)", ref.lower()):
        h, minute = int(m.group(1)), int(m.group(2) or 0)
        if h < 24 and minute < 60:
            times.append((h, minute))
            occupied.append(m.span())
    numbers = []
    for m in re.finditer(r"(?<!\w)\d+(?:[.,]\d+)*(?!\w)", ref):
        if any(a <= m.start() < b for a, b in occupied):
            continue
        digits = m.group().replace(".", "").replace(",", "")
        if digits.isdigit() and len(digits) <= 11:
            numbers.append(int(digits))
    time_ok = sum(find_form(hyp, time_forms(h, minute)) is not None for h, minute in times)
    num_ok = sum(find_form(hyp, value_forms(n)) is not None for n in numbers)
    names = name_proxy(ref)
    hyp_n = f" {norm(hyp)} "
    name_ok = sum(f" {norm(x)} " in hyp_n for x in names)
    return {"numbers": (len(numbers), num_ok), "times": (len(times), time_ok),
            "name_proxy": (len(names), name_ok)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["inspect", "run"])
    parser.add_argument("model", nargs="?", choices=list(MODELS))
    args = parser.parse_args()
    rows = samples()
    paths = [wav_info(row) for row in rows]
    if args.action == "inspect":
        durations = [x[1] for x in paths]
        print(json.dumps({"samples": len(rows), "audio_seconds": round(sum(durations), 2),
                          "max_clip_seconds": round(max(durations), 2),
                          "capitalized_internal_tokens": sum(len(name_proxy(r["audio_text"])) for r in rows)},
                         ensure_ascii=False))
        return
    if not args.model or os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("run requires model and CUDA_VISIBLE_DEVICES='' exactly")
    import sys as _sys
    _sys.path.insert(0, str(REPO_ROOT / "lifemate"))
    from lifemate.asr_train import wer
    state = memory_guard()
    local = download(args.model)
    infer = load_model(args.model, local)
    refs, hyps = [], []
    totals = {k: [0, 0] for k in ("numbers", "times", "name_proxy")}
    tic = time.perf_counter()
    for i, (row, (path, _duration)) in enumerate(zip(rows, paths), 1):
        hyp = infer(read_wav(path))
        ref = row["audio_text"]
        refs.append(ref)
        hyps.append(hyp)
        for key, (n, ok) in slot_counts(ref, hyp).items():
            totals[key][0] += n
            totals[key][1] += ok
        if i % 10 == 0:
            print(json.dumps({"completed": i, "elapsed_s": round(time.perf_counter()-tic, 1),
                              "peak_rss_mb": round(state["peak_rss"] / 1e6, 1)}), flush=True)
    elapsed = time.perf_counter() - tic
    state["done"] = True
    print(json.dumps({"model": args.model, "samples": len(refs), "wer": wer(refs, hyps),
                      "raw_wer": wer(refs, hyps, raw=True),
                      "slots": {k: {"n": v[0], "kept": v[1],
                                    "pct": round(100*v[1]/v[0], 1) if v[0] else None}
                                for k, v in totals.items()},
                      "audio_seconds": round(sum(d for _, d in paths), 2),
                      "runtime_seconds": round(elapsed, 2), "rtf": round(elapsed/sum(d for _, d in paths), 3),
                      "peak_rss_mb": round(state["peak_rss"]/1e6, 1)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
