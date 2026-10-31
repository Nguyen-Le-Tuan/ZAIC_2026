# Nhờ leader: train dự phòng trên Kaggle (31/10/2026)

*Anh nhờ leader chạy vì tài khoản Kaggle của Anh chưa xác minh số điện thoại, nên chưa bật được Internet. Bối cảnh và lý do chọn Kaggle: [`FREE_GPU_2026-10-31.md`](FREE_GPU_2026-10-31.md). Phần dưới đây là tin nhắn gửi leader, kèm ô lệnh hoàn chỉnh.*

*Kết quả (cập nhật 16:05, JOURNAL entry 46):*
- *Lượt Kaggle xong lúc khoảng 15:50 mà không train: ô lệnh đo được T4 chỉ 157 token/giây (khoảng 22,5 giờ mỗi epoch), nên tự bỏ qua 2 lượt train. Nó chỉ chấm lại adapter của laptop: 54,35 so với 53,92, chênh +0,43 (khoảng tin cậy −1,29 đến +2,15), 228/233 mẫu giống hệt.*
- *Không cần chạy lại lượt agent trên Kaggle.*

---

> **Sửa lỗi 31/10, 14:11.** Nếu bản trước dừng với `SETUP FAILED: bundle files differ from BUNDLE_MANIFEST.json`: thay **toàn bộ** ô lệnh bằng bản dưới đây, rồi Save Version → Save & Run All lại. **Không cần tải lại dataset.** (Kaggle tự giải nén gói và bỏ 99 file rác `.DS_Store` và `__pycache__`; ô lệnh mới bỏ chúng khỏi danh sách kiểm, mọi file khác vẫn kiểm đủ.)

Chào bạn, mình nhờ bạn chạy giúp một lượt train dự phòng trên Kaggle. Bạn chỉ mất khoảng 10 phút thao tác; máy tự chạy 8–11 giờ.

**Mục đích:** train 2 lượt **agent Qwen3-1.7B** (không phải ASR) trên GPU T4 miễn phí của Kaggle:
- **Agent học trên chữ PhoWhisper:** chưa ai chạy lượt này. Nó cho biết PhoWhisper có thắng Whisper-turbo không khi agent đã quen kiểu chữ của PhoWhisper. Kết quả này giúp bạn chọn model ASR để fine-tune.
- **Agent học trên chữ Whisper-turbo:** dự phòng, phòng khi máy Google của anh mình không train được. Tài khoản Kaggle của mình chưa xác minh số điện thoại nên không bật được Internet.

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
6. **Theo dõi** *(sửa 31/10, 15:20)*. Trong lúc bản Save & Run All đang chạy, Kaggle thường chỉ hiện vài dòng `Debugger warning: It seems that frozen modules are being used ...`, và Output đứng ở 0 B.
   - Đó là thông báo của Kaggle, **không phải lỗi**. Các dòng của ô lệnh (`OK: ...`, tốc độ T4, kết quả) chỉ hiện khi ô lệnh chạy xong. Ô lệnh cũng chỉ ghi file vào Output ở cuối.
   - Xem trạng thái của bản để biết nó có chạy ổn không:
     - **Kết thúc trong vài phút:** kiểm tra trước khi cài thất bại (thiếu GPU T4, Internet hoặc dataset). Mở log hoặc tab Notebook của bản đó, đọc dòng `LỖI: ...`, sửa theo lời nhắc rồi Save Version lại.
     - **Kết thúc sau khoảng 30–60 phút, không có `cloud_results_*`:** cài lỗi. Gửi mình `zac_logs.tar.gz`.
     - **Vẫn "Running" sau 1 giờ:** đã qua kiểm tra và cài đặt, đang train. Cứ để chạy.
7. Không cần ngồi canh. Ô lệnh tự dừng trong vòng 11 giờ, để Kaggle không cắt ở mốc 12 giờ. Nếu sau khoảng 11,5 giờ bản vẫn "Running", bấm dừng và báo mình. Tốc độ T4 đo được nằm trong `zac_logs.tar.gz` (file `plan.log`).
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
ARMS="pho asr"  # pho = học trên chữ PhoWhisper; asr = học trên chữ Whisper-turbo; up = công thức B-up
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
chmod -R u+w . 2>/dev/null
# Kaggle tự giải nén gói khi tải lên và bỏ file rác (.DS_Store, __pycache__): bỏ chúng khỏi danh sách kiểm gói.
# Mọi file khác (dữ liệu, gen, asr, adapter, lượt gốc) vẫn được kiểm sha256 như cũ.
python3 - <<'PY'
import json
from pathlib import Path
p = Path("BUNDLE_MANIFEST.json")
if p.exists():
    m = json.loads(p.read_text())
    junk = [f for f in m["files"] if not Path(f).is_file() and (Path(f).name == ".DS_Store" or "__pycache__" in Path(f).parts)]
    for f in junk:
        del m["files"][f]
    p.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n")
    print(f"Bỏ {len(junk)} file rác khỏi danh sách kiểm gói; còn {len(m['files'])} file được kiểm")
PY
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
  - Mặc định `ARMS="pho asr"` (Anh chọn 31/10, 13:58). Laptop chạy `asr` và `up` (JOURNAL entry 37), nên Kaggle thêm một lượt mới là `pho`, còn `asr` để dự phòng và để so T4 với laptop trên cùng công thức. Trước đó mặc định là `asr up`.
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
- **Lỗi lần chạy đầu (14:05):** Kaggle tự giải nén gói khi tải lên dataset và bỏ 2 file `.DS_Store` cùng 97 file `__pycache__/*.pyc` trong thư mục dữ liệu BTC. Bước kiểm gói của `cloud_setup.sh` đòi đủ từng file nên dừng. Các file này không cần để chạy. Ô lệnh nay bỏ chúng khỏi `BUNDLE_MANIFEST.json` trước khi cài; 2.369 file còn lại vẫn kiểm sha256.
  - Đã thử trên bản giải nén thật của gói v3, xoá đúng các file như Kaggle (thư mục chỉ đọc): trước khi sửa ra 99 file khác, giống hệt log Kaggle; sau khi sửa 0 file khác.
  - Đổi 1 byte trong `train.jsonl` thì bước kiểm vẫn bắt được. Hai bộ test CPU đạt trên bản thiếu `__pycache__`.
