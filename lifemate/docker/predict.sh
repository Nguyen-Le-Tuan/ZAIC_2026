#!/usr/bin/env bash
# /code/predict.sh: the organisers' entry point (Docker guide 04/11/2026, p. 4, 6-7, 10-12; summary with page numbers
# in docs/BTC_DOCKER_GUIDE_2026-11-06.md on main). At grading there is no network and no environment variable:
#   docker run --gpus '"device=0"' -v <data>:/data:ro -v <result>:/result <image> /bin/bash /code/predict.sh
# Steps: find the split under /data (the subfolder holding <name>_tools_catalog.json: private_test), run the submitted
# system with scripts/predict.sh (ASR of every wav, then the agent with one ToolEnv per sample, then the format and
# schema checks), write /result/submission.jsonl (rows: id, tool_calls, state_hash, time in ms), print the model load
# and prediction times. Intermediate files (ASR file, trace, metadata) go to a new temp folder, never under /data,
# which is mounted read-only.
#
# Every setting defaults to the submitted value (lifemate/submit.py DEFAULTS; tests/test_submit.py checks they agree).
# The variables exist only to test the same script elsewhere, e.g. on the laptop from the repo's lifemate/ folder:
#   DATA_ROOT=../data/train+public_test SPLIT=public_test RESULT_DIR=runs/code_pub WORK=runs/code_pub/work \
#     bash docker/predict.sh
#   LIFEMATE_DIR  folder holding lifemate/, scripts/, ckpt/ (default: this script's folder, or its parent, if it holds
#                 lifemate/infer.py; else /app/lifemate as in the 05/11 image)
#   PY            Python with torch & co. (default $LIFEMATE_DIR/.venv/bin/python when present, else python3)
#   DATA_ROOT (/data)  RESULT_DIR (/result)  SPLIT (found under DATA_ROOT)  WORK (new folder under $TMPDIR or /tmp)
#   IDS           file of sample ids: run only those (smoke tests)
#   ASR_MODEL ADAPTER LLM LOAD_4BIT TIME_BUDGET WARMUP SEED   the system (do not change for the submission)
#   DRY_RUN=1     print the resolved settings and stop before loading any model
set -euo pipefail
T0=$(date +%s%N)
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if [ -z "${LIFEMATE_DIR:-}" ]; then
  if [ -f "$HERE/lifemate/infer.py" ]; then LIFEMATE_DIR=$HERE
  elif [ -f "$HERE/../lifemate/infer.py" ]; then LIFEMATE_DIR=$HERE/..   # the repo copy, lifemate/docker/predict.sh
  else LIFEMATE_DIR=/app/lifemate; fi
fi
LIFEMATE_DIR=$(realpath -e "$LIFEMATE_DIR")
DATA_ROOT=$(realpath -e "${DATA_ROOT:-/data}")
RESULT_DIR=$(realpath -m "${RESULT_DIR:-/result}")
IDS=${IDS:+$(realpath -e "$IDS")}
ASR_MODEL=${ASR_MODEL:-ckpt/asr_phoft/merged}
ADAPTER=${ADAPTER:-ckpt/q4b4_all/final}
LLM=${LLM:-Qwen/Qwen3-4B-Instruct-2507}
LOAD_4BIT=${LOAD_4BIT:-1}
TIME_BUDGET=${TIME_BUDGET:-25}
WARMUP=${WARMUP:-1}
SEED=${SEED:-0}
if [ -z "${PY:-}" ]; then
  if [ -x "$LIFEMATE_DIR/.venv/bin/python" ]; then PY=$LIFEMATE_DIR/.venv/bin/python; else PY=$(command -v python3); fi
fi
export PYTHONHASHSEED=$SEED PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1

cd "$LIFEMATE_DIR"  # model paths (ckpt/...) are relative to it, as in scripts/predict.sh
SPLIT=$("$PY" -m lifemate.submit split --root "$DATA_ROOT" ${SPLIT:+--split "$SPLIT"})
if [ -n "${WORK:-}" ]; then WORK=$(realpath -m "$WORK")
elif [ "${DRY_RUN:-0}" != 1 ]; then WORK=$(mktemp -d "${TMPDIR:-/tmp}/lifemate_predict.XXXXXX")
fi
for d in ${WORK:+"$WORK"} "$RESULT_DIR"; do
  case "$d/" in "$DATA_ROOT"/*) echo "$d is inside $DATA_ROOT, which is read-only at grading" >&2; exit 1 ;; esac
done

echo "lifemate predict: split $SPLIT from $DATA_ROOT/$SPLIT${IDS:+ (ids in $IDS)}"
echo "system: ASR $ASR_MODEL | LLM $LLM + LoRA $ADAPTER (4-bit=$LOAD_4BIT) | budget ${TIME_BUDGET}s/sample | warm-up=$WARMUP | seed $SEED"
echo "code $LIFEMATE_DIR, python $PY, temp files in ${WORK:-a new folder under ${TMPDIR:-/tmp}}"
echo "output will be saved in $RESULT_DIR/submission.jsonl"
if [ "${DRY_RUN:-0}" = 1 ]; then
  for p in "$ASR_MODEL" "$ADAPTER"; do
    if [ -e "$p" ]; then echo "found $(realpath "$p")"; else echo "NOT FOUND $p (relative to $LIFEMATE_DIR)"; fi
  done
  "$PY" -c 'import sys; from huggingface_hub import snapshot_download as s; print("found", sys.argv[1], "in the offline cache:", s(sys.argv[1], local_files_only=True))' "$LLM" 2>/dev/null \
    || echo "NOT FOUND $LLM in the offline Hugging Face cache (HF_HOME=${HF_HOME:-default})"
  echo "DRY_RUN=1: stop before loading models"
  exit 0
fi

mkdir -p "$WORK" "$RESULT_DIR"
OUT=$WORK/submission.jsonl
rc=0
SPLIT=$SPLIT DATA=$DATA_ROOT IDS=$IDS OUT=$OUT PY=$PY ASR_MODEL=$ASR_MODEL ADAPTER=$ADAPTER LLM=$LLM \
  LOAD_4BIT=$LOAD_4BIT TIME_BUDGET=$TIME_BUDGET WARMUP=$WARMUP SEED=$SEED \
  bash scripts/predict.sh || rc=$?

if [ -s "$OUT" ]; then
  cp "$OUT" "$RESULT_DIR/.submission.jsonl.tmp"
  mv -f "$RESULT_DIR/.submission.jsonl.tmp" "$RESULT_DIR/submission.jsonl"
  "$PY" -m lifemate.submit report --asr-meta "${OUT%.jsonl}_asr.meta.json" --infer-meta "${OUT%.jsonl}.meta.json" \
    --submission "$RESULT_DIR/submission.jsonl" || true
  echo "wrote $RESULT_DIR/submission.jsonl ($(wc -l < "$RESULT_DIR/submission.jsonl") rows)"
else
  echo "FAILED: no submission was produced (exit $rc); $RESULT_DIR/submission.jsonl was not written" >&2
  [ "$rc" = 0 ] && rc=1
fi
[ "$rc" = 0 ] || echo "predict.sh: a step failed (exit $rc); see the messages above" >&2
echo "total wall time: $(( ($(date +%s%N) - T0) / 1000000 )) ms (both model loads included)"
exit "$rc"
