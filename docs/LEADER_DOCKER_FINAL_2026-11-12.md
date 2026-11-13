# Leader: Docker nộp cuối dùng Qwen3.5 + adapter gộp (12/11/2026)

*Claude viết lúc 23:05 ngày 12/11/2026 (giờ máy, EST), theo yêu cầu của Anh. Bối cảnh: JOURNAL entry 152–154, HUMAN_TODO B61, L9.*

## Vì sao đổi

- Hệ thống mới đạt **59,42** trên public. Bản 05/11 đang có trong Docker đạt 51,16.
- Phần đổi là LLM: `principled-intelligence/Qwen3.5-4B-text-only` thay Qwen3-4B-Instruct-2507, cộng adapter gộp hai seed `v7q35_avg` và bật search guard (D5). ASR giữ PhoWhisper-ft như cũ.
- Model gốc 4B, adapter 122 triệu tham số, cộng lại 4,33 tỷ, dưới 5 tỷ. Cả hệ thống tính thêm ASR khoảng 5,87 tỷ. BTC xác nhận Qwen3.5-4B tính là 4B (FAQ 11/11).

## Code

- Nhánh **`docker-final`**, PR: [PR #19](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/19) (commit `a021fdf`, vào nhánh `train-only-sft`). Nhánh này đi từ commit `a71ea32`, đúng code đã ra file 59,42, và chỉ đổi giá trị mặc định:
  - `lifemate/docker/predict.sh` (thành `/code/predict.sh`)
  - `lifemate/lifemate/submit.py` (notebook đọc giá trị ở đây)
  - `lifemate/scripts/predict.sh`
- Thư viện: như image cũ, cài theo `lifemate/requirements-lock.txt` (transformers 5.21.0). Laptop chạy Qwen3.5 bằng đúng bản transformers này.
- Khi tải model, transformers báo `causal_conv1d` và `flash-linear-attention` chưa cài nên dùng bản PyTorch chậm hơn. **Không cài thêm:** mọi file đã chấm đều chạy như vậy, và trên RTX 4090 thời gian vẫn trung bình 8,3 giây mỗi mẫu.

## File Anh gửi riêng

Không commit các file này lên repo, vì repo đang public.

| File | Cỡ | Ghi chú |
|---|---|---|
| `~/gui_leader_v7q35avg_2026-11-12.tar` | 508.907.520 byte | sha256 `202f7227cf7ffaf4b83cfd687456317d4cc062817a7a9182ffba7c57dc3802dc` |

Giải nén trong `lifemate/` là các thư mục vào đúng chỗ:

- `ckpt/v7q35_avg/final/`: adapter gộp. `adapter_model.safetensors` sha256 `7f69d43e8a2a438d…` (487.642.432 byte). Các file trong gói đã để quyền đọc cho mọi user.
- `runs/public_v7q35_avg.jsonl` và `runs/public_v7q35_avg_trace.jsonl`: file public 59,42 và trace của nó, dùng để so.

ASR `ckpt/asr_phoft/merged` Leader đã có từ 05/11 (sha256 `421a3f62…`), không gửi lại.

## Việc leader làm và kiểm

1. **Kiểm sha256** của gói và của `adapter_model.safetensors` như bảng trên.
2. **Model gốc trong cache Hugging Face của image** (máy chấm không có mạng):
   ```bash
   huggingface-cli download principled-intelligence/Qwen3.5-4B-text-only --revision efe91c59becdb61ece99546002ab3ce51606ea1b
   ```
   Sau đó `refs/main` trong thư mục cache của model phải là `efe91c59becdb61ece99546002ab3ce51606ea1b`. Nếu không, ghi giá trị đó vào file `refs/main`, vì code nạp model bằng tên, không kèm revision.
   Có thể gỡ Qwen3-4B-Instruct-2507 và adapter `q4b4_all` khỏi image: không còn dùng.
3. **Lệnh chạy** không đổi: `/bin/bash /code/predict.sh`, không biến môi trường. Dòng đầu stdout phải ghi:
   ```
   system: ASR ckpt/asr_phoft/merged | LLM principled-intelligence/Qwen3.5-4B-text-only + LoRA ckpt/v7q35_avg/final (4-bit=1) | budget 25s/sample | warm-up=1 | seed 0 | search guard=1
   ```
4. **Chạy thử trong Docker, tắt mạng.** Dùng `IDS` như lần trước, ví dụ 12 mẫu Claude đã chạy trên laptop:
   ```bash
   printf 'public_0571\npublic_0424\npublic_0277\npublic_0328\npublic_0538\npublic_0106\npublic_0176\npublic_0615\npublic_0222\npublic_0371\npublic_0505\npublic_0108\n' > ids_smoke.txt
   ```
   - `submission_check.json` có `"ok": true`.
   - So từng dòng với `runs/public_v7q35_avg.jsonl`. Trên laptop (ngoài Docker, 23:00 ngày 12/11), 11/12 dòng giống hệt cả call lẫn `state_hash`. Dòng `public_0571` khác vì trong file 59,42 nó rỗng (laptop khựng 110 giây trước khi model chạy); lần chạy thử ra 2 call, giống cả hai seed. Chữ ASR của 20 wav giống hệt file chữ ASR 05/11. Trên GPU khác có thể lệch vài dòng do số học; lệch nhiều thì báo Claude.
   - Laptop đo được: nạp model 18,8 giây; mỗi mẫu trung bình 7,5 giây, tối đa 11,1 giây.
5. **Thời gian:** file 59,42 chạy trên laptop (RTX 4070 8 GB, hạn 35 giây). Trên RTX 4090 cùng model, mỗi mẫu trung bình 8,3 giây, p95 khoảng 14 giây, không mẫu nào quá 25 giây. Nếu máy chấm là A30, cần đo lại trong Docker: báo Claude p95 và số mẫu quá 25 giây.
