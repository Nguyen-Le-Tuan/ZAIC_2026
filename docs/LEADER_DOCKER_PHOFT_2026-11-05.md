# Leader: đổi ASR trong Docker sang PhoWhisper-ft (05/11/2026)

*Claude viết lúc 08:54 ngày 05/11/2026 (giờ máy), theo yêu cầu của Anh. Bối cảnh: JOURNAL entry 85–87, HUMAN_TODO B26.*

## Vì sao đổi

- Bản nộp public dùng PhoWhisper-large fine-tune (adapter leader train trên Colab, L3) đạt **51,16**. Bản Whisper-turbo fine-tune đạt **46,29**, tức tăng 4,87 điểm.
- Hai bản chỉ khác nhau ở ASR. Agent `q4b4_all/final` và code giữ nguyên.
- Luật ghi trước khi nộp (HUMAN_TODO B24): public ≥ 46,29 thì Docker đổi sang PhoWhisper-ft.
- **Code không phải sửa:** `predict.sh` nhận model ASR qua biến `ASR_MODEL`.

## File Anh gửi riêng

Không commit các file này lên repo, vì repo đang public.

| File (trên laptop của Anh, trong `~/zac-c3/lifemate/`) | Cỡ | Ghi chú |
|---|---|---|
| `ckpt/asr_phoft/merged/` (6 file) | 2,9 GB | PhoWhisper-ft đã ghép, đúng bản cho ra 51,16 |
| `ckpt/q4b4_all/final/` (6 file) | 263 MB | Adapter agent. Đã nhận hôm 04/11 thì bỏ qua |
| `runs/e2e_public_phoft_asr.jsonl` | 344 KB | Tham chiếu: chữ ASR public trên laptop |
| `runs/e2e_public_q4b_all_phoft.jsonl` | 203 KB | Tham chiếu: file nộp 51,16 |
| `runs/e2e_public_q4b_all_phoft_trace.jsonl` | 995 KB | Tham chiếu: thời gian và cách dừng của từng mẫu |

Gói tất cả thành một file, giữ nguyên đường dẫn. Giải nén file này trong `lifemate/` là các thư mục vào đúng chỗ:

```bash
cd ~/zac-c3/lifemate && tar -cf ~/gui_leader_phoft_2026-11-05.tar ckpt/asr_phoft/merged ckpt/q4b4_all/final runs/e2e_public_phoft_asr.jsonl runs/e2e_public_q4b_all_phoft.jsonl runs/e2e_public_q4b_all_phoft_trace.jsonl
```

## Việc leader làm và kiểm

1. **Kiểm sha256 sau khi nhận:**
   - `ckpt/asr_phoft/merged/model.safetensors`: `421a3f62f45438c6248c338e605f5833dcabb651166ff69341880cc197c12b3f`
   - `ckpt/q4b4_all/final/adapter_model.safetensors`: `b786659c3fdf0ca7d57aad9ae6cf9aca2c6596bae40b61edec9f30018c20bc7c`
2. **Code và thư viện:**
   - Lấy code từ nhánh `q4b-laptop`. Code agent đổi lần cuối ở commit `2c56672` ([PR #12](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/12)).
   - Cài theo `lifemate/requirements-lock.txt`. Bản ghép được lưu bằng transformers 5.21.0, nên phải dùng đúng bản này: file `processor_config.json` là định dạng của transformers 5.
3. **Model trong image:**
   - Đặt thư mục ASR ở `lifemate/ckpt/asr_phoft/merged` và adapter ở `lifemate/ckpt/q4b4_all/final`.
   - `Qwen/Qwen3-4B-Instruct-2507` (revision `cdbee75f17c0`) phải nằm sẵn trong cache Hugging Face của image, vì máy chấm không có mạng.
   - Gỡ Whisper-turbo-ft khỏi image: không còn dùng, và gỡ đi thì tổng tham số rõ ràng hơn.
4. **Quyền file:** `model.safetensors` và `adapter_model.safetensors` đang để quyền 600. Nếu container chạy bằng user khác root, chạy `chmod 644` trước khi COPY.
5. **Lệnh chạy.** Các biến khác để mặc định: 4-bit, `TIME_BUDGET=25` (đã tính giây ASR), bước khởi động bật.

   ```bash
   SPLIT=public_test DATA=<thư mục dữ liệu> ASR_MODEL=ckpt/asr_phoft/merged ADAPTER=ckpt/q4b4_all/final OUT=runs/submission.jsonl bash scripts/predict.sh
   ```

   Chú thích ở đầu `predict.sh` vẫn ghi hệ thống cũ (turbo-ft + `q4b4_fit_random`). Cứ chạy theo các biến ở trên.
6. **Chạy thử trong Docker, tắt mạng, với 3 mẫu.**
   - Tạo file id (mỗi dòng một id, đường dẫn tính từ `lifemate/`), rồi thêm `IDS=<file>` vào lệnh ở bước 5:
     ```bash
     printf 'public_0002\npublic_0003\npublic_0004\n' > ids_smoke.txt
     ```
   - Kiểm `runs/submission_check.json` có `"ok": true`.
   - So chữ ASR các wav của 3 mẫu này với `runs/e2e_public_phoft_asr.jsonl`. Kết quả phải giống, hoặc chỉ lệch vài từ vì fp16 trên máy khác.
   - Nếu GPU 4 GB không chạy nổi bước agent thì báo lại.
7. **Thời gian:** chưa đo trên GPU 24 GB như A30. Số trên laptop (RTX 4070 8 GB, hạn 60 giây) để tham khảo:
   - ASR + agent mỗi mẫu: trung bình 10,4 giây, p95 21,1 giây.
   - PhoWhisper chậm hơn turbo trung bình 0,9 giây mỗi mẫu, nhiều nhất khoảng 3,4 giây.
   - Khi có GPU 24 GB: chạy đủ public, đếm số mẫu dừng vì hết giờ (`"stop": "time"` trong trace). So với file 51,16 thì không thể giống hệt, vì khác GPU, hạn 25 giây thay vì 60, và có bước khởi động.
8. **Ghi vào mô tả giải pháp:**
   - ASR: `vinai/PhoWhisper-large` revision `b9136a44`, giấy phép BSD-3, fine-tune LoRA rồi ghép: 1.543.304.960 tham số.
   - LLM: `Qwen/Qwen3-4B-Instruct-2507`, giấy phép Apache-2.0, nạp 4-bit: 4.022.468.096 tham số, cộng LoRA 66.060.288 tham số.
   - Tổng khoảng 5,63B, dưới trần 6B (LLM dưới 5B).

## Báo lại cho Anh

- Docker build được chưa, image nặng bao nhiêu.
- Chạy thử 3 mẫu có `"ok": true` không, chữ ASR có khớp file tham chiếu không.
- Có lỗi gì khi nạp model trong Docker.
