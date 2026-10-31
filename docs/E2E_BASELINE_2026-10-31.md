# Baseline đầu-cuối: audio → ASR → agent → file nộp (31/10/2026)

*Chạy tự động đêm 30–31/10 sau giai đoạn 2 của D: unit `lifemate-night` từ 03:09 tới 04:05, rồi chạy lại PhoWhisper tới 04:33. Dùng 2 model ASR có sẵn, không fine-tune, và 2 checkpoint SFT có sẵn, không train thêm. Kế hoạch ở JOURNAL entry 21–23. Code: [PR #4](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/4) (`lifemate/asr.py`, `scripts/asr_quality.py`, `scripts/predict.sh`, `scripts/e2e_baseline.sh`) và `scripts/asr_loss.py` ([PR #5](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/5)). Số liệu: [`baselines/e2e_2026-10-31.json`](baselines/e2e_2026-10-31.json).*

## Kết luận

1. **Đọc chữ ASR thay cho chữ chuẩn, agent mất khoảng 20 điểm.** Đây là chỗ mất điểm lớn nhất đã đo, lớn hơn mọi phần sửa agent (làm đủ các vế 6–8 điểm, chọn đúng ID 4–5, ngày giờ 2–4).

   | Agent đọc | dev_random (233) | dev_lao (262, app chưa thấy) |
   |---|---:|---:|
   | Chữ chuẩn `audio_text` (mốc cũ) | 53,92 | 35,53 |
   | **Whisper-large-v3-turbo** | **31,69** (−22,2; [−28,4; −16,1]) | **17,14** (−18,4; [−23,6; −13,3]) |
   | PhoWhisper-large | 27,90 (−26,0; [−32,3; −19,9]) | 15,58 (−19,9; [−25,4; −14,8]) |

   Ngoặc vuông là khoảng tin cậy 95% theo cặp, so với chữ chuẩn.
2. **ASR sai thật, không phải do nhãn lệch.**
   - Cả hai model sai khoảng 1/4 tới 1/3 số từ ở lượt cuối.
   - Ở dev_random, khi hai model nghe gần giống nhau (209/784 câu), chỉ 7 câu khác hẳn `audio_text`. Vậy người nói hiếm khi đọc lệch kịch bản.
3. **WER thấp hơn không có nghĩa là điểm agent cao hơn.** PhoWhisper sai ít từ hơn turbo (lượt cuối 26–27% so với 31%), nhưng điểm agent thấp hơn 3,8 và 1,6 điểm (chưa chắc ở từng tập).
   - PhoWhisper giữ được ít query tìm kiếm hơn: 58% so với 63% ở dev_random, 44% so với 60% ở dev_lao.
   - PhoWhisper không viết hoa (kể cả tên người), không có dấu phẩy, không viết chữ số. Với PhoWhisper, cả những câu sai dưới 10% số từ vẫn mất nhiều điểm (dev_lao 41,2 → 18,1).
   - → Chọn và fine-tune ASR theo **điểm agent và độ đúng của slot**, không theo WER.
4. **Theo luật đặt trước, chọn Whisper-turbo** (điểm cộng gộp 495 mẫu: turbo 23,99, PhoWhisper 21,38).
5. **File nộp public đã sẵn và đã kiểm:** `lifemate/runs/e2e_public_turbo.jsonl`, 634 dòng, `zaic_tools --validate` 0 lỗi. Tạo bằng một lệnh offline (`scripts/predict.sh`, `HF_HUB_OFFLINE=1`). **Chưa nộp.**
6. **Thời gian trên laptop** (RTX 4070 8GB, model đã nạp sẵn): mỗi mẫu trung bình 2,9 giây, p95 5,9 giây, chậm nhất 9,7 giây. Không mẫu nào quá 25 giây. Chưa đo trên A30.
7. **Tái lập:** chạy lại ASR (batch 1) trên 50 wav public cho kết quả giống hệt từng ký tự.

## Chất lượng ASR (trên wav của train; so với `audio_text`)

| | turbo dev_random | turbo dev_lao | Pho dev_random | Pho dev_lao |
|---|---:|---:|---:|---:|
| WER lượt cuối | 31,2 | 31,2 | **25,9** | **26,9** |
| WER lượt cuối, bỏ dấu | 27,8 | 28,0 | 23,2 | 24,1 |
| WER lượt history | 35,0 | 37,8 | **27,5** | **26,2** |
| Giữ đúng số tiền | 7/7 | 3/3 | 7/7 | 2/3 |
| Giữ đúng giờ | 61% | 68% | **75%** | 71% |
| Giữ đúng số nhỏ | 88% | 1/2 | 94% | 1/2 |
| Giữ từ phủ định / huỷ | 80% | 83% | 86% | 86% |
| Giữ query tìm kiếm | **63%** | **60%** | 58% | 44% |
| Câu có chữ số | 26% | 24% | 0% | 0% |

- `audio_text` gần như luôn viết hoa và có dấu câu. Chỉ 10% (dev_random) và 3% (dev_lao) câu có chữ số; còn lại số viết bằng chữ.
- "Giữ đúng" so dạng nói tương đương: "50 nghìn" khớp "năm mươi nghìn". Số tiền và số nhỏ có ít mẫu, chỉ để tham khảo.
- **Ảo giác kiểu Whisper** ("Cảm ơn các bạn đã theo dõi"…): turbo 13 và 17 mẫu có ít nhất một lượt bị, 22/1.933 wav public. PhoWhisper gần như không bị (1 mẫu mỗi tập). Đóng góp nhỏ vào phần mất điểm.

## Mất điểm ở đâu

**Theo WER của lượt cuối** (turbo; "mất" = số điểm trên tổng 100 mất trong nhóm, cộng lại bằng tổng mất):

| WER lượt cuối | dev_random: số mẫu / chữ chuẩn / ASR / mất | dev_lao: số mẫu / chữ chuẩn / ASR / mất |
|---|---|---|
| < 10% | 21 / 32,1 / 33,3 / −0,1 | 22 / 39,0 / 25,4 / 1,2 |
| 10–25% | 76 / 63,4 / 48,4 / 4,9 | 74 / 32,8 / 20,7 / 3,4 |
| 25–50% | 98 / 49,2 / 23,7 / **10,8** | 126 / 37,2 / 17,1 / **9,7** |
| ≥ 50% | 38 / 59,1 / 18,1 / 6,7 | 40 / 33,4 / 6,1 / 4,2 |

- Chỉ khoảng 9% số mẫu có lượt cuối sai dưới 10% số từ. Phần lớn điểm mất nằm ở nhóm sai 25–50%.
- **Model hay bỏ cuộc hơn:** số mẫu không gọi tool nào tăng từ 19 lên 43 (dev_random) và từ 10 lên 39 (dev_lao). File public có 106/634 dòng rỗng (17%), khớp với mức trên dev.
- **Mẫu không có history cũng mất nhiều** (dev_random 59,8 → 32,6). Vậy riêng lượt cuối đã làm mất phần lớn điểm. Muốn tách chính xác lượt cuối và history thì cần thí nghiệm 2×2 (Q11, leader).

**Câu turbo sai nhiều nhất** (để nghe; chỉ id, tất cả thuộc train): `train_0430`, `train_0880`, `train_1573`, `train_1510`, `train_1343`, `train_0543`, `train_0683`, `train_1061`, `train_0381`, `train_0033`, `train_1348`, `train_0483`, `train_1203`, `train_1480`, `train_1505`, `train_1479`, `train_1066`, `train_1695`.

## File nộp public

| Mục | Kết quả |
|---|---|
| File | `lifemate/runs/e2e_public_turbo.jsonl` (chỉ có trên máy Anh) |
| Model | Whisper-large-v3-turbo + `ckpt/q17b_fit_random/final` (Qwen3-1.7B LoRA) |
| Kiểm | 634/634 dòng, id khớp, không trùng; `zaic_tools --validate`: 0 lỗi; 1.198 call; 106 dòng rỗng |
| ASR (batch 1) | Tính theo mẫu: trung bình 0,51 giây, p95 1,52, chậm nhất 1,98. Tính theo wav: trung bình 0,17 giây (1.933 wav) |
| Agent | Trung bình 2,37 giây, p95 5,29, chậm nhất 9,44 |
| Tổng mỗi mẫu | Trung bình 2,88 giây, p95 5,91, chậm nhất 9,74; không mẫu nào quá 25 hay 30 giây |
| Tái lập | Chạy lại ASR 50 wav: 0 khác |

- **Dự đoán điểm public:** khoảng 17–32, theo hai tập dev. Public có thể có app mới, nên gần dev_lao hơn thì sẽ thấp.
- Thời gian trên không gồm thời gian nạp model (4–7 giây cho ASR, cộng thời gian nạp LLM). Chưa đo trên A30.

## Ý nghĩa cho kế hoạch

1. **ASR lên ưu tiên số 1.**
   - **Fine-tune ASR trên audio train** (wav của fit, nhãn `audio_text`; không dùng wav dev để còn đo; không dùng audio public). Phần này của leader, cần GPU cloud.
   - Đánh giá bằng điểm agent và độ đúng của slot, không chỉ WER.
2. **Train agent trên chữ ASR** (cùng công thức, chữ đầu vào lấy từ ASR thay cho `audio_text`).
   - Mục đích: agent quen với lỗi và kiểu chữ của ASR. Cách này cũng cho biết PhoWhisper có thắng không khi agent đã quen kiểu chữ không viết hoa của nó.
   - Bộ công cụ cloud đã hỗ trợ (`ASR_FIT`, `ASR_DEV`, PR #6); transcript ASR của toàn bộ wav train tạo đêm nay.
   - Khi dùng ASR đã fine-tune trên chính wav train, transcript dùng cho SFT phải là k-fold. Nếu không, ASR "thuộc lòng" câu train và chữ đầu vào sạch hơn thực tế.
3. **Chuẩn hoá chữ của ASR** (viết hoa tên, dấu câu, chữ số ↔ chữ) là hướng rẻ để thử sau, nếu train trên chữ ASR chưa đủ.
4. **Không đổi:** dùng luật chọn đặt trước. Turbo là ASR của file nộp hôm nay.

## Giới hạn

- **Chỉ đo trên wav của train** (dev_random và dev_lao). WER trên public không đo được vì không có nhãn, và không được gán nhãn.
- **Batch khác nhau giữa hai model ASR** (turbo 16, PhoWhisper 4, do hết bộ nhớ GPU 8 GB). Batch gần như không ảnh hưởng: chạy turbo lại trên toàn bộ wav train (batch ghép khác hẳn) cho 1.901 wav dev giống hệt từng ký tự.
- **Checkpoint agent chưa từng thấy chữ ASR**, chỉ thấy `audio_text`, kèm 30% câu viết thường bỏ dấu câu lúc train.
- **dev_random và dev_lao có một số mẫu chung**, nên không cộng số mẫu của hai tập như hai tập độc lập.

## Chạy lại

```bash
cd lifemate
bash scripts/e2e_baseline.sh > runs/e2e_baseline.log 2>&1     # bỏ qua bước đã xong
.venv/bin/python scripts/asr_loss.py --asr turbo --public runs/e2e_public_turbo_asr.jsonl --json runs/asr_loss_turbo.json
.venv/bin/python scripts/asr_loss.py --asr pho --json runs/asr_loss_pho.json
```

PhoWhisper trên GPU 8 GB cần `--batch-size 4` (lệnh trong `lifemate/runs/e2e_pho.log`).
