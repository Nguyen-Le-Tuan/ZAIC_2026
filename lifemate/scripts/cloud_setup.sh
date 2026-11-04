#!/usr/bin/env bash
# One-time setup on a rented GPU machine (Linux + NVIDIA driver), after unpacking the bundle that
# scripts/make_cloud_bundle.sh writes:
#   tar -xzf zac_cloud_bundle_*.tar.gz && cd ZAIC_2026 && bash lifemate/scripts/cloud_setup.sh 2>&1 | tee setup.log
# 1. checks the bundle: sha256 of data, gen/, adapters and runs against BUNDLE_MANIFEST.json
# 2. venv with the exact library versions of the local training machine (requirements-lock.txt) and
#    torch 2.15.0 in a CUDA build this driver supports
# 3. base models at the revisions the local runs used; refuses another revision (ALLOW_NEW_REVISION=1 overrides)
# 4. CPU tests; SFT files rebuilt and compared with the local ones (sha256 in the manifest)
# 5. GPU smoke test on GPU 0: 3 training steps + 2 rollouts per model in SMOKE_MODELS
# Writes lifemate/runs/cloud_setup.json (GPU, driver, versions, tokens/s, peak memory, rough hours per epoch).
# ASR_ONLY=1 stops after step 2 (enough for lifemate.asr_train / lifemate.asr: no LLM download, SFT files or smoke test).
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(cd .. && pwd)
TORCH_VERSION=2.15.0
declare -A REV=([Qwen/Qwen3-1.7B]=70d244cc86ccca08cf5af4e1e306ecf908b1ad5e
                [Qwen/Qwen3-4B-Instruct-2507]=cdbee75f17c01a7cc42f958dc650907174af0554)
SMOKE_MODELS=${SMOKE_MODELS:-"Qwen/Qwen3-4B-Instruct-2507 Qwen/Qwen3-1.7B"}
stamp() { echo "[$(date '+%F %T')] $*"; }
die() { echo "SETUP FAILED: $*" >&2; exit 1; }
mkdir -p runs ckpt sft

stamp "1/5 bundle"
[ -f "$ROOT/data/train+public_test/train/train.jsonl" ] || die "no data/train+public_test under $ROOT"
if [ -f "$ROOT/BUNDLE_MANIFEST.json" ]; then
  python3 - "$ROOT" <<'PY' || die "bundle files differ from BUNDLE_MANIFEST.json"
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1]); man = json.loads((root / "BUNDLE_MANIFEST.json").read_text())
# .DS_Store and __pycache__ files are junk some uploaders (Kaggle datasets) drop; missing ones are not an error
junk = lambda f: Path(f).name == ".DS_Store" or "__pycache__" in Path(f).parts
dropped = [f for f in man["files"] if junk(f) and not (root / f).is_file()]
bad = [f for f, h in man["files"].items() if f not in dropped
       and (not (root / f).is_file() or hashlib.sha256((root / f).read_bytes()).hexdigest() != h)]
print(f"bundle {man['commit'][:10]} ({man['ref']}): {len(man['files'])} files, {len(bad)} differ", bad[:5],
      f"({len(dropped)} missing .DS_Store/__pycache__ files ignored)" if dropped else "")
sys.exit(1 if bad else 0)
PY
else
  echo "no BUNDLE_MANIFEST.json: not unpacked from a bundle, skipping the file check"
fi
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader || die "no NVIDIA GPU visible"

stamp "2/5 python env"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
[ -x .venv/bin/python ] || uv venv --python 3.12 .venv
PY=.venv/bin/python
torch_ok() { $PY -c "import torch; assert torch.cuda.is_available(); torch.ones(1).cuda()" >/dev/null 2>&1; }
if ! torch_ok; then
  # PyPI's default build first; then older CUDA builds for older drivers. TORCH_INDEX_URL forces one.
  for idx in ${TORCH_INDEX_URL:-} pypi https://download.pytorch.org/whl/cu130 https://download.pytorch.org/whl/cu128 \
             https://download.pytorch.org/whl/cu126; do
    if [ "$idx" = pypi ]; then
      uv pip install --python $PY "torch==$TORCH_VERSION" || continue
    else
      uv pip install --python $PY --reinstall "torch==$TORCH_VERSION" --index-url "$idx" || continue
    fi
    if torch_ok; then echo "torch from $idx"; break; fi
  done
fi
torch_ok || die "torch $TORCH_VERSION cannot use this GPU; set TORCH_INDEX_URL to a matching CUDA build"
uv pip install --python $PY -r requirements-lock.txt
$PY -c "import torch, transformers, peft; print('torch', torch.__version__, 'cuda', torch.version.cuda, \
'transformers', transformers.__version__, 'peft', peft.__version__)"
if [ "${ASR_ONLY:-0}" = 1 ]; then
  stamp "ASR_ONLY=1: python env ready; LLM models, SFT files and the GPU smoke test skipped"
  exit 0
fi

stamp "3/5 base models"
for m in "${!REV[@]}"; do
  snap=$(.venv/bin/hf download "$m" --quiet 2>/dev/null | tail -1 || true)
  [ -n "$snap" ] || snap=$(.venv/bin/hf download "$m" | tail -1)
  got=$(basename "$snap")
  if [ "$got" != "${REV[$m]}" ]; then
    [ "${ALLOW_NEW_REVISION:-0}" = 1 ] || die "$m main is $got, local runs used ${REV[$m]} (ALLOW_NEW_REVISION=1 to accept)"
    echo "WARNING: $m at $got, not ${REV[$m]}"
  fi
  echo "$m @ $got"
done
export HF_HUB_OFFLINE=1   # from here on nothing is downloaded silently

stamp "4/5 tests and SFT files"
$PY -m lifemate.tests.test_scorer
$PY -m lifemate.tests.test_counterfactual
if [ -d "$ROOT/data/train+public_test/train/audio" ]; then $PY -m lifemate.tests.test_asr; else echo "no audio: test_asr skipped"; fi
$PY -m lifemate.sft --reuse --fit splits/fit_random.txt --out sft/fit_random.jsonl
$PY -m lifemate.sft --reuse --fit splits/fit_lao.txt --drop-apps splits/heldout_apps.json --out sft/fit_lao.jsonl
for d in dev_random dev_lao; do
  $PY -m lifemate.sft --reuse --fit "splits/$d.txt" --rename 0 --p-remove 0 --p-distract 0 --p-lower 0 --out "sft/$d.jsonl"
done
if [ -f "$ROOT/BUNDLE_MANIFEST.json" ]; then
  python3 - "$ROOT" <<'PY' || [ "${ALLOW_SFT_DIFF:-0}" = 1 ] || die "rebuilt SFT files differ from the local ones (ALLOW_SFT_DIFF=1 to go on)"
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1]); exp = json.loads((root / "BUNDLE_MANIFEST.json").read_text()).get("expected_sft", {})
bad = []
for name, h in exp.items():
    p = root / "lifemate" / "sft" / name
    if p.is_file():
        same = hashlib.sha256(p.read_bytes()).hexdigest() == h
        print(f"sft/{name}: {'same as local' if same else 'DIFFERENT'}")
        bad += [] if same else [name]
sys.exit(1 if bad else 0)
PY
fi

stamp "5/5 GPU smoke test on GPU 0"
for m in $SMOKE_MODELS; do
  t=$(echo "$m" | tr '/.' '__')
  CUDA_VISIBLE_DEVICES=0 $PY -m lifemate.train --model "$m" --data sft/fit_random.jsonl --max-steps 3 --log-every 1 \
      --save-every 100000 --out "ckpt/_smoke_$t" --overwrite > "runs/cloud_smoke_train_$t.log" 2>&1 \
      || { tail -20 "runs/cloud_smoke_train_$t.log"; die "training smoke test of $m"; }
  CUDA_VISIBLE_DEVICES=0 $PY -m lifemate.infer --split train --ids splits/dev_random.txt --limit 2 --text oracle \
      --backend hf --model "$m" --out "runs/cloud_smoke_infer_$t.jsonl" --trace "runs/cloud_smoke_infer_${t}_trace.jsonl" \
      --overwrite > "runs/cloud_smoke_infer_$t.log" 2>&1 || { tail -20 "runs/cloud_smoke_infer_$t.log"; die "rollout smoke test of $m"; }
done

$PY - "$SMOKE_MODELS" <<'PY'
import json, subprocess, sys
from pathlib import Path
import torch, transformers, peft
TOKENS_PER_EPOCH = 12.7e6  # fit_random / fit_lao, measured on the local runs (~1.4K tok/s for ~2.5 h)
smi = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                     capture_output=True, text=True).stdout.strip().splitlines()
out = {"gpus": smi, "torch": torch.__version__, "cuda": torch.version.cuda, "transformers": transformers.__version__,
       "peft": peft.__version__, "smoke": {}}
for m in sys.argv[1].split():
    t = m.replace("/", "_").replace(".", "_")
    recs = [json.loads(l) for l in Path(f"runs/cloud_smoke_train_{t}.log").read_text().splitlines() if l.startswith("{")]
    last = recs[-1] if recs else {}
    infer = Path(f"runs/cloud_smoke_infer_{t}.log").read_text().strip().splitlines()[-1:]
    tok_s = last.get("tok_s")
    out["smoke"][m] = {"tok_s": tok_s, "peak_gb": last.get("peak_gb"), "infer": infer,
                       "rough_hours_per_epoch": round(TOKENS_PER_EPOCH / tok_s / 3600, 2) if tok_s else None}
Path("runs/cloud_setup.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(json.dumps(out, indent=1, ensure_ascii=False))
PY
stamp "setup done. Next: bash lifemate/scripts/cloud_arms.sh lifemate/cloud/arms_2026-10-31.txt"
