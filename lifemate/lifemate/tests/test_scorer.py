"""Regression tests for the local scorer, in particular incomplete prediction files.

Run:  .venv/bin/python -m lifemate.tests.test_scorer        (also works under pytest)
The CLI tests use the real train split and are skipped when data/ is absent.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from lifemate.data import DEFAULT_ROOT
from lifemate.scorer import evaluate, load_predictions

CALL = {"name": "alarm.create", "arguments": {"time": "2026-10-30T06:00:00+07:00"}}
GOLD = {
    "exe": {"tool_calls": [CALL], "state_hash": "h_exe"},
    "oos": {"tool_calls": [], "state_hash": "h_oos"},
}
PKG_DIR = Path(__file__).resolve().parents[2]  # lifemate/ (holds the package and .venv)
EXECUTE_ID, OOS_ID = "train_0003", "train_0019"  # categories checked in the test itself


class Skip(Exception):
    pass


def _skip(msg: str):
    try:
        import pytest
        pytest.skip(msg)
    except ImportError:
        raise Skip(msg) from None


def _by_id(res):
    return {r["id"]: r for r in res["rows"]}


# ------------------------------------------------------------------ evaluate()

def test_missing_execute_scores_zero():
    res = evaluate({"oos": {"tool_calls": [], "state_hash": "x"}}, GOLD, {})
    r = _by_id(res)["exe"]
    assert (r["score"], r["call_f1"], r["hash_ok"], r.get("missing")) == (0.0, 0.0, False, True)


def test_missing_out_of_scope_scores_zero():
    # the bug found in review: a missing id with empty gold used to score 1
    res = evaluate({}, {"oos": GOLD["oos"]}, {})
    assert (res["score"], res["call_f1"], res["hash_acc"], res["missing"]) == (0.0, 0.0, 0.0, 1)


def test_explicit_empty_for_out_of_scope_scores_one():
    res = evaluate({"oos": {"tool_calls": [], "state_hash": "whatever"}}, {"oos": GOLD["oos"]}, {})
    assert (res["score"], res["missing"]) == (100.0, 0)
    assert _by_id(res)["oos"]["hash_ok"] is True


def test_explicit_empty_for_execute_scores_zero():
    res = evaluate({"exe": {"tool_calls": [], "state_hash": "h_exe"}}, {"exe": GOLD["exe"]}, {})
    assert (res["score"], res["missing"]) == (0.0, 0)


def test_correct_and_wrong_hash_unchanged():
    ok = evaluate({"exe": {"tool_calls": [CALL], "state_hash": "h_exe"}}, {"exe": GOLD["exe"]}, {})
    bad = evaluate({"exe": {"tool_calls": [CALL], "state_hash": "other"}}, {"exe": GOLD["exe"]}, {})
    assert ok["score"] == 100.0 and bad["score"] == 0.0 and bad["call_f1"] == 100.0


def test_extra_ids_are_ignored_and_counted():
    pred = {"exe": {"tool_calls": [CALL], "state_hash": "h_exe"}, "stray": {"tool_calls": [], "state_hash": "x"}}
    res = evaluate(pred, {"exe": GOLD["exe"]}, {})
    assert (res["n"], res["extra"], res["score"]) == (1, 1, 100.0)


def test_duplicate_ids_rejected():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "pred.jsonl"
        row = json.dumps({"id": "a", "tool_calls": [], "state_hash": "x"})
        p.write_text(row + "\n" + row + "\n")
        try:
            load_predictions(p)
        except ValueError as e:
            assert "more than once" in str(e)
        else:
            raise AssertionError("duplicate ids were accepted")


# ------------------------------------------------------------------ CLI on the real train split

def _cli(pred_rows: list[dict], ids: list[str] | None):
    if not (Path(DEFAULT_ROOT) / "train" / "train.jsonl").exists():
        _skip("train data not available")
    with tempfile.TemporaryDirectory() as d:
        pred = Path(d) / "pred.jsonl"
        pred.write_text("".join(json.dumps(r) + "\n" for r in pred_rows))
        cmd = [sys.executable, "-m", "lifemate.scorer", str(pred), "--split", "train"]
        if ids is not None:
            (Path(d) / "ids.txt").write_text("\n".join(ids) + "\n")
            cmd += ["--ids", str(Path(d) / "ids.txt")]
        return subprocess.run(cmd, cwd=PKG_DIR, capture_output=True, text=True)


def _check_categories():
    from lifemate.data import load_split
    from lifemate.scorer import category
    S = {s["id"]: s for s in load_split("train")}
    assert category(S[EXECUTE_ID]["label"]["tool_calls"]) == "execute"
    assert category(S[OOS_ID]["label"]["tool_calls"]) == "out_of_scope"


def test_cli_missing_ids_score_zero():
    p = _cli([{"id": OOS_ID, "tool_calls": [], "state_hash": "x"}], [EXECUTE_ID, OOS_ID])
    assert p.returncode == 0, p.stderr
    _check_categories()
    res = json.loads(p.stdout)
    assert (res["n"], res["missing"], res["score"]) == (2, 1, 50.0)
    assert "no prediction" in p.stderr


def test_cli_all_missing_including_out_of_scope():
    p = _cli([], [EXECUTE_ID, OOS_ID])
    assert p.returncode == 0, p.stderr
    res = json.loads(p.stdout)
    assert (res["n"], res["missing"], res["score"]) == (2, 2, 0.0)


def test_cli_rejects_duplicate_ids():
    row = {"id": OOS_ID, "tool_calls": [], "state_hash": "x"}
    p = _cli([row, row], [OOS_ID])
    assert p.returncode != 0 and "more than once" in p.stderr


def test_cli_rejects_ids_outside_split():
    p = _cli([{"id": "train_9999", "tool_calls": [], "state_hash": "x"}], None)
    assert p.returncode != 0 and "not in split" in p.stderr
    p = _cli([], ["train_9999"])
    assert p.returncode != 0 and "not in split" in p.stderr


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        try:
            fn()
            print(f"ok    {name}")
        except Skip as e:
            print(f"skip  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {name}: {type(e).__name__}: {e}")
    sys.exit(1 if failed else 0)
