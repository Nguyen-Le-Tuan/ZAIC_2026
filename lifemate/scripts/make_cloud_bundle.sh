#!/usr/bin/env bash
# Pack everything a cloud GPU machine needs to train and evaluate, as ONE private tarball:
#   ZAIC_2026/                     code at REF (git archive, so exactly the reviewed commit)
#   ZAIC_2026/data/train+public_test/   licensed competition data (audio only with WITH_AUDIO=1)
#   ZAIC_2026/lifemate/gen/        D-experiment data (train-derived, never in git)
#   ZAIC_2026/lifemate/asr/train_* ASR transcripts of train wavs (train-derived, never in git); public ASR is not packed
#   ZAIC_2026/lifemate/ckpt/<tag>/final   LoRA adapters to re-evaluate on the cloud (parity check)
#   ZAIC_2026/lifemate/runs/<run>* local runs those re-evaluations are compared with
#   ZAIC_2026/BUNDLE_MANIFEST.json commit, sha256 of every file that is not in git, sha256 of the local SFT files
# The tarball holds licensed data: upload it only to the team's own rented machine, never to git or a share.
# SFT files are not packed: scripts/cloud_setup.sh rebuilds them and their manifests prove they are identical.
#
#   bash lifemate/scripts/make_cloud_bundle.sh                       # from a checkout that has this script
#   SRC=~/"Zalo AI Challenge" REF=origin/cloud-train WITH_AUDIO=1 bash .../make_cloud_bundle.sh
# Env: SRC (folder with data/ and lifemate/{gen,ckpt,runs}; default: this checkout), REF (git ref, default HEAD),
#      ADAPTERS (ckpt tags), RUNS (run prefixes), WITH_AUDIO=1, OUT (tarball path).
set -euo pipefail
HERE="$(cd "$(dirname "$0")/../.." && pwd)"
SRC=${SRC:-$HERE}
REF=${REF:-HEAD}
ADAPTERS=${ADAPTERS:-"q17b_fit_random q17b_fit_lao"}
RUNS=${RUNS:-"sft_q17b_fit_random sft_q17b_fit_lao sft_q17b_fit_random_asrturbo sft_q17b_fit_lao_asrturbo sft_q17b_fit_random_asrpho sft_q17b_fit_lao_asrpho"}
WITH_AUDIO=${WITH_AUDIO:-0}
OUT=${OUT:-$HOME/zac_cloud_bundle_$(date +%Y%m%d_%H%M).tar.gz}
DATA="$SRC/data/train+public_test"
[ -f "$DATA/train/train.jsonl" ] || { echo "no $DATA/train/train.jsonl (set SRC)" >&2; exit 1; }
[ ! -e "$OUT" ] || { echo "refusing to overwrite $OUT" >&2; exit 1; }

STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
B="$STAGE/ZAIC_2026"
mkdir -p "$B"
COMMIT=$(git -C "$HERE" rev-parse "$REF")
git -C "$HERE" archive "$COMMIT" | tar -x -C "$B"
[ -f "$B/lifemate/scripts/cloud_setup.sh" ] || { echo "$REF has no lifemate/scripts/cloud_setup.sh" >&2; exit 1; }

mkdir -p "$B/data"
if [ "$WITH_AUDIO" = 1 ]; then
  cp -a "$DATA" "$B/data/"
else
  (cd "$SRC/data" && tar -c --exclude='train+public_test/*/audio' train+public_test) | tar -x -C "$B/data"
fi
cp -a "$SRC/lifemate/gen" "$B/lifemate/gen"
mkdir -p "$B/lifemate/asr"
for f in "$SRC"/lifemate/asr/train_*; do
  if [ -f "$f" ]; then cp -a "$f" "$B/lifemate/asr/"; fi
done
for t in $ADAPTERS; do
  [ -f "$SRC/lifemate/ckpt/$t/final/adapter_config.json" ] || { echo "no adapter ckpt/$t/final" >&2; exit 1; }
  mkdir -p "$B/lifemate/ckpt/$t" && cp -a "$SRC/lifemate/ckpt/$t/final" "$B/lifemate/ckpt/$t/final"
done
mkdir -p "$B/lifemate/runs"
for r in $RUNS; do
  for f in "$SRC/lifemate/runs/$r".jsonl "$SRC/lifemate/runs/$r".meta.json "$SRC/lifemate/runs/${r}"_{trace,rows}.jsonl \
           "$SRC/lifemate/runs/${r}"_score.json; do
    if [ -f "$f" ]; then cp -a "$f" "$B/lifemate/runs/"; fi
  done
done

python3 - "$B" "$COMMIT" "$REF" "$WITH_AUDIO" "$SRC/lifemate/sft" <<'PY'
import hashlib, json, sys, time
from pathlib import Path
b, commit, ref, audio = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4] == "1"
files = {}
for p in sorted(b.rglob("*")):
    rel = p.relative_to(b).as_posix()
    if p.is_file() and rel.startswith(("data/", "lifemate/gen/", "lifemate/asr/", "lifemate/ckpt/", "lifemate/runs/")):
        files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
# SFT files the cloud rebuilds; their local hashes prove the cloud trains on the same rows
sft = Path(sys.argv[5])
expected_sft = {n: hashlib.sha256((sft / n).read_bytes()).hexdigest()
                for n in ("fit_random.jsonl", "fit_lao.jsonl", "dev_random.jsonl", "dev_lao.jsonl") if (sft / n).is_file()}
man = {"created": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "ref": ref, "commit": commit, "with_audio": audio,
       "note": "private: licensed competition data; do not commit or share", "files": files,
       "expected_sft": expected_sft}
(b / "BUNDLE_MANIFEST.json").write_text(json.dumps(man, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"manifest: {len(files)} non-git files, commit {commit[:10]}")
PY

tar -czf "$OUT" -C "$STAGE" ZAIC_2026
echo "bundle: $OUT ($(du -h "$OUT" | cut -f1)), sha256 $(sha256sum "$OUT" | cut -d' ' -f1)"
echo "PRIVATE: contains the licensed dataset. Upload only to the team's own cloud machine."
