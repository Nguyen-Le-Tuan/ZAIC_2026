"""Tests for the Docker submission interface: lifemate.submit, lifemate.seeding, the `time` field (lifemate.infer,
scripts/check_submission.py) and docker/{predict.sh,start_jupyter.sh,predict_notebook.ipynb}. CPU only, no model:
the ASR and LLM are fakes, and scripts/predict.sh is replaced by a fake where the wrapper's own logic is tested.

Run:  .venv/bin/python -m lifemate.tests.test_submit     (also works under pytest)
Tests that need the train split are skipped when data/ is absent.
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from lifemate.agent import HFBackend, OracleBackend
from lifemate.asr import read_wav
from lifemate.data import DEFAULT_ROOT, load_jsonl, load_split, zaic_tools
from lifemate.seeding import seed_everything
from lifemate.submit import DEFAULTS, MAX_TOKENS, Runner, find_split, model_path, report, sample_wavs, settings
from lifemate.tests.test_scorer import Skip, _skip  # noqa: F401  (Skip is used by the __main__ runner)

PKG_DIR = Path(__file__).resolve().parents[2]  # lifemate/ (package, scripts/, docker/)
DOCKER = PKG_DIR / "docker"
HASH = re.compile(r"^[0-9a-f]{64}$")
IDS = ["train_0003", "train_0019", "train_0069"]  # execute, out of scope, user history + 4 gold calls


def _need_train():
    if not (Path(DEFAULT_ROOT) / "train" / "train.jsonl").exists():
        _skip("train data not available")


def _items(ids=IDS):
    by_id = {s["id"]: s for s in load_split("train")}
    return [by_id[i] for i in ids]


def _fake_data_root(d: Path, *splits: str) -> Path:
    for s in splits:
        (d / s).mkdir(parents=True)
        (d / s / f"{s}_tools_catalog.json").write_text("{}")
    return d


def _check_module():
    spec = importlib.util.spec_from_file_location("check_submission", PKG_DIR / "scripts" / "check_submission.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeASR:
    """Text = the wav's sample count, so a test can tell which wav was transcribed."""

    def __init__(self, *args, sleep: float = 0.0, **kw):
        self.sleep, self.calls, self.warmups = sleep, 0, 0

    def __call__(self, audios):
        self.calls += len(audios)
        time.sleep(self.sleep)
        return [f"len {len(a)}" for a in audios]

    def warmup(self):
        self.warmups += 1


class FakeLLM:
    """Answers without any call (the loop stops after one step)."""

    def __init__(self, *args, **kw):
        self.warmups = []

    def generate(self, prompt, deadline=None):
        return "Xong."

    def warmup(self, prompt, max_new_tokens=16):
        self.warmups.append(prompt)


# ------------------------------------------------------------------ settings shared by predict.sh and the notebook

def test_find_split_rules():
    with tempfile.TemporaryDirectory() as d:
        root = _fake_data_root(Path(d), "private_test")
        (root / "notes").mkdir()  # a folder without its catalog is not a split
        (root / "public_test").mkdir()  # nor is one whose catalog is missing
        assert find_split(root) == "private_test"
    with tempfile.TemporaryDirectory() as d:
        root = _fake_data_root(Path(d), "public_test", "private_test")
        assert find_split(root) == "private_test"
        assert find_split(root, "public_test") == "public_test"
    with tempfile.TemporaryDirectory() as d:
        root = _fake_data_root(Path(d), "train", "public_test")
        for bad in (None, "private_test"):
            try:
                find_split(root, bad)
            except ValueError as e:
                assert "train" in str(e) and "public_test" in str(e)
            else:
                raise AssertionError(f"find_split({bad!r}) should fail with two splits")
        assert find_split(root, "train") == "train"
    with tempfile.TemporaryDirectory() as d:
        try:
            find_split(d)
        except ValueError as e:
            assert "none" in str(e)
        else:
            raise AssertionError("an empty data folder has no split")


def test_settings_defaults_and_overrides():
    s = settings({})
    assert s == {"asr_model": "ckpt/asr_phoft/merged", "adapter": "ckpt/q4b4_all/final",
                 "llm": "Qwen/Qwen3-4B-Instruct-2507", "load_4bit": True, "time_budget": 25.0, "warmup": True, "seed": 0}
    assert settings({"TIME_BUDGET": "20", "WARMUP": "0", "ADAPTER": ""}) == {**s, "time_budget": 20.0, "warmup": False}
    for bad in ({"TIME_BUDGET": "30"}, {"TIME_BUDGET": "0"}, {"LOAD_4BIT": "yes"}, {"WARMUP": "2"}):
        try:
            settings(bad)
        except ValueError:
            continue
        raise AssertionError(f"settings({bad}) should fail")


def _shell_defaults(path: Path) -> dict[str, str]:
    return dict(re.findall(r"^([A-Z_0-9]+)=\$\{\1:-([^}]*)\}$", path.read_text(), re.M))


def test_docker_predict_defaults_match_submit():
    got = _shell_defaults(DOCKER / "predict.sh")
    assert {k: got.get(k) for k in DEFAULTS} == DEFAULTS


def test_pipeline_script_defaults_match_submit():
    got = _shell_defaults(PKG_DIR / "scripts" / "predict.sh")  # ASR_MODEL and ADAPTER are required there
    assert {k: got.get(k) for k in DEFAULTS if k not in ("ASR_MODEL", "ADAPTER")} == \
        {k: v for k, v in DEFAULTS.items() if k not in ("ASR_MODEL", "ADAPTER")}


def test_max_tokens_matches_infer_and_backend():
    assert '"--max-tokens", type=int, default=%d' % MAX_TOKENS in (PKG_DIR / "lifemate" / "infer.py").read_text()
    assert inspect.signature(HFBackend).parameters["max_tokens"].default == MAX_TOKENS


def test_model_path_prefers_local_folder():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "ckpt" / "x").mkdir(parents=True)
        assert model_path(d, "ckpt/x") == str(Path(d) / "ckpt" / "x")
        assert model_path(d, "Qwen/Qwen3-4B-Instruct-2507") == "Qwen/Qwen3-4B-Instruct-2507"


def test_seed_everything_repeats():
    import numpy as np
    import torch

    seed_everything(0)
    a = (random.random(), float(np.random.rand()), float(torch.rand(1)))
    random.random(), np.random.rand(), torch.rand(1)
    seed_everything(0)
    assert (random.random(), float(np.random.rand()), float(torch.rand(1))) == a
    assert os.environ["PYTHONHASHSEED"] == "0"
    assert torch.backends.cudnn.deterministic and not torch.backends.cudnn.benchmark


# ------------------------------------------------------------------ the time field

def test_check_submission_accepts_integer_time():
    errs = _check_module().structure_errors
    row = {"id": "a", "tool_calls": [{"name": "x.y", "arguments": {}}], "state_hash": "0" * 64}
    assert errs([row], ["a"]) == []
    assert errs([{**row, "time": 1234}], ["a"], require_time=True) == []
    assert errs([row], ["a"], require_time=True) == ["line 1: keys ['id', 'state_hash', 'tool_calls']"]
    for bad in (12.5, -1, True, "12"):
        assert errs([{**row, "time": bad}], ["a"]) == [f"a: time must be integer milliseconds >= 0, got {bad!r}"]
    assert errs([{**row, "time": 1, "extra": 0}], ["a"]) == ["line 1: keys ['extra', 'id', 'state_hash', 'time', 'tool_calls']"]


def test_report_lines():
    rows = [{"id": "a", "time": 1000}, {"id": "b", "time": 3000}, {"id": "c", "time": 26000}]
    lines = report({"timing": {"load_s": 5.0, "warmup_s": 0.5}}, {"load_s": 30.0, "warmup_s": 2.0,
                                                                    "args": {"time_budget": 25.0}}, rows)
    assert lines[0] == "load model: 37500 ms (ASR 5000 ms, ASR warm-up 500 ms, LLM 30000 ms, LLM warm-up 2000 ms)"
    assert lines[1].startswith("predict: 3 mẫu, 30000 ms, trung bình 10000.0 ms/mẫu (")
    assert "over 25 s: 1" in lines[1] and len(lines) == 2
    assert report({}, {}, [{"id": "a"}])[-1] == "WARNING: 1 of 1 rows have no integer time"


def test_infer_rows_carry_time():
    """lifemate.infer with an ASR file and the oracle backend: every row has an integer time that includes the ASR
    file's seconds; check_submission --require-time and the organisers' zaic_tools --validate accept the file."""
    _need_train()
    items = _items()
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "ids.txt").write_text("\n".join(IDS) + "\n")
        asr = [{"audio": item["audio"], "text": item["audio_text"], "seconds": 0.25} for item in items]
        asr += [{"audio": h["audio"], "text": h["audio_text"], "seconds": 0.25}
                for item in items for h in item["history"] if h["role"] == "user"]
        (d / "asr.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in asr))
        run = [sys.executable, "-m", "lifemate.infer", "--split", "train", "--ids", str(d / "ids.txt"), "--text", "asr",
               "--asr-file", str(d / "asr.jsonl"), "--backend", "oracle", "--out", str(d / "sub.jsonl"),
               "--trace", str(d / "trace.jsonl")]
        p = subprocess.run(run, cwd=PKG_DIR, capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        rows = {r["id"]: r for r in load_jsonl(d / "sub.jsonl")}
        for item in items:
            r = rows[item["id"]]
            assert set(r) == {"id", "tool_calls", "state_hash", "time"} and type(r["time"]) is int
            assert r["time"] >= 250 * len(sample_wavs(item))
        p = subprocess.run([sys.executable, "scripts/check_submission.py", str(d / "sub.jsonl"), "--split", "train",
                            "--ids", str(d / "ids.txt"), "--require-time"], cwd=PKG_DIR, capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        res = json.loads(p.stdout)
        assert res["ok"] and res["rows_with_time"] == 3
        assert (res["zaic_tools_validate"]["lines"], res["zaic_tools_validate"]["schema_errors"]) == (3, 0)
        p = subprocess.run([sys.executable, "-m", "lifemate.scorer", str(d / "sub.jsonl"), "--split", "train", "--ids",
                            str(d / "ids.txt")], cwd=PKG_DIR, capture_output=True, text=True)
        assert p.returncode == 0 and json.loads(p.stdout)["score"] == 100.0, p.stdout + p.stderr


# ------------------------------------------------------------------ the notebook's per-sample run

def test_runner_one_sample_at_a_time():
    """ASR of the sample's own wavs, then the agent on its one ToolEnv: with the oracle LLM, the state hash is the
    gold one, and the text the agent got is the final turn's transcript."""
    _need_train()
    from lifemate.scorer import gold_from_train
    gold = gold_from_train("train", DEFAULT_ROOT, IDS)
    zt = zaic_tools("train", DEFAULT_ROOT)
    asr = FakeASR()
    runner = Runner("train", DEFAULT_ROOT, asr, FakeLLM(), time_budget=25.0)
    for item in _items():
        runner.llm = OracleBackend(item["label"]["tool_calls"])
        t1 = time.perf_counter()
        env = zt.ToolEnv("train", item["id"], root=str(DEFAULT_ROOT))
        trace = runner.run(item, env, t1)
        ms = int((time.perf_counter() - t1) * 1000)
        assert env.get_state_hash() == gold[item["id"]]["state_hash"]
        assert env.get_tool_calls() == gold[item["id"]]["tool_calls"]
        n = len(read_wav(Path(DEFAULT_ROOT) / "train" / item["audio"]))
        assert trace["text"] == f"len {n}" and trace["stop"] in ("done", "ask_missing")
        assert 0 <= trace["asr_seconds"] <= trace["seconds"] <= ms / 1000 + 0.01
    assert asr.calls == sum(len(sample_wavs(s)) for s in _items())


def test_runner_budget_counts_asr():
    """The budget runs from t1 (before the audio is read): slow ASR leaves no time for an agent step."""
    _need_train()
    zt = zaic_tools("train", DEFAULT_ROOT)
    item = _items(["train_0003"])[0]
    runner = Runner("train", DEFAULT_ROOT, FakeASR(sleep=0.6), OracleBackend(item["label"]["tool_calls"]),
                    time_budget=1.2)  # 0.6 s left after ASR < the agent's 1 s minimum per step
    env = zt.ToolEnv("train", item["id"], root=str(DEFAULT_ROOT))
    trace = runner.run(item, env, time.perf_counter())
    assert trace["stop"] == "time" and trace["steps"] == [] and env.get_tool_calls() == []


def test_runner_warmup_uses_no_sample_audio():
    _need_train()
    asr, llm = FakeASR(), FakeLLM()
    runner = Runner("train", DEFAULT_ROOT, asr, llm)
    runner.warmup(_items(["train_0069"])[0])
    assert asr.warmups == 1 and asr.calls == 0 and len(llm.warmups) == 1 and "Xin chào." in llm.warmups[0]


# ------------------------------------------------------------------ docker/predict_notebook.ipynb

def _notebook():
    return json.loads((DOCKER / "predict_notebook.ipynb").read_text(encoding="utf-8"))


def _code_cells():
    return ["".join(c["source"]) for c in _notebook()["cells"] if c["cell_type"] == "code"]


def test_notebook_shape():
    nb = _notebook()
    assert nb["nbformat"] == 4 and nb["metadata"]["kernelspec"]["name"] == "python3"
    assert all(not c.get("outputs") and c.get("execution_count") is None for c in nb["cells"] if c["cell_type"] == "code")
    code = _code_cells()
    for src in code:
        compile(src, "<cell>", "exec")
    # the organisers' steps, in order: seed, models, test cases, per-sample loop writing jupyter_submission.jsonl
    order = [next(i for i, s in enumerate(code) if key in s)
             for key in ("seed_everything(", "HFBackend(", "load_split(", "for item in test_cases:")]
    assert order == sorted(order) and len(set(order)) == 4
    loop = code[order[3]]
    assert 'ToolEnv(SPLIT, item["id"], root=str(ROOT))' in loop and "time.perf_counter() - t1" in loop
    assert loop.index("t1 = time.perf_counter()") < loop.index("ToolEnv(") < loop.index("runner.run(")
    assert '"jupyter_submission.jsonl"' in loop and '"time": ms' in loop


def test_notebook_runs_with_fake_models():
    """Run All in this process with the ASR and LLM replaced by fakes: the notebook writes one row per sample with
    an integer time to RESULT_DIR/jupyter_submission.jsonl, and nothing else to RESULT_DIR."""
    _need_train()
    import lifemate.agent
    import lifemate.asr

    real = (lifemate.asr.Whisper, lifemate.agent.HFBackend)
    env_keys = ("LIFEMATE_DIR", "DATA_ROOT", "SPLIT", "IDS", "RESULT_DIR", "WORK")
    old_env = {k: os.environ.get(k) for k in env_keys}
    old_bytecode = sys.dont_write_bytecode
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "ids.txt").write_text("\n".join(IDS) + "\n")
        os.environ.update(LIFEMATE_DIR=str(PKG_DIR), DATA_ROOT=str(DEFAULT_ROOT), SPLIT="train",
                          IDS=str(d / "ids.txt"), RESULT_DIR=str(d / "result"), WORK=str(d / "work"))
        lifemate.asr.Whisper, lifemate.agent.HFBackend = FakeASR, FakeLLM
        try:
            ns = {"__name__": "__main__"}
            for src in _code_cells():
                exec(compile(src, "<cell>", "exec"), ns)
        finally:
            lifemate.asr.Whisper, lifemate.agent.HFBackend = real
            sys.dont_write_bytecode = old_bytecode
            for k, v in old_env.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        rows = load_jsonl(d / "result" / "jupyter_submission.jsonl")
        assert [r["id"] for r in rows] == IDS  # split order
        for r in rows:
            assert set(r) == {"id", "tool_calls", "state_hash", "time"} and type(r["time"]) is int and r["time"] >= 0
            assert r["tool_calls"] == [] and HASH.match(r["state_hash"])
        assert sorted(p.name for p in (d / "result").iterdir()) == ["jupyter_submission.jsonl"]
        assert len(load_jsonl(d / "work" / "jupyter_trace.jsonl")) == 3
        assert ns["asr_model"].warmups == 1 and len(ns["model"].warmups) == 1


# ------------------------------------------------------------------ docker/predict.sh and docker/start_jupyter.sh

def _wrapper(env: dict, lifemate_dir=PKG_DIR):
    e = {k: v for k, v in os.environ.items() if k not in ("SPLIT", "IDS", "WORK", "DRY_RUN")}
    e.update(LIFEMATE_DIR=str(lifemate_dir), PY=sys.executable, **env)
    return subprocess.run(["bash", str(DOCKER / "predict.sh")], capture_output=True, text=True, env=e)


def _listing(root: Path) -> list[str]:
    return sorted(str(p.relative_to(root)) for p in root.rglob("*"))


def test_wrapper_dry_run_finds_split_and_writes_nothing():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        data = _fake_data_root(d / "data", "private_test")
        before = _listing(d)
        p = _wrapper({"DATA_ROOT": str(data), "RESULT_DIR": str(d / "result"), "DRY_RUN": "1"})
        assert p.returncode == 0, p.stderr
        assert f"split private_test from {data}/private_test" in p.stdout
        assert f"output will be saved in {d}/result/submission.jsonl" in p.stdout
        assert _listing(d) == before  # no result folder, no temp folder, nothing under data
        p = _wrapper({"DATA_ROOT": str(data), "RESULT_DIR": str(d / "result"), "WORK": str(data / "w"), "DRY_RUN": "1"})
        assert p.returncode != 0 and "read-only" in p.stderr
        _fake_data_root(data, "train")
        p = _wrapper({"DATA_ROOT": str(data), "SPLIT": "train", "DRY_RUN": "1"})
        assert p.returncode == 0 and "split train" in p.stdout, p.stderr


FAKE_PIPELINE = """#!/usr/bin/env bash
# stands in for scripts/predict.sh: writes what the real one writes, from the environment the wrapper sets
set -euo pipefail
echo "fake pipeline SPLIT=$SPLIT DATA=$DATA OUT=$OUT SEED=$SEED TIME_BUDGET=$TIME_BUDGET PYTHONHASHSEED=$PYTHONHASHSEED"
[ "${FAKE_WRITE:-1}" = 1 ] || exit 3
printf '%s\\n' '{"id": "private_0001", "tool_calls": [], "state_hash": "ab", "time": 1500}' \\
  '{"id": "private_0002", "tool_calls": [], "state_hash": "cd", "time": 2500}' > "$OUT"
echo '{"timing": {"load_s": 4.0, "warmup_s": 1.0}}' > "${OUT%.jsonl}_asr.meta.json"
echo '{"load_s": 20.0, "warmup_s": 2.0, "args": {"time_budget": 25.0}}' > "${OUT%.jsonl}.meta.json"
exit "${FAKE_RC:-0}"
"""


def _fake_lifemate(d: Path) -> Path:
    lm = d / "lm"
    (lm / "scripts").mkdir(parents=True)
    (lm / "lifemate").symlink_to(PKG_DIR / "lifemate")
    (lm / "scripts" / "predict.sh").write_text(FAKE_PIPELINE)
    return lm


def test_wrapper_writes_result_and_times():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        data, lm = _fake_data_root(d / "data", "private_test"), _fake_lifemate(d)
        p = _wrapper({"DATA_ROOT": str(data), "RESULT_DIR": str(d / "result"), "WORK": str(d / "work")}, lm)
        assert p.returncode == 0, p.stdout + p.stderr
        assert f"SPLIT=private_test DATA={data} OUT={d}/work/submission.jsonl SEED=0 TIME_BUDGET=25 PYTHONHASHSEED=0" \
            in p.stdout
        assert "load model: 27000 ms (ASR 4000 ms, ASR warm-up 1000 ms, LLM 20000 ms, LLM warm-up 2000 ms)" in p.stdout
        assert "predict: 2 mẫu, 4000 ms, trung bình 2000.0 ms/mẫu" in p.stdout and "total wall time:" in p.stdout
        assert len(load_jsonl(d / "result" / "submission.jsonl")) == 2
        assert sorted(x.name for x in (d / "result").iterdir()) == ["submission.jsonl"]
        assert _listing(data) == ["private_test", "private_test/private_test_tools_catalog.json"]


def test_wrapper_failures():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        data, lm = _fake_data_root(d / "data", "private_test"), _fake_lifemate(d)
        # a late step fails (e.g. the check): the rows are still copied, the exit code says it failed
        p = _wrapper({"DATA_ROOT": str(data), "RESULT_DIR": str(d / "r1"), "WORK": str(d / "w1"), "FAKE_RC": "4"}, lm)
        assert p.returncode == 4 and (d / "r1" / "submission.jsonl").exists() and "exit 4" in p.stderr
        # nothing produced: no file, non-zero exit
        p = _wrapper({"DATA_ROOT": str(data), "RESULT_DIR": str(d / "r2"), "WORK": str(d / "w2"), "FAKE_WRITE": "0"}, lm)
        assert p.returncode == 3 and not (d / "r2" / "submission.jsonl").exists() and "FAILED" in p.stderr


def test_start_jupyter_uses_the_organisers_command():
    with tempfile.TemporaryDirectory() as d:
        fake_py = Path(d) / "python"
        fake_py.write_text('#!/usr/bin/env bash\n[ "$1" = -c ] && exit 0\n'
                           'echo "cwd=$PWD LIFEMATE_DIR=$LIFEMATE_DIR PYTHONHASHSEED=$PYTHONHASHSEED HF_HUB_OFFLINE=$HF_HUB_OFFLINE"\n'
                           'printf "%s\\n" "$@"\n')
        fake_py.chmod(0o755)
        e = {k: v for k, v in os.environ.items() if k != "LIFEMATE_DIR"}
        p = subprocess.run(["bash", str(DOCKER / "start_jupyter.sh")], capture_output=True, text=True,
                           env={**e, "PY": str(fake_py)})
        assert p.returncode == 0, p.stderr
        first, *args = p.stdout.splitlines()
        assert first == f"cwd={DOCKER} LIFEMATE_DIR={PKG_DIR} PYTHONHASHSEED=0 HF_HUB_OFFLINE=1"
        assert args == ["-m", "jupyterlab", "--port", "9777", "--ip", "0.0.0.0", "--NotebookApp.password=zac2026",
                        "--NotebookApp.token=zac2026", "--allow-root", "--no-browser"]


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
