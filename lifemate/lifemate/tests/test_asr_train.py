"""Tests for the ASR fine-tuning data split and helpers (lifemate.asr_train). No GPU, no model download.

Run:  .venv/bin/python -m lifemate.tests.test_asr_train     (also works under pytest)
Tests that need the data are skipped when data/ is absent.
"""
from __future__ import annotations

import sys
from pathlib import Path

from lifemate.asr_train import make_collate, pairs_of, split_samples, utterances, wer
from lifemate.data import DEFAULT_ROOT, load_split
from lifemate.runinfo import read_ids
from lifemate.tests.test_scorer import PKG_DIR, Skip, _skip


def _sample(i, n_hist=1):
    hist = []
    for k in range(n_hist):
        hist += [{"role": "user", "audio": f"audio/s{i}/u{k}.wav", "audio_text": f"câu {i}.{k}"},
                 {"role": "assistant", "text": "ok"}]
    return {"id": f"s{i}", "audio": f"audio/s{i}/s{i}.wav", "audio_text": f"Câu cuối {i}.", "history": hist}


def test_utterances_final_then_user_history():
    s = _sample(1, n_hist=2)
    assert utterances(s) == [("audio/s1/s1.wav", "Câu cuối 1."), ("audio/s1/u0.wav", "câu 1.0"),
                             ("audio/s1/u1.wav", "câu 1.1")]


def test_split_excludes_and_is_deterministic():
    items = [_sample(i) for i in range(40)]
    excl = {"s3", "s7", "s11"}
    tr, va = split_samples(items, excl, 0.1, seed=0)
    tr2, va2 = split_samples(list(reversed(items)), excl, 0.1, seed=0)
    ids_tr, ids_va = {s["id"] for s in tr}, {s["id"] for s in va}
    assert not (ids_tr | ids_va) & excl
    assert not ids_tr & ids_va
    assert len(ids_tr) + len(ids_va) == 37 and len(ids_va) == 4
    assert [s["id"] for s in tr] == [s["id"] for s in tr2] and [s["id"] for s in va] == [s["id"] for s in va2]


def test_pairs_unique():
    s = _sample(1)
    assert len(pairs_of([s, s])) == 2


def test_wer_normalised_and_raw():
    assert wer(["Nhắn Sếp Dũng giờ mới."], ["nhắn sếp dũng giờ mới"]) == 0.0
    assert wer(["Nhắn Sếp Dũng giờ mới."], ["nhắn sếp dũng giờ mới"], raw=True) == 80.0
    assert wer(["a b c d"], ["a x c"]) == 50.0  # one substitution, one deletion


def test_collate_strips_start_and_pads():
    import numpy as np
    collate = make_collate(start_id=7)
    f = np.zeros((2, 3), dtype=np.float32)
    feats, lab = collate([(f, [7, 1, 2, 3]), (f, [4, 5])])
    assert tuple(feats.shape) == (2, 2, 3)
    assert lab.tolist() == [[1, 2, 3], [4, 5, -100]]


def test_real_split_never_trains_on_dev():
    if not (Path(DEFAULT_ROOT) / "train" / "train.jsonl").exists():
        _skip("train data not available")
    items = load_split("train")
    splits = PKG_DIR / "splits"
    excl = set(read_ids(splits / "dev_random.txt")) | set(read_ids(splits / "dev_lao.txt"))
    tr, va = split_samples(items, excl, 0.05, seed=0)
    dev_wavs = {p for s in items if s["id"] in excl for p, _ in utterances(s)}
    tr_wavs, va_wavs = {p for p, _ in pairs_of(tr)}, {p for p, _ in pairs_of(va)}
    assert not dev_wavs & tr_wavs and not dev_wavs & va_wavs and not tr_wavs & va_wavs
    assert len(tr) + len(va) + len(excl) == len(items)
    assert all(t.strip() for _, t in pairs_of(tr) + pairs_of(va))


def main():
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"ok    {name}")
        except Skip as e:
            print(f"skip  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {name}: {e!r}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
