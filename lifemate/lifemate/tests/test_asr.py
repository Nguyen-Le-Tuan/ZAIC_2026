"""Tests for the ASR stage helpers (lifemate.asr), the ASR quality metrics and the submission checker. No GPU, no model.

Run:  .venv/bin/python -m lifemate.tests.test_asr     (also works under pytest)
Tests that need the data are skipped when data/ is absent.
"""
from __future__ import annotations

import json
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

from lifemate.asr import read_wav, wav_paths
from lifemate.data import DEFAULT_ROOT, load_split
from lifemate.tests.test_scorer import PKG_DIR, Skip, _skip

sys.path.insert(0, str(PKG_DIR / "scripts"))
import asr_quality as aq  # noqa: E402
import check_submission as cs  # noqa: E402


def _need_data():
    if not (Path(DEFAULT_ROOT) / "train" / "train.jsonl").exists():
        _skip("train data not available")


def _write_wav(path, x, rate=16000, channels=1):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((np.asarray(x) * 32767).astype("<i2").tobytes())


def test_wav_paths_final_then_history_unique():
    items = [{"audio": "audio/a/a.wav", "history": [{"role": "user", "audio": "audio/a/a_u1.wav"},
                                                    {"role": "assistant", "text": "ok"}]},
             {"audio": "audio/b/b.wav", "history": []},
             {"audio": "audio/a/a.wav", "history": []}]
    assert wav_paths(items) == ["audio/a/a.wav", "audio/a/a_u1.wav", "audio/b/b.wav"]


def test_read_wav_checks_format_and_length():
    with tempfile.TemporaryDirectory() as d:
        ok, stereo, slow, long = (Path(d) / n for n in ("ok.wav", "st.wav", "8k.wav", "long.wav"))
        _write_wav(ok, np.zeros(16000) + 0.5)
        _write_wav(stereo, np.zeros(32000), channels=2)
        _write_wav(slow, np.zeros(8000), rate=8000)
        _write_wav(long, np.zeros(16000 * 31))
        x = read_wav(ok)
        assert x.dtype == np.float32 and len(x) == 16000 and abs(float(x[0]) - 0.5) < 1e-3
        for bad in (stereo, slow, long):
            try:
                read_wav(bad)
            except ValueError:
                continue
            raise AssertionError(f"{bad.name} accepted")


def test_read_wav_refuses_environment_folder():
    try:
        read_wav("data/train/train_environment/train_0001/x.wav")
    except ValueError as e:
        assert "_environment" in str(e)
    else:
        raise AssertionError("environment path accepted")


def test_real_train_wavs_are_covered():
    _need_data()
    s = next(x for x in load_split("train") if any(h["role"] == "user" for h in x["history"]))
    paths = wav_paths([s])
    assert paths[0] == s["audio"] and len(paths) == 1 + sum(h["role"] == "user" for h in s["history"])
    x = read_wav(Path(DEFAULT_ROOT) / "train" / paths[0])
    assert 0.5 < len(x) / 16000 < 30


def test_wer_and_normalisation():
    assert aq.words("Hủy lịch, 9:30 nhé!") == aq.words("huỷ lịch 9 30 nhé")
    assert aq.edit_distance("a b c".split(), "a x c d".split()) == 2
    st = aq.turn_stats([("Mai mưa thì dời", "mai mưa thì dời"), ("bật đèn", "bật đen")])
    assert st["wer"] == round(100 * 1 / 6, 2) and st["wer_noacc"] == 0.0 and st["exact"] == 50.0


def test_slot_kept_counts_digits_and_words_alike():
    tools = {"ewallet.transfer": {"kind": "write"}, "contacts.search": {"kind": "read"}}
    s = {"id": "x", "audio_text": "chuyển cho Linh năm mươi nghìn, đừng gửi tin nhắn",
         "label": {"tool_calls": [{"name": "contacts.search", "arguments": {"query": "Linh"}},
                                  {"name": "ewallet.transfer", "arguments": {"contact_id": "c_1", "amount": 50000}}]}}
    for hyp, kept in (("Chuyển cho Lình 50.000đ, đừng gửi tin nhắn.", 1), ("chuyển cho linh 15 nghìn", 0)):
        c, misses = aq.Counter(), []
        aq.label_checks(s, hyp, tools, c, misses)
        assert c["slot amount n"] == 1 and c["slot amount kept"] == kept, (hyp, c)
        assert c["query n"] == 1 and c["query kept"] == 1
        assert c["negation n"] == 1 and c["negation kept"] == kept, (hyp, c)
        assert len(misses) == 1 - kept


def test_submission_structure_errors():
    h = "0" * 64
    good = [{"id": "a", "tool_calls": [{"name": "x.y", "arguments": {}}], "state_hash": h},
            {"id": "b", "tool_calls": [], "state_hash": h}]
    assert cs.structure_errors(good, ["a", "b"]) == []
    bad = [{"id": "a", "tool_calls": [{"name": "x.y"}], "state_hash": h},
           {"id": "a", "tool_calls": [], "state_hash": "zz"},
           {"id": "c", "tool_calls": [], "state_hash": h, "extra": 1}]
    errs = " | ".join(cs.structure_errors(bad, ["a", "b"]))
    for frag in ("a: bad tool_calls", "bad state_hash", "keys", "duplicate ids", "ids missing", "not in the split"):
        assert frag in errs, (frag, errs)


def test_zaic_tools_validate_on_sample_submission():
    root = Path(DEFAULT_ROOT)
    sample = root / "public_test" / "sample_submission.jsonl"
    if not sample.exists():
        _skip("public_test not available")
    r = cs.schema_check(str(sample), "public_test", str(root))
    assert r["returncode"] == 0 and r["lines"] == 3 and r["schema_errors"] == 0, r
    rows = [json.loads(line) for line in sample.read_text().splitlines() if line.strip()]
    assert cs.structure_errors(rows, [x["id"] for x in rows]) == []


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
