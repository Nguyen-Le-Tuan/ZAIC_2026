# Việc của người — Anh và Leader

Danh sách việc trong lúc laptop của Anh train qua đêm, và sáng hôm sau. Phần cuối là 20 câu hỏi nghiên cứu, chép từ [`docs/PIPELINE.md`](docs/PIPELINE.md).

## Cách dùng file

- Mỗi việc ghi người phụ trách: **[Anh]**, **[Leader]** hoặc **[Cả hai]**.
- Xong việc nào thì đánh dấu `[x]` và ghi kết quả ngắn ngay dưới việc đó. Commit thẳng lên `main` (tài liệu không cần PR).
- Lượt train qua đêm đã xong lúc 02:40 ngày 2026-10-29 (dev_random 9,9 → 53,9), nên GPU trên laptop của Anh đã trống. Các lệnh ở mục 2–6 chỉ dùng CPU.
- Các lệnh chạy trong thư mục `lifemate/`, trên nhánh `agent-pipeline` (code chưa vào `main`, đang nằm ở [PR #1](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/1)).
- *29/10:* công cụ đánh giá mới (`scripts/eval_ckpt.sh`, `lifemate.compare`, `train_local.sh` chọn `FIT`/`DEV`) nằm ở nhánh `eval-protocol`, [PR #2](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/2), xếp chồng lên PR #1. Thư mục làm việc trên máy Anh đang ở nhánh này.
- Mọi lệnh trong file đã được Claude chạy thử trên máy của Anh ngày 2026-10-28.

---

## Ngày 31/10: làm song song (kế hoạch chi tiết: [`docs/PLAN_2026-10-31.md`](docs/PLAN_2026-10-31.md))

*Claude viết rạng sáng 31/10. Đọc trước: mục 1 của file kế hoạch, rồi phần kết luận của [`docs/E2E_BASELINE_2026-10-31.md`](docs/E2E_BASELINE_2026-10-31.md) và [`docs/D_PHASE2_2026-10-31.md`](docs/D_PHASE2_2026-10-31.md).*

Tóm tắt: agent đọc chữ ASR mất khoảng 20 điểm (dev_random 53,92 → 31,69; dev_lao 35,53 → 17,14), nên ASR lên ưu tiên số 1. D bị loại.

**Anh quyết (sáng):**
- [ ] **[Anh]** Nộp public `lifemate/runs/e2e_public_turbo.jsonl` không? (Khuyến nghị: nộp, để có mốc đầu tiên; dev dự đoán khoảng 17–32.) Anh tự nộp; ghi điểm vào đây: …
- [ ] **[Anh]** Bật lượt cloud nào trong `lifemate/cloud/arms_2026-10-31.txt`. Khuyến nghị: 4 lượt mặc định + `q17b_random_asrtrain` + `q17b_random_up`; thêm `q4b_random_asrtrain` nếu có 4 GPU.
- [ ] **[Anh]** PR: review và merge #1 rồi #2 trước; leader review #4, #6; #3 (D) có thể đóng không merge.

**Anh làm:**
- [ ] **[Anh]** Thuê máy cloud (2–4 GPU từ 40 GB; ổ ≥ 150 GB nếu leader dùng chung để fine-tune ASR). Chạy theo [`docs/CLOUD_TRAIN_2026-10-31.md`](docs/CLOUD_TRAIN_2026-10-31.md). Gói mới nằm ở `~/` (tên và sha256 trong file đó).
- [ ] **[Anh]** Mang `cloud_results_*.tar.gz` về `~/Zalo AI Challenge/cloud_results/`, báo Claude. Tắt máy và xoá dữ liệu trên đó khi xong.

**Leader làm:**
- [ ] **[Leader]** Fine-tune ASR (PhoWhisper-large hoặc Whisper-turbo) trên wav của fit, nhãn `audio_text`. Không dùng wav của dev_random/dev_lao để train; không dùng audio public_test. Cần gói `WITH_AUDIO=1`.
  - Đo bằng `scripts/asr_quality.py`. Điểm agent: `ASR_FILE=<file> TAG=<tên> ADAPTER=ckpt/q17b_fit_random/final DEV=dev_random bash scripts/eval_ckpt.sh`, hoặc nhờ Claude chạy.
  - Chọn theo điểm agent, không theo WER: PhoWhisper sai ít từ hơn turbo nhưng điểm agent thấp hơn.
- [ ] **[Cả hai]** Nghe 10–20 câu ASR sai nhiều nhất (danh sách id trong báo cáo E2E): tiếng ồn, giọng, tốc độ nói, từ lạ.
- [ ] **[Leader]** Bản Docker đầu tiên quanh `lifemate/scripts/predict.sh`, chạy offline trên máy leader; ghi thời gian.
- [ ] **[Leader]** Forum BTC: hướng dẫn Docker, máy chấm, Q1.

**Điểm hẹn:** 9:00 (chốt quyết định), 13:00 (cloud setup và parity; WER đầu tiên của ASR fine-tune), 18:00 (kết quả cloud, chọn công thức vòng sau).

## 0. Tối 30/10, trong lúc máy Anh chạy (tới khoảng 6 giờ sáng 31/10), làm trên máy leader

**Máy Anh:** chỉ đọc file. Không đổi nhánh, không commit trong thư mục repo, không mở ứng dụng nặng. Máy đang chạy giai đoạn 2 của D, rồi tới lượt đo đầu-cuối.

**Ghi kết quả ở đâu:**
- Câu trả lời và ghi chú: `HUMAN_TODO.md` trên `main`. Sửa trên GitHub web, hoặc trong clone của leader ở nhánh `main`.
- Góp ý code: comment trên [PR #4](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/4); Claude sửa.
- Không commit `data/`, `gen/`, `asr/`, `runs/`.

Các việc dưới đây xếp theo mức có ích cho các quyết định sáng 31/10.

- [ ] **[Leader] 0.1 Dựng môi trường** (khoảng 15 phút). Dùng nhánh `e2e-baseline`: có đủ code của PR #1–#4 và tài liệu mới nhất. Chạy được 2 bộ test trên máy thứ hai cũng là một lần tập dượt cho Docker.
  ```bash
  git clone https://github.com/Nguyen-Le-Tuan/ZAIC_2026.git && cd ZAIC_2026 && git checkout e2e-baseline
  mkdir -p data && unzip -q /đường/dẫn/tới/train+public_test.zip -x '__MACOSX/*' -d data   # phải ra data/train+public_test/
  cd lifemate && uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
  .venv/bin/python -m lifemate.tests.test_asr && .venv/bin/python -m lifemate.tests.test_scorer
  ```
- [ ] **[Cả hai] 0.2 Nghe audio train** (45–60 phút). Làm theo mục 3 (30 mẫu ngẫu nhiên), **cộng 3 câu Whisper-turbo nghe sai** trong lần thử: `train_0003`, `train_0019`, `train_0025`. Đó là 3 wav đầu của dev_random; nếu không có `aplay` thì mở bằng trình phát bất kỳ.
  - **Câu cần trả lời:** `audio_text` là kịch bản người nói đọc theo, hay transcript thật? Người nói có đọc lệch không? Ví dụ `train_0019`:
    - `audio_text`: "Chị ơi, giúp tôi đặt phòng khách sạn ở Đà Lạt với nhé"
    - ASR: "Giờ tôi cần đặt phòng các sản ở Đà Lạt nữa nha"

    Nếu người nói đọc lệch kịch bản, WER đo sáng mai sẽ phạt oan ASR, và nhãn để fine-tune ASR phải xử lý khác.
  - Ghi vào bảng ghi chú ở mục 3.
- [ ] **[Leader] 0.3 Danh sách "cụm từ nguy hiểm" cho ASR** (khoảng 20 phút; mục 3, Q9). Viết từ những gì vừa nghe.
  - Đối chiếu với danh sách từ phủ định mà `lifemate/scripts/asr_quality.py` đang đo: `NEG = ["đừng", "không", "chưa", "thôi", "khỏi", "hủy", "bỏ"]`.
  - Thiếu biến thể nào (ví dụ "hông", "hổng", "thôi khỏi", "khỏi cần", "à không" khi tự sửa) thì comment trên PR #4.
- [ ] **[Leader] 0.4 Rà model ASR và LLM mới** phát hành từ 06/2026 tới 25/10/2026 (khoảng 30 phút; mục 5).
  - Ghi tên, số tham số, licence, ngày phát hành, revision trên Hugging Face.
  - Nếu có ASR tiếng Việt tốt hơn PhoWhisper, Claude thêm nó vào danh sách `MODELS` của `lifemate/scripts/e2e_baseline.sh`. Lần chạy lại chỉ đo model mới; các bước đã xong được bỏ qua.
- [ ] **[Leader] 0.5 Forum và câu hỏi cho BTC** (khoảng 20 phút; mục 4).
  - Ưu tiên: hướng dẫn Docker; CUDA và driver của máy chấm; giới hạn dung lượng image.
  - 30 giây mỗi mẫu có tính thời gian nạp model không.
  - Chấm có phân biệt chữ hoa/thường không.

  Các câu trả lời này quyết định cách đóng Docker quanh `lifemate/scripts/predict.sh`.
- [ ] **[Leader] 0.6 Review PR #4** (khoảng 30 phút). Đây là phần của leader (ASR, Docker), nên cần đồng ý với 2 giao kèo trước khi đóng Docker:
  - Định dạng file ASR (`lifemate/lifemate/asr.py`).
  - Giao diện biến môi trường của `lifemate/scripts/predict.sh` (`SPLIT`, `DATA`, `ASR_MODEL`, `LLM`, `ADAPTER`, `OUT`).

  Đọc thêm `lifemate/scripts/asr_quality.py` và `lifemate/scripts/check_submission.py`.
- [ ] **[Cả hai] 0.7 Chuẩn bị quyết định nộp public sáng mai** (khoảng 15 phút).
  - Chốt quy tắc dùng 5 lượt nộp mỗi ngày (Q7, mục 8).
  - Ghi trước con số nào sẽ coi là "khớp" với dev nội bộ. Lần nộp đầu dùng để lấy mốc điểm và kiểm các giả định của bộ chấm (Q1, Q8), không phải để leo bảng.
- [x] **[Anh] 0.9 Deep research bằng Codex.** Mở Codex trong thư mục repo trên máy Anh, gõ: *"Đọc và làm đúng theo `docs/CODEX_RESEARCH_PROMPT_2026-10-30.md`."*
  - Prompt cấm Codex đụng git, GPU và job đang chạy.
  - Codex sẽ ghi kết quả vào `docs/research/`. Sáng mai cả đội và Claude đọc, đối chiếu, rồi mới đưa lên `main`.
  - *Xong 30/10, 21:23.* Claude đã kiểm nguồn và kiểm không có dữ liệu thi; Anh đồng ý đưa lên `main` (JOURNAL entry 24). **[Leader]** đọc mục 0, 4 (P0-4, P0-5, P0-7) và 6 của báo cáo.
- [ ] **[Leader] 0.8 (tuỳ chọn, cần GPU)** Chạy Whisper-turbo trên chính các câu vừa nghe, để so bằng tai.
  - RTX 3050 4GB đủ cho turbo fp16 (1,6GB). PhoWhisper-large (3,1GB fp16) có thể không vừa.
  - Lệnh mẫu, với `ids_listen.txt` là danh sách id đã nghe:
    ```bash
    .venv/bin/python -m lifemate.asr --split train --ids ids_listen.txt --batch-size 1 --out asr/train_listen_turbo.jsonl
    ```
  - Lần đầu sẽ tải model 1,6GB.
  - **Chỉ chạy trên train.** Transcript của public_test chỉ được tạo bên trong `predict.sh` để nộp bài, không đem ra nghe, sửa hay dùng làm nhãn.

## 1. Ngay bây giờ (15 phút đầu)

- [x] **[Anh]** Mở terminal, paste lệnh train (lấy ở `JOURNAL.md`, mục "Lệnh chạy train qua đêm"). *Đã chạy 28/10 23:52 → 29/10 02:40, không lỗi (theo log). Không chạy lại.*
  ```bash
  cd ~/"Zalo AI Challenge/lifemate" && mkdir -p runs && { nohup systemd-inhibit --what=sleep:idle:handle-lid-switch --why="LifeMate training" bash scripts/train_local.sh > runs/overnight.log 2>&1 & } && sleep 5 && tail -f runs/overnight.log
  ```
- [ ] **[Anh]** Khoảng 10–15 phút sau, kiểm tra log:
  - Dòng `{"n": 233, ...}` của baseline zero-shot đã xuất hiện.
  - Khi bắt đầu train: `peak_gb` dưới khoảng 6,3 và `tok_s` khoảng 1.400.
  - Ghi `eta_min` (số phút còn lại) vào đây: …
- [ ] **[Anh]** Cắm sạc. Không mở game, video hay ứng dụng nặng GPU, vì VRAM chỉ còn dư khoảng 0,9GB.
- [ ] **[Leader]** Chuẩn bị máy của mình để chạy được code:
  ```bash
  git clone https://github.com/Nguyen-Le-Tuan/ZAIC_2026.git && cd ZAIC_2026 && git checkout agent-pipeline
  mkdir -p data && unzip -q /đường/dẫn/tới/train+public_test.zip -x '__MACOSX/*' -d data   # phải ra data/train+public_test/
  command -v uv || curl -LsSf https://astral.sh/uv/install.sh | sh
  cd lifemate && uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
  ```

## 2. Hiểu bài và hiểu code (khoảng 1 giờ)

- [ ] **[Cả hai]** Đọc `JOURNAL.md` (mục 0–4) và `docs/PIPELINE.md` (mục 1–4).
- [ ] **[Cả hai]** Đọc README gốc của BTC: `data/train+public_test/README.md` và `data/train+public_test/train/zaic_tools/README.md`. **Ghi lại mọi chỗ khác với `JOURNAL.md`**, vì Claude có thể đã hiểu sai.
- [ ] **[Cả hai]** Xem tận mắt prompt mà model nhìn thấy cho mẫu `train_0001`, rồi đối chiếu với lời giải ở `docs/PIPELINE.md` mục 2.4:
  ```bash
  cd lifemate && .venv/bin/python -c "
  from lifemate.data import *; from lifemate.prompt import *
  cat=load_catalog('train'); s=[x for x in load_split('train') if x['id']=='train_0001'][0]
  h=[t['audio_text'] for t in s['history'] if t['role']=='user']
  print(to_chatml(build_messages(s,s['audio_text'],h,catalog_tools(cat),{a['id']:a for a in cat['apps']})))" | less
  ```
- [ ] **[Cả hai]** Tự chạy lại kiểm chứng "phát lại đáp án phải ra 100" (chỉ dùng CPU, khoảng 1 phút):
  ```bash
  cd lifemate && .venv/bin/python -m lifemate.infer --split train --text oracle --backend oracle --out runs/oracle_train.jsonl \
    && .venv/bin/python -m lifemate.scorer runs/oracle_train.jsonl --split train
  ```
- [ ] **[Cả hai]** Review [PR #1](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/1) theo thứ tự `prompt.py` → `agent.py` → `scorer.py` → `sft.py` → `train.py`.
  - Comment trên GitHub mọi chỗ chưa hiểu hoặc nghi là sai.
  - **Mục tiêu:** mỗi người tự giải thích lại được vòng lặp agent bằng lời của mình.
- [ ] **[Cả hai]** Tự kiểm tra lại bằng tay một phát hiện của Claude. Ví dụ đọc 10 mẫu có `contacts.search` để xác nhận "query là tên lưu trong danh bạ, không phải lời người nói" (`JOURNAL.md`, phát hiện 13). Kết luận: đúng / sai / có ngoại lệ: …

## 3. Nghe audio: việc chỉ người làm được (khoảng 1 giờ)

- [ ] **[Cả hai]** Nghe 30 mẫu train ngẫu nhiên và so với `audio_text`.
  - Bước 1, tạo danh sách:
    ```bash
    cd lifemate && .venv/bin/python -c "
    import random; from lifemate.data import *
    random.seed(1); S=load_split('train')
    for s in random.sample(S,30): print(DEFAULT_ROOT/'train'/s['audio'], '|', s['context']['user_profile'].get('city'), '|', s['audio_text'])" > runs/listen_train.txt
    ```
  - Bước 2, nghe lần lượt (bấm Enter để sang mẫu sau):
    ```bash
    cd lifemate && while IFS='|' read -r f city text; do echo "== [$city]$text"; aplay -q "${f% }"; read -rp "   Enter để nghe tiếp " _ </dev/tty; done < runs/listen_train.txt
    ```
  - Ghi vào bảng ghi chú bên dưới. Câu cần trả lời: **`audio_text` là kịch bản người nói đọc theo, hay transcript thật của audio? Người nói có đọc lệch kịch bản không?** Câu trả lời quyết định nhãn dùng để train ASR.
- [ ] **[Cả hai]** Nghe 20 mẫu public để hiểu phân bố. **Chỉ nghe, không ghi transcript, không dùng để train**, vì thể lệ cấm gán nhãn tập test. Ghi lại khác biệt so với train.
  ```bash
  cd lifemate && .venv/bin/python -c "
  import random; from lifemate.data import *
  random.seed(2); S=load_split('public_test')
  for s in random.sample(S,20): print(DEFAULT_ROOT/'public_test'/s['audio'], '|', s['context']['user_profile'].get('city'), '|', ', '.join(s['context']['installed_apps']))" > runs/listen_public.txt
  while IFS='|' read -r f city apps; do echo "== [$city] app:$apps"; aplay -q "${f% }"; read -rp "   Enter để nghe tiếp " _ </dev/tty; done < runs/listen_public.txt
  ```
- [ ] **[Leader]** Từ những gì đã nghe, lập danh sách **"cụm từ nguy hiểm" cho ASR**: số tiền, giờ, ngày, tên người, từ phủ định ("đừng", "thôi khỏi"), tự sửa giữa câu. Đây là đầu vào cho Q9.

**Bảng ghi chú khi nghe** (mỗi mẫu một dòng):

| id | Giọng (Bắc/Trung/Nam) | Giọng nam/nữ, tuổi ước lượng | Nhiễu nền | Cách đọc số, giờ | Từ tiếng Anh | Audio lệch transcript? | Ghi chú |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## 4. Làm việc với BTC và cộng đồng

- [ ] **[Leader]** Đọc forum và kênh hỏi đáp của cuộc thi. Tìm hướng dẫn đóng gói Docker (BTC nói sẽ có tài liệu riêng) và các thông báo thay đổi dữ liệu.
- [ ] **[Leader]** Hỏi BTC những chỗ luật chưa rõ:
  1. Tham số không fuzzy được so khớp có phân biệt chữ hoa/thường và khoảng trắng không? List (ví dụ `params` của `sys.ask_missing_info`) có xét thứ tự không?
  2. "Token" trong token-F1 được tách theo khoảng trắng, hay có bỏ dấu câu trước?
  3. Giới hạn 30 giây mỗi mẫu có tính cả thời gian nạp model lúc khởi động không?
  4. Khi nào có hướng dẫn Docker? Máy chấm dùng phiên bản CUDA và driver nào? Image có giới hạn dung lượng không?
  5. Private test có dùng bản `zaic_tools` và catalog mới, tức là có app mới không?
  6. Mốc "phát hành trước 26/10/2026" tính theo ngày công bố trọng số model hay ngày công bố paper?
- [ ] **[Leader]** Xem bảng xếp hạng public: điểm cao nhất hiện tại, số đội tham gia. Ghi vào đây: …
- [ ] **[Leader]** *Quyết định:* có dùng 1 lượt nộp public hôm nay cho **bài nộp rỗng** không?
  - Mục đích: đo tỉ lệ mẫu ngoài phạm vi của public. Điểm nhận được = 100 × tỉ lệ đó; train là 7,18.
  - Đây là một lần dò để hiểu dữ liệu, không phải để leo bảng xếp hạng.
  - File nộp: `lifemate/runs/public_empty.jsonl` (đã có sẵn trên máy của Anh), hoặc tạo lại bằng:
    ```bash
    cd data/train+public_test && python3 -c "
    import json,sys; sys.path.insert(0,'public_test'); from zaic_tools import ToolEnv
    with open('public_test/public_test.jsonl',encoding='utf-8') as f, open('../../lifemate/runs/public_empty.jsonl','w',encoding='utf-8') as o:
        for l in f:
            i=json.loads(l)['id']; e=ToolEnv('public_test',i,root='.')
            o.write(json.dumps({'id':i,'tool_calls':[],'state_hash':e.get_state_hash()})+'\n')"
    PYTHONPATH=public_test python3 -m zaic_tools --split public_test --root . --validate ../../lifemate/runs/public_empty.jsonl
    ```
  - Kết quả (ghi thêm vào Q6): …
  - *29/10:* handoff của Anh đề xuất **không ưu tiên** nộp bài rỗng trong giai đoạn này (xem Q7). Leader chưa quyết; chưa nộp.

## 5. Chuẩn bị tài nguyên

- [ ] **[Anh hoặc Leader]** Chọn nhà cung cấp GPU cloud, tạo tài khoản và nạp tiền. Claude không làm các việc thanh toán. Cần 2 loại máy:
  - 1 máy A100 hoặc H100 80GB để train.
  - 1 máy 24GB (A30 nếu thuê được, không thì L4 hoặc A10) để đo thời gian giống máy chấm.
- [ ] **[Anh]** Tạo Hugging Face token (quyền read) để tải model nhanh hơn, không bị giới hạn lượt tải.
- [ ] **[Leader]** Rà Hugging Face tìm LLM dưới 5B và ASR tiếng Việt phát hành từ 06/2026 tới 25/10/2026. Kiến thức của Claude dừng ở giữa năm 2026 nên không biết các model này. Ghi tên, số tham số, licence, ngày phát hành.
- [ ] **[Leader]** Lập bảng licence các model ứng viên: Qwen3 (Apache-2.0), Whisper (MIT), PhoWhisper (BSD-3) và các model khác. Đánh dấu model nào dùng licence không thương mại (CC-BY-NC).

## 6. Tổ chức đội

- [ ] **[Cả hai]** Thống nhất quy trình review PR: ai review, trong bao lâu, tiêu chí để merge (ví dụ: kiểm chứng phát lại đáp án vẫn ra 100, điểm dev không giảm).
- [ ] **[Cả hai]** Đặt lịch họp ngắn hằng ngày và chốt mốc đóng băng tính năng (xem Q20).

## 7. Sáng mai, khi train xong

- [x] **[Anh]** Xem 2 file điểm: `lifemate/runs/zs_q17b_fit_random_score.json` (trước khi train) và `lifemate/runs/sft_q17b_fit_random_score.json` (sau khi train). *29/10: Anh đã đọc và dán kết quả vào chat (9,9 → 53,9).*
- [ ] **[Cả hai]** **Tự phân tích lỗi trước khi hỏi Claude.** In 15 mẫu sai, rồi tự phân nhóm nguyên nhân bằng mắt (sai ID, sai giờ, thiếu bước đọc, gọi thừa, hỏi lại sai lúc, gọi tool ở mẫu ngoài phạm vi…). Sau đó mới so với phân tích của Claude.
  ```bash
  cd lifemate && TAG=q17b_fit_random && .venv/bin/python -c "
  import json; from lifemate.data import *
  tag='$TAG'; rows=load_jsonl(f'runs/sft_{tag}_rows.jsonl'); pred={r['id']:r for r in load_jsonl(f'runs/sft_{tag}.jsonl')}
  S={s['id']:s for s in load_split('train')}
  for r in [r for r in rows if r['score']<1][:15]:
      s=S[r['id']]; print('=====',r['id'],r['category'],'| điểm',round(r['score'],2),'| hash đúng' if r['hash_ok'] else '| HASH SAI'); print('  NÓI   :',s['audio_text'])
      for c in s['label']['tool_calls']: print('  ĐÁP ÁN:',json.dumps(c,ensure_ascii=False))
      for c in pred[r['id']]['tool_calls']: print('  MODEL :',json.dumps(c,ensure_ascii=False))
  " | less
  ```
  - *29/10:* Anh đã audit lỗi với Codex hỗ trợ ([`docs/TRAIN_REVIEW_2026-10-29.md`](docs/TRAIN_REVIEW_2026-10-29.md)), Claude đã đối chiếu ([`docs/EVAL_2026-10-29.md`](docs/EVAL_2026-10-29.md)). Chưa ghi nhận việc hai người tự phân loại toàn bộ bằng mắt, nên việc này vẫn để mở.
- [ ] **[Anh]** *(30/10)* Đọc tay 23 mẫu thí nghiệm D trong `lifemate/gen/review_fit_lao.md` (chỉ có trên máy Anh). Đánh dấu `[x]` mẫu hợp lý, ghi lý do mẫu sai. Xem [`docs/EXPERIMENT_D.md`](docs/EXPERIMENT_D.md) mục 6.
  - *31/10: không còn cần.* D bị loại ở giai đoạn 2 ([`docs/D_PHASE2_2026-10-31.md`](docs/D_PHASE2_2026-10-31.md)). Anh quyết bỏ việc này hay vẫn đọc để lưu.
- [ ] **[Anh]** *(30/10)* Quyết có sinh đủ khoảng 230 mẫu D và chạy hai lượt D-lao, D-random hay không (EXPERIMENT_D mục 8).
  - *Cập nhật sau review 30/10:* kế hoạch đã đổi thành 4 giai đoạn có cổng chặn và có đối chứng "nhân bản mẫu hỏi lại thật" ([`docs/REVIEW_D_2026-10-30.md`](docs/REVIEW_D_2026-10-30.md) mục 5). Việc cần quyết bây giờ là **duyệt giai đoạn 1**.
- [ ] **[Anh hoặc Leader]** *(30/10)* Đọc tay 30 nhãn D của giai đoạn 1 (R8 trong review): nhãn có đúng cách BTC sẽ gán không, nhất là các nhãn không có tiền lệ.
  - *Đã sẵn sàng:* `lifemate/gen/review_v1_30.md`, gồm 30 mẫu ngẫu nhiên của D v1 (14 C, 16 B-vague). Đây là cổng còn mở của giai đoạn 1; cần ≥ 27/30 mẫu hợp lý.
- [x] **[Anh]** *(30/10)* Chọn bước tiếp theo của D: giai đoạn 1b rồi giai đoạn 2 có nhánh liều lượng (khuyến nghị), hay giai đoạn 2 ngay ([`docs/D_PHASE1_2026-10-30.md`](docs/D_PHASE1_2026-10-30.md) mục 5).
  - *Anh đã chọn trong chat (30/10):* "Làm giai đoạn 1b". Kết quả ở [`docs/D_PHASE1B_2026-10-30.md`](docs/D_PHASE1B_2026-10-30.md): D-train 77 mẫu; tỉ lệ người viết phải bỏ 27% (C 0%, B-vague 53%), cổng ≤ 15% vẫn không đạt.
- [x] **[Anh]** *(30/10)* Chọn bước tiếp theo sau giai đoạn 1b: giai đoạn 2 ngay với D-train 77 mẫu (khuyến nghị), hay giai đoạn 3 (nới luật để có thêm tool) trước ([`docs/D_PHASE1B_2026-10-30.md`](docs/D_PHASE1B_2026-10-30.md) mục 6). Giai đoạn 2 tốn khoảng 3 × 3,3 giờ GPU trên máy Anh.
  - *Anh đã chọn trong chat (30/10):* "Train giai đoạn 2". Đang chạy từ 18:17 trong unit `lifemate-phase2-d`, dự kiến khoảng 9 giờ.
- [ ] **[Anh]** *(30/10)* Trong khoảng 9 giờ train giai đoạn 2, cộng khoảng 2–2,5 giờ đo đầu-cuối ngay sau đó (tới khoảng 6 giờ sáng 31/10):
  - Giữ máy cắm điện; không gập nắp, vì unit chỉ chặn idle-sleep.
  - Hạn chế mở ứng dụng nặng (ngày 29/10 systemd-oomd đã từng kill app vì thiếu RAM).
  - **Không đổi nhánh git trong thư mục repo, và không commit từ thư mục đó.** Ngày 30/10 lúc 20:03, việc đổi sang `main` rồi đổi lại đã xoá `lifemate/gen/` trên máy. Claude đã khôi phục (JOURNAL entry 21). Muốn sửa tài liệu trên `main` thì dùng một git worktree riêng.
- [x] **[Anh]** *(30/10)* Chọn ưu tiên sau D. *Anh đã chọn trong chat:* "Ưu tiên đầu-cuối", và "Claude làm ASR baseline với 2 model" (Whisper-large-v3-turbo, PhoWhisper-large, không fine-tune). Code ở [PR #4](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/4); lượt đo chạy sau giai đoạn 2 (JOURNAL entry 21).
- [x] **[Anh]** *(30/10)* **Repo đang public.**
  - Commit `1bbd05a` đã đưa `lifemate/gen/` lên `main`. Thư mục này chứa lời nói, nhãn và kết quả tool chép từ train, trong khi README dữ liệu cấm phát tán.
  - Claude đã gỡ khỏi `main` (`4e908be`, Anh chọn "Gỡ khỏi main"), nhưng **bản cũ vẫn xem được trong lịch sử git**.
  - Quyết: chuyển repo sang private (GitHub → Settings → General → Danger Zone → Change visibility), hoặc viết lại lịch sử. Viết lại lịch sử thì leader phải đồng bộ lại.
  - Muốn chia sẻ file `gen/` cho leader thì gửi riêng, không qua repo.
  - *Anh đã chọn trong chat (30/10):* **giữ public**, không viết lại lịch sử.
- [ ] **[Anh]** *(sáng 31/10)* Khi có `docs/E2E_BASELINE_2026-10-31.md`, quyết có nộp `lifemate/runs/e2e_public_<asr>.jsonl` lên public không. File đã qua `check_submission.py`. Anh tự nộp trên trang thi; Claude không nộp. Mục đích: lấy mốc điểm public đầu tiên và kiểm các giả định của bộ chấm local (Q1, Q7, Q8).
- [ ] **[Leader]** *(30/10)* Claude đã dựng bước ASR baseline (`lifemate/asr.py`, PR #4) với 2 model chưa fine-tune.
  - Xem số liệu sáng 31/10: WER; số, tiền, giờ còn giữ được; từ phủ định; query tìm kiếm. Dùng chúng để quyết hướng fine-tune ASR và chuẩn hoá số (Q9, Q12).
  - Thử nhanh 3 câu trên CPU: Whisper-turbo nghe kém ("huỷ lịch" → "bị dịch").
  - `audio_text` viết số bằng chữ nhiều hơn chữ số (1.371 so với 481 câu).
- [ ] **[Leader]** Khi BTC có hướng dẫn Docker: đóng image quanh `lifemate/scripts/predict.sh` (một lệnh offline từ thư mục dữ liệu ra `submission.jsonl` đã kiểm).
- [ ] **[Anh hoặc Leader]** *(30/10)* Đọc tay 24 mẫu mới của giai đoạn 1b trong `lifemate/gen/review_1b.md` (chỉ có trên máy Anh). Chú ý: 7/8 câu B-vague được viết bằng cách bỏ hẳn người nhận, và 3 mẫu `banking.transfer.amount` không có tiền lệ hỏi thật.
  - *31/10: không còn cần.* D bị loại ở giai đoạn 2 ([`docs/D_PHASE2_2026-10-31.md`](docs/D_PHASE2_2026-10-31.md)). Anh quyết bỏ việc này hay vẫn đọc để lưu.
- [ ] **[Anh]** *(30/10)* Giữ nguyên các file `lifemate/gen/*_fit_lao.jsonl`, `lifemate/gen/*_v1*` và `lifemate/gen/*_1b*` (mốc so sánh, hash ghi trong `docs/baselines/`). Không xoá, không train trên nguồn của CS-pilot-23 hay D-eval-24.
  - *Ghi chú 30/10:* D-eval-24 có 1 mẫu rò rỉ nhãn (`train_1140#d1`). Tập vẫn giữ nguyên để so được với mốc; báo cáo kèm kết quả trên D-eval-23 (bỏ mẫu này).
- [x] **[Anh]** Mở chat với Claude: *29/10, kèm [`docs/CLAUDE_HANDOFF_2026-10-29.md`](docs/CLAUDE_HANDOFF_2026-10-29.md).* *"Đọc `JOURNAL.md`, `docs/PIPELINE.md` và `HUMAN_TODO.md`. Đây là kết quả train và câu trả lời của đội…"*

---

## 8. Hai mươi câu hỏi nghiên cứu

Chép từ [`docs/PIPELINE.md`](docs/PIPELINE.md) mục 5. **Ghi câu trả lời ở đây**, không ghi bên `PIPELINE.md`, để chỉ có một nơi lưu câu trả lời. Người phụ trách chỉ là gợi ý; ai có ý tưởng thì cứ viết thêm.

Ngày 29/10 đã điền câu trả lời làm việc, lấy từ handoff của Anh (soạn với Codex hỗ trợ). Mỗi câu ghi một trong bốn trạng thái: **đã xác minh**, **giả thuyết**, **chưa đo**, **chờ BTC**. Chưa câu nào được đánh dấu xong, vì có câu trả lời làm việc không có nghĩa là câu hỏi nghiên cứu đã giải quyết.

### A. Hiểu thước đo và chính sách sinh nhãn

- [ ] **[Leader]** **Q1. Server so khớp tham số không fuzzy thế nào: có phân biệt chữ hoa không, có gộp khoảng trắng không, list có xét thứ tự không?**
  - *Vì sao:* quyết định có cần viết hoa query, sắp xếp list `params` của `ask_missing` hay không.
  - *Gợi ý:* thiết kế 1–2 lần nộp public **dùng để dò thước đo**, không phải để tối ưu. Ví dụ nộp cùng một bài nhưng viết thường toàn bộ query của call đọc, rồi so điểm.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chờ BTC.**
    - Theo thể lệ: tham số non-fuzzy phải giống hệt; fuzzy được hạ chữ thường và chuẩn hoá NFC rồi so token-F1 > 0,6. Mặc định giữ so khớp chính xác, không tự hạ chữ thường hay gộp khoảng trắng.
    - Chưa rõ: cách tách token và xử lý dấu câu của fuzzy; tham số tuỳ chọn để trống so với ghi rõ giá trị mặc định (ví dụ `train_1474` thêm `days: "daily"` nên bộ chấm local cho 0 điểm dù hash đúng); thứ tự phần tử trong list.
    - Ưu tiên hỏi BTC; không coi điểm public là xác nhận.
- [ ] **[Cả hai]** **Q2. BTC sinh đáp án như thế nào: bằng template, bằng LLM, hay bằng một simulator chạy chính sách cố định? Tìm thêm dấu vết** (ngoài chuyện query dùng tên trong danh bạ).
  - *Vì sao:* biết cách nhãn được sinh thì tái tạo được chính sách cho app mới.
  - *Gợi ý:* so sánh nhiều mẫu cùng kiểu yêu cầu; xem tham số fuzzy được viết theo văn phong nào; xem thứ tự các call.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết.**
    - Nhãn có nhiều quy luật, nhưng chưa biết sinh bằng template, LLM hay pipeline kết hợp.
    - **Đã xác minh (Claude đo 29/10):** id của train đi theo từng lô có đặc điểm khác nhau. Lô id 1501+ có trung bình 7,0 lượt user trong history (96% mẫu có history). Lô id 1–300 có 12,2 app cài và 3,1 call đáp án mỗi mẫu. Các lô khác khoảng 8–9 app và khoảng 2 call.
    - Hướng làm: phân tích quy ước theo lô và nhóm trên fit; không ép một luật cho mọi lô.
- [ ] **[Cả hai]** **Q3. Viết thành luật: khi nào đáp án gọi call đọc trước lệnh ghi, khi nào đọc kèm bộ lọc, khi nào bỏ qua bước đọc?**
  - *Vì sao:* call đọc chiếm phần lớn F1, và luật tổng quát dùng được cho app mới.
  - *Gợi ý:* thống kê theo từng cặp (call đọc, lệnh ghi); đã biết 113/126 lần bật đèn có `get_status` trước, và 11 lần còn lại đều do đã có trong history.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết.**
    - Nguyên tắc làm việc: đọc khi thiếu đối tượng, thuộc tính hoặc điều kiện; dùng lại thông tin trong history nếu còn hiệu lực; theo dõi thay đổi sau mỗi lệnh ghi.
    - Tách hai mục tiêu: đủ thông tin để thực thi đúng, và khớp quy ước call của đáp án.
    - Cần thống kê các ngoại lệ (đọc có bộ lọc so với đọc `{}`) trên fit.
- [ ] **[Cả hai]** **Q4. Ranh giới giữa hỏi lại, tự quyết và bỏ qua: các "tín hiệu" nào dẫn tới `ask_missing_info`?**
  - *Vì sao:* 14% mẫu là hỏi lại, và danh sách `params` phải khớp chính xác.
  - *Gợi ý:* đọc 217 mẫu hỏi lại, phân nhóm: trùng tên, thiếu giờ, thiếu số tiền, yêu cầu mơ hồ ("hạ xuống chút")… Rút ra danh sách kiểm tra.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết (nguyên tắc); đã xác minh (quy mô lỗi trên dev_random).**
    - Nguyên tắc: chỉ hỏi khi thông tin bắt buộc không tra được hoặc đối tượng còn mơ hồ. Với x-one-of, có số điện thoại thì không cần `contact_id`. Tôn trọng lời tự sửa cuối cùng của người dùng.
    - **Claude đo (29/10):** 14 mẫu execute bị hỏi thừa và 16 mẫu cần hỏi lại không hỏi, tổng 30 mẫu, mất 12,7 điểm. Đây là nhóm hành vi mất điểm lớn nhất; 22/30 mẫu nằm ngoài nhóm 51.
    - Hướng làm: cặp mẫu gần giống nhau (đủ/thiếu slot, một/nhiều đối tượng) sinh từ fit. Đo riêng hỏi thừa, bỏ hỏi và sai `params`.
    - **Thêm 30/10 (đã xác minh, [EXPERIMENT_D](docs/EXPERIMENT_D.md) mục 2–3):**
      - Nhãn hỏi lại có 3 kiểu: A trùng tên khi tra cứu, B chọn mơ hồ ID, C thiếu slot.
      - Model đã làm tốt kiểu A; bỏ hỏi chủ yếu ở B và C, nhất là với tool mới.
- [ ] **[Cả hai]** **Q5. Phân loại 111 mẫu ngoài phạm vi theo nguyên nhân. Có mẫu "làm được một phần" không, và đáp án xử lý ra sao?**
  - *Vì sao:* gọi dù chỉ một call ở mẫu ngoài phạm vi là mất trắng; còn yêu cầu nhiều ý mà chỉ một ý làm được thì cách xử lý chưa rõ.
  - *Gợi ý:* lọc các mẫu có nhiều ý định mà thiếu một app; xem đáp án làm phần còn lại hay trả `[]`.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chưa đo.**
    - Đã biết 111 mẫu gồm thiếu app, huỷ hoặc phủ định, trò chuyện, và thông tin đã có sẵn.
    - Chưa phân loại đủ 111 mẫu, chưa rõ chính sách khi yêu cầu chỉ làm được một phần.
    - Không suy luật từ từ khoá (ví dụ có chữ "thôi" thì trả rỗng).

### B. Tổng quát hoá và tín hiệu đánh giá

- [ ] **[Cả hai]** **Q6. Private test có thể khác public ở những điểm nào** (app mới, phân bố loại mẫu, giọng nói, độ dài history)? **Bộ dev nào mô phỏng private tốt nhất?** Leave-apps-out đã đủ chưa, hay cần leave-groups-out?
  - *Gợi ý:* so phân bố của public với train (app đã cài, độ dài history, thành phố); đặt giả định "xấu nhất hợp lý".
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết.**
    - Rủi ro chính: app/schema mới, history dài, giọng nói, thứ tự entity, tổ hợp tác vụ.
    - Tập đo: dev_random đo tiến bộ trong cùng miền; fit_lao → dev_lao đo app chưa thấy (chưa chạy).
    - **Claude đo (29/10):** điểm giảm theo lô id (68 → 35) và theo history (59,8 khi không có history → 33,1 khi từ 6 lượt). Từ nay báo điểm kèm lát cắt.
    - Vì dev_random đã bị phân tích kỹ, nên giữ riêng một tập kiểm tra kín (lockbox). Xem [docs/EVAL_2026-10-29.md](docs/EVAL_2026-10-29.md).
    - **Thí nghiệm B (chiều 29/10):**
      - fit_lao → dev_lao đạt 35,53 điểm (zero-shot 10,88).
      - Trong cùng các mẫu, lời gọi thực hiện vào app mới không kém app đã thấy, nhưng hỏi lại về tool mới được 0/23.
      - Lockbox chỉ dùng được cho model train lại từ model gốc, theo review của Codex.
      - Chi tiết ở EVAL mục 7.
- [ ] **[Leader]** **Q7. Dùng 5 lần nộp public mỗi ngày vào việc gì để không overfit?** Đặt quy tắc cho đội, ví dụ "chỉ nộp khi dev nội bộ tăng ít nhất X điểm" hoặc "dành một lần nộp mỗi ngày để dò thước đo hoặc đo ASR".
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết (đề xuất của Anh; leader chưa chốt).**
    - Coi public là kiểm tra tích hợp. Chỉ nộp khi có candidate rõ checkpoint, config và mục đích đo; ghi lịch sử nộp.
    - Không dùng bài nộp rỗng để dò phân bố trong giai đoạn này; hỏi BTC về metric.
- [ ] **[Cả hai]** **Q8. Nếu điểm dev nội bộ và điểm public lệch nhau, những nguyên nhân nào có thể giải thích, và kiểm tra từng nguyên nhân thế nào?** Ví dụ: ASR thật so với text chuẩn, app mới, khác biệt của bộ chấm, phiên bản `zaic_tools`.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chưa đo.**
    - Nguồn có thể gây lệch: ASR, schema mới, tỉ lệ loại tác vụ, history, bộ chấm, runtime, phiên bản `zaic_tools`.
    - Cách đo trên phần train giữ riêng: so oracle với ASR trên cùng agent; seen với unseen app theo đúng protocol; timeout và lỗi parse.

### C. ASR

- [ ] **[Leader]** **Q9. Lỗi ASR nào thực sự làm mất điểm? Định nghĩa "tỉ lệ lỗi slot" thay cho WER thế nào?**
  - *Gợi ý:* từ bảng ở mục 3.2, lấy các tham số của lệnh ghi có nguồn là ngày giờ hoặc số, tìm cụm từ tương ứng trong `audio_text` (ví dụ "muộn 1 tiếng", "hai triệu tám"), rồi đo ASR nghe đúng các cụm đó bao nhiêu phần trăm. Đừng quên từ phủ định: "đừng", "thôi khỏi".
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chưa đo** (chưa có báo cáo nghe audio hay benchmark ASR).
    - Ngoài WER, đo độ đúng theo loại thông tin: số tiền, số điện thoại, ngày giờ, khoảng thời gian, tên, phủ định, điều kiện, tự sửa. Báo cả tỉ lệ câu đúng toàn bộ thông tin quan trọng.
    - Đo chênh lệch điểm agent giữa oracle và ASR theo cặp.
- [ ] **[Leader]** **Q10. Có dùng được ngữ cảnh hợp lệ để sửa ASR không?** Ví dụ tên app đã cài, enum trong schema, tên kênh, và sau khi agent đọc danh bạ thì sửa lại tên người.
  - *Lưu ý:* chỉ được dùng dữ liệu lấy qua tool, không được đọc `state.json`.
  - *Gợi ý:* Whisper có `initial_prompt` hoặc hotword; hoặc sửa ở lớp sau, khi so khớp với kết quả tool.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết, chưa đo.**
    - Dùng profile, thời gian, installed_apps, schema và history. Entity chỉ biết sau một lần gọi tool thì chỉ dùng sau khi tool đó trả về.
    - Giữ transcript gốc để debug; đo số câu được sửa đúng và số câu bị làm hỏng.
    - Nếu dùng model sửa riêng lúc inference, model đó tính vào giới hạn tham số và thời gian.
- [ ] **[Leader]** **Q11. Lượt user trong history có cần ASR chất lượng cao không, hay model nhỏ, nhanh là đủ?**
  - *Gợi ý:* trên train, thay transcript history bằng ASR kém hơn (hoặc cố tình làm nhiễu) rồi đo điểm agent giảm bao nhiêu.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chưa đo.**
    - Thí nghiệm 2×2: lượt cuối và history, mỗi phần dùng oracle hoặc ASR; cùng checkpoint, cùng mẫu.
- [ ] **[Leader]** **Q12. Chuẩn hoá chữ thành số đặt ở đâu: ASR xuất thẳng chữ số, một bộ quy tắc riêng, hay để LLM tự hiểu?**
  - *Vì sao:* 11% tham số của lệnh ghi là số phải tính.
  - *Gợi ý:* thử cả 3 cách trên các mẫu có `amount`, `time`, `phone`.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chưa đo.**
    - Đề xuất: ASR giữ nguyên lời nói; một bộ phân tích có kiểu xử lý số tiền, điện thoại, khoảng thời gian, giờ. LLM chọn ý định, mốc và phép toán; code tính kết quả.
    - So ba cách (raw ASR, ASR + ITN, để LLM tự xử lý) trên cùng tập dev.

### D. Agent và mô hình

- [ ] **[Anh]** **Q13. Phần nào nên chuyển từ LLM sang code tất định, và mỗi phần cứu được bao nhiêu điểm?**
  - *Gợi ý:* dùng mục 3.2 làm khung; với từng nhóm (ngày giờ, số, ID, quy ước call đọc), ước lượng số mẫu bị ảnh hưởng × xác suất LLM làm sai.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết (chưa có ablation).**
    - Ưu tiên thử: tính ngày giờ, số học và so sánh có kiểu; validate; enum và nguồn gốc ID; theo dõi việc còn dở; xử lý `done=false`; phục hồi lỗi JSON.
    - **Claude đo (29/10), đây là trần trên dev_random, không phải điểm cứu chắc chắn:**
      - `done=false` chỉ xuất hiện ở 7/233 rollout, tối đa khoảng 3,0 điểm.
      - Lỗi JSON/schema có ở 5 trace, 1 trace tự sửa được.
      - Nhóm số/giờ 15 mẫu, tối đa 6,4 điểm; nhóm điều kiện 11 mẫu, tối đa 4,7 điểm.
    - **Thêm 30/10:** luật tất định "ID lấy từ lần tra ≥ 2 mục trùng tên thì hỏi lại" không báo nhầm lần nào trên fit, nhưng phát lại trên rollout chỉ kích hoạt 0–1 mẫu, nên không đưa vào agent ([EXPERIMENT_D](docs/EXPERIMENT_D.md) mục 4).
- [ ] **[Anh]** **Q14. Có nên ép model chỉ được sinh ID đã xuất hiện trong kết quả tool hoặc history, và chỉ sinh enum hợp lệ** (constrained decoding)? Rủi ro là gì?
  - *Ví dụ rủi ro:* chặn nhầm ID hợp lệ được tạo trong lượt; làm chậm suy luận.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết.**
    - Enum theo schema. ID theo x-ref và dữ liệu đã thấy còn hiệu lực, kể cả ID vừa tạo trong lượt.
    - Ràng buộc này không đủ: `train_1511` chọn một ID có thật nhưng sai xe.
    - So hậu kiểm với constrained decoding trước khi áp dụng rộng.
- [ ] **[Anh]** **Q15. Đánh đổi giữa model 4B và 1.7B, LoRA và full fine-tune, có thêm một dòng "kế hoạch ngắn" trước khi gọi tool hay không — trong giới hạn 30 giây và 16K token. Thí nghiệm nào trả lời rẻ nhất?**
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: đã xác minh (checkpoint 1.7B); giả thuyết (4B, full fine-tune, kế hoạch ngắn).**
    - **Claude đo (29/10) trên đủ 233 mẫu dev:** step_100 38,95 → step_200 52,47 → final 53,92. Final và step_200 không phân biệt được.
    - Final đạt 80,2 trên 233 mẫu đã train so với 53,9 trên dev.
    - Thí nghiệm kế tiếp (A: 2 epoch; E: 4B cùng protocol) ở [docs/EVAL_2026-10-29.md](docs/EVAL_2026-10-29.md) mục 5. Chưa ưu tiên full fine-tune hay RL.
- [ ] **[Anh]** **Q16. vLLM có cho kết quả giống hệt nhau qua 5 lần chạy không (greedy, batch 1, cùng GPU)? Nếu không, khử khác biệt bằng cách nào?**
  - *Vì sao:* nếu lần chạy lại của BTC khác kết quả đã nộp, họ lấy trung bình 5 lần, có thể tụt điểm.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chưa đo (vLLM, A30, có ASR); đã xác minh (HF greedy trên RTX 4070, chỉ agent).**
    - **Claude đo (29/10):** chạy lại checkpoint final cho cùng lời gọi, cùng hash và cùng output thô ở 233/233 mẫu.
    - Chưa chứng minh tái lập với vLLM, trên A30, hay khi có ASR. Vẫn cần 5 lần chạy trên môi trường triển khai.

### E. Dữ liệu

- [ ] **[Anh]** **Q17. Làm sao để dữ liệu tổng hợp tuân theo chính sách của BTC chứ không theo "thói quen" của LLM sinh dữ liệu? Kiểm chứng độ "giống thật" ra sao?**
  - *Gợi ý:* (a) chỉ train trên dữ liệu tổng hợp rồi đo trên train thật; (b) huấn luyện một bộ phân loại thật/giả; (c) so phân bố số call, tỉ lệ hỏi lại, tỉ lệ ngoài phạm vi.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết.**
    - Ưu tiên dữ liệu phản thực tế sinh từ fit: đổi số dư quanh ngưỡng, giờ, entity/ID, thứ tự danh sách, lời tự sửa, đủ/thiếu slot. Sinh lại nhãn rồi kiểm bằng thực thi.
    - Cần thêm: kiểm tra theo chính sách (đọc, hỏi, tham số tuỳ chọn, văn phong fuzzy); ablation chỉ dữ liệu thật so với thật + tổng hợp; kiểm trên tập giữ riêng chưa dùng để sinh nhãn.
    - Không đọc file environment của BTC để làm fixture.
    - **Thêm 30/10:** bộ sinh cặp đủ/thiếu từ fit đã có ([PR #3](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/3)).
      - Mọi nhãn phát lại qua ToolEnv; câu qua 7 kiểm tra; loại nguồn từ dev.
      - Chạy thử ra 23 mẫu; chưa có người đọc tay, chưa train.
- [ ] **[Anh]** **Q18. Đa dạng hoá ngôn ngữ nói thế nào và theo tỉ lệ bao nhiêu?** Gồm phương ngữ, tự sửa giữa câu ("5 giờ, à không, 5 rưỡi"), phủ định, nhiều ý định trong một câu, từ tiếng Anh xen vào. Cần TTS cho ASR hay chỉ cần text cho LLM?
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết.**
    - Paraphrase từ fit: phủ định, tự sửa, tham chiếu history, nhiều ý trong một câu, phương ngữ, từ tiếng Anh xen vào.
    - Thử vài mức trộn định trước và báo learning curve. Chỉ dùng TTS nếu thí nghiệm ASR cho thấy cần.
    - Đội chưa nghe audio để xác nhận audio khớp kịch bản.
    - **Thêm 30/10 (việc của Leader):** Anh gợi ý VieNeu (TTS tiếng Việt, https://www.vieneu.io/) để tạo audio tăng cường cho ASR. Trang chưa ghi licence, kích thước model hay khả năng chạy offline; cần kiểm theo thể lệ (ngày phát hành, licence, chỉ dùng lúc phát triển) trước khi dùng.

### F. Kỹ thuật và quản trị rủi ro

- [ ] **[Leader]** **Q19. Liệt kê các kịch bản khiến bài nộp private về 0 hoặc mất nhiều điểm, và cách phòng cho từng kịch bản.**
  - *Ví dụ:* Docker cố tải model khi không có mạng; dùng sai bản `zaic_tools`; tràn bộ nhớ ở mẫu dài; quá 30 giây; đường dẫn `/data` sai; mã hoá UTF-8.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết (danh sách kiểm tra); chờ BTC (hướng dẫn Docker; cold-start có tính vào 30 giây không).**
    - Cần kiểm: model và tokenizer có sẵn offline, đúng phiên bản `zaic_tools`, entrypoint, đủ mẫu, UTF-8, một ToolEnv mỗi mẫu, tổng tham số, latency toàn pipeline (p50/p95/max), tính tái lập, checksum.
    - `time_budget` của agent hiện chỉ kiểm giữa các vòng, chưa chặn một lần generate chạy quá hạn.
- [ ] **[Cả hai]** **Q20. Trong 19 ngày còn lại, đâu là đường găng (critical path)? Việc nào hai người làm song song được? Mốc "đóng băng tính năng" đặt ở ngày nào?**
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết (lịch đề xuất, chưa họp chốt).**
    - 29–31/10: audit, sửa đánh giá, chọn checkpoint, baseline ASR, Docker smoke test.
    - 01–05/11: ablation, fit_lao, cấu hình lớn hơn.
    - 06–10/11: tích hợp ASR, đánh giá end-to-end.
    - 11–13/11: đóng băng tính năng.
    - 14–15/11: hoàn thiện, nộp sớm.
    - 16/11: dự phòng.
    - 20–23/11: chạy bản đã đóng băng trên private.
