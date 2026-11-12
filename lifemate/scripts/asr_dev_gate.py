"""Dev gate for beam search on the final user turn's ASR: a greedy and a beam ASR file of the same train samples,
scored against each sample's gold audio_text. Read-only over train; nothing here is used at inference.

  .venv/bin/python scripts/asr_dev_gate.py --greedy asr/train_dev_union_phoft_v8.jsonl \
      --beam asr/train_dev_union_phoft_v8_beam4.jsonl --split-ids splits/dev_random.txt splits/dev_lao.txt \
      --md runs/asr_beam_gate.md --json runs/asr_beam_gate.json

Final turn only (each sample's own `audio` against its `audio_text`), pooled over the union of the --split-ids files
(a sample in two files counts once) and per file. Both files get the same normalisation (scripts/asr_quality.py
words(): lowercase, NFC, punctuation removed, "huỷ" written "hủy") and the same alignment (minimum edits; ties take
the diagonal, then a deletion, then an insertion):
  wer            word edits / reference words, in % (asr_quality.py's final-turn wer)
  rare errors    edits on rare words: non-number words seen fewer than --rare-below (3) times in the audio_text of
                 every user turn of the fit samples (train samples in none of the --split-ids files: the ASR's
                 fine-tuning set). A substitution or deletion counts by its reference word, an insertion by its word.
  number errors  the same for number words: tokens with a digit, or a Vietnamese numeral of NUM_WORDS ("không" is
                 left out: in these requests it is nearly always the negation)
  seconds        the final-turn record's ASR seconds (mean, p95): per-wav latency when the run used --batch-size 1
  changed        samples whose final-turn transcript differs between the files (raw text; and after normalisation)
Also: samples better / worse by edits (two-sided sign test), a paired bootstrap 95% interval of the WER change, and
asr_quality.py's label checks (slot values, negation, query words still spoken in the final turn).

Gate fixed before the run: KEEP the beam file only if (a) final-turn WER drops by >= 0.3 absolute, (b) rare + number
errors do not rise, (c) the paired agent score on dev_lao (run separately, not here) and (d) p95 seconds rises by
<= 1 s. The verdict printed here covers (a), (b) and (d), on the pooled samples.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from asr_quality import edit_distance, label_checks, rate, turn_stats, words  # noqa: E402
from lifemate.data import DEFAULT_ROOT, catalog_tools, load_catalog, load_jsonl, load_split  # noqa: E402
from lifemate.runinfo import git_state, now, percentile, read_ids, sha256_file, write_json  # noqa: E402

NUM_WORDS = {"một", "mốt", "hai", "ba", "bốn", "tư", "năm", "lăm", "nhăm", "sáu", "bảy", "bẩy", "tám", "chín",
             "mười", "mươi", "chục", "trăm", "linh", "lẻ", "nghìn", "ngàn", "triệu", "tỷ", "tỉ", "rưỡi"}
DIGIT = re.compile(r"\d")
GATE = {"a_wer_drop_min": 0.3, "d_p95_rise_max_s": 1.0}


def is_number(w: str) -> bool:
    return bool(DIGIT.search(w)) or w in NUM_WORDS


def align(r: list[str], h: list[str]) -> list[tuple[str, str | None, str | None]]:
    """[(op, reference word, hypothesis word)] with op "=", "sub", "del" or "ins"; a minimum-edit alignment."""
    n, m = len(r), len(h)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i - 1][j - 1] + (r[i - 1] != h[j - 1]), d[i - 1][j] + 1, d[i][j - 1] + 1)
    ops, i, j = [], n, m
    while i or j:
        if i and j and d[i][j] == d[i - 1][j - 1] + (r[i - 1] != h[j - 1]):
            ops.append(("=" if r[i - 1] == h[j - 1] else "sub", r[i - 1], h[j - 1]))
            i, j = i - 1, j - 1
        elif i and d[i][j] == d[i - 1][j] + 1:
            ops.append(("del", r[i - 1], None))
            i -= 1
        else:
            ops.append(("ins", None, h[j - 1]))
            j -= 1
    return ops[::-1]


def utterance(ref: str, hyp: str, rare, rare_fv) -> dict:
    """Edits of one final turn, with those on rare words and on number words counted apart (rare_fv: the rare test
    with the final-turn-only vocabulary, a sensitivity check)."""
    r, h = words(ref), words(hyp)
    edits = [rw if op != "ins" else hw for op, rw, hw in align(r, h) if op != "="]
    assert len(edits) == edit_distance(r, h)
    return {"ref_words": len(r), "edits": len(edits), "norm": h,
            "rare_err": sum(1 for w in edits if not is_number(w) and rare(w)),
            "rare_err_fv": sum(1 for w in edits if not is_number(w) and rare_fv(w)),
            "num_err": sum(1 for w in edits if is_number(w)),
            "rare_ref": sum(1 for w in r if not is_number(w) and rare(w)),
            "num_ref": sum(1 for w in r if is_number(w))}


def sign_test(better: int, worse: int) -> float:
    """Two-sided exact binomial p-value of better vs worse (ties dropped)."""
    n = better + worse
    if n == 0:
        return 1.0
    k = min(better, worse)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def bootstrap_wer_drop(g: list[dict], b: list[dict], reps: int = 2000, seed: int = 0) -> list[float]:
    """95% interval of WER(greedy) - WER(beam) in points, resampling samples (paired)."""
    rng = random.Random(seed)
    n, out = len(g), []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        words_n = sum(g[i]["ref_words"] for i in idx) or 1
        out.append(100 * (sum(g[i]["edits"] for i in idx) - sum(b[i]["edits"] for i in idx)) / words_n)
    out.sort()
    return [round(percentile(out, .025), 2), round(percentile(out, .975), 2)]


def summary(us: list[dict], secs: list[float], sample_secs: list[float]) -> dict:
    words_n = sum(u["ref_words"] for u in us)
    rare_e, num_e = sum(u["rare_err"] for u in us), sum(u["num_err"] for u in us)
    return {"samples": len(us), "ref_words": words_n, "edits": sum(u["edits"] for u in us),
            "wer": round(100 * sum(u["edits"] for u in us) / max(words_n, 1), 2),
            "exact": round(100 * sum(u["edits"] == 0 for u in us) / max(len(us), 1), 1),
            "rare_err": rare_e, "rare_ref": sum(u["rare_ref"] for u in us),
            "num_err": num_e, "num_ref": sum(u["num_ref"] for u in us), "rare_plus_num_err": rare_e + num_e,
            "rare_err_final_vocab": sum(u["rare_err_fv"] for u in us),
            "sec_mean": round(sum(secs) / max(len(secs), 1), 4), "sec_p95": round(percentile(secs, .95), 4),
            "sec_max": round(max(secs, default=0.0), 4),
            "sample_sec_mean": round(sum(sample_secs) / max(len(sample_secs), 1), 4),
            "sample_sec_p95": round(percentile(sample_secs, .95), 4)}


def compare(items: list[dict], hyp_g: dict, hyp_b: dict, rare, rare_fv, tools: dict) -> dict:
    ug, ub, sg, sb, label = [], [], [], [], {"greedy": (Counter(), []), "beam": (Counter(), [])}
    tg, tb = [], []  # ASR seconds of the whole sample: final turn + user history turns
    for s in items:
        wavs = [s["audio"]] + [h["audio"] for h in s["history"] if h["role"] == "user"]
        for us, secs, tot, hyp, key in ((ug, sg, tg, hyp_g, "greedy"), (ub, sb, tb, hyp_b, "beam")):
            tot.append(sum(hyp[p]["seconds"] for p in wavs))
            row = hyp[s["audio"]]
            u = utterance(s["audio_text"], row["text"], rare, rare_fv)
            u["id"], u["text"] = s["id"], row["text"]
            us.append(u)
            secs.append(row["seconds"])
            label_checks(s, row["text"], tools, *label[key])
    better = sum(b["edits"] < g["edits"] for g, b in zip(ug, ub))
    worse = sum(b["edits"] > g["edits"] for g, b in zip(ug, ub))
    G, B = summary(ug, sg, tg), summary(ub, sb, tb)
    labels = {k: {"slot_" + g: rate(c, f"slot {g}") for g in ("amount", "time", "small_int")} |
              {"negation": rate(c, "negation"), "query": rate(c, "query")} for k, (c, _) in label.items()}
    return {"greedy": G, "beam": B,
            "changed_raw": sum(g["text"] != b["text"] for g, b in zip(ug, ub)),
            "changed_norm": sum(g["norm"] != b["norm"] for g, b in zip(ug, ub)),
            "better": better, "worse": worse, "sign_test_p": round(sign_test(better, worse), 4),
            "wer_drop": round(100 * (G["edits"] - B["edits"]) / max(G["ref_words"], 1), 4),
            "wer_drop_ci95": bootstrap_wer_drop(ug, ub),
            "labels": labels,
            "_utts": (ug, ub)}


def gate(c: dict) -> dict:
    G, B = c["greedy"], c["beam"]
    a = c["wer_drop"] >= GATE["a_wer_drop_min"]
    b = B["rare_plus_num_err"] <= G["rare_plus_num_err"]
    d = round(B["sec_p95"] - G["sec_p95"], 4) <= GATE["d_p95_rise_max_s"]
    return {"a": a, "b": b, "d": d, "a_b_d": a and b and d}


def md_report(res: dict, examples: list[str]) -> str:
    P = res["pooled"]
    gt = res["gate"]
    ok = lambda x: "pass" if x else "FAIL"  # noqa: E731
    lines = [
        "# ASR beam search on the final turn: dev gate",
        "",
        f"Generated {res['finished']} by `lifemate/scripts/asr_dev_gate.py` (branch asr-beam, {res['git'].get('commit', '?')[:7]}).",
        "",
        f"- Greedy: `{res['greedy']}` (sha256 {res['greedy_sha256'][:12]})",
        f"- Beam:   `{res['beam']}` (sha256 {res['beam_sha256'][:12]})",
        f"- Samples: {P['greedy']['samples']} unique train samples = union of "
        + ", ".join(f"{k} ({v['greedy']['samples']})" for k, v in res["per_split"].items())
        + (f"; {res['overlap']} samples are in more than one split file (the {res['ids_sum']} ids of the files count "
           "them twice)." if res["overlap"] else "."),
        f"- Gold: each sample's final-turn `audio_text`. Normalisation (both files): lowercase, NFC, punctuation removed, "
        "\"huỷ\"→\"hủy\" (scripts/asr_quality.py `words`).",
        f"- Rare word: non-number word seen < {res['rare_below']} times in the audio_text of all user turns of the "
        f"{res['fit_samples']} fit samples (train samples in none of the split files; {res['fit_tokens']} tokens, "
        f"{res['fit_vocab']} types){res['fit_check']}. Number word: token with a digit, or one of "
        f"{', '.join(sorted(NUM_WORDS))} (\"không\" excluded: negation).",
        "- Edits on a class: a substitution/deletion counts by its reference word, an insertion by its inserted word.",
        "- ASR s: the final-turn record's `seconds` (per-wav decode time when the run used --batch-size 1); sample ASR s: "
        "the sum over the sample's final and user history turns (what enters the 30 s budget).",
        f"- History-turn rows identical in both files: {res['history_identical']}/{res['history_rows']}"
        " (all expected when the beam file copies the greedy history rows).",
        "",
        "## Final-turn metrics",
        "",
        "| set | file | WER % | exact % | rare-word err (rare ref words) | number-word err (number ref words) | rare+number | ASR s mean | ASR s p95 | ASR s max | sample ASR s mean / p95 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, c in [("pooled", P)] + list(res["per_split"].items()):
        for k in ("greedy", "beam"):
            x = c[k]
            lines.append(f"| {name} (n={x['samples']}) | {k} | {x['wer']:.2f} | {x['exact']:.1f} | {x['rare_err']} ({x['rare_ref']}) | "
                         f"{x['num_err']} ({x['num_ref']}) | {x['rare_plus_num_err']} | {x['sec_mean']:.3f} | {x['sec_p95']:.3f} | {x['sec_max']:.3f} | "
                         f"{x['sample_sec_mean']:.3f} / {x['sample_sec_p95']:.3f} |")
    lines += ["", "| set | WER drop (greedy − beam), 95% CI | samples changed raw / normalised | better / worse (sign test p) | Δ rare+number err | Δ p95 s |",
              "|---|---|---|---|---:|---:|"]
    for name, c in [("pooled", P)] + list(res["per_split"].items()):
        lines.append(f"| {name} | {c['wer_drop']:+.2f} [{c['wer_drop_ci95'][0]:+.2f}, {c['wer_drop_ci95'][1]:+.2f}] | "
                     f"{c['changed_raw']} / {c['changed_norm']} | {c['better']} / {c['worse']} (p={c['sign_test_p']}) | "
                     f"{c['beam']['rare_plus_num_err'] - c['greedy']['rare_plus_num_err']:+d} | "
                     f"{c['beam']['sec_p95'] - c['greedy']['sec_p95']:+.3f} |")
    lines += ["", "## Gate (fixed before the run; pooled samples)", "",
              "| criterion | threshold | greedy | beam | value | result |", "|---|---|---:|---:|---:|---|",
              f"| (a) final-turn WER drop | ≥ {GATE['a_wer_drop_min']} points | {P['greedy']['wer']:.2f} | {P['beam']['wer']:.2f} | "
              f"{P['wer_drop']:+.2f} | {ok(gt['a'])} |",
              f"| (b) rare + number errors | do not rise | {P['greedy']['rare_plus_num_err']} | {P['beam']['rare_plus_num_err']} | "
              f"{P['beam']['rare_plus_num_err'] - P['greedy']['rare_plus_num_err']:+d} | {ok(gt['b'])} |",
              "| (c) paired agent score, dev_lao | (team) | | | | not run here |",
              f"| (d) p95 ASR s per final turn | rise ≤ {GATE['d_p95_rise_max_s']} s | {P['greedy']['sec_p95']:.3f} | {P['beam']['sec_p95']:.3f} | "
              f"{P['beam']['sec_p95'] - P['greedy']['sec_p95']:+.3f} | {ok(gt['d'])} |",
              "", f"**Verdict (a)(b)(d): {res['verdict']}**", "",
              "Per split (information only): " + "; ".join(
                  f"{k}: a {ok(v['gate']['a'])}, b {ok(v['gate']['b'])}, d {ok(v['gate']['d'])}" for k, v in res["per_split"].items()),
              "", "## Secondary checks (final turn, asr_quality.py label checks: value still spoken in any form)", "",
              "| set | file | slot amount kept | slot time kept | slot small int kept | negation kept | query kept | rare err, final-turn-only vocab |",
              "|---|---|---|---|---|---|---|---:|"]
    for name, c in [("pooled", P)] + list(res["per_split"].items()):
        for k in ("greedy", "beam"):
            L = c["labels"][k]
            cell = lambda r: f"{r['kept']}/{r['n']}"  # noqa: E731
            lines.append(f"| {name} | {k} | {cell(L['slot_amount'])} | {cell(L['slot_time'])} | {cell(L['slot_small_int'])} | "
                         f"{cell(L['negation'])} | {cell(L['query'])} | {c[k]['rare_err_final_vocab']} |")
    lines += ["", "## Changed final-turn transcripts (pooled; edits greedy → beam)", ""] + examples + [""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--greedy", required=True)
    ap.add_argument("--beam", required=True)
    ap.add_argument("--split-ids", nargs="+", required=True, help="dev split id files; pooled = their union")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--rare-below", type=int, default=3)
    ap.add_argument("--asr-split", help="the ASR checkpoint's split_ids.json: check that the fit samples are its "
                                        "train + val samples")
    ap.add_argument("--examples", type=int, default=40, help="changed transcripts listed in the report")
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()

    split_ids = {Path(f).stem: read_ids(f) for f in a.split_ids}
    union = set().union(*split_ids.values())
    train = load_split("train", a.root)
    items = [s for s in train if s["id"] in union]
    fit = [s for s in train if s["id"] not in union]
    vocab, vocab_fv = Counter(), Counter()
    for s in fit:
        vocab_fv.update(words(s["audio_text"]))
        vocab.update(words(s["audio_text"]))
        for h in s["history"]:
            if h["role"] == "user":
                vocab.update(words(h["audio_text"]))
    fit_check = ""
    if a.asr_split:
        sp = json.loads(Path(a.asr_split).read_text())
        same = {s["id"] for s in fit} == set(sp["train"]) | set(sp["val"])
        fit_check = f" ({'=' if same else 'NOT the same as'} the train + val samples of {a.asr_split})"
    rare = lambda w: vocab[w] < a.rare_below  # noqa: E731
    rare_fv = lambda w: vocab_fv[w] < a.rare_below  # noqa: E731

    hyp_g = {r["audio"]: r for r in load_jsonl(a.greedy)}
    hyp_b = {r["audio"]: r for r in load_jsonl(a.beam)}
    missing = [s["audio"] for s in items if s["audio"] not in hyp_g or s["audio"] not in hyp_b]
    if missing:
        sys.exit(f"{len(missing)} final-turn wavs missing from a file (first {missing[0]})")
    if set(hyp_g) != set(hyp_b):
        sys.exit("the two files do not cover the same wavs")
    finals = {s["audio"] for s in items}
    hist = [p for p in hyp_g if p not in finals]
    tools = catalog_tools(load_catalog("train", a.root))

    pooled = compare(items, hyp_g, hyp_b, rare, rare_fv, tools)
    ref = turn_stats([(s["audio_text"], hyp_g[s["audio"]]["text"]) for s in items])
    assert ref["wer"] == pooled["greedy"]["wer"], (ref, pooled["greedy"]["wer"])  # same WER as asr_quality.py
    per = {}
    for name, ids in split_ids.items():
        keep = set(ids)
        c = compare([s for s in items if s["id"] in keep], hyp_g, hyp_b, rare, rare_fv, tools)
        c["gate"] = gate(c)
        per[name] = c
    g = gate(pooled)
    verdict = ("PASS on (a), (b) and (d): keep beam4 as a candidate, pending (c) the paired agent score on dev_lao"
               if g["a_b_d"] else
               "DROP beam4: fails " + ", ".join(f"({k})" for k in ("a", "b", "d") if not g[k]))

    ug, ub = pooled["_utts"]
    by_id = {s["id"]: s for s in items}
    changed = [(gu, bu) for gu, bu in zip(ug, ub) if gu["text"] != bu["text"]]
    changed.sort(key=lambda x: (x[1]["edits"] - x[0]["edits"], x[0]["id"]))
    examples = []
    for gu, bu in changed[: a.examples]:
        examples += [f"- `{gu['id']}` edits {gu['edits']} → {bu['edits']} (rare {gu['rare_err']} → {bu['rare_err']}, "
                     f"number {gu['num_err']} → {bu['num_err']})",
                     f"  - gold:   {by_id[gu['id']]['audio_text']}", f"  - greedy: {gu['text']}", f"  - beam:   {bu['text']}"]
    if len(changed) > a.examples:
        examples.append(f"- ... {len(changed) - a.examples} more (all in the JSON)")

    strip = lambda c: {k: v for k, v in c.items() if k != "_utts"}  # noqa: E731
    ids_sum = sum(len(v) for v in split_ids.values())
    res = {"finished": now(), "git": git_state(), "greedy": a.greedy, "beam": a.beam,
           "greedy_sha256": sha256_file(a.greedy), "beam_sha256": sha256_file(a.beam),
           "split_ids": {k: len(v) for k, v in split_ids.items()}, "ids_sum": ids_sum, "overlap": ids_sum - len(union),
           "fit_samples": len(fit), "fit_tokens": sum(vocab.values()), "fit_vocab": len(vocab), "fit_check": fit_check,
           "rare_below": a.rare_below, "number_words": sorted(NUM_WORDS), "gate_thresholds": GATE,
           "history_rows": len(hist), "history_identical": sum(hyp_g[p] == hyp_b[p] for p in hist),
           "pooled": strip(pooled), "per_split": {k: strip(v) for k, v in per.items()}, "gate": g, "verdict": verdict,
           "changed": [{"id": gu["id"], "gold": by_id[gu["id"]]["audio_text"], "greedy": gu["text"], "beam": bu["text"],
                        "edits": [gu["edits"], bu["edits"]], "rare_err": [gu["rare_err"], bu["rare_err"]],
                        "num_err": [gu["num_err"], bu["num_err"]]} for gu, bu in changed]}
    if a.json:
        write_json(a.json, res)
    if a.md:
        Path(a.md).parent.mkdir(parents=True, exist_ok=True)
        Path(a.md).write_text(md_report(res, examples), encoding="utf-8")
    P = res["pooled"]
    print(f"pooled n={P['greedy']['samples']}: WER {P['greedy']['wer']} -> {P['beam']['wer']} (drop {P['wer_drop']:+.2f}, "
          f"CI {P['wer_drop_ci95']}); rare+num err {P['greedy']['rare_plus_num_err']} -> {P['beam']['rare_plus_num_err']}; "
          f"p95 s {P['greedy']['sec_p95']} -> {P['beam']['sec_p95']}; changed {P['changed_raw']}; {verdict}")


if __name__ == "__main__":
    main()
