"""Answers from canonical tables (dm.assemble) for a parsed query (dm.qparse), following the train rulebook.

Every executor returns an Answer: ("number", 123) | ("percent", 1.5) | ("date", "2026-01-02") | ("list", [...]) |
("string", "...") | ("boolean", True) | ("table", {...}) | ("unanswerable", reason) | ("abstain", why).
"""
from __future__ import annotations

import datetime as dt
import math
import re
from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import periods as P
from .assemble import pkey
from .qparse import Query
from .textnorm import fold


class Abstain(Exception):
    pass


class Unanswerable(Exception):
    pass


@dataclass
class Answer:
    type: str
    value: object = None
    why: str = ""

    def to_json(self, qid: str) -> dict:
        if self.type == "abstain":
            return {"id": qid, "type": "abstain"}
        if self.type == "unanswerable":
            return {"id": qid, "type": "unanswerable", "reason": str(self.value or self.why or "")}
        return {"id": qid, "type": self.type, "answer": self.value}


def round_half_up(x: float, nd: int = 0) -> float:
    q = 10 ** nd
    return math.floor(x * q + 0.5) / q if x >= 0 else -math.floor(-x * q + 0.5) / q


def money(x: float) -> int:
    return int(round_half_up(float(x), 0))


def pct(x: float) -> float:
    return round_half_up(float(x), 2)


def _toks(s: str) -> list[str]:
    return re.sub(r"[^a-z0-9]+", " ", fold(s)).split()


def _find_sub(hay: list[str], needle: list[str]) -> int:
    n = len(needle)
    if n == 0:
        return -1
    for i in range(len(hay) - n + 1):
        if hay[i:i + n] == needle:
            return i
    return -1


class Ctx:
    """One business: canonical tables + entity lists for matching names in questions."""

    def __init__(self, C: dict, cal_path: str | None):
        self.C = C
        self.cal = cal_path
        self.L = C.get("lines")
        self.O = C.get("orders")
        self.Pr = C.get("products")
        self.end = C.get("_data_end")
        self.start = C.get("_data_start")
        names = set()
        if self.L is not None:
            names |= set(self.L["prod_name"].unique())
        if self.Pr is not None and "prod_name" in self.Pr:
            names |= set(self.Pr["prod_name"].unique())
        self.prod_names = sorted({n for n in names if n}, key=lambda s: -len(s))
        self.prod_toks = [(n, _toks(n)) for n in self.prod_names]
        cats = set()
        if self.Pr is not None and "category" in self.Pr:
            cats |= set(self.Pr["category"].unique())
        self.categories = sorted({c for c in cats if c}, key=lambda s: -len(s))
        groups = set()
        for df in (self.O, C.get("customers")):
            if df is not None and "cust_group" in df:
                groups |= set(df["cust_group"].unique())
        self.cust_groups = sorted({g for g in groups if g}, key=lambda s: -len(s))
        ings = set()
        if self.Pr is not None and "ingredient" in self.Pr:
            ings |= set(self.Pr["ingredient"].unique())
        self.ingredients = sorted({i for i in ings if i}, key=lambda s: -len(s))
        cust = set()
        if self.O is not None and "cust_name" in self.O:
            cust |= set(self.O["cust_name"].unique())
        if C.get("customers") is not None and "cust_name" in C["customers"]:
            cust |= set(C["customers"]["cust_name"].unique())
        self.customers = sorted({c for c in cust if c and len(c) > 3}, key=lambda s: -len(s))
        us = set()
        if self.L is not None:
            us |= {fold(u) for u in self.L["unit"].unique() if u and len(u) <= 12}
        for (_k, u) in C.get("_conv", {}):
            us.add(fold(u))
        for u in C.get("_base_unit", {}).values():
            if u and len(u) <= 12:
                us.add(fold(u))
        self.units = sorted({u for u in us if u and not u.isdigit()}, key=len, reverse=True)
        staff = set()
        if self.O is not None and "staff_name" in self.O:
            staff |= set(self.O["staff_name"].unique())
        elif self.O is not None and "staff" in self.O:
            staff |= set(self.O["staff"].unique())
        self.staff = sorted({s for s in staff if s}, key=lambda s: -len(s))

    # ---------------- entity matching ----------------
    def match_entities(self, t: str, raw_fold: str, q: Query):
        qt = _toks(raw_fold)
        qt2 = _toks(t)
        used = []

        def find(cands, toks_list=None):
            best = None
            for n in cands:
                nt = _toks(n)
                if len(nt) == 0:
                    continue
                for hay in (qt, qt2):
                    i = _find_sub(hay, nt)
                    if i >= 0:
                        if best is None or len(nt) > len(best[1]):
                            best = (n, nt, i)
                        break
            return best

        # categories ("nhom hang X", "nhom X")
        m = re.search(r"nhom (hang )?(.+)", raw_fold)
        if self.categories and re.search(r"nhom|danh muc|loai", raw_fold):
            b = find(self.categories)
            if b:
                q.filters["category"] = b[0]
        if self.cust_groups and re.search(r"nhom|khach (si|le|vip|than thiet)|than thiet|khach quen", raw_fold):
            b = find(self.cust_groups)
            if b:
                q.filters["cust_group"] = b[0]
        if self.ingredients and "hoat chat" in raw_fold:
            b = find(self.ingredients)
            if b:
                q.filters["ingredient"] = b[0]
        b = find(self.prod_names)
        if b:
            q.filters["product"] = b[0]
        if self.customers and re.search(r"\bkhach\b|\bkh\b|ghi no|tra no", raw_fold):
            b = find(self.customers)
            if b and len(b[1]) >= 2:
                q.filters["customer"] = b[0]
        if self.staff and "nhan vien" in raw_fold:
            b = find(self.staff)
            if b:
                q.filters["staff"] = b[0]

    # ---------------- basic selections ----------------
    def require(self, cond: bool, why: str):
        if not cond:
            raise Unanswerable(why)

    def check_period(self, p):
        if self.start is None or self.end is None or pd.isna(self.start) or pd.isna(self.end):
            return
        lo, hi = self.start.date(), self.end.date()
        if P.overlaps(p, lo, hi) == "none":
            raise Unanswerable("kỳ hỏi nằm ngoài khoảng ngày có dữ liệu")

    def orders_in(self, p, statuses=("completed", "delivering")):
        O = self.O
        self.require(O is not None, "không có dữ liệu đơn")
        m = (O["date"] >= pd.Timestamp(p[0])) & (O["date"] <= pd.Timestamp(p[1]))
        if statuses is not None:
            m &= O["status"].isin(statuses)
        return O[m]

    def lines_in(self, p, statuses=("completed", "delivering")):
        L = self.L
        self.require(L is not None, "không có dữ liệu bán hàng")
        m = (L["date"] >= pd.Timestamp(p[0])) & (L["date"] <= pd.Timestamp(p[1]))
        if statuses is not None:
            m &= L["status"].isin(statuses)
        return L[m]

    def apply_order_filters(self, df, f):
        if "pay_list" in f and len(f["pay_list"]) == 1:
            self.require("pay" in df, "không ghi hình thức thanh toán")
            df = df[df["pay"] == f["pay_list"][0]]
        if "channel" in f:
            self.require("channel" in df, "không ghi kênh bán")
            df = df[df["channel"].map(fold) == f["channel"]]
        if "cust_group" in f:
            self.require("cust_group" in df, "không ghi nhóm khách")
            df = df[df["cust_group"] == f["cust_group"]]
        if "staff" in f:
            col = "staff_name" if "staff_name" in df and (df["staff_name"] == f["staff"]).any() else "staff"
            self.require(col in df, "không ghi nhân viên")
            df = df[df[col] == f["staff"]]
        if "shift_list" in f and len(f["shift_list"]) == 1:
            df = self._shift(df, f["shift_list"][0])
        return df

    def _shift(self, df, which):
        self.require("ts" in df and df["ts"].notna().any(), "không ghi giờ đơn")
        h = df["ts"].dt.hour
        lo, hi = P.SHIFTS[which]
        return df[(h >= lo) & (h <= hi)]

    def apply_line_filters(self, df, f):
        if "product" in f:
            pid = self.prod_id_of(f["product"])
            if pid and (df["prod_id"] == pid).any():
                df = df[df["prod_id"] == pid]
            else:
                df = df[df["pkey"] == pkey(f["product"])]
        if "category" in f:
            cat = self._prod_attr("category")
            df = df[df["prod_id"].map(cat.get("id", {})).fillna(df["pkey"].map(cat.get("name", {}))) == f["category"]]
        if "size" in f:
            df = df[df["prod_name"].str.strip().str.upper().str.endswith(f"({f['size']})")]
        if "rx" in f:
            rx = self._prod_attr("rx")
            v = df["prod_id"].map(rx.get("id", {})).fillna(df["pkey"].map(rx.get("name", {})))
            self.require(v.notna().any(), "không ghi thuốc kê đơn")
            df = df[v.fillna(False).astype(bool) == f["rx"]]
        if "ingredient" in f:
            ing = self._prod_attr("ingredient")
            v = df["prod_id"].map(ing.get("id", {})).fillna(df["pkey"].map(ing.get("name", {})))
            df = df[v == f["ingredient"]]
        return df

    def prod_id_of(self, name):
        if not hasattr(self, "_pid"):
            self._pid = {}
            src = []
            if self.Pr is not None and "prod_id" in self.Pr:
                src.append(self.Pr[["prod_id", "pkey"]])
            if self.L is not None and "prod_id" in self.L:
                src.append(self.L[["prod_id", "pkey"]].drop_duplicates())
            for d in src:
                for pid, pk in zip(d["prod_id"], d["pkey"]):
                    if pid and pk and pk not in self._pid:
                        self._pid[pk] = pid
        return self._pid.get(pkey(name))

    def _prod_attr(self, col):
        Pr = self.Pr
        if Pr is None or col not in Pr:
            raise Unanswerable(f"không có thông tin {col}")
        out = {"id": {}, "name": {}}
        for _, r in Pr.iterrows():
            v = r[col]
            if v == "" or (isinstance(v, float) and np.isnan(v)):
                continue
            if r.get("prod_id"):
                out["id"][r["prod_id"]] = v
            if r.get("pkey"):
                out["name"][r["pkey"]] = v
        return out

    def has_line_filter(self, f):
        return any(k in f for k in ("product", "category", "size", "rx", "ingredient"))

    # ---------------- metrics ----------------
    def revenue(self, p, f):
        self.check_period(p)
        if self.has_line_filter(f) or self.O is None:
            L = self.lines_in(p)
            if self.O is not None:
                L = self.apply_order_filters(L, f)
            elif any(k in f for k in ("pay_list", "channel", "cust_group", "staff")):
                raise Unanswerable("không có thông tin đơn")
            elif "shift_list" in f:
                L = self.apply_order_filters(L, f)
            L = self.apply_line_filters(L, f)
            return float(L["line_amount"].sum())
        O = self.apply_order_filters(self.orders_in(p), f)
        return float(O["revenue"].sum())

    def n_orders(self, p, f, statuses=("completed", "delivering")):
        self.check_period(p)
        self.require(self.O is not None and "order_id" in self.O, "không ghi mã đơn")
        if self.has_line_filter(f):
            L = self.apply_line_filters(self.lines_in(p, statuses), f)
            ids = set(L["order_id"])
            O = self.orders_in(p, statuses)
            O = O[O["order_id"].isin(ids)]
        else:
            O = self.orders_in(p, statuses)
        O = self.apply_order_filters(O, f)
        return int(O["order_id"].nunique())

    def qty(self, p, f, unit=None):
        self.check_period(p)
        L = self.lines_in(p)
        if self.O is not None:
            L = self.apply_order_filters(L, f)
        L = self.apply_line_filters(L, f)
        L = L[~L["is_fee"]]
        if unit and "product" not in f:
            bu = self._base_units()
            uk = re.sub(r"\s+", "", fold(unit))
            keep = L["prod_id"].map(bu["id"]).fillna(L["pkey"].map(bu["name"]))
            # products with no known base unit: the unit written on their lines when it never changes
            L = L[keep.map(lambda u: re.sub(r"\s+", "", fold(u)) if isinstance(u, str) else "") == uk]
        return float(L["qty_base"].sum())

    def _base_units(self):
        out = {"id": {}, "name": {}}
        for (kind, k), u in self.C.get("_base_unit", {}).items():
            out[kind][k] = u
        if self.L is not None:
            # a product whose lines all use one unit and has no conversion: that unit is its base unit
            g = self.L.groupby("pkey")["unit"].agg(lambda s: s.mode().iat[0] if len(s.mode()) else "")
            conv_names = {k[1] for (k, _u) in self.C.get("_conv", {}) if k[0] == "name"}
            for pk, u in g.items():
                if pk not in out["name"] and pk not in conv_names and u:
                    out["name"][pk] = u
        return out

    def daily_revenue(self, p, f):
        if self.O is None:
            L = self.apply_line_filters(self.apply_order_filters(self.lines_in(p), f), f)
            s = L.groupby("date")["line_amount"].sum()
        elif self.has_line_filter(f):
            L = self.apply_line_filters(self.lines_in(p), f)
            s = L.groupby("date")["line_amount"].sum()
        else:
            O = self.apply_order_filters(self.orders_in(p), f)
            s = O.groupby("date")["revenue"].sum()
        idx = pd.date_range(pd.Timestamp(p[0]), pd.Timestamp(p[1]), freq="D")
        lo = max(pd.Timestamp(p[0]), self.start) if self.start is not None else pd.Timestamp(p[0])
        hi = min(pd.Timestamp(p[1]), self.end) if self.end is not None else pd.Timestamp(p[1])
        idx = idx[(idx >= lo) & (idx <= hi)]
        return s.reindex(idx, fill_value=0.0)

    def metric(self, name, p, f, q):
        if name == "revenue":
            return self.revenue(p, f)
        if name == "orders":
            return self.n_orders(p, f)
        if name == "qty":
            return self.qty(p, f, q.unit)
        if name == "aov":
            n = self.n_orders(p, f)
            if n == 0:
                raise Unanswerable("không có đơn")
            return self.revenue(p, f) / n
        if name == "customer_count":
            return self.customer_count(p, f)
        if name == "gross_profit":
            return self.gross_profit(p, f)
        raise Abstain(f"metric {name}")

    def customer_key(self, O):
        if "cust_id" in O and (O["cust_id"] != "").any():
            return O["cust_id"].where(O["cust_id"] != "", None)
        self.require("cust_name" in O, "không ghi khách")
        nm = O["cust_name"].map(lambda s: fold(s))
        walk = nm.isin(["", "khach le", "le", "khach vang lai", "vang lai", "khach", "kl", "k l", "k.l", "-", "khong ten",
                        "khach ghe", "khach qua duong", "guest", "walk in", "walk-in"])
        return nm.where(~walk, None)

    def customer_count(self, p, f):
        O = self.apply_order_filters(self.orders_in(p), f)
        k = self.customer_key(O)
        return int(k.dropna().nunique())

    def gross_profit(self, p, f):
        L = self.lines_in(p)
        if self.O is not None:
            L = self.apply_order_filters(L, f)
        L = self.apply_line_filters(L, f)
        self.require("cost_unit" in L and L["cost_unit"].notna().any(), "không có giá vốn")
        return float((L["line_amount"] - L["qty_num"] * L["cost_unit"]).sum())


def _per(q: Query, asof):
    if not q.periods:
        raise Abstain("không hiểu kỳ")
    return q.periods[0]


def answer(q: Query, ctx: Ctx, asof: dt.date) -> Answer:
    try:
        return _answer(q, ctx, asof)
    except Unanswerable as e:
        return Answer("unanswerable", str(e))
    except Abstain as e:
        return Answer("abstain", why=str(e))


def _cmp_period(q: Query, p):
    c = q.compare
    if c is None:
        return None
    if c == "prev":
        a, b = p
        if a.day == 1 and (b + dt.timedelta(days=1)).day == 1 and (b - a).days >= 27:
            y, m = P.shift_month(a.year, a.month, -1)
            return P.month(m, y)
        if (b - a).days == 6 and a.weekday() == 0:
            return a - dt.timedelta(days=7), b - dt.timedelta(days=7)
        if a.month in (1, 4, 7, 10) and a.day == 1 and (b - a).days > 80:
            y, m = P.shift_month(a.year, a.month, -3)
            return P.quarter((m - 1) // 3 + 1, y)
        return P.previous_period(p)
    if c == "yoy":
        return P.same_period_last_year(p)
    return c


def _value_type(intent: str, q: Query):
    return "number"


def _answer(q: Query, ctx: Ctx, asof: dt.date) -> Answer:
    it = q.intent
    f = q.filters
    if it in ("unknown",):
        raise Abstain("không hiểu câu hỏi")
    if it == "unanswerable_attr":
        raise Unanswerable("dữ liệu không ghi thông tin này")
    if it in ("revenue", "orders", "qty", "aov", "customer_count", "gross_profit"):
        # two shifts compared ("ca chiều so với ca sáng")
        if len(f.get("shift_list", [])) == 2 and q.output in ("pct_change", "diff"):
            p = _per(q, asof)
            a = dict(f, shift_list=[f["shift_list"][0]])
            b = dict(f, shift_list=[f["shift_list"][1]])
            # "ca chiều so với ca sáng: mốc là ca sáng"
            if f["shift_list"][0] == "sang":
                a, b = b, a
            va, vb = ctx.metric(it, p, a, q), ctx.metric(it, p, b, q)
            return _cmp_out(q, it, va, vb)
        p = _per(q, asof)
        if q.output in ("pct_change", "diff"):
            pc = _cmp_period(q, p) if q.compare else (q.periods[1] if len(q.periods) > 1 else None)
            if pc is None:
                raise Abstain("không rõ kỳ so")
            if len(q.periods) > 1 and q.compare is None:
                p, pc = q.periods[0], q.periods[1]
            ctx.check_period(pc)
            va, vb = ctx.metric(it, p, f, q), ctx.metric(it, pc, f, q)
            return _cmp_out(q, it, va, vb)
        v = ctx.metric(it, p, f, q)
        return _fmt(it, v)
    if it == "cancel_count":
        p = _per(q, asof)
        ctx.check_period(p)
        O = ctx.apply_order_filters(ctx.orders_in(p, statuses=None), f)
        return Answer("number", int((O["status"] == "cancelled").sum()))
    if it == "cancel_rate":
        p = _per(q, asof)
        ctx.check_period(p)
        O = ctx.apply_order_filters(ctx.orders_in(p, statuses=None), f)
        if len(O) == 0:
            raise Unanswerable("không có đơn")
        return Answer("percent", pct(100.0 * (O["status"] == "cancelled").sum() / len(O)))
    if it == "best_day":
        p = _per(q, asof)
        ctx.check_period(p)
        s = ctx.daily_revenue(p, f)
        if len(s) == 0:
            raise Unanswerable("không có dữ liệu")
        low = bool(re.search(r"thap nhat|it nhat|ban it nhat|e nhat", q.text))
        v = s.min() if low else s.max()
        days = s[s == v].index
        return Answer("date", days[0].strftime("%Y-%m-%d"))
    if it == "best_month":
        months = q.extra.get("months") or []
        if not months:
            raise Abstain("không rõ các tháng")
        vals = [(ctx.revenue(P.month(m, y), f), (y, m)) for y, m in months]
        low = bool(re.search(r"thap nhat|it nhat", q.text))
        best = min(vals) if low else max(vals, key=lambda x: x[0])
        return Answer("date", f"{best[1][0]:04d}-{best[1][1]:02d}")
    if it == "months_list":
        months = q.extra.get("months") or []
        metric = "orders" if re.search(r"(bao nhieu|so) don", q.text) else "revenue"
        vals = [ctx.metric(metric, P.month(m, y), f, q) for y, m in months]
        return Answer("list", [money(v) for v in vals])
    if it == "trend":
        months = q.extra.get("months") or []
        if len(months) < 2:
            raise Abstain("không rõ các tháng")
        vals = [ctx.revenue(P.month(m, y), f) for y, m in months]
        down = bool(re.search(r"giam lien tuc|giam deu", q.text))
        ok = all((b < a) if down else (b > a) for a, b in zip(vals, vals[1:]))
        return Answer("boolean", bool(ok))
    if it == "days_threshold":
        p = _per(q, asof)
        ctx.check_period(p)
        s = ctx.daily_revenue(p, f)
        return Answer("number", int(_cmp_op(s, q.threshold).sum()))
    if it == "orders_threshold":
        p = _per(q, asof)
        ctx.check_period(p)
        O = ctx.apply_order_filters(ctx.orders_in(p), f)
        return Answer("number", int(_cmp_op(O["revenue"], q.threshold).sum()))
    if it == "share":
        p = _per(q, asof)
        ctx.check_period(p)
        num_f = dict(f)
        if not any(k in num_f for k in ("category", "cust_group", "pay_list", "product", "rx", "channel", "ingredient",
                                         "size", "staff")):
            raise Abstain("không rõ phần tử số")
        total = ctx.revenue(p, {})
        if total == 0:
            raise Unanswerable("không có doanh thu")
        return Answer("percent", pct(100.0 * ctx.revenue(p, num_f) / total))
    if it == "pay_split":
        p = _per(q, asof)
        ctx.check_period(p)
        vals = [ctx.revenue(p, dict(f, pay_list=[k])) for k in f["pay_list"]]
        return Answer("list", [money(v) for v in vals])
    if it == "channel_split":
        p = _per(q, asof)
        ctx.check_period(p)
        vals = [ctx.revenue(p, dict({k: v for k, v in f.items() if k != "channel_list"}, channel=k)) for k in f["channel_list"]]
        return Answer("list", [money(v) for v in vals])
    if it == "top_items":
        p = _per(q, asof)
        ctx.check_period(p)
        L = ctx.lines_in(p)
        if ctx.O is not None:
            L = ctx.apply_order_filters(L, f)
        L = ctx.apply_line_filters(L, {k: v for k, v in f.items() if k != "product"})
        L = L[~L["is_fee"]]
        by_money = bool(re.search(r"doanh thu|nhieu tien|tien nhat", q.text))
        gk = L["prod_id"].where(L["prod_id"] != "", L["pkey"])
        g = L.assign(_g=gk).groupby("_g").agg(v=("line_amount" if by_money else "qty_base", "sum"),
                                               name=("prod_name", lambda s: s.mode().iat[0]), pid=("prod_id", "first"))
        low = bool(re.search(r"it nhat|cham nhat|e nhat|thap nhat", q.text))
        g = g.assign(code=g["pid"].where(g["pid"] != "", g["name"]))
        g = g.sort_values(["v", "code"], ascending=[low, True])
        k = q.k or 1
        names = list(g["name"].head(k))
        if q.k and q.k > 1:
            return Answer("list", names)
        if not names:
            raise Unanswerable("không có hàng bán")
        return Answer("string", names[0])
    if it in ("top_customers", "top_customers_orders"):
        p = _per(q, asof)
        ctx.check_period(p)
        O = ctx.apply_order_filters(ctx.orders_in(p), f)
        key = ctx.customer_key(O)
        O = O.assign(_k=key).dropna(subset=["_k"])
        if len(O) == 0:
            raise Unanswerable("không có khách")
        if it == "top_customers_orders":
            g = O.groupby("_k").agg(v=("order_id", "nunique"), name=("cust_name", "first"))
        else:
            g = O.groupby("_k").agg(v=("revenue", "sum"), name=("cust_name", "first"))
        g = g.reset_index().sort_values(["v", "_k"], ascending=[False, True])
        names = list(g["name"].head(q.k or 1))
        if q.k and q.k > 1:
            return Answer("list", names)
        return Answer("string", names[0])
    if it in ("customers_min_orders", "customers_min_orders_pct"):
        p = _per(q, asof)
        ctx.check_period(p)
        m = re.search(r"it nhat (\d+) don|tu (\d+) don|(?:>=|≥) ?(\d+) don", q.text)
        n = int(m.group(1) or m.group(2) or m.group(3)) if m else (int(q.threshold[1]) if q.threshold else None)
        if n is None:
            raise Abstain("không rõ số đơn")
        O = ctx.apply_order_filters(ctx.orders_in(p), f)
        key = ctx.customer_key(O)
        cnt = O.assign(_k=key).dropna(subset=["_k"]).groupby("_k")["order_id"].nunique()
        hit = int((cnt >= n).sum())
        if it == "customers_min_orders":
            return Answer("number", hit)
        if len(cnt) == 0:
            raise Unanswerable("không có khách")
        return Answer("percent", pct(100.0 * hit / len(cnt)))
    if it == "items_in_orders":
        p = _per(q, asof)
        ctx.check_period(p)
        m = re.search(r"(\d+) don", q.text)
        n = int(m.group(1))
        L = ctx.lines_in(p)
        L = L[~L["is_fee"]]
        c = L.groupby("pkey")["order_id"].nunique()
        return Answer("number", int((c >= n).sum()))
    if it == "unsold":
        p = _per(q, asof)
        ctx.check_period(p)
        Lall = ctx.L[ctx.L["status"].isin(("completed", "delivering")) & ~ctx.L["is_fee"]]
        before = set(Lall[Lall["date"] < pd.Timestamp(p[0])]["pkey"])
        during = set(Lall[(Lall["date"] >= pd.Timestamp(p[0])) & (Lall["date"] <= pd.Timestamp(p[1]))]["pkey"])
        items = sorted(before - during)
        if re.search(r"liet ke|nhung (mat hang|mon)|mat hang nao|mon nao|la gi", q.text):
            names = Lall.drop_duplicates("pkey").set_index("pkey")
            codes = [(names.loc[k, "prod_id"] or names.loc[k, "prod_name"], names.loc[k, "prod_name"]) for k in items]
            return Answer("list", [n for _, n in sorted(codes)])
        return Answer("number", len(items))
    if it == "price_on_date":
        p = _per(q, asof)
        self_L = ctx.L
        ctx.require(self_L is not None, "không có dữ liệu bán")
        if "product" not in f:
            raise Abstain("không rõ mặt hàng")
        L = ctx.apply_line_filters(self_L[self_L["date"] == pd.Timestamp(p[0])], {"product": f["product"]})
        if len(L) == 0:
            raise Unanswerable("không có dòng bán ngày đó")
        fac = L["factor"].fillna(1.0)
        up = (L["unit_price"] / fac).round(2)
        return Answer("number", money(up.mode().iat[0]))
    if it == "price_effect":
        m = re.search(r"(\d+) ngay", q.text)
        dm = re.findall(r"(\d{1,2})/(\d{1,2})/(20\d\d)", q.text)
        if not m or not dm or "product" not in f:
            raise Abstain("không đủ thông tin")
        n = int(m.group(1))
        d0 = dt.date(int(dm[0][2]), int(dm[0][1]), int(dm[0][0]))
        after = (d0, d0 + dt.timedelta(days=n - 1))
        before = (d0 - dt.timedelta(days=n), d0 - dt.timedelta(days=1))
        va = ctx.qty(after, {"product": f["product"]})
        vb = ctx.qty(before, {"product": f["product"]})
        if vb == 0:
            raise Unanswerable("không có số bán kỳ trước")
        return Answer("percent", pct(100.0 * (va - vb) / vb))
    if it.startswith("purchase") or it.startswith("stock") or it.startswith("debt") or it in (
            "delivery_rounds", "stockout_count", "stockout_list", "net_profit", "top_profit_item"):
        from .engine2 import answer2
        return answer2(q, ctx, asof)
    raise Abstain(f"chưa làm intent {it}")


def _cmp_op(s, th):
    op, v = th
    return {"<": s < v, "<=": s <= v, ">": s > v, ">=": s >= v}[op]


def _fmt(it, v):
    if it in ("orders", "customer_count"):
        return Answer("number", int(v))
    if it == "qty":
        return Answer("number", int(round(v)) if abs(v - round(v)) < 1e-6 else round_half_up(v, 2))
    return Answer("number", money(v))


def _cmp_out(q, it, va, vb):
    if q.output == "pct_change":
        if vb == 0:
            raise Unanswerable("kỳ so bằng 0")
        return Answer("percent", pct(100.0 * (va - vb) / vb))
    d = va - vb
    return _fmt(it, d)
