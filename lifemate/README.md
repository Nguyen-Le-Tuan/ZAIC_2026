# LifeMate — ZAC 2026

Pipeline: ASR (~0.8B) → chuẩn hoá số → Qwen3-4B agent (vòng lặp gọi tool) → `zaic_tools.ToolEnv` → `submission.jsonl`.

## Cấu trúc

| File | Việc |
|---|---|
| `lifemate/data.py` | Đọc split, catalog; nạp đúng `zaic_tools` của split. Agent không bao giờ đọc `*_environment/`. |
| `lifemate/prompt.py` | Prompt ChatML Qwen3: luật, profile, bảng ngày (−7…+14), schema tool dạng gọn, history kèm tool_results. |
| `lifemate/agent.py` | Vòng lặp agent + lớp kiểm soát: `validate()` trước khi gọi (call sai không vào bài nộp), bỏ trùng call đọc, dừng sau `ask_missing_info`, giới hạn bước và thời gian. Backend: `openai` (vLLM server), `vllm` (trong tiến trình, cho Docker), `oracle` (phát lại đáp án để test). |
| `lifemate/infer.py` | Chạy cả split → `submission.jsonl` (+ trace). `--text oracle` dùng `audio_text`, `--text asr` dùng file ASR. |
| `lifemate/scorer.py` | Bộ chấm local theo công thức của BTC (hash + F1 call, token-F1 > 0.6 cho tham số fuzzy). |
| `scripts/make_splits.py` | `splits/dev_random.txt` (233 mẫu) và `splits/dev_lao.txt` (262 mẫu dùng 6 app giữ riêng, mô phỏng app chưa thấy). |
| `lifemate/sft.py` | Sinh dữ liệu SFT (ChatML + mask loss) bằng đúng code prompt của lúc suy luận. Gộp call độc lập vào một bước, tăng cường: đổi tên app/tool, gỡ app → `[]`, thêm app gây nhiễu (cả app của public_test), transcript kiểu ASR. Lượt history tắt mặc định vì quy ước khác đáp án. |
| `scripts/check_sft.py` | Kiểm tra prompt SFT khớp từng ký tự với prompt của agent thật, gộp bước không mất call (100 điểm), ranh giới token ổn định. |
| `lifemate/train.py` | LoRA SFT bằng vòng lặp PyTorch thuần: chỉ tính logits ở vị trí có loss, gradient checkpointing, batch 1 + tích luỹ gradient, `--load-4bit` cho QLoRA. Dev loss tính trên **mọi** dòng dev (`--eval-n 0`). Ghi `ckpt/<tag>/log.jsonl`, `run_info.json` (hash dữ liệu, id dev, commit), lưu adapter mỗi 100 bước và `final/`. Không ghi đè checkpoint đã có. |
| `lifemate/runinfo.py` | Provenance: sha256 file/thư mục/danh sách id, commit git, phiên bản thư viện, chặn ghi đè kết quả cũ. |
| `lifemate/eval_loss.py` | Loss teacher-forced của một checkpoint trên mọi dòng của một file SFT (chỉ để chẩn đoán; chọn checkpoint bằng điểm rollout). |
| `lifemate/compare.py` | So sánh theo cặp nhiều lượt đánh giá trên cùng tập mẫu: điểm, call-F1, hash, từng loại, latency, Δ kèm bootstrap 95%, lát cắt theo độ dài history và dải id. |
| `scripts/eval_ckpt.sh` | Đánh giá một checkpoint (hoặc model gốc) trên một tập dev, đúng protocol oracle-text, không ghi đè lượt cũ. |
| `scripts/train_local.sh` | Chạy trên máy local: baseline zero-shot → train → đánh giá rollout **mọi** checkpoint đã lưu → bảng so sánh. Chọn cặp `FIT`/`DEV` (mặc định fit_random/dev_random); file SFT chỉ dùng lại khi manifest khớp. |
| `scripts/count_tokens.py` | Độ dài prompt bằng tokenizer Qwen3 (hiện: TB ~3K, max ~6.1K token). |
| `scripts/cloud_baseline.sh` | Baseline zero-shot trên GPU cloud. |

## Lệnh

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python scripts/make_splits.py
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
