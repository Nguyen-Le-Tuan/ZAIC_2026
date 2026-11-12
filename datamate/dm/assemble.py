"""Typed canonical tables of a business (dm.canon.Business -> dict of DataFrames).

lines:   one row per sold line: order_id, prod_id, prod_name, pkey, qty, unit, qty_base, factor, unit_price,
         line_discount, line_amount, cost_unit, + order fields (order_date, ts, status, cust_*, pay_method, ...)
orders:  one row per order: order_id, date, ts, status, cust_id, cust_name, cust_group, pay_method, channel, staff,
         branch, shift_id, order_gross, order_discount, order_total, ship_fee, vat, paid, remaining, due_*,
         revenue (sum of line amounts), n_items
products, conversions (pkey, ukey -> factor), customers, payments, purchases, po_headers, lots, lot_sales,
price_hist, returns, deliveries, moves, stock.
Statuses: completed | cancelled | returned | delivering ('' -> taken from the first line of the order, rulebook §8).
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from .canon import Business
from .textnorm import fold
from .values import parse_datetime, parse_number, parse_qty, to_datetime_series, to_number_series

STATUS_WORDS = [
    ("cancelled", r"huy|cancel|khong giao duoc|that bai|failed"),
    ("returned", r"tra hang|tra lai|tra ve|hoan tra|hoan hang|doi tra|return|refund"),
    ("delivering", r"dang (giao|gui|van chuyen|xu ly|ship)|shipping|delivering|pending|cho giao"),
    ("completed", r"xong|hoan thanh|thanh cong|da lay|da giao|^ok$|completed|done|success|hoan tat|da thanh toan|da nhan"),
]
PAY_WORDS = [
    ("cod", r"\bcod\b|thu ho|giao hang thu tien"),
    ("debt", r"no\b|debt|cong no|ghi no|tra sau"),
    ("ewallet", r"vi\b|ewallet|e-wallet|momo|zalo ?pay|vnpay|shopeepay"),
    ("transfer", r"chuyen khoan|transfer|bank|ck\b|ngan hang"),
    ("card", r"\bthe\b|card|pos|quet the"),
    ("cash", r"tien mat|cash|\btm\b"),
]


def canon_status(v) -> str:
    s = fold(v)
    if not s:
        return ""
    for k, pat in STATUS_WORDS:
        if re.search(pat, s):
            return k
    return "unknown:" + s


def canon_pay(v) -> str:
    s = fold(v)
    if not s:
        return ""
    for k, pat in PAY_WORDS:
        if re.search(pat, s):
            return k
    return "other:" + s


def pkey(name) -> str:
    return re.sub(r"\s+", " ", fold(name)).strip()


def ukey(u) -> str:
    return re.sub(r"\s+", "", fold(u))


def _frame(b: Business, role: str) -> list[pd.DataFrame]:
    out = []
    for mt in b.tables.values():
        if mt.role != role:
            continue
        df = pd.DataFrame({f: mt.raw.df[c] for c, f in mt.fields.items() if "__" not in f})
        df["_src"] = mt.raw.df["_src"]
        df["_year"] = mt.raw.df["_year"]
        df["_tbl"] = mt.name
        df["_row"] = np.arange(len(df))
        out.append(df)
    return out


def _num(df, col):
    return to_number_series(df[col]) if col in df else pd.Series(np.nan, index=df.index)


def _year_hint(df):
    return pd.to_numeric(df["_year"], errors="coerce").astype("Int64").astype(object).where(df["_year"] != "", None)


def _dates(df, col):
    if col not in df:
        return pd.Series(pd.NaT, index=df.index)
    return to_datetime_series(df[col], _year_hint(df))


def _ffill_groups(df: pd.DataFrame, key: str, cols: list[str]) -> pd.DataFrame:
    """Rulebook §8: an empty cell in later rows of the same order takes the value of the order's first row."""
    if key not in df:
        return df
    for c in cols:
        if c in df:
            s = df[c].replace("", np.nan)
            df[c] = s.groupby(df[key]).transform("first").fillna("")
    return df


ORDER_LEVEL = ["order_date", "order_ts", "order_time", "status", "cust_id", "cust_name", "cust_group", "pay_method",
               "channel", "staff", "branch", "note", "shift_id"]


def build(b: Business) -> dict:
    C: dict[str, pd.DataFrame] = {}
    notes = b.notes

    # ---------------- products, conversions ----------------
    prods = []
    for df in _frame(b, "products") + _frame(b, "stock") + _frame(b, "drug_info"):
        prods.append(df)
    P = pd.DataFrame(columns=["prod_id", "prod_name"])
    if prods:
        # merge by prod_id where available, else by name
        base = None
        for df in prods:
            keep = [c for c in df.columns if not c.startswith("_")]
            df = df[keep].copy()
            if base is None:
                base = df
                continue
            on = "prod_id" if ("prod_id" in df and "prod_id" in base and (df["prod_id"] != "").any()) else \
                ("prod_name" if "prod_name" in df and "prod_name" in base else None)
            if on is None:
                continue
            if on == "prod_name":
                df = df.assign(_k=df["prod_name"].map(pkey))
                base = base.assign(_k=base["prod_name"].map(pkey))
                on = "_k"
            extra = [c for c in df.columns if c not in base.columns or c == on]
            base = base.merge(df[extra], on=on, how="outer")
            base = base.drop(columns=[c for c in ("_k",) if c in base])
        P = base.fillna("")
    if "prod_name" not in P:
        P["prod_name"] = ""
    if "prod_id" not in P:
        P["prod_id"] = ""
    P["pkey"] = P["prod_name"].map(pkey)
    for c in ("list_price", "cost", "stock"):
        if c in P:
            P[c] = to_number_series(P[c])
    if "rx" in P:
        P["rx"] = P["rx"].map(lambda v: fold(v) in ("true", "1", "co", "yes", "x", "ke don", "thuoc ke don", "kedon"))
    C["products"] = P

    conv = {}
    base_unit = {}
    for df in _frame(b, "conversions"):
        for _, r in df.iterrows():
            f = parse_number(r.get("conv_factor"))
            u = ukey(r.get("conv_unit", ""))
            keys = []
            if r.get("prod_id"):
                keys.append(("id", r["prod_id"]))
            if r.get("prod_name"):
                keys.append(("name", pkey(r["prod_name"])))
            for k in keys:
                if f and u:
                    conv[(k, u)] = f
                if r.get("base_unit"):
                    base_unit[k] = r["base_unit"]
    for name, big, f, base in b.readme.conversions:
        conv[(("name", pkey(name)), ukey(big))] = f
        base_unit.setdefault(("name", pkey(name)), base)
    for _, r in P.iterrows():
        bu = r.get("base_unit", "")
        if bu:
            if r.get("prod_id"):
                base_unit.setdefault(("id", r["prod_id"]), bu)
            if r.get("pkey"):
                base_unit.setdefault(("name", r["pkey"]), bu)
    C["_conv"] = conv
    C["_base_unit"] = base_unit

    id2name = {r["prod_id"]: r["prod_name"] for _, r in P.iterrows() if r.get("prod_id") and r.get("prod_name")}
    name2id = {r["pkey"]: r["prod_id"] for _, r in P.iterrows() if r.get("prod_id") and r.get("pkey")}

    # ---------------- lines ----------------
    L = None
    frames = _frame(b, "lines")
    if frames:
        L = pd.concat(frames, ignore_index=True).fillna("")
        has_oid = "order_id" in L and (L["order_id"] != "").mean() > 0.5
        if has_oid:
            # duplicate rows inside one order are an export error: count once (§8)
            # identical raw rows of one order are an export error: count once (§8); compare raw cells, before
            # filling blank order-level cells from the order's first row
            raw_cols = [c for c in L.columns if not c.startswith("_")]
            dup = L.duplicated(subset=raw_cols + ["_tbl"], keep="first") & (L["order_id"] != "")
            if dup.any():
                notes.append(f"lines: dropped {int(dup.sum())} duplicate rows within orders")
            L = L[~dup].copy()
            L = _ffill_groups(L, "order_id", [c for c in ORDER_LEVEL if c in L])
        if "prod_name" not in L:
            L["prod_name"] = L["prod_id"].map(id2name).fillna("") if "prod_id" in L else ""
        elif "prod_id" in L:
            miss = L["prod_name"] == ""
            L.loc[miss, "prod_name"] = L.loc[miss, "prod_id"].map(id2name).fillna("")
        if "prod_id" not in L:
            L["prod_id"] = L["prod_name"].map(lambda n: name2id.get(pkey(n), ""))
        L["pkey"] = L["prod_name"].map(pkey)
        q = L["qty"].map(parse_qty) if "qty" in L else pd.Series([(np.nan, None)] * len(L))
        L["qty_num"] = [x[0] if x[0] is not None else np.nan for x in q]
        unit_from_qty = [x[1] for x in q]
        if "unit" not in L:
            L["unit"] = ""
        L["unit"] = [u if u else (uq or "") for u, uq in zip(L["unit"], unit_from_qty)]
        L["qty_base_given"] = _num(L, "qty_base")
        L["unit_price"] = _num(L, "unit_price")
        L["line_discount"] = _num(L, "line_discount").fillna(0.0)
        L["line_amount"] = _num(L, "line_amount")
        L["cost_unit"] = _num(L, "cost_unit")
        # conversion factor of the line's unit to the base unit
        facs = []
        for pid, pk, u in zip(L["prod_id"], L["pkey"], L["unit"]):
            uk = ukey(u)
            f = None
            for k in ((("id", pid),) if pid else ()) + ((("name", pk),) if pk else ()):
                if (k, uk) in conv:
                    f = conv[(k, uk)]
                    break
                bu = base_unit.get(k)
                if bu is not None and ukey(bu) == uk:
                    f = 1.0
                    break
            facs.append(f)
        L["factor"] = pd.Series(facs, index=L.index, dtype="float64")
        qb = L["qty_base_given"].copy()
        est = L["qty_num"] * L["factor"].fillna(1.0)
        L["qty_base"] = qb.where(qb.notna(), est)
        # line amount when missing: qty * price - discount
        miss = L["line_amount"].isna()
        if miss.any():
            L.loc[miss, "line_amount"] = L.loc[miss, "qty_num"] * L.loc[miss, "unit_price"] - L.loc[miss, "line_discount"]
        L["is_fee"] = L["pkey"].str.contains(r"^phi phuc vu|^phi dich vu|^phu thu", regex=True)

    # ---------------- orders ----------------
    O = None
    oframes = _frame(b, "orders")
    if oframes:
        # the order list with the most order-level fields first; other order tables (debt terms, tables/rooms) add
        # columns by order id
        oframes.sort(key=lambda d: (-len([c for c in d.columns if c in ("order_date", "order_ts", "status", "order_total",
                                                                        "order_gross", "pay_method")]), -len(d)))
        O = oframes[0].drop(columns=["_src", "_tbl", "_row"]).copy()
        O = O[O["order_id"] != ""].drop_duplicates(subset=["order_id"], keep="first")
        for extra in oframes[1:]:
            ex = extra.drop(columns=["_src", "_year", "_tbl", "_row"])
            ex = ex[ex["order_id"] != ""].drop_duplicates(subset=["order_id"])
            cols = ["order_id"] + [c for c in ex.columns if c not in O.columns]
            O = O.merge(ex[cols], on="order_id", how="outer")
        O = O.fillna("")
    if L is not None and "order_id" in L and (L["order_id"] != "").mean() > 0.5:
        lv = [c for c in ORDER_LEVEL if c in L]
        LO = L[L["order_id"] != ""].groupby("order_id", sort=False).agg({c: "first" for c in lv + ["_year"]}).reset_index()
        if O is None:
            O = LO
        else:
            main_has_date = ("order_date" in O or "order_ts" in O) and \
                ((O.get("order_date", "") != "").mean() > 0.5 if "order_date" in O else True)
            if main_has_date:
                add = [c for c in LO.columns if c not in O.columns]
                O = O.merge(LO[["order_id"] + add], on="order_id", how="outer").fillna("")
                missing = set(LO["order_id"]) - set(oframes[0]["order_id"])
                if missing:
                    notes.append(f"orders: {len(missing)} order ids only in lines")
            else:
                # order tables without dates (debt terms, room/table lists) only add columns to the orders from lines
                add = [c for c in O.columns if c not in LO.columns or c == "order_id"]
                O = LO.merge(O[add], on="order_id", how="left").fillna("")
    # customer group and names from the customer list
    CU = _frame(b, "customers")
    if O is not None and CU:
        cu = pd.concat(CU, ignore_index=True).fillna("")
        if "cust_id" in O and "cust_id" in cu:
            for col in ("cust_group", "cust_name"):
                if col in cu:
                    mp = dict(zip(cu["cust_id"], cu[col]))
                    if col not in O:
                        O[col] = O["cust_id"].map(mp).fillna("")
                    else:
                        O[col] = O[col].where(O[col] != "", O["cust_id"].map(mp).fillna(""))
        elif "cust_name" in O and "cust_name" in cu and "cust_group" in cu and "cust_group" not in O:
            mp = dict(zip(cu["cust_name"].map(fold), cu["cust_group"]))
            O["cust_group"] = O["cust_name"].map(lambda n: mp.get(fold(n), ""))
    # staff names from the staff list
    ST = _frame(b, "staff")
    if O is not None and ST and "staff" in O:
        st = pd.concat(ST, ignore_index=True).fillna("")
        if "staff_name" in st:
            mp = dict(zip(st["staff"], st["staff_name"]))
            O["staff_name"] = O["staff"].map(mp).fillna("")
    if O is not None:
        O["date"] = _dates(O, "order_date")
        ts = _dates(O, "order_ts")
        O["ts"] = ts
        if "order_time" in O:
            t = O["order_time"].map(lambda v: _hhmm(v))
            dd = O["date"].dt.normalize()
            O["ts"] = O["ts"].where(O["ts"].notna(), dd + pd.to_timedelta(t, unit="m"))
        O["date"] = O["date"].where(O["date"].notna(), O["ts"]).dt.normalize()
        O["status"] = O["status"].map(canon_status) if "status" in O else "completed"
        if "pay_method" in O:
            O["pay"] = O["pay_method"].map(canon_pay)
        for c in ("order_gross", "order_discount", "order_total", "ship_fee", "vat", "paid", "remaining", "due_days"):
            if c in O:
                O[c] = to_number_series(O[c])
        if "due_date" in O:
            O["due_date"] = _dates(O, "due_date")
        if L is not None and "order_id" in L:
            g = L.groupby("order_id")
            rev = g["line_amount"].sum()
            O["revenue"] = O["order_id"].map(rev)
            if "order_gross" in O:
                O["revenue"] = O["revenue"].where(O["revenue"].notna(), O["order_gross"])
            O["n_items"] = O["order_id"].map(g.size()).fillna(0)
        elif "order_gross" in O:
            O["revenue"] = O["order_gross"]
        C["orders"] = O

    # bring order fields onto lines
    if L is not None:
        if O is not None and "order_id" in L:
            cols = [c for c in ("date", "ts", "status", "cust_id", "cust_name", "pay", "channel", "staff", "branch",
                                "cust_group", "staff_name") if c in O]
            L = L.drop(columns=[c for c in cols if c in L and c not in ("order_id",)], errors="ignore")
            L = L.merge(O[["order_id"] + cols], on="order_id", how="left")
        else:
            L["date"] = _dates(L, "order_date").dt.normalize()
            ts = _dates(L, "order_ts")
            if "order_time" in L:
                t = L["order_time"].map(lambda v: _hhmm(v))
                ts = ts.where(ts.notna(), L["date"] + pd.to_timedelta(t, unit="m"))
            L["ts"] = ts
            L["status"] = L["status"].map(canon_status) if "status" in L else "completed"
        C["lines"] = L

    # ---------------- customers, payments ----------------
    for role in ("customers",):
        fr = _frame(b, role)
        if fr:
            C[role] = pd.concat(fr, ignore_index=True).fillna("")
    fr = _frame(b, "payments")
    if fr:
        Pm = pd.concat(fr, ignore_index=True).fillna("")
        Pm["ts"] = _dates(Pm, "pay_ts")
        Pm["amount"] = _num(Pm, "pay_amount")
        if "pay_method" in Pm:
            Pm["pay"] = Pm["pay_method"].map(canon_pay)
        C["payments"] = Pm

    # ---------------- purchases ----------------
    po_lines = []
    for role in ("purchases", "lots"):
        for df in _frame(b, role):
            if "po_id" in df and ({"qty", "qty_base"} & set(df.columns)) and ({"prod_id", "prod_name"} & set(df.columns)):
                po_lines.append(df)
    H = None
    fr = _frame(b, "po_headers")
    if fr:
        H = pd.concat(fr, ignore_index=True).fillna("")
        H["date"] = _dates(H, "po_date")
        H["total"] = _num(H, "po_total")
        H["cancelled"] = H["po_status"].map(lambda v: canon_status(v) == "cancelled") if "po_status" in H else False
        C["po_headers"] = H
    if po_lines:
        PL = pd.concat(po_lines, ignore_index=True).fillna("")
        if "prod_name" not in PL and "prod_id" in PL:
            PL["prod_name"] = PL["prod_id"].map(id2name).fillna("")
        if "prod_id" not in PL:
            PL["prod_id"] = PL["prod_name"].map(lambda n: name2id.get(pkey(n), ""))
        PL["pkey"] = PL["prod_name"].map(pkey)
        q = PL["qty"].map(parse_qty) if "qty" in PL else pd.Series([(np.nan, None)] * len(PL))
        PL["qty_num"] = [x[0] if x[0] is not None else np.nan for x in q]
        if "unit" not in PL:
            PL["unit"] = ""
        PL["unit"] = [u if u else (x[1] or "") for u, x in zip(PL["unit"], q)]
        PL["unit_cost"] = _num(PL, "unit_cost")
        PL["amount"] = _num(PL, "po_amount")
        PL["qty_base_given"] = _num(PL, "qty_base")
        if H is not None and "po_id" in H:
            PL = PL.merge(H[["po_id", "date", "cancelled"] + [c for c in ("supplier_id", "supplier", "note") if c in H
                                                                and c not in PL]], on="po_id", how="left")
        else:
            PL["date"] = _dates(PL, "po_date")
            PL["cancelled"] = PL["po_status"].map(lambda v: canon_status(v) == "cancelled") if "po_status" in PL else False
        miss = PL["amount"].isna()
        PL.loc[miss, "amount"] = PL.loc[miss, "qty_num"] * PL.loc[miss, "unit_cost"]
        C["purchases"] = PL

    for role in ("lots", "lot_sales", "price_hist", "returns", "deliveries", "moves", "stock"):
        fr = _frame(b, role)
        if fr:
            C[role] = pd.concat(fr, ignore_index=True).fillna("")
    if "price_hist" in C:
        ph = C["price_hist"]
        ph["date"] = _dates(ph, "eff_date")
        for c in ("new_price", "old_price"):
            if c in ph:
                ph[c] = to_number_series(ph[c])
        if "prod_name" not in ph and "prod_id" in ph:
            ph["prod_name"] = ph["prod_id"].map(id2name).fillna("")
        ph["pkey"] = ph["prod_name"].map(pkey)
    if "deliveries" in C:
        dv = C["deliveries"]
        dv["date"] = _dates(dv, "deliv_date")
    if "moves" in C:
        mv = C["moves"]
        mv["ts"] = _dates(mv, "mv_ts")
        mv["qty_base"] = _num(mv, "qty_base")
        mv["stock"] = _num(mv, "stock")
    if "lots" in C:
        lt = C["lots"]
        lt["expiry_d"] = _dates(lt, "expiry")
    # data range
    dmax = None
    if O is not None and "date" in O:
        dmax = O["date"].max()
    elif L is not None:
        dmax = L["date"].max()
    C["_data_end"] = pd.Timestamp(b.readme.data_end) if b.readme.data_end else dmax
    dmin = None
    if O is not None and "date" in O:
        dmin = O["date"].min()
    elif L is not None:
        dmin = L["date"].min()
    C["_data_start"] = dmin
    b.canon = C
    return C


def _hhmm(v):
    s = str(v or "").strip()
    m = re.match(r"^(\d{1,2}):(\d{2})", s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    d = parse_datetime(s)
    if d is not None:
        return d.hour * 60 + d.minute
    x = parse_number(s)
    if x is not None and 0 <= x < 1:          # Excel time fraction
        return int(round(x * 24 * 60))
    return np.nan
