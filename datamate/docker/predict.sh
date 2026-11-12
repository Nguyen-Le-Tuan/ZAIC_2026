#!/usr/bin/env bash
# DataMate entry point: reads /data (data/<business_id>/, rulebook.md, calendar.csv, questions.jsonl),
# writes /result/submission.jsonl (one line per question, written as soon as it is answered) and /result/logs/log.jsonl.
# No arguments, no environment variables needed; everything is fixed here. CPU only, no model, no network.
set -euo pipefail
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
DATA=/data
OUT=/result
mkdir -p "$OUT/logs" /tmp/dm_cache
cd /code/src
t0=$(date +%s%3N)
python -m dm.run --split "$DATA" --out "$OUT" --cache /tmp/dm_cache -v
t1=$(date +%s%3N)
n=$(wc -l < "$OUT/submission.jsonl")
echo "model load time: 0 ms (no model)"
echo "prediction time: $((t1 - t0)) ms for $n questions"
