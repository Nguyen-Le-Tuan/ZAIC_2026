# Sinh dữ liệu và tự cải thiện model: phân tích và đề xuất

*Claude viết ngày 08/11/2026, trong lúc Codex tra cứu model (`docs/CODEX_MODEL_COMBOS_PROMPT_2026-11-08.md`). Đây là bản suy luận và đề xuất; **chưa viết code, chưa train, chưa gọi API**. Các số đo mới ở mục 1 chạy trên CPU, chỉ dùng nhãn train và **hành vi** của chính hệ thống trên public (không dùng hay suy ra nhãn public).*

---

## 0. Tóm tắt

1. **Nhãn của BTC có cấu trúc rất chặt, và catalog mô tả gần đủ cấu trúc đó.**
   - Mọi ID trong lệnh ghi đều có nguồn: 922 lấy từ call đọc trong lượt, 308 từ history, chỉ 1 không rõ nguồn.
   - 96% ID lấy từ call đọc đến từ **đúng tool đọc mà catalog ghi là trả về collection đó** (`x-ref` ↔ `returns`).
   - 76% call đọc chỉ điền tham số bắt buộc.

   Điều này ủng hộ giả thuyết nhãn được sinh bằng chương trình theo kịch bản, không phải do LLM tự do.
2. **Hai pilot dữ liệu sinh trước đây làm ngược thứ tự:** LLM viết kịch bản, rồi LLM khác giải ra call. Quy ước của call vì vậy trôi theo thói quen LLM. Đề xuất chính là **"chương trình trước, lời nói sau"**: code sinh nhãn từ catalog và simulator, LLM chỉ viết câu nói.
3. **Một lỗi mới, đo được, rất cụ thể ở app mới:**
   - Bản 51,16 có 98 lệnh tìm kiếm trả về rỗng trong 55 mẫu (8,7% public), chủ yếu ở app mới. Nguyên nhân là model tự thêm bộ lọc tuỳ chọn hoặc viết query quá dài.
   - Trong nhãn train, lệnh tìm kiếm có tham số **gần như không bao giờ rỗng (4/555)**, và không lần nào được nối bằng hỏi lại. Vậy kết quả rỗng gần như chắc là lỗi của ta.
   - Sau khi gặp rỗng, model lại hỏi lại (37), lặp lại (30) hoặc dừng (22).
   - Đây là chỗ dữ liệu sinh (và một lớp code nhỏ) nhắm trúng được.
4. **Pilot v2 chưa chứng minh dữ liệu sinh vô ích.** Trên chữ chuẩn, app bị giấu tăng +2,4, nhưng độ lệch giữa hai seed là 4,4, nên thiết kế thí nghiệm không đủ độ nhạy để thấy. Trên chữ ASR thì không tăng, vì dữ liệu sinh toàn chữ sạch và không đụng tới lỗi ASR ở tên riêng của app mới.
5. **Ba hướng nên làm trước** (sẽ xếp lại khi có báo cáo Codex):
   - **D2:** chưng cất lý lẽ ngắn từ Meta lên nhãn thật (rẻ, không rủi ro nhãn).
   - **D1:** dữ liệu sinh "chương trình trước" cho 11 app public (trần cao nhất, tốn công nhất).
   - **D5:** dữ liệu sửa sai và lớp code chống tìm kiếm rỗng và vòng lặp đọc.
   - **Ngân sách Meta khoảng 90 USD là đủ.** Nút thắt là thời gian code và GPU để đo đủ 2–3 seed, không phải tiền API.

---

## 1. Số đo mới (08/11)

### 1.1 Cấu trúc nhãn train (1.545 mẫu)

Chạy lại mọi số ở mục 1 (CPU, khoảng 10 giây, không cần `.venv`), trong thư mục `lifemate/`:

```bash
PYTHONPATH=. python3 ../docs/research/tools/label_policy_probe_2026-11-08.py --trace runs/e2e_public_q4b_all_phoft_trace.jsonl
```

| Đo | Kết quả |
|---|---|
| Collection có `x-ref` trong catalog train | 37; **33 có đúng 1 tool đọc** trả về nó, 2 không có tool nào |
| Nguồn của ID (`x-ref`) trong lệnh ghi | call trong lượt **922** · history **308** · không rõ **1** |
| ID lấy từ call trong lượt: có phải từ đúng tool đọc trả về collection đó | **886/922 (96%)** |
| Call đọc: tham số | chỉ tham số bắt buộc **1.212** (76%) · có thêm tuỳ chọn 387 |
| Call ghi: tham số | chỉ bắt buộc 1.124 (65%) · có thêm tuỳ chọn 601; tỉ lệ ô tuỳ chọn được điền 34,5% |
| Call đọc mà kết quả không được dùng lại | 511/1.599. Call kế tiếp là hỏi lại (132), đọc (183) hoặc ghi (196); 479/511 lần call kế tiếp thuộc **app khác**. Tức là đọc để **kiểm điều kiện**, để **phân giải trước khi hỏi**, hoặc để **trả lời thông tin**: do nội dung câu nói quyết định |
| `contacts.search` có từ 2 kết quả trở lên | hỏi lại ngay 74/103 · làm tiếp 26 · dừng 3. Có 1 kết quả: luôn làm tiếp (131/131) |
| Call đọc có tham số trả về danh sách rỗng | **4/555 (0,7%)**; không lần nào được nối bằng hỏi lại. Call đọc với `{}`: 0/902 |

**Đọc kết quả:**
- Call đọc trong nhãn chia làm hai loại.
  - **Đọc lấy ID:** quyết định hoàn toàn bởi schema. Ghi cần ID → gọi đúng tool đọc trả về collection đó, chỉ với tham số bắt buộc → chọn đối tượng → ghi.
  - **Đọc theo nghĩa:** điều kiện, hỏi thông tin, phân giải để hỏi lại. Do kịch bản quyết định.
- Cả hai đều viết được thành chương trình, **nếu ta biết kịch bản**. Khi sinh dữ liệu thì ta biết kịch bản, vì chính ta tạo ra nó.
- Đây cũng là lý do catalog có `x-ref`/`returns`. Prompt hiện tại không in hai trường này, và lượt thử in chúng (prompt `xref`) chỉ chạy 1 seed với −1,0, nằm trong nhiễu. Nên chưa thể kết luận là vô ích.

### 1.2 Hành vi của bản 51,16 trên public (chỉ đếm hành vi, không dùng nhãn)

| Hiện tượng | Số đo | Chi tiết |
|---|---|---|
| Lệnh tìm kiếm có bộ lọc trả về rỗng | **98 lần trong 55 mẫu** | `event_tickets.search` 26, `flights.search` 21, `train_bus_tickets.search` 19, `contacts.search` 8, `grocery.search` 6, `maps.search_place` 6 |
| Sau khi rỗng, model làm gì | hỏi lại 37 · gọi đọc lại 30 · dừng 22 · ghi 9 | Nhãn train gần như không bao giờ hỏi lại sau một lệnh đọc rỗng |
| `train_bus_tickets.search` | **thêm tham số tuỳ chọn `type`: rỗng 14/15**; chỉ tham số bắt buộc: rỗng 5/11 | Tự thêm bộ lọc làm mất kết quả |
| `event_tickets.search` (query tuỳ chọn) | có query: rỗng 24/34; gọi `{}`: trúng 2/2 | Query quá dài hoặc quá cụ thể |
| Vòng lặp đọc tới hết 8 bước | 18 mẫu, không gửi lệnh ghi hay hỏi lại nào | Chủ yếu `event_tickets.search`, `stocks.get_quote`, `flights.search` |
| Lệnh ghi không có tác dụng (`done: false`) | 51 lần trong 19 mẫu | `stocks` 14: mã cổ phiếu tự bịa |

**Ý nghĩa:**
- Ở app mới, model không biết quy ước **"tìm kiếm tối giản"** mà nhãn train tuân theo.
- Khi tìm không thấy, model không có chiến lược phục hồi, vì nhãn train **không bao giờ** dạy tình huống này: kịch bản của BTC luôn có đối tượng tồn tại.
- Lỗi ASR ở tên riêng (tên sự kiện, ga, sản phẩm) cũng dẫn tới đúng tình huống "tìm không thấy".

---

## 2. Vì sao hai pilot trước không ăn

| | Pilot 1 (02/11) | Pilot v2 (07–08/11) |
|---|---|---|
| Cách sinh | LLM viết kịch bản và câu nói; LLM khác giải ra call; giữ mẫu khi trạng thái cuối khớp | Như pilot 1, cộng khung kịch bản rút theo tỉ lệ thật (lịch sử, dùng lại ID, hai app, câu không gọi tool) |
| Quy mô | 280 mẫu, 6 app bị giấu, 1 seed | 202 mẫu, 6 app, **2 seed mỗi bên** |
| dev_lao, chữ ASR | −2,09 | −0,46 (app bị giấu −0,98) |
| dev_lao, chữ chuẩn | −2,83 | +1,20 (**app bị giấu +2,39**) |
| Ghi chú | trạng thái đúng tăng (51,5% → 53,4%) nhưng F1 giảm; app đã thấy giảm −4,7 | hai seed của **bản gốc** lệch nhau 4,36 điểm |

**Ba nguyên nhân về cấu trúc:**
1. **Nhãn do LLM giải, nên quy ước trôi.** Trạng thái cuối có thể đúng, nhưng chọn call đọc nào, điền tham số nào là thói quen của LLM. Pilot 1 đúng như vậy: trạng thái đúng nhiều hơn mà F1 thấp hơn.
2. **Dữ liệu sinh toàn chữ sạch.** Ở app bị giấu, ASR làm mất khoảng 10,7 điểm (49,99 → 39,26 trong pilot v2). Phần lớn mất ở tên riêng của app, đúng chỗ chữ sạch không dạy được gì.
3. **Thí nghiệm không đủ độ nhạy.** Luật cần +2,0 điểm trong khi độ lệch giữa hai seed là 4,4. Một hiệu ứng thật cỡ +2 có thể bị đánh trượt rất dễ.

---

## 3. Nguyên lý thiết kế mới

**P1. Chương trình trước, lời nói sau.**
1. Code tạo **kịch bản có cấu trúc**: ý định, đối tượng đích, ô nào được nói ra, có điều kiện không, có cần hỏi lại không.
2. Code sinh **nhãn** bằng chính sách đo được ở mục 1.1:
   - đọc lấy ID qua `x-ref` ↔ `returns`, chỉ tham số bắt buộc;
   - query bằng tên đã lưu của đối tượng (phát hiện 13 trong JOURNAL);
   - có từ 2 đối tượng khớp mà câu không phân biệt được thì `ask_missing_info(tool, [tham số])`;
   - tham số tuỳ chọn chỉ điền khi kịch bản ghi là người dùng có nói.
3. **Simulator thật** chạy nhãn để kiểm trạng thái. App public dùng `zaic_tools` của public_test (BTC cho phép), app train dùng `zaic_tools` của train. State do ta tự tạo, không đọc `*_environment/`.
4. **LLM (Meta) chỉ viết câu nói** đúng kịch bản: nói đúng những ô được đánh dấu, không thêm thông tin ngoài kịch bản. Kèm giọng vùng miền, tự sửa giữa câu, chêm tiếng Anh theo tỉ lệ thật.
5. **Bộ kiểm bằng code:** mọi giá trị ô được nói phải tìm thấy trong câu (số, giờ, tên; dùng `vinum.py`); ô không được nói thì không được xuất hiện.

**P2. Sinh đúng chỗ đang hỏng.** Kịch bản cho tìm kiếm tối giản; kịch bản "tìm rỗng thì nới bộ lọc hoặc rút ngắn query rồi tìm lại"; kịch bản mã hay ID chỉ lấy từ kết quả tool; app không có tool tra mã thì hỏi lại hoặc không gọi, thay vì bịa.

**P3. Đưa ASR vào vòng sinh, có lọc "thông tin còn sống".**
- Câu sinh → TTS tiếng Việt (chỉ dùng lúc phát triển) → ASR của chính ta → chữ có lỗi giống thật.
- Chỉ giữ mẫu mà thông tin cần cho nhãn **vẫn còn suy ra được** từ chữ ASR, hoặc phục hồi được bằng một lệnh tìm nới lỏng mà simulator xác nhận là trúng.
- **Giả thuyết vì sao "agent học trên chữ ASR" trước đây hại chữ chuẩn (−5,4):** khi ASR đã làm mất thông tin mà nhãn vẫn đòi giá trị đúng, model học cách **bịa**. Lọc như trên tránh đúng điều này.

**P4. Đo đủ mạnh.**
- Mỗi bên tối thiểu 2 seed, tốt nhất 3.
- Ngưỡng giữ/bỏ đặt theo độ lệch đã đo, kèm một lát cắt mục tiêu viết trước. Ví dụ: các mẫu dev_lao mà nhãn có tìm kiếm ở app bị giấu.
- Tách hai phần: trạng thái đúng (hash) và F1.

---

## 4. Các phương án cụ thể

| # | Phương án | Nhắm vào | Chi Meta (ước) | Công | GPU | Bằng chứng | Rủi ro |
|---|---|---|---|---|---|---|---|
| **D1** | Dữ liệu sinh **chương trình trước** cho 6 app dev_lao (pilot), rồi 11 app public | App mới (theo dự đoán của bản 51,16, 43% mẫu public có gọi tool của chúng) | 15–30 USD (chủ yếu viết câu nói) | 2–3 ngày code (dùng lại khung state và simulator trong `lifemate/synth.py` của nhánh `synth-v2`) | pilot 2×2 seed, rồi train bản nộp | Mục 1.1 (cấu trúc nhãn); v2 chữ chuẩn +2,4 ở app bị giấu | Kịch bản không phủ hết kiểu yêu cầu; câu nói đơn điệu; quy ước riêng từng app public không kiểm được |
| **D2** | **Chưng cất lý lẽ ngắn từ Meta lên nhãn thật:** đưa model Meta mẫu train kèm nhãn đúng, nhờ viết 1–2 câu kế hoạch (cần ID gì, lấy ở đâu, vì sao hỏi lại hay bỏ qua). Train 4B sinh câu kế hoạch đó rồi mới gọi tool | Quyết định làm / hỏi / bỏ qua (+10,6 so với API) và chọn ID (+5,0) | 8–15 USD (1.545 mẫu × vài biến thể) | 1 ngày (đổi định dạng SFT, sửa parse) | 2×2 seed | Kỹ thuật dạng "distilling step-by-step" / STaR; chưa đo trên LifeMate | Thêm khoảng 30–50 token mỗi bước (máy chấm RTX 5090 thừa thời gian); có thể không tăng |
| **D3** | Viết lại câu nói của mẫu train (giọng vùng miền, tự sửa giữa câu, chêm tiếng Anh, cách đọc số), **giữ nguyên nhãn**, kiểm ô bằng code | Độ bền ngôn ngữ | 5–10 USD | 0,5 ngày | đi kèm D1/D2 | Chuẩn trong ngành | Tăng ít; câu viết lại lệch nghĩa thì nhãn sai |
| **D4** | **TTS → ASR:** sinh audio cho câu nói (sinh và thật) bằng TTS tiếng Việt; (a) fine-tune ASR trên từ vựng của app mới; (b) cho agent học trên chữ ASR có lọc (P3) | ASR (khoảng 13 điểm), nhất là tên riêng ở app mới | 0 (TTS chạy local) | 1–2 ngày | ASR fine-tune vài giờ | Phụ thuộc chất lượng và licence TTS (Codex đang tra) | Audio TTS khác giọng người thật; **nếu audio của BTC vốn là TTS thì lợi rất lớn** (mục 7) |
| **D5** | **Dữ liệu sửa sai** (DAgger): chạy 4B trên train, tìm bước đi sai (tìm rỗng, lặp đọc, thêm bộ lọc); tạo mẫu "từ trạng thái sai này, bước đúng tiếp theo là gì". Kèm **lớp code**: tìm rỗng thì nới một lần, cấm gọi lại đúng lệnh đọc cũ | Vòng lặp đọc (18 mẫu), tìm rỗng (55 mẫu) | 0 | 1 ngày | 1 lượt suy luận trên train | Mục 1.2; DAgger là phương pháp kinh điển | Lớp code làm thêm call đọc nên giảm F1, nhưng mẫu đang 0 điểm thì không mất gì |
| **D6** | **Trung bình LoRA nhiều seed** (model soup) | Nhiễu 2–4 điểm giữa các lần train | 0 | vài giờ | cần 2–3 lượt train cùng công thức | Model soups (Wortsman và cộng sự, 2022) | LoRA khác seed có thể không trung bình được tốt; phải đo |
| D7 | Self-training có verifier: 4B (hoặc Meta) thử nhiều lần trên kịch bản D1, giữ lời giải mà simulator xác nhận | Phủ thêm cách làm đúng | 5–20 USD nếu dùng Meta | 1 ngày | lớn | RFT, STaR | Lặp lại thói quen sai của chính model |
| D8 | RL với phần thưởng kiểm chứng được (GRPO trên ToolEnv) | Toàn bộ chính sách | 0 | nhiều | **rất lớn** | Nhiều paper 2025 cho tool use | Không kịp trước 16/11; để sau cuộc thi |

**Xếp hạng tạm** (trước khi có báo cáo Codex): **D5** (chắc nhất, rẻ) → **D2** (rẻ, nhắm trúng chỗ chênh lớn nhất) → **D1** (trần cao nhất, tốn công nhất) → **D4** (phụ thuộc kết quả nghe audio và licence TTS) → D6 (đi kèm nếu đằng nào cũng train nhiều seed) → D3 → D7. D8 để sau.

Các phương án này **không phụ thuộc model**: nếu Codex tìm ra LLM tốt hơn (ví dụ Qwen3.5-4B), cùng bộ dữ liệu vẫn dùng để train model mới.

---

## 5. Dùng 90 USD credit Meta

Số tham khảo từ sổ chi cũ: sinh và giải một mẫu đạt khoảng 0,041–0,044 USD; agent API mức suy nghĩ cao khoảng 0,024 USD mỗi mẫu. Cách "chương trình trước" chỉ nhờ LLM viết câu nói, nên rẻ hơn nhiều. **Phải chạy thử 20 mẫu để đo giá thật trước khi chạy lô lớn.**

| Hạng mục | Ước chi | Ghi chú |
|---|---:|---|
| Thử giá và chất lượng (20 mẫu mỗi loại) | 2 | Bắt buộc trước mọi lô |
| D2: lý lẽ ngắn cho 1.545 mẫu train (1–2 biến thể) | 8–15 | Không cần kiểm nhãn |
| Đối tượng và state cho 11 app public và 6 app dev_lao (tên sự kiện, sản phẩm, ga, món ăn, mã cổ phiếu…) | 5–10 | Một lần, dùng lại nhiều kịch bản |
| D1: câu nói cho khoảng 1.500–2.500 kịch bản | 15–30 | Kiểm ô bằng code, không tốn API |
| D3: viết lại câu nói train | 5–10 | |
| Dự phòng | 20–30 | Cho lô bổ sung nếu pilot qua luật |

---

## 6. Lịch khả thi (chạy song song với L9, không được làm chậm L9)

| Ngày | Việc |
|---|---|
| 09/11 | Đọc báo cáo Codex, xếp hạng model (Claude). Leader nghe audio (mục 7). Quyết hướng và quyết có thuê GPU cloud không |
| 09–10/11 | Code D5 (lớp chống tìm rỗng và lặp, đo ngay trên adapter cũ vì chỉ đổi lúc suy luận) và D2 (định dạng SFT mới). Bắt đầu D1 |
| 10–11/11 | Pilot trên dev_lao, 2–3 seed mỗi bên: gốc, +D2, +D1. Cần khoảng 6–9 lượt train 4B: máy anh trai mất 2 đêm; GPU thuê thì vài giờ |
| 12/11 | Train bản nộp với tổ hợp qua luật, trên đủ dữ liệu, 2 seed (thêm D6 nếu được) |
| 13/11 | Chốt adapter và ASR, thay vào image, chạy lại B28 |
| 14–16/11 | Chỉ còn việc Docker (L9) |

**Nhận xét thẳng:** với máy anh trai (1 lượt mỗi ngày) và laptop 8 GB, lịch này **chỉ vừa đủ cho 1 vòng pilot**. Muốn đo 2–3 seed cho nhiều phương án thì nên thuê GPU cloud. Đội từng ghi là ngân sách thuê GPU không giới hạn, nhưng chưa thuê lần nào. Codex đang ước giá.

---

## 7. Việc người làm được ngay: nghe 20 audio train (30 phút, đúng vai Leader)

Nghe 20 file wav lượt cuối ngẫu nhiên trong `data/train+public_test/train/audio/`, ghi lại:
- **Giọng người thật hay TTS?** (nhịp, hơi thở, độ đều, có lỗi đọc không);
- bao nhiêu giọng khác nhau; giọng Bắc / Trung / Nam;
- có tiếng ồn không; tốc độ nói;
- tên riêng, số và giờ được đọc thế nào.

**Vì sao quan trọng:**
- Nếu audio là TTS, chọn được TTS gần giống để sinh audio (D4) có thể đẩy ASR lên rất cao. Đây là một ứng viên cho câu hỏi "vì sao top đạt 96".
- Nếu là người thật, D4 vẫn có ích cho từ vựng app mới, nhưng kỳ vọng thấp hơn.
- Đây cũng là việc HUMAN_TODO giao từ 30/10 (B5/L5) mà chưa ai làm.

*Chỉ nghe audio train. Không nghe để ghi lại nội dung audio public.*
