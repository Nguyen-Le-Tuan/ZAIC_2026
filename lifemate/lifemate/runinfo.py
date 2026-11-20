"""Provenance for every artefact: which code, data, ids, model and settings produced it.

Each SFT file, training run and evaluation run writes a small JSON next to its output, so a number in the journal
can be traced back to exact inputs instead of trusting file names.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def sha256_dir(path) -> str:
    """Digest of every file in a directory (relative name + content), e.g. a LoRA adapter."""
    h = hashlib.sha256()
    for p in sorted(Path(path).rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(path)).encode() + b"\0" + sha256_file(p).encode() + b"\n")
    return h.hexdigest()


def ids_digest(ids) -> dict:
    ids = sorted(set(ids))
    return {"n": len(ids), "sha256": sha256_bytes("\n".join(ids).encode())}


def read_ids(path) -> list[str]:
    return Path(path).read_text().split()


def code_digest(names=("data.py", "prompt.py", "sft.py", "agent.py")) -> str:
    """Digest of the modules that shape prompts and SFT targets."""
    return sha256_bytes(b"".join((PKG / n).read_bytes() for n in names))


def git_state() -> dict:
    def run(*cmd):
        try:
            return subprocess.run(["git", "-C", str(REPO), *cmd], capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    dirty = run("status", "--porcelain", "--untracked-files=no", "--", "lifemate")
    return {"commit": run("rev-parse", "HEAD"), "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
            "lifemate_dirty": bool(dirty) if dirty is not None else None}


def env_info() -> dict:
    info = {"python": platform.python_version(), "host": platform.node()}
    for mod in ("torch", "transformers", "peft"):
        m = sys.modules.get(mod)
        if m is not None:
            info[mod] = getattr(m, "__version__", None)
    torch = sys.modules.get("torch")
    if torch is not None and torch.cuda.is_available():
        info["gpu"] = torch.cuda.get_device_name(0)
    return info


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def write_json(path, obj) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def refuse_existing(*paths, overwrite: bool = False) -> None:
    """Earlier predictions, scores and checkpoints are evidence: never replace them silently."""
    hit = [str(p) for p in paths if p and Path(p).exists()]
    if hit and not overwrite:
        sys.exit(f"refusing to overwrite {', '.join(hit)} (pick a new tag, or pass --overwrite on purpose)")


def percentile(xs: list[float], q: float) -> float:
    if not xs:
        return 0.0
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)
