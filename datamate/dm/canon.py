"""Canonical tables of one business, built from its raw tables and README.

Step 1 (map): every raw column gets a canonical field (README meaning > column-name synonym > ID value prefix).
Step 2 (role): every raw table gets a role (lines, orders, payments, products, conversions, customers, purchases,
        po_headers, stock, lots, lot_sales, price_hist, returns, deliveries, moves, staff, other).
Step 3 (assemble, dm.assemble): typed canonical DataFrames.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

import pandas as pd

from .io import RawTable, load_business
from .readme import Readme, parse_readme
from .schema import PREFIX_FIELD, id_prefix, meaning_field, name_field
from .textnorm import colkey, fold
from .values import frac_parsed

ID_FIELDS = {"order_id", "po_id", "pay_id", "prod_id", "cust_id", "supplier_id", "ret_id", "mv_id", "lot_id", "shift_id"}


@dataclass
class Mapped:
    name: str
    raw: RawTable
    fields: dict = field(default_factory=dict)      # raw column -> field
    how: dict = field(default_factory=dict)         # raw column -> 'readme' | 'name' | 'prefix'
    role: str = "other"
    unmapped: list = field(default_factory=list)


def map_table(t: RawTable, rd: Readme) -> Mapped:
    mt = Mapped(name=t.name, raw=t)
    used = set()
    cols = [c for c in t.df.columns if c not in ("_src", "_year")]
    for c in cols:
        m = rd.meaning(t.name, c) or rd.any_meaning(c)
        mf = meaning_field(m) if m else None
        nf = name_field(c)
        cands = [(mf, "readme"), (nf, "name")]
        # ID columns: the value prefix decides when it disagrees with an ID-ish guess
        p = id_prefix(t.df[c].tolist())
        if p and p in PREFIX_FIELD:
            pf = PREFIX_FIELD[p]
            if mf is None or mf in ID_FIELDS or mf in ("staff", "branch", "promo", "line_no"):
                cands.insert(0, (pf, "prefix"))
        f, how = None, None
        for cf, ch in cands:
            if cf and cf not in used:
                f, how = cf, ch
                break
        if f is None:
            first = next(((cf, ch) for cf, ch in cands if cf), None)
            if first:
                f, how = first[0] + "__2", first[1]
        if f:
            mt.fields[c] = f
            mt.how[c] = how
            used.add(f)
        else:
            mt.unmapped.append(c)
    mt.role = classify(mt)
    finalize(mt)
    return mt


# role-specific renames: the same header means different things in different tables
ROLE_RENAME = {
    "payments": {"order_date": "pay_ts", "order_ts": "pay_ts", "unit_price": "pay_amount", "line_amount": "pay_amount",
                 "paid": "pay_amount", "order_total": "pay_amount"},
    "po_headers": {"order_date": "po_date", "order_ts": "po_date", "status": "po_status", "line_amount": "po_total",
                   "order_total": "po_total"},
    "purchases": {"order_date": "po_date", "order_ts": "po_date", "unit_price": "unit_cost", "line_amount": "po_amount",
                  "status": "po_status"},
    "lots": {"order_date": "po_date", "order_ts": "po_date", "unit_price": "unit_cost", "line_amount": "po_amount"},
    "moves": {"order_ts": "mv_ts", "order_date": "mv_ts", "order_id": "ref_id", "mv_type__2": "ref_type", "po_id": "ref_id"},
    "products": {"unit": "base_unit", "unit_price": "list_price", "order_ts": "created_ts", "name": "prod_name",
                 "status": "prod_status", "line_amount": "list_price"},
    "stock": {"unit": "base_unit", "name": "prod_name"},
    "drug_info": {"name": "prod_name"},
    "conversions": {"unit": "conv_unit", "unit_price": "conv_price", "name": "prod_name"},
    "price_hist": {"unit_price": "new_price", "unit_price__2": "old_price", "name": "prod_name"},
    "customers": {"prod_name": "cust_name", "name": "cust_name", "status": "cust_status", "order_ts": "created_ts"},
    "suppliers": {"name": "supplier"},
    "staff": {"name": "staff_name"},
    "lines": {"discount": "line_discount", "cost": "cost_unit", "order_gross": "line_amount", "name": "prod_name"},
    "orders": {"discount": "order_discount", "line_amount": "order_gross"},
    "lot_sales": {"qty_base__2": "ret_qty_base", "qty": "qty_base"},
    "deliveries": {"qty_base": "deliv_qty_base", "qty": "deliv_qty"},
    "returns": {"order_ts": "ret_ts", "order_date": "ret_ts"},
}
# unmapped columns that take a field from the role when they hold numbers
ROLE_NUMERIC_FALLBACK = {"payments": "pay_amount", "lines": "line_amount", "po_headers": "po_total"}


def finalize(mt: Mapped) -> None:
    ren = ROLE_RENAME.get(mt.role, {})
    present = set(mt.fields.values())
    for c, f in list(mt.fields.items()):
        g = ren.get(f)
        if g and g not in present:
            mt.fields[c] = g
            present.discard(f)
            present.add(g)
    # price history: decide new/old price by header name when both exist
    if mt.role == "price_hist":
        for c in list(mt.fields):
            k = colkey(c)
            if k in ("giamoi",):
                mt.fields[c] = "new_price"
            elif k in ("giacu",):
                mt.fields[c] = "old_price"
    fb = ROLE_NUMERIC_FALLBACK.get(mt.role)
    if fb and fb not in set(mt.fields.values()):
        for c in list(mt.unmapped):
            if frac_parsed(mt.raw.df[c], "number") > 0.9:
                mt.fields[c] = fb
                mt.how[c] = "role"
                mt.unmapped.remove(c)
                break


def classify(mt: Mapped) -> str:
    F = set(v.split("__")[0] for v in mt.fields.values())
    has_prod = bool(F & {"prod_id", "prod_name"})
    if "cust_id" in F and "prod_name" in F and not (F & {"order_id", "qty", "unit_price", "category", "cost", "base_unit", "prod_id"}):
        has_prod = False         # a customer list whose name column was read as a product name
    name = fold(mt.name)
    if "lot_id" in F and "order_id" in F:
        return "lot_sales"
    if "lot_id" in F and ("expiry" in F or "po_id" in F or "po_date" in F):
        return "lots"
    if "conv_factor" in F and has_prod:
        return "conversions"
    if "eff_date" in F and has_prod:
        return "price_hist"
    if "ret_id" in F:
        return "returns"
    if "mv_id" in F or ("mv_type" in F and "stock" in F):
        return "moves"
    if "po_id" in F and has_prod:
        return "purchases"
    if "po_id" in F:
        return "po_headers"
    if "pay_id" in F and not has_prod:
        return "payments"
    if ("deliv_date" in F or "deliv_round" in F) and "order_id" in F and not ({"unit_price", "line_amount"} & F):
        return "deliveries"
    if "order_id" in F and has_prod:
        return "lines"
    if "order_id" in F and not has_prod:
        if "pay_amount" in F or ("pay_ts" in F and not (F & {"status", "order_total", "order_gross"})):
            return "payments"
        return "orders"
    if has_prod and ({"qty", "line_amount", "qty_base"} & F) and (F & {"order_date", "order_ts"}):
        return "lines"           # flat sales log without order IDs
    if has_prod and "stock" in F and len(F - {"prod_id", "prod_name", "unit", "base_unit", "stock"}) <= 1:
        return "stock"
    if has_prod and (F & {"rx", "ingredient"}) and not (F & {"unit_price", "cost", "category"}):
        return "drug_info"
    if "cust_id" in F and ("cust_name" in F or "name" in F or "phone" in F or "address" in F) and not (F & {"category", "unit_price", "cost", "base_unit"}):
        return "customers"
    if has_prod or ("name" in F and (F & {"category", "unit_price", "cost", "base_unit", "list_price"})):
        return "products"
    if "staff" in F:
        return "staff"
    if "supplier_id" in F or "supplier" in F:
        return "suppliers"
    return "other"


@dataclass
class Business:
    biz: str
    path: str
    readme: Readme
    tables: dict            # name -> Mapped
    canon: dict = field(default_factory=dict)   # role -> DataFrame (dm.assemble)
    notes: list = field(default_factory=list)


def open_business(path: str, cache_dir: str | None = None) -> Business:
    rd = parse_readme(open(os.path.join(path, "README.md"), encoding="utf-8").read()) if os.path.exists(
        os.path.join(path, "README.md")) else parse_readme("")
    raw = load_business(path, cache_dir=cache_dir)
    tables = {n: map_table(t, rd) for n, t in raw.items()}
    return Business(biz=os.path.basename(path.rstrip("/")), path=path, readme=rd, tables=tables)


def profile(b: Business) -> str:
    out = [f"## {b.biz} end={b.readme.data_end} conv={len(b.readme.conversions)}"]
    for n, mt in b.tables.items():
        fl = ", ".join(f"{c}->{f}{'' if mt.how[c] == 'name' else '*' if mt.how[c] == 'readme' else '^'}"
                       for c, f in mt.fields.items())
        out.append(f"  [{mt.role}] {n} rows={len(mt.raw.df)}: {fl}")
        if mt.unmapped:
            out.append(f"      unmapped: {mt.unmapped}")
    return "\n".join(out)


if __name__ == "__main__":
    import sys

    for bz in sys.argv[2:]:
        print(profile(open_business(os.path.join(sys.argv[1], bz), cache_dir=os.path.expanduser("~/zac-dm/cache/raw"))))
