"""Check a submission.jsonl before anyone uploads it, and sum per-sample wall time (ASR + agent) when given the files.

  .venv/bin/python scripts/check_submission.py runs/e2e_public_turbo.jsonl --split public_test \
      --asr-file runs/e2e_public_turbo_asr.jsonl --trace runs/e2e_public_turbo_trace.jsonl --json runs/e2e_public_turbo_check.json

Fails (exit 1) on: a line that is not {"id", "tool_calls": [{"name", "arguments"}...], "state_hash": 64 hex}, duplicate
ids, ids missing from or foreign to the split. Also runs the organiser's schema check (python -m zaic_tools --validate);
schema errors are reported, not fatal, because rejected calls are part of a valid submission (the agent normally
validates before calling, so expect 0).
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate.data import DEFAULT_ROOT, load_jsonl, load_split  # noqa: E402
from lifemate.runinfo import percentile, read_ids, write_json  # noqa: E402

HASH = re.compile(r"^[0-9a-f]{64}$")


def structure_errors(rows: list[dict], want: list[str]) -> list[str]:
    errs = []
    for i, r in enumerate(rows):
        if set(r) != {"id", "tool_calls", "state_hash"}:
            errs.append(f"line {i + 1}: keys {sorted(r)}")
            continue
        if not isinstance(r["state_hash"], str) or not HASH.match(r["state_hash"]):
            errs.append(f"{r['id']}: bad state_hash")
        calls = r["tool_calls"]
        if not isinstance(calls, list) or not all(
                isinstance(c, dict) and set(c) == {"name", "arguments"} and isinstance(c["name"], str)
                and isinstance(c["arguments"], dict) for c in calls):
            errs.append(f"{r['id']}: bad tool_calls")
    ids = [r.get("id") for r in rows]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        errs.append(f"duplicate ids: {dup[:5]}")
    missing, extra = sorted(set(want) - set(ids)), sorted(set(ids) - set(want))
    if missing:
        errs.append(f"{len(missing)} ids missing (first {missing[:3]})")
    if extra:
        errs.append(f"{len(extra)} ids not in the split (first {extra[:3]})")
    return errs


def schema_check(path: str, split: str, root: str) -> dict:
    p = subprocess.run([sys.executable, "-m", "zaic_tools", "--split", split, "--root", str(Path(root).resolve()),
                        "--validate", str(Path(path).resolve())], cwd=Path(root) / split, capture_output=True, text=True)
    last = (p.stdout.strip().splitlines() or [""])[-1]
    m = re.match(r"(\d+) lines checked, (\d+) schema errors", last)
    return {"returncode": p.returncode, "lines": int(m.group(1)) if m else None,
            "schema_errors": int(m.group(2)) if m else None, "tail": p.stdout.strip().splitlines()[-5:],
            "stderr": p.stderr.strip()[-500:]}


def timing(items: list[dict], asr_file: str, trace_file: str) -> dict:
    asr = {r["audio"]: r.get("seconds", 0.0) for r in load_jsonl(asr_file)}
    agent = {t["id"]: t["seconds"] for t in load_jsonl(trace_file)}
    tot, asr_s = [], []
    for s in items:
        a = sum(asr[p] for p in [s["audio"]] + [h["audio"] for h in s.get("history", []) if h["role"] == "user"])
        asr_s.append(a)
        tot.append(a + agent[s["id"]])

    def summ(x):
        return {"mean_s": round(sum(x) / len(x), 3), "p50_s": round(percentile(x, .5), 3),
                "p95_s": round(percentile(x, .95), 3), "max_s": round(max(x), 3)}
    return {"asr": summ(asr_s), "agent": summ([agent[s["id"]] for s in items]), "total": summ(tot),
            "over_25s": sum(t > 25 for t in tot), "over_30s": sum(t > 30 for t in tot),
            "note": "wall time on this machine, models already loaded; not the A30"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("submission")
    ap.add_argument("--split", default="public_test")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--ids", help="the submission covers only these ids (dev runs); default: the whole split")
    ap.add_argument("--asr-file")
    ap.add_argument("--trace")
    ap.add_argument("--json")
    a = ap.parse_args()
    items = load_split(a.split, a.root)
    if a.ids:
        keep = set(read_ids(a.ids))
        items = [s for s in items if s["id"] in keep]
    rows = load_jsonl(a.submission)
    errs = structure_errors(rows, [s["id"] for s in items])
    res = {"submission": a.submission, "split": a.split, "lines": len(rows), "expected": len(items),
           "errors": errs, "ok": not errs, "zaic_tools_validate": schema_check(a.submission, a.split, a.root),
           "calls": sum(len(r.get("tool_calls") or []) for r in rows),
           "empty_rows": sum(not r.get("tool_calls") for r in rows)}
    if a.asr_file and a.trace:
        res["timing"] = timing(items, a.asr_file, a.trace)
    print(json.dumps({k: v for k, v in res.items() if k != "errors"} | {"errors": errs[:10]}, ensure_ascii=False, indent=1))
    if a.json:
        write_json(a.json, res)
    sys.exit(0 if res["ok"] else 1)


if __name__ == "__main__":
    main()
