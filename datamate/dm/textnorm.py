"""Text normalisation for DataMate.

- fold(): lowercase, no diacritics (đ -> d), single spaces. Used to compare names and column headers.
- colkey(): folded column name with only letters and digits ('Mã hóa đơn', 'MaHoaDon', 'ma_hoa_don' -> 'mahoadon').
- qfold(): folded question with Telex typos undone and common abbreviations expanded, for intent rules.
- score_norm(): the organisers' string normalisation (diacritics kept), used to compare string answers.
"""
from __future__ import annotations

import re
import unicodedata

_TRANS = str.maketrans({"đ": "d", "Đ": "d"})


def nfc(s) -> str:
    return unicodedata.normalize("NFC", str(s))


def fold(s) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize("NFD", str(s).translate(_TRANS).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()


def colkey(s) -> str:
    return re.sub(r"[^a-z0-9]", "", fold(s))


def score_norm(s) -> str:
    s = unicodedata.normalize("NFC", str(s)).lower()
    s = "".join(c if (c.isalnum() or c.isspace()) else " " for c in s)
    return re.sub(r"\s+", " ", s).strip()


# Folded Vietnamese syllables never end in s, f, r, x, j and never contain 'w', 'dd', 'aa', 'ee', 'oo' (bar a few loan
# words), so a word that does was typed with Telex keys left in ("tieenf" -> "tien", "ddown" -> "don", "cuwar" -> "cua").
_KEEP = {"sales", "size", "store", "cash", "transfer", "ewallet", "bill", "best", "seller", "revenue", "total", "check",
         "top", "hot", "cod", "list", "orders", "order", "shopee", "lazada", "tiki", "grab", "online", "offline", "voucher",
         "xoong", "boong", "goong", "plus", "max", "pro", "lux", "box", "fax"}


def _telex_word(w: str) -> str:
    if w in _KEEP or not w.isascii() or not w.isalpha() or len(w) < 3:
        return w
    v = w
    if v[-1] in "sfrxj" and re.search(r"[aeiouy]", v[:-1]):
        v = v[:-1]
    for a, b in (("dd", "d"), ("aa", "a"), ("ee", "e"), ("oo", "o"), ("aw", "a"), ("ow", "o"), ("uw", "u")):
        v = v.replace(a, b)
    return v.replace("w", "") if "w" in v and not v.startswith("w") else v


ABBR = [
    (r"\bbest ?seller\b", "ban chay nhat"),
    (r"\brevenue\b|\bdthu\b|\bdoanh so\b", "doanh thu"),
    (r"\bbnhiu\b|\bbnh\b|\bbn\b|\bbao nhiu\b|\bnhiu\b", "bao nhieu"),
    (r"(?<!bao )\bnhieu (tien|don|ly|chai|kg|goi|hop|lon|phan|dia|cai|%)", r"bao nhieu \1"),
    (r"\bdc\b|\bdk\b|\bduoc\b", "duoc"),
    (r"\bhnay\b", "hom nay"),
    (r"\bhqua\b|\bbua qua\b|\bbua truoc\b", "hom qua"),
    (r"\btrc\b", "truoc"),
    (r"\bko\b|\bk\b|\bkhg\b|\bhok\b", "khong"),
    (r"\bsp\b", "san pham"),
    (r"\bnv\b", "nhan vien"),
    (r"\bvs\b", "voi"),
    (r"\bbill\b|\bhd\b|\bhoa don\b", "don"),
    (r"\btotal\b", "tong cong"),
    (r"\bthg\b", "thang"),
    (r"\bthanh toan bang\b", "tra bang"),
]


def qfold(q: str) -> str:
    s = re.sub(r"\s+", " ", "".join(_telex_word(t) for t in re.split(r"(\W+)", fold(q))))
    for pat, rep in ABBR:
        s = re.sub(pat, rep, s)
    return re.sub(r"\s+", " ", s).strip()
