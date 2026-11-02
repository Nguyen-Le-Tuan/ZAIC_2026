"""Tests for the synthetic-sample checks (lifemate.synth); no API call is made.

Run:  .venv/bin/python -m lifemate.tests.test_synth     (also works under pytest)
Tests need the train catalog and its zaic_tools; they are skipped when data/ is absent.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

from lifemate.data import DEFAULT_ROOT
from lifemate.tests.test_scorer import Skip, _skip

ASK = "sys.ask_missing_info"
CTX = {"current_time": "2026-11-05T09:00:00+07:00", "timezone": "Asia/Ho_Chi_Minh", "location": {"lat": 10.77, "lng": 106.7},
       "user_profile": {"name": "Anh Minh", "home_address": "12 Lê Lợi, Quận 1", "work_address": "Quận 3", "city": "TP.HCM"},
       "installed_apps": {"library": {"tools": ["library.search", "library.reserve"]},
                          "notes": {"tools": ["notes.create", "notes.search"]}}}
STATE = {"library": {"books": [
    {"id": "book_01", "title": "Dế Mèn phiêu lưu ký", "author": "Tô Hoài", "available": True},
    {"id": "book_02", "title": "Tắt đèn", "author": "Ngô Tất Tố", "available": False},
    {"id": "book_03", "title": "Vợ chồng A Phủ", "author": "Tô Hoài", "available": True}], "reservations": []}}
SEARCH = {"name": "library.search", "arguments": {"query": "Dế Mèn"}}
RESERVE1 = {"name": "library.reserve", "arguments": {"book_id": "book_01"}}


def _env():
    if not (Path(DEFAULT_ROOT) / "train" / "train_tools_catalog.json").exists():
        _skip("train data not available")
    from lifemate.data import catalog_tools, load_catalog, zaic_tools
    cat = load_catalog("train")
    return zaic_tools("train"), catalog_tools(cat), cat


def _g(calls, category="execute", request="Giữ giùm anh cuốn Dế Mèn phiêu lưu ký nha", state=STATE):
    return {"id": "t", "app": "library", "context": copy.deepcopy(CTX), "state": copy.deepcopy(state),
            "calls": calls, "category": category, "request": request}


def _check(g):
    from lifemate.synth import check_sample
    zt, tools, cat = _env()
    return check_sample(zt, g, tools, cat)


def test_execute_read_then_write_passes():
    reason, results = _check(_g([SEARCH, RESERVE1]))
    assert reason is None, reason
    assert results[1]["reservation"]["book_id"] == "book_01"


def test_invented_id_rejected():
    reason, _ = _check(_g([RESERVE1]))
    assert reason and reason.startswith("invented_id"), reason


def test_noop_rejected():
    reason, _ = _check(_g([SEARCH, {"name": "library.reserve", "arguments": {"book_id": "book_99"}}]))
    assert reason and reason.startswith("noop"), reason


def test_schema_error_rejected():
    reason, _ = _check(_g([SEARCH, {"name": "library.reserve", "arguments": {}}]))
    assert reason and reason.startswith("schema"), reason


def test_tool_not_installed_rejected():
    reason, _ = _check(_g([{"name": "sms.send", "arguments": {"contact_id": "c_01", "content": "hi"}}]))
    assert reason and reason.startswith("schema") and "not installed" in reason, reason


def test_id_in_request_rejected():
    reason, _ = _check(_g([SEARCH, RESERVE1], request="giữ sách book_01 giùm anh"))
    assert reason and reason.startswith("id_in_text"), reason


def test_execute_without_write_rejected():
    reason, _ = _check(_g([SEARCH]))
    assert reason == "no_write", reason


def test_ask_after_read_passes():
    ask = {"name": ASK, "arguments": {"tool_name": "library.reserve", "params": ["book_id"]}}
    reason, _ = _check(_g([{"name": "library.search", "arguments": {"query": "Tô Hoài"}}, ask], "ask_missing",
                          "Giữ giùm anh một cuốn của Tô Hoài nha"))
    assert reason is None, reason


def test_ask_for_optional_param_rejected():
    ask = {"name": ASK, "arguments": {"tool_name": "library.search", "params": ["query"]}}
    reason, _ = _check(_g([ask], "ask_missing", "Tìm sách giùm anh"))
    assert reason and reason.startswith("bad_ask") and "not required" in reason, reason


def test_ask_about_a_tool_already_called_rejected():
    ask = {"name": ASK, "arguments": {"tool_name": "library.reserve", "params": ["book_id"]}}
    reason, _ = _check(_g([SEARCH, RESERVE1, ask], "ask_missing"))
    assert reason and reason.startswith("bad_ask") and "already called" in reason, reason


def test_write_for_another_part_then_ask_passes():
    """Gold does the parts it can (a note), then asks about the rest (which book)."""
    note = {"name": "notes.create", "arguments": {"title": "Đọc sách", "content": "đọc sách tối nay"}}
    ask = {"name": ASK, "arguments": {"tool_name": "library.reserve", "params": ["book_id"]}}
    reason, _ = _check(_g([note, {"name": "library.search", "arguments": {"query": "Tô Hoài"}}, ask], "ask_missing",
                          "Ghi chú tối nay đọc sách, rồi giữ giùm anh một cuốn của Tô Hoài"))
    assert reason is None, reason


def test_state_for_app_not_installed_rejected():
    state = {**STATE, "contacts": {"contacts": []}}
    reason, _ = _check(_g([SEARCH, RESERVE1], state=state))
    assert reason and reason.startswith("state_not_installed"), reason


def test_lookup_read_only_passes():
    reason, _ = _check(_g([{"name": "library.search", "arguments": {"query": "Tô Hoài"}}], "lookup",
                          "Thư viện còn sách nào của Tô Hoài không em"))
    assert reason is None, reason


def test_lookup_with_write_rejected():
    reason, _ = _check(_g([SEARCH, RESERVE1], "lookup"))
    assert reason and reason.startswith("bad_lookup"), reason


def test_parse_args_tolerates_stray_braces_only():
    from lifemate.synth import parse_args
    assert parse_args('{"query": "Tô Hoài"}}') == {"query": "Tô Hoài"}
    assert parse_args("{} }") == {}
    assert parse_args("  ") == {}
    for bad in ('{"a": 1} {"b": 2}', '[1, 2]', '{"a": 1} trailing'):
        try:
            parse_args(bad)
        except ValueError:
            continue
        raise AssertionError(f"accepted {bad!r}")


def test_budget_caps_refuse_before_any_request():
    import json
    import os
    import tempfile
    from lifemate.synth import BudgetExceeded, Client
    old = os.environ.get("META_API_KEY")
    os.environ["META_API_KEY"] = "test-key-not-real"
    try:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "synth_a_usage.jsonl").write_text(json.dumps({"usd": 0.6}) + "\n")
            (d / "synth_b_usage.jsonl").write_text(json.dumps({"usd": 0.5}) + "\n")
            # the tag is under its own cap, but all tags together reached the total cap
            c = Client("muse-spark-1.3", "http://127.0.0.1:9/v1", d / "synth_new_usage.jsonl", max_usd=5, total_usd=1.0)
            try:
                c.chat([{"role": "user", "content": "x"}], {"type": "object"}, "x")
                raise AssertionError("no BudgetExceeded")
            except BudgetExceeded as e:
                assert "all tags" in str(e)
            c = Client("muse-spark-1.3", "http://127.0.0.1:9/v1", d / "synth_a_usage.jsonl", max_usd=0.5, total_usd=10)
            try:
                c.chat([{"role": "user", "content": "x"}], {"type": "object"}, "x")
                raise AssertionError("no BudgetExceeded")
            except BudgetExceeded as e:
                assert "tag spent" in str(e)
    finally:
        if old is None:
            os.environ.pop("META_API_KEY", None)
        else:
            os.environ["META_API_KEY"] = old


def test_contributor_tier_refused():
    import os
    from lifemate.synth import Client
    os.environ.setdefault("META_API_KEY", "test-key-not-real")
    try:
        Client("muse-spark-1.3-contributor", "http://127.0.0.1:9/v1", Path("/nonexistent/x.jsonl"), 1)
    except SystemExit as e:
        assert "contributor" in str(e)
        return
    raise AssertionError("contributor tier accepted")


def test_solver_agreement():
    from lifemate.synth import solver_agrees
    zt, tools, cat = _env()
    g = _g([SEARCH, RESERVE1])
    assert solver_agrees(zt, g, [RESERVE1], tools, cat) is None  # same write and final state; reads may differ
    other = [SEARCH, {"name": "library.reserve", "arguments": {"book_id": "book_03"}}]
    assert solver_agrees(zt, g, other, tools, cat) == "solver: other final state"
    r = solver_agrees(zt, g, [SEARCH], tools, cat)
    assert r and r.startswith("solver: other writes"), r


def test_sft_rows_from_accepted_sample():
    from lifemate.data import load_catalog
    from lifemate.sft import build_all
    from lifemate.synth import to_train_sample
    zt, tools, cat = _env()
    g = _g([SEARCH, RESERVE1])
    reason, results = _check(g)
    assert reason is None
    s = to_train_sample(g, results)
    apps = {x["id"]: x for x in cat["apps"]}
    pool = {x["id"]: x for x in load_catalog("public_test")["apps"]} | apps
    rows = build_all([s], tools, apps, pool, rename=2, p_remove=0.0, p_distract=0.0, p_lower=0.0, seed=0)
    assert len(rows) == 3 and all(r["src"] == "synthetic-api" for r in rows)
    text = "".join(t for t, _ in rows[0]["segments"])
    assert "Dế Mèn phiêu lưu ký" in text and "library.reserve" in text and "book_01" in text
    assert any(loss for _, loss in rows[0]["segments"])


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
