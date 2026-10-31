# Lệnh ghi sai vì sao, và mỗi nguyên nhân đáng bao nhiêu điểm (30/10/2026)

*Anh chọn "Làm luôn" sau báo cáo chốt chặn ID ([`ID_GUARD_2026-10-30.md`](ID_GUARD_2026-10-30.md)). Chỉ dùng CPU, không train, không chạy model, chỉ dùng dữ liệu train. Script: `lifemate/scripts/param_errors.py` ([PR #5](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/5)). Số liệu: [`baselines/param_errors_2026-10-30.json`](baselines/param_errors_2026-10-30.json).*

## Kết luận

1. **Mất điểm nhiều nhất là do không làm đủ, không phải do điền sai tham số.**
   - Nếu sửa được hết các lệnh ghi bị thiếu: dev_random +6,2 điểm; dev_lao +8,4 (B0) và +14,4 (D3).
   - Nếu bỏ được hết lệnh ghi sai tool hoặc ghi thừa: thêm +2,6 / +6,8 / +5,5.
   - Lệnh ghi bị thiếu có hai nguồn:
     - **Model tự dừng** khi chưa làm hết (20 / 33 / 44 mẫu). Thường là yêu cầu nhiều vế mà chỉ làm một phần, hoặc câu điều kiện đi nhầm nhánh.
     - **Model hỏi lại thay vì làm** (14 / 15 / 33 mẫu). D3 hỏi lại nhiều hơn hẳn, khớp với số hỏi thừa đã đo (15 → 34).
2. **Trong lỗi tham số, nhóm lớn nhất là chọn nhầm ID (+4–5 điểm), rồi tới ngày giờ (+2–4).** Các nhóm còn lại mỗi nhóm khoảng ≤ 2 điểm: số, chữ tự do, tham số thừa, enum.
   - Sửa hết mọi lỗi tham số cùng lúc được khoảng +14–16 điểm.
   - Sửa hết mọi lỗi lệnh ghi được +30 / +39 / +42 điểm. Phần còn lại tới 100 là quyết định hỏi lại / ngoài phạm vi, và call đọc.
3. **Hầu hết là lỗi suy luận, không có luật code rẻ nào sửa được.** Ví dụ: chọn đúng đối tượng, làm đủ các vế, đi đúng nhánh điều kiện, tính giờ nhiều bước.
   - Điều này ủng hộ hai hướng trong báo cáo Codex: thử model 4B (cần Anh quyết thuê cloud), và dữ liệu SFT có nhiều vế hoặc điều kiện.
   - Phần rẻ hơn có thể làm: quy ước sáng/tối và "tuần sau" trong ngày giờ.

"Đáng bao nhiêu điểm" ở đây là **sửa giả định**:
- Sửa đúng một nguyên nhân bằng giá trị của đáp án, giữ nguyên mọi thứ khác, chạy lại trên ToolEnv rồi chấm.
- Đây là trần cho việc sửa hoàn hảo nguyên nhân đó, không phải mức sẽ đạt.
- Một mẫu có nhiều lỗi chỉ được điểm khi sửa hết, nên cộng các dòng lại không ra dòng "mọi lỗi".

## Điểm thêm nếu sửa hoàn hảo từng nguyên nhân (điểm trên thang 100)

| Nguyên nhân | dev_random (`q17b_fit_random`) | dev_lao, B0 | dev_lao, D3 |
|---|---:|---:|---:|
| *Điểm gốc* | *53,92* | *35,53* | *31,23* |
| **Thiếu lệnh ghi** (tự dừng, hoặc hỏi lại thay vì làm) | **+6,15** | **+8,36** | **+14,37** |
| **Sai tool hoặc ghi thừa** | +2,63 | **+6,82** | +5,47 |
| **ID chọn nhầm** (đã thấy, nhưng sai đối tượng) | **+4,86** | +3,98 | +4,57 |
| **Ngày giờ** | +3,96 | +3,90 | +1,84 |
| Số | +2,13 | 0 | 0 |
| Chữ tự do (token-F1 ≤ 0,6) | +1,04 | +1,05 | +1,43 |
| Thừa tham số tuỳ chọn | +0,43 | +1,11 | +1,75 |
| Chuỗi phải khớp chính xác | +0,43 | +0,99 | +0,28 |
| Enum | +0,86 | +0,19 | 0 |
| Mảng | +0,82 | +0,48 | +0,57 |
| Thiếu tham số | +0,43 | +0,33 | +0,45 |
| Số điện thoại | 0 | 0 | +0,38 |
| *Mọi lỗi tham số cùng lúc* | *+16,42* | *+16,43* | *+14,48* |
| *Mọi lỗi lệnh ghi cùng lúc* | *+29,94* | *+38,78* | *+42,04* |

Tham khảo, lượt `q17b_fit_random` trên 233 mẫu fit mà model đã train qua: điểm gốc 80,22; mọi lỗi lệnh ghi cùng lúc +11,60.

## Số lệnh ghi sai theo nguyên nhân (một call có thể có nhiều nguyên nhân)

| | dev_random | B0 dev_lao | D3 dev_lao |
|---|---:|---:|---:|
| Lệnh ghi đúng / sai | 157 / 91 | 140 / 157 | 120 / 135 |
| Lệnh ghi bị thiếu (đáp án có, lượt chạy không làm) | 39 | 58 | 89 |
| Sai tool hoặc ghi thừa | 35 | 64 | 53 |
| Ngày giờ | 18 | 23 | 18 |
| ID | 17 | 23 | 25 |
| Chữ tự do | 14 | 30 | 29 |
| Thừa tham số tuỳ chọn | 4 | 17 | 17 |
| Chuỗi khớp chính xác | 1 | 13 | 5 |
| Số | 6 | 0 | 0 |
| Thiếu tham số / mảng / enum / số điện thoại | 1 / 2 / 3 / 0 | 6 / 4 / 1 / 0 | 5 / 3 / 0 / 1 |

Cách ghép ở đây là một-một: một lệnh trong đáp án đã khớp đúng thì không được dùng để ghép nữa. Vì vậy số lỗi ID (17) khác số 23 trong báo cáo chốt chặn ID, nơi cách ghép lỏng hơn.

## Chi tiết từng nhóm

### Lệnh ghi bị thiếu

| Lý do (số mẫu) | dev_random | B0 dev_lao | D3 dev_lao |
|---|---:|---:|---:|
| Model tự dừng ("done") | 20 | 33 | 44 |
| Model hỏi lại thay vì làm | 14 | 15 | 33 |
| Hết số lần thử lại | 0 | 1 | 1 |

- Không mẫu nào dừng vì hết giờ hay hết bước.
- **Câu có điều kiện** ("nếu mưa thì…, không thì…"). Số này đếm nhanh bằng regex, chưa nằm trong script, chỉ để định hướng.
  - Ở dev_random, loại câu này chiếm khoảng 33/162 mẫu execute có lệnh ghi, nhưng điểm thấp hơn rõ (39,9 so với 54,4) và chiếm 7/19 ca model tự dừng mà còn thiếu lệnh ghi.
  - Ở dev_lao không thấy khác biệt (40,9 so với 39,0).
- **Phần còn lại phần lớn là yêu cầu nhiều vế làm thiếu một vế.** Ví dụ: dời lịch, rồi mở phòng họp online; model mở phòng họp nhưng tạo lịch mới thay vì dời lịch cũ.

### Ngày giờ

- **dev_random:** 15 sai giờ trong ngày, 7 sai ngày. Lệch từ 30 tới 180 phút, hoặc +2 / +4 ngày.
  - Gần như đều là phép tính giờ nhiều bước dựa trên giờ của một sự kiện khác. Ví dụ: "đón sớm 30 phút so với giờ hẹn", "đặt báo thức trước đó một tiếng" sau khi đã dời lịch, "dời muộn thêm nửa tiếng".
- **dev_lao (B0):** 14 sai ngày, 11 sai giờ.
  - Có nhầm sáng/tối: "chín giờ tối" thành `09:00` hoặc `23:00`, lệch đúng 720 phút ×2.
  - Có nhầm "thứ ba tuần sau" (+7 ngày ×3), và nhầm tháng.
- **Phần rẻ có thể sửa:** quy ước sáng/tối và "tuần này / tuần sau".
  - Ví dụ: thêm nhãn tuần vào bảng ngày trong prompt, hoặc một bộ chuẩn hoá giờ nói tiếng Việt.
  - Đổi prompt thì phải train lại mới đo công bằng được. Phép tính nhiều bước là phần suy luận, không có cách rẻ.

### Các nhóm khác

- **Số:** 6 call ở dev_random, đều là lỗi tính toán; không có lỗi lệch hàng nghìn (×1000). Ví dụ "giảm còn phân nửa", "thêm hẳn một trăm", lấy đúng tiền hoá đơn tháng này.
- **Chữ tự do:** nội dung tin nhắn, nhắc việc, tiêu đề. 12/14 ở dev_random có token-F1 từ 0,3 tới 0,6, tức là gần đúng nhưng diễn đạt khác.
- **Thừa tham số tuỳ chọn:** chủ yếu `robot_vacuum.start.mode = "vacuum"` (9–10 lần ở dev_lao), trong khi đáp án bỏ trống.
  - Schema không khai báo giá trị mặc định nào, nên không có luật code để bỏ. Đây là quy ước model phải học.
- **Chuỗi khớp chính xác ở dev_lao:** chủ yếu `loyalty.redeem`. Model điền tên chương trình thay cho mã (`prog_…`), và điền mã quà không khớp đáp án.
  - `reward_id` có mô tả "ID lấy từ state…" nhưng không có `x-ref`, nên chốt chặn ID không bắt được.
- **App chỉ có ở train:** `robot_vacuum`, `loyalty`, `video_meeting`, `home_automation`, `library` không có ở public. Các lỗi riêng theo app ở dev_lao không chuyển sang public, nhưng các nhóm lỗi thì có.

## Ý nghĩa cho kế hoạch

1. **Ưu tiên dữ liệu và model hơn luật code.**
   - Các nguyên nhân lớn nhất (thiếu vế, nhầm nhánh điều kiện, chọn nhầm đối tượng, tính giờ nhiều bước) đều là lỗi suy luận.
   - Hai hướng nên làm: dữ liệu SFT có yêu cầu nhiều vế và điều kiện, kiểm chứng bằng ToolEnv (P1 trong báo cáo Codex); và model 4B (cần Anh quyết thuê cloud).
2. **Thí nghiệm D:** lỗi "hỏi lại thay vì làm" ở D3 tăng từ 14 lên 33 mẫu. Đây đúng là cái giá của D, nên khi so D3 với B-up cần nhìn cả hai phía.
3. **Ngày giờ:** phần sáng/tối và "tuần sau" có thể thử bằng prompt hoặc chuẩn hoá. Cần một lượt train lại để đo, nên làm sau giai đoạn 2.
4. **Không làm:** luật bỏ tham số tuỳ chọn (không có giá trị mặc định để dựa vào), và luật ×1000 cho số tiền (không thấy lỗi này).

## Giới hạn

- **Chỉ đo trên chữ chuẩn `audio_text`.** Với chữ ASR, nhóm số, ngày giờ và chữ tự do có thể tăng. Lượt đo đầu-cuối đêm nay sẽ cho biết.
- **Sửa giả định không phải điều model sẽ làm.** Nó chỉ cho biết trần của từng nguyên nhân.
- **Phân loại chỉ dùng kiểu trong schema.** Ví dụ `loyalty.redeem.program` bị xếp vào "chuỗi khớp chính xác" dù thực chất là một mã.

## Chạy lại

```bash
cd lifemate
.venv/bin/python scripts/param_errors.py --run runs/sft_q17b_fit_random --run runs/sft_q17b_fit_lao \
    --run runs/sft_q17b_lao_d3 --run runs/sft_q17b_fit_random_probefit --json runs/param_errors.json
```

Mất khoảng 14 giây trên CPU. File JSON trong `runs/` có thêm ví dụ giá trị; bản trên `main` đã bỏ phần ví dụ.
