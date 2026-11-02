"""Vietnamese surface forms of numbers, amounts and clock times.

Used by experiment D to check that a rewritten request no longer carries a removed value ("50 ngàn", "năm chục
nghìn", "2tr", "5 rưỡi", "6h chiều") and that a slot value is actually spoken in the request (not computed).
Forms are generated, not parsed; matching is whole-word on lowercase NFC text.
"""
from __future__ import annotations

import re

from .askpolicy import norm

D = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]


def _two(n: int) -> list[str]:
    """0..99 in words, with the usual variants (mươi/chục, tư/bốn, lăm/năm, mốt/một)."""
    if n < 10:
        return [D[n]]
    t, u = divmod(n, 10)
    heads = ["mười"] if t == 1 else [f"{D[t]} mươi", f"{D[t]} chục"]
    if u == 0:
        return heads
    tails = {1: ["một"] if t == 1 else ["mốt", "một"], 4: ["bốn"] if t == 1 else ["tư", "bốn"], 5: ["lăm"]}.get(u, [D[u]])
    out = [f"{h} {x}" for h in heads for x in tails]
    if t > 1:  # "hai lăm", "bốn lăm"
        out += [f"{D[t]} {x}" for x in tails]
    return out


def _three(n: int) -> list[str]:
    if n < 100:
        return _two(n)
    h, r = divmod(n, 100)
    if r == 0:
        return [f"{D[h]} trăm"]
    if r < 10:
        return [f"{D[h]} trăm {z} {D[r]}" for z in ("linh", "lẻ")]
    out = [f"{D[h]} trăm {x}" for x in _two(r)]
    if r % 10 == 0:  # "hai trăm rưỡi" style is too loose; keep "hai trăm tư" (=240) colloquial
        out.append(f"{D[h]} trăm {D[r // 10]}")
    return out


def int_words(n: int) -> list[str]:
    """Words for 0 <= n < 1e12 (nghìn/ngàn, triệu, tỷ), main variants only."""
    if n < 1000:
        return _three(n)
    for size, names in ((10**9, ["tỷ", "tỉ"]), (10**6, ["triệu"]), (10**3, ["nghìn", "ngàn"])):
        if n >= size:
            hi, lo = divmod(n, size)
            heads = [f"{w} {u}" for w in int_words(hi) for u in names]
            if lo == 0:
                return heads
            rest = int_words(lo)
            out = [f"{h} {r}" for h in heads[:2] for r in rest[:3]]
            if size >= 10**3 and lo % (size // 10) == 0:  # colloquial "hai triệu tám", "năm nghìn rưỡi"-like tails
                out += [f"{h} {D[lo // (size // 10)]}" for h in heads[:2]]
            if lo == size // 2:
                out += [f"{h} rưỡi" for h in heads[:2]]
            return out
    return [str(n)]


def amount_forms(n: int) -> set[str]:
    forms = {str(n), f"{n:,}".replace(",", "."), f"{n:,}"}
    forms |= set(int_words(n))
    if n % 1000 == 0 and n >= 1000:
        k = n // 1000
        forms |= {f"{k} nghìn", f"{k} ngàn", f"{k}k", f"{k} k"}
        if k >= 100:  # "hai trăm" for 200.000 in casual speech
            forms |= set(int_words(k))
    if n % 100000 == 0 and n >= 10**6:
        m = n / 10**6
        ms = str(int(m)) if m.is_integer() else str(m).replace(".", ",")
        forms |= {f"{ms} triệu", f"{ms}tr", f"{ms} tr", f"{ms} củ"}
    return {norm(f) for f in forms}


def small_int_forms(n: int) -> set[str]:
    return {norm(f) for f in [str(n), *int_words(n)]}


def time_forms(h: int, m: int) -> set[str]:
    """Clock time h:m (24h) as people say it: 24h and 12h hour, digits and words, rưỡi / kém."""
    out = set()
    hours = {h, h - 12} if h > 12 else {h, h + 12} if h in (0, 12) else {h}
    for hh in hours:
        if hh < 0:
            continue
        for hw in {str(hh), *_two(hh)}:
            if m == 0:
                out |= {f"{hw} giờ", f"{hw}h", f"{hw} giờ đúng"}
            else:
                for mw in {f"{m:02d}", str(m), *_two(m)}:
                    out |= {f"{hw} giờ {mw}", f"{hw}h{mw}", f"{hw}:{mw}", f"{hw} giờ {mw} phút"}
                if m == 30:
                    out |= {f"{hw} rưỡi", f"{hw} giờ rưỡi", f"{hw}h rưỡi"}
            if m in (40, 45, 50, 55):
                nxt = (hh + 1) % 24
                for nw in {str(nxt), *_two(nxt)}:
                    for kw in {str(60 - m), *_two(60 - m)}:
                        out |= {f"{nw} giờ kém {kw}", f"{nw} kém {kw}"}
    return {norm(f) for f in out}


def find_form(text: str, forms) -> str | None:
    """First form present in text as whole words (lowercase NFC), else None."""
    t = norm(text)
    for f in sorted(forms, key=len, reverse=True):
        if f and re.search(rf"(?<![\w.,]){re.escape(f)}(?![\w])", t):
            return f
    return None


def value_forms(v) -> set[str]:
    """Spoken forms of a slot value: amounts and ints, ISO datetimes / HH:MM clock times."""
    if isinstance(v, bool):
        return set()
    if isinstance(v, (int, float)) and float(v).is_integer():
        n = int(v)
        return amount_forms(n) if n >= 1000 else small_int_forms(n)
    s = str(v)
    m = re.search(r"(?:T|^)(\d{2}):(\d{2})", s)
    if m:
        return time_forms(int(m.group(1)), int(m.group(2)))
    return set()
