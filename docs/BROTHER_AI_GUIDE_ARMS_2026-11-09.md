# Chạy thử nghiệm liên tục trên máy anh trai Anh (09–10/11/2026), và so sánh với thuê GPU

*Đội ZAIC 2026 LifeMate soạn ngày 08/11/2026.*

- **Phần A** dành cho Leader, Anh và anh trai: so sánh hai cách chạy và chọn cách.
- **Phần B** dành cho **Claude chạy trên máy anh trai**: làm đúng từng bước.

> **Claude bên máy anh trai: đọc toàn bộ Phần B và làm theo. Phần A chỉ để biết vì sao; không cần làm gì ở đó.**

*Bản này nằm trong repo công khai nên không ghi link thư mục Drive. Bản Anh gửi cho anh trai phải điền `<LINK_THU_MUC_DRIVE>` và `<ID_THU_MUC_DRIVE>` (phần sau `/folders/` trong link).*

---

# PHẦN A. Thuê GPU hay để máy anh trai chạy liên tục

## A1. Việc cần chạy

| Giai đoạn | Nội dung | Khối lượng (đo trên RTX 4090, 4-bit) |
|---|---|---|
| Cài đặt | venv, tải 2 model mới (Qwen3-4B-Thinking-2507, Qwen3.5-4B text-only, mỗi model khoảng 8 GB), chạy thử | khoảng 30–45 phút |
| **Giai đoạn 1** | 7 lượt train trên `fit_lao` + chấm `dev_lao` hai lần (chữ chuẩn, chữ PhoWhisper-ft): A0 đối chứng; A1 Qwen3.5 ×2 seed; A2 Thinking + lý lẽ ×2; A3 Instruct + lý lẽ ×2. **Cộng một lượt public** của model đang nộp có bật lớp chống tìm kiếm rỗng (D5) | khoảng 3,5 giờ mỗi lượt (A1 có thể chậm hơn vì kiến trúc mới); lượt public khoảng 1–1,5 giờ |
| Luật | tự áp luật đã ghi trước, chọn nhánh thắng | vài giây |
| **Giai đoạn 2** (chỉ khi có nhánh thắng) | train nhánh thắng trên đủ 1.545 mẫu, 2 seed, rồi làm file public để đội nộp. Nhánh thắng là Qwen3.5 thì train thêm 1 nhánh dự phòng | khoảng 4 giờ mỗi lượt |

Tất cả gói trong **một lệnh** (`lifemate/scripts/brother_run.sh`). Lệnh tự chạy hết, tự tiếp tục nếu bị ngắt, tự đóng gói kết quả. Không ai phải ngồi canh.

## A2. So sánh

| | **Máy anh trai, chạy liên tục** (2× RTX 4090) | **Thuê 4× RTX 4090** | **Thuê 8× RTX 4090** |
|---|---|---|---|
| Giai đoạn 1 xong sau | khoảng **17 giờ** (mỗi GPU làm 3–4 lượt nối tiếp) | khoảng **9–10 giờ** | khoảng **5–6 giờ** |
| Cả hai giai đoạn | khoảng **21–25 giờ** | khoảng **14 giờ** | khoảng **10 giờ** |
| Kết quả D5 trên public | khoảng 2–3 giờ sau khi bắt đầu | như nhau | như nhau |
| Chi phí | 0 (điện của anh trai) | khoảng **22–40 USD** (0,4–0,7 USD/GPU-giờ, tính cả lúc chờ) | khoảng **30–55 USD** |
| Ai vận hành | Claude bên máy anh trai, tự chạy theo Phần B. Đội chỉ biết tiến độ qua Anh | Claude của đội điều khiển qua SSH, thấy lỗi là sửa ngay | như cột bên trái |
| Môi trường | **Đã chạy được 2 lần** (gói v3 ngày 05/11, pilot v2 ngày 07/11), điểm khớp với laptop | máy mới: có thể vướng driver hay CUDA (một máy 3090 driver 570 từng hỏng ở bước cài torch) | như cột bên trái |
| Rủi ro chính | anh trai cần dùng máy giữa chừng (dừng được, chạy lại thì tiếp; chỉ mất lượt đang dở); trễ liên lạc qua Anh; chỉ 2 GPU nên lâu | host cộng đồng có thể rớt mạng; quên tắt máy thì vẫn bị tính tiền; phải có người trả tiền | như cột bên trái |
| Dữ liệu thi | ở trên máy người quen; BTC đã xác nhận được phép | ở trên máy thuê riêng của đội | như cột bên trái |
| So sánh giữa các nhánh | mọi nhánh cùng một máy nên so được với nhau | như cột bên trái | như cột bên trái |

## A3. Khuyến nghị

*Giờ dưới đây ghi cả giờ New York (giờ máy của đội, cũng là giờ của hạn Docker 11:59 ngày 16/11) và giờ Việt Nam (nhanh hơn 12 giờ).*

- **Chọn máy anh trai nếu** anh trai bắt đầu được **trong khoảng 12 giờ tới**, tức trước khoảng 12:00 ngày 09/11 giờ New York (24:00 ngày 09/11 giờ Việt Nam), và để máy chạy khoảng một ngày.
  - Kết quả về khoảng trưa 10/11 giờ New York, vẫn kịp mốc chốt model 13/11, và không tốn tiền.
  - Bắt đầu muộn hơn mốc này thì thời gian để nộp public, kiểm và đóng Docker trước 13/11 bị co lại rất nhanh.
- **Chọn thuê 4× RTX 4090 nếu** anh trai không bắt đầu được trong khoảng đó, hoặc chỉ chạy được từng buổi ngắn.
  - Thuê ngay sau khi có gói thì kết quả về khoảng chiều 09/11 giờ New York, sớm hơn chừng một ngày.
  - Thời gian là thứ thiếu nhất: mỗi ngày trễ là bớt một ngày để kiểm và đóng Docker.
  - Với cách này, Claude của đội chạy qua SSH theo `docs/RUNBOOK_CLOUD_ARMS_2026-11-09.md` (cùng gói, cùng lệnh).
- **Không nên chia đôi** (một phần trên máy anh trai, một phần trên máy thuê). Hai máy khác nhau lệch 2–4 điểm giữa các lần train, nên các nhánh không còn so được với nhau.
- Chạy cách nào thì Leader vẫn làm L9 (gói Docker) song song.
- **Trước khi tải gói lên Drive:** thư mục phải ở chế độ **"Hạn chế"**, chỉ chia sẻ cho tài khoản của anh trai (việc B34: ngày 08/11 thư mục từng mở cho bất kỳ ai có link).

---

# PHẦN B. Hướng dẫn cho Claude trên máy anh trai

## B0. Vai trò và giới hạn

Bạn là trợ lý chạy trên máy GPU của anh trai Anh. Việc của bạn:
1. lấy gói;
2. chạy **một lệnh**;
3. theo dõi định kỳ;
4. gửi kết quả lên thư mục Drive của đội.

Mọi quyết định khoa học đã được đội viết sẵn vào code và vào luật; bạn không phải và **không được** tự quyết thêm.

**Được làm:** các lệnh trong Phần B; đọc log; xử lý lỗi theo bảng B7; tải gói và kết quả lên/xuống thư mục Drive của đội.

**Không được làm:**
- sửa code, sửa file danh sách lượt (`lifemate/cloud/arms_2026-11-09_models_d2.txt`), đổi seed, learning rate, độ dài, model hay bất kỳ tham số nào, kể cả khi thấy chạy chậm;
- dùng các biến bỏ qua kiểm tra (`ALLOW_SFT_DIFF`, `ALLOW_NEW_REVISION`);
- chạy thêm thí nghiệm ngoài lệnh này;
- mở, đọc, chép hay phân tích bất kỳ file nào trong các thư mục `*_environment/` (luật cuộc thi cấm);
- đưa gói, dữ liệu hay kết quả lên git, link công khai hay dịch vụ nào khác ngoài thư mục Drive của đội;
- đổi quyền chia sẻ của thư mục Drive; xoá hay sửa file của đội trên Drive;
- xoá các thư mục cũ trên máy (`~/ZAIC_2026`, `~/zac_v4`…) khi chưa hỏi anh trai.

Gặp tình huống không có trong bảng B7: **dừng, ghi lại, báo anh trai.** Đừng tự sáng tạo cách khác.

## B1. Tóm tắt

1. Kiểm máy (B2).
2. Tải `zac_cloud_bundle_20261109_arms.tar.gz` từ thư mục Drive về `~/`, kiểm kích thước và sha256 (B3).
3. Giải nén vào **thư mục mới** `~/zac_v5`, chạy đúng lệnh ở B4.
4. Theo dõi khoảng 30–60 phút một lần (B5). Khi file public D5 xong (khoảng 2–3 giờ sau khi bắt đầu), gửi trước file đó (B6).
5. Khi `run.log` có dòng `XONG`: gửi `~/zac_v5_results.tar.gz` và báo cáo (B8).

## B2. Yêu cầu máy và kiểm tra trước

```bash
nvidia-smi --query-gpu=index,name,memory.total,driver_version,compute_cap --format=csv,noheader
df -h ~ ; free -g ; python3 --version
```

- GPU NVIDIA có bf16 (compute capability ≥ 8.0: RTX 30/40, A100, L4, H100). Lệnh B4 tự kiểm và dừng nếu không đạt.
- Driver nên ≥ 570; lần trước máy này đã chạy được.
- Ổ đĩa trống **≥ 50 GB**: venv khoảng 10 GB, hai model mới khoảng 17 GB, checkpoint và log. Không đủ thì hỏi anh trai dọn chỗ, đừng tự xoá.
- Có mạng: để cài thư viện, tải model và tải file lên/xuống Drive.
- Có `python3` và `curl`. `uv` sẽ được lệnh tự cài nếu chưa có.

## B3. Lấy gói và kiểm

Thư mục Drive **không công khai**: chỉ tài khoản Google được chia sẻ mới mở được. Vì vậy `wget` hay `gdown` không tải được. Dùng một trong hai cách:

- **Cách A, trình duyệt:**
  - Anh trai mở `<LINK_THU_MUC_DRIVE>` bằng đúng tài khoản được chia sẻ.
  - Tải `zac_cloud_bundle_20261109_arms.tar.gz` về.
  - Nếu máy GPU là máy khác thì chép lên: `scp zac_cloud_bundle_20261109_arms.tar.gz <user>@<máy GPU>:~/`.
- **Cách B, `rclone`** (đã cấu hình từ lần trước; nếu chưa thì xem phụ lục):

  ```bash
  ~/bin/rclone copy gdrive: ~/ --drive-root-folder-id <ID_THU_MUC_DRIVE> --include "zac_cloud_bundle_20261109_arms.tar.gz" -P
  ```

Kiểm:

```bash
ls -l ~/zac_cloud_bundle_20261109_arms.tar.gz
sha256sum ~/zac_cloud_bundle_20261109_arms.tar.gz
```

- Kích thước phải là **KICH_THUOC** byte.
- sha256 phải là `SHA256_GOI`.
- Khác thì tải lại; vẫn khác thì dừng và báo.

## B4. Chạy, đúng một lệnh

```bash
mkdir -p ~/zac_v5 && cd ~/zac_v5 && tar -xzf ~/zac_cloud_bundle_20261109_arms.tar.gz && cd ZAIC_2026 && nohup bash lifemate/scripts/brother_run.sh > run.log 2>&1 &
```

Lệnh chạy nền, nên đóng SSH hay đóng terminal vẫn chạy tiếp. Nó làm lần lượt:

1. **Khoá chống chạy trùng.** Nếu lỡ chạy lần hai, lần hai thoát ngay với dòng `another brother_run.sh is already running`. Lần trước (pilot v2) từng bị chạy trùng.
2. **Kiểm máy:** GPU có bf16, ổ đĩa đủ chỗ.
3. **Cài đặt** (`cloud_setup.sh`, khoảng 30–45 phút):
   - kiểm toàn bộ file trong gói với manifest;
   - tạo venv đúng phiên bản thư viện, torch 2.15 (tự thử bản CUDA hợp với driver);
   - tải model ở đúng phiên bản đã ghim;
   - chạy test, dựng lại dữ liệu SFT và so với bản của đội;
   - chạy thử 3 bước train và 2 mẫu suy luận cho từng model mới.
4. **Giai đoạn 1:**
   - 7 lượt train và chấm (`cloud_arms.sh`), chia đều cho các GPU;
   - **cùng lúc**, trên GPU cuối, lượt public của model đang nộp có bật lớp chống (D5), ra `lifemate/runs/pub_c0_guard.jsonl`.
5. **Luật:** `lifemate/runs/arms_decision.txt` cho biết nhánh nào thắng.
6. **Giai đoạn 2** (chỉ khi có nhánh thắng): train trên đủ dữ liệu, ra adapter `lifemate/ckpt/f_<nhánh>_s<seed>/final` và file public `lifemate/runs/public_f_<nhánh>_s<seed>.jsonl`.
7. **Đóng gói** `~/zac_v5_results.tar.gz` (log, kết quả chấm, adapter giai đoạn 2), rồi in `XONG <ngày giờ>`. Nếu dừng vì lỗi, dòng cuối là `DUNG ...`, và gói kết quả vẫn được tạo với những gì đã có.

**Bị ngắt giữa chừng** (mất điện, khởi động lại, anh trai cần máy): chạy lại **đúng phần cuối của lệnh trên**, trong `~/zac_v5/ZAIC_2026`, và **không** giải nén lại:

```bash
cd ~/zac_v5/ZAIC_2026 && nohup bash lifemate/scripts/brother_run.sh >> run.log 2>&1 &
```

Lượt nào xong rồi thì giữ; lượt đang dở thì làm lại từ đầu lượt đó.

**Anh trai cần dừng hẳn để dùng máy:**

```bash
pkill -f "brother_run.sh|cloud_arms.sh|train_local.sh|eval_ckpt.sh|final_train.sh|lifemate\.(train|infer|sft)"
```

Khi máy rảnh lại thì chạy lệnh tiếp tục ở trên.

## B5. Theo dõi (khoảng 30–60 phút một lần)

```bash
cd ~/zac_v5/ZAIC_2026
tail -5 run.log                                        # tiến độ chung
cat lifemate/runs/cloud_arms_*.log                     # lượt nào bắt đầu / done / FAILED
tail -2 lifemate/runs/cloud_a*.log                     # từng lượt: bước train, hoặc giây/mẫu khi chấm
tail -2 lifemate/runs/pub_c0_guard.log                 # lượt public D5
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader
```

**Các mốc cần thấy trong `run.log`, theo thứ tự:**

1. `preflight ok: 2 GPU(s), ...`
2. Trong phần cài đặt: `bundle ...: N files, 0 differ`; các dòng `sft/<tên>.jsonl: same as local`; `setup done.`
3. `2. stage 1`, `7 arms on 2 GPU(s)`, rồi các dòng `GPU 0: start train a0_q4b4_lao_s0` …
4. `3. rule`, bảng điểm các nhánh, và dòng `winner: ... | fallback: ...`.
5. `4. stage 2: ...`, hoặc `no arm passed the rule`.
6. `results: .../zac_v5_results.tar.gz`, rồi `XONG`.

**Thời gian dự kiến trên 2× RTX 4090:**
- giai đoạn 1 khoảng 17 giờ;
- giai đoạn 2 khoảng 4 giờ (8 giờ nếu có nhánh dự phòng).

Dấu hiệu bình thường: mỗi GPU dùng khoảng 5–12 GB khi train; log train in bước và loss đều đặn; khi chấm, mỗi mẫu vài giây.

**Một lượt không có dòng log mới trong hơn 90 phút** (trừ lúc đang tải model): xem B7.

## B6. Gửi trước kết quả D5 (khoảng 2–3 giờ sau khi bắt đầu)

Khi có file `lifemate/runs/pub_c0_guard_check.json` (và `run.log` chưa báo lỗi cho lượt này):

```bash
cd ~/zac_v5/ZAIC_2026/lifemate/runs && tar -czf ~/zac_v5_d5_public.tar.gz pub_c0_guard.jsonl pub_c0_guard_check.json pub_c0_guard.meta.json pub_c0_guard.log && ls -l ~/zac_v5_d5_public.tar.gz && sha256sum ~/zac_v5_d5_public.tar.gz
```

Tải `~/zac_v5_d5_public.tar.gz` lên thư mục Drive (cách tải ở B8) và nhắn Anh "đã có file D5". Đội sẽ nộp file này lên public để đo lớp chống. **Bạn không nộp gì lên trang thi.** Lệnh chính vẫn chạy tiếp, không cần dừng.

## B7. Khi có lỗi

Chỉ xử lý theo bảng. Trường hợp khác: dừng, ghi 30 dòng cuối của log liên quan vào báo cáo, báo anh trai.

| Thấy gì | Làm gì |
|---|---|
| `another brother_run.sh is already running` | Bình thường: đã có một lần chạy. Không chạy thêm. |
| `DUNG: a GPU without bf16` | Máy không đạt. Gửi `~/zac_v5_results.tar.gz` (có `run.log`) và báo. |
| `DUNG: only N GB free` | Báo anh trai để dọn chỗ, rồi chạy lệnh tiếp tục. |
| `bundle files differ` | Gói hỏng. Tải lại, kiểm sha256, xoá `~/zac_v5`, chạy lại B4 từ đầu. |
| `SETUP FAILED: torch ... cannot use this GPU` | Chạy lệnh tiếp tục, có thêm `TORCH_INDEX_URL=https://download.pytorch.org/whl/cu128` trước `nohup` (đổi `cu128` theo driver: `cu126` nếu driver cũ hơn). |
| `SETUP FAILED: ... main is ..., local runs used ...` | Model trên Hugging Face đã đổi phiên bản. **Dừng và báo**, không tự cho phép phiên bản mới. |
| Lỗi tải model (mạng, 429, 5xx) | Đợi 10 phút, chạy lệnh tiếp tục. Lặp quá 3 lần thì báo. |
| `rebuilt SFT files differ` | Dừng, báo. Không chạy tiếp. |
| Một lượt `FAILED` trong `cloud_arms_*.log` (ví dụ hết VRAM) | Các lượt khác vẫn chạy tiếp. Khi lệnh xong, chạy lệnh tiếp tục **một lần**: lượt hỏng sẽ được làm lại. Hỏng lần nữa thì ghi vào báo cáo và để vậy. |
| `WARNING: the public C0 + guard job failed` | Ghi vào báo cáo kèm `lifemate/runs/pub_c0_guard.log`. Chạy lệnh tiếp tục một lần sau khi lệnh chính xong. |
| Một lượt im hơn 90 phút, GPU 0% | Có thể bị treo. Ghi lại; dừng hẳn bằng lệnh `pkill` ở B4, rồi chạy lệnh tiếp tục. |
| `WARNING: stage 2 ... failed` | Ghi vào báo cáo kèm `lifemate/runs/final_<tag>.log`. Không tự chạy lại riêng. |

## B8. Gửi kết quả cuối

Khi `run.log` có `XONG` (hoặc `DUNG` mà không xử lý được), tải lên **chính thư mục Drive đó**:

1. `~/zac_v5_results.tar.gz` (giữ nguyên tên). Có adapter giai đoạn 2 nên có thể nặng 0,5–1,5 GB.
2. Báo cáo `ZAIC_arms_report_<ngày>.md` theo mẫu dưới.

```markdown
# Thử nghiệm 09–10/11: kết quả
- Bắt đầu / kết thúc (giờ máy); có bị ngắt không, bao nhiêu lần chạy lại:
- GPU (nvidia-smi -L), driver, torch (lifemate/runs/cloud_setup.json: tok_s, peak_gb từng model):
- Nội dung lifemate/runs/arms_decision.txt (nguyên văn):
- Lượt public D5: dòng cuối của lifemate/runs/pub_c0_guard.log, nội dung pub_c0_guard_check.json:
- Giai đoạn 2: các file lifemate/runs/public_f_*.jsonl đã tạo, nội dung các file *_check.json:
- Lượt FAILED / lỗi / cảnh báo, kèm 30 dòng cuối log:
- File kết quả: tên, kích thước (ls -l), sha256:
```

**Cách tải lên:**
- **Cách A:** chép về máy có trình duyệt (`scp <user>@<máy GPU>:~/zac_v5_results.tar.gz .`), mở thư mục Drive, chọn "Mới" → "Tải tệp lên".
- **Cách B:**

  ```bash
  ~/bin/rclone copy ~/zac_v5_results.tar.gz gdrive: --drive-root-folder-id <ID_THU_MUC_DRIVE> -P
  ~/bin/rclone copy ~/ZAIC_arms_report_<ngày>.md gdrive: --drive-root-folder-id <ID_THU_MUC_DRIVE> -P
  ~/bin/rclone ls gdrive: --drive-root-folder-id <ID_THU_MUC_DRIVE>
  ```

Xong thì nhắn Anh. Claude của đội sẽ tự chấm lại và kiểm luật từ các file trong `lifemate/runs`.

## B9. Dọn dẹp (chỉ khi Anh báo đã nhận đủ)

Xoá: `~/zac_v5`, `~/zac_cloud_bundle_20261109_arms.tar.gz`, `~/zac_v5_results.tar.gz`, `~/zac_v5_d5_public.tar.gz`, file báo cáo, và `~/.zac_v5.lock`. Các thư mục cũ (`~/ZAIC_2026`, `~/zac_v4`, `zac_cloud_bundle_*`) xoá theo lời anh trai: đội đã đề nghị xoá từ 08/11 (việc B34). Cache model (`~/.cache/huggingface`) không chứa dữ liệu thi; giữ hay xoá tuỳ anh trai.

## B10. Quy tắc bắt buộc (nhắc lại)

- Gói chứa **dữ liệu thi có licence**. Chỉ để trên máy này và trong thư mục Drive riêng của đội.
- Không đọc `*_environment/`. Không train hay chỉnh gì trên `public_test`. File public chỉ để đội nộp.
- Không đổi lệnh hay tham số. Mọi so sánh chỉ có nghĩa khi chạy đúng công thức đã ghi.
- Không cần API key hay mật khẩu nào. Ai hỏi xin thì từ chối.

## Phụ lục: cấu hình `rclone` một lần (nếu chưa có)

```bash
mkdir -p ~/bin && cd /tmp && curl -LO https://downloads.rclone.org/rclone-current-linux-amd64.zip && unzip -o rclone-current-linux-amd64.zip && cp rclone-*-linux-amd64/rclone ~/bin/
~/bin/rclone config
```

Chọn `n` (remote mới), đặt tên `gdrive`, loại `drive`, scope `drive`, để trống client id. Máy không có trình duyệt thì chọn auto config = `n`: chạy lệnh `rclone authorize "drive"` mà nó in ra trên một máy có trình duyệt, đăng nhập đúng tài khoản được chia sẻ, rồi dán token về.
