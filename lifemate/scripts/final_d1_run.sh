#!/usr/bin/env bash
# The two final runs with D1 data on one GPU machine (JOURNAL entry 127): the submitted recipe (Qwen3-4B-Instruct-2507
# NF4, QLoRA r32, lr 2e-4, 1 epoch, max length 6144) on ALL train samples plus the D1 file (synthetic samples
# for the 11 apps only public_test has), seeds 0 and 1, one per GPU; then a public_test file from each (25 s budget,
# search guard on). From the unpacked bundle folder ZAIC_2026/:
#   nohup bash lifemate/scripts/final_d1_run.sh > run.log 2>&1 &
# A restart (same command) resumes: a finished adapter or public file is kept (scripts/final_train.sh).
# Env: D1 (default gen/d1_pub_v1.jsonl: all 2,139 samples, Anh's choice on 09/11; gen/d1_pub_v1_105.jsonl is the
#      105-per-app subset, the density the dev_lao pilot measured), SEEDS (default "0 1"), MIN_FREE_GB (default 40).
set -uo pipefail
cd "$(dirname "$0")/.."
ROOT=$(cd .. && pwd)
D1=${D1:-gen/d1_pub_v1.jsonl}
SEEDS=${SEEDS:-"0 1"}
stamp() { echo "[$(date '+%F %T')] $*"; }
die() { stamp "DUNG: $*"; exit 1; }
pack() {
  local ad=()
  for d in ckpt/fd1_s*/final; do [ -f "$d/adapter_config.json" ] && ad+=("lifemate/$d"); done
  (cd "$ROOT" && tar -czf "$HOME/zac_v6_results.tar.gz" run.log lifemate/runs "${ad[@]}" 2>/dev/null) \
    && stamp "results: $HOME/zac_v6_results.tar.gz ($(du -h "$HOME/zac_v6_results.tar.gz" | cut -f1))"
}
trap 'rc=$?; pack; if [ $rc = 0 ]; then echo "XONG $(date)"; else echo "DUNG (exit $rc) $(date)"; fi' EXIT
exec 9>"$HOME/.zac_v6.lock"
flock -n 9 || { echo "another final_d1_run.sh is already running (lock $HOME/.zac_v6.lock); this one exits"; trap - EXIT; exit 3; }
mkdir -p runs ckpt sft
[ -f "$D1" ] || die "no $D1 (D1 samples, in the bundle)"
[ -f runs/e2e_public_phoft_asr.jsonl ] || die "no runs/e2e_public_phoft_asr.jsonl (public transcripts of the 05/11 system, in the bundle)"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader || die "no NVIDIA GPU"
NGPU=${GPUS:-$(nvidia-smi -L | wc -l)}
free_gb=$(df -Pk . | awk 'NR==2{print int($4/1048576)}')
[ "$free_gb" -ge "${MIN_FREE_GB:-40}" ] || die "only ${free_gb} GB free here, need ${MIN_FREE_GB:-40}"
if [ -f runs/cloud_setup.json ] && [ -x .venv/bin/python ]; then
  stamp "setup: already done"
else
  stamp "setup"
  SMOKE_MODELS="Qwen/Qwen3-4B-Instruct-2507" bash scripts/cloud_setup.sh || die "setup failed (see the lines above)"
fi
stamp "D1 samples: $(wc -l < "$D1") rows, sha256 $(sha256sum "$D1" | cut -c1-16)"
i=0; pids=()
for s in $SEEDS; do
  gpu=$((i % NGPU)); i=$((i + 1))
  stamp "start fd1_s$s on GPU $gpu"
  ( CUDA_VISIBLE_DEVICES=$gpu TAG=fd1_s$s SEED=$s D1_SAMPLES=$D1 bash scripts/final_train.sh > "runs/final_fd1_s$s.log" 2>&1 \
      && stamp "fd1_s$s done" || stamp "WARNING: fd1_s$s failed (runs/final_fd1_s$s.log)" ) &
  pids+=($!)
  if [ "$NGPU" -lt 2 ]; then wait "${pids[-1]}"; fi
done
wait
for f in runs/public_fd1_s*_check.json; do
  [ -f "$f" ] && stamp "$f: $(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print({k: d[k] for k in ('ok', 'rows', 'errors') if k in d})" "$f")"
done
exit 0
