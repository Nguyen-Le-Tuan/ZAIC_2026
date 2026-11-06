"""ASR transcripts against train audio_text, with the errors that can change a state hash counted apart from WER.
Read-only over train; nothing here is used at inference.

  .venv/bin/python scripts/asr_quality.py asr/train_dev_random_turbo.jsonl asr/train_dev_random_pho.jsonl \
      --ids splits/dev_random.txt --json runs/asr_quality_dev_random.json

Per ASR file, separately for the final turn (the scored request) and the user history turns:
  wer          word error rate after lowercase + NFC + punctuation removed; wer_noacc also strips Vietnamese accents
  exact        share of utterances identical after that normalisation
Final turn only, from the gold label (docs/PIPELINE.md 3.2, team question Q9):
  slots        numbers, amounts and clock times of write-call arguments that are spoken in audio_text
               (vinum forms: digits and words both count) and are still spoken, in any form, in the ASR text
  negation     negation / cancel words of audio_text that the ASR text keeps
  query        read-call `query` arguments spoken in audio_text (accents ignored, as the search tools do) kept by ASR
Style (all turns): share of utterances with digits, punctuation, capital letters, in audio_text and in the ASR text.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate.askpolicy import norm  # noqa: E402
from lifemate.data import catalog_tools, load_catalog, load_jsonl, load_split  # noqa: E402
from lifemate.runinfo import read_ids, write_json  # noqa: E402
from lifemate.vinum import find_form, value_forms  # noqa: E402

NEG = ["đừng", "không", "chưa", "thôi", "khỏi", "hủy", "bỏ"]
PUNCT = re.compile(r"[^\w\s]")


def words(s: str, accents: bool = True) -> list[str]:
    s = norm(s).replace("huỷ", "hủy")
    return norm(PUNCT.sub(" ", s), strip_accents=not accents).split()


def edit_distance(a: list, b: list) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def spoken(text: str, forms) -> bool:
    """find_form on text, also with currency/unit letters glued to digits split off ("50.000đ" -> "50.000 đ")."""
    return find_form(text, forms) is not None or find_form(re.sub(r"(\d)([^\d\s.,:])", r"\1 \2", text), forms) is not None


def has_word(text: str, w: str, accents: bool = True) -> bool:
    return re.search(rf"(?<!\w){re.escape(w)}(?!\w)", " ".join(words(text, accents))) is not None


def turn_stats(pairs: list[tuple[str, str]]) -> dict:
    err = err_na = n = n_na = exact = 0
    for ref, hyp in pairs:
        r, h = words(ref), words(hyp)
        err += edit_distance(r, h)
        n += len(r)
        rn, hn = words(ref, accents=False), words(hyp, accents=False)
        err_na += edit_distance(rn, hn)
        n_na += len(rn)
        exact += r == h
    return {"utterances": len(pairs), "ref_words": n, "wer": round(100 * err / max(n, 1), 2),
            "wer_noacc": round(100 * err_na / max(n_na, 1), 2), "exact": round(100 * exact / max(len(pairs), 1), 1)}


def kind_of(v) -> str:
    if isinstance(v, str):
        return "time"
    return "amount" if abs(v) >= 1000 else "small_int"


def label_checks(s: dict, hyp: str, tools: dict, c: Counter, misses: list) -> None:
    ref = s["audio_text"]
    seen = set()
    for call in s["label"]["tool_calls"]:
        kind = tools.get(call["name"], {}).get("kind")
        for k, v in call["arguments"].items():
            if kind == "write" and not isinstance(v, (list, dict)):
                forms = value_forms(v)
                if forms and (k, str(v)) not in seen and spoken(ref, forms):
                    seen.add((k, str(v)))
                    g = kind_of(v)
                    c[f"slot {g} n"] += 1
                    ok = spoken(hyp, forms)
                    c[f"slot {g} kept"] += ok
                    if not ok and len(misses) < 40:
                        misses.append({"id": s["id"], "param": k, "value": v, "ref": ref, "hyp": hyp})
            if kind == "read" and k == "query" and isinstance(v, str) and v.strip():
                q = " ".join(words(v, accents=False))
                if q and q in " ".join(words(ref, accents=False)):
                    c["query n"] += 1
                    c["query kept"] += q in " ".join(words(hyp, accents=False))
    for w in NEG:
        if has_word(ref, w):
            c["negation n"] += 1
            c["negation kept"] += has_word(hyp, w)


def style(texts: list[str]) -> dict:
    n = max(len(texts), 1)
    return {"digits": round(100 * sum(bool(re.search(r"\d", t)) for t in texts) / n, 1),
            "punct": round(100 * sum(bool(PUNCT.search(t)) for t in texts) / n, 1),
            "upper": round(100 * sum(t != t.lower() for t in texts) / n, 1)}


def rate(c: Counter, key: str) -> dict:
    n = c[f"{key} n"]
    return {"n": n, "kept": c[f"{key} kept"], "pct": round(100 * c[f"{key} kept"] / n, 1) if n else None}


def evaluate(asr_file: str, items: list[dict], tools: dict) -> dict:
    hyp = {r["audio"]: r["text"] for r in load_jsonl(asr_file)}
    missing = [p for s in items for p in [s["audio"]] + [h["audio"] for h in s["history"] if h["role"] == "user"]
               if p not in hyp]
    if missing:
        sys.exit(f"{asr_file}: {len(missing)} wavs of the selected samples have no transcript (first: {missing[0]})")
    final = [(s["audio_text"], hyp[s["audio"]]) for s in items]
    hist = [(h["audio_text"], hyp[h["audio"]]) for s in items for h in s["history"] if h["role"] == "user"]
    c, misses = Counter(), []
    for s in items:
        label_checks(s, hyp[s["audio"]], tools, c, misses)
    every = final + hist
    return {"file": asr_file, "final": turn_stats(final), "history": turn_stats(hist),
            "slots": {g: rate(c, f"slot {g}") for g in ("amount", "time", "small_int")},
            "negation": rate(c, "negation"), "query": rate(c, "query"),
            "style": {"audio_text": style([r for r, _ in every]), "asr": style([h for _, h in every])},
            "empty": sum(not h.strip() for _, h in every),
            "slot_misses": misses}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("asr_files", nargs="+")
    ap.add_argument("--ids", required=True)
    ap.add_argument("--json")
    a = ap.parse_args()
    keep = set(read_ids(a.ids))
    items = [s for s in load_split("train") if s["id"] in keep]
    tools = catalog_tools(load_catalog("train"))
    res = {"ids": a.ids, "samples": len(items), "runs": [evaluate(f, items, tools) for f in a.asr_files]}
    for r in res["runs"]:
        s = r["slots"]
        print(f"{r['file']}: final WER {r['final']['wer']} (no accents {r['final']['wer_noacc']}), "
              f"history WER {r['history']['wer']}; slots kept amount {s['amount']['pct']}% time {s['time']['pct']}% "
              f"small int {s['small_int']['pct']}%; negation {r['negation']['pct']}%; query {r['query']['pct']}%")
    if a.json:
        write_json(a.json, res)


if __name__ == "__main__":
    main()
