"""README.md of a business: column meanings per file, conventions, data end date, unit conversions.

Typical layout (organisers' generator):
    ## Cột trong `ban_hang.csv`
    - **Giá bán**: đơn giá
    ## Quy ước
    - Dữ liệu có đến hết 24/08/2026.
    - **Quy đổi đơn vị**: số lượng ghi theo đơn vị của dòng:
      - Coca Cola 330ml: 1 thùng = 24 lon
"""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field

from .textnorm import fold, nfc


@dataclass
class Readme:
    text: str = ""
    columns: dict = field(default_factory=dict)        # file name (as written) -> {column: meaning}
    conventions: list = field(default_factory=list)    # bullet lines under "Quy ước" (and other prose)
    data_end: dt.date | None = None
    conversions: list = field(default_factory=list)    # (product name, big unit, factor, base unit)
    tables_note: str = ""

    def meaning(self, file_name: str, column: str) -> str | None:
        """Meaning of a column of a file; matches the file by name without extension too (sqlite tables use 'tbl')."""
        fkeys = [k for k in self.columns if _fmatch(k, file_name)]
        for k in fkeys:
            for c, m in self.columns[k].items():
                if c == column or fold(c) == fold(column):
                    return m
        return None

    def any_meaning(self, column: str) -> str | None:
        hits = {m for cols in self.columns.values() for c, m in cols.items() if c == column or fold(c) == fold(column)}
        return next(iter(hits)) if len(hits) == 1 else None


def _fmatch(readme_name: str, file_name: str) -> bool:
    a = fold(readme_name).strip("`")
    b = fold(file_name)
    b_base = re.sub(r"\[.*$", "", b.split(":")[0])
    a_stem = re.sub(r"\.(xlsx|csv|sqlite)$", "", a)
    b_stem = re.sub(r"\.(xlsx|csv|sqlite)$", "", b_base)
    # split files: "DonHang_ChiTiet_1.xlsx" ~ "DonHang_ChiTiet_2026.xlsx" ~ "DonHang_ChiTiet.xlsx"
    a_core = re.sub(r"_(\d{1,2}|20\d\d)$", "", a_stem)
    b_core = re.sub(r"_(\d{1,2}|20\d\d)$", "", b_stem)
    if a_core == b_core or a_stem == b_stem:
        return True
    # sqlite tables: readme writes `don_hang`, file name is "pos.sqlite:don_hang"
    if ":" in b and fold(b.split(":", 1)[1]).startswith(a_stem):
        return True
    return False


_CONV = re.compile(r"^\s*[-*]\s*(.+?)\s*:\s*1\s+(.+?)\s*=\s*([\d.,]+)\s+(.+?)\s*\.?\s*$")
_END = re.compile(r"đến hết (?:ngày )?(\d{1,2})/(\d{1,2})/(\d{4})")


def parse_readme(text: str) -> Readme:
    text = nfc(text or "")
    r = Readme(text=text)
    section = None
    cur_file = None
    for raw in text.splitlines():
        line = raw.rstrip()
        m = re.match(r"^#+\s*(.*)$", line)
        if m:
            title = m.group(1).strip()
            mm = re.match(r"(?i)^c[ộo]t trong\s+`([^`]+)`", title)
            if mm:
                section, cur_file = "cols", mm.group(1)
                r.columns.setdefault(cur_file, {})
            elif fold(title).startswith("quy uoc"):
                section, cur_file = "conv", None
            elif fold(title).startswith("bang"):
                section, cur_file = "tables", None
            else:
                section, cur_file = "other", None
            continue
        if section == "cols" and cur_file:
            mm = re.match(r"^\s*[-*]\s*\*\*(.+?)\*\*\s*:\s*(.+)$", line)
            if mm:
                r.columns[cur_file][mm.group(1).strip()] = mm.group(2).strip()
                continue
        mc = _CONV.match(line)
        if mc:
            name, big, fac, base = mc.groups()
            try:
                f = float(fac.replace(",", "."))
            except ValueError:
                f = None
            if f:
                r.conversions.append((name.strip(), big.strip(), f, base.strip()))
            continue
        if section == "tables":
            r.tables_note += line + "\n"
        if line.strip().startswith(("-", "*")) or section in ("conv", "other", "tables"):
            if line.strip():
                r.conventions.append(line.strip(" -*"))
    m = _END.search(text)
    if m:
        d, mo, y = map(int, m.groups())
        r.data_end = dt.date(y, mo, d)
    return r
