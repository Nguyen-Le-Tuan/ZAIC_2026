"""Unit tests for lifemate.agent.safe_args (R0-R3, JOURNAL entry 146). CPU only, synthetic schemas.

Run:  .venv/bin/python -m lifemate.tests.test_arg_rules        (also works under pytest)
"""
from __future__ import annotations

import sys

from lifemate.agent import safe_args

TOOLS = {
    "cal.create_event": {"kind": "write", "parameters": {
        "required": ["title", "start"],
        "properties": {"title": {"type": "string"},
                       "start": {"type": "string", "description": "Start time, ISO-8601 with offset"},
                       "end": {"type": "string", "format": "date-time"},
                       "note": {"type": "string"}}}},
    "alarm.set_daily": {"kind": "write", "parameters": {
        "required": ["time"],
        "properties": {"time": {"type": "string", "description": "HH:MM"},
                       "day": {"type": "string", "format": "date"}}}},
    "pay.transfer": {"kind": "write", "parameters": {
        "required": ["amount"], "x-one-of": [["contact_id", "phone"]],
        "properties": {"amount": {"type": "number"}, "contact_id": {"type": "string"}, "phone": {"type": "string"},
                       "memo": {"type": "string"}}}},
}
NOW = "2026-09-21T08:15:00+07:00"


def test_r0_drops_unknown_args():
    c = {"name": "cal.create_event", "arguments": {"title": "họp", "start": "2026-09-22T09:00:00+07:00", "foo": 1}}
    assert safe_args(c, TOOLS, NOW)["arguments"] == {"title": "họp", "start": "2026-09-22T09:00:00+07:00"}


def test_r1_iso_fill():
    c = {"name": "cal.create_event", "arguments": {"title": "a", "start": "9:30", "end": "2026-09-22T10:00"}}
    a = safe_args(c, TOOLS, NOW)["arguments"]
    assert a["start"] == "2026-09-21T09:30:00+07:00"
    assert a["end"] == "2026-09-22T10:00:00+07:00"
    c = {"name": "cal.create_event", "arguments": {"title": "a", "start": "2026-09-22T09:00:00"}}
    assert safe_args(c, TOOLS, NOW)["arguments"]["start"] == "2026-09-22T09:00:00+07:00"


def test_r2_full_iso_to_hhmm_and_date():
    c = {"name": "alarm.set_daily", "arguments": {"time": "2026-09-22T06:30:00+07:00", "day": "2026-09-22T00:00:00+07:00"}}
    assert safe_args(c, TOOLS, NOW)["arguments"] == {"time": "06:30", "day": "2026-09-22"}


def test_r3_ask_keeps_required_and_one_of_in_schema_order():
    c = {"name": "sys.ask_missing_info", "arguments": {"tool_name": "pay.transfer", "params": ["memo", "phone", "amount"]}}
    assert safe_args(c, TOOLS, NOW)["arguments"]["params"] == ["amount", "phone"]
    only_optional = {"name": "sys.ask_missing_info", "arguments": {"tool_name": "pay.transfer", "params": ["memo"]}}
    assert safe_args(only_optional, TOOLS, NOW) is only_optional  # nothing allowed would be left: keep as is


def test_unchanged_call_is_the_same_object():
    c = {"name": "cal.create_event", "arguments": {"title": "a", "start": "2026-09-22T09:00:00+07:00"}}
    assert safe_args(c, TOOLS, NOW) is c
    unknown_tool = {"name": "x.y", "arguments": {"a": 1}}
    assert safe_args(unknown_tool, TOOLS, NOW) is unknown_tool


def test_bad_current_time_skips_hhmm_fill():
    c = {"name": "cal.create_event", "arguments": {"title": "a", "start": "9:30"}}
    assert safe_args(c, TOOLS, None) is c


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        try:
            fn()
            print(f"ok    {name}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {name}: {type(e).__name__}: {e}")
    sys.exit(1 if failed else 0)
