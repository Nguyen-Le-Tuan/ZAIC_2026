# LifeMate: pipeline có ROI cao nhất tới hạn Docker 16/11 (tổng hợp nghiên cứu 11/11/2026)

*Claude tổng hợp lúc 19:37 ngày 11/11 (giờ Buffalo) từ 4 nhóm nghiên cứu chạy song song. Báo cáo đầy đủ (tiếng Anh, ngoài git vì có mô tả mẫu train): `cloud_results/research_2026-11-11/{rivals,errors,methods,setter}.md`. Mọi con số gắn "ước" là ước lượng, chưa đo.*

## 0. Kết luận

- **Không có đường nào lên 90 điểm trong 4 ngày, và nhiều khả năng các điểm 90+ trên bảng public không lặp lại được khi chấm Docker.** Các hệ thống model nhỏ có tài liệu công khai tốt nhất chỉ được **61–63** (THE ALCHEMISTS 62,76; Hephaestus 62,01; Datyth 61,26). Đội mình (HELIX) được 57,03, khoảng hạng 241/509 ở cột SLM.
- **ROI cao nhất:** giữ nguyên model (Qwen3.5 train lại, v7q35) và ASR. Thêm **4 thay đổi rẻ lúc suy luận**, mỗi cái có cửa giữ/bỏ viết trước. Dùng máy anh trai đang rảnh cho **một lượt đo train thêm 1 epoch** trên dev.
- **Kỳ vọng (ước):** **+1 đến +3 điểm public**, tức khoảng 58–60, nếu các cửa đều qua. Rủi ro lớn nhất vẫn là gói Docker hỏng: mất trắng nhiều hơn mọi thứ ở đây cộng lại.

## 1. Bảng xếp hạng thật sự nói gì

- Cột SLM do đội tự khai và chấm trên **file nộp**, không phải trên Docker. 6/26 đội ≥ 90 có điểm SLM trùng điểm API tới hai số lẻ (40/355 đội nói chung). Một file 89,34 được một trợ lý lập trình "giải tay" từng mẫu. Một đội tự sửa tay 725 transcript public. Vài repo sinh dữ liệu train từ catalog hay bộ mô phỏng public (FAQ cấm).
- **Không đội nào ≥ 70 có mã nguồn hay mô tả công khai**, trừ TCL (91,84): chỉ có hai checkpoint Qwen3.5-4B bf16 ("sft-all", epoch 1 và 2), không có code.
- **Công thức chấm** (tab Evaluation, cập nhật 25/10): gold rỗng thì nộp rỗng mới được 1. Ngược lại, điểm bằng 0 nếu `state_hash` sai hoặc không có call nào khớp; nếu không thì bằng F1, với P = M/(M+U) và R = M/|G|. U tính cả call bị từ chối vì sai schema (agent của đội không gửi những call này). Tham số fuzzy cần token-F1 > 0,6. `sys.ask_missing_info` chấm như mọi tool. FAQ thêm: tham số thừa hợp lệ không làm hỏng việc khớp call, nhưng có thể đổi hash nếu là lệnh ghi.
- **ASR quyết định rất nhiều, kể cả với model API.** Một đội đo Claude Haiku trên 100 mẫu train: 94,1 với chữ chuẩn, 90,1 qua ASR khoảng 4% WER, 64,4 qua ASR khoảng 14% WER. Điểm API 75,5 của đội mình nằm gần đường đó.

## 2. Đội mình mất điểm ở đâu (A1 trên dev_lao, 2 seed, chấm lại bằng cách phát lại call: khớp 100% điểm đã lưu)

| Nhóm lỗi | Mất (chữ chuẩn) | Mất (chữ ASR) |
|---|---:|---:|
| Chọn sai loại quyết định (làm / hỏi lại / chỉ đọc / không gọi) | 11,4 | 22,3 |
| Lệnh ghi sai tham số (sai ý: id đối tượng, giờ, nội dung) | 15,8 | 15,7 |
| Thiếu, thừa hoặc sai tool ghi | 5,6 | 9,3 |
| Chỉ sai lệnh đọc (state đúng) | 4,2 | 4,9 |
| Hỏi lại sai tham số | 0,9 | 0,4 |

- Lỗi quyết định lớn nhất: **nhãn hỏi lại mà model tự làm** (tự bịa giờ 09:00). Model chỉ hỏi lại đúng ở 66% số mẫu cần hỏi với chữ chuẩn, 50% với chữ ASR.
- **ASR làm mất 14,6 điểm.** Lỗi đến từ lượt nói cuối (14,4/14,7 điểm), là các từ nội dung nghe sai (tên món, tên app, địa danh); con số chỉ chiếm 1,5% lỗi. WER lượt cuối 12,9%, nhiều chỗ là biến thể vô hại.
- **Nhiễu seed lớn:** 44/262 mẫu chỉ đúng ở một trong hai seed.
- **Nhãn gần như tất định** (góc nhìn người ra đề): hai họ dữ liệu, mẫu câu theo template (train_0001–0918) và kịch bản LLM viết (train_0919–1753; dev_lao 76% thuộc họ này). Một bộ sinh call từ ý định hoàn hảo tái tạo đúng 96,6% train. Nhưng model của đội đã theo quy ước; lỗi còn lại là lỗi hiểu ý, nên các luật sửa hậu kỳ chỉ thêm khoảng +0,6 điểm.

## 3. Danh sách thay đổi, xếp theo ROI (gain là điểm dev_lao chữ ASR so với v7q35, ước)

| # | Thay đổi | Loại | Gain (ước) | Công | Cửa giữ (viết trước) |
|---:|---|---|---|---|---|
| 1 | **Bộ chấm của đội theo FAQ** (bỏ qua tham số thừa trên call khớp) | đánh giá | đúng hơn 1–1,6 điểm khi đo | 1 giờ | luôn làm; chỉ ảnh hưởng cách đo |
| 2 | **Luật tham số an toàn** trước `env.call`: bỏ tham số không có trong schema; giờ đủ ISO khi schema nói ISO, HH:MM khi không; hỏi lại chỉ với tham số bắt buộc/one-of | suy luận | **+0,6** [+0,10; +1,34] (Qwen3-4B: +1,34) | 1,5 giờ | chạy thật trên dev: trung bình ≥ +0,3, không file nào < −0,5 |
| 3 | **ASR beam 4 ở lượt nói cuối** | suy luận | 0 tới +1,2 | 1 giờ + 15 phút GPU | WER lượt cuối trên dev giảm ≥ 0,3; lỗi từ hiếm và con số không tăng; điểm agent ≥ greedy − 0,3; p95 thời gian tăng ≤ 1 giây |
| 4 | **Trung bình hai seed v7q35** (ghép LoRA theo rank: đúng bằng trung bình ΔW) | trọng số | 0 tới +1 | 2 giờ | public bản trung bình ≥ trung bình public hai seed; tổng 5,87B < 6B, LLM 4,33B < 5B |
| 5 | **bf16 lúc suy luận** (cùng adapter) | suy luận | 0 tới +2 | 2 giờ GPU 24 GB | dev_lao (2 adapter fit_lao) ≥ NF4 + 1,0; **và** phải chạy được image trên GPU ≥ 24 GB trước khi nộp (laptop 8 GB không chạy được) |
| 6 | **Train thêm 1 epoch, LR giảm về 0** | train | +0,5 tới +3 (đội khác); −2 tới +2 (survey) | 1 giờ code + máy anh trai | luật E1: 2 seed, dev_lao chữ ASR ≥ mốc cùng máy + 3,0 và chữ chuẩn ≥ mốc − 2,0; rồi public 2 seed ≥ v7q35 + 1,5 |

**Thêm nếu còn thời gian:** hiệu chỉnh hỏi lại / làm bằng xác suất token đầu (+0,5 tới +2, cần nửa ngày code, phải chỉnh ngưỡng trên dữ liệu khác dev_lao); vệ sinh vòng lặp (0 tới +1).

**Không làm trước 16/11** (bằng chứng âm hoặc quá rủi ro): RL/GRPO, DPO/KTO, distill on-policy (API không cho log-prob), dữ liệu sinh hay ghép app (−1,3 và −1,6 public ở đội khác), bỏ bộ lọc của lệnh đọc (−0,5), verifier cùng model (−19), router tool, hotword/prompt cho Whisper, dữ liệu TTS cho ASR, 3 epoch LR không đổi (−4,1), đổi model hay đổi ASR, MoE (BTC đếm tổng tham số), grammar decoding (chỉ 3–4/262 call sai schema), nhiều ứng viên mỗi mẫu (p95 15 giây, không đủ ngân sách 25 giây). Retrieval few-shot trong SFT (−1 tới +4) cần 5–6 giờ code, rủi ro cao; để sau cuộc thi.

## 4. Kế hoạch theo ngày (giờ Buffalo)

- **Tối thứ Tư 11/11 (Claude, laptop):** việc 1–4 thành cờ mặc định tắt, test CPU, qua PR. Laptop (GPU rảnh sau lượt chạy thử Qwen3.5): chép lại chữ ASR của dev_random và dev_lao (greedy và beam 4) để chấm cửa 3, và để có file chữ ASR dev cho các lượt đo.
- **Sáng thứ Năm 12/11:** có file public v7q35 và v7q3; Anh nộp; áp luật entry 138. Làm adapter trung bình v7q35 rồi nộp public (cửa 4). Máy anh trai (gói và hướng dẫn mới):
  - **M1:** mốc fit_lao (code v7, 1 epoch, 2 seed). Vừa làm mốc cùng máy, vừa cho adapter fit_lao đúng luật để chấm việc 2, 3, 5 trên dev.
  - **M2:** fit_lao 2 epoch (2 seed), cho cửa 6.
  - **M3:** bản đủ dữ liệu 2 epoch (2 seed), chạy trước để kịp; chỉ dùng nếu M2 qua cửa.
- **Tối thứ Năm:** chấm các cửa. bf16 so với NF4 trên adapter M1 (máy anh trai).
- **Thứ Sáu 13/11, 18:00:** chốt cấu hình (adapter, cờ 2–5). Leader đóng image L9; mọi thay đổi chỉ là cờ hoặc thư mục adapter.
- **Thứ Bảy 14/11:** kiểm image offline: chạy hết public, ≥ 95% dòng giống bản ngoài Docker; 2 lần chạy 100 mẫu giống nhau; p95 dưới 20 giây.
- **Chủ nhật 15/11:** tải image lên Drive (khoảng 12–13 GB), nộp lần 1. Giữ lần nộp 2 để sửa lỗi.
- **Thứ Hai 16/11:** chỉ đổi sang bản dự phòng nếu có lỗi; hạn 11:59.

## 5. Việc của người

- **Anh:** hỏi anh trai còn adapter fit_lao của A1 (`~/zac_v5/ZAIC_2026/lifemate/ckpt/a1_q35t_lao_s{0,1}/final`) không, và đừng xoá `~/zac_v5` lúc này. Còn thì có thể chấm việc 2, 3 trên Qwen3.5 sớm hơn. Giữ máy anh trai rảnh cho M1–M3 từ sáng thứ Năm.
- **Leader:** L9 theo cấu hình chốt thứ Sáu; review PR #17 và PR của việc 1–4.
