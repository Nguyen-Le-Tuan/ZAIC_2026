# Hướng dẫn chạy pilot v2 (dành cho AI trên máy anh trai)

*Đội ZAIC 2026 LifeMate soạn ngày 06/11/2026, sửa lúc 17:40: lấy file và nộp kết quả qua Google Drive. Bạn là AI trợ lý chạy trên máy GPU của anh trai Anh. File này nói đủ những gì cần làm: train gì, lấy file ở đâu, chạy lệnh nào, kiểm gì, gửi lại cái gì.*

**Thư mục Google Drive của đội** (lấy gói ở đây, tải kết quả lên đây): link Anh gửi kèm file này

*Bản này nằm trong repo công khai nên không ghi link thư mục. `<ID_THU_MUC_DRIVE>` là phần sau `/folders/` trong link. Bản Anh gửi cho máy anh trai đã điền sẵn cả hai (`cloud_results/anh_trai/BROTHER_AI_GUIDE_PILOT_V2_2026-11-07.md` trên laptop, ngoài git).*

## 1. Việc cần làm (tóm tắt)

1. **Lấy file:** tải gói `zac_cloud_bundle_20261106_synthv2.tar.gz` từ thư mục Drive ở trên vào thư mục home (`~/`) của máy GPU, rồi kiểm sha256 (mục 4, bước 1).
2. **Chạy:** đúng **một lệnh** ở mục 4. Lệnh tự cài đặt, tự train 4 lượt, tự chấm, tự đóng gói kết quả.
3. **Theo dõi:** chờ khoảng 5–7 giờ, tới khi `run.log` có dòng `XONG`.
4. **Nộp kết quả:** tải lên **chính thư mục Drive đó** file `~/zac_v4_results.tar.gz` và một báo cáo ngắn theo mẫu ở mục 7, rồi nhắn Anh.

Chỉ chạy **một lần**. Không train thêm gì khác, không sửa code.

## 2. Đang train cái gì

- **Model:** Qwen3-4B-Instruct-2507, train LoRA trên nền 4-bit (QLoRA). Đây là đúng công thức của model đội đang nộp.
- **Dữ liệu:** tập train của cuộc thi, bỏ 6 app (dùng làm tập kiểm `dev_lao`, 262 mẫu).
- **So sánh:** có và không có 202 mẫu dữ liệu sinh cho đúng 6 app đó.
- **4 lượt, mỗi lượt train rồi chấm `dev_lao` hai lần** (chữ chuẩn và chữ ASR PhoWhisper-ft):

  | GPU | Lượt chạy trước | Lượt chạy sau |
  |---|---|---|
  | 0 | `q4b4_lao_base_s0` (không có dữ liệu sinh, seed 0) | `q4b4_lao_v2_s1` (có dữ liệu sinh, seed 1) |
  | 1 | `q4b4_lao_v2_s0` (có dữ liệu sinh, seed 0) | `q4b4_lao_base_s1` (không có dữ liệu sinh, seed 1) |

- **Danh sách lượt:** nằm trong `lifemate/cloud/arms_2026-11-07_synth_v2.txt` trong gói. Lệnh ở mục 4 đã trỏ sẵn tới file đó.
- **Máy có hơn 2 GPU:** các lượt tự chia ra, chạy nhanh hơn.
- **Máy chỉ có 1 GPU:** 4 lượt chạy lần lượt, khoảng 10–12 giờ.

## 3. Yêu cầu máy

- Linux, GPU NVIDIA có bf16, tức compute capability từ 8.0 trở lên (RTX 30/40, A100, L4, H100…). Lệnh tự kiểm và dừng nếu GPU không đạt.
- Driver NVIDIA ≥ 550.
- Có mạng trong lúc cài đặt (tải thư viện; model 4B đã có trong cache Hugging Face từ lần chạy trước) và lúc tải file lên / xuống Drive.
- Ổ đĩa trống ≥ 40 GB: venv mới khoảng 10 GB, checkpoint, log.
- Đã chạy một lần trước đó (gói v3, thư mục `~/ZAIC_2026`). **Để nguyên thư mục đó.** Lần này giải nén vào thư mục mới `~/zac_v4`.

## 4. Các bước

**Bước 1. Tải gói từ Drive về `~/`, rồi kiểm.**

Thư mục Drive không công khai: chỉ tài khoản Google được Anh chia sẻ mới mở được. Vì vậy `gdown` hay `wget` không tải được; dùng một trong hai cách:

- **Cách A, qua trình duyệt** (dễ nhất):
  - Anh trai mở link thư mục trên máy có trình duyệt, đăng nhập đúng tài khoản được chia sẻ.
  - Tải file `zac_cloud_bundle_20261106_synthv2.tar.gz` về.
  - Nếu máy GPU là máy khác (máy chủ qua SSH), chép lên: `scp zac_cloud_bundle_20261106_synthv2.tar.gz <user>@<máy GPU>:~/`.
- **Cách B, bằng `rclone` ngay trên máy GPU:** cài và cấu hình một lần theo phụ lục ở cuối file, rồi:

  ```bash
  ~/bin/rclone copy gdrive: ~/ --drive-root-folder-id <ID_THU_MUC_DRIVE> --include "zac_cloud_bundle_20261106_synthv2.tar.gz" -P
  ```

Rồi kiểm file:

```bash
ls -l ~/zac_cloud_bundle_20261106_synthv2.tar.gz
sha256sum ~/zac_cloud_bundle_20261106_synthv2.tar.gz
```

- Kích thước phải là **5752327** byte.
- sha256 phải là `8314687a327301d30410549489644494250067d5522548d3b49c4accc5c0c6a3`.
- Khác thì **dừng**: tải lại từ Drive. Vẫn khác thì báo Anh.

**Bước 2. Chạy đúng lệnh này**, nguyên một dòng, từ bất kỳ thư mục nào:

```bash
mkdir -p ~/zac_v4 && cd ~/zac_v4 && tar -xzf ~/zac_cloud_bundle_20261106_synthv2.tar.gz && cd ZAIC_2026 && nohup bash -c 'if nvidia-smi --query-gpu=compute_cap --format=csv,noheader | awk -F. "\$1<8{bad=1} END{exit bad}"; then SMOKE_MODELS=Qwen/Qwen3-4B-Instruct-2507 SMOKE_TRAIN_ARGS="--load-4bit --optim adamw8bit --max-len 6144" SMOKE_INFER_ARGS=--load-4bit bash lifemate/scripts/cloud_setup.sh && PACK=0 bash lifemate/scripts/cloud_arms.sh lifemate/cloud/arms_2026-11-07_synth_v2.txt; (cd lifemate && .venv/bin/python scripts/pilot_rule.py --base runs/sft_q4b4_lao_base_s0 runs/sft_q4b4_lao_base_s1 --new runs/sft_q4b4_lao_v2_s0 runs/sft_q4b4_lao_v2_s1 --ids splits/dev_lao.txt --json runs/pilot_v2_rule.json > runs/pilot_v2_rule.txt 2>&1); else echo "DUNG: GPU khong co bf16"; nvidia-smi -L; fi; tar -czf ~/zac_v4_results.tar.gz run.log lifemate/runs; echo "XONG $(date)"' > run.log 2>&1 &
```

Lệnh chạy nền (`nohup`), nên đóng SSH vẫn chạy tiếp. Lệnh làm lần lượt:

1. Kiểm GPU có bf16.
2. `cloud_setup.sh`, khoảng 15–30 phút:
   - kiểm toàn bộ file trong gói với manifest;
   - tạo venv với đúng phiên bản thư viện;
   - kiểm model;
   - chạy test;
   - dựng lại 4 file dữ liệu SFT và so với bản của đội;
   - chạy thử 3 bước train 4-bit để đo tốc độ.
3. `cloud_arms.sh`: train và chấm 4 lượt, chạy song song trên các GPU, khoảng 5–6 giờ trên 2× RTX 4090.
4. `pilot_rule.py`: tính kết quả theo luật đội đã ghi trước, ghi vào `lifemate/runs/pilot_v2_rule.txt`.
5. Đóng gói `~/zac_v4_results.tar.gz` (log và kết quả chấm, không có checkpoint; khoảng vài chục MB), rồi in `XONG`.

## 5. Theo dõi

```bash
tail -f ~/zac_v4/ZAIC_2026/run.log                      # nhật ký chung
cat ~/zac_v4/ZAIC_2026/lifemate/runs/cloud_arms_*.log    # lượt nào bắt đầu / xong / FAILED
tail -3 ~/zac_v4/ZAIC_2026/lifemate/runs/cloud_q4b4_lao_*.log   # tiến độ từng lượt (bước train, giây/mẫu khi chấm)
nvidia-smi
```

**Các mốc cần thấy trong `run.log`**, theo thứ tự:

- `bundle 4769d3a069 (HEAD): 2317 files, 0 differ`
- 4 dòng `sft/<tên>.jsonl: same as local`
- `setup done.`
- `4 arms on 2 GPU(s) ...`, rồi các dòng `GPU 0: start train ...`, `GPU 1: start train ...`
- Cuối cùng: 8 dòng điểm (4 lượt × 2 loại chữ), `RULE PASS` hoặc `RULE FAIL` (nằm trong `pilot_v2_rule.txt`), rồi `XONG <ngày giờ>`.

Train xong thì mỗi lượt có `ckpt/<TAG>/final` (khoảng 263 MB). Checkpoint không cần gửi về.

## 6. Khi có lỗi

**Không sửa code, không sửa file danh sách lượt, không dùng các biến cho phép bỏ qua kiểm tra** (`ALLOW_SFT_DIFF`, `ALLOW_NEW_REVISION`). Chỉ xử lý theo bảng dưới; trường hợp khác thì dừng và báo lại, kèm 30 dòng cuối của log liên quan.

| Thấy gì | Làm gì |
|---|---|
| `DUNG: GPU khong co bf16` | GPU không đạt. Không làm gì thêm; gửi `~/zac_v4_results.tar.gz` (có `run.log`). |
| `bundle files differ` | File gói hỏng. Tải lại từ Drive, kiểm sha256, xoá `~/zac_v4` rồi chạy lại từ đầu. |
| `SETUP FAILED: torch ... cannot use this GPU` | Xoá `~/zac_v4`, chạy lại lệnh ở bước 2 nhưng thêm `TORCH_INDEX_URL=https://download.pytorch.org/whl/cu128` ngay trước `bash lifemate/scripts/cloud_setup.sh` (đổi `cu128` cho hợp với driver). |
| `rebuilt SFT files differ` | Dừng, báo lại. Không chạy tiếp. |
| Một lượt `FAILED` trong `cloud_arms_*.log` (ví dụ hết VRAM) | Để các lượt khác chạy tiếp. Ghi tên lượt và 30 dòng cuối của `lifemate/runs/cloud_<TAG>.log` vào báo cáo. |
| Máy bị dừng giữa chừng, hoặc phải dừng | Không tự chạy lại. Trong `~/zac_v4/ZAIC_2026` chạy `tar -czf ~/zac_v4_results.tar.gz run.log lifemate/runs`, gửi file đó và ghi rõ dừng lúc nào. Cặp seed 0 chạy trước nên thường đã có kết quả để đọc. |

## 7. Nộp cái gì, ở đâu

**Tải hai file lên chính thư mục Drive ở đầu file này** (thư mục có gói), không đặt ở chỗ nào khác:

1. **`~/zac_v4_results.tar.gz`** (giữ nguyên tên).
2. **Báo cáo ngắn** dạng Markdown, đặt tên `ZAIC_pilot_v2_report_<ngày>.md`, theo mẫu dưới đây. Ghi cả kích thước và sha256 của file kết quả (`ls -l`, `sha256sum`).

```markdown
# Pilot v2: kết quả
- Bắt đầu / kết thúc (giờ máy):
- GPU (nvidia-smi -L), driver, torch:
- Tốc độ train 4B 4-bit: tok_s và peak_gb trong lifemate/runs/cloud_setup.json
- Bảng điểm (các dòng điểm cuối run.log):
  | Lượt | Chữ chuẩn | Chữ ASR (_asr) |
- Nội dung lifemate/runs/pilot_v2_rule.txt (nguyên văn)
- Lượt FAILED / lỗi / cảnh báo (nếu có), kèm log
- File kết quả: tên, kích thước, sha256
```

**Cách tải lên:**

- **Cách A, trình duyệt:**
  - Nếu máy GPU là máy chủ, chép kết quả về máy có trình duyệt: `scp <user>@<máy GPU>:~/zac_v4_results.tar.gz .`
  - Mở thư mục Drive, bấm "Mới" → "Tải tệp lên", chọn hai file.
- **Cách B, `rclone`:**

  ```bash
  ~/bin/rclone copy ~/zac_v4_results.tar.gz gdrive: --drive-root-folder-id <ID_THU_MUC_DRIVE> -P
  ~/bin/rclone copy ~/ZAIC_pilot_v2_report_<ngày>.md gdrive: --drive-root-folder-id <ID_THU_MUC_DRIVE> -P
  ~/bin/rclone ls gdrive: --drive-root-folder-id <ID_THU_MUC_DRIVE>     # kiểm đã lên đủ
  ```

**Trong thư mục Drive:** chỉ thêm file kết quả. Không xoá hay sửa file của Anh, không đổi quyền chia sẻ của thư mục.

**Xong thì nhắn Anh** là đã tải lên. Anh tải hai file về `~/Zalo AI Challenge/cloud_results/anh_trai/` trên laptop rồi báo Claude. Claude sẽ tự kiểm lại luật từ các file trong `lifemate/runs`.

## 8. Quy tắc bắt buộc

- **Dữ liệu có licence của cuộc thi:** gói, dữ liệu và kết quả chỉ để trên máy GPU và trong thư mục Drive riêng của đội. Không đưa lên git, link công khai hay bất kỳ dịch vụ nào khác.
- **Không mở, đọc, chép hay phân tích file trong các thư mục `*_environment/`** (ví dụ `data/train+public_test/train/train_environment/`). Luật cuộc thi cấm việc này; code của đội chỉ truy cập qua `zaic_tools`.
- **Không train trên `public_test`,** không dùng `public_test` để chỉnh gì.
- **Không đổi lệnh hay tham số train** (seed, số bước, learning rate…). Kết quả chỉ so sánh được khi chạy đúng công thức.
- **Không động tới `~/ZAIC_2026`** (lần chạy trước).
- **Sau khi Anh báo đã nhận đủ:** xoá `~/zac_v4`, `~/ZAIC_2026`, các file `zac_cloud_bundle_*.tar.gz`, `cloud_results_*.tar.gz`, `zac_logs.tar.gz` và `zac_v4_results.tar.gz`.

## 9. Nếu kết quả đạt

Luật đạt khi bản có dữ liệu sinh hơn bản gốc ít nhất 2,0 điểm trên chữ ASR, và không kém quá 2,0 trên chữ chuẩn.

- **Đạt:** đội sẽ gửi một gói mới cho lần chạy thứ hai: train bản cuối trên đủ dữ liệu. Gói đó có hướng dẫn riêng.
- **Không đạt:** không còn việc gì cho máy này.

## Phụ lục: cài `rclone` cho Google Drive (chỉ cho cách B, làm một lần)

Không cần sudo:

```bash
mkdir -p ~/bin && cd /tmp && curl -fsSLO https://downloads.rclone.org/rclone-current-linux-amd64.zip \
  && unzip -o -q rclone-current-linux-amd64.zip && cp rclone-*-linux-amd64/rclone ~/bin/ && ~/bin/rclone version
~/bin/rclone config
```

Trong `rclone config`:
- chọn `n` (remote mới), đặt tên `gdrive`, loại `drive`;
- để trống `client_id` và `client_secret`, chọn scope `1` (toàn quyền, cần để tải lên);
- để trống `service_account_file`, không sửa cấu hình nâng cao.

Đăng nhập Google:
- **Máy GPU không có trình duyệt:** khi được hỏi "Use web browser to automatically authenticate", chọn `n`. rclone in ra một lệnh `rclone authorize "drive" "..."`. Anh trai chạy lệnh đó trên máy có trình duyệt và rclone, đăng nhập **đúng tài khoản Google được chia sẻ thư mục**, rồi dán chuỗi token trả về vào máy GPU.
- Câu hỏi "Shared Drive (Team Drive)": chọn `n`.

`--drive-root-folder-id` trỏ thẳng vào thư mục được chia sẻ, nên không cần tìm thư mục trong "Shared with me". Thư mục chỉ cho xem mà không cho sửa thì bước tải lên sẽ báo lỗi quyền: nhắn Anh cấp quyền "Người chỉnh sửa".
