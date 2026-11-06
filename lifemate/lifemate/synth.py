"""Synthetic samples for apps the agent has not seen, written by an external LLM and kept only if they run correctly.

Why: public_test installs 11 apps that train never shows (410/634 public samples have at least one), and the 4B agent
scores about 15 points lower on held-out apps (dev_lao) than on seen ones. The rules allow an external LLM to make
synthetic training data during development (never at inference) and forbid labelling public/private test.

Inputs, and only these: the split's tools catalog, the simulator source of its zaic_tools package (to know what an
app's state looks like), and fit samples of train (context templates and a few examples of the gold conventions).
Never <split>_environment/, never dev or test requests.

Commands (outputs go to gen/, which is git-ignored; the API key is read from MODEL_API_KEY or META_API_KEY):
  python -m lifemate.synth gen   --apps library,loyalty --per-app 4 --tag t20 --max-usd 3
  python -m lifemate.synth check --tag t20          # simulator checks + an independent re-derivation of the calls
  python -m lifemate.synth sft   --tag t20 --out sft/synth_t20.jsonl
  python -m lifemate.synth show  --tag t20          # accepted and rejected samples as text, for reading
  python -m lifemate.synth stats --tag t20          # shape of the accepted samples next to the real fit samples
Recipe v2 (--recipe v2 for gen and check, 06/11): each sample gets a shape drawn from the real fit_lao shares
(history, an ID reused from a previous turn, two apps, no-call requests); the checks enforce it.
Every API call is logged in gen/synth_<tag>_usage.jsonl; a call is refused once the tag reached --max-usd or all
tags together reached --total-usd (default 30: Anh's limit for all synthetic data, raised from 10 on 02/11; more only after asking).

Checks (check): every gold call is run in the split's zaic_tools simulator on the generated state.
  schema       the call passes zaic_tools' schema check and its tool is installed
  noop         a call returned ok=false or done=false (unknown ID, not enough balance...)
  invented_id  an x-ref argument (an ID) that no earlier result returned
  id_in_text   the request says an ID out loud (users never do)
  no_write     an execute sample changes nothing (read-only questions are the `lookup` category)
  bad_lookup   a lookup sample writes or asks
  bad_ask      an ask_missing sample does not end with sys.ask_missing_info naming required parameters of an
               installed tool, or calls the tool it asks about (writes for other parts of the request are fine,
               as in gold)
  duplicate    the request nearly repeats an accepted request of the same app (difflib ratio >= 0.8)
  solver       (asked twice when its arguments JSON is broken) an independent LLM call, given the request, the context and the state (as the results the tools would
               return), predicts the calls; the sample is kept only if the predicted calls reach the same final state
               and make the same write/ask calls by name
"""
from __future__ import annotations

import argparse
import copy
import difflib
import inspect
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

from . import runinfo
from .askpolicy import required
from .data import DEFAULT_ROOT, catalog_tools, load_catalog, load_jsonl, load_split, write_jsonl, zaic_tools
from .prompt import SYSTEM_RULES

ASK = "sys.ask_missing_info"
SRC = "synthetic-api"
GEN_DIR = Path("gen")

# USD per million tokens (input, output); reasoning tokens are billed as output. Meta Model API, standard tier
# (content not used for training); the contributor tier is never used: prompts carry competition files.
PRICES = {"muse-spark-1.3": (1.25, 4.25), "muse-spark-1.2": (1.25, 4.25), "muse-spark-1.1": (1.25, 4.25),
          "muse-wonder-1.0": (4.0, 20.0)}
DEFAULT_BASE_URL = "https://api.meta.ai/v1"
DEFAULT_MODEL = "muse-spark-1.3"


# ---------------------------------------------------------------- LLM client (OpenAI-compatible chat completions)

class BudgetExceeded(RuntimeError):
    pass


def ledger_usd(path: Path) -> float:
    return sum(r["usd"] for r in load_jsonl(path)) if path.exists() else 0.0


def total_spent(gen_dir: Path = GEN_DIR) -> float:
    """Every tag's ledger together: what the API has cost so far, all runs included."""
    return sum(ledger_usd(p) for p in sorted(gen_dir.glob("synth_*_usage.jsonl")))


class Client:
    """Chat Completions over urllib (no extra package). Every call is appended to the tag's usage ledger. A call is
    refused once the tag reached max_usd, or once all tags together reached total_usd (Anh's limit: 30 USD for
    all synthetic data, more only after asking him)."""

    def __init__(self, model: str, base_url: str, ledger: Path, max_usd: float, total_usd: float = 30.0,
                 timeout: float = 300):
        if "contributor" in model:
            raise SystemExit("contributor-tier models may train on prompts; prompts here carry competition files")
        key = os.environ.get("MODEL_API_KEY") or os.environ.get("META_API_KEY")
        if not key:
            raise SystemExit("no API key: put `export META_API_KEY=...` in ~/.zac_meta_env and `source` it")
        self.key, self.model, self.url = key, model, base_url.rstrip("/") + "/chat/completions"
        self.ledger, self.max_usd, self.total_usd, self.timeout = ledger, max_usd, total_usd, timeout
        self.price = PRICES.get(model)
        if self.price is None:
            raise SystemExit(f"no price for {model!r}; add it to PRICES first (the budget cap needs it)")

    def spent(self) -> float:
        return ledger_usd(self.ledger)

    def chat(self, messages: list[dict], schema: dict, name: str, effort: str = "medium", purpose: str = "") -> dict:
        if self.spent() >= self.max_usd:
            raise BudgetExceeded(f"tag spent {self.spent():.3f} USD >= cap {self.max_usd}")
        total = total_spent(self.ledger.parent)
        if total >= self.total_usd:
            raise BudgetExceeded(f"all tags spent {total:.3f} USD >= total cap {self.total_usd}")
        body = {"model": self.model, "messages": messages, "reasoning_effort": effort,
                "response_format": {"type": "json_schema", "json_schema": {"name": name, "schema": schema, "strict": True}}}
        req = urllib.request.Request(self.url, json.dumps(body).encode(), {
            "Content-Type": "application/json", "Authorization": f"Bearer {self.key}"})
        delay = 1.0
        for attempt in range(6):
            t0 = time.time()
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    resp = json.loads(r.read())
                break
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="replace")[:500]
                if e.code in (429, 500, 502, 503, 504) and attempt < 5:
                    wait = float(e.headers.get("Retry-After") or delay)
                    time.sleep(wait + random.random() * 0.5)
                    delay *= 2
                    continue
                raise RuntimeError(f"HTTP {e.code}: {msg}") from None
            except (TimeoutError, urllib.error.URLError) as e:
                if attempt < 5:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise RuntimeError(f"network: {e}") from None
        u = resp.get("usage") or {}
        pin, pout = u.get("prompt_tokens", 0), u.get("completion_tokens", 0)
        usd = (pin * self.price[0] + pout * self.price[1]) / 1e6
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps({"time": runinfo.now(), "purpose": purpose, "model": self.model, "prompt_tokens": pin,
                                "completion_tokens": pout,
                                "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                                "seconds": round(time.time() - t0, 1), "usd": round(usd, 5)}) + "\n")
        choice = resp["choices"][0]
        content = choice["message"].get("content") or ""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise RuntimeError(f"not JSON (finish_reason={choice.get('finish_reason')}): {content[:300]}") from None


# ---------------------------------------------------------------- inputs

def app_source(zt, app: str) -> str:
    cls = zt.executor.APPS[app]
    return Path(inspect.getsourcefile(cls)).read_text(encoding="utf-8")


def base_source(zt) -> str:
    return Path(inspect.getsourcefile(zt.executor.App)).read_text(encoding="utf-8")


def fit_samples(root, fit_path: str, drop_apps: set[str]) -> list[dict]:
    keep = set(Path(fit_path).read_text().split())
    out = []
    for s in load_split("train", root):
        if s["id"] not in keep:
            continue
        used = {c["name"].split(".", 1)[0] for c in s["label"]["tool_calls"]}
        if used & drop_apps:
            continue
        out.append(s)
    return out


def pick_examples(fits: list[dict], rng: random.Random, k_exec: int = 3, k_ask: int = 2) -> list[dict]:
    """A few gold samples without history: executes that read then write, and asks."""
    no_hist = [s for s in fits if not s["history"] and s["label"]["tool_calls"]]
    asks = [s for s in no_hist if s["label"]["tool_calls"][-1]["name"] == ASK]
    execs = [s for s in no_hist if s["label"]["tool_calls"][-1]["name"] != ASK and len(s["label"]["tool_calls"]) >= 2]
    return rng.sample(execs, k_exec) + rng.sample(asks, k_ask)


def example_text(s: dict) -> str:
    calls = "\n".join(json.dumps(c, ensure_ascii=False) for c in s["label"]["tool_calls"]) or "(không gọi tool nào)"
    return (f"- Thời điểm: {s['context']['current_time']}\n  Người dùng nói: \"{s['audio_text']}\"\n"
            f"  Các lời gọi đúng:\n" + "\n".join("    " + line for line in calls.splitlines()))


def make_context(template: dict, app: str, apps_by_id: dict, drop_apps: set[str], rng: random.Random) -> dict:
    """Context of a fit sample with the target app added: same time, place and user; 2-4 of its other apps kept."""
    ctx = copy.deepcopy(template["context"])
    others = [a for a in ctx["installed_apps"] if a not in drop_apps and a != app and a in apps_by_id]
    keep = rng.sample(others, min(len(others), rng.randint(2, 4)))
    apps = {a: {"tools": [t["name"] for t in apps_by_id[a]["tools"]]} for a in keep + [app]}
    ctx["installed_apps"] = dict(sorted(apps.items(), key=lambda kv: rng.random()))
    return ctx


# ---------------------------------------------------------------- prompts

STRING_CALL = {"type": "object", "additionalProperties": False, "required": ["name", "arguments_json"],
               "properties": {"name": {"type": "string"}, "arguments_json": {"type": "string"}}}
GEN_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["samples"], "properties": {"samples": {
    "type": "array", "items": {"type": "object", "additionalProperties": False,
                               "required": ["context_index", "category", "scenario", "state_json", "request", "calls"],
                               "properties": {
                                   "context_index": {"type": "integer"},
                                   "category": {"type": "string", "enum": ["execute", "lookup", "ask_missing"]},
                                   "scenario": {"type": "string"},
                                   "state_json": {"type": "string"},
                                   "request": {"type": "string"},
                                   "calls": {"type": "array", "items": STRING_CALL}}}}}}
SOLVE_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["calls"],
                "properties": {"calls": {"type": "array", "items": STRING_CALL}}}

GEN_TASK = """Bạn tạo dữ liệu huấn luyện cho một trợ lý giọng nói tiếng Việt. Trợ lý nhận câu nói của người dùng và gọi tool của các app đã cài trên điện thoại. Điểm được chấm bằng cách so các lời gọi tool và trạng thái cuối của app với đáp án, nên đáp án phải đúng tuyệt đối.

Hãy viết {n} mẫu MỚI, khác nhau, đều dùng app `{app}` ({name_vi}: {desc}). Mỗi mẫu dùng đúng context có số thứ tự `context_index` tương ứng trong danh sách context bên dưới (mẫu thứ i dùng context i).
- {n_ask} mẫu loại `ask_missing`, {n_lookup} mẫu loại `lookup`, còn lại loại `execute`.
- `execute`: người dùng nói đủ thông tin; đáp án là chuỗi lời gọi tool làm xong việc, thường đọc trước (tìm/liệt kê để lấy ID) rồi mới ghi.
- `lookup`: người dùng chỉ hỏi thông tin (xem, kiểm tra, còn bao nhiêu...); đáp án chỉ gồm lời gọi đọc, không ghi gì.
- `ask_missing`: người dùng thiếu một tham số bắt buộc không suy ra được (hoặc có nhiều đối tượng khớp mà không biết chọn cái nào); đáp án có thể đọc trước, rồi kết thúc bằng sys.ask_missing_info với tool_name và params còn thiếu (đúng tên trong schema). Không gọi chính tool đang thiếu tham số. Nếu câu có nhiều việc, làm xong các việc đủ thông tin trước rồi mới hỏi phần thiếu.

Yêu cầu với từng mẫu:
1. `state_json`: chuỗi JSON của trạng thái ban đầu, dạng {{"<app id>": {{...}}}}, viết đúng cấu trúc mà code bộ giả lập bên dưới đọc (tên collection, tên trường, kiểu dữ liệu). Có 3-8 bản ghi hợp lý, có cả bản ghi gây nhiễu. ID theo kiểu ngắn như code dùng (ví dụ book_01). Nếu đáp án gọi tool của app khác (ví dụ contacts), thêm state cho app đó và app đó phải có trong context.
2. `request`: câu người dùng NÓI, tự nhiên như giọng nói thật, 8-40 từ. Người dùng không bao giờ đọc ID. Ngày giờ nói kiểu tương đối ("mai", "thứ sáu này", "chín giờ tối"). Các câu trong lượt này phải KHÁC NHAU về cách nói: đổi cách mở đầu (có câu bắt đầu bằng "ừ,", "ờ", "thế", "nếu", hay vào thẳng động từ), đổi từ nhờ vả ("giúp" khoảng 1/4 số câu, "giùm" chỉ khoảng 1/8, còn lại "cho", "với", hoặc không dùng), khoảng 2/5 số câu có từ hai việc trở lên, có giọng miền; câu tự sửa giữa chừng ("à không...") và câu điều kiện ("nếu ... thì ...") mỗi loại chỉ khoảng 1/10 số câu như dữ liệu thật. Không câu nào được lặp khuôn của câu khác. Bắt chước phân bố cách nói của các câu thật dưới đây (chỉ học cách nói, không chép nội dung).
3. `calls`: danh sách lời gọi tool đúng theo thứ tự; mỗi lời gọi có `name` và `arguments_json` (chuỗi JSON của tham số). ID phải lấy từ kết quả của lời gọi đọc trước đó (trợ lý không thấy state). Thời gian đầy đủ ISO-8601 có giây và +07:00, tính từ thời điểm của context.
4. Chạy thử trong đầu từng lời gọi trên state bằng code bộ giả lập: không được có lời gọi trả về done=false hoặc lỗi.
5. `scenario`: một câu mô tả ngắn mẫu này kiểm tra điều gì.

Quy tắc của trợ lý (đáp án phải theo đúng các quy tắc này):
{rules}

Ví dụ đáp án đúng từ dữ liệu thật (app khác, chỉ để học quy ước):
{examples}

Các câu người dùng thật nói (chỉ để học cách nói):
{styles}

Các tool của app `{app}` (JSON schema; `required` là tham số bắt buộc; `x-ref` là ID lấy từ kết quả tool khác):
{tools}

Tool hệ thống:
{ask_tool}

Code bộ giả lập của app `{app}` (cấu trúc state và cách mỗi tool chạy):
```python
{app_src}
```

Các hàm dùng chung của bộ giả lập (read/find/create/patch...):
```python
{base_src}
```

Danh sách context (thời điểm, người dùng, app đã cài):
{contexts}
"""

SOLVE_TASK = """Bạn là trợ lý giọng nói tiếng Việt. Hãy liệt kê các lời gọi tool mà trợ lý phải làm cho câu nói dưới đây, theo đúng thứ tự.
Trợ lý KHÔNG thấy dữ liệu của app: muốn biết ID thì phải gọi tool đọc trước. Dữ liệu app được đưa cho bạn chỉ để bạn biết các lời gọi đọc sẽ trả về gì.

Quy tắc của trợ lý:
{rules}

Ví dụ đáp án đúng từ dữ liệu thật:
{examples}

Thời điểm: {now}
Người dùng: {profile}
Các tool có thể gọi (JSON schema):
{tools}

Dữ liệu app (chỉ để bạn biết kết quả các lời gọi đọc):
{state}

Câu người dùng nói: "{request}"

Trả về `calls`: mỗi lời gọi có `name` và `arguments_json` (chuỗi JSON của tham số). Không cần gọi tool nào thì trả về danh sách rỗng."""


def tools_json(names: list[str], tools: dict) -> str:
    return "\n".join(json.dumps({k: v for k, v in tools[n].items() if k in ("name", "kind", "description", "parameters")},
                                ensure_ascii=False) for n in names)


def context_text(i: int, ctx: dict) -> str:
    p = ctx.get("user_profile", {})
    return (f"[{i}] thời điểm {ctx['current_time']}; người dùng {p.get('name')}, ở {p.get('city')}, nhà {p.get('home_address')}, "
            f"chỗ làm {p.get('work_address')}; app đã cài: {', '.join(ctx['installed_apps'])}")


# ---------------------------------------------------------------- checks

def parse_args(text: str) -> dict:
    """The JSON object in arguments_json. Stray closing braces after it (`{}}`, seen from the model) are ignored;
    any other trailing text is an error."""
    text = (text or "").strip()
    if not text:
        return {}
    obj, end = json.JSONDecoder().raw_decode(text)
    if text[end:].strip(" \n\t}"):
        raise ValueError(f"extra text after arguments: {text[end:][:40]!r}")
    if not isinstance(obj, dict):
        raise ValueError("arguments are not an object")
    return obj


def parse_calls(raw: list[dict]) -> list[dict]:
    return [{"name": c["name"], "arguments": parse_args(c.get("arguments_json", ""))} for c in raw]


def _strings(x, out: set) -> set:
    if isinstance(x, dict):
        for v in x.values():
            _strings(v, out)
    elif isinstance(x, list):
        for v in x:
            _strings(v, out)
    elif isinstance(x, (str, int)) and not isinstance(x, bool):
        out.add(str(x))
    return out


def state_ids(state: dict) -> set[str]:
    ids = set()

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("id"), str):
                ids.add(x["id"])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(state)
    return ids


def simulate(zt, ctx: dict, state: dict, calls: list[dict], catalog: dict):
    """Run calls on a fresh simulator. Returns (results, final states, simulator)."""
    apps = {a: {"tools": v["tools"], "state": copy.deepcopy(state.get(a, {}))} for a, v in ctx["installed_apps"].items()}
    sim = zt.executor.Simulator({"context": {"current_time": ctx["current_time"], "installed_apps": apps}}, catalog)
    results = [sim.call(c["name"], c["arguments"]) for c in calls]
    return results, sim


def check_sample(zt, g: dict, tools: dict, catalog: dict) -> tuple[str | None, list]:
    """Simulator checks of one generated sample (no LLM). Returns (reject reason or None, tool results)."""
    ctx, state, calls = g["context"], g["state"], g["calls"]
    installed = {t for a in ctx["installed_apps"].values() for t in a["tools"]} | {ASK}
    for app in state:
        if app not in ctx["installed_apps"]:
            return f"state_not_installed: {app}", []
    ids = state_ids(state)
    for i in sorted(ids, key=len, reverse=True):
        if re.search(rf"(?<![\w]){re.escape(i)}(?![\w])", g["request"], re.I):
            return f"id_in_text: {i}", []
    if not calls and g["category"] != "out_of_scope":
        return "no_calls", []
    for c in calls:
        if c["name"] not in installed:
            return f"schema: {c['name']} not installed", []
    results, sim = simulate(zt, ctx, state, calls, catalog)
    seen = set()
    for c, r in zip(calls, results):
        if isinstance(r, dict) and r.get("ok") is False:
            return f"schema: {c['name']}: {str(r.get('error'))[:100]}", results
        if isinstance(r, dict) and r.get("done") is False:
            return f"noop: {c['name']}: {str(r.get('message'))[:100]}", results
        props = tools.get(c["name"], {}).get("parameters", {}).get("properties", {})
        for k, v in c["arguments"].items():
            if props.get(k, {}).get("x-ref") and isinstance(v, str) and v not in seen:
                return f"invented_id: {c['name']}.{k}={v}", results
        _strings(r, seen)
    kinds = [tools.get(c["name"], {}).get("kind") for c in calls]
    if g["category"] in ("execute", "lookup") and calls[-1]["name"] == ASK:
        return f"bad_{g['category']}: ends with ask", results
    if g["category"] == "execute":
        initial = {a: state.get(a, {}) for a in ctx["installed_apps"]}
        if "write" not in kinds or sim.states == initial:
            return "no_write", results
    elif g["category"] == "lookup":
        if any(k != "read" for k in kinds):
            return "bad_lookup: not read-only", results
    elif g["category"] == "ask_missing":
        last = calls[-1]
        if last["name"] != ASK:
            return "bad_ask: does not end with sys.ask_missing_info", results
        tname, params = last["arguments"].get("tool_name"), last["arguments"].get("params")
        if tname not in installed or tname == ASK or not isinstance(params, list) or not params:
            return f"bad_ask: tool {tname}", results
        if any(c["name"] == tname for c in calls[:-1]):
            return f"bad_ask: {tname} already called before asking for it", results
        req = set(required(tools[tname]))
        if not set(params) <= req:
            return f"bad_ask: {sorted(set(params) - req)} not required by {tname}", results
    if len(calls) > 8:
        return "too_many_calls", results
    return None, results


def write_ask_names(calls: list[dict], tools: dict) -> Counter:
    return Counter(c["name"] for c in calls if tools.get(c["name"], {}).get("kind") in ("write", "meta"))


def ask_key(calls: list[dict]):
    a = [c for c in calls if c["name"] == ASK]
    return (a[-1]["arguments"].get("tool_name"), sorted(a[-1]["arguments"].get("params") or [])) if a else None


def _norm_text(t: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", t.lower()).split())


def near_duplicate(text: str, seen: list[str], threshold: float = 0.8) -> str | None:
    """An earlier accepted request (same app) that this one nearly repeats."""
    t = _norm_text(text)
    for s in seen:
        if difflib.SequenceMatcher(None, t, _norm_text(s)).ratio() >= threshold:
            return s
    return None


def solver_agrees(zt, g: dict, solved: list[dict], tools: dict, catalog: dict) -> str | None:
    """None when the independent calls reach the same final state with the same write/ask calls."""
    _, sim_gold = simulate(zt, g["context"], g["state"], g["calls"], catalog)
    _, sim_solv = simulate(zt, g["context"], g["state"], solved, catalog)
    if write_ask_names(g["calls"], tools) != write_ask_names(solved, tools):
        return (f"solver: other writes/asks {dict(write_ask_names(solved, tools))} "
                f"vs {dict(write_ask_names(g['calls'], tools))}")
    if ask_key(g["calls"]) != ask_key(solved):
        return f"solver: other ask {ask_key(solved)} vs {ask_key(g['calls'])}"
    if sim_gold.states != sim_solv.states:
        return "solver: other final state"
    return None


# ---------------------------------------------------------------- recipe v2 (06/11): the shape of real samples
#
# Pilot 1 (lao_w1) samples had no history, used one app and always made a call. Real fit_lao samples (1,283;
# JOURNAL entry 104): 64% have history, 16% reuse an ID returned in it, 46% use two apps or more, 8% make no call,
# 14% end with an ask, 8% only read. v2 asks the generator for each of these shapes per sample and checks them.
# The same measurement showed that pilot-1 calls were not the problem one might expect: optional parameters filled
# per write call 0.31 vs 0.32 real, and executes without history start with a read 89% vs 90% real.

V2_CATEGORY = (("none", 0.07), ("ask_missing", 0.14), ("lookup", 0.08), ("execute", 0.71))
V2_HIST_REF = 0.20       # a previous turn on the app returns the object the request then refers to (not for none)
V2_HIST_DISTRACT = 0.45  # an unrelated real conversation (the template's own history) comes before the request
V2_REF_DISTRACT = 0.5    # a ref sample also gets the unrelated conversation before its previous turn
V2_MULTI = 0.40          # of execute / ask samples: the request also needs one more installed app
V2_MAX_HIST = 8          # history entries of a distractor conversation (real: 2-24, most <= 8)
COMBINE_APPS = ("contacts", "calendar", "reminders", "notes", "sms", "chat_ott", "email", "alarm", "tasks",
                "banking", "ewallet", "maps", "shopping_list")

HIST_TURN = {"type": "object", "additionalProperties": False, "required": ["request", "calls", "reply"],
             "properties": {"request": {"type": "string"}, "calls": {"type": "array", "items": STRING_CALL},
                            "reply": {"type": "string"}}}
GEN_SCHEMA_V2 = {"type": "object", "additionalProperties": False, "required": ["samples"], "properties": {"samples": {
    "type": "array", "items": {"type": "object", "additionalProperties": False,
                               "required": ["context_index", "category", "scenario", "state_json", "history_turns",
                                            "request", "calls"],
                               "properties": {
                                   "context_index": {"type": "integer"},
                                   "category": {"type": "string", "enum": ["execute", "lookup", "ask_missing", "none"]},
                                   "scenario": {"type": "string"},
                                   "state_json": {"type": "string"},
                                   "history_turns": {"type": "array", "items": HIST_TURN},
                                   "request": {"type": "string"},
                                   "calls": {"type": "array", "items": STRING_CALL}}}}}}

GEN_TASK_V2 = """Bạn tạo dữ liệu huấn luyện cho một trợ lý giọng nói tiếng Việt. Trợ lý nhận câu nói của người dùng và gọi tool của các app đã cài trên điện thoại. Điểm được chấm bằng cách so các lời gọi tool và trạng thái cuối của app với đáp án, nên đáp án phải đúng tuyệt đối và theo đúng quy ước của dữ liệu thật.

Hãy viết {n} mẫu MỚI, khác nhau, đều dùng app `{app}` ({name_vi}: {desc}). Mẫu thứ i dùng context i và PHẢI theo đúng yêu cầu i trong danh sách "Yêu cầu từng mẫu" ở cuối.

Các loại mẫu (`category`):
- `execute`: người dùng nói đủ thông tin; đáp án là chuỗi lời gọi làm xong việc. Cần ID thì đọc trước (tìm/liệt kê) rồi mới ghi; ID đã có trong lượt trước thì dùng lại, không đọc lại.
- `lookup`: người dùng chỉ hỏi thông tin (xem, kiểm tra, còn bao nhiêu...); đáp án chỉ gồm lời gọi đọc.
- `ask_missing`: người dùng thiếu một tham số bắt buộc không suy ra được (hoặc nhiều đối tượng khớp mà không biết chọn cái nào); đáp án có thể đọc trước, rồi kết thúc bằng sys.ask_missing_info với tool_name và params còn thiếu (đúng tên trong schema). Không gọi chính tool đang thiếu tham số. Câu có nhiều việc thì làm xong các việc đủ thông tin trước rồi mới hỏi phần thiếu.
- `none`: trợ lý không gọi tool nào (`calls` rỗng): người dùng huỷ hay đổi ý giữa câu ("à thôi khỏi"), dặn đừng làm gì, chỉ trò chuyện hay cảm ơn, hoặc nhờ việc liên quan tới app `{app}` mà không tool nào đã cài làm được.

Yêu cầu "dùng thêm app B": câu nói có hai việc (hoặc một việc cần cả hai app); đáp án gọi tool của cả `{app}` và B. Viết state cho cả hai app.
Yêu cầu "có lượt trước": `history_turns` có đúng 1 lượt trước đó trong cùng cuộc trò chuyện: người dùng hỏi hay nhờ một việc với app `{app}`, trợ lý gọi tool (thường là đọc) và trả lời một câu ngắn nêu kết quả (`reply`, ví dụ tên và thông tin chính của đối tượng, không đọc ID). Câu cuối (`request`) nhắc lại đối tượng đó ("cuốn đó", "cái lúc nãy", hoặc gọi tên), và đáp án cuối dùng lại ID có trong kết quả của lượt trước, KHÔNG gọi lại tool đọc để lấy ID đó. Lời gọi của lượt trước chạy trên state trước, rồi mới tới đáp án cuối. Không có yêu cầu này thì `history_turns` là danh sách rỗng.

Yêu cầu với từng mẫu:
1. `state_json`: chuỗi JSON của trạng thái ban đầu, dạng {{"<app id>": {{...}}}}, viết đúng cấu trúc mà code bộ giả lập bên dưới đọc (tên collection, tên trường, kiểu dữ liệu). Có 3-8 bản ghi hợp lý, có cả bản ghi gây nhiễu. ID theo kiểu ngắn như code dùng (ví dụ book_01). Chỉ viết state cho app có trong context.
2. `request`: câu người dùng NÓI, tự nhiên như giọng nói thật, 8-40 từ. Người dùng không bao giờ đọc ID. Ngày giờ nói kiểu tương đối ("mai", "thứ sáu này", "chín giờ tối"). Phần lớn người dùng chỉ nói thông tin cần thiết; chỉ nói thêm chi tiết tuỳ chọn khi tự nhiên. Các câu trong lượt này phải KHÁC NHAU về cách nói: đổi cách mở đầu (có câu bắt đầu bằng "ừ,", "ờ", "thế", "nếu", hay vào thẳng động từ), đổi từ nhờ vả ("giúp" khoảng 1/4 số câu, "giùm" chỉ khoảng 1/8, còn lại "cho", "với", hoặc không dùng), có giọng miền; câu tự sửa giữa chừng ("à không...") và câu điều kiện ("nếu ... thì ...") mỗi loại chỉ khoảng 1/10 số câu như dữ liệu thật. Không câu nào được lặp khuôn của câu khác. Bắt chước phân bố cách nói của các câu thật dưới đây (chỉ học cách nói, không chép nội dung).
3. `calls`: danh sách lời gọi tool đúng theo thứ tự; mỗi lời gọi có `name` và `arguments_json` (chuỗi JSON của tham số). ID phải lấy từ kết quả của lời gọi đọc trước đó hoặc của lượt trước (trợ lý không thấy state). Chỉ điền tham số tuỳ chọn khi người dùng nói rõ giá trị đó. Thời gian đầy đủ ISO-8601 có giây và +07:00, tính từ thời điểm của context.
4. Chạy thử trong đầu từng lời gọi (cả của lượt trước) trên state bằng code bộ giả lập: không được có lời gọi trả về done=false hoặc lỗi.
5. `scenario`: một câu mô tả ngắn mẫu này kiểm tra điều gì.

Quy tắc của trợ lý (đáp án phải theo đúng các quy tắc này):
{rules}

Ví dụ đáp án đúng từ dữ liệu thật (app khác, chỉ để học quy ước):
{examples}

Các câu người dùng thật nói (chỉ để học cách nói):
{styles}

Các tool (JSON schema; `required` là tham số bắt buộc; `x-ref` là ID lấy từ kết quả tool khác):
{tools}

Tool hệ thống:
{ask_tool}

Code bộ giả lập của các app (cấu trúc state và cách mỗi tool chạy):
{app_src}

Các hàm dùng chung của bộ giả lập (read/find/create/patch...):
```python
{base_src}
```

Danh sách context (thời điểm, người dùng, app đã cài):
{contexts}

Yêu cầu từng mẫu:
{specs}
"""

SOLVE_TASK_V2 = """Bạn là trợ lý giọng nói tiếng Việt. Hãy liệt kê các lời gọi tool mà trợ lý phải làm cho câu nói CUỐI của người dùng dưới đây, theo đúng thứ tự.
Trợ lý KHÔNG thấy dữ liệu của app: muốn biết ID thì phải gọi tool đọc trước, trừ khi ID đã có trong kết quả của lượt trước. Dữ liệu app được đưa cho bạn chỉ để bạn biết các lời gọi đọc sẽ trả về gì.

Quy tắc của trợ lý:
{rules}

Ví dụ đáp án đúng từ dữ liệu thật:
{examples}

Thời điểm: {now}
Người dùng: {profile}
Các tool có thể gọi (JSON schema):
{tools}

Dữ liệu app lúc này (chỉ để bạn biết kết quả các lời gọi đọc):
{state}

Các lượt trước trong cuộc trò chuyện:
{history}

Câu người dùng nói cuối cùng: "{request}"

Trả về `calls`: mỗi lời gọi có `name` và `arguments_json` (chuỗi JSON của tham số). Không cần gọi tool nào thì trả về danh sách rỗng."""


def _pick_weighted(rng: random.Random, pairs) -> str:
    r, acc = rng.random(), 0.0
    for k, p in pairs:
        acc += p
        if r < acc:
            return k
    return pairs[-1][0]


def _history_apps(history: list[dict]) -> set[str]:
    return {c["name"].split(".", 1)[0] for h in history for c in (h.get("tool_calls") or [])}


def history_ref_examples(fits: list[dict], tools: dict) -> list[tuple[dict, int]]:
    """(sample, index of the assistant turn) where the final calls reuse an x-ref ID that turn returned."""
    out = []
    for s in fits:
        if not s["history"]:
            continue
        own, ids = set(), []
        for i, c in enumerate(s["label"]["tool_calls"]):
            props = tools.get(c["name"], {}).get("parameters", {}).get("properties", {})
            ids += [v for k, v in c["arguments"].items() if props.get(k, {}).get("x-ref") and isinstance(v, str) and v not in own]
            if i < len(s["label"].get("tool_results") or []):
                _strings(s["label"]["tool_results"][i], own)
        for j in range(len(s["history"]) - 1, -1, -1):
            h = s["history"][j]
            if h["role"] == "assistant" and j > 0 and set(ids) & _strings(h.get("tool_results") or [], set()):
                out.append((s, j))
                break
    return out


def pick_examples_v2(fits: list[dict], refs: list[tuple[dict, int]], tools: dict, rng: random.Random) -> str:
    """New gold examples for every call: 3 executes (one with two apps), an ask, a lookup, a no-call request,
    and a request that reuses an ID from the previous turn (shown with that turn only)."""
    no_hist = [s for s in fits if not s["history"]]

    def kind(s):
        c = s["label"]["tool_calls"]
        if not c:
            return "none"
        if c[-1]["name"] == ASK:
            return "ask"
        if all(tools.get(x["name"], {}).get("kind") == "read" for x in c):
            return "lookup"
        return "multi" if len({x["name"].split(".", 1)[0] for x in c}) > 1 else "execute"
    by = {}
    for s in no_hist:
        by.setdefault(kind(s), []).append(s)
    chosen = rng.sample(by.get("execute", []), 2) + rng.sample(by.get("multi", []), 1)
    for k in ("ask", "lookup", "none"):
        chosen += rng.sample(by.get(k, []), 1) if by.get(k) else []
    texts = [example_text(s) for s in chosen]
    if refs:
        s, j = rng.choice(refs)
        u, a = s["history"][j - 1], s["history"][j]
        calls = "\n".join("    " + json.dumps(c, ensure_ascii=False) for c in a.get("tool_calls") or [])
        res = json.dumps(a.get("tool_results") or [], ensure_ascii=False)[:600]
        final = "\n".join("    " + json.dumps(c, ensure_ascii=False) for c in s["label"]["tool_calls"])
        texts.append(f"- Thời điểm: {s['context']['current_time']}\n  Lượt trước, người dùng nói: \"{u.get('audio_text')}\"\n"
                     f"  Trợ lý gọi:\n{calls}\n  Kết quả: {res}\n  Trợ lý trả lời: \"{a.get('text')}\"\n"
                     f"  Người dùng nói tiếp: \"{s['audio_text']}\"\n  Các lời gọi đúng:\n{final}")
    rng.shuffle(texts)
    return "\n".join(texts)


def make_specs_v2(n: int, app: str, fits: list[dict], apps_by_id: dict, drop: set[str], zt, rng: random.Random):
    """(context, spec, distractor history) for each sample of one generation call."""
    with_hist = [s for s in fits if 0 < len(s["history"]) <= V2_MAX_HIST and not (_history_apps(s["history"]) & drop)]
    out = []
    for _ in range(n):
        cat = _pick_weighted(rng, V2_CATEGORY)
        r = rng.random()
        hist = "ref" if cat != "none" and r < V2_HIST_REF else ("distract" if r < V2_HIST_REF + V2_HIST_DISTRACT else "")
        distract = hist == "distract" or (hist == "ref" and rng.random() < V2_REF_DISTRACT)
        tpl = rng.choice(with_hist if distract else fits)
        ctx = copy.deepcopy(tpl["context"])
        apps = {a: v for a, v in ctx["installed_apps"].items() if a not in drop and a in apps_by_id}
        items = list(apps.items())
        items.insert(rng.randint(0, len(items)), (app, {"tools": [t["name"] for t in apps_by_id[app]["tools"]]}))
        ctx["installed_apps"] = dict(items)
        other = None
        if cat in ("execute", "ask_missing") and rng.random() < V2_MULTI:
            cands = [a for a in COMBINE_APPS if a != app and a in apps_by_id and a in zt.executor.APPS and a not in drop]
            installed = [a for a in cands if a in ctx["installed_apps"]]
            other = rng.choice(installed or cands)
            if other not in ctx["installed_apps"]:
                ctx["installed_apps"][other] = {"tools": [t["name"] for t in apps_by_id[other]["tools"]]}
        spec = {"category": cat, "other_app": other, "history": hist}
        out.append((ctx, spec, copy.deepcopy(tpl["history"]) if distract else []))
    return out


def spec_text(i: int, spec: dict) -> str:
    parts = [f"loại `{spec['category']}`"]
    if spec.get("other_app"):
        parts.append(f"dùng thêm app `{spec['other_app']}`")
    parts.append("có lượt trước (history_turns 1 lượt)" if spec.get("history") == "ref" else "history_turns rỗng")
    return f"[{i}] " + "; ".join(parts)


def simulate_v2(zt, ctx: dict, state: dict, turns: list[list[dict]], calls: list[dict], catalog: dict):
    """Run the previous turns' calls, then the final calls, on one simulator.
    Returns (results of each previous turn, final results, state after the previous turns, simulator)."""
    apps = {a: {"tools": v["tools"], "state": copy.deepcopy(state.get(a, {}))} for a, v in ctx["installed_apps"].items()}
    sim = zt.executor.Simulator({"context": {"current_time": ctx["current_time"], "installed_apps": apps}}, catalog)
    turn_results = [[sim.call(c["name"], c["arguments"]) for c in t] for t in turns]
    before = copy.deepcopy(sim.states)
    results = [sim.call(c["name"], c["arguments"]) for c in calls]
    return turn_results, results, before, sim


def _arg_strings(x) -> set[str]:
    return {v for v in _strings(x, set()) if isinstance(v, str)}


def _call_errors(calls, results, tools, seen: set, installed: set, where: str, ids: set[str] = frozenset()) -> str | None:
    """ids: the IDs of the state. An argument equal to one of them must come from an earlier result (many schemas
    do not mark their ID parameters with x-ref, e.g. loyalty.redeem.reward_id)."""
    for c in calls:
        if c["name"] not in installed:
            return f"{where}schema: {c['name']} not installed"
    for c, r in zip(calls, results):
        if isinstance(r, dict) and r.get("ok") is False:
            return f"{where}schema: {c['name']}: {str(r.get('error'))[:100]}"
        if isinstance(r, dict) and r.get("done") is False:
            return f"{where}noop: {c['name']}: {str(r.get('message'))[:100]}"
        props = tools.get(c["name"], {}).get("parameters", {}).get("properties", {})
        for k, v in c["arguments"].items():
            if props.get(k, {}).get("x-ref") and isinstance(v, str) and v not in seen:
                return f"{where}invented_id: {c['name']}.{k}={v}"
            bad = sorted((_arg_strings(v) & ids) - seen)
            if bad:
                return f"{where}invented_id: {c['name']}.{k}={bad[0]}"
        _strings(r, seen)
    return None


def check_sample_v2(zt, g: dict, tools: dict, catalog: dict) -> tuple[str | None, list, list]:
    """Checks of one v2 sample. g: context, state, calls, category, request, turns (previous turns with parsed
    calls), spec. Returns (reject reason or None, results of the previous turns, final results)."""
    ctx, state, calls, spec, turns = g["context"], g["state"], g["calls"], g["spec"], g["turns"]
    installed = {t for a in ctx["installed_apps"].values() for t in a["tools"]} | {ASK}
    for app in state:
        if app not in ctx["installed_apps"]:
            return f"state_not_installed: {app}", [], []
    if g["category"] != spec["category"]:
        return f"spec_category: {g['category']} instead of {spec['category']}", [], []
    want_turns = 1 if spec.get("history") == "ref" else 0
    if len(turns) != want_turns:
        return f"spec_history: {len(turns)} previous turns, wanted {want_turns}", [], []
    ids = state_ids(state)
    texts = [g["request"]] + [t["request"] for t in turns] + [t.get("reply", "") for t in turns]
    for i in sorted(ids, key=len, reverse=True):
        for text in texts:
            if re.search(rf"(?<![\w]){re.escape(i)}(?![\w])", text, re.I):
                return f"id_in_text: {i}", [], []
    turn_results, results, before, sim = simulate_v2(zt, ctx, state, [t["calls"] for t in turns], calls, catalog)
    seen: set = set()
    for t, tr in zip(turns, turn_results):
        if not t["calls"]:
            return "spec_history: previous turn makes no call", turn_results, results
        err = _call_errors(t["calls"], tr, tools, seen, installed, "history_", ids)
        if err:
            return err, turn_results, results
    from_history = set(seen)
    if g["category"] == "none":
        return (None if not calls else "bad_none: calls a tool"), turn_results, results
    if not calls:
        return "no_calls", turn_results, results
    err = _call_errors(calls, results, tools, seen, installed, "", ids)
    if err:
        return err, turn_results, results
    kinds = [tools.get(c["name"], {}).get("kind") for c in calls]
    if g["category"] in ("execute", "lookup") and calls[-1]["name"] == ASK:
        return f"bad_{g['category']}: ends with ask", turn_results, results
    if g["category"] == "execute":
        if "write" not in kinds or sim.states == before:
            return "no_write", turn_results, results
    elif g["category"] == "lookup":
        if any(k != "read" for k in kinds):
            return "bad_lookup: not read-only", turn_results, results
    elif g["category"] == "ask_missing":
        last = calls[-1]
        if last["name"] != ASK:
            return "bad_ask: does not end with sys.ask_missing_info", turn_results, results
        tname, params = last["arguments"].get("tool_name"), last["arguments"].get("params")
        if tname not in installed or tname == ASK or not isinstance(params, list) or not params:
            return f"bad_ask: tool {tname}", turn_results, results
        if any(c["name"] == tname for c in calls[:-1]):
            return f"bad_ask: {tname} already called before asking for it", turn_results, results
        req = set(required(tools[tname]))
        if not set(params) <= req:
            return f"bad_ask: {sorted(set(params) - req)} not required by {tname}", turn_results, results
    if spec.get("other_app"):
        from .sft import used_apps
        if not {g["app"], spec["other_app"]} <= used_apps(calls):
            return f"spec_other_app: calls do not use both {g['app']} and {spec['other_app']}", turn_results, results
    if spec.get("history") == "ref":
        own, reused = set(), False
        for c, r in zip(calls, results):
            reused |= bool((_arg_strings(c["arguments"]) & ids & from_history) - own)
            _strings(r, own)
        if not reused:
            return "spec_history: final calls do not reuse an ID from the previous turn", turn_results, results
    if len(calls) > 8:
        return "too_many_calls", turn_results, results
    return None, turn_results, results


def _norm_state(x):
    """Final states compared up to case and spaces of free text ("Họp" vs "họp" in a title is not a wrong label)."""
    if isinstance(x, dict):
        return {k: _norm_state(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_norm_state(v) for v in x]
    return " ".join(x.lower().split()) if isinstance(x, str) else x


def solver_agrees_v2(zt, g: dict, solved: list[dict], tools: dict, catalog: dict) -> str | None:
    turns = [t["calls"] for t in g["turns"]]
    _, _, _, sim_gold = simulate_v2(zt, g["context"], g["state"], turns, g["calls"], catalog)
    _, _, _, sim_solv = simulate_v2(zt, g["context"], g["state"], turns, solved, catalog)
    if write_ask_names(g["calls"], tools) != write_ask_names(solved, tools):
        return (f"solver: other writes/asks {dict(write_ask_names(solved, tools))} "
                f"vs {dict(write_ask_names(g['calls'], tools))}")
    if ask_key(g["calls"]) != ask_key(solved):
        return f"solver: other ask {ask_key(solved)} vs {ask_key(g['calls'])}"
    if _norm_state(sim_gold.states) != _norm_state(sim_solv.states):
        return "solver: other final state"
    return None


def history_text(history: list[dict]) -> str:
    """Previous turns as the solver reads them (results shortened)."""
    lines = []
    for h in history:
        if h["role"] == "user":
            lines.append(f"- Người dùng: \"{h.get('audio_text')}\"")
            continue
        for c, r in zip(h.get("tool_calls") or [], h.get("tool_results") or [{}] * 99):
            lines.append(f"  Trợ lý gọi {c['name']} {json.dumps(c['arguments'], ensure_ascii=False)} -> "
                         f"{json.dumps(r, ensure_ascii=False)[:800]}")
        lines.append(f"  Trợ lý: \"{h.get('text') or ''}\"")
    return "\n".join(lines) or "(không có)"


def turns_as_history(turns: list[dict], turn_results: list[list]) -> list[dict]:
    out = []
    for t, r in zip(turns, turn_results):
        out += [{"role": "user", "audio": None, "audio_text": t["request"]},
                {"role": "assistant", "text": t.get("reply", ""), "tool_calls": t["calls"], "tool_results": r}]
    return out


# ---------------------------------------------------------------- sft

def to_train_sample(g: dict, results: list, history: list | None = None) -> dict:
    return {"id": g["id"], "audio": None, "audio_text": g["request"], "context": g["context"], "history": history or [],
            "label": {"tool_calls": g["calls"], "tool_results": results}, "_src": SRC, "_app": g["app"]}


# ---------------------------------------------------------------- commands

def _paths(tag: str, no_solver: bool = False) -> dict:
    """A check without the solver writes its own files, so it never replaces a full check's result."""
    out = f"synth_{tag}_nosolver" if no_solver else f"synth_{tag}"
    return {"raw": GEN_DIR / f"synth_{tag}_raw.jsonl", "ok": GEN_DIR / f"{out}.jsonl",
            "rej": GEN_DIR / f"{out}_rejected.jsonl", "usage": GEN_DIR / f"synth_{tag}_usage.jsonl",
            "report": GEN_DIR / f"{out}.report.json", "solver": GEN_DIR / f"synth_{tag}_solver.jsonl"}


def cmd_gen(a):
    if a.recipe == "v2":
        return cmd_gen_v2(a)
    P = _paths(a.tag)
    rng = random.Random(a.seed)
    zt = zaic_tools(a.split, a.root)
    catalog = load_catalog(a.split, a.root)
    tools, apps_by_id = catalog_tools(catalog), {x["id"]: x for x in catalog["apps"]}
    drop = set(json.loads(Path(a.drop_apps).read_text())) if a.drop_apps else set()
    fits = fit_samples(a.root, a.fit, drop)
    examples = "\n".join(example_text(s) for s in pick_examples(fits, rng))
    client = Client(a.model, a.base_url, P["usage"], a.max_usd, a.total_usd)
    done = Counter(r["app"] for r in load_jsonl(P["raw"])) if P["raw"].exists() else Counter()
    n_out = sum(done.values())
    for app in a.apps.split(","):
        if app not in apps_by_id or app not in zt.executor.APPS:
            raise SystemExit(f"app {app!r} not in the {a.split} catalog or simulator")
        while done[app] < a.per_app:
            n = min(a.batch, a.per_app - done[app])
            n_ask = max(0, round(n * a.ask_frac + rng.random() - 0.5))
            n_lookup = min(max(0, round(n * a.lookup_frac + rng.random() - 0.5)), max(0, n - 1 - n_ask))
            styles = "\n".join(f'- "{s["audio_text"]}"' for s in rng.sample(fits, 12))  # new real requests every call
            ctxs = [make_context(rng.choice(fits), app, apps_by_id, drop, rng) for _ in range(n)]
            prompt = GEN_TASK.format(
                n=n, app=app, name_vi=apps_by_id[app].get("name_vi", ""), desc=apps_by_id[app].get("description", ""),
                n_ask=n_ask, n_lookup=n_lookup, rules=SYSTEM_RULES, examples=examples, styles=styles,
                tools=tools_json([t["name"] for t in apps_by_id[app]["tools"]], tools), ask_tool=tools_json([ASK], tools),
                app_src=app_source(zt, app), base_src=base_source(zt),
                contexts="\n".join(context_text(i, c) for i, c in enumerate(ctxs)))
            try:
                out = client.chat([{"role": "user", "content": prompt}], GEN_SCHEMA, "samples", a.effort, f"gen {app}")
            except BudgetExceeded as e:
                print(json.dumps({"stop": str(e)}))
                return
            except RuntimeError as e:
                print(json.dumps({"app": app, "error": str(e)[:300]}), file=sys.stderr)
                done[app] += n  # do not loop forever on a failing app
                continue
            rows = []
            for s in out.get("samples", [])[:n]:
                i = s.get("context_index")
                ctx = ctxs[i] if isinstance(i, int) and 0 <= i < n else ctxs[0]
                rows.append({"id": f"synth_{a.tag}_{n_out:04d}", "app": app, "model": a.model, "context": ctx, **s})
                n_out += 1
            with open(P["raw"], "a", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            done[app] += n
            print(json.dumps({"app": app, "got": len(rows), "spent_usd": round(client.spent(), 4),
                              "all_tags_usd": round(total_spent(P["usage"].parent), 4)}))


def cmd_check(a):
    if a.recipe == "v2":
        return cmd_check_v2(a)
    P = _paths(a.tag, a.no_solver)
    rng = random.Random(a.seed + 1)
    zt = zaic_tools(a.split, a.root)
    catalog = load_catalog(a.split, a.root)
    tools = catalog_tools(catalog)
    drop = set(json.loads(Path(a.drop_apps).read_text())) if a.drop_apps else set()
    examples = "\n".join(example_text(s) for s in pick_examples(fit_samples(a.root, a.fit, drop), rng))
    client = None if a.no_solver else Client(a.model, a.base_url, P["usage"], a.max_usd, a.total_usd)
    ok, rej, reasons = [], [], Counter()
    cache = {}
    for x in (load_jsonl(P["solver"]) if P["solver"].exists() else []):
        try:
            parse_calls(x["calls"])
            cache[x["id"]] = x["calls"]  # only answers that parse: a broken one is asked again
        except ValueError:
            pass
    seen_by_app: dict[str, list[str]] = {}
    for r in load_jsonl(P["raw"]):
        g = {**r}
        try:
            g["state"] = json.loads(r["state_json"])
            g["calls"] = parse_calls(r["calls"])
            if not isinstance(g["state"], dict):
                raise ValueError("state is not an object")
        except (ValueError, KeyError, TypeError) as e:
            reason, results = f"parse: {e}", []
        else:
            reason, results = check_sample(zt, g, tools, catalog)
        if reason is None:
            dup = near_duplicate(g["request"], seen_by_app.get(g["app"], []))
            if dup:
                reason = f"duplicate: {dup[:60]}"
        if reason is None and (client is not None or g["id"] in cache):
            names = [t for v in g["context"]["installed_apps"].values() for t in v["tools"]] + [ASK]
            p = g["context"].get("user_profile", {})
            prompt = SOLVE_TASK.format(
                rules=SYSTEM_RULES, examples=examples, now=g["context"]["current_time"],
                profile=f"{p.get('name')}, {p.get('city')}, nhà {p.get('home_address')}, chỗ làm {p.get('work_address')}",
                tools=tools_json(names, tools), state=json.dumps(g["state"], ensure_ascii=False), request=g["request"])
            try:
                if g["id"] in cache:  # paid for already: reuse
                    solved = parse_calls(cache[g["id"]])
                else:
                    for attempt in range(2):  # the solver sometimes leaves junk after the arguments JSON: ask once more
                        raw_calls = client.chat([{"role": "user", "content": prompt}], SOLVE_SCHEMA, "calls",
                                                a.solver_effort, f"solve {g['id']}")["calls"]
                        try:
                            solved = parse_calls(raw_calls)
                            break
                        except ValueError:
                            if attempt:
                                raise
                    with open(P["solver"], "a", encoding="utf-8") as f:
                        f.write(json.dumps({"id": g["id"], "calls": raw_calls}, ensure_ascii=False) + "\n")
                g["solver_calls"] = solved
                reason = solver_agrees(zt, g, solved, tools, catalog)
            except BudgetExceeded as e:
                print(json.dumps({"stop": str(e)}))
                break
            except (RuntimeError, ValueError, KeyError, TypeError) as e:
                reason = f"solver_error: {str(e)[:150]}"
        reasons[(reason or "ok").split(":")[0]] += 1
        row = {**g, "results": results, "reason": reason}
        (rej if reason else ok).append(row)
        if reason is None:
            seen_by_app.setdefault(g["app"], []).append(g["request"])
    write_jsonl(P["ok"], [to_train_sample(r, r["results"]) | {"_scenario": r.get("scenario"), "_category": r.get("category")}
                         for r in ok])
    write_jsonl(P["rej"], rej)
    spent = client.spent() if client else (sum(x["usd"] for x in load_jsonl(P["usage"])) if P["usage"].exists() else 0)
    rep = {"created": runinfo.now(), "tag": a.tag, "raw": len(ok) + len(rej), "accepted": len(ok), "reasons": reasons,
           "accepted_by_app": Counter(r["app"] for r in ok), "accepted_by_category": Counter(r["category"] for r in ok),
           "spent_usd": round(spent, 4), "usd_per_accepted": round(spent / len(ok), 4) if ok else None,
           "solver": not a.no_solver, "git": runinfo.git_state()}
    runinfo.write_json(P["report"], rep)
    print(json.dumps(rep, ensure_ascii=False, default=str))


def cmd_gen_v2(a):
    P = _paths(a.tag)
    rng = random.Random(a.seed)
    zt = zaic_tools(a.split, a.root)
    catalog = load_catalog(a.split, a.root)
    tools, apps_by_id = catalog_tools(catalog), {x["id"]: x for x in catalog["apps"]}
    drop = set(json.loads(Path(a.drop_apps).read_text())) if a.drop_apps else set()
    fits = fit_samples(a.root, a.fit, drop)
    refs = [r for r in history_ref_examples(fits, tools) if not (_history_apps(r[0]["history"]) & drop)]
    client = Client(a.model, a.base_url, P["usage"], a.max_usd, a.total_usd)
    done = Counter(r["app"] for r in load_jsonl(P["raw"])) if P["raw"].exists() else Counter()
    n_out = sum(done.values())
    for app in a.apps.split(","):
        if app not in apps_by_id or app not in zt.executor.APPS:
            raise SystemExit(f"app {app!r} not in the {a.split} catalog or simulator")
        while done[app] < a.per_app:
            n = min(a.batch, a.per_app - done[app])
            triples = make_specs_v2(n, app, fits, apps_by_id, drop, zt, rng)
            others = sorted({sp["other_app"] for _, sp, _ in triples if sp["other_app"]})
            names = [t["name"] for x in [app] + others for t in apps_by_id[x]["tools"]]
            src = "\n\n".join(f"App `{x}`:\n```python\n{app_source(zt, x)}\n```" for x in [app] + others)
            styles = "\n".join(f'- "{s["audio_text"]}"' for s in rng.sample(fits, 12))
            prompt = GEN_TASK_V2.format(
                n=n, app=app, name_vi=apps_by_id[app].get("name_vi", ""), desc=apps_by_id[app].get("description", ""),
                rules=SYSTEM_RULES, examples=pick_examples_v2(fits, refs, tools, rng), styles=styles,
                tools=tools_json(names, tools), ask_tool=tools_json([ASK], tools), app_src=src, base_src=base_source(zt),
                contexts="\n".join(context_text(i, c) for i, (c, _, _) in enumerate(triples)),
                specs="\n".join(spec_text(i, sp) for i, (_, sp, _) in enumerate(triples)))
            try:
                out = client.chat([{"role": "user", "content": prompt}], GEN_SCHEMA_V2, "samples", a.effort, f"gen {app}")
            except BudgetExceeded as e:
                print(json.dumps({"stop": str(e)}))
                return
            except RuntimeError as e:
                print(json.dumps({"app": app, "error": str(e)[:300]}), file=sys.stderr)
                done[app] += n
                continue
            rows = []
            for j, s in enumerate(out.get("samples", [])[:n]):
                i = s.get("context_index")
                i = i if isinstance(i, int) and 0 <= i < n else j
                ctx, spec, dh = triples[i]
                rows.append({"id": f"synth_{a.tag}_{n_out:04d}", "app": app, "model": a.model, "recipe": "v2",
                             "context": ctx, "spec": spec, "distract_history": dh, **s})
                n_out += 1
            with open(P["raw"], "a", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            done[app] += n
            print(json.dumps({"app": app, "got": len(rows), "spent_usd": round(client.spent(), 4),
                              "all_tags_usd": round(total_spent(P["usage"].parent), 4)}))


def cmd_check_v2(a):
    P = _paths(a.tag, a.no_solver)
    rng = random.Random(a.seed + 1)
    zt = zaic_tools(a.split, a.root)
    catalog = load_catalog(a.split, a.root)
    tools = catalog_tools(catalog)
    drop = set(json.loads(Path(a.drop_apps).read_text())) if a.drop_apps else set()
    fits = fit_samples(a.root, a.fit, drop)
    refs = [r for r in history_ref_examples(fits, tools) if not (_history_apps(r[0]["history"]) & drop)]
    examples = pick_examples_v2(fits, refs, tools, rng)
    client = None if a.no_solver else Client(a.model, a.base_url, P["usage"], a.max_usd, a.total_usd)
    cache = {}
    for x in (load_jsonl(P["solver"]) if P["solver"].exists() else []):
        try:
            parse_calls(x["calls"])
            cache[x["id"]] = x["calls"]
        except ValueError:
            pass
    ok, rej, reasons, dropped = [], [], Counter(), 0
    seen_by_app: dict[str, list[str]] = {}
    for r in load_jsonl(P["raw"]):
        g = {**r}
        turn_results, results, history = [], [], []
        try:
            g["state"] = json.loads(r["state_json"])
            if not isinstance(g["state"], dict):
                raise ValueError("state is not an object")
            g["calls"] = parse_calls(r["calls"])
            g["turns"] = [{"request": t["request"], "reply": t.get("reply", ""), "calls": parse_calls(t["calls"])}
                          for t in r.get("history_turns") or []]
        except (ValueError, KeyError, TypeError) as e:
            reason = f"parse: {e}"
        else:
            reason, turn_results, results = check_sample_v2(zt, g, tools, catalog)
            dh = r.get("distract_history") or []
            if dh and _strings([h.get("tool_results") for h in dh], set()) & state_ids(g["state"]):
                dh, dropped = [], dropped + 1  # the unrelated conversation returned IDs this state also uses
            history = dh + turns_as_history(g["turns"], turn_results)
        if reason is None:
            dup = near_duplicate(g["request"], seen_by_app.get(g["app"], []))
            if dup:
                reason = f"duplicate: {dup[:60]}"
        if reason is None and (client is not None or g["id"] in cache):
            used = {c["name"].split(".", 1)[0] for c in g["calls"]} | {g["app"]} | _history_apps(history)
            if g["spec"].get("other_app"):
                used.add(g["spec"]["other_app"])
            names = [t for a_, v in g["context"]["installed_apps"].items() if a_ in used for t in v["tools"]] + [ASK]
            _, _, before, _ = simulate_v2(zt, g["context"], g["state"], [t["calls"] for t in g["turns"]], [], catalog)
            p = g["context"].get("user_profile", {})
            prompt = SOLVE_TASK_V2.format(
                rules=SYSTEM_RULES, examples=examples, now=g["context"]["current_time"],
                profile=f"{p.get('name')}, {p.get('city')}, nhà {p.get('home_address')}, chỗ làm {p.get('work_address')}",
                tools=tools_json(names, tools), state=json.dumps(before, ensure_ascii=False),
                history=history_text(history), request=g["request"])
            try:
                if g["id"] in cache:
                    solved = parse_calls(cache[g["id"]])
                else:
                    for attempt in range(2):
                        raw_calls = client.chat([{"role": "user", "content": prompt}], SOLVE_SCHEMA, "calls",
                                                a.solver_effort, f"solve {g['id']}")["calls"]
                        try:
                            solved = parse_calls(raw_calls)
                            break
                        except ValueError:
                            if attempt:
                                raise
                    with open(P["solver"], "a", encoding="utf-8") as f:
                        f.write(json.dumps({"id": g["id"], "calls": raw_calls}, ensure_ascii=False) + "\n")
                g["solver_calls"] = solved
                reason = solver_agrees_v2(zt, g, solved, tools, catalog)
            except BudgetExceeded as e:
                print(json.dumps({"stop": str(e)}))
                break
            except (RuntimeError, ValueError, KeyError, TypeError) as e:
                reason = f"solver_error: {str(e)[:150]}"
        reasons[(reason or "ok").split(":")[0]] += 1
        row = {**g, "results": results, "history": history, "reason": reason}
        (rej if reason else ok).append(row)
        if reason is None:
            seen_by_app.setdefault(g["app"], []).append(g["request"])
    write_jsonl(P["ok"], [to_train_sample(r, r["results"], r["history"])
                         | {"_scenario": r.get("scenario"), "_category": r.get("category"), "_spec": r.get("spec")}
                         for r in ok])
    write_jsonl(P["rej"], rej)
    spent = client.spent() if client else (sum(x["usd"] for x in load_jsonl(P["usage"])) if P["usage"].exists() else 0)
    rep = {"created": runinfo.now(), "tag": a.tag, "recipe": "v2", "raw": len(ok) + len(rej), "accepted": len(ok),
           "reasons": reasons, "accepted_by_app": Counter(r["app"] for r in ok),
           "accepted_by_category": Counter(r["category"] for r in ok),
           "accepted_with_history": sum(1 for r in ok if r["history"]),
           "accepted_history_ref": sum(1 for r in ok if r["spec"].get("history") == "ref"),
           "accepted_two_apps": sum(1 for r in ok if r["spec"].get("other_app")),
           "distractor_history_dropped": dropped,
           "spent_usd": round(spent, 4), "usd_per_accepted": round(spent / len(ok), 4) if ok else None,
           "solver": not a.no_solver, "git": runinfo.git_state()}
    runinfo.write_json(P["report"], rep)
    print(json.dumps(rep, ensure_ascii=False, default=str))


def shape_stats(samples: list[dict], tools: dict) -> dict:
    """Shape of samples (real or synthetic), the numbers v2 matches: history, ID reuse from history, apps per
    request, categories, calls per sample, optional parameters filled per write call."""
    from .sft import used_apps
    n = len(samples)
    c = Counter()
    for s in samples:
        calls, res = s["label"]["tool_calls"], s["label"].get("tool_results") or []
        hs = _strings([h.get("tool_results") for h in s["history"] if h["role"] == "assistant"], set())
        c["history"] += bool(s["history"])
        own, reuse = set(), False
        for i, x in enumerate(calls):
            props = tools.get(x["name"], {}).get("parameters", {}).get("properties", {})
            reuse |= any(props.get(k, {}).get("x-ref") and isinstance(v, str) and v in hs and v not in own
                         for k, v in x["arguments"].items())
            if i < len(res):
                _strings(res[i], own)
        c["history_id_reuse"] += reuse
        c["two_apps"] += len(used_apps(calls)) > 1
        c[f"calls_{min(len(calls), 5)}"] += 1
        if not calls:
            c["cat_none"] += 1
        elif calls[-1]["name"] == ASK:
            c["cat_ask"] += 1
        elif all(tools.get(x["name"], {}).get("kind") == "read" for x in calls):
            c["cat_lookup"] += 1
        else:
            c["cat_execute"] += 1
        for x in calls:
            spec = tools.get(x["name"], {})
            if x["name"] == ASK or spec.get("kind") == "read":
                continue
            props = spec.get("parameters", {}).get("properties", {})
            req = set(required(spec))
            c["writes"] += 1
            c["optional_filled"] += sum(1 for k in props if k not in req and not props[k].get("x-ref") and k in x["arguments"])
    out = {k: round(100 * v / n, 1) for k, v in sorted(c.items()) if k not in ("writes", "optional_filled")}
    out["optional_filled_per_write"] = round(c["optional_filled"] / max(c["writes"], 1), 2)
    out["n"] = n
    return out


def cmd_stats(a):
    tools = catalog_tools(load_catalog(a.split, a.root))
    drop = set(json.loads(Path(a.drop_apps).read_text())) if a.drop_apps else set()
    rows = {"real": shape_stats(fit_samples(a.root, a.fit, drop), tools)}
    for tag in a.tag.split(","):
        rows[tag] = shape_stats(load_jsonl(_paths(tag)["ok"]), tools)
    keys = sorted({k for r in rows.values() for k in r})
    print("| | " + " | ".join(rows) + " |\n|---|" + "---:|" * len(rows))
    for k in keys:
        print(f"| {k} | " + " | ".join(str(r.get(k, 0)) for r in rows.values()) + " |")


def cmd_sft(a):
    from .sft import build_all
    P = _paths(a.tag)
    catalog = load_catalog(a.split, a.root)
    tools, apps = catalog_tools(catalog), {x["id"]: x for x in catalog["apps"]}
    pool = {x["id"]: x for x in load_catalog("public_test", a.root)["apps"]} | {x["id"]: x for x in load_catalog("train", a.root)["apps"]}
    samples = load_jsonl(P["ok"])
    rows = build_all(samples, tools, apps, pool, rename=a.rename, p_remove=a.p_remove, p_distract=a.p_distract,
                     p_lower=a.p_lower, seed=a.seed)
    out = Path(a.out)
    runinfo.refuse_existing(out, overwrite=a.overwrite)
    write_jsonl(out, rows)
    runinfo.write_json(out.with_name(out.name + ".manifest.json"), {
        "kind": "sft-synth", "created": runinfo.now(), "samples": str(P["ok"]), "samples_sha256": runinfo.sha256_file(P["ok"]),
        "rows": len(rows), "out_sha256": runinfo.sha256_file(out), "args": {k: v for k, v in vars(a).items() if k != "func"},
        "code_sha256": runinfo.code_digest(("data.py", "prompt.py", "sft.py", "synth.py")), "git": runinfo.git_state()})
    print(json.dumps({"samples": len(samples), "rows": len(rows), "out": str(out)}))


def cmd_show(a):
    P = _paths(a.tag)
    for title, path in (("ACCEPTED", P["ok"]), ("REJECTED", P["rej"])):
        if not path.exists():
            continue
        print(f"=== {title}")
        for r in load_jsonl(path):
            calls = r["label"]["tool_calls"] if "label" in r else r.get("calls")
            print(f"\n[{r['id']}] {r.get('_app') or r.get('app')} / {r.get('_category') or r.get('category')}"
                  + (f"  -> {r['reason']}" if r.get("reason") else ""))
            spec = r.get("_spec") or r.get("spec")
            if spec:
                print(f"  shape: {spec}")
            for t in r.get("history_turns") or []:
                print(f"  lượt trước: {t.get('request')} -> {[c.get('name') for c in t.get('calls') or []]} / {t.get('reply')}")
            hist = r.get("history") or []
            if hist and "label" in r:
                print(f"  history: {sum(1 for h in hist if h['role'] == 'user')} user turns, last: "
                      f"{next((h.get('audio_text') for h in reversed(hist) if h['role'] == 'user'), '')}")
            print(f"  nói: {r.get('audio_text') or r.get('request')}")
            print(f"  ({r.get('_scenario') or r.get('scenario')})")
            for c in calls or []:
                print("   ", json.dumps(c, ensure_ascii=False)[:220])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, llm=True):
        p.add_argument("--tag", required=True)
        p.add_argument("--root", default=str(DEFAULT_ROOT))
        p.add_argument("--split", default="train", help="whose catalog and simulator: train (held-out apps) or public_test")
        p.add_argument("--fit", default="splits/fit_lao.txt", help="train ids for context templates and examples")
        p.add_argument("--drop-apps", default="splits/heldout_apps.json", help="apps never shown in examples or as extra installed apps")
        p.add_argument("--seed", type=int, default=0)
        if llm:
            p.add_argument("--model", default=DEFAULT_MODEL)
            p.add_argument("--base-url", default=DEFAULT_BASE_URL)
            p.add_argument("--effort", default="medium", choices=["minimal", "low", "medium", "high", "xhigh"])
            p.add_argument("--max-usd", type=float, help="hard cap on the tag's usage ledger (needed for any API call)")
            p.add_argument("--total-usd", type=float, default=30.0,
                           help="hard cap on all tags together (Anh's limit; raise only after asking him)")

    p = sub.add_parser("gen")
    common(p)
    p.add_argument("--recipe", default="v1", choices=["v1", "v2"], help="v2: history, two apps, no-call requests (06/11)")
    p.add_argument("--apps", required=True, help="comma-separated app ids")
    p.add_argument("--per-app", type=int, default=4)
    p.add_argument("--batch", type=int, default=4, help="samples per LLM call")
    p.add_argument("--ask-frac", type=float, default=0.2)
    p.add_argument("--lookup-frac", type=float, default=0.1, help="read-only requests (8%% of fit_lao)")
    p.set_defaults(func=cmd_gen)

    p = sub.add_parser("check")
    common(p)
    p.add_argument("--recipe", default="v1", choices=["v1", "v2"])
    p.add_argument("--no-solver", action="store_true", help="simulator checks only (no API call)")
    p.add_argument("--solver-effort", default="low", choices=["minimal", "low", "medium", "high", "xhigh"],
                   help="reasoning effort of the re-derivation (its reasoning tokens were half the t20 cost)")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("sft")
    common(p, llm=False)
    p.add_argument("--out", required=True)
    p.add_argument("--rename", type=int, default=2)
    p.add_argument("--p-remove", type=float, default=0.3)
    p.add_argument("--p-distract", type=float, default=0.5)
    p.add_argument("--p-lower", type=float, default=0.3)
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_sft)

    p = sub.add_parser("show")
    common(p, llm=False)
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("stats", help="shape of accepted samples (comma-separated tags) next to the real fit samples")
    common(p, llm=False)
    p.set_defaults(func=cmd_stats)

    a = ap.parse_args()
    if a.cmd in ("gen", "check") and not getattr(a, "no_solver", False) and a.max_usd is None:
        ap.error("--max-usd is required for commands that call the API")
    a.func(a)


if __name__ == "__main__":
    main()
