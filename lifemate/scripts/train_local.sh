#!/usr/bin/env bash
# Overnight run on the local RTX 4070 8GB: zero-shot baseline -> LoRA SFT -> eval, all on dev_random.
#   cd lifemate && nohup systemd-inhibit --what=sleep:idle:handle-lid-switch bash scripts/train_local.sh > runs/overnight.log 2>&1 &
# Measured on the 4070 Laptop with Qwen3-1.7B: ~1.4K tok/s training (1 epoch of fit_random ~2.7h), peak 5.4GB VRAM,
# eval ~3s/sample. Keep the laptop plugged in and avoid other GPU-heavy apps (the desktop already uses ~1.7GB).
# Env overrides: MODEL, TAG, EPOCHS, SKIP_ZS=1 (skip the baseline), TRAIN_ARGS (extra args for lifemate.train).
set -euo pipefail
cd "$(dirname "$0")/.."
MODEL=${MODEL:-Qwen/Qwen3-1.7B}
TAG=${TAG:-q17b_fit_random}
EPOCHS=${EPOCHS:-1}
PY=.venv/bin/python
NOTHINK='<think>\n\n</think>\n\n'   # zero-shot only: hybrid Qwen3 answers without thinking
mkdir -p runs ckpt sft
stamp() { echo "[$(date '+%F %T')] $*"; }

[ -f sft/fit_random.jsonl ] || $PY -m lifemate.sft --fit splits/fit_random.txt --out sft/fit_random.jsonl
[ -f sft/dev_random.jsonl ] || $PY -m lifemate.sft --fit splits/dev_random.txt --rename 0 --p-remove 0 --p-distract 0 --p-lower 0 --out sft/dev_random.jsonl

if [ "${SKIP_ZS:-0}" != 1 ]; then
  stamp "zero-shot baseline on dev_random"
  $PY -m lifemate.infer --split train --ids splits/dev_random.txt --text oracle --backend hf --model "$MODEL" \
      --assistant-prefix "$NOTHINK" --out runs/zs_$TAG.jsonl --trace runs/zs_${TAG}_trace.jsonl
  $PY -m lifemate.scorer runs/zs_$TAG.jsonl --split train --rows runs/zs_${TAG}_rows.jsonl | tee runs/zs_${TAG}_score.json
fi

stamp "training $MODEL on sft/fit_random.jsonl ($EPOCHS epoch)"
$PY -m lifemate.train --model "$MODEL" --data sft/fit_random.jsonl --eval-data sft/dev_random.jsonl \
    --epochs "$EPOCHS" --out ckpt/$TAG ${TRAIN_ARGS:-}

stamp "eval of the fine-tuned model on dev_random"
$PY -m lifemate.infer --split train --ids splits/dev_random.txt --text oracle --backend hf --model "$MODEL" \
    --adapter ckpt/$TAG/final --out runs/sft_$TAG.jsonl --trace runs/sft_${TAG}_trace.jsonl
$PY -m lifemate.scorer runs/sft_$TAG.jsonl --split train --rows runs/sft_${TAG}_rows.jsonl | tee runs/sft_${TAG}_score.json
stamp "done: runs/zs_${TAG}_score.json vs runs/sft_${TAG}_score.json"
