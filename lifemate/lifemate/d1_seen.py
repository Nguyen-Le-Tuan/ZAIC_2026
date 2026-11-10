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
    people = [p for p in rng.sample(G.PEOPLE, rng.randint(5, 8)) if not twin or twin.lower() not in p[0].lower().split()]
    rows = [(n, rel) for n, rel in people]
    twins = []
    if twin:
        if rng.random() < 0.85:   # the real twins carry the very same name and differ by relation (8 of 8 looked at)
            r1, r2 = rng.sample(["đồng nghiệp", "khách hàng", "bạn", "bạn học", "chị họ", "anh họ", "hàng xóm", "vợ", "chồng", "em gái"], 2)
            twins = [(twin, r1), (twin, r2)]
        else:
            a, b = rng.choice(TWINS)
            twins = [(a.format(g=twin), "người quen"), (b.format(g=twin), "khách hàng")]
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


# ---------------------------------------------------------------- part 2: the 7 apps that lose most points
# State: label.final_state[app] of the shell sample itself (the app after that sample's own writes): a real state in the
# real format, at the shell's own date. Conventions: the fit_random labels of each tool (scripts/d1_compare.py).

import copy
from datetime import datetime, timedelta

from .d1_gen import day_phrase, iso, money_phrase, pick_datetime, time_phrase

BILL_VI = {"electricity": "điện", "water": "nước", "internet": "internet", "tv": "truyền hình", "tuition": "học phí", "phone": "điện thoại"}
IATA = {"HAN": "Hà Nội", "SGN": "TP.HCM", "DAD": "Đà Nẵng", "HUI": "Huế", "VCA": "Cần Thơ", "VDH": "Đồng Hới", "CXR": "Nha Trang", "PQC": "Phú Quốc",
        "DLI": "Đà Lạt", "HPH": "Hải Phòng", "VII": "Vinh", "UIH": "Quy Nhơn", "BMV": "Buôn Ma Thuột", "VCS": "Côn Đảo", "THD": "Thanh Hoá", "PXU": "Pleiku"}
PLACES = ["Văn phòng", "Nhà hàng Sen Vàng", "Quán cà phê Góc Phố", "Sân bóng Mini", "Trường tiểu học", "Phòng khám Hoà Bình", "Nhà văn hoá phường",
          "Công viên trung tâm", "Phòng họp tầng 3", "Nhà bà ngoại"]
EVENT_TITLES = ["Họp nhóm dự án", "Khám răng", "Đi ăn với khách", "Học tiếng Anh", "Đá bóng", "Họp phụ huynh", "Tập gym", "Cà phê với bạn cũ", "Phỏng vấn",
                "Đón người thân ở sân bay", "Sinh nhật mẹ", "Nộp hồ sơ", "Đi chợ hoa", "Bảo dưỡng xe", "Chạy bộ", "Học đàn", "Họp tổ dân phố", "Đi khám tổng quát"]


def state_of(profile: dict, app: str):
    fs = (profile["_shell"]["label"].get("final_state") or {}).get(app)
    if fs is None:
        raise ValueError(f"{app}: the shell has no state")
    return copy.deepcopy(fs)


def unique(items: list[dict], key) -> list[dict]:
    """Items whose key value no other item shares (the user can name them without ambiguity)."""
    n = {}
    for it in items:
        n[key(it)] = n.get(key(it), 0) + 1
    return [it for it in items if key(it) is not None and n[key(it)] == 1]


def app_bill_payment(rng, now, profile):
    st = state_of(profile, "bill_payment")
    wallet = (profile["_shell"]["label"].get("final_state") or {}).get("ewallet")
    open_ = unique([b for b in st.get("bills", []) if not b.get("paid") and b.get("type") in BILL_VI], lambda b: b["type"])

    def src(b):
        ok = wallet is not None and wallet.get("balance", 0) >= b.get("amount", 0)
        s = rng.choice(["bank", "bank", "ewallet"]) if ok else "bank"
        return s, "ngân hàng" if s == "bank" else "ví điện tử"

    def pay(n=1):
        if len(open_) < n:
            return None
        bs = rng.sample(open_, n)
        parts, ws = [], []
        for b in bs:
            s, vi = src(b)
            if s == "ewallet" and any(w["arguments"]["source"] == "ewallet" for w in ws):
                s, vi = "bank", "ngân hàng"
            ws.append(call("bill_payment.pay", bill_id=b["id"], source=s))
            parts.append(f"hoá đơn «{BILL_VI[b['type']]}» bằng {vi}")
        return Intent("thanh toán " + " và ".join(parts), ws, refs={b["id"]: {"mention": None} for b in bs}, must=[BILL_VI[b["type"]] for b in bs])

    def autopay():
        ty = rng.choice(list(BILL_VI))
        return Intent(f"bật tự động thanh toán hoá đơn «{BILL_VI[ty]}»", [call("bill_payment.schedule_autopay", type=ty, enabled=True)], must=[BILL_VI[ty]])

    def look():
        return Intent("hỏi còn những hoá đơn nào chưa thanh toán", reads=[call("bill_payment.list_bills")], kind="lookup")
    extra = {"ewallet": copy.deepcopy(wallet)} if wallet is not None else {}
    return st, {"execute": [pay] * 8 + [lambda: pay(2)] * 2 + [autopay], "lookup": [look], "ask": []}, extra


def app_calendar(rng, now, profile):
    st = state_of(profile, "calendar")
    evs = unique([e for e in st.get("events", []) if e.get("status") == "confirmed" and e.get("start", "") > iso(now)], lambda e: e.get("title"))

    def create():
        title = rng.choice([x for x in EVENT_TITLES if x not in {e.get("title") for e in st.get("events", [])}])
        dt, ph = pick_datetime(rng, now, days=(0, 6), hours=(7, 20))
        end = iso(dt + timedelta(hours=1)) if rng.random() < 0.67 else None   # 22 of 33 real calls carry end = start + 1 h
        loc = rng.choice(PLACES) if rng.random() < 0.21 else None              # 7 of 33 carry a location
        return Intent(f"tạo lịch «{title}» lúc {ph}" + (f" tại «{loc}»" if loc else ""),
                      [call("calendar.create_event", title=title, start=iso(dt), end=end, location=loc)], must=[title] + ([loc] if loc else []))

    def move():
        if not evs:
            return None
        e = rng.choice(evs)
        s0, e0 = datetime.fromisoformat(e["start"]).replace(tzinfo=None), datetime.fromisoformat(e["end"]).replace(tzinfo=None)
        dt, ph = pick_datetime(rng, now, days=(0, 5), hours=(7, 20))
        if dt == s0:
            return None
        return Intent(f"dời lịch «{e['title']}» sang {ph}", [call("calendar.update_event", event_id=e["id"], start=iso(dt), end=iso(dt + (e0 - s0)))],
                      refs={e["id"]: {"mention": None}}, must=[e["title"]])

    def cancel():
        if not evs:
            return None
        e = rng.choice(evs)
        return Intent(f"huỷ lịch «{e['title']}»", [call("calendar.cancel_event", event_id=e["id"])], refs={e["id"]: {"mention": None}}, must=[e["title"]])

    def look():
        if rng.random() < 0.16:   # 14 of 87 real list_events calls carry a date range
            d = now + timedelta(days=rng.choice([0, 1, 1, 2]))
            day = d.strftime("%Y-%m-%d")
            return Intent(f"hỏi {day_phrase(now, d)} mình có những lịch gì", reads=[call("calendar.list_events", date_from=day, date_to=day)], kind="lookup")
        return Intent(rng.choice(["hỏi sắp tới mình có những lịch gì", "hỏi lịch của mình mấy hôm tới"]), reads=[call("calendar.list_events")], kind="lookup")
    return st, {"execute": [create] * 4 + [move] * 4 + [cancel] * 3, "lookup": [look], "ask": []}


def app_reminders(rng, now, profile):
    st = state_of(profile, "reminders")
    rems = unique([r for r in st.get("reminders", []) if not r.get("done")], lambda r: r.get("content"))

    def create():
        dt, ph = pick_datetime(rng, now, days=(0, 4), hours=(6, 21))
        what = rng.choice(G.REMIND)
        return Intent(f"nhắc mình «{what}» lúc {ph}", [call("reminders.create", content=what, time=iso(dt))], must=[what])

    def done():
        if not rems:
            return None
        r = rng.choice(rems)
        return Intent(f"đánh dấu việc nhắc «{r['content']}» là đã xong", [call("reminders.complete", reminder_id=r["id"])], refs={r["id"]: {"mention": None}}, must=[r["content"]])

    def delete():
        if not rems:
            return None
        r = rng.choice(rems)
        return Intent(f"xoá việc nhắc «{r['content']}»", [call("reminders.delete", reminder_id=r["id"])], refs={r["id"]: {"mention": None}}, must=[r["content"]])

    def look():
        return Intent("hỏi mình đang có những việc nhắc nào", reads=[call("reminders.list")], kind="lookup")
    return st, {"execute": [create] * 6 + [done] * 2 + [delete], "lookup": [look], "ask": []}


def app_banking(rng, now, profile):
    st = state_of(profile, "banking")
    accs, bens = st.get("accounts", []), unique(st.get("beneficiaries", []), lambda b: b.get("name"))
    main = next((a for a in accs if "thanh toán" in (a.get("name") or "").lower()), accs[0] if accs else None)

    def transfer(n=1):
        if main is None or len(bens) < n:
            return None
        bs = rng.sample(bens, n)
        amts = [rng.choice([150000, 200000, 350000, 500000, 800000, 1200000, 2500000, 3000000]) for _ in bs]
        if sum(amts) > main.get("balance", 0):
            return None
        return Intent("chuyển khoản ngân hàng " + " và ".join(f"{money_phrase(a)} đồng cho «{b['name']}»" for a, b in zip(amts, bs)),
                      [call("banking.transfer", from_account_id=main["id"], beneficiary_id=b["id"], amount=a) for a, b in zip(amts, bs)],
                      refs={main["id"]: {"mention": None}, **{b["id"]: {"mention": None} for b in bs}}, must=[b["name"] for b in bs])

    def savings():
        if main is None or main.get("balance", 0) < 5000000:
            return None
        amt = rng.choice([x for x in (3000000, 5000000, 10000000, 20000000) if x <= main["balance"]])
        m = rng.choice([1, 3, 6, 12])
        return Intent(f"gửi tiết kiệm {money_phrase(amt)} đồng kỳ hạn {m} tháng", [call("banking.open_savings", from_account_id=main["id"], amount=amt, term_months=m)],
                      refs={main["id"]: {"mention": None}})

    def look():
        return Intent("hỏi số dư các tài khoản ngân hàng", reads=[call("banking.get_balance")], kind="lookup")
    return st, {"execute": [transfer] * 8 + [lambda: transfer(2)] * 2 + [savings], "lookup": [look], "ask": []}


def app_flights(rng, now, profile):
    st = state_of(profile, "flights")
    fls = [f for f in st.get("flights", []) if f.get("origin") in IATA and f.get("destination") in IATA and f.get("date", "") >= now.strftime("%Y-%m-%d")]
    bks = [b for b in st.get("bookings", []) if b.get("status") == "confirmed"]
    by_id = {f["id"]: f for f in st.get("flights", [])}

    def where(f):
        hh, mm = map(int, f["depart"].split(":"))
        return f"từ «{IATA[f['origin']]}» đi «{IATA[f['destination']]}» {day_phrase(now, datetime.strptime(f['date'], '%Y-%m-%d'))}, chuyến cất cánh lúc {time_phrase(hh, mm)}"

    def book():
        if not fls:
            return None
        f = rng.choice(fls)
        same = [x for x in fls if (x["origin"], x["destination"], x["date"], x["depart"]) == (f["origin"], f["destination"], f["date"], f["depart"])]
        if len(same) != 1:
            return None
        n = rng.choice([1, 2, 2, 3])
        return Intent(f"đặt {n} vé máy bay {where(f)}", [call("flights.book", flight_id=f["id"], passengers=n)],
                      refs={f["id"]: {"mention": None, "slots": {"origin": f["origin"], "destination": f["destination"], "date": f["date"]}}},
                      must=[IATA[f["origin"]], IATA[f["destination"]]])

    def _one_booking():
        ok = [b for b in bks if by_id.get(b.get("flight_id"), {}).get("destination") in IATA]
        return ok[0] if len(ok) == 1 else None

    def checkin():
        b = _one_booking()
        if b is None:
            return None
        return Intent(f"làm thủ tục online cho chuyến bay đi «{IATA[by_id[b['flight_id']]['destination']]}» đã đặt", [call("flights.check_in", booking_id=b["id"])],
                      refs={b["id"]: {"mention": None}}, must=[IATA[by_id[b["flight_id"]]["destination"]]])

    def cancel():
        b = _one_booking()
        if b is None:
            return None
        return Intent(f"huỷ vé máy bay đi «{IATA[by_id[b['flight_id']]['destination']]}» đã đặt", [call("flights.cancel", booking_id=b["id"])],
                      refs={b["id"]: {"mention": None}}, must=[IATA[by_id[b["flight_id"]]["destination"]]])

    def look():
        if bks and rng.random() < 0.5:
            return Intent("hỏi mình đã đặt những vé máy bay nào", reads=[call("flights.my_bookings")], kind="lookup")
        if not fls:
            return None
        f = rng.choice(fls)
        return Intent(f"hỏi {day_phrase(now, datetime.strptime(f['date'], '%Y-%m-%d'))} có những chuyến bay nào từ «{IATA[f['origin']]}» đi «{IATA[f['destination']]}»",
                      reads=[call("flights.search", origin=f["origin"], destination=f["destination"], date=f["date"])], must=[IATA[f["origin"]], IATA[f["destination"]]], kind="lookup")
    # flights.cancel is left out: its 3 real labels all take the booking from the history, never from my_bookings
    return st, {"execute": [book] * 5 + [checkin] * 3, "lookup": [look], "ask": []}


def app_chat_seen(rng, now, profile):
    st = state_of(profile, "chat_ott")
    chats = unique(st.get("chats", []), lambda c: c.get("name"))

    def send():
        if not chats:
            return None
        c = rng.choice(chats)
        msg = rng.choice(MSGS)
        return Intent(f"nhắn qua Zalo cho «{c['name']}» nội dung «{msg}»", [call("chat_ott.send_message", chat_id=c["id"], content=msg)],
                      refs={c["id"]: {"mention": None}}, must=[c["name"], msg])

    def location():
        if not chats:
            return None
        c = rng.choice(chats)
        return Intent(f"gửi vị trí hiện tại qua Zalo cho «{c['name']}»", [call("chat_ott.send_location", chat_id=c["id"])], refs={c["id"]: {"mention": None}}, must=[c["name"]])

    def ring():
        if not chats:
            return None
        c = rng.choice(chats)
        video = rng.random() < 0.75   # 3 of 4 real calls carry video
        return Intent(f"gọi {'video ' if video else ''}Zalo cho «{c['name']}»", [call("chat_ott.call", chat_id=c["id"], video=True if video else None)],
                      refs={c["id"]: {"mention": None}}, must=[c["name"]])

    def read():
        with_msgs = [c for c in chats if c.get("messages")]
        if not with_msgs:
            return None
        c = rng.choice(with_msgs)
        return Intent(f"đọc lại tin nhắn Zalo với «{c['name']}»", reads=[call("chat_ott.list_chats"), call("chat_ott.read_chat", chat_id=c["id"])], must=[c["name"]], kind="lookup")
    return st, {"execute": [send] * 12 + [location, ring], "lookup": [read], "ask": []}


def app_email(rng, now, profile):
    st = state_of(profile, "email")
    inbox = unique([m for m in st.get("emails", []) if m.get("folder", "inbox") == "inbox" and m.get("from_name")], lambda m: m["from_name"])
    replies = ["em nhận được rồi ạ, cảm ơn chị", "chiều nay tôi gửi lại nhé", "mai mình họp bàn thêm nha", "tôi đồng ý với đề xuất này", "em sẽ kiểm tra và báo lại sau",
               "cảm ơn anh, em đã lưu lịch rồi", "tuần sau tôi mới rảnh, mình dời được không"]

    def reply():
        if not inbox:
            return None
        m = rng.choice(inbox)
        body = rng.choice(replies)
        return Intent(f"trả lời email của «{m['from_name']}» với nội dung «{body}»", [call("email.reply", email_id=m["id"], body=body)],
                      refs={m["id"]: {"mention": None}}, must=[m["from_name"], body])

    def archive():
        if not inbox:
            return None
        m = rng.choice(inbox)
        act, vi = rng.choice([("archive", "lưu trữ"), ("delete", "xoá")])
        return Intent(f"{vi} email của «{m['from_name']}»", [call("email.archive", email_id=m["id"], action=act)], refs={m["id"]: {"mention": None}}, must=[m["from_name"]])

    def read():
        if not inbox:
            return None
        m = rng.choice(inbox)
        return Intent(f"mở đọc email của «{m['from_name']}»", reads=[call("email.list"), call("email.read", email_id=m["id"])], must=[m["from_name"]], kind="lookup")

    def look():
        return Intent("hỏi hộp thư có những email nào", reads=[call("email.list")], kind="lookup")
    return st, {"execute": [reply, archive], "lookup": [read, look], "ask": []}


# email is written above but not used: real replies and archives take the email from the history in 8 of 10 labels (the
# generated ones list the inbox first in 85-88%), and create_draft / send need contacts that carry an email address.
APPS7 = {"bill_payment": app_bill_payment, "calendar": app_calendar, "reminders": app_reminders, "banking": app_banking, "flights": app_flights,
         "chat_ott": app_chat_seen}
WEIGHTS7 = {"execute": 40, "execute+side": 32, "lookup": 16, "lookup+side": 7, "not_installed": 5}


def shells_with_state(app: str, shells: list[dict]) -> list[dict]:
    out = [s for s in shells if app in (s["label"].get("final_state") or {})]
    if not out:
        raise SystemExit(f"no shell with a final_state for {app}")
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--part", choices=["asks", "apps"], default="asks")
    b.add_argument("--total", type=int, default=400, help="asks: scenarios in all")
    b.add_argument("--n", type=int, default=60, help="apps: scenarios per app")
    b.add_argument("--apps")
    b.add_argument("--shells", default="splits/fit_random.txt")
    b.add_argument("--seed", type=int, default=0)
    b.add_argument("--tag", required=True)
    a = ap.parse_args()
    a.split = "train"
    if a.part == "asks":
        s = sum(SHARE.values())
        G.cmd_build(a, registry=SEEN, weights=WEIGHTS, counts={k: max(1, round(a.total * v / s)) for k, v in SHARE.items()})
    else:
        G.cmd_build(a, registry=APPS7, weights=WEIGHTS7, shells_for=shells_with_state, history_ids=True)


if __name__ == "__main__":
    main()
