#!/usr/bin/env bash
# Experiment D, phase 2 (docs/D_PHASE1B_2026-10-30.md section 6): arms trained from the base model on fit_lao plus
# extra samples, all with the same number of optimizer steps as B0 (q17b_fit_lao, 254), then scored on dev_lao and on
# the contrast sets D-eval-24 and CS-pilot-23. Re-running skips finished steps.
#   cd lifemate && bash scripts/phase2_d.sh > runs/phase2_d.log 2>&1
# Arms (TAG:extra samples), most informative first: D x3 and its matched control share the same row count, so with
# seed 0 they see the same gold rows and differ only in the extra rows.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
B0=${B0:-q17b_fit_lao}
STEPS=${STEPS:-254}
ARMS=${ARMS:-"q17b_lao_d3:gen/d_train_1b_x3.jsonl q17b_lao_up:gen/up_real_asks_232.jsonl q17b_lao_d1:gen/d_train_1b.jsonl"}
stamp() { echo "[$(date '+%F %T')] $*"; }

for arm in $ARMS; do
  tag=${arm%%:*}; extra=${arm#*:}
  if [ -e "runs/sft_${tag}_score.json" ]; then
    stamp "skip training/eval of $tag (runs/sft_${tag}_score.json exists)"
  elif [ -e "ckpt/$tag/final" ]; then
    stamp "eval $tag (checkpoint exists, no score yet)"
    TAG="$tag" ADAPTER="ckpt/$tag/final" DEV=dev_lao LOSS=1 bash scripts/eval_ckpt.sh
  else
    stamp "arm $tag: fit_lao + $extra, $STEPS steps"
    FIT=fit_lao DEV=dev_lao TAG="$tag" EXTRA_SAMPLES="$extra" SKIP_ZS=1 EVAL_STEPS=0 TRAIN_ARGS="--max-steps $STEPS" \
      bash scripts/train_local.sh
  fi
  for set in dv1eval:gen/d_v1_eval.jsonl pilot:gen/d_fit_lao.jsonl; do
    name=${set%%:*}; f=${set#*:}
    if [ ! -e "runs/contrast_${tag}_$name.summary.json" ]; then
      stamp "contrast $tag on $name"
      $PY scripts/contrast_eval.py --samples "$f" --adapter "ckpt/$tag/final" --out "runs/contrast_${tag}_$name.jsonl" > /dev/null
    fi
  done
  $PY -m lifemate.compare "runs/sft_$B0" "runs/sft_$tag" --ids splits/dev_lao.txt --slices --json "runs/compare_${B0}_vs_$tag.json"
  stamp "arm $tag done"
done
stamp "phase 2 done"
