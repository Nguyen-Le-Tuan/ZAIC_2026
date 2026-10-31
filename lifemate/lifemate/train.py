"""LoRA SFT on the segments jsonl written by lifemate.sft. Plain PyTorch loop, sized for small GPUs.

Memory savers (8GB laptop GPU):
  * logits only at loss positions: the full [seq x 152k vocab] logits of a ~3K-token prompt would take
    2-4GB, while only ~76 tokens per example are trained on
  * gradient checkpointing, batch size 1 + gradient accumulation, bf16 weights, fp32 LoRA params
  * --load-4bit: QLoRA (NF4) for bigger models, e.g. Qwen3-4B on 8GB

Examples:
  python -m lifemate.train --data sft/fit_random.jsonl --eval-data sft/dev_random.jsonl --out ckpt/q17b_fit_random
  python -m lifemate.train --model Qwen/Qwen3-4B-Instruct-2507 --load-4bit --data sft/all.jsonl --out ckpt/q4b_all
  python -m lifemate.train ... --max-steps 5        # smoke test: memory and speed
"""
from __future__ import annotations

import os

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402

from . import runinfo  # noqa: E402

LORA_TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def load_rows(path, tok, max_len: int, limit: int | None = None):
    """[(row id, input_ids, labels)], labels = -100 outside loss segments. Too-long rows are skipped, not truncated."""
    out, skipped = [], 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if limit and len(out) >= limit:
                break
            row = json.loads(line)
            segs = row["segments"]
            enc = tok([t for t, _ in segs], add_special_tokens=False)["input_ids"]
            ids, labels = [], []
            for (_, loss), t in zip(segs, enc):
                ids += t
                labels += t if loss else [-100] * len(t)
            if len(ids) > max_len:
                skipped += 1
                continue
            out.append((row["id"], ids, labels))
    return out, skipped


def load_examples(path, tok, max_len: int, limit: int | None = None):
    """[(input_ids, labels)] (see load_rows)."""
    rows, skipped = load_rows(path, tok, max_len, limit)
    return [(ids, labels) for _, ids, labels in rows], skipped


def build_model(a):
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig

    kw = {"dtype": torch.bfloat16, "attn_implementation": "sdpa", "device_map": {"": 0}}
    if a.load_4bit:
        kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                       bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(a.model, **kw)
    model.config.use_cache = False
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    cfg = LoraConfig(r=a.lora_r, lora_alpha=a.lora_alpha, lora_dropout=a.lora_dropout,
                     target_modules=LORA_TARGETS, task_type="CAUSAL_LM")
    model = get_peft_model(model, cfg)
    for p in model.parameters():
        if p.requires_grad:
            p.data = p.data.float()
    return model


def example_loss(base, ids, labels, device):
    """(sum of token CE over loss positions, number of loss tokens). Logits only where labels != -100."""
    x = torch.tensor([ids], device=device)
    y = torch.tensor([labels[1:]], device=device)
    with torch.autocast("cuda", dtype=torch.bfloat16):
        h = base.model(input_ids=x, use_cache=False).last_hidden_state[:, :-1]
        mask = y != -100
        logits = base.lm_head(h[mask]).float()
    return F.cross_entropy(logits, y[mask], reduction="sum"), int(mask.sum())


@torch.no_grad()
def evaluate_loss(model, base, data, device) -> float:
    model.eval()
    tot, n = 0.0, 0
    for ids, labels in data:
        loss, k = example_loss(base, ids, labels, device)
        tot, n = tot + loss.item(), n + k
    model.train()
    return tot / max(n, 1)


def main():
    ap = argparse.ArgumentParser(description="LoRA SFT for the LifeMate agent")
    ap.add_argument("--model", default="Qwen/Qwen3-1.7B")
    ap.add_argument("--data", required=True)
    ap.add_argument("--eval-data", help="segments jsonl (e.g. sft/dev_random.jsonl) for a periodic loss check")
    ap.add_argument("--eval-n", type=int, default=0,
                    help="0 = every dev example (default). >0 takes a seeded random subset, never the head of the "
                         "file: dev files are sorted by id and later ids are harder")
    ap.add_argument("--eval-every", type=int, default=50, help="optimizer steps")
    ap.add_argument("--out", required=True)
    ap.add_argument("--load-4bit", action="store_true")
    ap.add_argument("--lora-r", type=int, default=32)
    ap.add_argument("--lora-alpha", type=int, default=64)
    ap.add_argument("--lora-dropout", type=float, default=0.05)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--warmup", type=float, default=0.03)
    ap.add_argument("--epochs", type=float, default=1.0)
    ap.add_argument("--grad-accum", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=8192)
    ap.add_argument("--max-steps", type=int, help="stop after this many optimizer steps (smoke tests)")
    ap.add_argument("--save-every", type=int, default=100, help="optimizer steps")
    ap.add_argument("--log-every", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--overwrite", action="store_true", help="allow writing into an --out that already has a checkpoint")
    a = ap.parse_args()

    from transformers import AutoTokenizer, get_cosine_schedule_with_warmup

    random.seed(a.seed)
    torch.manual_seed(a.seed)
    device = torch.device("cuda")
    out = Path(a.out)
    runinfo.refuse_existing(out / "final", out / "log.jsonl", overwrite=a.overwrite)
    out.mkdir(parents=True, exist_ok=True)
    (out / "train_args.json").write_text(json.dumps(vars(a), indent=1))

    tok = AutoTokenizer.from_pretrained(a.model)
    t0 = time.time()
    data, skipped = load_examples(a.data, tok, a.max_len)
    dev, dev_ids, dev_skipped = [], [], 0
    if a.eval_data:
        rows, dev_skipped = load_rows(a.eval_data, tok, a.max_len)
        if dev_skipped:
            print(f"warning: {dev_skipped} dev rows longer than --max-len are not in the dev loss", flush=True)
        pick = sorted(random.Random(a.seed).sample(range(len(rows)), a.eval_n)) if 0 < a.eval_n < len(rows) else range(len(rows))
        dev, dev_ids = [rows[k][1:] for k in pick], [rows[k][0] for k in pick]
    n_tok = sum(len(i) for i, _ in data)
    print(f"data: {len(data)} examples ({skipped} too long), {n_tok / 1e6:.1f}M tokens, "
          f"{sum(sum(x != -100 for x in lab) for _, lab in data) / 1e6:.2f}M loss tokens; dev {len(dev)}; tokenized in {time.time() - t0:.0f}s", flush=True)

    model = build_model(a)
    base = model.get_base_model()
    model.print_trainable_parameters()
    runinfo.write_json(out / "run_info.json", {
        "kind": "train", "created": runinfo.now(), "args": vars(a), "git": runinfo.git_state(), "env": runinfo.env_info(),
        "data": {"path": a.data, "sha256": runinfo.sha256_file(a.data), "examples": len(data), "skipped_too_long": skipped},
        "eval": {"path": a.eval_data, "sha256": runinfo.sha256_file(a.eval_data) if a.eval_data else None,
                 "examples": len(dev), "skipped_too_long": dev_skipped, "ids": runinfo.ids_digest(dev_ids)}})
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=a.lr, weight_decay=0.0, betas=(0.9, 0.999))
    total_steps = math.ceil(len(data) * a.epochs / a.grad_accum)
    if a.max_steps:
        total_steps = min(total_steps, a.max_steps)
    sched = get_cosine_schedule_with_warmup(opt, max(1, int(a.warmup * total_steps)), total_steps)

    # example order: reshuffled every epoch
    order = []
    rng = random.Random(a.seed)
    while len(order) < total_steps * a.grad_accum:
        perm = list(range(len(data)))
        rng.shuffle(perm)
        order += perm
    order = order[: total_steps * a.grad_accum]

    model.train()
    torch.cuda.reset_peak_memory_stats()
    t_start, seen_tok, log_loss, log_n = time.time(), 0, 0.0, 0
    log_file = open(out / "log.jsonl", "a", encoding="utf-8")
    for step in range(1, total_steps + 1):
        window = [data[i] for i in order[(step - 1) * a.grad_accum: step * a.grad_accum]]
        n_loss = sum(sum(x != -100 for x in lab[1:]) for _, lab in window)
        for ids, labels in window:
            loss, k = example_loss(base, ids, labels, device)
            (loss / max(n_loss, 1)).backward()
            log_loss, log_n, seen_tok = log_loss + loss.item(), log_n + k, seen_tok + len(ids)
        gnorm = torch.nn.utils.clip_grad_norm_(params, 1.0).item()
        opt.step()
        sched.step()
        opt.zero_grad(set_to_none=True)

        if step % a.log_every == 0 or step == total_steps:
            el = time.time() - t_start
            rec = {"step": step, "of": total_steps, "loss": round(log_loss / max(log_n, 1), 4), "gnorm": round(gnorm, 3),
                   "lr": sched.get_last_lr()[0], "tok_s": round(seen_tok / el), "elapsed_min": round(el / 60, 1),
                   "eta_min": round(el / step * (total_steps - step) / 60, 1),
                   "peak_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)}
            print(json.dumps(rec), flush=True)
            log_file.write(json.dumps(rec) + "\n")
            log_file.flush()
            log_loss, log_n = 0.0, 0
        if dev and (step % a.eval_every == 0 or step == total_steps):
            rec = {"step": step, "dev_loss": round(evaluate_loss(model, base, dev, device), 4), "dev_n": len(dev)}
            print(json.dumps(rec), flush=True)
            log_file.write(json.dumps(rec) + "\n")
            log_file.flush()
        if step % a.save_every == 0 and step != total_steps:
            model.save_pretrained(out / f"step_{step}")
    model.save_pretrained(out / "final")
    tok.save_pretrained(out / "final")
    print(f"saved {out / 'final'}", flush=True)


if __name__ == "__main__":
    main()
