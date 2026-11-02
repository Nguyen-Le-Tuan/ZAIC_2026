#!/usr/bin/env bash
# Evaluate one checkpoint (or the base model) on a dev split with the oracle-text protocol; never overwrites a run.
#   TAG=q17b_fit_random_s100 ADAPTER=ckpt/q17b_fit_random/step_100 bash scripts/eval_ckpt.sh
#   TAG=q17b_base bash scripts/eval_ckpt.sh                      # no ADAPTER = zero-shot (forces an empty <think>)
# Env: TAG (required), ADAPTER, MODEL, DEV (split name, default dev_random), LOSS=1 (also teacher-forced loss on
#      every dev row; needs sft/$DEV.jsonl), ASR_FILE=asr/x.jsonl (user turns from that ASR file instead of
#      audio_text; the loss stays on sft/$DEV.jsonl).
# Writes runs/{sft|zs}_$TAG{.jsonl,.meta.json,_trace.jsonl,_rows.jsonl,_score.json} (+ runs/loss_$TAG.json).
set -euo pipefail
cd "$(dirname "$0")/.."
: "${TAG:?set TAG}"
MODEL=${MODEL:-Qwen/Qwen3-1.7B}
DEV=${DEV:-dev_random}
ADAPTER=${ADAPTER:-}
TEXT=(--text oracle)
if [ -n "${ASR_FILE:-}" ]; then
  [ -f "$ASR_FILE" ] || { echo "no $ASR_FILE" >&2; exit 1; }
  TEXT=(--text asr --asr-file "$ASR_FILE")
fi
PY=.venv/bin/python
[ -f "splits/$DEV.txt" ] || { echo "no splits/$DEV.txt" >&2; exit 1; }

if [ -n "$ADAPTER" ]; then
  KIND=sft; EXTRA=(--adapter "$ADAPTER")
else
  KIND=zs; EXTRA=(--assistant-prefix '<think>\n\n</think>\n\n')   # hybrid Qwen3 answers without thinking
fi
P=runs/${KIND}_$TAG
for f in "$P.jsonl" "${P}_rows.jsonl" "${P}_score.json"; do
  [ ! -e "$f" ] || { echo "refusing to overwrite $f (pick a new TAG)" >&2; exit 1; }
done

if [ "${LOSS:-0}" = 1 ] && [ -n "$ADAPTER" ]; then
  $PY -m lifemate.eval_loss --model "$MODEL" --adapter "$ADAPTER" --data "sft/$DEV.jsonl" --out "runs/loss_$TAG.json"
fi
$PY -m lifemate.infer --split train --ids "splits/$DEV.txt" "${TEXT[@]}" --backend hf --model "$MODEL" "${EXTRA[@]}" \
    --out "$P.jsonl" --trace "${P}_trace.jsonl"
# --ids: a sample missing from the predictions counts as 0 instead of silently shrinking the denominator
$PY -m lifemate.scorer "$P.jsonl" --split train --ids "splits/$DEV.txt" --rows "${P}_rows.jsonl" > "${P}_score.json"
cat "${P}_score.json"
