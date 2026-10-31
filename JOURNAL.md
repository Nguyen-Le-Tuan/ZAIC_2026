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

*Cập nhật: 2026-10-31 05:00. Giai đoạn 2 của D và baseline đầu-cuối đã xong (entry 30–31); kế hoạch ngày 31/10 ở `docs/PLAN_2026-10-31.md`. Bản trước xem lịch sử git.*

- **Baseline phần agent: đã xong và tái lập được.** Model đọc chữ chuẩn `audio_text`, chưa qua ASR.

  | Mốc | Train → chấm | Điểm |
  |---|---|---|
  | Zero-shot Qwen3-1.7B | – → dev_random / dev_lao | 9,90 / 10,88 |
  | **SFT Qwen3-1.7B LoRA, 1 epoch (mốc chính)** | fit_random → dev_random (233 mẫu) | **53,92** (chạy lại giống hệt 233/233 mẫu) |
  | **B0** (đo trên app chưa thấy) | fit_lao → dev_lao (262 mẫu) | **35,53**: hỏi lại 7,48; execute 39,73; ngoài phạm vi 71,43 |

  - Chi tiết: [`docs/EVAL_2026-10-29.md`](docs/EVAL_2026-10-29.md).
  - Code ở [PR #1](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/1) → [#2](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/2) → [#3](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/3), chưa merge.
- **Baseline đầu-cuối theo đề (audio → ASR → agent): đã có** (31/10, entry 31, [`docs/E2E_BASELINE_2026-10-31.md`](docs/E2E_BASELINE_2026-10-31.md)).

  | Agent đọc | dev_random | dev_lao |
  |---|---:|---:|
  | Chữ chuẩn `audio_text` | 53,92 | 35,53 |
  | **Whisper-turbo (chưa fine-tune; được chọn)** | **31,69** | **17,14** |
  | PhoWhisper-large (chưa fine-tune) | 27,90 | 15,58 |

  - **Lỗi ASR là chỗ mất điểm lớn nhất hiện nay** (khoảng 20 điểm). ASR sai 26–31% số từ; người nói hiếm khi đọc lệch kịch bản.
  - **File nộp public đã kiểm:** `lifemate/runs/e2e_public_turbo.jsonl` (634 dòng). **Chưa nộp**; Anh tự nộp.
  - Thời gian trên laptop: trung bình 2,9 giây mỗi mẫu, chậm nhất 9,7 giây. Chưa có Docker offline, chưa đo trên A30.
  - Code: [PR #4](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/4), chưa merge.
- **Kế hoạch hôm nay (31/10):** [`docs/PLAN_2026-10-31.md`](docs/PLAN_2026-10-31.md). Ưu tiên: fine-tune ASR (leader), train agent trên chữ ASR và 4B (Anh chạy cloud), Docker (leader).
- **Điểm yếu lớn nhất đã đo:** hỏi lại, nhất là với app chưa thấy (0/23 mẫu ở dev_lao), và thiếu lệnh ghi do làm thiếu vế (entry 28).
  - **Thí nghiệm D bị loại** (entry 30, [`docs/D_PHASE2_2026-10-31.md`](docs/D_PHASE2_2026-10-31.md)): thua lượt đối chứng B-up, chỉ nhân bản mẫu hỏi lại thật. B-up: hỏi lại 7,5 → 30,0, tổng 35,53 → 36,94 (chưa chắc).
  - Bước tiếp: thử công thức B-up trên fit_random (lượt cloud, chờ Anh bật).
- **Đang chạy:** không có job train. Đêm 31/10 đã chạy ASR trên toàn bộ wav train (`lifemate/asr/train_all_*.jsonl`) để làm dữ liệu cho lượt cloud train agent trên chữ ASR.
- **Chờ Anh:**
  - Cùng leader làm mục 0 của [`HUMAN_TODO.md`](HUMAN_TODO.md) (0.1–0.8), trên máy leader.
  - Review PR #1 → #2 → #3 → #4 → #5 → #6.
  - Thuê cloud và chạy gói train theo [`docs/CLOUD_TRAIN_2026-10-31.md`](docs/CLOUD_TRAIN_2026-10-31.md).
  - Đọc tay `lifemate/gen/review_v1_30.md` và `review_1b.md`.
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
18. **Giai đoạn 1 của D: D v1** (Anh duyệt "Duyệt giai đoạn 1"; chưa train). Chi tiết ở [`docs/D_PHASE1_2026-10-30.md`](docs/D_PHASE1_2026-10-30.md); số liệu ở [`docs/baselines/d_phase1_2026-10-30.json`](docs/baselines/d_phase1_2026-10-30.json).
    - **Thêm lượt đọc theo nghĩa (R7):** người đọc chỉ thấy câu mới và danh sách mục (PR #3, commit `701dcb4`; 17/17 test đạt).
    - **Pipeline:**
      - 130 task (giới hạn 8 mẫu mỗi tool; loại nguồn từ dev và 49 nguồn của đợt thử).
      - Claude viết lại 83, bỏ qua 47 có lý do.
      - 0 lỗi kiểm tra chữ; **6 câu bị lượt đọc theo nghĩa loại** (có 1 câu đổi nhầm đối tượng).
      - **77 mẫu giữ lại**, phát lại qua ToolEnv đều thành công.
      - D-train 53 / D-eval 24 (tách theo mẫu gốc, không trùng dev hay mẫu thử).
    - **Chất lượng nguồn:**
      - 3 tool đứng đầu chiếm 27% (mốc 56–66%).
      - 29 tool đích.
      - 68% nhãn có tiền lệ.
    - **Đo trên GPU, D-eval-24:**
      - Cả hai checkpoint hỏi lại **0/24** câu thiếu thông tin; làm đúng 15–17/24 câu gốc; 0/24 cặp đúng cả hai vế.
      - Cộng mốc đợt thử: 1/40.
    - **Cổng:** chống rò rỉ đạt; tỉ lệ bỏ qua ≤ 15% **không đạt** (36%); người đọc tay đang chờ.
    - **Giới hạn mới:** với luật chặt, nguồn từ fit chỉ đủ khoảng 140–150 mẫu D. D-train 53 mẫu (khoảng 4% số dòng) có thể quá ít để giai đoạn 2 thấy được hiệu ứng.
    - **Đề xuất:**
      - Giai đoạn 1b: bộ lọc v2 cho khoảng 30/47 lý do bỏ qua tự động hoá được; nâng giới hạn lên 16 mẫu mỗi tool; D-train khoảng 80–90 mẫu.
      - Giai đoạn 2 thêm nhánh liều lượng: B-up, B-D1, B-D3.
19. **Giai đoạn 1b của D: bộ lọc nguồn v2, D-train 77 mẫu** (Anh chọn "Làm giai đoạn 1b"; chưa train). Chi tiết ở [`docs/D_PHASE1B_2026-10-30.md`](docs/D_PHASE1B_2026-10-30.md); số liệu ở [`docs/baselines/d_phase1b_2026-10-30.json`](docs/baselines/d_phase1b_2026-10-30.json).
    - **Code** (PR #3, commit `b317660`; 22/22 test đạt):
      - `filter_v2_reason` gồm 15 luật cho các lý do bỏ qua tự động hoá được.
      - Lọc câu trùng khuôn (ngưỡng 0,75).
      - `build` chặn rò rỉ nhãn (câu mới đã bỏ từ mà nhãn vẫn dùng).
      - `d_quality.py` thêm D-M6v2, D-M10/11 trên mẫu giữ lại, và D-M14 (phản tiền lệ, thô).
      - Không truyền cờ mới thì task v1 tái lập giống từng byte.
    - **Bộ lọc v2, đo trên 130 quyết định v1 (in-sample):** bắt 37/53 nguồn xấu, loại nhầm 6/77. Bản đầu dựa trên chữ "thì/nếu" loại nhầm 17 câu tốt nên đã thu hẹp.
    - **Đợt 1b:**
      - 33 task trên 4 tool.
      - Người viết bỏ **9/33 (27%)**: C 0/16, B-vague 9/17. **Cổng ≤ 15% vẫn không đạt**; con số in-sample (khoảng 12%) là quá lạc quan.
      - R7 loại 0/24; 24 mẫu giữ lại, phát lại qua ToolEnv đều thành công, tất cả có tiền lệ hỏi thật.
    - **Lỗi phát hiện:**
      - **Rò rỉ nhãn trong v1** ở `train_1140`: câu mới đã bỏ "xăng" nhưng nhãn vẫn có `news.search(query="giá xăng")`. Mẫu này nằm trong D-eval-24; giữ nguyên tập để so với mốc, và báo thêm kết quả trên D-eval-23.
      - **Chính sách tài khoản nguồn:** khi lời nói không nêu tài khoản, fit luôn chọn mặc định (7 lần thực hiện, 0 lần hỏi). 2 task "hỏi tài khoản nào" bị bỏ trước khi vào dữ liệu.
    - **D-train 1b = 77 mẫu**, 242 dòng SFT (6,0% số dòng gold). **Dưới mục tiêu 80–90.**
      - Tỉ trọng 3 tool đầu tăng 32% → 47%; số tool vẫn là 25.
      - Phần 1b phủ thêm 0 lần bỏ hỏi trên dev_lao (v1 phủ 4/12 lần ở tool đã thấy).
    - **Model hiện tại trên 24 mẫu 1b:** hỏi đúng 0/24 (fit_lao) và 1/24 (fit_random). Hai lượt chạy bằng `systemd-run`, mỗi lượt khoảng 2,5 phút. systemd đã thay `${t}` bằng chuỗi rỗng nên file của lượt fit_lao bị ghi sai tên; mình đã đổi tên lại.
    - **Nguồn gần cạn:** theo luật hiện tại chỉ còn 27 nguồn sạch, 16 là `reminders.create`.
    - **Đề xuất:**
      - Giai đoạn 2 ngay với D-train 77 mẫu (B-up / B-D1 / B-D3, 254 bước); phép so quan trọng nhất là B-D với B-up.
      - Phương án thay thế: giai đoạn 3 (nới luật) trước.
      - Việc đọc tay `review_v1_30.md` và `review_1b.md` vẫn mở.
20. **Giai đoạn 2 của D: bắt đầu train** (Anh chọn "Train giai đoạn 2", 30/10 18:17). Đang chạy; kết quả sẽ ghi vào báo cáo riêng.
    - **Code** (PR #3, commit `8209095`):
      - `train_local.sh` nhận `EXTRA_SAMPLES` và dựng file train riêng `sft/fit_lao_<TAG>.jsonl`, không đụng vào file của B0.
      - `scripts/phase2_d.sh` chạy cả giai đoạn; chạy lại thì bỏ qua bước đã xong.
    - **Ba lượt mới**, tất cả train lại từ Qwen3-1.7B gốc trên fit_lao, với đúng thiết lập của B0 (`q17b_fit_lao`):
      - Cùng 254 bước (`--max-steps 254`), seed 0, LoRA r32, lr 2e-4, grad_accum 16.
      - Chỉ đánh giá checkpoint final.

      | Lượt | Dữ liệu thêm | Số dòng thêm |
      |---|---|---:|
      | `q17b_lao_d3` | D-train 1b lặp 3 lần | 734 |
      | `q17b_lao_up` (đối chứng) | 232 bản sao mẫu hỏi lại thật kiểu B/C của fit_lao (112 mẫu gốc: 67 C, 45 B) | 734 |
      | `q17b_lao_d1` | D-train 1b | 242 |

    - **Đã kiểm trước khi chạy:**
      - Phần gold của cả 3 file SFT giống B0 từng byte (4.051 dòng).
      - B-D3 và B-up có cùng tổng số dòng (4.785). Với seed 0, hai lượt này thấy đúng cùng một tập dòng gold, chỉ khác phần dòng thêm.
      - Vì giữ 254 bước, mỗi lượt chỉ đi qua 4.064 dòng đầu của lượt xáo trộn: khoảng 85% dữ liệu với D3 và B-up, khoảng 95% với D1. B0 thấy toàn bộ.
    - **Chạy bằng** `systemd-run` (unit `lifemate-phase2-d`, MemoryHigh 6G / MemoryMax 8G); có chặn idle-sleep, không ghi đè hành vi gập nắp. Log ở `lifemate/runs/phase2_d.log`.
    - **Đo được:** khoảng 150 phút train mỗi lượt (như B0), đỉnh VRAM 5,62GB.
    - **Chấm mỗi lượt:** dev_lao (so theo cặp với B0), D-eval-24 và CS-pilot-23.
    - **Ghi chú vận hành:** trong lúc train, không đổi nhánh trong thư mục repo. `main` không có code `lifemate/`, nên đổi nhánh sẽ xoá script đang chạy. Tài liệu trên `main` được sửa qua một git worktree riêng.
21. **Ưu tiên baseline đầu-cuối; sự cố `lifemate/gen/` trên repo public** (30/10, 20:10–20:45).
    - **Anh trả lời "Baseline đã xong chưa?":**
      - Phần agent (đọc chữ chuẩn) đã xong.
      - Đầu-cuối (audio → ASR → agent → Docker) thì chưa.
    - **Anh chọn:**
      - "Ưu tiên đầu-cuối" sau giai đoạn 2.
      - "Claude làm ASR baseline với 2 model".
      - "Gỡ `gen/` khỏi `main`".
    - **Sự cố `gen/`:**
      - Lúc 20:03, commit `1bbd05a` ("update") đưa 29 file `lifemate/gen/` (3,4 MB: lời nói, nhãn, kết quả tool chép từ train) lên `main`. Lý do: `.gitignore` của `main` khi đó chưa có `gen/`. Repo đang **public**, trong khi README dữ liệu cấm phát tán.
      - Có vẻ thư mục repo chính đã được đổi sang `main` để commit rồi đổi lại `exp-d`. Khi đổi lại, git **xoá các file `gen/` trên máy**, đúng lúc giai đoạn 2 sắp cần chúng: CS-pilot-23, D-eval-24, dữ liệu thêm của B-up và B-D1.
      - **Đã xử lý:**
        - Khôi phục cả 29 file từ `1bbd05a`. Hash của `d_train_1b_x3.jsonl` khớp manifest SFT của lượt D3; `tasks_v1.jsonl` vẫn là `67f48ca1…`.
        - Gỡ `gen/` khỏi `main` (`4e908be`) và thêm `gen/` vào `.gitignore` của `main`.
        - Đồng bộ sang `agent-pipeline`, `eval-protocol`, `exp-d`. Giai đoạn 2 không bị gián đoạn.
      - **Còn lại:** bản cũ vẫn xem được trong lịch sử git. Chuyển repo sang private, hoặc viết lại lịch sử, là việc Anh quyết. Muốn chia sẻ file `gen/` cho leader thì gửi riêng, không qua repo.
      - **Anh quyết giữ repo public** (30/10, trong chat). Lịch sử không bị viết lại; `1bbd05a` vẫn còn. Từ nay `gen/`, `asr/`, `runs/`, `sft/`, `ckpt/`, `data/` đều được bỏ qua trên mọi nhánh.
    - **Code baseline đầu-cuối** ([PR #4](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/4), nhánh `e2e-baseline` xếp chồng lên PR #3, commit `236bca1`). Chỉ thêm file mới; `infer.py`, `agent.py`, `prompt.py` giữ nguyên vì giai đoạn 2 đang chạy từ thư mục này.
      - `lifemate/asr.py`: ASR có sẵn cho mọi wav của một split (lượt cuối và lượt user trong history). Giải mã greedy, tiếng Việt, ghi đúng giao kèo mà `infer.py --text asr` đọc; không bao giờ đọc `<split>_environment/`.
      - `scripts/asr_quality.py`: WER (có và không dấu) cho lượt cuối và history. Đo riêng những gì làm đổi hash: số, tiền, giờ của lệnh ghi còn được nói ra không (chữ số và chữ đều tính), từ phủ định, query tìm kiếm.
      - `scripts/check_submission.py`: kiểm cấu trúc, id và `zaic_tools --validate` của BTC; tính thời gian ASR + agent mỗi mẫu.
      - `scripts/predict.sh`: một lệnh offline (`HF_HUB_OFFLINE=1`) từ thư mục dữ liệu ra `submission.jsonl` đã kiểm. Đây là lõi để đóng Docker.
      - `scripts/e2e_baseline.sh`: lượt đo đêm nay. Không train.
      - Test: `test_asr` 8/8, `test_scorer` 11/11, `test_counterfactual` 22/22.
    - **Model ASR** (đã tải về cache, ghim revision; cả hai phát hành trước 26/10/2026):

      | Model | Tham số | Licence | Revision |
      |---|---|---|---|
      | `openai/whisper-large-v3-turbo` | 0,8B | MIT | `41f01f3f` |
      | `vinai/PhoWhisper-large` | 1,55B | BSD-3 | `b9136a44` |

    - **Thử nhanh trên CPU, 3 câu dev, Whisper-turbo bf16:** chạy được, nhưng nghe kém. Ví dụ "huỷ lịch" → "bị dịch", "nạp giúp" → "nặng chúc". Chưa kết luận được: chỉ 3 câu, và bf16 trên CPU có thể làm kém đi.
    - **Đã đo:** `audio_text` của train viết số bằng chữ nhiều hơn chữ số (1.371 so với 481 trên 5.036 câu), trong khi Whisper hay xuất chữ số. Model agent học theo kiểu của `audio_text`, nên đây là một nguồn lệch cần đo.
    - **Lượt đo đã xếp lịch** (unit `lifemate-e2e-baseline`, MemoryHigh 7G / MemoryMax 9G, chặn idle-sleep). Unit chờ `lifemate-phase2-d` xong rồi chạy `e2e_baseline.sh`, log ở `lifemate/runs/e2e_baseline.log`:
      1. ASR 2 model trên wav của dev_random (784) và dev_lao (1.117), rồi đo chất lượng ASR.
      2. Agent đọc chữ ASR: `q17b_fit_random/final` trên dev_random, B0 trên dev_lao. So theo cặp với run chữ chuẩn đã có (53,92 và 35,53).
      3. Chọn model ASR theo luật đặt trước: điểm gộp dev_random + dev_lao cao hơn; cách nhau dưới 1 điểm thì chọn turbo.
      4. public_test qua `predict.sh` (ASR batch 1 để đo độ trễ), được `runs/e2e_public_<asr>.jsonl` đã kiểm.
      5. Chạy lại ASR trên 50 wav để kiểm tái lập.
    - Dự kiến khoảng 2–2,5 giờ GPU, có số liệu khoảng 6 giờ sáng 31/10. Báo cáo sẽ ở `docs/E2E_BASELINE_2026-10-31.md`.
    - **Ngoài phạm vi, cần Anh quyết riêng:**
      - Nộp public: Anh tự nộp.
      - Train thêm.
      - Thuê cloud (4B, A30, vLLM).
      - Cài Docker trên máy này.
      - Fine-tune ASR và chuẩn hoá số (phần của leader).
22. **Prompt deep research cho Codex** (30/10, 21:00).
    - Anh muốn dùng Codex, trong lúc máy chạy, để nghiên cứu rộng các paper, kỹ thuật và repo liên quan, rồi đối chiếu với những gì đội đã, đang và định làm.
    - Claude viết prompt: [`docs/CODEX_RESEARCH_PROMPT_2026-10-30.md`](docs/CODEX_RESEARCH_PROMPT_2026-10-30.md). Nội dung gồm:
      - luật an toàn trên máy đang chạy job: không đụng git, GPU, `runs/`; không đưa dữ liệu thi ra ngoài;
      - bối cảnh và số liệu; danh sách file phải đọc;
      - 12 trục nghiên cứu A–L, gắn với Q1–Q20;
      - tiêu chuẩn trích dẫn; bộ lọc tuân thủ luật thi; khung chấm đề xuất;
      - 7 điểm phản biện bắt buộc về các lựa chọn hiện tại.
    - **Đầu ra dự kiến:** `docs/research/CODEX_DEEP_RESEARCH_2026-10-31.md` và `docs/research/codex_sources_2026-10-31.csv`. Codex chỉ ghi file, không commit; đội đọc rồi mới đưa lên `main`.
23. **Sự cố đổi nhánh lần 2; job chuyển sang worktree riêng** (30/10, 20:56–21:18).
    - Lúc 20:56:43, thư mục repo chính bị chuyển từ `e2e-baseline` sang `main` (reflog: `checkout: moving from e2e-baseline to main`). Không rõ người làm; Codex desktop đang chạy trên máy từ 20:38.
    - **Hậu quả:**
      - `main` không có code `lifemate/`. Lúc 20:58:53 bước chấm lượt D3 báo `No module named lifemate.infer`, và unit giai đoạn 2 dừng.
      - Unit đo đầu-cuối thấy giai đoạn 2 dừng nên tự khởi động, rồi hỏng vì không có script.
      - Train D3 đã xong và checkpoint `final` đã lưu trước đó, nên không mất gì.
      - `gen/` lần này không bị xoá, vì `main` đã bỏ qua `gen/` (entry 21).
    - **Xử lý:** từ 21:01, mọi job dài chạy từ worktree riêng **`~/zac-jobs`** (detached, ở commit `e19fb0e` của `e2e-baseline`).
      - `data`, `lifemate/{.venv,ckpt,runs,sft,gen,asr}` là symlink về thư mục chính, nên kết quả vẫn ghi đúng chỗ cũ.
      - Đổi nhánh trong thư mục chính không còn làm hỏng job.
      - Unit `lifemate-night` (script `~/zac-jobs/run_night.sh`) chạy lần lượt: chấm D3 → B-up → B-D1 → đo đầu-cuối. Dự kiến xong khoảng 5 giờ sáng 31/10.
    - **D3 đã có số** (chưa kết luận khi chưa có đối chứng; báo cáo đầy đủ sẽ có trong `docs/D_PHASE2_*.md`):
      - dev_lao 31,23 so với 35,53 của B0 (−4,30; khoảng tin cậy 95% từ −9,18 tới +0,55).
      - Hỏi lại 20,24 so với 7,48; hỏi đúng ở app chưa thấy 8/23 so với 0/23.
      - Nhưng hỏi thừa ở mẫu execute tăng từ 15 lên 34.
24. **Báo cáo deep research của Codex** (30/10, 21:23; Anh đồng ý đưa lên `main`): [`docs/research/CODEX_DEEP_RESEARCH_2026-10-31.md`](docs/research/CODEX_DEEP_RESEARCH_2026-10-31.md), kèm [bảng 81 nguồn](docs/research/codex_sources_2026-10-31.csv).
    - **Claude đã kiểm:**
      - **Không có dữ liệu thi:** dò mọi đoạn 6 từ liên tiếp của 5.036 câu `audio_text` trong train, 0 câu trùng.
      - **6 paper ACL 2025–2026:** When2Call, Learning to Ask, Ask-Answer-or-Act, Calibration is the Bottleneck, ToolWeave, State-Path Menu. Tiêu đề đều khớp.
      - **9 model trên Hugging Face:** ngày, licence, số tham số khớp. Riêng Gemma-4-E2B có repo từ 02/03/2026, không phải 02/04; vẫn trước mốc.
      - **NeMo `r1.2.0`** (05/06/2026): có ITN tiếng Việt.
      - **Qwen3-ASR-0.6B:** có tiếng Việt, cần package `qwen-asr`.
      - **`agent.py:150`** đúng là chỉ xem đồng hồ ở đầu mỗi bước, nên bước cuối có thể vượt 30 giây.
    - **Thông tin mới quan trọng:**
      - Qwen3-ASR-0.6B (thực tế 938M tham số; với Qwen3-4B tổng 4,96B).
      - NeMo ITN tiếng Việt.
      - Gipformer 68M và BuzzASR (số tự báo).
      - Bẫy đếm tham số: Qwen3.5-4B thực tế 4,66B; Qwen3-ASR-1.7B cộng Qwen3-4B vượt 6B.
      - Hướng "calibration theo kiểu hành vi" (hỏi / làm / bỏ qua) cho ranh giới hỏi lại.
    - **Claude đồng ý:**
      - P0: chặn lệnh ghi dùng ID chưa từng xuất hiện trong kết quả tool hay history (rẻ, không train).
      - P0: thêm Qwen3-ASR-0.6B vào so sánh ASR; thử NeMo ITN.
      - P0: Qwen3-4B; Docker/A30 tái lập 5 lần.
      - P1: dữ liệu tổng hợp quy mô nhỏ.
      - P2: RL, audio-LLM end-to-end.
    - **Claude xếp khác:**
      - Ép định dạng JSON lúc sinh xuống thấp hơn, vì chỉ 5/233 trace có lỗi định dạng.
      - Đề xuất thêm: chỉnh ngưỡng xác suất chọn `ask_missing_info` lúc suy luận, để giữ phần lợi của D mà bớt hỏi thừa. Ngưỡng chỉnh trên tập dò từ fit, không chỉnh trên dev.
    - **Đã cũ trong báo cáo:** "hai job chưa có điểm do lỗi đường chạy" (Codex đọc trước khi chạy lại). Các đề xuất sẽ được gộp vào kế hoạch khi có báo cáo giai đoạn 2 và báo cáo đầu-cuối.
25. **Bổ sung: việc tối 30/10 cho Anh và leader** (30/10, 20:40; ghi muộn, phát hiện khi rà ở entry 26).
    - Anh hỏi: trong lúc chờ máy chạy, Anh và leader làm gì, trong file nào, trên máy leader.
    - Claude viết mục 0 của [`HUMAN_TODO.md`](HUMAN_TODO.md) (commit `8d9026b`). Lượt này khi đó chỉ ghi vào HUMAN_TODO, chưa có entry ở đây.
      - **Máy Anh chỉ đọc file:** không đổi nhánh, không commit trong thư mục repo, không mở ứng dụng nặng.
      - **Ghi kết quả:** câu trả lời vào `HUMAN_TODO.md` trên `main`; góp ý code bằng comment trên PR #4. Không commit `data/`, `gen/`, `asr/`, `runs/`.
    - **Các việc**, xếp theo mức có ích cho các quyết định sáng 31/10 (chọn ASR, nộp public, Docker):
      - 0.1 [Leader] dựng môi trường từ nhánh `e2e-baseline` và chạy test. Đây cũng là lần tập dượt cho Docker.
      - 0.2 [Cả hai] nghe audio train, gồm 3 câu Whisper-turbo nghe sai. Câu cần trả lời: `audio_text` là kịch bản người nói đọc theo, hay transcript thật? Nếu người nói đọc lệch kịch bản, WER sẽ phạt oan ASR.
      - 0.3 [Leader] danh sách cụm từ nguy hiểm cho ASR, đối chiếu với danh sách từ phủ định trong `asr_quality.py`.
      - 0.4 [Leader] rà model ASR và LLM mới.
      - 0.5 [Leader] forum và câu hỏi cho BTC về Docker.
      - 0.6 [Leader] review PR #4: định dạng file ASR và biến môi trường của `predict.sh`.
      - 0.7 [Cả hai] chuẩn bị quyết định nộp public.
      - 0.8 [Leader, tuỳ chọn] chạy turbo trên các câu vừa nghe. Chỉ chạy trên train.
      - 0.9 [Anh] Codex deep research. Đã xong (entry 24).
26. **Anh hỏi: journal có tự cập nhật các lượt vừa rồi chưa, và đang chờ gì** (30/10, 23:05).
    - **Cách Claude ghi journal:**
      - Sau mỗi lượt có nội dung, Claude thêm entry ở mục 7, sửa mục 0 và mục 8, commit thẳng lên `main`, rồi đồng bộ sang các nhánh code.
      - Nội dung ghi: câu hỏi và lựa chọn của Anh, những gì đã kiểm, kết luận và lý do, kể cả chỗ Claude không đồng ý (ví dụ entry 24). Không chép nguyên văn suy nghĩ nội bộ.
    - **Kiểm lại lúc này:**
      - Các lượt tới "Đưa lên main" đã có ở entry 21–24.
      - Thiếu lượt "việc tối nay": nay bổ sung ở entry 25.
      - Mục 8 thêm các việc rút từ báo cáo Codex.
    - **Máy lúc 23:05:**
      - B-up ở bước 175/254, loss khoảng 0,03–0,05.
      - Đỉnh VRAM 5,78 GB; RAM còn khoảng 5 GB.
    - **Đang chờ** (giờ 31/10 là ước tính):

      | Khoảng giờ | Mốc | Claude làm ngay sau |
      |---|---|---|
      | 0:15 | B-up (đối chứng) có điểm | So D3 với B-up. Hai lượt thấy cùng các dòng gold, cùng số dòng thêm; chỉ khác dòng thêm là D hay mẫu hỏi lại thật nhân bản. Đây là phép thử chính của D. Tiêu chí đặt trước: B-D phải hơn B0 ≥ 10 điểm hỏi lại (D3 đã đạt: 20,24 so với 7,48) **và** hơn B-up ≥ 5 điểm. |
      | 3:00 | B-D1 có điểm, giai đoạn 2 xong | Chạy `phase2_report.py`. Viết `docs/D_PHASE2_2026-10-31.md` và kết luận theo tiêu chí. |
      | 5:00–5:30 | Đo đầu-cuối xong | Viết `docs/E2E_BASELINE_2026-10-31.md`: điểm mất do ASR, model ASR được chọn, file public đã kiểm, thời gian mỗi mẫu. Anh quyết có nộp không. |

    - **Trong lúc chờ:** GPU bận tới sáng, nên chỉ làm được việc chạy trên CPU. Ví dụ: đo trên trace có sẵn xem chốt chặn ID (entry 24) cứu được bao nhiêu mẫu, trước khi viết code.
27. **Đo chốt chặn ID trên CPU** (30/10, 23:10–23:20; Anh chọn "Làm luôn"). Chi tiết ở [`docs/ID_GUARD_2026-10-30.md`](docs/ID_GUARD_2026-10-30.md); số liệu ở [`docs/baselines/id_guard_2026-10-30.json`](docs/baselines/id_guard_2026-10-30.json); script ở [PR #5](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/5), chỉ phân tích, không đổi agent.
    - **Quy tắc:** chặn lệnh ghi khi một tham số có `x-ref` trong schema mang ID chưa từng xuất hiện trong prompt, history hay kết quả tool trước đó.
      - Quy tắc dựa trên catalog, nên áp dụng được cho app chưa thấy.
      - Chạy lại các call của 4 lượt có sẵn trên ToolEnv: khớp file nộp 100%.
    - **Kết quả:**
      - Chặn nhầm 1/912 giá trị của đáp án fit. Ca đó là do dữ liệu lệch.
      - dev_random chặn 0 call, điểm không đổi. dev_lao chặn 4 call (B0) và 7 call (D3), tất cả đều sai.
      - Điểm chỉ đổi ở D3: +0,19 tới +0,26, nhờ 1 mẫu.
    - **Lỗi ID thật là chọn nhầm một ID đã thấy** (7–9% mẫu), ví dụ chuyển tiền từ nhầm tài khoản. Chốt chặn không bắt được loại này.
    - **Lệnh ghi sai nhiều nhất** là ở tham số không phải ID (giờ, số tiền, nội dung: 24 / 54 / 41 call), rồi tới ghi sai tool và ghi thay vì hỏi lại.
    - **Quyết định đề xuất:** hạ chốt chặn ID từ P0 xuống lưới an toàn. Viết khoảng 20 dòng cùng lúc với phần sửa thời gian ở `agent.py` trước Docker; không cần lượt GPU riêng.
    - **Việc CPU tiếp theo đáng làm:** tách nhóm "sai tham số khác" theo loại (ngày giờ, số tiền, chữ tự do, enum).
28. **Lệnh ghi sai vì sao, mỗi nguyên nhân đáng bao nhiêu điểm** (30/10, 23:20–23:35; Anh chọn "Làm luôn"). Chi tiết ở [`docs/PARAM_ERRORS_2026-10-30.md`](docs/PARAM_ERRORS_2026-10-30.md); số liệu ở [`docs/baselines/param_errors_2026-10-30.json`](docs/baselines/param_errors_2026-10-30.json); script `param_errors.py` thêm vào [PR #5](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/5).
    - **Cách đo:**
      - Ghép mỗi lệnh ghi sai với lệnh cùng tool gần nhất trong đáp án, rồi phân loại tham số lệch theo kiểu trong schema.
      - Đếm riêng lệnh ghi sai tool và lệnh ghi bị thiếu.
      - Sửa giả định từng nguyên nhân theo đáp án, chạy lại trên ToolEnv rồi chấm, để có trần điểm của nguyên nhân đó.
      - Chỉ CPU, 14 giây, chạy lại khớp file nộp 100%.
    - **Đính chính entry 27:** nhóm "sai tham số không phải ID" không phải nguồn mất điểm lớn nhất. Lớn nhất là **không làm đủ**:
      - Thiếu lệnh ghi: +6,2 (dev_random), +8,4 (B0) và +14,4 (D3) nếu sửa hết.
      - Ghi sai tool hoặc ghi thừa: +2,6 / +6,8 / +5,5.
      - Lệnh ghi bị thiếu là do model tự dừng (20 / 33 / 44 mẫu: yêu cầu nhiều vế làm thiếu một vế, câu điều kiện đi nhầm nhánh), hoặc hỏi lại thay vì làm (14 / 15 / 33 mẫu; D3 tăng mạnh).
    - **Trong lỗi tham số:** chọn nhầm ID +4–5; ngày giờ +2–4; còn lại mỗi nhóm ≤ ~2 (số, chữ tự do, tham số thừa, enum). Sửa hết lỗi tham số cùng lúc: +14–16.
    - **Ngày giờ:**
      - dev_random chủ yếu sai ở phép tính giờ nhiều bước, ví dụ "đón sớm 30 phút so với giờ hẹn".
      - dev_lao có thêm nhầm sáng/tối ("chín giờ tối" thành 09:00 hoặc 23:00) và nhầm "thứ ba tuần sau".
    - **Số:** chỉ 6 call, đều là lỗi tính toán, không có lỗi ×1000.
    - **Không có luật code rẻ nào cho phần lớn lỗi.** Schema cũng không khai báo giá trị mặc định, nên không bỏ được `robot_vacuum.start.mode` thừa bằng code.
    - **Hướng đề xuất:**
      - Dữ liệu SFT có yêu cầu nhiều vế và điều kiện, kiểm chứng bằng ToolEnv.
      - Model 4B (Anh quyết thuê cloud).
      - Phần rẻ: quy ước sáng/tối và "tuần sau", nhưng phải train lại mới đo được, nên làm sau giai đoạn 2.
      - Khi so D3 với B-up cần nhìn cả cái giá "hỏi lại thay vì làm".
29. **Anh đi ngủ; Claude tự làm tiếp qua đêm; được thuê cloud** (30/10, 23:58).
    - **Anh yêu cầu:**
      - Claude tự thu và đánh giá kết quả train.
      - Tự lên kế hoạch ngày mai để Anh, leader và Claude làm song song.
      - Đội thuê được cloud, nên Claude chuẩn bị gói code, dữ liệu và tài liệu để Anh đẩy lên cloud train cho nhanh.
    - **Bộ công cụ cloud** ([PR #6](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/6), nhánh `cloud-train`; hướng dẫn ở [`docs/CLOUD_TRAIN_2026-10-31.md`](docs/CLOUD_TRAIN_2026-10-31.md)):
      - `make_cloud_bundle.sh`: gói riêng tư gồm code ở một commit, dữ liệu (audio tuỳ chọn), `gen/`, adapter và các lượt gốc. Kèm manifest sha256 của các file ngoài git và của các file SFT local.
      - `cloud_setup.sh`:
        - Kiểm gói; tạo venv đúng phiên bản thư viện local, với torch 2.15.0 bản CUDA hợp với driver.
        - Ghim revision model gốc, dựng lại SFT rồi so với bản local.
        - Smoke test 3 bước train cộng 2 rollout.
      - `cloud_arms.sh`: chạy các lượt bằng đúng pipeline local, mỗi GPU một hàng đợi, tự so theo cặp với lượt gốc, rồi đóng gói kết quả.
      - **Lượt mặc định:** chấm lại 2 adapter 1.7B (kiểm parity); 4B với đúng công thức 1.7B trên fit_random và fit_lao.
      - **Đã kiểm trên máy local:**
        - Gói thật 255 MB, ở `~/zac_cloud_bundle_20261031.tar.gz`. Kiểm gói 0 file lệch.
        - Test đạt; **4 file SFT dựng lại giống hệt từng byte**.
        - Chạy thử khô việc chia lượt cho 2 GPU: đúng.
      - **Chưa kiểm:** cài torch và smoke test 4B trên máy thuê thật; parity giữa hai máy.
    - **Kết quả tạm của giai đoạn 2** (00:07; B-D1 chưa xong):

      | dev_lao (262) | Tổng | Hỏi lại | Execute | Ngoài phạm vi |
      |---|---:|---:|---:|---:|
      | B0 | 35,53 | 7,5 | 39,7 | 71,4 |
      | D3 | 31,23 | 20,2 | 32,5 | 57,1 |
      | B-up (đối chứng) | **36,94** | **30,0** | 36,7 | **85,7** |

      - **D3 so với B-up:** −5,70 điểm, khoảng tin cậy 95% từ −10,32 tới −1,15. D3 thua đối chứng rẻ, nên **không đạt tiêu chí đặt trước** (phải hơn B-up ít nhất 5 điểm hỏi lại).
      - **B-up so với B0:** +1,41, khoảng tin cậy từ −2,86 tới +5,82; chưa chắc chắn.
      - Theo kế hoạch đặt trước ([REVIEW_D](docs/REVIEW_D_2026-10-30.md)), trường hợp này dẫn tới: cân lại tỉ trọng mẫu hỏi lại thật, và hạ ưu tiên D. Kết luận đủ khi có B-D1 (khoảng 3 giờ sáng).
30. **Giai đoạn 2 của D xong: D bị loại theo tiêu chí đặt trước** (31/10, 03:09–03:20; Claude tự làm trong lúc Anh ngủ). Báo cáo: [`docs/D_PHASE2_2026-10-31.md`](docs/D_PHASE2_2026-10-31.md).
    - **B-D1** (77 dòng D, mỗi dòng một lần): tổng 37,32, hỏi lại 20,41, execute 39,45. Cao nhất về tổng, nhưng hơn B0 chỉ +1,79 (khoảng tin cậy −2,80 tới +6,37) và hơn B-up +0,39.
    - **Tiêu chí:** D1 và D3 đều chỉ đạt 1/5 điều kiện (hỏi lại hơn B0 ≥ 10). Cả hai thua B-up khoảng 9,6 điểm hỏi lại, hỏi thừa tăng 17–19 mẫu, D-eval chỉ lật đúng 1/24 và 4/24 cặp. → **Không giữ D; không làm giai đoạn 3.**
    - **B-up:** hỏi lại +22,5 (khoảng tin cậy +10,7 tới +35,3), tổng +1,4 (chưa chắc). Theo kế hoạch đặt trước: thử cân lại tỉ trọng hỏi lại trên fit_random (ràng buộc dev_random không giảm quá 1 điểm). Lượt đã sẵn trong gói cloud, chờ Anh bật.
    - **Claude tự suy luận thêm, đo bằng script mới** `scripts/overask_cost.py` (PR #5, commit `cdee489`, chỉ đọc `runs/`):
      - Câu hỏi: hỏi thừa tăng gấp đôi (16 → 31–35 mẫu) thì mất bao nhiêu điểm? Nếu nhiều, nên làm ngưỡng hỏi lại lúc suy luận (việc Codex đề xuất).
      - Trả lời: chỉ mất 1,2–2,4 điểm, vì model hỏi thừa ở các mẫu khó mà B0 cũng làm sai (B0 chỉ đúng 4,5/21 mẫu). Lọc hoàn hảo cũng chỉ thêm tối đa 1,7 điểm. → **Hạ ưu tiên ngưỡng hỏi lại.**
      - D3 mất 3,9 điểm ở các mẫu nó không hỏi thừa; D1 không bị. Nhân dữ liệu tổng hợp 3 lần làm execute kém đi.
      - Loss trên dev gần như bằng nhau (0,134–0,138) dù điểm cách nhau 6. Tiếp tục chọn bằng điểm rollout.
    - **Không đề xuất** ghép B-up với D1: không có trong kế hoạch đặt trước, và dev_lao đã bị xem nhiều lần.
    - Lượt đo đầu-cuối bắt đầu 03:09 trong cùng unit; ASR turbo trên dev_random mất 84 giây cho 784 wav (0,11 giây mỗi wav, batch 16).
31. **Baseline đầu-cuối xong: lỗi ASR làm mất khoảng 20 điểm** (31/10, 03:09–05:00; Claude tự làm trong lúc Anh ngủ). Báo cáo: [`docs/E2E_BASELINE_2026-10-31.md`](docs/E2E_BASELINE_2026-10-31.md).
    - **Điểm:** chữ chuẩn → Whisper-turbo: dev_random 53,92 → 31,69, dev_lao 35,53 → 17,14. PhoWhisper: 27,90 và 15,58. Khoảng tin cậy của cả bốn chênh lệch đều loại 0.
    - **PhoWhisper hết bộ nhớ GPU ở batch 16** (03:13). Claude tự chạy lại ở batch 4 trong unit `lifemate-pho` để vẫn so đủ hai model như kế hoạch.
    - **Chọn turbo theo luật đặt trước** (cộng gộp 495 mẫu: 23,99 so với 21,38). File nộp public `runs/e2e_public_turbo.jsonl` đã kiểm 0 lỗi; chạy lại ASR 50 wav giống hệt.
    - **Claude tự suy luận thêm:**
      - *Người nói có đọc lệch kịch bản không* (câu hỏi ở HUMAN_TODO 0.2)? Ở dev_random, khi hai model ASR nghe gần giống nhau (209 câu), chỉ 7 câu khác hẳn `audio_text`. → Hiếm; WER phản ánh lỗi nghe thật.
      - *Vì sao PhoWhisper sai ít từ hơn mà điểm thấp hơn?* PhoWhisper giữ query kém hơn (44–58% so với 60–63%), và không viết hoa, không dấu phẩy, không chữ số. Ngay cả câu sai dưới 10% số từ vẫn mất nhiều điểm. → Chọn ASR theo điểm agent và độ đúng slot, không theo WER.
      - *Mất ở đâu?* Chỉ khoảng 9% mẫu có lượt cuối sai dưới 10% số từ. Phần lớn điểm mất ở nhóm sai 25–50%. Số mẫu model không gọi tool nào tăng gấp 2–4 lần (script mới `scripts/asr_loss.py`, PR #5).
    - **Đổi ưu tiên:** ASR lên số 1, vì lớn hơn mọi phần sửa agent đã đo (6–8, 4–5, 2–4 điểm).
    - **Chuẩn bị cho cloud** (PR #6, commit `84c0a0b` cùng các commit sau):
      - `train_local.sh` / `eval_ckpt.sh` nhận `ASR_FIT`, `ASR_DEV`, `ASR_FILE`. `cloud_arms.sh` nhận `REF_ASR`. Gói đóng thêm `asr/train_*`.
      - Hai lượt 4B mặc định giờ chấm cả trên chữ turbo.
      - Lượt mới, đang để ghi chú chờ Anh: `q17b_random_asrtrain` (học trên chữ turbo), `q17b_random_asrtrain_pho`, `q4b_random_asrtrain`.
      - Transcript turbo và PhoWhisper của toàn bộ 5.036 wav train tạo trên laptop lúc 04:33–05:04. Chỉ train; public_test không bị chạy ASR ngoài `predict.sh`. Batch khác nhau gần như không đổi transcript (dev: 0/1.901 wav khác với turbo, 1/1.901 với PhoWhisper).
      - Dữ liệu SFT fit_random dựng từ chữ turbo: đúng 4.150 dòng, phần được train và cách tăng cường giống hệt bản chữ chuẩn.
      - **Gói mới** `~/zac_cloud_bundle_20261031_asr.tar.gz` (256 MB, sha256 `3a3fb94822a9…`, code `f34defa`); gói cũ không dùng nữa.
      - **Chạy thật trên laptop** một lượt qua `cloud_arms.sh` từ gói vừa giải nén (chấm 1.7B trên chữ turbo): 31,69, giống hệt 233/233 dự đoán của lượt đầu-cuối. Bộ công cụ chạy đúng đầu-cuối; chưa chạy thật lượt train nào.
    - **Kế hoạch ngày 31/10** cho Anh, leader và Claude: [`docs/PLAN_2026-10-31.md`](docs/PLAN_2026-10-31.md).

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
- [x] D giai đoạn 1 (D v1, 77 mẫu) và giai đoạn 1b (bộ lọc v2, D-train 77 mẫu) (30/10, `docs/D_PHASE1_2026-10-30.md`, `docs/D_PHASE1B_2026-10-30.md`).
- [x] Anh quyết: giai đoạn 2 ngay với D-train 77 mẫu (khuyến nghị), hay giai đoạn 3 (nới luật) trước. *Anh chọn giai đoạn 2 (30/10).*
- [x] Giai đoạn 2 của D: xong 31/10 03:09. **D bị loại**, B-up thắng; xem `docs/D_PHASE2_2026-10-31.md` (entry 30).
- [ ] **Cân lại tỉ trọng hỏi lại trên fit_random** (`q17b_random_up`, cloud): dev_random không giảm quá 1 điểm thì dùng công thức B-up làm mặc định.
- [x] Anh quyết ưu tiên sau D: **baseline đầu-cuối** (30/10, entry 21).
- [x] **Baseline đầu-cuối** ([PR #4](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/4)): xong 31/10 (entry 31). ASR làm mất khoảng 20 điểm.
- [ ] Anh quyết có nộp `lifemate/runs/e2e_public_turbo.jsonl` lên public không (Anh tự nộp).
- [ ] **Fine-tune ASR** trên wav của fit (leader, cloud); đánh giá bằng điểm agent và độ đúng slot.
- [ ] **Train agent trên chữ ASR** (`q17b_random_asrtrain`, cloud; chờ Anh bật).
- [ ] **Từ báo cáo Codex (entry 24), chưa làm:**
  - [x] **Chốt chặn ID: đã đo** (entry 27). Gần như không thêm điểm (0 / 0 / +0,26), nên hạ xuống lưới an toàn: viết cùng phần sửa `agent.py:150`, không cần lượt GPU riêng.
  - [x] **Tách lệnh ghi sai theo nguyên nhân** (entry 28): mất nhiều nhất là thiếu lệnh ghi và ghi sai tool, rồi tới chọn nhầm ID và ngày giờ.
  - **Dữ liệu SFT nhiều vế và điều kiện** (P1 trong báo cáo Codex), kiểm chứng bằng ToolEnv; nhắm vào lỗi "tự dừng khi chưa làm đủ" (entry 28).
  - **Ngày giờ:** thử quy ước sáng/tối và "tuần này / tuần sau" (nhãn tuần trong bảng ngày, hoặc chuẩn hoá giờ nói). Cần train lại để đo, nên làm sau giai đoạn 2.
  - **Ngưỡng hỏi lại:** chỉnh ngưỡng xác suất chọn `ask_missing_info` lúc suy luận. Ngưỡng chỉnh trên tập dò từ fit, không chỉnh trên dev. Cần GPU, nên làm sau giai đoạn 2. *(31/10: hạ ưu tiên. Trần chỉ 1,2–1,7 điểm trên dev_lao, entry 30.)*
  - **Sửa `agent.py:150`:** xem thời gian còn lại trước khi sinh mỗi bước, để bước cuối không vượt 30 giây. Làm trước khi đóng Docker.
  - **[Leader]** Thêm Qwen3-ASR-0.6B vào so sánh ASR; thử ITN tiếng Việt của NeMo (`r1.2.0`).
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
  - Benchmark Whisper-turbo và PhoWhisper trên audio train: WER và độ đúng của số, giờ, tên. *(30/10: Claude chạy bản không fine-tune trên dev_random + dev_lao trong lượt đo đầu-cuối, `scripts/asr_quality.py`; leader dùng số liệu này làm điểm xuất phát.)*
  - Viết bộ chuẩn hoá chữ thành số (ITN).
  - Xuất `asr/<split>.jsonl` theo giao kèo; làm transcript k-fold cho SFT (`--asr-file`). *(Định dạng file đã có trong `lifemate/asr.py`, PR #4.)*
- [ ] Dữ liệu app tổng hợp: LLM mạnh sinh app, schema, simulator, câu yêu cầu và đáp án; chạy thật qua executor để kiểm chứng.
- [ ] **Cloud:** chạy gói train ([`docs/CLOUD_TRAIN_2026-10-31.md`](docs/CLOUD_TRAIN_2026-10-31.md), PR #6). Trước hết cần 2 lượt parity, rồi 4B trên fit_random và fit_lao với công thức 1.7B.
- [ ] Docker offline: dùng backend vLLM, đo thời gian trên GPU 24GB, chạy 5 lần kiểm tra tính tái lập. *(Lõi chạy offline: `scripts/predict.sh`, PR #4.)*

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
- Có model LLM hoặc ASR nào tốt hơn phát hành trước 26/10/2026 không? *(Một phần đã có trong mục 6 của báo cáo Codex, entry 24; leader rà tiếp ở HUMAN_TODO 0.4.)*
