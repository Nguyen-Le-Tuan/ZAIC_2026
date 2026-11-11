# Kế hoạch DataMate: từ tối 11/11 tới hạn Docker 16/11

*Claude viết lúc 18:45 ngày 11/11 (giờ Buffalo, tức 06:45 ngày 12/11 GMT+7), theo yêu cầu của Anh: "Lên kế hoạch thực hiện DataMate hoàn chỉnh trong khoảng thời gian bây giờ đến deadline" (JOURNAL entry 141). Đọc đề: [`DATAMATE_2026-11-11.md`](DATAMATE_2026-11-11.md). Mọi giờ trong file này là giờ Buffalo (EST), trừ chỗ ghi GMT+7.*

*Dữ liệu và hướng dẫn Docker đã tải lúc 18:38 về `data/datamate/` (nằm trong `.gitignore`): `train.zip` 128.118.095 byte, `public_test.zip` 64.149.714 byte, PDF 840.677 byte; kích thước khớp header máy chủ.*

## 0. Tóm tắt

- **Hạn:** nộp Docker DataMate trước **11:59 trưa thứ Hai 16/11**. Kế hoạch nhắm **nộp lần 1 chiều thứ Bảy 14/11** (bản an toàn) và **lần 2 tối Chủ nhật 15/11** (bản đầy đủ). Sáng thứ Hai để dự phòng.
- **Dữ liệu cho thấy:** câu hỏi sinh theo khoảng 40 mẫu, có lỗi gõ (không dấu, gõ Telex sai, viết tắt). 15 mẫu đầu phủ khoảng 75–80% bộ train. Mọi con số do luật trong rulebook quyết. Dữ liệu là file xuất từ phần mềm bán hàng: train có khoảng 10 kiểu file; **public có 14 tiệm, chỉ 6 tiệm trùng kiểu file của train**, còn lại là biến thể hoặc kiểu mới (có tiệm sửa xe máy). Private còn có loại tiệm mới.
- **Cách làm:** code tất định tính mọi con số. Model chỉ giúp ở chỗ luật không với tới:
  1. Đọc mọi file vào các bảng chuẩn (đơn, dòng hàng, thanh toán, hàng hoá, nhập hàng, tồn, lô…) nhờ README và từ điển tên cột, không viết riêng cho từng tiệm.
  2. Hiểu câu hỏi bằng luật trên chữ đã chuẩn hoá, ra một lệnh có cấu trúc (loại câu, kỳ, bộ lọc, k…).
  3. Một hàm tính cho mỗi loại câu, theo đúng rulebook. Không chắc thì **abstain** (0 điểm, không bị trừ).
  4. Giai đoạn 2 (nếu thuê được GPU): Qwen3-14B qua vLLM giúp hiểu câu hỏi luật không bắt được, ghép cột cho file lạ, và viết code cho câu ngoài mẫu.
- **Hai bản Docker:**
  - **A, chỉ CPU** (khoảng 1–2 GB): xong và nộp trước, là lưới an toàn.
  - **B, có LLM** (base `vllm/vllm-openai:v0.10.1.1`, Qwen3-14B): chỉ thay A khi qua luật viết trước.

  BTC chỉ chấm lần nộp cuối, nên thứ tự A rồi B dùng vừa 2 lần nộp.
- **LifeMate đi trước:** việc của Leader (L9, PR #17) không đổi. Anh chỉ phải làm vài việc ngắn cho DataMate (thuê máy, nộp file, tải image lên). Claude viết toàn bộ code và tài liệu DataMate.
- **Kỳ vọng thật:** bản A khoảng 0,35–0,5 trên public (tiệm có kiểu file lạ sẽ abstain nhiều); bản B khoảng 0,5–0,7, quanh trung vị public 0,598. Không có cửa top 2 (43 đội đã 1,000).
- **Chờ Anh:** B51 (thuê một máy ảo GPU có Docker, cần từ sáng thứ Sáu, **hoặc không thuê**: mục 10), B52 (đo tốc độ tải lên Drive, chỉ cần khi có image B). Không cần tiền API.

---

## 1. Soi dữ liệu (chỉ bộ train)

| Mục | Số đo |
|---|---|
| Câu hỏi | 3.000, 30 tiệm (`biz_101`–`biz_130`): 7 tiệm 40 câu (một file nhật ký bán), 23 tiệm 118–119 câu |
| Kiểu đáp án | number 1.884 (62,8%), percent 578 (19,3%), list 193 (6,4%), date 145 (4,8%), string 88 (2,9%), **unanswerable 70 (2,3%)**, boolean 23, table 19 |
| Đặc điểm đáp án | **cả 1.884 đáp án number đều là số nguyên**; list dài 2, 3 hoặc 5 phần tử; table 2 cột, 3 hoặc 5 dòng; 167 câu có `alias` |
| `as_of_date` | 15/01/2025 – 20/09/2026 |
| File | 107 xlsx (nhiều file có 12–20 sheet theo tháng), 20 csv, 1 sqlite (17 bảng), 30 README |
| README | từ 739 tới 8.539 ký tự; nhiều README liệt kê từng cột kèm nghĩa ("**Giá bán**: đơn giá"), mốc hết dữ liệu, bảng quy đổi đơn vị ("1 thùng = 24 lon") |
| Câu hỏi | trung vị 59 ký tự; nhiều câu không dấu, viết tắt (`dthu`, `bn`, `dc`, `hnay`, `trc`), gõ Telex sai (`tieenf`, `ddown`, `heets`), chữ Anh (`revenue`, `bill`, `best seller`) |

**Nhóm câu hỏi** (phân bằng từ khoá, ước lượng thô):

| Nhóm | Số câu | Cộng dồn |
|---|---:|---:|
| Doanh thu theo kỳ, theo hàng, theo nhóm | khoảng 600 | 20% |
| Số lượng bán theo đơn vị | khoảng 240 | 28% |
| Phần trăm tăng giảm so kỳ trước | khoảng 230 | 36% |
| Số đơn; số đơn huỷ; tỉ lệ huỷ | khoảng 400 | 49% |
| Ngày bán cao nhất; giá trị trung bình một đơn; thanh toán theo hình thức | khoảng 270 | 58% |
| Khách (nhiều nhất, nhóm khách); hàng bán chạy và ế | khoảng 300 | 68% |
| Hiệu ứng tăng giá; size M/L; ca sáng/chiều | khoảng 240 | 76% |
| Tồn kho; giá nhập bình quân; giá bán ngày D; tiền nhập | khoảng 230 | 84% |
| Nhà thuốc (hoạt chất, kê đơn, hạn dùng); công nợ (tổng, theo khách, tuổi nợ, thu nợ) | khoảng 200 | 91% |
| Còn lại: nhân viên, chi nhánh, đợt giao, lãi gộp, lãi ròng, Tết, ngưỡng đơn/ngày | khoảng 150 | 97% |

**Rulebook train** (10 mục, 143 dòng) quyết định gần như mọi con số: đơn trả hàng (kể cả trả một phần) bị bỏ cả đơn khỏi doanh thu nhưng vẫn tính nợ; doanh thu theo hình thức ghi trên đơn (COD là hình thức riêng); tuần từ thứ Hai; "tháng này" so với cùng số ngày của tháng trước; Tết theo `calendar.csv`; bán chạy theo số lượng quy về đơn vị cơ bản; tồn theo đơn vị lớn là list `[số nguyên, số lẻ]`; giá vốn lấy trên dòng bán; khi nào thì unanswerable; thứ tự list và cách phá hoà. **Rulebook public dài hơn rulebook train (23,8 KB so với 18,5 KB)**, đúng như đề nói rulebook đổi theo split.

**Public test** (chỉ xem tên file, không đọc nội dung): 14 tiệm, 1.000 câu.
- 6 tiệm có bộ file giống một kiểu của train: sổ bán hàng kiểu MISA; sổ bán + bảng giá + sổ nhập + tồn; `pos.sqlite`; một file csv hoá đơn; bộ csv POS; một file `SoBanHang.xlsx`.
- 3 tiệm là biến thể: file theo từng tháng, hoặc nhà thuốc tách file khác train.
- 5 tiệm là kiểu mới: `chi_tiet_hoa_don.csv` + `danh_muc_hang.csv`; `ChiTietHoaDon.xlsx` + `DanhMucHang.xlsx`; `SoSuaXe.xlsx` + `DanhSachTho.xlsx` (tiệm sửa xe); `BanHang.xlsx` + `QuanLy.xlsx`; `SoNo.xlsx` + `ThuMayCu.xlsx`.

→ **Không thể viết tay cho từng kiểu file.** Bước đọc dữ liệu phải tự hiểu file nhờ README và tên cột. Điểm public sẽ là thước đo trung thực cho private.

### Luật dùng dữ liệu (theo Rule 6 và FAQ)

- Public test chỉ dùng để **chạy suy luận và nộp**. Không đọc câu hỏi, dữ liệu, README hay rulebook của public để viết code; chỉ xem tên file (để biết định dạng cần đọc được). Điểm public là phản hồi duy nhất được dùng.
- Phát triển và đo hoàn toàn trên train. Không train model, nên cả 3.000 câu train dùng làm dev; giữ riêng một phần (mục 4) để đo độ tổng quát.
- Không gọi API lúc suy luận. Không có logic nào dựa trên ID câu hỏi hay ID tiệm.

---

## 2. Kiến trúc

```
/data ──► (1) đọc file thô ──► (2) hiểu schema ──► bảng chuẩn (mỗi tiệm, đệm trong /tmp)
                                                       │
câu hỏi ──► (3) chuẩn hoá chữ ──► (4) hiểu câu hỏi ──► lệnh có cấu trúc
                                                       │
rulebook của split ──► (6) chốt rulebook ──────────────┤
                                                       ▼
                                     (5) hàm tính theo rulebook ──► (7) định dạng đáp án / abstain ──► submission + log
```

1. **Đọc file thô:** csv (đoán mã hoá, dấu phân cách), xlsx (mọi sheet; tìm dòng tiêu đề; ô trống ở các dòng sau của cùng đơn thì lấy theo dòng đầu nhóm, §8; năm lấy theo tên sheet khi ngày không ghi năm), sqlite (mọi bảng). Đệm thành parquet trong `/tmp`.
2. **Hiểu schema → bảng chuẩn:**
   - **Bảng chuẩn:**
     - `orders` (mã, ngày giờ đặt, trạng thái 4 loại, khách, nhóm khách, hình thức thanh toán, nhân viên, chi nhánh, giảm giá cả đơn, VAT, phí giao, tổng phải trả);
     - `lines` (đơn, hàng, số lượng, đơn vị, số lượng quy về đơn vị cơ bản, đơn giá, giảm giá dòng, thành tiền, giá vốn trên dòng);
     - `payments`; `products` (mã, tên, các cách viết, nhóm, đơn vị cơ bản, quy đổi, giá vốn danh mục, kê đơn, hoạt chất);
     - `purchases`; tồn (ảnh chụp hoặc thẻ kho); lô và hạn dùng; lịch sử giá; chi phí; đợt giao; khách.
   - **Thứ tự cách hiểu:**
     - (a) đọc README: dòng "**cột**: nghĩa", mốc hết dữ liệu, quy đổi đơn vị, giá trị trạng thái;
     - (b) từ điển tên cột tiếng Việt của các phần mềm bán hàng;
     - (c) đoán theo kiểu giá trị;
     - (d) giai đoạn 2: hỏi LLM cho phần còn thiếu.
   - **Kiểm khớp sau khi dựng:** thành tiền ≈ số lượng × đơn giá − giảm giá; tổng đơn khớp tổng dòng; trạng thái chỉ thuộc 4 loại; ngày nằm trong khoảng README ghi. Bảng nào không qua kiểm thì nhóm câu cần bảng đó abstain.
3. **Chuẩn hoá chữ:** NFC, chữ thường, sửa lỗi gõ Telex (`tieenf` → `tiền`), bung viết tắt, bản bỏ dấu để so khớp. Dùng lại ý của `askpolicy.norm` và `vinum.py` (số kiểu "9.600.000 đồng", "2tr", "50 ngàn").
4. **Hiểu câu hỏi:** luật trên chữ đã chuẩn hoá ra lệnh, ví dụ `{"loai": "doanh_thu", "ky": {"thang": 6, "nam": 2025}, "loc": {"hang": "Nếp cái hoa vàng"}, "don_vi": "kg"}`.
   - Tên hàng, khách, nhóm, nhân viên được dò mờ (không dấu, sai chính tả) trên danh mục của tiệm; trả về đúng tên như trong dữ liệu.
   - Giai đoạn 2: Qwen3-14B đọc câu luật không bắt được, kèm vài ví dụ train gần nhất, và trả lệnh dạng JSON.
5. **Hàm tính:** khoảng 40 hàm, mỗi nhóm câu một hàm.
   - Bộ giải kỳ: hôm nay, tuần này, tuần rồi, tháng này so cùng số ngày, N ngày gần nhất, quý, "tháng M không ghi năm", Tết theo âm lịch, ca sáng/chiều.
   - Luật trạng thái đơn, xếp hạng và phá hoà theo mã, làm tròn (tiền về đồng, phần trăm 2 chữ số), unanswerable (§7: kỳ nằm hoàn toàn ngoài dữ liệu, hoặc tiệm không ghi loại thông tin đó).
   - Ghi log theo mẫu 2 của hướng dẫn: tên hàm, tham số, kết quả.
6. **Chốt rulebook:**
   - Tách rulebook của split thành từng dòng luật rồi so với rulebook train.
   - Mỗi hàm khai báo những dòng luật nó dựa vào.
   - Dòng đó đổi hay mất thì hàm không được tự trả lời: giai đoạn 2 chuyển sang LLM viết code kèm luật mới, giai đoạn 1 abstain.
   - Luật ngành mới (§6) cũng đi đường này.
7. **Đáp án:**
   - Định dạng đúng từng type (mục 9 của rulebook).
   - Abstain khi: không hiểu câu, thiếu bảng, bảng không qua kiểm, luật đổi, hay hàm báo lỗi.
   - Mỗi câu ghi ngay một dòng vào `submission.jsonl` và một dòng log gồm `id`, `answer`, `elapsed_ms`, `thinking` (null ở đường CPU), `code`, `inputs`, `output`.

**Giai đoạn 2 (LLM):**
- **Model:** Qwen3-14B, chạy bằng vLLM 0.10.1.1. Đây là đúng bộ BTC đã thử trên 2 × RTX 5090 (nạp khoảng 2 phút).
- **Ba việc:** hiểu câu hỏi khi luật bó tay; ghép cột cho file lạ; viết code pandas cho câu ngoài mẫu hoặc có luật đổi (chạy trong tiến trình con, có giới hạn thời gian).
- Giải mã greedy, seed cố định; ghi `thinking` đầy đủ nếu bật chế độ suy nghĩ.
- **So model (luật viết trước):** Qwen3-4B-Instruct-2507 đọ với Qwen3-14B trên phần train giữ riêng. Chỉ dùng 14B nếu PA hơn ít nhất 0,02, vì 4B cho image nhỏ hơn và tải lên nhanh hơn.

**Thời gian chạy:** đường CPU khoảng 0,1–1 giây mỗi câu, nạp dữ liệu vài phút. Đường LLM với khoảng 20–40% số câu vẫn dưới 1 giờ cho 500 câu, xa giới hạn 6 giờ.

---

## 3. Lịch theo ngày

| Khi nào | Ai | Việc | Ra gì |
|---|---|---|---|
| **Thứ Tư 11/11, 19:00–02:00** | Claude (CPU laptop) | Nhánh `datamate` (worktree riêng `~/zac-dm/repo`, không đụng checkout chính); bộ đọc file thô và đệm; hồ sơ 30 tiệm train; bộ chấm PA và kiểm định dạng; bộ giải kỳ (gồm Tết); chuẩn hoá chữ | khung code, bộ chấm có test |
| **Thứ Năm 12/11, sáng** | Claude | Bộ hiểu schema (README, từ điển cột, kiểu giá trị) → bảng chuẩn cho cả 30 tiệm; kiểm khớp từng tiệm | bảng chuẩn đạt kiểm |
| **Thứ Năm 12/11, chiều** | Claude | Luật hiểu câu hỏi và hàm tính cho 15 nhóm đầu (khoảng 76% câu); chấm train theo nhóm, theo tiệm | PA train lần đầu |
| **Thứ Năm 12/11, tối** | Claude → Anh | Chạy public bằng bản CPU; Anh nộp **public lần 1** | điểm public thật đầu tiên |
| **Cửa 1: 23:59 thứ Năm** | | Mục 4 | đi tiếp / thu hẹp / dừng |
| **Thứ Sáu 13/11, 08:00** | Anh | Máy ảo GPU sẵn, Claude vào được bằng SSH (B51) | |
| **Thứ Sáu 13/11, cả ngày** | Claude | Hàm tính cho các nhóm còn lại, unanswerable, chốt rulebook; Docker A (CPU) dựng và thử trên laptop. Trên máy ảo: vLLM + Qwen3-14B và Qwen3-4B; ba việc của LLM; đo trên phần giữ riêng | bản B chạy ngoài Docker |
| **Thứ Sáu 13/11, tối** | Anh | Nộp **public lần 2** (bản B), và lần 3 nếu cần so A với B | |
| **Cửa 2: 23:59 thứ Sáu** | | Mục 4: giữ hay bỏ giai đoạn LLM | |
| **Thứ Bảy 14/11, sáng** | Claude | Docker A chạy đúng lệnh chấm của BTC (tắt mạng, `/data` chỉ đọc); xuất `tar.gz` + md5 | image A |
| **Thứ Bảy 14/11, chiều** | Anh | Tải image A (1–2 GB) lên Drive, "Anyone with the link"; **nộp Solution lần 1 (A)**; nộp thử ở tab Test Solution | lưới an toàn đã nộp |
| **Thứ Bảy 14/11, cả ngày** | Claude (máy ảo) | Docker B theo Dockerfile mẫu của BTC (NCCL 2.27.7, `NCCL_P2P_DISABLE=1`); chạy đủ public bằng đúng lệnh chấm trên 2 GPU; đo giờ; chạy 2 lần trên train để kiểm tái lập | image B đã kiểm |
| **Chủ nhật 15/11, đến 12:00** | Claude | Sửa lỗi cuối, chốt image B (**Cửa 3**) | |
| **Chủ nhật 15/11, 12:00–18:00** | Anh (hoặc Claude từ máy ảo nếu Anh cài `rclone`) | Tải image B (khoảng 20–35 GB) lên Drive; tải về một máy khác để `md5sum -c` | |
| **Chủ nhật 15/11, trước 20:00** | Anh | **Nộp Solution lần 2 (B)** nếu qua cửa 3; không thì giữ A | |
| **Thứ Hai 16/11, trước 11:59** | | Dự phòng; không đổi gì nếu đã ổn | |
| **Thứ Năm 19/11 21:00 – thứ Hai 23/11 11:59** | Claude (máy ảo 2 GPU) → Anh | Chạy image đã nộp trên private bằng đúng lệnh chấm; Anh nộp file | điểm private tạm |

LifeMate chạy song song: B49 (gói v7 lên Drive, anh trai train khoảng 6,5 giờ), chọn model theo luật entry 138, L9 của Leader, tải image LifeMate lên. **Khi trùng giờ hay trùng đường mạng, LifeMate đi trước:** image LifeMate tải lên trước image DataMate B.

---

## 4. Cửa dừng (viết trước khi có kết quả)

Số đo chính: **PA trên train** (3.000 câu) và **PA trên phần giữ riêng**:
- **Câu giữ riêng:** 20% câu của mỗi nhóm, chọn ngẫu nhiên (seed 0) trước khi viết luật. Claude không đọc các câu này khi viết luật.
- **Tiệm giữ riêng:** 6 tiệm train, mỗi tiệm một kiểu file khác nhau, chạy bằng đường hiểu schema chung, không có chỉnh tay nào cho tiệm đó. Đây là phép thử gần nhất với kiểu file lạ ở public và private. Không chọn `biz_101`, `biz_106` (đã đọc README lúc soi dữ liệu).
- Lúc soi dữ liệu Claude đã thấy khoảng 120 câu train (mẫu ngẫu nhiên và ví dụ theo nhóm). Một vài câu trong số đó có thể rơi vào phần giữ riêng; ảnh hưởng nhỏ, ghi lại cho rõ.

| Cửa | Lúc | Điều kiện | Không đạt thì |
|---|---|---|---|
| **1** | 23:59 thứ Năm 12/11 | PA train ≥ 0,50 và có file public hợp lệ | PA 0,20–0,50: bỏ giai đoạn LLM, chỉ làm và nộp bản A. Dưới 0,20: dừng DataMate |
| **2** | 23:59 thứ Sáu 13/11 | Bản B hơn bản A ít nhất 0,02 PA trên phần giữ riêng, **hoặc** hơn ít nhất 0,02 trên public; và tỉ lệ đúng trên câu đã trả lời của B ≥ 0,90 | Bỏ giai đoạn LLM, nộp A |
| **3** | 12:00 Chủ nhật 15/11 | Image B chạy hết public bằng đúng lệnh chấm trên 2 GPU, không lỗi, không mạng; ước giờ private (nạp + trung bình mỗi câu × 500) dưới 3 giờ; hai lần chạy trên train lệch PA ≤ 0,01; PA public của B ≥ A | Giữ A, không nộp B |
| **LifeMate** | bất kỳ lúc nào | L9 hay B49 cần Anh hoặc Leader | DataMate chờ; Claude vẫn làm phần code |

---

## 5. Máy, tiền và việc tải lên

- **Laptop (CPU):** đủ cho toàn bộ giai đoạn 1 và Docker A. GPU laptop đang chạy thử Qwen3.5 cho LifeMate (B48); DataMate không cần nó.
- **Máy ảo GPU (B51)**, cần từ sáng thứ Sáu tới tối Chủ nhật, rồi 20–23/11 cho private:
  - **phải là máy ảo chạy được Docker với `--gpus`** (nhiều chỗ cho thuê GPU giá rẻ chỉ cho một container, không chạy Docker bên trong được);
  - 2 × RTX 5090 là tốt nhất (đúng máy chấm). Không có thì 2 GPU từ 32 GB trở lên, hoặc 1 GPU 80 GB cho giai đoạn phát triển rồi 2 × 5090 cho lần thử cuối;
  - đĩa từ 300 GB (image mẫu của BTC cần khoảng 57 GB cho build và 50 GB lúc xuất);
  - Anh thuê và trả tiền; thêm khoá SSH công khai của laptop để Claude điều khiển; Claude báo trước từng lệnh tốn tiền;
  - Chi phí ước 30–80 USD tuỳ nơi và loại GPU (chưa kiểm giá; Anh xem giá rồi quyết).
- **Không thuê được máy** thì vẫn có bài DataMate hợp lệ: chỉ bản A. Giai đoạn 2 thu về Qwen3-4B trên GPU laptop sau khi LifeMate xong lượt thử, và không có image B.
- **Tải lên (B52):**
  - Image B với Qwen3-14B bf16 khoảng 34 GB nén (theo mẫu của BTC: 50,6 GB `.tar` → 34,4 GB `.tar.gz`); với Qwen3-4B khoảng 15–20 GB.
  - Anh tải thử 1 GB lên Drive để đo tốc độ: dưới 20 Mbit/s thì tải từ laptop mất hơn 4 giờ. Khi đó dùng `rclone` trên máy ảo (Anh tự cấu hình, Claude không xem token) hoặc chọn bản 4B.
  - Laptop còn 96 GB đĩa trống, không đủ build image B bf16; image B build trên máy ảo.
- **API:** không cần. Luật hiểu câu hỏi do Claude viết trong phiên này. Hai trần API giữ nguyên cho LifeMate.

---

## 6. Docker (theo hướng dẫn của BTC, 10 trang, ngày 05/11)

- **Cấu trúc:**
  - `/code/predict.sh` chạy không tham số, đọc `/data` (gồm `data/<business_id>/`, `rulebook.md`, `calendar.csv`, `questions.jsonl`), ghi `/result/submission.jsonl` và `/result/logs/`.
  - Mọi tham số đặt cứng trong code.
  - `/code/README.md` ghi cách làm, model (tên, nguồn, revision, ngày phát hành, licence, số tham số), dữ liệu.
  - `/code/training_code/` cùng `data_manifest.json`. Đội không train: ghi rõ điều đó, kèm từ điển cột và luật hiểu câu hỏi.
- **Lệnh chấm (kiểm đúng lệnh này):**
  ```
  docker run --rm --gpus '"device=0,1"' --network none --shm-size=16g --entrypoint bash \
    -v <public_test>:/data:ro -v <out>:/result zaic2026_datamate_<team>:final /code/predict.sh
  ```
- **Image B:**
  - `FROM vllm/vllm-openai:v0.10.1.1`, `ENTRYPOINT []`;
  - `nvidia-nccl-cu12==2.27.7`, `NCCL_P2P_DISABLE=1`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`;
  - trọng số trong `/code/models/`.
- **Image A:** base nhỏ (Python 3.12), không GPU, vẫn chạy được bằng đúng lệnh trên.
- **Nộp:**
  - `set -o pipefail; docker save … | pigz > zaic2026_datamate_<team>.tar.gz`;
  - `md5sum` ra file `.md5`; đo cỡ `.tar` chưa nén (tối đa 100 GB);
  - link Drive "Anyone with the link"; tải lại trên máy khác để `md5sum -c`;
  - nộp qua form "Solution Submission"; tối đa 2 lần, lấy lần cuối.
- **Tab Test Solution** (1 lần mỗi ngày): nộp thử A vào thứ Bảy, B vào Chủ nhật, nếu BTC xác nhận tab này không tính vào 2 lần nộp (Leader thêm câu hỏi này vào email gửi BTC, entry 140).

---

## 7. Rủi ro

| Rủi ro | Dấu hiệu | Cách đỡ |
|---|---|---|
| File lạ không hiểu được (public 5/14 tiệm, private nhiều hơn) | tiệm giữ riêng của train có PA thấp; điểm public thấp hơn train nhiều | README trước, từ điển cột sau, LLM ghép cột ở giai đoạn 2; không hiểu thì abstain cả tiệm thay vì đoán |
| Rulebook của split khác train | bước chốt rulebook báo dòng đổi | hàm dựa trên dòng đổi không tự trả lời; LLM viết code kèm luật mới, hoặc abstain |
| Trả lời sai bị trừ điểm | tỉ lệ đúng trên câu đã trả lời dưới 0,9 ở nhóm nào đó | tắt nhóm đó (abstain), không cố vớt |
| Docker trên RTX 5090 (NCCL, sm_120) | lỗi khởi tạo 2 GPU | làm đúng Dockerfile mẫu của BTC; thử trên 2 × 5090 trước khi nộp B; bản A không phụ thuộc GPU |
| Tải image B quá lâu | B52 đo dưới 20 Mbit/s | `rclone` từ máy ảo, hoặc 4B, hoặc chỉ nộp A |
| Lệch quá 0,03 khi BTC chạy lại | hai lần chạy B khác nhau | đường CPU tất định; LLM greedy; chạy private trên đúng 2 × 5090; log đủ `thinking`, `code`, `output` để giải thích |
| Thiếu người | Anh hoặc Leader bận LifeMate | việc DataMate của Anh chỉ còn thuê máy, nộp file, tải lên; Leader không phải làm gì cho DataMate |
| Phiên Claude bị ngắt hoặc nén ngữ cảnh | | code commit thường xuyên lên nhánh `datamate`; file này và JOURNAL là nguồn để làm tiếp |

---

## 8. Phân việc

- **Claude:** toàn bộ code DataMate (nhánh `datamate`, PR vào `main`, không tự merge); bộ chấm và các lượt đo; Dockerfile và `predict.sh`; README và `training_code`; dựng và thử image; chạy trên máy ảo; ghi JOURNAL và bảng điều phối.
- **Anh:**
  - **B51:** thuê máy ảo GPU (Docker + NVIDIA Container Toolkit) trước 08:00 thứ Sáu và cho Claude SSH.
  - **B52:** đo tốc độ tải lên Drive.
  - Nộp public (tối thứ Năm, tối thứ Sáu).
  - Tải image lên và nộp Solution (A chiều thứ Bảy, B tối Chủ nhật).
  - Chạy và nộp private 20–23/11.
- **Leader:** không có việc DataMate bắt buộc, ngoài việc thêm câu hỏi về tab Test Solution vào email gửi BTC (entry 140). Review PR DataMate nếu còn thời gian.
- **Anh trai:** không dùng cho DataMate. Máy anh trai dành cho LifeMate (v7), và mỗi ngày chỉ chạy được một lần, không hợp để sửa lặp.

## 9. Việc chờ Anh

- **B51 (trước 08:00 thứ Sáu 13/11):** thuê một máy ảo GPU theo mục 5 và gửi Claude địa chỉ và cổng SSH (không gửi mật khẩu; thêm khoá công khai của laptop). Hoặc báo "không thuê", khi đó kế hoạch chạy theo đường chỉ có bản A.
- **B52 (trước tối thứ Sáu):** tải thử một file 1 GB lên Drive và báo số phút.
- **Bắt đầu:** Claude làm phần tối nay (mục 3, dòng đầu) khi Anh đồng ý. Phần này không tốn tiền và không đụng LifeMate.

## 10. Không thuê máy ảo GPU (bổ sung 18:54 ngày 11/11, entry 144)

Anh hỏi: "không thuê máy ảo GPU có được không?" **Được.** Đề không bắt dùng LLM. Hướng dẫn Docker có sẵn mẫu log "gọi hàm đóng gói sẵn" với `thinking: null` (mẫu 2, trang 4). Bản A (chỉ CPU) đã là một bài hoàn chỉnh và hợp lệ.

| | Thuê máy (mục 2–9) | Không thuê |
|---|---|---|
| Bài chính | B (Qwen3-14B) nếu qua cửa, không thì A | **A (chỉ CPU)** |
| LLM | Qwen3-14B, 2 GPU, vLLM | bỏ; hoặc model nhỏ có sẵn trên laptop (Qwen3-1.7B, Qwen3-4B-Instruct-2507) trên 1 GPU, chỉ khi bản A xong sớm |
| Kiểm trên RTX 5090 | có | không; bản A không dùng GPU nên không cần |
| Chạy private 20–23/11 | máy ảo | laptop, vài phút (bản A) |
| Tải lên Drive | 20–35 GB | 1–2 GB |
| Tái lập (lệch ≤ 0,03) | phần LLM có thể lệch khi đổi GPU | bản A tất định, không lệch |
| Tiền | 30–80 USD | 0 |
| Kỳ vọng public | A 0,35–0,5; B 0,5–0,7 | A 0,35–0,5, có thể cao hơn vì dồn thêm thời gian vào bộ hiểu file và luật |

**Mất gì:** LLM chủ yếu giúp ở kiểu file lạ và loại tiệm mới, đúng chỗ private có nhiều. Không có LLM thì những tiệm, những câu đó abstain: 0 điểm, không bị trừ. Phần bù: thời gian dành cho máy ảo và image B chuyển sang bộ hiểu README và tên cột (đo bằng 6 tiệm train giữ riêng) và phủ thêm nhóm câu.

**Nếu vẫn muốn một LLM nhỏ khi không thuê máy:**
- Dùng base `vllm/vllm-openai:v0.10.1.1` (torch 2.7.1+cu128) như BTC khuyên. **Không dùng lại base của image LifeMate** (CUDA 13.2): hướng dẫn DataMate chỉ ghi CUDA ≥ 12.8 và driver R570 trở lên, nên máy chấm DataMate có thể không chạy được CUDA 13.2.
- Model chạy trên 1 GPU, không chia 2 GPU, để tránh lỗi NCCL mà hướng dẫn nhắc.
- `predict.sh` chạy đường CPU trước. LLM chỉ là phần thêm: nạp lỗi hay chạy lỗi thì ghi log rồi làm tiếp như bản A.
- Chỉ làm khi bản A xong trước tối thứ Sáu, GPU laptop không bận việc LifeMate, và qua cửa 2.

**Lịch khi không thuê:**

| Khi nào | Việc |
|---|---|
| Thứ Tư tối – thứ Năm | như mục 3 (toàn bộ chạy CPU) |
| Thứ Năm, 23:59 | **Cửa 1** như mục 4 |
| Thứ Sáu | phủ thêm nhóm câu, unanswerable, chốt rulebook, bộ hiểu file đo trên 6 tiệm giữ riêng; Docker A dựng và thử trên laptop bằng lệnh chấm (đổi `device=0,1` thành `device=0` vì laptop có 1 GPU); Anh nộp public lần 2 |
| Thứ Bảy, chiều | Anh tải image A (1–2 GB) lên Drive; **nộp Solution lần 1**; nộp thử ở tab Test Solution nếu BTC xác nhận |
| Chủ nhật, trước 20:00 | bản A2 (sửa thêm) chỉ thay A khi PA trên phần train giữ riêng hơn ít nhất 0,02 và PA public không thấp hơn A; khi đó **nộp Solution lần 2** |
| 19/11 tối – 23/11 trưa | chạy image đã nộp trên laptop, Anh nộp file private |

**Việc của Anh khi không thuê:** nộp public (tối thứ Năm, thứ Sáu), tải image A lên Drive và nộp (chiều thứ Bảy, có thể thêm tối Chủ nhật), nộp private. B51 và B52 không cần nữa.
