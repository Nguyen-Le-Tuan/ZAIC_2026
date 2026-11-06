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

Phase 1b (docs/D_PHASE1B_2026-10-30.md): `candidates --filter-v2 --dedup 0.75 --dedup-against <earlier task files>`
drops sources a writer would skip (filter_v2_reason) and near-duplicate requests; `build` also rejects a rewrite
whose kept label prefix still uses words the rewrite removed (label_leak). Without these flags v1 output is unchanged.
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
from .vinum import find_form, value_forms

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

GENERIC = {"cái", "chiếc", "con", "gói", "nhắc", "bài", "việc", "đơn", "lịch", "xe", "máy", "tin", "nhóm", "mục", "người",
           "chị", "anh", "em", "cô", "chú", "bác", "của", "cho", "với", "và", "the", "plus", "premium", "gói"}


def is_answer_turn(s) -> bool:
    """A short request right after earlier turns is usually the answer to the assistant's question; its slot
    value belongs to the dialogue, so removing it does not make a natural "missing slot" request."""
    return bool(s.get("history")) and len(words(s["audio_text"])) <= 6


def spoken_in(text: str, v, spec: dict) -> bool:
    """Is slot value v actually said in the request (not computed, not an enum code)?"""
    if "enum" in spec or isinstance(v, bool):
        return False
    vals = v if isinstance(v, list) else [v]
    for x in vals:
        forms = value_forms(x)
        if forms:
            if not find_form(text, forms):
                return False
        elif isinstance(x, str):
            toks = {w for w in words(re.sub(r"[@._]", " ", x)) if len(w) >= 3}
            if not toks or not (toks & words(text)):
                return False
        else:
            return False
    return True


def c_filter_reason(s, task, tools) -> str | None:
    """Why a C candidate is not worth rewriting (None = keep)."""
    if is_answer_turn(s):
        return "answer to an earlier turn"
    spec = tools[task["tool"]]["parameters"]["properties"].get(task["param"], {})
    if not spoken_in(s["audio_text"], task["value"], spec):
        return "value not spoken (computed, enum or from history)"
    return None


def candidates_c(s, tools, attested, prefilter: bool = True) -> list[dict]:
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
        t = {"kind": "C", "write_index": w, "tool": c["name"], "param": p, "value": v,
             "param_desc": tools[c["name"]]["parameters"]["properties"].get(p, {}).get("description", "")}
        if prefilter and c_filter_reason(s, t, tools):
            continue
        out.append(t)
    return out


def _list_pick(calls, results, upto: int, value) -> tuple[list[dict], int] | None:
    """The last read before `upto` whose entity list (>=2) contains id `value`: (entities, index of value)."""
    for i in range(upto - 1, -1, -1):
        ents = entities(results[i])
        ids = [str(e.get("id")) for e in ents]
        if len(ents) >= 2 and str(value) in ids:
            return ents, ids.index(str(value))
    return None


def candidates_b_vague(s, tools, prefilter: bool = True) -> list[dict]:
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
        toks = re.split(r"[^\w]+", norm(s["audio_text"]))
        if prefilter and any(toks.count(w) > 1 for w in dist):  # the word also belongs to another part of the request
            continue
        out.append({"kind": "B-vague", "write_index": w, "tool": c["name"], "param": p, "value": v,
                    "distinguishing_words": dist, "entities": ents})
    return out


def candidates_b_specific(s, tools, rng, prefilter: bool = True) -> list[dict]:
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
            content = text - GENERIC if prefilter else text
            options = [k for k in range(len(ents)) if _unique_words(ents, k) and _ent_words(ents[k]) & content]
            if not options:
                return []
            k = rng.choice(options)
            return [{"kind": "B-specific", "tool": tool, "param": p, "value": ents[k].get("id"),
                     "add_words": sorted(_unique_words(ents, k)), "entities": ents}]
    return []


# ---------------------------------------------------------------- source filter v2 (phase 1b)
# Rules for the skip reasons of D v1 that a rule can catch (docs/D_PHASE1_2026-10-30.md section 2). Each rule
# returns its own reason so its hits can be counted against the writer's decisions.

IF_THEN = re.compile(r"(?<!\w)(nếu|thì)(?!\w)")
ELSE = re.compile(r"(?<!\w)(không thì|hổng thì|hông thì|còn không|nếu không)(?!\w)")
NUMBER = re.compile(r"\d|(?<!\w)(một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|trăm|nghìn|ngàn|triệu|rưỡi)(?!\w)")
SELF_CORRECTION = re.compile(r"(?<!\w)(à không|à nhầm|à thôi|mà thôi|à khoan|khoan|không phải|ý lộn|nhầm rồi)(?!\w)")
HISTORY_DEIXIS = re.compile(r"(?<!\w)(hồi nãy|lúc nãy|ban nãy|vừa nãy|qua đấy|qua đó|ra đấy|chỗ đó|chỗ đấy|lần trước|"
                            r"như cũ|y như|như anh dặn|như chị dặn|như em dặn|như đã dặn|số đó|số đấy)(?!\w)")
TIME_ANAPHORA = re.compile(r"(?<!\w)(giờ đó|giờ đấy|giờ ấy|lúc đó|lúc đấy)(?!\w)")
# words that single nothing out when spoken: pronouns, time of day, function words
WEAK = {"anh", "chị", "em", "cô", "chú", "bác", "con", "ông", "bà", "có", "không", "tối", "sáng", "chiều", "trưa", "nay",
        "mai", "cái", "một", "được", "ra", "đi", "là", "cho", "với", "mới"}


def _clauses(text: str) -> list[str]:
    return [c for c in re.split(r"[,.;:!?…]+", norm(text)) if c.strip()]


def _str_tokens(x) -> set[str]:
    return {w for w in words(re.sub(r"[@._]", " ", str(x))) if len(w) >= 3} - WEAK


def _target_clauses(text: str, task: dict) -> list[str]:
    """Clauses of the request that carry the targeted value (C) or distinguishing words (B-vague)."""
    cl = _clauses(text)
    if task["kind"] == "C":
        vals = task["value"] if isinstance(task["value"], list) else [task["value"]]
        hit = [c for c in cl if any((find_form(c, value_forms(x)) if value_forms(x) else _str_tokens(x) & words(c))
                                    for x in vals)]
    else:
        hit = [c for c in cl if set(task.get("distinguishing_words", [])) & words(c)]
    return hit or cl


def _args_words(calls: list[dict]) -> set[str]:
    """Words of every string argument of the calls."""
    return set().union(*[words(x) for c in calls for x in _atoms(c["arguments"]) if isinstance(x, str)] or [set()])


def _count_form(text: str, forms) -> int:
    """Non-overlapping mentions of a value (longest form first: "một trăm hai mươi nghìn" counts once)."""
    t, taken = norm(text), []
    for f in sorted((f for f in forms if f), key=len, reverse=True):
        for m in re.finditer(rf"(?<![\w.,]){re.escape(f)}(?![\w])", t):
            if not any(m.start() < e and s < m.end() for s, e in taken):
                taken.append((m.start(), m.end()))
    return len(taken)


def filter_v2_reason(s: dict, task: dict, tools: dict) -> str | None:
    """Why a candidate (C or B-vague) is not worth rewriting under the v2 source rules (None = keep)."""
    calls = s["label"]["tool_calls"]
    w, v, kind = task["write_index"], task["value"], task["kind"]
    text = s["audio_text"]
    cl = _clauses(text)
    tc = _target_clauses(text, task)
    hist = words(" ".join([h["audio_text"] for h in s.get("history", []) if h["role"] == "user"][-2:]))
    if s.get("history") and any(HISTORY_DEIXIS.search(c) for c in tc):
        return "v2: target refers back to the dialogue"
    if sum(c["name"] == task["tool"] for c in calls) > 1:
        return "v2: target tool called more than once"
    others = [c for i, c in enumerate(calls) if i != w]
    if any(str(v) in _atoms(c["arguments"]) for c in others):
        return "v2: target value also used by another call"
    if kind == "C":
        forms = value_forms(v) if not isinstance(v, list) else set()
        if forms:
            if _count_form(text, forms) > 1:
                return "v2: value said twice"
            # if/else on the same slot: "mưa thì bảy giờ, không thì chín giờ"
            for i, c in enumerate(cl):
                if c in tc:
                    near = [cl[j] for j in (i - 1, i + 1) if 0 <= j < len(cl)]
                    if any((ELSE.search(c) or ELSE.search(n)) and NUMBER.search(n) for n in near):
                        return "v2: alternative value in an if/else"
            if any(find_form(x, forms) for c in others for x in _atoms(c["arguments"]) if isinstance(x, str)):
                return "v2: target value also said in another call"
            if TIME_ANAPHORA.search(norm(text)) and re.search(r"\d{2}:\d{2}", str(v)):
                return "v2: time referred to again ('giờ đó')"
        elif isinstance(v, str) and _str_tokens(v) & hist:
            return "v2: value in the dialogue history"
        return None
    if is_answer_turn(s):
        return "v2: answer to an earlier turn"
    if SELF_CORRECTION.search(norm(text)):
        return "v2: self-correction in the request"
    ents, k = task["entities"], [str(e.get("id")) for e in task["entities"]].index(str(v))
    strong = set(task["distinguishing_words"]) - WEAK
    if not strong:
        return "v2: only weak distinguishing words"
    if strong & _args_words(calls[:w]):  # the label prefix (kept as is) would still name the entity
        return "v2: distinguishing word used by an earlier call"
    if (_unique_words(ents, k) - WEAK) & hist:
        return "v2: entity named in the dialogue history"
    other = set().union(*[_unique_words(ents, j) for j in range(len(ents)) if j != k] or [set()]) - WEAK - GENERIC
    if any(IF_THEN.search(c) for c in tc) and other & words(text):
        return "v2: choice between listed entities depends on a condition"
    name = norm(ent_name(ents[k]) or "")
    same = [e for j, e in enumerate(ents) if j != k and norm(ent_name(e) or "") == name]
    if name and same and (words(name) - WEAK) & words(text):
        return "v2: same-name entities and the name is said (would be type A)"
    return None


def label_leak(task: dict, new_text: str, label: list[dict]) -> str | None:
    """Words the rewrite removed that the kept label prefix still uses (e.g. a search query)."""
    gone = (words(task["text"]) - words(new_text)) - WEAK
    hit = gone & _args_words(label[:-1])
    return f"label uses words the rewrite removed ({', '.join(sorted(hit))})" if hit else None


def _too_similar(text: str, seen: list[str], th: float) -> bool:
    t = norm(text)
    return any(difflib.SequenceMatcher(None, t, x).ratio() >= th for x in seen)


INSTRUCTIONS = {
    "C": "Viết lại câu yêu cầu, bỏ ĐÚNG thông tin cho tham số {param} (= {value}) của {tool}; giữ nguyên phần còn lại "
         "nhiều nhất có thể, câu vẫn tự nhiên và vẫn yêu cầu hành động đó. removed_span = đoạn đã bỏ, chép nguyên văn từ "
         "câu gốc. Nếu bỏ đi làm các bước khác vô nghĩa thì trả skip kèm lý do.",
    "B-vague": "Viết lại câu yêu cầu để không còn chỉ rõ mục {value} trong danh sách: bỏ các từ phân biệt {words}, thay bằng "
               "cách nói mơ hồ (ví dụ 'một cái', 'cái đó') sao cho ít nhất 2 mục đều khớp. removed_span = đoạn đã bỏ/thay.",
    "B-specific": "Viết lại câu yêu cầu để chỉ rõ đúng mục {value}, dùng ít nhất một trong các từ {words}; giữ nguyên phần còn lại. "
                  "added_span = đoạn đã thêm (nguyên văn trong câu mới).",
}


def precedents(samples, tools) -> set[tuple]:
    """(ask type, tool, param) combinations that real fit asks attest."""
    out = set()
    for s in samples:
        t = ask_type(s, tools)
        if t in ("B", "C"):
            a = s["label"]["tool_calls"][-1]["arguments"]
            out.add((t, a["tool_name"], a["params"][0]))
    return out


def make_tasks(samples, tools, attested, n_c, n_bv, n_bs, seed, max_per_tool=None, require_precedent=False,
               filter_v2=False, dedup=None, dedup_seed=None, stats=None) -> list[dict]:
    """Pick tasks spread over as many tools as possible (round robin over tools, seeded), one task per sample,
    at most max_per_tool per (kind, tool). Each task records whether a real ask attests its (type, tool, param).
    filter_v2: drop candidates that filter_v2_reason rejects. dedup: skip a pick whose request is at least this
    similar to one already picked (or given in dedup_seed {(kind, tool): [texts]}) for the same (kind, tool).
    stats (a Counter) receives the drop counts."""
    rng = random.Random(seed)
    stats = stats if stats is not None else Counter()
    prec = precedents(samples, tools)
    pools: dict[str, dict[str, list]] = {"C": defaultdict(list), "B-vague": defaultdict(list), "B-specific": defaultdict(list)}
    for s in samples:
        for t in candidates_c(s, tools, attested) + candidates_b_vague(s, tools) + candidates_b_specific(s, tools, rng):
            t["precedent"] = ("C" if t["kind"] == "C" else "B", t["tool"], t["param"]) in prec
            if require_precedent and not t["precedent"] and t["kind"] != "B-specific":
                continue
            if filter_v2 and t["kind"] != "B-specific":
                r = filter_v2_reason(s, t, tools)
                if r:
                    stats[r] += 1
                    continue
            pools[t["kind"]][t["tool"]].append((s, t))
    seen = defaultdict(list, {k: [norm(x) for x in v] for k, v in (dedup_seed or {}).items()})
    used, tasks = set(), []
    for kind, n in (("B-specific", n_bs), ("B-vague", n_bv), ("C", n_c)):
        by_tool = {k: rng.sample(v, len(v))[:max_per_tool] for k, v in sorted(pools[kind].items())}
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
                if dedup and _too_similar(s["audio_text"], seen[(kind, tool)], dedup):
                    stats["dedup: near-duplicate request"] += 1
                    continue
                seen[(kind, tool)].append(norm(s["audio_text"]))
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
            for x in (task["value"] if isinstance(task["value"], list) else [task["value"]]):
                hit = find_form(new, value_forms(x))
                if hit:
                    return f"value still present ({hit})"
                if isinstance(x, str) and not value_forms(x):  # e-mail, address, name: no token of it may remain
                    left = {w for w in words(re.sub(r"[@._]", " ", x)) if len(w) >= 3} & words(new) & words(old)
                    if left:
                        return f"value still present ({', '.join(sorted(left))})"
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


def _ent_brief(e: dict) -> str:
    keys = [k for k in e if k not in ("id",) and isinstance(e[k], (str, int, float)) and not isinstance(e[k], bool)]
    return "; ".join(f"{k}={e[k]}" for k in keys[:6])


def judge_tasks(tasks, rewrites) -> list[dict]:
    """Second, meaning-level read of each rewrite (R7 of the 30/10 review). The judge sees only the NEW request and,
    for B, the listed entities; never the original request or which entity/value was targeted."""
    rw_by = {r["task_id"]: r for r in rewrites if r.get("new_text")}
    out = []
    for t in tasks:
        rw = rw_by.get(t["task_id"])
        if rw is None:
            continue
        if t["kind"] == "C":
            out.append({"task_id": t["task_id"], "kind": "C", "new_text": rw["new_text"],
                        "question": f"Yêu cầu có còn cho biết giá trị của tham số '{t['param']}' ({t.get('param_desc') or ''}) "
                                    f"cho {t['tool']} không? Trả slot_given true/false."})
        else:
            out.append({"task_id": t["task_id"], "kind": t["kind"], "new_text": rw["new_text"],
                        "question": "Những mục nào trong danh sách khớp với yêu cầu? Trả matches = danh sách id.",
                        "options": [{"id": e.get("id"), "about": _ent_brief(e)} for e in t["entities"]]})
    return out


def judge_reason(task: dict, j: dict | None) -> str | None:
    if j is None:
        return "judge: no judgment"
    if task["kind"] == "C":
        return "judge: slot still given" if j.get("slot_given") else None
    matches = [str(x) for x in j.get("matches", [])]
    if task["kind"] == "B-vague":
        if str(task["value"]) not in matches:
            return "judge: target entity no longer fits"
        return None if len(matches) >= 2 else "judge: still singles out one entity"
    return None if matches == [str(task["value"])] else "judge: does not single out the chosen entity"


def build(tasks, rewrites, S, fit_ids, exclude_ids, drop_apps, root, judgments=None) -> tuple[list[dict], list[dict]]:
    zt = zaic_tools("train", root)
    rw_by = {r["task_id"]: r for r in rewrites}
    jd = {j["task_id"]: j for j in judgments} if judgments is not None else None
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
            if reason is None and jd is not None:
                reason = judge_reason(t, jd.get(t["task_id"]))
        label, results = None, None
        if reason is None:
            s = S[t["origin_id"]]
            label = make_label(t, s)
            if used_apps(label) & drop_apps:
                reason = "uses a held-out app"
            elif label_leak(t, rw["new_text"], label):
                reason = label_leak(t, rw["new_text"], label)
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


def split_by_origin(samples, eval_frac: float) -> tuple[list, list]:
    """Stable split on the origin id (sha256), so a D-eval contrast set never shares an origin with D-train."""
    def bucket(o):
        return int(runinfo.sha256_bytes(o.encode())[:8], 16) / 0xFFFFFFFF
    ev = [x for x in samples if bucket(x["_origin"]) < eval_frac]
    tr = [x for x in samples if bucket(x["_origin"]) >= eval_frac]
    return tr, ev


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
    c.add_argument("--max-per-tool", type=int, help="cap per (kind, tool) so a few tools do not dominate")
    c.add_argument("--require-precedent", action="store_true", help="only (type, tool, param) a real fit ask attests")
    c.add_argument("--filter-v2", action="store_true", help="source filter v2 (phase 1b): drop sources a writer would skip")
    c.add_argument("--dedup", type=float, help="skip a request this similar (difflib ratio) to one already picked")
    c.add_argument("--dedup-against", nargs="*", help="earlier task files whose requests count as already picked")
    c.add_argument("--out", required=True)
    b = sub.add_parser("build")
    b.add_argument("--tasks", required=True)
    b.add_argument("--rewrites", required=True)
    b.add_argument("--fit", required=True)
    b.add_argument("--exclude", nargs="*", help="id files that must never be a source (dev splits)")
    b.add_argument("--drop-apps", help="json list of held-out apps that labels must not use")
    b.add_argument("--judgments", help="R7 meaning-level judgments ({task_id, slot_given} or {task_id, matches})")
    b.add_argument("--out", required=True)
    jt = sub.add_parser("judge-tasks", help="tasks for the meaning-level second read (new text only)")
    jt.add_argument("--tasks", required=True)
    jt.add_argument("--rewrites", required=True)
    jt.add_argument("--out", required=True)
    sp = sub.add_parser("split", help="D-train / D-eval by origin (the eval part is a contrast set, never trained on)")
    sp.add_argument("--samples", required=True)
    sp.add_argument("--eval-frac", type=float, default=0.2)
    sp.add_argument("--out-train", required=True)
    sp.add_argument("--out-eval", required=True)
    r = sub.add_parser("review")
    r.add_argument("--samples", required=True)
    r.add_argument("--out", required=True)
    for p in (c, b, sp, r, jt):
        p.add_argument("--root", default=str(DEFAULT_ROOT))
    a = ap.parse_args()

    S = {s["id"]: s for s in load_split("train", a.root)}
    tools = catalog_tools(load_catalog("train", a.root))
    if a.cmd == "candidates":
        fit = [S[i] for i in sorted(set(runinfo.read_ids(a.fit)) - _ids(a.exclude))]
        attested = attested_plain_params(fit, tools)
        seed_texts = defaultdict(list)
        for f in a.dedup_against or []:
            for t in load_jsonl(f):
                seed_texts[(t["kind"], t["tool"])].append(t["text"])
        stats = Counter()
        tasks = make_tasks(fit, tools, attested, a.n_c, a.n_b_vague, a.n_b_specific, a.seed, a.max_per_tool,
                           a.require_precedent, a.filter_v2, a.dedup, seed_texts, stats)
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        write_jsonl(a.out, tasks)
        print(json.dumps({"out": a.out, "tasks": len(tasks), "by_kind": Counter(t["kind"] for t in tasks),
                          "tools": len({t["tool"] for t in tasks}), "dropped": dict(sorted(stats.items())),
                          "attested_plain_params": sorted(attested)}, ensure_ascii=False))
    elif a.cmd == "build":
        tasks, rewrites = load_jsonl(a.tasks), load_jsonl(a.rewrites)
        drop = set(json.loads(Path(a.drop_apps).read_text())) if a.drop_apps else set()
        judg = load_jsonl(a.judgments) if a.judgments else None
        kept, report = build(tasks, rewrites, S, set(runinfo.read_ids(a.fit)), _ids(a.exclude), drop, a.root, judg)
        write_jsonl(a.out, kept)
        summary = {"tasks": len(tasks), "kept": len(kept), "kept_by_kind": Counter(r["kind"] for r in report if r["kept"]),
                   "rejected": Counter((r["reason"] or "").split(":")[0].split(" (")[0] for r in report if not r["kept"])}
        runinfo.write_json(Path(a.out).with_suffix(".report.json"), {
            "created": runinfo.now(), "args": vars(a), "summary": summary, "rows": report,
            "inputs_sha256": {k: runinfo.sha256_file(getattr(a, k)) for k in ("tasks", "rewrites", "fit", "judgments") if getattr(a, k)},
            "out_sha256": runinfo.sha256_file(a.out), "git": runinfo.git_state()})
        print(json.dumps(summary, ensure_ascii=False))
    elif a.cmd == "judge-tasks":
        jts = judge_tasks(load_jsonl(a.tasks), load_jsonl(a.rewrites))
        write_jsonl(a.out, jts)
        print(json.dumps({"out": a.out, "judge_tasks": len(jts)}))
    elif a.cmd == "split":
        tr, ev = split_by_origin(load_jsonl(a.samples), a.eval_frac)
        write_jsonl(a.out_train, tr)
        write_jsonl(a.out_eval, ev)
        print(json.dumps({"train": len(tr), "eval": len(ev), "eval_by_kind": Counter(x["_kind"] for x in ev)}))
    else:
        samples = load_jsonl(a.samples)
        Path(a.out).write_text(review_md(samples, S), encoding="utf-8")
        print(json.dumps({"out": a.out, "samples": len(samples)}))


if __name__ == "__main__":
    main()
