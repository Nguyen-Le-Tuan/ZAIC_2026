#!/usr/bin/env bash
# Zero-shot baseline of the agent alone (oracle transcripts) on a cloud GPU with >= 24GB.
# Copy the whole "Zalo AI Challenge" folder (lifemate/ + data/train+public_test/, without the zip and .venv), then:
#   cd lifemate && bash scripts/cloud_baseline.sh
set -euo pipefail
MODEL=${MODEL:-Qwen/Qwen3-4B-Instruct-2507}
WORKERS=${WORKERS:-32}

command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
[ -d .venv-gpu ] || uv venv --python 3.12 .venv-gpu
uv pip install --python .venv-gpu/bin/python vllm
PY=.venv-gpu/bin/python

.venv-gpu/bin/vllm serve "$MODEL" --max-model-len 16384 --enable-prefix-caching --seed 0 --port 8000 > runs/vllm.log 2>&1 &
SERVER=$!
trap 'kill $SERVER' EXIT
until curl -sf localhost:8000/v1/models >/dev/null; do sleep 5; done

TAG=$(basename "$MODEL")
for SPLIT in dev_random dev_lao; do
  $PY -m lifemate.infer --split train --ids splits/$SPLIT.txt --text oracle --backend openai \
      --model "$MODEL" --workers "$WORKERS" --out runs/zs_${TAG}_$SPLIT.jsonl --trace runs/zs_${TAG}_${SPLIT}_trace.jsonl
  $PY -m lifemate.scorer runs/zs_${TAG}_$SPLIT.jsonl --split train --ids splits/$SPLIT.txt --rows runs/zs_${TAG}_${SPLIT}_rows.jsonl
done
