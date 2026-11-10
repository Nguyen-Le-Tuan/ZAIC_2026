"""Grow the name pools of lifemate.d1_gen with an external LLM (Meta), once; the result is lifemate/d1_pools.json.

  cd lifemate && set -a && . ~/.zac_meta_env && set +a && PYTHONPATH=. python3 scripts/d1_pools.py --max-usd 2

Only invented names are asked for: the prompt carries the rows already in d1_gen (themselves invented) as the format
to follow, and nothing from the competition files. Rows are checked by code (types, the short mention is inside the
name after folding, no duplicate) before they are kept. Calls are logged in gen/d1_pools_usage.jsonl and count
against the Meta cap of lifemate.d1_say.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from lifemate import d1_gen as G
from lifemate.d1_say import GEN_DIR, Ledger, fold, meta_writer

S, I, A = {"type": "string"}, {"type": "integer"}, {"type": "array", "items": {"type": "string"}}
# pool -> (fields, target size, what the rows are, index of a "short mention" field that must sit inside field 0)
POOLS = {
    "EVENTS": (["name", "mention", "category", "venue", "price"], [S, S, S, S, I], 90, "sự kiện có bán vé ở Việt Nam (ca nhạc, kịch, phim, thể thao, triển lãm, hài, xiếc, hội thảo...); mention là phần tên ngắn 2-4 từ mà người ta hay gọi, PHẢI là một đoạn liền trong name", 1),
    "GROCERY": (["name", "mention", "unit", "category", "price"], [S, S, S, S, I], 110, "sản phẩm của app đi chợ online (thực phẩm tươi, đồ khô, đồ uống, gia vị, đồ gia dụng nhỏ); nên có vài nhóm cùng hai từ đầu nhưng khác nhãn hiệu; mention là cách gọi ngắn, PHẢI là một đoạn liền trong name", 1),
    "PANTRY": (["name", "unit"], [S, S], 70, "món đồ khô, gia vị, thực phẩm thường có trong tủ bếp gia đình Việt; name 1-3 từ, không nhãn hiệu", None),
    "HABITS": (["name"], [S], 60, "thói quen hằng ngày người ta theo dõi (sức khoẻ, học tập, công việc, gia đình); name 2-6 từ, viết hoa chữ đầu", None),
    "PHRASES": (["text"], [S], 90, "câu ngắn 4-9 từ mà người đi du lịch, đi làm, đi học hay nhờ dịch sang tiếng nước ngoài; chữ thường, không dấu chấm câu", None),
    "LOTS": (["name", "address", "area", "price"], [S, S, S, I], 60, "bãi đỗ xe ở Hà Nội, TP.HCM, Đà Nẵng, Huế, Cần Thơ, Hải Phòng; area là tên địa danh hoặc khu vực mà người ta nói 'gần ...', mỗi area chỉ dùng MỘT lần và không nằm trong name/address của bãi khác; price là giá mỗi giờ", None),
    "SHOP": (["name", "mention", "seller", "category", "price"], [S, S, S, S, I], 110, "sản phẩm trên sàn thương mại điện tử (điện tử, gia dụng, thời trang, sách, mỹ phẩm, đồ trẻ em, thể thao); nên có vài nhóm cùng hai từ đầu nhưng khác hãng; mention là cách gọi ngắn, PHẢI là một đoạn liền trong name", 1),
    "REMIND": (["text"], [S], 70, "việc người ta nhờ nhắc (2-6 từ, bắt đầu bằng động từ, chữ thường), ví dụ 'gọi cho mẹ'", None),
    "BOOKS": (["title", "author"], [S, S], 90, "sách tiếng Việt hoặc sách dịch nổi tiếng có trong thư viện; nên có vài tác giả có 2-3 cuốn", None),
    "MEDS": (["name"], [S], 60, "thuốc, vitamin, thực phẩm chức năng người ta uống theo lịch; name 1-4 từ", None),
    "MEETINGS": (["title"], [S], 70, "tên cuộc họp trực tuyến ở công ty, trường học, gia đình; 2-6 từ", None),
    "PEOPLE": (["name", "relation"], [S, S], 70, "tên người lưu trong danh bạ kiểu người Việt hay lưu (có thể kèm vai vế: 'Chị Ngọc', 'Sếp Thắng', 'Bác Tư', hoặc tên riêng 'Minh Anh'); mỗi name khác hẳn nhau; relation là quan hệ viết thường", None),
    "PROGRAMS": (["name", "merchant"], [S, S], 36, "chương trình thành viên/tích điểm của một thương hiệu bán lẻ, cà phê, hàng không, rạp phim, siêu thị (tên bịa, nghe như thật)", None),
    "ROOMS": (["name"], [S], 24, "tên phòng/khu vực trong nhà mà robot hút bụi dọn (chữ thường)", None),
}


def schema(fields, types):
    return {"type": "object", "additionalProperties": False, "required": ["rows"], "properties": {"rows": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": fields, "properties": dict(zip(fields, types))}}}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-usd", type=float, required=True)
    ap.add_argument("--model", default="muse-spark-1.3")
    ap.add_argument("--pools")
    a = ap.parse_args()
    out_path = Path(G.__file__).with_name("d1_pools.json")
    have = json.loads(out_path.read_text()) if out_path.exists() else {}
    ledger = Ledger(GEN_DIR / "d1_pools_usage.jsonl", a.model, a.max_usd)
    ask = meta_writer(a.model)
    for name in (a.pools.split(",") if a.pools else POOLS):
        fields, types, target, what, mention = POOLS[name]
        base = [list(r) if isinstance(r, (tuple, list)) else [r] for r in getattr(G, name + "_BASE", getattr(G, name))]
        rows = [r[:len(fields)] for r in base] + have.get(name, [])
        seen = {fold(r[0]) for r in rows}
        tries = 0
        while len(rows) < target and tries < 4:
            tries += 1
            why = ledger.blocked()
            if why:
                print(why)
                break
            need = min(60, target - len(rows) + 8)
            system = ("Bạn tạo dữ liệu tên bịa cho một bộ sinh dữ liệu tiếng Việt. Trả về JSON đúng schema. Mỗi dòng phải KHÁC các dòng đã có, "
                      "tự nhiên như thật ở Việt Nam, đa dạng vùng miền và chủng loại; giá là số nguyên đồng, hợp lý.")
            user = (f"Loại dữ liệu: {what}.\nCác trường theo thứ tự: {fields}.\nCác dòng đã có (đừng lặp lại):\n" +
                    "\n".join(json.dumps(dict(zip(fields, r)), ensure_ascii=False) for r in rows[-40:]) + f"\n\nHãy viết thêm {need} dòng mới.")
            t0 = time.time()
            try:
                text, pin, pout, _ = ask(system, user, schema(fields, types), "low")
                new = json.loads(text)["rows"]
            except (RuntimeError, json.JSONDecodeError, KeyError) as e:
                print(name, "call failed:", str(e)[:160])
                continue
            ledger.add(pin, pout, time.time() - t0, f"pool {name}")
            kept = 0
            for r in new:
                row = [r.get(f) for f in fields]
                if any(v is None or (isinstance(v, str) and not v.strip()) for v in row) or fold(row[0]) in seen:
                    continue
                if mention is not None and fold(row[mention]) not in fold(row[0]):
                    continue
                seen.add(fold(row[0]))
                rows.append(row)
                kept += 1
            print(f"{name}: +{kept} of {len(new)} -> {len(rows)}/{target}")
        have[name] = rows[len(base):]
        out_path.write_text(json.dumps(have, ensure_ascii=False, indent=0) + "\n")
    print(f"spent {ledger.spent():.3f} USD -> {out_path}")


if __name__ == "__main__":
    main()
