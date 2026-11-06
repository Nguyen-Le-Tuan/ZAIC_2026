# Hướng dẫn Docker của BTC: tóm tắt và những gì image còn thiếu (06/11/2026)

*Claude đọc lúc 09:36 ngày 06/11/2026 (giờ máy). Nguồn: bản PDF mà leader gửi link, [Docker_Guide_ZAC2026_LifeMate.pdf](https://dl-challenge.zalo.ai/2026/lifemate_argfzdgert/Docker_Guide_ZAC2026_LifeMate.pdf) (19 trang, tạo ngày 04/11/2026). Phần dưới do Claude tóm tắt, có ghi số trang; chỗ nào cần chắc chắn thì mở bản gốc. Leader đã đọc trước và báo lại trong tin nhắn sáng 06/11 (L4).*

## Máy chấm (tr. 4)

- **Phần cứng:** 1 × RTX 5090 32 GB, CPU 16 nhân Xeon Gold 6459C, RAM 64 GB, driver 595.58.03, CUDA 13.2.0.
- **Base image:** CUDA không được cao hơn 13.2. Ví dụ BTC đưa: `nvidia/cuda:13.2.0-devel-ubuntu22.04`. Trang 7 còn ghi là *bắt buộc* dùng base image CUDA 13.2. Chọn đúng 13.2 thì đạt cả hai câu.
- **RTX 5090 là kiến trúc Blackwell (sm_120),** nên PyTorch trong image phải được build kèm sm_120. Venv trên laptop dùng torch `2.15.0+cu132`, có sm_120. Image chưa kiểm; tối nay bước `info` của B28 sẽ in ra.
- **Hướng dẫn không nhắc tới A30 hay mức 30 giây mỗi mẫu.** BTC đo thời gian bằng notebook (mục dưới). Luật cũ (30 giây trên A30) còn áp dụng hay không thì chưa rõ, nên giữ `TIME_BUDGET=25`.

## Giao diện khi chấm (tr. 4, 6–8, 10–11)

- **Lệnh BTC dùng để kiểm** (tr. 11):
  ```
  docker run --gpus '"device=0"' -v <data>:/data:ro -v <result>:/result <image> /bin/bash /code/predict.sh
  ```
  - Khi chấm, container không có mạng (tr. 7).
  - Mọi model (ASR, LLM, tokenizer) phải có sẵn trong image (tr. 8).
- **Đầu vào:** `/data/private_test/`, cùng cấu trúc với gói public (tr. 6):
  - `private_test.jsonl`;
  - `private_test_tools_catalog.json`;
  - `private_test_environment/`: chỉ đọc qua `zaic_tools`;
  - `audio/<id>/...`;
  - `zaic_tools/`.
- **`zaic_tools` phải nạp từ `/data/<split>/`, không dùng bản copy trong image.** Code hiện tại đã làm vậy (`lifemate/data.py`, hàm `zaic_tools`).
- **`/data` được mount chỉ-đọc,** nên code không được ghi gì vào đó. Tối nay B28 mount dữ liệu chỉ-đọc để kiểm việc này.
- **Đầu ra:** `/result/submission.jsonl`, và code phải tự tạo thư mục `/result` (tr. 7, 10).
  - Mỗi dòng trong ví dụ có `id`, `tool_calls`, `state_hash` và **`time`** (mili giây, tính từ trước khi đọc audio tới khi xong mẫu).
  - **File của mình hiện chưa có trường `time`.**
- **stdout:** in thời gian nạp model và thời gian predict (tr. 4).
- **Không có biến môi trường:** tham số phải đặt mặc định sẵn trong code. BTC không chịu trách nhiệm nếu đội muốn đổi tham số sau khi nộp (tr. 11).
- **Tên split:** notebook mẫu tìm thư mục con của `/data` có file `<tên>_tools_catalog.json` (tr. 16).

## Notebook đo thời gian (tr. 9, 12–18)

- **Trong image phải có:**
  - `jupyterlab`;
  - `/code/start_jupyter.sh`: chạy `jupyter lab` ở cổng 9777, mật khẩu và token đều là `zac2026`;
  - `/code/predict_notebook.ipynb`.
- **Notebook có ít nhất các ô sau:** đặt seed cố định; nạp model; đọc các test case; chạy từng mẫu (ASR → LLM → tool) rồi ghi `/result/jupyter_submission.jsonl`, có trường `time`.
- **BTC chỉ bấm "Run all".**
  - Thời gian mỗi mẫu tính từ lúc đọc file tới lúc ra kết quả, không tính thời gian nạp model.
  - Điểm của `jupyter_submission.jsonl` phải bằng điểm của `submission.jsonl` thì BTC mới dùng trường `time` của notebook.

## Mã nguồn và dữ liệu train (tr. 14–15)

- **`README.md`:** tóm tắt ý tưởng:
  - model ASR;
  - LLM: tên, số tham số, context length;
  - cách gọi tool và vòng lặp agent;
  - dữ liệu, và cách sinh dữ liệu tổng hợp nếu có.
- **`training_code/`, kèm README:** toàn bộ code train. BTC chạy lại phần train, có internet.
- **Dữ liệu train và model:** đưa lên HuggingFace hoặc dịch vụ tương tự và ghi URL tải. Không được sửa sau hạn nộp Docker.
- **Không để base model dùng lúc train trong image;** chỉ để weights dùng lúc inference.
- **Seed:** cố định cả khi train lẫn inference. Model train lại phải cho kết quả giống model dùng lúc inference.

## Nộp (tr. 14, 18–19)

- **Đóng gói:** `docker save <image> | gzip > zac2026_TeamName.tar.gz`, rồi thử `docker load` trên một máy khác.
- **Gửi:** tính `md5sum` của file nén, tải lên Google Drive và chia sẻ "Anyone with the link". Nộp link và checksum theo thông báo của BTC.
- **Hạn:** image phải xong trước khi BTC công bố private test. Hạn của đội: 11:59 ngày 16/11 (giờ máy).

## Image 05/11 so với hướng dẫn

Image 05/11 (`zaic-lifemate`) chỉ dùng để kiểm nội bộ (B28), chưa phải gói nộp cuối. Leader cũng đã nói rõ điều này.

| # | Yêu cầu của BTC | Image 05/11 | Việc cần làm |
|---|---|---|---|
| 1 | `/code/predict.sh`, đọc `/data/<split>`, ghi `/result/submission.jsonl`, không dùng biến môi trường | Chưa có: đang chạy `/app/lifemate/scripts/predict.sh` và cần biến môi trường | Script bọc ở `/code`: tự tìm split, đặt sẵn `ASR_MODEL`/`ADAPTER`, ghi file tạm ngoài `/data` rồi chép sang `/result` |
| 2 | Trường `time` (mili giây) trên mỗi dòng | Chưa có | Sửa code: `time` = giây ASR của mẫu + giây agent, đổi ra mili giây |
| 3 | In thời gian nạp model và thời gian predict ra stdout | Mới có dòng giờ bắt đầu/kết thúc từng bước | Thêm dòng in thời gian |
| 4 | Base image CUDA 13.2; torch có sm_120 | Chưa biết | Tối nay bước `info` của B28 in ra |
| 5 | `jupyterlab`, `start_jupyter.sh`, `predict_notebook.ipynb` chạy ASR → agent **từng mẫu một** | Chưa có. `predict.sh` hiện chạy ASR cho cả split trước, rồi mới chạy agent | Viết notebook, kiểm điểm notebook bằng điểm `submission.jsonl` |
| 6 | `README.md`, `training_code/`, URL dữ liệu và model | Chưa có | Đội quyết: dữ liệu là của BTC, `gen/` sinh từ train, repo đang public |
| 7 | Seed cố định | Giải mã greedy, nhưng chưa đặt seed rõ ràng | Đặt seed ở đầu `predict` và notebook |
| 8 | Nén gzip, md5, Drive "Anyone with the link" | Hiện chia sẻ riêng cho Anh, sha256 | Leader làm khi nộp |
| 9 | Không ghi vào `/data` | Chưa biết | Tối nay B28 mount chỉ-đọc |
