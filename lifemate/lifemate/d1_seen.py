"""D1 for the apps the train labels already cover (46 apps), by what loses most points on dev_random first.

  python -m lifemate.d1_seen build --total 400 --seed 0 --tag seenask0 [--shells splits/fit_random.txt]
  python scripts/d1_compare.py --tag seenask0 --asks --ids splits/fit_random.txt      # against the real fit labels

Part 1 (this file, so far): clarifications. In the fit_random labels 184 samples end with sys.ask_missing_info; most
are one of a few programmes (counts from fit_random):
  phone.call / sms.send / email.create_draft / chat_ott.send_message: the name the user says matches two contacts or
      chats -> the look-up, then ask for contact_id / to / chat_id (the look-up returns exactly 2 in 58 of 63 cases);
  ewallet.transfer: the person is found, the amount is not said ("chút tiền") -> the look-up, then ask for amount;
  reminders.create without a time, fitness.set_goal without steps, home_energy.set_alert without a threshold -> ask.
40% of them come with another, complete request in the same sentence (73 of 184).
The label conventions are the real ones (lifemate.d1_policy and the patterns above); states are built here: these
programmes only read contacts and chats, which name pools give. Programmes that write (the 7 apps that lose most:
bill_payment, calendar, reminders, banking, flights, chat_ott, email) will take their states from label.final_state
of fit samples; not written yet.
"""
from __future__ import annotations

import argparse

from . import d1_gen as G
from .d1_gen import ASK, Intent, call, call_key, ids

GIVEN = ["Minh", "Hương", "Lan", "Tuấn", "Hà", "Linh", "Nam", "Thảo", "Quân", "Vy", "Hùng", "Mai", "Phương", "Dũng", "Trang", "Khánh",
         "Ngân", "An", "Huy", "Thu", "Long", "Yến", "Sơn", "Nga", "Bình", "Hải", "Oanh", "Tâm", "Đức", "Loan"]
TWINS = [("Anh {g}", "Chú {g}"), ("Chị {g}", "{g} kế toán"), ("{g}", "{g} hàng xóm"), ("{g} công ty", "{g} lớp cũ"), ("Bác {g}", "{g} sửa xe"),
         ("Em {g}", "Cô {g}"), ("{g}", "Sếp {g}"), ("{g} nhà trẻ", "{g} bảo vệ")]
MSGS = ["mai gửi mình file nhé", "nhớ mang hộ cái sạc", "chiều nay mình tới trễ mười lăm phút", "họp dự án chuyển sang ba giờ chiều", "tối nay ăn cơm ở nhà nhé",
        "em nhận được hồ sơ rồi", "bản demo xong rồi", "cuối tuần qua nhà chơi nha", "nhớ đón con lúc năm giờ", "mình đang trên đường tới",
        "gửi lại giúp mình hoá đơn tháng này", "mai nghỉ học nhé", "đã chuyển khoản rồi nha", "tới nơi thì gọi mình", "nhớ khoá cửa trước khi đi"]


def contacts(rng, twin: str | None = None) -> tuple[list[dict], list[dict]]:
    """A contact book from the name pool; with `twin`, two entries carry that given name. -> (contacts, the twins)."""
    fold = G.atoms  # noqa: F841  (kept for parity of imports)
    people = [p for p in rng.sample(G.PEOPLE, rng.randint(5, 8)) if not twin or twin.lower() not in p[0].lower().split()]
    rows = [(n, rel) for n, rel in people]
    twins = []
    if twin:
        a, b = rng.choice(TWINS)
        twins = [(a.format(g=twin), rng.choice(["đồng nghiệp", "bạn", "hàng xóm", "người quen"])), (b.format(g=twin), rng.choice(["bạn", "khách hàng", "người quen"]))]
        rows += twins
    rng.shuffle(rows)
    out = [{"id": i, "name": n, "relation": rel, "phone": "09" + "".join(rng.choice("0123456789") for _ in range(8))} for i, (n, rel) in zip(ids("c", len(rows), rng), rows)]
    return out, [c for c in out if twins and c["name"] in {t[0] for t in twins}]


def _twin_ask(tool: str, param: str, say: str):
    def builder(rng, now, profile):
        g = rng.choice(GIVEN)
        book, _ = contacts(rng, g)
        msg = rng.choice(MSGS)

        def ask():
            r = call("contacts.search", query=g)
            return Intent(say.format(g=g, msg=msg), reads=[r], ask=call(ASK, tool_name=tool, params=[param]), must=[g], kind="ask", hits={call_key(r): ">=2"})
        return {}, {"execute": [], "lookup": [], "ask": [ask]}, {"contacts": {"contacts": book}}
    return builder


def app_ewallet(rng, now, profile):
    book, _ = contacts(rng)
    c = rng.choice(book)

    def ask():
        r = call("contacts.search", query=c["name"])
        return Intent(f"chuyển tiền qua ví điện tử cho «{c['name']}» (chỉ nói \"chút tiền\" hoặc \"ít tiền\", không nói bao nhiêu)", reads=[r],
                      ask=call(ASK, tool_name="ewallet.transfer", params=["amount"]), must=[c["name"]], kind="ask", hits={call_key(r): "==1"})
    return {"balance": rng.choice([350000, 1200000, 4800000])}, {"execute": [], "lookup": [], "ask": [ask]}, {"contacts": {"contacts": book}}


def app_chat_ott(rng, now, profile):
    g = rng.choice(GIVEN)
    book, _ = contacts(rng, g)
    chats = [{"id": i, "name": c["name"], "type": "direct", "members": [c["name"]], "messages": []} for i, c in zip(ids("chat", len(book), rng), book)]
    msg = rng.choice(MSGS)

    def ask():
        return Intent(f"nhắn qua ứng dụng chat (Zalo) cho «{g}» (có hai cuộc trò chuyện với người tên này; không nói rõ ai), nội dung: {msg}",
                      reads=[call("chat_ott.list_chats")], ask=call(ASK, tool_name="chat_ott.send_message", params=["chat_id"]), must=[g], kind="ask")
    return {"chats": chats}, {"execute": [], "lookup": [], "ask": [ask]}


def _plain_ask(tool: str, param: str, says: list[str]):
    def builder(rng, now, profile):
        what = rng.choice(G.REMIND)

        def ask():
            return Intent(rng.choice(says).format(what=what), ask=call(ASK, tool_name=tool, params=[param]), must=[what] if "{what}" in says[0] else [], kind="ask")
        return {}, {"execute": [], "lookup": [], "ask": [ask]}
    return builder


SEEN = {
    "phone": _twin_ask("phone.call", "contact_id", "gọi điện cho «{g}» (danh bạ có hai người tên này; không nói rõ ai)"),
    "sms": _twin_ask("sms.send", "contact_id", "nhắn tin SMS cho «{g}» (danh bạ có hai người tên này; không nói rõ ai), nội dung: {msg}"),
    "email": _twin_ask("email.create_draft", "to", "soạn email gửi «{g}» (danh bạ có hai người tên này; không nói rõ ai), nội dung: {msg}"),
    "ewallet": app_ewallet,
    "chat_ott": app_chat_ott,
    "reminders": _plain_ask("reminders.create", "time", ["nhắc mình «{what}» (không nói nhắc lúc nào)"]),
    "fitness": _plain_ask("fitness.set_goal", "steps", ["đổi mục tiêu số bước chân mỗi ngày (không nói bao nhiêu bước)", "hạ mục tiêu bước chân mỗi ngày xuống một chút (không nói con số)"]),
    "home_energy": _plain_ask("home_energy.set_alert", "threshold_kwh", ["đặt cảnh báo khi dùng điện nhiều (không nói ngưỡng bao nhiêu)"]),
}
# share of the real clarifications each programme stands for (fit_random counts)
SHARE = {"phone": 32, "sms": 26, "ewallet": 17, "reminders": 5, "chat_ott": 4, "email": 3, "fitness": 3, "home_energy": 3}
WEIGHTS = {"ask": 60, "ask+side": 40}   # 73 of 184 real clarifications come with another complete request


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--total", type=int, default=400)
    b.add_argument("--apps")
    b.add_argument("--shells", default="splits/fit_random.txt")
    b.add_argument("--seed", type=int, default=0)
    b.add_argument("--tag", required=True)
    a = ap.parse_args()
    a.split, a.n = "train", 0
    s = sum(SHARE.values())
    G.cmd_build(a, registry=SEEN, weights=WEIGHTS, counts={k: max(1, round(a.total * v / s)) for k, v in SHARE.items()})


if __name__ == "__main__":
    main()
