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

from lifemate.asr import decode_passes, final_paths, read_wav, transcribe, wav_paths
from lifemate.data import DEFAULT_ROOT, load_split
from lifemate.tests.test_scorer import PKG_DIR, Skip, _skip

sys.path.insert(0, str(PKG_DIR / "scripts"))
import asr_beam_final as abf  # noqa: E402
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


class RecordingASR:
    """Stands in for Whisper: records each call's wav lengths and beams; text = the wav's sample count."""

    def __init__(self):
        self.calls = []  # (lengths of the batch, num_beams, whether num_beams was passed at all)

    def __call__(self, audios, **kw):
        self.calls.append(([len(a) for a in audios], kw.get("num_beams", 1), "num_beams" in kw))
        return [f"len {len(a)}" for a in audios]


# two samples: a (final + 2 user history turns) and b (final only); lengths chosen so length order mixes the turns
TURNS = {"audio/a/a.wav": 5000, "audio/a/a_u1.wav": 3000, "audio/a/a_u2.wav": 9000, "audio/b/b.wav": 4000}
ITEMS = [{"audio": "audio/a/a.wav", "history": [{"role": "user", "audio": "audio/a/a_u1.wav"},
                                                {"role": "assistant", "text": "ok"},
                                                {"role": "user", "audio": "audio/a/a_u2.wav"}]},
         {"audio": "audio/b/b.wav", "history": []}]


def _turn_wavs(d: Path) -> Path:
    for p, n in TURNS.items():
        (d / p).parent.mkdir(parents=True, exist_ok=True)
        _write_wav(d / p, np.zeros(n) + 0.1)
    return d


def test_final_paths_are_each_samples_own_audio():
    assert final_paths(ITEMS) == {"audio/a/a.wav", "audio/b/b.wav"}
    assert final_paths([]) == set()
    paths = wav_paths(ITEMS)
    assert [p for p in paths if p not in final_paths(ITEMS)] == ["audio/a/a_u1.wav", "audio/a/a_u2.wav"]


def test_decode_passes_split_by_mode():
    paths, final = wav_paths(ITEMS), final_paths(ITEMS)
    assert decode_passes(paths, 8) == [(1, paths, 8)]  # beams 1: one greedy pass over every wav
    assert decode_passes(paths, 8, beams=1, final=final) == [(1, paths, 8)]
    assert decode_passes(paths, 8, beams=4, final=final) == [
        (1, ["audio/a/a_u1.wav", "audio/a/a_u2.wav"], 8), (4, ["audio/a/a.wav", "audio/b/b.wav"], 2)]
    assert decode_passes(paths, 1, beams=4, final=final)[1] == (4, ["audio/a/a.wav", "audio/b/b.wav"], 1)
    for bad in ({"beams": 0, "final": final}, {"beams": 4}):  # beams > 1 must be told which wavs are final turns
        try:
            decode_passes(paths, 8, **bad)
        except ValueError:
            continue
        raise AssertionError(f"decode_passes accepted {bad}")


def test_transcribe_beams_on_final_turns_only():
    with tempfile.TemporaryDirectory() as d:
        root, paths, final = _turn_wavs(Path(d)), wav_paths(ITEMS), final_paths(ITEMS)
        asr = RecordingASR()
        rows = transcribe(asr, root, paths, batch_size=8, beams=4, final=final)
        assert [r["audio"] for r in rows] == paths  # rows in the order of paths, whatever the decode order
        assert all(set(r) == {"audio", "text", "seconds", "audio_s"} for r in rows)
        assert [r["text"] for r in rows] == [f"len {TURNS[p]}" for p in paths]
        # history turns: one greedy batch, plain asr(batch); final turns: 8 // 4 = 2 per batch, all with 4 beams
        assert asr.calls == [([3000, 9000], 1, False), ([4000, 5000], 4, True)]
        asr = RecordingASR()
        transcribe(asr, root, paths, batch_size=1, beams=4, final=final)
        assert asr.calls == [([3000], 1, False), ([9000], 1, False), ([4000], 4, True), ([5000], 4, True)]


def test_transcribe_beams_1_is_the_greedy_run():
    """beams = 1 decodes as before the option: every wav in one length-sorted pass, asr(batch) without num_beams."""
    with tempfile.TemporaryDirectory() as d:
        root, paths = _turn_wavs(Path(d)), wav_paths(ITEMS)
        for kw in ({}, {"beams": 1, "final": final_paths(ITEMS)}):
            asr = RecordingASR()
            rows = transcribe(asr, root, paths, batch_size=3, **kw)
            assert asr.calls == [([3000, 4000, 5000], 1, False), ([9000], 1, False)]
            assert [r["audio"] for r in rows] == paths


def test_beam_final_merge_replaces_final_rows_only():
    """scripts/asr_beam_final.py: the greedy file's rows and order; only the final turns take the beam rows."""
    paths, final = wav_paths(ITEMS), final_paths(ITEMS)
    greedy = [{"audio": p, "text": "g", "seconds": 0.1, "audio_s": 1.0} for p in paths]
    beam = [{"audio": p, "text": "b", "seconds": 0.3, "audio_s": 1.0} for p in sorted(final)]
    out = abf.merge(greedy, beam)
    assert [r["audio"] for r in out] == paths
    assert [r["text"] for r in out] == ["b" if p in final else "g" for p in paths]
    assert all(r is greedy[i] for i, r in enumerate(out) if r["audio"] not in final)  # history rows copied as is
    try:
        abf.merge(greedy, [{**beam[0], "beams": 4}])
    except ValueError:
        pass
    else:
        raise AssertionError("a beam row with other keys than the greedy rows was accepted")


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


def test_real_final_turns_are_the_samples_audio():
    """In train, each sample's `audio` is its own wav, never a history turn of any sample: the beam pass of a run
    decodes exactly one wav per sample."""
    _need_data()
    items = load_split("train")
    final = final_paths(items)
    hist = {h["audio"] for s in items for h in s["history"] if h["role"] == "user"}
    assert len(final) == len(items) and not final & hist
    s = next(x for x in items if any(h["role"] == "user" for h in x["history"]))
    passes = decode_passes(wav_paths([s]), 1, beams=4, final=final_paths([s]))
    assert passes[1][1] == [s["audio"]] and s["audio"] not in passes[0][1]
    assert sorted(passes[0][1]) == sorted(h["audio"] for h in s["history"] if h["role"] == "user")


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
