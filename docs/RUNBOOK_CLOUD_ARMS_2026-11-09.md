# Chạy các nhánh thử trên GPU thuê (09–10/11/2026)

*Claude viết ngày 08/11/2026. Kế hoạch: `docs/RANKING_FINAL_WEEK_2026-11-08.md`.*

## 1. Đã sẵn

Toàn bộ code nằm ở nhánh **`search-guard`** (worktree `/home/nguyenletuan/Desktop/zaic-d5`), tách từ `docker-submit`. Mới commit local, **chưa push**.

| Commit | Nội dung |
|---|---|
| `3b40685` | **D5:** lớp chống tìm kiếm rỗng và vòng lặp đọc (`--search-guard`, `SEARCH_GUARD=1`), mặc định tắt. Test: phát lại đáp án 1.545 mẫu train với lớp chống bật được 99,98 |
| `43ccbe2` | **D2:** `lifemate.rationale` (sinh lý lẽ bằng Meta), `sft --thoughts` (khối `<think>` trong dữ liệu train), agent giữ khối `<think>` trong ngữ cảnh. Không bật `--thoughts` thì dữ liệu SFT giống từng byte bản cũ; `check_sft.py` vẫn 1544/1545 |
| `ed26568` | `train --lora-targets` (Qwen3.5 cần thêm `in_proj_qkv`, `in_proj_z`, `out_proj`) |
| `8202b17` | File nhánh `lifemate/cloud/arms_2026-11-09_models_d2.txt` (A0–A3, 7 lượt) và các biến `THOUGHTS`, `LORA_TARGETS`, `MODELS` cho script cloud |
| `c914602` | Script đóng gói đọc được `data/` dạng symlink |
| `eb6a85f` | `brother_run.sh` (một lệnh: khoá chống chạy trùng, chạy tiếp sau khi ngắt, giai đoạn 1 cùng lượt public D5, luật, giai đoạn 2, đóng gói), `arms_rule.py` (luật tự động), `final_train.sh` (train trên đủ dữ liệu rồi làm file public) |

**Dữ liệu tạo trên máy này** (không vào git):
- `lifemate/gen/rationale_d2all.jsonl`: lý lẽ cho 1.545 mẫu train (đang chạy; thử 20 mẫu đạt 20/20, 0,006 USD/mẫu);
- `lifemate/asr/train_dev_union_phoft.jsonl`: transcript PhoWhisper-ft cho 458 mẫu dev, chạy bằng image 05/11 trên RTX 3050 (đang chạy).

## 2. Thuê máy

- **GPU:** 4× RTX 4090 24 GB, hoặc 2× nếu muốn rẻ hơn (lâu gấp đôi). A100/H100 cũng được.
- **Driver:** cài được torch 2.15. Script tự thử bản CUDA 13.2, 13.0, 12.8, 12.6. Lần trước một máy 3090 với driver 570 đã hỏng ở bước này, nên chọn máy có driver ≥ 580 nếu trang thuê cho lọc.
- **Ổ đĩa ≥ 150 GB, RAM ≥ 64 GB, Ubuntu,** có Internet (tải model ở bước cài).
- **Thời gian và tiền** (ước theo số đo cũ: 4090 train 4B 4-bit khoảng 1.430 token/giây):
  - mỗi lượt khoảng 2,5 giờ train + 1 giờ chấm (2 loại chữ), tức khoảng 3,5 giờ;
  - 7 lượt trên 4 GPU khoảng 2 vòng, tức khoảng 7–8 giờ;
  - giá 0,35–0,7 USD/GPU-giờ, tổng khoảng **15–25 USD**;
  - cộng thêm lượt public C0 + D5 (mục 4) khoảng 1–1,5 giờ trên một GPU.
- **Gói chứa dữ liệu thi có licence:** chỉ đưa lên máy thuê riêng của đội; xong thì xoá máy.

## 3. Hai cách vận hành, bạn chọn một

- **(a) Claude làm qua SSH (nhanh nhất):** bạn thuê máy, thêm host vào `~/.ssh/config` trên máy này (ví dụ `Host zac-gpu`), rồi nhắn "máy là zac-gpu". Claude tạo gói, `scp` lên, cài, chạy, theo dõi và lấy kết quả về.
- **(b) Bạn tự chạy:** Claude tạo gói `~/zac_cloud_bundle_20261109_arms.tar.gz`. Bạn tải lên máy và chạy đúng một lệnh, giống hệt lệnh cho máy anh trai (`docs/BROTHER_AI_GUIDE_ARMS_2026-11-09.md`, mục B4):

  ```bash
  mkdir -p ~/zac_v5 && cd ~/zac_v5 && tar -xzf ~/zac_cloud_bundle_20261109_arms.tar.gz && cd ZAIC_2026 && nohup bash lifemate/scripts/brother_run.sh > run.log 2>&1 &
  ```

  Lệnh tự làm hết: cài đặt, giai đoạn 1 (7 lượt cùng lượt public D5), áp luật, giai đoạn 2, đóng gói `~/zac_v5_results.tar.gz`. Chạy lại đúng lệnh (không giải nén lại) thì tiếp từ chỗ dừng. Xong thì gửi lại file đó.

## 4. Lượt public C0 + D5 (đo D5 bằng điểm public thật)

Không cần train. Dùng đúng adapter `ckpt/q4b4_all/final` và đúng transcript public của bản 51,16 (`runs/e2e_public_phoft_asr.jsonl`), chỉ bật thêm lớp chống. Gói kèm sẵn hai thứ này, và `brother_run.sh` tự chạy lượt này trên GPU cuối, song song với giai đoạn 1. Kết quả ra `lifemate/runs/pub_c0_guard.jsonl`, đã kiểm định dạng, khoảng 2–3 giờ sau khi bắt đầu.

Xong thì Claude so từng dòng với file 51,16, rồi bạn nộp. **Luật:** giữ D5 nếu điểm ≥ 51,07 − 0,3.

## 5. Sau khi có kết quả (Claude làm)

- Chấm và so theo cặp từng nhánh với A0 (cùng máy) và với 3 lượt C0 cũ.
- Áp luật đã viết trong file nhánh: thắng khi trung bình 2 seed trên dev_lao chữ PhoWhisper-ft ≥ mốc + 3,0, và chữ chuẩn không giảm quá 2,0.
- Nhánh thắng thì train lại trên đủ train (2 seed), làm file public, nộp. Rồi chốt model vào image trước khoảng 13/11.
