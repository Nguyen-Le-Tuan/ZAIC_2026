#!/usr/bin/env bash
# Stage 2 of the 09-10/11 cloud runs: train ONE configuration on ALL train samples with the 4-bit recipe of the
# submitted adapter (QLoRA r32, lr 2e-4, 1 epoch, 8-bit AdamW, max length 6144), then make a public_test submission
# with it from the 05/11 PhoWhisper-ft public transcripts (25 s budget, search guard on) and check its format.
# The public file is for the team to submit; nothing here submits anything.
#   TAG=f_a2_s0 MODEL=Qwen/Qwen3-4B-Thinking-2507 THOUGHTS=gen/rationale_d2all.jsonl SEED=0 bash scripts/final_train.sh
# Env: TAG (required), MODEL (default Qwen/Qwen3-4B-Instruct-2507), SEED (default 0), THOUGHTS (sft --thoughts file,
#      empty = none), LORA_TARGETS (comma list, empty = train.py default), EPOCHS (default 1; the learning rate
#      decays to 0 over all of them), PUBLIC_ASR (default
#      runs/e2e_public_phoft_asr.jsonl), SEARCH_GUARD (default 1), TIME_BUDGET (default 25), DRY_RUN=1 (print only).
# Restartable: a finished adapter ckpt/$TAG/final is reused (training is skipped); a public file that already has its
# check file is kept; a public file without one is moved aside and redone.
# Writes sft/all_$TAG.jsonl, ckpt/$TAG/final, runs/public_$TAG{.jsonl,.meta.json,_trace.jsonl,_check.json}.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${TAG:?set TAG}"
MODEL=${MODEL:-Qwen/Qwen3-4B-Instruct-2507}
SEED=${SEED:-0}
THOUGHTS=${THOUGHTS:-}
LORA_TARGETS=${LORA_TARGETS:-}
EPOCHS=${EPOCHS:-1}
PUBLIC_ASR=${PUBLIC_ASR:-runs/e2e_public_phoft_asr.jsonl}
SEARCH_GUARD=${SEARCH_GUARD:-1}
TIME_BUDGET=${TIME_BUDGET:-25}
PY=.venv/bin/python
stamp() { echo "[$(date '+%F %T')] $*"; }
run() { echo "+ $*"; if [ "${DRY_RUN:-0}" != 1 ]; then "$@"; fi; }
[ -f "$PUBLIC_ASR" ] || { echo "no $PUBLIC_ASR" >&2; exit 1; }
[ -z "$THOUGHTS" ] || [ -f "$THOUGHTS" ] || { echo "no $THOUGHTS" >&2; exit 1; }
case $SEARCH_GUARD in 1) G=(--search-guard) ;; 0) G=() ;; *) echo "SEARCH_GUARD must be 0 or 1" >&2; exit 1 ;; esac
mkdir -p runs ckpt sft
SFT=sft/all_$TAG.jsonl
OUT=runs/public_$TAG

if [ -f "ckpt/$TAG/final/adapter_config.json" ]; then
  stamp "reuse ckpt/$TAG/final (training skipped)"
else
  if [ -e "ckpt/$TAG" ]; then   # an interrupted run (no resumable state): keep it aside, train again from the start
    run mv "ckpt/$TAG" "ckpt/${TAG}.interrupted-$(date +%s)"
  fi
  stamp "SFT rows: all train samples${THOUGHTS:+, thoughts from $THOUGHTS}"
  # shellcheck disable=SC2086
  run $PY -m lifemate.sft --reuse ${THOUGHTS:+--thoughts "$THOUGHTS"} --out "$SFT"
  stamp "train $MODEL on $SFT (4-bit, seed $SEED, $EPOCHS epoch(s)${LORA_TARGETS:+, LoRA on $LORA_TARGETS})"
  run $PY -m lifemate.train --model "$MODEL" --data "$SFT" --out "ckpt/$TAG" --load-4bit --optim adamw8bit \
      --max-len 6144 --seed "$SEED" --epochs "$EPOCHS" ${LORA_TARGETS:+--lora-targets "$LORA_TARGETS"}
fi

if [ -f "${OUT}_check.json" ]; then
  stamp "keep $OUT.jsonl (already checked)"
else
  for f in "$OUT.jsonl" "${OUT}_trace.jsonl" "$OUT.meta.json"; do
    if [ -e "$f" ]; then run mv "$f" "$f.partial-$(date +%s)"; fi
  done
  stamp "public_test with ckpt/$TAG/final (budget ${TIME_BUDGET}s, search guard $SEARCH_GUARD)"
  run $PY -m lifemate.infer --split public_test --text asr --asr-file "$PUBLIC_ASR" --backend hf --model "$MODEL" \
      --load-4bit --adapter "ckpt/$TAG/final" --time-budget "$TIME_BUDGET" "${G[@]}" --seed "$SEED" \
      --out "$OUT.jsonl" --trace "${OUT}_trace.jsonl"
  run $PY scripts/check_submission.py "$OUT.jsonl" --split public_test --require-time --asr-file "$PUBLIC_ASR" \
      --trace "${OUT}_trace.jsonl" --json "${OUT}_check.json"
fi
stamp "done $TAG: ckpt/$TAG/final, $OUT.jsonl"
