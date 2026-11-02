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
Every API call is logged in gen/synth_<tag>_usage.jsonl; a call is refused once the tag reached --max-usd or all
tags together reached --total-usd (default 10: Anh's limit for all synthetic data, 02/11; more only after asking).

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
  solver       an independent LLM call, given the request, the context and the state (as the results the tools would
               return), predicts the calls; the sample is kept only if the predicted calls reach the same final state
               and make the same write/ask calls by name
"""
from __future__ import annotations

import argparse
import copy
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
    refused once the tag reached max_usd, or once all tags together reached total_usd (Anh's limit: about 10 USD for
    all synthetic data, more only after asking him)."""

    def __init__(self, model: str, base_url: str, ledger: Path, max_usd: float, total_usd: float = 10.0,
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
    calls = "\n".join(json.dumps(c, ensure_ascii=False) for c in s["label"]["tool_calls"])
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
2. `request`: câu người dùng NÓI, tự nhiên như giọng nói thật, 8-40 từ. Người dùng không bao giờ đọc ID. Ngày giờ nói kiểu tương đối ("mai", "thứ sáu này", "chín giờ tối"). Các câu trong lượt này phải KHÁC NHAU về cách nói: đổi cách mở đầu (có câu bắt đầu bằng "ừ,", "ờ", "thế", "nếu", hay vào thẳng động từ), đổi từ nhờ vả ("giúp", "giùm", "cho", "với", hoặc không dùng), có câu dài nhiều ý, có câu tự sửa giữa chừng ("à không..."), có câu điều kiện ("nếu ... thì ..."), có giọng miền. Không câu nào được lặp khuôn của câu khác. Bắt chước phân bố cách nói của các câu thật dưới đây (chỉ học cách nói, không chép nội dung).
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


# ---------------------------------------------------------------- sft

def to_train_sample(g: dict, results: list) -> dict:
    return {"id": g["id"], "audio": None, "audio_text": g["request"], "context": g["context"], "history": [],
            "label": {"tool_calls": g["calls"], "tool_results": results}, "_src": SRC, "_app": g["app"]}


# ---------------------------------------------------------------- commands

def _paths(tag: str) -> dict:
    return {"raw": GEN_DIR / f"synth_{tag}_raw.jsonl", "ok": GEN_DIR / f"synth_{tag}.jsonl",
            "rej": GEN_DIR / f"synth_{tag}_rejected.jsonl", "usage": GEN_DIR / f"synth_{tag}_usage.jsonl",
            "report": GEN_DIR / f"synth_{tag}.report.json"}


def cmd_gen(a):
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
    P = _paths(a.tag)
    rng = random.Random(a.seed + 1)
    zt = zaic_tools(a.split, a.root)
    catalog = load_catalog(a.split, a.root)
    tools = catalog_tools(catalog)
    drop = set(json.loads(Path(a.drop_apps).read_text())) if a.drop_apps else set()
    examples = "\n".join(example_text(s) for s in pick_examples(fit_samples(a.root, a.fit, drop), rng))
    client = None if a.no_solver else Client(a.model, a.base_url, P["usage"], a.max_usd, a.total_usd)
    ok, rej, reasons = [], [], Counter()
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
        if reason is None and client is not None:
            names = [t for v in g["context"]["installed_apps"].values() for t in v["tools"]] + [ASK]
            p = g["context"].get("user_profile", {})
            prompt = SOLVE_TASK.format(
                rules=SYSTEM_RULES, examples=examples, now=g["context"]["current_time"],
                profile=f"{p.get('name')}, {p.get('city')}, nhà {p.get('home_address')}, chỗ làm {p.get('work_address')}",
                tools=tools_json(names, tools), state=json.dumps(g["state"], ensure_ascii=False), request=g["request"])
            try:
                solved = parse_calls(client.chat([{"role": "user", "content": prompt}], SOLVE_SCHEMA, "calls", a.solver_effort,
                                                 f"solve {g['id']}")["calls"])
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
            p.add_argument("--total-usd", type=float, default=10.0,
                           help="hard cap on all tags together (Anh's limit; raise only after asking him)")

    p = sub.add_parser("gen")
    common(p)
    p.add_argument("--apps", required=True, help="comma-separated app ids")
    p.add_argument("--per-app", type=int, default=4)
    p.add_argument("--batch", type=int, default=4, help="samples per LLM call")
    p.add_argument("--ask-frac", type=float, default=0.2)
    p.add_argument("--lookup-frac", type=float, default=0.1, help="read-only requests (8%% of fit_lao)")
    p.set_defaults(func=cmd_gen)

    p = sub.add_parser("check")
    common(p)
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

    a = ap.parse_args()
    if a.cmd in ("gen", "check") and not getattr(a, "no_solver", False) and a.max_usd is None:
        ap.error("--max-usd is required for commands that call the API")
    a.func(a)


if __name__ == "__main__":
    main()
