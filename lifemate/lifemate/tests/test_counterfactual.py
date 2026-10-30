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


# ------------------------------------------------------------------ remedies of the 30/10 review

def test_vinum_spoken_forms():
    from lifemate.vinum import find_form, value_forms
    cases = [("nạp 50 ngàn nha", 50000), ("trích 2tr cho Tuấn", 2000000), ("nạp hai trăm ngàn", 200000),
             ("năm chục nghìn thôi", 50000), ("báo thức 5 rưỡi sáng", "2026-12-18T05:30:00+07:00"),
             ("6h chiều hôm trước", "2026-10-08T18:00:00+07:00"), ("cứ 7 rưỡi tối", "19:30"),
             ("sáu giờ kém mười lăm", "17:45")]
    for text, v in cases:
        assert find_form(text, value_forms(v)), (text, v)
    assert find_form("qua số 18 phố Trúc Bạch", value_forms("2026-10-08T18:00:00+07:00")) is None
    assert find_form("thêm ngàn rưỡi thôi", value_forms(9500)) is None


def test_c_rejects_spoken_value_leaks():
    for new in ("Nạp dùm em Linh 50 ngàn cho số của Linh nha.", "Nạp dùm em Linh năm chục nghìn cho số của Linh nha."):
        r = check_rewrite(C_TASK, {"new_text": new, "removed_span": "50 ngàn" if "50 ngàn" not in new else "xx"})
        assert r, new
    task = {"kind": "C", "text": "soạn thư nháp gửi family a còng example chấm test nhé", "value": ["family@example.test"]}
    r = check_rewrite(task, {"new_text": "soạn thư nháp gửi hộp thư family nhé", "removed_span": "family a còng example chấm test"})
    assert r and "family" in r


def test_c_prefilter():
    from lifemate.counterfactual import c_filter_reason
    tools = {"alarm.create": {"parameters": {"properties": {"time": {"type": "string"}}}},
             "tv.control": {"parameters": {"properties": {"action": {"type": "string", "enum": ["off", "mute"]}}}}}
    s = {"audio_text": "Đặt báo thức năm giờ rưỡi sáng mai giúp anh với nha", "history": []}
    assert c_filter_reason(s, {"tool": "alarm.create", "param": "time", "value": "2026-12-18T05:30:00+07:00"}, tools) is None
    computed = {"audio_text": "Đặt báo thức trước giờ họp hai tiếng giúp anh nha", "history": []}
    assert "not spoken" in c_filter_reason(computed, {"tool": "alarm.create", "param": "time", "value": "2026-12-18T05:30:00+07:00"}, tools)
    answer = {"audio_text": "Năm giờ rưỡi em nhé.", "history": [{"role": "user", "audio_text": "..."}]}
    assert "answer" in c_filter_reason(answer, {"tool": "alarm.create", "param": "time", "value": "05:30"}, tools)
    enum = {"audio_text": "Tắt tiếng tivi giùm mình xíu nha, sắp họp rồi", "history": []}
    assert c_filter_reason(enum, {"tool": "tv.control", "param": "action", "value": "mute"}, tools)


def _v2(text, task, calls, history=()):
    from lifemate.counterfactual import filter_v2_reason
    s = {"audio_text": text, "history": [{"role": "user", "audio_text": h} for h in history],
         "label": {"tool_calls": calls}}
    return filter_v2_reason(s, task, {})


def test_filter_v2_c_rules():
    t19 = "2026-11-25T19:00:00+07:00"
    lesson = [{"name": "learning.schedule_lesson", "arguments": {"course_id": "c1", "time": t19}}]
    task = {"kind": "C", "write_index": 0, "tool": "learning.schedule_lesson", "param": "time", "value": t19}
    assert _v2("Xếp buổi học lúc bảy giờ tối mai nghe em.", task, lesson) is None
    assert "if/else" in _v2("Mai Huế mưa thì xếp bảy giờ tối, không thì chín giờ.", task, lesson)
    goal = [{"name": "fitness.set_goal", "arguments": {"steps": 6000}}]
    gt = {"kind": "C", "write_index": 0, "tool": "fitness.set_goal", "param": "steps", "value": 6000}
    assert "twice" in _v2("Hôm qua đi chưa tới sáu ngàn bước thì hạ mục tiêu còn sáu ngàn nghen.", gt, goal)
    # one spoken amount matched by overlapping forms ("một trăm hai mươi nghìn" / "một trăm hai mươi") counts once
    pay = [{"name": "ewallet.transfer", "arguments": {"to": "Hòa", "amount": 120000}}]
    pt = {"kind": "C", "write_index": 0, "tool": "ewallet.transfer", "param": "amount", "value": 120000}
    assert _v2("Chuyển cho Hòa một trăm hai mươi nghìn qua ví giúp anh cái.", pt, pay) is None
    t14 = "2026-10-02T14:00:00+07:00"
    two = [{"name": "chat_ott.send_message", "arguments": {"chat_id": "chat_01", "content": "Ca mới bắt đầu lúc 14 giờ"}},
           {"name": "calendar.create_event", "arguments": {"title": "Bàn giao ca", "start": t14}}]
    ct = {"kind": "C", "write_index": 1, "tool": "calendar.create_event", "param": "start", "value": t14}
    assert "another call" in _v2("Nhắn chị Lan là ca mới bắt đầu lúc hai giờ chiều mai, rồi tạo lịch vào giờ đó.", ct, two)
    ride = [{"name": "ride_hailing.book", "arguments": {"pickup": "nhà", "dropoff": "Nhà thủ công Bờ Sông"}}]
    rt = {"kind": "C", "write_index": 0, "tool": "ride_hailing.book", "param": "dropoff", "value": "Nhà thủ công Bờ Sông"}
    assert "dialogue" in _v2("Ừ thì gọi cho anh cái ô tô từ nhà qua đấy luôn.", rt, ride, ["Tìm mấy tiệm đồ thủ công gần bờ sông"])


def test_filter_v2_b_vague_rules():
    ents = [{"id": "ben_01", "name": "Nguyễn Thị Lan"}, {"id": "ben_02", "name": "Lê Minh"}]
    lst = {"name": "banking.list_beneficiaries", "arguments": {}}
    tr = lambda b: {"name": "banking.transfer", "arguments": {"beneficiary_id": b, "amount": 100000}}  # noqa: E731
    task = {"kind": "B-vague", "write_index": 1, "tool": "banking.transfer", "param": "beneficiary_id", "value": "ben_01",
            "entities": ents, "distinguishing_words": ["lan", "nguyễn", "thị"]}
    assert _v2("Chuyển cho Nguyễn Thị Lan một trăm nghìn nha.", task, [lst, tr("ben_01")]) is None
    assert "more than once" in _v2("Chuyển Nguyễn Thị Lan một trăm, Lê Minh một trăm nha.", task, [lst, tr("ben_01"), tr("ben_02")])
    assert "weak" in _v2("Chuyển cho anh một trăm nghìn nha.", {**task, "distinguishing_words": ["anh"]}, [lst, tr("ben_01")])
    search = {"name": "banking.list_beneficiaries", "arguments": {"query": "Lan"}}
    assert "earlier call" in _v2("Chuyển cho Nguyễn Thị Lan một trăm nghìn nha.", task, [search, tr("ben_01")])
    assert "history" in _v2("Chuyển cho Nguyễn Thị Lan một trăm nghìn nha.", task, [lst, tr("ben_01")], ["Lan nhắn gì đó em?"])
    assert "self-correction" in _v2("Chuyển cho Minh, à không, cho Nguyễn Thị Lan một trăm nghìn nha.", task, [lst, tr("ben_01")])
    assert "condition" in _v2("Chuyển cho Nguyễn Thị Lan nếu ví đủ, không thì Lê Minh nha.", task, [lst, tr("ben_01")])


def test_label_leak():
    from lifemate.counterfactual import label_leak
    task = {"text": "Ờ, bài giá xăng sắp giảm ba trăm đồng ấy, em lưu lại."}
    label = [{"name": "news.search", "arguments": {"query": "giá xăng"}},
             {"name": "sys.ask_missing_info", "arguments": {"tool_name": "news.save", "params": ["article_id"]}}]
    assert "xăng" in label_leak(task, "Ờ, bài báo ấy em lưu lại.", label)
    assert label_leak(task, "Ờ, bài giá xăng ấy em lưu lại.", label) is None


def test_judge_reason_rules():
    from lifemate.counterfactual import judge_reason, judge_tasks
    c = {"kind": "C"}
    assert judge_reason(c, {"slot_given": False}) is None
    assert "still given" in judge_reason(c, {"slot_given": True})
    assert "no judgment" in judge_reason(c, None)
    bv = {"kind": "B-vague", "value": "bike_7"}
    assert judge_reason(bv, {"matches": ["bike_7", "bike_8"]}) is None
    assert "singles out" in judge_reason(bv, {"matches": ["bike_7"]})
    assert "no longer fits" in judge_reason(bv, {"matches": ["bike_8", "bike_9"]})
    bs = {"kind": "B-specific", "value": "rem_1"}
    assert judge_reason(bs, {"matches": ["rem_1"]}) is None
    assert judge_reason(bs, {"matches": ["rem_1", "rem_2"]})
    # the judge never sees the original request or the target
    t = {"task_id": "x#B-vague", "kind": "B-vague", "text": "ORIGINAL", "value": "bike_7",
         "entities": [{"id": "bike_7", "name": "a"}, {"id": "bike_8", "name": "b"}]}
    jt = judge_tasks([t], [{"task_id": "x#B-vague", "new_text": "NEW"}])[0]
    assert "ORIGINAL" not in json.dumps(jt, ensure_ascii=False) and "value" not in jt


def test_split_by_origin_is_stable_and_disjoint():
    from lifemate.counterfactual import split_by_origin
    xs = [{"_origin": f"train_{i:04d}", "id": f"train_{i:04d}#d1"} for i in range(200)]
    tr, ev = split_by_origin(xs, 0.2)
    tr2, ev2 = split_by_origin(list(reversed(xs)), 0.2)
    assert {x["id"] for x in ev} == {x["id"] for x in ev2} and not ({x["_origin"] for x in tr} & {x["_origin"] for x in ev})
    assert 20 <= len(ev) <= 60


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


def test_make_tasks_filter_v2_and_dedup():
    _need_data()
    import difflib
    from collections import Counter
    from lifemate import counterfactual as cf
    from lifemate.askpolicy import attested_plain_params, norm
    from lifemate.data import catalog_tools, load_catalog, load_split
    from lifemate.runinfo import read_ids
    S = {s["id"]: s for s in load_split("train")}
    tools = catalog_tools(load_catalog("train"))
    fit = [S[i] for i in sorted(read_ids(PKG_DIR / "splits" / "fit_lao.txt"))][:600]
    att = attested_plain_params(fit, tools)
    stats = Counter()
    tasks = cf.make_tasks(fit, tools, att, 100, 100, 0, 3, max_per_tool=16, filter_v2=True, dedup=0.75, stats=stats)
    assert tasks and stats
    for t in tasks:
        assert cf.filter_v2_reason(S[t["origin_id"]], t, tools) is None
    for a in tasks:
        for b in tasks:
            if a is not b and (a["kind"], a["tool"]) == (b["kind"], b["tool"]):
                assert difflib.SequenceMatcher(None, norm(a["text"]), norm(b["text"])).ratio() < 0.75
    # without the new options the selection is unchanged (v1 reproducibility)
    plain = cf.make_tasks(fit, tools, att, 100, 100, 0, 3, max_per_tool=16)
    assert plain == cf.make_tasks(fit, tools, att, 100, 100, 0, 3, max_per_tool=16, filter_v2=False, dedup=None)


def test_build_rejects_label_leak():
    cf, S, tasks, rws = _real_tasks()
    task = dict(tasks[0], text=tasks[0]["text"] + " xăng")
    calls = S["train_1364"]["label"]["tool_calls"]
    s = dict(S["train_1364"], label=dict(S["train_1364"]["label"],
                                         tool_calls=[{"name": "news.search", "arguments": {"query": "xăng"}}] + calls))
    task["write_index"] += 1
    kept, report = cf.build([task], rws[:1], {**S, "train_1364": s}, {"train_1364"}, set(), set(), DEFAULT_ROOT)
    assert not kept and "removed" in report[0]["reason"]


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
