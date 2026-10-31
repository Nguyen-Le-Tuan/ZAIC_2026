"""SFT data builder: train samples -> ChatML sequences with loss masks, built with the SAME prompt code as inference.

Each output line: {"id", "src", "aug", "segments": [[text, loss], ...]}. Concatenating the texts gives the full
sequence; loss=True marks the model's own turns (tool calls of each step and the final short answer).

Steps: the gold call list is flat, the agent emits one or more calls per step. A new step starts when a call uses a
value returned inside the current step, or when a write/meta call follows a read in the current step (its decision
may depend on what the read returned). The final answer is a fixed short text; the sequence ends right after
sys.ask_missing_info because inference stops there.

Sources:
  gold      label.tool_calls of each sample (the only source following the scored conventions)
  history   earlier assistant turns (opt-in). Their conventions differ from gold (e.g. get_status{room} vs {}),
            so "tagged" marks them in the system prompt and inference never uses that mark.

Augmentations (gold only):
  rename    apps/tools renamed consistently (schema, history, targets) so the model reads schemas instead of memorising names
  remove    every app in the groups the request needs is uninstalled -> target becomes no call
  distract  1-3 unrelated apps (other groups, also from the public_test catalog) added to installed_apps
  lower     user transcripts lower-cased without punctuation (ASR-like)
"""
from __future__ import annotations

import argparse
import copy
import json
import random
import re
from collections import Counter
from pathlib import Path

from . import runinfo
from .data import DEFAULT_ROOT, catalog_tools, load_catalog, load_jsonl, load_split
from .prompt import build_messages, render_calls, render_results

FINAL_DONE = "Đã xong."
FINAL_NONE = "Không cần gọi tool."
HISTORY_TAG = "\n\n# Chế độ: lượt cũ"

# ---------------------------------------------------------------- steps

def _atoms(x, out=None) -> set[str]:
    """Scalar values that could carry information from a tool result into a later call."""
    out = set() if out is None else out
    if isinstance(x, dict):
        for v in x.values():
            _atoms(v, out)
    elif isinstance(x, list):
        for v in x:
            _atoms(v, out)
    elif isinstance(x, bool) or x is None:
        pass
    elif isinstance(x, (int, float)):
        if abs(x) >= 10:
            out.add(str(x))
    elif isinstance(x, str) and len(x) >= 3:
        out.add(x)
    return out


def group_steps(calls: list[dict], results: list, tools: dict) -> list[list[int]]:
    steps, cur, cur_atoms, cur_read = [], [], set(), False
    for i, (c, r) in enumerate(zip(calls, results)):
        kind = tools.get(c["name"], {}).get("kind", "write")
        if cur and ((_atoms(c.get("arguments") or {}) & cur_atoms) or (kind != "read" and cur_read)):
            steps.append(cur)
            cur, cur_atoms, cur_read = [], set(), False
        cur.append(i)
        _atoms(r, cur_atoms)
        cur_read |= kind == "read"
    if cur:
        steps.append(cur)
    return steps


# ---------------------------------------------------------------- sequence

def _chatml(role: str, content: str) -> str:
    return f"<|im_start|>{role}\n{content}<|im_end|>\n"


def build_example(item, user_text, history_texts, calls, results, tools, apps, system_suffix="") -> list[list]:
    """Segments [[text, loss], ...] for one request. Prompt text is identical to what Agent.run feeds the model."""
    msgs = build_messages(item, user_text, history_texts, tools, apps)
    msgs[0]["content"] += system_suffix
    segs = [["".join(_chatml(m["role"], m["content"]) for m in msgs) + "<|im_start|>assistant\n", False]]
    if not calls:
        segs.append([FINAL_NONE + "<|im_end|>", True])
        return segs
    for step in group_steps(calls, results, tools):
        step_calls = [calls[i] for i in step]
        segs.append([render_calls(step_calls) + "<|im_end|>", True])
        if any(c["name"] == "sys.ask_missing_info" for c in step_calls):
            return segs
        segs.append(["\n" + _chatml("user", render_results([results[i] for i in step])) + "<|im_start|>assistant\n", False])
    segs.append([FINAL_DONE + "<|im_end|>", True])
    return segs


# ---------------------------------------------------------------- augmentations

APP_SYNONYMS = {
    "smart_home": "home_iot", "ride_hailing": "taxi", "food_delivery": "food_order", "chat_ott": "messenger",
    "bill_payment": "bills", "ewallet": "wallet", "banking": "bank", "reminders": "reminder", "calendar": "schedule",
    "contacts": "phonebook", "alarm": "clock", "notes": "notebook", "tasks": "todo", "weather": "forecast",
    "music": "music_player", "tv": "television", "email": "mail", "phone": "dialer", "sms": "text_message",
    "maps": "navigation", "flights": "airline", "shopping_list": "shop_list", "gold_price": "gold", "fuel_price": "petrol",
}
VERB_SYNONYMS = {
    "get": "fetch", "list": "show", "search": "find", "create": "add", "add": "create", "send": "post",
    "delete": "remove", "remove": "delete", "cancel": "abort", "book": "reserve", "update": "edit", "read": "open",
    "set": "change", "pay": "settle", "call": "dial", "play": "start", "transfer": "send_money",
}


def _rename_app(app: str, rng: random.Random) -> str:
    opts = [app.replace("_", ""), app + "_app", "vn_" + app]
    if app in APP_SYNONYMS:
        opts += [APP_SYNONYMS[app]] * 2
    return rng.choice(opts)


def _rename_action(action: str, rng: random.Random) -> str:
    toks = action.split("_")
    if rng.random() < 0.5 and toks[0] in VERB_SYNONYMS:
        toks = VERB_SYNONYMS[toks[0]].split("_") + toks[1:]
    elif rng.random() < 0.5 and toks[-1] in VERB_SYNONYMS:
        toks = toks[:-1] + VERB_SYNONYMS[toks[-1]].split("_")
    if len(toks) == 2 and rng.random() < 0.3:
        toks = toks[::-1]
    return "_".join(toks)


def make_rename(item: dict, rng: random.Random) -> dict[str, str]:
    """{old tool name: new tool name} for every installed tool (sys untouched)."""
    mapping, used = {}, set()
    for app, a in item["context"]["installed_apps"].items():
        new_app = _rename_app(app, rng)
        if new_app in used or new_app == "sys":
            new_app = app + "_app"
        used.add(new_app)
        seen = set()
        for t in a["tools"]:
            action = t.split(".", 1)[1]
            new_action = _rename_action(action, rng)
            if new_action in seen:
                new_action = action
            seen.add(new_action)
            mapping[t] = f"{new_app}.{new_action}"
    return mapping


def _replace_names(text: str, mapping: dict[str, str]) -> str:
    if not text:
        return text
    return re.sub(r"\b[a-z_]+\.[a-z_]+\b", lambda m: mapping.get(m.group(0), m.group(0)), text)


def _rename_spec(spec, mapping):
    if isinstance(spec, dict):
        return {k: (_replace_names(v, mapping) if k == "description" and isinstance(v, str) else _rename_spec(v, mapping)) for k, v in spec.items()}
    if isinstance(spec, list):
        return [_rename_spec(v, mapping) for v in spec]
    return spec


def rename_call(c: dict, mapping) -> dict:
    c = {"name": mapping.get(c["name"], c["name"]), "arguments": copy.deepcopy(c.get("arguments") or {})}
    if c["name"] == "sys.ask_missing_info" and isinstance(c["arguments"].get("tool_name"), str):
        c["arguments"]["tool_name"] = mapping.get(c["arguments"]["tool_name"], c["arguments"]["tool_name"])
    return c


def apply_rename(item, calls, tools, apps, mapping):
    """Renamed copies of (item, calls, tools_by_name, apps_by_id)."""
    item = copy.deepcopy(item)
    old_apps = item["context"]["installed_apps"]
    new_installed, new_apps = {}, {}
    for app, a in old_apps.items():
        new_tools = [mapping.get(t, t) for t in a["tools"]]
        new_app = new_tools[0].split(".", 1)[0] if new_tools else app
        new_installed[new_app] = {**a, "tools": new_tools}
        if app in apps:
            new_apps[new_app] = {**apps[app], "id": new_app, "description": _replace_names(apps[app].get("description", ""), mapping)}
    item["context"]["installed_apps"] = new_installed
    new_tools_by_name = dict(tools)
    for old, new in mapping.items():
        if old in tools:
            new_tools_by_name[new] = {**_rename_spec(tools[old], mapping), "name": new, "app": new.split(".", 1)[0]}
    if "sys.ask_missing_info" in tools:
        new_tools_by_name["sys.ask_missing_info"] = _rename_spec(tools["sys.ask_missing_info"], mapping)
    for h in item["history"]:
        if h.get("tool_calls"):
            h["tool_calls"] = [rename_call(c, mapping) for c in h["tool_calls"]]
    return item, [rename_call(c, mapping) for c in calls], new_tools_by_name, new_apps


def used_apps(calls) -> set[str]:
    out = set()
    for c in calls:
        out.add(c["name"].split(".", 1)[0])
        if c["name"] == "sys.ask_missing_info" and isinstance(c.get("arguments", {}).get("tool_name"), str):
            out.add(c["arguments"]["tool_name"].split(".", 1)[0])
    return out - {"sys"}


def make_removal(item, calls, apps_by_id) -> dict | None:
    """Uninstall every app in the groups the gold calls need -> nothing can handle the request -> no call.
    Skipped when history used one of those apps (the conversation would be inconsistent)."""
    need = used_apps(calls)
    if not need:
        return None
    groups = {apps_by_id.get(a, {}).get("group", a) for a in need}
    installed = item["context"]["installed_apps"]
    drop = {a for a in installed if apps_by_id.get(a, {}).get("group", a) in groups} | need
    hist_apps = used_apps([c for h in item["history"] for c in (h.get("tool_calls") or [])])
    keep = {a: v for a, v in installed.items() if a not in drop}
    if hist_apps & drop or len(keep) < 2:
        return None
    item = copy.deepcopy(item)
    item["context"]["installed_apps"] = keep
    return item


def add_distractors(item, calls, apps_by_id, pool: dict[str, dict], rng, k_max=3) -> dict | None:
    """Add 1..k_max apps from groups the request does not touch."""
    installed = item["context"]["installed_apps"]
    groups = {apps_by_id.get(a, {}).get("group") for a in used_apps(calls)}
    cands = sorted(a for a, info in pool.items() if a not in installed and info.get("group") not in groups and a != "sys")
    if not cands:
        return None
    item = copy.deepcopy(item)
    for a in rng.sample(cands, min(len(cands), rng.randint(1, k_max))):
        item["context"]["installed_apps"][a] = {"tools": [t["name"] for t in pool[a]["tools"]]}
    return item


_PUNCT = re.compile(r"[.,!?;:…\"“”]+")


def asr_style(text: str) -> str:
    return " ".join(_PUNCT.sub(" ", text.lower()).split())


# ---------------------------------------------------------------- driver

def user_texts(s: dict, asr: dict | None) -> tuple[str, list[str]]:
    pick = lambda turn: (asr or {}).get(turn["audio"]) or turn["audio_text"]  # noqa: E731
    return pick(s), [pick(h) for h in s["history"] if h["role"] == "user"]


def history_examples(s, user_text_list, tools, apps, tagged: bool):
    """One example per earlier assistant turn. Clarifying/greeting turns without calls ('?') are skipped:
    in gold, a clarification is a sys.ask_missing_info call, not plain text."""
    out, ui = [], -1
    for idx, turn in enumerate(s["history"]):
        if turn["role"] == "user":
            ui += 1
            continue
        calls = turn.get("tool_calls") or []
        if not calls and "?" in (turn.get("text") or ""):
            continue
        sub = {**s, "history": s["history"][: idx - 1]}
        segs = build_example(sub, user_text_list[ui], user_text_list[:ui], calls, turn.get("tool_results") or [],
                             tools, apps, HISTORY_TAG if tagged else "")
        out.append({"id": f"{s['id']}#h{idx}", "src": "history", "aug": [], "segments": segs})
    return out


def build_all(samples, tools, apps, pool, *, rename=2, p_remove=0.3, p_distract=0.5, p_lower=0.3,
              history="off", drop_apps=(), asr=None, seed=0):
    """pool: {app id: catalog app} for distractors (train + public_test catalogs; shared tools have identical schemas)."""
    rng = random.Random(seed)
    all_tools = {t["name"]: t for a in pool.values() for t in a["tools"]} | tools
    all_apps = pool | apps
    out = []
    for s in samples:
        s = copy.deepcopy(s)
        for a in drop_apps:  # leave-apps-out: never show held-out schemas
            s["context"]["installed_apps"].pop(a, None)
        calls, results = s["label"]["tool_calls"], s["label"]["tool_results"]
        utext, htexts = user_texts(s, asr)

        for k in range(1 + rename):
            it, cl, tb, ab, aug = s, calls, tools, apps, []
            # distractors first (original names), then rename everything installed, distractors included
            if calls and rng.random() < p_distract:
                d = add_distractors(it, cl, all_apps, pool, rng)
                if d is not None:
                    it, tb, ab, aug = d, all_tools, all_apps, ["distract"]
            if k > 0:
                it, cl, tb, ab = apply_rename(it, cl, tb, ab, make_rename(it, rng))
                aug = [f"rename{k}"] + aug
            low = rng.random() < p_lower
            u, h = (asr_style(utext), [asr_style(x) for x in htexts]) if low else (utext, htexts)
            out.append({"id": s["id"], "src": "gold", "aug": aug + (["lower"] if low else []),
                        "segments": build_example(it, u, h, cl, results, tb, ab)})
        if calls and rng.random() < p_remove:
            r = make_removal(s, calls, apps)
            if r is not None:
                out.append({"id": s["id"], "src": "gold", "aug": ["remove"], "segments": build_example(r, utext, htexts, [], [], tools, apps)})
        if history != "off":
            out += history_examples(s, htexts + [utext], tools, apps, tagged=history == "tagged")
    return out


def main():
    ap = argparse.ArgumentParser(description="build SFT jsonl from train")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--fit", help="ids to use (default: all train)")
    ap.add_argument("--drop-apps", help="json list of apps to remove from every sample (leave-apps-out)")
    ap.add_argument("--rename", type=int, default=2, help="renamed variants per sample")
    ap.add_argument("--p-remove", type=float, default=0.3)
    ap.add_argument("--p-distract", type=float, default=0.5)
    ap.add_argument("--p-lower", type=float, default=0.3)
    ap.add_argument("--history", choices=["off", "tagged", "plain"], default="off")
    ap.add_argument("--asr-file", help="use ASR transcripts (k-fold, so not trained on) instead of audio_text")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reuse", action="store_true",
                    help="keep an existing --out only if its manifest matches these settings and its sha256 "
                         "(a file without manifest is kept only if a rebuild is byte-identical); otherwise rebuild")
    a = ap.parse_args()

    out = Path(a.out)
    man_path = out.with_name(out.name + ".manifest.json")
    spec = _spec(a)
    if a.reuse and out.exists() and man_path.exists():
        man = json.loads(man_path.read_text())
        if man.get("spec") == spec and man.get("out_sha256") == runinfo.sha256_file(out):
            print(json.dumps({"reuse": str(out), "rows": man["rows"], "ids": man["ids"]}))
            return

    cat = load_catalog("train", a.root)
    tools, apps = catalog_tools(cat), {x["id"]: x for x in cat["apps"]}
    drop = set(json.loads(Path(a.drop_apps).read_text())) if a.drop_apps else set()
    pool = {x["id"]: x for x in load_catalog("public_test", a.root)["apps"]} | apps  # distractor schemas (text only)
    pool = {k: v for k, v in pool.items() if k not in drop}
    samples = load_split("train", a.root)
    if a.fit:
        keep = set(Path(a.fit).read_text().split())
        samples = [s for s in samples if s["id"] in keep]
    asr = {r["audio"]: r["text"] for r in load_jsonl(a.asr_file)} if a.asr_file else None
    rows = build_all(samples, tools, apps, pool, rename=a.rename, p_remove=a.p_remove, p_distract=a.p_distract,
                     p_lower=a.p_lower, history=a.history, drop_apps=drop, asr=asr, seed=a.seed)
    data = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode()
    new_sha = runinfo.sha256_bytes(data)
    status = "new"
    if out.exists():
        old_sha = runinfo.sha256_file(out)
        if old_sha == new_sha:
            status = "identical rebuild (existing file kept)"
        else:
            # the old file may be what a checkpoint was trained on: keep it next to the new one
            keep = out.with_name(f"{out.name}.prev-{old_sha[:12]}")
            out.rename(keep)
            if man_path.exists():
                man_path.rename(keep.with_name(keep.name + ".manifest.json"))
            status = f"rebuilt; previous content differed and was moved to {keep.name}"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        out.write_bytes(data)
    runinfo.write_json(man_path, {
        "kind": "sft", "created": runinfo.now(), "spec": spec, "rows": len(rows),
        "ids": runinfo.ids_digest(s["id"] for s in samples), "out_sha256": new_sha,
        "aug": Counter(x for r in rows for x in (r["aug"] or ["none"])), "git": runinfo.git_state()})
    aug = Counter(x for r in rows for x in (r["aug"] or ["none"]))
    print(json.dumps({"samples": len(samples), "examples": len(rows), "src": Counter(r["src"] for r in rows), "aug": aug,
                      "status": status, "sha256": new_sha[:12]}, ensure_ascii=False))


def _spec(a) -> dict:
    """Everything that determines the SFT file's content: settings, input files and the code that renders it."""
    root = Path(a.root)
    files = {"train_jsonl": root / "train" / "train.jsonl", "train_catalog": root / "train" / "train_tools_catalog.json",
             "public_catalog": root / "public_test" / "public_test_tools_catalog.json"}
    return {
        "args": {k: v for k, v in vars(a).items() if k not in ("out", "reuse", "root")},
        "fit_ids": runinfo.ids_digest(runinfo.read_ids(a.fit)) if a.fit else "all",
        "drop_apps": sorted(json.loads(Path(a.drop_apps).read_text())) if a.drop_apps else [],
        "asr_sha256": runinfo.sha256_file(a.asr_file) if a.asr_file else None,
        "inputs_sha256": {k: runinfo.sha256_file(p) for k, p in files.items()},
        "code_sha256": runinfo.code_digest(("data.py", "prompt.py", "sft.py")),
    }


if __name__ == "__main__":
    main()
