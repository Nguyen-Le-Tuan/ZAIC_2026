"""Paths, loaders and the split's own zaic_tools package.

Agent code may only touch: <split>.jsonl, the tools catalog, audio, and zaic_tools.ToolEnv.
Never read <split>_environment/ from here.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2] / "data" / "train+public_test"


def load_jsonl(path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path, rows) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_split(split: str, root=DEFAULT_ROOT) -> list[dict]:
    return load_jsonl(Path(root) / split / f"{split}.jsonl")


def load_catalog(split: str, root=DEFAULT_ROOT) -> dict:
    with open(Path(root) / split / f"{split}_tools_catalog.json", encoding="utf-8") as f:
        return json.load(f)


def catalog_tools(catalog: dict) -> dict[str, dict]:
    """{tool name: tool spec} for every app of the catalog."""
    return {t["name"]: t for app in catalog["apps"] for t in app["tools"]}


def fuzzy_params(catalog: dict) -> dict[str, set[str]]:
    """{tool name: names of its x-match: fuzzy parameters}."""
    out = {}
    for name, t in catalog_tools(catalog).items():
        props = t.get("parameters", {}).get("properties", {})
        out[name] = {k for k, v in props.items() if v.get("x-match") == "fuzzy"}
    return out


_loaded_split = None


def zaic_tools(split: str, root=DEFAULT_ROOT):
    """Import the zaic_tools package that ships with `split`.
    Each split has its own version, so one process can only use one split."""
    global _loaded_split
    if _loaded_split is not None and _loaded_split != split:
        raise RuntimeError(f"zaic_tools of split {_loaded_split!r} already loaded; use a new process for {split!r}")
    if _loaded_split is None:
        sys.path.insert(0, str(Path(root) / split))
        _loaded_split = split
    return importlib.import_module("zaic_tools")
