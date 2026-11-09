# Xếp hạng phương án tuần cuối (sau báo cáo Codex)

*Claude viết ngày 08/11/2026. Đầu vào:*
- *báo cáo Codex `docs/research/CODEX_MODEL_COMBOS_2026-11-08.md` (153 ứng viên, 20 tổ hợp, Pha D);*
- *phân tích dữ liệu sinh `docs/SYNTH_DATA_PLAN_2026-11-08.md`;*
- *kết quả Leader nghe 20 audio;*
- *các phép kiểm chéo Claude chạy hôm nay (mục 2, 3).*

*Hạn Docker 16/11 23:59 GMT+7; chốt model khoảng 13/11.*

---

## 0. Kết luận ngắn

1. **Không có "tổ hợp thần kỳ" lấp đầy trần tham số.**
   - Qwen3.5-4B text-only có 4,206B tham số, hơn Qwen3-4B 183M, nhưng phần tính toán (không kể embedding) lại **ít hơn**: 3,570B so với 3,634B. Phần tăng thêm nằm hết ở embedding, vì vocab lớn hơn (248K so với 152K token).
   - Nếu Qwen3.5 tốt hơn thì là nhờ **thế hệ huấn luyện mới**, không phải nhờ lấp đầy trần.
   - Trong 153 ứng viên, không có LLM mở nào cỡ 4,5–4,99B có bằng chứng mạnh hơn Qwen ở tiếng Việt cộng gọi tool. **Trần 5B không phải nút thắt về năng lực.**
2. **Ba tín hiệu thật, xếp theo độ chắc:**
   - (a) **Lỗi tìm kiếm rỗng và vòng lặp đọc** chạm 60 mẫu (9,5% public), sửa bằng code, đo thẳng trên public mà không vướng nhiễu train.
   - (b) **Qwen3.5-4B**: thế hệ mới, và ít nhất một đội khác cũng đang dùng.
   - (c) **Model Thinking cộng lý lẽ ngắn sinh bằng Meta.**
3. **Audio là giọng người thật, đọc theo kịch bản, đi qua một kênh bị lọc** (mục 3):
   - 99% năng lượng nằm dưới khoảng 3,5 kHz; phổ tụt 24 dB giữa 5 kHz và 6 kHz;
   - âm lượng chuẩn hoá quanh −26 dBFS.

   Mọi dữ liệu ASR thêm (TTS hay bộ dữ liệu ngoài) phải được đưa qua đúng kênh này.
4. **Gipformer (68M)** chưa fine-tune mà đã nghe đúng số 97% và giờ 100% trên 100 wav. Đáng thử làm **ASR phụ cho số và giờ**, vì vừa vặn với ngân sách tham số.
5. **Kỳ vọng thực tế tuần này:** cộng hết các bước khả thi thì có thể lên khoảng 55–62 public. **Lên 80 trong 5 ngày là không thực tế.** Chỉ hướng D1 (dữ liệu sinh đúng quy ước cho app mới) có trần đủ cao, nhưng rủi ro thời gian lớn nhất.
6. **Quyết định cần ngay:**
   - thuê GPU cloud cho các nhánh thử (khoảng 20–50 USD; mục 5);
   - gửi BTC câu hỏi về cách đếm tham số bản text-only (mục 6);
   - tạo file key Meta (mục 7).

---

## 1. Bảng xếp hạng

Kỳ vọng tính theo điểm public; số nào cũng là giả thuyết cho tới khi đo.

| Hạng | Phương án | Vì sao | Kỳ vọng | Công / GPU / tiền | Rủi ro | Kịp 13/11? |
|---|---|---|---|---|---|---|
| **1** | **D5: lớp chống tìm kiếm rỗng và vòng lặp đọc trên C0.** Tìm rỗng thì bỏ bộ lọc tuỳ chọn hoặc rút ngắn query, tìm lại một lần; không gọi lại đúng lệnh đọc đã có kết quả; không bịa mã khi app không có tool tra cứu | 60 mẫu public bị (9,5%); nhãn train gần như không bao giờ có tìm kiếm rỗng (4/555) | **+1 tới +3** | 0,5 ngày code; 1 lượt public trên laptop của Anh (khoảng 2 giờ); 0 USD | Thấp: chỉ kích hoạt khi kết quả rỗng hoặc lặp | **Có** |
| **2** | **A1: Qwen3.5-4B text-only + PhoWhisper-large-ft (C1 của Codex)**, cùng công thức SFT, thêm LoRA cho lớp linear attention | Thế hệ mới; transformers 5.21 đang pin đã chạy được (Claude kiểm); đối thủ cũng dùng | −4 tới +8 | Sửa nhỏ (`train.py` thêm `in_proj_qkv`, `in_proj_z`, `out_proj`); 2 seed × khoảng 3 giờ GPU | **Luật:** BTC có thể đếm cả checkpoint gốc (6,26B, vượt trần). Kiến trúc lai có thể chậm nếu thiếu kernel. Docker phải đổi model | Có, nếu thuê GPU |
| **3** | **A2: Qwen3-4B-Thinking-2507 + D2 (lý lẽ ngắn do Meta viết, đặt trong `<think>`)** | Cùng kiến trúc với C0 nên gần như không sửa code hay Docker; nhắm vào chỗ chênh lớn nhất so với model API (quyết định làm / hỏi / bỏ qua) | −3 tới +6 | Meta 10–20 USD; 1 ngày làm dữ liệu; 2 seed GPU | Lý lẽ dài thì chậm; có thể không tăng | Có, nếu thuê GPU |
| 4 | **D1 thu gọn: dữ liệu sinh "chương trình trước" cho các app mới có tool tìm kiếm** (event_tickets, train_bus_tickets, grocery, ecommerce, recipes, stocks…), đo bằng **public** (đúng các app đó) | Trần cao nhất cho app mới (43% mẫu public có gọi tool của chúng) | −2 tới +8 | 1,5–2 ngày code; Meta 10–25 USD; train 2 seed | **Thời gian:** có thể không xong. Mốc dừng: hết ngày 10/11 chưa có dữ liệu đạt kiểm thì bỏ | Rủi ro |
| 5 | **A3: Qwen3-4B-Instruct + D2 dạng "một câu kế hoạch"** | Tách riêng hiệu ứng của D2 khỏi việc đổi model | −2 tới +4 | 2 seed GPU | Thấp | Có, nếu dư GPU |
| 6 | **G3: Gipformer làm ASR phụ cho số và giờ** (C0 + Gipformer = 5,70B; C1 + Gipformer = 5,88B) | Pha D: số 97%, giờ 100% khi chưa fine-tune | 0 tới +1,5 | Leader đo PhoWhisper-ft trên đúng 100 wav đó trên máy 3050; viết luật thay số khi hai ASR khác nhau | Căn chỉnh hai transcript sai thì hỏng chữ | Có (chỉ cần chạy ASR) |
| 7 | **A4: SEA-LION v4 4B** (`aisingapore/Qwen-SEA-LION-v4-4B-VL`; MIT; nền Qwen3-VL-4B, tinh chỉnh cho tiếng Đông Nam Á; 4,438B kể cả vision). **Codex bỏ sót**; một đội khác đang dùng | Tiếng Việt tốt hơn có thể chịu lỗi ASR tốt hơn | −5 tới +5 | Phải tách phần text; 2 seed | Không có bằng chứng về gọi tool | Có, nếu dư GPU |
| 8 | **D6:** trung bình LoRA hai seed của phương án thắng | Giảm nhiễu giữa các lần train | 0 tới +2 | Chỉ tốn công chấm | Có thể không cộng được | Có |
| 9 | **G2:** gợi ý từ ngữ cho Whisper (tên app, tên trong history) | Lỗi ASR rơi vào tên riêng | −1 tới +2 | 0,5 ngày; 1 lượt chấm | Whisper có thể lặp lại chữ trong gợi ý | Có thể |
| — | Cắt vocab; cắt decoder PhoWhisper; speech-LLM (Voxtral, Gemma 4 E2B); prune model 7–8B; RL (GRPO) | Codex và Claude cùng đánh giá: không kịp, hoặc rủi ro luật | — | — | — | **Sau cuộc thi** |
| — | C2, C3, C5 (Qwen3.5 bản đầy đủ + ASR nhỏ hơn) | Chỉ dùng **nếu BTC không chấp nhận bản text-only** | | | | Dự phòng cho A1 |

**Thứ tự thực hiện:** hạng 1 làm ngay, không phụ thuộc gì. Hạng 2, 3 (và 5, 7 nếu dư GPU) chạy **song song trên GPU thuê**. Hạng 4 code song song, có mốc dừng. Hạng 6 là việc ASR của Leader trên máy 3050.

---

## 2. Claude kiểm chéo báo cáo Codex (08/11, qua HF API và transformers 5.21)

| Khẳng định | Kết quả kiểm |
|---|---|
| Qwen3.5-4B text-only 4.205.751.296 tham số, Apache-2.0, trước hạn | **Đúng.** Có hai bản: `principled-intelligence/Qwen3.5-4B-text-only` (11/03/2026, 2.202 lượt tải; **nên dùng bản này**, hoặc tự tách từ bản gốc) và `tuandunghcmut/...` (24/06/2026, 7 lượt tải) |
| Cách làm bản text-only | Nạp checkpoint gốc `Qwen/Qwen3.5-4B` (27/02/2026) bằng `Qwen3_5ForCausalLM` rồi lưu lại. **Đội tự làm được**, nên nguồn gốc là trọng số chính thức của Qwen |
| transformers đang pin có chạy được không | **Có:** transformers 5.21 dựng được `Qwen3_5ForCausalLM`, đếm đúng 4.205.751.296 |
| Kiến trúc | Lai: **24 lớp linear attention (Gated DeltaNet) + 8 lớp full attention**. Module: `in_proj_qkv`, `in_proj_z`, `in_proj_a`, `in_proj_b`, `out_proj` ở lớp linear; `q/k/v/o_proj` chỉ ở 8 lớp full. Danh sách LoRA hiện tại của `train.py` bỏ sót 3/4 số lớp attention |
| Embedding so với tính toán | Qwen3.5 text: embedding 635.699.200, **phần còn lại 3.570.052.096**. Qwen3-4B: embedding 388.956.160, phần còn lại **3.633.511.936** |
| Card của bản text-only | Chỉ kiểm với transformers ≥5.2; **vLLM chưa hỗ trợ**. Đội đang dùng backend HF nên không vướng |
| SEA-LION v4 4B | Codex ghi "không tìm thấy". **Có thật:** `aisingapore/Qwen-SEA-LION-v4-4B-VL`, 4.437.815.808, MIT, 21/11/2025, nền Qwen3-VL-4B-Instruct. Còn có `Gemma-SEA-LION-v4-4B-VL` (licence Gemma, phải hỏi BTC) |
| Hai đối thủ có README công khai | Một đội dùng **Qwen3.5-4B (bật thinking, prompt tiếng Anh, chèn ví dụ train tương tự vào prompt)** + faster-whisper. Một đội dùng **Gipformer fine-tune + Qwen SEA-LION v4 4B**. Không đội nào công bố điểm. Repo không có licence nên chỉ đọc ý tưởng, không chép code |

---

## 3. Đặc tính kênh âm thanh (150 wav train ngẫu nhiên; chỉ phổ và mức âm, không đọc nội dung)

| Đo | Trung vị (p10–p90) | Ý nghĩa |
|---|---|---|
| Tần số chứa 99% năng lượng giọng | **3,5 kHz** (1,5–4,6) | Giọng sạch ở 16 kHz thường còn năng lượng tới 7–8 kHz |
| Năng lượng trên 6 kHz | 0,002% | Gần như bằng không |
| Phổ trung bình (dB so với đỉnh) | 4 kHz −25 · 5 kHz −36 · **6 kHz −59** · 7 kHz −74 | **Tụt 24 dB giữa 5 kHz và 6 kHz**: dấu hiệu bộ lọc thông thấp hoặc codec khoảng 5,5 kHz. Khớp cảm giác "bịt micro, rè" |
| RMS | −25,7 dBFS (−28,2 tới −23,7) | Âm lượng đã được chuẩn hoá |
| Chênh mức giọng và nền | 39,7 dB (**p10: 17,2**) | Khoảng 10% file khá ồn |
| Clipping | 0 | |

**Hệ quả:**
- Fine-tune ASR trên audio train (đã làm) là khớp kênh nhất.
- Dữ liệu ASR thêm (TTS cho từ vựng app mới; Common Voice tiếng Việt CC0; FLEURS CC-BY) phải đi qua cùng xử lý: lọc thông thấp khoảng 5,5 kHz, chuẩn hoá RMS khoảng −26 dBFS, thêm nhiễu ở 15–40 dB.
- Private test gần như chắc đi qua cùng kênh. ASR nào chưa fine-tune trên kênh này sẽ thiệt; đó cũng là lý do Gipformer chưa fine-tune còn WER 16,9.

---

## 4. Lịch 09–13/11

| Ngày | Claude | Leader | Anh / laptop 4070 | GPU thuê |
|---|---|---|---|---|
| **09/11** | Code D5, test CPU. Thử 20 mẫu D2 trên Meta, rồi chạy cả 1.545 mẫu. Chuẩn bị gói chạy cho các nhánh A0–A3 (dùng lại `make_cloud_bundle.sh` / `cloud_arms.sh`). Bắt đầu D1 | **Gửi câu hỏi BTC.** Thuê GPU. Tạo file key Meta. **L9** | B28 (đăng nhập lại). Chạy public bằng C0 + D5 | Smoke test: nạp Qwen3.5 text-only, LoRA, sinh thử, đo tốc độ |
| **10/11** | Theo dõi các nhánh. D1: dữ liệu đạt kiểm hay bỏ (**mốc dừng**) | Nộp public C0 + D5 (so với 51,07). G3 trên máy 3050. L9 | — | A0 (1 seed C0, đối chứng máy), A1 ×2, A2 ×2; A3/A4 nếu dư |
| **11/11** | Đọc kết quả theo luật mục 5; chọn phương án thắng | L9 | — | Train bản nộp trên đủ dữ liệu, 2 seed (+D1 nếu đạt); làm file public |
| **12/11** | Thử trung bình LoRA (D6); so điểm | Nộp public phương án thắng và bản trung bình | — | — |
| **13/11** | Chốt; viết hướng dẫn thay vào image | Thay model vào image; kiểm image lại (như B28) | Kiểm image | — |
| 14–16/11 | Hỗ trợ L9 | **Hoàn thiện L9, nộp** | | |

---

## 5. Luật chọn (viết trước khi có kết quả)

- **D5:** giữ nếu public của C0 + D5 ≥ 51,07 − 0,3. D5 chỉ đổi lúc suy luận và greedy tất định, nên kết quả public không vướng nhiễu train.
- **Nhánh model:**
  - Mốc C0 trên dev_lao: chữ PhoWhisper-ft khoảng 41,1, chữ chuẩn khoảng 52,2 (trung bình 3 lượt đã có), cộng lượt A0 trên máy thuê để hiệu chỉnh độ lệch giữa các máy.
  - Một nhánh **thắng** khi **trung bình 2 seed** trên dev_lao, chữ PhoWhisper-ft, **≥ mốc + 3,0**, và chữ chuẩn không giảm quá 2,0.
  - Nhiều nhánh cùng thắng thì chọn nhánh cao nhất; hoà thì chọn nhánh ít đổi Docker hơn (A2 trước A1).
- **A1 chỉ được dùng cho bản nộp khi BTC trả lời là đếm theo trọng số thực sự nạp.** Chưa có trả lời trước 12/11 thì chuyển A1 sang dự phòng C5/C2, hoặc bỏ.
- **D1:** giữ nếu public của bản có D1 ≥ bản không D1 + 1,5, trên trung bình 2 seed.
- Không phương án nào thắng thì nộp **C0 + D5**.

---

## 6. Câu hỏi gửi BTC ngay (rút từ báo cáo Codex, mục 2)

1. Nếu dùng checkpoint text-only của Qwen3.5-4B (phát hành trước 26/10, hoặc đội tự tách từ bản gốc chính thức) và chỉ nạp phần language model, BTC đếm tham số theo **trọng số thực sự nạp lúc suy luận** (4,21B) hay theo **toàn bộ checkpoint gốc** (4,66B)?
2. LoRA chưa merge có cộng vào cả tổng hệ thống lẫn trần 5B của LLM không? Nếu đội merge trước khi nộp thì chỉ đếm trọng số đã merge, đúng không?
3. Máy chấm cuối cùng là A30 24 GB (theo thể lệ) hay RTX 5090 32 GB (theo Docker Guide)? Giới hạn 30 giây mỗi mẫu có giữ nguyên không?

---

## 7. Meta API

- **Tạo file key** (Leader tự gõ trong terminal; key không hiện lên màn hình, **không dán key vào chat**):

  ```bash
  read -rs -p "Meta API key: " K; echo; printf 'export META_API_KEY=%s\n' "$K" > ~/.zac_meta_env; chmod 600 ~/.zac_meta_env; unset K
  ```

- **Giá** (bảng giá đội ghi trong code; kiểm lại bằng 20 mẫu thử): `muse-spark-1.3` 1,25 USD / 1 triệu token vào, 4,25 USD / 1 triệu token ra (token suy luận tính như token ra). `muse-wonder-1.0` 4 / 20 USD.
- **Đợt 1 (ngày 09/11):**

  | Việc | Chi |
  |---|---:|
  | Thử 20 mẫu D2 | khoảng 0,2 USD |
  | D2 cho 1.545 mẫu train | khoảng 8–15 USD |
  | Đối tượng và state cho các app mới (chuẩn bị D1) | khoảng 5 USD |

  Trần đặt trong code: 90 USD tổng; mỗi đợt có trần riêng.
- **Gói tier tiêu chuẩn** (Meta không dùng nội dung để train), như đội đã dùng. Tuyệt đối không dùng tier "contributor"; code đã chặn sẵn.
