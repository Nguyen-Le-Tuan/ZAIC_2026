# Thí nghiệm D: dạy ranh giới hỏi lại / tự làm

*30/10/2026. Claude viết theo yêu cầu "Thiết kế D" của Anh: thống kê trên fit trước, đề xuất cách sinh dữ liệu đủ/thiếu slot và kiểm tra tất định cho tham số bắt buộc. Anh quyết thêm: viết lại câu ngay trong phiên và làm luôn bộ sinh dữ liệu, **chưa train**.*

- **Code:** [PR #3](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/3) (`exp-d`, xếp chồng lên PR #2).
- **Review và mốc đo (30/10):** [`docs/REVIEW_D_2026-10-30.md`](REVIEW_D_2026-10-30.md). Bản review **thay mục 8 bên dưới** bằng kế hoạch có đối chứng (nhân bản mẫu hỏi lại thật) và các cổng chặn theo giai đoạn.
- **Tái lập số liệu:** `lifemate/scripts/ask_policy_stats.py`, lệnh ở cuối tài liệu.
- **Nhãn của từng kết luận:**
  - **[Quan sát]**: đếm hoặc đo trực tiếp.
  - **[Suy luận]**: diễn giải, chưa có can thiệp.
  - **[Can thiệp]**: kết quả sau khi chạy thử một thay đổi.

## 0. Tóm tắt

- **Nhãn hỏi lại có ba kiểu:**
  - **A, trùng tên khi tra cứu:** model đã học tốt.
  - **B, chọn mơ hồ một ID** trong danh sách hoặc từ history.
  - **C, câu thiếu một slot thường** (số tiền, giờ…).
- **Model bỏ hỏi gần như chỉ ở B và C.** Trên dev_lao, bỏ hỏi 17/21 mẫu B và 16/19 mẫu C, phần lớn là tool của app giữ riêng. Với C, model thường **bịa giá trị** cho đúng slot lẽ ra phải hỏi.
- **Kiểm tra tất định đã thử và loại khỏi hướng chính.** Luật "ID chọn từ lần tra ≥ 2 mục trùng tên → hỏi lại" không báo nhầm lần nào trên fit, nhưng khi phát lại các rollout thì chỉ kích hoạt 0/233 mẫu dev_random và 1/262 mẫu dev_lao (+0,25 điểm). Lý do: model đã tự học được kiểu A.
- **Hướng chính là dữ liệu cặp đủ/thiếu sinh từ fit** (C, B-vague, B-specific). Nhãn được phát lại qua ToolEnv và câu viết lại phải qua các kiểm tra văn bản.
- **Chạy thử:** 49 task → Claude viết lại 27 (22 bỏ qua có lý do) → **23 mẫu qua mọi kiểm tra**. Chưa có người đọc tay.
- **Train D cần Anh duyệt riêng.** Đề xuất 2 lượt giữ nguyên số bước (dev_lao và dev_random), tiêu chí giữ/bỏ ở mục 8.

## 1. Vì sao làm D

- **Thí nghiệm B, model `fit_lao`:** hỏi lại được 7,5 điểm. Với 23 mẫu cần hỏi về tool của app giữ riêng, model được 0 điểm.
- **Trên dev_random:** 14 mẫu hỏi thừa và 16 mẫu bỏ hỏi, mất 12,7 điểm. Đây là nhóm hành vi mất điểm lớn nhất ([EVAL mục 2.2 và 7.2](EVAL_2026-10-29.md)).
- **[Suy luận]** Private có thêm app mới, nên chính sách hỏi lại trên schema chưa thấy là đòn bẩy cụ thể nhất hiện có.

## 2. Chính sách hỏi lại trong nhãn (đo trên fit) [Quan sát]

| | fit_random | fit_lao |
|---|---:|---:|
| Mẫu / mẫu hỏi lại | 1.312 / 184 | 1.283 / 176 |
| Số tool đích / số app đích khác nhau | 54 / 37 | 46 / 32 |
| Số tham số mỗi lần hỏi | luôn đúng 1 | luôn đúng 1 |
| Hỏi lại sau khi đã thực hiện ý khác | 73 | 74 |
| Tham số được hỏi là ID có `x-ref` | 112 | 109 |
| Kiểu A / B / C | 57 / 55 / 72 | 64 / 45 / 67 |
| Slot C hay gặp | amount 19, time 7, start 6, to 4, steps 4 | amount 19, time 10, steps 5, to 4 |

- **Hỏi lại luôn là call cuối cùng, và mỗi mẫu chỉ hỏi một lần.** Các ý làm được thì thực hiện trước (ví dụ đặt báo thức rồi hỏi người cần gọi).
- **Kiểu A:** cả 57 lần, lần tra trước đó đều trả về ≥ 2 mục trùng đúng tên; không lần nào trả về 0 mục. Ngược lại, 26 mẫu execute cũng nhận ≥ 2 kết quả nhưng chỉ một mục trùng tên, hoặc câu đã phân biệt được (ví dụ "anh Quân bên kho").
- **Chính sách có ngoại lệ.** Thiếu số tiền khi chuyển ví: 17 mẫu tra danh bạ trước rồi mới hỏi, 2 mẫu hỏi luôn.
- **Hỏi lại tập trung vào vài khuôn câu lặp lại** (17 mẫu gần giống nhau dạng "đặt báo thức … rồi chuyển ví cho bố chút tiền"). **[Suy luận]** Dữ liệu hỏi lại ít đa dạng, khớp với việc model tổng quát kém sang tool mới.

## 3. Model hiện tại theo kiểu hỏi lại [Quan sát]

| Kiểu | dev_random (final fit_random) | dev_lao (final fit_lao) | 233 mẫu đã train (final fit_random) |
|---|---|---|---|
| A | 8/8 có hỏi | 1/1 có hỏi | 9/9 có hỏi |
| B | bỏ hỏi 7/11 (1 tool giữ riêng) | bỏ hỏi 17/21 (9 tool giữ riêng) | bỏ hỏi 4/11 |
| C | bỏ hỏi 9/14 (1 tool giữ riêng) | bỏ hỏi 16/19 (12 tool giữ riêng) | bỏ hỏi 6/15 |
| Mẫu execute bị hỏi thừa | 14 | 15 | 3 |

- Với C, khi bỏ hỏi thì **21/25 lần model gọi đúng tool đích kèm một giá trị tự điền** cho đúng slot lẽ ra phải hỏi; 4 lần còn lại không gọi tool đích.

## 4. Kiểm tra tất định: đã thử, loại khỏi hướng chính

**Luật:** nếu một lệnh ghi dùng ID lấy từ lần tra trả về ≥ 2 mục trùng tên (không phân biệt dấu), và câu không có từ nào chỉ thuộc riêng một mục, thì đổi lệnh ghi đó thành `ask_missing(tool, [param])` rồi dừng.

- **[Quan sát] Trên nhãn fit:** bắt đúng 57/184 (fit_random) và 64/176 (fit_lao) lần hỏi lại. **0 lần báo nhầm** trên 1.034 và 1.003 mẫu execute. Bản đầu báo nhầm 2 lần, do câu phân biệt bằng nơi làm việc ("bên kho", "bên nhà cung cấp"); đã sửa bằng cách so khớp theo từ riêng của từng mục.
- **[Can thiệp] Phát lại trên rollout đã lưu** (gắn luật vào agent, chấm lại):

  | Rollout | Số mẫu luật kích hoạt | Điểm thay đổi |
  |---|---:|---:|
  | 233 mẫu đã train | 0/233 | 0 |
  | dev_random | 0/233 | 0 |
  | dev_lao | 1/262 | +0,25 |

- **Kết luận: không đáng đưa vào agent lúc này.** Model đã tự làm đúng kiểu A; còn B và C không thể bắt bằng so khớp tên.
- **Kiểm tra nguồn gốc giá trị của slot thường** (giá trị phải có trong câu, history hoặc kết quả tool) **không làm tất định được**. Theo đo đạc cũ, khoảng 15% giá trị là ngày giờ phải tính, 11% là số phải tính, và gần như không giá trị nào là nguyên văn lời nói, nên luật này sẽ báo nhầm nhiều. Chỉ ghi lại như một giả thuyết.

## 5. Thiết kế bộ sinh dữ liệu (`lifemate/counterfactual.py`)

Mỗi mẫu tổng hợp là **một mẫu fit được viết lại câu**, sao cho hành động đúng đổi chiều. Mẫu gốc giữ nguyên trong dữ liệu làm vế còn lại của cặp.

| Loại | Nguồn | Viết lại | Nhãn mới |
|---|---|---|---|
| **C** | Mẫu execute; lệnh ghi **cuối cùng**; một tham số bắt buộc, không phải ID, **thuộc loại nhãn từng hỏi trong fit**, giá trị không chép từ kết quả tool hay history | Bỏ đúng thông tin của slot đó | Các call trước lệnh ghi + `ask_missing(tool, [slot])` |
| **B-vague** | Mẫu execute; lệnh ghi cuối chọn ID trong danh sách ≥ 2 mục; câu gốc có từ chỉ thuộc riêng mục đó | Bỏ hoặc thay các từ phân biệt bằng cách nói mơ hồ, để ≥ 2 mục cùng khớp | Các call trước lệnh ghi + `ask_missing(tool, [id])` |
| **B-specific** | Mẫu hỏi lại kiểu B mà tool đích chỉ có một tham số bắt buộc là ID; mục được chọn phải có từ trùng với câu và có từ chỉ thuộc riêng nó | Thêm từ phân biệt của mục đó vào câu | Các call trước lần hỏi + lệnh ghi với ID đó |

- **Không sinh cho kiểu A**, vì model đã học được.
- **Không sinh C cho content hay title:** dữ liệu không có tiền lệ về cách nhãn xử lý khi thiếu các slot này.
- **Nguồn không bao giờ lấy từ dev_random hay dev_lao.** Sau khi loại cả hai, nguồn của fit_random và fit_lao trùng nhau: **223 nguồn C** (20 tool), **200 nguồn B-vague** (31 tool), **8 nguồn B-specific** (7 tool).
- **Mọi mẫu phải qua các kiểm tra sau** (`build` loại và ghi lý do):
  1. Nhãn phát lại được qua ToolEnv của mẫu gốc; không call nào lỗi hoặc trả `done=false`.
  2. Hỏi lại nằm cuối và hỏi đúng 1 tham số.
  3. Đoạn bỏ đi phải có trong câu gốc và không còn trong câu mới; đoạn thêm vào phải có trong câu mới.
  4. Giá trị đã bỏ không còn ở dạng khác. Ví dụ bỏ 50000 thì không được còn "50.000", "50 nghìn" hay "50k"; bỏ giờ thì không được còn "5:30", "5 giờ".
  5. B-vague không còn từ phân biệt; B-specific có ít nhất một từ phân biệt.
  6. Phần còn lại giữ gần nguyên (độ giống `difflib` ≥ 0,6).
  7. Nguồn thuộc fit và không thuộc dev; nhãn không dùng app giữ riêng.
- **Đưa vào SFT:** `lifemate.sft --extra-samples gen/d_<split>.jsonl`. Mẫu D đi qua cùng các bước đổi tên, thêm app nhiễu và viết thường như mẫu gốc, có cột `src = synthetic-D`. Không truyền tham số này thì cả bốn file SFT cũ dựng lại giống từng byte.
- **Dữ liệu sinh ra nằm ở `lifemate/gen/`** (đã gitignore), vì bắt nguồn từ dữ liệu đề.

## 6. Chạy thử trên fit_lao [Can thiệp]

- **Quy trình:**
  1. `candidates` chọn 49 task trải trên 35 tool: 30 C, 10 B-vague, 9 B-specific.
  2. Claude viết lại **27 task** và **bỏ qua 22 task**, có ghi lý do.
  3. `build` giữ lại **23 mẫu** (11 C, 5 B-vague, 7 B-specific); mọi mẫu giữ lại đều phát lại thành công.
  4. 4 mẫu bị loại vì nguồn nằm trong dev_random, trong đó có `train_1409` mà Codex từng phân tích. Bước `candidates` nay loại các nguồn này ngay từ đầu.
- **Lý do bỏ qua** (cho biết bộ chọn nguồn cần lọc thêm gì):

  | Lý do | Số task |
  |---|---:|
  | Giá trị phải tính ("thêm ngàn rưỡi", "trước họp hai tiếng", giá vé…) | 6 |
  | Giá trị lấy từ history, hoặc câu chỉ là câu trả lời cho lượt trước | 5 |
  | Bỏ hành động đi thì câu vô nghĩa ("tắt tiếng tivi") | 3 |
  | Câu vẫn suy ra được mục cần chọn, nên không thật sự mơ hồ | 3 |
  | Tự sửa kèm điều kiện, bỏ slot làm câu rối | 2 |
  | Từ phân biệt trùng với một ý khác trong câu ("máy rửa **bát**" / "cất **bát**") | 2 |
  | Mục được chọn không khớp câu (từ chung "gói") | 1 |

- **Ví dụ:**
  - **C:**
    - Gốc: "…với đặt báo thức năm giờ rưỡi sáng mai giúp anh."
    - Mới: "…với đặt báo thức sáng mai giúp anh."
    - Nhãn: `alarm.create(time)` → `ask_missing(alarm.create, [time])`.
  - **B-vague:**
    - Gốc: "Giữ giùm anh chiếc xe đạp chở hàng ở trạm Chợ Hôm nha…"
    - Mới: "Giữ giùm anh một chiếc xe đạp ở trạm Chợ Hôm nha…"
    - Trạm có 2 xe, nên nhãn: `reserve(bike_07)` → `ask_missing(bike_rental.reserve, [bike_id])`.
  - **B-specific:**
    - Gốc: "Con xoá lẹ giùm cô cái nhắc đi chợ nghe."
    - Mới: "Con xoá lẹ giùm cô cái nhắc đi chợ Cồn mua đồ đám giỗ nghe."
    - Nhãn: `ask_missing(reminders.delete, [reminder_id])` → `reminders.delete(rem_1307)`.
- **Ước lượng bộ đầy đủ** (thô, theo tỉ lệ của lần chạy thử): khoảng 100 mẫu C, 120 mẫu B-vague và dưới 8 mẫu B-specific, tức **khoảng 230 mẫu, tương đương khoảng 700 dòng SFT** sau khi tăng cường.

## 7. Rủi ro và giới hạn

1. **Nhãn sinh ra dựa trên suy luận về chính sách, chưa được BTC xác nhận.**
   - B-specific và C giữ nguyên tham số của các lần tra cứu từ câu gốc. Với câu đã sửa, đáp án thật có thể tra bằng truy vấn khác.
   - Chính sách tra danh bạ trước khi hỏi số tiền có ngoại lệ (17:2).
2. **Người viết lại có "thói quen" riêng.** Toàn bộ câu do Claude viết, nên văn phong có thể khác người dùng thật. Cần Anh đọc tay, và cần đo trên tập chưa dùng để sinh dữ liệu.
3. **Tỉ lệ bỏ qua ở C cao (16/30).** Bộ chọn nguồn nên lọc thêm câu ngắn trả lời lượt trước, giá trị phải tính, và dùng danh sách từ dừng cho B-specific. Chưa làm.
4. **B-specific quá ít nguồn (8).** Nếu cần cân bằng hỏi lại và tự làm, phải mở rộng sang tool có nhiều tham số bắt buộc, khi đó phải sinh cả các tham số còn lại.
5. **dev_random đã bị phân tích kỹ.** D chỉ dùng thống kê tổng hợp trên dev, không sửa theo từng mẫu dev. Nguồn đã loại cả hai tập dev.
6. **Có thể làm tăng hỏi thừa.** Tiêu chí giữ/bỏ ở mục 8 có ràng buộc riêng cho việc này.

## 8. Protocol train D (cần Anh duyệt riêng)

| Lượt | Train | Chấm | Đối chứng | Thay đổi duy nhất |
|---|---|---|---|---|
| D-lao | `fit_lao` + D, **giữ đúng 254 bước** (`--max-steps 254`) | dev_lao (262) | final `q17b_fit_lao` (35,53) | Thêm khoảng 700 dòng D |
| D-random | `fit_random` + D, **giữ đúng 260 bước** | dev_random (233) | final `q17b_fit_random` (53,92) | Như trên |

- **Lý do giữ số bước:** để tách hiệu ứng của dữ liệu khỏi hiệu ứng thêm compute. Cái giá là khoảng 14% dòng gốc không được thấy trong 1 lượt. Nếu Anh muốn, chạy thêm một lượt đủ 1 epoch để so.
- **Giữ D nếu cả bốn điều kiện đều đạt:**
  - Hỏi lại trên dev_lao tăng ≥ 10 điểm.
  - Số mẫu execute bị hỏi thừa không tăng quá 3, trên cả hai dev.
  - Điểm tổng dev_lao tăng, với khoảng tin cậy 95% theo cặp loại 0.
  - dev_random không giảm quá 1 điểm.
- **Chi phí:** khoảng 3,3 giờ mỗi lượt trên laptop, chạy bằng `systemd-run` (mẫu lệnh ở [EVAL mục 5.3](EVAL_2026-10-29.md)), cộng thời gian sinh và đọc dữ liệu.

## 9. Việc tiếp theo

- **Anh:**
  - Đọc tay 23 mẫu trong `lifemate/gen/review_fit_lao.md` (chỉ có trên máy Anh): đánh dấu mẫu hợp lý, ghi lý do mẫu sai.
  - Quyết có sinh đủ bộ (khoảng 230 mẫu) và chạy hai lượt ở mục 8 hay không.
- **Claude, nếu được duyệt:**
  - Lọc thêm ở bước chọn nguồn (mục 7.3).
  - Sinh và viết lại đủ bộ, chạy `build` và báo cáo.
  - Chạy D-lao rồi D-random.
- **Leader:** VieNeu (TTS tiếng Việt, https://www.vieneu.io/) có thể dùng để tạo audio tăng cường cho ASR (Q18). Đây là phần ASR, ngoài phạm vi D. Trang chưa ghi licence, kích thước model hay khả năng chạy offline, nên cần kiểm theo thể lệ trước khi dùng.

## Tái lập

```bash
cd lifemate
.venv/bin/python scripts/ask_policy_stats.py --fit splits/fit_random.txt splits/fit_lao.txt \
  --runs runs/sft_q17b_fit_random_rerun:splits/dev_random.txt runs/sft_q17b_fit_lao:splits/dev_lao.txt \
         runs/sft_q17b_fit_random_probefit:splits/probe_fit_random_233.txt
.venv/bin/python -m lifemate.tests.test_counterfactual
```
