# Nhật ký dự án — ZAIC 2026 LifeMate

File này ghi lại toàn bộ trao đổi và quyết định của đội, để:

1. **Leader và các thành viên theo dõi tiến độ** qua lịch sử commit trên GitHub.
2. **Làm context khi mở đoạn chat mới với Claude.** Mở chat mới thì yêu cầu: *"Đọc `JOURNAL.md` trước rồi tiếp tục"*.

**Quy tắc cập nhật:** sau mỗi buổi trao đổi hoặc mỗi mốc quan trọng, thêm một mục mới vào [Nhật ký theo thời gian](#7-nhật-ký-theo-thời-gian), sửa phần [Trạng thái hiện tại](#0-trạng-thái-hiện-tại), rồi commit và push. Mục cũ không xoá; nếu sai thì ghi đính chính ở mục mới.

**Quy tắc git:** tài liệu (`JOURNAL.md`, `docs/`, `README.md`) được commit thẳng vào `main`. **Code mới phải đi qua Pull Request.**

**Tài liệu liên quan:**
- [`docs/PIPELINE.md`](docs/PIPELINE.md): moat, pipeline nền móng, tự đánh giá, đề án nâng cấp và 20 câu hỏi cho đội.
- [`HUMAN_TODO.md`](HUMAN_TODO.md): việc của người, kèm câu trả lời làm việc cho 20 câu hỏi.
- Ngày 29/10:
  - [`docs/TRAIN_REVIEW_2026-10-29.md`](docs/TRAIN_REVIEW_2026-10-29.md): audit lượt train đầu, Anh làm với Codex hỗ trợ.
  - [`docs/CLAUDE_HANDOFF_2026-10-29.md`](docs/CLAUDE_HANDOFF_2026-10-29.md): yêu cầu của Anh cho phiên 29/10.
  - [`docs/EVAL_2026-10-29.md`](docs/EVAL_2026-10-29.md): Claude đối chiếu audit, chấm các checkpoint và đề xuất thí nghiệm tiếp theo.

---

## 0. Trạng thái hiện tại

*Cập nhật: 2026-10-29, sau audit và đánh giá các checkpoint.*

- **Đã xong:**
  - Phân tích đề, chốt kiến trúc.
  - Viết bộ chấm điểm local, prompt, vòng lặp agent, sinh dữ liệu SFT, script train LoRA. Toàn bộ trong `lifemate/`, nằm ở **[PR #1](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/1) (`agent-pipeline` → `main`)**, chờ review.
  - Sửa đường đánh giá (dev loss trên toàn dev, file provenance, chặn ghi đè, chấm mọi checkpoint): **[PR #2](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/2) (`eval-protocol` → `agent-pipeline`)**, chờ review. Thư mục làm việc trên máy Anh đang ở nhánh `eval-protocol`.
  - Train Qwen3-1.7B (LoRA), 1 epoch. Trên đủ 233 mẫu dev_random, cùng protocol:
    - **step_100: 38,95**
    - **step_200: 52,47**
    - **final: 53,92**, chọn làm mốc. Final và step_200 không phân biệt được.
  - Chạy lại final cho kết quả giống hệt 233/233 mẫu.
  - Final đạt **80,2 trên 233 mẫu đã train**, cho thấy khoảng cách tổng quát hoá lớn. Chi tiết ở [`docs/EVAL_2026-10-29.md`](docs/EVAL_2026-10-29.md).
- **Đọc con số 53,9 cho đúng:**
  - Đây là điểm tham chiếu với chữ chuẩn `audio_text` (chưa qua ASR), chỉ gồm app đã có trong train.
  - Không phải cận trên của private. Private có ASR và app mới; chưa đo được ảnh hưởng.
- **Thí nghiệm B đã chạy** (train `fit_lao`, chấm `dev_lao`, chiều 29/10):
  - Final đạt **35,53** trên `dev_lao` (zero-shot 10,88). Không có tiến bộ rõ sau bước 100.
  - Trong cùng các mẫu, lời gọi thực hiện vào app mới không kém app đã thấy (54% so với 51%).
  - Điểm yếu tập trung ở **hỏi lại về tool mới**: 0 điểm trên 23 mẫu. Chi tiết ở `docs/EVAL_2026-10-29.md` mục 7.
- **Lỗi bộ chấm đã sửa** (30/10, PR #2): mẫu thiếu prediction giờ tính 0; điểm các lượt cũ không đổi.
- **Thí nghiệm D đã thiết kế** (30/10, [`docs/EXPERIMENT_D.md`](docs/EXPERIMENT_D.md), công cụ ở [PR #3](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/3)):
  - Model bỏ hỏi ở kiểu B (chọn mơ hồ ID) và C (thiếu slot); kiểu A (trùng tên) đã học được.
  - Luật tất định đã thử và loại khỏi hướng chính.
  - Bộ sinh cặp đủ/thiếu đã chạy thử: 23 mẫu qua mọi kiểm tra. **Chưa train.**
- **Review D và mốc đo** (30/10, [`docs/REVIEW_D_2026-10-30.md`](docs/REVIEW_D_2026-10-30.md), file số liệu [`docs/baselines/d_review_2026-10-30.json`](docs/baselines/d_review_2026-10-30.json)):
  - Model hỏi lại 1/16 trên câu thiếu thông tin.
  - Kiểm tra câu viết lại: bắt được 6/22 câu rò rỉ, sau khi sửa lên 15/22.
  - Nhãn chưa kiểm chứng được chính sách: chỉ 4 cặp đối chứng, khoảng 1/3 nhãn là ngoại suy.
  - Kế hoạch mới có đối chứng "nhân bản mẫu hỏi lại thật".
- **Chờ Anh:** đọc tay 23 mẫu D; duyệt giai đoạn 1 (sinh D v1 sạch); review PR #1 → #2 → #3.
- **Việc tiếp theo:** xem [mục 8](#8-việc-tiếp-theo).

---

## 1. Đề bài (tóm tắt)

### 1.1 Nhiệm vụ

Xây agent nhận **yêu cầu bằng giọng nói tiếng Việt** (có thể lẫn từ tiếng Anh, giọng Bắc/Trung/Nam) và **gọi tool** để thực hiện.

- **Đầu vào:**
  - `audio`: lượt nói cuối cần xử lý.
  - `context`: `current_time`, `timezone`, `location`, `user_profile` (tên, nhà, nơi làm, thành phố), `installed_apps` (app đã cài kèm danh sách tool).
  - `history`: các lượt trước. Lượt user chỉ có audio; lượt assistant có `text`, `tool_calls`, `tool_results`.
  - Môi trường giả lập `zaic_tools.ToolEnv` giữ dữ liệu app. Chỉ được đọc và ghi qua tool.
- **Đầu ra:** mỗi mẫu một dòng `{"id", "tool_calls": [{"name", "arguments"}...], "state_hash"}`, trong đó `state_hash = env.get_state_hash()`.
- **3 kiểu hành vi:**
  - Thực thi: gọi tool cho tới khi đạt trạng thái mong muốn.
  - Hỏi thiếu thông tin: `sys.ask_missing_info(tool_name, params)`, có thể sau vài call khác.
  - Ngoài phạm vi: `[]`.

### 1.2 Chấm điểm

```
gold rỗng           -> 1 nếu nộp rỗng, ngược lại 0
hash sai hoặc M = 0 -> 0
còn lại             -> F1 = 2PR/(P+R),  P = M/(M+U),  R = M/|G|
Final = 100/N * Σ Score_i
```

- **Một call khớp với call đáp án khi:**
  - Cùng tên tool.
  - Mọi tham số không phải fuzzy giống hệt.
  - Mọi tham số fuzzy (`x-match: fuzzy`) có token-F1 > 0.6, sau khi lowercase và chuẩn hoá Unicode NFC.
- Mỗi call chỉ khớp được tối đa một call; không xét thứ tự.
- `U` là số call thừa, **tính cả call bị từ chối vì sai schema**.
- `sys.ask_missing_info` được chấm như mọi tool khác.
- **Phân hạng khi bằng điểm:** chấm lại F1 bỏ qua hash; nếu vẫn bằng, đội có thời gian trung bình mỗi mẫu thấp hơn xếp trên.

### 1.3 Ràng buộc kỹ thuật

- **Kích thước model:** toàn hệ thống (ASR + LLM + mọi thành phần khác) **dưới 6B** tham số; LLM **dưới 5B** và context tối đa **16.384** token.
- **Thời gian và phần cứng chấm:** **30 giây mỗi mẫu**; 1 GPU A30 24GB, CPU Xeon Gold 6442Y 16 nhân, RAM 64GB. Chạy offline hoàn toàn, không gọi API ngoài.
- **Tái lập:** cố định mọi seed, giải mã greedy hoặc temperature 0. Nếu chạy lại ra kết quả khác, BTC chạy Docker 5 lần và lấy điểm trung bình.
- **Truy cập dữ liệu:**
  - **Không được đọc, copy hay parse file trong `<split>_environment/`** (kể cả `state.json`).
  - Mỗi mẫu đúng **một** `ToolEnv`, và mọi call đã gọi phải có trong bài nộp.
- **Dữ liệu và model được dùng:** dữ liệu công khai và model mã nguồn mở phát hành **trước 26/10/2026**, licence cho phép. Dùng LLM hoặc TTS ngoài để sinh dữ liệu tổng hợp lúc phát triển là được, lúc suy luận thì không. **Cấm gán nhãn public_test hoặc private_test** để train.
- **Phát tán dữ liệu:** README của gói dữ liệu cấm chia sẻ bộ dữ liệu, nên **không bao giờ commit `data/`**.

### 1.4 Lịch

| Mốc | Thời gian |
|---|---|
| Vòng public test | 26/10 – 16/11/2026, tối đa 5 lần nộp mỗi ngày |
| **Nộp Docker** (code train + suy luận + dữ liệu, link Google Drive + checksum, tối đa 2 lần, lấy lần cuối) | **16/11/2026 23:59 GMT+7** |
| Private test (BTC mount `/data`, chạy script suy luận, lấy `result/submission.jsonl`) | Phát đề 20/11 9:00 → nộp trước 23/11 23:59 |
| Công bố top 2 | 02/12/2026 |

### 1.5 Ý kiến của BTC (đội nhận được)

Điều gì thể lệ không cấm thì được làm. Vì vậy được dùng catalog và `zaic_tools` của public_test để sinh dữ liệu tổng hợp. Gán nhãn hoặc pseudo-label audio và yêu cầu của tập test vẫn bị cấm.

---

## 2. Dữ liệu — số liệu đã đo

**Gói dữ liệu:** `v3.2.0`, build 2026-10-24. Train có 1545 mẫu (có nhãn), public_test có 634 mẫu. Giải nén vào `data/train+public_test/`.

### 2.1 Cấu trúc

- `<split>.jsonl`: mỗi dòng một mẫu. Train có thêm `audio_text` (transcript của mọi lượt user) và `label` gồm `tool_calls`, `tool_results`, `final_state`.
- `<split>_tools_catalog.json`: schema version 2.7.0. Mỗi tool có `name`, `kind` (`read` / `write` / `meta`), `parameters` (JSON Schema mở rộng với `x-ref`, `x-match: fuzzy`, `x-one-of`), `returns`.
- `zaic_tools/`: **mỗi split một bản riêng**. Ví dụ `utils.py` khác nhau ở:
  - `LIVE_APPS`: train gồm exchange_rate, fuel_price, gold_price, lottery, weather; public chỉ gồm fuel_price, gold_price, weather.
  - `FREE_TEXT_KEYS`: public thêm `text`, bỏ `expression`.

  Luôn dùng đúng bản `zaic_tools` của split đang chạy.
- **`state_hash`:** sha256 của `canon(state)`. Hàm `canon` bỏ `_meta`, bỏ các app thông tin (live), bỏ các trường text tự do; lowercase chuỗi, gộp khoảng trắng, coi `700 cm` = `700cm`, sắp xếp danh sách giá trị đơn.
- **Call bị từ chối** (`ok: false`) chỉ khi sai schema. ID không tồn tại, không đủ tiền… thì vẫn trả `ok: true, done: false` và không đổi state.
- **`env.validate()` không bị ghi vào log**, nên kiểm schema trước khi gọi không tốn điểm.
- Gói không kèm bộ chấm F1; đội tự viết (xem mục 6).

### 2.2 App và tool

| | Số app | Số tool |
|---|---|---|
| Train | 46 | 147 |
| Public test | 36 | 122 |
| Chung cả hai (schema giống hệt) | 25 | 88 |
| **Chỉ có ở public** | **11** | **34** |
| Chỉ có ở train | 21 | — |

- **App chỉ có ở public:** ecommerce, event_tickets, grocery, habit_tracker, pantry, parking, public_transit, recipes, stocks, train_bus_tickets, translator.
- **Kết luận:** private test gần như chắc chắn cũng có app mới, nên model phải **đọc và hiểu schema**, không được học thuộc từng app.

### 2.3 Thống kê tập train

- **Loại mẫu:**

  | Loại | Số mẫu | Tỉ lệ |
  |---|---|---|
  | Thực thi | 1217 | 79% |
  | Gọi tool rồi mới hỏi thiếu thông tin | 157 | 10% |
  | Chỉ hỏi thiếu thông tin | 60 | 4% |
  | Ngoài phạm vi | 111 | 7% |

- **Số call mỗi mẫu:** 0 call: 111 · 1: 369 · 2: 428 · 3: 359 · 4: 161 · 5: 107 · 6: 10.
- **History:** 0–24 lượt, khoảng 1/3 số mẫu không có history.
- **App cài mỗi mẫu:** trung bình 9,2 app, khoảng 32,5 tool.
- **Tool hay gặp nhất:** `contacts.search` 234, `sys.ask_missing_info` 217, `smart_home.light_set` 126, `reminders.create` 115, `bill_payment.list_bills` 112.
- **Phát lại đáp án** bằng `zaic_tools` tái tạo đúng `final_state` ở **1545/1545** mẫu.
- **Audio:** WAV 16kHz mono, trung bình 5,1 giây, dài nhất 17,1 giây. Public có 1933 file wav, vì phải ASR cả các lượt user trong history.
- **Dữ liệu cho ASR từ train:** 5036 câu nói có transcript, tổng 6,83 giờ.
- **Múi giờ:** mọi mẫu đều là `Asia/Ho_Chi_Minh`. Thành phố: Hà Nội 791, TP.HCM 343, Đà Nẵng 242, Cần Thơ 92, Huế 77.

### 2.4 Độ dài prompt (tokenizer Qwen3, khoảng 2,9 ký tự mỗi token)

- Schema JSON thô của các tool đã cài: trung bình 12,8K ký tự, dài nhất 24,6K. Phải viết gọn lại.
- Sau khi viết gọn (system prompt khoảng 2,3K token):

  | Split | Trung bình | p95 | Dài nhất |
  |---|---|---|---|
  | Train (tính cả các bước gọi tool) | ~3,1K token | 4,6K | 6,1K |
  | Public (ước lượng) | ~2,7K token | — | 5,3K |

  Còn dư nhiều so với 16K.

---

## 3. Phát hiện quan trọng (ảnh hưởng trực tiếp tới điểm)

1. **State hash là cổng "được hoặc không":** một lệnh ghi sai là mẫu đó được 0 điểm. Trường text tự do (`content`, `title`, `note`, `address`, `pickup`…) **không tính vào hash**, chỉ cần token-F1 > 0.6.
2. **Call chỉ đọc vẫn tính vào F1**, nên phải bắt chước đúng quy ước của đáp án:
   - `smart_home.get_status`: gọi `{}` 93/107 lần.
   - `calendar.list_events`: gọi `{}` 87/105 lần.
   - `smart_home.light_set` có `get_status` đứng trước trong 113/126 mẫu.
   - Đọc thừa thì giảm precision, thiếu bước đọc thì giảm recall.
3. **`ask_missing_info` luôn là call cuối cùng:** 217/217 lần. Tham số hay hỏi nhất là `contact_id` (73), `amount` (21), `time` (10). Ví dụ: tìm ra 2 người tên "Minh" → `contacts.search` rồi `ask_missing_info(phone.call, [contact_id])`.
4. **Ngoài phạm vi không chỉ là thiếu app.**
   - Khoảng 40% là người dùng hủy hoặc phủ định ("à thôi khỏi", "đừng tắt đèn bếp").
   - Phần còn lại là chưa cài app, chỉ trò chuyện, hoặc thông tin đã có trong history.
   - **Không được thay bằng app gần giống:** "đặt taxi" khi chỉ có `bike_rental` → `[]`.
   - Câu "đặt sữa chua bên app đi chợ" ở train là `[]` vì chưa cài app, trong khi `grocery` là app thật ở public. Model phải quyết định dựa trên app đã cài, không dựa trên chủ đề câu nói.
5. **Có logic điều kiện:** "mưa thì hủy buổi tập" → tra thời tiết; nếu không mưa thì dừng, không hủy.
6. **Phải dùng lại thông tin trong history:** 294/1020 call có tham số ID lấy ID chỉ xuất hiện trong history. Vì vậy prompt phải giữ `tool_results` của history.
7. **27% mẫu có tham số ngày giờ**, ví dụ "thứ tư trừ 3 tiếng", "45 phút sau". Model nhỏ hay tính sai, nên đưa bảng ngày vào prompt.
8. **Lệnh ghi lặp lại có thể hợp lệ:** đổi điểm 2 lần để lấy 2 vé. Chỉ được bỏ trùng các call đọc.
9. **Lượt assistant trong history theo quy ước khác với đáp án được chấm:**
   - `get_status`: history dùng `{room}` 124/167 lần, đáp án dùng `{}`.
   - `list_events`: history có khoảng ngày 130/139 lần, đáp án dùng `{}`.
   - Khi hỏi lại, history chỉ nói thành câu thay vì gọi `ask_missing_info`; history chỉ có 22 lần `ask_missing_info`.

   **Không được dùng nguyên các lượt history làm đích huấn luyện.**
10. **Transcript và ngôn ngữ nói:**
    - Kiểu viết số trộn lẫn: "1 tiếng", "50 nghìn", số điện thoại đọc từng chữ số.
    - Người nói tự sửa giữa câu: "5 giờ nhé, à không, 5 rưỡi".
    - Phương ngữ: "mô, rứa, hông, coi, giùm".
    - Từ tiếng Anh xen vào: "book", "target", "deadline".
11. **Các tool search tự bỏ dấu khi so khớp** (Hương / Hường đều thành "huong"), nên ASR nghe sai dấu ở tên người ít gây hại.
12. **Tham số của lệnh ghi đến từ đâu** (2681 giá trị không fuzzy):

    | Nguồn | Tỉ lệ |
    |---|---|
    | Kết quả tool ngay trong lượt | 46% |
    | History | 15% |
    | Ngày giờ tự tính | 15% |
    | Số tự tính hoặc chuẩn hoá chữ thành số | 11% |
    | Enum hoặc boolean | 9% |
    | Chép nguyên văn lời nói | **gần 0%** |

    605/1545 mẫu (39%) có tham số của lệnh ghi phải tính từ lời nói. Kỹ năng cốt lõi là chọn đúng đối tượng và tính đúng, không phải chép lời.
13. **Query `contacts.search` là tên lưu trong danh bạ**, không phải lời người nói:
    - 166/204 trùng nguyên văn lời nói.
    - 31/204 chỉ khác chữ hoa ("bác Ba" → "Bác Ba").
    - 7/204 là tên đầy đủ ("cô Mai" → "Cô giáo Mai"). Đây là trần điểm không vượt được.
14. **Luật "đọc trước khi ghi":** cả 11/11 lần bật đèn mà không gọi `get_status` trước đều là do thông tin thiết bị đã có trong history.

---

## 4. Kiến trúc đã chốt

```
audio lượt cuối + audio các lượt user trong history (ASR theo batch)
  → ASR (~0,8B) → chuẩn hoá chữ thành số (ITN)
  → prompt: luật + profile + bảng ngày (−7…+14) + schema tool viết gọn + history (kèm tool_results)
  → vòng lặp agent Qwen3 (greedy): LLM sinh tool call → env.validate() → env.call() → kết quả trả lại LLM → …
  → dừng khi: LLM báo xong / vừa gọi ask_missing_info / đủ 8 bước / chạm mốc ~25 giây
```

- **Chọn kiến trúc nối tầng (ASR → LLM), không dùng audio-LLM end-to-end.** Các model audio-LLM dưới 5B nghe tiếng Việt còn yếu, khó debug, và không tận dụng được `audio_text` để train và đánh giá riêng từng phần.
- **LLM:** Qwen3-4B-Instruct-2507 (Apache-2.0, khoảng 4,0B tham số), chế độ không suy nghĩ. **Bắt buộc fine-tune (SFT)**, vì zero-shot không biết các quy ước của đáp án. Nên rà Hugging Face xem có model mới hơn phát hành trước 26/10/2026 không.
- **ASR:** ứng viên là Whisper-large-v3-turbo (0,8B, MIT) và PhoWhisper-medium/large (0,77B/1,55B, BSD). Đo bằng **độ chính xác của số, giờ, tên** chứ không chỉ WER. Lỗi ASR ở các lượt history ít nguy hiểm hơn ở lượt cuối.
- **Ngân sách tham số:**

  | Cấu hình | Thành phần | Tổng |
  |---|---|---|
  | A (đề xuất) | Qwen3-4B + Whisper-turbo hoặc PhoWhisper-medium | ~4,8B |
  | B | Qwen3-4B + PhoWhisper-large | ~5,6B (sát trần) |
  | C (dự phòng nếu chậm) | Qwen3-1.7B + PhoWhisper-large | ~3,3B |

- **Lớp code kiểm soát lỗi:**
  - `validate()` trước mỗi call; sai thì trả lỗi lại cho model, không gọi thật.
  - Chỉ bỏ trùng call đọc.
  - Dừng ngay sau `ask_missing_info`.
  - Bảng ngày trong prompt.
  - Giới hạn số bước và thời gian.
- **Đòn bẩy lớn nhất:** dữ liệu tổng hợp với **app mới** (LLM mạnh sinh app, schema, simulator theo khuôn `zaic_tools/apps/base.py`, kiểm chứng bằng cách chạy thật), kèm tăng cường bằng đổi tên schema và gỡ app.
- **Đánh giá 2 tầng:** dùng `audio_text` để đo trần điểm của agent; dùng ASR thật để đo điểm bị mất do nghe sai.

---

## 5. Đội và tài nguyên

| Người | Máy | Phụ trách |
|---|---|---|
| Anh (git `Anh-08`) | RTX 4070 Laptop 8GB VRAM (màn hình chiếm sẵn khoảng 1,7GB), RAM 14GB | Agent / LLM: bộ chấm, prompt, SFT, dữ liệu tổng hợp, train |
| Leader | RTX 3050 4GB | ASR, chuẩn hoá số, đóng Docker, đo thời gian trên GPU 24GB |

- **Ngân sách không giới hạn**, thuê GPU cloud tuỳ ý.
- **Repo:** https://github.com/Nguyen-Le-Tuan/ZAIC_2026. Bản clone local chính là thư mục `~/Zalo AI Challenge`. Nhánh làm việc của phần agent là `agent-pipeline`.
- **Quy tắc git:** tài liệu commit thẳng vào `main`; code mới mở PR vào `main`.

---

## 6. Code đã có (`lifemate/`)

### 6.1 Thành phần

| File | Việc |
|---|---|
| `lifemate/data.py` | Đọc split và catalog; nạp đúng `zaic_tools` của split. Code agent không đọc `*_environment/`. |
| `lifemate/scorer.py` | Bộ chấm local theo công thức của BTC. |
| `lifemate/prompt.py` | Prompt ChatML của Qwen3 với thẻ `<tool_call>`/`<tool_response>`, schema viết gọn một dòng mỗi tool, bảng ngày, profile, history. |
| `lifemate/agent.py` | Vòng lặp agent kèm lớp kiểm soát. Các backend: `openai` (vLLM server), `vllm` (trong tiến trình, cho Docker), `hf` (transformers + LoRA), `oracle` (phát lại đáp án), `PrefixBackend`. |
| `lifemate/infer.py` | Chạy cả split, ghi `submission.jsonl` và trace. `--text oracle` dùng `audio_text`; `--text asr` đọc file ASR. |
| `lifemate/sft.py` | Sinh dữ liệu SFT (xem 6.3). |
| `lifemate/train.py` | LoRA SFT bằng PyTorch thuần (xem 6.4). |
| `scripts/make_splits.py` | Chia tập dev. |
| `scripts/check_sft.py` | Kiểm prompt SFT khớp suy luận, ranh giới token. |
| `scripts/count_tokens.py` | Đo độ dài prompt. |
| `scripts/cloud_baseline.sh` | Baseline zero-shot bằng vLLM trên cloud. |
| `scripts/train_local.sh` | Chạy qua đêm: baseline zero-shot → train → đánh giá. |

- **Định dạng file ASR** (giao kèo giữa phần ASR và phần agent): `asr/<split>.jsonl`, mỗi dòng `{"audio": "audio/<id>/<file>.wav", "text": "..."}`, phủ **mọi** file wav (cả lượt cuối lẫn các lượt user trong history).
- **3 điểm đề không nói rõ**, bộ chấm local chọn cách khắt khe:
  - Tập tham số phải giống hệt nhau.
  - Chuỗi không fuzzy phải khớp chính xác.
  - Token tách theo khoảng trắng.

  Cần xác nhận bằng lần nộp public đầu tiên.

### 6.2 Kiểm chứng đã chạy

| Kiểm tra | Kết quả |
|---|---|
| Nộp đúng đáp án train | 100,0 |
| Nộp toàn rỗng | 7,18 (đúng bằng tỉ lệ mẫu ngoài phạm vi) |
| Bỏ một call đọc đầu tiên | 88,1 (hash vẫn đúng, F1 giảm) |
| Vòng lặp agent phát lại đáp án, toàn bộ train | 100,0 (lần đầu ra 99,87 do bỏ trùng cả lệnh ghi; đã sửa thành chỉ bỏ trùng call đọc) |
| Lớp kiểm soát trên public_test | Call sai schema và JSON hỏng bị chặn, 0 call lọt vào bài nộp, qua bộ kiểm tra chính thức `--validate` |
| Prompt SFT so với prompt suy luận | Khớp từng ký tự, 1545/1545 |
| Dữ liệu SFT đã gộp bước, phát lại | 100,0 |
| Ranh giới token khi tách đoạn | 300/300 giống hệt |

### 6.3 Tập dev và dữ liệu SFT

- **Tập dev:**
  - `splits/dev_random.txt`: 233 mẫu (hỏi thiếu 33 · thực thi 183 · ngoài phạm vi 17), chia ngẫu nhiên 15% theo loại.
  - `splits/dev_lao.txt`: 262 mẫu (41 · 214 · 7), là mọi mẫu dùng 6 app được giữ riêng: library, robot_vacuum, loyalty, medication, video_meeting, home_security.
  - Khi train cho bản leave-apps-out phải bỏ các app này khỏi `installed_apps`.
  - Từng có lỗi: lúc chia tập chưa tính `tool_name` của `ask_missing_info`, làm lộ tên app bị giữ riêng. Đã sửa, dev_lao tăng từ 256 lên 262 mẫu.
- **Định dạng SFT:** mỗi dòng là `{"id", "src", "aug", "segments": [[text, loss], ...]}`.
- **Gộp bước:** các call độc lập được gom vào cùng một bước. Sang bước mới khi call dùng giá trị vừa trả về trong bước hiện tại, hoặc khi lệnh ghi đứng sau lệnh đọc. Trung bình còn 1,74 bước so với 2,29 call.
- **Câu trả lời cuối** là một câu ngắn cố định: "Đã xong." khi đã gọi tool, "Không cần gọi tool." khi không gọi. Chuỗi dừng ngay sau `ask_missing_info`.
- **Tăng cường:**
  - Đổi tên app/tool nhất quán (2 biến thể mỗi mẫu).
  - Gỡ mọi app cùng nhóm với app yêu cầu cần → đích thành `[]` (xác suất 0,3).
  - Thêm 1–3 app gây nhiễu thuộc nhóm khác, lấy cả từ catalog public (xác suất 0,5).
  - Transcript kiểu ASR: viết thường, bỏ dấu câu (xác suất 0,3).
- **Nguồn lượt history** tắt mặc định (xem phát hiện 9). Có tuỳ chọn `--history tagged` để thử nghiệm.
- **Số liệu các file** (trong `lifemate/sft/`, không commit, chạy lại lệnh để sinh):

  | File | Ví dụ | Ghi chú |
  |---|---|---|
  | `fit_random.jsonl` | 4150 | ~3,3K token/ví dụ, ~76 token tính loss, ~13,3M token/epoch |
  | `fit_lao.jsonl` | 4051 | |
  | `all.jsonl` | 4874 | dùng train bản nộp |
  | `fit_random_hist.jsonl` | 6988 | thử nghiệm thêm lượt history |
  | `dev_random.jsonl` | 233 | không tăng cường, dùng đo dev loss |

### 6.4 Train

- **Cách tiết kiệm VRAM:** chỉ tính logits tại vị trí có loss (riêng chỗ này tiết kiệm 2–4GB); gradient checkpointing; batch 1 kèm tích luỹ gradient 16; trọng số bf16, tham số LoRA fp32; `--load-4bit` để chạy QLoRA.
- **Mặc định:** LoRA r=32, alpha=64, dropout 0,05, 7 module chiếu; lr 2e-4, cosine, warmup 3%; độ dài tối đa 8192.
- **Số đo trên RTX 4070 Laptop với Qwen3-1.7B:**
  - 34,9M tham số train được (1,99%).
  - Khoảng **1.385 token/giây**, nên 1 epoch `fit_random` (260 bước tối ưu) mất khoảng **2,7 giờ**.
  - Đỉnh **5,4GB** VRAM với mẫu dài nhất.
  - Chạy thử 3 bước: loss 1,77 → 1,08, dev loss 1,00.
- **Zero-shot Qwen3-1.7B** (với khối `<think>\n\n</think>\n\n` ép sẵn): **10/100 trên 10 mẫu**, khoảng 2,6 giây mỗi mẫu. Model bịa số điện thoại, hỏi lại thay vì tự tra lịch, trả lời bằng câu chữ thay vì gọi tool. Không ép khối `<think>` thì model "suy nghĩ" tới giới hạn 512 token và bị cắt.
- **Môi trường:** `lifemate/.venv` (Python 3.12, torch 2.15.0+cu132, transformers 5.21.0, peft 0.21.2). Transformers 5 dùng `dtype=` thay cho `torch_dtype=`.

#### Lệnh chạy train qua đêm

```bash
cd ~/"Zalo AI Challenge/lifemate" && mkdir -p runs && { nohup systemd-inhibit --what=sleep:idle:handle-lid-switch --why="LifeMate training" bash scripts/train_local.sh > runs/overnight.log 2>&1 & } && sleep 5 && tail -f runs/overnight.log
```

- Bấm Ctrl+C chỉ thoát khỏi phần xem log; train vẫn chạy.
- Dừng train: `pkill -f "train_local.sh|lifemate\.(train|infer)"`.
- Tổng khoảng 3 giờ 15 phút: baseline khoảng 10 phút → train khoảng 2 giờ 40 phút → đánh giá khoảng 15–20 phút.

#### Kết quả train qua đêm (2026-10-29)

- **Thiết lập:**
  - Model Qwen3-1.7B, LoRA, 1 epoch trên `sft/fit_random.jsonl` (4.150 ví dụ, 13,3M token, trong đó 0,32M token tính loss).
  - Chấm trên `dev_random` (233 mẫu); chữ đầu vào là `audio_text`, chưa qua ASR.
  - Log đầy đủ ở `lifemate/runs/overnight.log`, chỉ có trên máy Anh.
- **Thời gian:** chạy từ 23:52 đến 02:40, không lỗi. Riêng phần train mất 2 giờ 26 phút cho 260 bước, khoảng 1.540 token/giây, đỉnh 5,63GB VRAM.

| | Zero-shot | Sau SFT |
|---|---|---|
| **Điểm** | 9,9 | **53,9** |
| F1 của lời gọi (bỏ qua hash) | 13,7 | 67,2 |
| Hash trạng thái đúng | 25,3% | 63,1% |
| ask_missing (33 mẫu) | 2,0 | 49,4 |
| execute (183 mẫu) | 9,5 | 51,0 |
| out_of_scope (17 mẫu) | 29,4 | 94,1 |
| Thời gian mỗi mẫu, trung bình / tối đa | 2,9 s / 15,3 s | 2,5 s / 7,3 s |

- **Loss:**
  - Loss train giảm từ 1,62 xuống 0,03.
  - Dev loss qua các bước 50, 100, 150, 200, 250, 260: 0,060 → 0,041 → 0,028 → 0,0245 → 0,0233 → 0,0234. Đã chững lại ở cuối.
- **Phân bố điểm sau SFT:** 113 mẫu đúng hoàn toàn, 20 mẫu đúng một phần, 100 mẫu 0 điểm.
- **Điểm bị mất (107,4 trên 233 mẫu):** execute mất 89,7; ask_missing mất 16,7; out_of_scope mất 1,0.
- **Nhóm lỗi trong execute (183 mẫu):**

  | Nhóm | Số mẫu | Điểm |
  |---|---|---|
  | Có lời gọi khớp đáp án nhưng hash sai: trạng thái cuối khác đáp án (sai tham số ghi, thiếu hoặc thừa lệnh ghi) | **51** | 0 |
  | Hash sai và không lời gọi nào khớp | 22 | 0 |
  | Hash đúng nhưng không lời gọi nào khớp | 11 | 0 |
  | Hash đúng, F1 một phần: lời gọi thừa hoặc thiếu không làm đổi trạng thái (ví dụ lệnh đọc) | 17 | một phần |

- **Nhóm lỗi trong ask_missing (33 mẫu):** 12 mẫu hash sai, 3 mẫu hash đúng nhưng không lời gọi nào khớp, 3 mẫu đúng một phần.
- **Nhận xét:**
  - **Không chọn checkpoint theo loss.** Dev loss rất thấp (0,023) mà điểm chỉ 54, nghĩa là lỗi dồn vào vài token quyết định: ID, ngày giờ, số phải tính. Phải chấm bằng bộ chấm.
  - **Chưa đo được khả năng xử lý app mới.** Checkpoint này đã thấy mọi app của dev_random khi train. Muốn đo phải train lại trên `fit_lao` rồi chấm `dev_lao`. Hiện `scripts/train_local.sh` cố định dùng `fit_random`, nên cần sửa script.
  - **Tốc độ đã đủ.** Trên RTX 4070 laptop với backend HF (chưa dùng vLLM), mẫu chậm nhất mất 7,3 giây, dưới xa giới hạn 30 giây.
- Claude mới chỉ đếm nhóm lỗi, chưa đọc từng mẫu, để đội tự phân loại nguyên nhân trước ([`HUMAN_TODO.md`](HUMAN_TODO.md) mục 7).
- **Đính chính 29/10** (xem mục 7, entry 12):
  - Dev loss 0,023 ở trên chỉ đo **100 mẫu đầu** của file dev, vì `--eval-n 100` lấy đầu một file sắp theo id. Loss trên toàn 233 mẫu là **0,0685**: 100 mẫu đầu 0,0234, 133 mẫu sau 0,1153. Nhận xét "loss rất thấp mà điểm chỉ 54" vì vậy so hai tập mẫu khác nhau.
  - Kết luận vẫn giữ: chọn checkpoint chủ yếu bằng điểm rollout. Nhưng vẫn theo dõi loss toàn dev để chẩn đoán.
  - Tốc độ mới đo phần agent trên RTX 4070, chưa có ASR, chưa trên A30, chưa dùng vLLM.

---

## 7. Nhật ký theo thời gian

### 2026-10-28 — Phiên 1 (Anh + Claude)

1. **Phân tích đề.** Đọc README, mã `zaic_tools`, thống kê train và public. Phát hiện 11 app chỉ có ở public; history ở test chỉ có audio; tập trung vào state hash và quy ước của call đọc (mục 2–3).
2. **Bàn kiến trúc.** Chọn nối tầng ASR → Qwen3-4B SFT kèm lớp kiểm soát; lộ trình 19 ngày. Phát hiện máy local 8GB không đủ để SFT model 4B.
3. **Chốt tài nguyên.** Ngân sách không giới hạn, GPU cloud tuỳ ý, đội 2 người. BTC cho phép những gì không bị cấm. Dựng phần nền: bộ chấm, prompt, agent, infer, chia tập dev, script baseline cho cloud.
4. **Bộ sinh dữ liệu SFT.** Phát hiện lượt history theo quy ước khác đáp án nên tắt nguồn này mặc định. Thêm gộp bước, tăng cường, các kiểm chứng; sửa lỗi lộ app khi chia tập.
5. **Repo và script train.** Clone repo vào `~/Zalo AI Challenge`, nhánh `agent-pipeline`, commit `164b7a3`. Viết `train.py` tiết kiệm VRAM, backend HF, `train_local.sh`. Chạy thử train và zero-shot trên RTX 4070.
6. **Lệnh train qua đêm** cho Anh tự chạy.
7. **Tạo file nhật ký này.** Anh yêu cầu cập nhật liên tục và commit lên GitHub để leader theo dõi, đồng thời dùng làm context cho các đoạn chat sau.
8. **Câu hỏi về moat và tài liệu pipeline.**
   - **Anh hỏi:** nếu mọi đội đều có AI agent và tài nguyên như nhau thì khác biệt nằm ở đâu?
   - **Trả lời:** moat nằm ở việc hiểu chính sách sinh nhãn, có bộ dev mô phỏng private, phân vai giữa LLM và code tất định, dữ liệu tổng hợp đúng chính sách, ASR thiết kế theo slot, vòng lặp phân tích lỗi, và độ tin cậy của hệ thống.
   - **Nghiên cứu thêm:** đo nguồn gốc tham số của đáp án (phát hiện 12–14).
   - **Kết quả:** viết [`docs/PIPELINE.md`](docs/PIPELINE.md) gồm pipeline nền móng (sơ đồ, mã giả, đi qua mẫu `train_0001`, tính điểm từng kiểu lỗi), tự đánh giá, đề án nâng cấp 5 tầng và 20 câu hỏi.
   - **Quy tắc git mới:** tài liệu vào thẳng `main`, code qua PR. Đã mở [PR #1](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/1) `agent-pipeline` → `main` cho code.
9. **Câu hỏi về vai trò của con người** (ghi lại để các phiên sau hiểu tâm lý hiện tại của đội).
   - **Anh và leader băn khoăn:** khi đã có Claude Code với model tốt nhất, AI đọc nhiều paper và hiểu nhiều kỹ thuật cũng như giới hạn kỹ thuật, thì con người còn hơn AI ở đâu? Ngày xưa lợi thế nằm ở kỹ năng và kinh nghiệm fine-tune; giờ cuộc thi có thành "AI đấu AI" không? Bỏ qua thuyết trình, nộp bài, bỏ tiền, thì đóng góp riêng của người nằm ở đâu?
   - **Tâm lý hiện tại:** lo rằng lợi thế kỹ năng truyền thống đã bị san phẳng, và chưa rõ mình đóng góp gì ngoài việc chạy lệnh.
   - **Claude trả lời, tóm tắt:**
     - Không phải AI đấu AI. Khi mọi đội dùng cùng một model, năng lực thực thi bị san phẳng, nên khác biệt nằm ở **con người điều khiển AI**: hỏi gì, kiểm chứng gì, nhận ra điều gì, quyết định gì.
     - Lợi thế đã dịch chuyển: không còn ở chỗ biết nhiều kỹ thuật hơn, mà ở những việc AI không làm được hoặc làm kém.
     - Bằng chứng ngay trong phiên này:
       - Claude **không nghe được audio**. Dữ liệu gần 100% là giọng thật của 3 miền, và Claude chưa nghe file nào.
       - Claude **chỉ biết điều được đưa cho**: ý kiến của BTC, quy tắc repo, ngân sách đều do Anh mang tới.
       - Claude **sai một cách nghe rất hợp lý**: đã tự gây ra 4 lỗi trong phiên (bỏ trùng cả lệnh ghi, lộ app khi chia tập, app gây nhiễu không hiện schema, `dtype` của transformers 5), chỉ bắt được nhờ có kiểm chứng.
       - Kiến thức về model của Claude dừng ở giữa năm 2026.
       - Claude **không nhớ** qua các phiên; file này tồn tại vì lý do đó.
       - Claude **tối ưu đúng thứ được giao**: chính câu hỏi về moat của Anh đã đổi hướng công việc, từ "train thêm" sang "hiểu chính sách sinh nhãn".
   - **Phân vai đã thống nhất:**

     | Người (Anh, leader) | Claude |
     |---|---|
     | Đặt mục tiêu và ràng buộc; quyết định đặt cược khi thiếu dữ liệu; chịu trách nhiệm kết quả | Đề xuất phương án kèm bằng chứng và rủi ro |
     | Nghe audio, đánh giá lỗi ASR và phương ngữ theo cảm nhận của người bản ngữ | Viết công cụ để đo và gom lỗi |
     | Làm việc với BTC, theo dõi forum và các đội khác; xác nhận các chỗ luật chưa rõ | Liệt kê các chỗ chưa rõ cần hỏi |
     | Trả lời 20 câu hỏi trong `docs/PIPELINE.md` bằng phán đoán và thí nghiệm | Chạy thí nghiệm, phân tích dữ liệu |
     | Giữ chuẩn kiểm chứng ("số này đo ở đâu? sai thì thấy dấu hiệu gì?"); review PR | Viết test và kiểm chứng, báo cáo trung thực cả khi thất bại |
     | Giữ mạch ý đồ suốt 19 ngày; hiểu pipeline đủ sâu để bắt lỗi của Claude | Ghi nhật ký này sau mỗi phiên |
10. **Tạo [`HUMAN_TODO.md`](HUMAN_TODO.md).** Anh yêu cầu gom việc của người trong lúc chờ train thành danh sách checkbox, kèm 20 câu hỏi.
    - Việc được chia theo người phụ trách và theo giai đoạn: ngay bây giờ → hiểu bài và code → nghe audio → làm việc với BTC → chuẩn bị tài nguyên → tổ chức đội → sáng mai khi train xong.
    - Mọi lệnh trong file đã được chạy thử.
    - Đã chuẩn bị sẵn bài nộp rỗng cho public (`lifemate/runs/public_empty.jsonl`, qua bộ kiểm tra chính thức) để leader quyết định có dùng 1 lượt nộp đo tỉ lệ mẫu ngoài phạm vi hay không.
    - 20 câu hỏi được chép tự động từ `docs/PIPELINE.md`. Từ nay **câu trả lời ghi ở `HUMAN_TODO.md`**; `PIPELINE.md` chỉ để đọc.

### 2026-10-29 — Kết quả train qua đêm

11. **Train qua đêm chạy xong, không lỗi** (23:52 → 02:40). Anh dán log vào chat và hỏi đã xong chưa.
    - Đã xong: log có dòng cuối `done:`, process đã thoát, GPU đã trống. Lệnh `tail -f` vẫn giữ terminal; bấm Ctrl+C để thoát.
    - **Điểm dev_random: 9,9 (zero-shot) → 53,9 (sau SFT).** out_of_scope lên 94, ask_missing lên 49, execute lên 51. Bảng chi tiết ở [mục 6.4](#kết-quả-train-qua-đêm-2026-10-29).
    - Chỗ yếu nhất là execute: 51 mẫu có lời gọi đúng nhưng trạng thái cuối sai, nên bị 0 điểm.
    - Con số này chưa tính lỗi ASR và app mới, nên là mức trần lạc quan so với private test.

### 2026-10-29 — Audit, sửa đường đánh giá, chấm các checkpoint

12. **Anh gửi audit lượt train đầu, làm với Codex hỗ trợ** ([`docs/TRAIN_REVIEW_2026-10-29.md`](docs/TRAIN_REVIEW_2026-10-29.md)), kèm yêu cầu cho phiên này ([`docs/CLAUDE_HANDOFF_2026-10-29.md`](docs/CLAUDE_HANDOFF_2026-10-29.md)): đối chiếu, sửa đường đánh giá, chấm các checkpoint có sẵn và chốt thí nghiệm kế tiếp. Chưa thuê cloud, chưa nộp public, chưa train dài. Kết quả ở [`docs/EVAL_2026-10-29.md`](docs/EVAL_2026-10-29.md).
    - **Đối chiếu 21 nhận định của Codex:** 13 đồng ý, 6 đồng ý kèm bổ sung hoặc sửa, 2 chưa đủ bằng chứng. Phát hiện lớn nhất của Codex được xác nhận: dev loss trong log chỉ đo 100 mẫu đầu.
    - **Claude đo thêm:**
      - id train đi theo lô có đặc điểm khác nhau. Lô 1501+ có trung bình 7 lượt user trong history; lô 1–300 có 12 app cài và 3 call đáp án mỗi mẫu. Điểm dev giảm theo lô id và theo độ dài history.
      - Ranh giới hỏi lại (30 mẫu, 12,7 điểm) là nhóm hành vi mất điểm lớn nhất; ưu tiên "51 mẫu" hôm qua đã đánh giá thấp nhóm này.
      - `done=false` chỉ xuất hiện ở 7/233 rollout.
      - Ở `train_0098`, model đã thấy `done=false` rồi vẫn gửi SMS.
    - **Sửa đường đánh giá ([PR #2](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/2)):**
      - Dev loss tính trên toàn dev.
      - Mỗi file SFT có manifest; mỗi lượt chạy có meta (commit, sha256 của adapter, id, latency).
      - Không ghi đè kết quả cũ; trace lưu kết quả tool.
      - Thêm `eval_loss`, `compare` (so theo cặp kèm bootstrap và lát cắt), `eval_ckpt.sh`; `train_local.sh` chọn được `FIT`/`DEV` và chấm mọi checkpoint.
      - Ba file SFT cũ dựng lại giống từng byte.
    - **Kết quả trên đủ 233 mẫu:**
      - step_100: 38,95.
      - step_200: 52,47.
      - final: 53,92. Final hơn step_200 +1,45, khoảng tin cậy [−1,85; +4,78].
      - Chạy lại final cho kết quả giống hệt 233/233 mẫu.
      - Tập dò 233 mẫu lấy từ fit: 80,2.
    - **Quyết định đề xuất:**
      - Giữ final làm mốc.
      - Thí nghiệm B (fit_lao → dev_lao) tối nay, A (2 epoch) sau đó, thiết kế D (dữ liệu phản thực tế) song song.
      - Cân nhắc tách lockbox vì dev_random đã bị đọc kỹ từng mẫu.
    - `HUMAN_TODO.md`: điền câu trả lời làm việc cho 20 câu, mỗi câu có trạng thái (đã xác minh / giả thuyết / chưa đo / chờ BTC). Chỉ đánh dấu xong 3 việc có bằng chứng: lệnh train, xem file điểm, mở chat.
13. **Sự cố bộ nhớ lúc 08:26.** Anh báo máy hết bộ nhớ và tự tắt.
    - Kiểm tra cho thấy máy không khởi động lại. `systemd-oomd` kill cả nhóm tiến trình của app Claude, khi đó dùng 6,6GB, vì áp lực bộ nhớ toàn máy. Các lượt đánh giá đang chạy trong nhóm đó nên chết theo.
    - Không mất file nào: step_100 đã xong; các bước sau chưa kịp ghi file.
    - Đã chạy lại trong unit systemd riêng, giới hạn 5–6,5GB. Mỗi lượt đánh giá chỉ đạt đỉnh khoảng 1,25GB, train thử 1 bước đạt 2,9GB. Áp lực bộ nhớ đến từ tổng các ứng dụng đang mở (app Claude, ChatGPT, trình duyệt…), không chỉ từ đánh giá.
    - **Quy tắc mới:** việc dài (train, đánh giá) chạy bằng `systemd-run --user` có `MemoryHigh`/`MemoryMax`, để app và phiên làm việc không bị kill theo. Lệnh mẫu ở `docs/EVAL_2026-10-29.md` mục 5.3.
14. **Review của Codex và thí nghiệm B** (chiều 29/10).
    - **Review** ([`docs/REVIEW_CLAUDE_EVAL_2026-10-29.md`](docs/REVIEW_CLAUDE_EVAL_2026-10-29.md)):
      - Xác nhận lại mọi điểm checkpoint.
      - Chỉ ra lỗi bộ chấm: mẫu thiếu prediction mà gold rỗng vẫn được 1 điểm. Claude đã tái hiện; lỗi không làm sai số nào đã báo.
      - Bổ sung điều kiện cho lockbox; nhắc 225/262 mẫu `dev_lao` nằm trong `fit_random`; yêu cầu hạ mức khẳng định ở vài chỗ.
      - Claude đồng ý cả bốn ý (EVAL mục 7.1).
    - **Thí nghiệm B:** review khuyên chưa chạy vì Anh cần tắt máy, nhưng Anh chọn "Chạy B ngay" trong chat.
      - Claude chạy trong unit systemd riêng, **không** chặn chế độ ngủ khi gập máy, để laptop không nóng trong balo. Chạy 09:20 → 12:45, không lỗi.
      - Kết quả trên `dev_lao`: zero-shot 10,88 → step_100 33,02 → step_200 35,48 → final 35,53. Dev loss phẳng từ bước 100.
      - Trong cùng các mẫu, tỉ lệ tìm lại lời gọi đáp án: app giữ riêng 54,4%, app đã thấy 51,2%.
      - Hỏi lại về tool của app giữ riêng: 0 điểm trên 23 mẫu.
      - Thành phần mẫu (lô id, history) giải thích khoảng 2–11 trong 18,4 điểm chênh với `dev_random`. Đây là ước lượng thô, không phải nhân quả.
    - **Suy luận:** đòn bẩy rõ nhất cho app mới là chính sách hỏi lại với schema chưa thấy. Thí nghiệm A có giá trị thấp hơn dự kiến với protocol này.

### 2026-10-30 — Sửa lỗi bộ chấm

15. **Sửa lỗi bộ chấm khi thiếu prediction** (Anh chọn "Sửa ngay"; commit `d6208a1` trong [PR #2](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/2)).
    - Trước: `evaluate()` coi mẫu thiếu prediction như đã nộp danh sách call rỗng, nên mẫu ngoài phạm vi bị thiếu vẫn được 1 điểm.
    - Nay:
      - Mẫu thiếu prediction tính 0 và được đánh dấu `missing`.
      - Id trùng thì báo lỗi.
      - Id ngoài split, cả trong prediction lẫn trong `--ids`, thì báo lỗi để mẫu số không âm thầm thay đổi.
      - Kết quả có thêm số mẫu `missing` và `extra`.
    - **Kiểm chứng:**
      - 11 test đạt (7 test logic, 4 test qua dòng lệnh trên dữ liệu train thật).
      - Chấm lại 10 lượt chạy đã lưu ra đúng điểm cũ, cả tổng lẫn từng dòng theo mẫu.
      - Phát lại đáp án vẫn được 100; `check_sft.py` đạt.
    - **Ghi chú:** `gh pr edit` lỗi do API Projects classic của GitHub đã bị gỡ; mô tả PR cập nhật bằng `gh api -X PATCH repos/.../pulls/<n> -F body=@file`.
16. **Thiết kế thí nghiệm D** (Anh chọn "Thiết kế D"; sau đó quyết: Claude viết lại câu ngay trong phiên, làm luôn bộ sinh dữ liệu, chưa train). Chi tiết ở [`docs/EXPERIMENT_D.md`](docs/EXPERIMENT_D.md); code ở [PR #3](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/3).
    - **Chính sách hỏi lại trên fit_random:**
      - 184 lần hỏi lại, mỗi lần đúng 1 tham số, luôn là call cuối.
      - 73 lần đã thực hiện ý khác trước.
      - Kiểu A/B/C = 57/55/72.
    - **Model hiện tại:**
      - Kiểu A làm tốt (dev_random 8/8 có hỏi).
      - Bỏ hỏi B 7/11 và C 9/14 trên dev_random; B 17/21 và C 16/19 trên dev_lao.
      - Với C, model bịa giá trị cho đúng slot lẽ ra phải hỏi (21/25 lần).
    - **Luật tất định:**
      - "ID lấy từ lần tra ≥ 2 mục trùng tên thì hỏi lại": 0 lần báo nhầm trên fit.
      - Nhưng phát lại trên rollout chỉ kích hoạt 0–1 mẫu (+0 đến +0,25 điểm), nên loại khỏi hướng chính.
      - Kiểm tra nguồn gốc giá trị slot thường không làm tất định được.
    - **Bộ sinh dữ liệu** (`lifemate/counterfactual.py`):
      - Ba loại cặp: C, B-vague, B-specific.
      - Nhãn phát lại qua ToolEnv; câu phải qua 7 kiểm tra; loại nguồn từ dev.
      - `sft.py --extra-samples` nối mẫu D vào SFT. Không truyền thì bốn file SFT cũ dựng lại giống từng byte.
      - 12 test mới đạt.
    - **Chạy thử trên fit_lao:**
      - 49 task → Claude viết lại 27, bỏ qua 22 có lý do (6 giá trị phải tính, 5 lấy từ history…) → **23 mẫu qua mọi kiểm tra**.
      - 4 mẫu có nguồn trong dev_random bị loại, gồm `train_1409`; bước chọn nguồn nay loại sớm.
    - **Ước lượng bộ đầy đủ:** khoảng 230 mẫu, tương đương khoảng 700 dòng SFT.
    - **Đề xuất train:** 2 lượt giữ nguyên số bước (D-lao, D-random), tiêu chí ở EXPERIMENT_D mục 8. Chờ Anh duyệt.
    - **VieNeu** (TTS tiếng Việt Anh gợi ý): ghi cho leader ở Q18; ngoài phạm vi D vì D chỉ là văn bản. Cần kiểm licence và khả năng chạy offline.
17. **Review thí nghiệm D và đặt mốc đo** (Anh yêu cầu đánh giá lại, định lượng nhược điểm, được chạy thử tuỳ ý, rồi lập kế hoạch; bản này là mốc so sánh). Xem [`docs/REVIEW_D_2026-10-30.md`](docs/REVIEW_D_2026-10-30.md).
    - **Đo trên GPU, 23 cặp thử, cả hai checkpoint** (trong unit `systemd-run`; tiến trình dùng khoảng 1,2GB RAM, phần còn lại là page cache):
      - Câu thiếu thông tin: model hỏi lại 1/16 lần, 15 lần tự làm.
      - Mẫu hỏi lại kiểu B đã có trong train: model hỏi 0–1/7.
      - Cặp đúng cả hai vế: 1/23 và 0/23.
    - **Nhược điểm đã định lượng:**
      - Chỉ có 4 cặp tự nhiên để đối chiếu nhãn (3 cặp khớp).
      - 34–36% nhãn là ngoại suy.
      - Chuỗi lệnh đọc khớp nhãn thật 70–78%.
      - Kiểm tra câu bắt được 6/22 câu rò rỉ.
      - Người viết phải bỏ 45% task.
      - 3 tool đứng đầu chiếm 56–66% nguồn; B-specific chỉ có 5–8 nguồn.
      - 15/21 lần bỏ hỏi với app giữ riêng không được phủ.
      - Chưa có đối chứng cho D.
    - **Đã sửa** (PR #3, commit `8799da5`):
      - `vinum.py` nhận ra số và giờ viết bằng chữ, viết tắt: bắt rò rỉ lên 15/22, vẫn 0/27 loại nhầm.
      - Bộ lọc nguồn: bắt trước 17/22 task người viết bỏ, loại nhầm 3/27, đo trên chính lần thử.
      - Giới hạn số mẫu mỗi tool: tỉ trọng 3 tool đứng đầu còn khoảng 30%.
      - Cờ tiền lệ; tách D-train / D-eval.
      - `contrast_eval.py`, `d_quality.py`.
      - 16 test bộ sinh dữ liệu đạt.
    - **Kế hoạch:**
      - Giai đoạn 1: D v1 sạch (đọc theo nghĩa, người đọc tay, tách D-eval).
      - Giai đoạn 2: ba lượt B0 / B-up (đối chứng) / B-D với số bước giữ nguyên; giữ D chỉ khi thắng cả B0 lẫn B-up.
      - Giai đoạn 3: mở rộng.
      - Giai đoạn 4: đưa vào công thức train cuối.
    - **Đính chính:** trong chat, số cặp tự nhiên là 4 cặp, 3 cặp khớp (không phải 5 và 4).

---

## 8. Việc tiếp theo

- [ ] Anh và leader làm theo [`HUMAN_TODO.md`](HUMAN_TODO.md), trả lời 20 câu hỏi ngay trong file đó, rồi thảo luận với Claude để chốt kế hoạch nâng cấp.
- [ ] Review và merge PR `agent-pipeline` → `main`.
- [x] Đọc kết quả train qua đêm: dev_random 9,9 → 53,9 (2026-10-29).
- [x] Phân tích lỗi của checkpoint `q17b_fit_random`: Anh audit với Codex hỗ trợ, Claude đối chiếu (29/10, [`docs/EVAL_2026-10-29.md`](docs/EVAL_2026-10-29.md)). Việc hai người tự phân loại bằng mắt vẫn mở trong `HUMAN_TODO.md`.
- [x] Sửa `scripts/train_local.sh` để chọn được tập train và tập dev: [PR #2](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/2), chờ review.
- [x] Chấm step_100, step_200 và final trên đủ 233 mẫu; chọn final làm mốc (29/10).
- [ ] Review và merge PR #2 (người review quyết).
- [x] **Thí nghiệm B:** train `fit_lao` → chấm `dev_lao`. Final đạt 35,53; hỏi lại về tool mới được 0 điểm (29/10, EVAL mục 7).
- [x] Sửa lỗi bộ chấm khi thiếu prediction, kèm 11 test (30/10, PR #2, commit `d6208a1`).
- [x] Thiết kế D: thống kê chính sách hỏi lại, thử luật tất định, viết bộ sinh dữ liệu, chạy thử 23 mẫu (30/10, PR #3, `docs/EXPERIMENT_D.md`).
- [ ] Anh đọc tay 23 mẫu D (`lifemate/gen/review_fit_lao.md`).
- [ ] Nếu duyệt: sinh đủ khoảng 230 mẫu D, chạy D-lao và D-random với số bước giữ nguyên (EXPERIMENT_D mục 8).
- [ ] Thiết kế D, ưu tiên hỏi lại với schema chưa thấy: dữ liệu đủ/thiếu slot trên schema đổi tên hoặc tổng hợp; thử kiểm tra tất định xem tham số bắt buộc có nguồn trong lời nói, history hoặc kết quả tool không, đo trên fit trước.
- [ ] **Thí nghiệm A:** 2 epoch trên fit_random, để tách "thiếu ngân sách train" với "thiếu dữ liệu đa dạng".
- [ ] **Thí nghiệm C:** trong agent, giữ nguyên call JSON hỏng và nhắc khi gặp `done=false`; PR riêng, 12 phút đánh giá.
- [ ] **Thí nghiệm D:** thiết kế dữ liệu phản thực tế từ fit cho điều kiện và ranh giới hỏi lại; mọi nhãn phải qua kiểm tra thực thi.
- [ ] Quyết có tách lockbox khoảng 200 mẫu từ fit hay không.
- [ ] Nộp public lần đầu để kiểm chứng 3 giả định của bộ chấm (mục 6.1).
- [ ] Cloud:
  - Baseline zero-shot Qwen3-4B-Instruct-2507 (`scripts/cloud_baseline.sh`).
  - SFT 4B trên `all.jsonl`.
  - Thử nghiệm so sánh `--history tagged` và `--rename 0/2/4`.
- [ ] Phần ASR (leader):
  - Benchmark Whisper-turbo và PhoWhisper trên audio train: WER và độ đúng của số, giờ, tên.
  - Viết bộ chuẩn hoá chữ thành số (ITN).
  - Xuất `asr/<split>.jsonl` theo giao kèo; làm transcript k-fold cho SFT (`--asr-file`).
- [ ] Dữ liệu app tổng hợp: LLM mạnh sinh app, schema, simulator, câu yêu cầu và đáp án; chạy thật qua executor để kiểm chứng.
- [ ] Docker offline: dùng backend vLLM, đo thời gian trên GPU 24GB, chạy 5 lần kiểm tra tính tái lập.

### Lộ trình tới hạn Docker 16/11

| Ngày | Việc |
|---|---|
| 1–3 | Bộ chấm, prompt, baseline, benchmark ASR *(đã xong phần agent)* |
| 4–9 | SFT v1, chốt và fine-tune ASR, nộp public lần đầu |
| 8–13 | Dữ liệu app tổng hợp, SFT v2, phân tích lỗi |
| 14–17 | Docker offline, đo thời gian, kiểm tra tái lập |
| 18–19 | Dự phòng |

### Câu hỏi mở

- Server chấm có so khớp chính xác tham số không fuzzy và tách token theo khoảng trắng như bộ chấm local giả định không?
- Licence của các model ASR tiếng Việt: một số dùng CC-BY-NC, có được dùng không?
- Có model LLM hoặc ASR nào tốt hơn phát hành trước 26/10/2026 không?
