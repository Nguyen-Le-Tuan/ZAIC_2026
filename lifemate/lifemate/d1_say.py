"""D1, words: an external LLM turns a scenario's `say` lines (lifemate.d1_gen) into one spoken request. The label is
already fixed by code; the LLM writes nothing that is scored.

  python -m lifemate.d1_say write  --tag t1 --model claude-opus-5-5 --n 30 --max-usd 1     # Anthropic (SDK)
  python -m lifemate.d1_say write  --tag t1 --model muse-spark-1.3  --n 30 --max-usd 1     # Meta (chat completions)
  python -m lifemate.d1_say report --tag t1 --models claude-opus-5-5,muse-spark-1.3        # side by side + checks

Keys come from the environment only (ANTHROPIC_API_KEY; META_API_KEY or MODEL_API_KEY); never printed, never logged.
Every call is logged in gen/d1_<tag>_say_<model>_usage.jsonl; a run stops once that ledger reaches --max-usd.
What is sent: the instructions below, a dozen train requests as examples of how users talk (the same practice as the
earlier synthetic runs), and the `say` lines. No history, no state, no label, nothing from public_test.

Checks on the returned request (code, no model): every `must` string is in it (case and diacritics folded), no «»,
no "(không nói" left over, no ID, 6-55 words.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import random
import re
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

from .data import load_jsonl, load_split, write_jsonl

GEN_DIR = Path("gen")
# USD per million tokens (input, output). Meta: standard tier, as in the earlier runs. Anthropic: first-party API.
PRICES = {"muse-spark-1.3": (1.25, 4.25), "muse-wonder-1.0": (4.0, 20.0), "claude-opus-5-5": (4.0, 20.0)}
META_URL = "https://api.meta.ai/v1/chat/completions"
# Two prepaid credits, never pooled (Anh, 09/11/2026 20:35): Anthropic 100 USD in total; Meta 81 USD left at that moment.
# Spending past a credit charges the team's card, and these ledgers are estimates from token counts, so each cap keeps a
# 5 USD margin. Anthropic counts every d1 ledger row; Meta counts the rows written after the moment the 81 was stated.
PROVIDER_CAP = {"anthropic": 95.0, "meta": 76.0}
META_SINCE = "2026-11-09T20:25"


def provider(model: str) -> str:
    return "anthropic" if model.startswith("claude-") else "meta"


def provider_spent(name: str) -> float:
    total = 0.0
    for path in sorted(GEN_DIR.glob("d1_*_usage.jsonl")):
        for r in load_jsonl(path):
            if provider(r["model"]) != name:
                continue
            if name == "meta" and r["time"][:16] < META_SINCE:
                continue
            total += r["usd"]
    return total

SYSTEM = """Bạn viết lời nói của người dùng cho dữ liệu huấn luyện một trợ lý giọng nói tiếng Việt trên điện thoại.

Mỗi lần bạn nhận: thời điểm hiện tại, một gợi ý về cách nói, và danh sách những việc người dùng muốn (mỗi dòng một việc, đã có giá trị chính xác). Hãy viết ĐÚNG MỘT câu nói mà người dùng sẽ nói với trợ lý để nhờ tất cả các việc đó, theo đúng thứ tự các dòng.

Quy tắc bắt buộc:
1. Tự nhiên như người thật nói, không như văn viết; dài 8 đến 40 từ. Không xuống dòng, không ngoặc kép, không giải thích.
2. Cụm nằm trong «…» là tên riêng hoặc lời phải giữ nguyên từng chữ (được đổi chữ hoa/thường); khi viết thì bỏ dấu «».
3. Nói đủ và đúng mọi con số, số lượng, số tiền, ngày, giờ có trong mô tả. Được đọc số bằng chữ ("hai vé", "bảy giờ rưỡi") và đổi thứ tự ngày giờ ("sáng mai bảy giờ"), nhưng không được đổi nghĩa.
4. Phần trong ngoặc đơn kiểu "(không nói …)" là chỉ dẫn cho bạn: người dùng KHÔNG nhắc tới thông tin đó; đừng viết lại chỉ dẫn, cũng đừng nói "không biết" hay "tuỳ".
5. Không thêm bất kỳ thông tin nào ngoài mô tả: không thêm số lượng, giờ, tên, địa chỉ, lý do. Không bao giờ đọc mã ID.
6. Làm theo gợi ý cách nói. Nếu gợi ý là tự sửa giữa câu, giá trị nói SAU khi sửa phải đúng là giá trị trong mô tả.

Vài câu người dùng thật đã nói (chỉ để học giọng điệu, không chép nội dung):
{styles}"""

HINTS = ["vào thẳng việc, không rào đón", "vào thẳng việc, không rào đón", "mở đầu bằng \"ờ\" hoặc \"à\"", "gọi \"trợ lý ơi\" hoặc \"em ơi\" rồi mới nhờ",
         "giọng miền Nam (nha, giùm, hông, coi)", "giọng miền Nam (nha, giùm, hông, coi)", "giọng miền Trung nhẹ (chi, rứa, nghe)",
         "xưng \"mình\", nói ngắn gọn", "xưng \"anh\" hoặc \"chị\", gọi trợ lý là \"em\"", "nói hơi dài dòng, có một câu dẫn ngắn trước khi nhờ",
         "tự sửa giữa câu một lần (\"à không\", \"à nhầm\")", "chêm một từ tiếng Anh thông dụng (book, check, order) nếu hợp"]


def fold(s: str) -> str:
    t = unicodedata.normalize("NFD", str(s).lower()).replace("đ", "d")
    return " ".join("".join(c for c in t if not unicodedata.combining(c)).split())


def check(text: str, g: dict) -> list[str]:
    """Why the request cannot be used; [] when it can."""
    errs = []
    f = fold(text)
    for m in g["must"]:
        if fold(m) not in f:
            errs.append(f"missing «{m}»")
    if "«" in text or "»" in text:
        errs.append("guillemets left")
    if "(khong noi" in f or "khong noi" in f and "(" in text:
        errs.append("instruction leaked")
    if re.search(r"\b[a-z]{2,8}_\d{2,4}\b", text):
        errs.append("ID spoken")
    n = len(text.split())
    if not 6 <= n <= 55:
        errs.append(f"{n} words")
    if "\n" in text.strip():
        errs.append("more than one line")
    return errs


def user_prompt(g: dict, hint: str) -> str:
    lines = "\n".join(f"- {s}" for s in g["say"])
    return f"Thời điểm hiện tại: {g['context']['current_time']}\nGợi ý cách nói: {hint}\nNgười dùng muốn:\n{lines}"


class Ledger:
    def __init__(self, path: Path, model: str, max_usd: float):
        self.path, self.model, self.max_usd = path, model, max_usd
        self.price = PRICES[model]

    def spent(self) -> float:
        return sum(r["usd"] for r in load_jsonl(self.path)) if self.path.exists() else 0.0

    def blocked(self) -> str | None:
        """Why no further call may be made, or None."""
        if self.spent() >= self.max_usd:
            return f"budget: this run reached its cap of {self.max_usd} USD"
        name = provider(self.model)
        if provider_spent(name) >= PROVIDER_CAP[name]:
            return f"budget: {name} reached {PROVIDER_CAP[name]} USD of its credit (hard cap, not pooled with the other platform)"
        return None

    def add(self, pin: int, pout: int, seconds: float, purpose: str, extra: dict | None = None) -> None:
        usd = (pin * self.price[0] + pout * self.price[1]) / 1e6
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "purpose": purpose, "model": self.model,
                                "prompt_tokens": pin, "completion_tokens": pout, "seconds": round(seconds, 1),
                                "usd": round(usd, 5), **(extra or {})}) + "\n")


def meta_writer(model: str):
    key = os.environ.get("MODEL_API_KEY") or os.environ.get("META_API_KEY")
    if not key:
        raise SystemExit("no Meta key: `set -a; . ~/.zac_meta_env; set +a` first")

    def write(system: str, user: str, schema: dict | None = None, effort: str = "low") -> tuple[str, int, int, dict]:
        body = {"model": model, "reasoning_effort": effort,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if schema is not None:
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": "verdict", "schema": schema, "strict": True}}
        req = urllib.request.Request(META_URL, json.dumps(body).encode(), {"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
        delay = 2.0
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    resp = json.loads(r.read())
                break
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="replace")[:300]
                if e.code in (429, 500, 502, 503, 504) and attempt < 4:
                    time.sleep(float(e.headers.get("Retry-After") or delay))
                    delay *= 2
                    continue
                raise RuntimeError(f"HTTP {e.code}: {msg}") from None
            except (TimeoutError, urllib.error.URLError) as e:
                if attempt < 4:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise RuntimeError(f"network: {e}") from None
        u = resp.get("usage") or {}
        return (resp["choices"][0]["message"].get("content") or "").strip(), u.get("prompt_tokens", 0), u.get("completion_tokens", 0), {}
    return write


def anthropic_writer(model: str):
    import anthropic   # official SDK; reads ANTHROPIC_API_KEY from the environment

    client = anthropic.Anthropic()

    def write(system: str, user: str) -> tuple[str, int, int, dict]:
        # Thinking is always on for this model; effort "low" is enough for one sentence. The system prompt is the same
        # for every request, so it is the cached prefix. A request the safety classifiers decline is re-run on the
        # default fallback model inside the same call (server-side fallback).
        try:
            r = client.beta.messages.create(
                model=model, max_tokens=4000, system=system, cache_control={"type": "ephemeral"},
                output_config={"effort": "low"}, betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                messages=[{"role": "user", "content": user}])
        except anthropic.RateLimitError as e:
            raise RuntimeError(f"rate limited: {e.message}") from None
        except anthropic.APIStatusError as e:
            raise RuntimeError(f"HTTP {e.status_code}: {e.message}") from None
        except anthropic.APIConnectionError as e:
            raise RuntimeError(f"network: {e}") from None
        if r.stop_reason == "refusal":
            raise RuntimeError(f"refusal: {getattr(r.stop_details, 'category', None)}")
        text = " ".join(b.text for b in r.content if b.type == "text").strip()
        u = r.usage
        cr, cw = getattr(u, "cache_read_input_tokens", 0) or 0, getattr(u, "cache_creation_input_tokens", 0) or 0
        # priced as uncached input: an upper bound (cache reads cost less, cache writes slightly more)
        return text, u.input_tokens + cr + cw, u.output_tokens, {"cache_read": cr, "cache_write": cw, "served_by": r.model}
    return write


def pick(rows: list[dict], n: int, seed: int) -> list[dict]:
    """n scenarios spread over apps and kinds, the same for every model."""
    rng = random.Random(seed)
    by = {}
    for g in rows:
        by.setdefault((g["app"], g["kind"]), []).append(g)
    keys = sorted(by)
    rng.shuffle(keys)
    out, i = [], 0
    while len(out) < min(n, len(rows)):
        k = keys[i % len(keys)]
        if by[k]:
            out.append(by[k].pop(rng.randrange(len(by[k]))))
        i += 1
    return out


def items(rows: list[dict]) -> list[dict]:
    """What has to be written: every scenario's request, and the request of the turn before for follow-ups."""
    out = []
    for g in rows:
        out.append(g)
        if g.get("prev"):
            out.append({"id": g["id"] + "#prev", "say": g["prev"]["say"], "must": g["prev"]["must"], "context": g["context"],
                        "kind": "prev", "app": g["app"]})
    return out


def cmd_write(a):
    scen = load_jsonl(GEN_DIR / f"d1_{a.tag}_scen.jsonl")
    rows = items(scen if a.n <= 0 else pick(scen, a.n, a.seed))
    rng = random.Random(a.seed)
    train = load_split("train")
    styles = "\n".join(f"- {s['audio_text']}" for s in rng.sample(train, 12))
    system = SYSTEM.format(styles=styles)
    hints = {g["id"]: rng.choice(HINTS) for g in rows}
    out_path = GEN_DIR / f"d1_{a.tag}_say_{a.model}.jsonl"
    done = {r["id"]: r for r in load_jsonl(out_path)} if out_path.exists() else {}
    ledger = Ledger(GEN_DIR / f"d1_{a.tag}_say_{a.model}_usage.jsonl", a.model, a.max_usd)
    write = anthropic_writer(a.model) if a.model.startswith("claude-") else meta_writer(a.model)
    todo = [g for g in rows if g["id"] not in done]

    def one(g):
        why = ledger.blocked()
        if why:
            return g["id"], None, why
        t0 = time.time()
        try:
            text, pin, pout, extra = write(system, user_prompt(g, hints[g["id"]]))
        except RuntimeError as e:
            return g["id"], None, str(e)[:200]
        ledger.add(pin, pout, time.time() - t0, "say", extra)
        return g["id"], text, None

    fails = []
    with concurrent.futures.ThreadPoolExecutor(a.workers) as ex:
        for sid, text, err in ex.map(one, todo):
            if err:
                fails.append((sid, err))
                continue
            g = next(x for x in rows if x["id"] == sid)
            done[sid] = {"id": sid, "request": text, "hint": hints[sid], "errors": check(text, g), "model": a.model}
    write_jsonl(out_path, [done[g["id"]] for g in rows if g["id"] in done])
    ok = sum(not r["errors"] for r in done.values())
    name = provider(a.model)
    print(f"{a.model}: {len(done)}/{len(rows)} written, {ok} pass the checks, {len(fails)} calls failed; this run {ledger.spent():.3f} USD; "
          f"{name} so far {provider_spent(name):.2f} of {PROVIDER_CAP[name]} USD -> {out_path}")
    for sid, err in fails[:5]:
        print("  failed:", sid, err)


JUDGE_SYSTEM = """Bạn kiểm tra dữ liệu huấn luyện cho một trợ lý giọng nói tiếng Việt. Bạn nhận: (1) danh sách những việc người dùng MUỐN, đã có giá trị chính xác; (2) câu người dùng NÓI. Trợ lý chỉ nghe câu nói. Hãy xét: một trợ lý cẩn thận nghe câu nói này có hiểu ra ĐÚNG các việc trong danh sách, không hơn không kém?

Đánh dấu ok = false khi có bất kỳ điều nào sau:
- thiếu một việc, hoặc thiếu một giá trị (số lượng, số tiền, ngày, giờ, tên) có trong danh sách;
- một giá trị bị đổi (kể cả ngày giờ lệch nghĩa); câu tự sửa giữa chừng thì lấy giá trị nói SAU cùng;
- câu nói huỷ hoặc phủ định một việc trong danh sách;
- câu nói nhờ thêm một việc khác, hỏi thêm một thông tin khác, hoặc thêm một giá trị (số lượng, giờ, tên, địa chỉ) mà danh sách không có;
- danh sách ghi "(không nói …)" mà câu nói lại nêu thông tin đó.

KHÔNG coi là lỗi: lời chào, lời dẫn hay lý do không kèm việc mới; đọc số bằng chữ; đổi thứ tự từ; giọng vùng miền; viết hoa/thường; bỏ chữ "mã", "sự kiện", "món" trước tên.

Trả về JSON: ok (true/false) và problems (danh sách ngắn, tiếng Việt; rỗng khi ok)."""
JUDGE_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["ok", "problems"],
                "properties": {"ok": {"type": "boolean"}, "problems": {"type": "array", "items": {"type": "string"}}}}


def cmd_judge(a):
    """A second model, from the other provider than the writer, checks that the request means what `say` says."""
    scen = {g["id"]: g for g in items(load_jsonl(GEN_DIR / f"d1_{a.tag}_scen.jsonl"))}
    src = GEN_DIR / f"d1_{a.tag}_say_{a.writer}.jsonl"
    rows = [r for r in load_jsonl(src) if not r["errors"]]
    out_path = GEN_DIR / f"d1_{a.tag}_judge_{a.writer}.jsonl"
    done = {r["id"]: r for r in load_jsonl(out_path)} if out_path.exists() else {}
    ledger = Ledger(GEN_DIR / f"d1_{a.tag}_judge_{a.writer}_usage.jsonl", a.model, a.max_usd)
    ask = meta_writer(a.model)

    def one(r):
        why = ledger.blocked()
        if why:
            return r["id"], None, why
        g = scen[r["id"]]
        user = "Người dùng MUỐN:\n" + "\n".join(f"- {s}" for s in g["say"]) + f"\n\nThời điểm hiện tại: {g['context']['current_time']}\nCâu người dùng NÓI: {r['request']}"
        t0 = time.time()
        try:
            text, pin, pout, _ = ask(JUDGE_SYSTEM, user, JUDGE_SCHEMA, "medium")
            v = json.loads(text)
        except (RuntimeError, json.JSONDecodeError) as e:
            return r["id"], None, str(e)[:200]
        ledger.add(pin, pout, time.time() - t0, "judge")
        return r["id"], v, None

    fails = []
    with concurrent.futures.ThreadPoolExecutor(a.workers) as ex:
        for sid, v, err in ex.map(one, [r for r in rows if r["id"] not in done]):
            if err:
                fails.append((sid, err))
            else:
                done[sid] = {"id": sid, "ok": bool(v["ok"]), "problems": v["problems"]}
    write_jsonl(out_path, [done[r["id"]] for r in rows if r["id"] in done])
    bad = [d for d in done.values() if not d["ok"]]
    print(f"judge {a.model} on {a.writer}: {len(done)}/{len(rows)} judged, {len(bad)} rejected, {len(fails)} calls failed; this run {ledger.spent():.3f} USD; "
          f"meta so far {provider_spent('meta'):.2f} of {PROVIDER_CAP['meta']} USD -> {out_path}")
    req = {r["id"]: r["request"] for r in rows}
    for d in bad[:a.show]:
        print(f"  REJECT {d['id']}: {req[d['id']]}\n         {d['problems']}")
    for sid, err in fails[:3]:
        print("  failed:", sid, err)


def cmd_final(a):
    """Train-format samples from the scenarios whose request (and previous-turn request) passed both checks."""
    scen = load_jsonl(GEN_DIR / f"d1_{a.tag}_scen.jsonl")
    say = {r["id"]: r for r in load_jsonl(GEN_DIR / f"d1_{a.tag}_say_{a.writer}.jsonl")}
    jpath = GEN_DIR / f"d1_{a.tag}_judge_{a.writer}.jsonl"
    judge = {r["id"]: r for r in load_jsonl(jpath)} if jpath.exists() else None
    if judge is None and not a.no_judge:
        raise SystemExit(f"no {jpath}: run `judge` first (or pass --no-judge)")

    def good(i: str) -> bool:
        return i in say and not say[i]["errors"] and (judge is None or (i in judge and judge[i]["ok"]))

    out, drop = [], {"no_request": 0, "code_check": 0, "judge": 0}
    for g in scen:
        need = [g["id"]] + ([g["id"] + "#prev"] if g.get("prev") else [])
        if any(i not in say for i in need):
            drop["no_request"] += 1
            continue
        if any(say[i]["errors"] for i in need):
            drop["code_check"] += 1
            continue
        if not all(good(i) for i in need):
            drop["judge"] += 1
            continue
        history = list(g["history"])
        if g.get("prev"):
            history += [{"role": "user", "audio": None, "audio_text": say[g["id"] + "#prev"]["request"]},
                        {"role": "assistant", "text": g["prev"]["reply"], "tool_calls": g["prev"]["calls"], "tool_results": g["prev"]["results"]}]
        used = sorted({c["name"].split(".")[0] for c in g["calls"] if c["name"] != "sys.ask_missing_info"} | set(g["state"]))
        out.append({"id": g["id"], "audio": None, "audio_text": say[g["id"]]["request"], "context": g["context"], "history": history,
                    "label": {"tool_calls": g["calls"], "tool_results": g["results"]}, "_src": "d1", "_app": g["app"], "_kind": g["kind"],
                    "_keep_apps": used if g["kind"] != "not_installed" else []})
    path = GEN_DIR / f"d1_{a.tag}.jsonl"
    write_jsonl(path, out)
    print(f"{len(out)}/{len(scen)} samples -> {path}; dropped {drop}")


def cmd_report(a):
    scen = {g["id"]: g for g in load_jsonl(GEN_DIR / f"d1_{a.tag}_scen.jsonl")}
    models = a.models.split(",")
    outs = {m: {r["id"]: r for r in load_jsonl(GEN_DIR / f"d1_{a.tag}_say_{m}.jsonl")} for m in models}
    ids_ = [i for i in outs[models[0]] if all(i in outs[m] for m in models)]
    for m in models:
        rows = [outs[m][i] for i in ids_]
        led = GEN_DIR / f"d1_{a.tag}_say_{m}_usage.jsonl"
        usd = sum(r["usd"] for r in load_jsonl(led)) if led.exists() else 0.0
        words = sorted(len(r["request"].split()) for r in rows)
        errs = {}
        for r in rows:
            for e in r["errors"]:
                errs[e.split("«")[0].strip()] = errs.get(e.split("«")[0].strip(), 0) + 1
        print(f"{m}: n={len(rows)} pass {sum(not r['errors'] for r in rows)} | words median {words[len(words) // 2]} | {usd:.3f} USD "
              f"({1000 * usd / max(len(rows), 1):.2f} USD per 1000) | errors {errs}")
    lines = []
    for i in ids_:
        g = scen[i]
        lines.append(f"\n### {i} [{g['kind']}] hint: {outs[models[0]][i]['hint']}")
        lines += [f"  muốn: {s}" for s in g["say"]]
        for m in models:
            r = outs[m][i]
            lines.append(f"  {m:16s} {'OK ' if not r['errors'] else 'ERR'} {r['request']}" + (f"   <- {r['errors']}" if r["errors"] else ""))
    text = "\n".join(lines)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
        print("side by side ->", a.out)
    else:
        print(text)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("--tag", required=True)
    w.add_argument("--model", required=True, choices=sorted(PRICES))
    w.add_argument("--n", type=int, default=30, help="scenarios to write (spread over apps and kinds); 0 = all")
    w.add_argument("--seed", type=int, default=0)
    w.add_argument("--workers", type=int, default=4)
    w.add_argument("--max-usd", type=float, required=True)
    w.set_defaults(fn=cmd_write)
    jd = sub.add_parser("judge")
    jd.add_argument("--tag", required=True)
    jd.add_argument("--writer", required=True, help="model whose requests are judged")
    jd.add_argument("--model", default="muse-spark-1.3", choices=["muse-spark-1.3", "muse-wonder-1.0"])
    jd.add_argument("--workers", type=int, default=6)
    jd.add_argument("--show", type=int, default=12)
    jd.add_argument("--max-usd", type=float, required=True)
    jd.set_defaults(fn=cmd_judge)
    fn = sub.add_parser("final")
    fn.add_argument("--tag", required=True)
    fn.add_argument("--writer", required=True)
    fn.add_argument("--no-judge", action="store_true")
    fn.set_defaults(fn=cmd_final)
    r = sub.add_parser("report")
    r.add_argument("--tag", required=True)
    r.add_argument("--models", required=True)
    r.add_argument("--out")
    r.set_defaults(fn=cmd_report)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
