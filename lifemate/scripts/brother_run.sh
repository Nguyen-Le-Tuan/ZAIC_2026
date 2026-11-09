#!/usr/bin/env bash
# Unattended run of the 09-10/11 experiments on one GPU machine (Anh's brother's 2x RTX 4090, or a rented one).
# From the unpacked bundle folder ZAIC_2026/:
#   nohup bash lifemate/scripts/brother_run.sh > run.log 2>&1 &
# Steps, in order; a restart (same command) resumes: finished parts are kept, interrupted ones are redone.
#   0. lock (a second start exits at once: pilot v2 was started twice by mistake) and preflight: bf16 GPU, disk, RAM
#   1. setup: scripts/cloud_setup.sh with the two extra base models (skipped once runs/cloud_setup.json exists)
#   2. stage 1, in parallel: the arms of cloud/arms_2026-11-09_models_d2.txt that have no results yet, and on the last
#      GPU the public_test run of the submitted adapter with the search guard (D5, runs/pub_c0_guard.jsonl)
#   3. rule: scripts/arms_rule.py -> runs/arms_decision.{json,txt}
#   4. stage 2 when an arm won: scripts/final_train.sh on all train samples, winner seeds 0 and 1 (GPU 0 and 1), then
#      seed 0 of the fallback arm when there is one -> ckpt/f_<arm>_s<seed>/final + runs/public_f_<arm>_s<seed>.jsonl
#   5. pack ~/zac_v5_results.tar.gz (run.log, lifemate/runs, stage-2 adapters) and print XONG
# Env: ARMS (arms file, default the one above), MIN_FREE_GB (default 50), STAGE2=0 (stop after the rule),
#      DRY_RUN=1 (print the plan: no preflight, setup or GPU job).
set -uo pipefail
cd "$(dirname "$0")/.."                      # lifemate/
ROOT=$(cd .. && pwd)                          # ZAIC_2026/
ARMS=${ARMS:-cloud/arms_2026-11-09_models_d2.txt}
PUBLIC_ASR=runs/e2e_public_phoft_asr.jsonl
DRY=${DRY_RUN:-0}
PY=.venv/bin/python
stamp() { echo "[$(date '+%F %T')] $*"; }
die() { stamp "DUNG: $*"; exit 1; }

pack() {   # results to send back, whatever state the run is in
  [ "$DRY" = 1 ] && return 0
  local ad=()
  for d in ckpt/f_*/final; do [ -f "$d/adapter_config.json" ] && ad+=("lifemate/$d"); done
  (cd "$ROOT" && tar -czf "$HOME/zac_v5_results.tar.gz" run.log lifemate/runs "${ad[@]}" 2>/dev/null) \
    && stamp "results: $HOME/zac_v5_results.tar.gz ($(du -h "$HOME/zac_v5_results.tar.gz" | cut -f1))"
}
trap 'rc=$?; pack; if [ $rc = 0 ]; then echo "XONG $(date)"; else echo "DUNG (exit $rc) $(date)"; fi' EXIT

# ---------------------------------------------------------------- 0. lock + preflight
exec 9>"$HOME/.zac_v5.lock"
flock -n 9 || { echo "another brother_run.sh is already running (lock $HOME/.zac_v5.lock); this one exits"; trap - EXIT; exit 3; }
mkdir -p runs ckpt sft
[ -f "$ARMS" ] || die "no $ARMS"
[ -f "$PUBLIC_ASR" ] || die "no $PUBLIC_ASR (public transcripts of the 05/11 system, in the bundle)"
[ -f ckpt/q4b4_all/final/adapter_config.json ] || die "no ckpt/q4b4_all/final (submitted adapter, in the bundle)"
if [ "$DRY" = 1 ]; then
  NGPU=${GPUS:-2}
  stamp "DRY_RUN: assuming $NGPU GPU(s)"
else
  nvidia-smi --query-gpu=index,name,memory.total,driver_version,compute_cap --format=csv,noheader || die "no NVIDIA GPU"
  nvidia-smi --query-gpu=compute_cap --format=csv,noheader | awk -F. '$1<8{bad=1} END{exit bad}' \
    || die "a GPU without bf16 (compute capability < 8.0): this recipe needs RTX 30/40, A100, L4, H100..."
  NGPU=${GPUS:-$(nvidia-smi -L | wc -l)}
  free_gb=$(df -Pk . | awk 'NR==2{print int($4/1048576)}')
  [ "$free_gb" -ge "${MIN_FREE_GB:-50}" ] || die "only ${free_gb} GB free here, need ${MIN_FREE_GB:-50}"
  stamp "preflight ok: $NGPU GPU(s), ${free_gb} GB free, RAM $(free -g | awk '/Mem:/{print $2}') GB"
fi

# ---------------------------------------------------------------- 1. setup
if [ -f runs/cloud_setup.json ] && [ -x "$PY" ]; then
  stamp "1. setup: already done (runs/cloud_setup.json)"
elif [ "$DRY" = 1 ]; then
  stamp "1. setup: would run scripts/cloud_setup.sh with MODELS (Thinking-2507, Qwen3.5-4B text-only)"
else
  stamp "1. setup"
  MODELS="Qwen/Qwen3-4B-Thinking-2507 principled-intelligence/Qwen3.5-4B-text-only" \
  SMOKE_MODELS="principled-intelligence/Qwen3.5-4B-text-only Qwen/Qwen3-4B-Thinking-2507" \
    bash scripts/cloud_setup.sh || die "setup failed (see the lines above)"
fi

# ---------------------------------------------------------------- 2. stage 1
PENDING=runs/arms_pending.txt
python3 - "$ARMS" "$PENDING" "$DRY" <<'PY'
# arms without results -> pending file; trained arms with missing rollouts become eval lines; partial files are moved
# aside so the scripts (which refuse to overwrite) can redo them
import sys, time
from pathlib import Path
arms, out, dry = sys.argv[1], Path(sys.argv[2]), sys.argv[3] == "1"
runs, now, lines = Path("runs"), int(time.time()), []
def aside(p: Path):
    if p.exists():
        print(f"  move aside {p}")
        if not dry:
            p.rename(p.with_name(f"{p.name}.partial-{now}"))
def clear(part):
    for suf in (".jsonl", "_rows.jsonl", "_score.json", "_trace.jsonl", ".meta.json"):
        aside(runs / f"sft_{part}{suf}")
for raw in Path(arms).read_text().splitlines():
    s = raw.split("#", 1)[0].strip()
    if not s.startswith("train "):
        continue
    kv = dict(x.split("=", 1) for x in s.split()[1:])
    tag = kv["TAG"]
    ok = {p: (runs / f"sft_{p}_score.json").exists() for p in (tag, f"{tag}_asr")}
    if all(ok.values()):
        print(f"  done   {tag}")
        continue
    if (Path("ckpt") / tag / "final" / "adapter_config.json").exists():
        base = {k: kv[k] for k in ("MODEL", "DEV", "LOAD_4BIT", "TIME_BUDGET") if k in kv}
        for part, extra in ((tag, {}), (f"{tag}_asr", {"ASR_FILE": kv["ASR_DEV"]})):
            if not ok[part]:
                clear(part)
                lines.append("eval " + " ".join(f"{k}={v}" for k, v in {"TAG": part, "ADAPTER": f"ckpt/{tag}/final", **base, **extra}.items()))
        print(f"  eval   {tag} (trained; rollouts to redo)")
    else:
        aside(Path("ckpt") / tag)
        clear(tag); clear(f"{tag}_asr")
        lines.append(s)
        print(f"  train  {tag}")
out.write_text("".join(l + "\n" for l in lines))
print(f"{len(lines)} pending line(s) -> {out}")
PY

pub_c0_guard() {   # D5 on public_test: the submitted adapter and transcripts, only --search-guard added
  local out=runs/pub_c0_guard
  if [ -f "${out}_check.json" ]; then stamp "public C0 + search guard: already done"; return 0; fi
  for f in "$out.jsonl" "${out}_trace.jsonl" "$out.meta.json"; do [ -e "$f" ] && mv "$f" "$f.partial-$(date +%s)"; done
  stamp "public C0 + search guard on GPU $1"
  CUDA_VISIBLE_DEVICES=$1 $PY -m lifemate.infer --split public_test --text asr --asr-file "$PUBLIC_ASR" --backend hf \
      --model Qwen/Qwen3-4B-Instruct-2507 --load-4bit --adapter ckpt/q4b4_all/final --time-budget 25 --search-guard \
      --out "$out.jsonl" --trace "${out}_trace.jsonl" \
    && $PY scripts/check_submission.py "$out.jsonl" --split public_test --require-time --asr-file "$PUBLIC_ASR" \
      --trace "${out}_trace.jsonl" --json "${out}_check.json"
}

LAST=$((NGPU - 1))
if [ "$DRY" = 1 ]; then
  stamp "2. stage 1: would run cloud_arms.sh on $PENDING and the public C0 + guard job on GPU $LAST"
  [ -s "$PENDING" ] && GPUS=$NGPU DRY_RUN=1 bash scripts/cloud_arms.sh "$PENDING" | grep "^GPU" || true
else
  stamp "2. stage 1"
  (pub_c0_guard "$LAST" > runs/pub_c0_guard.log 2>&1) &
  PUB=$!
  if [ -s "$PENDING" ]; then PACK=0 bash scripts/cloud_arms.sh "$PENDING"; else stamp "no arm left to run"; fi
  wait "$PUB" || stamp "WARNING: the public C0 + guard job failed (runs/pub_c0_guard.log)"
fi

# ---------------------------------------------------------------- 3. rule
if [ "$DRY" = 1 ] && [ ! -f runs/sft_a0_q4b4_lao_s0_score.json ]; then
  stamp "3. rule: would run scripts/arms_rule.py (no results yet in this dry run)"
  exit 0
fi
stamp "3. rule"
python3 scripts/arms_rule.py --arms "$ARMS" --json runs/arms_decision.json | tee runs/arms_decision.txt \
  || die "arms_rule.py failed"

# ---------------------------------------------------------------- 4. stage 2
[ "${STAGE2:-1}" = 1 ] || { stamp "STAGE2=0: stop after the rule"; exit 0; }
read -r WIN FALL < <(python3 -c "import json; d=json.load(open('runs/arms_decision.json')); print(d['winner'] or '-', d['fallback'] or '-')")
if [ "$WIN" = "-" ]; then
  stamp "4. stage 2: no arm passed the rule; nothing to train on all data (the team keeps the 05/11 system)"
  exit 0
fi
envs() {   # KEY=value words of an arm's config, for env(1)
  python3 - "$1" <<'PY'
import json, sys
c = json.load(open("runs/arms_decision.json"))["arms"][sys.argv[1]]["config"]
print(" ".join(f"{k}={c[k]}" for k in ("MODEL", "THOUGHTS", "LORA_TARGETS") if c.get(k)))
PY
}
final() {   # arm seed gpu
  local tag="f_${1}_s$2"
  stamp "stage 2: $tag on GPU $3 ($(envs "$1"))"
  if [ "$DRY" = 1 ]; then return 0; fi
  # shellcheck disable=SC2046
  env CUDA_VISIBLE_DEVICES="$3" TAG="$tag" SEED="$2" $(envs "$1") bash scripts/final_train.sh > "runs/final_$tag.log" 2>&1 \
    && stamp "stage 2: $tag done" || stamp "WARNING: stage 2 $tag failed (runs/final_$tag.log)"
}
stamp "4. stage 2: winner $WIN${FALL:+, fallback $FALL}"
if [ "$NGPU" -ge 2 ]; then
  ( final "$WIN" 0 0; [ "$FALL" != "-" ] && final "$FALL" 0 0 ) &
  A=$!
  final "$WIN" 1 1
  wait "$A"
else
  final "$WIN" 0 0; final "$WIN" 1 0; [ "$FALL" != "-" ] && final "$FALL" 0 0
fi
for f in runs/public_f_*_check.json runs/pub_c0_guard_check.json; do
  [ -f "$f" ] && stamp "$f: $(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print({k: d[k] for k in ('ok', 'rows', 'errors') if k in d})" "$f")"
done
exit 0
