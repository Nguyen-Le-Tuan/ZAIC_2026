"""Teacher-forced loss of a checkpoint on EVERY row of an SFT file (same shifted CE and mask as lifemate.train).

Loss is a diagnostic only: checkpoints are chosen by rollout score (lifemate.infer + lifemate.scorer).

Example:
  python -m lifemate.eval_loss --adapter ckpt/q17b_fit_random/step_100 --data sft/dev_random.jsonl \
      --out runs/loss_q17b_fit_random_s100.json
"""
from __future__ import annotations

import argparse
import json
import time

import torch
import torch.nn.functional as F

from . import runinfo
from .train import load_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-1.7B")
    ap.add_argument("--adapter", help="LoRA adapter dir (omit for the base model)")
    ap.add_argument("--data", required=True)
    ap.add_argument("--max-len", type=int, default=8192)
    ap.add_argument("--out", required=True)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    runinfo.refuse_existing(a.out, overwrite=a.overwrite)

    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.manual_seed(0)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, attn_implementation="sdpa", device_map={"": 0})
    if a.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, a.adapter)  # not merged: same numerics as the in-training dev loss
    model.eval()
    base = model.get_base_model() if a.adapter else model
    rows, skipped = load_rows(a.data, tok, a.max_len)

    per, t0 = [], time.time()
    with torch.no_grad():
        for rid, ids, labels in rows:
            x = torch.tensor([ids], device="cuda")
            y = torch.tensor([labels[1:]], device="cuda")
            mask = y != -100
            with torch.autocast("cuda", dtype=torch.bfloat16):
                h = base.model(input_ids=x, use_cache=False).last_hidden_state[:, :-1]
                logits = base.lm_head(h[mask]).float()
            target = y[mask]
            ce = F.cross_entropy(logits, target, reduction="sum").item()
            per.append({"id": rid, "tokens": int(target.numel()), "loss_sum": ce,
                        "argmax_errors": int((logits.argmax(-1) != target).sum())})

    n_tok = sum(r["tokens"] for r in per)
    summary = {"rows": len(per), "skipped_too_long": skipped, "tokens": n_tok,
               "loss": sum(r["loss_sum"] for r in per) / max(n_tok, 1),
               "token_acc": 1 - sum(r["argmax_errors"] for r in per) / max(n_tok, 1),
               "rows_without_argmax_error": sum(r["argmax_errors"] == 0 for r in per), "seconds": round(time.time() - t0, 1)}
    runinfo.write_json(a.out, {
        "kind": "eval_loss", "created": runinfo.now(), "args": vars(a), "summary": summary,
        "data_sha256": runinfo.sha256_file(a.data), "ids": runinfo.ids_digest(r["id"] for r in per),
        "adapter_sha256": runinfo.sha256_dir(a.adapter) if a.adapter else None,
        "git": runinfo.git_state(), "env": runinfo.env_info(), "per_row": per})
    print(json.dumps({"out": a.out, **summary}))


if __name__ == "__main__":
    main()
