#!/usr/bin/env bash
# One offline command from the data folder to a checked submission.jsonl: ASR on every wav of the split -> agent loop
# (one ToolEnv per sample) -> format and schema checks. This is the core a Docker image will wrap.
# Current system (JOURNAL entries 52, 58, 62): fine-tuned Whisper-turbo (merged) + Qwen3-4B-Instruct-2507 in 4-bit
# with a LoRA adapter trained on that 4-bit base:
#   SPLIT=public_test ASR_MODEL=ckpt/asr_turboft/merged ADAPTER=ckpt/q4b4_fit_random/final \
#     OUT=runs/e2e_public_q4b.jsonl bash scripts/predict.sh
# Older 1.7B system: LLM=Qwen/Qwen3-1.7B LOAD_4BIT=0 ADAPTER=ckpt/q17b_fit_random/final ...
# Env: SPLIT, ASR_MODEL, ADAPTER, OUT (required);
#      LLM (default Qwen/Qwen3-4B-Instruct-2507);
#      LOAD_4BIT (default 1: base in NF4, adapter not merged, as in every 4B dev run; 0 = bf16 + merged adapter, whose
#        score has not been checked yet, HUMAN_TODO B16);
#      TIME_BUDGET (default 25: seconds per sample, the sample's ASR seconds included; the competition limit is 30 on
#        an A30; the laptop dev runs used 60 because the laptop is slower);
#      WARMUP (default 1: one untimed generation after loading, so the first sample does not pay the first-call
#        cost; 0 skips it);
#      ASR_REV, DATA (default the repo's data folder), IDS (subset), ASR_BATCH (default 1 = per-file latency),
#      ASR_OUT (default ${OUT%.jsonl}_asr.jsonl), SEED (default 0, the training seed),
#      PY (default .venv/bin/python, else python3);
#      SEARCH_GUARD (default 0 = the 05/11 system; 1 = retry empty filtered reads once with looser arguments and stop
#        repeated-read loops, `lifemate.infer --search-guard`).
# Rows carry the organisers' "time" (integer ms: the sample's ASR seconds + its agent seconds). The final Docker entry
# point docker/predict.sh (copied to /code/predict.sh) calls this script with the submitted settings.
# Models must already be in the Hugging Face cache or on disk: nothing is downloaded (HF_HUB_OFFLINE=1). Re-running
# skips the ASR step when its file exists; the agent step refuses to overwrite OUT.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${SPLIT:?set SPLIT}" "${ASR_MODEL:?set ASR_MODEL}" "${ADAPTER:?set ADAPTER}" "${OUT:?set OUT}"
DATA=${DATA:-../data/train+public_test}
LLM=${LLM:-Qwen/Qwen3-4B-Instruct-2507}
LOAD_4BIT=${LOAD_4BIT:-1}
TIME_BUDGET=${TIME_BUDGET:-25}
WARMUP=${WARMUP:-1}
SEED=${SEED:-0}
SEARCH_GUARD=${SEARCH_GUARD:-0}
ARG_RULES=${ARG_RULES:-0}   # 1 = lifemate.infer --arg-rules (safe argument rules R0-R3, JOURNAL entry 146)
ASR_REV=${ASR_REV:-}
ASR_BATCH=${ASR_BATCH:-1}
IDS=${IDS:-}
ASR_OUT=${ASR_OUT:-${OUT%.jsonl}_asr.jsonl}
TRACE=${OUT%.jsonl}_trace.jsonl
if [ -z "${PY:-}" ]; then PY=.venv/bin/python; [ -x "$PY" ] || PY=python3; fi
# PYTHONHASHSEED must be set before Python starts; no bytecode is written next to the split's zaic_tools (read-only)
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  PYTHONHASHSEED=$SEED PYTHONDONTWRITEBYTECODE=1
stamp() { echo "[$(date '+%F %T')] $*"; }
case $LOAD_4BIT in 1) Q=(--load-4bit) ;; 0) Q=() ;; *) echo "LOAD_4BIT must be 0 or 1" >&2; exit 1 ;; esac
case $WARMUP in 1) W=() ;; 0) W=(--no-warmup) ;; *) echo "WARMUP must be 0 or 1" >&2; exit 1 ;; esac
case $SEARCH_GUARD in 1) G=(--search-guard) ;; 0) G=() ;; *) echo "SEARCH_GUARD must be 0 or 1" >&2; exit 1 ;; esac
case $ARG_RULES in 1) G+=(--arg-rules) ;; 0) ;; *) echo "ARG_RULES must be 0 or 1" >&2; exit 1 ;; esac
awk -v t="$TIME_BUDGET" 'BEGIN { exit !(t > 0 && t < 30) }' || { echo "TIME_BUDGET must be above 0 and below 30" >&2; exit 1; }

if [ -e "$ASR_OUT" ]; then
  stamp "reuse $ASR_OUT"
else
  stamp "asr $SPLIT with $ASR_MODEL -> $ASR_OUT"
  "$PY" -m lifemate.asr --split "$SPLIT" --root "$DATA" ${IDS:+--ids "$IDS"} --model "$ASR_MODEL" \
      ${ASR_REV:+--revision "$ASR_REV"} --batch-size "$ASR_BATCH" "${W[@]}" --seed "$SEED" --out "$ASR_OUT"
fi
stamp "agent $LLM + $ADAPTER (4-bit=$LOAD_4BIT, budget ${TIME_BUDGET}s, warm-up=$WARMUP, seed $SEED, search guard=$SEARCH_GUARD, arg rules=$ARG_RULES) -> $OUT"
"$PY" -m lifemate.infer --split "$SPLIT" --root "$DATA" ${IDS:+--ids "$IDS"} --text asr --asr-file "$ASR_OUT" \
    --backend hf --model "$LLM" "${Q[@]}" --adapter "$ADAPTER" --time-budget "$TIME_BUDGET" "${W[@]}" "${G[@]}" \
    --seed "$SEED" --out "$OUT" --trace "$TRACE"
stamp "check $OUT"
"$PY" scripts/check_submission.py "$OUT" --split "$SPLIT" --root "$DATA" ${IDS:+--ids "$IDS"} --require-time \
    --asr-file "$ASR_OUT" --trace "$TRACE" --json "${OUT%.jsonl}_check.json"
stamp "predict done"
