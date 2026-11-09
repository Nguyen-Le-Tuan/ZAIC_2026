# Lấy lại gốc: ZAIC 2026 LifeMate

*Viết ngày 08/11/2026 cho người đã để Claude tự chạy lâu ngày và muốn tự nắm lại repo. Mọi số liệu lấy từ `JOURNAL.md` trên `origin/main` (tới entry 110), `HUMAN_TODO.md` và báo cáo `docs/research/CODEX_4B_STRATEGY_2026-11-04.md`, cộng vài phép đo Claude chạy lại trên máy này (ghi rõ chỗ nào).*

---

## 0. Tóm tắt trong 1 phút

- **Bài toán:** câu nói tiếng Việt → chuỗi lời gọi tool. Hệ thống hiện tại có hai tầng: **ASR** (PhoWhisper-large fine-tune) → **agent** (Qwen3-4B-Instruct + LoRA, nạp 4-bit) chạy vòng lặp gọi tool.
- **Điểm public tốt nhất: 51,16** (05/11). Bản thử bằng đúng cấu hình nộp cuối: 51,07 (08/11). Cùng pipeline mà thay agent bằng model API mạnh thì được 75,52. Top cột SLM lúc 04/11 là 96,66.
- **Từ 05/11 tới giờ, 5 lần thử cải tiến đều không qua luật giữ/bỏ.** Đội đã quyết đóng gói bản 05/11 và dồn sức cho Docker.
- **Hạn Docker là 16/11, 23:59 giờ Việt Nam** (11:59 trưa 16/11 giờ máy EST). Sau hạn này model bị đóng băng, vì BTC chạy chính image đó trên private test (20–23/11). **Còn 8 ngày.**
- **Chẩn đoán chính của tài liệu này (mục 6):** đội không kẹt vì thiếu công suất train. Có ba lý do: (1) độ nhiễu giữa các lần train (2–4 điểm) lớn hơn hiệu ứng của mọi thí nghiệm đã thử; (2) model học thuộc quy ước của từng app thay vì học chính sách chung, trong khi 65% mẫu public dùng app chưa thấy; (3) câu hỏi then chốt "BTC sinh nhãn bằng luật gì" chưa ai trả lời. Hướng có đòn bẩy lớn nhất làm được trên CPU, ngay trên máy này.

---

## 1. Branch nào là mới nhất?

### 1.1 Câu trả lời ngắn

| Câu hỏi | Branch | Ngày |
|---|---|---|
| Cập nhật gần nhất (tài liệu) | `origin/main` | 20:54 ngày 08/11 (Journal 110) |
| Code của bản nộp 51,16 | `q4b-laptop` (= `docker-ready`) | 03/11 |
| **Code giao diện nộp BTC (cần cho L9)** | **`docker-submit`** ([PR #15](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/15), chưa merge) | 06/11 |
| Code mới nhất nói chung | `synth-v2` (hướng dữ liệu sinh, **đã dừng** ngày 08/11) | 06/11 |

**Đừng tin ngày commit của các nhánh khác.** Mỗi lần Claude sửa tài liệu trên `main`, nó tự merge `main` vào **cả 13 nhánh** cùng một phút. Vì vậy nhánh nào trông cũng như vừa sửa lúc 20:54 ngày 08/11. Muốn biết code thật sự đổi lúc nào, xem commit riêng của nhánh (không tính merge):

```bash
git log -1 --no-merges --format='%ci %h %s' origin/main..origin/docker-submit
```

### 1.2 Cây nhánh (code xếp chồng, chưa bao giờ vào `main`)

```
main  ← chỉ có tài liệu + code PR #1 (baseline 1.7B). Các PR sau chưa merge.

agent-pipeline (30/10: bộ chấm, prompt, vòng lặp agent, SFT, train)
 └─ eval-protocol = exp-d (30/10)
     └─ e2e-baseline (30/10: bước ASR, predict.sh)
         └─ id-guard-check (31/10)
             └─ cloud-train (31/10)
                 └─ asr-finetune (31/10: fine-tune Whisper bằng LoRA)
                     └─ time-budget (31/10: hạn giờ mỗi mẫu, chốt chặn ID)
                         ├─ synth-data (02/11) ─ synth-v2 (06/11)    ← dữ liệu sinh, ĐÃ DỪNG
                         └─ q4b-laptop = docker-ready (03/11)        ← CODE BẢN 51,16
                              ├─ api-agent (04/11, PR #13: bản API tham khảo)
                              ├─ prompt-xref (04/11, PR #14 đã đóng)
                              ├─ docker-submit (06/11, PR #15)       ← GIAO DIỆN NỘP BTC
                              └─ codex/docker-phoft (CHỈ CÓ Ở MÁY NÀY) + Dockerfile chưa commit
```

Mỗi nhánh con chứa toàn bộ code của nhánh cha. Ví dụ `docker-submit` có đủ code của `q4b-laptop`, cộng thêm `lifemate/docker/`, `submit.py` và `seeding.py`.

### 1.3 Máy này đang ở đâu

- Nhánh hiện tại: `codex/docker-phoft` = `q4b-laptop` + các file **chưa commit**: `lifemate/Dockerfile`, `lifemate/.dockerignore`, `docs/DOCKER_PHOFT_SOLUTION.md`, `docker_handoff_2026-11-06.txt`, ảnh chụp Drive, sửa `.gitignore`.
- `main` local **chậm 23 commit** so với `origin/main`. Vì vậy `HUMAN_TODO.md` và `JOURNAL.md` trong thư mục làm việc là bản 05/11, đã cũ.
- Máy này có dữ liệu (`data/train+public_test/`), checkpoint (`lifemate/ckpt/asr_phoft`, `q4b4_all`) và file image 12,6 GB. **Không có `.venv`.** Python hệ thống (3.14) vẫn chạy được bộ chấm và phần dựng prompt, vì hai phần này chỉ dùng thư viện chuẩn (mục 7).

Đọc tài liệu mới nhất mà không phải đổi nhánh hay đụng vào file chưa commit:

```bash
git show origin/main:HUMAN_TODO.md | less
```

Muốn có một bản code giao diện nộp bài ở thư mục riêng, không ảnh hưởng thư mục hiện tại:

```bash
git worktree add ../zaic-docker-submit origin/docker-submit
```

---

## 2. HUMAN_TODO còn phải làm gì?

File có khoảng 60 ô `[ ]` chưa đánh dấu, nhưng **phần lớn đã lỗi thời** (việc của 28–31/10). Lọc lại thì còn:

### 2.1 Đường găng (không làm thì mất bài)

| Việc | Ai | Trạng thái thật | Việc cụ thể |
|---|---|---|---|
| **L9. Gói nộp cuối theo hướng dẫn BTC** | **Leader** | Code ở PR #15 đã có (`/code/predict.sh`, notebook, `start_jupyter.sh`, trường `time`, seed), test CPU đạt. **Chưa chạy trên GPU, chưa merge.** `lifemate/Dockerfile` ở máy này vẫn dùng `python:3.12-slim`. | 9 mục ở cuối `docs/BTC_DOCKER_GUIDE_2026-11-06.md`. Quan trọng nhất: base image CUDA 13.2 có torch build cho `sm_120` (**máy chấm giờ là RTX 5090 32 GB**, không còn là A30); `/data` chỉ đọc → `/result/submission.jsonl`; notebook ra cùng điểm với `predict.sh`; `README.md` và `training_code/`; `docker save \| gzip`, md5, Drive "Anyone with the link". Tối đa 2 lần nộp, BTC lấy lần cuối. |
| **B28/B31. Chạy thử image trên laptop RTX 4070** | Anh | Đã vào nhóm `docker`, **còn phải đăng xuất rồi đăng nhập lại**, sau đó nhắn Claude "chạy B28". | Kết quả cần có: `"ok": true`, thời gian mỗi mẫu, số dòng khác nhau giữa hai lần chạy, số dòng khác file 51,16. |
| **B34. Khoá thư mục Drive** | Anh | Thư mục Drive `ZAIC_2026` **đang mở cho bất kỳ ai có link** và chứa dữ liệu thi có licence. | Chuyển sang "Hạn chế", xoá hai gói `zac_cloud_bundle_*`, nhờ anh trai xoá dữ liệu trên máy. **Rủi ro vi phạm thể lệ**, nên làm ngay hôm nay. |
| **Quyết định chung cho mục 6 của L9** | Cả hai | Chưa quyết | BTC đòi URL dữ liệu train và model. Dữ liệu là của BTC (cấm phát tán), còn `gen/` sinh từ train. Phải quyết đưa gì lên Hugging Face. |

### 2.2 Đã xong nhưng chưa đánh dấu

- **B30** (cài Docker và NVIDIA toolkit, tải image): xong lúc 09:47 ngày 06/11 (entry 100).
- **B26** (đổi ASR trong Docker sang PhoWhisper-ft): phần build đã xong, chỉ còn chờ B28.

### 2.3 Lỗi thời, bỏ qua được

B1, B3, B5, B6, B7, L5, L6, L7, C5 và toàn bộ mục 0–7 (việc ngày 28–31/10). Chuỗi review PR (#8 → #4 → …) chưa ai làm, nên `main` không có code mới. **Sau khi nộp Docker** nên merge chuỗi `docker-submit` vào `main` để repo dễ hiểu lại.

### 2.4 Phần đáng giá nhất của file: mục 8, "Hai mươi câu hỏi nghiên cứu"

**Q1–Q20 chưa câu nào có người trả lời.** Đó lại chính là bản đồ để bạn tự nghiên cứu. Mục 8 dưới đây nói nên bắt đầu từ câu nào: Q2, Q3, Q4, Q9, Q13.

---

## 3. Kiến thức nền tối thiểu

Mỗi khái niệm dưới đây gắn với chỗ nó xuất hiện trong repo. Đọc theo thứ tự.

### 3.1 Bài toán và dữ liệu

- **Đầu vào mỗi mẫu:** audio lượt nói cuối; `context` (giờ hiện tại, hồ sơ người dùng, `installed_apps` kèm danh sách tool); `history` (các lượt trước: lượt user chỉ có audio, lượt assistant có `tool_calls` và `tool_results`).
- **Đầu ra:** danh sách `tool_calls` và `state_hash` (băm trạng thái môi trường sau khi gọi).
- **Môi trường giả lập** `zaic_tools.ToolEnv`: mỗi mẫu một môi trường. Agent chỉ được đọc và ghi qua tool, **cấm đọc thư mục `*_environment/`**.
- **3 kiểu hành vi:** thực thi (79% train); hỏi lại bằng `sys.ask_missing_info` (14%, luôn là call cuối); ngoài phạm vi → `[]` (7%).
- **Train:** 1.545 mẫu, 46 app. **Public:** 634 mẫu, 36 app, trong đó **11 app không có trong train**, và 410/634 mẫu có cài ít nhất một app mới.

### 3.2 Thước đo: hiểu sai thước đo là tối ưu sai

```
gold rỗng           → 1 nếu nộp rỗng, ngược lại 0
hash sai            → 0
còn lại             → F1 giữa call nộp và call đáp án
```

Code ở [`scorer.py:44-94`](../lifemate/lifemate/scorer.py). Hai hệ quả:

1. **Hash là cổng được-hoặc-mất.** Một lệnh ghi sai tham số, thiếu hoặc thừa một lệnh ghi là cả mẫu về 0. Call đọc không đổi hash nhưng vẫn tính vào F1.
2. **Điểm ≈ (tỉ lệ hash đúng) × (F1 trung bình khi hash đúng).** Với 4B, chữ chuẩn, dev_random: hash đúng 73,0% → điểm 65,61, tức F1 khi hash đúng khoảng 0,90. **Phần lớn điểm mất ở hash (trạng thái cuối), không phải ở F1.** Muốn đạt 80 thì cần khoảng 87% hash đúng với F1 khoảng 0,92.

Quy ước của đáp án được chấm rất chặt, ví dụ `smart_home.get_status` gọi với `{}` ở 93/107 lần, và `light_set` có `get_status` đứng trước ở 113/126 lần (JOURNAL mục 3). Model phải bắt chước đúng các quy ước này thì mới được điểm F1.

### 3.3 ASR (nhận dạng tiếng nói)

- **Whisper** là model encoder–decoder: encoder đọc phổ âm thanh (log-mel), decoder sinh chữ từng token. PhoWhisper là Whisper do VinAI fine-tune cho tiếng Việt.
- **WER (tỉ lệ lỗi từ)** = (số từ thay + xoá + chèn) / số từ đúng. Code: [`asr_train.py:82`](../lifemate/lifemate/asr_train.py).
- **Fine-tune bằng LoRA rồi merge:** học trên khoảng 5.000 câu nói của train (6,8 giờ audio), sau đó cộng trọng số LoRA vào model gốc (`ckpt/asr_phoft/merged`).
- **Trong repo:** [`asr.py`](../lifemate/lifemate/asr.py) (chạy ASR cho mọi file wav), [`asr_train.py`](../lifemate/lifemate/asr_train.py) (fine-tune), [`vinum.py`](../lifemate/lifemate/vinum.py) (các cách đọc số tiếng Việt, dùng để phân tích lỗi).
- **Điều cần nhớ:** WER không đo đúng thứ làm mất điểm. Một lỗi ở tên người, số tiền hay giờ có thể làm sai cả hash, trong khi lỗi ở từ đệm thì không sao (Q9).

### 3.4 LLM agent và gọi tool (function calling)

- **ChatML:** định dạng hội thoại của Qwen: `<|im_start|>role\n...<|im_end|>`. Model sinh `<tool_call>{json}</tool_call>`, code gọi tool thật, rồi trả kết quả lại dưới dạng `<tool_response>`. Code: [`prompt.py:156`](../lifemate/lifemate/prompt.py).
- **Vòng lặp agent** (kiểu ReAct): sinh → phân tích JSON → kiểm schema → gọi env → đưa kết quả lại cho model → … → dừng. Code: [`agent.py:181-252`](../lifemate/lifemate/agent.py).
- **Greedy decoding** (luôn chọn token xác suất cao nhất) để kết quả tái lập được. BTC yêu cầu điều này.

### 3.5 SFT, LoRA, QLoRA

- **SFT (supervised fine-tuning):** dạy model bắt chước đáp án mẫu. Loss chỉ tính trên các token model phải sinh (call và câu trả lời cuối), không tính trên prompt. Trong repo trung bình chỉ khoảng **76 token mỗi ví dụ** có loss, trên khoảng 3.300 token prompt.
- **LoRA:** đóng băng model gốc, chỉ học hai ma trận nhỏ A·B (hạng r) cộng thêm vào mỗi lớp chiếu. Ở đây r = 32, khoảng 66M tham số trên 4B.
- **QLoRA:** model gốc nạp ở 4-bit (NF4) để vừa GPU 8 GB, LoRA vẫn học ở độ chính xác cao. **Adapter đang nộp được train trên nền 4-bit** và chưa ai kiểm khi chạy trên nền bf16 (B16).
- **Trong repo:** [`sft.py`](../lifemate/lifemate/sft.py) (dựng dữ liệu, gộp bước, tăng cường), [`train.py`](../lifemate/lifemate/train.py) (vòng train PyTorch thuần; [`train.py:89-97`](../lifemate/lifemate/train.py) chỉ tính logits ở vị trí có loss để tiết kiệm VRAM).

### 3.6 Đánh giá đúng cách (phần đội làm chưa tốt)

- **Tập dev:** `dev_random` (233 mẫu, chia ngẫu nhiên) đo trên app đã thấy. `dev_lao` (262 mẫu, mọi mẫu dùng 6 app bị giữ riêng khỏi train) **mô phỏng app chưa thấy, gần public hơn**. "Gộp 495 dòng" là hai tập cộng lại; 37 id nằm ở cả hai tập, mỗi tập chấm bằng adapter riêng.
- **Paired bootstrap:** so hai hệ thống trên cùng mẫu, lấy mẫu lại nhiều lần để có khoảng tin cậy 95% cho mức chênh. Code: [`compare.py`](../lifemate/lifemate/compare.py).
- **Độ nhiễu giữa các lần train:** cùng công thức train trên hai máy lệch tới **4,21 điểm** (entry 101). Khoảng tin cậy bootstrap chỉ đo nhiễu do chọn mẫu, **không** đo nhiễu này. Mục 6.1 nói vì sao điều này quan trọng.

### 3.7 Docker và GPU (phần của Leader)

- **Image** đóng gói code, thư viện và trọng số; `--network none` để chạy offline. **NVIDIA Container Toolkit** cho container dùng được GPU.
- **Compute capability:** RTX 5090 là `sm_120`. Bản torch phải được build có `sm_120` (CUDA 12.8 trở lên). Nếu không, image chạy được trên RTX 3050 hay 4070 nhưng **hỏng trên máy chấm**. Đây là rủi ro mất bài lớn nhất của L9.

### 3.8 Tài liệu học (nguồn đáng tin, theo thứ tự)

1. **Hugging Face LLM Course** (huggingface.co/learn/llm-course): transformer, tokenizer, fine-tune. Nên đọc các chương về chat template và SFT.
2. **Hugging Face Audio Course** (huggingface.co/learn/audio-course): Whisper, WER, fine-tune ASR.
3. **Paper Whisper** (Radford và cộng sự, 2022, "Robust Speech Recognition via Large-Scale Weak Supervision"), mục 2 và 3. **PhoWhisper** (VinAI, 2024).
4. **LoRA** (Hu và cộng sự, 2021) và **QLoRA** (Dettmers và cộng sự, 2023): chỉ cần phần phương pháp.
5. **Agent gọi tool:** τ-bench (Yao và cộng sự, 2024) và Berkeley Function Calling Leaderboard (BFCL). Rất gần bài này: có môi trường giả lập, có chấm theo trạng thái cuối.
6. **Nền tảng nếu muốn chắc từ gốc:** Karpathy, "Neural Networks: Zero to Hero" (YouTube), nhất là bài "Let's build GPT".

---

## 4. Kiến trúc hiện tại, đi theo luồng dữ liệu

### 4.1 Sơ đồ

```
/data/<split>/audio/*.wav  (lượt cuối + mọi lượt user trong history)
   │
   ▼  lifemate/asr.py            PhoWhisper-large fine-tune, greedy, từng file
asr/<split>.jsonl  {"audio": "...wav", "text": "..."}
   │
   ▼  lifemate/infer.py          mỗi mẫu: 1 ToolEnv, ghép chữ ASR vào history
   │     └─ lifemate/prompt.py   system = luật + hồ sơ + bảng ngày + schema tool viết gọn
   │     └─ lifemate/agent.py    vòng lặp: sinh → parse → validate → chốt chặn ID → env.call → …
   │           └─ lifemate/guard.py   chặn lệnh ghi dùng ID chưa từng xuất hiện
   ▼
submission.jsonl  {"id", "tool_calls", "state_hash"}  (+ "time" ở bản docker-submit)
   │
   ▼  scripts/check_submission.py   kiểm định dạng và schema
   ▼  lifemate/scorer.py            (chỉ chạy trên train/dev, vì public không có nhãn)

Đường train:
train.jsonl ──► lifemate/sft.py ──► sft/*.jsonl ──► lifemate/train.py ──► ckpt/<tên>/final (LoRA)
train wav   ──► lifemate/asr_train.py ──► ckpt/asr_phoft/merged
```

Lệnh nối tất cả: [`scripts/predict.sh`](../lifemate/scripts/predict.sh) (ASR cả split trước, rồi agent, rồi kiểm). Bản theo giao diện BTC nằm ở `lifemate/docker/predict.sh` trên nhánh `docker-submit`.

### 4.2 Đọc file theo thứ tự này (khoảng 3 giờ)

| # | File | Đọc chỗ nào | Câu hỏi tự trả lời khi đọc |
|---|---|---|---|
| 1 | [`scorer.py`](../lifemate/lifemate/scorer.py) | `calls_match`, `score_sample` (dòng 44–94) | Vì sao thêm một tham số tuỳ chọn mà đáp án không có lại làm mất khớp? |
| 2 | [`prompt.py`](../lifemate/lifemate/prompt.py) | `SYSTEM_RULES` (15–23), `render_tool` (61–68), `history_messages` (131–145) | Prompt **không** nói ra những gì? (`x-ref`, `returns`, quy ước `{}` của call đọc…) |
| 3 | [`agent.py`](../lifemate/lifemate/agent.py) | `Agent.run` (181–252), `HFBackend` (100–141) | Bước nào là code tất định, bước nào là model? Khi nào vòng lặp dừng? |
| 4 | [`guard.py`](../lifemate/lifemate/guard.py) | `unseen_ids` (46–50) | Vì sao chốt chặn ID gần như không thêm điểm (entry 27)? |
| 5 | [`infer.py`](../lifemate/lifemate/infer.py) | `main`, hàm `infer` (108–117) | Thời gian ASR được trừ vào hạn 25 giây thế nào? |
| 6 | [`sft.py`](../lifemate/lifemate/sft.py) | docstring (1–21), `group_steps` (62–74), các tham số tăng cường (314–317) | Đổi tên app (`rename`) dạy model điều gì? Vì sao nó vẫn chưa đủ để xử lý app mới? |
| 7 | [`train.py`](../lifemate/lifemate/train.py) | docstring, `example_loss` (89–97), tham số (122–141) | lr, r, số epoch là bao nhiêu? Một epoch có bao nhiêu bước tối ưu? |
| 8 | [`asr.py`](../lifemate/lifemate/asr.py), [`asr_train.py`](../lifemate/lifemate/asr_train.py) | toàn bộ | ASR có dùng ngữ cảnh nào không (tên app, tên danh bạ)? *(Không.)* |

Các file còn lại (`counterfactual.py`, `askpolicy.py`, `eval_loss.py`, `runinfo.py`, `scripts/*`) là công cụ phân tích hoặc dữ liệu cho các thí nghiệm đã bỏ. Chưa cần đọc.

### 4.3 Cấu hình đang nộp

| Thành phần | Giá trị |
|---|---|
| ASR | `vinai/PhoWhisper-large` + LoRA đã merge, 1,54B tham số |
| LLM | `Qwen/Qwen3-4B-Instruct-2507` (rev `cdbee75f17c0`), NF4 4-bit, chế độ không suy nghĩ |
| Adapter | `ckpt/q4b4_all/final`: LoRA r32, 1 epoch trên `sft/all.jsonl` (4.874 ví dụ từ 1.545 mẫu) |
| Tổng tham số | 5,63B (trần 6B; riêng LLM dưới 5B) |
| Suy luận | backend HF (transformers), greedy, tối đa 8 bước, hạn 25 giây mỗi mẫu tính cả ASR, có bước khởi động trước mẫu đầu |
| Tốc độ trên laptop 4070 | trung bình 10,4 giây/mẫu, p95 21,1 giây. **Chưa đo trên RTX 5090.** |

---

## 5. Điểm đang mất ở đâu (đã đo)

### 5.1 Các mốc

| Hệ thống | Điểm |
|---|---:|
| Nộp rỗng toàn bộ (trên train) | 7,18 |
| Lần nộp đầu: Whisper-turbo chưa fine-tune + 1.7B | 25,93 |
| ASR fine-tune | 35,24 |
| Agent 4B | 45,39 → 46,29 (train trên đủ 1.545 mẫu) |
| **ASR PhoWhisper-ft** | **51,16** |
| Cùng pipeline, agent là model API `xhigh` + luật bỏ tham số hiếm | 75,52 |
| Top cột SLM (04/11) | 96,66 |

### 5.2 Phân rã trên dev (4B)

| | Điểm | Hash đúng |
|---|---:|---:|
| dev_random, chữ chuẩn | 65,61 | 73,0% |
| dev_random, chữ ASR | 54,01 | 63,5% |
| dev_lao, chữ chuẩn | 53,40 | 66,8% |
| dev_lao, chữ ASR | 39,20 | 51,5% |

- **ASR:** mất khoảng 13 điểm (gộp 59,15 → 46,17 với Whisper-turbo-ft; PhoWhisper-ft bớt được khoảng 1,7).
- **App chưa thấy:** mất khoảng 12–15 điểm, và **lỗi ASR hại app chưa thấy gấp đôi** (17,1 so với 7,6 điểm, Codex mục 7).
- **Ngay cả chữ chuẩn và app đã thấy, 27% mẫu vẫn sai trạng thái cuối.**
- **So với model API** (80 mẫu, Codex mục 3): chênh lớn nhất ở **quyết định làm / hỏi / bỏ qua** (+10,6), rồi tới **chọn ID từ history hoặc kết quả đọc** (+5,0).

### 5.3 Đã thử và thất bại (đừng thử lại y như cũ)

| Thử | Kết quả | Vì sao (theo đội) |
|---|---|---|
| Agent học trên chữ ASR | chữ chuẩn −5,4 | model học cả lỗi của ASR |
| B-up (nhân bản mẫu hỏi lại) | −2,7 | hỏi thừa ở mẫu cần làm |
| Thí nghiệm D (dữ liệu phản thực tế cho hỏi lại) | thua B-up | |
| Chữ trộn (nửa chuẩn, nửa ASR) | qua dev_random (+2,3), trượt gộp (−0,7) | |
| Dữ liệu sinh bằng LLM, pilot 1 | dev_lao −2,1 | **trạng thái đúng nhưng call lệch quy ước nhãn**; 90% mẫu sinh mở đầu bằng call đọc (thật: 59%) |
| Prompt `xref` (in `x-ref` và `returns`) | −1,0 | |
| PhoWhisper-ft train trên gần đủ train | public 49,65 | |
| Dữ liệu sinh v2 | −0,46 | |
| Luật bỏ tham số hiếm (cho 4B) | −0,26 | 4B đã tự học quy ước này |
| Train thêm epoch | loss dev đã phẳng | |

---

## 6. Chẩn đoán: vì sao kẹt ở 51

Phần này là nhận định của Claude khi đọc lại toàn bộ repo bằng con mắt mới. Đây là giả thuyết để bạn kiểm, chưa phải kết luận.

### 6.1 Nhiễu lớn hơn tín hiệu: đội đang quyết định gần như tung đồng xu

- Luật giữ/bỏ của đội thường cần **+1 hoặc +2 điểm trên một lần train**. Nhưng cùng công thức train hai lần đã lệch **2–4 điểm** (entry 101). Khoảng tin cậy của các thí nghiệm cũng rộng khoảng ±3,4 điểm, ví dụ +1,71 [−1,68; +5,12].
- **Hệ quả:** mọi hiệu ứng nhỏ hơn khoảng 4 điểm đều không phân biệt được với nhiễu. Vài ý tưởng tốt có thể đã bị bỏ oan (chữ trộn +2,3 rồi −0,7 là ví dụ điển hình), và ngược lại.
- **Cách sửa rẻ nhất:** ưu tiên **thay đổi chỉ ở lúc suy luận** (prompt lúc chạy, bỏ phiếu, ràng buộc giải mã, sửa ASR), giữ nguyên adapter. Khi đó suy luận greedy là tất định, so theo cặp chỉ còn nhiễu do chọn mẫu, và đo được ngay trong 1–2 giờ GPU. Với thay đổi cần train lại, phải train **ít nhất 2 seed mỗi bên** thì mới kết luận.

### 6.2 Model học thuộc app, không học chính sách

- SFT dạy model bắt chước 1.545 lời giải trên 46 app. Phép đổi tên app có giúp, nhưng cấu trúc của app (tool nào đọc, tool nào ghi, ID lấy từ đâu) vẫn y nguyên. Vì vậy model vẫn chỉ quen với cấu trúc của 46 app đó.
- 65% mẫu public dùng app chưa thấy. Với app mới, model phải tự suy ra những quy ước mà prompt không nói. [`SYSTEM_RULES`](../lifemate/lifemate/prompt.py) chỉ có 6 luật chung, không có luật như "trước lệnh ghi lên thiết bị thì đọc trạng thái, với `{}`".
- **Dấu hiệu:** với 4B, dev_lao kém dev_random 12 điểm ngay trên chữ chuẩn. Model API (chưa từng train trên dữ liệu này) lại làm dev_lao **tốt hơn** dev_random: 67 so với 62, trên 40 mẫu mỗi tập (Codex mục 3).

### 6.3 Câu hỏi then chốt chưa ai trả lời: BTC sinh nhãn thế nào? (Q2)

- Top SLM đạt 96,66 trong khi model API chỉ 75,52. Một khả năng (chưa kiểm): **nhãn được sinh bằng một chính sách gần như tất định**, và các đội top đã giải mã được chính sách đó, rồi sinh dữ liệu cho 11 app public. BTC **cho phép** dùng catalog và `zaic_tools` của public_test để sinh dữ liệu (JOURNAL mục 1.5).
- Hai pilot dữ liệu sinh của đội để LLM tự viết cả đáp án, nên đáp án lệch quy ước. Đó đúng là lý do Codex chỉ ra.
- **Bằng chứng nhỏ Claude đo lại trên máy này (train, CPU, vài giây):** sau `contacts.search`, nếu kết quả có 1 người thì nhãn **luôn** làm tiếp (131/131). Nếu có từ 2 người trở lên thì 74/103 lần nhãn gọi `ask_missing_info` ngay, 26 lần làm tiếp và 3 lần dừng. 26 ca này rất có thể là câu nói đã đủ thông tin để chọn (ví dụ có quan hệ "sếp"). **Nếu luật kiểu này giải thích được phần lớn nhãn, ta viết được bộ sinh nhãn bằng code cho app mới**, và chỉ cần LLM viết câu nói.

### 6.4 Chưa dùng phần cứng chấm

- Máy chấm là RTX 5090 32 GB, nhưng hệ thống vẫn chạy như trên laptop 8 GB: 4-bit, backend HF, một lần sinh greedy. Code đã có backend vLLM ([`agent.py:81`](../lifemate/lifemate/agent.py)) nhưng chưa dùng cho bản nộp.
- Hạn 25–30 giây mỗi mẫu đủ chỗ cho tính toán thêm lúc suy luận: sinh nhiều phương án rồi bỏ phiếu cho quyết định làm / hỏi / bỏ qua (chỗ mất nhiều nhất), hoặc thử bản "thinking". **Rủi ro:** adapter train trên nền 4-bit chưa được kiểm trên nền bf16, và còn 8 ngày.

### 6.5 ASR dùng zero ngữ cảnh

- ASR giải mã từng file wav độc lập, không biết tên app đã cài, tên người trong history hay tên trong kết quả tool. Lỗi nặng nhất lại rơi vào `query`, `content`, `time`, `title` (Codex mục 7).
- Whisper hỗ trợ **prompt cho decoder** (`prompt_ids`, hay `initial_prompt`). Đưa danh sách tên riêng hợp lệ vào đó có thể sửa đúng loại lỗi này mà không phải train lại. Đây là việc đúng vai Leader (ASR).

### 6.6 Bằng chứng từ trace của bản 51,16 (đo ngày 08/11, chỉ đếm hành vi, không dùng nhãn)

File `lifemate/runs/e2e_public_q4b_all_phoft_trace.jsonl` (634 mẫu, hạn 60 giây):

- **Vòng lặp đọc ở app mới.** 21 mẫu chạy hết 8 bước. Trong đó **18 mẫu gọi lại đúng một call đọc** đã có kết quả. Code bỏ trùng nên trả lại kết quả cũ mà không nhắc gì, model gọi tiếp, và cuối cùng **không gửi lệnh ghi hay hỏi lại nào**. Hầu hết rơi vào app mới: `event_tickets.search` bị gọi lại 55 lần, `stocks.get_quote` 18 lần, `recipes.search` 7 lần (ngoài ra có `flights.search` 15 lần). Các mẫu này gần như chắc chắn được 0 điểm (khoảng 2,8% public), lại tốn trung bình 23,9 giây mỗi mẫu.
- **Lệnh ghi không làm gì.** 51 kết quả `ok: true, done: false` trong 19 mẫu. Nhiều nhất là `stocks` (14 lần): model tự bịa mã cổ phiếu từ lời nói, vì app này không có tool tra mã. Chốt chặn ID không bắt được, vì tham số mã không có `x-ref`.
- **Quy mô app mới:** 275/634 mẫu (43%) có gọi tool của 11 app mới.
- **Lỗi định dạng gần như không còn:** chỉ 12 mẫu có lỗi schema, JSON hoặc bị chốt chặn ID chặn. Vấn đề không nằm ở định dạng.

---

## 7. Bài tập tự làm trên máy này (CPU, không cần `.venv`)

Chạy trong `lifemate/`. Bộ chấm và phần dựng prompt chỉ dùng thư viện chuẩn, nên Python hệ thống chạy được. **Chỉ dùng train/dev. Không suy nhãn từ public** (thể lệ cấm gán nhãn tập test).

**Bài 1: tự kiểm "phát lại đáp án ra 100" và thấy cổng hash hoạt động.** Claude đã chạy thử trên máy này: đáp án đúng được 100,0; bỏ call đọc đầu tiên còn 79,37 (hash vẫn đúng 100%, chỉ F1 giảm); giữ call đúng nhưng hash sai thì chỉ còn các mẫu ngoài phạm vi có điểm.

```python
# lưu thành ex_oracle.py rồi chạy:
#   PYTHONPATH=. python3 ex_oracle.py gold > /tmp/o.jsonl
#   python3 -m lifemate.scorer /tmp/o.jsonl --split train --ids splits/dev_random.txt
import json, sys
from lifemate.data import load_split, load_catalog, catalog_tools, zaic_tools, DEFAULT_ROOT
mode = sys.argv[1] if len(sys.argv) > 1 else "gold"          # gold | drop_first_read
ids = set(open("splits/dev_random.txt").read().split())
tools = catalog_tools(load_catalog("train")); zt = zaic_tools("train")
for s in load_split("train"):
    if s["id"] not in ids: continue
    calls = list(s["label"]["tool_calls"])
    if mode == "drop_first_read":
        for i, c in enumerate(calls):
            if tools.get(c["name"], {}).get("kind") == "read": calls.pop(i); break
    env = zt.ToolEnv("train", s["id"], root=str(DEFAULT_ROOT))
    for c in calls: env.call(c["name"], c["arguments"])
    print(json.dumps({"id": s["id"], "tool_calls": calls, "state_hash": env.get_state_hash()}, ensure_ascii=False))
```

**Bài 2: xem tận mắt prompt mà model nhìn thấy.**

```python
# PYTHONPATH=. python3 ex_prompt.py   (in prompt khoảng 9.000 ký tự cho mẫu đầu tiên của train)
from lifemate.data import load_split, load_catalog, catalog_tools
from lifemate.prompt import build_messages, to_chatml
from lifemate.infer import texts_for          # cách repo lấy chữ: "oracle" = audio_text, "asr" = file ASR
cat = load_catalog("train"); tools = catalog_tools(cat); apps = {x["id"]: x for x in cat["apps"]}
s = load_split("train")[0]
user_text, history_texts = texts_for(s, "oracle", None)
print(to_chatml(build_messages(s, user_text, history_texts, tools, apps)))
```

Chỉ in ra màn hình để đọc. **Không chép nội dung dữ liệu vào file trong repo**, vì repo đang public và thể lệ cấm phát tán dữ liệu.

Tự hỏi khi đọc: nếu là một model chưa từng thấy app này, bạn có đủ thông tin để biết phải đọc trước khi ghi không? Biết lấy ID từ đâu không?

**Bài 3: tự viết luật cho một quy ước** (bắt đầu trả lời Q3, Q4). Chọn một app, ví dụ `smart_home` hoặc `banking`. Đếm trong nhãn train:

- lệnh ghi có call đọc cùng app đứng trước không;
- call đọc có tham số hay `{}`;
- khi nào nhãn hỏi lại.

Viết luật thành hàm Python, rồi đo **luật tái tạo đúng bao nhiêu phần trăm nhãn**. Đây chính là H1 ở mục 8.

**Bài 4: tự phân loại 15 mẫu sai trước khi hỏi Claude** (HUMAN_TODO mục 7, chưa ai làm). Cần file `*_rows.jsonl` và trace của lượt chấm dev, đang nằm ở `~/zac-c3/lifemate/runs/` trên laptop của Anh, ví dụ `sft_q4b4_fit_lao_asrturboft_rows.jsonl`. Nhờ Anh gửi riêng. Với từng mẫu, so call nộp với nhãn và ghi một nguyên nhân: sai quyết định, sai ID, sai giờ, thiếu bước đọc, ASR nghe sai…

---

## 8. Hướng nghiên cứu để tự phát triển, xếp theo đòn bẩy

Mỗi hướng ghi rõ: giả thuyết, bước đầu rẻ nhất, cách đo, file phải sửa. Ưu tiên hướng **đo được không cần train lại** (mục 6.1).

### H1. Giải mã chính sách sinh nhãn, rồi sinh dữ liệu bằng code (Q2, Q3, Q4, Q17)

- **Giả thuyết:** phần lớn nhãn tuân theo luật tất định (đọc trước ghi, `{}` cho call đọc, hỏi lại khi có nhiều đối tượng khớp, `[]` khi người dùng huỷ…).
- **Bước 1 (CPU, máy này, 1–2 ngày):** viết "oracle luật" cho 5–10 app train phổ biến. Đầu vào là ý định đã biết (lấy từ nhãn) và trạng thái env; đầu ra là chuỗi call theo luật. Đo % mẫu mà call của luật **khớp 100% với nhãn** (dùng `scorer.calls_match`). Nếu trên 80%, giả thuyết đứng vững.
- **Bước 2:** tổng quát hoá luật qua metadata của catalog (`kind`, `x-ref`, `returns`), không viết tay từng app. Kiểm trên 6 app của dev_lao như thể chưa thấy chúng.
- **Bước 3:** sinh mẫu cho 11 app public. LLM chỉ viết câu nói (và TTS nếu cần), còn **nhãn do luật sinh và được kiểm bằng ToolEnv của public**. BTC cho phép dùng catalog và `zaic_tools` của public; điều bị cấm là gán nhãn audio hay yêu cầu của tập test.
- **File:** `lifemate/synth.py` trên nhánh `synth-v2` đã có khung (sinh state, chạy simulator). Thay phần đáp án do LLM sinh bằng oracle luật.
- **Rủi ro:** tốn công. Nếu luật chỉ giải thích được khoảng 60% nhãn thì dừng sớm và ghi lại vì sao.

### H2. Sửa quy trình đánh giá trước khi thử thêm

- **Bước 1:** dùng Bài 4 để biết lỗi thật nằm ở đâu.
- **Bước 2:** quy ước mới: thay đổi lúc suy luận thì so theo cặp, cùng adapter; thay đổi cần train thì ít nhất 2 seed mỗi bên, báo cả trung bình lẫn khoảng lệch giữa các seed.
- **Tài liệu:** `compare.py` đã có paired bootstrap. Chỉ cần thêm phần gộp nhiều seed.

### H3. Ràng buộc và bỏ phiếu lúc suy luận cho quyết định làm / hỏi / bỏ qua

- **Giả thuyết:** quyết định ở bước đầu là chỗ chênh lớn nhất so với model API (+10,6 điểm trên 80 mẫu).
- **Bước 1 (cần GPU, laptop của Anh, chạy sau B28):** cho bước đầu sinh nhiều phương án (prompt hoán vị thứ tự app, hoặc sampling có seed cố định), bỏ phiếu theo loại quyết định, rồi chạy tiếp greedy. Đo trên 80 mẫu dev theo cặp, cùng adapter.
- **File:** `agent.py`, hàm `Agent.run`. Thêm một nhánh trước vòng lặp.
- **Ràng buộc:** kết quả phải tái lập (seed cố định), và đo thời gian. Trên RTX 5090 dùng bf16 + vLLM thì nhanh hơn nhiều, nhưng phải kiểm lại điểm khi đổi nền 4-bit sang bf16 (B16).

### H4. ASR có ngữ cảnh (Q9, Q10, Q12): việc đúng vai Leader

- **Bước 1 (máy này chạy được ASR trên GPU 4 GB, PhoWhisper-large fp16 khoảng 3 GB):** đưa tên app đã cài, tên người trong `user_profile` và tên xuất hiện trong `tool_results` của history vào prompt của decoder Whisper.
- **Đo:** không đo WER. Đo **tỉ lệ đúng của các slot** (tên, số, giờ) trên dev, so với `audio_text`. `vinum.py` và `scripts/asr_quality.py` đã có phần nhận dạng số và giờ.
- **Bước 2:** nếu slot đúng hơn rõ, nhờ Anh chấm agent trên chữ mới. Đây là thay đổi chỉ lúc suy luận, adapter giữ nguyên.
- **File:** [`asr.py`](../lifemate/lifemate/asr.py), lớp `Whisper` (dòng 55–80). Thêm `prompt_ids` vào lời gọi `self.model.generate(...)` ở dòng 75. Lưu ý: hiện mỗi lần gọi xử lý một lô file, nên muốn có prompt riêng cho từng mẫu thì phải chạy batch 1, vốn là mặc định của `predict.sh`.

### H5. Rà model mới (HUMAN_TODO 0.4, giao cho Leader, chưa làm)

- Tìm trên Hugging Face các LLM dưới 5B và ASR tiếng Việt phát hành từ 06/2026 tới 25/10/2026. Kiến thức của Claude dừng ở giữa năm 2026, nên không biết các model này.
- Tiêu chí: điểm tool-calling (BFCL), licence, có bản Instruct hay không.
- Chỉ đáng đổi khi có lợi rõ và còn kịp train lại. Với hạn 16/11 thì gần như chắc là không kịp; ghi lại cho lần sau.

### H6 (thấp): ràng buộc giải mã ID và enum (Q14)

Chốt chặn ID chặn sau khi sinh đã gần như không thêm điểm (entry 27). Ràng buộc ngay lúc giải mã chắc cũng ít tác dụng. Làm sau cùng.

---

## 9. Lộ trình 8 ngày còn lại, nói thẳng

- **Vượt 80 trước 16/11 là rất khó.** Từ 51 cần thêm khoảng 29 điểm. ASR hoàn hảo chỉ bù khoảng 13 điểm, và model API trên cùng pipeline cũng mới 75,5. Không còn núm chỉnh nhỏ nào cho được mức đó; chỉ có H1 nếu đúng mới có thể tạo bước nhảy.
- **Ưu tiên 1, không thương lượng:** L9 xong và chạy được trên GPU **trước khoảng 13/11**. Một image hỏng trên RTX 5090 là mất 0 điểm private.
- **Song song, trên máy này (CPU):** H1 bước 1 và H4 bước 1. Cả hai không chiếm GPU của Anh.
- **Mốc chốt model khoảng 13/11** (đội đã đặt). Thay adapter hoặc ASR chỉ cần thay một thư mục trong image, rồi chạy lại B28.
- **Dù không kịp cho 16/11**, H1 và H2 vẫn là kiến thức bạn tự sở hữu. Đó là thứ giúp bạn không phải "train đi train lại" nữa.

### Kiểm tra bản thân: đã lấy lại gốc chưa?

Trả lời được các câu sau mà không mở Claude:

1. Vì sao mẫu có call đọc thừa vẫn có điểm, còn mẫu có lệnh ghi sai thì 0?
2. Agent dừng trong những trường hợp nào? (5 trường hợp, ở `agent.py`)
3. Vì sao không dùng các lượt assistant trong history làm đích train? (JOURNAL mục 3, phát hiện 9)
4. dev_lao mô phỏng điều gì, và vì sao nó quan trọng hơn dev_random?
5. Vì sao "+1,5 điểm trên một lần train" chưa chứng minh được gì?
6. Image hiện tại thiếu những gì để chạy được trên RTX 5090 theo giao diện BTC?
