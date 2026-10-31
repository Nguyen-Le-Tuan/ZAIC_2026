"""Prompt building in Qwen3 ChatML with <tool_call>/<tool_response> tags (the format Qwen3 was trained on),
but with a compact one-line-per-tool schema instead of full JSON to fit the 16K context.

Messages are plain dicts {"role": "system"|"user"|"assistant", "content": str}; tool results go back as a user
message holding <tool_response> blocks, exactly as Qwen3's chat template renders the "tool" role.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta

WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
RELATIVE = {-2: "hôm kia", -1: "hôm qua", 0: "hôm nay", 1: "ngày mai", 2: "ngày kia"}

SYSTEM_RULES = """Bạn là trợ lý giọng nói LifeMate. Nhiệm vụ: biến yêu cầu cuối cùng của người dùng (tiếng Việt, đã chuyển từ giọng nói nên có thể sai chính tả) thành các lời gọi tool.

Quy tắc:
1. Chỉ gọi tool có trong danh sách. Không bịa ID: lấy ID từ kết quả tool hoặc từ lịch sử hội thoại.
2. Thông tin đã có trong lịch sử thì dùng lại, không gọi tool đọc lại khi không cần.
3. Thiếu thông tin bắt buộc mà không suy ra được, hoặc có nhiều đối tượng khớp mà không biết chọn cái nào: gọi sys.ask_missing_info với tool_name và params còn thiếu, rồi dừng.
4. Không gọi tool nào khi: không app nào đã cài làm được, người dùng hủy hoặc đổi ý, hoặc chỉ trò chuyện.
5. Thời gian: ISO-8601 đầy đủ giây và múi giờ, ví dụ 2026-11-11T05:30:00+07:00. Số tiền: số nguyên VND, ví dụ 200000.
6. Mỗi lượt có thể gọi một hoặc nhiều tool. Làm xong thì trả lời một câu ngắn, không kèm tool_call."""

TOOL_FORMAT = """Gọi tool bằng JSON trong thẻ <tool_call></tool_call>, mỗi lời gọi một thẻ:
<tool_call>
{"name": "<tên tool>", "arguments": {<tham số>}}
</tool_call>"""

# Descriptions repeated across many tools; covered once by rule 5.
_GENERIC_DESC_PREFIXES = ("ISO-8601", "Số nguyên, không dấu")


def _type_str(spec: dict) -> str:
    t = spec.get("type", "any")
    if spec.get("format") == "date-time":
        return "datetime"
    if t == "array":
        items = spec.get("items", {})
        if items.get("type") == "object":
            return "[{" + ", ".join(_param_str(k, v, k in items.get("required", [])) for k, v in items.get("properties", {}).items()) + "}]"
        return f"[{_type_str(items)}]"
    return {"string": "str", "integer": "int", "number": "num", "boolean": "bool"}.get(t, t)


def _param_str(name: str, spec: dict, required: bool) -> str:
    s = f"{name}{'*' if required else ''}: "
    s += "|".join(map(str, spec["enum"])) if "enum" in spec else _type_str(spec)
    if "exclusiveMinimum" in spec:
        s += f" >{spec['exclusiveMinimum']}"
    if "minimum" in spec:
        s += f" >={spec['minimum']}"
    if "maximum" in spec:
        s += f" <={spec['maximum']}"
    desc = spec.get("description", "")
    if desc and not desc.startswith(_GENERIC_DESC_PREFIXES):
        s += f" ({desc})"
    return s


def render_tool(tool: dict) -> str:
    params = tool.get("parameters", {})
    req = set(params.get("required", []))
    args = "; ".join(_param_str(k, v, k in req) for k, v in params.get("properties", {}).items())
    line = f"- {tool['name']}({args}) — {tool.get('description', '')}"
    if params.get("x-one-of"):
        line += " | cần một trong: " + " hoặc ".join("[" + ", ".join(g) + "]" for g in params["x-one-of"])
    return line


def render_tools(item: dict, tools_by_name: dict, apps_by_id: dict) -> str:
    """Installed apps of the sample (+ sys), grouped by app, in the sample's own order."""
    blocks = []
    for app, a in item["context"]["installed_apps"].items():
        info = apps_by_id.get(app, {})
        head = f"## {app}" + (f" — {info['name_vi']}: {info.get('description', '')}" if info else "")
        lines = [render_tool(tools_by_name[t]) for t in a["tools"] if t in tools_by_name]
        blocks.append("\n".join([head, *lines]))
    if "sys.ask_missing_info" in tools_by_name:
        blocks.append("## sys\n" + render_tool(tools_by_name["sys.ask_missing_info"]))
    return "\n\n".join(blocks)


def date_table(current_time: str, back: int = 7, ahead: int = 14) -> str:
    now = datetime.fromisoformat(current_time)
    lines = [f"Bây giờ: {WEEKDAYS[now.weekday()]} {now.isoformat()}"]
    for d in range(-back, ahead + 1):
        day = now + timedelta(days=d)
        tag = f" ({RELATIVE[d]})" if d in RELATIVE else ""
        lines.append(f"{day.date().isoformat()} {WEEKDAYS[day.weekday()]}{tag}")
    return "\n".join(lines)


def render_context(ctx: dict) -> str:
    p = ctx.get("user_profile", {})
    labels = {"name": "Tên", "home_address": "Nhà", "work_address": "Nơi làm việc", "city": "Thành phố"}
    lines = [f"{labels.get(k, k)}: {v}" for k, v in p.items()]
    if ctx.get("location"):
        lines.append(f"Vị trí hiện tại: {ctx['location'].get('lat')}, {ctx['location'].get('lng')}")
    lines.append(f"Múi giờ: {ctx.get('timezone', 'Asia/Ho_Chi_Minh')}")
    return "\n".join(lines)


def build_system(item: dict, tools_by_name: dict, apps_by_id: dict) -> str:
    ctx = item["context"]
    return "\n\n".join([
        SYSTEM_RULES,
        "# Người dùng\n" + render_context(ctx),
        "# Lịch\n" + date_table(ctx["current_time"]),
        "# Tools\n" + render_tools(item, tools_by_name, apps_by_id),
        TOOL_FORMAT,
    ])


def render_calls(calls: list[dict]) -> str:
    return "\n".join(
        "<tool_call>\n" + json.dumps({"name": c["name"], "arguments": c.get("arguments") or {}}, ensure_ascii=False) + "\n</tool_call>"
        for c in calls
    )


def compact_result(result, max_chars: int = 4000) -> str:
    s = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
    return s if len(s) <= max_chars else s[:max_chars] + "…(cắt bớt)"


def render_results(results: list) -> str:
    return "\n".join(f"<tool_response>\n{compact_result(r)}\n</tool_response>" for r in results)


def history_messages(history: list[dict], user_texts: list[str]) -> list[dict]:
    """history turns -> messages. user_texts[i] is the transcript of the i-th user turn (ASR or audio_text)."""
    msgs, ui = [], 0
    for turn in history:
        if turn["role"] == "user":
            msgs.append({"role": "user", "content": user_texts[ui]})
            ui += 1
            continue
        calls = turn.get("tool_calls") or []
        if calls:
            msgs.append({"role": "assistant", "content": render_calls(calls)})
            results = turn.get("tool_results") or [{"ok": True}] * len(calls)
            msgs.append({"role": "user", "content": render_results(results)})
        msgs.append({"role": "assistant", "content": turn.get("text") or ""})
    return msgs


def build_messages(item: dict, user_text: str, history_texts: list[str], tools_by_name: dict, apps_by_id: dict) -> list[dict]:
    return [
        {"role": "system", "content": build_system(item, tools_by_name, apps_by_id)},
        *history_messages(item.get("history", []), history_texts),
        {"role": "user", "content": user_text},
    ]


def to_chatml(messages: list[dict], add_generation_prompt: bool = True) -> str:
    out = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in messages)
    return out + ("<|im_start|>assistant\n" if add_generation_prompt else "")
