"""Local scorer following the official formula.

Per sample:
  gold empty      -> 1 if submitted list empty else 0
  hash mismatch   -> 0
  otherwise       -> F1 between submitted and gold calls (P = M/len(sub), R = M/len(gold), 0 if M == 0)
A submitted call matches a gold call when the tool name is the same, every non-fuzzy argument is identical
and every fuzzy argument has token-F1 > 0.6 (lowercase + NFC). Each call matches at most one call; order ignored.

Points the official text leaves open (kept strict here, may differ from the server):
  * argument key sets must be equal (an extra optional argument breaks the match)
  * non-fuzzy values are compared exactly (no case folding); lists in order
  * fuzzy tokens = whitespace split after lowercase + NFC

Local protocol for incomplete files: a gold id with no prediction row scores 0 even when its gold is empty
("no answer" is not "answered with no call"); a repeated id or an id outside the split is an error.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import unicodedata

from .data import DEFAULT_ROOT, fuzzy_params, load_catalog, load_jsonl, load_split, zaic_tools


def _tokens(s) -> list[str]:
    return unicodedata.normalize("NFC", str(s).lower()).split()


def token_f1(a, b) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb:
        return 1.0
    common = sum((collections.Counter(ta) & collections.Counter(tb)).values())
    if common == 0:
        return 0.0
    p, r = common / len(ta), common / len(tb)
    return 2 * p * r / (p + r)


def calls_match(sub: dict, gold: dict, fuzzy: dict[str, set[str]]) -> bool:
    if sub.get("name") != gold.get("name"):
        return False
    sa, ga = sub.get("arguments") or {}, gold.get("arguments") or {}
    if set(sa) != set(ga):
        return False
    fz = fuzzy.get(gold["name"], set())
    for k, gv in ga.items():
        sv = sa[k]
        if k in fz and isinstance(gv, str) and isinstance(sv, str):
            if token_f1(sv, gv) <= 0.6:
                return False
        elif sv != gv:
            return False
    return True


def max_matching(sub: list[dict], gold: list[dict], fuzzy) -> int:
    """Maximum bipartite matching (each call matches at most one call)."""
    adj = [[j for j, g in enumerate(gold) if calls_match(s, g, fuzzy)] for s in sub]
    owner = [-1] * len(gold)

    def augment(i, seen):
        for j in adj[i]:
            if j in seen:
                continue
            seen.add(j)
            if owner[j] == -1 or augment(owner[j], seen):
                owner[j] = i
                return True
        return False

    return sum(augment(i, set()) for i in range(len(sub)))


def call_f1(sub: list[dict], gold: list[dict], fuzzy) -> float:
    if not gold:
        return 1.0 if not sub else 0.0
    m = max_matching(sub, gold, fuzzy)
    if m == 0:
        return 0.0
    p, r = m / len(sub), m / len(gold)
    return 2 * p * r / (p + r)


def score_sample(sub_calls, sub_hash, gold_calls, gold_hash, fuzzy) -> float:
    if not gold_calls:
        return 1.0 if not sub_calls else 0.0
    if sub_hash != gold_hash:
        return 0.0
    return call_f1(sub_calls, gold_calls, fuzzy)


def category(gold_calls: list[dict]) -> str:
    names = [c["name"] for c in gold_calls]
    if not names:
        return "out_of_scope"
    if "sys.ask_missing_info" in names:
        return "ask_missing"
    return "execute"


def gold_from_train(split: str, root, ids=None) -> dict[str, dict]:
    """{id: {"tool_calls", "state_hash"}}: gold hash = replay label.tool_calls on the initial state.
    Scorer-only: uses ToolEnv the same way the organisers do; never import this from agent code."""
    zt = zaic_tools(split, root)
    gold = {}
    for s in load_split(split, root):
        if ids is not None and s["id"] not in ids:
            continue
        env = zt.ToolEnv(split, s["id"], root=str(root))
        for c in s["label"]["tool_calls"]:
            env.call(c["name"], c["arguments"])
        gold[s["id"]] = {"tool_calls": s["label"]["tool_calls"], "state_hash": env.get_state_hash()}
    return gold


def evaluate(pred: dict[str, dict], gold: dict[str, dict], fuzzy) -> dict:
    """Scores every gold id. A gold id without a prediction row scores 0 (score, call-F1 and hash), also when
    its gold is empty. Prediction ids outside gold are ignored and counted in "extra"."""
    per_cat = collections.defaultdict(list)
    rows = []
    for sid, g in gold.items():
        cat = category(g["tool_calls"])
        p = pred.get(sid)
        if p is None:
            row = {"id": sid, "score": 0.0, "call_f1": 0.0, "hash_ok": False, "category": cat, "missing": True}
        else:
            s = score_sample(p["tool_calls"], p["state_hash"], g["tool_calls"], g["state_hash"], fuzzy)
            f1 = call_f1(p["tool_calls"], g["tool_calls"], fuzzy)
            hash_ok = (not g["tool_calls"] and not p["tool_calls"]) or (bool(g["tool_calls"]) and p["state_hash"] == g["state_hash"])
            row = {"id": sid, "score": s, "call_f1": f1, "hash_ok": hash_ok, "category": cat}
        per_cat[cat].append(row["score"])
        rows.append(row)
    n = len(rows)
    return {
        "n": n,
        "missing": sum(r.get("missing", False) for r in rows),
        "extra": len(set(pred) - set(gold)),
        "score": 100 * sum(r["score"] for r in rows) / max(n, 1),
        "call_f1": 100 * sum(r["call_f1"] for r in rows) / max(n, 1),
        "hash_acc": 100 * sum(r["hash_ok"] for r in rows) / max(n, 1),
        "by_category": {c: {"n": len(v), "score": 100 * sum(v) / len(v)} for c, v in sorted(per_cat.items())},
        "rows": rows,
    }


def load_predictions(path) -> dict[str, dict]:
    """{id: row}. A repeated id is an error: which of its lines would be scored is ambiguous."""
    rows = load_jsonl(path)
    dup = sorted(i for i, c in collections.Counter(r["id"] for r in rows).items() if c > 1)
    if dup:
        raise ValueError(f"{path}: {len(dup)} ids appear more than once, e.g. {dup[:5]}")
    return {r["id"]: r for r in rows}


def main():
    ap = argparse.ArgumentParser(description="score a submission.jsonl against train labels")
    ap.add_argument("pred")
    ap.add_argument("--split", default="train")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--ids", help="file with one sample id per line (default: every id in pred); "
                                  "ids missing from pred score 0")
    ap.add_argument("--rows", help="write per-sample rows to this jsonl")
    a = ap.parse_args()
    try:
        pred = load_predictions(a.pred)
    except ValueError as e:
        sys.exit(str(e))
    split_ids = {s["id"] for s in load_split(a.split, a.root)}
    for name, bad in (("predicted", set(pred) - split_ids),
                      ("--ids", (set(open(a.ids).read().split()) if a.ids else set()) - split_ids)):
        if bad:  # would silently drop out of the denominator
            sys.exit(f"{len(bad)} {name} ids are not in split {a.split}, e.g. {sorted(bad)[:5]}")
    ids = set(open(a.ids).read().split()) if a.ids else set(pred)
    gold = gold_from_train(a.split, a.root, ids)
    res = evaluate(pred, gold, fuzzy_params(load_catalog(a.split, a.root)))
    rows = res.pop("rows")
    if res["missing"]:
        print(f"warning: {res['missing']} of {res['n']} ids have no prediction and score 0", file=sys.stderr)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    if a.rows:
        with open(a.rows, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
