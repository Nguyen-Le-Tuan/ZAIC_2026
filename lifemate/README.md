# LifeMate — ZAC 2026

Pipeline: ASR (~0.8B) → chuẩn hoá số → Qwen3-4B agent (vòng lặp gọi tool) → `zaic_tools.ToolEnv` → `submission.jsonl`.

## Cấu trúc

| File | Việc |
|---|---|
| `lifemate/data.py` | Đọc split, catalog; nạp đúng `zaic_tools` của split. Agent không bao giờ đọc `*_environment/`. |
| `lifemate/prompt.py` | Prompt ChatML Qwen3: luật, profile, bảng ngày (−7…+14), schema tool dạng gọn, history kèm tool_results. |
| `lifemate/agent.py` | Vòng lặp agent + lớp kiểm soát: `validate()` trước khi gọi (call sai không vào bài nộp), bỏ trùng call đọc, dừng sau `ask_missing_info`, giới hạn bước và thời gian. Backend: `openai` (vLLM server), `vllm` (trong tiến trình, cho Docker), `oracle` (phát lại đáp án để test). |
| `lifemate/infer.py` | Chạy cả split → `submission.jsonl` (+ trace). `--text oracle` dùng `audio_text`, `--text asr` dùng file ASR. |
| `lifemate/scorer.py` | Bộ chấm local theo công thức của BTC (hash + F1 call, token-F1 > 0.6 cho tham số fuzzy). Mẫu có trong `--ids` mà thiếu prediction tính 0 (kể cả mẫu ngoài phạm vi); id trùng hoặc id ngoài split thì báo lỗi. Test: `python -m lifemate.tests.test_scorer`. |
| `scripts/make_splits.py` | `splits/dev_random.txt` (233 mẫu) và `splits/dev_lao.txt` (262 mẫu dùng 6 app giữ riêng, mô phỏng app chưa thấy). |
| `lifemate/sft.py` | Sinh dữ liệu SFT (ChatML + mask loss) bằng đúng code prompt của lúc suy luận. Gộp call độc lập vào một bước, tăng cường: đổi tên app/tool, gỡ app → `[]`, thêm app gây nhiễu (cả app của public_test), transcript kiểu ASR. Lượt history tắt mặc định vì quy ước khác đáp án. |
| `scripts/check_sft.py` | Kiểm tra prompt SFT khớp từng ký tự với prompt của agent thật, gộp bước không mất call (100 điểm), ranh giới token ổn định. |
| `lifemate/train.py` | LoRA SFT bằng vòng lặp PyTorch thuần: chỉ tính logits ở vị trí có loss, gradient checkpointing, batch 1 + tích luỹ gradient, `--load-4bit` cho QLoRA. Dev loss tính trên **mọi** dòng dev (`--eval-n 0`). Ghi `ckpt/<tag>/log.jsonl`, `run_info.json` (hash dữ liệu, id dev, commit), lưu adapter mỗi 100 bước và `final/`. Không ghi đè checkpoint đã có. |
| `lifemate/submit.py`, `docker/` | Giao diện nộp Docker của BTC: `/code/predict.sh`, notebook đo thời gian, `start_jupyter.sh` (mục "Nộp Docker" bên dưới). `lifemate/seeding.py`: seed cố định lúc suy luận. |
| `lifemate/runinfo.py` | Provenance: sha256 file/thư mục/danh sách id, commit git, phiên bản thư viện, chặn ghi đè kết quả cũ. |
| `lifemate/eval_loss.py` | Loss teacher-forced của một checkpoint trên mọi dòng của một file SFT (chỉ để chẩn đoán; chọn checkpoint bằng điểm rollout). |
| `lifemate/compare.py` | So sánh theo cặp nhiều lượt đánh giá trên cùng tập mẫu: điểm, call-F1, hash, từng loại, latency, Δ kèm bootstrap 95%, lát cắt theo độ dài history và dải id. |
| `lifemate/askpolicy.py` | Chính sách hỏi lại của nhãn dưới dạng hàm: kiểu A (trùng tên khi tra), B (chọn mơ hồ ID), C (thiếu slot thường); luật "≥ 2 kết quả trùng tên mà câu không phân biệt". Chỉ dùng để phân tích và sinh dữ liệu, agent không import. |
| `lifemate/counterfactual.py` | Bộ sinh cặp đủ/thiếu cho thí nghiệm D: `candidates` (chọn nguồn từ fit) → viết lại câu (người hoặc LLM) → `build` (kiểm tra câu, phát lại nhãn qua ToolEnv, loại mẫu dev) → `review` (file đọc tay). Đầu ra ở `gen/`, không commit. |
| `scripts/ask_policy_stats.py` | Tái lập số liệu của `docs/EXPERIMENT_D.md`: chính sách hỏi lại trên fit, hành vi model theo kiểu, mô phỏng luật trùng tên, số nguồn sinh dữ liệu. |
| `scripts/eval_ckpt.sh` | Đánh giá một checkpoint (hoặc model gốc) trên một tập dev, đúng protocol oracle-text, không ghi đè lượt cũ. |
| `scripts/train_local.sh` | Chạy trên máy local: baseline zero-shot → train → đánh giá rollout **mọi** checkpoint đã lưu → bảng so sánh. Chọn cặp `FIT`/`DEV` (mặc định fit_random/dev_random); file SFT chỉ dùng lại khi manifest khớp. |
| `scripts/count_tokens.py` | Độ dài prompt bằng tokenizer Qwen3 (hiện: TB ~3K, max ~6.1K token). |
| `scripts/cloud_baseline.sh` | Baseline zero-shot trên GPU cloud. |

## Lệnh

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python scripts/make_splits.py
# test bộ chấm (thiếu prediction, id trùng, id ngoài split):
.venv/bin/python -m lifemate.tests.test_scorer
# thí nghiệm D: sinh cặp hỏi lại / tự làm từ fit (chưa train)
.venv/bin/python -m lifemate.counterfactual candidates --fit splits/fit_lao.txt --exclude splits/dev_lao.txt splits/dev_random.txt --out gen/tasks_fit_lao.jsonl
#   viết gen/rewrites_fit_lao.jsonl ({"task_id","new_text","removed_span"|"added_span"} hoặc {"task_id","skip"})
.venv/bin/python -m lifemate.counterfactual build --tasks gen/tasks_fit_lao.jsonl --rewrites gen/rewrites_fit_lao.jsonl \
    --fit splits/fit_lao.txt --exclude splits/dev_lao.txt splits/dev_random.txt --drop-apps splits/heldout_apps.json --out gen/d_fit_lao.jsonl
.venv/bin/python -m lifemate.sft --fit splits/fit_lao.txt --drop-apps splits/heldout_apps.json --extra-samples gen/d_fit_lao.jsonl --out sft/fit_lao_d.jsonl
.venv/bin/python -m lifemate.tests.test_counterfactual
# kiểm tra toàn pipeline không cần model (phải ra 100):
.venv/bin/python -m lifemate.infer --split train --text oracle --backend oracle --out runs/oracle_train.jsonl
.venv/bin/python -m lifemate.scorer runs/oracle_train.jsonl --split train
# baseline thật trên GPU cloud:
bash scripts/cloud_baseline.sh
# dữ liệu SFT (mỗi dòng: {"id","src","aug","segments": [[text, loss], ...]}; kèm <file>.manifest.json ghi split,
# tham số, hash input và code; --reuse chỉ giữ file cũ khi manifest khớp hoặc dựng lại ra đúng từng byte):
.venv/bin/python -m lifemate.sft --fit splits/fit_random.txt --out sft/fit_random.jsonl          # đánh giá trên dev_random
.venv/bin/python -m lifemate.sft --fit splits/fit_lao.txt --drop-apps splits/heldout_apps.json --out sft/fit_lao.jsonl  # đo app chưa thấy
.venv/bin/python -m lifemate.sft --out sft/all.jsonl                                              # train bản nộp
.venv/bin/python scripts/check_sft.py
```

### Train

```bash
# qua đêm trên laptop (RTX 4070 8GB, Qwen3-1.7B): ~2.7h train + ~25 phút đánh giá
nohup systemd-inhibit --what=sleep:idle:handle-lid-switch bash scripts/train_local.sh > runs/overnight.log 2>&1 &
tail -f runs/overnight.log                       # tiến độ: loss, tok/s, eta_min, peak_gb, dev_loss
# trên GPU cloud: model lớn hơn, cùng script
.venv/bin/python -m lifemate.train --model Qwen/Qwen3-4B-Instruct-2507 --data sft/all.jsonl --out ckpt/q4b_all
# đo app chưa thấy: train trên fit_lao (đã bỏ 6 app), chấm dev_lao
FIT=fit_lao DEV=dev_lao TAG=q17b_fit_lao SKIP_ZS=1 bash scripts/train_local.sh
# đánh giá một adapter (đủ 233 mẫu, ghi runs/sft_<TAG>* + meta, không ghi đè)
TAG=q17b_fit_random_s100 ADAPTER=ckpt/q17b_fit_random/step_100 LOSS=1 bash scripts/eval_ckpt.sh
# so sánh theo cặp (lượt đầu là mốc)
.venv/bin/python -m lifemate.compare runs/sft_q17b_fit_random runs/sft_q17b_fit_random_s100 --ids splits/dev_random.txt --slices
```

Số đo trên RTX 4070 Laptop 8GB (Qwen3-1.7B, LoRA r=32): ~1.4K token/s, đỉnh 5.4GB VRAM với mẫu dài nhất
(màn hình chiếm thêm ~1.7GB). Zero-shot cần `--assistant-prefix '<think>\n\n</think>\n\n'` để Qwen3 lai không "suy nghĩ";
model đã SFT thì không cần.

Thử nghiệm so sánh nên chạy: `--history tagged` (thêm 2.838 lượt history, có gắn nhãn trong system prompt),
`--rename 0/2/4`, `--asr-file` (transcript ASR k-fold khi phần ASR có kết quả).

## Nộp Docker: giao diện của BTC (`docker/`)

Theo hướng dẫn Docker của BTC ngày 04/11 (tóm tắt có số trang: `docs/BTC_DOCKER_GUIDE_2026-11-06.md` trên `main`).
Dockerfile và base image (CUDA 13.2, torch có sm_120) là việc của leader; ở đây chỉ có ba file đặt ở `/code`:

| File trong repo | Chép tới | Việc |
|---|---|---|
| `docker/predict.sh` | `/code/predict.sh` | Tự tìm split trong `/data` (thư mục có `<tên>_tools_catalog.json`), chạy `scripts/predict.sh` với cấu hình nộp (PhoWhisper-ft `ckpt/asr_phoft/merged`, Qwen3-4B-Instruct-2507 NF4 + `ckpt/q4b4_all/final`, 25 s/mẫu, warm-up, seed 0), file trung gian để trong thư mục tạm (không ghi vào `/data`), ghi `/result/submission.jsonl` và in `load model: … ms` / `predict: N mẫu, … ms, trung bình … ms/mẫu`. Không cần biến môi trường. |
| `docker/start_jupyter.sh` | `/code/start_jupyter.sh` | `jupyter lab --port 9777 --ip 0.0.0.0`, mật khẩu/token `zac2026`, `--allow-root --no-browser`, đúng lệnh của BTC; chạy bằng cùng Python với `predict.sh`. |
| `docker/predict_notebook.ipynb` | `/code/predict_notebook.ipynb` | Cùng hệ thống nhưng **từng mẫu một** (đọc wav → ASR → agent, một `ToolEnv` mỗi mẫu). Các ô: seed → nạp model → đọc test case → warm-up → vòng lặp; ghi `/result/jupyter_submission.jsonl`. |

Mỗi dòng kết quả có `time` (mili giây, số nguyên). Với `predict.sh`: giây ASR của mẫu (lấy từ file ASR) + giây agent.
Với notebook: từ trước khi tạo `ToolEnv` và đọc audio tới khi có `state_hash`. Cả hai không tính thời gian nạp model và
warm-up. Phần dùng chung (cấu hình, tìm split, chạy từng mẫu) nằm ở `lifemate/submit.py`; seed ở `lifemate/seeding.py`.

**Cách leader chép vào image** (một trong hai):

```bash
# A. cả thư mục lifemate/ làm /code (ckpt/asr_phoft/merged và ckpt/q4b4_all/final đi kèm), rồi đưa ba file ra gốc
cp -r lifemate/. /code/ && cp /code/docker/predict.sh /code/docker/start_jupyter.sh /code/docker/predict_notebook.ipynb /code/
# B. giữ code ở /app/lifemate như image 05/11 (phải cập nhật lên nhánh này), /code chỉ có ba file
cp lifemate/docker/predict.sh lifemate/docker/start_jupyter.sh lifemate/docker/predict_notebook.ipynb /code/
```

- Script tìm code ở thư mục của chính nó, rồi thư mục cha, rồi `/app/lifemate`; Python là `.venv/bin/python` trong thư
  mục code nếu có, nếu không thì `python3`. `jupyterlab` phải cài vào **đúng Python đó** (`pip install jupyterlab`).
- Base model `Qwen/Qwen3-4B-Instruct-2507` phải nằm trong cache Hugging Face của image (chạy offline).
- Kiểm nhanh trong image, không nạp model: `DRY_RUN=1 bash /code/predict.sh` (in split, đường dẫn, model có hay chưa).
- Đã thử `start_jupyter.sh` với jupyterlab 4.6.6 / jupyter_server 2.21.1: cờ `--NotebookApp.*` của BTC vẫn chạy (chỉ báo
  deprecated), nhập `zac2026` ở ô "Password or token" là vào được.

**Thử trên laptop** (từ thư mục `lifemate/`, cùng script; các biến chỉ để thử, bản nộp không cần):

```bash
DATA_ROOT=../data/train+public_test SPLIT=public_test RESULT_DIR=runs/code_pub WORK=runs/code_pub/work bash docker/predict.sh
# notebook: mở bằng jupyter từ docker/, hoặc chạy không giao diện; IDS=<file id> để chạy một phần
DATA_ROOT=../data/train+public_test SPLIT=public_test RESULT_DIR=runs/nb_pub WORK=runs/nb_pub/work jupyter lab docker/
.venv/bin/python -m lifemate.tests.test_submit   # test CPU: split, cấu hình, trường time, notebook với model giả, script bọc
```

## Giao kèo giữa ASR và agent

ASR ghi `asr/<split>.jsonl`, mỗi dòng `{"audio": "audio/<id>/<file>.wav", "text": "..."}`, phủ **mọi** file wav
(cả lượt cuối lẫn các lượt user trong history). Agent đọc bằng `--text asr --asr-file asr/<split>.jsonl`.

## Chia việc

- **Agent / LLM** (máy RTX 4070 8GB + cloud): bộ chấm, prompt, SFT data, dữ liệu app tổng hợp, train Qwen3-4B.
- **ASR + Docker** (máy RTX 3050 4GB + cloud): benchmark ASR trên audio train (WER + độ đúng của số/giờ/tên),
  fine-tune, chuẩn hoá chữ → số, đóng Docker offline, đo thời gian trên GPU 24GB.

## Ranh giới thể lệ

- Không đọc/parse file trong `*_environment/` từ code agent (chỉ `scorer.py` dùng `ToolEnv` để replay đáp án train).
- Mỗi mẫu đúng một `ToolEnv`; mọi call thật đều vào bài nộp.
- Không gán nhãn hay pseudo-label audio/yêu cầu của public_test/private_test để train.
