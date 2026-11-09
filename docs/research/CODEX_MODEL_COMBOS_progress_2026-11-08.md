# Nhật ký nghiên cứu tổ hợp model — 08/11/2026

## Pha A — hoàn tất phần luật và bộ kiểm; số HF đang chờ làm giàu lại

- Đã đọc prompt, JOURNAL mục 1, báo cáo 31/10 và tóm tắt Docker Guide; đã ghi nhận trạng thái git ban đầu, không đổi nhánh hay file sẵn có.
- Đã tìm thấy cổng LifeMate chính thức và Docker Guide. Cần trích văn bản gốc của luật và phân biệt A30 trong đề với RTX 5090 trong hướng dẫn Docker.
- Ở thời điểm Pha A, Pha D chưa được cho phép; không tải trọng số, không truy cập dữ liệu thi.
- Đã đọc nguyên văn luật từ API công khai `https://api-challenge.zalo.ai/fe/api/config-detail?name=rule&title=1` với Origin của portal: `<6B` toàn bộ, `<5B` LLM, `≤16,384` context, 30 giây/mẫu, A30. Docker Guide PDF trang 4 ghi RTX 5090 32 GB, driver 595.58.03, CUDA 13.2. Chưa có văn bản chính thức nói rõ guide thay thế luật phần cứng/thời gian.
- Đã viết script metadata-only `tools/hf_model_audit_2026-11-08.py`. Lượt đầu xác nhận nhiều số safetensors; lượt truy vấn commit hàng loạt chạm giới hạn HF 500 request/5 phút và CSV cần quét lại sau khi giới hạn đặt lại. Không đăng nhập.

## Pha B — hoàn tất lượt quét

- Đã sàng lọc 153 dòng: 59 LLM, 40 ASR, 12 speech-LLM, 7 aux, 16 kỹ thuật, 14 TTS, 3 teacher và 2 draft. `verified` ở CSV có nghĩa repo/số đếm được kiểm trực tiếp, không có nghĩa chất lượng LifeMate đã đo.
- Quét 6 trang HF ASR gắn `vi` theo `createdAt`: 424 repo tạo từ 01/06 đến 25/10/2026; nhiều bản sao/adapter. Phát hiện Moonshine tiny-vi 27.015.360 tham số, VieGem-ASR nhưng licence NC, QUAN-Transcribe có checkpoint nhiều thành phần nên số HF chỉ là một phần.
- Đọc safetensors header bằng HTTP Range, không tải trọng số: Qwen3.5-4B đầy đủ 4.659.865.088, text-only 4.205.751.296; PhoWhisper-large 1.543.304.960. Bản `tuandunghcmut/Qwen3.5-4B-text-only` có trọng số trước hạn, ghép cùng PhoWhisper-large và LoRA r32 60.948.480 thành 5.810.004.736.
- Xác minh Qwen2.5-Omni-3B có licence `qwen-research` nên loại; Ultravox HF API chỉ đếm phần adapter, base Llama 8B không đủ điều kiện. `ByteDance/Dolphin` là OCR, không phải ASR. Repo đúng của FrogNano là `microsoft/FrogNano-4B-2609`; BuzzASR là `BuzzASR/vietnamese`.
- Đã lập CSV 20 tổ hợp và 130 nguồn. Ở thời điểm Pha B, Pha D chưa được cho phép; không tải trọng số hay chạy GPU.

## Pha C — hoàn tất

- Đã viết báo cáo 13 mục: top 5, luật/câu hỏi BTC, kho model, kỹ thuật R5, 20 tổ hợp và biên Pareto, 7 thẻ thí nghiệm, phản biện và phụ lục độ phủ.
- Kiểm CSV: 153 ứng viên, 20 tổ hợp, 130 nguồn; không thiếu repo_id/URL nguồn; không tổ hợp nào có `headroom_6b` hoặc `headroom_5b` ≤0. C14 được ghi rõ **loại do licence** dù số tham số đủ.
- Sửa đếm Gemma4 E2B thống nhất theo safetensors header 5.123.178.979 thay vì metadata HF lệch 928; kiểm first-weight commit Qwen3-4B-Thinking-2507 là 05/08/2025. Các hạt giống chưa xác nhận vẫn ghi `unverified`, không dùng để lập tổ hợp.
- Ở thời điểm Pha C, Pha D chưa được cho phép; không tải trọng số, không chạy train/inference, không đọc dữ liệu thi hay đổi trạng thái git.

## Pha D — hoàn tất sau khi Leader cho phép

- Tạo venv Python 3.12 bằng `uv` tại `~/zac-codex-env`; cài PyTorch CPU 2.15.0, Transformers 5.21.0, sherpa-onnx và các phụ thuộc vào venv, không vào Python hệ thống. Chỉ dùng CPU (`CUDA_VISIBLE_DEVICES=''`, một thread); watchdog dừng nếu RSS đạt 1,85 GB.
- Chọn đúng 100 ID đầu trong `lifemate/splits/dev_random.txt`; chỉ đọc `train.jsonl` và 100 wav **lượt cuối**, tổng 717,36 giây audio. Không đọc history wav, public/private hay thư mục `_environment`.
- Đã chạy tuần tự 4 model, mỗi trọng số <500 MB, tổng trọng số tải 622.856.016 byte: Gipformer1.5 int8 ONNX WER **16,89**, Moonshine tiny-vi fp32 **41,29**, PhoWhisper-tiny fp32 **42,21**, PhoWhisper-base fp32 **40,55**. Hàm WER là `lifemate.asr_train.wer`; slot số/giờ/tên proxy và RSS/RTF ở mục 5 báo cáo. Tất cả bốn model đều chưa fine-tune trong miền.
- Gipformer tốt nhất trong bốn ASR nhỏ, nhưng không có căn cứ thay PhoWhisper-large-ft của C0: mốc WER 9,2 của đội là trên toàn dev_random và model đã fine-tune, không so cặp với 100 wav này. C6 với Moonshine được hạ ưu tiên trong combo CSV.
- Đã xóa cụ thể cả bốn revision bằng `hf cache rm` (630,5 MB cả metadata/processor), xác nhận `hf cache ls` rỗng; `uv cache clean` dọn thêm 1005,4 MiB cache cài đặt. Venv khoảng 1 GB còn tại `~/zac-codex-env` để tái lập, không có trọng số ASR. Không ghi transcript/dự đoán vào báo cáo hay file.
