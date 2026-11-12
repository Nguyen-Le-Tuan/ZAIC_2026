"""Time periods of the train rulebook (§2), resolved against as_of_date. Periods are inclusive (start, end) dates.

- day(d); today; yesterday
- last_n_days(n): n consecutive days ending today
- this_week: Monday of the current week .. today; last_week: the whole previous Monday..Sunday
- month(m, y): whole month; this_month: 1st .. today; prev_month_same_days: 1st .. same day number of last month
  (or the end of last month if it has no such day)
- ytd: 1 Jan .. today; year(y)
- month_no_year(m) / quarter_no_year(q): this year unless that is after today, else last year
- tet(y): 23 tháng Chạp of lunar year y-1 .. mùng 10 tháng Giêng of lunar year y (solar dates via calendar.csv);
  before_tet(y): the same number of days right before 23 tháng Chạp
"""
from __future__ import annotations

import calendar as _cal
import csv
import datetime as dt
from functools import lru_cache

D = dt.date


def day(d: D):
    return d, d


def last_n_days(asof: D, n: int):
    return asof - dt.timedelta(days=n - 1), asof


def this_week(asof: D):
    return asof - dt.timedelta(days=asof.weekday()), asof


def last_week(asof: D):
    mon = asof - dt.timedelta(days=asof.weekday() + 7)
    return mon, mon + dt.timedelta(days=6)


def week_of(d: D):
    mon = d - dt.timedelta(days=d.weekday())
    return mon, mon + dt.timedelta(days=6)


def month(m: int, y: int):
    return D(y, m, 1), D(y, m, _cal.monthrange(y, m)[1])


def this_month(asof: D):
    return D(asof.year, asof.month, 1), asof


def prev_month(asof: D):
    y, m = (asof.year, asof.month - 1) if asof.month > 1 else (asof.year - 1, 12)
    return month(m, y)


def prev_month_same_days(asof: D):
    y, m = (asof.year, asof.month - 1) if asof.month > 1 else (asof.year - 1, 12)
    last = _cal.monthrange(y, m)[1]
    return D(y, m, 1), D(y, m, min(asof.day, last))


def shift_month(y: int, m: int, k: int):
    t = y * 12 + (m - 1) + k
    return t // 12, t % 12 + 1


def ytd(asof: D):
    return D(asof.year, 1, 1), asof


def year(y: int):
    return D(y, 1, 1), D(y, 12, 31)


def month_no_year(asof: D, m: int):
    y = asof.year if D(asof.year, m, 1) <= asof else asof.year - 1
    return month(m, y)


def quarter(q: int, y: int):
    return D(y, 3 * q - 2, 1), D(y, 3 * q, _cal.monthrange(y, 3 * q)[1])


def quarter_no_year(asof: D, q: int):
    y = asof.year if D(asof.year, 3 * q - 2, 1) <= asof else asof.year - 1
    return quarter(q, y)


def this_quarter(asof: D):
    q = (asof.month - 1) // 3 + 1
    return D(asof.year, 3 * q - 2, 1), asof


def same_period_last_year(p):
    a, b = p
    def sub(d):
        try:
            return d.replace(year=d.year - 1)
        except ValueError:
            return d.replace(year=d.year - 1, day=28)
    return sub(a), sub(b)


def previous_period(p):
    """The period of the same length right before p."""
    a, b = p
    n = (b - a).days + 1
    return a - dt.timedelta(days=n), a - dt.timedelta(days=1)


@lru_cache(maxsize=8)
def _lunar(path: str):
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows[(int(r["lunar_year"]), int(r["lunar_month"]), int(r["lunar_day"]), r.get("lunar_leap", "false") == "true")] = \
                D.fromisoformat(r["date"])
    return rows


def lunar_to_solar(cal_path: str, ly: int, lm: int, ld: int) -> D | None:
    return _lunar(cal_path).get((ly, lm, ld, False))


def tet(cal_path: str, y: int):
    a = lunar_to_solar(cal_path, y - 1, 12, 23)
    b = lunar_to_solar(cal_path, y, 1, 10)
    if a is None or b is None:
        return None
    return a, b


def before_tet(cal_path: str, y: int):
    p = tet(cal_path, y)
    if p is None:
        return None
    n = (p[1] - p[0]).days + 1
    return p[0] - dt.timedelta(days=n), p[0] - dt.timedelta(days=1)


SHIFTS = {"sang": (6, 13), "chieu": (14, 21)}   # hours inclusive: 06:00-13:59, 14:00-21:59


def overlaps(p, lo: D, hi: D) -> str:
    """'none' if p is entirely outside [lo, hi], 'part' if partly, 'all' if inside."""
    a, b = p
    if b < lo or a > hi:
        return "none"
    if a >= lo and b <= hi:
        return "all"
    return "part"
