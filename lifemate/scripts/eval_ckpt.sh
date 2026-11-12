#!/usr/bin/env bash
# Evaluate one checkpoint (or the base model) on a dev split with the oracle-text protocol; never overwrites a run.
#   TAG=q17b_fit_random_s100 ADAPTER=ckpt/q17b_fit_random/step_100 bash scripts/eval_ckpt.sh
#   TAG=q17b_base bash scripts/eval_ckpt.sh                      # no ADAPTER = zero-shot (forces an empty <think>)
# Env: TAG (required), ADAPTER, MODEL, DEV (split name, default dev_random), LOSS=1 (also teacher-forced loss on
#      every dev row; needs sft/$DEV.jsonl), ASR_FILE=asr/x.jsonl (user turns from that ASR file instead of
#      audio_text; the loss stays on sft/$DEV.jsonl), LOAD_4BIT=1 (base model in NF4 and adapter not merged, as the
#      4B adapters were trained; LOSS=1 is then refused because eval_loss loads bf16, and train.py already logs the
#      dev loss), TIME_BUDGET (seconds per sample, default 25; the 4B laptop dev runs used 60).
#   4B on the laptop: TAG=q4b4_x ADAPTER=ckpt/q4b4_x/final MODEL=Qwen/Qwen3-4B-Instruct-2507 LOAD_4BIT=1 TIME_BUDGET=60 \
#     bash scripts/eval_ckpt.sh
# Writes runs/{sft|zs}_$TAG{.jsonl,.meta.json,_trace.jsonl,_rows.jsonl,_score.json} (+ runs/loss_$TAG.json).
set -euo pipefail
cd "$(dirname "$0")/.."
: "${TAG:?set TAG}"
MODEL=${MODEL:-Qwen/Qwen3-1.7B}
DEV=${DEV:-dev_random}
ADAPTER=${ADAPTER:-}
LOAD_4BIT=${LOAD_4BIT:-0}
TIME_BUDGET=${TIME_BUDGET:-25}
case $LOAD_4BIT in 1) Q=(--load-4bit) ;; 0) Q=() ;; *) echo "LOAD_4BIT must be 0 or 1" >&2; exit 1 ;; esac
# inference switches of the submission (default off = the rollouts of every earlier dev measurement)
case ${SEARCH_GUARD:-0} in 1) Q+=(--search-guard) ;; 0) ;; *) echo "SEARCH_GUARD must be 0 or 1" >&2; exit 1 ;; esac
case ${ARG_RULES:-0} in 1) Q+=(--arg-rules) ;; 0) ;; *) echo "ARG_RULES must be 0 or 1" >&2; exit 1 ;; esac
if [ "${LOSS:-0}" = 1 ] && [ "$LOAD_4BIT" = 1 ]; then
  echo "LOSS=1 needs a bf16 load (lifemate.eval_loss has no 4-bit option); train.py already logs the dev loss" >&2; exit 1
fi
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
$PY -m lifemate.infer --split train --ids "splits/$DEV.txt" "${TEXT[@]}" --backend hf --model "$MODEL" "${Q[@]}" \
    "${EXTRA[@]}" --time-budget "$TIME_BUDGET" --out "$P.jsonl" --trace "${P}_trace.jsonl"
# --ids: a sample missing from the predictions counts as 0 instead of silently shrinking the denominator
$PY -m lifemate.scorer "$P.jsonl" --split train --ids "splits/$DEV.txt" --rows "${P}_rows.jsonl" > "${P}_score.json"
cat "${P}_score.json"
