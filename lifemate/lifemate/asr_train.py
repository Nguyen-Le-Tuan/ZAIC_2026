"""Fine-tune a Whisper-architecture ASR (Whisper-large-v3-turbo, PhoWhisper-large) on the train wavs, with LoRA.

  python -m lifemate.asr_train --model openai/whisper-large-v3-turbo \
      --revision 41f01f3fe87f28c78e2fbf8b568835947dd65ed9 --out ckpt/asr_turbo_ft
  python -m lifemate.asr --split train --ids splits/dev_random.txt --model ckpt/asr_turbo_ft/merged \
      --out asr/train_dev_random_turboft.jsonl                      # then scripts/asr_quality.py, eval_ckpt.sh ASR_FILE=

Data: every wav of the train split (final turn and user history turns) with its audio_text as the label, minus every
sample listed in --exclude (default: dev_random and dev_lao, so both dev sets stay unheard and the whole pipeline can be
scored on them). A fixed --val-frac of the remaining samples (all their wavs) is held out; its WER, measured before
training and after each epoch, picks the epoch. Dev is never used to choose anything here.
Reads only train.jsonl and train/audio/, never public_test, never <split>_environment/.

Model: base weights in fp16 on one GPU (fits a 16 GB T4), LoRA on the attention and MLP projections of encoder and
decoder with fp32 adapter weights, fp16 autocast with a gradient scaler, gradient checkpointing, SpecAugment on.
The labels are the exact audio_text (capitals, punctuation, numbers as written there), so the ASR also learns the text
style the agent was trained on.

Writes to --out: adapter/ (best epoch, PEFT), merged/ (full fp16 model and processor; lifemate.asr --model loads it),
train_log.jsonl, split_ids.json, asr_train.meta.json. --merge-only rebuilds merged/ from adapter/ on another machine.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import time
from pathlib import Path

import numpy as np

from . import runinfo
from .asr import MAX_NEW_TOKENS, SR, read_wav
from .data import DEFAULT_ROOT, load_split

TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "out_proj", "fc1", "fc2"]  # encoder and decoder, self and cross attention


def utterances(s: dict) -> list[tuple[str, str]]:
    """(audio path, audio_text) for the final turn and every user history turn of one sample."""
    return [(s["audio"], s["audio_text"])] + [(h["audio"], h["audio_text"]) for h in s.get("history", [])
                                              if h["role"] == "user"]


def split_samples(items: list[dict], exclude: set[str], val_frac: float, seed: int) -> tuple[list[dict], list[dict]]:
    """Train / held-out samples from everything not excluded. Sample level, so no wav is in both."""
    pool = sorted((s for s in items if s["id"] not in exclude), key=lambda s: s["id"])
    rng = random.Random(seed)
    order = list(range(len(pool)))
    rng.shuffle(order)
    n_val = max(1, round(val_frac * len(pool))) if val_frac > 0 else 0
    val_idx = set(order[:n_val])
    return [s for i, s in enumerate(pool) if i not in val_idx], [s for i, s in enumerate(pool) if i in val_idx]


def pairs_of(samples: list[dict]) -> list[tuple[str, str]]:
    seen, out = set(), []
    for s in samples:
        for p, t in utterances(s):
            if p not in seen:
                seen.add(p)
                out.append((p, t))
    return out


def _words(s: str, raw: bool) -> list[str]:
    return s.split() if raw else re.findall(r"\w+", " ".join(s.lower().split()))


def _edits(a: list[str], b: list[str]) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def wer(refs: list[str], hyps: list[str], raw: bool = False) -> float:
    """Corpus WER in %. raw=False: lower case, punctuation dropped; raw=True: whitespace tokens as written."""
    errs = sum(_edits(_words(r, raw), _words(h, raw)) for r, h in zip(refs, hyps))
    return round(100 * errs / max(1, sum(len(_words(r, raw)) for r in refs)), 2)


class Utterances:
    """torch Dataset of (log-mel features, label ids) computed on the fly from the wavs."""

    def __init__(self, root_split: Path, pairs, processor):
        self.root, self.pairs, self.fe, self.tok = root_split, pairs, processor.feature_extractor, processor.tokenizer

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, i):
        path, text = self.pairs[i]
        feats = self.fe(read_wav(self.root / path), sampling_rate=SR, return_tensors="np").input_features[0]
        return feats.astype(np.float32), self.tok(text).input_ids


def make_collate(start_id: int):
    import torch

    def collate(batch):
        feats = torch.from_numpy(np.stack([f for f, _ in batch]))
        labels = [ids[1:] if ids and ids[0] == start_id else ids for _, ids in batch]  # the model prepends the start token
        n = max(len(x) for x in labels)
        lab = torch.full((len(labels), n), -100, dtype=torch.long)
        for k, x in enumerate(labels):
            lab[k, :len(x)] = torch.tensor(x)
        return feats, lab
    return collate


def transcribe(whisper, processor, root_split: Path, paths: list[str], batch_size: int, device, dtype) -> list[str]:
    import torch
    audio = {p: read_wav(root_split / p) for p in paths}
    order = sorted(paths, key=lambda p: len(audio[p]))
    out = {}
    whisper.eval()
    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.float16, enabled=device.type == "cuda"):
        for i in range(0, len(order), batch_size):
            batch = order[i:i + batch_size]
            x = processor.feature_extractor([audio[p] for p in batch], sampling_rate=SR, return_tensors="pt")
            ids = whisper.generate(x.input_features.to(device, dtype), language="vi", task="transcribe", num_beams=1,
                                   do_sample=False, max_new_tokens=MAX_NEW_TOKENS, use_cache=True)
            for p, t in zip(batch, processor.batch_decode(ids, skip_special_tokens=True)):
                out[p] = t.strip()
    return [out[p] for p in paths]


def load_base(model: str, revision: str | None, device, dtype):
    from transformers import WhisperForConditionalGeneration, WhisperProcessor
    processor = WhisperProcessor.from_pretrained(model, revision=revision)
    whisper = WhisperForConditionalGeneration.from_pretrained(model, revision=revision, dtype=dtype,
                                                              attn_implementation="sdpa").to(device)
    return processor, whisper


def save_merged(peft_model, processor, out_dir: Path, dtype) -> Path:
    merged = peft_model.merge_and_unload().to(dtype)
    merged.config.use_cache = True
    merged.config.apply_spec_augment = False
    merged.save_pretrained(out_dir, safe_serialization=True)
    processor.save_pretrained(out_dir)
    return out_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/whisper-large-v3-turbo")
    ap.add_argument("--revision")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--exclude", nargs="*", default=["splits/dev_random.txt", "splits/dev_lao.txt"],
                    help="id files whose samples are never trained on (default: both dev sets)")
    ap.add_argument("--val-frac", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--grad-accum", type=int, default=2)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--warmup-steps", type=int, default=50)
    ap.add_argument("--lora-r", type=int, default=32)
    ap.add_argument("--lora-alpha", type=int, default=64)
    ap.add_argument("--lora-dropout", type=float, default=0.05)
    ap.add_argument("--eval-batch-size", type=int, default=16)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--log-every", type=int, default=20)
    ap.add_argument("--max-steps", type=int, help="stop after N optimizer steps (smoke tests)")
    ap.add_argument("--max-minutes", type=float, help="stop training after this long, keeping the best epoch so far")
    ap.add_argument("--limit-samples", type=int, help="first N train samples and N/10 held-out samples (smoke tests)")
    ap.add_argument("--device")
    ap.add_argument("--dtype", choices=["fp16", "fp32"], help="base weights (default fp16 on GPU, fp32 on CPU)")
    ap.add_argument("--no-merge", action="store_true", help="skip writing merged/ (smoke tests)")
    ap.add_argument("--merge-only", action="store_true", help="only rebuild --out/merged from --out/adapter")
    ap.add_argument("--out", required=True)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()

    import torch
    from peft import LoraConfig, PeftModel, get_peft_model, get_peft_model_state_dict, set_peft_model_state_dict

    out = Path(a.out)
    device = torch.device(a.device or ("cuda" if torch.cuda.is_available() else "cpu"))
    dtype = {"fp16": torch.float16, "fp32": torch.float32}[a.dtype or ("fp16" if device.type == "cuda" else "fp32")]

    if a.merge_only:
        processor, whisper = load_base(a.model, a.revision, device, dtype)
        peft_model = PeftModel.from_pretrained(whisper, out / "adapter")
        runinfo.refuse_existing(out / "merged", overwrite=a.overwrite)
        print(json.dumps({"merged": str(save_merged(peft_model, processor, out / "merged", dtype))}))
        return

    runinfo.refuse_existing(out / "adapter", out / "asr_train.meta.json", overwrite=a.overwrite)
    out.mkdir(parents=True, exist_ok=True)
    started, t_start = runinfo.now(), time.monotonic()
    random.seed(a.seed)
    np.random.seed(a.seed)
    torch.manual_seed(a.seed)

    root_split = Path(a.root) / "train"
    items = load_split("train", a.root)
    exclude = set().union(*(set(runinfo.read_ids(f)) for f in a.exclude)) if a.exclude else set()
    train_s, val_s = split_samples(items, exclude, a.val_frac, a.seed)
    if a.limit_samples:
        train_s, val_s = train_s[:a.limit_samples], val_s[:max(1, a.limit_samples // 10)]
    train_p, val_p = pairs_of(train_s), pairs_of(val_s)
    held = {p for s in items if s["id"] in exclude for p, _ in utterances(s)}
    assert not held & {p for p, _ in train_p + val_p}, "an excluded (dev) wav would be trained on"
    assert not {p for p, _ in train_p} & {p for p, _ in val_p}, "a wav is in both train and held-out"
    assert all(t.strip() for _, t in train_p + val_p), "empty audio_text"
    runinfo.write_json(out / "split_ids.json", {"train": [s["id"] for s in train_s], "val": [s["id"] for s in val_s],
                                                "excluded_files": a.exclude})

    processor, whisper = load_base(a.model, a.revision, device, dtype)
    processor.tokenizer.set_prefix_tokens(language="vietnamese", task="transcribe", predict_timestamps=False)
    whisper.config.use_cache = False
    whisper.config.apply_spec_augment = True  # time masking (mask_time_prob from the model config), training mode only
    whisper.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    lora = LoraConfig(r=a.lora_r, lora_alpha=a.lora_alpha, lora_dropout=a.lora_dropout,
                      target_modules=TARGET_MODULES, bias="none")
    model = get_peft_model(whisper, lora)  # injects LoRA into `whisper` in place; whisper.generate uses it
    for p in model.parameters():
        if p.requires_grad and p.dtype != torch.float32:
            p.data = p.data.float()  # fp32 adapter weights: the gradient scaler needs them
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())

    start_id = whisper.config.decoder_start_token_id
    loader = torch.utils.data.DataLoader(
        Utterances(root_split, train_p, processor), batch_size=a.batch_size, shuffle=True, drop_last=False,
        num_workers=a.workers, collate_fn=make_collate(start_id), generator=torch.Generator().manual_seed(a.seed),
        persistent_workers=a.workers > 0)
    steps_per_epoch = math.ceil(len(loader) / a.grad_accum)
    total_steps = min(a.max_steps or 10 ** 9, steps_per_epoch * a.epochs)
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=a.lr, weight_decay=0.0)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: min(1.0, (s + 1) / max(1, a.warmup_steps)) * max(0.0, 1 - s / max(1, total_steps)))
    use_amp = device.type == "cuda" and dtype == torch.float16
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    log = (out / "train_log.jsonl").open("w", encoding="utf-8")

    def emit(rec):
        rec = {"t_min": round((time.monotonic() - t_start) / 60, 2), **rec}
        log.write(json.dumps(rec, ensure_ascii=False) + "\n")
        log.flush()
        print(json.dumps(rec, ensure_ascii=False), flush=True)

    val_paths, val_refs = [p for p, _ in val_p], [t for _, t in val_p]

    def evaluate(epoch):
        t0 = time.monotonic()
        hyps = transcribe(whisper, processor, root_split, val_paths, a.eval_batch_size, device, dtype)
        model.train()
        rec = {"epoch": epoch, "val_wer": wer(val_refs, hyps), "val_wer_raw": wer(val_refs, hyps, raw=True),
               "val_wavs": len(hyps), "val_empty": sum(not h for h in hyps), "eval_s": round(time.monotonic() - t0, 1),
               "examples": [{"ref": r, "hyp": h} for r, h in list(zip(val_refs, hyps))[:3]]}
        emit(rec)
        return rec

    emit({"start": True, "model": a.model, "revision": a.revision, "device": str(device), "dtype": str(dtype),
          "train_samples": len(train_s), "train_wavs": len(train_p), "val_samples": len(val_s), "val_wavs": len(val_p),
          "excluded_samples": len(exclude), "trainable_params": trainable, "total_params": total,
          "steps_per_epoch": steps_per_epoch, "total_steps": total_steps})
    epochs_log = [evaluate(0)]  # the base model on the held-out wavs: same machine, same decoding
    best = {"epoch": 0, "val_wer": epochs_log[0]["val_wer"], "state": None}
    step, stop, seen, t_log, loss_sum, loss_n = 0, None, 0, time.monotonic(), 0.0, 0
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats()
    model.train()
    for epoch in range(1, a.epochs + 1):
        opt.zero_grad(set_to_none=True)
        for i, (feats, labels) in enumerate(loader):
            feats, labels = feats.to(device, dtype), labels.to(device)
            with torch.autocast("cuda", dtype=torch.float16, enabled=use_amp):
                loss = model(input_features=feats, labels=labels).loss
            scaler.scale(loss / a.grad_accum).backward()
            loss_sum, loss_n, seen = loss_sum + loss.item(), loss_n + 1, seen + feats.shape[0]
            if (i + 1) % a.grad_accum and i + 1 != len(loader):
                continue
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
            scaler.step(opt)
            scaler.update()
            opt.zero_grad(set_to_none=True)
            sched.step()
            step += 1
            if step % a.log_every == 0 or step == 1:
                dt = time.monotonic() - t_log
                emit({"step": step, "epoch": epoch, "loss": round(loss_sum / max(1, loss_n), 4),
                      "lr": float(f"{sched.get_last_lr()[0]:.3g}"), "wavs_per_s": round(seen / max(dt, 1e-9), 2),
                      "peak_gb": round(torch.cuda.max_memory_allocated() / 2 ** 30, 2) if device.type == "cuda" else None})
                t_log, loss_sum, loss_n, seen = time.monotonic(), 0.0, 0, 0
            if a.max_steps and step >= a.max_steps:
                stop = "max_steps"
            elif a.max_minutes and (time.monotonic() - t_start) / 60 >= a.max_minutes:
                stop = "max_minutes"
            if stop:
                break
        rec = evaluate(epoch)
        epochs_log.append(rec)
        if best["state"] is None or rec["val_wer"] < best["val_wer"]:
            best = {"epoch": epoch, "val_wer": rec["val_wer"],
                    "state": {k: v.detach().cpu().clone() for k, v in get_peft_model_state_dict(model).items()}}
            model.save_pretrained(out / "adapter")
        if stop:
            break

    # best trained epoch (also when the base model scored better: the comparison is in the log and the meta)
    set_peft_model_state_dict(model, best["state"])
    merged = None if a.no_merge else str(save_merged(model, processor, out / "merged", dtype))
    summary = {"best_epoch": best["epoch"], "best_val_wer": best["val_wer"], "base_val_wer": epochs_log[0]["val_wer"],
               "base_val_wer_raw": epochs_log[0]["val_wer_raw"],
               "best_val_wer_raw": next(r["val_wer_raw"] for r in epochs_log if r["epoch"] == best["epoch"]),
               "stopped": stop or "epochs", "steps": step, "minutes": round((time.monotonic() - t_start) / 60, 1),
               "peak_gb": round(torch.cuda.max_memory_allocated() / 2 ** 30, 2) if device.type == "cuda" else None}
    emit({"done": True, **summary, "merged": merged})
    log.close()
    runinfo.write_json(out / "asr_train.meta.json", {
        "kind": "asr_train", "started": started, "finished": runinfo.now(), "args": vars(a),
        "model": a.model, "revision": a.revision, "commit": getattr(whisper.config, "_commit_hash", None),
        "lora": {"r": a.lora_r, "alpha": a.lora_alpha, "dropout": a.lora_dropout, "targets": TARGET_MODULES},
        "train": runinfo.ids_digest(s["id"] for s in train_s), "val": runinfo.ids_digest(s["id"] for s in val_s),
        "train_wavs": len(train_p), "val_wavs": len(val_p),
        "exclude_files": {f: runinfo.sha256_file(f) for f in a.exclude or []},
        "epochs": [{k: v for k, v in r.items() if k != "examples"} for r in epochs_log], **summary,
        "git": runinfo.git_state(), "env": runinfo.env_info()})


if __name__ == "__main__":
    main()
