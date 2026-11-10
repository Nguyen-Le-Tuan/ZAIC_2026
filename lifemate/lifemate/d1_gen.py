"""D1 scenario generator ("programme first, words later") for apps that have no train labels.

  python -m lifemate.d1_gen build --n 40 --seed 0 --tag t0          # gen/d1_t0_scen.jsonl (git-ignored)
  python -m lifemate.d1_gen show  --tag t0 --n 20                   # scenarios as text
  python -m lifemate.d1_gen stats --tag t0                          # label shapes next to the train labels

Code decides everything that is scored: the state of the app, what the user wants, and the label.
  state     built here from name pools (never from <split>_environment/); the app's own simulator (zaic_tools of
            public_test, which the organisers allow for synthetic data) runs every label
  intent    the write calls, the questions and the clarification, with the objects they refer to
  label     lifemate.d1_policy adds the reads that fetch IDs (canonical reader, required arguments + query), the
            convention measured on the train labels (scripts/d1_gate0.py: 92.8% of the ID reads reproduced exactly)
  checks    every call passes the schema and returns ok without done=false; every ID of a write was returned by an
            earlier read; a query finds exactly one object the user could mean (or two or more for a clarification)
An LLM only turns `say` (what the user wants, in plain Vietnamese with the exact values) into a spoken request
(lifemate.d1_say, later); `must` lists the words that request has to contain.

Context and history come from a train sample (the "shell"): its time, user, installed apps and previous turns, with
the target app added. Shells are drawn from --shells (default: all train ids).
"""
from __future__ import annotations

import argparse
import collections
import copy
import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from .d1_policy import atoms, call_key, canonical_readers, read_args, reader_index, xref_values
from .data import DEFAULT_ROOT, catalog_tools, load_catalog, load_jsonl, load_split, write_jsonl, zaic_tools

ASK = "sys.ask_missing_info"
GEN_DIR = Path("gen")
SPLIT = "public_test"      # whose catalog and simulator the scenarios use


# ---------------------------------------------------------------- time

WEEKDAYS = ["thứ hai", "thứ ba", "thứ tư", "thứ năm", "thứ sáu", "thứ bảy", "chủ nhật"]


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S+07:00")


def parse_now(ctx: dict) -> datetime:
    return datetime.fromisoformat(ctx["current_time"]).replace(tzinfo=None)


def day_phrase(now: datetime, d: datetime) -> str:
    """How a user names the day; unambiguous given the current time."""
    n = (d.date() - now.date()).days
    if n == 0:
        return "hôm nay"
    if n == 1:
        return "ngày mai"
    if n == 2:
        return "ngày kia"
    if n == -1:
        return "hôm qua"
    return f"ngày {d.day} tháng {d.month}"


def time_phrase(h: int, m: int) -> str:
    part = "sáng" if h < 11 else ("trưa" if h < 13 else ("chiều" if h < 18 else "tối"))
    h12 = h if h <= 12 else h - 12
    mm = "" if m == 0 else (" rưỡi" if m == 30 else f" {m}")
    return f"{h12} giờ{mm} {part}"


def pick_datetime(rng: random.Random, now: datetime, days=(0, 6), hours=(6, 21)) -> tuple[datetime, str]:
    """A future moment and how it is said ("7 giờ rưỡi sáng ngày mai")."""
    for _ in range(50):
        d = now + timedelta(days=rng.randint(*days))
        dt = d.replace(hour=rng.randint(*hours), minute=rng.choice([0, 0, 0, 30, 30, 15, 45]), second=0, microsecond=0)
        if dt > now + timedelta(minutes=45):
            return dt, f"{time_phrase(dt.hour, dt.minute)} {day_phrase(now, dt)}"
    dt = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    return dt, f"{time_phrase(8, 0)} ngày mai"


def money_phrase(v: int) -> str:
    if v % 1_000_000 == 0:
        return f"{v // 1_000_000} triệu"
    if v >= 1_000_000 and v % 100_000 == 0:
        return f"{v // 1_000_000} triệu {(v % 1_000_000) // 100_000}"
    return f"{v // 1000} nghìn"


# ---------------------------------------------------------------- intents

@dataclass
class Intent:
    say: str                                   # what the user wants, plain Vietnamese, «names» verbatim
    writes: list = field(default_factory=list)  # write calls, IDs filled in
    reads: list = field(default_factory=list)   # reads the scenario itself needs (questions, look-ups before asking)
    ask: dict | None = None                    # the sys.ask_missing_info call
    refs: dict = field(default_factory=dict)    # ID -> {"mention": str, "slots": {..}} for the ID read
    must: list = field(default_factory=list)    # words the request has to contain
    kind: str = "execute"                      # execute | lookup | ask
    hits: dict = field(default_factory=dict)    # call_key of a read -> how many results it must return (">=2", "1", ">=1")


def call(name: str, **args) -> dict:
    return {"name": name, "arguments": {k: v for k, v in args.items() if v is not None}}


def ids(prefix: str, n: int, rng: random.Random) -> list[str]:
    return [f"{prefix}_{i:02d}" for i in range(1, n + 1)]


# ---- pools (invented names; nothing copied from the competition files)

EVENTS = [  # name, short mention, category, venue, price
    ("Đêm nhạc Trịnh Công Sơn", "đêm nhạc Trịnh", "ca nhạc", "Nhà hát Lớn Hà Nội", 450000),
    ("Liveshow Hà Anh Tuấn - Chân Trời Rực Rỡ", "liveshow Hà Anh Tuấn", "ca nhạc", "Trung tâm Hội nghị Quốc gia", 1200000),
    ("Kịch Số Đỏ", "kịch Số Đỏ", "kịch", "Nhà hát Tuổi Trẻ", 250000),
    ("Hài kịch Tết Này Ai Đến", "Tết Này Ai Đến", "kịch", "Sân khấu Idecaf", 300000),
    ("Chung kết Cúp Quốc gia", "chung kết Cúp Quốc gia", "thể thao", "Sân vận động Mỹ Đình", 200000),
    ("Giải chạy Marathon Hồ Tây", "marathon Hồ Tây", "thể thao", "Hồ Tây", 350000),
    ("Triển lãm Tranh Sơn Mài Việt", "triển lãm tranh sơn mài", "triển lãm", "Bảo tàng Mỹ thuật Việt Nam", 80000),
    ("Phim Mùa Hè Năm Ấy", "Mùa Hè Năm Ấy", "phim", "CGV Vincom Bà Triệu", 110000),
    ("Hòa nhạc Giao hưởng Mùa Thu", "giao hưởng Mùa Thu", "hòa nhạc", "Nhà hát Thành phố", 600000),
    ("Lễ hội Âm nhạc Sóng Xanh", "Sóng Xanh", "ca nhạc", "Phố đi bộ Nguyễn Huệ", 500000),
    ("Xiếc Làng Tôi", "xiếc Làng Tôi", "xiếc", "Nhà hát Lớn Hà Nội", 700000),
    ("Triển lãm Công nghệ TechDay", "TechDay", "triển lãm", "Trung tâm Triển lãm SECC", 50000),
    ("Cải lương Tiếng Trống Mê Linh", "Tiếng Trống Mê Linh", "cải lương", "Nhà hát Trần Hữu Trang", 220000),
    ("Bóng rổ Saigon Heat gặp Hanoi Buffaloes", "Saigon Heat", "thể thao", "Nhà thi đấu CIS", 180000),
    ("Phim Người Giữ Rừng", "Người Giữ Rừng", "phim", "Lotte Cinema Gò Vấp", 95000),
    ("Hài độc thoại Sài Gòn Tếu", "Sài Gòn Tếu", "hài", "Nhà Văn hóa Thanh Niên", 280000),
    ("Múa rối nước Thăng Long", "múa rối nước", "múa rối", "Nhà hát Múa rối Thăng Long", 150000),
    ("Đêm nhạc Phú Quang - Hà Nội Phố", "đêm nhạc Phú Quang", "ca nhạc", "Cung Văn hóa Hữu nghị", 550000),
    ("Kịch Hồn Trương Ba Da Hàng Thịt", "Hồn Trương Ba", "kịch", "Nhà hát Kịch Việt Nam", 200000),
    ("Giải cầu lông Mở rộng Đà Nẵng", "giải cầu lông Mở rộng", "thể thao", "Cung Thể thao Tiên Sơn", 120000),
]
GROCERY = [  # name, mention, unit, category, price
    ("Trứng gà ta hộp 10 quả", "trứng gà ta", "hộp", "trứng", 42000), ("Trứng vịt lộn", "trứng vịt lộn", "quả", "trứng", 6000),
    ("Sữa tươi Vinamilk không đường 1 lít", "sữa tươi Vinamilk", "hộp", "sữa", 34000),
    ("Sữa tươi TH true Milk ít đường 1 lít", "sữa tươi TH", "hộp", "sữa", 36000),
    ("Rau muống", "rau muống", "bó", "rau", 9000), ("Cải thìa", "cải thìa", "bó", "rau", 12000),
    ("Thịt ba chỉ heo 500g", "thịt ba chỉ", "khay", "thịt", 85000), ("Ức gà phi lê 500g", "ức gà", "khay", "thịt", 62000),
    ("Gạo ST25 túi 5kg", "gạo ST25", "túi", "gạo", 185000), ("Nước mắm Nam Ngư 750ml", "nước mắm Nam Ngư", "chai", "gia vị", 45000),
    ("Dầu ăn Tường An 1 lít", "dầu ăn Tường An", "chai", "gia vị", 58000), ("Cà chua", "cà chua", "kg", "rau", 28000),
    ("Chuối tiêu", "chuối tiêu", "nải", "trái cây", 35000), ("Táo Envy", "táo Envy", "kg", "trái cây", 210000),
    ("Mì Hảo Hảo tôm chua cay thùng 30 gói", "mì Hảo Hảo", "thùng", "mì", 118000), ("Bánh mì sandwich", "bánh mì sandwich", "gói", "bánh", 27000),
    ("Đậu phụ", "đậu phụ", "bìa", "đậu", 5000), ("Cá hồi phi lê 300g", "cá hồi", "khay", "cá", 165000),
    ("Hành tây", "hành tây", "kg", "rau", 24000), ("Khoai tây", "khoai tây", "kg", "rau", 26000),
    ("Sữa chua Vinamilk có đường lốc 4 hộp", "sữa chua Vinamilk", "lốc", "sữa", 28000),
    ("Nước suối Lavie thùng 24 chai", "nước suối Lavie", "thùng", "nước", 92000), ("Bơ lạt Anchor 227g", "bơ lạt", "hộp", "bơ sữa", 98000),
    ("Phô mai Con Bò Cười 8 miếng", "phô mai Con Bò Cười", "hộp", "bơ sữa", 39000), ("Cam sành", "cam sành", "kg", "trái cây", 32000),
    ("Tôm sú 500g", "tôm sú", "khay", "hải sản", 175000), ("Xúc xích Đức Việt 500g", "xúc xích Đức Việt", "gói", "thịt", 69000),
    ("Nấm kim châm", "nấm kim châm", "gói", "rau", 14000), ("Bột giặt Omo 3kg", "bột giặt Omo", "túi", "gia dụng", 135000),
]
PANTRY = [("gạo", "kg"), ("trứng gà", "quả"), ("sữa tươi", "hộp"), ("mì gói", "gói"), ("nước mắm", "chai"), ("đường trắng", "kg"),
          ("muối hạt", "gói"), ("dầu ăn", "chai"), ("cà phê phin", "gói"), ("bột mì", "kg"), ("hành tím", "củ"), ("tỏi", "củ"),
          ("bơ lạt", "hộp"), ("phô mai lát", "lát"), ("xúc xích", "cây"), ("yến mạch", "gói"), ("nước tương", "chai"),
          ("bánh quy", "gói"), ("cá hộp", "hộp"), ("miến dong", "gói"), ("đậu xanh", "kg"), ("nước cốt dừa", "lon")]
HABITS = ["Uống đủ 2 lít nước", "Chạy bộ buổi sáng", "Đọc sách 30 phút", "Thiền 10 phút", "Học tiếng Anh", "Ngủ trước 11 giờ",
          "Tập yoga", "Viết nhật ký", "Đi bộ 10.000 bước", "Ăn rau xanh", "Không uống nước ngọt", "Tập gym", "Học đàn guitar",
          "Gọi điện cho bố mẹ", "Uống vitamin", "Dọn bàn làm việc"]
PHRASES = ["cho tôi một ly cà phê sữa đá", "nhà vệ sinh ở đâu", "cảm ơn bạn rất nhiều", "phòng này bao nhiêu tiền một đêm",
           "tôi bị dị ứng hải sản", "làm ơn nói chậm lại", "ga tàu ở hướng nào", "chúc mừng sinh nhật", "hẹn gặp lại ngày mai",
           "tôi muốn đổi phòng", "món này có cay không", "cho tôi xin hóa đơn", "tôi bị lạc đường", "gần đây có hiệu thuốc không",
           "mấy giờ thì cửa hàng đóng cửa", "tôi muốn đặt bàn cho bốn người", "xin lỗi vì đã đến muộn", "bạn có thể giúp tôi không",
           "tôi cần gọi taxi ra sân bay", "rất vui được gặp bạn"]
LANGS = [("en", "tiếng Anh"), ("ja", "tiếng Nhật"), ("ko", "tiếng Hàn"), ("zh", "tiếng Trung"), ("fr", "tiếng Pháp"),
         ("de", "tiếng Đức"), ("th", "tiếng Thái")]
RECIPES = [  # name, tags, servings, ingredients (name, quantity, unit)
    ("Phở bò", ["nước dùng", "bò"], 4, [("bánh phở", 800, "g"), ("thịt bò", 500, "g"), ("hành tây", 2, "củ")]),
    ("Bún chả", ["nướng", "heo"], 4, [("thịt ba chỉ", 600, "g"), ("bún tươi", 1, "kg"), ("nước mắm", 4, "thìa")]),
    ("Canh chua cá lóc", ["canh", "cá"], 4, [("cá lóc", 500, "g"), ("cà chua", 2, "quả"), ("me chua", 50, "g")]),
    ("Gà kho gừng", ["kho", "gà"], 4, [("thịt gà", 700, "g"), ("gừng", 1, "củ"), ("nước mắm", 3, "thìa")]),
    ("Súp bí đỏ", ["súp", "chay"], 2, [("bí đỏ", 400, "g"), ("kem tươi", 100, "ml"), ("hành tây", 1, "củ")]),
    ("Thịt kho tàu", ["kho", "heo"], 4, [("thịt ba chỉ", 800, "g"), ("trứng vịt", 6, "quả"), ("nước dừa", 500, "ml")]),
    ("Gỏi cuốn tôm thịt", ["cuốn", "tôm"], 4, [("tôm", 300, "g"), ("bánh tráng", 20, "cái"), ("bún tươi", 300, "g")]),
    ("Cơm rang dưa bò", ["cơm", "bò"], 2, [("cơm nguội", 2, "bát"), ("thịt bò", 200, "g"), ("dưa cải", 150, "g")]),
    ("Bánh xèo", ["bánh", "tôm"], 4, [("bột bánh xèo", 400, "g"), ("tôm", 300, "g"), ("giá đỗ", 200, "g")]),
    ("Chè đậu xanh", ["chè", "tráng miệng"], 6, [("đậu xanh", 300, "g"), ("đường", 200, "g"), ("nước cốt dừa", 200, "ml")]),
    ("Salad ức gà", ["salad", "gà"], 2, [("ức gà", 300, "g"), ("xà lách", 200, "g"), ("cà chua bi", 10, "quả")]),
    ("Mì Ý sốt bò bằm", ["mì", "bò"], 2, [("mì Ý", 200, "g"), ("thịt bò xay", 250, "g"), ("cà chua", 3, "quả")]),
    ("Cháo gà", ["cháo", "gà"], 4, [("gạo", 200, "g"), ("thịt gà", 400, "g"), ("hành lá", 3, "nhánh")]),
    ("Đậu hũ sốt cà chua", ["chay", "đậu"], 2, [("đậu hũ", 4, "bìa"), ("cà chua", 3, "quả"), ("hành lá", 2, "nhánh")]),
    ("Bò lúc lắc", ["xào", "bò"], 2, [("thịt bò", 300, "g"), ("ớt chuông", 2, "quả"), ("khoai tây", 2, "củ")]),
    ("Canh bí đao nấu tôm", ["canh", "tôm"], 4, [("bí đao", 500, "g"), ("tôm", 200, "g"), ("hành lá", 2, "nhánh")]),
    ("Nem rán", ["chiên", "heo"], 6, [("thịt heo xay", 400, "g"), ("bánh đa nem", 30, "cái"), ("miến", 50, "g")]),
    ("Lẩu thái hải sản", ["lẩu", "hải sản"], 4, [("tôm", 400, "g"), ("mực", 300, "g"), ("nấm", 200, "g")]),
]
ROUTES = [  # id, name, type, stops, fare, duration_min, headway_min
    ("bus_32", "Tuyến 32", "bus", ["Bến xe Giáp Bát", "Đại học Bách Khoa", "Hồ Gươm", "Cầu Giấy", "Nhổn"], 9000, 60, 10),
    ("bus_09", "Tuyến 09", "bus", ["Bờ Hồ", "Kim Mã", "Cầu Giấy", "Mỹ Đình"], 7000, 45, 15),
    ("metro_2a", "Metro 2A Cát Linh - Hà Đông", "metro", ["Cát Linh", "Láng", "Thượng Đình", "Văn Quán", "Yên Nghĩa"], 15000, 25, 10),
    ("metro_3", "Metro 3 Nhổn - Ga Hà Nội", "metro", ["Nhổn", "Cầu Diễn", "Cầu Giấy", "Kim Mã", "Ga Hà Nội"], 15000, 30, 10),
    ("bus_150", "Tuyến 150", "bus", ["Bến xe Chợ Lớn", "Đại học Sài Gòn", "Chợ Bến Thành", "Ngã tư Hàng Xanh", "Bến xe Miền Đông"], 7000, 55, 12),
    ("metro_1", "Metro 1 Bến Thành - Suối Tiên", "metro", ["Bến Thành", "Ba Son", "Thảo Điền", "Thủ Đức", "Suối Tiên"], 20000, 30, 8),
    ("bus_19", "Tuyến 19", "bus", ["Bến Thành", "Hàng Xanh", "Khu Công nghệ cao", "Đại học Quốc gia"], 7000, 65, 15),
    ("bus_05", "Tuyến 05", "bus", ["Bến xe Đà Nẵng", "Cầu Rồng", "Biển Mỹ Khê", "Ngũ Hành Sơn"], 8000, 40, 20),
]
LOTS = [  # name, address, area, price_per_hour
    ("Bãi xe Vincom Bà Triệu", "191 Bà Triệu", "Hai Bà Trưng", 30000), ("Bãi đỗ Tràng Tiền Plaza", "24 Hai Bà Trưng", "Hồ Gươm", 40000),
    ("Bãi xe Nhà hát Lớn", "1 Tràng Tiền", "Nhà hát Lớn", 35000), ("Bãi xe Royal City", "72A Nguyễn Trãi", "Thanh Xuân", 20000),
    ("Bãi xe sân bay Nội Bài T1", "Sân bay Nội Bài", "Nội Bài", 25000), ("Bãi xe Lotte Center", "54 Liễu Giai", "Ba Đình", 30000),
    ("Bãi xe Chợ Bến Thành", "Lê Lợi", "Bến Thành", 35000), ("Bãi xe Landmark 81", "720A Điện Biên Phủ", "Bình Thạnh", 30000),
    ("Bãi xe Bitexco", "2 Hải Triều", "Phố đi bộ Nguyễn Huệ", 45000), ("Bãi xe sân bay Tân Sơn Nhất", "Trường Sơn", "Tân Sơn Nhất", 25000),
    ("Bãi xe Cầu Rồng", "Trần Hưng Đạo", "Cầu Rồng", 15000), ("Bãi xe Bệnh viện Bạch Mai", "78 Giải Phóng", "Bạch Mai", 20000),
    ("Bãi xe Aeon Mall Long Biên", "27 Cổ Linh", "Long Biên", 10000), ("Bãi xe Đại học Bách Khoa", "1 Đại Cồ Việt", "Bách Khoa", 15000),
]
CITY_PAIRS = [("Hà Nội", "Hải Phòng"), ("Hà Nội", "Vinh"), ("Hà Nội", "Lào Cai"), ("Hà Nội", "Đà Nẵng"), ("Đà Nẵng", "Huế"),
              ("TP.HCM", "Nha Trang"), ("TP.HCM", "Đà Lạt"), ("TP.HCM", "Cần Thơ"), ("TP.HCM", "Vũng Tàu"), ("Hà Nội", "Ninh Bình"),
              ("Đà Nẵng", "Quy Nhơn"), ("Hà Nội", "Thanh Hóa")]
OPERATORS = {"train": ["Đường sắt Việt Nam SE1", "Đường sắt Việt Nam SE3", "Đường sắt Việt Nam SE7", "Đường sắt Việt Nam LP5"],
             "bus": ["Phương Trang", "Hoàng Long", "Thành Bưởi", "Sao Việt", "Kumho Samco", "Văn Minh"]}
SHOP = [  # name, mention, seller, category, price
    ("Tai nghe bluetooth Sony WH-CH520", "tai nghe Sony", "Sony Official", "điện tử", 990000),
    ("Tai nghe bluetooth JBL Tune 520", "tai nghe JBL", "JBL Store", "điện tử", 850000),
    ("Nồi chiên không dầu Philips 4 lít", "nồi chiên không dầu Philips", "Philips Home", "gia dụng", 2190000),
    ("Bình giữ nhiệt Lock&Lock 500ml", "bình giữ nhiệt Lock&Lock", "Lock&Lock VN", "gia dụng", 289000),
    ("Sạc dự phòng Anker 10000mAh", "sạc dự phòng Anker", "Anker Official", "điện tử", 459000),
    ("Áo khoác gió nam Coolmate", "áo khoác gió Coolmate", "Coolmate", "thời trang", 399000),
    ("Giày chạy bộ Biti's Hunter", "giày Biti's Hunter", "Biti's", "thời trang", 780000),
    ("Chuột không dây Logitech M331", "chuột Logitech", "Logitech VN", "điện tử", 320000),
    ("Bàn phím cơ Keychron K2", "bàn phím Keychron", "Keychron VN", "điện tử", 1890000),
    ("Máy xay sinh tố Sunhouse", "máy xay sinh tố Sunhouse", "Sunhouse", "gia dụng", 549000),
    ("Sách Đắc Nhân Tâm", "sách Đắc Nhân Tâm", "Nhà sách Fahasa", "sách", 86000),
    ("Balo laptop Mikkor", "balo Mikkor", "Mikkor", "thời trang", 450000),
    ("Đèn bàn học Rạng Đông", "đèn bàn Rạng Đông", "Rạng Đông", "gia dụng", 215000),
    ("Kem chống nắng Anessa 60ml", "kem chống nắng Anessa", "Anessa Official", "mỹ phẩm", 465000),
    ("Ốp lưng iPhone 15 trong suốt", "ốp lưng iPhone 15", "Phụ kiện Số", "điện tử", 79000),
    ("Quạt cầm tay mini Xiaomi", "quạt cầm tay Xiaomi", "Xiaomi Store", "gia dụng", 199000),
    ("Robot hút bụi Ecovacs N10", "robot hút bụi Ecovacs", "Ecovacs VN", "gia dụng", 6490000),
    ("Bộ nồi inox Sunhouse 3 chiếc", "bộ nồi Sunhouse", "Sunhouse", "gia dụng", 690000),
]
STOCKS = [("VNM", "Vinamilk", 68000), ("FPT", "FPT", 132000), ("HPG", "Hòa Phát", 27500), ("VCB", "Vietcombank", 92000),
          ("MWG", "Thế Giới Di Động", 61000), ("VIC", "Vingroup", 43000), ("TCB", "Techcombank", 24500), ("MSN", "Masan", 76000),
          ("SSI", "Chứng khoán SSI", 26800), ("VHM", "Vinhomes", 41500), ("ACB", "Ngân hàng Á Châu", 25200), ("GAS", "PV Gas", 71000),
          ("PNJ", "Vàng bạc Phú Nhuận", 98000), ("MBB", "Ngân hàng Quân đội", 23900), ("REE", "Cơ điện lạnh REE", 64000)]
REMIND = ["gọi cho mẹ", "nộp báo cáo tuần", "đón con ở trường", "mua thuốc cho bà", "tưới cây ngoài ban công", "thanh toán tiền điện",
          "mang áo mưa", "gửi hồ sơ cho phòng nhân sự", "đặt bánh sinh nhật", "kiểm tra hộp thư", "rút quần áo", "uống thuốc"]


# ---- state + intents per app. Each builder returns (state, [Intent makers]); a maker returns an Intent or None.

def app_event_tickets(rng, now, profile):
    rows = rng.sample(EVENTS, rng.randint(4, 7))
    evs = []
    for i, (name, short, cat, venue, price) in zip(ids("evt", len(rows), rng), rows):
        d = now + timedelta(days=rng.randint(1, 20))
        evs.append({"id": i, "name": name, "category": cat, "date": d.strftime("%Y-%m-%d"), "time": rng.choice(["19:30", "20:00", "18:00", "15:00", "09:00"]),
                    "venue": venue, "price": price, "available": rng.choice([12, 40, 85, 150, 300])})
    short = {e["id"]: s for e, (_, s, *_r) in zip(evs, rows)}
    state = {"events": evs, "bookings": []}

    def book():
        e = rng.choice(evs); q = rng.choice([1, 2, 2, 3, 4])
        return Intent(f"đặt {q} vé sự kiện «{short[e['id']]}»", [call("event_tickets.book", event_id=e["id"], quantity=q)],
                      refs={e["id"]: {"mention": short[e["id"]]}}, must=[short[e["id"]]])

    def book_two():
        a, b = rng.sample(evs, 2); qa, qb = rng.choice([1, 2, 3]), rng.choice([1, 2, 4])
        return Intent(f"đặt {qa} vé «{short[a['id']]}» và {qb} vé «{short[b['id']]}»",
                      [call("event_tickets.book", event_id=a["id"], quantity=qa), call("event_tickets.book", event_id=b["id"], quantity=qb)],
                      refs={a["id"]: {"mention": short[a["id"]]}, b["id"]: {"mention": short[b["id"]]}}, must=[short[a["id"]], short[b["id"]]])

    def look():
        if rng.random() < 0.3:
            return Intent("hỏi hiện đang có những sự kiện nào", reads=[call("event_tickets.search")], kind="lookup")
        e = rng.choice(evs)
        key, what = rng.choice([(e["category"], f"có sự kiện «{e['category']}» nào"), (short[e["id"]], f"sự kiện «{short[e['id']]}» diễn ra khi nào, giá vé bao nhiêu")])
        return Intent(f"hỏi {what}", reads=[call("event_tickets.search", query=key)], must=[key], kind="lookup")

    def ask():
        cats = collections.Counter(e["category"] for e in evs)
        cat = next((c for c, n in cats.items() if n >= 2), None)
        if cat is None:
            return None
        q = rng.choice([2, 3])
        r = call("event_tickets.search", query=cat)
        return Intent(f"đặt {q} vé xem «{cat}» (không nói sự kiện nào)", reads=[r], ask=call(ASK, tool_name="event_tickets.book", params=["event_id"]),
                      must=[cat], kind="ask", hits={call_key(r): ">=2"})
    return state, {"execute": [book, book, book_two], "lookup": [look], "ask": [ask]}


def _products(rows, rng, prefix, extra):
    out, short = [], {}
    for i, row in zip(ids(prefix, len(rows), rng), rows):
        p = {"id": i, **extra(row)}
        out.append(p)
        short[i] = row[1]
    return out, short


def shared_head(prods: list[dict], rng) -> str | None:
    """First two words that two or more product names start with ("tai nghe", "sữa tươi"): what a user says when he
    does not name the brand."""
    heads = collections.defaultdict(int)
    for p in prods:
        heads[" ".join(p["name"].split()[:2]).lower()] += 1
    cands = sorted(h for h, n in heads.items() if n >= 2)
    return rng.choice(cands) if cands else None


def app_grocery(rng, now, profile):
    rows = rng.sample(GROCERY, rng.randint(6, 10))
    prods, short = _products(rows, rng, "prod", lambda r: {"name": r[0], "price": r[4], "unit": r[2], "category": r[3], "in_stock": True})
    state = {"products": prods, "cart": [], "orders": []}

    def add(n=1, checkout=False):
        ps = rng.sample(prods, n)
        qs = [rng.choice([1, 2, 2, 3, 5]) for _ in ps]
        ws = [call("grocery.add_to_cart", product_id=p["id"], quantity=q) for p, q in zip(ps, qs)]
        say = "thêm vào giỏ đi chợ: " + ", ".join(f"{q} {p['unit']} «{short[p['id']]}»" for p, q in zip(ps, qs))
        if checkout:
            when = None
            if rng.random() < 0.35:
                dt, ph = pick_datetime(rng, now, days=(0, 2), hours=(8, 20))
                when = iso(dt)
                say += f", rồi đặt hàng luôn, giao lúc {ph}"
            else:
                say += ", rồi đặt hàng luôn"
            ws.append(call("grocery.checkout", delivery_time=when))
        return Intent(say, ws, refs={p["id"]: {"mention": short[p["id"]]} for p in ps}, must=[short[p["id"]] for p in ps])

    def look():
        p = rng.choice(prods)
        key = rng.choice([short[p["id"]], p["category"]])
        return Intent(f"hỏi app đi chợ có bán «{key}» không, giá bao nhiêu", reads=[call("grocery.search", query=key)], must=[key], kind="lookup")

    def ask():
        cat = shared_head(prods, rng)
        if cat is None:
            return None
        r = call("grocery.search", query=cat)
        return Intent(f"thêm 2 phần «{cat}» vào giỏ đi chợ (không nói nhãn hiệu hay loại nào)", reads=[r],
                      ask=call(ASK, tool_name="grocery.add_to_cart", params=["product_id"]), must=[cat], kind="ask", hits={call_key(r): ">=2"})
    return state, {"execute": [add, add, lambda: add(2), lambda: add(1, True), lambda: add(2, True)], "lookup": [look], "ask": [ask]}


def app_pantry(rng, now, profile):
    rows = rng.sample(PANTRY, rng.randint(6, 10))
    items = [{"id": i, "name": n, "stock": rng.choice([2, 3, 5, 6, 10, 12]), "unit": u} for i, (n, u) in zip(ids("item", len(rows), rng), rows)]
    state = {"items": items}

    def use(n=1):
        its = rng.sample(items, n)
        qs = [rng.randint(1, min(4, it["stock"])) for it in its]
        return Intent("ghi nhận vừa dùng hết: " + ", ".join(f"{q} {it['unit']} «{it['name']}»" for it, q in zip(its, qs)) + " trong tủ bếp",
                      [call("pantry.consume", item_id=it["id"], quantity=q) for it, q in zip(its, qs)],
                      refs={it["id"]: {"mention": it["name"]} for it in its}, must=[it["name"] for it in its])

    def look():
        it = rng.choice(items)
        what = rng.choice([f"trong tủ bếp còn bao nhiêu «{it['name']}»", "trong tủ bếp còn những gì"])
        return Intent(f"hỏi {what}", reads=[call("pantry.list_items")], must=[it["name"]] if "«" in what else [], kind="lookup")

    def ask():
        it = rng.choice(items)
        return Intent(f"ghi nhận vừa dùng «{it['name']}» trong tủ bếp (không nói dùng bao nhiêu)", reads=[call("pantry.list_items")],
                      ask=call(ASK, tool_name="pantry.consume", params=["quantity"]), must=[it["name"]], kind="ask")
    return state, {"execute": [use, use, lambda: use(2)], "lookup": [look], "ask": [ask]}


def app_habit_tracker(rng, now, profile):
    rows = rng.sample(HABITS, rng.randint(4, 7))
    habits = [{"id": i, "name": n, "streak": rng.choice([0, 1, 3, 5, 12, 20]),
               "last_logged": (now - timedelta(days=rng.choice([1, 2, 2, 3, 5]))).strftime("%Y-%m-%d")} for i, n in zip(ids("habit", len(rows), rng), rows)]
    state = {"habits": habits, "logs": []}

    def log(n=1):
        hs = rng.sample(habits, n)
        d = now - timedelta(days=rng.choice([0, 0, 0, 1]))
        day = d.strftime("%Y-%m-%d")
        if any(h["last_logged"] >= day for h in hs):
            d, day = now, now.strftime("%Y-%m-%d")
        return Intent(f"đánh dấu {day_phrase(now, d)} đã làm thói quen: " + ", ".join(f"«{h['name']}»" for h in hs),
                      [call("habit_tracker.log", habit_id=h["id"], date=day) for h in hs],
                      refs={h["id"]: {"mention": h["name"]} for h in hs}, must=[h["name"] for h in hs])

    def look():
        h = rng.choice(habits)
        what = rng.choice([f"chuỗi ngày của thói quen «{h['name']}» đang là bao nhiêu", "đang theo dõi những thói quen nào"])
        return Intent(f"hỏi {what}", reads=[call("habit_tracker.list_habits")], must=[h["name"]] if "«" in what else [], kind="lookup")
    return state, {"execute": [log, log, lambda: log(2)], "lookup": [look], "ask": []}


def app_translator(rng, now, profile):
    def tr():
        text = rng.choice(PHRASES); code, lang = rng.choice(LANGS)
        return Intent(f"nhờ dịch câu «{text}» sang {lang}", reads=[call("translator.translate", text=text, to_lang=code)], must=[text], kind="lookup")
    return {}, {"execute": [], "lookup": [tr], "ask": []}


def app_recipes(rng, now, profile):
    rows = rng.sample(RECIPES, rng.randint(5, 8))
    recs = [{"id": i, "name": n, "tags": tags, "servings": sv, "ingredients": [{"name": a, "quantity": q, "unit": u} for a, q, u in ing],
             "steps": ["Sơ chế nguyên liệu", "Nấu theo hướng dẫn", "Nêm nếm và trình bày"]} for i, (n, tags, sv, ing) in zip(ids("rec", len(rows), rng), rows)]
    state = {"recipes": recs, "saved": []}

    def save():
        r = rng.choice(recs)
        return Intent(f"lưu công thức món «{r['name']}»", [call("recipes.save", recipe_id=r["id"])], refs={r["id"]: {"mention": r["name"]}}, must=[r["name"]])

    def look():
        r = rng.choice(recs)
        if rng.random() < 0.4:
            n = rng.choice([x for x in (2, 3, 5, 6, 8, 10) if x != r["servings"]])
            return Intent(f"hỏi nấu món «{r['name']}» cho {n} người thì cần những nguyên liệu gì", reads=[call("recipes.search", query=r["name"], servings=n)],
                          must=[r["name"]], kind="lookup")
        return Intent(f"hỏi công thức món «{r['name']}»", reads=[call("recipes.search", query=r["name"])], must=[r["name"]], kind="lookup")
    return state, {"execute": [save], "lookup": [look, look], "ask": []}


def app_public_transit(rng, now, profile):
    routes = rng.sample(ROUTES, rng.randint(3, 5))
    rs = [{"id": i, "name": n, "type": t, "stops": st, "fare": f, "duration_min": d, "headway_min": h} for i, n, t, st, f, d, h in routes]
    deps = []
    for r in rs:
        for stop in rng.sample(r["stops"], 2):
            t0 = now + timedelta(minutes=rng.randint(3, 20))
            deps += [{"stop": stop, "route": r["id"], "time": iso(t0 + timedelta(minutes=k * r["headway_min"]))} for k in range(3)]
    state = {"card_balance": rng.choice([0, 15000, 42000, 100000]), "routes": rs, "departures": deps, "topups": []}

    def topup():
        amt = rng.choice([50000, 100000, 100000, 200000, 300000, 500000])
        return Intent(f"nạp {money_phrase(amt)} đồng vào thẻ đi xe buýt, metro", [call("public_transit.topup_card", amount=amt)])

    def look():
        r = rng.choice(rs)
        if rng.random() < 0.5:
            a, b = sorted(rng.sample(range(len(r["stops"])), 2))
            o, d = r["stops"][a], r["stops"][b]
            return Intent(f"hỏi đi xe buýt hoặc metro từ «{o}» đến «{d}» thì đi tuyến nào", reads=[call("public_transit.find_routes", origin=o, destination=d)],
                          must=[o, d], kind="lookup")
        stop = rng.choice(sorted({d["stop"] for d in deps if d["route"] == r["id"]}))
        return Intent(f"hỏi mấy giờ có chuyến kế tiếp ở trạm «{stop}»", reads=[call("public_transit.next_departures", stop=stop)], must=[stop], kind="lookup")

    def ask():
        return Intent("nạp tiền vào thẻ đi xe buýt (không nói số tiền)", ask=call(ASK, tool_name="public_transit.topup_card", params=["amount"]), kind="ask")
    return state, {"execute": [topup], "lookup": [look, look], "ask": [ask]}


def app_parking(rng, now, profile):
    rows = rng.sample(LOTS, rng.randint(3, 6))
    lots = [{"id": i, "name": n, "address": a, "area": ar, "price_per_hour": p, "available_spots": rng.choice([3, 8, 20, 45])}
            for i, (n, a, ar, p) in zip(ids("lot", len(rows), rng), rows)]
    sessions = []
    if rng.random() < 0.6:
        for i, lot in zip(ids("park", rng.randint(1, 2), rng), rng.sample(lots, min(2, len(lots)))):
            st = now - timedelta(hours=rng.randint(1, 3))
            sessions.append({"id": i, "lot_id": lot["id"], "from_time": iso(st.replace(minute=0, second=0, microsecond=0)), "hours": 4,
                             "end_time": iso(st.replace(minute=0, second=0, microsecond=0) + timedelta(hours=4)), "total": lot["price_per_hour"] * 4, "status": "reserved"})
    state = {"lots": lots, "sessions": sessions}

    def reserve():
        lot = rng.choice(lots)
        dt, ph = pick_datetime(rng, now, days=(0, 3), hours=(7, 20))
        h = rng.choice([1, 2, 2, 3, 4])
        return Intent(f"đặt chỗ đỗ xe gần «{lot['area']}» từ {ph}, trong {h} tiếng", [call("parking.reserve", lot_id=lot["id"], from_time=iso(dt), hours=h)],
                      refs={lot["id"]: {"mention": lot["area"], "slots": {"near": lot["area"]}}}, must=[lot["area"]])

    def end():
        if not sessions:
            return None
        s = rng.choice(sessions)
        name = next(l["name"] for l in lots if l["id"] == s["lot_id"])
        return Intent(f"kết thúc phiên đỗ xe ở «{name}»", [call("parking.end_session", session_id=s["id"])], refs={s["id"]: {"mention": name}}, must=[name])

    def look():
        if sessions and rng.random() < 0.4:
            return Intent("hỏi mình đang có những chỗ đỗ xe nào đã đặt", reads=[call("parking.list_sessions")], kind="lookup")
        lot = rng.choice(lots)
        return Intent(f"hỏi gần «{lot['area']}» có bãi đỗ xe nào, giá bao nhiêu", reads=[call("parking.find", near=lot["area"])], must=[lot["area"]], kind="lookup")

    def ask():
        lot = rng.choice(lots)
        dt, ph = pick_datetime(rng, now, days=(0, 3), hours=(7, 20))
        r = call("parking.find", near=lot["area"])
        return Intent(f"đặt chỗ đỗ xe gần «{lot['area']}» từ {ph} (không nói đỗ bao lâu)", reads=[r],
                      ask=call(ASK, tool_name="parking.reserve", params=["hours"]), must=[lot["area"]], kind="ask")
    return state, {"execute": [reserve, reserve, end], "lookup": [look], "ask": [ask]}


def app_train_bus_tickets(rng, now, profile):
    trips, n = [], 0
    pairs = rng.sample(CITY_PAIRS, rng.randint(2, 3))
    for o, d in pairs:
        day = now + timedelta(days=rng.randint(1, 9))
        for hh in rng.sample([5, 6, 7, 9, 11, 13, 15, 19, 21, 22], rng.randint(2, 3)):
            n += 1
            typ = rng.choice(["train", "bus"])
            trips.append({"id": f"trip_{n:02d}", "type": typ, "operator": rng.choice(OPERATORS[typ]), "origin": o, "destination": d,
                          "date": day.strftime("%Y-%m-%d"), "depart": f"{hh:02d}:{rng.choice(['00', '30'])}", "arrive": f"{(hh + rng.randint(2, 9)) % 24:02d}:15",
                          "price": rng.choice([120000, 180000, 250000, 320000, 480000, 650000]), "seats_left": rng.choice([4, 9, 20, 36])})
    bookings = []
    if rng.random() < 0.5:
        t = rng.choice(trips)
        bookings.append({"id": "tk_01", "trip_id": t["id"], "seats": 2, "total": t["price"] * 2, "status": "confirmed"})
    state = {"trips": trips, "bookings": bookings}

    def _day(t):
        return datetime.strptime(t["date"], "%Y-%m-%d")

    def book():
        t = rng.choice(trips); seats = rng.choice([1, 2, 2, 3])
        hh, mm = map(int, t["depart"].split(":"))
        kind = "tàu" if t["type"] == "train" else "xe khách"
        return Intent(f"đặt {seats} vé {kind} từ «{t['origin']}» đi «{t['destination']}» {day_phrase(now, _day(t))}, chuyến khởi hành lúc {time_phrase(hh, mm)}",
                      [call("train_bus_tickets.book", trip_id=t["id"], seats=seats)],
                      refs={t["id"]: {"mention": None, "slots": {"origin": t["origin"], "destination": t["destination"], "date": t["date"]}}},
                      must=[t["origin"], t["destination"]])

    def cancel():
        if not bookings:
            return None
        b = bookings[0]
        return Intent("huỷ vé tàu xe đã đặt", [call("train_bus_tickets.cancel", booking_id=b["id"])], refs={b["id"]: {"mention": None}})

    def look():
        if bookings and rng.random() < 0.3:
            return Intent("hỏi mình đã đặt những vé tàu xe nào", reads=[call("train_bus_tickets.my_bookings")], kind="lookup")
        t = rng.choice(trips)
        return Intent(f"hỏi {day_phrase(now, _day(t))} có những chuyến tàu xe nào từ «{t['origin']}» đi «{t['destination']}»",
                      reads=[call("train_bus_tickets.search", origin=t["origin"], destination=t["destination"], date=t["date"])],
                      must=[t["origin"], t["destination"]], kind="lookup")

    def ask():
        t = rng.choice(trips)
        hh, mm = map(int, t["depart"].split(":"))
        r = call("train_bus_tickets.search", origin=t["origin"], destination=t["destination"], date=t["date"])
        return Intent(f"đặt vé {'tàu' if t['type'] == 'train' else 'xe khách'} từ «{t['origin']}» đi «{t['destination']}» {day_phrase(now, _day(t))}, "
                      f"chuyến khởi hành lúc {time_phrase(hh, mm)} (không nói mấy vé)", reads=[r],
                      ask=call(ASK, tool_name="train_bus_tickets.book", params=["seats"]), must=[t["origin"], t["destination"]], kind="ask")
    return state, {"execute": [book, book, cancel], "lookup": [look], "ask": [ask]}


def app_ecommerce(rng, now, profile):
    rows = rng.sample(SHOP, rng.randint(5, 8))
    prods, short = _products(rows, rng, "sp", lambda r: {"name": r[0], "price": r[4], "seller": r[2], "category": r[3], "rating": rng.choice([4.2, 4.5, 4.7, 4.9]), "in_stock": True})
    orders = []
    for i, (p, status) in enumerate(zip(rng.sample(prods, min(3, len(prods))), rng.sample(["placed", "shipping", "delivered", "delivered"], 3)), 1):
        o = {"id": f"dh_{i:02d}", "items": [{"product_id": p["id"], "name": p["name"], "price": p["price"], "quantity": 1}], "total": p["price"],
             "status": status, "placed_at": iso(now - timedelta(days=rng.randint(1, 9)))}
        if status == "delivered":
            o["delivered_at"] = iso(now - timedelta(hours=rng.randint(3, 40)))
        orders.append(o)
    state = {"products": prods, "cart": [], "orders": orders, "returns": []}
    oname = {o["id"]: short[o["items"][0]["product_id"]] for o in orders}

    def add(checkout=False):
        p = rng.choice(prods); q = rng.choice([1, 1, 1, 2])
        ws = [call("ecommerce.add_to_cart", product_id=p["id"], quantity=q)]
        say = f"thêm {q} cái «{short[p['id']]}» vào giỏ hàng trên sàn mua sắm"
        if checkout:
            pay = rng.choice([None, None, "ewallet", "bank"])
            say += ", rồi đặt hàng luôn" + ({"ewallet": ", thanh toán bằng ví điện tử", "bank": ", thanh toán chuyển khoản ngân hàng"}.get(pay, ""))
            ws.append(call("ecommerce.checkout", payment=pay))
        return Intent(say, ws, refs={p["id"]: {"mention": short[p["id"]]}}, must=[short[p["id"]]])

    def cancel():
        os_ = [o for o in orders if o["status"] in ("placed", "shipping")]
        if not os_:
            return None
        o = rng.choice(os_)
        return Intent(f"huỷ đơn hàng «{oname[o['id']]}» đã đặt trên sàn mua sắm", [call("ecommerce.cancel_order", order_id=o["id"])],
                      refs={o["id"]: {"mention": None}}, must=[oname[o["id"]]])

    def ret():
        os_ = [o for o in orders if o["status"] == "delivered"]
        if not os_:
            return None
        o = rng.choice(os_)
        reason, why = rng.choice([("wrong_item", "shop giao sai hàng"), ("damaged", "hàng bị hỏng"), ("changed_mind", "đổi ý, không cần nữa")])
        return Intent(f"yêu cầu trả hàng đơn «{oname[o['id']]}» vì {why}", [call("ecommerce.request_return", order_id=o["id"], reason=reason)],
                      refs={o["id"]: {"mention": None}}, must=[oname[o["id"]]])

    def look():
        if rng.random() < 0.5:
            return Intent("hỏi các đơn hàng trên sàn mua sắm đang ở trạng thái nào", reads=[call("ecommerce.order_status")], kind="lookup")
        p = rng.choice(prods)
        if rng.random() < 0.35:
            cap = rng.choice([x for x in (300000, 500000, 1000000, 2000000, 3000000) if x >= p["price"]] or [10000000])
            return Intent(f"tìm «{p['category']}» trên sàn mua sắm giá dưới {money_phrase(cap)}", reads=[call("ecommerce.search", query=p["category"], max_price=cap)],
                          must=[p["category"]], kind="lookup")
        return Intent(f"hỏi trên sàn mua sắm «{short[p['id']]}» giá bao nhiêu", reads=[call("ecommerce.search", query=short[p["id"]])], must=[short[p["id"]]], kind="lookup")

    def ask():
        head = shared_head(prods, rng)
        if head is None:
            return None
        r = call("ecommerce.search", query=head)
        return Intent(f"thêm 1 cái «{head}» vào giỏ hàng trên sàn mua sắm (không nói hãng hay mẫu nào)", reads=[r],
                      ask=call(ASK, tool_name="ecommerce.add_to_cart", params=["product_id"]), must=[head], kind="ask", hits={call_key(r): ">=2"})
    return state, {"execute": [add, add, lambda: add(True), cancel, ret], "lookup": [look], "ask": [ask]}


def app_stocks(rng, now, profile):
    rows = rng.sample(STOCKS, rng.randint(6, 9))
    quotes = [{"symbol": s, "name": n, "price": p, "change_pct": rng.choice([-2.1, -0.8, 0.0, 0.6, 1.4, 3.2])} for s, n, p in rows]
    held = rng.sample(rows, 3)
    holdings = [{"symbol": s, "name": n, "quantity": rng.choice([100, 200, 500, 1000]), "avg_price": int(p * rng.choice([0.9, 0.95, 1.05])), "price": p} for s, n, p in held]
    state = {"holdings": holdings, "orders": [], "alerts": [], "quotes": quotes}

    def order():
        side = rng.choice(["buy", "buy", "sell"])
        if side == "sell":
            h = rng.choice(holdings); sym = h["symbol"]; q = rng.choice([x for x in (100, 200, 500) if x <= h["quantity"]])
        else:
            sym = rng.choice(quotes)["symbol"]; q = rng.choice([100, 200, 300, 500, 1000])
        price = None
        say = f"đặt lệnh {'mua' if side == 'buy' else 'bán'} {q} cổ phiếu mã «{sym}»"
        if rng.random() < 0.3:
            base = next(x["price"] for x in quotes + holdings if x["symbol"] == sym)
            price = int(round(base * rng.choice([0.97, 0.99, 1.01, 1.03]), -2))
            say += f" với giá {price} đồng một cổ"
        return Intent(say, [call("stocks.place_order", symbol=sym, side=side, quantity=q, price=price)], must=[sym])

    def alert():
        q = rng.choice(quotes); d = rng.choice(["above", "below"])
        price = int(round(q["price"] * (1.05 if d == "above" else 0.95), -2))
        return Intent(f"đặt cảnh báo khi giá cổ phiếu mã «{q['symbol']}» {'lên trên' if d == 'above' else 'xuống dưới'} {price} đồng",
                      [call("stocks.set_price_alert", symbol=q["symbol"], price=price, direction=d)], must=[q["symbol"]])

    def look():
        if rng.random() < 0.35:
            return Intent("hỏi danh mục cổ phiếu của mình đang có những mã nào", reads=[call("stocks.get_portfolio")], kind="lookup")
        q = rng.choice(quotes)
        return Intent(f"hỏi giá cổ phiếu mã «{q['symbol']}» hôm nay", reads=[call("stocks.get_quote", symbol=q["symbol"])], must=[q["symbol"]], kind="lookup")

    def ask():
        q = rng.choice(quotes)
        if rng.random() < 0.5:
            return Intent(f"đặt lệnh mua cổ phiếu mã «{q['symbol']}» (không nói mua bao nhiêu)",
                          ask=call(ASK, tool_name="stocks.place_order", params=["quantity"]), must=[q["symbol"]], kind="ask")
        return Intent(f"đặt cảnh báo giá cho cổ phiếu mã «{q['symbol']}» khi giá lên (không nói mức giá)",
                      ask=call(ASK, tool_name="stocks.set_price_alert", params=["price"]), must=[q["symbol"]], kind="ask")
    return state, {"execute": [order, order, alert], "lookup": [look], "ask": [ask]}


APPS = {"event_tickets": app_event_tickets, "grocery": app_grocery, "pantry": app_pantry, "habit_tracker": app_habit_tracker,
        "translator": app_translator, "recipes": app_recipes, "public_transit": app_public_transit, "parking": app_parking,
        "train_bus_tickets": app_train_bus_tickets, "ecommerce": app_ecommerce, "stocks": app_stocks}


# ---- side intents on apps the train labels already cover (their conventions are in the train labels)

def side_intents(rng, now):
    def alarm():
        dt, ph = pick_datetime(rng, now, days=(0, 2), hours=(5, 22))
        return "alarm", Intent(f"đặt báo thức lúc {ph}", [call("alarm.create", time=iso(dt))])

    def remind():
        dt, ph = pick_datetime(rng, now, days=(0, 4), hours=(7, 21))
        what = rng.choice(REMIND)
        return "reminders", Intent(f"nhắc mình «{what}» lúc {ph}", [call("reminders.create", content=what, time=iso(dt))], must=[what])

    def remind_ask():
        what = rng.choice(REMIND)
        return "reminders", Intent(f"nhắc mình «{what}» (không nói nhắc lúc nào)", ask=call(ASK, tool_name="reminders.create", params=["time"]), must=[what], kind="ask")
    return {"execute": [alarm, remind], "ask": [remind_ask]}


# ---------------------------------------------------------------- label + checks

def assemble(intents: list[Intent], tools: dict, idx: dict) -> tuple[list[dict], dict]:
    """The label: per intent its own reads, then per write the ID reads the policy adds, the clarification last."""
    calls, seen, known, hits, ask = [], set(), set(), {}, None

    def add(c):
        k = call_key(c)
        if c["name"] != ASK and tools[c["name"]]["kind"] == "read":
            if k in seen:
                return
            seen.add(k)
        calls.append(c)

    for it in intents:
        hits.update(it.hits)
        for r in it.reads:
            add(r)
        for w in it.writes:
            for _, col, v in xref_values(tools[w["name"]], w["arguments"]):
                if str(v) in known:
                    continue
                ref = it.refs.get(v) or {}
                reader = tools[canonical_readers(col, tools, idx)[0]]
                args = read_args(reader, {"name": ref.get("mention")} if ref.get("mention") else None, ref.get("slots"))
                if args is None:
                    raise ValueError(f"cannot fill {reader['name']} for {col}")
                r = {"name": reader["name"], "arguments": args}
                add(r)
                hits.setdefault(call_key(r), "has:" + str(v))
                known.add(str(v))
            add(w)
        if it.ask is not None:
            if ask is not None:
                raise ValueError("two clarifications in one sample")
            ask = it.ask
    if ask is not None:
        calls.append(ask)
    return calls, hits


def list_items(result) -> list:
    return [x for v in result.values() if isinstance(v, list) for x in v] if isinstance(result, dict) else []


def check(calls, results, hits, tools) -> str | None:
    """None when the label runs as a gold label does; otherwise why not."""
    shown = set()
    for c, r in zip(calls, results):
        if not isinstance(r, dict) or r.get("ok") is not True:
            return f"schema: {c['name']} -> {str(r)[:120]}"
        if r.get("done") is False:
            return f"noop: {c['name']} -> {r.get('message')}"
        if c["name"] == ASK:
            continue
        t = tools[c["name"]]
        if t["kind"] == "write":
            for _, _, v in xref_values(t, c["arguments"]):
                if str(v) not in shown:
                    return f"invented_id: {c['name']} {v}"
        else:
            want = hits.get(call_key(c))
            items = list_items(r)
            if want and want.startswith("has:") and want[4:] not in atoms(r):
                return f"id_not_returned: {c['name']} {c['arguments']} misses {want[4:]}"
            if want and want.startswith("has:") and ({"query", "near"} & set(c["arguments"])) and len(items) != 1:
                return f"ambiguous_query: {c['name']} {c['arguments']} -> {len(items)} results"
            if want == ">=2" and len(items) < 2:
                return f"not_ambiguous: {c['name']} {c['arguments']} -> {len(items)}"
            if c["arguments"] and any(isinstance(v, list) for v in r.values()) and not items:
                return f"empty_read: {c['name']} {c['arguments']}"
        atoms(r, shown)
    return None


def build_one(rng: random.Random, sid: str, app: str, shell: dict, cat: dict, tools: dict, idx: dict, zt, weights) -> dict:
    apps_by_id = {a["id"]: a for a in cat["apps"]}
    ctx = copy.deepcopy(shell["context"])
    now = parse_now(ctx)
    state, makers = APPS[app](rng, now, ctx.get("user_profile", {}))
    kinds = [k for k in weights if makers.get(k.split("+")[0]) or k == "not_installed"]
    kind = rng.choices(kinds, [weights[k] for k in kinds])[0]
    base = "execute" if kind == "not_installed" and makers["execute"] else ("lookup" if kind == "not_installed" else kind.split("+")[0])
    main = None
    for _ in range(20):
        main = rng.choice(makers[base])()
        if main is not None:
            break
    if main is None:
        raise ValueError(f"{app}: no {base} intent")
    intents, extra_apps = [main], []
    if "+" in kind:
        side_app, side = rng.choice(side_intents(rng, now)["ask" if kind.endswith("+askside") else "execute"])()
        extra_apps.append(side_app)
        intents = [main, side] if rng.random() < 0.5 else [side, main]
    # installed apps: the shell's own (as the shell lists them: its history may use them), plus the target and side app
    inst = {a: v for a, v in ctx["installed_apps"].items() if a != app}
    for a in extra_apps + ([app] if kind != "not_installed" else []):
        inst[a] = {"tools": [t["name"] for t in apps_by_id[a]["tools"]]}
    order = list(inst)
    rng.shuffle(order)
    ctx["installed_apps"] = {a: inst[a] for a in order}
    if kind == "not_installed":
        calls, hits, results = [], {}, []
    else:
        calls, hits = assemble(intents, tools, idx)
        sim_apps = {a: {"tools": ctx["installed_apps"][a]["tools"], "state": copy.deepcopy(state) if a == app else {}} for a in [app] + extra_apps}
        sim = zt.executor.Simulator({"context": {"current_time": ctx["current_time"], "installed_apps": sim_apps}}, cat)
        results = [sim.call(c["name"], c["arguments"]) for c in calls]
        err = check(calls, results, hits, tools)
        if err:
            raise ValueError(err)
    return {"id": sid, "app": app, "kind": kind, "shell": shell["id"], "context": ctx, "history": shell.get("history", []),
            "state": {app: state}, "say": [it.say for it in intents], "must": [m for it in intents for m in it.must],
            "calls": calls, "results": results}


WEIGHTS = {"execute": 36, "execute+side": 28, "lookup": 7, "lookup+side": 4, "ask": 10, "execute+askside": 6, "not_installed": 7}


def shape(calls: list[dict], tools: dict) -> str:
    out = []
    for c in calls:
        out.append("A" if c["name"] == ASK else ("W" if tools[c["name"]]["kind"] == "write" else "r"))
    return "".join(out) or "(rong)"


def cmd_build(a):
    rng = random.Random(a.seed)
    cat = load_catalog(SPLIT)
    tools, idx = catalog_tools(cat), reader_index(catalog_tools(cat))
    zt = zaic_tools(SPLIT)
    shells = load_split("train")
    if a.shells:
        keep = {l.strip() for l in Path(a.shells).read_text().split() if l.strip()}
        shells = [s for s in shells if s["id"] in keep]
    apps = a.apps.split(",") if a.apps else list(APPS)
    out, fails = [], collections.Counter()
    for app in apps:
        got = tries = 0
        while got < a.n and tries < a.n * 30:
            tries += 1
            try:
                g = build_one(rng, f"d1_{a.tag}_{app}_{got:04d}", app, rng.choice(shells), cat, tools, idx, zt, WEIGHTS)
            except ValueError as e:
                fails[f"{app}: {str(e).split(':')[0]}"] += 1
                continue
            out.append(g)
            got += 1
    GEN_DIR.mkdir(exist_ok=True)
    path = GEN_DIR / f"d1_{a.tag}_scen.jsonl"
    write_jsonl(path, out)
    print(f"{len(out)} scenarios -> {path}")
    print("rejected while building:", dict(fails))
    print("kinds:", dict(collections.Counter(g["kind"] for g in out)))
    print("shapes:", collections.Counter(shape(g["calls"], tools) for g in out).most_common(12))


def cmd_show(a):
    rows = load_jsonl(GEN_DIR / f"d1_{a.tag}_scen.jsonl")
    rng = random.Random(a.seed)
    for g in rng.sample(rows, min(a.n, len(rows))):
        print(f"\n## {g['id']} [{g['kind']}] now={g['context']['current_time']} history_turns={len(g['history'])} installed={len(g['context']['installed_apps'])}")
        for s in g["say"]:
            print("   muốn:", s)
        for c, r in zip(g["calls"], g["results"]):
            print("   ", json.dumps(c, ensure_ascii=False), "=>", json.dumps(r, ensure_ascii=False)[:150])


def cmd_stats(a):
    rows = load_jsonl(GEN_DIR / f"d1_{a.tag}_scen.jsonl")
    tools = catalog_tools(load_catalog(SPLIT))
    ttools = catalog_tools(load_catalog("train"))
    real = load_split("train")
    n = len(rows)
    print(f"{n} scenarios; per app: {dict(collections.Counter(g['app'] for g in rows))}")
    for name, xs, tl in (("generated", [g["calls"] for g in rows], tools), ("train labels", [s["label"]["tool_calls"] for s in real], ttools)):
        m = len(xs)
        kinds = collections.Counter("empty" if not c else ("ask" if any(x["name"] == ASK for x in c) else
                                    ("lookup" if all(tl[x["name"]]["kind"] == "read" for x in c) else "execute")) for c in xs)
        reads = [x for c in xs for x in c if x["name"] != ASK and tl[x["name"]]["kind"] == "read"]
        minimal = sum(set(x["arguments"]) <= set(tl[x["name"]]["parameters"].get("required", [])) | {"query"} for x in reads)
        print(f"  {name:13s} n={m}: " + ", ".join(f"{k} {100 * v / m:.1f}%" for k, v in sorted(kinds.items())) +
              f" | calls per sample {sum(len(c) for c in xs) / m:.2f} | starts with a read {100 * sum(bool(c) and c[0]['name'] != ASK and tl[c[0]['name']]['kind'] == 'read' for c in xs) / m:.1f}%"
              f" | reads with only required+query {100 * minimal / max(len(reads), 1):.1f}%")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--n", type=int, default=20, help="scenarios per app")
    b.add_argument("--apps", help="comma list (default: the 11 apps public_test adds)")
    b.add_argument("--shells", help="file of train ids whose context and history may be used (default: all train)")
    b.add_argument("--seed", type=int, default=0)
    b.add_argument("--tag", required=True)
    b.set_defaults(fn=cmd_build)
    s = sub.add_parser("show")
    s.add_argument("--tag", required=True)
    s.add_argument("--n", type=int, default=12)
    s.add_argument("--seed", type=int, default=0)
    s.set_defaults(fn=cmd_show)
    st = sub.add_parser("stats")
    st.add_argument("--tag", required=True)
    st.set_defaults(fn=cmd_stats)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
