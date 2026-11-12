"""Rulebook guard: compare the split's rulebook with the train rulebook the engine implements.

Rows of the markdown tables ("| Cách nói | Nghĩa |") and bullets become (key, text) pairs. A row whose text differs
(after normalisation) or that is missing is "changed". Each question depends on some rows (by intent, period kind and
filters); if any of them changed, the engine must not answer from its train-rule code, so the runner abstains.
The reference (train) rulebook is read from a file that ships inside the image, not from git (dataset licence).
"""
from __future__ import annotations

import re

from .textnorm import fold


def _norm(s: str) -> str:
    s = re.sub(r"[*_`]", "", s)
    s = fold(s)
    s = re.sub(r"[^a-z0-9%/ ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_rows(md: str) -> dict:
    rows = {}
    section = ""
    for line in (md or "").splitlines():
        h = re.match(r"^#+\s*(.*)$", line)
        if h:
            section = _norm(h.group(1))
            continue
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2 or set(cells[0]) <= set("-: ") or _norm(cells[0]) in ("luat", "cach noi", "type", "tu", "cach ghi"):
                continue
            key = _norm(cells[0])
            rows[f"{section}|{key}"] = _norm(" | ".join(cells[1:]))
        elif re.match(r"^\s*[-*]\s+", line):
            txt = _norm(line)
            rows[f"{section}|bullet:{txt[:40]}"] = txt
    return rows


# question features -> rulebook row keys (substring match on the 'key' part of 'section|key')
DEPS = {
    "revenue": ["don tinh vao doanh thu", "doanh thu mot don", "don thuoc ky nao", "ban duoc bao nhieu tien"],
    "orders": ["so don", "don tinh vao doanh thu", "don thuoc ky nao"],
    "cancel": ["don bi huy", "ti le don huy", "don thuoc ky nao"],
    "pct_change": ["phan tram thay doi"],
    "diff": ["chenh lech"],
    "aov": ["gia tri trung binh mot don"],
    "pay": ["doanh thu theo hinh thuc thanh toan"],
    "cust_group": ["doanh thu theo nhom khach"],
    "items": ["mat hang", "ban chay", "nhom hang"],
    "unit_qty": ["ban duoc bao nhieu", "don vi co ban"],
    "customers": ["xac dinh khach"],
    "staff": ["nhan vien ban gioi nhat"],
    "debt": ["don duoc tinh vao no", "no mot don", "no theo khach", "don cod", "tuoi no", "no them"],
    "purchase": ["tien nhap hang", "gia nhap binh quan", "nhap tru ban"],
    "stock": ["den het ngay x", "ton theo don vi lon", "gia tri hang ton", "mat hang het hang"],
    "unsold": ["mat hang khong ban duoc"],
    "price": ["gia ban x ngay d", "hieu ung tang gia"],
    "profit": ["gia von", "lai gop", "lai rong"],
    "expiry": ["het han", "lo gan het han"],
    "rx": ["thuoc ke don"],
    "ingredient": ["doanh thu theo hoat chat"],
    "size": ["size m"],
    "delivery": ["giao nhieu dot"],
    # periods
    "p_day": ["ngay x hom nay hom qua"],
    "p_range": ["tu x den y"],
    "p_lastn": ["n ngay gan nhat"],
    "p_week": ["tuan"],
    "p_month": ["thang m/y"],
    "p_this_month": ["thang nay"],
    "p_ytd": ["tu dau nam"],
    "p_noyear": ["thang m quy q khong ghi nam"],
    "p_tet": ["tet nam y"],
    "p_shift": ["ca sang ca chieu"],
    "p_threshold": ["qua n hon n tren n duoi n"],
    "rank": ["bang nhau", "danh sach"],
}

INTENT_FEATS = {
    "revenue": ["revenue"], "orders": ["orders"], "qty": ["revenue", "unit_qty"], "aov": ["revenue", "orders", "aov"],
    "cancel_count": ["cancel"], "cancel_rate": ["cancel"], "best_day": ["revenue"], "best_month": ["revenue"],
    "days_threshold": ["revenue", "p_threshold"], "orders_threshold": ["revenue", "p_threshold"],
    "share": ["revenue"], "pay_split": ["revenue", "pay"], "channel_split": ["revenue"], "months_list": ["revenue"],
    "trend": ["revenue"], "top_items": ["items", "rank"], "top_customers": ["customers", "revenue", "rank"],
    "top_customers_orders": ["customers", "orders", "rank"], "customers_min_orders": ["customers", "orders"],
    "customers_min_orders_pct": ["customers", "orders"], "customer_count": ["customers"], "unsold": ["unsold"],
    "items_in_orders": ["items", "orders"], "price_on_date": ["price"], "price_effect": ["price"],
    "purchase_total": ["purchase"], "purchase_avg_price": ["purchase"], "purchase_supplier_top": ["purchase"],
    "stock": ["stock"], "stock_big": ["stock"], "stock_value": ["stock"], "stockout_count": ["stock"],
    "stockout_list": ["stock"], "debt_total": ["debt"], "debt_top": ["debt", "customers"], "debt_count": ["debt", "customers"],
    "debt_aging": ["debt"], "debt_paid": ["debt"], "debt_new": ["debt"], "debt_paid_new": ["debt"],
    "delivery_rounds": ["delivery"], "gross_profit": ["profit", "revenue"],
}


class Guard:
    def __init__(self, ref_md: str | None, split_md: str | None):
        self.active = bool(ref_md) and bool(split_md)
        self.changed = set()
        if not self.active:
            return
        ref, cur = parse_rows(ref_md), parse_rows(split_md)
        cur_by_key = {}
        for k, v in cur.items():
            cur_by_key.setdefault(k.split("|", 1)[1], []).append(v)
        for k, v in ref.items():
            key = k.split("|", 1)[1]
            if v not in cur_by_key.get(key, []):
                self.changed.add(key)

    def features(self, q) -> list[str]:
        feats = list(INTENT_FEATS.get(q.intent, []))
        if q.output == "pct_change":
            feats.append("pct_change")
        elif q.output == "diff":
            feats.append("diff")
        f = q.filters
        for k, feat in (("pay_list", "pay"), ("cust_group", "cust_group"), ("rx", "rx"), ("ingredient", "ingredient"),
                        ("size", "size"), ("shift_list", "p_shift"), ("staff", "staff")):
            if k in f:
                feats.append(feat)
        t = q.text
        if re.search(r"\btuan\b", t):
            feats.append("p_week")
        if "thang nay" in t:
            feats.append("p_this_month")
        if re.search(r"\d+ ngay (gan|qua|vua)", t):
            feats.append("p_lastn")
        if re.search(r"tu dau nam|nam nay", t):
            feats.append("p_ytd")
        if re.search(r"\btet\b", t):
            feats.append("p_tet")
        if re.search(r"\btu .* den\b", t):
            feats.append("p_range")
        if re.search(r"hom nay|hom qua", t):
            feats.append("p_day")
        return feats

    def blocking(self, q) -> list[str]:
        if not self.active or not self.changed:
            return []
        out = []
        for feat in self.features(q):
            for dep in DEPS.get(feat, []):
                for ch in self.changed:
                    if dep in ch:
                        out.append(ch)
        return sorted(set(out))
