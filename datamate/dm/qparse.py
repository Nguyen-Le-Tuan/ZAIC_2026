"""Question -> structured query, by rules on the folded question (dm.textnorm.qfold).

Query fields:
  intent     what to compute (revenue, orders, qty, cancel_count, cancel_rate, aov, best_day, best_month,
             days_threshold, orders_threshold, items_in_orders, top_items, top_customers, customers_min_orders,
             share, pay_split, price_on_date, price_effect, unsold, stock, stock_units, debt_*, purchase_*,
             delivery_rounds, gross_profit, top_profit_item, net_profit, trend, months_list, customer_count, ...)
  periods    list of (start, end) dates; compare: None | 'prev' | 'prev_same_days' | 'yoy' | (start, end)
  output     'value' | 'pct_change' | 'diff' | 'pct_share'
  filters    product, category, cust_group, pay, channel, shift, size, staff, customer, ingredient, rx
  k, unit, threshold (op, value), state_date (for "đến hết ngày X")
The entity lists (product names, categories, ...) come from the business (dm.engine.Ctx) for matching.
"""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field

from . import periods as P
from .textnorm import fold, qfold

D = dt.date


@dataclass
class Query:
    intent: str = ""
    periods: list = field(default_factory=list)
    compare: object = None
    output: str = "value"
    filters: dict = field(default_factory=dict)
    k: int | None = None
    unit: str | None = None
    threshold: tuple | None = None
    state_date: D | None = None
    extra: dict = field(default_factory=dict)
    text: str = ""
    why: str = ""


_DATE = r"(\d{1,2})/(\d{1,2})/(20\d\d)"


def _d(m, i=1):
    return D(int(m.group(i + 2)), int(m.group(i + 1)), int(m.group(i)))


def _num(s: str) -> float | None:
    s = s.strip()
    m = re.fullmatch(r"([\d.,]+)\s*(trieu|tr|k|nghin|ngan|dong|d)?", s)
    if not m:
        return None
    v = m.group(1)
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", v):
        x = float(re.sub(r"[.,]", "", v))
    else:
        x = float(v.replace(",", "."))
    u = m.group(2) or ""
    if u in ("trieu", "tr"):
        x *= 1e6
    elif u in ("k", "nghin", "ngan"):
        x *= 1e3
    return x


_NUMW = {"mot": 1, "hai": 2, "ba": 3, "bon": 4, "nam": 5, "bay": 7, "tam": 8, "chin": 9, "muoi": 10,
         "muoi mot": 11, "muoi hai": 12, "muoi lam": 15, "muoi bon": 14, "hai muoi": 20, "ba muoi": 30, "bon muoi lam": 45,
         "sau muoi": 60, "chin muoi": 90}
_ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4}
_WD = {"thu hai": 0, "thu ba": 1, "thu tu": 2, "thu nam": 3, "thu sau": 4, "thu bay": 5, "chu nhat": 6, "cn": 6}


def normalize_periods(t: str, asof: D) -> str:
    """Rewrite period variants into the forms parse_periods knows."""
    y = asof.year
    # number words before a time unit: "ba ngay gan nhat" -> "3 ngay gan nhat"
    for w, n in sorted(_NUMW.items(), key=lambda kv: -len(kv[0])):
        t = re.sub(rf"\b{w} (ngay|tuan|thang|quy|nam)\b(?! (nay|ngoai|truoc|roi|sau))", f"{n} \\1", t)
    # ISO and dashed/dotted dates -> dd/mm/yyyy
    t = re.sub(r"\b(20\d\d)-(\d{1,2})-(\d{1,2})\b", lambda m: f"{int(m.group(3)):02d}/{int(m.group(2)):02d}/{m.group(1)}", t)
    t = re.sub(r"\b(\d{1,2})[-.](\d{1,2})[-.](20\d\d)\b", r"\1/\2/\3", t)
    # month forms: T6/2025, thg 6/2025, 06/2025 (not part of a date), 6-2025, 2025-06
    t = re.sub(r"\bt(\d{1,2})\s*[/-]\s*(20\d\d)\b", r"thang \1/\2", t)
    t = re.sub(r"\b(?:thg|th)\.? ?(\d{1,2})\s*[/-]\s*(20\d\d)\b", r"thang \1/\2", t)
    t = re.sub(r"(?<![/\d])(?<!thang )(?<!quy )(?<!q)\b(\d{1,2})\s*[/-]\s*(20\d\d)\b", r"thang \1/\2", t)
    t = re.sub(r"\bsau thang (dau|cuoi)\b", r"6 thang \1", t)
    t = re.sub(r"\bthang (\d{1,2})\s*-\s*(20\d\d)\b", r"thang \1/\2", t)
    t = re.sub(r"\bthang (\d{1,2}) cua nam (20\d\d)", r"thang \1/\2", t)
    # quarters: quy II/2025, Q2/2025, quy 2 2025
    t = re.sub(r"\bquy (iv|iii|ii|i)\b", lambda m: f"quy {_ROMAN[m.group(1)]}", t)
    t = re.sub(r"\bq([1-4])\s*[/-]?\s*(20\d\d)\b", r"quy \1/\2", t)
    t = re.sub(r"\bquy ([1-4]) (20\d\d)\b", r"quy \1/\2", t)
    # relative years
    t = re.sub(r"\b(thang|quy) (\d{1,2}) (?:cua )?nam (ngoai|truoc|roi)\b", lambda m: f"{m.group(1)} {m.group(2)}/{y - 1}", t)
    t = re.sub(r"\b(thang|quy) (\d{1,2}) (?:cua )?nam nay\b", lambda m: f"{m.group(1)} {m.group(2)}/{y}", t)
    t = re.sub(r"\bnam (ngoai|truoc|roi)\b(?! nua)", f"nam {y - 1}", t)
    t = re.sub(r"\bnam kia\b|\bnam truoc nua\b", f"nam {y - 2}", t)
    # date without year: "ngay 5/6" -> this year unless after today
    def _dm(m):
        d_, mo = int(m.group(2)), int(m.group(3))
        try:
            yy = y if D(y, mo, d_) <= asof else y - 1
        except ValueError:
            return m.group(0)
        return f"{m.group(1)} {d_:02d}/{mo:02d}/{yy}"
    t = re.sub(r"\b(ngay|hom|tu|den|toi|het)\s+(\d{1,2})/(\d{1,2})\b(?!/)", _dm, t)
    return t


def parse_periods(t: str, asof: D, cal: str | None) -> tuple[list, object, dict]:
    """Return (periods, compare, info). info may hold 'state_date', 'months' etc."""
    info = {}
    t = normalize_periods(t, asof)
    y0 = asof.year
    # named relative periods
    if re.search(r"\bhom kia\b", t):
        d = asof - dt.timedelta(days=2)
        return [(d, d)], None, info
    if re.search(r"\btuan truoc nua\b|\b2 tuan truoc\b", t):
        a, b = P.last_week(asof)
        return [(a - dt.timedelta(days=7), b - dt.timedelta(days=7))], None, info
    if re.search(r"\bthang truoc nua\b|\b2 thang truoc\b", t):
        yy, mm = P.shift_month(asof.year, asof.month, -2)
        return [P.month(mm, yy)], None, info
    m = re.search(r"\bcuoi tuan (truoc|roi|qua|vua roi)\b", t)
    if m:
        a, b = P.last_week(asof)
        return [(b - dt.timedelta(days=1), b)], None, info
    m = re.search(r"\b(thu hai|thu ba|thu tu|thu nam|thu sau|thu bay|chu nhat) (tuan truoc|tuan roi|tuan nay|vua roi|vua qua)\b", t)
    if m:
        wd = _WD[m.group(1)]
        if m.group(2) in ("tuan nay",):
            a, _ = P.this_week(asof)
        elif m.group(2) in ("vua roi", "vua qua"):
            d = asof - dt.timedelta(days=1)
            while d.weekday() != wd:
                d -= dt.timedelta(days=1)
            return [(d, d)], None, info
        else:
            a, _ = P.last_week(asof)
        d = a + dt.timedelta(days=wd)
        return [(d, d)], None, info
    if re.search(r"\bquy (truoc|roi|vua roi|vua qua)\b", t):
        q = (asof.month - 1) // 3 + 1
        yy, q2 = (asof.year, q - 1) if q > 1 else (asof.year - 1, 4)
        return [P.quarter(q2, yy)], None, info
    m = re.search(r"\b(nua dau|6 thang dau)( nam)?(?: (20\d\d))?\b", t)
    if m:
        yy = int(m.group(3)) if m.group(3) else y0
        return [(D(yy, 1, 1), D(yy, 6, 30))], None, info
    m = re.search(r"\b(nua cuoi|6 thang cuoi)( nam)?(?: (20\d\d))?\b", t)
    if m:
        yy = int(m.group(3)) if m.group(3) else (y0 if asof.month == 12 else y0 - 1)
        return [(D(yy, 7, 1), D(yy, 12, 31))], None, info
    if cal:
        m = re.search(r"\btrung thu(?: nam)? (20\d\d)?", t)
        if m:
            yy = int(m.group(1)) if m.group(1) else y0
            d = P.lunar_to_solar(cal, yy, 8, 15)
            if d:
                return [(d, d)], None, info
        hol = _holiday(t, asof, cal)
        if hol:
            return [hol], None, info
    # explicit range
    m = re.search(r"tu (?:ngay )?" + _DATE + r" (?:den|toi|-) (?:het )?(?:ngay )?" + _DATE, t)
    if m:
        return [(_d(m, 1), _d(m, 4))], None, info
    # tet
    m = re.search(r"\btet\b(?: am lich| nguyen dan)?(?: nam)? (20\d\d)", t) or re.search(r"(?:dip|mua) tet (20\d\d)", t)
    if m and cal:
        y = int(m.group(1))
        p = P.tet(cal, y)
        if p:
            cmp_ = None
            mm = re.search(r"(\d+) ngay (?:ngay )?truoc (?:dip )?tet", t)
            if "truoc tet" in t:
                bt = P.before_tet(cal, y)
                if mm and bt:
                    n = int(mm.group(1))
                    bt = (p[0] - dt.timedelta(days=n), p[0] - dt.timedelta(days=1))
                cmp_ = bt
            info["tet"] = y
            return [p], cmp_, info
    # list of months: "N thang lien nhau ket thuc o thang M/Y"
    m = re.search(r"(\d+) thang lien (?:nhau|tiep) ket thuc (?:o |vao |tai )?thang (\d{1,2})(?:/| nam )(20\d\d)", t)
    if m:
        n, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        months = [P.shift_month(y, mo, -i) for i in range(n - 1, -1, -1)]
        info["months"] = months
        return [P.month(mm_, yy) for yy, mm_ in months], None, info
    m = re.search(r"tu thang (\d{1,2})(?:/| nam )(20\d\d) (?:den|toi|qua) (?:het )?thang (\d{1,2})(?:/| nam )(20\d\d)", t)
    if m:
        y1, m1, y2, m2 = int(m.group(2)), int(m.group(1)), int(m.group(4)), int(m.group(3))
        months = []
        y, mo = y1, m1
        while (y, mo) <= (y2, m2) and len(months) < 24:
            months.append((y, mo))
            y, mo = P.shift_month(y, mo, 1)
        info["months"] = months
        return [P.month(mo_, y_) for y_, mo_ in months], None, info
    ms = re.findall(r"thang (\d{1,2})(?:/| nam )(20\d\d)", t)
    if len(ms) >= 3 or (len(ms) >= 2 and re.search(r"lien tuc|moi thang|lan luot|theo thu tu", t)):
        months = [(int(y), int(mo)) for mo, y in ms]
        info["months"] = months
        return [P.month(mo, y) for y, mo in months], None, info
    m = re.search(r"(\d+) thang\s*(\d{1,2})/(20\d\d),?\s*(\d{1,2})/(20\d\d)(?:,? (?:va )?(\d{1,2})/(20\d\d))?", t)
    if m:
        g = [x for x in m.groups()[1:] if x]
        months = [(int(g[i + 1]), int(g[i])) for i in range(0, len(g), 2)]
        info["months"] = months
        return [P.month(mo, y) for y, mo in months], None, info

    per = []
    cmp_ = None
    # state "den het ngay X" / "cuoi ngay hom nay"
    m = re.search(r"(?:den|toi) (?:het |cuoi )?(?:ngay )?" + _DATE, t)
    if m:
        info["state_date"] = _d(m, 1)
    elif re.search(r"(den|toi) (het |cuoi )?(ngay )?hom nay|cuoi ngay hom nay|hom nay .*cuoi ngay|het hom nay|hien (tai|gio|nay)|bay gio|con (ton|no)", t):
        info["state_date"] = asof
    m = re.search(r"(\d+) ngay (gan nhat|gan day|qua|vua qua|vua roi|cuoi)", t)
    if m:
        per.append(P.last_n_days(asof, int(m.group(1))))
    m = re.search(r"\bquy (\d)(?:/| nam )(20\d\d)", t)
    if m:
        per.append(P.quarter(int(m.group(1)), int(m.group(2))))
    elif re.search(r"\bquy nay\b", t):
        per.append(P.this_quarter(asof))
    else:
        m = re.search(r"\bquy (\d)\b", t)
        if m:
            per.append(P.quarter_no_year(asof, int(m.group(1))))
    for mo, y in re.findall(r"thang (\d{1,2})(?:/| nam )(20\d\d)", t):
        per.append(P.month(int(mo), int(y)))
    if not per:
        m = re.search(r"\bthang (\d{1,2})\b(?! ?nam)(?!/)", t)
        if m and not re.search(r"\d+ thang", t[:m.start() + 1]) and 1 <= int(m.group(1)) <= 12:
            per.append(P.month_no_year(asof, int(m.group(1))))
    for dd, mo, y in re.findall(r"(?:ngay|hom|vao)\s+" + _DATE, t):
        pass
    if not per:
        dates = re.findall(_DATE, t)
        if dates and "state_date" not in info:
            d0 = D(int(dates[0][2]), int(dates[0][1]), int(dates[0][0]))
            per.append((d0, d0))
    if re.search(r"\bthang nay\b|dau thang (nay )?(den|toi)", t):
        per.append(P.this_month(asof))
        if re.search(r"cung ky thang (truoc|roi)|cung so ngay", t):
            cmp_ = P.prev_month_same_days(asof)
        elif re.search(r"so (voi|vs) thang (truoc|roi)|hon hay kem thang (truoc|roi)", t):
            cmp_ = P.prev_month_same_days(asof)
    if re.search(r"\bthang (truoc|roi|lien truoc)\b", t) and not per:
        per.append(P.prev_month(asof))
    if re.search(r"\btuan nay\b", t):
        per.append(P.this_week(asof))
    if re.search(r"\btuan (truoc|roi|qua)\b", t):
        per.append(P.last_week(asof))
    if re.search(r"tu dau nam|nam nay|dau nam (den|toi)", t):
        per.append(P.ytd(asof))
    m = re.search(r"\bnam (20\d\d)\b", t)
    if m and not per:
        per.append(P.year(int(m.group(1))))
    if re.search(r"\bhom qua\b", t):
        per.append(P.day(asof - dt.timedelta(days=1)))
    if re.search(r"\bhom nay\b|\bngay hom nay\b|trong ngay\b(?! \d)", t) and not per and "state_date" not in info:
        per.append(P.day(asof))
    if re.search(r"\bhom nay\b", t) and not per and info.get("state_date") == asof and not re.search(r"ton|no\b|thieu", t):
        per.append(P.day(asof))
    # dedupe keeping order
    seen, out = set(), []
    for p in per:
        if p not in seen:
            seen.add(p)
            out.append(p)
    # comparisons
    if cmp_ is None and out:
        if re.search(r"cung ky nam (ngoai|truoc)|so (voi|vs) .*nam (ngoai|truoc)", t):
            cmp_ = "yoy"
        elif re.search(r"(thang|tuan|ky|quy|nam) (lien )?(truoc|roi)|ky truoc", t) and len(out) == 1:
            cmp_ = "prev"
    return out, cmp_, info


def _holiday(t: str, asof: D, cal: str):
    """A day named in calendar.csv's holiday column ("dịp Quốc khánh 2025", "lễ 30/4")."""
    import csv
    try:
        rows = list(csv.DictReader(open(cal, encoding="utf-8")))
    except OSError:
        return None
    names = {}
    for r in rows:
        h = fold(r.get("holiday") or "")
        if h:
            names.setdefault(h, []).append(D.fromisoformat(r["date"]))
    alias = {"quoc khanh": "2/9", "le 2/9": "2/9", "ngay 2/9": "2/9", "giai phong mien nam": "30/4", "thong nhat": "30/4",
             "le 30/4": "30/4", "quoc te lao dong": "1/5", "le 1/5": "1/5", "gio to hung vuong": "gio to", "gio to": "gio to",
             "tet duong lich": "tet duong lich", "tet tay": "tet duong lich", "nam moi duong lich": "tet duong lich"}
    for a, h in sorted(alias.items(), key=lambda kv: -len(kv[0])):
        if re.search(r"\b" + re.escape(a) + r"\b", t) and h in names:
            m = re.search(re.escape(a) + r"(?: nam)? (20\d\d)", t)
            ds = [d for d in names[h] if (d.year == int(m.group(1)) if m else d <= asof)]
            if ds:
                d = max(ds)
                return d, d
    for h in sorted(names, key=len, reverse=True):
        if len(h) >= 5 and h in t:
            m = re.search(re.escape(h) + r"(?: nam)? (20\d\d)", t)
            ds = names[h]
            if m:
                ds = [d for d in ds if d.year == int(m.group(1))]
            else:
                ds = [d for d in ds if d <= asof]
            if ds:
                d = max(ds)
                return d, d
    return None


UNITS = ["ly", "chai", "lon", "kg", "goi", "hop", "cay", "bao", "thung", "cai", "vien", "phan", "dia", "m3", "tui",
         "cuon", "bo", "vi", "tuyp", "binh", "lit", "loc", "con", "qua", "mieng", "tam", "m2", "m", "bich", "cap", "doi",
         "suat", "to", "chen", "coc", "ve", "lo", "ong", "chiec", "hu", "keo", "cuc", "banh", "tep", "xe", "khay",
         "vien", "tan", "khoi", "bo", "manh", "soi", "cuon", "can", "thanh", "mai", "nam", "trai", "ky"]


def extract_threshold(t: str):
    t = t.replace("≥", " >= ").replace("≤", " <= ")
    m = re.search(r"(tu|tren|hon|qua|duoi|it hon|nhieu hon|tu \S+ tro len|>=|>|<=|<|it nhat|toi thieu|dat|vuot)\s*"
                  r"([\d][\d.,]*\s*(?:trieu|tr|k|nghin|ngan)?)\s*(?:dong|d\b|vnd)?\s*(tro len|tro xuong)?", t)
    if not m:
        return None
    v = _num(m.group(2).replace(" ", ""))
    if v is None:
        return None
    w = m.group(1)
    tail = m.group(3) or ""
    if tail == "tro len" or w in ("tu", "it nhat", "toi thieu", "dat", ">="):
        op = ">="
    elif tail == "tro xuong":
        op = "<="
    elif w in ("tren", "hon", "qua", "nhieu hon", "vuot", ">"):
        op = ">"
    elif w in ("duoi", "it hon", "<"):
        op = "<"
    else:
        op = ">="
    return op, v


def parse(question: str, asof: D, ctx=None, cal: str | None = None) -> Query:
    t = qfold(question)
    raw_fold = fold(question)
    q = Query(text=t)
    per, cmp_, info = parse_periods(t, asof, cal)
    q.periods, q.compare = per, cmp_
    q.state_date = info.get("state_date")
    if "months" in info:
        q.extra["months"] = info["months"]
    if "tet" in info:
        q.extra["tet"] = info["tet"]
    # k for top-k
    m = re.search(r"\btop (\d+)\b|(?<![/\d])\b(\d+) (?:mat hang|mon|san pham|hang|khach|khach hang|nguoi|nhan vien|thuoc|loai)\b", t)
    if m and int(m.group(1) or m.group(2)) <= 50:
        q.k = int(m.group(1) or m.group(2))
    # filters
    f = q.filters
    if ctx is not None:
        ctx.match_entities(t, raw_fold, q)
    if re.search(r"\bca sang\b", t):
        f.setdefault("shift_list", []).append("sang")
    if re.search(r"\bca chieu\b", t):
        f.setdefault("shift_list", []).append("chieu")
    m = re.search(r"\bsize (m|l|s)\b", t)
    if m:
        f["size"] = m.group(1).upper()
    pays = []
    for k, pat in (("cash", r"tien mat|\btm\b|tien tuoi|tien le"), ("transfer", r"chuyen khoan|\bck\b"), ("ewallet", r"vi dien tu|vi (momo|zalo ?pay|vnpay|shopee ?pay)|(tra|thanh toan|bang|qua) (bang |qua )?vi\b(?! tri)"),
                   ("cod", r"\bcod\b|\bthu ho\b"), ("debt", r"ghi no|tra cham|mua no"), ("card", r"\bquet the\b|\bthe ngan hang\b")):
        for mm in re.finditer(pat, t):
            pays.append((mm.start(), k))
    pays = [k for _, k in sorted(pays)]
    if pays:
        f["pay_list"] = list(dict.fromkeys(pays))
    chans = []
    for k, pat in (("store", r"tai quay|tai cua hang|tai cho|offline|truc tiep"), ("zalo_oa", r"\bzalo\b"),
                   ("phone", r"dien thoai|goi dien|qua dt\b")):
        for mm in re.finditer(pat, t):
            chans.append((mm.start(), k))
    chans = list(dict.fromkeys(k for _, k in sorted(chans)))
    if len(chans) == 1:
        f["channel"] = chans[0]
    elif len(chans) >= 2:
        f["channel_list"] = chans
    if re.search(r"(khong|hong|ko|chua|khong phai|khong can) (phai )?(thuoc |hang )?ke don|tru (cac |nhung )?(thuoc |hang )?ke don", t):
        f["rx"] = False
    elif re.search(r"ke don", t):
        f["rx"] = True

    th = extract_threshold(t)
    if th:
        q.threshold = th
    units = set(UNITS) | (set(ctx.units) if ctx is not None and getattr(ctx, "units", None) else set())
    m = re.search(r"(?:bao nhieu|may|so|tong( cong)?|tinh theo|cong moi mat hang tinh theo|bao nhieu tien mot|mot)\s+(" +
                  "|".join(re.escape(u) for u in sorted(units, key=len, reverse=True)) + r")\b(?! nhieu)", t)
    if m:
        q.unit = m.group(2)
    q.intent, q.output = classify(t, q)
    return q


def classify(t: str, q: Query) -> tuple[str, str]:
    pct = bool(re.search(r"phan tram|%|\bpt\b", t))
    cmpw = bool(re.search(r"so (voi|vs)|hon hay kem|thay doi|tang hay giam|tang/giam|tang giam|chenh|tang truong|tang bao nhieu|giam bao nhieu|"
                          r"nhieu hay it hon|hon .* bao nhieu|kem .* bao nhieu", t))
    out = "value"
    if pct and cmpw:
        out = "pct_change"
    elif cmpw and not pct:
        out = "diff"
    # ---- debts ----
    if re.search(r"tuoi no", t):
        return "debt_aging", "value"
    if re.search(r"(tra no|thu no|thu duoc .* no|khach tra .*no)", t):
        return ("debt_paid_new" if re.search(r"no them", t) else "debt_paid"), "value"
    if re.search(r"no them|phat sinh no|ghi no them", t):
        return "debt_new", "value"
    if re.search(r"(con no|dang no|cong no|no nhieu|tong no|so no|thieu tien|chua tra|con thieu|du no|khach no|\bno\b.*(nhat|bao nhieu))", t):
        if re.search(r"bao nhieu khach|may khach|so khach", t):
            return "debt_count", "value"
        if q.k or re.search(r"nhieu nhat|lon nhat|cao nhat", t):
            return "debt_top", "value"
        return "debt_total", "value"
    # ---- inventory / expiry ----
    if re.search(r"het han|han (su )?dung|can date|gan het han", t):
        if re.search(r"tien von|gia tri|bao nhieu tien", t):
            return "expiry_value", "value"
        if re.search(r"ngay nao|han .* ngay nao|la ngay", t):
            return "expiry_lot_date", "value"
        if re.search(r"liet ke|nhung (mat hang|thuoc)|mat hang nao|thuoc nao", t):
            return "expiry_list", "value"
        return "expiry_count", "value"
    if re.search(r"gia tri (hang )?ton|ton kho .*gia tri|tri gia ton", t):
        return "stock_value", "value"
    if re.search(r"het hang", t):
        return ("stockout_list" if re.search(r"nhung|liet ke|mat hang nao|nao", t) else "stockout_count"), "value"
    if re.search(r"\bton\b|trong kho|con (lai )?(may|bao nhieu)|con hang", t) and not re.search(r"\be\b", t):
        if re.search(r"chan .*le|(thung|hop|loc|bao|vi|thung) .*(le|\bva\b)|may .* chan", t):
            return "stock_big", "value"
        return "stock", "value"
    # ---- purchases ----
    if re.search(r"nhap .*tru .*ban|chenh .*nhap|nhap tru ban", t):
        return "purchase_minus_sales", "value"
    if re.search(r"nha cung cap", t):
        return "purchase_supplier_top", "value"
    if re.search(r"(gia nhap|nhap (vao )?(gia )?binh quan|binh quan .*nhap|nhap vao gia|nhap .*binh quan)", t):
        return "purchase_avg_price", "value"
    if re.search(r"nhap hang|phieu nhap|tien nhap|nhap vao|\bnhap\b", t):
        return "purchase_total", "value"
    # ---- price ----
    if re.search(r"tang gia|doi gia|len gia|giam gia xuong|ha gia", t) and re.search(r"\d+ ngay", t):
        return "price_effect", "pct_change" if pct else "diff"
    if re.search(r"(don )?gia (bao nhieu|la bao nhieu|ban)|voi (don )?gia|ban gia|gia ban|gia mot|bao nhieu tien mot", t) and \
            q.periods and q.periods[0][0] == q.periods[0][1]:
        return "price_on_date", "value"
    # ---- profit ----
    if re.search(r"lai rong|tru (het )?chi phi", t):
        return "net_profit", "value"
    if re.search(r"loi nhat|lai nhat|lai gop cao nhat|lai nhieu nhat", t):
        return "top_profit_item", "value"
    if re.search(r"lai gop|loi gop|tien lai|lai bao nhieu", t):
        return "gross_profit", out
    if re.search(r"dot (giao|hang)|giao .*dot|cho giao|so dot|chuyen giao", t):
        return "delivery_rounds", "value"
    # ---- orders cancel ----
    if re.search(r"\bhuy\b", t):
        if re.search(r"ti le|ty le|phan tram|%", t):
            return "cancel_rate", "value"
        return "cancel_count", "value"
    # ---- customers ----
    if re.search(r"khach .*it nhat \d+ don|khach mua (tu )?\d+ don|khach .*(>=|≥|tu) ?\d+ don|khach .*\d+ don (tro len|tro len)", t):
        return ("customers_min_orders_pct" if (re.search(r"ti le|ty le", t) or pct) else "customers_min_orders"), "value"
    if re.search(r"(bao nhieu|may|so) khach", t) and not re.search(r"\bno\b|thieu", t):
        if re.search(r"duong|o pho|o quan|dia chi|song o|nha o", t):
            return "customer_address_count", "value"
        if re.search(r"nu\b|nam\b|gioi tinh|tuoi", t):
            return "unanswerable_attr", "value"
        return "customer_count", out
    if re.search(r"khach .*(nu|nam gioi|phu nu|dan ong)|gioi tinh|do tuoi|sinh nhat", t):
        return "unanswerable_attr", "value"
    if re.search(r"ti trong|ty trong|chiem|dong gop|phan cua", t) and re.search(r"doanh thu|tien", t):
        return "share", "value"
    if re.search(r"khach|ai (la|mua|chi)|nguoi mua", t) and \
            re.search(r"nhieu (tien |don |don hang |lan |bill )?nhat|cao nhat|lon nhat|\btop\b|chi tieu nhieu|mua nhieu|nhieu tien",
                      t.replace("bao nhieu", "")):
        if re.search(r"nhieu (don|lan|bill)|so don|mua nhieu lan", t):
            return "top_customers_orders", "value"
        return "top_customers", "value"
    # ---- items ----
    if re.search(r"(bi|hang|mat hang|mon) e\b|khong ban (ra )?duoc|ban khong duoc|ban cham|ton nhieu|khong ban ra", t):
        return "unsold", "value"
    if re.search(r"(duoc mua|co mat|xuat hien) (o|trong) (it nhat )?\d+ don|\d+ don khac nhau", t):
        return "items_in_orders", "value"
    if re.search(r"ban chay|ban nhieu nhat|hot nhat|chay nhat|ban duoc nhieu nhat|ban it nhat|it chay nhat|ban e nhat", t) or \
            (re.search(r"\btop\b", t) and re.search(r"mat hang|mon|san pham|hang", t)):
        return "top_items", "value"
    # ---- shares / pay split ----
    if re.search(r"ti trong|ty trong|chiem|dong gop|phan cua|phan tram tong doanh thu|bang (bao nhieu|may) (%|phan tram) (tong|doanh thu)|(ti le|ty le) .*tren tong|tren tong doanh thu", t) or \
            (pct and re.search(r"trong (tong )?doanh thu", t) and not cmpw):
        return "share", "value"
    if len(q.filters.get("pay_list", [])) >= 2:
        return "pay_split", out
    if len(q.filters.get("channel_list", [])) >= 2:
        return "channel_split", out
    # ---- days / months ----
    if re.search(r"thang nao", t):
        return "best_month", "value"
    if re.search(r"ngay nao", t):
        return "best_day", "value"
    if re.search(r"(bao nhieu|may|so) ngay", t) and q.threshold:
        return "days_threshold", "value"
    if re.search(r"lien tuc|tang deu|giam deu", t):
        return "trend", "value"
    if q.extra.get("months") and re.search(r"moi thang|lan luot|tung thang|theo thu tu|tu thang cu", t):
        return "months_list", "value"
    # ---- aov / orders / qty / revenue ----
    if re.search(r"trung binh|binh quan", t) and re.search(r"don|bill|hoa don|lan mua", t):
        return "aov", out
    if re.search(r"(bao nhieu|may|so|dem) (don|bill)|co (tong cong )?(bao nhieu|may) don|so don", t):
        if q.threshold and re.search(r"tien|doanh thu|dong|gia tri", t):
            return "orders_threshold", "value"
        return "orders", out
    if q.unit and re.search(r"ban (ra|duoc)|so .*ban|bao nhieu|may|tong cong|so luong", t) and \
            not re.search(r"bao nhieu tien|doanh thu|tien ban|tien hang", t):
        return "qty", out
    if re.search(r"so luong|bao nhieu (san pham|mat hang)", t):
        return "qty", out
    if re.search(r"doanh thu|tien|ban duoc|thu ve|thu duoc|ban ra", t):
        return "revenue", out
    return "unknown", out
