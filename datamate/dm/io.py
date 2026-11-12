"""Raw loading of one business folder: every csv, every xlsx sheet, every sqlite table, as string DataFrames.

- Header row: the row (among the first 25) with the most header-like cells (non-empty text that does not parse as a
  number or a date). Title rows above it ("Kênh bán: Tất cả", "Kỳ báo cáo: toàn bộ") are skipped.
- Tables with the same header in one file (monthly sheets) or across files (`..._1.xlsx`, `..._2026.xlsx`) are
  concatenated. Columns `_src` (file:sheet) and `_year` (a year in the sheet or file name, for dates without a year)
  are added.
- Cells are strings ('' for empty). Typed parsing happens in dm.canon.
- Results are cached as parquet under a cache dir keyed by path, size and mtime.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io as _io
import json
import os
import re
import sqlite3
from dataclasses import dataclass, field

import pandas as pd

from .textnorm import colkey
from .values import parse_datetime, parse_number, sheet_year


@dataclass
class RawTable:
    name: str                 # e.g. "DonHang_ChiTiet.xlsx" or "pos.sqlite:don_hang"
    df: pd.DataFrame          # string cells, original header names, plus _src and _year
    sources: list = field(default_factory=list)
    header_row: int = 0


def _cell_str(v) -> str:
    if v is None:
        return ""
    if isinstance(v, dt.datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, dt.date):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, float):
        if v != v:
            return ""
        return str(int(v)) if v.is_integer() else repr(v)
    if isinstance(v, bool):
        return "True" if v else "False"
    return str(v).strip()


def _headerish(c: str) -> bool:
    if not c or len(c) > 60:
        return False
    if parse_number(c) is not None:
        return False
    if parse_datetime(c) is not None:
        return False
    return bool(re.search(r"[A-Za-zÀ-ỹđĐ]", c))


def _find_header(rows: list[list[str]]) -> int:
    best, best_i = -1.0, 0
    for i, r in enumerate(rows[:25]):
        cells = [c for c in r if c != ""]
        if len(cells) < 2:
            continue
        h = sum(_headerish(c) for c in cells)
        # the row below should look like data (has some number or date) or be absent
        nxt = [c for c in (rows[i + 1] if i + 1 < len(rows) else []) if c != ""]
        data_like = sum(1 for c in nxt if not _headerish(c))
        score = h + (0.5 if data_like else 0) - (len(cells) - h) * 1.0
        if h >= max(2, 0.6 * len(cells)) and score > best:
            best, best_i = score, i
    return best_i


def _frame(rows: list[list[str]], src: str, year: int | None) -> tuple[pd.DataFrame, int]:
    if not rows:
        return pd.DataFrame(), 0
    width = max(len(r) for r in rows)
    rows = [list(r) + [""] * (width - len(r)) for r in rows]
    k = _find_header(rows)
    header = rows[k]
    names, seen = [], {}
    for j, h in enumerate(header):
        h = h or f"col{j}"
        if h in seen:
            seen[h] += 1
            h = f"{h}__{seen[h]}"
        else:
            seen[h] = 0
        names.append(h)
    body = [r for r in rows[k + 1:] if any(c != "" for c in r)]
    df = pd.DataFrame(body, columns=names, dtype="object")
    # drop all-empty unnamed columns
    keep = [c for c in df.columns if not (c.startswith("col") and (df[c] == "").all())]
    df = df[keep].copy()
    df["_src"] = src
    df["_year"] = "" if year is None else str(year)
    return df, k


def _read_xlsx(path: str) -> list[tuple[str, list[list[str]], int | None]]:
    import openpyxl

    out = []
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    fname = os.path.basename(path)
    for sn in wb.sheetnames:
        ws = wb[sn]
        rows = [[_cell_str(v) for v in r] for r in ws.iter_rows(values_only=True)]
        while rows and not any(rows[-1]):
            rows.pop()
        out.append((f"{fname}:{sn}", rows, sheet_year(sn) or sheet_year(fname)))
    wb.close()
    return out


def _read_csv(path: str) -> list[tuple[str, list[list[str]], int | None]]:
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "utf-8", "cp1258", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    sample = text[:20000]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        delim = dialect.delimiter
    except csv.Error:
        delim = ","
    rows = [[c.strip() for c in r] for r in csv.reader(_io.StringIO(text), delimiter=delim)]
    fname = os.path.basename(path)
    return [(fname, rows, sheet_year(fname))]


def _read_sqlite(path: str) -> list[tuple[str, pd.DataFrame]]:
    out = []
    con = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
    try:
        for (t,) in con.execute("select name from sqlite_master where type='table' order by name"):
            cur = con.execute(f'select * from "{t}"')
            cols = [c[0] for c in cur.description]
            data = [[_cell_str(v) for v in r] for r in cur.fetchall()]
            df = pd.DataFrame(data, columns=cols, dtype="object")
            df["_src"] = f"{os.path.basename(path)}:{t}"
            df["_year"] = ""
            out.append((f"{os.path.basename(path)}:{t}", df))
    finally:
        con.close()
    return out


def _sig(df: pd.DataFrame) -> tuple:
    return tuple(colkey(c) for c in df.columns if c not in ("_src", "_year"))


def _cache_key(path: str) -> str:
    st = os.stat(path)
    return hashlib.sha1(f"{os.path.abspath(path)}|{st.st_size}|{int(st.st_mtime)}".encode()).hexdigest()[:16]


def load_business(biz_dir: str, cache_dir: str | None = None) -> dict[str, RawTable]:
    """All raw tables of one business, merged by header signature. Keys are readable table names."""
    files = sorted(f for f in os.listdir(biz_dir) if f.lower().rsplit(".", 1)[-1] in ("csv", "xlsx", "xlsm", "sqlite", "db"))
    pieces: list[tuple[str, pd.DataFrame, int]] = []
    for f in files:
        p = os.path.join(biz_dir, f)
        ext = f.lower().rsplit(".", 1)[-1]
        cpath = None
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            cpath = os.path.join(cache_dir, f"{_cache_key(p)}.pkl")
            if os.path.exists(cpath):
                pieces.extend(pd.read_pickle(cpath))
                continue
        got: list[tuple[str, pd.DataFrame, int]] = []
        if ext in ("sqlite", "db"):
            for name, df in _read_sqlite(p):
                got.append((name, df, 0))
        else:
            sheets = _read_xlsx(p) if ext in ("xlsx", "xlsm") else _read_csv(p)
            for src, rows, year in sheets:
                df, k = _frame(rows, src, year)
                if len(df.columns) > 2 and len(df):
                    got.append((src, df, k))
        if cpath:
            pd.to_pickle(got, cpath)
        pieces.extend(got)
    # merge pieces with the same header signature (monthly sheets, split files)
    groups: dict[tuple, list] = {}
    order: list[tuple] = []
    for src, df, k in pieces:
        s = _sig(df)
        if s not in groups:
            groups[s] = []
            order.append(s)
        groups[s].append((src, df, k))
    tables: dict[str, RawTable] = {}
    for s in order:
        items = groups[s]
        df = pd.concat([d for _, d, _ in items], ignore_index=True) if len(items) > 1 else items[0][1]
        base = items[0][0]
        name = base if len(items) == 1 else re.sub(r":[^:]*$", "", base) + f"[{len(items)} parts]"
        while name in tables:
            name += "'"
        tables[name] = RawTable(name=name, df=df, sources=[src for src, _, _ in items], header_row=items[0][2])
    return tables


def describe(tables: dict[str, RawTable]) -> str:
    lines = []
    for name, t in tables.items():
        cols = [c for c in t.df.columns if c not in ("_src", "_year")]
        lines.append(f"{name}: rows={len(t.df)} hdr@{t.header_row} cols={cols}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    for b in sys.argv[2:]:
        print("##", b)
        print(describe(load_business(os.path.join(sys.argv[1], b), cache_dir=os.path.expanduser("~/zac-dm/cache/raw"))))
