"""Tests for the experiment-D generator (lifemate.counterfactual) and its SFT hook.

Run:  .venv/bin/python -m lifemate.tests.test_counterfactual     (also works under pytest)
Tests that need the train split are skipped when data/ is absent.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from lifemate.counterfactual import check_rewrite
from lifemate.data import DEFAULT_ROOT
from lifemate.tests.test_scorer import PKG_DIR, Skip, _skip

C_TASK = {"kind": "C", "text": "Nạp dùm em Linh 50 ngàn cho số của Linh nha.", "value": 50000}
BV_TASK = {"kind": "B-vague", "text": "Giữ giùm anh chiếc xe đạp chở hàng ở trạm Chợ Hôm nha.", "distinguishing_words": ["chở", "hàng"]}
BS_TASK = {"kind": "B-specific", "text": "Con xoá lẹ giùm cô cái nhắc đi chợ nghe.", "add_words": ["cồn", "giỗ"]}


def _need_data():
    if not (Path(DEFAULT_ROOT) / "train" / "train.jsonl").exists():
        _skip("train data not available")


# ------------------------------------------------------------------ text checks

def test_c_accepts_clean_removal():
    assert check_rewrite(C_TASK, {"new_text": "Nạp dùm em Linh cho số của Linh nha.", "removed_span": "50 ngàn"}) is None


def test_c_rejects_span_still_present():
    r = check_rewrite(C_TASK, {"new_text": "Nạp dùm em Linh 50 ngàn nha.", "removed_span": "50 ngàn"})
    assert r and "still in new text" in r


def test_c_rejects_value_in_another_form():
    r = check_rewrite(C_TASK, {"new_text": "Nạp dùm em Linh 50.000 cho số của Linh nha.", "removed_span": "50 ngàn"})
    assert r and "value still present" in r


def test_c_rejects_span_not_in_original():
    r = check_rewrite(C_TASK, {"new_text": "Nạp dùm em Linh cho số của Linh nha.", "removed_span": "năm chục"})
    assert r and "not in original" in r


def test_rejects_wholesale_rewrite():
    r = check_rewrite(C_TASK, {"new_text": "Em ơi nạp tiền điện thoại giúp chị với, chị cần gọi gấp lắm.", "removed_span": "50 ngàn"})
    assert r and "too different" in r


def test_b_vague_rejects_distinguishing_word_left():
    r = check_rewrite(BV_TASK, {"new_text": "Giữ giùm anh chiếc xe đạp hàng ở trạm Chợ Hôm nha.", "removed_span": "chở hàng"})
    assert r and "distinguishing" in r
    assert check_rewrite(BV_TASK, {"new_text": "Giữ giùm anh một chiếc xe đạp ở trạm Chợ Hôm nha.",
                                   "removed_span": "chở hàng"}) is None


def test_b_specific_needs_added_distinguishing_word():
    ok = {"new_text": "Con xoá lẹ giùm cô cái nhắc đi chợ Cồn mua đồ đám giỗ nghe.", "added_span": "Cồn mua đồ đám giỗ"}
    assert check_rewrite(BS_TASK, ok) is None
    r = check_rewrite(BS_TASK, {"new_text": "Con xoá lẹ giùm cô cái nhắc đi chợ sáng nghe.", "added_span": "sáng"})
    assert r and "no distinguishing word" in r


def test_unchanged_text_rejected():
    assert check_rewrite(C_TASK, {"new_text": C_TASK["text"], "removed_span": "50 ngàn"}) == "empty or unchanged text"


# ------------------------------------------------------------------ build on real fit samples

def _real_tasks():
    _need_data()
    from lifemate import counterfactual as cf
    from lifemate.data import catalog_tools, load_catalog, load_split
    import random
    S = {s["id"]: s for s in load_split("train")}
    tools = catalog_tools(load_catalog("train"))
    c = [t for t in cf.candidates_c(S["train_1364"], tools, {"time"}) if t["tool"] == "alarm.create"][0]
    b = cf.candidates_b_specific(S["train_1303"], tools, random.Random(0))
    assert b, "train_1303 should be a type-B ask over a reminder list"
    tc = {"task_id": "train_1364#C", "origin_id": "train_1364", **c, "text": S["train_1364"]["audio_text"]}
    tb = {"task_id": "train_1303#B-specific", "origin_id": "train_1303", **b[0], "text": S["train_1303"]["audio_text"]}
    words = " ".join(tb["add_words"][:1])
    rws = [{"task_id": tc["task_id"], "removed_span": "năm giờ rưỡi",
            "new_text": tc["text"].replace(" năm giờ rưỡi", "")},
           {"task_id": tb["task_id"], "added_span": words, "new_text": tb["text"].replace("đi chợ", f"đi chợ {words}")}]
    return cf, S, [tc, tb], rws


def test_build_replays_c_and_b_specific():
    cf, S, tasks, rws = _real_tasks()
    kept, report = cf.build(tasks, rws, S, {"train_1364", "train_1303"}, set(), set(), DEFAULT_ROOT)
    assert [r["kept"] for r in report] == [True, True], report
    by = {k["_kind"]: k for k in kept}
    assert by["C"]["label"]["tool_calls"][-1] == {"name": "sys.ask_missing_info",
                                                  "arguments": {"tool_name": "alarm.create", "params": ["time"]}}
    assert by["B-specific"]["label"]["tool_calls"][-1]["name"] == "reminders.delete"
    assert all(k["_src"] == "synthetic-D" and k["audio"] is None for k in kept)
    assert len(by["C"]["label"]["tool_results"]) == len(by["C"]["label"]["tool_calls"])


def test_build_refuses_dev_origin():
    cf, S, tasks, rws = _real_tasks()
    kept, report = cf.build(tasks, rws, S, {"train_1364", "train_1303"}, {"train_1364"}, set(), DEFAULT_ROOT)
    assert [r["kept"] for r in report] == [False, True]
    assert "excluded" in report[0]["reason"]


# ------------------------------------------------------------------ sft hook

def _sft(extra_rows, fit_ids):
    with tempfile.TemporaryDirectory() as d:
        extra, fit, out = Path(d) / "extra.jsonl", Path(d) / "fit.txt", Path(d) / "out.jsonl"
        extra.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in extra_rows))
        fit.write_text("\n".join(fit_ids) + "\n")
        p = subprocess.run([sys.executable, "-m", "lifemate.sft", "--fit", str(fit), "--extra-samples", str(extra),
                            "--out", str(out)], cwd=PKG_DIR, capture_output=True, text=True)
        rows = [json.loads(x) for x in out.read_text().splitlines()] if out.exists() else []
        return p, rows


def test_sft_extra_samples_rows_and_src():
    cf, S, tasks, rws = _real_tasks()
    kept, _ = cf.build(tasks, rws, S, {"train_1364", "train_1303"}, set(), set(), DEFAULT_ROOT)
    p, rows = _sft(kept, ["train_1364", "train_1303"])
    assert p.returncode == 0, p.stderr
    src = [r["src"] for r in rows]
    assert src.count("synthetic-D") >= 2 * 3 and src.count("gold") >= 2 * 3  # original + 2 renames each
    assert {r["id"] for r in rows if r["src"] == "synthetic-D"} == {k["id"] for k in kept}


def test_sft_rejects_extra_from_outside_fit():
    cf, S, tasks, rws = _real_tasks()
    kept, _ = cf.build(tasks, rws, S, {"train_1364", "train_1303"}, set(), set(), DEFAULT_ROOT)
    p, _ = _sft(kept, ["train_1364"])  # train_1303 is not in this fit
    assert p.returncode != 0 and "outside --fit" in p.stderr


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
