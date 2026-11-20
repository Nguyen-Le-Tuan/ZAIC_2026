#!/usr/bin/env bash
# End-to-end baseline (docs/E2E_BASELINE_2026-10-31.md): off-the-shelf ASR -> the existing SFT checkpoints, no training.
#   cd lifemate && bash scripts/e2e_baseline.sh > runs/e2e_baseline.log 2>&1
# 1. ASR with each model on the wavs of dev_random and dev_lao (final + history user turns), then ASR quality.
# 2. Agent on ASR text: q17b_fit_random/final on dev_random, q17b_fit_lao/final (B0) on dev_lao; paired comparison with
#    the existing oracle-text runs of the same checkpoints.
# 3. Pick the ASR model by a rule fixed in advance: higher agent score over dev_random + dev_lao (495 samples); within
#    1 point, the smaller one (turbo).
# 4. public_test through scripts/predict.sh with the picked model (ASR batch 1 for latency) -> checked submission file.
# 5. Reproducibility: ASR again on the first 50 public wavs, batch 1, compared character by character.
# Re-running skips finished steps. A model that fails is logged and skipped; the other one carries on.
set -uo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
LLM=Qwen/Qwen3-1.7B
MODELS="turbo:openai/whisper-large-v3-turbo@41f01f3fe87f28c78e2fbf8b568835947dd65ed9 pho:vinai/PhoWhisper-large@b9136a44b5f2ca664bd0b8f74baecf1715f6eeeb"
DEVS="dev_random:q17b_fit_random dev_lao:q17b_fit_lao"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
stamp() { echo "[$(date '+%F %T')] $*"; }
mkdir -p asr runs

for m in $MODELS; do
  tag=${m%%:*}; spec=${m#*:}; model=${spec%@*}; rev=${spec#*@}
  for d in $DEVS; do
    dev=${d%%:*}; out=asr/train_${dev}_$tag.jsonl
    [ -e "$out" ] && continue
    stamp "asr $tag on $dev"
    $PY -m lifemate.asr --split train --ids "splits/$dev.txt" --model "$model" --revision "$rev" --batch-size 16 \
        --out "$out" || stamp "FAILED asr $tag on $dev"
  done
done

for d in $DEVS; do
  dev=${d%%:*}; files=()
  for m in $MODELS; do f=asr/train_${dev}_${m%%:*}.jsonl; [ -e "$f" ] && files+=("$f"); done
  [ ${#files[@]} -gt 0 ] && [ ! -e "runs/asr_quality_$dev.json" ] && \
    $PY scripts/asr_quality.py "${files[@]}" --ids "splits/$dev.txt" --json "runs/asr_quality_$dev.json"
done

for m in $MODELS; do
  tag=${m%%:*}
  for d in $DEVS; do
    dev=${d%%:*}; ck=${d#*:}; asrf=asr/train_${dev}_$tag.jsonl; P=runs/sft_${ck}_asr$tag
    [ -e "$asrf" ] || continue
    if [ ! -e "${P}_score.json" ]; then
      stamp "agent $ck on $dev with $tag text"
      $PY -m lifemate.infer --split train --ids "splits/$dev.txt" --text asr --asr-file "$asrf" --backend hf \
          --model "$LLM" --adapter "ckpt/$ck/final" --out "$P.jsonl" --trace "${P}_trace.jsonl" || { stamp "FAILED agent $P"; continue; }
      $PY -m lifemate.scorer "$P.jsonl" --split train --ids "splits/$dev.txt" --rows "${P}_rows.jsonl" > "${P}_score.json"
    fi
    $PY -m lifemate.compare "runs/sft_$ck" "$P" --ids "splits/$dev.txt" --slices --json "runs/compare_${ck}_vs_asr$tag.json" > /dev/null
  done
done

PICK=$($PY - "$MODELS" <<'EOF'
import json, sys
from pathlib import Path
models = [m.split(":")[0] for m in sys.argv[1].split()]
devs = {"dev_random": "q17b_fit_random", "dev_lao": "q17b_fit_lao"}
tot = {}
for t in models:
    s = [json.loads(Path(f"runs/sft_{ck}_asr{t}_score.json").read_text()) for ck in devs.values()
         if Path(f"runs/sft_{ck}_asr{t}_score.json").exists()]
    if len(s) == len(devs):
        tot[t] = sum(x["score"] * x["n"] for x in s) / sum(x["n"] for x in s)
best = max(tot, key=tot.get) if tot else ""
if "turbo" in tot and best != "turbo" and tot[best] - tot["turbo"] < 1:
    best = "turbo"
Path("runs/e2e_pick.json").write_text(json.dumps({"combined_score": tot, "pick": best,
    "rule": "higher score over dev_random + dev_lao; within 1 point prefer turbo"}, indent=1) + "\n")
print(best)
EOF
)
[ -n "$PICK" ] || { stamp "no ASR model finished both dev runs; stop"; exit 1; }
stamp "picked ASR: $PICK"
for m in $MODELS; do [ "${m%%:*}" = "$PICK" ] && spec=${m#*:}; done
model=${spec%@*}; rev=${spec#*@}
OUT=runs/e2e_public_$PICK.jsonl
if [ ! -e "${OUT%.jsonl}_check.json" ]; then
  SPLIT=public_test ASR_MODEL="$model" ASR_REV="$rev" ASR_BATCH=1 ADAPTER=ckpt/q17b_fit_random/final OUT="$OUT" \
    bash scripts/predict.sh || stamp "FAILED predict public_test"
fi

R=runs/e2e_public_${PICK}_asr_repro50.jsonl
if [ -e "${OUT%.jsonl}_asr.jsonl" ] && [ ! -e "$R" ]; then
  stamp "reproducibility: ASR again on 50 public wavs"
  $PY -m lifemate.asr --split public_test --max-wavs 50 --model "$model" --revision "$rev" --batch-size 1 --out "$R" && \
  $PY - "${OUT%.jsonl}_asr.jsonl" "$R" <<'EOF'
import json, sys
a = {r["audio"]: r["text"] for r in map(json.loads, open(sys.argv[1]))}
b = [json.loads(l) for l in open(sys.argv[2])]
diff = [r["audio"] for r in b if a.get(r["audio"]) != r["text"]]
print(json.dumps({"compared": len(b), "different": len(diff), "first": diff[:5]}))
EOF
fi
stamp "e2e baseline done"
