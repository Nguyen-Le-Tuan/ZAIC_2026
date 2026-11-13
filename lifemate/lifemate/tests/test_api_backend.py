"""Tests for the hosted-API agent backend (lifemate.api_backend). CPU only, local fake server, no real API call.

Run:  .venv/bin/python -m lifemate.tests.test_api_backend     (also works under pytest)
"""
from __future__ import annotations

import http.server
import json
import os
import sys
import tempfile
import threading
from pathlib import Path

from lifemate import api_backend
from lifemate.api_backend import ChatAPIBackend, chatml_to_messages
from lifemate.prompt import render_calls, render_results, to_chatml
from lifemate.tests.test_scorer import Skip

MSGS = [
    {"role": "system", "content": "Quy tắc\n\n# Tools\n- a.b(x*: str)"},
    {"role": "user", "content": "đặt lịch 7 giờ"},
    {"role": "assistant", "content": render_calls([{"name": "a.b", "arguments": {"x": "1"}}])},
    {"role": "user", "content": render_results([{"ok": True, "result": {"id": "e_1"}}])},
    {"role": "user", "content": "nhiều dòng\nvẫn giữ nguyên"},
]


def test_chatml_round_trip():
    assert chatml_to_messages(to_chatml(MSGS)) == MSGS


def test_chatml_needs_generation_prompt():
    try:
        chatml_to_messages(to_chatml(MSGS, add_generation_prompt=False))
    except ValueError:
        return
    raise AssertionError("a prompt without the generation prompt must be refused")


class _Fake(http.server.BaseHTTPRequestHandler):
    bodies: list = []

    def do_POST(self):  # noqa: N802
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        type(self).bodies.append(body)
        out = json.dumps({"choices": [{"message": {"content": "<tool_call>\n{}\n</tool_call>"}, "finish_reason": "stop"}],
                          "usage": {"prompt_tokens": 1_000_000, "completion_tokens": 0}}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *a):
        pass


def _backend(tmp: Path, **kw):
    handler = type("H", (_Fake,), {"bodies": []})
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    os.environ.setdefault("META_API_KEY", "test-key-not-real")
    kw = {"max_usd": 10.0, "total_usd": 30.0, **kw}
    b = ChatAPIBackend("muse-spark-1.3", tmp / "gen" / "agent_t_usage.jsonl", tmp / "gen" / "agent_t_cache.jsonl",
                       base_url=f"http://127.0.0.1:{srv.server_address[1]}/v1", **kw)
    return b, handler, srv


def test_ledger_cache_and_request_body():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        b, h, srv = _backend(tmp)
        try:
            p = to_chatml(MSGS)
            assert b.generate(p).startswith("<tool_call>")
            assert b.generate(p).startswith("<tool_call>")  # second time from the cache: no request
            assert len(h.bodies) == 1 and h.bodies[0]["messages"] == MSGS
            assert h.bodies[0]["temperature"] == 0 and h.bodies[0]["reasoning_effort"] == "minimal"
            rows = [json.loads(x) for x in (tmp / "gen" / "agent_t_usage.jsonl").read_text().splitlines()]
            assert len(rows) == 1 and rows[0]["usd"] == 1.25  # 1M input tokens at 1.25 USD
            b2, h2, srv2 = _backend(tmp)  # a rerun reads the cache and the ledger back
            try:
                assert b2.generate(p).startswith("<tool_call>") and h2.bodies == [] and b2.run_usd == 1.25
            finally:
                srv2.shutdown()
        finally:
            srv.shutdown()


def test_caps_refuse_without_a_request():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        (tmp / "gen").mkdir()
        (tmp / "gen" / "synth_old_usage.jsonl").write_text(json.dumps({"usd": 29.5}) + "\n")
        b, h, srv = _backend(tmp)
        try:
            assert b.all_usd == 29.5
            assert b.generate(to_chatml(MSGS[:2])) != ""  # 29.5 < 30: allowed, costs 1.25
            assert b.generate(to_chatml(MSGS[:3] + MSGS[3:4])) == ""  # all ledgers now 30.75 >= 30: refused
            assert len(h.bodies) == 1 and b.stats["refused"] == 1
        finally:
            srv.shutdown()
        b, h, srv = _backend(tmp, max_usd=1.0, total_usd=100.0)
        try:
            assert b.generate(to_chatml(MSGS)) == "" and h.bodies == []  # this run's ledger already 1.25 >= 1.0
        finally:
            srv.shutdown()


def test_contributor_tier_refused():
    try:
        api_backend.ChatAPIBackend("muse-spark-1.3-contributor", "x", "y", 1.0)
    except SystemExit:
        return
    raise AssertionError("contributor-tier models must be refused")


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
