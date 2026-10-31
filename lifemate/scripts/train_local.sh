#!/usr/bin/env bash
# Local run on the RTX 4070 8GB: zero-shot baseline -> LoRA SFT -> rollout eval of every saved checkpoint, on a
# chosen fit/dev pair. Defaults reproduce the first overnight run (fit_random -> dev_random).
#   cd lifemate && nohup systemd-inhibit --what=sleep:idle:handle-lid-switch bash scripts/train_local.sh > runs/overnight.log 2>&1 &
#   FIT=fit_lao DEV=dev_lao TAG=q17b_fit_lao SKIP_ZS=1 bash scripts/train_local.sh     # unseen-app measurement
# Measured with Qwen3-1.7B: ~1.5K tok/s (1 epoch of fit_random ~2.5h), peak 5.6GB VRAM, eval ~2.5s/sample.
# Env overrides: MODEL, FIT, DEV, TAG, EPOCHS, SKIP_ZS=1, TRAIN_ARGS (extra args for lifemate.train),
#   FIT_SFT_ARGS (default: --drop-apps splits/heldout_apps.json for fit_lao), EVAL_STEPS=0 (only evaluate final),
#   EXTRA_SAMPLES=gen/x.jsonl (appended with sft --extra-samples; the train file is then sft/${FIT}_$TAG.jsonl).
set -euo pipefail
cd "$(dirname "$0")/.."
MODEL=${MODEL:-Qwen/Qwen3-1.7B}
FIT=${FIT:-fit_random}
DEV=${DEV:-dev_random}
TAG=${TAG:-q17b_$FIT}
EPOCHS=${EPOCHS:-1}
PY=.venv/bin/python
case $FIT in fit_lao) FIT_SFT_ARGS=${FIT_SFT_ARGS:---drop-apps splits/heldout_apps.json} ;; *) FIT_SFT_ARGS=${FIT_SFT_ARGS:-} ;; esac
SFT_FIT=sft/$FIT.jsonl
if [ -n "${EXTRA_SAMPLES:-}" ]; then
  [ -f "$EXTRA_SAMPLES" ] || { echo "no $EXTRA_SAMPLES" >&2; exit 1; }
  FIT_SFT_ARGS="$FIT_SFT_ARGS --extra-samples $EXTRA_SAMPLES"
  SFT_FIT=sft/${FIT}_$TAG.jsonl
fi
mkdir -p runs ckpt sft
stamp() { echo "[$(date '+%F %T')] $*"; }

# fit and dev must not share a sample
overlap=$(comm -12 <(tr -s ' \n' '\n' < "splits/$FIT.txt" | sort -u) <(tr -s ' \n' '\n' < "splits/$DEV.txt" | sort -u) | wc -l)
[ "$overlap" = 0 ] || { echo "splits/$FIT.txt and splits/$DEV.txt share $overlap ids" >&2; exit 1; }
[ ! -e "ckpt/$TAG/final" ] || { echo "ckpt/$TAG/final exists; pick a new TAG" >&2; exit 1; }

# SFT files are reused only when their manifest proves same split, settings, inputs and code (else rebuilt)
# shellcheck disable=SC2086
$PY -m lifemate.sft --reuse --fit "splits/$FIT.txt" $FIT_SFT_ARGS --out "$SFT_FIT"
$PY -m lifemate.sft --reuse --fit "splits/$DEV.txt" --rename 0 --p-remove 0 --p-distract 0 --p-lower 0 --out "sft/$DEV.jsonl"

if [ "${SKIP_ZS:-0}" != 1 ]; then
  stamp "zero-shot baseline on $DEV"
  TAG="$TAG" MODEL="$MODEL" DEV="$DEV" bash scripts/eval_ckpt.sh     # -> runs/zs_$TAG*
fi

stamp "training $MODEL on $SFT_FIT ($EPOCHS epoch), dev loss on every row of sft/$DEV.jsonl"
# shellcheck disable=SC2086
$PY -m lifemate.train --model "$MODEL" --data "$SFT_FIT" --eval-data "sft/$DEV.jsonl" \
    --epochs "$EPOCHS" --out "ckpt/$TAG" ${TRAIN_ARGS:-}

stamp "rollout eval on $DEV (oracle text) of the saved checkpoints"
CKPTS=(final)
if [ "${EVAL_STEPS:-1}" = 1 ]; then
  for d in "ckpt/$TAG"/step_*; do [ -d "$d" ] && CKPTS+=("$(basename "$d")"); done
fi
for c in "${CKPTS[@]}"; do
  suffix=$([ "$c" = final ] && echo "" || echo "_s${c#step_}")
  stamp "eval $c"
  adapter="ckpt/$TAG/$c"
  TAG="$TAG$suffix" ADAPTER="$adapter" MODEL="$MODEL" DEV="$DEV" LOSS=1 bash scripts/eval_ckpt.sh
done
runs_list=("runs/sft_$TAG")
for c in "${CKPTS[@]:1}"; do runs_list+=("runs/sft_${TAG}_s${c#step_}"); done
$PY -m lifemate.compare "${runs_list[@]}" --ids "splits/$DEV.txt" --slices --json "runs/compare_$TAG.json"
stamp "done: runs/compare_$TAG.json"
