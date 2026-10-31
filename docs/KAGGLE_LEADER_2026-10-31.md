# Nhờ leader: train dự phòng trên Kaggle (31/10/2026)

*Anh nhờ leader chạy vì tài khoản Kaggle của Anh chưa xác minh số điện thoại, nên chưa bật được Internet. Bối cảnh và lý do chọn Kaggle: [`FREE_GPU_2026-10-31.md`](FREE_GPU_2026-10-31.md). Phần dưới đây là tin nhắn gửi leader, kèm ô lệnh hoàn chỉnh.*

---

Chào bạn, mình nhờ bạn chạy giúp một lượt train dự phòng trên Kaggle. Bạn chỉ mất khoảng 10 phút thao tác; máy tự chạy 8–11 giờ.

**Mục đích:** train dự phòng 2 lượt **agent Qwen3-1.7B** (không phải ASR) trên GPU T4 miễn phí của Kaggle, phòng khi máy Google của anh mình không train được. Tài khoản Kaggle của mình chưa xác minh số điện thoại nên không bật được Internet.

**Cần có:**
- Tài khoản Kaggle **đã xác minh số điện thoại** (để bật Internet).
- File `zac_cloud_bundle_20261031_v3.tar.gz` (256 MB) mình gửi riêng cho bạn. File có dữ liệu thi: không chia sẻ cho ai, để **Private**, và xoá khi xong.

**Các bước:**
1. Kaggle → **Datasets → New Dataset**: kéo file vào, đặt tên (ví dụ `zac-bundle`), để **Private**, bấm Create. Chờ tải lên xong.
2. Kaggle → **Code → New Notebook**.
3. Ở cột bên phải (Settings / Session options):
   - **Accelerator: GPU T4 x2** (không chọn P100).
   - **Internet: On**.
   - **Add Input** → Your Datasets (Your Work) → chọn `zac-bundle`.
4. Xoá ô có sẵn, dán **toàn bộ** ô lệnh bên dưới vào một ô. Không sửa gì.
5. Bấm **Save Version** (góc trên bên phải) → chọn **Save & Run All (Commit)** → Save. Đóng trình duyệt cũng được.
6. Khoảng 2 phút sau, mở bản vừa lưu và xem **Logs**:
   - Phải thấy dòng `OK: 2 x Tesla T4; có Internet; gói ...; ổ trống ...`.
   - Nếu thấy dòng `LỖI: ...`, làm theo lời nhắc trong dòng đó (bật GPU T4 x2, bật Internet, hoặc Add Input), rồi Save Version lại.
7. Khoảng 30–40 phút sau, log có dòng dạng `2 GPU, ~X h/epoch, ... -> train 2/2 arm(s)`. Chụp màn hình dòng này gửi mình: đó là tốc độ T4 đo thật.
8. Khi chạy xong (8–11 giờ; Kaggle dừng mọi phiên ở 12 giờ), mở bản đã lưu → tab **Output** → tải về:
   - `zac_logs.tar.gz` (luôn có);
   - `cloud_results_*.tar.gz` (có khi đã train; khoảng 0,3–0,5 GB).

   Gửi mình cả hai file.
9. Xoá dataset (trang dataset → Settings → Delete) và xoá notebook, vì có dữ liệu thi và kết quả train.

**Lưu ý:**
- Lượt này dùng khoảng 10–12 giờ trong khoảng 30 giờ GPU mỗi tuần của tài khoản bạn. Nếu bạn cần số giờ đó để fine-tune ASR thì báo mình trước.
- Ô lệnh tự kiểm GPU, Internet, gói và dung lượng ổ. Sau đó nó tự cài đúng phiên bản thư viện, tự tải model và đo tốc độ T4. Nếu T4 quá chậm, nó chỉ đo rồi dừng (mất khoảng 1 giờ), và vẫn để lại file log.
- Lỗi gì cũng gửi mình file `zac_logs.tar.gz` (hoặc ảnh chụp log). Đừng sửa code trên Kaggle.

**Ô lệnh** (dán nguyên văn vào một ô của notebook):

```bash
%%bash
# ZAC 2026: train dự phòng agent Qwen3-1.7B trên GPU T4 miễn phí (Kaggle "GPU T4 x2", hoặc Colab T4).
# Chỉ sửa dòng ARMS nếu cần. Hướng dẫn: docs/KAGGLE_LEADER_2026-10-31.md trong repo ZAIC_2026 (nhánh main).
ARMS="asr up"   # asr = học trên chữ Whisper-turbo; up = công thức B-up; pho = học trên chữ PhoWhisper
BUNDLE=zac_cloud_bundle_20261031_v3.tar.gz
START=$(date +%s); W=$HOME/zac
say() { echo "[$(date '+%H:%M:%S')] $*"; }
if [ -d /kaggle/input ]; then IN=/kaggle/input; OUT=/kaggle/working; else IN=/content/drive/MyDrive; OUT=/content/drive/MyDrive/zac_out; fi
pack() {
  cd "$W/ZAIC_2026" 2>/dev/null || return 0
  tar -czf "$OUT/zac_logs.tar.gz" setup.log plan.log arms.log arms_t4.txt lifemate/runs/cloud_* 2>/dev/null
  mv cloud_results_*.tar.gz "$OUT/" 2>/dev/null
  say "File cần gửi về:"; ls -la "$OUT" | grep -E "zac_logs|cloud_results"
}

# 0. Kiểm tra trước khi cài
GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null)
echo "$GPU" | grep -q T4 || { say "LỖI: cần GPU T4 (Kaggle: Settings > Accelerator > GPU T4 x2). Đang có: ${GPU:-không có GPU}"; exit 1; }
curl -sfI https://huggingface.co >/dev/null || { say "LỖI: không có Internet (Kaggle: Settings > Internet > On; cần xác minh số điện thoại)"; exit 1; }
B=$(find "$IN" -name "$BUNDLE" 2>/dev/null | head -1)
D=$(find "$IN" -maxdepth 6 -type d -name ZAIC_2026 2>/dev/null | head -1)
[ -n "$B$D" ] || { say "LỖI: không thấy $BUNDLE trong $IN (Kaggle: Add Input > Your Datasets)"; exit 1; }
FREE=$(df -BG --output=avail "$HOME" | tail -1 | tr -dc 0-9)
[ "${FREE:-0}" -ge 30 ] || { say "LỖI: ổ chỉ còn ${FREE}G trống, cần ít nhất 30G"; exit 1; }
say "OK: $(echo "$GPU" | wc -l) x $(echo "$GPU" | head -1); có Internet; gói ${B:-$D}; ổ trống ${FREE}G"

# 1. Giải nén và cài đặt (khoảng 20-40 phút)
mkdir -p "$OUT" "$W" && cd "$W" || exit 1
if [ -n "$B" ]; then tar -xzf "$B"; else cp -r "$D" .; fi
cd ZAIC_2026 || exit 1
say "Đang cài đặt (log: setup.log)..."
SMOKE_MODELS=Qwen/Qwen3-1.7B bash lifemate/scripts/cloud_setup.sh > setup.log 2>&1 || { say "LỖI khi cài, 25 dòng cuối:"; tail -25 setup.log; pack; say "DỪNG: gửi zac_logs.tar.gz cho Anh"; exit 0; }  # exit 0: Kaggle keeps the output

# 2. Đo tốc độ, chỉ chọn những lượt kịp xong trong phiên 12 giờ
NGPU=$(nvidia-smi -L | wc -l) START=$START ARMS="$ARMS" python3 - > plan.log 2>&1 <<'PY'
import json, os, time
h = json.load(open("lifemate/runs/cloud_setup.json"))["smoke"]["Qwen/Qwen3-1.7B"]["rough_hours_per_epoch"]
ngpu, left = int(os.environ["NGPU"]), 11.0 - (time.time() - int(os.environ["START"])) / 3600  # sessions stop at 12 h
arm = 1.2 * h + 1.0  # one epoch (+20% for a rough estimate) + two rollouts and the dev loss
base = "FIT=fit_random DEV=dev_random REF=runs/sft_q17b_fit_random"
lines = {
    "asr": f"train TAG=q17b_random_asrtrain_t4 {base} ASR_FIT=asr/train_all_turbo.jsonl "
           "ASR_DEV=asr/train_dev_random_turbo.jsonl REF_ASR=runs/sft_q17b_fit_random_asrturbo",
    "up": f"train TAG=q17b_random_up_t4 {base} EXTRA_SAMPLES=gen/up_real_asks_random.jsonl TRAIN_ARGS=--max-steps,260 "
          "ASR_DEV=asr/train_dev_random_turbo.jsonl REF_ASR=runs/sft_q17b_fit_random_asrturbo",
    "pho": f"train TAG=q17b_random_asrtrain_pho_t4 {base} ASR_FIT=asr/train_all_pho.jsonl "
           "ASR_DEV=asr/train_dev_random_pho.jsonl REF_ASR=runs/sft_q17b_fit_random_asrpho",
}
want = [lines[k] for k in os.environ["ARMS"].split() if k in lines]
n = max(k for k in range(len(want) + 1) if -(-k // ngpu) * arm <= left)
arms = want[:n]
if (n // ngpu) * arm + 0.5 <= left:  # re-score the laptop's adapter on T4: how far T4 numbers are from the laptop's
    arms.append("eval TAG=q17b_fit_random_t4 ADAPTER=ckpt/q17b_fit_random/final DEV=dev_random REF=runs/sft_q17b_fit_random")
open("arms_t4.txt", "w").write("".join(a + "\n" for a in arms))
print(f"{ngpu} GPU, ~{h} h/epoch, {left:.1f} h left -> train {n}/{len(want)} arm(s)"
      + (f"; {len(want) - n} skipped: too slow for one session" if n < len(want) else ""))
PY
cat plan.log

# 3. Train và chấm (vài giờ), rồi gom file kết quả
if [ -s arms_t4.txt ]; then say "Đang train (log: arms.log)..."; bash lifemate/scripts/cloud_arms.sh arms_t4.txt > arms.log 2>&1; tail -8 arms.log; fi
pack
say "XONG"
```

---

## Ghi chú cho Anh và Claude

- **Lượt chạy:**
  - Mặc định `ARMS="asr up"`: hai lượt dự phòng cho máy anh trai.
  - Laptop đang chạy đúng hai lượt này (JOURNAL entry 37). Muốn Kaggle cho thêm thông tin mới thay vì trùng, đổi thành `ARMS="pho asr"`: lượt học trên chữ PhoWhisper chưa ai chạy, và giúp leader chọn ASR.
  - Tên lượt có đuôi `_t4`, nên không trùng lượt của laptop hay máy anh trai.
  - Nếu còn giờ, ô lệnh chấm lại adapter 1.7B của laptop trên T4 (`q17b_fit_random_t4`). Lượt này cho biết số trên T4 lệch số trên laptop bao nhiêu.
- **Đã kiểm:** thử bằng script giả ở 11 trường hợp:
  - chạy bình thường;
  - Kaggle tự giải nén gói;
  - chọn 3 lượt;
  - T4 quá chậm;
  - máy P100;
  - không có Internet;
  - quên Add Input;
  - cài lỗi (vẫn để lại file log);
  - Colab 1 GPU.

  Các thông báo và file ra đều đúng.
- **Chưa kiểm:** chưa chạy trên Kaggle thật. Bản torch có hợp với driver của Kaggle không thì chỉ biết khi chạy: script tự thử các bản CUDA, và nếu không hợp thì dừng ở bước cài kèm file log.
- **Khi nhận file:** đặt vào `~/Zalo AI Challenge/cloud_results/` rồi báo Claude.
