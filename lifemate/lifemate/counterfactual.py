"""Counterfactual ask / execute pairs for experiment D (design: docs/EXPERIMENT_D.md on main).

Each synthetic sample is a fit sample whose request text is rewritten so that the right action flips:
  C           drop one slot the request gives (amount, time, ...) -> ask for it instead of the last write
  B-vague     make the reference to a listed entity vague (>=2 fit) -> ask for its id instead of the last write
  B-specific  from a type-B ask, name one listed entity by a distinguishing word -> do the write with its id
The original sample stays in the data as the other half of the pair. Labels are replayed through the origin
sample's ToolEnv; anything that fails a check is dropped with a reason. Only fit samples are used.

Commands (outputs go to gen/, which is git-ignored: it holds text derived from the competition data):
  python -m lifemate.counterfactual candidates --fit splits/fit_lao.txt --out gen/tasks_fit_lao.jsonl
  (write gen/rewrites_fit_lao.jsonl: {"task_id", "new_text", "removed_span" | "added_span"} or {"task_id", "skip": reason})
  python -m lifemate.counterfactual build --tasks gen/tasks_fit_lao.jsonl --rewrites gen/rewrites_fit_lao.jsonl \
      --fit splits/fit_lao.txt --exclude splits/dev_lao.txt splits/dev_random.txt --drop-apps splits/heldout_apps.json \
      --out gen/d_fit_lao.jsonl
  python -m lifemate.counterfactual review --samples gen/d_fit_lao.jsonl --tasks gen/tasks_fit_lao.jsonl --out gen/review_fit_lao.md
Then: python -m lifemate.sft --fit splits/fit_lao.txt ... --extra-samples gen/d_fit_lao.jsonl
"""
from __future__ import annotations

import argparse
import copy
import difflib
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from . import runinfo
from .askpolicy import ASK, entities, ent_name, is_ask_sample, is_xref, norm, required, words, _attr_words, ask_type, \
    attested_plain_params
from .data import DEFAULT_ROOT, catalog_tools, load_catalog, load_jsonl, load_split, write_jsonl, zaic_tools
from .sft import used_apps

SRC = "synthetic-D"
MIN_SIMILARITY = 0.6


# ---------------------------------------------------------------- helpers

def _atoms(x) -> set[str]:
    if isinstance(x, dict):
        return set().union(*[_atoms(v) for v in x.values()] or [set()])
    if isinstance(x, list):
        return set().union(*[_atoms(v) for v in x] or [set()])
    return {str(x)}


def _kind(tools, name) -> str | None:
    return tools.get(name, {}).get("kind")


def _last_write(calls, tools) -> int | None:
    idx = [i for i, c in enumerate(calls) if _kind(tools, c["name"]) == "write"]
    return idx[-1] if idx else None


def _speakable(w: str) -> bool:
    """Words a user could say: not internal ids (fl_5384) or timestamp fragments (24t18)."""
    return "_" not in w and not re.fullmatch(r"\d+t\d+", w)


def _ent_words(e: dict) -> set[str]:
    return {w for w in words(ent_name(e) or "") | _attr_words(e) if _speakable(w)}


def _unique_words(ents: list[dict], i: int) -> set[str]:
    """Speakable words of entity i (name + attributes) that no other listed entity has."""
    own = [_ent_words(e) for e in ents]
    return own[i] - set().union(*[w for j, w in enumerate(own) if j != i] or [set()])


def _history_atoms(s) -> set[str]:
    return _atoms([h.get("tool_results", []) for h in s.get("history", [])])


# ---------------------------------------------------------------- candidates

def candidates_c(s, tools, attested) -> list[dict]:
    calls, results = s["label"]["tool_calls"], s["label"]["tool_results"]
    if not calls or is_ask_sample(s):
        return []
    w = _last_write(calls, tools)
    if w is None:
        return []
    c = calls[w]
    seen = _atoms(results[:w]) | _history_atoms(s)
    out = []
    for p in required(tools.get(c["name"], {})):
        v = c["arguments"].get(p)
        if p not in attested or v is None or isinstance(v, bool) or is_xref(tools[c["name"]], p):
            continue
        if (all(str(x) in seen for x in v) if isinstance(v, list) else str(v) in seen):  # copied from a tool result
            continue
        out.append({"kind": "C", "write_index": w, "tool": c["name"], "param": p, "value": v,
                    "param_desc": tools[c["name"]]["parameters"]["properties"].get(p, {}).get("description", "")})
    return out


def _list_pick(calls, results, upto: int, value) -> tuple[list[dict], int] | None:
    """The last read before `upto` whose entity list (>=2) contains id `value`: (entities, index of value)."""
    for i in range(upto - 1, -1, -1):
        ents = entities(results[i])
        ids = [str(e.get("id")) for e in ents]
        if len(ents) >= 2 and str(value) in ids:
            return ents, ids.index(str(value))
    return None


def candidates_b_vague(s, tools) -> list[dict]:
    calls, results = s["label"]["tool_calls"], s["label"]["tool_results"]
    if not calls or is_ask_sample(s):
        return []
    w = _last_write(calls, tools)
    if w is None:
        return []
    c = calls[w]
    out = []
    text = words(s["audio_text"])
    for p, v in c["arguments"].items():
        if not is_xref(tools.get(c["name"], {}), p):
            continue
        pick = _list_pick(calls, results, w, v)
        if pick is None:
            continue
        ents, k = pick
        dist = sorted(_unique_words(ents, k) & text)
        if not dist:  # nothing in the request singles the entity out: cannot check that a rewrite made it vague
            continue
        out.append({"kind": "B-vague", "write_index": w, "tool": c["name"], "param": p, "value": v,
                    "distinguishing_words": dist, "entities": ents})
    return out


def candidates_b_specific(s, tools, rng) -> list[dict]:
    if ask_type(s, tools) != "B":
        return []
    calls, results = s["label"]["tool_calls"], s["label"]["tool_results"]
    a = calls[-1]["arguments"]
    tool, p = a["tool_name"], a["params"][0]
    if required(tools.get(tool, {})) != [p]:
        return []
    text = words(s["audio_text"])
    for i in range(len(calls) - 2, -1, -1):
        ents = entities(results[i])
        if len(ents) >= 2:
            # only entities the vague request could mean (share a word with it) and that one word can single out
            options = [k for k in range(len(ents)) if _unique_words(ents, k) and _ent_words(ents[k]) & text]
            if not options:
                return []
            k = rng.choice(options)
            return [{"kind": "B-specific", "tool": tool, "param": p, "value": ents[k].get("id"),
                     "add_words": sorted(_unique_words(ents, k)), "entities": ents}]
    return []


INSTRUCTIONS = {
    "C": "Viết lại câu yêu cầu, bỏ ĐÚNG thông tin cho tham số {param} (= {value}) của {tool}; giữ nguyên phần còn lại "
         "nhiều nhất có thể, câu vẫn tự nhiên và vẫn yêu cầu hành động đó. removed_span = đoạn đã bỏ, chép nguyên văn từ "
         "câu gốc. Nếu bỏ đi làm các bước khác vô nghĩa thì trả skip kèm lý do.",
    "B-vague": "Viết lại câu yêu cầu để không còn chỉ rõ mục {value} trong danh sách: bỏ các từ phân biệt {words}, thay bằng "
               "cách nói mơ hồ (ví dụ 'một cái', 'cái đó') sao cho ít nhất 2 mục đều khớp. removed_span = đoạn đã bỏ/thay.",
    "B-specific": "Viết lại câu yêu cầu để chỉ rõ đúng mục {value}, dùng ít nhất một trong các từ {words}; giữ nguyên phần còn lại. "
                  "added_span = đoạn đã thêm (nguyên văn trong câu mới).",
}


def make_tasks(samples, tools, attested, n_c, n_bv, n_bs, seed) -> list[dict]:
    """Pick tasks spread over as many tools as possible (round robin over tools, seeded), one task per sample."""
    rng = random.Random(seed)
    pools: dict[str, dict[str, list]] = {"C": defaultdict(list), "B-vague": defaultdict(list), "B-specific": defaultdict(list)}
    for s in samples:
        for t in candidates_c(s, tools, attested) + candidates_b_vague(s, tools) + candidates_b_specific(s, tools, rng):
            pools[t["kind"]][t["tool"]].append((s, t))
    used, tasks = set(), []
    for kind, n in (("B-specific", n_bs), ("B-vague", n_bv), ("C", n_c)):
        by_tool = {k: rng.sample(v, len(v)) for k, v in sorted(pools[kind].items())}
        order = sorted(by_tool)
        rng.shuffle(order)
        picked = 0
        while picked < n and any(by_tool.values()):
            for tool in order:
                while by_tool[tool] and by_tool[tool][0][0]["id"] in used:
                    by_tool[tool].pop(0)
                if not by_tool[tool] or picked >= n:
                    continue
                s, t = by_tool[tool].pop(0)
                used.add(s["id"])
                picked += 1
                hist = [h["audio_text"] for h in s.get("history", []) if h["role"] == "user"][-2:]
                instr = INSTRUCTIONS[kind].format(param=t["param"], value=t["value"], tool=t["tool"],
                                                  words=", ".join(t.get("distinguishing_words") or t.get("add_words") or []))
                tasks.append({"task_id": f"{s['id']}#{kind}", "origin_id": s["id"], **t, "text": s["audio_text"],
                              "recent_user_history": hist, "instruction": instr})
    return tasks


# ---------------------------------------------------------------- build + checks

def _value_forms(v) -> list[str]:
    """Surface forms of a removed value that must not survive in the new text."""
    s = str(v)
    m = re.match(r"\d{4}-\d{2}-\d{2}T(\d{2}):(\d{2})", s)
    if m:  # datetime: the clock time
        h, mi = int(m.group(1)), int(m.group(2))
        forms = [f"{h}:{mi:02d}", f"{h}h{mi:02d}" if mi else f"{h}h", f"{h} giờ"]
        if h > 12:
            forms.append(f"{h - 12} giờ")
        return forms
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        n = int(v) if float(v).is_integer() else v
        forms = [str(n)]
        if isinstance(n, int) and n >= 1000:
            forms += [f"{n:,}".replace(",", "."), f"{n:,}"]
            if n % 1000 == 0:
                forms.append(f"{n // 1000} nghìn")
                forms.append(f"{n // 1000}k")
        return forms
    return []


def check_rewrite(task: dict, rw: dict) -> str | None:
    """Text-level checks; returns a rejection reason or None."""
    old, new = task["text"], (rw.get("new_text") or "").strip()
    if not new or norm(new) == norm(old):
        return "empty or unchanged text"
    if task["kind"] in ("C", "B-vague"):
        span = rw.get("removed_span") or ""
        if not span or norm(span) not in norm(old):
            return "removed_span not in original"
        if norm(span) in norm(new):
            return "removed_span still in new text"
        if task["kind"] == "C":
            for f in _value_forms(task["value"]):
                if re.search(rf"(?<![\d.,]){re.escape(norm(f))}(?![\d])", norm(new)):
                    return f"value still present ({f})"
        else:
            left = set(task["distinguishing_words"]) & words(new)
            if left:
                return f"distinguishing words still present ({', '.join(sorted(left))})"
        a, b = norm(old).replace(norm(span), " "), norm(new)  # original minus the removed span vs new text
    else:
        span = rw.get("added_span") or ""
        if not span or norm(span) not in norm(new):
            return "added_span not in new text"
        if not set(task["add_words"]) & words(new):
            return "no distinguishing word of the chosen entity"
        a, b = norm(new).replace(norm(span), " "), norm(old)  # new text minus the added span vs original
    sim = difflib.SequenceMatcher(None, " ".join(a.split()), b).ratio()
    if sim < MIN_SIMILARITY:
        return f"too different from the original (similarity {sim:.2f})"
    return None


def make_label(task: dict, s: dict) -> list[dict]:
    calls = s["label"]["tool_calls"]
    if task["kind"] in ("C", "B-vague"):
        return copy.deepcopy(calls[: task["write_index"]]) + [
            {"name": ASK, "arguments": {"tool_name": task["tool"], "params": [task["param"]]}}]
    return copy.deepcopy(calls[:-1]) + [{"name": task["tool"], "arguments": {task["param"]: task["value"]}}]


def replay(zt, origin_id: str, calls: list[dict], root) -> tuple[list, str | None]:
    """Run the label in the origin sample's ToolEnv: every call must succeed and not report done=false."""
    env = zt.ToolEnv("train", origin_id, root=str(root))
    results = []
    for c in calls:
        v = env.validate(c["name"], c["arguments"])
        if not v["ok"]:
            return results, f"schema: {c['name']}: {v['error']}"
        r = env.call(c["name"], c["arguments"])
        results.append(r)
        if isinstance(r, dict) and (r.get("ok") is False or r.get("done") is False):
            return results, f"call failed: {c['name']}: {json.dumps(r, ensure_ascii=False)[:120]}"
    return results, None


def build(tasks, rewrites, S, fit_ids, exclude_ids, drop_apps, root) -> tuple[list[dict], list[dict]]:
    zt = zaic_tools("train", root)
    rw_by = {r["task_id"]: r for r in rewrites}
    kept, report = [], []
    counter = Counter()
    for t in tasks:
        rw = rw_by.get(t["task_id"])
        reason = None
        if rw is None:
            reason = "no rewrite"
        elif rw.get("skip"):
            reason = f"skipped by writer: {rw['skip']}"
        elif t["origin_id"] not in fit_ids or t["origin_id"] in exclude_ids:
            reason = "origin not in fit or in an excluded (dev) split"
        else:
            reason = check_rewrite(t, rw)
        label, results = None, None
        if reason is None:
            s = S[t["origin_id"]]
            label = make_label(t, s)
            if used_apps(label) & drop_apps:
                reason = "uses a held-out app"
            else:
                results, reason = replay(zt, t["origin_id"], label, root)
        if reason is None:
            asks = [c for c in label if c["name"] == ASK]
            if asks and (label[-1]["name"] != ASK or len(asks) > 1 or len(asks[0]["arguments"]["params"]) != 1):
                reason = "ask not last / not exactly one param"
        report.append({"task_id": t["task_id"], "kind": t["kind"], "kept": reason is None, "reason": reason})
        if reason is not None:
            continue
        s = S[t["origin_id"]]
        counter[t["origin_id"]] += 1
        kept.append({"id": f"{t['origin_id']}#d{counter[t['origin_id']]}", "_origin": t["origin_id"], "_src": SRC,
                     "_kind": t["kind"], "audio": None, "audio_text": rw["new_text"].strip(),
                     "context": copy.deepcopy(s["context"]), "history": copy.deepcopy(s.get("history", [])),
                     "label": {"tool_calls": label, "tool_results": results}})
    return kept, report


def review_md(samples, S) -> str:
    lines = ["# Mẫu D để đọc tay", "",
             "Mỗi mục: câu gốc → câu viết lại, nhãn gốc → nhãn mới. Đánh dấu [x] nếu hợp lý, ghi lý do nếu không.", ""]
    for s in samples:
        o = S[s["_origin"]]
        lines += [f"## [ ] {s['id']} ({s['_kind']})", "",
                  f"- **Gốc:** {o['audio_text']}", f"- **Mới:** {s['audio_text']}",
                  f"- **Nhãn gốc:** `{json.dumps(o['label']['tool_calls'], ensure_ascii=False)}`",
                  f"- **Nhãn mới:** `{json.dumps(s['label']['tool_calls'], ensure_ascii=False)}`", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------- CLI

def _ids(paths) -> set[str]:
    return set().union(*[set(runinfo.read_ids(p)) for p in paths or []] or [set()])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("candidates")
    c.add_argument("--fit", required=True)
    c.add_argument("--exclude", nargs="*", help="id files never used as a source (dev splits)")
    c.add_argument("--n-c", type=int, default=30)
    c.add_argument("--n-b-vague", type=int, default=10)
    c.add_argument("--n-b-specific", type=int, default=10)
    c.add_argument("--seed", type=int, default=0)
    c.add_argument("--out", required=True)
    b = sub.add_parser("build")
    b.add_argument("--tasks", required=True)
    b.add_argument("--rewrites", required=True)
    b.add_argument("--fit", required=True)
    b.add_argument("--exclude", nargs="*", help="id files that must never be a source (dev splits)")
    b.add_argument("--drop-apps", help="json list of held-out apps that labels must not use")
    b.add_argument("--out", required=True)
    r = sub.add_parser("review")
    r.add_argument("--samples", required=True)
    r.add_argument("--out", required=True)
    for p in (c, b, r):
        p.add_argument("--root", default=str(DEFAULT_ROOT))
    a = ap.parse_args()

    S = {s["id"]: s for s in load_split("train", a.root)}
    tools = catalog_tools(load_catalog("train", a.root))
    if a.cmd == "candidates":
        fit = [S[i] for i in sorted(set(runinfo.read_ids(a.fit)) - _ids(a.exclude))]
        attested = attested_plain_params(fit, tools)
        tasks = make_tasks(fit, tools, attested, a.n_c, a.n_b_vague, a.n_b_specific, a.seed)
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        write_jsonl(a.out, tasks)
        print(json.dumps({"out": a.out, "tasks": len(tasks), "by_kind": Counter(t["kind"] for t in tasks),
                          "tools": len({t["tool"] for t in tasks}), "attested_plain_params": sorted(attested)},
                         ensure_ascii=False))
    elif a.cmd == "build":
        tasks, rewrites = load_jsonl(a.tasks), load_jsonl(a.rewrites)
        drop = set(json.loads(Path(a.drop_apps).read_text())) if a.drop_apps else set()
        kept, report = build(tasks, rewrites, S, set(runinfo.read_ids(a.fit)), _ids(a.exclude), drop, a.root)
        write_jsonl(a.out, kept)
        summary = {"tasks": len(tasks), "kept": len(kept), "kept_by_kind": Counter(r["kind"] for r in report if r["kept"]),
                   "rejected": Counter((r["reason"] or "").split(":")[0].split(" (")[0] for r in report if not r["kept"])}
        runinfo.write_json(Path(a.out).with_suffix(".report.json"), {
            "created": runinfo.now(), "args": vars(a), "summary": summary, "rows": report,
            "inputs_sha256": {k: runinfo.sha256_file(getattr(a, k)) for k in ("tasks", "rewrites", "fit")},
            "out_sha256": runinfo.sha256_file(a.out), "git": runinfo.git_state()})
        print(json.dumps(summary, ensure_ascii=False))
    else:
        samples = load_jsonl(a.samples)
        Path(a.out).write_text(review_md(samples, S), encoding="utf-8")
        print(json.dumps({"out": a.out, "samples": len(samples)}))


if __name__ == "__main__":
    main()
