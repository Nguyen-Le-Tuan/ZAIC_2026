"""Parsers for the cell formats found in DataMate exports.

Raw cells are kept as strings (see dm.io). These functions turn them into numbers, quantities and timestamps:
- numbers: "560,000", "1.200.000", "24.000đ", "50k", "2tr", "1,5", "0.5", "-12.000"
- quantities: "2 kg" -> (2.0, "kg"), "1 bao 25kg" -> (1.0, "bao 25kg"), "3" -> (3.0, None)
- dates: Excel serials ("45717"), "01/02/2025", "1 thg 6 2025", "2025-02-01 06:03(:59)", "01/06" (year from the sheet)
"""
from __future__ import annotations

import datetime as dt
import math
import re

import pandas as pd

_EXCEL0 = dt.datetime(1899, 12, 30)
_MONEY_SUFFIX = re.compile(r"\s*(đ|đồng|dong|vnd|vnđ|₫)\s*$", re.I)


def parse_number(v):
    """Return a float, or None when the cell is not a number."""
    if v is None:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return None if (isinstance(v, float) and math.isnan(v)) else float(v)
    s = str(v).strip().replace(" ", " ")
    if not s or s.lower() in ("nan", "none", "null", "-", "—"):
        return None
    s = _MONEY_SUFFIX.sub("", s).strip()
    neg = s.startswith("-") or (s.startswith("(") and s.endswith(")"))
    s = s.strip("-() ").replace(" ", "")
    mult = 1.0
    m = re.fullmatch(r"([\d.,]+)\s*(k|nghin|ngan|nghìn|ngàn)", s, re.I)
    if m:
        s, mult = m.group(1), 1e3
    else:
        m = re.fullmatch(r"([\d.,]+)\s*(tr|trieu|triệu|m)(\d{1,3})?", s, re.I)
        if m:
            s, mult = m.group(1), 1e6
            if m.group(3):  # "1tr5" = 1.5 million
                s = f"{s}.{m.group(3)}"
    if not re.fullmatch(r"[\d.,]+", s):
        return None
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", s) and not (mult > 1 and re.fullmatch(r"\d+[.,]\d{1,2}", s)):
        # thousands separators; but "1,500" with both separators the same could also be a decimal: VN data uses
        # separators for money, so treat as integer
        if s.count(",") and s.count(".") == 0 or s.count(".") and s.count(",") == 0:
            val = float(re.sub(r"[.,]", "", s))
            return -val * mult if neg else val * mult
    if "," in s and "." in s:
        # whichever comes last is the decimal mark
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".") if re.fullmatch(r"\d+,\d{1,2}", s) else s.replace(",", "")
    elif s.count(".") > 1:
        s = s.replace(".", "")
    try:
        val = float(s) * mult
    except ValueError:
        return None
    return -val if neg else val


_QTY = re.compile(r"^\s*([-+]?\d+(?:[.,]\d+)?)\s*(.*?)\s*$")


def parse_qty(v):
    """(number, unit text or None). '2 kg' -> (2.0, 'kg'); '1 bao 25kg' -> (1.0, 'bao 25kg')."""
    if v is None:
        return None, None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return (None, None) if (isinstance(v, float) and math.isnan(v)) else (float(v), None)
    s = str(v).strip()
    if not s:
        return None, None
    n = parse_number(s)
    if n is not None:
        return n, None
    m = _QTY.match(s)
    if not m:
        return None, None
    num = parse_number(m.group(1))
    unit = m.group(2).strip() or None
    return num, unit


_DMY = re.compile(r"^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})(?:[ T,]+(\d{1,2}):(\d{2})(?::(\d{2}))?)?$")
_DM = re.compile(r"^(\d{1,2})[/\-.](\d{1,2})$")
_YMD = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T](\d{1,2}):(\d{2})(?::(\d{2}))?(?:\.\d+)?)?$")
_THG = re.compile(r"^(\d{1,2})\s*thg\s*(\d{1,2}),?\s*(\d{4})(?:[ ,]+(\d{1,2}):(\d{2})(?::(\d{2}))?)?$", re.I)
_SERIAL = re.compile(r"^(\d{5})(?:\.(\d+))?$")


def parse_datetime(v, year_hint: int | None = None):
    """A datetime, or None. year_hint fills dates written without a year (rulebook: the year of the sheet)."""
    if v is None:
        return None
    if isinstance(v, dt.datetime):
        return v
    if isinstance(v, dt.date):
        return dt.datetime(v.year, v.month, v.day)
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if isinstance(v, float) and math.isnan(v):
            return None
        if 30000 < v < 60000:
            return _EXCEL0 + dt.timedelta(days=float(v))
        return None
    s = str(v).strip()
    if not s or s.lower() in ("nan", "none", "nat"):
        return None
    try:
        m = _YMD.match(s)
        if m:
            y, mo, d, h, mi, se = m.groups()
            return dt.datetime(int(y), int(mo), int(d), int(h or 0), int(mi or 0), int(se or 0))
        m = _DMY.match(s)
        if m:
            d, mo, y, h, mi, se = m.groups()
            return dt.datetime(int(y), int(mo), int(d), int(h or 0), int(mi or 0), int(se or 0))
        m = _THG.match(s)
        if m:
            d, mo, y, h, mi, se = m.groups()
            return dt.datetime(int(y), int(mo), int(d), int(h or 0), int(mi or 0), int(se or 0))
        m = _SERIAL.match(s)
        if m:
            val = float(s)
            if 30000 < val < 60000:
                return _EXCEL0 + dt.timedelta(days=val)
        m = _DM.match(s)
        if m and year_hint:
            d, mo = m.groups()
            return dt.datetime(int(year_hint), int(mo), int(d))
    except ValueError:
        return None
    return None


def to_datetime_series(sr: pd.Series, year_hint: pd.Series | None = None) -> pd.Series:
    if year_hint is None:
        vals = [parse_datetime(x) for x in sr.tolist()]
    else:
        vals = [parse_datetime(x, y) for x, y in zip(sr.tolist(), year_hint.tolist())]
    return pd.to_datetime(pd.Series(vals, index=sr.index, dtype="object"), errors="coerce")


def to_number_series(sr: pd.Series) -> pd.Series:
    return pd.Series([parse_number(x) for x in sr.tolist()], index=sr.index, dtype="float64")


def frac_parsed(sr: pd.Series, kind: str, sample: int = 200) -> float:
    """Share of non-empty cells (in a sample) that parse as `kind` ('number' or 'date')."""
    vals = [x for x in sr.tolist()[:sample * 3] if x not in (None, "") and str(x).strip() != ""][:sample]
    if not vals:
        return 0.0
    f = parse_number if kind == "number" else parse_datetime
    ok = 0
    for x in vals:
        r = f(x)
        if kind == "date" and r is not None and not (2015 <= r.year <= 2030):
            r = None
        ok += r is not None
    return ok / len(vals)


def sheet_year(name: str) -> int | None:
    m = re.search(r"(20\d\d)", name or "")
    return int(m.group(1)) if m else None
