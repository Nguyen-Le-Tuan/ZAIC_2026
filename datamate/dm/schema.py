"""Column -> canonical field mapping: README meanings first, then column-name synonyms, then ID value prefixes."""
from __future__ import annotations

import re

from .textnorm import colkey, fold

# meaning text (folded) -> field; first match wins, so specific rules come first
MEANING_RULES = [
    (r"cot trong|khong co du lieu", None),
    (r"^ma (don|phieu) nhap|^so phieu nhap|^ma nhap hang", "po_id"),
    (r"^ma phieu thu|^ma thanh toan", "pay_id"),
    (r"^ma (phieu )?tra", "ret_id"),
    (r"^ma lo|^so lo|^lo hang|^lo\b", "lot_id"),
    (r"^ma (don|hoa don|bill|giao dich|chung tu)|^so hoa don|^so don", "order_id"),
    (r"^ma khach|^so khach hang", "cust_id"),
    (r"^ten khach|^khach hang|^ten nguoi mua", "cust_name"),
    (r"nhom khach|loai khach", "cust_group"),
    (r"^ma nha cung cap|^ma ncc", "supplier_id"),
    (r"^(ten )?nha cung cap|^ncc", "supplier"),
    (r"^ma (hang|san pham|mat hang)|^sku", "prod_id"),
    (r"^ten$|^ten goi$", None),
    (r"^ten( hang| san pham| mon| mat hang| sp)\b|^mat hang|^san pham", "prod_name"),
    (r"(so luong|sl)\b.*(tra lai|tra hang|khach tra|\btra\b).*(co ban|quy doi)", "ret_qty_base"),
    (r"(so luong|sl)\b.*(tra lai|tra hang|khach tra|\btra\b)", "ret_qty"),
    (r"so luong (da )?(doi|quy) ra|so luong quy doi|quy ra don vi|so luong .*don vi co ban", "qty_base"),
    (r"^so luong nhap", "qty"),
    (r"^so luong|^sl\b", "qty"),
    (r"^(don )?gia nhap", "unit_cost"),
    (r"^gia von", "cost"),
    (r"^don gia|^gia ban|^gia 1|^gia le|^gia\b", "unit_price"),
    (r"tong tien hang", "order_gross"),
    (r"thanh tien|tri gia dong", "line_amount"),
    (r"^don vi co ban|^don vi goc", "base_unit"),
    (r"^don vi lon|^don vi quy doi", "conv_unit"),
    (r"^he so", "conv_factor"),
    (r"^don vi tinh|^don vi\b|^dvt", "unit"),
    (r"^nhom hang|^danh muc|^loai san pham|^nhom san pham", "category"),
    (r"^hoat chat|^thanh phan", "ingredient"),
    (r"ke don", "rx"),
    (r"^han (su )?dung|^han dung", "expiry"),
    (r"^ngay giao|^ngay cho", "deliv_date"),
    (r"^dot giao|^lan giao|^luot giao", "deliv_round"),
    (r"^gio dat don|^gio\b", "order_time"),
    (r"^ton( kho| cuoi| thuc)?\b", "stock"),
    (r"tong tien hang", "order_gross"),
    (r"^giam gia|^chiet khau", "discount"),
    (r"^da thanh toan|^khach (da )?tra|^so tien (da )?tra", "paid"),
    (r"^so tien thu|^so tien tra lan|^tien thu", "pay_amount"),
    (r"thoi diem dat don|ngay gio dat|^thoi diem", "order_ts"),
    (r"^ngay (ban|dat|lap|mua)", "order_date"),
    (r"^ngay nhap", "po_date"),
    (r"^ngay (thu|tra tien)|^thoi gian thu", "pay_ts"),
    (r"^ngay ap dung", "eff_date"),
    (r"^tong tien (cua )?don|^so khach phai tra|^tong (tien )?thanh toan|^tong sau giam", "order_total"),
    (r"^tong tien (cua )?(ca )?phieu nhap|^tong gia tri nhap", "po_total"),
    (r"^con no|^con lai|^con phai thu", "remaining"),
    (r"^kenh ban", "channel"),
    (r"^ma nhan vien|^nhan vien", "staff"),
    (r"^ma ca", "shift_id"),
    (r"hinh thuc thanh toan|phuong thuc", "pay_method"),
    (r"so thu tu dong", "line_no"),
    (r"^trang thai", "status"),
    (r"^ghi chu|^dien giai", "note"),
    (r"^phi (giao|van chuyen|ship)", "ship_fee"),
    (r"^thue|^vat", "vat"),
    (r"^chi nhanh|^ma chi nhanh", "branch"),
]

# column-name synonyms (colkey) -> field
SYN = {
    "order_id": "mahoadon madonhang madon magd magiaodich machungtu mabill sohd sohoadon soct mahd sochungtu".split(),
    "line_no": "thutu ttdong stt sothutu no sttdong".split(),
    "order_date": "ngay ngayban ngaydathang ngaythang ngaygiaodich ngaylap ngaymua thoigian dathangdaduyet ngaychungtu".split(),
    "order_ts": "thoigiantao thoigianlap thoidiem ngaygiophatsinh ngaygiotao".split(),
    "order_time": "gio giodat giotao".split(),
    "status": "trangthai trangthaidon trangthaidonhang trangthaixuly ketqua tinhtrang tinhtrangdon xuly status ghichutt".split(),
    "cust_id": "makh makhachhang sokh customerid makhachmua makhachlesi".split(),
    "cust_name": "khachhang tenkhachhang tenkhach doitac kh khachhangten khach tenkh khachlesi".split(),
    "cust_group": "nhom nhomkhachhang loaikhachhang nhomkh nhomkhach".split(),
    "pay_method": "phuongthucthanhtoan phuongthuctt phuongthuc pttt httt trabang hinhthucthanhtoan".split(),
    "channel": "kenhban banqua loaiban kenhbanhang".split(),
    "staff": "nguoiban manhanvien nhanvien nhanvienban tennhanvien".split(),
    "branch": "machinhanh chinhanh".split(),
    "table_no": "phongban ban maban".split(),
    "area": "khuvuc".split(),
    "guests": "sokhach".split(),
    "shift_id": "macalam maca".split(),
    "promo": "makhuyenmai".split(),
    "order_gross": "tongtienhang tongtienhangcuadon".split(),
    "order_total": "tongsaugiamgia tongbill tongdon phaithu tongthanhtoan tongphaitra".split(),
    "discount": "giamgia chietkhau".split(),
    "vat": "thuegtgt thue vat".split(),
    "vat_rate": "tylethue".split(),
    "ship_fee": "phivanchuyen phigiaohang".split(),
    "paid": "khachdatra khachtra khachdatra datra".split(),
    "remaining": "conlai conno conphaithu duno".split(),
    "due_date": "hanthanhtoan hantra".split(),
    "due_days": "hanngay hannongay songayduocno".split(),
    "prod_id": "mahang mahanghoa mahh idsp masku sku masanphamban mamathang mahangban masanpham masp".split(),
    "prod_name": "tenhang tenhanghoa tensanpham tensp tenmon tenmathang mathang sanpham hang hangban hanghoa noidung product tenhh".split(),
    "qty": "soluong sl sluong slban soluongban soluongsanpham soluonghang slnhap soluongnhap".split(),
    "unit": "donvitinh dvt donvi dvtinh unit".split(),
    "qty_base": "quyradvle soluongquydoi slquydoi soluongdvtcoban soluongle slle slnhapquydoi".split(),
    "unit_price": "dongia dongiad dongiaban giaban giabanle giasanpham giadonvi gia1dv price gia giale giahientai gianiemyet".split(),
    "line_amount": "thanhtien thanhtiend ttien tienban trigia amount".split(),
    "cost": "giavon giavonlucban giavonhang".split(),
    "ret_qty": "soluongtra".split(),
    "ret_qty_base": "soluongtradvtcoban sltraquydoi".split(),
    "category": "nhomhang3cap nhomhanghoa nhomhang danhmuc loaisanpham".split(),
    "base_unit": "donvicoban dvgoc donvigoc donvicoso dvnho".split(),
    "stock": "toncuoiky toncuoi tonthuc".split(),
    "rx": "thuockedon bantheodon".split(),
    "ingredient": "hoatchat thanhphanchinh".split(),
    "conv_unit": "donviquydoi dvlon dvnhap".split(),
    "conv_factor": "tylequydoi heso hesoqd hesoquydoi quydoi".split(),
    "pay_id": "maphieuthu".split(),
    "pay_ts": "thoigianthu ngaythu ngaygiothu".split(),
    "pay_amount": "sotienthu sotien".split(),
    "name": "tengoi ten".split(),
    "new_price": "giamoi".split(),
    "old_price": "giacu".split(),
    "po_id": "manhaphang madonnhap maphieunhap sophieunhap".split(),
    "po_date": "ngaynhap ngaynhapkho".split(),
    "supplier": "nhacungcap tenncc tennhacungcap".split(),
    "supplier_id": "mancc manhacungcap".split(),
    "po_total": "cantrancc tonggiatrinhap".split(),
    "unit_cost": "gianhap dongianhap".split(),
    "note": "ghichu ghichu diengiai".split(),
    "lot_id": "lo malo".split(),
    "expiry": "hansudung handung".split(),
    "eff_date": "ngayapdung".split(),
    "ret_id": "maphieutra".split(),
    "ret_ts": "ngaygiotra".split(),
    "refund": "tienhoantra".split(),
    "deliv_date": "ngaygiaohang ngaycho".split(),
    "deliv_round": "langiao luotgiao".split(),
    "deliv_qty": "slthucgiao soluonggiao".split(),
    "mv_id": "magiaodichkho".split(),
    "mv_type": "loaigiaodich kieuchungtu".split(),
    "sellable": "duocbantructiep bantructiep".split(),
    "address": "diachi addr diachilienhe".split(),
    "phone": "dienthoai sodienthoai phone didong".split(),
}
SYN_REV = {}
for _f, _ks in SYN.items():
    for _k in _ks:
        SYN_REV.setdefault(_k, _f)

# ID value prefixes used by the organisers' generator
PREFIX_FIELD = {"ORD": "order_id", "PN": "po_id", "PAY": "pay_id", "SP": "prod_id", "KH": "cust_id", "NCC": "supplier_id",
                "NV": "staff", "CN": "branch", "TH": "ret_id", "MV": "mv_id", "CA": "shift_id", "KM": "promo"}
_ID = re.compile(r"^([A-Z]{2,4})(\d{3,})$")


def id_prefix(values) -> str | None:
    vals = [str(v).strip() for v in values if str(v).strip()][:300]
    if len(vals) < 3:
        return None
    pre = {}
    for v in vals:
        m = _ID.match(v)
        if not m:
            return None
        pre[m.group(1)] = pre.get(m.group(1), 0) + 1
    p, n = max(pre.items(), key=lambda kv: kv[1])
    return p if n >= 0.95 * len(vals) else None


def meaning_field(meaning: str) -> str | None:
    m = fold(meaning)
    for pat, f in MEANING_RULES:
        if re.search(pat, m):
            return f
    return None


def name_field(col: str) -> str | None:
    return SYN_REV.get(colkey(col))
