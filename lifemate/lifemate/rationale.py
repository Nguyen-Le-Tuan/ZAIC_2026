"""D2: short rationales ("thoughts") for train samples, written by a Meta Model API teacher that sees the gold calls.

lifemate.sft --thoughts puts them in front of each tool-call step as <think>...</think>, so the agent learns to think
briefly before it acts (plan in docs/SYNTH_DATA_PLAN_2026-11-08.md, docs/RANKING_FINAL_WEEK_2026-11-08.md). The teacher
is used only while building training data; it never runs at inference.

  source ~/.zac_meta_env                                          # export META_API_KEY=... (standard tier)
  python -m lifemate.rationale --ids gen/d2_probe20.txt --tag d2t20 --max-usd 1
  python -m lifemate.rationale --tag d2all --max-usd 20 --workers 8   # every train sample

Output gen/rationale_<tag>.jsonl, one line per sample: {"id", "n_steps", "thoughts": [one per gold step], "final",
"model"}; every API call is appended to gen/rationale_<tag>_usage.jsonl. A call is refused once the tag reached
--max-usd or all ledgers in gen/ together reached --total-usd (default 90: the leader's Meta budget, 08/11/2026).
Resumable: ids already in the output file are skipped. Reads only <split>.jsonl and the catalog, never
<split>_environment/. Prompts carry train samples, so contributor-tier models (which may train on prompts) are refused.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from . import runinfo
from .data import DEFAULT_ROOT, catalog_tools, load_catalog, load_jsonl, load_split
from .prompt import WEEKDAYS, compact_result, render_tool
from .sft import group_steps

GEN_DIR = Path("gen")
# USD per million tokens (input, output); reasoning tokens are billed as output. Meta Model API, standard tier.
PRICES = {"muse-spark-1.3": (1.25, 4.25), "muse-spark-1.2": (1.25, 4.25), "muse-spark-1.1": (1.25, 4.25),
          "muse-wonder-1.0": (4.0, 20.0)}
DEFAULT_BASE_URL = "https://api.meta.ai/v1"
DEFAULT_MODEL = "muse-spark-1.3"
MAX_WORDS = 45  # per thought; the system prompt asks for <= 30
BANNED = re.compile(r"đáp án|nhãn|\bgold\b|\blabel\b|bước \d|step \d", re.I)


class BudgetExceeded(RuntimeError):
    pass


def ledger_usd(path: Path) -> float:
    return sum(r["usd"] for r in load_jsonl(path)) if path.exists() else 0.0


def total_spent(gen_dir: Path = GEN_DIR) -> float:
    """Every usage ledger in gen/ together (rationale and synth runs)."""
    return sum(ledger_usd(p) for p in sorted(gen_dir.glob("*_usage.jsonl")))


class Client:
    """OpenAI-compatible Chat Completions over urllib with a budget cap. Thread-safe: the ledger is written under a lock
    and the caps are checked before every call (a few calls already in flight may finish after a cap is reached)."""

    def __init__(self, model: str, base_url: str, ledger: Path, max_usd: float, total_usd: float, timeout: float = 300):
        if "contributor" in model:
            raise SystemExit("contributor-tier models may train on prompts; prompts here carry competition files")
        key = os.environ.get("MODEL_API_KEY") or os.environ.get("META_API_KEY")
        if not key:
            raise SystemExit("no API key: put `export META_API_KEY=...` in ~/.zac_meta_env and `source` it")
        if model not in PRICES:
            raise SystemExit(f"no price for {model!r}; add it to PRICES first (the budget cap needs it)")
        self.key, self.model, self.url = key, model, base_url.rstrip("/") + "/chat/completions"
        self.ledger, self.max_usd, self.total_usd, self.timeout = ledger, max_usd, total_usd, timeout
        self.price, self.lock = PRICES[model], threading.Lock()
        self._spent = ledger_usd(ledger)
        self._others = total_spent(ledger.parent) - self._spent

    def spent(self) -> float:
        return self._spent

    def chat(self, messages: list[dict], schema: dict, name: str, effort: str, purpose: str) -> dict:
        with self.lock:
            if self._spent >= self.max_usd:
                raise BudgetExceeded(f"tag spent {self._spent:.3f} USD >= cap {self.max_usd}")
            if self._others + self._spent >= self.total_usd:
                raise BudgetExceeded(f"all ledgers {self._others + self._spent:.3f} USD >= total cap {self.total_usd}")
        body = {"model": self.model, "messages": messages, "reasoning_effort": effort,
                "response_format": {"type": "json_schema", "json_schema": {"name": name, "schema": schema, "strict": True}}}
        req = urllib.request.Request(self.url, json.dumps(body).encode(), {
            "Content-Type": "application/json", "Authorization": f"Bearer {self.key}"})
        delay, t0 = 1.0, time.time()
        for attempt in range(6):
            t0 = time.time()
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    resp = json.loads(r.read())
                break
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="replace")[:500]
                if e.code in (429, 500, 502, 503, 504) and attempt < 5:
                    time.sleep(float(e.headers.get("Retry-After") or delay) + random.random() * 0.5)
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
        with self.lock:
            self._spent += usd
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


# ---------------------------------------------------------------- what the teacher sees

SYSTEM = """Bạn viết "suy nghĩ ngắn" để dạy một trợ lý giọng nói tiếng Việt nhỏ cách gọi tool. Mỗi mẫu cho bạn: ngữ cảnh người dùng, các tool liên quan, lịch sử hội thoại, câu nói cuối, và các bước gọi tool ĐÚNG mà trợ lý phải làm (đã chạy thật, có kết quả). Nhiệm vụ: viết suy nghĩ mà trợ lý nên có NGAY TRƯỚC mỗi bước, để từ đó tự đi tới đúng bước ấy.

Luật:
1. Mỗi bước một suy nghĩ, theo đúng thứ tự. Thêm "final": suy nghĩ trước khi trả lời xong (vì sao dừng, hoặc vì sao không gọi tool nào).
2. Suy nghĩ trước bước k chỉ được dùng thông tin đã có lúc đó: câu nói, ngữ cảnh, lịch sử, kết quả của các bước trước. Không nhắc tới kết quả của chính bước k hay các bước sau.
3. Tiếng Việt, kiểu ghi chú gạch đầu dòng, tối đa 30 từ. Nêu điều quyết định: người dùng muốn gì; cần ID hay giá trị nào và lấy từ đâu (kết quả tool nào, lượt nào trong lịch sử); ngày giờ tính ra sao; vì sao phải hỏi lại (thiếu tham số nào, hay có nhiều đối tượng khớp); vì sao không gọi tool (app chưa cài, người dùng huỷ hoặc đổi ý, chỉ trò chuyện, thông tin đã có).
4. Gọi tool bằng tên đầy đủ dạng app.tool (ví dụ smart_home.get_status). Không chép lại JSON. Không dùng các từ "đáp án", "nhãn", "bước 1".
5. Nếu bước đọc dùng {} (không lọc) thì đó là chủ ý: lấy toàn bộ danh sách rồi tự chọn. Nếu một bước gọi nhiều tool cùng lúc thì một suy nghĩ cho cả bước.

Ví dụ (minh hoạ, không phải dữ liệu thật):
- Câu: "tắt đèn phòng ngủ giùm" | Bước 1: smart_home.get_status {} | Bước 2: smart_home.light_set {device_id: "d_03", power: "off"}
  -> thoughts: ["Muốn tắt đèn phòng ngủ; cần device_id, chưa có -> đọc smart_home.get_status lấy danh sách thiết bị.", "Đèn phòng ngủ là d_03 trong kết quả -> smart_home.light_set tắt."], final: "Đã tắt đèn, xong."
- Câu: "gọi cho Minh" | Bước 1: contacts.search {query: "Minh"} | Bước 2: sys.ask_missing_info {tool_name: "phone.call", params: ["contact_id"]}
  -> thoughts: ["Cần contact_id của Minh -> contacts.search theo tên.", "Có hai người tên Minh, câu không nói rõ ai -> hỏi lại contact_id cho phone.call."], final: "Đang chờ người dùng chọn."
- Câu: "à thôi khỏi đặt xe nha" | Không gọi tool
  -> thoughts: [], final: "Người dùng huỷ yêu cầu đặt xe -> không gọi tool."
"""

SCHEMA = {"type": "object", "properties": {"thoughts": {"type": "array", "items": {"type": "string"}},
                                           "final": {"type": "string"}},
          "required": ["thoughts", "final"], "additionalProperties": False}


def _call_text(c: dict) -> str:
    return f"{c['name']} {json.dumps(c.get('arguments') or {}, ensure_ascii=False)}"


def kind_of(calls: list[dict]) -> str:
    if not calls:
        return "out_of_scope (không gọi tool)"
    return "ask_missing (hỏi lại)" if any(c["name"] == "sys.ask_missing_info" for c in calls) else "execute (thực hiện)"


def brief(s: dict, tools: dict, apps: dict) -> tuple[str, int]:
    """(text shown to the teacher, number of gold steps). Steps are lifemate.sft.group_steps of the gold calls, i.e.
    exactly the assistant turns the SFT data trains on."""
    ctx = s["context"]
    now = datetime.fromisoformat(ctx["current_time"])
    calls, results = s["label"]["tool_calls"], s["label"]["tool_results"]
    steps = group_steps(calls, results, tools) if calls else []
    prof = "; ".join(f"{k}: {v}" for k, v in (ctx.get("user_profile") or {}).items())
    installed = ctx["installed_apps"]
    lines = ["# Ngữ cảnh", f"Bây giờ: {WEEKDAYS[now.weekday()]} {ctx['current_time']}", f"Người dùng: {prof}",
             "App đã cài: " + ", ".join(f"{a} ({apps.get(a, {}).get('name_vi', a)})" for a in installed)]
    used = [c["name"] for c in calls]
    for h in s.get("history", []):
        used += [c["name"] for c in (h.get("tool_calls") or [])]
    names = [n for n in dict.fromkeys(used) if n in tools]
    for a in dict.fromkeys(n.split(".")[0] for n in names):  # siblings: what else the same apps could have done
        names += [t for t in installed.get(a, {}).get("tools", []) if t in tools and t not in names][:4]
    lines += ["", "# Tool liên quan"] + [render_tool(tools[n]) for n in names]
    if s.get("history"):
        lines += ["", "# Lịch sử (rút gọn)"]
        for h in s["history"]:
            if h["role"] == "user":
                lines.append(f"user: {h.get('audio_text', '')}")
                continue
            for c, r in zip(h.get("tool_calls") or [], h.get("tool_results") or [{}] * len(h.get("tool_calls") or [])):
                lines.append(f"assistant gọi: {_call_text(c)} -> {compact_result(r, 300)}")
            if h.get("text"):
                lines.append(f"assistant: {h['text']}")
    lines += ["", "# Câu nói cuối của người dùng", s["audio_text"], "", f"# Loại: {kind_of(calls)}",
              "# Các bước đúng (một bước có thể gồm nhiều lời gọi chạy cùng lúc)"]
    if not steps:
        lines.append("Không gọi tool nào.")
    for k, st in enumerate(steps, 1):
        parts = [f"{_call_text(calls[i])} -> {compact_result(results[i], 400)}" for i in st]
        lines.append(f"Bước {k}: " + " || ".join(parts))
    lines.append(f"\nTrả về JSON: \"thoughts\" gồm đúng {len(steps)} chuỗi (một chuỗi mỗi bước), và \"final\".")
    return "\n".join(lines), len(steps)


def check(out: dict, n_steps: int) -> str | None:
    """None when usable, else why not."""
    th, fin = out.get("thoughts"), out.get("final")
    if not isinstance(th, list) or len(th) != n_steps:
        return f"need {n_steps} thoughts, got {len(th) if isinstance(th, list) else th!r}"
    for t in th + [fin]:
        if not isinstance(t, str) or not t.strip():
            return "empty thought"
        if len(t.split()) > MAX_WORDS:
            return f"too long ({len(t.split())} words)"
        if BANNED.search(t):
            return f"banned wording: {BANNED.search(t).group(0)!r}"
    return None


def one(client: Client, s: dict, tools: dict, apps: dict, effort: str) -> dict:
    text, n = brief(s, tools, apps)
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}]
    why = None
    for attempt in range(2):
        out = client.chat(msgs, SCHEMA, "thoughts", effort, purpose=f"{s['id']}#{attempt}")
        why = check(out, n)
        if why is None:
            return {"id": s["id"], "n_steps": n, "thoughts": [t.strip() for t in out["thoughts"]],
                    "final": out["final"].strip(), "model": client.model}
        msgs += [{"role": "assistant", "content": json.dumps(out, ensure_ascii=False)},
                 {"role": "user", "content": f"Chưa đạt: {why}. Viết lại theo đúng luật."}]
    return {"id": s["id"], "n_steps": n, "error": why, "model": client.model}


def main():
    ap = argparse.ArgumentParser(description="D2 rationales for train samples (Meta Model API teacher)")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--ids", help="file with sample ids (default: every train sample)")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--effort", default="low", help="reasoning_effort sent to the API")
    ap.add_argument("--max-usd", type=float, required=True, help="cap for this tag")
    ap.add_argument("--total-usd", type=float, default=90.0, help="cap for all ledgers in gen/ together")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true", help="print the first brief and size estimates, call nothing")
    a = ap.parse_args()

    cat = load_catalog("train", a.root)
    tools, apps = catalog_tools(cat), {x["id"]: x for x in cat["apps"]}
    samples = load_split("train", a.root)
    if a.ids:
        keep = set(Path(a.ids).read_text().split())
        samples = [s for s in samples if s["id"] in keep]
    out_path, ledger = GEN_DIR / f"rationale_{a.tag}.jsonl", GEN_DIR / f"rationale_{a.tag}_usage.jsonl"
    done = {r["id"] for r in load_jsonl(out_path) if "error" not in r} if out_path.exists() else set()
    todo = [s for s in samples if s["id"] not in done]
    if a.dry_run:
        chars = [len(SYSTEM) + len(brief(s, tools, apps)[0]) for s in todo]
        print(brief(todo[0], tools, apps)[0] if todo else "(nothing to do)")
        print(json.dumps({"todo": len(todo), "done": len(done), "mean_prompt_chars": round(sum(chars) / max(len(chars), 1)),
                          "max_prompt_chars": max(chars, default=0)}))
        return
    client = Client(a.model, a.base_url, ledger, a.max_usd, a.total_usd)
    print(json.dumps({"todo": len(todo), "done": len(done), "spent_tag": round(client.spent(), 4),
                      "spent_all": round(total_spent(GEN_DIR), 4)}), flush=True)
    lock, n_ok, n_err = threading.Lock(), 0, 0
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(a.workers) as pool, open(out_path, "a", encoding="utf-8") as f:
        futs = {pool.submit(one, client, s, tools, apps, a.effort): s["id"] for s in todo}
        for fut in as_completed(futs):
            try:
                row = fut.result()
            except BudgetExceeded as e:
                print(f"stop: {e}", flush=True)
                for other in futs:
                    other.cancel()
                break
            except RuntimeError as e:
                row = {"id": futs[fut], "error": str(e)[:300]}
            with lock:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                f.flush()
                n_ok += "error" not in row
                n_err += "error" in row
                if (n_ok + n_err) % 25 == 0:
                    print(json.dumps({"ok": n_ok, "error": n_err, "spent_tag": round(client.spent(), 4)}), flush=True)
    print(json.dumps({"ok": n_ok, "error": n_err, "spent_tag": round(client.spent(), 4),
                      "spent_all": round(total_spent(GEN_DIR), 4), "out": str(out_path)}), flush=True)


if __name__ == "__main__":
    main()
