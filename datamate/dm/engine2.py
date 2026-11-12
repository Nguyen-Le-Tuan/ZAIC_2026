"""Purchases, inventory, debts, deliveries, profit (rulebook §4, §5)."""
from __future__ import annotations

import datetime as dt
import re

import numpy as np
import pandas as pd

from . import periods as P
from .assemble import canon_pay, pkey, ukey
from .engine import Abstain, Answer, Ctx, Unanswerable, money, pct, round_half_up
from .qparse import Query
from .textnorm import fold

VALID = ("completed", "delivering")


def _ts(d):
    return pd.Timestamp(d)


def _state_date(q: Query, asof):
    if q.state_date:
        return q.state_date
    if q.periods and q.periods[0][0] == q.periods[0][1]:
        return q.periods[0][1]
    return asof


# ---------------- purchases ----------------
def _po_lines(ctx: Ctx):
    PL = ctx.C.get("purchases")
    if PL is None:
        raise Unanswerable("không có dữ liệu nhập hàng")
    PL = PL.copy()
    if "cancelled" not in PL:
        PL["cancelled"] = False
    PL["cancelled"] = PL["cancelled"].fillna(False).astype(bool)
    conv = ctx.C.get("_conv", {})
    bu = ctx.C.get("_base_unit", {})
    facs = []
    for pid, pk, u in zip(PL.get("prod_id", [""] * len(PL)), PL["pkey"], PL["unit"]):
        uk = ukey(u)
        f = None
        for k in ((("id", pid),) if pid else ()) + ((("name", pk),) if pk else ()):
            if (k, uk) in conv:
                f = conv[(k, uk)]
                break
            if k in bu and ukey(bu[k]) == uk:
                f = 1.0
                break
        facs.append(f if f is not None else 1.0)
    PL["factor"] = facs
    qb = PL["qty_base_given"] if "qty_base_given" in PL else pd.Series(np.nan, index=PL.index)
    PL["qty_base"] = qb.where(qb.notna(), PL["qty_num"] * PL["factor"])
    return PL


def purchase_total(ctx: Ctx, p):
    H = ctx.C.get("po_headers")
    if H is not None and "total" in H and H["total"].notna().any():
        h = H[(H["date"] >= _ts(p[0])) & (H["date"] <= _ts(p[1])) & ~H["cancelled"].astype(bool)]
        return float(h["total"].sum())
    PL = _po_lines(ctx)
    PL = PL[(PL["date"] >= _ts(p[0])) & (PL["date"] <= _ts(p[1])) & ~PL["cancelled"]]
    return float(PL["amount"].sum())


def purchase_avg_price(ctx: Ctx, p, product, unit):
    PL = _po_lines(ctx)
    pid = ctx.prod_id_of(product)
    sel = (PL["prod_id"] == pid) if pid and (PL["prod_id"] == pid).any() else (PL["pkey"] == pkey(product))
    PL = PL[sel & (PL["date"] >= _ts(p[0])) & (PL["date"] <= _ts(p[1])) & ~PL["cancelled"]]
    if len(PL) == 0:
        raise Unanswerable("không có phiếu nhập mặt hàng này trong kỳ")
    cost = PL["unit_cost"].where(PL["unit_cost"].notna(), PL["amount"] / PL["qty_num"])
    # per purchase unit; convert when the question asks another unit of the product
    if unit and PL["unit"].map(fold).nunique() == 1 and fold(PL["unit"].iat[0]) != fold(unit):
        f_line = PL["factor"].iat[0]
        conv = ctx.C.get("_conv", {})
        target = None
        for k in ((("id", pid),) if pid else ()) + ((("name", pkey(product)),)):
            if (k, ukey(unit)) in conv:
                target = conv[(k, ukey(unit))]
                break
            bu = ctx.C.get("_base_unit", {}).get(k)
            if bu and ukey(bu) == ukey(unit):
                target = 1.0
                break
        if target:
            per_base = (cost * PL["qty_num"]).sum() / (PL["qty_num"] * f_line).sum()
            return per_base * target
    return float((cost * PL["qty_num"]).sum() / PL["qty_num"].sum())


# ---------------- inventory ----------------
def _sales_base(ctx: Ctx):
    L = ctx.L
    if L is None:
        return None
    L = L[L["status"].isin(VALID) & ~L["is_fee"]]
    key = L["prod_id"].where(L["prod_id"] != "", L["pkey"])
    return pd.DataFrame({"k": key, "date": L["date"], "q": L["qty_base"]})


def _prod_key(ctx, product):
    pid = ctx.prod_id_of(product)
    return pid if pid else pkey(product)


def stock_at(ctx: Ctx, product, d: dt.date):
    """Stock (base units) of a product at the end of day d."""
    mv = ctx.C.get("moves")
    k = _prod_key(ctx, product)
    if mv is not None and "stock" in mv and mv["stock"].notna().any():
        m = mv[(mv.get("prod_id", "") == k) if "prod_id" in mv else (mv["prod_name"].map(pkey) == k)]
        m = m[m["ts"] <= _ts(d) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)]
        if len(m) == 0:
            return 0.0
        return float(m.sort_values(["ts"]).iloc[-1]["stock"])
    st = ctx.C.get("stock")
    if st is None or "stock" not in st:
        raise Unanswerable("không có dữ liệu tồn kho")
    st = st.copy()
    st["k"] = st["prod_id"] if "prod_id" in st else st["prod_name"].map(pkey)
    if "prod_id" in st:
        st["k"] = st["prod_id"].where(st["prod_id"] != "", st.get("prod_name", pd.Series("", index=st.index)).map(pkey))
    row = st[st["k"] == k]
    if len(row) == 0 and "prod_name" in st:
        row = st[st["prod_name"].map(pkey) == pkey(product)]
    if len(row) == 0:
        raise Unanswerable("mặt hàng không có trong báo cáo tồn")
    end_stock = float(pd.to_numeric(row["stock"].map(_n), errors="coerce").iat[0])
    end = ctx.end.date() if ctx.end is not None else d
    # undo movements after day d: add back sales, take away purchases
    sb = _sales_base(ctx)
    after_sales = 0.0
    if sb is not None:
        kk = sb["k"] == k
        if not kk.any():
            kk = sb["k"] == pkey(product)
        after_sales = float(sb[kk & (sb["date"] > _ts(d)) & (sb["date"] <= _ts(end))]["q"].sum())
    after_po = 0.0
    if ctx.C.get("purchases") is not None:
        PL = _po_lines(ctx)
        kk = (PL["prod_id"] == k) if (PL["prod_id"] == k).any() else (PL["pkey"] == pkey(product))
        after_po = float(PL[kk & ~PL["cancelled"] & (PL["date"] > _ts(d)) & (PL["date"] <= _ts(end))]["qty_base"].sum())
    return end_stock + after_sales - after_po


def _n(v):
    from .values import parse_number
    return parse_number(v) if not isinstance(v, (int, float)) else v


def _factor(ctx, product, unit):
    pid = ctx.prod_id_of(product)
    conv = ctx.C.get("_conv", {})
    for k in ((("id", pid),) if pid else ()) + ((("name", pkey(product)),)):
        if (k, ukey(unit)) in conv:
            return conv[(k, ukey(unit))]
        bu = ctx.C.get("_base_unit", {}).get(k)
        if bu and ukey(bu) == ukey(unit):
            return 1.0
    return None


def _big_unit(ctx, product):
    pid = ctx.prod_id_of(product)
    conv = ctx.C.get("_conv", {})
    best = None
    for (k, u), f in conv.items():
        if k in ((("id", pid),) if pid else ()) + ((("name", pkey(product)),)):
            if best is None or f > best[1]:
                best = (u, f)
    return best


# ---------------- debts ----------------
def _debt_orders(ctx: Ctx):
    O = ctx.O
    if O is None or "order_total" not in O:
        raise Unanswerable("không có dữ liệu công nợ")
    O = O[O["status"] != "cancelled"].copy()
    if "pay" in O:
        O = O[~O["pay"].isin(["cod"])]
    if "channel" in O:
        O = O[~O["channel"].map(fold).str.contains(r"shopee|lazada|tiki|san|tmdt|marketplace", regex=True)]
    return O


def _payments(ctx: Ctx):
    Pm = ctx.C.get("payments")
    if Pm is None or "amount" not in Pm:
        return None
    return Pm[Pm["amount"].notna()]


def debt_by_order(ctx: Ctx, d: dt.date):
    O = _debt_orders(ctx)
    O = O[O["date"] <= _ts(d)]
    Pm = _payments(ctx)
    if Pm is not None:
        paid = Pm[Pm["ts"].dt.normalize() <= _ts(d)].groupby("order_id")["amount"].sum()
        owed = O["order_total"] - O["order_id"].map(paid).fillna(0.0)
    elif "remaining" in O and (ctx.end is None or _ts(d) >= ctx.end.normalize()):
        owed = O["remaining"].fillna(0.0)
    else:
        raise Abstain("không có lịch sử trả nợ theo ngày")
    O = O.assign(owed=owed)
    return O[O["owed"] > 0.5]


def answer2(q: Query, ctx: Ctx, asof: dt.date) -> Answer:
    it, f = q.intent, q.filters
    t = q.text
    if it == "purchase_total":
        if not q.periods:
            raise Abstain("không rõ kỳ")
        p = q.periods[0]
        ctx.check_period(p)
        return Answer("number", money(purchase_total(ctx, p)))
    if it == "purchase_avg_price":
        if not q.periods or "product" not in f:
            raise Abstain("không rõ kỳ hay mặt hàng")
        return Answer("number", money(purchase_avg_price(ctx, q.periods[0], f["product"], q.unit)))
    if it == "purchase_supplier_top":
        if not q.periods:
            raise Abstain("không rõ kỳ")
        p = q.periods[0]
        H = ctx.C.get("po_headers")
        if H is None or ("supplier" not in H and "supplier_id" not in H):
            raise Unanswerable("không ghi nhà cung cấp")
        h = H[(H["date"] >= _ts(p[0])) & (H["date"] <= _ts(p[1])) & ~H["cancelled"].astype(bool)]
        col = "supplier" if "supplier" in h else "supplier_id"
        g = h.groupby(col)["total"].sum().sort_values(ascending=False)
        if len(g) == 0:
            raise Unanswerable("không có phiếu nhập")
        name = g.index[0]
        return Answer("string", name)
    if it in ("stock", "stock_big"):
        if "product" not in f:
            raise Abstain("không rõ mặt hàng")
        d = _state_date(q, asof)
        v = stock_at(ctx, f["product"], d)
        if it == "stock_big":
            bu = _big_unit(ctx, f["product"])
            if not bu:
                raise Abstain("không rõ đơn vị lớn")
            whole = int(v // bu[1])
            return Answer("list", [whole, int(round(v - whole * bu[1]))])
        if q.unit:
            fac = _factor(ctx, f["product"], q.unit)
            if fac and fac != 1.0:
                v = v / fac
        return Answer("number", int(round(v)) if abs(v - round(v)) < 1e-6 else round_half_up(v, 2))
    if it == "stock_value":
        d = _state_date(q, asof)
        Pr = ctx.Pr
        if Pr is None or "cost" not in Pr:
            raise Unanswerable("không có giá vốn trong danh mục")
        tot = 0.0
        for _, r in Pr.iterrows():
            name = r.get("prod_name", "")
            if not name or not isinstance(r.get("cost"), float) or np.isnan(r["cost"]):
                continue
            try:
                s = stock_at(ctx, name, d)
            except Unanswerable:
                continue
            if s > 0:
                tot += s * r["cost"]
        return Answer("number", money(tot))
    if it in ("stockout_count", "stockout_list"):
        d = _state_date(q, asof)
        Pr = ctx.Pr
        if Pr is None:
            raise Unanswerable("không có danh mục hàng")
        names = []
        for _, r in Pr.iterrows():
            name = r.get("prod_name", "")
            if not name:
                continue
            try:
                s = stock_at(ctx, name, d)
            except Unanswerable:
                continue
            if abs(s) < 1e-9:
                names.append((r.get("prod_id") or name, name))
        if it == "stockout_count":
            return Answer("number", len(names))
        return Answer("list", [n for _, n in sorted(names)])
    if it.startswith("debt"):
        d = _state_date(q, asof)
        if it == "debt_total":
            O = debt_by_order(ctx, d)
            m = re.search(r"(?:qua|hon|tren) (\d+) ngay", t)
            if m:
                age = (_ts(d) - O["date"]).dt.days
                O = O[age > int(m.group(1))]
            return Answer("number", money(O["owed"].sum()))
        if it == "debt_aging":
            O = debt_by_order(ctx, d)
            age = (_ts(d) - O["date"]).dt.days
            b = [O[(age >= 0) & (age <= 7)]["owed"].sum(), O[(age >= 8) & (age <= 15)]["owed"].sum(), O[age > 15]["owed"].sum()]
            return Answer("list", [money(x) for x in b])
        if it in ("debt_count", "debt_top"):
            O = debt_by_order(ctx, d)
            key = ctx.customer_key(O)
            O = O.assign(_k=key).dropna(subset=["_k"])
            g = O.groupby("_k").agg(owed=("owed", "sum"), name=("cust_name", "first")).reset_index()
            if it == "debt_count":
                return Answer("number", int((g["owed"] > 0.5).sum()))
            g = g.sort_values(["owed", "_k"], ascending=[False, True]).head(q.k or 1)
            return Answer("table", {"columns": ["khach_hang", "so_tien_no"],
                                    "rows": [[n, money(v)] for n, v in zip(g["name"], g["owed"])]})
        if it in ("debt_paid", "debt_new", "debt_paid_new"):
            if not q.periods:
                raise Abstain("không rõ kỳ")
            p = q.periods[0]
            O = _debt_orders(ctx)
            if "pay" not in O:
                raise Unanswerable("không ghi hình thức thanh toán")
            O = O[O["pay"] == "debt"]
            Pm = _payments(ctx)
            if Pm is None:
                raise Unanswerable("không có lịch sử trả tiền")
            Pm = Pm.merge(O[["order_id", "date"]], on="order_id", how="inner")
            later = Pm[Pm["ts"].dt.normalize() > Pm["date"]]
            if "customer" in f:
                pass
            paid = later[(later["ts"].dt.normalize() >= _ts(p[0])) & (later["ts"].dt.normalize() <= _ts(p[1]))]["amount"].sum()
            inper = O[(O["date"] >= _ts(p[0])) & (O["date"] <= _ts(p[1]))]
            same = Pm[Pm["ts"].dt.normalize() == Pm["date"]].groupby("order_id")["amount"].sum()
            new = (inper["order_total"] - inper["order_id"].map(same).fillna(0.0)).clip(lower=0).sum()
            if it == "debt_paid":
                return Answer("number", money(paid))
            if it == "debt_new":
                return Answer("number", money(new))
            return Answer("list", [money(new), money(paid)])
    if it == "delivery_rounds":
        if not q.periods:
            raise Abstain("không rõ kỳ")
        p = q.periods[0]
        dv = ctx.C.get("deliveries")
        if dv is None:
            raise Unanswerable("không có dữ liệu giao hàng")
        dd = dv[(dv["date"] >= _ts(p[0])) & (dv["date"] <= _ts(p[1]))]
        cols = [c for c in ("order_id", "deliv_round") if c in dd]
        return Answer("number", int(dd.drop_duplicates(subset=cols + ["date"] if "deliv_round" not in dd else cols).shape[0]))
    raise Abstain(f"chưa làm intent {it}")
