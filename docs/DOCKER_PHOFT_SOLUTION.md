# Giải pháp Docker PhoWhisper-ft

Pipeline nộp public dùng PhoWhisper-large fine-tune để nhận dạng tiếng nói, sau đó Qwen3-4B agent gọi `zaic_tools.ToolEnv` và xuất `submission.jsonl`. Bản public đạt 51,16; bản dùng Whisper-turbo-ft với cùng agent và code đạt 46,29.

## Model và giới hạn tham số

| Thành phần | Nguồn, giấy phép | Cách dùng | Tham số |
| --- | --- | --- | ---: |
| ASR | `vinai/PhoWhisper-large`, revision `b9136a44`, BSD-3 | Fine-tune LoRA, ghép trọng số vào model gốc | 1.543.304.960 |
| Agent | `Qwen/Qwen3-4B-Instruct-2507`, revision `cdbee75f17c0`, Apache-2.0 | Nạp NF4 4-bit | 4.022.468.096 |
| Adapter agent | LoRA `ckpt/q4b4_all/final` | Nạp cùng model agent | 66.060.288 |

Tổng: **5.631.833.344 tham số (~5,63B)**, dưới trần 6B; riêng LLM và LoRA là 4.088.528.384, dưới 5B. Image chỉ chứa PhoWhisper-ft, adapter agent và cache Qwen đã ghim revision; không chứa Whisper-turbo-ft.

## Build và chạy offline

Từ `lifemate/`, sau khi đặt hai thư mục checkpoint theo tài liệu bàn giao và kiểm SHA-256:

```bash
docker build -t zaic-lifemate:phoft-2026-11-05 .
printf 'public_0002\npublic_0003\npublic_0004\n' > ids_smoke.txt
docker run --rm --gpus all --network none \
  -v "$PWD/../data/train+public_test:/app/data/train+public_test:ro" \
  -v "$PWD/runs:/app/lifemate/runs" \
  -v "$PWD/ids_smoke.txt:/app/lifemate/ids_smoke.txt:ro" \
  -e SPLIT=public_test -e DATA=/app/data/train+public_test \
  -e ASR_MODEL=ckpt/asr_phoft/merged -e ADAPTER=ckpt/q4b4_all/final \
  -e OUT=runs/submission.jsonl -e IDS=ids_smoke.txt \
  zaic-lifemate:phoft-2026-11-05 bash scripts/predict.sh
```

Để chạy đủ public test, bỏ mount `ids_smoke.txt` và biến `IDS`. `predict.sh` dùng mặc định 4-bit, `TIME_BUDGET=25` giây tính cả ASR, và một lượt khởi động agent trước khi chấm mẫu đầu. Image tải Qwen khi build và ghim cache `main` vào revision trên; lúc chạy, `HF_HUB_OFFLINE=1` và `--network none`.

Lệnh `--gpus all` cần NVIDIA Container Toolkit trên host ([hướng dẫn chính thức](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)). Máy kiểm thử RTX 3050 hiện thiếu toolkit; kiểm tra CUDA và smoke test đã dùng bind mount các NVIDIA device và driver library của host vào container, vẫn với `--network none`.

## Kết quả kiểm trên RTX 3050 4 GB, 05/11/2026

- Build thành công; image `zaic-lifemate:phoft-2026-11-05` có `Size=12.635.549.589` byte (~12,6 GB).
- SHA-256 của cả hai file trọng số bên trong image khớp tài liệu bàn giao; quyền file là 644. Cache Qwen offline trỏ đến `cdbee75f17c01a7cc42f958dc650907174af0554`; không có `ckpt/asr_turboft`.
- ASR chạy thành công cho `public_0002`, `public_0003`, `public_0004`. Cả ba transcript **khớp nguyên văn** `runs/e2e_public_phoft_asr.jsonl`. Kết quả smoke được giữ ở `runs/smoke_3050_asr.jsonl` để lượt chạy đầy đủ không tái sử dụng nhầm file ASR chỉ có ba mẫu.
- Agent nạp Qwen 4-bit và LoRA, sau đó hết VRAM trong bước warmup (`torch.OutOfMemoryError`, cần thêm 116 MiB). Vì vậy smoke test chưa tạo `runs/submission.jsonl` hoặc `runs/submission_check.json`; cần chạy lại trên GPU có nhiều VRAM hơn để xác nhận `"ok": true`.

## Giao diện nộp BTC cần làm sau kiểm nội bộ

[Docker Guide LifeMate của BTC](https://dl-challenge.zalo.ai/2026/lifemate_argfzdgert/Docker_Guide_ZAC2026_LifeMate.pdf) ghi máy chấm là RTX 5090 32 GB, driver 595.58.03, CUDA 13.2. Image hiện tại là bản kiểm nội bộ và **chưa đáp ứng đầy đủ hướng dẫn nộp**: base image đang là `python:3.12-slim`; code chạy ở `/app/lifemate` và ghi vào `runs/`; file kết quả không có trường `time`; image chưa có JupyterLab, `/code/start_jupyter.sh`, `predict_notebook.ipynb` hay `training_code/`. BTC yêu cầu image nộp cuối nhận `/data`, ghi `/result/submission.jsonl`, có các tài liệu/code trên, xuất `.tar.gz`, tính MD5 và cung cấp link Google Drive cho phép người có link tải. Cần đóng gói lại trước khi nộp chính thức; kiểm laptop trên image này không thay thế bước đó.

## Thời gian tham khảo

Chưa đo trên GPU 24 GB. Trên laptop RTX 4070, ASR + agent trung bình 10,4 giây/mẫu, p95 21,1 giây/mẫu; PhoWhisper chậm hơn Whisper-turbo trung bình 0,9 giây/mẫu. Những số này không thay cho đo đạc trên máy chấm.
