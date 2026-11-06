# B28 trên laptop: chạy thử image Docker (06/11/2026)

*Claude viết lúc 02:04 ngày 06/11/2026 (giờ máy). Anh chọn dùng laptop thay vì thuê GPU (JOURNAL entry 98, HUMAN_TODO B28).*

## Cập nhật 09:40 ngày 06/11: leader đã gửi; Anh mang máy đi lúc 11:00, chạy tối nay

**Leader trả lời (L8):**
- Giữ nguyên image 05/11 (PhoWhisper-ft + `q4b4_all/final`), không build lại.
- File `zac_lifemate_2026-11-05.tar` nằm trên Google Drive, chỉ chia sẻ riêng cho tài khoản Google của Anh:
  - 12.635.573.248 byte;
  - sha256 `190bdeeb6157708d7e851c7f508ba2c583f22a15c939354d55d7753fd4f166a8`;
  - tên image `zaic-lifemate`.
- **Thiếu ID của image:** tin nhắn chỉ ghi "sha256", không có mã. Claude sẽ ghi ID sau khi nạp image và gửi lại leader để so.
- Leader đã chạy 3 mẫu trên RTX 3050 4 GB, phải mount driver thủ công:
  - chữ ASR khớp nguyên văn;
  - agent hết VRAM ở bước khởi động, nên chưa có `"ok"`.
- **Lệnh chạy:**
  - mount dữ liệu vào `/app/data/train+public_test` và `runs/` vào `/app/lifemate/runs`;
  - đặt các biến `SPLIT`, `DATA`, `ASR_MODEL=ckpt/asr_phoft/merged`, `ADAPTER=ckpt/q4b4_all/final`, `OUT`, `IDS`;
  - chạy `bash scripts/predict.sh`;
  - 4-bit, `TIME_BUDGET=25` và bước khởi động để mặc định.
  - Trên laptop, nhóm `--device`/driver được thay bằng `--gpus all`.
- **Hướng dẫn Docker của BTC:** máy chấm là RTX 5090 32 GB, giao diện nộp cuối khác image này. Tóm tắt và bảng việc còn thiếu: [`BTC_DOCKER_GUIDE_2026-11-06.md`](BTC_DOCKER_GUIDE_2026-11-06.md).

**Trước 11:00, Anh làm (B30):**
1. `sudo bash ~/zac-c3/b28_setup_docker.sh`: gồm đúng các lệnh ở mục 1 bên dưới, chạy trong một lần (khoảng 10–15 phút). Dòng cuối phải là `B28 SETUP OK`.
2. Mở link Drive của leader trong Chrome (đăng nhập tài khoản Google mà leader đã chia sẻ file), bấm Tải xuống rồi "Vẫn tải xuống", lưu vào `~/Downloads`. File này là file riêng, phải đăng nhập mới tải được, nên Claude không tải hộ.
3. Tuỳ Anh: `sudo usermod -aG docker $USER`, để Claude tự nạp image và chạy.

**Nếu kịp trước 11:00, Claude làm:** kiểm số byte và sha256, nạp image (`docker load`, khoảng 5–10 phút), chạy bước `info` rồi 3 mẫu (khoảng 3 phút). Tối nay khỏi phải chờ phần này.

**Tối nay (B31), khoảng 4 giờ:**
- **Laptop:** cắm sạc, tắt bớt app nặng (RAM 14 GB; container bị giới hạn 9 GB). Gập máy không sao, vì lệnh chặn ngủ cả khi gập.
- **Lệnh chạy:**
  - Nếu Anh đã vào nhóm `docker`, Claude chạy `bash ~/zac-c3/b28_start.sh all`. Lệnh này chạy trong một unit riêng, nên vẫn chạy tiếp nếu app Claude bị tắt.
  - Nếu chưa vào nhóm, Anh chạy lệnh dưới và để nguyên cửa sổ terminal:
    ```bash
    sudo systemd-inhibit --what=sleep:idle:handle-lid-switch --why=B28 bash /home/truyen-anh-thach/zac-c3/b28_run.sh all
    ```
- **`b28_run.sh` chạy lần lượt các bước,** bước nào đã xong thì bỏ qua:
  - `load`: kiểm số byte, sha256, rồi `docker load`;
  - `info`: ID image, CUDA, torch, có sm_120 cho RTX 5090 không, có jupyter không;
  - `smoke`: 3 mẫu, khoảng 3 phút;
  - `full1`: đủ 634 mẫu, khoảng 1 giờ 45 phút;
  - `full2`: đủ 634 mẫu lần nữa, khoảng 1 giờ 45 phút.
  - Bước nào hỏng hoặc `ok` không đúng thì script dừng luôn.
- **Cách chạy container:** `--network none --gpus all --memory 9g`, dữ liệu mount chỉ-đọc. Kết quả nằm ở `lifemate/runs/b28_docker_2026-11-06/` (không commit).
- **Tạm dừng:** `docker pause b28_full1`, chạy tiếp bằng `docker unpause b28_full1`. Mẫu đang chạy lúc dừng sẽ chạm hạn 25 giây.
- **Đã thử bằng một lệnh `docker` giả** (09:34): script chạy đủ các bước; chạy lại thì bỏ qua bước đã xong; `ok` sai thì dừng.

## Vì sao làm

- ASR đã chốt (B29: 49,65 < 51,16, giữ `ckpt/asr_phoft/merged`). Image leader build ngày 05/11 (12,6 GB) là bản cuối về model.
- Image đó chưa chạy trọn từ đầu tới cuối lần nào. GPU 4 GB của leader hết VRAM ở bước agent. Hạn nộp Docker là 11:59 ngày 16/11 (giờ máy).
- Ngày 05/11, `predict.sh` chạy ngoài Docker trên laptop với 3 mẫu đã đạt `"ok": true`, và cả 3 dòng giống hệt file 51,16. Vậy phần code đã đúng; còn phải kiểm chính image.

## Kiểm được gì, không kiểm được gì

- **Kiểm được:**
  - image chạy trọn khi tắt mạng, trên GPU NVIDIA 8 GB;
  - có `"ok": true`;
  - hai lần chạy cho ra kết quả giống nhau;
  - kết quả giống file 51,16 tới đâu.
- **Không kiểm được:** thời gian trên A30. RTX 4070 Laptop có băng thông bộ nhớ khoảng 256 GB/s, A30 khoảng 933 GB/s. Vì vậy số giây đo trên laptop là mức dè dặt, không phải số của máy chấm.

## 1. Anh cài trên laptop (khoảng 15 phút, cần sudo)

Laptop chạy Ubuntu 26.04, chưa có Docker. Ổ đĩa còn 160 GB.

**Docker** (gói `docker.io` 29.1.3 có sẵn trong kho của Ubuntu):

```bash
sudo apt-get update && sudo apt-get install -y docker.io
```

**NVIDIA Container Toolkit.** Kho mặc định của Ubuntu 26.04 không có gói này, nên lấy từ kho apt của NVIDIA:

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
```

```bash
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

```bash
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
```

```bash
sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker
```

**Kiểm GPU trong Docker.** Lệnh này tải image `ubuntu:24.04` (khoảng 30 MB). In ra bảng GPU là được:

```bash
sudo docker run --rm --gpus all ubuntu:24.04 nvidia-smi
```

**Tuỳ Anh: cho Claude chạy `docker` không cần sudo.**

```bash
sudo usermod -aG docker $USER
```

- Lưu ý: nhóm `docker` có quyền tương đương root trên máy.
- Không cần đăng xuất: Claude chạy qua `sg docker -c …`.
- Nếu Anh không muốn thêm nhóm, Claude soạn sẵn từng lệnh để Anh tự chạy với sudo.

## 2. Leader gửi

1. **File image:**
   - Chạy `docker save <tên image>:<tag> -o zac_lifemate_2026-11-05.tar`, rồi `sha256sum zac_lifemate_2026-11-05.tar`.
   - Gửi riêng cho Anh qua Google Drive (khoảng 12–13 GB). Không đẩy lên registry công khai.
2. **Đúng lệnh `docker run`** leader đã dùng để chạy 3 mẫu khi tắt mạng:
   - thư mục dữ liệu được mount vào đâu trong container;
   - file kết quả ghi ra đâu;
   - các biến môi trường (`SPLIT`, `IDS`, `OUT`…).
3. **Tên, tag và ID của image:** `docker inspect --format '{{.Id}}' <tên image>:<tag>`.

## 3. Claude chạy trên laptop (khoảng 5 giờ; chạy qua đêm được)

Anh nạp image vào Docker (`docker load -i zac_lifemate_2026-11-05.tar`, hoặc Claude nạp nếu đã có nhóm `docker`), kiểm sha256 xong thì xoá file tar. Mỗi lượt chạy với `--network none --gpus all --memory 9g`.

1. **3 mẫu** `public_0002`–`public_0004`:
   - cần `"ok": true`;
   - so với kết quả `predict.sh` chạy ngoài Docker ngày 05/11 (`runs/smoke_q4b_laptop_2026-11-05/`).
2. **Đủ 634 mẫu public:**
   - đo thời gian mỗi mẫu (ASR + agent) và đếm số mẫu dừng vì hết hạn 25 giây;
   - so với file 51,16. Không thể giống hệt, vì hạn 25 giây thay vì 60 và có bước warm-up.
3. **Chạy lại đủ 634 mẫu lần nữa,** so từng dòng với lượt 2 để kiểm tái lập.

Claude báo lại Anh và leader:
- có `"ok"` không;
- thời gian trung bình, p95, lâu nhất, số mẫu chạm hạn;
- số dòng khác giữa hai lần chạy;
- số dòng khác file 51,16.

## Tin nhắn cho leader (Anh copy gửi)

> Bọn mình kiểm image trên laptop của Anh (RTX 4070 8 GB), không thuê GPU. Model đã chốt: lần nộp ASR mới được 49,65, thấp hơn 51,16, nên giữ đúng image bạn build hôm 05/11 (PhoWhisper-ft + `q4b4_all/final`), không phải build lại. Bạn gửi giúp mình:
> 1. File image: `docker save <tên>:<tag> -o zac_lifemate_2026-11-05.tar`, kèm `sha256sum` của file, gửi riêng qua Google Drive (khoảng 12–13 GB).
> 2. Đúng lệnh `docker run` bạn đã dùng để chạy 3 mẫu khi tắt mạng: mount dữ liệu vào đâu, kết quả ghi ra đâu, các biến môi trường.
> 3. Tên, tag và ID của image (`docker inspect --format '{{.Id}}' <tên>:<tag>`).
>
> Bên mình sẽ chạy 3 mẫu để có `"ok"`, rồi chạy đủ 634 mẫu hai lần để đo thời gian và kiểm kết quả giống nhau, rồi báo lại bạn. Thời gian trên A30 vẫn chưa đo được; nếu bạn xem được hướng dẫn Docker của BTC (L4) thì gửi luôn, vì cách nộp và cách mount dữ liệu có thể khác lệnh hiện tại.
