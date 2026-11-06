# Pilot dữ liệu sinh v2 trên máy anh trai (tối 07/11/2026)

*Claude viết lúc 12:47 ngày 06/11/2026 (giờ máy). Anh duyệt lịch lúc 11:45 ngày 06/11 ("Làm theo lịch"; JOURNAL entry 103–104). Code: [PR #16](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/16), nhánh `synth-v2`, xếp trên PR #11, chưa merge.*

## Tóm tắt

- **Câu hỏi:** dữ liệu sinh cho app chưa thấy, làm theo cách mới (v2), có giúp agent 4B không?
- **Cách đo:**
  - Train đúng công thức của adapter đang nộp (4B 4-bit) trên fit_lao, chấm trên dev_lao (262 mẫu, 6 app bị giấu).
  - So bản gốc với bản có thêm dữ liệu sinh, **mỗi bên 2 seed**, tất cả trên cùng máy anh trai.
- **Luật ghi trước** (`lifemate/scripts/pilot_rule.py`), so trung bình 2 seed của bản v2 với trung bình 2 seed của bản gốc:
  - chữ PhoWhisper-ft tăng ít nhất **+2,0**;
  - chữ chuẩn không giảm quá **2,0**.
  - Đạt cả hai thì sinh tiếp cho 11 app public rồi train bản cuối (lần chạy thứ 2). Không đạt thì dừng, giữ bản 05/11.
- **Anh trai chạy một lệnh** (mục "Lệnh cho anh trai"), khoảng 5–7 giờ, rồi gửi lại hai file.

## Vì sao làm lại (v2)

Pilot 1 (02/11, entry 61) giảm 2,09 điểm, nhưng đó chỉ là một lần train. Mà hai lần train cùng công thức đã lệch tới 4,21 điểm (entry 101), nên kết quả đó chưa nói được gì chắc.

Hai nguyên nhân từng được nghi đều không đúng:
- điền thừa tham số tuỳ chọn;
- quá nhiều mẫu mở đầu bằng lời gọi đọc.

Đo trên 1.283 mẫu thật của fit_lao, các mẫu sinh của pilot 1 khác dữ liệu thật ở chỗ khác:

| | Mẫu thật (fit_lao) | Pilot 1 |
|---|---:|---:|
| Có lịch sử hội thoại | 64% | 0% |
| Câu cuối dùng lại ID lấy từ lịch sử | 16% | 0% |
| Dùng từ hai app trở lên | 48% | 0% |
| Không gọi tool | 8% | 0% |
| Tham số tuỳ chọn điền mỗi lời gọi ghi | 0,32 | 0,31 |
| Mẫu không có lịch sử mở đầu bằng lời gọi đọc | 90% | 89% |

Bản v2 giao cho mỗi mẫu một "khung" rút theo đúng các tỉ lệ thật:

| Khung | Tỉ lệ |
|---|---:|
| Không gọi tool | 7% |
| Kết thúc bằng hỏi lại | 14% |
| Chỉ đọc | 8% |
| Làm việc (execute) | 71% |
| Có lượt trước trả về đối tượng mà câu sau dùng lại | 20% |
| Có đoạn hội thoại thật không liên quan đứng trước | khoảng 45% |
| Dùng thêm một app đã cài (trong các mẫu execute và hỏi lại) | 40% |

Bước kiểm loại mẫu không theo khung, ngoài các bước kiểm cũ (chạy giả lập, solver độc lập giải lại).

## Các lượt (`lifemate/cloud/arms_2026-11-07_synth_v2.txt`)

| GPU | Lượt | Dữ liệu train |
|---|---|---|
| 0 | `q4b4_lao_base_s0`, rồi `q4b4_lao_v2_s1` | fit_lao; rồi fit_lao + dữ liệu sinh v2 |
| 1 | `q4b4_lao_v2_s0`, rồi `q4b4_lao_base_s1` | fit_lao + dữ liệu sinh v2; rồi fit_lao |

- **Công thức:** Qwen3-4B-Instruct-2507 4-bit (QLoRA), AdamW 8-bit, LoRA r32/α64, lr 2e-4, 1 epoch, `--max-len 6144`. Giống hệt `q4b4_fit_lao` (entry 55), chỉ đổi seed.
- **Chấm:** mỗi lượt chấm dev_lao hai lần, trên chữ chuẩn và trên chữ PhoWhisper-ft (chữ của bản nộp). Nạp 4-bit, hạn 60 giây, như các lượt trên laptop.
- **Thứ tự:** nếu lần chạy bị dừng giữa chừng, cặp seed 0 (một lượt mỗi GPU) xong trước nên vẫn có kết quả để đọc.

## Lệnh cho anh trai

**Gói:** `~/zac_cloud_bundle_20261106_synthv2.tar.gz` trên laptop.
- 5.752.327 byte (5,5 MB), sha256 `8314687a327301d30410549489644494250067d5522548d3b49c4accc5c0c6a3`; chỉ chủ máy đọc được.
- **Code:** commit `4769d3a` của `synth-v2`.
- **Dữ liệu:** train và public_test, không có audio; transcript ASR của train, trong đó có chữ PhoWhisper-ft của dev_lao.
- **Dữ liệu sinh:** `gen/synth_lao_v2.jsonl` (202 mẫu) và `gen/sft_synth_lao_v2.jsonl` (652 dòng SFT).
- Không có adapter hay lượt chạy cũ.
- **Gói có dữ liệu thi có licence:** chỉ để trong thư mục Google Drive riêng mà Anh chia sẻ cho anh trai (17:40 ngày 06/11; chế độ "Hạn chế", không bật "Bất kỳ ai có đường liên kết"). Không đưa lên git hay chỗ công khai. Link thư mục không ghi vào repo vì repo công khai.

**Anh đã tải gói lên thư mục Drive** (17:40). Anh gửi anh trai link thư mục, kèm bản hướng dẫn có sẵn link: `cloud_results/anh_trai/BROTHER_AI_GUIDE_PILOT_V2_2026-11-07.md` trên laptop, ngoài git. Bản trong repo là [`BROTHER_AI_GUIDE_PILOT_V2_2026-11-07.md`](BROTHER_AI_GUIDE_PILOT_V2_2026-11-07.md), không có link. File hướng dẫn viết cho AI trợ lý bên máy anh trai đọc: train gì, lệnh nào, kiểm gì, gửi lại gì.

Anh trai đặt gói vào thư mục home rồi chạy lệnh dưới (giống trong file hướng dẫn). Lệnh chạy xong thì tự áp luật bằng `scripts/pilot_rule.py`, ghi vào `lifemate/runs/pilot_v2_rule.txt`:

```bash
mkdir -p ~/zac_v4 && cd ~/zac_v4 && tar -xzf ~/zac_cloud_bundle_20261106_synthv2.tar.gz && cd ZAIC_2026 && nohup bash -c 'if nvidia-smi --query-gpu=compute_cap --format=csv,noheader | awk -F. "\$1<8{bad=1} END{exit bad}"; then SMOKE_MODELS=Qwen/Qwen3-4B-Instruct-2507 SMOKE_TRAIN_ARGS="--load-4bit --optim adamw8bit --max-len 6144" SMOKE_INFER_ARGS=--load-4bit bash lifemate/scripts/cloud_setup.sh && PACK=0 bash lifemate/scripts/cloud_arms.sh lifemate/cloud/arms_2026-11-07_synth_v2.txt; (cd lifemate && .venv/bin/python scripts/pilot_rule.py --base runs/sft_q4b4_lao_base_s0 runs/sft_q4b4_lao_base_s1 --new runs/sft_q4b4_lao_v2_s0 runs/sft_q4b4_lao_v2_s1 --ids splits/dev_lao.txt --json runs/pilot_v2_rule.json > runs/pilot_v2_rule.txt 2>&1); else echo "DUNG: GPU khong co bf16"; nvidia-smi -L; fi; tar -czf ~/zac_v4_results.tar.gz run.log lifemate/runs; echo "XONG $(date)"' > run.log 2>&1 &
```

- Lệnh giải nén vào thư mục mới `~/zac_v4`, nên không đụng tới `~/ZAIC_2026` của lần v3.
- **Thời gian:** cài đặt khoảng 15–30 phút (venv mới; model 4B đã có trong cache từ lần v3), rồi 4 lượt khoảng 5–6 giờ.
- **Xem tiến độ:** `tail -f ~/zac_v4/ZAIC_2026/run.log`. Xong khi dòng cuối có `XONG`.
- **Nộp kết quả lên chính thư mục Drive đó** (17:40): `~/zac_v4_results.tar.gz` (chỉ log và kết quả chấm, không có adapter; khoảng vài chục MB) và báo cáo `ZAIC_pilot_v2_report_<ngày>.md`. Anh tải về `~/Zalo AI Challenge/cloud_results/anh_trai/` rồi báo Claude.
- **Dừng sớm thì vẫn có kết quả:** cặp seed 0 chạy trước trên hai GPU. Nếu cần dừng, anh trai vẫn chạy dòng `tar -czf ~/zac_v4_results.tar.gz ...` trong `~/zac_v4/ZAIC_2026` rồi tải lên Drive.
- **Sau khi đội không cần nữa:** nhờ anh trai xoá `~/zac_v4`, `~/ZAIC_2026`, hai gói và các file kết quả trên máy GPU. Anh xoá gói và kết quả trong thư mục Drive.

## Đã kiểm trên laptop (06/11)

- **Chạy thử ngắn** (12:19–12:30, `~/zac-synth/lifemate/runs/smoke_v2_laptop.log`): train 4-bit 2 bước trên 4.051 dòng fit_lao cộng 41 dòng dữ liệu sinh thử; đỉnh 5,0 GB. Chấm 4-bit, hạn 60 giây, 2 mẫu trên mỗi loại chữ; so sánh chạy hết.
- **Kiểm gói** (12:45): giải nén vào thư mục tạm.
  - 2.317 file khớp manifest, không có audio.
  - 4 file SFT dựng lại giống hệt bản laptop; `fit_lao` là file `96254b3b…` mà `q4b4_fit_lao` đã học.
  - Test đạt.
  - Bản chạy thử (`DRY_RUN`) chia đúng 2 lượt mỗi GPU.

## Dữ liệu sinh v2 (06/11, 12:21–12:44)

- **Model:** muse-wonder-1.0 sinh, muse-spark-1.3 giải lại.
- **Đạt 202/289 mẫu thô (70%).**
  - Theo app: library 41, robot_vacuum 26, loyalty 34, medication 30, video_meeting 32, home_security 39.
  - Bị loại vì: solver giải lại khác 56, không theo khung lượt trước 15, hỏi lại sai luật 7, gần trùng 6, lỗi khác 3.
- **Chi phí:** 8,97 USD, gồm 0,39 USD ước cho 3 lần gọi bị dừng lúc 12:20 (Claude dừng nhầm vì đọc sai số chi). Cộng lượt thử 12 mẫu (0,38 USD), hôm nay tốn 9,36 USD. **Tổng API cả dự án: 52,39/80 USD.**
- **Khung của các mẫu đạt so với mẫu thật:**

  | | Mẫu thật | v2 | Pilot 1 |
  |---|---:|---:|---:|
  | Có lịch sử | 63,8% | 64,9% | 0% |
  | Dùng lại ID từ lịch sử | 16,3% | 14,9% | 0% |
  | Hai app trở lên | 48,0% | 23,8% | 0% |
  | Không gọi tool | 8,1% | 11,4% | 0% |
  | Từ 3 lời gọi trở lên | 42,2% | 15,3% | 37,2% |
  | Tham số tuỳ chọn mỗi lời gọi ghi | 0,32 | 0,38 | 0,31 |

  - Mẫu hai app bị loại nhiều hơn, nên tỉ lệ hai app thấp hơn khung đặt ra (khoảng 34%).
  - Mẫu v2 vẫn ngắn hơn mẫu thật.
- **SFT:** 652 dòng, 1,93 triệu token, khoảng 13% số dòng train (pilot 1: 924 dòng, 1,70 triệu token).

## Chưa kiểm

- **Tốc độ train 4-bit trên RTX 4090:** chưa đo. Bước cài đặt tự đo trước khi chạy và ghi vào `runs/cloud_setup.json`. Ước tính khoảng 2 giờ train và 30 phút chấm mỗi lượt, vậy mỗi GPU khoảng 5 giờ.
- **Quy ước của người gán nhãn với 6 app mới:** không kiểm được nếu không nhìn nhãn dev. Chỉ kết quả pilot đo được ảnh hưởng.
