# Nhật ký dự án — ZAIC 2026 LifeMate

File này ghi lại toàn bộ trao đổi và quyết định của đội, để:

1. **Leader và các thành viên theo dõi tiến độ** qua lịch sử commit trên GitHub.
2. **Làm context khi mở đoạn chat mới với Claude.** Mở chat mới thì yêu cầu: *"Đọc `JOURNAL.md` trước rồi tiếp tục"*.

**Quy tắc cập nhật:** sau mỗi buổi trao đổi hoặc mỗi mốc quan trọng, thêm một mục mới vào [Nhật ký theo thời gian](#7-nhật-ký-theo-thời-gian), sửa phần [Trạng thái hiện tại](#0-trạng-thái-hiện-tại), rồi commit và push. Mục cũ không xoá; nếu sai thì ghi đính chính ở mục mới.

**Quy tắc git:** tài liệu (`JOURNAL.md`, `docs/`, `README.md`) được commit thẳng vào `main`. **Code mới phải đi qua Pull Request.**

**Tài liệu liên quan:** [`docs/PIPELINE.md`](docs/PIPELINE.md) gồm moat, pipeline nền móng, tự đánh giá, đề án nâng cấp và 20 câu hỏi cho đội.

---

## 0. Trạng thái hiện tại

*Cập nhật: 2026-10-28, trước lượt train qua đêm đầu tiên.*

- **Đã xong:**
  - Phân tích đề, chốt kiến trúc.
  - Viết bộ chấm điểm local, prompt, vòng lặp agent, sinh dữ liệu SFT, script train LoRA. Toàn bộ trong `lifemate/`, nằm ở **PR `agent-pipeline` → `main`**, chờ review.
  - Chạy thử train trên RTX 4070 8GB thành công.
  - Viết tài liệu nghiên cứu [`docs/PIPELINE.md`](docs/PIPELINE.md).
- **Sắp chạy:** train Qwen3-1.7B qua đêm trên máy của Anh (lệnh ở [mục 6.4](#lệnh-chạy-train-qua-đêm); thư mục làm việc phải ở nhánh `agent-pipeline` vì code chưa vào `main`). Kết quả sẽ có ở `lifemate/runs/zs_q17b_fit_random_score.json` (trước khi train) và `lifemate/runs/sft_q17b_fit_random_score.json` (sau khi train).
- **Trong lúc train:** Anh và leader đọc `docs/PIPELINE.md` và trả lời 20 câu hỏi.
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
   - **Quy tắc git mới:** tài liệu vào thẳng `main`, code qua PR. Đã mở PR `agent-pipeline` → `main` cho code.

---

## 8. Việc tiếp theo

- [ ] Anh và leader trả lời 20 câu hỏi trong [`docs/PIPELINE.md`](docs/PIPELINE.md), rồi thảo luận với Claude để chốt kế hoạch nâng cấp.
- [ ] Review và merge PR `agent-pipeline` → `main`.
- [ ] Đọc kết quả train qua đêm: so điểm zero-shot với sau SFT trên dev_random, phân tích lỗi theo loại.
- [ ] Nộp public lần đầu để kiểm chứng 3 giả định của bộ chấm (mục 6.1).
- [ ] Cloud:
  - Baseline zero-shot Qwen3-4B-Instruct-2507 (`scripts/cloud_baseline.sh`).
  - SFT 4B trên `all.jsonl`.
  - Chạy `fit_lao` → `dev_lao` để đo khả năng xử lý app chưa thấy.
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
