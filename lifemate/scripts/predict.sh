#!/usr/bin/env bash
# One offline command from the data folder to a checked submission.jsonl: ASR on every wav of the split -> agent loop
# (one ToolEnv per sample) -> format and schema checks. This is the core a Docker image will wrap.
#   SPLIT=public_test ASR_MODEL=openai/whisper-large-v3-turbo ASR_REV=41f01f3fe87f28c78e2fbf8b568835947dd65ed9 \
#     ADAPTER=ckpt/q17b_fit_random/final OUT=runs/e2e_public_turbo.jsonl bash scripts/predict.sh
# Env: SPLIT, ASR_MODEL, ADAPTER, OUT (required); ASR_REV, LLM (default Qwen/Qwen3-1.7B), DATA (default the repo's data
#      folder), IDS (subset), ASR_BATCH (default 1 = per-file latency), ASR_OUT (default ${OUT%.jsonl}_asr.jsonl).
# Models must already be in the Hugging Face cache: nothing is downloaded (HF_HUB_OFFLINE=1). Re-running skips the ASR
# step when its file exists; the agent step refuses to overwrite OUT.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${SPLIT:?set SPLIT}" "${ASR_MODEL:?set ASR_MODEL}" "${ADAPTER:?set ADAPTER}" "${OUT:?set OUT}"
DATA=${DATA:-../data/train+public_test}
LLM=${LLM:-Qwen/Qwen3-1.7B}
ASR_REV=${ASR_REV:-}
ASR_BATCH=${ASR_BATCH:-1}
IDS=${IDS:-}
ASR_OUT=${ASR_OUT:-${OUT%.jsonl}_asr.jsonl}
TRACE=${OUT%.jsonl}_trace.jsonl
PY=.venv/bin/python
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
stamp() { echo "[$(date '+%F %T')] $*"; }

if [ -e "$ASR_OUT" ]; then
  stamp "reuse $ASR_OUT"
else
  stamp "asr $SPLIT with $ASR_MODEL -> $ASR_OUT"
  $PY -m lifemate.asr --split "$SPLIT" --root "$DATA" ${IDS:+--ids "$IDS"} --model "$ASR_MODEL" \
      ${ASR_REV:+--revision "$ASR_REV"} --batch-size "$ASR_BATCH" --out "$ASR_OUT"
fi
stamp "agent $LLM + $ADAPTER -> $OUT"
$PY -m lifemate.infer --split "$SPLIT" --root "$DATA" ${IDS:+--ids "$IDS"} --text asr --asr-file "$ASR_OUT" \
    --backend hf --model "$LLM" --adapter "$ADAPTER" --out "$OUT" --trace "$TRACE"
stamp "check $OUT"
$PY scripts/check_submission.py "$OUT" --split "$SPLIT" --root "$DATA" ${IDS:+--ids "$IDS"} \
    --asr-file "$ASR_OUT" --trace "$TRACE" --json "${OUT%.jsonl}_check.json"
stamp "predict done"
