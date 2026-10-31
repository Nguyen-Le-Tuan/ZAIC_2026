#!/usr/bin/env bash
# Run a list of train/eval arms on a multi-GPU cloud machine: one queue per GPU, arms spread round-robin.
# Each arm runs exactly the local pipeline (scripts/train_local.sh or scripts/eval_ckpt.sh, HF backend, greedy),
# so its numbers compare with the local runs; a parity arm checks that on this machine.
#   cd ZAIC_2026 && nohup bash lifemate/scripts/cloud_arms.sh lifemate/cloud/arms_2026-10-31.txt > arms.log 2>&1 &
# Arms file: one arm per line, "<train|eval> KEY=value ...", '#' starts a comment.
#   train TAG=q4b_fit_random MODEL=Qwen/Qwen3-4B-Instruct-2507 FIT=fit_random DEV=dev_random REF=runs/sft_q17b_fit_random
#   eval  TAG=q17b_fit_lao_cloud ADAPTER=ckpt/q17b_fit_lao/final DEV=dev_lao REF=runs/sft_q17b_fit_lao
# KEY=value pairs become the environment of train_local.sh / eval_ckpt.sh (TAG, MODEL, FIT, DEV, EPOCHS, ADAPTER,
# EXTRA_SAMPLES, ASR_FIT, ASR_DEV, ASR_FILE, TRAIN_ARGS=--lr,1e-4 where commas become spaces...).
# REF: paired comparison with that run -> runs/compare_<TAG>_vs_ref.json. REF_ASR: the same for the ASR-text rollout
# of a train arm with ASR_DEV (runs/sft_<TAG>_asr) -> runs/compare_<TAG>_asr_vs_ref.json.
# MIN_GPUS=N: run the arm only when the machine gives the arms at least N GPUs; otherwise it is skipped (and logged)
# before the round-robin placement, so the other arms keep their places.
# Train arms default to SKIP_ZS=1 EVAL_STEPS=0 (only the final checkpoint is rolled out).
# At the end: ../cloud_results_<host>_<time>.tar.gz with runs/ and the new adapters, to bring back.
# Env: GPUS (default: all visible), PACK=0 to skip the tarball, DRY_RUN=1 to print the plan and stop.
set -euo pipefail
cd "$(dirname "$0")/.."
ARMS=${1:?usage: cloud_arms.sh <arms file>}
[ -f "$ARMS" ] || ARMS="../$ARMS"
[ -f "$ARMS" ] || { echo "no arms file $1" >&2; exit 1; }
[ -x .venv/bin/python ] || { echo "run scripts/cloud_setup.sh first" >&2; exit 1; }
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
PY=.venv/bin/python
NGPU=${GPUS:-$(nvidia-smi -L | wc -l)}
STARTED=$(date +%Y%m%d_%H%M)
stamp() { echo "[$(date '+%F %T')] $*"; }

mapfile -t LINES < <(sed -e 's/#.*//' -e 's/[[:space:]]*$//' "$ARMS" | grep -v '^[[:space:]]*$')
[ "${#LINES[@]}" -gt 0 ] || { echo "no arms in $ARMS" >&2; exit 1; }
for l in "${LINES[@]}"; do   # validate everything before starting anything
  read -r kind rest <<< "$l"
  [[ $kind == train || $kind == eval ]] || { echo "bad kind in: $l" >&2; exit 1; }
  for kv in $rest; do [[ $kv =~ ^[A-Z_]+=[^[:space:]]*$ ]] || { echo "bad KEY=value '$kv' in: $l" >&2; exit 1; }; done
  [[ " $rest" == *" TAG="* ]] || { echo "no TAG in: $l" >&2; exit 1; }
done

get() {   # value of KEY in KEY=value args, empty if absent
  local k=$1 kv; shift
  for kv in "$@"; do if [[ $kv == "$k="* ]]; then echo "${kv#*=}"; return 0; fi; done
}

KEPT=()
for l in "${LINES[@]}"; do   # drop arms that need more GPUs than this run has (MIN_GPUS)
  read -r _ rest <<< "$l"; read -ra kv <<< "$rest"
  need=$(get MIN_GPUS "${kv[@]}")
  [[ -z $need || $need =~ ^[0-9]+$ ]] || { echo "bad MIN_GPUS in: $l" >&2; exit 1; }
  if [ -n "$need" ] && [ "$need" -gt "$NGPU" ]; then
    stamp "skip $(get TAG "${kv[@]}"): MIN_GPUS=$need, this run has $NGPU GPU(s)" | tee -a "runs/cloud_arms_$STARTED.log"
  else
    KEPT+=("$l")
  fi
done
[ "${#KEPT[@]}" -gt 0 ] || { echo "every arm needs more than $NGPU GPU(s)" >&2; exit 1; }
LINES=("${KEPT[@]}")

run_arm() {   # gpu, line
  local gpu=$1 kind rest
  read -r kind rest <<< "$2"
  local -a kv
  read -ra kv <<< "$rest"
  local i
  for i in "${!kv[@]}"; do [[ ${kv[$i]} == TRAIN_ARGS=* ]] && kv[$i]=${kv[$i]//,/ } || true; done   # commas -> spaces
  local tag dev ref ref_asr log
  tag=$(get TAG "${kv[@]}"); dev=$(get DEV "${kv[@]}"); ref=$(get REF "${kv[@]}"); ref_asr=$(get REF_ASR "${kv[@]}")
  dev=${dev:-dev_random}
  log=runs/cloud_$tag.log
  stamp "GPU $gpu: start $kind $tag" | tee -a "runs/cloud_arms_$STARTED.log"
  local ok=1
  if [ "${DRY_RUN:-0}" = 1 ]; then
    echo "GPU $gpu: $kind CUDA_VISIBLE_DEVICES=$gpu ${kv[*]} -> runs/sft_$tag (dev $dev, ref ${ref:-none})"
    return 0
  fi
  if [ "$kind" = train ]; then
    env CUDA_VISIBLE_DEVICES="$gpu" SKIP_ZS=1 EVAL_STEPS=0 "${kv[@]}" bash scripts/train_local.sh > "$log" 2>&1 || ok=0
  else
    env CUDA_VISIBLE_DEVICES="$gpu" "${kv[@]}" bash scripts/eval_ckpt.sh > "$log" 2>&1 || ok=0
  fi
  if [ "$ok" = 1 ] && [ -n "$ref" ]; then
    $PY -m lifemate.compare "$ref" "runs/sft_$tag" --ids "splits/$dev.txt" --slices \
        --json "runs/compare_${tag}_vs_ref.json" >> "$log" 2>&1 || ok=0
  fi
  if [ "$ok" = 1 ] && [ -n "$ref_asr" ]; then
    $PY -m lifemate.compare "$ref_asr" "runs/sft_${tag}_asr" --ids "splits/$dev.txt" --slices \
        --json "runs/compare_${tag}_asr_vs_ref.json" >> "$log" 2>&1 || ok=0
  fi
  stamp "GPU $gpu: $([ $ok = 1 ] && echo done || echo FAILED) $kind $tag (log $log)" | tee -a "runs/cloud_arms_$STARTED.log"
}

stamp "${#LINES[@]} arms on $NGPU GPU(s) from $ARMS" | tee -a "runs/cloud_arms_$STARTED.log"
for ((g = 0; g < NGPU; g++)); do
  (
    for ((i = g; i < ${#LINES[@]}; i += NGPU)); do run_arm "$g" "${LINES[$i]}"; done
  ) &
done
wait
[ "${DRY_RUN:-0}" = 1 ] && exit 0
for l in "${LINES[@]}"; do
  read -r _ rest <<< "$l"; read -ra kv <<< "$rest"; tag=$(get TAG "${kv[@]}")
  for t in "$tag" "${tag}_asr"; do
    f=runs/sft_${t}_score.json
    if [ -f "$f" ]; then
      echo "$t: $($PY -c "import json; d=json.load(open('$f')); print(round(d['score'], 2), {c: round(v['score'], 2) for c, v in d['by_category'].items()})")"
    fi
  done
done | tee -a "runs/cloud_arms_$STARTED.log"

if [ "${PACK:-1}" = 1 ]; then
  OUT=../cloud_results_$(hostname)_$STARTED.tar.gz
  adapters=()
  for l in "${LINES[@]}"; do
    read -r kind rest <<< "$l"; read -ra kv <<< "$rest"; tag=$(get TAG "${kv[@]}")
    if [ "$kind" = train ] && [ -d "ckpt/$tag/final" ]; then adapters+=("ckpt/$tag/final"); fi
  done
  tar -czf "$OUT" runs "${adapters[@]}"
  stamp "results: $OUT ($(du -h "$OUT" | cut -f1)); bring it back to the local machine"
fi
