#!/usr/bin/env bash
# Final runs on one GPU machine (JOURNAL entry 138): train ONE base model with the submitted recipe (NF4, QLoRA r32,
# lr 2e-4, 1 epoch, 8-bit AdamW, max length 6144; scripts/final_train.sh) on ALL train samples, seeds 0 and 1 (one per
# GPU), then a public_test file from each (25 s budget, search guard on), and pack the results.
# Training data comes from the train split only: lifemate.sft draws distractor apps from the train catalog, and no
# synthetic file is added (the organisers' FAQ of 09/11/2026 forbids using public_test data to build training data).
# From the unpacked bundle folder ZAIC_2026/:
#   RUN=v7q3 nohup bash lifemate/scripts/final_run.sh > run.log 2>&1 &
#   RUN=v7q35 MODEL=principled-intelligence/Qwen3.5-4B-text-only \
#     LORA_TARGETS=q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj,in_proj_qkv,in_proj_z,out_proj \
#     nohup bash lifemate/scripts/final_run.sh > run.log 2>&1 &
# Every RUN has its own lock (~/.zac_$RUN.lock), adapters (ckpt/${RUN}_s<seed>/final), public files
# (runs/public_${RUN}_s<seed>.jsonl) and results file (~/zac_${RUN}_results.tar.gz), so two runs unpacked in two
# folders of a shared home never touch each other's files. A restart with the same command resumes: a finished adapter
# or public file is kept (scripts/final_train.sh).
# Env: RUN (required; letters, digits, _), MODEL (default Qwen/Qwen3-4B-Instruct-2507), LORA_TARGETS (default: the
#      train.py default), SEEDS (default "0 1"), GPUS (default: every visible GPU), MIN_FREE_GB (default 40).
# The setup (scripts/cloud_setup.sh) checks the bundle and the pinned model revisions; after it the run is offline
# (HF_HUB_OFFLINE=1), so training and inference use only the cache the setup checked.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT=$(cd .. && pwd)
RUN=${RUN:-}
[[ $RUN =~ ^[A-Za-z0-9_]+$ ]] || { echo "set RUN (letters, digits, _), e.g. RUN=v7q3" >&2; exit 2; }
export MODEL=${MODEL:-Qwen/Qwen3-4B-Instruct-2507}
export LORA_TARGETS=${LORA_TARGETS:-}
SEEDS=${SEEDS:-"0 1"}
stamp() { echo "[$(date '+%F %T')] $*"; }
die() { stamp "DUNG: $*"; exit 1; }
pack() {
  local ad=()
  for d in ckpt/"${RUN}"_s*/final; do [ -f "$d/adapter_config.json" ] && ad+=("lifemate/$d"); done
  (cd "$ROOT" && tar -czf "$HOME/zac_${RUN}_results.tar.gz" run.log lifemate/runs "${ad[@]}" 2>/dev/null) \
    && stamp "results: $HOME/zac_${RUN}_results.tar.gz ($(du -h "$HOME/zac_${RUN}_results.tar.gz" | cut -f1))"
}
trap 'rc=$?; pack; if [ $rc = 0 ]; then echo "XONG $(date)"; else echo "DUNG (exit $rc) $(date)"; fi' EXIT
exec 9>"$HOME/.zac_${RUN}.lock"
flock -n 9 || { echo "another final_run.sh with RUN=$RUN is already running (lock $HOME/.zac_${RUN}.lock); this one exits"
                trap - EXIT; exit 3; }
mkdir -p runs ckpt sft
[ -f runs/e2e_public_phoft_asr.jsonl ] || die "no runs/e2e_public_phoft_asr.jsonl (public transcripts of the 05/11 system, in the bundle)"
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader || die "no NVIDIA GPU"
NGPU=${GPUS:-$(nvidia-smi -L | wc -l)}
free_gb=$(df -Pk . | awk 'NR==2{print int($4/1048576)}')
[ "$free_gb" -ge "${MIN_FREE_GB:-40}" ] || die "only ${free_gb} GB free here, need ${MIN_FREE_GB:-40}"
if [ -f runs/cloud_setup.json ] && [ -x .venv/bin/python ]; then
  stamp "setup: already done"
else
  case $MODEL in
    Qwen/Qwen3-4B-Instruct-2507 | Qwen/Qwen3-1.7B) extra="" ;;  # pinned in REV of scripts/cloud_setup.sh
    *) extra=$MODEL ;;                                           # must be pinned in EXTRA_REV of scripts/cloud_setup.sh
  esac
  stamp "setup (base model $MODEL)"
  MODELS="$extra" SMOKE_MODELS="$MODEL" bash scripts/cloud_setup.sh || die "setup failed (see the lines above)"
fi
export HF_HUB_OFFLINE=1   # from here on nothing is downloaded: the models are the ones the setup checked
stamp "run $RUN: $MODEL${LORA_TARGETS:+ (LoRA on $LORA_TARGETS)}, seeds $SEEDS, all train samples, distractors from the train catalog only"
i=0; pids=()
for s in $SEEDS; do
  gpu=$((i % NGPU)); i=$((i + 1))
  stamp "start ${RUN}_s$s on GPU $gpu"
  ( CUDA_VISIBLE_DEVICES=$gpu TAG=${RUN}_s$s SEED=$s bash scripts/final_train.sh > "runs/final_${RUN}_s$s.log" 2>&1 \
      && stamp "${RUN}_s$s done" || stamp "WARNING: ${RUN}_s$s failed (runs/final_${RUN}_s$s.log)" ) &
  pids+=($!)
  if [ "$NGPU" -lt 2 ]; then wait "${pids[-1]}"; fi
done
wait
for f in runs/public_"${RUN}"_s*_check.json; do
  [ -f "$f" ] && stamp "$f: $(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print({k: d[k] for k in ('ok', 'lines', 'expected', 'errors') if k in d})" "$f")"
done
exit 0
