# Nhật ký dự án — ZAIC 2026 LifeMate

File này ghi lại toàn bộ trao đổi và quyết định của đội, để:

1. **Leader và các thành viên theo dõi tiến độ** qua lịch sử commit trên GitHub.
2. **Làm context khi mở đoạn chat mới với Claude.** Mở chat mới thì yêu cầu: *"Đọc `JOURNAL.md` trước rồi tiếp tục"*.

**Quy tắc cập nhật:** sau mỗi buổi trao đổi hoặc mỗi mốc quan trọng, thêm một mục mới vào [Nhật ký theo thời gian](#7-nhật-ký-theo-thời-gian), sửa phần [Trạng thái hiện tại](#0-trạng-thái-hiện-tại), rồi commit và push. Mục cũ không xoá; nếu sai thì ghi đính chính ở mục mới.

**Quy tắc git:** tài liệu (`JOURNAL.md`, `docs/`, `README.md`) được commit thẳng vào `main`. **Code mới phải đi qua Pull Request.**

**Tài liệu liên quan:**
- [`docs/PIPELINE.md`](docs/PIPELINE.md): moat, pipeline nền móng, tự đánh giá, đề án nâng cấp và 20 câu hỏi cho đội.
- [`HUMAN_TODO.md`](HUMAN_TODO.md): việc của người, kèm câu trả lời làm việc cho 20 câu hỏi.
- Ngày 29/10:
  - [`docs/TRAIN_REVIEW_2026-10-29.md`](docs/TRAIN_REVIEW_2026-10-29.md): audit lượt train đầu, Anh làm với Codex hỗ trợ.
  - [`docs/CLAUDE_HANDOFF_2026-10-29.md`](docs/CLAUDE_HANDOFF_2026-10-29.md): yêu cầu của Anh cho phiên 29/10.
  - [`docs/EVAL_2026-10-29.md`](docs/EVAL_2026-10-29.md): Claude đối chiếu audit, chấm các checkpoint và đề xuất thí nghiệm tiếp theo.

---

## 0. Trạng thái hiện tại

*Cập nhật: 2026-11-11 15:51: **Anh chọn chạy cả hai hướng song song trên máy anh trai** (đã có 3 máy rảnh): Run Q = Qwen3.5 + D1 (khoảng 12–13 giờ), Run I = Qwen3-4B + D1 (khoảng 5–6 giờ), máy thứ ba dự phòng. File hướng dẫn mới `cloud_results/anh_trai/BROTHER_AI_GUIDE_V6_BOTH_2026-11-11_EN.md`, chờ Anh gửi kèm "go" (B47). **3 file public chờ nộp:** `cloud_results/nop_public_2026-11-11/` (B45). **Liên hệ BTC: email aichallenge@zalo.me** (email soạn sẵn ở entry 136). **Hạn Docker: 11:59 trưa thứ Hai 16/11 giờ Buffalo** (23:59 GMT+7); private test phát 23:00 ngày 19/11 giờ Buffalo (entry 136). 15:00: **Đợt A0–A3 trên máy anh trai xong (14:09): A1 (Qwen3.5-4B text-only) thắng luật viết trước.** dev_lao 2 seed: chữ ASR 47,36 (mốc 40,84; +7,27 so với A0 [+2,32; +12,27]), chữ chuẩn 62,02. A2, A3 (D2) thua. Giai đoạn 2 đã làm 2 file public của A1 (kiểm đạt, D5 bật), **chờ Anh nộp (B45)**. **A1 chỉ dùng được khi BTC chấp nhận cách đếm tham số bản text-only (4,21B); chưa thấy BTC trả lời.** Tính A0 vào mốc thì D1 cũng qua luật gốc (43,91 ≥ 43,84). Anh chọn lượt kế tiếp cho máy anh trai: Qwen3.5 + D1 hay Qwen3-4B + D1 (B46, entry 135). 14:03: **B43 xong: gói bản cuối đã lên Drive** (256,2 MB trên Drive, đúng 268.666.293 byte). Anh trai chỉ bắt đầu khi đợt v5 in `XONG` và Anh báo "go". Thư mục vẫn để "ai có link đều sửa được" (B34, entry 134). 13:59: **Anh nhờ Claude tải gói bản cuối lên Drive, nhưng Claude không tải được:** công cụ tải file qua Chrome chỉ nhận tối đa 10 MB, gói nặng 268 MB, laptop không có `rclone`. Gói đã kiểm lại (kích thước và sha256 khớp hướng dẫn); Anh tải lên từ Chrome trên laptop (B43). Thư mục Drive thuộc tài khoản Anh (entry 122 ghi nhầm là của Leader), vẫn để "ai có link đều sửa được" (B34, entry 133). 13:46: **Kết quả train của máy anh trai chưa có trên Drive:** chỉ có file D5 public 53 KB (`zac_v5_d5_public.tar.gz`, tạo 11/11). File này cho thấy giai đoạn 1 chạy từ khoảng 18:58 ngày 10/11, nên kết quả giai đoạn 1 ước khoảng trưa 11/11, giai đoạn 2 khoảng 16:00–20:00. **Gói bản cuối `…d1full` chưa có trên Drive (B43).** File D5 của anh trai khớp file 52,68 của laptop ở 581/634 dòng; 45 dòng khác do khác GPU. Đề xuất nộp file này làm mốc cùng máy cho luật 54,18 (B44, entry 132). Lượt dev_lao D1 trên laptop: trung bình 2 seed 43,91 / 55,82; seed 0 đạt nên bản cuối được chạy, trung bình 2 seed thiếu 0,2 ở chữ ASR (entry 131). 2026-11-09 22:42: **Anh chọn bản cuối dùng cả 2.139 mẫu D1.** Gói đã đóng lại với mặc định đó: **`~/zac_cloud_bundle_20261110_d1full.tar.gz`, 268.666.293 byte** (gói `…_d1final.tar.gz` lúc 22:35 đã xoá, đừng dùng). File hướng dẫn đã sửa theo gói mới; hai lượt bản cuối ước 8–9 giờ trên máy anh trai (entry 130). 22:35: **Dữ liệu D1 cho 11 app public đã xong (2.139 mẫu; bản cuối mặc định dùng 1.155 mẫu, 105 mỗi app). Gói cho máy anh trai đã đóng trên laptop và kiểm xong** (`~/zac_cloud_bundle_20261110_d1final.tar.gz`, 268.666.315 byte); file hướng dẫn tiếng Anh ở `cloud_results/anh_trai/BROTHER_AI_GUIDE_D1FINAL_2026-11-10_EN.md`. **Anh tải gói lên Drive và gửi file hướng dẫn; anh trai chỉ bắt đầu khi đợt cũ xong và Anh báo "go" (B43).** Lượt dev_lao: bước 65/380, seed 0 có điểm khoảng 08:30 ngày 10/11. API: Anthropic 30,12/100 USD; Meta 15,14/81 USD (entry 129). 21:45: **Anh: "Seed 0 đạt là chạy".** Hai lượt bản cuối bắt đầu ngay khi seed 0 của lượt dev_lao đạt cả hai ngưỡng (chữ PhoWhisper-ft ≥ 44,1 và chữ chuẩn ≥ 50,2), không chờ seed 1. Gói cho máy anh trai do laptop này đóng, không cần Leader (entry 128). 21:40: **Anh quyết B42 (qua một phiên phụ): bỏ 4 lượt đo nhánh app đã thấy; đợt GPU còn lại trên máy anh trai dành cho 2 lượt bản cuối (đủ 1.545 mẫu train + dữ liệu 11 app public).** Sinh dữ liệu public ngay, không chờ điểm dev_lao. **Luật thay bản nộp, ghi trước khi train: trung bình public 2 seed ≥ 54,18 (52,68 + 1,5).** `d1_seen_v1.jsonl` giữ lại, không train đợt này (entry 127). 21:30: **Nhánh app đã thấy: 6 trong 7 app ưu tiên đã viết, so với nhãn thật khớp 0,965, và đã sinh xong 752 mẫu (288 hỏi lại + 464 của 6 app).** Bỏ `email` và `flights.cancel` sau bước so. Chưa train nhánh này: cần 4 lượt trên cùng một máy (B42). Lượt đo dev_lao trên laptop chậm hơn ước tính: seed 0 có điểm khoảng 09:00 ngày 10/11, seed 1 khoảng 21:00. API: Anthropic 11,61/100 USD; Meta 6,38/81 USD (entry 126). 20:58: **Hai trần API tách riêng, không gộp:** Anthropic 100 USD tổng (đã dùng 5,56), Meta còn 81 USD tính từ 20:30 ngày 09/11 (đã dùng 3,14); code chặn ở 95 và 76. **Anh trai bắt đầu train lúc 18:30 ngày 09/11** (không phải 12:00): giai đoạn 1 xong khoảng 12:00–12:30 ngày 10/11, cả đợt xong khoảng 16:30–20:30. **Dữ liệu đo dev_lao đã sinh xong (633 mẫu); luật giữ/bỏ ghi trước ở entry 125; laptop train 2 seed, khoảng 21 giờ, xong khoảng 19:00 ngày 10/11.** Nhánh app đã thấy: phần hỏi lại đã viết và khớp nhãn thật 0,96; B41 xong (entry 125). 20:25: **Anh chọn `claude-opus-5-5` làm model viết chính. Sáu app của dev_lao đã vào bộ sinh, viết "mù" (chưa nhìn nhãn) rồi mới so với nhãn thật:** tool và cách lấy ID đúng hết; hỗn hợp bộ tham số khớp 0,845, lên 0,902 khi dùng tỉ lệ tham số tuỳ chọn đo trên app đã thấy. Thêm kịch bản dùng lại ID từ lượt trước (23% ID của nhãn thật đến từ history). **Anh giao nhánh D1 cho 46 app đã thấy; luật giữ/bỏ ghi ở entry 124. Một tiền đề của bản giao việc sai:** `final_state` chỉ chứa app mà nhãn đã ghi, không chứa state của app không ghi; đề xuất thay thế ở entry 124, chờ Anh xác nhận (B41). 19:18: **Bộ sinh kịch bản D1 chạy được cho cả 11 app mới của public** (1.100 kịch bản thử, nhãn nào cũng chạy qua bộ giả lập; phân bố nhãn gần train). **Thử viết câu nói với 3 model trên cùng 30 kịch bản (0,65 USD):** cả ba qua bộ kiểm code 30/30; đọc tay thì `claude-opus-5-5` và `muse-wonder-1.0` giữ đúng nghĩa, `muse-spark-1.3` rẻ nhất nhưng có 1 câu đổi nghĩa. **Anh đọc file so sánh và chọn model viết (B40).** Chưa làm: 6 app của dev_lao (để đo có nhãn), kho tên lớn hơn, bước kiểm đổi nghĩa, đưa catalog public vào bước tạo dữ liệu train (entry 123). 18:41: **Gói train đã nằm trên thư mục Drive (240 MB, Leader tải lên 08/11). Gói (và nhiều khả năng cả thư mục) vẫn để "bất kỳ ai có link đều sửa được"; cần chuyển sang "Hạn chế" ngay** (B34, entry 122). 18:22: **Gói train cho máy anh trai chỉ có trên máy Leader; laptop không tự tạo được** (thiếu file lý lẽ D2). File hướng dẫn tiếng Anh gửi anh trai đã điền kích thước và sha256 của gói (entry 121). 17:32: **Cửa 0 của D1 đạt:** quy tắc đọc lấy ID viết từ catalog khớp đúng 693/747 lệnh đọc lấy ID của nhãn train (92,8%); mẫu dùng 6 app của dev_lao không có lỗi quy tắc: 173/183 (94,5%, ngưỡng 80%). **Nhưng 849/1.599 lệnh đọc của nhãn không phải đọc lấy ID** (điều kiện, câu hỏi, tra giá trị, tra trước khi hỏi lại): phần này bộ sinh kịch bản phải tự quyết, và là rủi ro chính của cửa 1. Code ở nhánh `d1-program-first`. Việc kế: viết bộ sinh kịch bản; Anh tạo file key Anthropic (key Meta đã có trên máy) (entry 120, B39). 17:25: **Public có bật D5: 52,68** (bản thử không D5: 51,07; +1,61). Theo luật viết trước (≥ 50,77), **giữ D5**; điểm public tốt nhất của đội giờ là 52,68. **Leader đồng ý đưa D1 lên trước; trần API bỏ giới hạn; Claude bắt đầu cửa 0 của D1 (CPU, 0 USD).** Anh trai bắt đầu chạy khoảng 12:00 ngày 09/11, nên giai đoạn 1 xong khoảng 05:00–06:00 ngày 10/11, cả đợt xong khoảng 10:00–14:00 (entry 119). 17:15: **Anh muốn làm D1 (sinh dữ liệu "chương trình trước") bằng key Claude 100 USD và Meta 90 USD.** Claude đọc lại file đã gửi anh trai: một lệnh nhưng gồm 7 lượt train ở giai đoạn 1 (khoảng 17 giờ) và 2–3 lượt ở giai đoạn 2 (4–8 giờ), tổng 9–10 lượt, 22–26 giờ; vậy trước mốc chốt 13/11 máy anh trai chỉ còn chỗ cho khoảng một đợt nữa, không phải hai như entry 117 ghi. D1 có trần cao nhất nhưng tiền không phải nút thắt; đề xuất 3 cửa có mốc dừng, cửa 0 chạy CPU, 0 USD (entry 118). **Chờ Anh quyết B38.** 15:45: **Anh đã gửi gói cho anh trai chạy giai đoạn 1 (7 lượt train A0–A3). Trong lúc chờ, Claude đánh giá phương án của Leader và phân rã chỗ mất điểm trên dev_lao** (entry 117): 59 điểm đang mất gồm khoảng 27 điểm do chọn sai loại quyết định (làm / hỏi lại / dừng) và khoảng 28 điểm do quyết định đúng nhưng ghi sai; ASR lấy khoảng 10,5 điểm. Luật +3,0 có tỉ lệ thắng nhầm khoảng 2,5% mỗi nhánh nhưng chỉ bắt được 50% hiệu ứng thật cỡ +3. Kỳ vọng tới 16/11: 52–55, suôn sẻ 56–58, trần khoảng 60. **Chờ Anh quyết B37** (chạy D5 trên dev có nhãn bằng laptop; gửi Leader ba luật bổ sung viết trước khi có kết quả). Điểm public D5 (B36) chưa có. Nhật ký 112–117 chưa push. 04:02: **File public có bật D5 (search guard) đã xong, chờ Anh nộp (B36):** `lifemate/runs/pub_d5_2026-11-09/full/submission.jsonl`, 634 dòng, kiểm định dạng đạt, có `time`. 603/634 dòng giống hệt file thử 51,07; 30 dòng khác do guard tìm lại, 1 dòng do hạn 25 giây. Guard làm mất 9 lệnh hỏi lại mà file thử có, nên điểm có thể lên hoặc xuống. **Giữ D5 nếu điểm ≥ 50,77** (entry 116). 02:13: **B28 xong: image Docker 05/11 chạy đúng trên GPU và cho cùng kết quả với lúc chạy ngoài Docker** (lượt 1: 627/634 dòng giống hệt file 51,16; hai lượt chỉ khác 1 dòng, do hạn 25 giây). Còn L9: image chưa có `/code` và notebook. **D5 (search guard) đang chạy trên public, xong khoảng 04:10; Anh nộp, giữ D5 nếu điểm ≥ 50,77** (B36, entry 115). 00:21: File gửi anh trai bản tiếng Anh, có link Drive; còn thiếu kích thước và sha256 của gói, Leader điền (entry 114). 2026-11-08 23:45: Leader bàn giao nhánh `search-guard` (D5, D2, giai đoạn 1 với 7 lượt train); Anh chọn chạy D5 sau khi B28 xong (entry 112–113). 22:20: **B28 đang chạy trong Docker trên laptop:** image của leader nạp được, torch trong image có sm_120 (RTX 5090), 3 mẫu giống hệt file 51,16. Lượt 634 mẫu thứ nhất từ 22:19, xong khoảng 00:30; lượt thứ hai xong khoảng 02:40 (entry 111). 20:54: **Anh đã thêm tài khoản vào nhóm `docker`, nhưng B28 chưa chạy được:** app Claude mở từ trước khi thêm nhóm, và Ubuntu 26.04 không có `sg`/`newgrp`. **Anh đăng xuất rồi đăng nhập lại (hoặc khởi động lại máy), mở lại phiên này và nhắn "chạy B28"** (B31; entry 110). 20:25: **File public thử bằng cấu hình nộp cuối được 51,07** (file 05/11: 51,16; −0,09, đúng phần 25 giây cắt 9 dòng). Trang nộp nhận dòng có trường `time`. **Cấu hình nộp cuối đã chốt; việc còn lại là Docker (B28/B31, L9), hạn 11:59 ngày 16/11** (B35 xong; entry 109). 20:00: File public thử bằng đúng cấu hình nộp cuối đã xong, chờ Anh nộp (B35): `lifemate/runs/pub_trial_2026-11-08/full/submission.jsonl`, 634 dòng, kiểm định dạng đạt, có trường `time`. 625/634 dòng giống hệt file 51,16; 9 dòng khác đều do hạn 25 giây cắt các lời gọi cuối (entry 108). 17:57: Đang làm file public thử bằng đúng cấu hình nộp cuối; 3 mẫu giống hệt file 51,16. 16:45: **Pilot v2 không đạt luật ghi trước** (chữ ASR −0,46, cần +2,0); **dừng hướng dữ liệu sinh, giữ bản 05/11.** Việc còn lại là Docker: B28 chưa chạy, L9. Thư mục Drive đang mở công khai theo link (B34, entry 107). 2026-11-06 17:25: **Gói nằm trên thư mục Google Drive riêng; hướng dẫn đã sửa để tải gói và nộp kết quả qua thư mục đó** (bản có link nằm ngoài git; B33, entry 106). 17:20: **File hướng dẫn cho AI bên máy anh trai:** `docs/BROTHER_AI_GUIDE_PILOT_V2_2026-11-07.md`; Anh gửi kèm gói (B33, entry 105). 12:47: **Gói pilot v2 cho máy anh trai đã sẵn** (202 mẫu sinh, 4 lượt 4-bit, mỗi bên 2 seed; 9,36 USD, tổng API 52,39/80). Gửi được ngay tối nay (B33, entry 104). 11:45: Máy anh trai chỉ chạy 1 lần mỗi ngày. **Vẫn đủ cho dữ liệu sinh v2: cần 2 lần (pilot tối 07/11, train đủ dữ liệu tối 08–09/11), chốt 13/11**; chờ Anh duyệt (entry 103). 11:40: Anh hỏi train ở máy nào: **nếu train thì dùng máy anh trai; laptop để kiểm Docker** (entry 102). 11:35: **Kết quả gói v3 từ máy anh trai: không có adapter nào tốt hơn để thay vào image.** 4B bf16 so với 4B 4-bit đang nộp (chữ chuẩn): dev_random +5,70, dev_lao −2,12, gộp +1,56. Các mức này nằm trong độ lệch 2–4 điểm giữa hai lần train cùng công thức trên hai máy. Claude không đề xuất đổi sang bf16; B32 còn hướng dữ liệu sinh v2 (entry 101). 09:50: **File image đã tải xong (09:47), Docker đã cài; Anh chọn hướng cải tiến (B32).** Đóng gói bản 05/11 trước; có model tốt hơn thì thay một thư mục trong image (entry 100). 09:40: **Leader gửi image (L8); B28 chạy tối nay (B31),** vì Anh mang máy đi lúc 11:00. Trước 11:00, Anh cài Docker bằng `~/zac-c3/b28_setup_docker.sh` và tải file image (B30). **Hướng dẫn Docker của BTC:** máy chấm RTX 5090 32 GB, CUDA 13.2; gói nộp cuối phải theo `/code/predict.sh` → `/data` → `/result`, có notebook đo thời gian và trường `time` (L9, `docs/BTC_DOCKER_GUIDE_2026-11-06.md`) (entry 99). 02:04: **B28 trên laptop:** Anh cài Docker + NVIDIA toolkit (B30), leader gửi image và lệnh chạy (L8); hướng dẫn `docs/B28_LAPTOP_DOCKER_2026-11-06.md` (entry 98). 00:47: **B29: public 49,65 (thấp hơn 51,16), Docker giữ PhoWhisper-ft hiện tại.** Image leader đã build là bản cuối về model; còn B28 (kiểm image trên GPU 24 GB) (entry 95). 2026-11-05 18:15: **B27 xong: file public bằng PhoWhisper-ft-all sẵn để nộp** (`runs/e2e_public_q4b_all_phoftall_fix0497.jsonl`, B29); `predict.sh` 3 mẫu trên laptop đạt `"ok": true` (entry 94). 17:45: **B27 chạy tiếp** sau khi đóng băng từ 13:38; file public dự kiến xong khoảng 18:10–18:15 (entry 93). 13:38: Anh cần dùng máy, B27 đóng băng ở bước agent làm file public. Kiểm WER trên 54 mẫu đã qua: 7,65 → 7,08 (entry 92). 10:24: **Docker PhoWhisper-ft build xong (12,6 GB), chữ ASR khớp tham chiếu; bước agent hết VRAM trên GPU 4 GB của leader.** Cần chạy thử trên GPU lớn hơn; Anh quyết B28 (entry 91). 09:20: **B27 đang chạy từ 09:18:** fine-tune lại PhoWhisper trên gần đủ train, rồi kiểm WER trên 54 mẫu kiểm và làm file public; xong khoảng 14:00–14:30 (entry 90). 09:04: **Lượt prompt `xref` không qua cửa 1** (dev_lao chữ ASR −1,02, chữ chuẩn −0,69), dừng theo luật; PR #14 đã đóng (entry 88); laptop rảnh từ 06:38. Hướng dẫn leader đổi Docker sang PhoWhisper-ft: `docs/LEADER_DOCKER_PHOFT_2026-11-05.md` (B26, entry 87). Trước đó 00:30: **Public 51,16 với PhoWhisper-ft (+4,87 so với 46,29); Docker đổi sang PhoWhisper-ft** theo luật ghi trước. Tổng hệ thống khoảng 5,63B. Trước đó 18:41: **File nộp public bằng PhoWhisper-ft xong (18:40), chờ nộp (B25):** `~/zac-c3/lifemate/runs/e2e_public_q4b_all_phoft.jsonl`, 634 dòng, kiểm định dạng đạt; chỉ ASR khác file 46,29. ASR + agent mỗi mẫu trên laptop trung bình 10,4 giây (mốc 9,1). Luật: ≥ 46,29 thì Docker dùng PhoWhisper-ft (entry 85). Trước đó 16:46: B24 bắt đầu; model gốc vẫn còn trong cache, không phải tải (entry 84). Trước đó 16:10: **4B đọc chữ PhoWhisper fine-tune qua luật ghi trước:** gộp 495 dòng 46,17 → 47,88 (+1,71 [−1,68; +5,12]); dev_lao 39,20 → 41,30. Đề xuất làm file nộp public bằng PhoWhisper-ft; cần Anh cho tải lại model gốc 6,17 GB (B24, entry 83). Trước đó 14:49: **Anh duyệt cả hai thí nghiệm.** Chấm 4B với chữ PhoWhisper fine-tune đang chạy từ 14:44, xong khoảng 17:15. Lượt prompt `xref` ([PR #14](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/14)) hẹn tự chạy lúc 23:30, xong khoảng 07:30 ngày 05/11. Trần API thêm 30 USD (tổng 80), chỉ dùng khi cần. **Hạn Docker là 11:59 ngày 16/11 theo giờ máy (EST)** (entry 82). Trước đó 14:40: **Codex xong báo cáo chiến lược 4B** (`docs/research/CODEX_4B_STRATEGY_2026-11-04.md`): đạt 80 public trước 16/11 rất khó; đề xuất chấm 4B với chữ PhoWhisper fine-tune (khoảng 2,4 giờ GPU) và một lượt prompt `x-ref` + `returns` trên fit_lao (khoảng 8,5 giờ). Chờ Anh duyệt (B23, entry 81). Trước đó 13:51: **bản API `xhigh` + bỏ tham số hiếm được 75,52 trên public** (bản `minimal`: 69,47; 4B: 46,29). Đã viết prompt cho Codex phân tích sâu, tìm chiến lược cho 4B: `docs/CODEX_4B_STRATEGY_PROMPT_2026-11-04.md` (B22, entry 80). Trước đó 13:37: **file public bản API `xhigh` + bỏ tham số hiếm xong** (dev 80 mẫu: 64,75, bản trước 50,29); 634 dòng, kiểm đạt, 17,61 USD; **tổng API 43,03 / 50 USD** (Anh nâng trần lên 50). Chờ Anh nộp loại APIs/Others (B21, entry 79). Trước đó 12:53: **bản Meta API được 69,47 trên public** (4B: 46,29). Phân tích mất điểm: không có lỗi hệ thống nào giải thích khoảng cách 50 điểm tới top; 4B mất điểm rải ở nhiều chỗ (app chưa thấy, ASR, ghi sai); model API thiếu quy ước tham số tuỳ chọn, sửa được khoảng +7 trên dev (entry 78). Trước đó 12:45: **file nộp public bản API Meta xong** (`muse-spark-1.3`, cùng pipeline, chỉ thay model): 634 dòng, kiểm định dạng đạt, 6,75 USD (tổng API đã chi 21,15 / 30 USD). Chỉ để tham khảo ở cột APIs/Others; Docker vẫn dùng 4B ([PR #13](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/13), entry 77). Trước đó 12:22: **điểm public lần 4: 46,29** (adapter train trên đủ 1.545 mẫu; lần 3: 45,39, +0,90). Theo luật ghi trước, **Docker dùng `ckpt/q4b4_all/final`** (entry 76). Trước đó 07:55: **train lại trên đủ 1.545 mẫu xong 06:03, file nộp public mới xong 07:34**: `runs/e2e_public_q4b_all.jsonl`, 634 dòng, kiểm định dạng đạt; chờ Anh hoặc leader nộp (B19, entry 75). Trước đó 00:15: **laptop train lại 4B trên đủ 1.545 mẫu từ 00:13** (Anh bảo chạy ngay; tắt hẹn giờ 00:30). Train xong khoảng 06:35, file nộp public xong khoảng 08:20–08:45 (entry 74). Trước đó 2026-11-03 17:23: Anh nhờ Claude tự review và merge [PR #12](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/12); review đạt, đã merge vào `q4b-laptop` lúc 17:22 (commit `a2615ee`, entry 73). Trước đó 16:27: theo yêu cầu Anh, lượt train lại trên đủ 1.545 mẫu **tự chạy lúc 00:30 ngày 04/11** (chỉ khi đã cắm sạc; xong khoảng 08:30–09:00). Mở [PR #12](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/12): bước khởi động không tính giờ (mẫu đầu 110 → 13 giây), `predict.sh` mặc định 4B 4-bit, hạn 25 giây (entry 72). Trước đó 15:48: Anh hỏi lượt chữ trộn cho biết gì và vì sao còn train lại; Claude trả lời (entry 71). Trước đó 15:27: chấm dev_lao bằng chữ chuẩn xong 15:26: 53,40 → 49,97; gộp chữ chuẩn 59,15 → 57,54; script in RULE FAIL. Laptop rảnh từ 15:27, chờ Anh tự bật B17 (entry 70). Trước đó 15:11: Anh chọn tự bật lượt train lại trên đủ 1.545 mẫu sau (B17); laptop rảnh sau khoảng 15:30 (entry 69). Trước đó 15:07: **chữ trộn không qua luật gộp**: dev_lao chữ ASR fine-tune 39,20 → 35,85 (−3,35); gộp 495 dòng 46,17 → 45,49 (−0,69, ngưỡng +1,0). Bỏ chữ trộn; đã chuẩn bị train lại 4B chữ chuẩn trên đủ 1.545 mẫu rồi làm file nộp public (khoảng 8 giờ laptop), chờ Anh bật (B17, entry 68). Trước đó 08:56: **lượt chữ trộn qua cửa 1 trên dev_random** (chữ ASR fine-tune 54,01 → 56,32, +2,31; chữ chuẩn 65,61 → 66,05, +0,43; khoảng tin cậy còn chứa 0); laptop chạy cùng cách trộn trên fit_lao từ 08:54, chấm dev_lao xong khoảng 15:40, rồi quyết bằng điểm gộp 495 dòng (entry 67). Trước đó 01:05: ghi kế hoạch sau lượt chữ trộn theo hai nhánh qua / không qua cửa 1 (entry 66). Trước đó 00:54: laptop khởi động lại lúc 00:37 làm dừng train ở bước 10; chạy tiếp từ 00:53, chấm xong khoảng 07:25; B16 chưa cần (entry 65). Trước đó 00:22: **laptop train 4B học chữ trộn từ 00:19** (nửa chữ chuẩn, nửa chữ Whisper-turbo), chấm dev_random xong khoảng 07:05; Colab miễn phí (T4) không dùng được để train, Colab trả phí chưa cần (entry 64). Trước đó 2026-11-02 22:44: đề xuất chiến lược tiếp: 4B học trên chữ trộn, rồi train lại trên đủ train, rồi Docker; chờ Anh chọn (entry 63). Trước đó 22:39: **pilot dữ liệu sinh không đạt**, cả chữ ASR (39,20 → 37,12) lẫn chữ chuẩn (53,40 → 50,57); không dùng, không sinh cho 11 app public; đã chi 12,57 USD; GPU laptop rảnh (entry 61). Trước đó 22:17: pilot dữ liệu sinh **không đạt**: dev_lao chữ ASR 39,20 → 37,12 (−2,09 [−7,22; +3,01]); chữ chuẩn đang chấm (entry 61). Trước đó 21:16: train pilot xong 21:15, đang chấm dev_lao, xong khoảng 22:45 (entry 61). Trước đó 20:55: train pilot ở bước 300/311, xong cả chấm khoảng 22:40–23:10 (entry 61). Trước đó 20:23: bước 280/311. Trước đó 15:47: điểm public lần 3: **45,39** với agent 4B (lần 2: 35,24; dev gộp 46,17; entry 62). Trước đó 14:54: file nộp public 4B xong (634 dòng, kiểm định dạng đạt), chờ Anh nộp; pilot sinh 280/384 mẫu đạt, 11,55 USD (tổng đã chi 12,57 USD); train pilot tự bật 14:52, xong khoảng 22:30–23:00 (entry 61). Trước đó 13:40: trần 30 USD; pilot sinh bằng muse-wonder-1.0 đang chạy; script train pilot sẵn (entry 60). Trước đó 13:20: bài thử sinh dữ liệu đạt điều kiện đầu (t20 14/20, t12 9/12), chờ Anh chấm độ tự nhiên (entry 60). Trước đó 13:12: bài thử 20 mẫu đang chạy; trần 10 USD; đánh giá VieNeu (entry 60). Trước đó 12:35: viết xong bộ sinh dữ liệu (PR #11), bài thử 20 mẫu chờ key Meta (entry 60). Trước đó 12:20: credit Claude chưa dùng được, pilot có thể dùng model chữ của Meta (entry 59). Trước đó 12:15: Anh tự chạy file nộp public bằng 4B; đánh giá ý tưởng sinh dữ liệu bằng Claude API, đề xuất pilot (entry 59). Trước đó 10:20: chốt Qwen3-4B làm model agent; gộp 495 dòng chữ ASR fine-tune 33,07 → 46,17 (entry 58). Trước đó 03:40: 4B 4-bit thắng rõ trên dev_lao (+14,65 chữ ASR fine-tune, +17,78 chữ chuẩn); laptop chạy 4B trên fit_random để quyết bằng điểm gộp, dự kiến xong khoảng 10:00 (entry 57). Trước đó 2026-11-01 20:55: lượt 4B chạy lại từ 20:47, dự kiến xong khoảng 03:00 ngày 02/11 (entry 56). Trước đó 10:40: lượt 4B tạm dừng vì laptop mang đi học; thêm lưu và chạy tiếp (entry 56). Trước đó 09:30: train Qwen3-4B 4-bit, luật chọn đặt trước (entry 55). Trước đó 08:25: bắt đầu phần agent (entry 54). Trước đó 08:11: điểm public lần 2 là 35,24 (entry 53). Trước đó 01:05: ASR fine-tune (entry 52). Trước đó 2026-10-31 21:08: các dòng về laptop, B-up và giới hạn thời gian theo entry 48–50; bảng điều phối mới nhất ở đầu `HUMAN_TODO.md`. Cập nhật trước: 10:30. Giai đoạn 2 của D và baseline đầu-cuối đã xong (entry 30–31); kế hoạch ngày 31/10 ở `docs/PLAN_2026-10-31.md`; Anh đã chọn lượt cloud, gói v3 sẵn (entry 32). Bản trước xem lịch sử git.*

- **Baseline phần agent: đã xong và tái lập được.** Model đọc chữ chuẩn `audio_text`, chưa qua ASR.

  | Mốc | Train → chấm | Điểm |
  |---|---|---|
  | Zero-shot Qwen3-1.7B | – → dev_random / dev_lao | 9,90 / 10,88 |
  | **SFT Qwen3-1.7B LoRA, 1 epoch (mốc chính)** | fit_random → dev_random (233 mẫu) | **53,92** (chạy lại giống hệt 233/233 mẫu) |
  | **B0** (đo trên app chưa thấy) | fit_lao → dev_lao (262 mẫu) | **35,53**: hỏi lại 7,48; execute 39,73; ngoài phạm vi 71,43 |
  | **Qwen3-4B 4-bit QLoRA** (02/11, entry 57; cùng công thức B0) | fit_lao → dev_lao | **53,40** (chữ Whisper-turbo fine-tune: 39,20, so với 24,55 của 1.7B) |
  | **Qwen3-4B 4-bit QLoRA** (02/11, entry 58; **model agent đã chốt**) | fit_random → dev_random | **65,61** (chữ Whisper-turbo fine-tune: 54,01, so với 42,64 của 1.7B) |

  - Chi tiết: [`docs/EVAL_2026-10-29.md`](docs/EVAL_2026-10-29.md).
  - Code ở [PR #1](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/1) → [#2](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/2) → [#3](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/3), chưa merge.
- **Baseline đầu-cuối theo đề (audio → ASR → agent): đã có** (31/10, entry 31, [`docs/E2E_BASELINE_2026-10-31.md`](docs/E2E_BASELINE_2026-10-31.md)).

  | Agent đọc | dev_random | dev_lao |
  |---|---:|---:|
  | Chữ chuẩn `audio_text` | 53,92 | 35,53 |
  | **Whisper-turbo (chưa fine-tune; được chọn)** | **31,69** | **17,14** |
  | PhoWhisper-large (chưa fine-tune) | 27,90 | 15,58 |
  | Whisper-turbo fine-tune (01/11, entry 52; được chọn tới 04/11) | 42,64 | 24,55 |
  | **PhoWhisper-large fine-tune (01/11, entry 52; Docker dùng từ 05/11 sau public 51,16, entry 86)** | **43,04** | **24,85** |

  - ~~**Lỗi ASR là chỗ mất điểm lớn nhất hiện nay** (khoảng 20 điểm). ASR sai 26–31% số từ; người nói hiếm khi đọc lệch kịch bản.~~ *(01/11, entry 52: sau fine-tune, ASR sai 11–14% số từ và chỉ còn làm mất 11 điểm gộp. Agent mất khoảng 56 điểm ngay cả trên chữ chuẩn, nên giờ là đòn bẩy lớn nhất.)*
  - **File nộp public đã kiểm:** `lifemate/runs/e2e_public_turbo.jsonl` (634 dòng), đã nộp: **25,93** (entry 46). **File mới với ASR fine-tune:** `lifemate/runs/e2e_public_turboft.jsonl` (01/11, entry 52), Anh đã nộp: **35,24** (entry 53). **File 4B** `~/zac-c3/lifemate/runs/e2e_public_q4b.jsonl` (02/11, entry 61), Anh đã nộp: **45,39** (entry 62). File 4B học đủ 1.545 mẫu `~/zac-c3/lifemate/runs/e2e_public_q4b_all.jsonl`: **46,29** (entry 76). Cùng adapter với chữ PhoWhisper-ft `~/zac-c3/lifemate/runs/e2e_public_q4b_all_phoft.jsonl`: **51,16** (entry 86).
  - Thời gian trên laptop: trung bình 2,9 giây mỗi mẫu, chậm nhất 9,7 giây. Chưa có Docker offline, chưa đo trên A30.
  - Code: [PR #4](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/4), chưa merge.
- **Kế hoạch hôm nay (31/10):** [`docs/PLAN_2026-10-31.md`](docs/PLAN_2026-10-31.md). Ưu tiên: fine-tune ASR (leader), train agent trên chữ ASR và 4B (Anh chạy cloud), Docker (leader).
- **Điểm yếu lớn nhất đã đo:** hỏi lại, nhất là với app chưa thấy (0/23 mẫu ở dev_lao), và thiếu lệnh ghi do làm thiếu vế (entry 28).
  - **Thí nghiệm D bị loại** (entry 30, [`docs/D_PHASE2_2026-10-31.md`](docs/D_PHASE2_2026-10-31.md)): thua lượt đối chứng B-up, chỉ nhân bản mẫu hỏi lại thật. B-up: hỏi lại 7,5 → 30,0, tổng 35,53 → 36,94 (chưa chắc).
  - B-up trên fit_random (laptop, xong 31/10 20:19, entry 49): dev_random 53,92 → 51,19 (−2,72), giảm quá 1 điểm nên **không giữ**. Agent mặc định vẫn là SFT thường.
- **Laptop đã xong 2 lượt (13:48–20:19):** agent học trên chữ turbo không đáng dùng (entry 48); B-up không giữ (entry 49). GPU laptop rảnh, chờ transcript ASR fine-tune từ Colab để chấm. Giới hạn 30 giây (tính cả ASR) và chốt chặn ID: [PR #9](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/9), chờ review (entry 50). Kaggle xong mà không train vì T4 quá chậm; public lần đầu 25,93 (entry 46).
- **Anh trai của Anh (làm ở Google) sẽ chạy gói v3** bằng lệnh một dòng; Anh báo đã hỏi và được cho phép (entry 33–34). Chờ 2 file kết quả gửi về.
- **Dự phòng** nếu máy anh trai là TPU (entry 35, [`docs/FREE_GPU_2026-10-31.md`](docs/FREE_GPU_2026-10-31.md)): 1.7B trên laptop (chờ Anh đồng ý) hoặc Kaggle T4; 4B chỉ trên GPU trả phí.
- **Chờ Anh:**
  - Cùng leader làm mục 0 của [`HUMAN_TODO.md`](HUMAN_TODO.md) (0.1–0.8), trên máy leader.
  - Review PR #1 → #2 → #3 → #4 → #5 → #6.
  - Thuê cloud và chạy gói v3 `~/zac_cloud_bundle_20261031_v3.tar.gz` theo [`docs/CLOUD_TRAIN_2026-10-31.md`](docs/CLOUD_TRAIN_2026-10-31.md); các lượt Anh chọn đã bật sẵn (entry 32).
  - Đọc tay `lifemate/gen/review_v1_30.md` và `review_1b.md`.
- **Việc tiếp theo:** xem [mục 8](#8-việc-tiếp-theo).

---

## 1. Đề bài (tóm tắt)

### 1.1 Nhiệm vụ

Xây agent nhận **yêu cầu bằng giọng nói tiếng Việt** (có thể lẫn từ tiếng Anh, giọng Bắc/Trung/Nam) và **gọi tool** để thực hiện.

- **Đầu vào:**
  - `audio`: lượt nói cuối cần xử lý.
  - `context`: `current_time`, `timezone`, `location`, `user_profile` (tên, nhà, nơi làm, thành phố), `installed_apps` (app đã cài kèm danh sách tool).
  - `history`: các lượt trước. Lượt user chỉ có audio; lượt assistant có `text`, `tool_calls`, `tool_results`.
  - Môi trường giả lập `zaic_tools.ToolEnv` giữ dữ liệu app. Chỉ được đọc và ghi qua tool.
- **Đầu ra:** mỗi mẫu một dòng `{"id", "tool_calls": [{"name", "arguments"}...], "state_hash"}`, trong đó `state_hash = env.get_state_hash()`.
- **3 kiểu hành vi:**
  - Thực thi: gọi tool cho tới khi đạt trạng thái mong muốn.
  - Hỏi thiếu thông tin: `sys.ask_missing_info(tool_name, params)`, có thể sau vài call khác.
  - Ngoài phạm vi: `[]`.

### 1.2 Chấm điểm

```
gold rỗng           -> 1 nếu nộp rỗng, ngược lại 0
hash sai hoặc M = 0 -> 0
còn lại             -> F1 = 2PR/(P+R),  P = M/(M+U),  R = M/|G|
Final = 100/N * Σ Score_i
```

- **Một call khớp với call đáp án khi:**
  - Cùng tên tool.
  - Mọi tham số không phải fuzzy giống hệt.
  - Mọi tham số fuzzy (`x-match: fuzzy`) có token-F1 > 0.6, sau khi lowercase và chuẩn hoá Unicode NFC.
- Mỗi call chỉ khớp được tối đa một call; không xét thứ tự.
- `U` là số call thừa, **tính cả call bị từ chối vì sai schema**.
- `sys.ask_missing_info` được chấm như mọi tool khác.
- **Phân hạng khi bằng điểm:** chấm lại F1 bỏ qua hash; nếu vẫn bằng, đội có thời gian trung bình mỗi mẫu thấp hơn xếp trên.

### 1.3 Ràng buộc kỹ thuật

- **Kích thước model:** toàn hệ thống (ASR + LLM + mọi thành phần khác) **dưới 6B** tham số; LLM **dưới 5B** và context tối đa **16.384** token.
- **Thời gian và phần cứng chấm:** **30 giây mỗi mẫu**; 1 GPU A30 24GB, CPU Xeon Gold 6442Y 16 nhân, RAM 64GB. Chạy offline hoàn toàn, không gọi API ngoài.
- **Tái lập:** cố định mọi seed, giải mã greedy hoặc temperature 0. Nếu chạy lại ra kết quả khác, BTC chạy Docker 5 lần và lấy điểm trung bình.
- **Truy cập dữ liệu:**
  - **Không được đọc, copy hay parse file trong `<split>_environment/`** (kể cả `state.json`).
  - Mỗi mẫu đúng **một** `ToolEnv`, và mọi call đã gọi phải có trong bài nộp.
- **Dữ liệu và model được dùng:** dữ liệu công khai và model mã nguồn mở phát hành **trước 26/10/2026**, licence cho phép. Dùng LLM hoặc TTS ngoài để sinh dữ liệu tổng hợp lúc phát triển là được, lúc suy luận thì không. **Cấm gán nhãn public_test hoặc private_test** để train.
- **Phát tán dữ liệu:** README của gói dữ liệu cấm chia sẻ bộ dữ liệu, nên **không bao giờ commit `data/`**.

### 1.4 Lịch

| Mốc | Thời gian |
|---|---|
| Vòng public test | 26/10 – 16/11/2026, tối đa 5 lần nộp mỗi ngày |
| **Nộp Docker** (code train + suy luận + dữ liệu, link Google Drive + checksum, tối đa 2 lần, lấy lần cuối) | **16/11/2026 23:59 GMT+7** |
| Private test (BTC mount `/data`, chạy script suy luận, lấy `result/submission.jsonl`) | Phát đề 20/11 9:00 → nộp trước 23/11 23:59 |
| Công bố top 2 | 02/12/2026 |

### 1.5 Ý kiến của BTC (đội nhận được)

Điều gì thể lệ không cấm thì được làm. Vì vậy được dùng catalog và `zaic_tools` của public_test để sinh dữ liệu tổng hợp. Gán nhãn hoặc pseudo-label audio và yêu cầu của tập test vẫn bị cấm.

---

## 2. Dữ liệu — số liệu đã đo

**Gói dữ liệu:** `v3.2.0`, build 2026-10-24. Train có 1545 mẫu (có nhãn), public_test có 634 mẫu. Giải nén vào `data/train+public_test/`.

### 2.1 Cấu trúc

- `<split>.jsonl`: mỗi dòng một mẫu. Train có thêm `audio_text` (transcript của mọi lượt user) và `label` gồm `tool_calls`, `tool_results`, `final_state`.
- `<split>_tools_catalog.json`: schema version 2.7.0. Mỗi tool có `name`, `kind` (`read` / `write` / `meta`), `parameters` (JSON Schema mở rộng với `x-ref`, `x-match: fuzzy`, `x-one-of`), `returns`.
- `zaic_tools/`: **mỗi split một bản riêng**. Ví dụ `utils.py` khác nhau ở:
  - `LIVE_APPS`: train gồm exchange_rate, fuel_price, gold_price, lottery, weather; public chỉ gồm fuel_price, gold_price, weather.
  - `FREE_TEXT_KEYS`: public thêm `text`, bỏ `expression`.

  Luôn dùng đúng bản `zaic_tools` của split đang chạy.
- **`state_hash`:** sha256 của `canon(state)`. Hàm `canon` bỏ `_meta`, bỏ các app thông tin (live), bỏ các trường text tự do; lowercase chuỗi, gộp khoảng trắng, coi `700 cm` = `700cm`, sắp xếp danh sách giá trị đơn.
- **Call bị từ chối** (`ok: false`) chỉ khi sai schema. ID không tồn tại, không đủ tiền… thì vẫn trả `ok: true, done: false` và không đổi state.
- **`env.validate()` không bị ghi vào log**, nên kiểm schema trước khi gọi không tốn điểm.
- Gói không kèm bộ chấm F1; đội tự viết (xem mục 6).

### 2.2 App và tool

| | Số app | Số tool |
|---|---|---|
| Train | 46 | 147 |
| Public test | 36 | 122 |
| Chung cả hai (schema giống hệt) | 25 | 88 |
| **Chỉ có ở public** | **11** | **34** |
| Chỉ có ở train | 21 | — |

- **App chỉ có ở public:** ecommerce, event_tickets, grocery, habit_tracker, pantry, parking, public_transit, recipes, stocks, train_bus_tickets, translator.
- **Kết luận:** private test gần như chắc chắn cũng có app mới, nên model phải **đọc và hiểu schema**, không được học thuộc từng app.

### 2.3 Thống kê tập train

- **Loại mẫu:**

  | Loại | Số mẫu | Tỉ lệ |
  |---|---|---|
  | Thực thi | 1217 | 79% |
  | Gọi tool rồi mới hỏi thiếu thông tin | 157 | 10% |
  | Chỉ hỏi thiếu thông tin | 60 | 4% |
  | Ngoài phạm vi | 111 | 7% |

- **Số call mỗi mẫu:** 0 call: 111 · 1: 369 · 2: 428 · 3: 359 · 4: 161 · 5: 107 · 6: 10.
- **History:** 0–24 lượt, khoảng 1/3 số mẫu không có history.
- **App cài mỗi mẫu:** trung bình 9,2 app, khoảng 32,5 tool.
- **Tool hay gặp nhất:** `contacts.search` 234, `sys.ask_missing_info` 217, `smart_home.light_set` 126, `reminders.create` 115, `bill_payment.list_bills` 112.
- **Phát lại đáp án** bằng `zaic_tools` tái tạo đúng `final_state` ở **1545/1545** mẫu.
- **Audio:** WAV 16kHz mono, trung bình 5,1 giây, dài nhất 17,1 giây. Public có 1933 file wav, vì phải ASR cả các lượt user trong history.
- **Dữ liệu cho ASR từ train:** 5036 câu nói có transcript, tổng 6,83 giờ.
- **Múi giờ:** mọi mẫu đều là `Asia/Ho_Chi_Minh`. Thành phố: Hà Nội 791, TP.HCM 343, Đà Nẵng 242, Cần Thơ 92, Huế 77.

### 2.4 Độ dài prompt (tokenizer Qwen3, khoảng 2,9 ký tự mỗi token)

- Schema JSON thô của các tool đã cài: trung bình 12,8K ký tự, dài nhất 24,6K. Phải viết gọn lại.
- Sau khi viết gọn (system prompt khoảng 2,3K token):

  | Split | Trung bình | p95 | Dài nhất |
  |---|---|---|---|
  | Train (tính cả các bước gọi tool) | ~3,1K token | 4,6K | 6,1K |
  | Public (ước lượng) | ~2,7K token | — | 5,3K |

  Còn dư nhiều so với 16K.

---

## 3. Phát hiện quan trọng (ảnh hưởng trực tiếp tới điểm)

1. **State hash là cổng "được hoặc không":** một lệnh ghi sai là mẫu đó được 0 điểm. Trường text tự do (`content`, `title`, `note`, `address`, `pickup`…) **không tính vào hash**, chỉ cần token-F1 > 0.6.
2. **Call chỉ đọc vẫn tính vào F1**, nên phải bắt chước đúng quy ước của đáp án:
   - `smart_home.get_status`: gọi `{}` 93/107 lần.
   - `calendar.list_events`: gọi `{}` 87/105 lần.
   - `smart_home.light_set` có `get_status` đứng trước trong 113/126 mẫu.
   - Đọc thừa thì giảm precision, thiếu bước đọc thì giảm recall.
3. **`ask_missing_info` luôn là call cuối cùng:** 217/217 lần. Tham số hay hỏi nhất là `contact_id` (73), `amount` (21), `time` (10). Ví dụ: tìm ra 2 người tên "Minh" → `contacts.search` rồi `ask_missing_info(phone.call, [contact_id])`.
4. **Ngoài phạm vi không chỉ là thiếu app.**
   - Khoảng 40% là người dùng hủy hoặc phủ định ("à thôi khỏi", "đừng tắt đèn bếp").
   - Phần còn lại là chưa cài app, chỉ trò chuyện, hoặc thông tin đã có trong history.
   - **Không được thay bằng app gần giống:** "đặt taxi" khi chỉ có `bike_rental` → `[]`.
   - Câu "đặt sữa chua bên app đi chợ" ở train là `[]` vì chưa cài app, trong khi `grocery` là app thật ở public. Model phải quyết định dựa trên app đã cài, không dựa trên chủ đề câu nói.
5. **Có logic điều kiện:** "mưa thì hủy buổi tập" → tra thời tiết; nếu không mưa thì dừng, không hủy.
6. **Phải dùng lại thông tin trong history:** 294/1020 call có tham số ID lấy ID chỉ xuất hiện trong history. Vì vậy prompt phải giữ `tool_results` của history.
7. **27% mẫu có tham số ngày giờ**, ví dụ "thứ tư trừ 3 tiếng", "45 phút sau". Model nhỏ hay tính sai, nên đưa bảng ngày vào prompt.
8. **Lệnh ghi lặp lại có thể hợp lệ:** đổi điểm 2 lần để lấy 2 vé. Chỉ được bỏ trùng các call đọc.
9. **Lượt assistant trong history theo quy ước khác với đáp án được chấm:**
   - `get_status`: history dùng `{room}` 124/167 lần, đáp án dùng `{}`.
   - `list_events`: history có khoảng ngày 130/139 lần, đáp án dùng `{}`.
   - Khi hỏi lại, history chỉ nói thành câu thay vì gọi `ask_missing_info`; history chỉ có 22 lần `ask_missing_info`.

   **Không được dùng nguyên các lượt history làm đích huấn luyện.**
10. **Transcript và ngôn ngữ nói:**
    - Kiểu viết số trộn lẫn: "1 tiếng", "50 nghìn", số điện thoại đọc từng chữ số.
    - Người nói tự sửa giữa câu: "5 giờ nhé, à không, 5 rưỡi".
    - Phương ngữ: "mô, rứa, hông, coi, giùm".
    - Từ tiếng Anh xen vào: "book", "target", "deadline".
11. **Các tool search tự bỏ dấu khi so khớp** (Hương / Hường đều thành "huong"), nên ASR nghe sai dấu ở tên người ít gây hại.
12. **Tham số của lệnh ghi đến từ đâu** (2681 giá trị không fuzzy):

    | Nguồn | Tỉ lệ |
    |---|---|
    | Kết quả tool ngay trong lượt | 46% |
    | History | 15% |
    | Ngày giờ tự tính | 15% |
    | Số tự tính hoặc chuẩn hoá chữ thành số | 11% |
    | Enum hoặc boolean | 9% |
    | Chép nguyên văn lời nói | **gần 0%** |

    605/1545 mẫu (39%) có tham số của lệnh ghi phải tính từ lời nói. Kỹ năng cốt lõi là chọn đúng đối tượng và tính đúng, không phải chép lời.
13. **Query `contacts.search` là tên lưu trong danh bạ**, không phải lời người nói:
    - 166/204 trùng nguyên văn lời nói.
    - 31/204 chỉ khác chữ hoa ("bác Ba" → "Bác Ba").
    - 7/204 là tên đầy đủ ("cô Mai" → "Cô giáo Mai"). Đây là trần điểm không vượt được.
14. **Luật "đọc trước khi ghi":** cả 11/11 lần bật đèn mà không gọi `get_status` trước đều là do thông tin thiết bị đã có trong history.

---

## 4. Kiến trúc đã chốt

```
audio lượt cuối + audio các lượt user trong history (ASR theo batch)
  → ASR (~0,8B) → chuẩn hoá chữ thành số (ITN)
  → prompt: luật + profile + bảng ngày (−7…+14) + schema tool viết gọn + history (kèm tool_results)
  → vòng lặp agent Qwen3 (greedy): LLM sinh tool call → env.validate() → env.call() → kết quả trả lại LLM → …
  → dừng khi: LLM báo xong / vừa gọi ask_missing_info / đủ 8 bước / chạm mốc ~25 giây
```

- **Chọn kiến trúc nối tầng (ASR → LLM), không dùng audio-LLM end-to-end.** Các model audio-LLM dưới 5B nghe tiếng Việt còn yếu, khó debug, và không tận dụng được `audio_text` để train và đánh giá riêng từng phần.
- **LLM:** Qwen3-4B-Instruct-2507 (Apache-2.0, khoảng 4,0B tham số), chế độ không suy nghĩ. **Bắt buộc fine-tune (SFT)**, vì zero-shot không biết các quy ước của đáp án. Nên rà Hugging Face xem có model mới hơn phát hành trước 26/10/2026 không.
- **ASR:** ứng viên là Whisper-large-v3-turbo (0,8B, MIT) và PhoWhisper-medium/large (0,77B/1,55B, BSD). Đo bằng **độ chính xác của số, giờ, tên** chứ không chỉ WER. Lỗi ASR ở các lượt history ít nguy hiểm hơn ở lượt cuối.
- **Ngân sách tham số:**

  | Cấu hình | Thành phần | Tổng |
  |---|---|---|
  | A (đề xuất) | Qwen3-4B + Whisper-turbo hoặc PhoWhisper-medium | ~4,8B |
  | B | Qwen3-4B + PhoWhisper-large | ~5,6B (sát trần) |
  | C (dự phòng nếu chậm) | Qwen3-1.7B + PhoWhisper-large | ~3,3B |

- **Lớp code kiểm soát lỗi:**
  - `validate()` trước mỗi call; sai thì trả lỗi lại cho model, không gọi thật.
  - Chỉ bỏ trùng call đọc.
  - Dừng ngay sau `ask_missing_info`.
  - Bảng ngày trong prompt.
  - Giới hạn số bước và thời gian.
- **Đòn bẩy lớn nhất:** dữ liệu tổng hợp với **app mới** (LLM mạnh sinh app, schema, simulator theo khuôn `zaic_tools/apps/base.py`, kiểm chứng bằng cách chạy thật), kèm tăng cường bằng đổi tên schema và gỡ app.
- **Đánh giá 2 tầng:** dùng `audio_text` để đo trần điểm của agent; dùng ASR thật để đo điểm bị mất do nghe sai.

---

## 5. Đội và tài nguyên

| Người | Máy | Phụ trách |
|---|---|---|
| Anh (git `Anh-08`) | RTX 4070 Laptop 8GB VRAM (màn hình chiếm sẵn khoảng 1,7GB), RAM 14GB | Agent / LLM: bộ chấm, prompt, SFT, dữ liệu tổng hợp, train |
| Leader | RTX 3050 4GB | ASR, chuẩn hoá số, đóng Docker, đo thời gian trên GPU 24GB |

- **Ngân sách không giới hạn**, thuê GPU cloud tuỳ ý.
- **Repo:** https://github.com/Nguyen-Le-Tuan/ZAIC_2026. Bản clone local chính là thư mục `~/Zalo AI Challenge`. Nhánh làm việc của phần agent là `agent-pipeline`.
- **Quy tắc git:** tài liệu commit thẳng vào `main`; code mới mở PR vào `main`.

---

## 6. Code đã có (`lifemate/`)

### 6.1 Thành phần

| File | Việc |
|---|---|
| `lifemate/data.py` | Đọc split và catalog; nạp đúng `zaic_tools` của split. Code agent không đọc `*_environment/`. |
| `lifemate/scorer.py` | Bộ chấm local theo công thức của BTC. |
| `lifemate/prompt.py` | Prompt ChatML của Qwen3 với thẻ `<tool_call>`/`<tool_response>`, schema viết gọn một dòng mỗi tool, bảng ngày, profile, history. |
| `lifemate/agent.py` | Vòng lặp agent kèm lớp kiểm soát. Các backend: `openai` (vLLM server), `vllm` (trong tiến trình, cho Docker), `hf` (transformers + LoRA), `oracle` (phát lại đáp án), `PrefixBackend`. |
| `lifemate/infer.py` | Chạy cả split, ghi `submission.jsonl` và trace. `--text oracle` dùng `audio_text`; `--text asr` đọc file ASR. |
| `lifemate/sft.py` | Sinh dữ liệu SFT (xem 6.3). |
| `lifemate/train.py` | LoRA SFT bằng PyTorch thuần (xem 6.4). |
| `scripts/make_splits.py` | Chia tập dev. |
| `scripts/check_sft.py` | Kiểm prompt SFT khớp suy luận, ranh giới token. |
| `scripts/count_tokens.py` | Đo độ dài prompt. |
| `scripts/cloud_baseline.sh` | Baseline zero-shot bằng vLLM trên cloud. |
| `scripts/train_local.sh` | Chạy qua đêm: baseline zero-shot → train → đánh giá. |

- **Định dạng file ASR** (giao kèo giữa phần ASR và phần agent): `asr/<split>.jsonl`, mỗi dòng `{"audio": "audio/<id>/<file>.wav", "text": "..."}`, phủ **mọi** file wav (cả lượt cuối lẫn các lượt user trong history).
- **3 điểm đề không nói rõ**, bộ chấm local chọn cách khắt khe:
  - Tập tham số phải giống hệt nhau.
  - Chuỗi không fuzzy phải khớp chính xác.
  - Token tách theo khoảng trắng.

  Cần xác nhận bằng lần nộp public đầu tiên.

### 6.2 Kiểm chứng đã chạy

| Kiểm tra | Kết quả |
|---|---|
| Nộp đúng đáp án train | 100,0 |
| Nộp toàn rỗng | 7,18 (đúng bằng tỉ lệ mẫu ngoài phạm vi) |
| Bỏ một call đọc đầu tiên | 88,1 (hash vẫn đúng, F1 giảm) |
| Vòng lặp agent phát lại đáp án, toàn bộ train | 100,0 (lần đầu ra 99,87 do bỏ trùng cả lệnh ghi; đã sửa thành chỉ bỏ trùng call đọc) |
| Lớp kiểm soát trên public_test | Call sai schema và JSON hỏng bị chặn, 0 call lọt vào bài nộp, qua bộ kiểm tra chính thức `--validate` |
| Prompt SFT so với prompt suy luận | Khớp từng ký tự, 1545/1545 |
| Dữ liệu SFT đã gộp bước, phát lại | 100,0 |
| Ranh giới token khi tách đoạn | 300/300 giống hệt |

### 6.3 Tập dev và dữ liệu SFT

- **Tập dev:**
  - `splits/dev_random.txt`: 233 mẫu (hỏi thiếu 33 · thực thi 183 · ngoài phạm vi 17), chia ngẫu nhiên 15% theo loại.
  - `splits/dev_lao.txt`: 262 mẫu (41 · 214 · 7), là mọi mẫu dùng 6 app được giữ riêng: library, robot_vacuum, loyalty, medication, video_meeting, home_security.
  - Khi train cho bản leave-apps-out phải bỏ các app này khỏi `installed_apps`.
  - Từng có lỗi: lúc chia tập chưa tính `tool_name` của `ask_missing_info`, làm lộ tên app bị giữ riêng. Đã sửa, dev_lao tăng từ 256 lên 262 mẫu.
- **Định dạng SFT:** mỗi dòng là `{"id", "src", "aug", "segments": [[text, loss], ...]}`.
- **Gộp bước:** các call độc lập được gom vào cùng một bước. Sang bước mới khi call dùng giá trị vừa trả về trong bước hiện tại, hoặc khi lệnh ghi đứng sau lệnh đọc. Trung bình còn 1,74 bước so với 2,29 call.
- **Câu trả lời cuối** là một câu ngắn cố định: "Đã xong." khi đã gọi tool, "Không cần gọi tool." khi không gọi. Chuỗi dừng ngay sau `ask_missing_info`.
- **Tăng cường:**
  - Đổi tên app/tool nhất quán (2 biến thể mỗi mẫu).
  - Gỡ mọi app cùng nhóm với app yêu cầu cần → đích thành `[]` (xác suất 0,3).
  - Thêm 1–3 app gây nhiễu thuộc nhóm khác, lấy cả từ catalog public (xác suất 0,5).
  - Transcript kiểu ASR: viết thường, bỏ dấu câu (xác suất 0,3).
- **Nguồn lượt history** tắt mặc định (xem phát hiện 9). Có tuỳ chọn `--history tagged` để thử nghiệm.
- **Số liệu các file** (trong `lifemate/sft/`, không commit, chạy lại lệnh để sinh):

  | File | Ví dụ | Ghi chú |
  |---|---|---|
  | `fit_random.jsonl` | 4150 | ~3,3K token/ví dụ, ~76 token tính loss, ~13,3M token/epoch |
  | `fit_lao.jsonl` | 4051 | |
  | `all.jsonl` | 4874 | dùng train bản nộp |
  | `fit_random_hist.jsonl` | 6988 | thử nghiệm thêm lượt history |
  | `dev_random.jsonl` | 233 | không tăng cường, dùng đo dev loss |

### 6.4 Train

- **Cách tiết kiệm VRAM:** chỉ tính logits tại vị trí có loss (riêng chỗ này tiết kiệm 2–4GB); gradient checkpointing; batch 1 kèm tích luỹ gradient 16; trọng số bf16, tham số LoRA fp32; `--load-4bit` để chạy QLoRA.
- **Mặc định:** LoRA r=32, alpha=64, dropout 0,05, 7 module chiếu; lr 2e-4, cosine, warmup 3%; độ dài tối đa 8192.
- **Số đo trên RTX 4070 Laptop với Qwen3-1.7B:**
  - 34,9M tham số train được (1,99%).
  - Khoảng **1.385 token/giây**, nên 1 epoch `fit_random` (260 bước tối ưu) mất khoảng **2,7 giờ**.
  - Đỉnh **5,4GB** VRAM với mẫu dài nhất.
  - Chạy thử 3 bước: loss 1,77 → 1,08, dev loss 1,00.
- **Zero-shot Qwen3-1.7B** (với khối `<think>\n\n</think>\n\n` ép sẵn): **10/100 trên 10 mẫu**, khoảng 2,6 giây mỗi mẫu. Model bịa số điện thoại, hỏi lại thay vì tự tra lịch, trả lời bằng câu chữ thay vì gọi tool. Không ép khối `<think>` thì model "suy nghĩ" tới giới hạn 512 token và bị cắt.
- **Môi trường:** `lifemate/.venv` (Python 3.12, torch 2.15.0+cu132, transformers 5.21.0, peft 0.21.2). Transformers 5 dùng `dtype=` thay cho `torch_dtype=`.

#### Lệnh chạy train qua đêm

```bash
cd ~/"Zalo AI Challenge/lifemate" && mkdir -p runs && { nohup systemd-inhibit --what=sleep:idle:handle-lid-switch --why="LifeMate training" bash scripts/train_local.sh > runs/overnight.log 2>&1 & } && sleep 5 && tail -f runs/overnight.log
```

- Bấm Ctrl+C chỉ thoát khỏi phần xem log; train vẫn chạy.
- Dừng train: `pkill -f "train_local.sh|lifemate\.(train|infer)"`.
- Tổng khoảng 3 giờ 15 phút: baseline khoảng 10 phút → train khoảng 2 giờ 40 phút → đánh giá khoảng 15–20 phút.

#### Kết quả train qua đêm (2026-10-29)

- **Thiết lập:**
  - Model Qwen3-1.7B, LoRA, 1 epoch trên `sft/fit_random.jsonl` (4.150 ví dụ, 13,3M token, trong đó 0,32M token tính loss).
  - Chấm trên `dev_random` (233 mẫu); chữ đầu vào là `audio_text`, chưa qua ASR.
  - Log đầy đủ ở `lifemate/runs/overnight.log`, chỉ có trên máy Anh.
- **Thời gian:** chạy từ 23:52 đến 02:40, không lỗi. Riêng phần train mất 2 giờ 26 phút cho 260 bước, khoảng 1.540 token/giây, đỉnh 5,63GB VRAM.

| | Zero-shot | Sau SFT |
|---|---|---|
| **Điểm** | 9,9 | **53,9** |
| F1 của lời gọi (bỏ qua hash) | 13,7 | 67,2 |
| Hash trạng thái đúng | 25,3% | 63,1% |
| ask_missing (33 mẫu) | 2,0 | 49,4 |
| execute (183 mẫu) | 9,5 | 51,0 |
| out_of_scope (17 mẫu) | 29,4 | 94,1 |
| Thời gian mỗi mẫu, trung bình / tối đa | 2,9 s / 15,3 s | 2,5 s / 7,3 s |

- **Loss:**
  - Loss train giảm từ 1,62 xuống 0,03.
  - Dev loss qua các bước 50, 100, 150, 200, 250, 260: 0,060 → 0,041 → 0,028 → 0,0245 → 0,0233 → 0,0234. Đã chững lại ở cuối.
- **Phân bố điểm sau SFT:** 113 mẫu đúng hoàn toàn, 20 mẫu đúng một phần, 100 mẫu 0 điểm.
- **Điểm bị mất (107,4 trên 233 mẫu):** execute mất 89,7; ask_missing mất 16,7; out_of_scope mất 1,0.
- **Nhóm lỗi trong execute (183 mẫu):**

  | Nhóm | Số mẫu | Điểm |
  |---|---|---|
  | Có lời gọi khớp đáp án nhưng hash sai: trạng thái cuối khác đáp án (sai tham số ghi, thiếu hoặc thừa lệnh ghi) | **51** | 0 |
  | Hash sai và không lời gọi nào khớp | 22 | 0 |
  | Hash đúng nhưng không lời gọi nào khớp | 11 | 0 |
  | Hash đúng, F1 một phần: lời gọi thừa hoặc thiếu không làm đổi trạng thái (ví dụ lệnh đọc) | 17 | một phần |

- **Nhóm lỗi trong ask_missing (33 mẫu):** 12 mẫu hash sai, 3 mẫu hash đúng nhưng không lời gọi nào khớp, 3 mẫu đúng một phần.
- **Nhận xét:**
  - **Không chọn checkpoint theo loss.** Dev loss rất thấp (0,023) mà điểm chỉ 54, nghĩa là lỗi dồn vào vài token quyết định: ID, ngày giờ, số phải tính. Phải chấm bằng bộ chấm.
  - **Chưa đo được khả năng xử lý app mới.** Checkpoint này đã thấy mọi app của dev_random khi train. Muốn đo phải train lại trên `fit_lao` rồi chấm `dev_lao`. Hiện `scripts/train_local.sh` cố định dùng `fit_random`, nên cần sửa script.
  - **Tốc độ đã đủ.** Trên RTX 4070 laptop với backend HF (chưa dùng vLLM), mẫu chậm nhất mất 7,3 giây, dưới xa giới hạn 30 giây.
- Claude mới chỉ đếm nhóm lỗi, chưa đọc từng mẫu, để đội tự phân loại nguyên nhân trước ([`HUMAN_TODO.md`](HUMAN_TODO.md) mục 7).
- **Đính chính 29/10** (xem mục 7, entry 12):
  - Dev loss 0,023 ở trên chỉ đo **100 mẫu đầu** của file dev, vì `--eval-n 100` lấy đầu một file sắp theo id. Loss trên toàn 233 mẫu là **0,0685**: 100 mẫu đầu 0,0234, 133 mẫu sau 0,1153. Nhận xét "loss rất thấp mà điểm chỉ 54" vì vậy so hai tập mẫu khác nhau.
  - Kết luận vẫn giữ: chọn checkpoint chủ yếu bằng điểm rollout. Nhưng vẫn theo dõi loss toàn dev để chẩn đoán.
  - Tốc độ mới đo phần agent trên RTX 4070, chưa có ASR, chưa trên A30, chưa dùng vLLM.

---

## 7. Nhật ký theo thời gian

### 2026-10-28 — Phiên 1 (Anh + Claude)

1. **Phân tích đề.** Đọc README, mã `zaic_tools`, thống kê train và public. Phát hiện 11 app chỉ có ở public; history ở test chỉ có audio; tập trung vào state hash và quy ước của call đọc (mục 2–3).
2. **Bàn kiến trúc.** Chọn nối tầng ASR → Qwen3-4B SFT kèm lớp kiểm soát; lộ trình 19 ngày. Phát hiện máy local 8GB không đủ để SFT model 4B.
3. **Chốt tài nguyên.** Ngân sách không giới hạn, GPU cloud tuỳ ý, đội 2 người. BTC cho phép những gì không bị cấm. Dựng phần nền: bộ chấm, prompt, agent, infer, chia tập dev, script baseline cho cloud.
4. **Bộ sinh dữ liệu SFT.** Phát hiện lượt history theo quy ước khác đáp án nên tắt nguồn này mặc định. Thêm gộp bước, tăng cường, các kiểm chứng; sửa lỗi lộ app khi chia tập.
5. **Repo và script train.** Clone repo vào `~/Zalo AI Challenge`, nhánh `agent-pipeline`, commit `164b7a3`. Viết `train.py` tiết kiệm VRAM, backend HF, `train_local.sh`. Chạy thử train và zero-shot trên RTX 4070.
6. **Lệnh train qua đêm** cho Anh tự chạy.
7. **Tạo file nhật ký này.** Anh yêu cầu cập nhật liên tục và commit lên GitHub để leader theo dõi, đồng thời dùng làm context cho các đoạn chat sau.
8. **Câu hỏi về moat và tài liệu pipeline.**
   - **Anh hỏi:** nếu mọi đội đều có AI agent và tài nguyên như nhau thì khác biệt nằm ở đâu?
   - **Trả lời:** moat nằm ở việc hiểu chính sách sinh nhãn, có bộ dev mô phỏng private, phân vai giữa LLM và code tất định, dữ liệu tổng hợp đúng chính sách, ASR thiết kế theo slot, vòng lặp phân tích lỗi, và độ tin cậy của hệ thống.
   - **Nghiên cứu thêm:** đo nguồn gốc tham số của đáp án (phát hiện 12–14).
   - **Kết quả:** viết [`docs/PIPELINE.md`](docs/PIPELINE.md) gồm pipeline nền móng (sơ đồ, mã giả, đi qua mẫu `train_0001`, tính điểm từng kiểu lỗi), tự đánh giá, đề án nâng cấp 5 tầng và 20 câu hỏi.
   - **Quy tắc git mới:** tài liệu vào thẳng `main`, code qua PR. Đã mở [PR #1](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/1) `agent-pipeline` → `main` cho code.
9. **Câu hỏi về vai trò của con người** (ghi lại để các phiên sau hiểu tâm lý hiện tại của đội).
   - **Anh và leader băn khoăn:** khi đã có Claude Code với model tốt nhất, AI đọc nhiều paper và hiểu nhiều kỹ thuật cũng như giới hạn kỹ thuật, thì con người còn hơn AI ở đâu? Ngày xưa lợi thế nằm ở kỹ năng và kinh nghiệm fine-tune; giờ cuộc thi có thành "AI đấu AI" không? Bỏ qua thuyết trình, nộp bài, bỏ tiền, thì đóng góp riêng của người nằm ở đâu?
   - **Tâm lý hiện tại:** lo rằng lợi thế kỹ năng truyền thống đã bị san phẳng, và chưa rõ mình đóng góp gì ngoài việc chạy lệnh.
   - **Claude trả lời, tóm tắt:**
     - Không phải AI đấu AI. Khi mọi đội dùng cùng một model, năng lực thực thi bị san phẳng, nên khác biệt nằm ở **con người điều khiển AI**: hỏi gì, kiểm chứng gì, nhận ra điều gì, quyết định gì.
     - Lợi thế đã dịch chuyển: không còn ở chỗ biết nhiều kỹ thuật hơn, mà ở những việc AI không làm được hoặc làm kém.
     - Bằng chứng ngay trong phiên này:
       - Claude **không nghe được audio**. Dữ liệu gần 100% là giọng thật của 3 miền, và Claude chưa nghe file nào.
       - Claude **chỉ biết điều được đưa cho**: ý kiến của BTC, quy tắc repo, ngân sách đều do Anh mang tới.
       - Claude **sai một cách nghe rất hợp lý**: đã tự gây ra 4 lỗi trong phiên (bỏ trùng cả lệnh ghi, lộ app khi chia tập, app gây nhiễu không hiện schema, `dtype` của transformers 5), chỉ bắt được nhờ có kiểm chứng.
       - Kiến thức về model của Claude dừng ở giữa năm 2026.
       - Claude **không nhớ** qua các phiên; file này tồn tại vì lý do đó.
       - Claude **tối ưu đúng thứ được giao**: chính câu hỏi về moat của Anh đã đổi hướng công việc, từ "train thêm" sang "hiểu chính sách sinh nhãn".
   - **Phân vai đã thống nhất:**

     | Người (Anh, leader) | Claude |
     |---|---|
     | Đặt mục tiêu và ràng buộc; quyết định đặt cược khi thiếu dữ liệu; chịu trách nhiệm kết quả | Đề xuất phương án kèm bằng chứng và rủi ro |
     | Nghe audio, đánh giá lỗi ASR và phương ngữ theo cảm nhận của người bản ngữ | Viết công cụ để đo và gom lỗi |
     | Làm việc với BTC, theo dõi forum và các đội khác; xác nhận các chỗ luật chưa rõ | Liệt kê các chỗ chưa rõ cần hỏi |
     | Trả lời 20 câu hỏi trong `docs/PIPELINE.md` bằng phán đoán và thí nghiệm | Chạy thí nghiệm, phân tích dữ liệu |
     | Giữ chuẩn kiểm chứng ("số này đo ở đâu? sai thì thấy dấu hiệu gì?"); review PR | Viết test và kiểm chứng, báo cáo trung thực cả khi thất bại |
     | Giữ mạch ý đồ suốt 19 ngày; hiểu pipeline đủ sâu để bắt lỗi của Claude | Ghi nhật ký này sau mỗi phiên |
10. **Tạo [`HUMAN_TODO.md`](HUMAN_TODO.md).** Anh yêu cầu gom việc của người trong lúc chờ train thành danh sách checkbox, kèm 20 câu hỏi.
    - Việc được chia theo người phụ trách và theo giai đoạn: ngay bây giờ → hiểu bài và code → nghe audio → làm việc với BTC → chuẩn bị tài nguyên → tổ chức đội → sáng mai khi train xong.
    - Mọi lệnh trong file đã được chạy thử.
    - Đã chuẩn bị sẵn bài nộp rỗng cho public (`lifemate/runs/public_empty.jsonl`, qua bộ kiểm tra chính thức) để leader quyết định có dùng 1 lượt nộp đo tỉ lệ mẫu ngoài phạm vi hay không.
    - 20 câu hỏi được chép tự động từ `docs/PIPELINE.md`. Từ nay **câu trả lời ghi ở `HUMAN_TODO.md`**; `PIPELINE.md` chỉ để đọc.

### 2026-10-29 — Kết quả train qua đêm

11. **Train qua đêm chạy xong, không lỗi** (23:52 → 02:40). Anh dán log vào chat và hỏi đã xong chưa.
    - Đã xong: log có dòng cuối `done:`, process đã thoát, GPU đã trống. Lệnh `tail -f` vẫn giữ terminal; bấm Ctrl+C để thoát.
    - **Điểm dev_random: 9,9 (zero-shot) → 53,9 (sau SFT).** out_of_scope lên 94, ask_missing lên 49, execute lên 51. Bảng chi tiết ở [mục 6.4](#kết-quả-train-qua-đêm-2026-10-29).
    - Chỗ yếu nhất là execute: 51 mẫu có lời gọi đúng nhưng trạng thái cuối sai, nên bị 0 điểm.
    - Con số này chưa tính lỗi ASR và app mới, nên là mức trần lạc quan so với private test.

### 2026-10-29 — Audit, sửa đường đánh giá, chấm các checkpoint

12. **Anh gửi audit lượt train đầu, làm với Codex hỗ trợ** ([`docs/TRAIN_REVIEW_2026-10-29.md`](docs/TRAIN_REVIEW_2026-10-29.md)), kèm yêu cầu cho phiên này ([`docs/CLAUDE_HANDOFF_2026-10-29.md`](docs/CLAUDE_HANDOFF_2026-10-29.md)): đối chiếu, sửa đường đánh giá, chấm các checkpoint có sẵn và chốt thí nghiệm kế tiếp. Chưa thuê cloud, chưa nộp public, chưa train dài. Kết quả ở [`docs/EVAL_2026-10-29.md`](docs/EVAL_2026-10-29.md).
    - **Đối chiếu 21 nhận định của Codex:** 13 đồng ý, 6 đồng ý kèm bổ sung hoặc sửa, 2 chưa đủ bằng chứng. Phát hiện lớn nhất của Codex được xác nhận: dev loss trong log chỉ đo 100 mẫu đầu.
    - **Claude đo thêm:**
      - id train đi theo lô có đặc điểm khác nhau. Lô 1501+ có trung bình 7 lượt user trong history; lô 1–300 có 12 app cài và 3 call đáp án mỗi mẫu. Điểm dev giảm theo lô id và theo độ dài history.
      - Ranh giới hỏi lại (30 mẫu, 12,7 điểm) là nhóm hành vi mất điểm lớn nhất; ưu tiên "51 mẫu" hôm qua đã đánh giá thấp nhóm này.
      - `done=false` chỉ xuất hiện ở 7/233 rollout.
      - Ở `train_0098`, model đã thấy `done=false` rồi vẫn gửi SMS.
    - **Sửa đường đánh giá ([PR #2](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/2)):**
      - Dev loss tính trên toàn dev.
      - Mỗi file SFT có manifest; mỗi lượt chạy có meta (commit, sha256 của adapter, id, latency).
      - Không ghi đè kết quả cũ; trace lưu kết quả tool.
      - Thêm `eval_loss`, `compare` (so theo cặp kèm bootstrap và lát cắt), `eval_ckpt.sh`; `train_local.sh` chọn được `FIT`/`DEV` và chấm mọi checkpoint.
      - Ba file SFT cũ dựng lại giống từng byte.
    - **Kết quả trên đủ 233 mẫu:**
      - step_100: 38,95.
      - step_200: 52,47.
      - final: 53,92. Final hơn step_200 +1,45, khoảng tin cậy [−1,85; +4,78].
      - Chạy lại final cho kết quả giống hệt 233/233 mẫu.
      - Tập dò 233 mẫu lấy từ fit: 80,2.
    - **Quyết định đề xuất:**
      - Giữ final làm mốc.
      - Thí nghiệm B (fit_lao → dev_lao) tối nay, A (2 epoch) sau đó, thiết kế D (dữ liệu phản thực tế) song song.
      - Cân nhắc tách lockbox vì dev_random đã bị đọc kỹ từng mẫu.
    - `HUMAN_TODO.md`: điền câu trả lời làm việc cho 20 câu, mỗi câu có trạng thái (đã xác minh / giả thuyết / chưa đo / chờ BTC). Chỉ đánh dấu xong 3 việc có bằng chứng: lệnh train, xem file điểm, mở chat.
13. **Sự cố bộ nhớ lúc 08:26.** Anh báo máy hết bộ nhớ và tự tắt.
    - Kiểm tra cho thấy máy không khởi động lại. `systemd-oomd` kill cả nhóm tiến trình của app Claude, khi đó dùng 6,6GB, vì áp lực bộ nhớ toàn máy. Các lượt đánh giá đang chạy trong nhóm đó nên chết theo.
    - Không mất file nào: step_100 đã xong; các bước sau chưa kịp ghi file.
    - Đã chạy lại trong unit systemd riêng, giới hạn 5–6,5GB. Mỗi lượt đánh giá chỉ đạt đỉnh khoảng 1,25GB, train thử 1 bước đạt 2,9GB. Áp lực bộ nhớ đến từ tổng các ứng dụng đang mở (app Claude, ChatGPT, trình duyệt…), không chỉ từ đánh giá.
    - **Quy tắc mới:** việc dài (train, đánh giá) chạy bằng `systemd-run --user` có `MemoryHigh`/`MemoryMax`, để app và phiên làm việc không bị kill theo. Lệnh mẫu ở `docs/EVAL_2026-10-29.md` mục 5.3.
14. **Review của Codex và thí nghiệm B** (chiều 29/10).
    - **Review** ([`docs/REVIEW_CLAUDE_EVAL_2026-10-29.md`](docs/REVIEW_CLAUDE_EVAL_2026-10-29.md)):
      - Xác nhận lại mọi điểm checkpoint.
      - Chỉ ra lỗi bộ chấm: mẫu thiếu prediction mà gold rỗng vẫn được 1 điểm. Claude đã tái hiện; lỗi không làm sai số nào đã báo.
      - Bổ sung điều kiện cho lockbox; nhắc 225/262 mẫu `dev_lao` nằm trong `fit_random`; yêu cầu hạ mức khẳng định ở vài chỗ.
      - Claude đồng ý cả bốn ý (EVAL mục 7.1).
    - **Thí nghiệm B:** review khuyên chưa chạy vì Anh cần tắt máy, nhưng Anh chọn "Chạy B ngay" trong chat.
      - Claude chạy trong unit systemd riêng, **không** chặn chế độ ngủ khi gập máy, để laptop không nóng trong balo. Chạy 09:20 → 12:45, không lỗi.
      - Kết quả trên `dev_lao`: zero-shot 10,88 → step_100 33,02 → step_200 35,48 → final 35,53. Dev loss phẳng từ bước 100.
      - Trong cùng các mẫu, tỉ lệ tìm lại lời gọi đáp án: app giữ riêng 54,4%, app đã thấy 51,2%.
      - Hỏi lại về tool của app giữ riêng: 0 điểm trên 23 mẫu.
      - Thành phần mẫu (lô id, history) giải thích khoảng 2–11 trong 18,4 điểm chênh với `dev_random`. Đây là ước lượng thô, không phải nhân quả.
    - **Suy luận:** đòn bẩy rõ nhất cho app mới là chính sách hỏi lại với schema chưa thấy. Thí nghiệm A có giá trị thấp hơn dự kiến với protocol này.

### 2026-10-30 — Sửa lỗi bộ chấm

15. **Sửa lỗi bộ chấm khi thiếu prediction** (Anh chọn "Sửa ngay"; commit `d6208a1` trong [PR #2](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/2)).
    - Trước: `evaluate()` coi mẫu thiếu prediction như đã nộp danh sách call rỗng, nên mẫu ngoài phạm vi bị thiếu vẫn được 1 điểm.
    - Nay:
      - Mẫu thiếu prediction tính 0 và được đánh dấu `missing`.
      - Id trùng thì báo lỗi.
      - Id ngoài split, cả trong prediction lẫn trong `--ids`, thì báo lỗi để mẫu số không âm thầm thay đổi.
      - Kết quả có thêm số mẫu `missing` và `extra`.
    - **Kiểm chứng:**
      - 11 test đạt (7 test logic, 4 test qua dòng lệnh trên dữ liệu train thật).
      - Chấm lại 10 lượt chạy đã lưu ra đúng điểm cũ, cả tổng lẫn từng dòng theo mẫu.
      - Phát lại đáp án vẫn được 100; `check_sft.py` đạt.
    - **Ghi chú:** `gh pr edit` lỗi do API Projects classic của GitHub đã bị gỡ; mô tả PR cập nhật bằng `gh api -X PATCH repos/.../pulls/<n> -F body=@file`.
16. **Thiết kế thí nghiệm D** (Anh chọn "Thiết kế D"; sau đó quyết: Claude viết lại câu ngay trong phiên, làm luôn bộ sinh dữ liệu, chưa train). Chi tiết ở [`docs/EXPERIMENT_D.md`](docs/EXPERIMENT_D.md); code ở [PR #3](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/3).
    - **Chính sách hỏi lại trên fit_random:**
      - 184 lần hỏi lại, mỗi lần đúng 1 tham số, luôn là call cuối.
      - 73 lần đã thực hiện ý khác trước.
      - Kiểu A/B/C = 57/55/72.
    - **Model hiện tại:**
      - Kiểu A làm tốt (dev_random 8/8 có hỏi).
      - Bỏ hỏi B 7/11 và C 9/14 trên dev_random; B 17/21 và C 16/19 trên dev_lao.
      - Với C, model bịa giá trị cho đúng slot lẽ ra phải hỏi (21/25 lần).
    - **Luật tất định:**
      - "ID lấy từ lần tra ≥ 2 mục trùng tên thì hỏi lại": 0 lần báo nhầm trên fit.
      - Nhưng phát lại trên rollout chỉ kích hoạt 0–1 mẫu (+0 đến +0,25 điểm), nên loại khỏi hướng chính.
      - Kiểm tra nguồn gốc giá trị slot thường không làm tất định được.
    - **Bộ sinh dữ liệu** (`lifemate/counterfactual.py`):
      - Ba loại cặp: C, B-vague, B-specific.
      - Nhãn phát lại qua ToolEnv; câu phải qua 7 kiểm tra; loại nguồn từ dev.
      - `sft.py --extra-samples` nối mẫu D vào SFT. Không truyền thì bốn file SFT cũ dựng lại giống từng byte.
      - 12 test mới đạt.
    - **Chạy thử trên fit_lao:**
      - 49 task → Claude viết lại 27, bỏ qua 22 có lý do (6 giá trị phải tính, 5 lấy từ history…) → **23 mẫu qua mọi kiểm tra**.
      - 4 mẫu có nguồn trong dev_random bị loại, gồm `train_1409`; bước chọn nguồn nay loại sớm.
    - **Ước lượng bộ đầy đủ:** khoảng 230 mẫu, tương đương khoảng 700 dòng SFT.
    - **Đề xuất train:** 2 lượt giữ nguyên số bước (D-lao, D-random), tiêu chí ở EXPERIMENT_D mục 8. Chờ Anh duyệt.
    - **VieNeu** (TTS tiếng Việt Anh gợi ý): ghi cho leader ở Q18; ngoài phạm vi D vì D chỉ là văn bản. Cần kiểm licence và khả năng chạy offline.
17. **Review thí nghiệm D và đặt mốc đo** (Anh yêu cầu đánh giá lại, định lượng nhược điểm, được chạy thử tuỳ ý, rồi lập kế hoạch; bản này là mốc so sánh). Xem [`docs/REVIEW_D_2026-10-30.md`](docs/REVIEW_D_2026-10-30.md).
    - **Đo trên GPU, 23 cặp thử, cả hai checkpoint** (trong unit `systemd-run`; tiến trình dùng khoảng 1,2GB RAM, phần còn lại là page cache):
      - Câu thiếu thông tin: model hỏi lại 1/16 lần, 15 lần tự làm.
      - Mẫu hỏi lại kiểu B đã có trong train: model hỏi 0–1/7.
      - Cặp đúng cả hai vế: 1/23 và 0/23.
    - **Nhược điểm đã định lượng:**
      - Chỉ có 4 cặp tự nhiên để đối chiếu nhãn (3 cặp khớp).
      - 34–36% nhãn là ngoại suy.
      - Chuỗi lệnh đọc khớp nhãn thật 70–78%.
      - Kiểm tra câu bắt được 6/22 câu rò rỉ.
      - Người viết phải bỏ 45% task.
      - 3 tool đứng đầu chiếm 56–66% nguồn; B-specific chỉ có 5–8 nguồn.
      - 15/21 lần bỏ hỏi với app giữ riêng không được phủ.
      - Chưa có đối chứng cho D.
    - **Đã sửa** (PR #3, commit `8799da5`):
      - `vinum.py` nhận ra số và giờ viết bằng chữ, viết tắt: bắt rò rỉ lên 15/22, vẫn 0/27 loại nhầm.
      - Bộ lọc nguồn: bắt trước 17/22 task người viết bỏ, loại nhầm 3/27, đo trên chính lần thử.
      - Giới hạn số mẫu mỗi tool: tỉ trọng 3 tool đứng đầu còn khoảng 30%.
      - Cờ tiền lệ; tách D-train / D-eval.
      - `contrast_eval.py`, `d_quality.py`.
      - 16 test bộ sinh dữ liệu đạt.
    - **Kế hoạch:**
      - Giai đoạn 1: D v1 sạch (đọc theo nghĩa, người đọc tay, tách D-eval).
      - Giai đoạn 2: ba lượt B0 / B-up (đối chứng) / B-D với số bước giữ nguyên; giữ D chỉ khi thắng cả B0 lẫn B-up.
      - Giai đoạn 3: mở rộng.
      - Giai đoạn 4: đưa vào công thức train cuối.
    - **Đính chính:** trong chat, số cặp tự nhiên là 4 cặp, 3 cặp khớp (không phải 5 và 4).
18. **Giai đoạn 1 của D: D v1** (Anh duyệt "Duyệt giai đoạn 1"; chưa train). Chi tiết ở [`docs/D_PHASE1_2026-10-30.md`](docs/D_PHASE1_2026-10-30.md); số liệu ở [`docs/baselines/d_phase1_2026-10-30.json`](docs/baselines/d_phase1_2026-10-30.json).
    - **Thêm lượt đọc theo nghĩa (R7):** người đọc chỉ thấy câu mới và danh sách mục (PR #3, commit `701dcb4`; 17/17 test đạt).
    - **Pipeline:**
      - 130 task (giới hạn 8 mẫu mỗi tool; loại nguồn từ dev và 49 nguồn của đợt thử).
      - Claude viết lại 83, bỏ qua 47 có lý do.
      - 0 lỗi kiểm tra chữ; **6 câu bị lượt đọc theo nghĩa loại** (có 1 câu đổi nhầm đối tượng).
      - **77 mẫu giữ lại**, phát lại qua ToolEnv đều thành công.
      - D-train 53 / D-eval 24 (tách theo mẫu gốc, không trùng dev hay mẫu thử).
    - **Chất lượng nguồn:**
      - 3 tool đứng đầu chiếm 27% (mốc 56–66%).
      - 29 tool đích.
      - 68% nhãn có tiền lệ.
    - **Đo trên GPU, D-eval-24:**
      - Cả hai checkpoint hỏi lại **0/24** câu thiếu thông tin; làm đúng 15–17/24 câu gốc; 0/24 cặp đúng cả hai vế.
      - Cộng mốc đợt thử: 1/40.
    - **Cổng:** chống rò rỉ đạt; tỉ lệ bỏ qua ≤ 15% **không đạt** (36%); người đọc tay đang chờ.
    - **Giới hạn mới:** với luật chặt, nguồn từ fit chỉ đủ khoảng 140–150 mẫu D. D-train 53 mẫu (khoảng 4% số dòng) có thể quá ít để giai đoạn 2 thấy được hiệu ứng.
    - **Đề xuất:**
      - Giai đoạn 1b: bộ lọc v2 cho khoảng 30/47 lý do bỏ qua tự động hoá được; nâng giới hạn lên 16 mẫu mỗi tool; D-train khoảng 80–90 mẫu.
      - Giai đoạn 2 thêm nhánh liều lượng: B-up, B-D1, B-D3.
19. **Giai đoạn 1b của D: bộ lọc nguồn v2, D-train 77 mẫu** (Anh chọn "Làm giai đoạn 1b"; chưa train). Chi tiết ở [`docs/D_PHASE1B_2026-10-30.md`](docs/D_PHASE1B_2026-10-30.md); số liệu ở [`docs/baselines/d_phase1b_2026-10-30.json`](docs/baselines/d_phase1b_2026-10-30.json).
    - **Code** (PR #3, commit `b317660`; 22/22 test đạt):
      - `filter_v2_reason` gồm 15 luật cho các lý do bỏ qua tự động hoá được.
      - Lọc câu trùng khuôn (ngưỡng 0,75).
      - `build` chặn rò rỉ nhãn (câu mới đã bỏ từ mà nhãn vẫn dùng).
      - `d_quality.py` thêm D-M6v2, D-M10/11 trên mẫu giữ lại, và D-M14 (phản tiền lệ, thô).
      - Không truyền cờ mới thì task v1 tái lập giống từng byte.
    - **Bộ lọc v2, đo trên 130 quyết định v1 (in-sample):** bắt 37/53 nguồn xấu, loại nhầm 6/77. Bản đầu dựa trên chữ "thì/nếu" loại nhầm 17 câu tốt nên đã thu hẹp.
    - **Đợt 1b:**
      - 33 task trên 4 tool.
      - Người viết bỏ **9/33 (27%)**: C 0/16, B-vague 9/17. **Cổng ≤ 15% vẫn không đạt**; con số in-sample (khoảng 12%) là quá lạc quan.
      - R7 loại 0/24; 24 mẫu giữ lại, phát lại qua ToolEnv đều thành công, tất cả có tiền lệ hỏi thật.
    - **Lỗi phát hiện:**
      - **Rò rỉ nhãn trong v1** ở `train_1140`: câu mới đã bỏ "xăng" nhưng nhãn vẫn có `news.search(query="giá xăng")`. Mẫu này nằm trong D-eval-24; giữ nguyên tập để so với mốc, và báo thêm kết quả trên D-eval-23.
      - **Chính sách tài khoản nguồn:** khi lời nói không nêu tài khoản, fit luôn chọn mặc định (7 lần thực hiện, 0 lần hỏi). 2 task "hỏi tài khoản nào" bị bỏ trước khi vào dữ liệu.
    - **D-train 1b = 77 mẫu**, 242 dòng SFT (6,0% số dòng gold). **Dưới mục tiêu 80–90.**
      - Tỉ trọng 3 tool đầu tăng 32% → 47%; số tool vẫn là 25.
      - Phần 1b phủ thêm 0 lần bỏ hỏi trên dev_lao (v1 phủ 4/12 lần ở tool đã thấy).
    - **Model hiện tại trên 24 mẫu 1b:** hỏi đúng 0/24 (fit_lao) và 1/24 (fit_random). Hai lượt chạy bằng `systemd-run`, mỗi lượt khoảng 2,5 phút. systemd đã thay `${t}` bằng chuỗi rỗng nên file của lượt fit_lao bị ghi sai tên; mình đã đổi tên lại.
    - **Nguồn gần cạn:** theo luật hiện tại chỉ còn 27 nguồn sạch, 16 là `reminders.create`.
    - **Đề xuất:**
      - Giai đoạn 2 ngay với D-train 77 mẫu (B-up / B-D1 / B-D3, 254 bước); phép so quan trọng nhất là B-D với B-up.
      - Phương án thay thế: giai đoạn 3 (nới luật) trước.
      - Việc đọc tay `review_v1_30.md` và `review_1b.md` vẫn mở.
20. **Giai đoạn 2 của D: bắt đầu train** (Anh chọn "Train giai đoạn 2", 30/10 18:17). Đang chạy; kết quả sẽ ghi vào báo cáo riêng.
    - **Code** (PR #3, commit `8209095`):
      - `train_local.sh` nhận `EXTRA_SAMPLES` và dựng file train riêng `sft/fit_lao_<TAG>.jsonl`, không đụng vào file của B0.
      - `scripts/phase2_d.sh` chạy cả giai đoạn; chạy lại thì bỏ qua bước đã xong.
    - **Ba lượt mới**, tất cả train lại từ Qwen3-1.7B gốc trên fit_lao, với đúng thiết lập của B0 (`q17b_fit_lao`):
      - Cùng 254 bước (`--max-steps 254`), seed 0, LoRA r32, lr 2e-4, grad_accum 16.
      - Chỉ đánh giá checkpoint final.

      | Lượt | Dữ liệu thêm | Số dòng thêm |
      |---|---|---:|
      | `q17b_lao_d3` | D-train 1b lặp 3 lần | 734 |
      | `q17b_lao_up` (đối chứng) | 232 bản sao mẫu hỏi lại thật kiểu B/C của fit_lao (112 mẫu gốc: 67 C, 45 B) | 734 |
      | `q17b_lao_d1` | D-train 1b | 242 |

    - **Đã kiểm trước khi chạy:**
      - Phần gold của cả 3 file SFT giống B0 từng byte (4.051 dòng).
      - B-D3 và B-up có cùng tổng số dòng (4.785). Với seed 0, hai lượt này thấy đúng cùng một tập dòng gold, chỉ khác phần dòng thêm.
      - Vì giữ 254 bước, mỗi lượt chỉ đi qua 4.064 dòng đầu của lượt xáo trộn: khoảng 85% dữ liệu với D3 và B-up, khoảng 95% với D1. B0 thấy toàn bộ.
    - **Chạy bằng** `systemd-run` (unit `lifemate-phase2-d`, MemoryHigh 6G / MemoryMax 8G); có chặn idle-sleep, không ghi đè hành vi gập nắp. Log ở `lifemate/runs/phase2_d.log`.
    - **Đo được:** khoảng 150 phút train mỗi lượt (như B0), đỉnh VRAM 5,62GB.
    - **Chấm mỗi lượt:** dev_lao (so theo cặp với B0), D-eval-24 và CS-pilot-23.
    - **Ghi chú vận hành:** trong lúc train, không đổi nhánh trong thư mục repo. `main` không có code `lifemate/`, nên đổi nhánh sẽ xoá script đang chạy. Tài liệu trên `main` được sửa qua một git worktree riêng.
21. **Ưu tiên baseline đầu-cuối; sự cố `lifemate/gen/` trên repo public** (30/10, 20:10–20:45).
    - **Anh trả lời "Baseline đã xong chưa?":**
      - Phần agent (đọc chữ chuẩn) đã xong.
      - Đầu-cuối (audio → ASR → agent → Docker) thì chưa.
    - **Anh chọn:**
      - "Ưu tiên đầu-cuối" sau giai đoạn 2.
      - "Claude làm ASR baseline với 2 model".
      - "Gỡ `gen/` khỏi `main`".
    - **Sự cố `gen/`:**
      - Lúc 20:03, commit `1bbd05a` ("update") đưa 29 file `lifemate/gen/` (3,4 MB: lời nói, nhãn, kết quả tool chép từ train) lên `main`. Lý do: `.gitignore` của `main` khi đó chưa có `gen/`. Repo đang **public**, trong khi README dữ liệu cấm phát tán.
      - Có vẻ thư mục repo chính đã được đổi sang `main` để commit rồi đổi lại `exp-d`. Khi đổi lại, git **xoá các file `gen/` trên máy**, đúng lúc giai đoạn 2 sắp cần chúng: CS-pilot-23, D-eval-24, dữ liệu thêm của B-up và B-D1.
      - **Đã xử lý:**
        - Khôi phục cả 29 file từ `1bbd05a`. Hash của `d_train_1b_x3.jsonl` khớp manifest SFT của lượt D3; `tasks_v1.jsonl` vẫn là `67f48ca1…`.
        - Gỡ `gen/` khỏi `main` (`4e908be`) và thêm `gen/` vào `.gitignore` của `main`.
        - Đồng bộ sang `agent-pipeline`, `eval-protocol`, `exp-d`. Giai đoạn 2 không bị gián đoạn.
      - **Còn lại:** bản cũ vẫn xem được trong lịch sử git. Chuyển repo sang private, hoặc viết lại lịch sử, là việc Anh quyết. Muốn chia sẻ file `gen/` cho leader thì gửi riêng, không qua repo.
      - **Anh quyết giữ repo public** (30/10, trong chat). Lịch sử không bị viết lại; `1bbd05a` vẫn còn. Từ nay `gen/`, `asr/`, `runs/`, `sft/`, `ckpt/`, `data/` đều được bỏ qua trên mọi nhánh.
    - **Code baseline đầu-cuối** ([PR #4](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/4), nhánh `e2e-baseline` xếp chồng lên PR #3, commit `236bca1`). Chỉ thêm file mới; `infer.py`, `agent.py`, `prompt.py` giữ nguyên vì giai đoạn 2 đang chạy từ thư mục này.
      - `lifemate/asr.py`: ASR có sẵn cho mọi wav của một split (lượt cuối và lượt user trong history). Giải mã greedy, tiếng Việt, ghi đúng giao kèo mà `infer.py --text asr` đọc; không bao giờ đọc `<split>_environment/`.
      - `scripts/asr_quality.py`: WER (có và không dấu) cho lượt cuối và history. Đo riêng những gì làm đổi hash: số, tiền, giờ của lệnh ghi còn được nói ra không (chữ số và chữ đều tính), từ phủ định, query tìm kiếm.
      - `scripts/check_submission.py`: kiểm cấu trúc, id và `zaic_tools --validate` của BTC; tính thời gian ASR + agent mỗi mẫu.
      - `scripts/predict.sh`: một lệnh offline (`HF_HUB_OFFLINE=1`) từ thư mục dữ liệu ra `submission.jsonl` đã kiểm. Đây là lõi để đóng Docker.
      - `scripts/e2e_baseline.sh`: lượt đo đêm nay. Không train.
      - Test: `test_asr` 8/8, `test_scorer` 11/11, `test_counterfactual` 22/22.
    - **Model ASR** (đã tải về cache, ghim revision; cả hai phát hành trước 26/10/2026):

      | Model | Tham số | Licence | Revision |
      |---|---|---|---|
      | `openai/whisper-large-v3-turbo` | 0,8B | MIT | `41f01f3f` |
      | `vinai/PhoWhisper-large` | 1,55B | BSD-3 | `b9136a44` |

    - **Thử nhanh trên CPU, 3 câu dev, Whisper-turbo bf16:** chạy được, nhưng nghe kém. Ví dụ "huỷ lịch" → "bị dịch", "nạp giúp" → "nặng chúc". Chưa kết luận được: chỉ 3 câu, và bf16 trên CPU có thể làm kém đi.
    - **Đã đo:** `audio_text` của train viết số bằng chữ nhiều hơn chữ số (1.371 so với 481 trên 5.036 câu), trong khi Whisper hay xuất chữ số. Model agent học theo kiểu của `audio_text`, nên đây là một nguồn lệch cần đo.
    - **Lượt đo đã xếp lịch** (unit `lifemate-e2e-baseline`, MemoryHigh 7G / MemoryMax 9G, chặn idle-sleep). Unit chờ `lifemate-phase2-d` xong rồi chạy `e2e_baseline.sh`, log ở `lifemate/runs/e2e_baseline.log`:
      1. ASR 2 model trên wav của dev_random (784) và dev_lao (1.117), rồi đo chất lượng ASR.
      2. Agent đọc chữ ASR: `q17b_fit_random/final` trên dev_random, B0 trên dev_lao. So theo cặp với run chữ chuẩn đã có (53,92 và 35,53).
      3. Chọn model ASR theo luật đặt trước: điểm gộp dev_random + dev_lao cao hơn; cách nhau dưới 1 điểm thì chọn turbo.
      4. public_test qua `predict.sh` (ASR batch 1 để đo độ trễ), được `runs/e2e_public_<asr>.jsonl` đã kiểm.
      5. Chạy lại ASR trên 50 wav để kiểm tái lập.
    - Dự kiến khoảng 2–2,5 giờ GPU, có số liệu khoảng 6 giờ sáng 31/10. Báo cáo sẽ ở `docs/E2E_BASELINE_2026-10-31.md`.
    - **Ngoài phạm vi, cần Anh quyết riêng:**
      - Nộp public: Anh tự nộp.
      - Train thêm.
      - Thuê cloud (4B, A30, vLLM).
      - Cài Docker trên máy này.
      - Fine-tune ASR và chuẩn hoá số (phần của leader).
22. **Prompt deep research cho Codex** (30/10, 21:00).
    - Anh muốn dùng Codex, trong lúc máy chạy, để nghiên cứu rộng các paper, kỹ thuật và repo liên quan, rồi đối chiếu với những gì đội đã, đang và định làm.
    - Claude viết prompt: [`docs/CODEX_RESEARCH_PROMPT_2026-10-30.md`](docs/CODEX_RESEARCH_PROMPT_2026-10-30.md). Nội dung gồm:
      - luật an toàn trên máy đang chạy job: không đụng git, GPU, `runs/`; không đưa dữ liệu thi ra ngoài;
      - bối cảnh và số liệu; danh sách file phải đọc;
      - 12 trục nghiên cứu A–L, gắn với Q1–Q20;
      - tiêu chuẩn trích dẫn; bộ lọc tuân thủ luật thi; khung chấm đề xuất;
      - 7 điểm phản biện bắt buộc về các lựa chọn hiện tại.
    - **Đầu ra dự kiến:** `docs/research/CODEX_DEEP_RESEARCH_2026-10-31.md` và `docs/research/codex_sources_2026-10-31.csv`. Codex chỉ ghi file, không commit; đội đọc rồi mới đưa lên `main`.
23. **Sự cố đổi nhánh lần 2; job chuyển sang worktree riêng** (30/10, 20:56–21:18).
    - Lúc 20:56:43, thư mục repo chính bị chuyển từ `e2e-baseline` sang `main` (reflog: `checkout: moving from e2e-baseline to main`). Không rõ người làm; Codex desktop đang chạy trên máy từ 20:38.
    - **Hậu quả:**
      - `main` không có code `lifemate/`. Lúc 20:58:53 bước chấm lượt D3 báo `No module named lifemate.infer`, và unit giai đoạn 2 dừng.
      - Unit đo đầu-cuối thấy giai đoạn 2 dừng nên tự khởi động, rồi hỏng vì không có script.
      - Train D3 đã xong và checkpoint `final` đã lưu trước đó, nên không mất gì.
      - `gen/` lần này không bị xoá, vì `main` đã bỏ qua `gen/` (entry 21).
    - **Xử lý:** từ 21:01, mọi job dài chạy từ worktree riêng **`~/zac-jobs`** (detached, ở commit `e19fb0e` của `e2e-baseline`).
      - `data`, `lifemate/{.venv,ckpt,runs,sft,gen,asr}` là symlink về thư mục chính, nên kết quả vẫn ghi đúng chỗ cũ.
      - Đổi nhánh trong thư mục chính không còn làm hỏng job.
      - Unit `lifemate-night` (script `~/zac-jobs/run_night.sh`) chạy lần lượt: chấm D3 → B-up → B-D1 → đo đầu-cuối. Dự kiến xong khoảng 5 giờ sáng 31/10.
    - **D3 đã có số** (chưa kết luận khi chưa có đối chứng; báo cáo đầy đủ sẽ có trong `docs/D_PHASE2_*.md`):
      - dev_lao 31,23 so với 35,53 của B0 (−4,30; khoảng tin cậy 95% từ −9,18 tới +0,55).
      - Hỏi lại 20,24 so với 7,48; hỏi đúng ở app chưa thấy 8/23 so với 0/23.
      - Nhưng hỏi thừa ở mẫu execute tăng từ 15 lên 34.
24. **Báo cáo deep research của Codex** (30/10, 21:23; Anh đồng ý đưa lên `main`): [`docs/research/CODEX_DEEP_RESEARCH_2026-10-31.md`](docs/research/CODEX_DEEP_RESEARCH_2026-10-31.md), kèm [bảng 81 nguồn](docs/research/codex_sources_2026-10-31.csv).
    - **Claude đã kiểm:**
      - **Không có dữ liệu thi:** dò mọi đoạn 6 từ liên tiếp của 5.036 câu `audio_text` trong train, 0 câu trùng.
      - **6 paper ACL 2025–2026:** When2Call, Learning to Ask, Ask-Answer-or-Act, Calibration is the Bottleneck, ToolWeave, State-Path Menu. Tiêu đề đều khớp.
      - **9 model trên Hugging Face:** ngày, licence, số tham số khớp. Riêng Gemma-4-E2B có repo từ 02/03/2026, không phải 02/04; vẫn trước mốc.
      - **NeMo `r1.2.0`** (05/06/2026): có ITN tiếng Việt.
      - **Qwen3-ASR-0.6B:** có tiếng Việt, cần package `qwen-asr`.
      - **`agent.py:150`** đúng là chỉ xem đồng hồ ở đầu mỗi bước, nên bước cuối có thể vượt 30 giây.
    - **Thông tin mới quan trọng:**
      - Qwen3-ASR-0.6B (thực tế 938M tham số; với Qwen3-4B tổng 4,96B).
      - NeMo ITN tiếng Việt.
      - Gipformer 68M và BuzzASR (số tự báo).
      - Bẫy đếm tham số: Qwen3.5-4B thực tế 4,66B; Qwen3-ASR-1.7B cộng Qwen3-4B vượt 6B.
      - Hướng "calibration theo kiểu hành vi" (hỏi / làm / bỏ qua) cho ranh giới hỏi lại.
    - **Claude đồng ý:**
      - P0: chặn lệnh ghi dùng ID chưa từng xuất hiện trong kết quả tool hay history (rẻ, không train).
      - P0: thêm Qwen3-ASR-0.6B vào so sánh ASR; thử NeMo ITN.
      - P0: Qwen3-4B; Docker/A30 tái lập 5 lần.
      - P1: dữ liệu tổng hợp quy mô nhỏ.
      - P2: RL, audio-LLM end-to-end.
    - **Claude xếp khác:**
      - Ép định dạng JSON lúc sinh xuống thấp hơn, vì chỉ 5/233 trace có lỗi định dạng.
      - Đề xuất thêm: chỉnh ngưỡng xác suất chọn `ask_missing_info` lúc suy luận, để giữ phần lợi của D mà bớt hỏi thừa. Ngưỡng chỉnh trên tập dò từ fit, không chỉnh trên dev.
    - **Đã cũ trong báo cáo:** "hai job chưa có điểm do lỗi đường chạy" (Codex đọc trước khi chạy lại). Các đề xuất sẽ được gộp vào kế hoạch khi có báo cáo giai đoạn 2 và báo cáo đầu-cuối.
25. **Bổ sung: việc tối 30/10 cho Anh và leader** (30/10, 20:40; ghi muộn, phát hiện khi rà ở entry 26).
    - Anh hỏi: trong lúc chờ máy chạy, Anh và leader làm gì, trong file nào, trên máy leader.
    - Claude viết mục 0 của [`HUMAN_TODO.md`](HUMAN_TODO.md) (commit `8d9026b`). Lượt này khi đó chỉ ghi vào HUMAN_TODO, chưa có entry ở đây.
      - **Máy Anh chỉ đọc file:** không đổi nhánh, không commit trong thư mục repo, không mở ứng dụng nặng.
      - **Ghi kết quả:** câu trả lời vào `HUMAN_TODO.md` trên `main`; góp ý code bằng comment trên PR #4. Không commit `data/`, `gen/`, `asr/`, `runs/`.
    - **Các việc**, xếp theo mức có ích cho các quyết định sáng 31/10 (chọn ASR, nộp public, Docker):
      - 0.1 [Leader] dựng môi trường từ nhánh `e2e-baseline` và chạy test. Đây cũng là lần tập dượt cho Docker.
      - 0.2 [Cả hai] nghe audio train, gồm 3 câu Whisper-turbo nghe sai. Câu cần trả lời: `audio_text` là kịch bản người nói đọc theo, hay transcript thật? Nếu người nói đọc lệch kịch bản, WER sẽ phạt oan ASR.
      - 0.3 [Leader] danh sách cụm từ nguy hiểm cho ASR, đối chiếu với danh sách từ phủ định trong `asr_quality.py`.
      - 0.4 [Leader] rà model ASR và LLM mới.
      - 0.5 [Leader] forum và câu hỏi cho BTC về Docker.
      - 0.6 [Leader] review PR #4: định dạng file ASR và biến môi trường của `predict.sh`.
      - 0.7 [Cả hai] chuẩn bị quyết định nộp public.
      - 0.8 [Leader, tuỳ chọn] chạy turbo trên các câu vừa nghe. Chỉ chạy trên train.
      - 0.9 [Anh] Codex deep research. Đã xong (entry 24).
26. **Anh hỏi: journal có tự cập nhật các lượt vừa rồi chưa, và đang chờ gì** (30/10, 23:05).
    - **Cách Claude ghi journal:**
      - Sau mỗi lượt có nội dung, Claude thêm entry ở mục 7, sửa mục 0 và mục 8, commit thẳng lên `main`, rồi đồng bộ sang các nhánh code.
      - Nội dung ghi: câu hỏi và lựa chọn của Anh, những gì đã kiểm, kết luận và lý do, kể cả chỗ Claude không đồng ý (ví dụ entry 24). Không chép nguyên văn suy nghĩ nội bộ.
    - **Kiểm lại lúc này:**
      - Các lượt tới "Đưa lên main" đã có ở entry 21–24.
      - Thiếu lượt "việc tối nay": nay bổ sung ở entry 25.
      - Mục 8 thêm các việc rút từ báo cáo Codex.
    - **Máy lúc 23:05:**
      - B-up ở bước 175/254, loss khoảng 0,03–0,05.
      - Đỉnh VRAM 5,78 GB; RAM còn khoảng 5 GB.
    - **Đang chờ** (giờ 31/10 là ước tính):

      | Khoảng giờ | Mốc | Claude làm ngay sau |
      |---|---|---|
      | 0:15 | B-up (đối chứng) có điểm | So D3 với B-up. Hai lượt thấy cùng các dòng gold, cùng số dòng thêm; chỉ khác dòng thêm là D hay mẫu hỏi lại thật nhân bản. Đây là phép thử chính của D. Tiêu chí đặt trước: B-D phải hơn B0 ≥ 10 điểm hỏi lại (D3 đã đạt: 20,24 so với 7,48) **và** hơn B-up ≥ 5 điểm. |
      | 3:00 | B-D1 có điểm, giai đoạn 2 xong | Chạy `phase2_report.py`. Viết `docs/D_PHASE2_2026-10-31.md` và kết luận theo tiêu chí. |
      | 5:00–5:30 | Đo đầu-cuối xong | Viết `docs/E2E_BASELINE_2026-10-31.md`: điểm mất do ASR, model ASR được chọn, file public đã kiểm, thời gian mỗi mẫu. Anh quyết có nộp không. |

    - **Trong lúc chờ:** GPU bận tới sáng, nên chỉ làm được việc chạy trên CPU. Ví dụ: đo trên trace có sẵn xem chốt chặn ID (entry 24) cứu được bao nhiêu mẫu, trước khi viết code.
27. **Đo chốt chặn ID trên CPU** (30/10, 23:10–23:20; Anh chọn "Làm luôn"). Chi tiết ở [`docs/ID_GUARD_2026-10-30.md`](docs/ID_GUARD_2026-10-30.md); số liệu ở [`docs/baselines/id_guard_2026-10-30.json`](docs/baselines/id_guard_2026-10-30.json); script ở [PR #5](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/5), chỉ phân tích, không đổi agent.
    - **Quy tắc:** chặn lệnh ghi khi một tham số có `x-ref` trong schema mang ID chưa từng xuất hiện trong prompt, history hay kết quả tool trước đó.
      - Quy tắc dựa trên catalog, nên áp dụng được cho app chưa thấy.
      - Chạy lại các call của 4 lượt có sẵn trên ToolEnv: khớp file nộp 100%.
    - **Kết quả:**
      - Chặn nhầm 1/912 giá trị của đáp án fit. Ca đó là do dữ liệu lệch.
      - dev_random chặn 0 call, điểm không đổi. dev_lao chặn 4 call (B0) và 7 call (D3), tất cả đều sai.
      - Điểm chỉ đổi ở D3: +0,19 tới +0,26, nhờ 1 mẫu.
    - **Lỗi ID thật là chọn nhầm một ID đã thấy** (7–9% mẫu), ví dụ chuyển tiền từ nhầm tài khoản. Chốt chặn không bắt được loại này.
    - **Lệnh ghi sai nhiều nhất** là ở tham số không phải ID (giờ, số tiền, nội dung: 24 / 54 / 41 call), rồi tới ghi sai tool và ghi thay vì hỏi lại.
    - **Quyết định đề xuất:** hạ chốt chặn ID từ P0 xuống lưới an toàn. Viết khoảng 20 dòng cùng lúc với phần sửa thời gian ở `agent.py` trước Docker; không cần lượt GPU riêng.
    - **Việc CPU tiếp theo đáng làm:** tách nhóm "sai tham số khác" theo loại (ngày giờ, số tiền, chữ tự do, enum).
28. **Lệnh ghi sai vì sao, mỗi nguyên nhân đáng bao nhiêu điểm** (30/10, 23:20–23:35; Anh chọn "Làm luôn"). Chi tiết ở [`docs/PARAM_ERRORS_2026-10-30.md`](docs/PARAM_ERRORS_2026-10-30.md); số liệu ở [`docs/baselines/param_errors_2026-10-30.json`](docs/baselines/param_errors_2026-10-30.json); script `param_errors.py` thêm vào [PR #5](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/5).
    - **Cách đo:**
      - Ghép mỗi lệnh ghi sai với lệnh cùng tool gần nhất trong đáp án, rồi phân loại tham số lệch theo kiểu trong schema.
      - Đếm riêng lệnh ghi sai tool và lệnh ghi bị thiếu.
      - Sửa giả định từng nguyên nhân theo đáp án, chạy lại trên ToolEnv rồi chấm, để có trần điểm của nguyên nhân đó.
      - Chỉ CPU, 14 giây, chạy lại khớp file nộp 100%.
    - **Đính chính entry 27:** nhóm "sai tham số không phải ID" không phải nguồn mất điểm lớn nhất. Lớn nhất là **không làm đủ**:
      - Thiếu lệnh ghi: +6,2 (dev_random), +8,4 (B0) và +14,4 (D3) nếu sửa hết.
      - Ghi sai tool hoặc ghi thừa: +2,6 / +6,8 / +5,5.
      - Lệnh ghi bị thiếu là do model tự dừng (20 / 33 / 44 mẫu: yêu cầu nhiều vế làm thiếu một vế, câu điều kiện đi nhầm nhánh), hoặc hỏi lại thay vì làm (14 / 15 / 33 mẫu; D3 tăng mạnh).
    - **Trong lỗi tham số:** chọn nhầm ID +4–5; ngày giờ +2–4; còn lại mỗi nhóm ≤ ~2 (số, chữ tự do, tham số thừa, enum). Sửa hết lỗi tham số cùng lúc: +14–16.
    - **Ngày giờ:**
      - dev_random chủ yếu sai ở phép tính giờ nhiều bước, ví dụ "đón sớm 30 phút so với giờ hẹn".
      - dev_lao có thêm nhầm sáng/tối ("chín giờ tối" thành 09:00 hoặc 23:00) và nhầm "thứ ba tuần sau".
    - **Số:** chỉ 6 call, đều là lỗi tính toán, không có lỗi ×1000.
    - **Không có luật code rẻ nào cho phần lớn lỗi.** Schema cũng không khai báo giá trị mặc định, nên không bỏ được `robot_vacuum.start.mode` thừa bằng code.
    - **Hướng đề xuất:**
      - Dữ liệu SFT có yêu cầu nhiều vế và điều kiện, kiểm chứng bằng ToolEnv.
      - Model 4B (Anh quyết thuê cloud).
      - Phần rẻ: quy ước sáng/tối và "tuần sau", nhưng phải train lại mới đo được, nên làm sau giai đoạn 2.
      - Khi so D3 với B-up cần nhìn cả cái giá "hỏi lại thay vì làm".
29. **Anh đi ngủ; Claude tự làm tiếp qua đêm; được thuê cloud** (30/10, 23:58).
    - **Anh yêu cầu:**
      - Claude tự thu và đánh giá kết quả train.
      - Tự lên kế hoạch ngày mai để Anh, leader và Claude làm song song.
      - Đội thuê được cloud, nên Claude chuẩn bị gói code, dữ liệu và tài liệu để Anh đẩy lên cloud train cho nhanh.
    - **Bộ công cụ cloud** ([PR #6](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/6), nhánh `cloud-train`; hướng dẫn ở [`docs/CLOUD_TRAIN_2026-10-31.md`](docs/CLOUD_TRAIN_2026-10-31.md)):
      - `make_cloud_bundle.sh`: gói riêng tư gồm code ở một commit, dữ liệu (audio tuỳ chọn), `gen/`, adapter và các lượt gốc. Kèm manifest sha256 của các file ngoài git và của các file SFT local.
      - `cloud_setup.sh`:
        - Kiểm gói; tạo venv đúng phiên bản thư viện local, với torch 2.15.0 bản CUDA hợp với driver.
        - Ghim revision model gốc, dựng lại SFT rồi so với bản local.
        - Smoke test 3 bước train cộng 2 rollout.
      - `cloud_arms.sh`: chạy các lượt bằng đúng pipeline local, mỗi GPU một hàng đợi, tự so theo cặp với lượt gốc, rồi đóng gói kết quả.
      - **Lượt mặc định:** chấm lại 2 adapter 1.7B (kiểm parity); 4B với đúng công thức 1.7B trên fit_random và fit_lao.
      - **Đã kiểm trên máy local:**
        - Gói thật 255 MB, ở `~/zac_cloud_bundle_20261031.tar.gz`. Kiểm gói 0 file lệch.
        - Test đạt; **4 file SFT dựng lại giống hệt từng byte**.
        - Chạy thử khô việc chia lượt cho 2 GPU: đúng.
      - **Chưa kiểm:** cài torch và smoke test 4B trên máy thuê thật; parity giữa hai máy.
    - **Kết quả tạm của giai đoạn 2** (00:07; B-D1 chưa xong):

      | dev_lao (262) | Tổng | Hỏi lại | Execute | Ngoài phạm vi |
      |---|---:|---:|---:|---:|
      | B0 | 35,53 | 7,5 | 39,7 | 71,4 |
      | D3 | 31,23 | 20,2 | 32,5 | 57,1 |
      | B-up (đối chứng) | **36,94** | **30,0** | 36,7 | **85,7** |

      - **D3 so với B-up:** −5,70 điểm, khoảng tin cậy 95% từ −10,32 tới −1,15. D3 thua đối chứng rẻ, nên **không đạt tiêu chí đặt trước** (phải hơn B-up ít nhất 5 điểm hỏi lại).
      - **B-up so với B0:** +1,41, khoảng tin cậy từ −2,86 tới +5,82; chưa chắc chắn.
      - Theo kế hoạch đặt trước ([REVIEW_D](docs/REVIEW_D_2026-10-30.md)), trường hợp này dẫn tới: cân lại tỉ trọng mẫu hỏi lại thật, và hạ ưu tiên D. Kết luận đủ khi có B-D1 (khoảng 3 giờ sáng).
30. **Giai đoạn 2 của D xong: D bị loại theo tiêu chí đặt trước** (31/10, 03:09–03:20; Claude tự làm trong lúc Anh ngủ). Báo cáo: [`docs/D_PHASE2_2026-10-31.md`](docs/D_PHASE2_2026-10-31.md).
    - **B-D1** (77 dòng D, mỗi dòng một lần): tổng 37,32, hỏi lại 20,41, execute 39,45. Cao nhất về tổng, nhưng hơn B0 chỉ +1,79 (khoảng tin cậy −2,80 tới +6,37) và hơn B-up +0,39.
    - **Tiêu chí:** D1 và D3 đều chỉ đạt 1/5 điều kiện (hỏi lại hơn B0 ≥ 10). Cả hai thua B-up khoảng 9,6 điểm hỏi lại, hỏi thừa tăng 17–19 mẫu, D-eval chỉ lật đúng 1/24 và 4/24 cặp. → **Không giữ D; không làm giai đoạn 3.**
    - **B-up:** hỏi lại +22,5 (khoảng tin cậy +10,7 tới +35,3), tổng +1,4 (chưa chắc). Theo kế hoạch đặt trước: thử cân lại tỉ trọng hỏi lại trên fit_random (ràng buộc dev_random không giảm quá 1 điểm). Lượt đã sẵn trong gói cloud, chờ Anh bật.
    - **Claude tự suy luận thêm, đo bằng script mới** `scripts/overask_cost.py` (PR #5, commit `cdee489`, chỉ đọc `runs/`):
      - Câu hỏi: hỏi thừa tăng gấp đôi (16 → 31–35 mẫu) thì mất bao nhiêu điểm? Nếu nhiều, nên làm ngưỡng hỏi lại lúc suy luận (việc Codex đề xuất).
      - Trả lời: chỉ mất 1,2–2,4 điểm, vì model hỏi thừa ở các mẫu khó mà B0 cũng làm sai (B0 chỉ đúng 4,5/21 mẫu). Lọc hoàn hảo cũng chỉ thêm tối đa 1,7 điểm. → **Hạ ưu tiên ngưỡng hỏi lại.**
      - D3 mất 3,9 điểm ở các mẫu nó không hỏi thừa; D1 không bị. Nhân dữ liệu tổng hợp 3 lần làm execute kém đi.
      - Loss trên dev gần như bằng nhau (0,134–0,138) dù điểm cách nhau 6. Tiếp tục chọn bằng điểm rollout.
    - **Không đề xuất** ghép B-up với D1: không có trong kế hoạch đặt trước, và dev_lao đã bị xem nhiều lần.
    - Lượt đo đầu-cuối bắt đầu 03:09 trong cùng unit; ASR turbo trên dev_random mất 84 giây cho 784 wav (0,11 giây mỗi wav, batch 16).
31. **Baseline đầu-cuối xong: lỗi ASR làm mất khoảng 20 điểm** (31/10, 03:09–05:00; Claude tự làm trong lúc Anh ngủ). Báo cáo: [`docs/E2E_BASELINE_2026-10-31.md`](docs/E2E_BASELINE_2026-10-31.md).
    - **Điểm:** chữ chuẩn → Whisper-turbo: dev_random 53,92 → 31,69, dev_lao 35,53 → 17,14. PhoWhisper: 27,90 và 15,58. Khoảng tin cậy của cả bốn chênh lệch đều loại 0.
    - **PhoWhisper hết bộ nhớ GPU ở batch 16** (03:13). Claude tự chạy lại ở batch 4 trong unit `lifemate-pho` để vẫn so đủ hai model như kế hoạch.
    - **Chọn turbo theo luật đặt trước** (cộng gộp 495 mẫu: 23,99 so với 21,38). File nộp public `runs/e2e_public_turbo.jsonl` đã kiểm 0 lỗi; chạy lại ASR 50 wav giống hệt.
    - **Claude tự suy luận thêm:**
      - *Người nói có đọc lệch kịch bản không* (câu hỏi ở HUMAN_TODO 0.2)? Ở dev_random, khi hai model ASR nghe gần giống nhau (209 câu), chỉ 7 câu khác hẳn `audio_text`. → Hiếm; WER phản ánh lỗi nghe thật.
      - *Vì sao PhoWhisper sai ít từ hơn mà điểm thấp hơn?* PhoWhisper giữ query kém hơn (44–58% so với 60–63%), và không viết hoa, không dấu phẩy, không chữ số. Ngay cả câu sai dưới 10% số từ vẫn mất nhiều điểm. → Chọn ASR theo điểm agent và độ đúng slot, không theo WER.
      - *Mất ở đâu?* Chỉ khoảng 9% mẫu có lượt cuối sai dưới 10% số từ. Phần lớn điểm mất ở nhóm sai 25–50%. Số mẫu model không gọi tool nào tăng gấp 2–4 lần (script mới `scripts/asr_loss.py`, PR #5).
    - **Đổi ưu tiên:** ASR lên số 1, vì lớn hơn mọi phần sửa agent đã đo (6–8, 4–5, 2–4 điểm).
    - **Chuẩn bị cho cloud** (PR #6, commit `84c0a0b` cùng các commit sau):
      - `train_local.sh` / `eval_ckpt.sh` nhận `ASR_FIT`, `ASR_DEV`, `ASR_FILE`. `cloud_arms.sh` nhận `REF_ASR`. Gói đóng thêm `asr/train_*`.
      - Hai lượt 4B mặc định giờ chấm cả trên chữ turbo.
      - Lượt mới, đang để ghi chú chờ Anh: `q17b_random_asrtrain` (học trên chữ turbo), `q17b_random_asrtrain_pho`, `q4b_random_asrtrain`.
      - Transcript turbo và PhoWhisper của toàn bộ 5.036 wav train tạo trên laptop lúc 04:33–05:04. Chỉ train; public_test không bị chạy ASR ngoài `predict.sh`. Batch khác nhau gần như không đổi transcript (dev: 0/1.901 wav khác với turbo, 1/1.901 với PhoWhisper).
      - Dữ liệu SFT fit_random dựng từ chữ turbo: đúng 4.150 dòng, phần được train và cách tăng cường giống hệt bản chữ chuẩn.
      - **Gói mới** `~/zac_cloud_bundle_20261031_asr.tar.gz` (256 MB, sha256 `3a3fb94822a9…`, code `f34defa`); gói cũ không dùng nữa.
      - **Chạy thật trên laptop** một lượt qua `cloud_arms.sh` từ gói vừa giải nén (chấm 1.7B trên chữ turbo): 31,69, giống hệt 233/233 dự đoán của lượt đầu-cuối. Bộ công cụ chạy đúng đầu-cuối; chưa chạy thật lượt train nào.
    - **Kế hoạch ngày 31/10** cho Anh, leader và Claude: [`docs/PLAN_2026-10-31.md`](docs/PLAN_2026-10-31.md).

32. **Anh chọn lượt cloud theo khuyến nghị; gói v3; chạy thử đường train trên laptop** (31/10, 10:00–10:20).
    - Anh trả lời "As recommended" cho câu hỏi "bật lượt cloud nào".
    - **PR #6, commit `8c70d4f`:**
      - Bật `q17b_random_asrtrain` (1.7B học trên chữ turbo) và `q17b_random_up` (B-up trên fit_random). `q17b_random_up` nay chấm thêm trên chữ turbo; luật quyết vẫn trên chữ chuẩn (không giảm quá 1 điểm so với 53,92).
      - Bật `q4b_random_asrtrain` với khoá mới `MIN_GPUS=4`: `cloud_arms.sh` tự bỏ qua lượt này (và ghi log) khi các lượt có dưới 4 GPU. Như vậy "bật nếu có 4 GPU" không cần Anh sửa file trên cloud.
      - Thứ tự dòng chọn sao cho, với 2 hoặc 4 GPU, lượt này chạy sau lượt gốc `q4b_fit_random` trên cùng GPU. Kiểm bằng `DRY_RUN=1` với 1, 2, 3, 4 và 8 GPU. Với 5 GPU trở lên, bước so theo cặp của nó có thể báo FAILED; chạy lại `lifemate.compare` sau là được.
      - Lượt PhoWhisper và 4B B-up vẫn tắt, nằm cuối file.
    - **Gói v3:** `~/zac_cloud_bundle_20261031_v3.tar.gz` (256 MB, sha256 `bfe980b32f46…`, code `8c70d4f`). Hai gói trước không dùng nữa; chưa xoá.
    - **Claude tự làm thêm: chạy thử đường train trên laptop.** Trước đó chưa lượt train nào chạy thật qua `cloud_arms.sh`. Chạy từ gói v3 giải nén, 2 lượt 1.7B, mỗi lượt chỉ 2 bước train và chấm 10 mẫu dev_random. Đây là kiểm đường chạy, không phải kết quả.
      - `smoke_asrtrain` (như `q17b_random_asrtrain`, 10:07–10:13): file ASR phủ 4.252/4.252 lượt user của fit_random; dựng 4.150 dòng SFT; train; chấm trên chữ chuẩn và chữ turbo; so theo cặp với hai lượt gốc.
      - `smoke_up` (như `q17b_random_up`, 10:13–10:21): dựng 4.979 dòng SFT, gồm 829 dòng từ 263 mẫu hỏi lại nhân bản; các bước còn lại như trên.
      - Lượt có `MIN_GPUS=4` được bỏ qua và ghi log. Gói kết quả 189 MB, có 2 adapter (mỗi adapter 1.7B khoảng 144 MB).
      - **Phát hiện:** gói kết quả nằm ở `ZAIC_2026/cloud_results_*.tar.gz`, không phải `~/` như hướng dẫn cũ ghi. Đã sửa đường dẫn `scp` trong `CLOUD_TRAIN`, HUMAN_TODO và `PLAN_2026-10-31.md` (sửa chỗ sai, không phải cập nhật kết quả).
      - Chưa chạy lượt train đầy đủ hay lượt 4B nào qua `cloud_arms.sh`; laptop 8 GB không nạp nổi 4B.
    - Sửa [`CLOUD_TRAIN`](docs/CLOUD_TRAIN_2026-10-31.md): tên gói v3, bảng số GPU → lượt chạy → thời gian ước tính, cách giải nén đè lên gói cũ khi đã cài, `GPUS=` khi leader giữ 1 GPU cho ASR.
33. **Anh hỏi: nhờ anh trai làm ở Google train giùm** (31/10, khoảng 10:15).
    - Anh trai nhận đúng một lần, không có thời gian đọc hướng dẫn. Anh muốn một lệnh hoàn chỉnh, giải thích lệnh đó, và biết làm gì sau khi train xong.
    - **Claude kiểm điều khoản dữ liệu:** README của BTC (`data/train+public_test/README.md`, dòng đầu) ghi: dữ liệu chỉ cấp cho đội đã đăng ký, các đội không chia sẻ, phát tán hay phân phối.
      - Gói có dữ liệu train và public_test. Gửi gói cho người ngoài đội là trái điều này, nên có thể bị loại.
      - Claude khuyến nghị: hỏi BTC trước (leader đang theo dõi forum); hoặc anh trai cấp cho Anh một máy GPU và Anh tự chạy, để dữ liệu chỉ do người trong đội xử lý. Dùng máy của công ty cho việc riêng cũng cần công ty cho phép. Anh quyết.
    - **Yêu cầu của máy:** Linux, GPU NVIDIA (không chạy được trên TPU), driver ≥ 550, internet tới PyPI, pytorch.org, astral.sh và Hugging Face, ổ ≥ 100 GB. Revision model ghim vẫn là bản `main` hiện tại trên Hugging Face (kiểm 10:14), nên bước tải model sẽ không dừng.
    - **Lệnh một dòng** Claude đưa: giải nén gói v3, cài, chạy các lượt trong nền (`nohup`, thoát SSH vẫn chạy), rồi luôn để lại ở `~` hai file cần gửi về: `cloud_results_*.tar.gz` (khoảng 1 GB) và `zac_logs.tar.gz`. Đã thử với script giả: khi thành công có đủ hai file; khi cài đặt lỗi vẫn có file log ghi lý do.

34. **Anh báo đã được cho phép nhờ anh trai train** (31/10, 10:29).
    - Anh viết: "Tôi đã hỏi và họ cho phép rồi nên không sao." Claude hiểu "họ" là BTC (câu trả lời trước đề xuất hỏi BTC). Claude không tự kiểm được; ghi đúng theo lời Anh.
    - Claude đề nghị lưu lại bằng chứng cho phép (link forum hoặc ảnh chụp) ở HUMAN_TODO mục 4, phòng khi BTC hỏi lại.
    - Việc tiếp: Anh gửi gói v3 cùng lệnh một dòng (entry 33) cho anh trai. Anh trai gửi lại `~/cloud_results_*.tar.gz` và `~/zac_logs.tar.gz`, rồi xoá gói, thư mục `~/ZAIC_2026` và hai file đó.
    - Nếu anh trai chạy các lượt này thì máy cloud Anh thuê (nếu có) không cần chạy lại chúng; có thể chỉ dùng cho phần fine-tune ASR của leader.

35. **Anh hỏi: dùng Colab free / Kaggle làm dự phòng cho máy của anh trai** (31/10, 13:25–13:40). Hướng dẫn: [`docs/FREE_GPU_2026-10-31.md`](docs/FREE_GPU_2026-10-31.md).
    - Anh muốn tận dụng Colab free của mình; leader đang cân nhắc Kaggle. Mục đích: không phụ thuộc máy Google của anh trai, phòng khi máy đó là TPU.
    - **Claude kiểm:** code train và chấm dùng bf16. GPU miễn phí thường là T4, không có bf16 phần cứng, nên chạy được nhưng chậm. Ước tính thô, chưa đo: 1.7B mất 6–9 giờ mỗi epoch trên T4, so với 2,5 giờ trên laptop. 4B không thực tế trên T4.
    - Giới hạn theo nguồn bên thứ ba: Kaggle khoảng 30 giờ GPU/tuần, mỗi phiên tối đa 12 giờ, có T4 x2, chạy nền được. Colab free tối đa khoảng 12 giờ, có thể bị ngắt khi không tương tác, không đảm bảo có GPU.
    - **Khuyến nghị:**
      - 1.7B: dự phòng bằng laptop (cùng GPU với mốc cũ, khoảng 3 giờ mỗi lượt).
      - 4B: chỉ GPU trả phí từ 24 GB, nếu máy anh trai hỏng.
      - Nếu dùng GPU miễn phí thì chọn Kaggle. Kaggle hợp hơn cho việc fine-tune ASR của leader (Whisper fp16 chạy tốt trên T4).
    - **Ô lệnh notebook** dùng chung cho Kaggle và Colab: cài, đo tốc độ T4, chỉ train những lượt kịp xong trong phiên 12 giờ, luôn để lại file log. Tên lượt có đuôi `_t4` để không trùng lượt của máy anh trai. Đã thử logic ở 6 trường hợp bằng script giả; chưa chạy trên Kaggle hay Colab thật.
    - Claude chưa chạy gì trên laptop. Chạy 2 lượt 1.7B trên laptop là train dài, nên cần Anh đồng ý.
    - Laptop đã khởi động lại lúc 11:00 (giữa entry 34 và 35); thư mục tạm của Claude trong `/tmp` mất theo. Không mất gì cần giữ: code và tài liệu đã trên git, gói v3 ở `~` còn nguyên (sha256 khớp). Hai mốc giờ ghi nhầm 10:40 trong lần commit đầu của entry này đã sửa.

36. **Anh hỏi: Kaggle fine-tune ASR dùng 1.7B hay 4B; T4 x2 có chạy song song không** (31/10, 13:42).
    - **1.7B và 4B là LLM Qwen3 của agent, không phải ASR.** ASR là Whisper: turbo (0,8B) hoặc PhoWhisper-large (1,55B). Ô lệnh Kaggle/Colab ở entry 35 train agent Qwen3-1.7B, không train ASR.
    - **Chưa có code fine-tune ASR** trên nhánh nào. `lifemate/asr.py` chỉ chạy Whisper có sẵn để nhận dạng. Fine-tune ASR là phần của leader (Anh chốt 30/10); Claude viết script nếu leader muốn.
    - **Song song:** `cloud_arms.sh` chạy mỗi lượt trên 1 GPU (`CUDA_VISIBLE_DEVICES`), nên T4 x2 chạy 2 lượt khác nhau cùng lúc. Một lượt không nhanh hơn khi có 2 GPU: `train.py` nạp model lên đúng 1 GPU, không có DDP.
      - Thêm DDP thì mỗi lượt có thể nhanh gần gấp đôi, nhưng phải sửa code qua PR và kiểm parity lại. Không đáng làm lúc này, vì laptop (2,5 giờ mỗi lượt) vẫn nhanh hơn T4.
      - Fine-tune Whisper bằng HF Trainer thì dùng được cả 2 T4 (chạy bằng `torchrun --nproc_per_node 2`, fp16). Việc này thuộc script ASR của leader.
    - Anh sẽ quyết sau câu trả lời này: có chạy 2 lượt 1.7B dự phòng trên laptop không.

37. **Anh duyệt chạy 2 lượt 1.7B dự phòng trên laptop; nhờ leader chạy Kaggle** (31/10, 13:46–14:00).
    - Anh muốn tận dụng hết GPU, CPU, RAM và NPU của máy, miễn không làm crash máy. Tài khoản Kaggle của Anh chưa xác minh số điện thoại, nên nhờ leader chạy Kaggle.
    - **Laptop, bắt đầu 13:48** (unit `lifemate-laptop`, giới hạn RAM 7G/9G, chặn ngủ máy; code `7ab83a4`, giống hệt code trong gói v3):
      - Chạy nối nhau `q17b_random_asrtrain`, rồi `q17b_random_up`. Đây đúng hai dòng trong file lượt cloud (`runs/arms_laptop_2026-10-31.txt`).
      - **Không chạy song song trên GPU được:** một lượt train đã dùng tới 5,78 GB VRAM (đo ở các lượt trước), hai lượt cần khoảng 11,6 GB, vượt 8 GB.
      - GPU đang chạy 100% (86 W, 5,5 GB VRAM). Máy cắm sạc, chế độ điện `performance`.
      - CPU dựng sẵn dữ liệu SFT cho lượt thứ hai trong lúc GPU train lượt đầu (4.979 dòng). RAM và CPU không phải điểm nghẽn.
      - **NPU** (Intel Meteor Lake) không dùng được: PyTorch train trên CUDA, còn NPU chỉ chạy suy luận qua OpenVINO.
      - Dữ liệu SFT chữ turbo dựng trên laptop có sha256 `0b9d3303de97`, trùng bản dựng từ gói cloud lúc chạy thử (entry 32).
      - **Dự kiến:** lượt chữ ASR xong khoảng 16:45, lượt B-up khoảng 19:40.
      - **Sửa lời Claude ở entry 36:** câu "xong trước buổi hẹn 18:00 nếu bắt đầu 13:42" là sai, vì 6 giờ tính từ 13:42 là 19:42. Kịp 18:00 chỉ có lượt chữ ASR.
    - **Kaggle (leader):** tin nhắn và ô lệnh ở [`docs/KAGGLE_LEADER_2026-10-31.md`](docs/KAGGLE_LEADER_2026-10-31.md).
      - Ô lệnh có kiểm tra trước khi cài: GPU phải là T4, có Internet, có gói, ổ trống từ 30 GB. Báo lỗi bằng tiếng Việt.
      - Chọn lượt bằng dòng `ARMS`; mặc định `asr up`. Claude gợi ý `pho asr` để Kaggle không trùng việc với laptop.
      - Khi cài lỗi vẫn lưu file log. Thử bằng script giả ở 11 trường hợp; chưa chạy trên Kaggle thật.

38. **Anh chọn Kaggle chạy `pho asr`** (31/10, 13:58).
    - Mặc định của ô lệnh trong [`docs/KAGGLE_LEADER_2026-10-31.md`](docs/KAGGLE_LEADER_2026-10-31.md) đổi từ `asr up` sang `pho asr`. Phần mục đích trong tin nhắn cho leader cũng sửa theo.
      - `pho`: agent 1.7B học trên chữ PhoWhisper. Đây là lượt mới, chưa ai chạy; nó giúp leader chọn model ASR để fine-tune.
      - `asr`: dự phòng cho máy anh trai, đồng thời so T4 với laptop trên cùng công thức.
    - Gói v3 có đủ file cho lượt `pho`: `asr/train_all_pho.jsonl` (5.036 dòng, không dòng rỗng), `asr/train_dev_random_pho.jsonl`, và lượt gốc `runs/sft_q17b_fit_random_asrpho`.
    - Ô lệnh trong tài liệu giống hệt bản đã thử bằng script giả; trường hợp 3 lượt có `pho` đứng đầu đã nằm trong lần thử đó.
    - Link GitHub trỏ vào `main`, nên nếu Anh đã gửi link cho leader thì leader sẽ thấy bản mới.

39. **Kaggle lần đầu dừng ở bước kiểm gói; đã sửa ô lệnh** (31/10, 14:05–14:11).
    - Leader Save Version lúc 14:05 (log Kaggle ghi 18:05 UTC). `cloud_setup.sh` dừng ở bước 1: `2468 files, 99 differ`, rồi `SETUP FAILED: bundle files differ from BUNDLE_MANIFEST.json`. Anh mang file `zac_logs.tar.gz` về.
    - **Nguyên nhân:** khi tải `.tar.gz` lên dataset, Kaggle tự giải nén và bỏ file ẩn cùng thư mục `__pycache__`.
      - 99 file thiếu là đúng 2 file `.DS_Store` và 97 file `__pycache__/*.pyc` trong thư mục dữ liệu BTC (`zaic_tools`). Gói v3 có đúng 99 file loại này.
      - Các file này không cần để chạy. 2.369 file còn lại khớp sha256.
    - **Sửa trong ô lệnh** ([`docs/KAGGLE_LEADER_2026-10-31.md`](docs/KAGGLE_LEADER_2026-10-31.md)): trước khi cài, bỏ khỏi `BUNDLE_MANIFEST.json` những file vừa thiếu vừa là `.DS_Store` hoặc nằm trong `__pycache__`. Mọi file khác vẫn kiểm như cũ. Leader không cần tải lại dataset.
    - **Đã kiểm:**
      - Giải nén gói v3 thật, xoá đúng các file như Kaggle, để thư mục chỉ đọc: trước khi sửa ra 99 file khác, giống hệt log Kaggle; sau khi sửa 0 file khác.
      - Đổi 1 byte trong `train.jsonl` thì bước kiểm vẫn bắt được.
      - Hai bộ test CPU đạt trên bản thiếu `__pycache__`.
      - Chạy ô lệnh đã sửa trên bản mô phỏng (bước cài thay bằng bước kiểm gói) cho kết quả đúng.
    - **Chưa kiểm:** các bước sau bước kiểm gói trên Kaggle thật (cài torch, tải model, chạy thử GPU). Lỗi tiếp theo, nếu có, sẽ nằm ở đó.
    - Gói tạo sau này nên loại sẵn `.DS_Store` và `__pycache__`. Việc này cần sửa `make_cloud_bundle.sh` qua PR #6; gói v3 hiện tại vẫn dùng được nhờ ô lệnh.

40. **Anh hỏi: trong lúc chờ laptop và Kaggle thì Anh và leader nên làm gì** (31/10, 14:35).
    - Tình hình: laptop ở bước 75/260 lúc 14:34, đúng dự kiến (lượt chữ ASR xong khoảng 16:50, lượt B-up khoảng 19:40). Kaggle chạy lại theo ô lệnh đã sửa (entry 39).
    - **Claude đề xuất** (ghi vào HUMAN_TODO, đầu mục "Ngày 31/10"):
      - **Anh:** nộp public; xác minh số điện thoại Kaggle; nghe 18 câu ASR sai nhiều nhất cùng leader; review rồi merge PR #1, #2.
      - **Leader:** forum BTC; Docker đầu tiên; nghe audio.
    - **Fine-tune ASR (ưu tiên số 1) đang bị chặn.** GPU của leader (RTX 3050 4 GB) không đủ fine-tune Whisper-large, Kaggle của leader đang bận lượt agent, và repo chưa có script fine-tune.
      - Đề xuất: Claude viết script fine-tune Whisper (LoRA hoặc chỉ train decoder, fp16, vừa T4 16 GB) cùng gói có audio, để leader chạy trên Colab T4 của Anh.
      - Phần này thuộc leader, nên Claude chờ Anh và leader đồng ý.
    - **Claude làm trong lúc chờ (chỉ CPU, vì GPU laptop đang bận):** PR #7 (sửa `agent.py:150` cho giới hạn 30 giây, kèm chốt chặn ID làm lưới an toàn); đọc kết quả lượt chữ ASR khi xong; chuẩn bị số cho buổi 18:00.

41. **Script fine-tune ASR cho Colab; PR #7; phát hiện PR #2, #3 merge vào nhánh nền** (31/10, 14:40–15:11; Anh chọn "Viết script ASR").
    - **[PR #7](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/7)** (nhánh `asr-finetune`, xếp chồng lên #6), chưa merge:
      - **`lifemate/asr_train.py`:** fine-tune Whisper-turbo hoặc PhoWhisper-large bằng LoRA trên wav train, nhãn là `audio_text`. Chạy fp16, vừa T4 16 GB.
        - Dữ liệu: train 1.033 mẫu (3.092 wav), giữ riêng 54 mẫu (210 wav) để chọn epoch. Loại hẳn 458 mẫu của dev_random và dev_lao, có kiểm ở mức từng wav.
        - Ra adapter, model đã gộp (`lifemate.asr --model` nạp được), log và file meta.
      - `cloud_setup.sh` thêm `ASR_ONLY=1`, và bỏ qua file rác bị thiếu (lỗi Kaggle ở entry 39).
      - `make_cloud_bundle.sh` thêm `WITH_AUDIO=train`, và không bao giờ đóng file rác.
    - **Gói có audio:** `~/zac_asr_bundle_20261031.tar.gz` (845 MB, sha256 `703275377669…`, code `e618cdf`): 7.405 file ngoài git, 5.036 wav train, không có audio public.
    - **Hướng dẫn và ô lệnh Colab:** [`docs/ASR_FINETUNE_2026-10-31.md`](docs/ASR_FINETUNE_2026-10-31.md). Colab không cần xác minh số điện thoại, nên đề xuất chạy song song: Anh `turbo`, leader `pho`.
    - **Đã kiểm, chỉ trên CPU** (GPU laptop đang train agent):
      - 6 test đạt.
      - Chạy với Whisper-tiny: đủ đường chạy; `--merge-only` cho trọng số giống hệt.
      - Ô lệnh chạy trọn từ gói thật với GPU giả lập.
      - **Chưa chạy trên GPU nào.**
    - **Sự cố nhỏ:** lần đầu chạy `cloud_setup.sh` với `ASR_ONLY=1`, script ưu tiên `uv` thật trong `~/.local/bin` thay vì bản giả. Lệnh này chỉ kiểm môi trường Python dùng chung với job train ("Checked 37 packages", không cài hay gỡ gì). Lần thử sau dùng `uv` giả đặt đúng chỗ.
    - **RAM:** hai bản giải nén gói có audio trong `/tmp` (nằm trong RAM) làm RAM trống còn 3 GB. Claude xoá ngay bản đã kiểm xong; RAM trống lên khoảng 5 GB, job train không bị ảnh hưởng.
    - **Merge PR (14:47–14:48):**
      - Anh merge #1 vào `main`.
      - Leader merge #2 vào `agent-pipeline` và #3 vào `eval-protocol`, tức là vào nhánh nền của chúng. GitHub không tự đổi nhánh đích của PR xếp chồng.
      - Kết quả: `main` mới có code của #1. Code của #2 và #3 nằm ở `eval-protocol` (23 file, +2.861 dòng so với `main`).
      - Claude đề xuất mở PR `eval-protocol → main`. Việc merge là của Anh và leader.
    - **Thư mục repo chính** đã fast-forward lên `main` mới (`3d31d64`); `lifemate/` giờ có code. Trước đó đã kiểm: các thư mục chưa theo dõi chỉ chứa `__pycache__`, và `main` không theo dõi file nào trong `runs/`, `ckpt/`, `sft/`, `gen/`, `asr/`.
    - **`.gitignore` của `main`:** thêm `asr/`, `cloud_results/` và `*.tar.gz`, để transcript làm từ dữ liệu thi và các gói không thể lỡ tay commit lên repo public.

42. **Mở PR #8 `eval-protocol → main`** (31/10, 15:18; Anh chọn "Mở PR đó").
    - [PR #8](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/8) đưa code của #2 và #3 (đã merge vào nhánh nền ở entry 41) vào `main`. Không có code mới: 23 file, toàn bộ trong `lifemate/`.
    - Trên đúng cây `eval-protocol` (`3cd56e6`): `test_scorer` 11/11, `test_counterfactual` 22/22. GitHub báo MERGEABLE, CLEAN.
    - **Sau khi #8 merge:** đổi nhánh đích của #4 sang `main`. Từ đó merge từng PR từ dưới lên, mỗi lần merge xong thì đổi đích PR kế tiếp sang `main` trước khi merge nó. Claude không merge.

43. **Log Kaggle chỉ có "Debugger warning"; không dừng** (31/10, 15:20).
    - Leader gửi ảnh: bản đang chạy khoảng 62 phút (3.708 giây), GPU T4 x2, Output 0 B. Log chỉ có 8 dòng `Debugger warning ... frozen modules` ở giây thứ 7–8, không có dòng `OK:` như hướng dẫn dặn.
    - **Claude kết luận: để chạy tiếp.**
      - Các dòng đó là thông báo mặc định khi kernel của Kaggle khởi động, không liên quan tới code.
      - Ô lệnh chỉ ghi file vào Output ở cuối, nên Output 0 B là bình thường.
      - Nếu kiểm tra trước khi cài thất bại, bản đã kết thúc trong vài giây (ô lệnh `exit 1`). Nếu cài lỗi, nó cũng kết thúc trong khoảng 30–60 phút. Vẫn chạy sau 62 phút nghĩa là đã qua cả hai bước và đang train (hoặc vừa cài xong).
      - Ô lệnh tự dừng trong vòng 11 giờ, nên tối đa tới khoảng 01:00 đêm nay.
    - **Lỗi của hướng dẫn:** bước 6 dặn chờ dòng `OK:` sau 2 phút, nhưng khi chạy bằng Save & Run All, Kaggle thường chỉ hiện đầu ra của ô lệnh khi ô chạy xong. Đã sửa bước 6–7 trong [`docs/KAGGLE_LEADER_2026-10-31.md`](docs/KAGGLE_LEADER_2026-10-31.md): nhận biết qua trạng thái của bản (kết thúc sớm, kết thúc sau 30–60 phút, hay vẫn "Running").
    - Chưa xác minh được Kaggle có hiện đầu ra của `%%bash` trong lúc chạy hay không; kết luận trên dựa vào thời gian chạy. Lần sau có thể cho ô lệnh ghi tiến độ vào Output trong lúc chạy.

44. **Anh bắt đầu phần Colab: theo `docs/ASR_FINETUNE_2026-10-31.md`, chạy `MODELS="turbo"`** (31/10, 15:24).
    - Hai chỗ đã sửa trong hướng dẫn trước khi Anh chạy:
      - Ô lệnh nhận cả bản sao Drive bị đổi tên (`-name "*$BUNDLE"`). Khi leader bấm "Tạo bản sao" từ file Anh chia sẻ, file mới tên "Bản sao của ...". Đã thử với đúng tên đó.
      - Bước 5 thêm cách xem tiến độ khi ô lệnh chưa in gì: thanh Resources (GPU RAM), và log trong thư mục Files (`/root/zac/ZAIC_2026/...`). Lý do: rút kinh nghiệm từ Kaggle (entry 43).
    - Leader chạy `MODELS="pho"` trên Colab của mình, nếu leader đồng ý.

45. **HUMAN_TODO viết lại thành bảng điều phối chiều–tối 31/10** (31/10, 15:31; Anh yêu cầu trước khi bắt đầu Colab).
    - Mục "Ngày 31/10, chiều và tối" thay cho mục viết lúc sáng sớm, gồm:
      - A. Máy nào đang chạy gì, xong lúc nào, kết quả ở đâu.
      - B. Việc tiếp theo theo thứ tự: B1–B7 cho Anh, L1–L7 cho leader, C1–C5 cho Claude. Leader nộp public trước 18:00 (L1); Anh chạy Colab turbo (B2), leader chạy Colab PhoWhisper (L3).
      - C. Mốc giờ.
      - D. Gửi kết quả một lần: mỗi nguồn một thư mục trong `cloud_results/` (`kaggle`, `colab_anh`, `colab_leader`, `anh_trai`), để các file cùng tên `zac_logs.tar.gz` không đè lên nhau.
      - E. Các quyết định đã chốt trong ngày, và việc còn mở.
    - Cập nhật mục "Cách dùng file": `main` đã có code PR #1; các mục cũ từ "0." trở xuống giữ lại để tra cứu.
    - Trạng thái lúc này: laptop ở bước 165/260 của lượt (1). Anh chưa chạy Colab. Kaggle đang chạy. Máy anh trai chưa rõ.

46. **Kaggle xong mà không train (T4 quá chậm); điểm public đầu tiên 25,93; nguyên tắc tổng quát hoá** (31/10, 16:06).
    - **Kết quả Kaggle** (`cloud_results_9b233565a56a_20261031_1842.tar.gz`, 462 KB, giải nén ở `cloud_results/kaggle/x/`):
      - Kaggle cấp 2 × T4, driver 580. Torch 2.15.0+cu132 cài được.
      - Chạy thử train 1.7B: **157 token/giây**, đỉnh 10,6 GB. Laptop đạt khoảng 1.400, nên T4 chậm gần 9 lần, tức **khoảng 22,5 giờ mỗi epoch**. Ô lệnh thấy không kịp trong phiên nên tự bỏ qua 2 lượt train (`pho`, `asr`); chỉ chạy lượt chấm lại.
      - **Chấm lại adapter của laptop trên T4:** 54,35 so với 53,92, chênh +0,43 (khoảng tin cậy −1,29 đến +2,15). 228/233 mẫu giống hệt, 3 tốt hơn, 2 kém hơn. → Khác phần cứng chỉ làm số lệch rất nhỏ.
      - Chấm trên T4 mất 17,5 giây mỗi mẫu (p95 31,6, chậm nhất 38 giây), so với 2,5 giây trên laptop.
      - Lượt chạy xong khoảng 15:50, tốn khoảng 1,6 giờ GPU của leader.
    - **Claude ước tính sai:** đã đoán 6–9 giờ mỗi epoch trên T4; đo thật là 22,5 giờ. bf16 không có phần cứng trên T4 chậm hơn Claude nghĩ. Ô lệnh đo trước khi train nên không mất phiên 12 giờ. Đã sửa `FREE_GPU`, `KAGGLE_LEADER`, `CLOUD_TRAIN`.
    - **Hệ quả:**
      - Train agent cần **GPU có bf16** (Ampere trở lên: A100, A10, A30, L4, H100, RTX 30/40). T4, V100, P100 không dùng được.
      - Lệnh cho anh trai thêm bước kiểm GPU: compute capability dưới 8.0 thì dừng ngay, vẫn để lại log. Đã thử bằng GPU giả. Lệnh nằm trong `CLOUD_TRAIN`, mục "Khi nhờ người khác chạy giúp".
      - Fine-tune ASR trên Colab T4 không bị ảnh hưởng, vì Whisper chạy fp16.
      - A30 của BTC là Ampere (có bf16). Giới hạn 30 giây vẫn phải đo trên A30 thật.
    - **Lượt agent học trên chữ PhoWhisper** giờ chưa ai chạy (Kaggle không kịp; gói v3 để tắt). Chỉ còn laptop chạy được, sau 19:40, mất khoảng 3 giờ. Anh quyết.
    - **Điểm public đầu tiên: 25,9300.** Leader nộp file `e2e_public_turbo.jsonl` (Whisper-turbo chưa fine-tune và Qwen3-1.7B LoRA); Anh báo lúc 16:04.
      - Theo dev, điểm dự đoán là 17–32: dev_random 31,69 (app đã thấy), dev_lao 17,14 (app chưa thấy), gộp 495 mẫu 23,99.
      - 25,93 nằm giữa hai tập dev và gần số gộp. → Bộ chấm và hai tập dev local dự đoán public khá sát, nên tiếp tục ra quyết định trên dev được.
    - **Anh nêu nguyên tắc:** điểm này chấp nhận được như mốc baseline; không đánh đổi bằng việc học thuộc public, mà tìm cách tổng quát hoá đúng nhất. Claude đồng ý; cách làm cụ thể ghi vào HUMAN_TODO mục F:
      - Chọn model và công thức trên dev_random và dev_lao, so theo cặp có khoảng tin cậy, với luật đặt trước.
      - Coi trọng dev_lao (app chưa thấy), vì tập private có thể có app mới.
      - Public chỉ để kiểm, nộp ít, không bao giờ chỉnh theo public. Không train trên public, không pseudo-label.

47. **Đã gửi anh trai; Colab vẫn chạy ngay; HUMAN_TODO cập nhật theo mỗi thay đổi** (31/10, 16:12).
    - Anh đã gửi anh trai gói v3 và lệnh có kiểm GPU; đang chờ phản hồi.
    - Anh hỏi: tiếp tục Colab, hay gửi luôn việc fine-tune ASR cho anh trai. Anh cũng nói thêm: chuyện dữ liệu đã hỏi BTC rõ ràng, được phép.
    - **Claude khuyến nghị chạy Colab ngay** và không gửi ASR cho anh trai:
      - Anh trai chỉ chạy một lần, lần đó dành cho các lượt agent (nhất là 4B, thứ chỉ máy đó chạy được).
      - Máy anh trai chưa rõ GPU gì.
      - Colab T4 fine-tune ASR được bình thường (fp16) và có kết quả khoảng 18:00–18:30.
      - Nếu sau này anh trai có GPU mạnh và chạy thêm được một lần, Claude làm gói ASR riêng.
    - **Anh yêu cầu:** cập nhật HUMAN_TODO mỗi khi có thay đổi, để đội không bị xao nhãng vì quyết định đã đổi. Bảng điều phối nay có khung "Thay đổi gần nhất" ở đầu; quy tắc này đã lưu vào memory của Claude.

48. **Lượt laptop (1) xong: agent học trên chữ turbo không đáng dùng** (31/10, 13:48–17:00; Claude đọc lúc 17:01).
    - `q17b_random_asrtrain`: công thức `q17b_fit_random`, nhưng chữ của người nói trong dữ liệu SFT lấy từ Whisper-turbo chưa fine-tune thay cho `audio_text`. Chấm trên dev_random (233 mẫu):

      | Đọc chữ gì khi chấm | Agent học trên `audio_text` | Agent học trên chữ turbo | Chênh [khoảng tin cậy 95%] | Hỏi lại / Execute / Ngoài phạm vi (mới) |
      |---|---:|---:|---|---|
      | Chữ turbo | 31,69 | 33,22 | +1,52 [−3,58; +6,62], tốt 25 / kém 24 | 21,8 / 31,8 / 70,6 (cũ 24,4 / 28,3 / 82,4) |
      | Chữ chuẩn | 53,92 | 48,55 | **−5,37 [−10,75; −0,05]**, tốt 19 / kém 38 | 33,3 / 48,7 / 76,5 (cũ 49,4 / 51,0 / 94,1) |

    - **Đọc:**
      - Học trên chữ ASR chỉ giúp rất ít, và chưa chắc, khi đọc chữ ASR. Đổi lại, agent kém rõ khi chữ sạch: hỏi lại và ngoài phạm vi giảm mạnh.
      - Lỗi ASR làm mất thông tin (tên, số, query) mà agent không đoán lại được. Tập agent quen với lỗi không thay được việc sửa ASR.
      - → **Giữ agent học trên `audio_text`, dồn sức cho fine-tune ASR** (ưu tiên số 1). ASR càng tốt, chữ càng gần `audio_text`, thì agent hiện tại càng được lợi.
    - **Giả thuyết, chưa thử:** trộn chữ chuẩn với chữ ASR (ví dụ một nửa mỗi loại) có thể giữ được điểm trên chữ sạch mà vẫn chịu được lỗi. Chỉ đáng thử sau khi có ASR fine-tune.
    - **Lượt agent học trên chữ PhoWhisper** (chưa ai chạy): Claude nay khuyến nghị không chạy trên laptop. Cùng hướng với lượt vừa rồi, nên khó thắng; GPU laptop sau lượt (2) nên dành cho việc chấm transcript ASR fine-tune (C3).
    - Lượt (2) `q17b_random_up` bắt đầu 17:00, dự kiến xong khoảng 20:00, trễ 10 phút so với ước tính cũ vì bước chấm lâu hơn.

49. **Lượt laptop (2) xong: không giữ B-up trên fit_random** (31/10, 17:00–20:19; Claude đọc lúc 20:22).
    - `q17b_random_up`: công thức `q17b_fit_random` cộng 829 dòng từ 263 mẫu hỏi lại thật nhân bản (`gen/up_real_asks_random.jsonl`), 260 bước. Chấm trên dev_random (233 mẫu):

      | Đọc chữ gì khi chấm | Mốc `q17b_fit_random` | B-up | Chênh [khoảng tin cậy 95%] | Hỏi lại / Execute / Ngoài phạm vi (B-up) |
      |---|---:|---:|---|---|
      | Chữ chuẩn | 53,92 | 51,19 | −2,72 [−8,08; +2,52], tốt 22 / kém 30 | 69,1 / 44,0 / 94,1 (mốc 49,4 / 51,0 / 94,1) |
      | Chữ turbo | 31,69 | 29,06 | −2,64 [−6,58; +1,35], tốt 11 / kém 20 | 30,3 / 23,9 / 82,4 (mốc 24,4 / 28,3 / 82,4) |

    - **Luật đặt trước** (entry 30): dev_random không giảm quá 1 điểm thì dùng B-up làm mặc định. Giảm 2,72 → **không giữ**. Công thức agent mặc định vẫn là SFT thường (`q17b_fit_random`, `q17b_fit_lao`).
    - **Vì sao giảm:** B-up dạy model hỏi lại nhiều hơn.
      - Mẫu cần hỏi lại (33): hỏi đúng 23 mẫu, mốc 17.
      - Mẫu cần làm (183): hỏi thừa 22 mẫu, mốc 14. Cộng theo mẫu, execute mất 12,9 trong khi hỏi lại được 6,5, nên tổng giảm.
      - Giống điều đã thấy ở thí nghiệm D: tăng hỏi lại kéo theo hỏi thừa. Trên fit_lao (entry 30), mốc hỏi lại gần 0 nên B-up có lợi; trên fit_random, mốc đã 49 nên phần hỏi thừa trội hơn.
    - **Không dò tiếp tỉ lệ nhân bản trên dev_random**, theo mục F của HUMAN_TODO: chọn trên dev bằng luật đặt trước, không dò nhiều lần trên cùng tập dev. Nếu muốn cân lại sau này, dò trên tập tách từ fit, như mục "ngưỡng hỏi lại" ở mục 8.
    - **Phát hiện phụ cho C4:** mẫu `train_0830` sinh lặp "000…" trong tham số `content` hai bước liền, mỗi bước tới trần 512 token (Qwen tách mỗi chữ số thành một token), tổng 23,4 giây. Mốc chậm nhất chỉ 7,3 giây. Một mẫu như vậy cộng thời gian ASR là sát giới hạn 30 giây. Phần sửa `agent.py:150` (C4) cần có trần thời gian và trần token cho mỗi bước.
    - GPU laptop rảnh từ 20:19. Chưa nhận `asr_results_*` từ Colab nên C3 chưa chạy. Lượt agent học trên chữ PhoWhisper vẫn chờ Anh quyết; Claude khuyến nghị không chạy.
    - Máy anh trai cũng có lượt `q17b_random_up` trong gói v3. Nếu chạy, đó là một lần lặp lại trên GPU khác, dùng để kiểm độ ổn định, không đổi quyết định.

50. **C4: giới hạn 30 giây mỗi mẫu (tính cả ASR) và chốt chặn ID trong agent** (31/10, 20:25–21:08; Anh chọn "Làm C4 ngay"). Code ở [PR #9](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/9), xếp chồng lên #7, chờ review.
    - **Sửa gì:**
      - Mỗi mẫu có một hạn chót cứng: 25 giây trừ số giây ASR của mẫu.
        - Backend HF dừng sinh đúng lúc hết giờ (`max_time`); client OpenAI dừng chờ.
        - Không bắt đầu bước mới khi còn dưới 1 giây. Call đã viết xong trước lúc cắt vẫn chạy.
      - Trần 512 token mỗi bước giữ nguyên, vì bước dài nhất trong dữ liệu train là 200 token, còn dư cho app chưa thấy. Thứ đảm bảo không vượt giới hạn là hạn chót.
      - **Chốt chặn ID chạy ngay trong vòng lặp.** Quy tắc giữ như entry 27, nay nằm ở `lifemate/guard.py`, dùng chung với script phân tích (chạy lại cho đúng từng số cũ).
        - Call bị chặn không chạy; model nhận lỗi giống lỗi schema.
        - Tắt bằng `--no-id-guard`.
      - **Giới hạn:** backend vLLM chạy trong tiến trình không dừng được giữa chừng. Docker hiện dùng backend HF.
    - **Luật đặt trước** (ghi trong script trước khi chạy):
      - nhận phần thời gian nếu dev_random giống hệt từng dòng;
      - bật chốt chặn mặc định nếu dev_random và dev_lao đều không giảm.
    - **Kết quả trên GPU laptop** (20:32–21:05, commit `3fed57d`):

      | Lượt | Giống hệt từng dòng | Điểm cũ → mới | Call bị chặn |
      |---|---:|---|---:|
      | dev_random, chữ chuẩn | 233/233 | 53,92 → 53,92 | 0 |
      | dev_random, chữ turbo (trừ thời gian ASR) | 233/233 | 31,69 → 31,69 | 0 |
      | dev_lao, chữ chuẩn | 258/262 | 35,53 → 35,62 (+0,10 [0,00; +0,29]; tốt 1, kém 0) | 4 |
      | `train_0830`, adapter B-up, ngân sách 15 giây | | dừng ở 15,01 giây (code cũ: 23,4) | 0 |

    - **Đọc:**
      - Phần thời gian không đổi kết quả nào trên dev, vì trên laptop không mẫu nào gần hạn. Nó chỉ có tác dụng ở ca xấu như `train_0830`.
      - Chốt chặn chặn đúng 4 call sai mà phân tích CPU đã dự đoán.
        - Ở `train_1093`, sau khi bị chặn, model tra danh bạ rồi làm lại: 0 → 0,25.
        - Ba mẫu kia dừng luôn và vẫn 0 điểm, vì còn lỗi khác.
        - Lợi ích nhỏ, đúng như entry 27: đây là lưới an toàn, không phải nguồn điểm.
      - Trên train, chốt chặn chặn nhầm đúng 1 mẫu (`train_1696`, dữ liệu lệch). Vì vậy `check_sft` nay báo 1544/1545 thay cho 1545/1545.
      - → Theo luật đặt trước: **nhận phần thời gian; chốt chặn bật mặc định.**
    - **Chưa kiểm:**
      - thời gian trên A30;
      - cold start có tính vào giới hạn mỗi mẫu không (Q19);
      - backend vLLM.
    - Leader dựng Docker (L6) nên lấy từ nhánh `time-budget` để có giới hạn thời gian.

51. **Anh hỏi: vấn đề lớn nhất có phải ASR, và có phải đội mới chỉ tối ưu ASR** (31/10, 21:19; Anh dừng phiên hôm nay, chờ kết quả Colab).
    - **Điểm mất ở đâu** (gộp dev_random + dev_lao, 495 mẫu):

      | Agent đọc | dev_random | dev_lao | Gộp |
      |---|---:|---:|---:|
      | Chữ chuẩn `audio_text` (ASR hoàn hảo) | 53,92 | 35,53 | 44,2 |
      | Chữ Whisper-turbo chưa fine-tune | 31,69 | 17,14 | 24,0 |

      - ASR làm mất khoảng 20 điểm. Đây là chỗ tụt lớn nhất giữa hai khâu, và là đòn bẩy rẻ nhất lúc này: một model ASR tốt hơn nâng mọi mẫu.
      - Nhưng phần agent (gọi tool) mất khoảng 56 điểm ngay cả khi chữ đúng hoàn toàn. ASR hoàn hảo cũng chỉ đưa điểm gộp lên khoảng 44.
      - Lượt laptop (1) (entry 48) cho thấy agent không bù được lỗi ASR, nên lỗi ASR phải sửa tận gốc.
    - **Đội không chỉ tối ưu ASR.**
      - 28–30/10 gần như toàn bộ là phần agent: pipeline và SFT (9,9 → 53,92), thí nghiệm B (app chưa thấy, 35,53), thí nghiệm D (bị loại), phân tích lỗi (entry 27–28).
      - ASR chỉ thành ưu tiên số 1 từ sáng 31/10, sau khi baseline đầu-cuối đo ra 20 điểm (entry 31).
    - **Điểm yếu đã đo của agent** (trên chữ chuẩn, entry 28 và 30):
      - Không làm đủ: model tự dừng khi yêu cầu nhiều vế hoặc có điều kiện. Sửa hết thì +6,2 (dev_random), +8,4 (dev_lao).
      - Sai giá trị tham số: sửa hết cùng lúc thì +14–16. Trong đó chọn nhầm ID +4–5, ngày giờ +2–4.
      - Hỏi lại ở app chưa thấy: 7,48 điểm trên dev_lao.
    - **Phần agent chưa bắt đầu:**
      - dữ liệu SFT nhiều vế và điều kiện, kiểm chứng bằng ToolEnv;
      - quy ước ngày giờ (sáng/tối, "tuần sau");
      - dữ liệu app tổng hợp cho app chưa thấy.
      - Bản 4B đang chờ máy anh trai.
    - **Claude khuyến nghị:** sau khi chấm ASR fine-tune (C3, C5), đòn bẩy lớn tiếp theo là agent. Thứ tự: kết quả 4B (nếu có), rồi dữ liệu SFT nhiều vế. Chọn trên dev theo luật đặt trước, coi trọng dev_lao (mục F của HUMAN_TODO).
    - **Anh đồng ý** (21:21). Phiên sau: chấm ASR fine-tune (C3, C5) trước, rồi chuyển sang agent. Anh dừng phiên hôm nay, chờ kết quả Colab.

52. **C3: chấm agent với chữ của hai ASR fine-tune; chọn Whisper-turbo fine-tune** (01/11, 00:00–01:05; Anh báo kết quả hai Colab đã về, máy anh trai vẫn chờ).
    - **Fine-tune ASR** (Colab T4, LoRA r = 32, 3 epoch, khoảng 160 phút mỗi model, code PR #7):
      - Train trên 1.033 mẫu train (3.092 wav), kiểm trên 54 mẫu giữ lại.
      - Bỏ toàn bộ 458 mẫu của dev_random và dev_lao: sha256 của hai file id khớp bản trên máy; script chỉ đọc `train`, có assert chặn wav dev.

      | Model | WER kiểm giữ lại (train) | WER lượt cuối dev_random | WER lượt cuối dev_lao | Giữ giờ (dev_random) | Giữ từ phủ định |
      |---|---|---|---|---|---|
      | Whisper-turbo | 33,7 → **9,0** | 31,2 → **11,2** | 31,2 → **14,4** | 61 → 97% | 80 → 96% |
      | PhoWhisper-large | 23,7 → **7,7** | 25,9 → **9,2** | 26,9 → **12,9** | 75 → 97% | 86 → 98% |

    - **Luật đặt trước** (ghi trong script trước khi chạy; luật từ kế hoạch đầu-cuối 30/10, có bổ sung):
      - so điểm gộp 495 dòng, mỗi tập dev dùng adapter agent của nó;
      - model nào cao hơn thì thắng; cách nhau dưới 1 điểm thì chọn Whisper-turbo;
      - nếu người thắng kém hơn trên dev_lao quá 1 điểm thì không tự chọn mà báo đội;
      - ASR fine-tune thay turbo nếu hơn ít nhất 1 điểm.
    - **Kết quả** (GPU laptop, code `time-budget` `3519e21`, chốt chặn ID bật; agent giữ nguyên `q17b_fit_random` / `q17b_fit_lao`):

      | Agent đọc | dev_random | dev_lao | Gộp 495 |
      |---|---:|---:|---:|
      | Chữ chuẩn `audio_text` | 53,92 | 35,62 | 44,23 |
      | Whisper-turbo chưa fine-tune | 31,69 | 17,14 | 23,99 |
      | **Whisper-turbo fine-tune (được chọn)** | **42,64** | **24,55** | **33,07** |
      | PhoWhisper fine-tune | 43,04 | 24,85 | 33,41 |

      | So sánh theo cặp (gộp 495) | Chênh | KTC 95% | Tốt / kém |
      |---|---:|---|---|
      | turbo-ft so với turbo | +9,08 | [+5,42; +12,84] | 93 / 36 |
      | Pho-ft so với turbo | +9,42 | [+5,73; +13,25] | 93 / 36 |
      | Pho-ft so với turbo-ft | +0,35 | [−2,89; +3,61] | 48 / 49 |
      | turbo-ft so với chữ chuẩn | −11,17 | [−14,47; −7,87] | 22 / 93 |

      - Lượt chữ turbo trên dev_lao được chạy lại bằng cùng code: vẫn 17,14 (chốt chặn chặn 4 call, không đổi điểm).
      - Số liệu: `docs/baselines/c3_asr_ft_2026-11-01.json`.
    - **Đọc:**
      - **Fine-tune ASR thêm khoảng 9 điểm** trên cả hai tập dev; khoảng tin cậy nằm hẳn trên 0. Phần điểm ASR làm mất giảm từ 20 xuống 11.
      - Tăng nhiều nhất ở execute: dev_random 28,3 → 39,4; dev_lao 16,5 → 25,1. Hỏi lại trên dev_random 24,4 → 40,2.
      - **Hai model fine-tune gần như hoà:** cách 0,35 điểm, 48 mẫu tốt hơn và 49 mẫu kém hơn. PhoWhisper có WER thấp hơn 2 điểm, nhưng điểm agent không khác.
      - → Theo luật: **chọn Whisper-turbo fine-tune.** Model nhỏ hơn (0,8B so với 1,55B) và nhanh hơn. Với agent 4B, tổng là 4,8B so với 5,6B, vẫn dưới trần 6B.
      - Trên dev_lao, chốt chặn ID chặn 1 call (turbo-ft) và 7 call (Pho-ft). Cả 8 call đều mang ID bịa như `contact_01`, `scene_1001`, không có trong history hay kết quả tool.
      - Agent mất trung bình 2,4 giây mỗi mẫu, chậm nhất 8,1 giây với turbo-ft (chưa tính ASR).
    - **File nộp public mới (C5, 00:54–01:29):**
      - Ghép adapter turbo-ft trên laptop (cùng phiên bản peft, transformers, torch như Colab). Chạy lại ASR dev_random: khớp bản Colab 768/784 câu; khác 24 trên 11.084 từ, do sai số fp16 giữa T4 và RTX 4070.
      - `predict.sh` trên public_test: `lifemate/runs/e2e_public_turboft.jsonl`, 634 dòng, `zaic_tools --validate` 0 lỗi, sha256 bắt đầu `f87c8e1fc863`. Agent `q17b_fit_random` như lần nộp 25,93, nên chỉ ASR thay đổi.
      - So với file 25,93: 162/634 dòng giống hệt; số dòng không có call 106 → 54; tổng số call 1.198 → 1.368.
      - Thời gian trên laptop (model đã nạp): ASR 0,48 giây mỗi mẫu (chậm nhất 1,92, bằng bản turbo gốc); cả mẫu 3,04 giây (p95 5,89, chậm nhất 11,74). Không mẫu nào quá 25 giây. Chốt chặn chặn 7 call.
      - Ước lượng thô: dev gộp tăng 9 điểm, nên public có thể quanh 33–35. Anh hoặc leader tự nộp (B8).
    - **Chưa kiểm:** độ trễ ASR fine-tune trên A30; ITN số (fine-tune đã học kiểu viết của `audio_text`, nên giữ giờ đã lên 97%).

53. **Điểm public lần 2: 35,24 với ASR fine-tune; dev vẫn dự đoán public sát** (01/11, 08:11).
    - Anh nộp `lifemate/runs/e2e_public_turboft.jsonl` (Whisper-turbo fine-tune, agent `q17b_fit_random`; entry 52) và báo lúc 08:11. B8 xong.

      | Lần nộp | ASR | dev_random | dev_lao | Dev gộp 495 | Public |
      |---|---|---:|---:|---:|---:|
      | 1 (31/10, leader) | Whisper-turbo | 31,69 | 17,14 | 23,99 | 25,93 |
      | 2 (01/11, Anh) | Whisper-turbo fine-tune | 42,64 | 24,55 | 33,07 | **35,24** |
      | Chênh | | +10,95 | +7,41 | +9,08 | +9,31 |

    - **Đọc:**
      - Public tăng 9,31, gần đúng mức tăng trên dev gộp (+9,08) và nằm trong khoảng tin cậy 95% của nó (+5,42 đến +12,84).
      - Cả hai lần, public cao hơn dev gộp khoảng 2 điểm (+1,94 và +2,17) và nằm giữa dev_random và dev_lao. → Dev gộp vẫn là thước đo đáng tin; giữ cách chọn trên dev theo nguyên tắc ở entry 46 (HUMAN_TODO mục F).
      - Mới có hai điểm public, và cả hai lần chỉ khác nhau ở ASR. Thay đổi ở agent có thể chuyển sang public khác đi; tập private có thể có thêm app mới.
    - **Việc tiếp:** agent là đòn bẩy lớn nhất. ASR giờ chỉ làm mất 11 điểm gộp, còn agent mất khoảng 56 điểm ngay trên chữ chuẩn (entry 51–52). Thứ tự đã thống nhất: kết quả 4B của anh trai (chưa về), rồi dữ liệu SFT nhiều vế và có điều kiện, kiểm bằng ToolEnv.

54. **Bắt đầu phần agent: mẫu nhiều vế không phải chỗ mất điểm chính; đề xuất thử 4B 4-bit trên laptop** (01/11, 08:12–08:25; Anh chọn "Có, sang agent").
    - **Đo lại trên hai tập dev** (chỉ CPU, dữ liệu train; agent `q17b_fit_random` / `q17b_fit_lao`, đọc chữ chuẩn và chữ Whisper-turbo fine-tune):
      - Tập fit đã có nhiều mẫu nhiều vế: 36% mẫu có từ 2 lệnh ghi trở lên (477/1.312 ở fit_random), 9% có câu điều kiện.
      - Điểm theo số lệnh ghi trong đáp án (chỉ mẫu execute; chữ chuẩn / chữ ASR fine-tune; "thiếu" = số mẫu model làm ít lệnh ghi hơn đáp án):

        | Nhóm | dev_random: n, điểm, thiếu | dev_lao: n, điểm, thiếu |
        |---|---|---|
        | 1 lệnh ghi | 94; 54,9 / 47,0; 3 / 9 | 111; 44,2 / 27,2; 13 / 21 |
        | 2 lệnh ghi | 52; 48,1 / 31,5; 5 / 11 | 69; 37,3 / 24,2; 11 / 17 |
        | 3 lệnh ghi trở lên | 16; 42,0 / 15,9; 3 / 5 | 12; 8,3 / 0,0; 5 / 5 |
        | Có câu điều kiện | 22; 38,3 / 26,8; 2 / 3 | 32; 37,6 / 26,5; 5 / 7 |
        | Mọi mẫu execute | 183; 51,0 / 39,4; 11 / 25 | 214; 39,8 / 25,1; 29 / 43 |

      - Mẫu chỉ có 1 lệnh ghi cũng sai gần một nửa. Phần lớn điểm mất là làm sai một lệnh (chọn nhầm đối tượng, sai giá trị, sai tool), không phải làm thiếu vế. Nhiều vế và chữ ASR cộng dồn: 3 lệnh ghi trở lên trên chữ ASR gần như 0 điểm.
      - Mẫu ghi đúng (hash đúng) nhưng danh sách call vẫn lệch đáp án mất 9–13 điểm. Lỗi rải đều: thiếu hay thừa call đọc, tham số call đọc, thiếu hỏi lại. Không có quy ước nào sửa rẻ được.
      - Số liệu: `docs/baselines/agent_buckets_2026-11-01.json` (chỉ số, không id).
    - **Hệ quả:** dữ liệu nhiều vế chỉ nhắm vào phần nhỏ (trần +6 / +8 điểm theo entry 28). Đòn bẩy rộng hơn là model lớn hơn (4B) và ngân sách train. Thí nghiệm A (2 epoch) vẫn mở; model 1 epoch mới đạt 80,22 trên chính các mẫu đã train (entry 28).
    - **4B trên laptop:** code đã có QLoRA (`--load-4bit`, chỉ tính logits ở vị trí có loss) nhưng chưa từng đo. Chạy thử lúc 08:22 dừng ngay, vì máy chỉ có tokenizer của Qwen3-4B-Instruct-2507, chưa có trọng số (khoảng 8 GB). Cần Anh đồng ý tải (HUMAN_TODO B9).
    - **Claude đề xuất thứ tự:**
      1. Tải 4B, chạy thử 15 phút để đo VRAM và tốc độ. Nếu một epoch dưới khoảng 8 giờ, train fit_lao → dev_lao qua đêm.
      2. Thí nghiệm A: 1.7B, 2 epoch.
      3. Dữ liệu nhiều vế làm sau, nếu hai việc trên còn để lại chỗ.
      - Chọn theo luật đặt trước trên dev, coi trọng dev_lao (HUMAN_TODO mục F).
    - **Giới hạn của 4B trên laptop:** QLoRA train trên trọng số 4-bit, và chấm local cũng phải 4-bit (4B bf16 không vừa 8 GB). Trên A30 có thể chạy đúng bản 4-bit để khớp với số đo local. Máy anh trai (4B bf16) vẫn chưa trả lời.

55. **Train Qwen3-4B bản 4-bit ngay trên laptop (QLoRA); luật chọn đặt trước** (01/11, 08:50–09:30; Anh chọn "Có, tải 4B").
    - **Tải:** `Qwen/Qwen3-4B-Instruct-2507`, revision `cdbee75f` (cùng bản tokenizer đã có trên máy), Apache-2.0, 8,06 GB, tải mất 64 giây.
    - **Chạy thử trên laptop** (màn hình và trình duyệt giữ khoảng 1,35 GB VRAM):
      - Train 4 bước trên `sft/fit_lao.jsonl`: 704 token/giây, đỉnh 5,39 GB. Một epoch (12,8M token) khoảng 5–5,5 giờ.
      - Chấm 4-bit 12 mẫu dev_lao (adapter mới 4 bước): trung bình 10,9 giây mỗi mẫu, so với 2,4 giây của 1.7B bf16. Giải mã 4-bit trên laptop chậm.
      - 32 mẫu dài nhất (5,3K–6,6K token) **tràn VRAM ở bước 2**, lúc trạng thái AdamW fp32 được cấp phát. Mẫu tới 5.632 token chạy được nhưng chỉ dư khoảng 0,15 GB.
      - Thêm `--optim adamw8bit` (AdamW 8-bit của bitsandbytes) vào `train.py`: cùng 32 mẫu dài nhất đỉnh 5,64 GB, không tràn. Code: [PR #10](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/10), xếp chồng lên #9; mặc định không đổi.
    - **Lượt `q4b4_fit_lao`** (từ 09:27, unit `lifemate-q4b-lao`, worktree `~/zac-c3` ở commit `cfd9c85`):
      - Đúng công thức B0 (`q17b_fit_lao`: LoRA r32/α64, lr 2e-4, 1 epoch, grad-accum 16, cùng `sft/fit_lao.jsonl`). Chỉ khác: base Qwen3-4B nạp 4-bit, AdamW 8-bit, `--max-len 6144` (bỏ 1/4.051 mẫu, dài 6.644 token).
      - Chấm dev_lao, nạp 4-bit, code `time-budget` (chốt chặn ID bật), giới hạn 60 giây để laptop chậm không cắt mẫu nào. Trước hết trên chữ Whisper-turbo fine-tune, rồi trên chữ chuẩn.
      - Dự kiến: train khoảng 6 giờ, chấm khoảng 1,2 giờ, xong khoảng 16:30–17:00.
    - **Luật đặt trước** (ghi trong script trước khi chạy):
      - Số chính: chênh lệch theo cặp trên dev_lao chữ ASR fine-tune (262 mẫu), so với `sft_c3_fit_lao_asrturboft` (24,55).
      - Hơn ít nhất 1,0 điểm → 4B thắng vòng này; lượt laptop tiếp theo là 4B trên fit_random / dev_random, rồi quyết bằng điểm gộp 495 dòng như C3.
      - Kém hơn mức đó → giữ 1.7B. Ngoại lệ: chữ chuẩn hơn từ 3 điểm trở lên thì báo để đội quyết.
      - Báo thêm: chênh lệch trên chữ chuẩn (so với `sft_c4_fit_lao`, 35,62), số giây mỗi mẫu, số mẫu quá 25 giây.
    - **Giới hạn:** train và chấm đều 4-bit. Điểm trên A30 có thể khác nếu ở đó chạy bf16; chạy đúng bản 4-bit trên A30 thì khớp hơn. Tốc độ trên A30 chưa đo.

56. **Lượt 4B tạm dừng vì laptop phải mang đi học; thêm lưu và chạy tiếp** (01/11, 10:12–10:40; Anh hỏi lượt train có lưu checkpoint không, vì 11:00 phải mang máy đi học).
    - **Trả lời:** không. Code cũ chỉ lưu adapter ở bước 100 (khoảng 11:30), không lưu trạng thái optimizer, nên không chạy tiếp được. Lượt còn chặn máy ngủ, nên phải dừng trước khi bỏ máy vào cặp.
    - Claude dừng lượt lúc 10:13, ở bước 35/254 (loss 0,09, 694 token/giây). Phần đã chạy không dùng lại được; log giữ ở `runs/q4b4_fit_lao_2026-11-01_aborted.log`.
    - **Thêm vào `train.py`** (PR #10, commit `9de4e1a`):
      - `--state-every N` (mặc định 0, tức như cũ): cứ N bước ghi `state.pt` (trọng số LoRA, optimizer, scheduler, RNG). SIGTERM làm vòng lặp lưu sau bước đang chạy rồi thoát với mã 75.
      - `--resume`: chạy tiếp từ `state.pt`; từ chối nếu tham số hoặc dữ liệu khác.
    - **Thử trên GPU** (4B 4-bit, 4 bước trên 32 mẫu ngắn): lượt bị dừng giữa bước 2 lưu được, chạy tiếp từ bước 3 với đúng learning rate. Loss sau khi chạy tiếp cùng mức với lượt chạy liền (bước 4: 0,223 so với 0,228). Không khớp từng bit, vì GPU đã lệch nhẹ ngay ở bước 1, trước khi dừng.
    - **Bài học bộ nhớ:** trần RAM 5 GB của unit quá thấp. Bộ nhớ đệm khi đọc file model 8 GB cũng tính vào trần, nên bài thử chạy chậm. Lượt chính dùng trần 7/9 GB như trước.
    - **Lượt chính** chưa bắt đầu lại (chỉ còn khoảng 15 phút trước 11:00). Script `~/zac-c3/run_q4b_lao.sh` giờ lưu mỗi 10 bước và tự chạy tiếp; bật bằng `bash ~/zac-c3/start_q4b.sh` (HUMAN_TODO B10). Luật chọn ở entry 55 giữ nguyên.
    - **20:47:** Anh về, bấm "Chạy tiếp 4B"; máy cắm sạc. Lượt chạy lại từ đầu bằng code `9de4e1a`, unit `lifemate-q4b-lao` (trần RAM 7/9 GB, chờ dừng tối đa 10 phút). Bước 5: 711 token/giây, đỉnh 4,99 GB. Dự kiến train xong khoảng 01:30, chấm xong khoảng 03:00 ngày 02/11.

57. **4B 4-bit thắng rõ trên dev_lao; chạy tiếp 4B trên fit_random để quyết bằng điểm gộp** (02/11, 03:28–03:40; lượt C6 chạy 20:47 ngày 01/11 – 03:28 ngày 02/11).
    - **Train** (`q4b4_fit_lao`, 254 bước, 318 phút, 672–711 token/giây, đỉnh 5,55 GB, không bị dừng giữa chừng): dev loss 0,1216 (bước 50) → 0,1074 (cuối).
    - **Kết quả** trên dev_lao (262 mẫu). Hai bên dùng cùng code suy luận (`code_sha256` giống nhau), cùng file ASR, cùng danh sách id, cùng máy:

      | Agent đọc | 1.7B (mốc) | 4B 4-bit | Chênh lệch theo cặp [95%] | tốt / kém / giống |
      |---|---:|---:|---|---|
      | Chữ Whisper-turbo fine-tune | 24,55 | **39,20** | **+14,65** [+8,79; +20,49] | 78 / 30 / 154 |
      | Chữ chuẩn | 35,62 | **53,40** | **+17,78** [+11,74; +23,61] | 89 / 30 / 143 |

    - **Tăng ở đâu** (chữ ASR fine-tune; số trong ngoặc là phần đóng góp vào điểm tổng):
      - execute (214 mẫu): 25,1 → 38,6 (+11,0);
      - hỏi lại (41 mẫu): 11,1 → 39,4 (+4,4);
      - ngoài phạm vi (7 mẫu): 85,7 → 57,1 (−0,8).
      - Chữ chuẩn tương tự: execute +12,6, hỏi lại 7,5 → 43,2 (+5,6). Mẫu đủ điểm: 44 → 74 (chữ ASR), 70 → 108 (chữ chuẩn).
    - **Thời gian trên laptop** (4-bit, backend HF): chữ ASR trung bình 7,8 giây, p95 14,1, chậm nhất 27,9; chữ chuẩn 8,0 / 13,8 / 26,9. 1.7B bf16: 2,4–2,7 giây.
      - Mỗi lượt có đúng 1 mẫu quá 25 giây (`train_0304`, `train_1677`). Cả hai vốn 0 điểm, nên nếu dùng hạn 25 giây như lượt mốc thì điểm cũng không đổi.
      - Ngoài model, hai bên chỉ khác hạn giờ (25 so với 60 giây). Không mẫu nào của 1.7B chạm 25 giây (chậm nhất 12 giây).
    - **Luật đặt trước (entry 55):** +14,65 ≥ +1,0 → **4B thắng vòng này.** Không cần tới ngoại lệ chữ chuẩn.
    - **Lượt tiếp (C7, từ 03:30, unit `lifemate-q4b-random`):**
      - Script `~/zac-c3/run_q4b_random.sh`, cùng công thức trên `sft/fit_random.jsonl`: 4.150 mẫu, 13,3M token, không mẫu nào quá 6.144 token.
      - Chấm dev_random bằng chữ ASR fine-tune rồi chữ chuẩn, rồi tính điểm gộp 495 dòng như C3.
      - 37 mẫu có trong cả hai tập dev được tính hai lần, mỗi lần với adapter của tập đó. Bước gộp chạy thử trên các lượt 1.7B ra đúng 33,07 và 44,23 của C3.
      - Dự kiến train xong khoảng 08:50, chấm xong khoảng 10:00.
    - **Luật đặt trước cho điểm gộp** (ghi trong script trước khi chạy):
      - 4B hơn 1.7B (gộp chữ ASR fine-tune 33,07) ít nhất 1,0 điểm → 4B thành model agent.
      - Kém hơn mức đó → giữ 1.7B.
      - Riêng dev_random mà 4B kém quá 1 điểm thì báo đội quyết.
    - **Còn chưa biết:**
      - Thời gian trên A30. 4B ở bf16 nặng khoảng 8 GB, vừa A30 24 GB; A30 đọc bộ nhớ nhanh hơn GPU laptop nhiều, nhưng chưa đo. Cả mẫu, tính cả ASR (khoảng 0,5 giây), vẫn phải dưới 30 giây.
      - Adapter học trên base 4-bit. Nạp base bf16 trên A30 có thể làm điểm lệch nhẹ; nạp 4-bit thì khớp hơn nhưng có thể chậm hơn. Cần đo cả điểm lẫn thời gian.
      - Tổng tham số: 4B + Whisper-turbo 0,8B = 4,8B, dưới trần 6B; LLM dưới 5B.

58. **Chốt Qwen3-4B làm model agent** (02/11, 10:13–10:20; lượt C7 chạy 03:30–10:13; Anh hỏi lượt chạy tới đâu).
    - **Train** (`q4b4_fit_random`, 260 bước, 323 phút, 690–742 token/giây, đỉnh 5,56 GB; không mẫu nào bị bỏ vì quá dài): dev loss 0,0710 (bước 50) → 0,0503 (cuối).
    - **dev_random** (233 mẫu; cùng code suy luận và file ASR với lượt mốc 1.7B):

      | Agent đọc | 1.7B (mốc) | 4B 4-bit | Chênh lệch theo cặp [95%] | tốt / kém / giống |
      |---|---:|---:|---|---|
      | Chữ Whisper-turbo fine-tune | 42,64 | **54,01** | **+11,37** [+5,35; +17,45] | 49 / 23 / 161 |
      | Chữ chuẩn | 53,92 | **65,61** | **+11,70** [+5,58; +17,82] | 50 / 23 / 160 |

    - **Gộp 495 dòng** (233 dev_random + 262 dev_lao, mỗi tập chấm bằng adapter của nó; `runs/q4b4_pooled_2026-11-02.json`):

      | Agent đọc | 1.7B | 4B 4-bit | Chênh lệch theo cặp [95%] | tốt / kém / giống |
      |---|---:|---:|---|---|
      | Chữ Whisper-turbo fine-tune | 33,07 | **46,17** | **+13,11** [+8,94; +17,32] | 127 / 53 / 315 |
      | Chữ chuẩn | 44,23 | **59,15** | **+14,92** [+10,73; +19,28] | 139 / 53 / 303 |

      - Theo loại mẫu (gộp, chữ ASR fine-tune): hỏi lại 24,1 → 43,8; execute 31,7 → 44,6; ngoài phạm vi 83,3 → 79,2 (nhóm nhỏ, giảm nhẹ).
    - **Luật đặt trước:** +13,11 ≥ +1,0, và dev_random không kém (+11,37) → **4B thành model agent.** Không cần đội quyết.
    - **Thời gian trên laptop** (4-bit, HF, hạn 60 giây): dev_random chữ ASR trung bình 9,0 giây, p95 17,4; chữ chuẩn 8,6 / 16,8.
      - Trên dev_random, 4 mẫu quá 25 giây ở mỗi lượt. Gộp cả bốn lượt 4B, **không mẫu nào quá 25 giây mà có điểm**, nên dùng hạn 25 giây như lượt mốc cũng không đổi điểm. Các mẫu chậm phần lớn là vòng lặp chuyển tiền khi "số dư không đủ" (`train_0267`, `0299`, `0361`).
      - **Mẫu đầu tiên của lượt chữ ASR (`train_0003`) chạy 110 giây**, dừng vì hết giờ, chỉ 1 bước. Cùng mẫu ở lượt chữ chuẩn mất 13,1 giây. Lần sinh đầu tiên sau khi nạp model rất chậm; giới hạn thời gian của HF chỉ kiểm sau mỗi token, nên không cắt được. Trên dev_lao, mẫu đầu của lượt chữ ASR cũng chậm (27,9 giây, so với 8,6 giây ở lượt chữ chuẩn). Mẫu này 0 điểm ở cả 1.7B lẫn 4B, nên không đổi kết quả. **Docker và `predict.sh` cần chạy khởi động một lần trước mẫu đầu tiên**, ngoài giờ tính của mẫu.
    - **Việc tiếp:**
      - File nộp public bằng 4B (HUMAN_TODO B11, chờ Anh quyết): `q4b4_fit_random` nạp 4-bit, dùng lại chữ ASR của lần nộp 35,24 (`runs/e2e_public_turboft_asr.jsonl`), nên chỉ agent thay đổi. Khoảng 1,5–2 giờ trên laptop. Không cần sửa code: `lifemate.infer` đã có `--load-4bit`.
      - PR: thêm `--load-4bit` vào `predict.sh`, `eval_ckpt.sh`, `train_local.sh`, kèm bước khởi động trước mẫu đầu.
      - Đo trên A30 (hoặc GPU 24 GB gần nhất), cả 4-bit lẫn bf16, cả điểm lẫn thời gian. Đây là rủi ro lớn nhất còn lại của 4B.

59. **File nộp public 4B giao Anh tự chạy; ý tưởng sinh dữ liệu bằng Claude API** (02/11, khoảng 10:30–12:15). Anh: "Để tôi chạy sau, gửi tôi lệnh chạy riêng"; Anh có ý dùng model của Anthropic hoặc Meta (có API key cả hai: 100 USD credit Claude, 100 USD cho dịch vụ chuyển giọng nói thành chữ của Meta) để bổ sung dữ liệu train.
    - **Lệnh file nộp public:** `~/zac-c3/start_public_q4b.sh` gọi `run_e2e_public_q4b.sh` trong unit `lifemate-public-q4b` (trần RAM 7/9 GB, chặn máy ngủ).
      - Dùng lại chữ ASR của lần nộp 35,24 (`runs/e2e_public_turboft_asr.jsonl`), nên chỉ agent thay đổi.
      - Agent: `q4b4_fit_random` nạp 4-bit, hạn 60 giây như các lượt dev. Kiểm bằng `check_submission.py`.
      - Thử 2 mẫu public (`--limit 2`): 12,0 và 19,0 giây, kết quả đúng định dạng.
    - **Luật thi (mục 1.3, 1.5):** được dùng LLM hoặc TTS bên ngoài để sinh dữ liệu tổng hợp lúc phát triển, lúc suy luận thì không. BTC cho dùng catalog và `zaic_tools` của public_test để sinh dữ liệu. Cấm gán nhãn hay pseudo-label audio và yêu cầu của public/private test.
    - **Phát hiện: public_test có 11 app không có trong train**: ecommerce, event_tickets, grocery, habit_tracker, pantry, parking, public_transit, recipes, stocks, train_bus_tickets, translator (34 tool).
      - 410/634 mẫu public cài ít nhất một app này; 266 lượt assistant trong history của public gọi tới chúng.
      - 25 app có ở cả hai catalog, và tool của chúng giống hệt nhau.
      - `zaic_tools` của public_test có sẵn bộ giả lập cho cả 11 app (`apps/grocery.py`…), nên kiểm được từng call bằng cách chạy thật.
      - Đây đúng là tình huống dev_lao mô phỏng: 4B trên dev_lao (app bị giấu) đạt 39,20 so với 54,01 trên dev_random (chữ ASR fine-tune). Khoảng cách 15 điểm này là chỗ dữ liệu tổng hợp có thể lấp.
    - **Đánh giá:**
      - **Claude API: đáng làm**, nhắm vào app chưa thấy, không sinh đại trà cho app đã có đủ mẫu.
      - **Dịch vụ chuyển giọng nói thành chữ của Meta: gần như không dùng được.** Chạy trên audio test là gán nhãn test (cấm); lúc suy luận phải offline; audio train đã có nhãn `audio_text`. Chỉ có ích nếu sau này cần TTS sinh audio cho từ vựng app mới, mà dịch vụ này không phải TTS.
    - **Đề xuất pilot (chờ Anh duyệt, HUMAN_TODO B12):**
      - Sinh 300–600 mẫu cho 6 app bị giấu của dev_lao (catalog và bộ giả lập của train), trộn execute / hỏi lại / ngoài phạm vi theo tỉ lệ của train.
      - Mỗi mẫu gồm context (giờ, hồ sơ, app đã cài), trạng thái ban đầu do Claude viết theo cấu trúc trong code bộ giả lập, câu yêu cầu kiểu nói (số viết bằng chữ như `audio_text`), và chuỗi call đúng. Không đọc `<split>_environment/`, không dùng trạng thái của mẫu test.
      - Lọc: chạy chuỗi call trong `zaic_tools.Session`; bỏ mẫu có call lỗi, sai schema, hay không đổi trạng thái khi phải đổi. Mẫu hỏi lại phải thật sự thiếu tham số. Rồi cho một model khác giải lại từ câu yêu cầu; không khớp thì bỏ.
      - Train 4B trên fit_lao + mẫu sinh (cùng công thức), chấm dev_lao. **Luật đặt trước:** tăng ít nhất 2,0 điểm trên chữ ASR fine-tune (mốc 39,20) thì sinh tiếp cho 11 app của public và train bản cuối; dưới mức đó thì dừng.
      - Chi phí: Claude Opus 5.5 giá 4 / 20 USD mỗi triệu token vào / ra, Batch API giảm 50%. Mỗi lần gọi sinh vài mẫu cho cùng một app, nên ước khoảng 10–20 USD cho pilot. Script có trần tiền cứng. Claude Sonnet 5.5 rẻ bằng nửa, nếu Anh muốn tiết kiệm.
      - Key: Anh tự đặt trong `~/.zac_anthropic_env` (chmod 600); Claude không cần thấy key, không commit key.
    - **Cần Anh tự kiểm:** điều khoản API của Anthropic có điều cấm dùng dịch vụ để train model cạnh tranh. Agent 4B cho cuộc thi nhiều khả năng không thuộc diện đó, nhưng Anh nên đọc lại. Dữ liệu sinh ra và code sinh phải nằm trong gói Docker, vì BTC yêu cầu nộp cả code train và dữ liệu.
    - **12:20:** Anh báo credit Claude API chưa dùng được (tài khoản chưa đủ 7 ngày), hỏi dùng model của Meta thay được không.
      - Tra web (nguồn bên thứ ba, chưa có trang chính thức của Meta): Meta Model API có model chữ Muse Spark 1.1 (khoảng 1,25 / 4,25 USD mỗi triệu token vào / ra, kiểu OpenAI, có structured output và gọi tool) và Muse Wonder (khoảng 4 / 20 USD). Muse Voice Transcribe khoảng 0,18 USD mỗi giờ audio. Tài liệu của Meta được dẫn là credit miễn phí tính cho cả nền tảng.
      - **Trả lời: được**, nếu 100 USD của Anh dùng được cho model chữ. Luật thi cho dùng LLM ngoài bất kỳ để sinh dữ liệu. Bộ lọc chạy thật trong `zaic_tools` giữ chất lượng; model yếu hơn chỉ làm nhiều mẫu bị bỏ hơn.
      - Chưa biết: tiếng Việt của Muse Spark tốt tới đâu (thử 20 mẫu trước), và điều khoản của Meta về dùng đầu ra để train model khác (Anh tự đọc).

60. **Bộ sinh dữ liệu tổng hợp: code xong, bài thử 20 mẫu chờ key** (02/11, 12:20–12:35; Anh chọn "Viết và thử 20 mẫu").
    - **API của Meta** (đọc tài liệu dev.meta.ai): `https://api.meta.ai/v1/chat/completions`, key qua header Bearer, kiểu OpenAI. Model chữ: `muse-spark-1.3` (khuyên dùng), 1.2, 1.1 cùng giá 1,25 / 4,25 USD mỗi triệu token; `muse-wonder-1.0` 4 / 20 USD (đang preview). Có structured output (`response_format` json_schema). Model luôn suy luận ngầm; token suy luận tính tiền như token ra. Không có Batch API.
      - Gói Standard: Meta không dùng nội dung để train. Gói contributor rẻ hơn nhưng Meta được dùng prompt để train; code từ chối gói này, vì prompt chứa catalog và code bộ giả lập của gói dữ liệu thi (cấm phát tán).
    - **Code** ([PR #11](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/11), nhánh `synth-data` xếp chồng lên #10, worktree `~/zac-synth`): `lifemate/synth.py`.
      - `gen`: mỗi lần gọi API sinh 4 mẫu cho một app. Prompt gồm quy tắc của trợ lý (`prompt.SYSTEM_RULES`), 5 ví dụ đáp án thật từ fit_lao (3 execute, 2 hỏi lại), schema tool của app, code bộ giả lập của app và hàm dùng chung, và 4 context lấy từ fit_lao (giờ, người dùng, 2–4 app khác). Khoảng 5K token mỗi lần.
      - `check`: chạy từng call trong bộ giả lập trên state do model viết; loại mẫu lỗi schema, call trả done=false, ID không do lời gọi đọc trả về, ID bị đọc ra trong câu nói, execute không đổi trạng thái, hỏi lại sai luật. Rồi một lần gọi API khác giải lại từ câu nói; giữ mẫu khi cùng trạng thái cuối và cùng các lời gọi ghi/hỏi.
      - Ví dụ thật cho thấy gold được làm phần việc đủ thông tin trước rồi mới hỏi phần thiếu (`alarm.create` rồi hỏi `ewallet.transfer`), nên bộ kiểm chỉ loại mẫu hỏi lại nếu đã gọi chính tool đang hỏi.
      - `sft`: mẫu đạt thành dòng SFT bằng `sft.build_all`, cùng các biến thể đổi tên, app gây nhiễu, viết thường như fit.
      - Trần tiền cứng theo sổ ghi từng lần gọi (`gen/synth_<tag>_usage.jsonl`). Key đọc từ biến môi trường, không ghi ra file.
      - 14 test CPU đạt (`lifemate.tests.test_synth`), không gọi API.
    - **Bài thử 20 mẫu** (`~/zac-synth/run_synth_t20.sh`): library, loyalty, medication, video_meeting, home_security × 4 mẫu, trần 3 USD; ước tốn dưới 1 USD. robot_vacuum để dành cho pilot vì tool của nó không có tham số bắt buộc, không có mẫu hỏi lại.
    - **Luật đặt trước để sang pilot:** ít nhất 8/20 mẫu qua mọi bước kiểm, và Anh thấy ít nhất 4/5 câu được nhận là tự nhiên. Pilot: 300–600 mẫu, train 4B trên fit_lao + mẫu sinh, giữ nếu dev_lao chữ ASR fine-tune tăng ít nhất 2,0 điểm so với 39,20. Không đạt thì sửa prompt một lần (hoặc dùng `muse-wonder-1.0`) và thử lại; vẫn không đạt thì dừng.
    - **Chờ:** key Meta trong `~/.zac_meta_env` (HUMAN_TODO B13). Claude cài lệnh chờ: file có là bài thử tự chạy.
    - **13:10:** Anh lưu key; bài thử tự chạy. Anh đặt **trần chi tiêu: tổng dưới khoảng 10 USD cho việc sinh dữ liệu bằng API, vượt mức phải hỏi Anh.**
    - **Anh hỏi: dùng VieNeu (local) để sinh tiếng Việt train thêm, hay tập trung vào Meta / Anthropic?**
      - VieNeu là model TTS tiếng Việt chạy trên máy (có nhân bản giọng, bản v3 Turbo 48 kHz, gói `vieneu` trên PyPI). Nó đọc chữ thành audio; không tự viết câu yêu cầu và đáp án. Nên nó **không thay được** bước sinh bằng Meta, mà dùng **sau** bước đó: đọc các câu đã sinh thành audio để train ASR.
      - Số đo trên dev_lao (chữ Whisper-turbo fine-tune, cùng các lượt ở entry 57):

        | Mẫu dev_lao | n | 4B chữ chuẩn | 4B chữ ASR | ASR làm mất | 1.7B mất |
        |---|---:|---:|---:|---:|---:|
        | Dùng app bị giấu | 183 | 51,9 | 34,8 | **17,1** | 13,8 |
        | Chỉ dùng app đã thấy | 79 | 56,9 | 49,3 | 7,6 | 4,7 |

        WER lượt cuối: 15,1% ở mẫu dùng app bị giấu, 12,6% ở mẫu còn lại. ASR sai nhiều hơn một chút, nhưng agent mất điểm nhiều hơn hẳn khi gặp app lạ và chữ sai cùng lúc.
      - **Kết luận:** làm Meta trước, vì agent mất khoảng 48 điểm ngay trên chữ chuẩn ở app chưa thấy. VieNeu đáng thử sau, dùng chính các câu đã sinh: trộn một phần audio TTS với audio thật để fine-tune lại ASR, đo WER và điểm agent trên dev_lao.
      - Trước khi dùng VieNeu phải kiểm licence: nguồn tìm được không khớp nhau (một bản sao ghi Apache-2.0, vài repo dùng checkpoint 1000h/140h ghi CC-BY-NC-4.0). Luật thi đòi licence cho phép. Ngoài ra audio TTS sạch và ít giọng hơn audio thật, nên chỉ nên là phần nhỏ.
    - **Kết quả t20** (13:10–13:14, code `ada293c`): **14/20 mẫu qua mọi bước kiểm**, 0,366 USD (0,026 USD mỗi mẫu đạt).
      - Bị loại: 3 vì bước giải lại ra lời gọi ghi/hỏi khác (đều là câu mơ hồ thật: "đặt giữ Đắc Nhân Tâm" khi có nhiều ấn bản, "đánh dấu đã xem" khi có nhiều cảnh báo); 2 vì bước giải lại thừa dấu `}` sau JSON tham số; 1 câu chỉ hỏi thông tin bị loại nhầm là `no_write`.
      - Chi phí: mỗi lần sinh khoảng 4,2K token vào, 6,8K token ra (4,6K là suy luận ngầm), 0,034 USD cho 4 mẫu. Mỗi lần giải lại 2,9K vào, 1,6K ra (1,5K suy luận), khoảng 0,01 USD.
      - Giọng văn lệch so với 1.283 câu thật của fit_lao: "giùm" 95% so với 12%, "rồi" 55% so với 32%, dài 15,7 so với 22,5 từ.
      - Giới hạn không lọc được: quy ước tham số của người gán nhãn thật với app mới (ví dụ `loyalty.redeem` nhận tên hay ID chương trình, đều chạy được). Không được nhìn đáp án dev_lao để chỉnh, nên chỉ pilot mới đo được ảnh hưởng.
    - **Sửa** (commit `06aabfa`, PR #11; 19 test CPU):
      - thêm loại `lookup` (câu chỉ hỏi thông tin, 8% của fit_lao);
      - mỗi lần sinh kèm 12 câu thật mới từ fit_lao làm mẫu giọng văn, cùng yêu cầu đa dạng (mở đầu khác nhau, câu điều kiện, tự sửa giữa chừng, giọng miền);
      - đọc tham số bỏ qua dấu `}` thừa; bước giải lại suy luận mức thấp;
      - trần tổng mọi lượt (mặc định 10 USD, theo Anh), kiểm trước mỗi lần gọi.
    - **Kết quả t12** (13:16–13:19, code `06aabfa`; robot_vacuum, home_security, library × 4): **9/12 đạt**, 0,187 USD (0,021 USD mỗi mẫu đạt).
      - Câu đa dạng hơn: "Thế cho anh hút bụi phòng khách với bếp luôn đi...", "Ừ, cho nó chạy lau cái bếp giùm em, à không lau cả phòng khách nữa mới sạch", "Cho dọn cả nhà luôn đi bây, hút bụi thôi nghe, bụi quá chịu không nổi mô", "Nếu cuốn Nhà Giả Kim còn trong thư viện thì đặt giữ luôn nhé".
      - Bị loại: 1 hỏi lại tham số không bắt buộc (`robot_vacuum.start` rooms), 2 câu mơ hồ mà bước giải lại hiểu khác. Lượt này không có câu `lookup` (do bốc ngẫu nhiên).
      - Câu tự sửa "à không" giờ hơi nhiều (3/12); để ý khi sinh pilot.
    - **Điều kiện đầu đạt** (cần ít nhất 8/20, tức 40%): t20 70%, t12 75%. **Tổng đã chi: 0,553 USD.**
    - **Chờ Anh** chấm độ tự nhiên trên `lifemate/gen/synth_review_t12_t20.md` (23 câu đạt; HUMAN_TODO B14).
    - **Kế hoạch pilot nếu đạt:** khoảng 380 mẫu đạt cho 6 app (khoảng 8 USD với giá 0,021 USD mỗi mẫu đạt; tổng dưới 10 USD), train 4B trên fit_lao + mẫu sinh, chấm dev_lao. Luật: giữ nếu tăng ít nhất 2,0 điểm trên chữ ASR fine-tune so với 39,20. Sinh cho 11 app của public sau đó sẽ vượt 10 USD, nên phải hỏi Anh.
    - **13:30:** Anh **nâng trần lên 30 USD** ("để thoải mái và tăng chất lượng"), báo đang chạy file nộp public (B11, từ 13:10) nên chưa train 4B được. Chưa báo kết quả chấm độ tự nhiên.
    - **Sửa thêm** (commit `7c70a9e`, `9a02d14`; 20 test CPU):
      - trần tổng mặc định 30 USD;
      - loại câu gần trùng câu đã nhận của cùng app (difflib ≥ 0,8);
      - lưu từng kết quả giải lại ngay khi có, chạy lại thì dùng lại, không trả tiền hai lần;
      - kiểm không gọi API ghi ra file riêng (`*_nosolver*`). Lần kiểm thử loại này trước đó đã ghi đè kết quả t12; đã chạy lại bước kiểm đầy đủ để khôi phục (10/12, vì bước giải lại có chút ngẫu nhiên);
      - prompt nêu tỉ lệ thật: tự sửa và điều kiện mỗi loại khoảng 1/10 câu (fit_lao: 8% và 6%), khoảng 2/5 câu có từ hai việc, "giúp" khoảng 1/4, "giùm" khoảng 1/8;
      - bước giải lại hỏi lại một lần khi JSON tham số hỏng.
    - **Thử `muse-wonder-1.0` làm model sinh** (tag `wonder_t8`, library và medication × 4; bước giải lại vẫn là `muse-spark-1.3`):
      - 8/8 đạt (2 mẫu lần đầu hỏng vì bước giải lại chèn chữ rác sau JSON; hỏi lại thì đạt); 0,078 USD mỗi lần sinh 4 mẫu, gấp 2,3 lần `muse-spark-1.3`; khoảng 0,029 USD mỗi mẫu đạt.
      - Câu dài 21 từ (thật: 22,5; spark 19–20), nhưng "giùm" vẫn 50%. Kịch bản phong phú hơn: câu nhiều việc, làm phần đủ thông tin rồi hỏi phần thiếu ("Xoá nhắc thuốc Canxi..., rồi thêm nhắc uống thuốc sắt..." → xoá, rồi hỏi `times`), lịch "mấy ngày trong tuần, đừng nhắc cuối tuần" → `days=weekdays`.
      - Chọn `muse-wonder-1.0` cho pilot. Lượt `lao_p1` bằng spark đã dừng sau 4 lần gọi (16 mẫu thô, 0,15 USD, không dùng).
    - **Pilot đang chạy** (unit `lifemate-synth-w1`, từ 13:38, `~/zac-synth/run_synth_lao_w1.sh`): 6 app của dev_lao × 64 mẫu thô, trần lượt 12 USD, ước khoảng 9 USD, xong khoảng 14:55.
    - **Script train + chấm pilot** (`~/zac-synth/run_q4b_lao_synth.sh`, bật bằng `start_q4b_lao_synth.sh`, unit `lifemate-q4b-synth`): đúng công thức `q4b4_fit_lao`, dữ liệu `sft/fit_lao.jsonl` + dòng SFT của mẫu đạt (train.py tự xáo, seed 0). Chấm dev_lao chữ ASR fine-tune và chữ chuẩn, so với `sft_q4b4_fit_lao` (39,20 / 53,40), kèm lát cắt app bị giấu (183 mẫu) và app đã thấy (79). Luật đặt trước: giữ nếu chữ ASR tăng ít nhất 2,0 điểm. Chờ GPU rảnh sau B11.
    - **Dự tính chi:** pilot khoảng 9 USD; 11 app public cùng cỡ khoảng 16,5 USD; tổng khoảng 26,5 USD, dưới trần 30. **Đã chi tới 13:40: 0,9 USD.**
    - **13:47:** Anh chọn "Tự bật khi xong". Claude cài lệnh chờ: khi `lifemate-public-q4b` và `lifemate-synth-w1` đều xong, và có ít nhất 100 mẫu đạt, chạy `start_q4b_lao_synth.sh`. Giá thật của `muse-wonder-1.0` trong pilot khoảng 0,095 USD mỗi lần sinh (19 lần đầu, 1,80 USD), cao hơn ước tính 0,078. Pilot vì vậy khoảng 10–11 USD; phần 11 app public phải giảm số mẫu mỗi app, hoặc hỏi Anh nếu tổng sẽ vượt 30 USD.

61. **File nộp public 4B xong; pilot sinh 280 mẫu đạt; train pilot tự bật** (02/11, 14:42–14:54).
    - **File nộp public (B11, Anh bật 13:10):** xong 14:42, kiểm định dạng 14:51. 634 dòng, `zaic_tools --validate` 0 lỗi, `ok=True`. File: `~/zac-c3/lifemate/runs/e2e_public_q4b.jsonl`, sha256 `2fc287ffa729…`. 1.452 lời gọi; 54 dòng không có lời gọi nào.
      - Thời gian mỗi mẫu trên laptop (model đã nạp sẵn, không phải A30): ASR trung bình 0,48 giây; agent trung bình 8,6 giây, p95 17,1 giây, lâu nhất 38,2 giây. Tổng trung bình 9,1 giây, p95 17,9 giây.
      - 2/634 mẫu quá 30 giây (30,9 và 38,2 giây), cả hai chạy hết 8 bước mà không dừng. Lượt này đặt hạn 60 giây; bản Docker phải đặt hạn dưới 30 giây và có bước khởi động trước khi tính giờ.
      - Anh hoặc leader tự nộp; Claude không nộp.
    - **Pilot sinh `lao_w1`** (13:38–14:45, `muse-wonder-1.0` sinh, `muse-spark-1.3` giải lại, code `a0a6936`): **280/384 mẫu đạt** (73%), **11,55 USD** (0,041 USD mỗi mẫu đạt; trần lượt 12 USD).
      - Theo app: library 54, robot_vacuum 44, loyalty 56, medication 46, video_meeting 30, home_security 50.
      - Theo loại: execute 210, hỏi lại 41, chỉ hỏi thông tin 29.
      - Số lời gọi mỗi mẫu: 1 (41 mẫu), 2 (135), 3 (75), 4 (29).
      - Bị loại: bước giải lại ra lời gọi ghi/hỏi khác 50; gần trùng câu đã nhận 23; hỏi lại sai luật 16; bước giải lại hỏng JSON 9; lỗi schema 3; execute không ghi 2; state cho app chưa cài 1.
      - Giọng văn so với 1.283 câu thật của fit_lao: dài 20,6 từ (thật 22,5); "giùm" 10% (12%); "giúp" 24% (23%); câu điều kiện 5% (6%); tự sửa giữa chừng khoảng 4% (8%). Gần câu thật hơn nhiều so với bài thử đầu.
    - **Tổng đã chi: 12,57 USD** (t20 0,37; t12 0,27; wonder_t8 0,23; lao_p1 0,15; lao_w1 11,55). Còn 17,43 USD tới trần 30 USD.
    - **Train pilot tự bật lúc 14:52** (unit `lifemate-q4b-synth`, code `a0a6936`): 280 mẫu thành 924 dòng SFT; cộng 4.051 dòng fit_lao, tổng 4.974 dòng (1 dòng quá dài bị bỏ), 14,5 triệu token. Nhiều hơn mốc `q4b4_fit_lao` khoảng 23%, nên train khoảng 5,5–6 giờ, chấm dev_lao khoảng 2 giờ; dự kiến xong khoảng 22:30–23:00.
    - **Luật đặt trước (giữ nguyên):** giữ mẫu sinh nếu dev_lao chữ ASR fine-tune tăng ít nhất 2,0 điểm so với 39,20. Kèm số chữ chuẩn (mốc 53,40) và hai lát cắt app bị giấu (183 mẫu) / app đã thấy (79).
    - **20:23 (Anh hỏi tiến độ):** train ở bước 280/311, còn khoảng 37 phút, rồi chấm dev_lao khoảng 1,5–2 giờ; xong khoảng 22:30–23:00. Loss trên dev_lao ở bước 250: 0,1019, so với 0,1074 của `q4b4_fit_lao` cùng bước. Chỉ là tín hiệu sớm; luật giữ hay bỏ vẫn dựa trên điểm chấm.
    - **20:55 (Anh hỏi lại):** bước 300/311, loss dev_lao 0,1016 (mốc cuối 0,1074); train xong khoảng 21:10, chấm xong khoảng 22:40–23:10.
    - **21:16 (Anh hỏi lại):** train xong 21:15 (311 bước, 371 phút; loss dev_lao cuối 0,1014 so với 0,1074 của mốc). Đang chấm dev_lao trên chữ ASR fine-tune (từ 21:15), rồi chữ chuẩn; mỗi lượt khoảng 40–50 phút, xong khoảng 22:45.
    - **22:17: kết quả chữ ASR fine-tune: 39,20 → 37,12, tức −2,09, khoảng tin cậy 95% [−7,22; +3,01]; tốt hơn 35 mẫu, kém hơn 49, như nhau 178. Không đạt luật đặt trước (cần ít nhất +2,0), nên không giữ dữ liệu sinh ở dạng này, và chưa sinh cho 11 app public.**
      - App bị giấu (183 mẫu): 34,84 → 33,87 (−0,96). App đã thấy (79 mẫu): 49,31 → 44,62 (−4,69).
      - call-F1 51,41 → 47,81; tỉ lệ đúng trạng thái 51,53% → 53,44%. Mẫu đủ điểm 74 → 61, được một phần 47 → 60, 0 điểm vẫn 141.
      - Theo loại: hỏi lại 39,4 → 33,3; execute 38,6 → 36,7; ngoài phạm vi 57,1 → 71,4 (chỉ 7 mẫu).
      - Lượt chấm chữ chuẩn đang chạy, xong khoảng 22:40.
    - **22:37: chữ chuẩn cũng giảm: 53,40 → 50,57, tức −2,83 [−7,93; +2,35]**; tốt hơn 36 mẫu, kém hơn 56. App bị giấu 51,90 → 49,26 (−2,65); app đã thấy 56,88 → 53,62 (−3,26). call-F1 63,33 → 60,27; tỉ lệ đúng trạng thái gần như giữ (66,79% → 66,41%).
    - **Đọc:**
      - Cả hai loại chữ đều giảm khoảng 2–3 điểm; khoảng tin cậy chứa 0, nên có thể là không đổi, nhưng chắc chắn không có mức tăng 2 điểm luật cần. Dữ liệu sinh không giúp ngay cả trên đúng các app nó nhắm tới.
      - Kiểm thói quen gọi tool (không nhìn đáp án dev): số lời gọi, số lời gọi đọc mỗi mẫu của hai model gần như giống nhau (2,20 so với 2,16; 0,92 so với 0,91). Mẫu sinh mở đầu bằng lời gọi đọc 90% số mẫu, câu thật chỉ 59%, nhưng model dự đoán vẫn giữ 59–61%. Model mới hỏi lại ít hơn trên chữ chuẩn (0,15 → 0,10 lần mỗi mẫu).
      - Giả thuyết chưa kiểm: quy ước tham số và cách chọn bước của model sinh khác người gán nhãn thật (entry 60 đã nêu là giới hạn không lọc được). Muốn kiểm phải nhìn từng lỗi trên dev_lao, mà dùng lỗi dev để sửa bộ sinh thì dev không còn là thước đo sạch.
    - **Kết luận theo luật đặt trước: không dùng dữ liệu sinh `lao_w1`, không sinh cho 11 app public.** Tổng đã chi giữ ở 12,57 USD. Code ở [PR #11](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/11) vẫn để đó, chưa merge. GPU laptop rảnh từ 22:38.
    - **Phần 11 app public sau pilot (nếu giữ):** còn 17,43 USD. Với 0,041 USD mỗi mẫu đạt, khoảng 30 mẫu đạt mỗi app tốn khoảng 13,5 USD; muốn nhiều hơn thì hỏi Anh.

62. **Điểm public lần 3: 45,39 với agent 4B** (02/11, Anh báo lúc 15:47). B11 xong.
    - Anh nộp `~/zac-c3/lifemate/runs/e2e_public_q4b.jsonl` (entry 61): agent `q4b4_fit_random` nạp 4-bit, cùng chữ Whisper-turbo fine-tune với lần 2, nên chỉ agent thay đổi.

      | Lần nộp | ASR | Agent | dev_random | dev_lao | Dev gộp 495 | Public |
      |---|---|---|---:|---:|---:|---:|
      | 1 (31/10, leader) | Whisper-turbo | 1.7B | 31,69 | 17,14 | 23,99 | 25,93 |
      | 2 (01/11, Anh) | Whisper-turbo fine-tune | 1.7B | 42,64 | 24,55 | 33,07 | 35,24 |
      | 3 (02/11, Anh) | Whisper-turbo fine-tune | **4B 4-bit** | 54,01 | 39,20 | 46,17 | **45,39** |
      | Chênh lần 3 so với lần 2 | | | +11,37 | +14,65 | +13,11 | +10,15 |

    - **Đọc:**
      - Public tăng 10,15, ít hơn mức tăng trên dev gộp (+13,11) nhưng vẫn trong khoảng tin cậy 95% của nó (+8,94 đến +17,32). Dev gộp vẫn dự đoán đúng hướng và gần đúng cỡ.
      - Lần này public thấp hơn dev gộp 0,78 điểm; hai lần trước cao hơn khoảng 2 điểm. Một lần đổi chiều như vậy vẫn nằm trong mức nhiễu, chưa đủ để kết luận.
      - Một giả thuyết, chưa kiểm: 410/634 mẫu public có cài ít nhất một trong 11 app không có trong train. Các app này lạ hơn các app bị giấu của dev_lao, vì chúng không có trong catalog train. Nếu đúng, dữ liệu sinh cho 11 app này (sau pilot) là chỗ đáng làm. Không được nhìn đáp án public, nên chỉ kiểm được gián tiếp qua lần nộp sau.
      - Đây là lần đầu thay đổi ở agent; hai lần trước chỉ khác ASR.

63. **Anh hỏi còn chiến lược nào để nộp public thêm; Claude xếp hạng** (02/11, 22:44). Còn 14 ngày tới hạn Docker 16/11; laptop chạy được khoảng một thí nghiệm 4B mỗi ngày (6–7 giờ).
    - **Mất điểm còn nằm ở đâu (4B, dev):** agent mất 34–47 điểm ngay trên chữ chuẩn (dev_random 65,61; dev_lao 53,40). ASR mất thêm 11,6 điểm trên dev_random và 14,2 điểm trên dev_lao.
    - **Đã thử, không đạt:** dữ liệu sinh bằng API (entry 61), hạ ngưỡng hỏi lại (trần 1,2–1,7 điểm, entry 30), B-up (entry 49), chốt chặn ID (gần 0, entry 27), D (entry 30), agent học thuần chữ turbo (1.7B: chữ ASR +1,52 không chắc, chữ chuẩn −5,37, entry 48).
    - **Đề xuất, theo thứ tự:**
      1. **4B học trên chữ trộn:** một nửa mẫu fit_random dùng `audio_text`, nửa còn lại dùng chữ Whisper-turbo chưa fine-tune (đã có `asr/train_all_turbo.jsonl`, không phải chạy ASR lại). Đây là giả thuyết còn mở ở entry 48: giữ điểm chữ chuẩn mà vẫn quen lỗi ASR. Nhắm vào 11–14 điểm ASR làm mất. Một lượt khoảng 6,7 giờ, chấm được trên dev_random. Luật đề xuất: giữ nếu dev_random chữ ASR fine-tune tăng ít nhất 1,0 so với 54,01 và chữ chuẩn không giảm quá 2,0 so với 65,61. Giới hạn: chữ turbo chưa fine-tune sai khoảng 26–31% số từ, nhiều hơn ASR lúc chạy thật (11–14%); chữ của ASR fine-tune trên fit thì gần như thuộc lòng nên không dùng được.
      2. **Train lại công thức thắng trên đủ 1.545 mẫu train** (fit_random + 233 mẫu dev_random, thêm khoảng 18% dữ liệu). Đây là model cuối cho Docker. Không còn dev để chấm, nên chỉ kiểm vài mẫu, rồi nộp public làm mốc.
      3. **Sẵn sàng Docker** (không đổi điểm public nhưng giữ điểm private): bước khởi động trước khi tính giờ, hạn dưới 30 giây mỗi mẫu, nạp 4-bit hay bf16 trên A30 (laptop 8 GB không đo được bf16).
    - **Không đề xuất lúc này:** sinh thêm dữ liệu bằng API (pilot vừa không đạt; sửa bộ sinh phải dựa vào lỗi trên dev_lao); 2 epoch (loss dev_lao gần như phẳng từ bước 150: 0,1062 → 0,1074); đổi ASR (PhoWhisper fine-tune ngang turbo fine-tune); model LLM lớn hơn (4B đã là cỡ lớn nhất của Qwen3 dưới 5B).
    - Tỉ lệ dòng không có lời gọi trên public (8,5%) gần bằng trên dev (6,4–8,2%), nên không có dấu hiệu lỗi riêng ở public.
    - **Chờ Anh chọn** (HUMAN_TODO B15).

64. **Anh hỏi lại các chiến lược và có nên train song song trên Colab; laptop chạy 4B học chữ trộn** (03/11, 00:16–00:22; Anh: "test song song sáng mai cùng với bản đêm nay train", tức chọn chạy đêm nay ở B15).
    - **Laptop bắt đầu lượt 4B học chữ trộn lúc 00:19** (`q4b4_fit_random_mix50`; unit `lifemate-q4b-mix`; script `~/zac-c3/run_q4b_random_mix.sh`, ngoài repo như các script chạy khác).
      - Dữ liệu: 656/1.312 mẫu fit_random (chọn bằng `random.Random(0)`) lấy mọi dòng từ bản dựng chữ Whisper-turbo chưa fine-tune (`sft/fit_random_q17b_random_asrtrain.jsonl`, bản đã dùng ở entry 48). Nửa còn lại lấy từ `sft/fit_random.jsonl`. Tổng 2.062/4.150 dòng dùng chữ turbo.
      - Đã kiểm hai bản dựng khớp từng dòng: cùng id, cùng augmentation, phần model phải học giống hệt (0 dòng lệch); chỉ khác lời người dùng. 10 dòng giống hệt vì turbo nghe đúng từng chữ.
      - Việc trộn là bước dựng dữ liệu một lần trong script chạy; chưa thêm cờ vào `sft.py`. Nếu công thức thắng, cờ `--asr-frac` sẽ đi qua PR.
      - Công thức giữ nguyên `q4b4_fit_random`: cùng 4.150 ví dụ (0 ví dụ quá dài), 260 bước. Dự kiến train xong khoảng 05:50, chấm xong khoảng 07:05 (lượt mốc: train 5,5 giờ, chấm 1,2 giờ).
    - **Luật đặt trước** (ghi ở đầu script trước khi chạy):
      - **Cửa 1, dev_random**, so theo cặp với 4B học chữ chuẩn: chữ ASR fine-tune tăng ít nhất 1,0 so với 54,01, **và** chữ chuẩn không giảm quá 2,0 so với 65,61.
      - **Qua cửa 1:** chạy cùng công thức trên fit_lao → dev_lao, rồi quyết cuối bằng điểm gộp 495 dòng với hai ngưỡng như trên (chữ ASR fine-tune so với 46,17; chữ chuẩn so với điểm gộp của 4B chữ chuẩn). Qua bước này thì chữ trộn thành công thức cho lượt train lại trên đủ train.
      - **Không qua:** bỏ chữ trộn; train lại công thức hiện tại trên đủ 1.545 mẫu.
    - **Colab:**
      - **Colab miễn phí không dùng được để train agent.** Colab miễn phí cấp GPU T4. Entry 46 đã đo trên Kaggle T4 (cùng loại GPU): train 1.7B chậm gần 9 lần laptop, khoảng 22,5 giờ mỗi epoch, vì T4 không có bf16. 4B còn chậm hơn, không xong kịp sáng mai, và Colab miễn phí còn cắt phiên khi lâu không tương tác.
      - **Colab trả phí** có thể cấp L4 hoặc A100 (có bf16), nhưng không đảm bảo lúc nào cũng có. Giá theo nguồn bên thứ ba: khoảng 10 USD cho 100 đơn vị tính; mức tiêu mỗi giờ của từng loại GPU giữa các nguồn không khớp nhau. Đây là tiền riêng của Anh, không tính vào trần 30 USD cho API.
      - **Khuyến nghị: đêm nay chưa cần thuê.** Lượt song song có ích nhất là cùng công thức trên fit_lao, nhưng lượt đó chỉ có giá trị khi cửa 1 qua. Còn 13 đêm tới hạn Docker; cái thiếu là một công thức thắng, không phải giờ GPU.
      - **Chỗ Colab trả phí có giá trị riêng** là chiến lược 3, phần laptop 8 GB không làm được: so nạp bf16 với 4-bit trên GPU 24 GB (L4 cùng cỡ bộ nhớ với A30 của BTC) và đo thời gian mỗi mẫu. Việc này khoảng 1–2 giờ GPU, làm ban ngày được (HUMAN_TODO B16).
    - **Danh sách chiến lược hiện tại** (thứ tự như entry 63): (1) 4B học chữ trộn: đang chạy; (2) train lại công thức thắng trên đủ 1.545 mẫu, rồi nộp public làm mốc; (3) sẵn sàng Docker. Không đề xuất lúc này: sinh thêm dữ liệu bằng API, 2 epoch, đổi ASR, LLM lớn hơn (lý do ở entry 63).

65. **Anh trả lời B16: chưa cần Colab trả phí; laptop khởi động lại lúc 00:37 làm dừng train, đã chạy tiếp** (03/11, 00:52–00:54).
    - **B16:** Anh chọn "Chưa cần". Việc so nạp bf16 với 4-bit và đo thời gian trên GPU 24 GB vẫn mở, làm sau.
    - **Lượt chữ trộn bị dừng ở bước 10:** lúc 00:37:21 máy nhận lệnh khởi động lại thường ("The system will reboot now!" của systemd-logind), không phải crash hay hết bộ nhớ. Unit nhận SIGTERM; bản lưu gần nhất là bước 10 (00:32), nên chỉ mất vài phút train. Lỗi cấp bộ nhớ GPU cho màn hình (`Failed to allocate NVKMS memory`) có lúc 00:33, nhưng lỗi này cũng có trong các lượt 4B trước mà máy không khởi động lại.
    - **Chạy tiếp lúc 00:53** từ bước 10/260 (`resumed from ... at step 10/260`). Dự kiến train xong khoảng 06:10, chấm xong khoảng 07:25.

66. **Anh hỏi: train và chấm xong thì Claude định làm gì** (03/11, 01:05). Lượt đêm nay chấm trên **dev_random**, không phải dev_lao; dev_lao là bước sau nếu qua cửa 1. Kế hoạch theo luật đặt trước ở entry 64:
    - **Khoảng 07:25, đọc kết quả cửa 1** (dev_random, so theo cặp với 4B học chữ chuẩn): điểm chữ ASR fine-tune và chữ chuẩn, khoảng tin cậy 95%, số mẫu tốt hơn / kém hơn, theo loại mẫu (execute, hỏi lại, ngoài phạm vi), giây mỗi mẫu. Ghi vào JOURNAL và HUMAN_TODO.
    - **Nếu qua cửa 1** (chữ ASR tăng ≥ 1,0 và chữ chuẩn giảm ≤ 2,0):
      1. Chạy cùng công thức trên fit_lao → dev_lao, khoảng 6,8 giờ laptop (train 4.051 dòng, chấm 262 mẫu); dừng và chạy tiếp được nếu Anh mang máy đi.
      2. Quyết cuối bằng điểm gộp 495 dòng, cùng hai ngưỡng (chữ ASR so với 46,17).
      3. Qua → thêm cờ `--asr-frac` vào `sft.py` qua PR (để bản train đủ dữ liệu dựng lại được), rồi train lại trên đủ 1.545 mẫu.
    - **Nếu không qua:** bỏ chữ trộn, train lại công thức hiện tại trên đủ 1.545 mẫu (thêm 233 mẫu so với adapter `q4b4_fit_random` đã cho 45,39), khoảng 6,5 giờ.
    - **Sau bước train lại, theo cả hai nhánh:** không còn dev để chấm, nên chỉ kiểm loss, định dạng và vài mẫu; làm file nộp public (khoảng 1,5–2 giờ laptop); Anh hoặc leader nộp làm mốc "4B trên đủ dữ liệu train".
    - **Việc không cần GPU, làm song song ban ngày:** PR thêm `--load-4bit`, bước khởi động và hạn dưới 30 giây vào `predict.sh` / `eval_ckpt.sh` / `train_local.sh` cho Docker (đề xuất từ entry 58, chưa làm).
    - **Ước tính lịch:** nhánh không qua có file nộp mới khoảng 04–05/11; nhánh qua thêm khoảng 2 ngày (lượt fit_lao rồi lượt train lại), khoảng 06–07/11. Cả hai còn hơn một tuần cho Docker trước 16/11.

67. **Lượt chữ trộn qua cửa 1 trên dev_random; laptop chạy tiếp trên fit_lao** (03/11; chấm xong 07:30, Claude đọc lúc 08:51 khi Anh hỏi "tới đâu rồi"; lượt fit_lao bắt đầu 08:54).
    - **Train:** xong 06:09, 260 bước. Loss cuối 0,025; dev loss 0,0517 (bản chữ chuẩn 0,0503).
    - **Kết quả dev_random (233 mẫu)**, so theo cặp với 4B học chữ chuẩn:

      | Chữ đầu vào | 4B chữ chuẩn | 4B chữ trộn | Chênh [95% CI] | tốt hơn / kém hơn / như nhau |
      |---|---:|---:|---|---|
      | Whisper-turbo fine-tune | 54,01 | **56,32** | **+2,31** [−2,52; +7,08] | 29 / 22 / 182 |
      | Chữ chuẩn | 65,61 | 66,05 | +0,43 [−4,73; +5,58] | 27 / 27 / 179 |

    - **Cửa 1 qua:** chữ ASR tăng 2,31 (ngưỡng ≥ 1,0), chữ chuẩn không giảm (ngưỡng: giảm không quá 2,0). Khoảng tin cậy vẫn chứa 0, nên đây mới là điều kiện để chạy bước sau, chưa phải bằng chứng. Luật đặt trước quyết bằng điểm gộp 495 dòng.
    - **Theo loại mẫu** (chênh, khoảng tin cậy 95% bootstrap theo cặp):
      - execute (183 mẫu): chữ ASR +4,8 [−0,4; +10,2]; chữ chuẩn +2,2 [−3,6; +7,9]. Phần tăng nằm ở đây.
      - Hỏi lại (`ask_missing`, 33 mẫu): chữ ASR −7,4 [−21,2; +6,5]; chữ chuẩn −9,1 [−22,7; +3,0]. Giảm ở cả hai loại chữ (6 và 5 mẫu kém hơn; 3 và 2 mẫu tốt hơn). Ít mẫu nên chưa chắc, nhưng cần theo dõi trên dev_lao.
      - Ngoài phạm vi (17 mẫu): chữ ASR −5,9 (1 tốt hơn, 2 kém hơn); chữ chuẩn không đổi.
    - **Giây mỗi mẫu** (laptop, nạp 4-bit, hạn 60 giây):
      - Chữ ASR: trung bình 8,34, p95 16,81, tối đa 27,34. Bản chữ chuẩn: 9,03 / 17,41 / 110,12.
      - Chữ chuẩn: 8,59 / 17,67 / 62,43.
      - Thời gian trên A30 vẫn chưa đo (B16 để sau).
    - **Bước tiếp theo theo luật: cùng cách trộn trên fit_lao → dev_lao. Laptop chạy từ 08:54** (`q4b4_fit_lao_mix50`; unit `lifemate-q4b-lao-mix`; script `~/zac-c3/run_q4b_lao_mix.sh`).
      - Dữ liệu: dựng `sft/fit_lao_q4b_lao_asrtrain.jsonl` từ `asr/train_all_turbo.jsonl` (Whisper-turbo chưa fine-tune), cùng code `sft.py` (sha 17c606b9) và cùng tham số với `sft/fit_lao.jsonl`.
      - Đã kiểm khớp từng dòng: 4.051 dòng, cùng id và augmentation, 0 dòng lệch phần model học.
      - 641/1.283 mẫu (chọn bằng `random.Random(0)`) dùng chữ turbo, tổng 2.038/4.051 dòng.
      - Công thức giữ nguyên `q4b4_fit_lao`: 254 bước, bỏ 1 ví dụ quá dài như bản cũ. Dự kiến train xong khoảng 14:20, chấm dev_lao xong khoảng 15:40 (bản cũ: train 5,4 giờ, chấm 1,3 giờ).
    - **Quyết cuối** (luật entry 64, không đổi): điểm gộp 495 dòng, chữ ASR fine-tune tăng ít nhất 1,0 so với 46,17, **và** chữ chuẩn không giảm quá 2,0 so với 59,15. 59,15 là điểm gộp của 4B học chữ chuẩn, tính lúc 08:52. Script tự in PASS/FAIL vào log và `runs/q4b4_mix50_pooled_2026-11-03.json`.
    - Để tham khảo: nếu dev_lao giữ nguyên như bản cũ, riêng phần dev_random cho điểm gộp chữ ASR +1,09 [−1,15; +3,33]. Vậy dev_lao chỉ cần không giảm là qua ngưỡng chữ ASR.
    - Cần mang máy đi: `systemctl --user stop lifemate-q4b-lao-mix`, đợi 1–3 phút rồi gập máy. Về chạy `bash ~/zac-c3/start_q4b_lao_mix.sh` là tiếp từ chỗ dừng.

68. **Chữ trộn không qua luật gộp: dev_lao chữ ASR giảm 3,35; bỏ chữ trộn** (03/11; chấm chữ ASR xong 14:51, Claude đọc lúc 15:04 khi Anh hỏi "tiến trình hiện tại tới đâu rồi").
    - **Train trên fit_lao:** xong 14:15, 254 bước, không bị dừng. Loss cuối 0,029; dev loss 0,1142 (bản chữ chuẩn 0,1074).
    - **dev_lao (262 mẫu), chữ Whisper-turbo fine-tune**, so theo cặp với 4B học chữ chuẩn: 39,20 → **35,85**, **−3,35** [−8,46; +1,77]. Tốt hơn / kém hơn / như nhau: 33 / 46 / 183.
      - execute (214 mẫu): −2,3 [−7,6; +3,0].
      - Hỏi lại (`ask_missing`, 41 mẫu): −12,0 [−27,7; +3,5]; 6 mẫu tốt hơn, 13 mẫu kém hơn.
      - Ngoài phạm vi (7 mẫu): +14,3; 1 mẫu tốt hơn.
    - **Điểm gộp 495 dòng, chữ ASR fine-tune:** 46,17 → 45,49, **−0,69** [−4,24; +2,74]. Ngưỡng là +1,0, nên **luật đặt trước không qua**. Luật cần cả hai điều kiện, nên kết quả chữ chuẩn trên dev_lao không đổi được kết luận. Phần chữ chuẩn đang chấm, xong khoảng 15:30, vẫn ghi lại cho đủ báo cáo.
    - **Đọc kết quả:**
      - Phần tăng ở dev_random (app đã thấy khi train) không lặp lại trên dev_lao (app chưa thấy).
      - Tín hiệu nhất quán nhất là mẫu hỏi lại giảm ở cả hai dev: dev_random −7,4 (chữ ASR) và −9,1 (chữ chuẩn); dev_lao −12,0 (chữ ASR). Từng phần đều ít mẫu và khoảng tin cậy chứa 0. Nguyên nhân chưa kiểm; giả thuyết: chữ turbo nhiễu làm model khó nhận ra khi nào thật sự thiếu thông tin.
    - **Bước tiếp theo theo kế hoạch ở entry 66: bỏ chữ trộn; train lại công thức 4B chữ chuẩn trên đủ 1.545 mẫu, rồi làm file nộp public.**
      - Đã chuẩn bị, **chưa bật**: script `~/zac-c3/run_q4b_all.sh`, lệnh bật `bash ~/zac-c3/start_q4b_all.sh`, unit `lifemate-q4b-all`. Script tự chờ lượt chấm dev_lao xong rồi mới chạy.
      - Dữ liệu `sft/all_q4b.jsonl` (dựng lúc 15:05): 1.545 mẫu (fit_random + dev_random), không bỏ app nào. Cùng code `sft.py` (sha 17c606b9) và tham số augmentation như các bản trước; 4.874 dòng, khoảng 305 bước. Cờ train giống hệt `q4b4_fit_random`.
      - Không còn dev để chấm, nên chỉ kiểm loss và định dạng file nộp. File nộp dùng cùng chữ ASR fine-tune với bản 45,39, chỉ đổi adapter: `runs/e2e_public_q4b_all.jsonl`.
      - Thời gian: train khoảng 6,3 giờ, file nộp khoảng 1,7 giờ, tổng khoảng 8 giờ laptop. Bật lúc khoảng 15:30 thì xong khoảng 23:30.
      - Chờ Anh chọn bật ngay hay để sau (HUMAN_TODO B17), vì máy sẽ bận tới khuya.

69. **Anh trả lời B17: tự bật lượt train lại sau** (03/11, 15:11; Anh chọn "I'll start it later").
    - Claude không bật `lifemate-q4b-all`. Script và dữ liệu vẫn sẵn; lệnh bật: `bash ~/zac-c3/start_q4b_all.sh`. Nếu lượt chấm dev_lao còn chạy, script tự chờ nó xong.
    - Lượt train cần khoảng 8 giờ laptop (train 6,3 giờ, file nộp 1,7 giờ), dừng và chạy tiếp được.
    - Laptop rảnh sau khi lượt chấm dev_lao bằng chữ chuẩn xong (khoảng 15:30).

70. **Lượt chữ trộn chấm xong hết; luật gộp in FAIL; laptop rảnh** (03/11, 15:27; Claude ghi lúc 15:27, không có câu hỏi mới của Anh).
    - **dev_lao, chữ chuẩn**, so theo cặp với 4B học chữ chuẩn: 53,40 → **49,97**, **−3,44** [−7,98; +1,12]. Tốt hơn / kém hơn / như nhau: 26 / 39 / 197.
      - execute (214 mẫu): −2,3 [−7,0; +2,9].
      - Hỏi lại (41 mẫu): −10,2 [−24,0; +3,3]; 3 mẫu tốt hơn, 8 mẫu kém hơn.
      - Ngoài phạm vi (7 mẫu): không đổi.
    - **Điểm gộp 495 dòng** (`runs/q4b4_mix50_pooled_2026-11-03.json`):

      | Chữ đầu vào | 4B chữ chuẩn | 4B chữ trộn | Chênh [95% CI] | Ngưỡng |
      |---|---:|---:|---|---|
      | Whisper-turbo fine-tune | 46,17 | 45,49 | −0,69 [−4,24; +2,74] | ≥ +1,0: **không đạt** |
      | Chữ chuẩn | 59,15 | 57,54 | −1,62 [−5,06; +1,78] | ≥ −2,0: đạt |

      Script in `RULE FAIL`, khớp kết luận ở entry 68.
    - **Hỏi lại giảm ở cả bốn phép so:** dev_random −7,4 (chữ ASR) và −9,1 (chữ chuẩn); dev_lao −12,0 và −10,2. Đây là điểm cần nhớ nếu sau này thử lại kiểu train trên chữ ASR.
    - **Giây mỗi mẫu trên dev_lao** (laptop, nạp 4-bit, hạn 60 giây): chữ ASR trung bình 8,12, p95 14,31, tối đa 26,54; chữ chuẩn 8,03 / 14,15 / 26,95. Ngang bản cũ.
    - **Laptop rảnh từ 15:27.** Lượt train lại trên đủ 1.545 mẫu chưa bật: Anh tự bật (B17), lệnh `bash ~/zac-c3/start_q4b_all.sh`.

71. **Anh hỏi: lượt train vừa rồi cho biết điều gì mà phải train thêm lần nữa?** (03/11, 15:48).
    - **Lượt chữ trộn cho biết:**
      - Học trên chữ ASR nhiễu giúp một chút với app đã thấy (dev_random chữ ASR +2,31), nhưng làm kém đi với app chưa thấy (dev_lao chữ ASR −3,35, chữ chuẩn −3,44). Public_test có 11 app không có trong train, nên cách này nhiều khả năng làm giảm điểm public.
      - Phần bị hại rõ nhất là hỏi lại khi thiếu thông tin: giảm ở cả bốn phép so (−7,4 / −9,1 / −12,0 / −10,2).
      - Kết luận: giữ công thức hiện tại (học chữ chuẩn). Adapter cho 45,39 vẫn là bản tốt nhất đã biết. Lượt này tránh được một lần nộp public và một lượt train đủ dữ liệu bằng công thức kém hơn.
    - **Lượt train lại không phải do lượt chữ trộn**, mà là bước cuối đã định cho cả hai nhánh (entry 63, mục 2; entry 66):
      - Adapter 45,39 học trên 1.312/1.545 mẫu; 233 mẫu dev_random được giữ lại chỉ để chấm khi còn chọn công thức. Nay đã chốt công thức, không cần giữ lại nữa; model cuối cho Docker nên học trên đủ dữ liệu (thêm khoảng 18%).
      - 233 mẫu này thuộc các app đã có trong fit_random, không thêm app mới. Nên lợi ích dự kiến nhỏ, và không đo được trên dev vì không còn dev. Chỉ điểm public cho biết; chênh 1–2 điểm trên 634 mẫu public có thể chỉ là nhiễu.
      - Rủi ro thấp vì cùng công thức. Nếu điểm public thấp hơn rõ so với 45,39 thì giữ adapter cũ cho Docker.
      - Không bắt buộc: bỏ qua thì Docker dùng adapter 45,39. Chi phí là khoảng 8 giờ laptop; hợp nhất là chạy qua đêm, ban ngày làm phần sẵn sàng Docker (bước khởi động, hạn dưới 30 giây, cờ 4-bit), phần này quan trọng hơn cho hạn 16/11.

72. **Anh mang laptop đi tối nay; nhờ hẹn lượt train lại lúc 00:30 và làm trước các việc không cần kết quả train** (03/11, khoảng 16:08; Claude xong lúc 16:27).
    - **Hẹn giờ (B17 xong):** timer `lifemate-q4b-all-kick.timer` (file trong `~/.config/systemd/user/`, đã enable) chạy một lần lúc **00:30 ngày 04/11**, gọi `~/zac-c3/kick_q4b_all.sh`.
      - Script chỉ bật khi máy đang cắm sạc. Nếu đang chạy pin, nó kiểm lại mỗi phút và bật ngay khi cắm sạc, để không train 8 giờ bằng pin.
      - Rồi gọi `start_q4b_all.sh` như cũ (unit `lifemate-q4b-all`, giới hạn RAM 7–9 GB, chặn ngủ khi rảnh): train khoảng 6,3 giờ, rồi file nộp public khoảng 1,7 giờ. Bắt đầu 00:30 thì xong khoảng 08:30–09:00.
      - Timer có `Persistent=true`: nếu lúc 00:30 máy tắt hay ngủ, nó chạy ngay khi máy bật lại và Anh đăng nhập. Gập máy (ngủ) lúc 00:30 thì lượt chờ tới khi mở máy.
      - Đã thử: một user service gọi được `systemd-run --user`, và kiểm cắm sạc đúng (máy đang cắm, `ACAD` online).
      - Huỷ hẹn: `systemctl --user disable --now lifemate-q4b-all-kick.timer`. Dừng khi đang chạy: `systemctl --user stop lifemate-q4b-all`.
    - **Sẵn sàng Docker ([PR #12](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/12), nhánh `docker-ready` xếp chồng lên #10, worktree `~/zac-docker`):**
      - **Bước khởi động không tính giờ** (`infer.py`, `agent.py`): sau khi nạp model, sinh một lần trên prompt dài như thật, gồm system prompt dựng chỉ từ `context` của mẫu đầu cộng câu "Xin chào.". Không dùng audio, chữ, history hay nhãn, không tạo `ToolEnv`. `--no-warmup` để bỏ; thời gian ghi vào meta (`warmup_s`).
      - **`predict.sh`** mặc định theo hệ thống hiện tại: Qwen3-4B-Instruct-2507 nạp 4-bit, hạn 25 giây (tính cả ASR), có khởi động; từ chối hạn từ 30 giây trở lên. `eval_ckpt.sh` và `train_local.sh` thêm `LOAD_4BIT`, `TIME_BUDGET`.
      - **Test CPU:** `test_agent` 16/16 (2 test mới), `test_scorer` 11/11, `test_asr` 8/8, `test_counterfactual` 22/22, `test_asr_train` 6/6.
      - **Thử GPU** (16:14–16:25, `q4b4_fit_random/final`, 4-bit):
        - 4 mẫu đầu dev_random, chữ ASR, hạn 25 giây: mẫu đầu `train_0003` từ 110,1 giây (hết giờ sau 1 bước) xuống **13,0 giây** (chạy hết 3 bước). Điểm mẫu này vẫn 0; 3 mẫu còn lại giống hệt lượt cũ. Khởi động mất 4,8 giây.
        - `predict.sh` đầu-cuối trên 3 mẫu public_test: chữ ASR giống từng ký tự file ASR của lần nộp 45,39, 3 dòng nộp giống hệt `runs/e2e_public_q4b.jsonl`, `check_submission` đạt. Khởi động lần này mất 66 giây vì laptop thiếu RAM; không có bước khởi động thì 66 giây đó rơi vào mẫu đầu.
      - **Phát hiện phụ:** trên laptop, `lifemate.infer` có lúc mất vài phút mới thoát sau khi ghi xong file, khi unit chạm giới hạn RAM 7 GB (tiến trình chờ đọc lại trang nhớ). Lượt đêm 03/11 cũng gặp một lần (xong 07:20:52, chấm 07:30:32), nên không do PR này. Không ảnh hưởng file nộp hay giây mỗi mẫu.
      - **Chưa làm:** đo trên GPU 24 GB (giây mỗi mẫu; bf16 + gộp adapter so với 4-bit, B16 để sau); Dockerfile và đường dẫn BTC (`/data` → `result/submission.jsonl`), phần của leader (L6).
    - Lượt 00:30 chạy code đang có ở `~/zac-c3` (9de4e1a, chưa có bước khởi động, hạn 60 giây như các lượt trước). Như vậy file nộp mới so được thẳng với bản 45,39: chỉ adapter khác.

73. **Anh nhờ Claude tự review [PR #12](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/12) và merge nếu đạt; đã merge** (03/11; Anh: "review the PR yourself and merge if it satisfy"; merge lúc 17:22).
    - **Quyền merge:** Anh cho phép cho riêng PR này. Quy tắc chung vẫn giữ: Claude không merge PR khi chưa được Anh cho phép.
    - **Đã kiểm khi review:**
      - Merge chỉ đổi 6 file code (`agent.py`, `infer.py`, `test_agent.py`, `predict.sh`, `eval_ckpt.sh`, `train_local.sh`); tài liệu hai nhánh đã giống nhau.
      - Đọc lại từng thay đổi: bước khởi động chỉ dùng `context` của mẫu đầu và câu cố định, không tạo `ToolEnv`, không đọc `<split>_environment/`.
      - shellcheck: 0 cảnh báo trước và sau.
      - Chạy ba script với một python giả chỉ ghi lại tham số:
        - Mặc định của `eval_ckpt.sh` và `train_local.sh` cho đúng lệnh như trước.
        - `LOAD_4BIT=1` thêm `--load-4bit` (train thêm `--optim adamw8bit`) và tắt bước loss.
        - `predict.sh` từ chối hạn từ 30 giây trở lên, và từ chối `LOAD_4BIT`, `WARMUP` sai.
      - Test trên commit được merge (`d444f91`): `test_agent` 16/16, `test_scorer` 11/11, `test_asr` 8/8, `test_counterfactual` 22/22, `test_asr_train` 6/6.
      - Lượt thử GPU ở entry 72 vẫn đúng cho commit này: code giống hệt, chỉ thêm commit tài liệu.
      - Không xung đột với PR #11 (`synth-data`, cùng nhắm vào `q4b-laptop`).
    - **Ghi chú, không chặn merge:**
      - Với `--backend openai` kèm `--assistant-prefix`, meta ghi `warmup_s` gần 0 dù không có gì được khởi động. Đây là đường chỉ dùng khi dev.
      - `VLLMBackend.warmup` chưa chạy thử: máy này không cài vLLM, và Docker hiện dùng backend HF.
    - **Merge kiểu merge commit** vào `q4b-laptop` (commit `a2615ee`, ghi lại phần review), giữ đúng commit đã review (`--match-head-commit`). Nhánh `docker-ready` không còn trong danh sách đồng bộ tài liệu; worktree `~/zac-docker` chuyển sang `origin/q4b-laptop`.
    - **Vị trí code:** `q4b-laptop` nằm trong chuỗi PR #8 → … → #9 → #10, nên phần này tới `main` khi chuỗi đó được merge. Leader đóng Docker nên lấy từ `q4b-laptop` (HUMAN_TODO L6).
    - Lượt train lại lúc 00:30 không bị ảnh hưởng, vì nó chạy code ở `~/zac-c3` (9de4e1a).

74. **Anh bảo chạy train ngay; lượt train lại trên đủ 1.545 mẫu bắt đầu lúc 00:13** (04/11; Anh: "bây giờ chạy training đi", lúc khoảng 00:13).
    - Lúc đó là 00:13, hẹn giờ 00:30 chưa chạy, máy đang cắm sạc (`ACAD` online, pin 100%). Máy vừa bật lại khoảng 00:06.
    - Claude **tắt hẹn giờ** (`systemctl --user disable --now lifemate-q4b-all-kick.timer`) để khỏi chạy lần hai, rồi bật `bash ~/zac-c3/start_q4b_all.sh`. Unit `lifemate-q4b-all`, code `~/zac-c3` (9de4e1a), công thức như entry 68.
    - Log đầu: dữ liệu dùng lại `sft/all_q4b.jsonl` (đúng manifest: 1.545 mẫu, 4.874 dòng). Train có 4.868 ví dụ: **6 ví dụ dài quá 6.144 token bị bỏ** (0,1%), cùng luật `--max-len 6144` như các lượt 4B trước (fit_random bỏ 0, fit_lao bỏ 1). Không có dev (dev 0).
    - **Dự kiến:** 305 bước, khoảng 6,3 giờ, train xong khoảng 06:35. Sau đó file nộp public 634 mẫu khoảng 1,7 giờ, xong khoảng 08:20–08:45. Kết quả: `runs/e2e_public_q4b_all.jsonl` kèm `_check.json`; Anh hoặc leader nộp.
    - Cần mang máy đi giữa chừng: `systemctl --user stop lifemate-q4b-all`, đợi 1–3 phút rồi gập máy. Về chạy `bash ~/zac-c3/start_q4b_all.sh` là tiếp từ chỗ dừng. Bước làm file nộp chạy lại từ mẫu đầu nếu bị dừng giữa chừng.
    - Lần khởi động lại máy tối 03/11 xoá `/tmp`, nên script đồng bộ tài liệu sang các nhánh được viết lại, cùng cách làm.
    - **00:26, bước 10/305:** loss 0,31, 695 token/giây, đỉnh 5,46 GB, đã lưu `state.pt`. Cùng nhịp các lượt 4B trước. Dự kiến train xong khoảng 06:25.
75. **Train lại xong; file nộp public mới sẵn sàng** (04/11; Anh hỏi "sao r" lúc 07:53).
    - **Train:** xong 06:03, đủ 305/305 bước trong 349 phút, không bị dừng. Loss cuối 0,016 (bước 10: 0,31). Đỉnh 5,56 GB, 749 token/giây. Không có dev nên chỉ xem được loss. Adapter: `ckpt/q4b4_all/final`, kèm `step_100`, `step_200`, `step_300`.
    - **File nộp:** `~/zac-c3/lifemate/runs/e2e_public_q4b_all.jsonl`, xong 07:34. 634 dòng, id khớp, `zaic_tools --validate` 0 lỗi, sha256 `483fecf54c75…`. Cùng chữ ASR fine-tune với bản 45,39, chỉ đổi adapter.
    - **So với bản 45,39** (`e2e_public_q4b.jsonl`):
      - 277/634 dòng giống hệt, 357 dòng khác.
      - Tổng call 1.452 → 1.507; dòng rỗng (không gọi tool) 54 → 53.
      - Cách dừng: 521 xong, 90 hỏi lại, 23 chạy hết 8 bước.
    - **Thời gian trên laptop** (hạn 60 giây, không phải A30): mỗi mẫu trung bình 9,1 giây, p95 18,7 giây, chậm nhất 44,0 giây. 5 mẫu quá 30 giây (bản cũ: 2), đều do chạy hết 8 bước. Bản Docker đặt hạn 25 giây (PR #12) nên các mẫu này sẽ bị cắt. Mẫu đầu 9,9 giây.
    - **Cách quyết, ghi trước khi có điểm:** điểm public của file mới từ 44,39 trở lên (không kém 45,39 quá 1 điểm) thì Docker dùng `ckpt/q4b4_all/final`, vì học thêm 233 mẫu (dev_random, dev_lao). Kém hơn 1 điểm thì giữ adapter cũ `ckpt/q4b4_fit_random/final`. Ngưỡng 1 điểm vì đây chỉ là một lần nộp: nhiễu public lớn hơn mức chênh dự kiến.
    - Laptop rảnh từ 07:34. Unit `lifemate-q4b-all` đã kết thúc; hẹn giờ vẫn tắt.
76. **Điểm public lần 4: 46,29; chốt adapter mới cho Docker** (04/11; Anh báo lúc khoảng 12:21: "đây là kết quả sau khi nộp: 46.29000").
    - File nộp: `runs/e2e_public_q4b_all.jsonl` (entry 75). So với lần 3 (45,39, cùng chữ ASR, adapter học 1.312 mẫu): **+0,90**.
    - Các lần nộp: 35,24 (1.7B) → 45,39 (4B) → **46,29** (4B học đủ 1.545 mẫu).
    - **Theo luật ghi trước ở entry 75** (từ 44,39 trở lên thì dùng adapter mới): **Docker dùng `ckpt/q4b4_all/final`**. Mức tăng 0,90 là một lần nộp nên chưa chắc, nhưng không cần chắc mới chọn: luật chỉ cần adapter mới không kém rõ.
    - Adapter: `~/zac-c3/lifemate/ckpt/q4b4_all/final`, 263 MB (`adapter_model.safetensors` kèm tokenizer). Không commit (repo public); Anh gửi riêng cho leader.
    - Lệnh trong Docker: `ADAPTER=ckpt/q4b4_all/final`. Dòng ví dụ ở đầu `predict.sh` vẫn ghi `ckpt/q4b4_fit_random/final`; script bắt buộc truyền `ADAPTER` nên không ảnh hưởng, sửa khi có PR code tiếp theo.
77. **File nộp public bằng Meta API (cột APIs/Others), để biết pipeline này đạt tới đâu khi có model mạnh** (04/11; Anh gửi ảnh bảng xếp hạng public lúc khoảng 12:25: "bây giờ tôi muốn bạn thử cho tôi một file kết quả sử dụng Meta API được không để tôi xem điểm tốt nhất có thể đạt được với baseline này. Thêm vào đó, anh tôi cũng đang bắt đầu training rồi").
    - **Bảng xếp hạng public:** có 3 cột SLM (dưới 6B), LLM (từ 6B), APIs/Others. Chỉ cột SLM tính hạng. Top 4 cột SLM lúc Anh chụp: 96,66; 96,58; 96,25; 95,74. Đội mình 46,29, cách top khoảng 50 điểm.
    - **Anh trai Anh đã bắt đầu train** (Anh báo, chưa rõ cấu hình). Chờ kết quả cho C5.
    - **Code:** [PR #13](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/13) (nhánh `api-agent`, nhắm vào `q4b-laptop`). Thêm `--backend api`: gửi đúng prompt của agent tới Meta Model API dưới dạng tin nhắn chat, đọc `<tool_call>` như thường.
      - Cùng chữ ASR (Whisper-turbo fine-tune), cùng prompt, vòng lặp, chốt chặn ID và kiểm schema như 4B; chỉ khác model.
      - Trần chi riêng mỗi lượt và trần tổng 30 USD trên mọi sổ chi trong `gen/`. Câu trả lời được lưu lại nên chạy lại không tốn thêm. Không dùng gói contributor.
      - Test mới 5/5 (server giả, không gọi API thật); `test_agent` vẫn đạt. Chưa merge, chờ Anh.
    - **Thử trên 40 mẫu dev_random + 40 mẫu dev_lao** (chọn ngẫu nhiên, seed 0; chữ ASR fine-tune), so với 4B trên đúng các mẫu đó:

      | | dev_random 40 | dev_lao 40 | Gộp | Chi |
      |---|---|---|---|---|
      | 4B (adapter fit_random / fit_lao) | 51,04 | 27,16 | 39,10 | – |
      | `muse-spark-1.3`, suy nghĩ `minimal` | 46,79 | 53,80 | 50,29 | 0,82 USD |
      | `muse-spark-1.3`, suy nghĩ `low` | 48,21 | 55,65 | 51,93 | 1,01 USD |

      - Model API hơn 4B rất nhiều trên app chưa thấy (dev_lao +26,6), nhưng kém nhẹ trên app đã thấy (dev_random −4,3). Public có 410/634 mẫu cài app không có trong train, nên bản API có thể cao hơn 46,29.
      - Mẫu nhỏ (40 mỗi bên), nên các con số trên chỉ cho biết xu hướng.
      - Luật chọn ghi trước lượt `low`: lấy điểm gộp cao hơn; nếu cách nhau dưới 2 điểm thì lấy `minimal` vì rẻ hơn. `low` hơn 1,64, nên **dùng `minimal`**.
      - Mỗi bước gửi trung bình khoảng 2.800 token, khoảng 1.060 token trong đó được API cache. Sổ chi vẫn tính đủ giá, nên số tiền ghi có thể cao hơn thực tế.
    - **File public:** `~/zac-docker/lifemate/runs/e2e_public_api_spark_min.jsonl`, 634 dòng, `zaic_tools --validate` 0 lỗi, sha256 `0d264ca094e8…`.
      - 1.666 lần gọi API, 6,75 USD, không lần nào lỗi hay bị chặn vì trần.
      - Mỗi mẫu trung bình 6,2 giây (gọi song song 8 mẫu).
      - Cách dừng: 480 xong, 154 hỏi lại (4B: 90). Dòng rỗng 33 (4B: 53).
      - Chỉ 119/634 dòng giống hệt bản 46,29.
    - **Tổng API đã chi: 21,15 / 30 USD** (sinh dữ liệu 12,57; thử dev 1,83; public 6,75).
    - **Lưu ý khi nộp:** chọn đúng loại APIs/Others để bài này không bị tính vào cột SLM. Kết quả trên public_test không bao giờ dùng để train (không gán nhãn giả). Docker vẫn dùng 4B offline.
78. **Bản Meta API được 69,47; baseline có vấn đề không?** (04/11; Anh lúc khoảng 12:50: "tôi đã submit và được 69.47000 điểm ... ngay cả dùng model API bên thứ 3 còn không lên nổi trên 90 thì làm sao mà model 4B chúng ta đang làm có thể vượt trần được? Có phải baseline của chúng ta có vấn đề không?").
    - **Điểm public:** bản API (`muse-spark-1.3`, cột APIs/Others) **69,47**; bản 4B 46,29. Top cột SLM lúc Anh chụp: 96,66.
    - **Bộ chấm local vẫn khớp public:** 4B dev gộp 46,17 → public 45,39 và 46,29. Bản API thử trên 80 mẫu dev được 50,29, lên public 69,47. Mức chênh này hợp lý vì 410/634 mẫu public có app chưa thấy, đúng chỗ API hơn 4B nhiều (dev_lao +26,6). Không thấy dấu hiệu bộ chấm hay định dạng nộp sai.
    - **Phân tích mất điểm** (script tạm trong scratchpad, chưa đưa vào repo; chỉ dùng train):
      - **Model API: thiếu quy ước của nhãn.** Trên dev_random, 33 điểm mất ở mẫu **trạng thái cuối đúng** nhưng call không khớp. Lý do chính là model điền thêm tham số tuỳ chọn mà nhãn không có. Trong nhãn train (bỏ id dev): `alarm.create.repeat` có mặt 0/193 lần, `color` 0/126, `label` 2/92, `note` 3/115.
        - Thử luật "bỏ 23 tham số tuỳ chọn mà nhãn train gần như không dùng (dưới 5%)", chạy lại call trên `ToolEnv` mới (train) rồi chấm lại.
        - Bản API: dev_random 46,79 → 58,33 (+11,54), dev_lao 53,80 → 56,71 (+2,92).
        - 4B: không đổi (−0,2 đến +0,1), vì 4B đã học quy ước này từ dữ liệu.
        - Luật lấy từ thống kê train nên không phủ được 11 app mới của public. Với app mới cần nói rõ quy ước trong prompt.
      - **4B: mất điểm rải ở nhiều chỗ, không phải một lỗi.**

        | 4B, toàn bộ dev | Điểm | Trạng thái đúng |
        |---|---|---|
        | dev_random, chữ chuẩn | 65,61 | 73,0% |
        | dev_random, chữ ASR fine-tune | 54,01 | 63,5% |
        | dev_lao, chữ chuẩn | 53,40 | 66,8% |
        | dev_lao, chữ ASR fine-tune | 39,20 | 51,5% |

        - ASR làm mất 11,6 đến 14,2 điểm.
        - App chưa thấy làm mất khoảng 12 đến 15 điểm.
        - Ngay cả với chữ chuẩn và app đã thấy, trạng thái cuối sai ở 27% mẫu. Lỗi hay gặp: nội dung tin nhắn không đủ giống (fuzzy), sai `from_account_id`, `time`, `query`, thiếu hoặc thừa call đọc.
    - **Về mức 96 của top:** với cách đo hiện có, chưa thấy đường nào tới 96. Chữ chuẩn (không lỗi ASR) cộng 4B chỉ được 59,15 gộp; model API cộng luật quy ước khoảng 58 trên dev. Có thể các đội đó có pipeline tốt hơn hẳn, ví dụ dữ liệu phủ 11 app mới hoặc ASR rất tốt. Cũng có thể bảng public chưa phản ánh đúng: file nộp do đội tự tạo, loại model do đội tự khai, mỗi ngày nộp được 5 lần, và BTC chỉ kiểm bằng Docker trên private. Không kiểm được nên không kết luận.
    - **Việc đáng làm tiếp, theo số đo:**
      - (1) App chưa thấy: 65% mẫu public, 4B kém 12–15 điểm.
      - (2) ASR: 12–14 điểm.
      - (3) Ghi sai khi chữ đã đúng.
      - Luật quy ước chỉ giúp model zero-shot, không giúp 4B.
79. **Anh nâng trần API lên 50 USD; chạy lại bản API với mức suy nghĩ cao hơn** (04/11; Anh lúc khoảng 12:55: "tôi nâng cấp, cho bạn thêm 30usd budget để gọi thêm (tức là tổng budget 50usd) bạn hãy chạy lại cho tôi để tôi xem kết quả tốt nhất nếu tăng effort model lên thì là bao nhiêu điểm ... sao bạn chọn 4B mà không chọn 6B?").
    - **Trần chi:** câu của Anh có cả "thêm 30" lẫn "tổng 50"; Claude dùng con số chặt hơn: **tổng 50 USD** cho mọi lần gọi API (sinh dữ liệu và agent).
    - **Code** (thêm vào [PR #13](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/13)):
      - `lifemate.rare_params` liệt kê các tham số tuỳ chọn mà nhãn train điền dưới 5% (ít nhất 5 call).
      - `infer --drop-params` cho agent bỏ các tham số đó **trước** khi kiểm schema và gọi `env`, nên call đã chạy và bài nộp luôn khớp nhau.
      - Mặc định tắt, vì 4B không cần.
      - Test: `test_agent` 17/17, `test_api_backend` 5/5.
    - **Luật được tính từ:** khi thử trên dev, chỉ dùng 1.087 mẫu train không thuộc dev (23 tham số); khi chạy public, dùng đủ 1.545 mẫu train (30 tham số).
    - **Thử trên 80 mẫu dev** (cùng 40 + 40 mẫu, chữ ASR fine-tune, bỏ tham số hiếm khi chạy):

      | `muse-spark-1.3` | dev_random | dev_lao | Gộp | Chi 80 mẫu |
      |---|---|---|---|---|
      | `minimal` (bản 69,47, không bỏ tham số) | 46,79 | 53,80 | 50,29 | 0,82 USD |
      | `minimal` + bỏ tham số | 57,67 | 58,23 | 57,95 | 0,84 USD |
      | `high` + bỏ tham số | 62,85 | 62,13 | 62,49 | 1,51 USD |
      | `xhigh` + bỏ tham số | 62,44 | 67,06 | **64,75** | 1,92 USD |

      - Luật chọn ghi trước: điểm gộp cao nhất, trừ khi một cấu hình rẻ hơn kém dưới 2 điểm; chi dự kiến cho public cộng 15% phải vừa trần. `xhigh` hơn `high` 2,26 nên **chọn `xhigh`**.
      - Không thử `max` và `muse-wonder-1.0`: ước riêng public đã từ 23 USD trở lên, vượt phần còn lại.
    - **File public:** `~/zac-docker/lifemate/runs/e2e_public_api_spark_xhigh_drop.jsonl`, xong 13:34.
      - 634 dòng, `zaic_tools --validate` 0 lỗi, sha256 `99b2ff9b6656…`.
      - 1.757 lần gọi API, **17,61 USD** (ước 15,2), không lỗi, không bị chặn vì trần.
      - Luật đổi 327 call.
      - Cách dừng: 514 xong, 110 hỏi lại, 10 hết bước.
      - Mỗi mẫu trung bình 19,9 giây, chậm nhất 124,6 giây (không phải đường Docker).
    - **Tổng API đã chi: 43,03 / 50 USD.**
    - **Vì sao 4B mà không 6B:** thể lệ cho LLM **dưới 5B** và cả hệ thống **dưới 6B** (mục 1.3); "SLM < 6B" trên bảng xếp hạng là giới hạn cả hệ thống. Hệ thống hiện tại: Whisper-turbo fine-tune (khoảng 0,8B) + Qwen3-4B (khoảng 4,0B) = khoảng 4,8B. Qwen3-4B là model mạnh nhất họ Qwen3 dưới 5B. Model khác dưới 5B, phát hành trước 26/10/2026, chưa được rà kỹ (mục 4).
    - **Tiếp theo:** Anh nộp loại APIs/Others (B21). Khi có điểm, Claude viết prompt cho Codex để phân tích sâu và phối hợp tìm chiến lược cho 4B (Anh: trên 80 điểm với SLM thì có khả năng đậu).
80. **Bản API `xhigh` được 75,52; viết prompt cho Codex** (04/11; Anh lúc khoảng 13:45: "tôi đẫ submit và được 75.52000 điểm. Viết prompt cho codex ngay bây giờ").
    - **Điểm public, cột APIs/Others:** `minimal` 69,47 → `xhigh` + bỏ tham số hiếm **75,52** (+6,05). Trên 80 mẫu dev mức tăng là +14,46 (50,29 → 64,75); public tăng ít hơn dev. 4B (cột SLM) vẫn 46,29.
    - **Prompt cho Codex:** [`docs/CODEX_4B_STRATEGY_PROMPT_2026-11-04.md`](docs/CODEX_4B_STRATEGY_PROMPT_2026-11-04.md). Anh mở Codex trong `~/Zalo AI Challenge` và gõ: *"Đọc và làm đúng theo `docs/CODEX_4B_STRATEGY_PROMPT_2026-11-04.md`."*
      - **Vai trò:** Codex phân tích trên CPU bằng số liệu sẵn có và đề xuất thí nghiệm kèm luật giữ/bỏ ghi trước. Claude chạy GPU và API theo thứ tự Anh duyệt, và giữ JOURNAL/HUMAN_TODO.
      - **Câu hỏi cho Codex:**
        - Q1: tách chênh lệch API so với 4B (39,10 → 64,75 trên 80 mẫu) theo nguyên nhân.
        - Q2: vì sao 4B kém trên app chưa thấy.
        - Q3: học từ thầy API (distillation), và vì sao pilot dữ liệu sinh thất bại.
        - Q4: model dưới 5B có suy luận, chạy kịp 25 giây.
        - Q5: ASR còn đáng đầu tư không.
        - Q6: luật tất định cho 4B.
        - Q7: đạt 80 public bằng SLM có khả thi không.
      - **Luật an toàn:**
        - Không đổi git ở các thư mục sẵn có; Codex làm trong worktree riêng `~/zac-codex`, nhánh `codex-analysis`, chỉ mở PR nháp.
        - Không GPU, không API.
        - Không đọc `*_environment/`.
        - Không dùng dự đoán public làm dữ liệu train, prompt hay luật.
      - **Sản phẩm:** `docs/research/CODEX_4B_STRATEGY_2026-11-04.md`. Claude đọc, rồi commit lên `main`.
    - **Script:** [PR #13](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/13) thêm `scripts/loss_breakdown.py` (bản sạch của script ở entry 78) để Codex dùng lại.
81. **Codex xong báo cáo chiến lược 4B; Claude review** (04/11; Anh dán tin Codex lúc khoảng 14:38).
    - **Báo cáo:** [`docs/research/CODEX_4B_STRATEGY_2026-11-04.md`](docs/research/CODEX_4B_STRATEGY_2026-11-04.md).
      - Script tái lập ở worktree `~/zac-codex`, nhánh `codex-analysis` (commit `369d269`, chưa push).
      - Codex không dùng GPU hay API, không đọc `*_environment/`, public chỉ đếm tổng hợp.
    - **Kết luận chính của Codex:**
      - **80 public trước 16/11 rất khó.** Theo thước dev, 4B cần khoảng +33,8. ASR hoàn hảo chỉ bù khoảng 13; phần agent còn thiếu khoảng 21.
      - **API hơn 4B +25,65 [+14,43; +36,90] trên 80 mẫu.** Phần lớn chênh lệch nằm ở quyết định làm, hỏi hay bỏ qua (+10,59) và chọn ID từ history hoặc kết quả đọc (+5,00). Đây là gán một nguyên nhân chính cho mỗi mẫu trên n = 80, chỉ mang tính mô tả.
      - **ASR làm 4B mất 12,98 [−16,57; −9,58] trên 495 dòng.**
      - **Luật bỏ tham số hiếm trên 4B:** −0,26 [−0,95; +0,28], không bật. Khử đọc trùng và chuẩn hoá params hỏi lại: 0 thay đổi.
      - **Prompt rút gọn** không in `x-ref` (68 tham số) và `returns` (70 tool).
      - **Qwen3-4B-Thinking-2507** (4,0B, Apache-2.0, 08/2025) hợp lệ về kích thước, nhưng chưa có số đo tốc độ trên A30.
      - **Pilot dữ liệu sinh thất bại vì:** state đúng nhưng call lệch quy ước nhãn, và phân bố lệch (90% mở đầu bằng call đọc).
    - **Đề xuất xếp hạng của Codex:**
      - (1) Prompt `x-ref` + `returns`, train và chạy cùng prompt, trên fit_lao.
      - (2) Chấm 4B với chữ PhoWhisper fine-tune đã có.
      - (3) Thử nhanh model Thinking trên A30.
      - (4) Pilot "thầy" API nhỏ, kiểm cả hash lẫn F1.
      - (5) Đóng Docker và đo trên A30.
    - **Claude kiểm lại:**
      - Số dev, số 80 mẫu, số ASR khớp các file.
      - dev_random và dev_lao **trùng 37 id** (đúng). "495 dòng" là cặp (tập, id), mỗi tập dùng adapter riêng, như cách tính từ trước.
      - **Đề xuất (1) có thể chỉ tăng ít:**
        - `returns` rất ngắn, ví dụ `accounts[]` hay `contacts[]`, chỉ thêm khoảng 5% độ dài prompt hệ thống (8.505 → khoảng 8.900 ký tự).
        - Mô tả tham số ID đã ghi nguồn, ví dụ "ID tài khoản, lấy từ banking.get_balance".
        - Codex cũng tự ước −2 đến +5.
      - **Lệnh làm dữ liệu dev của Codex thiếu** `--rename 0 --p-remove 0 --p-distract 0 --p-lower 0`, nên dữ liệu dev sẽ bị tăng cường. Chỉ ảnh hưởng loss dev; khi chạy sẽ dùng cách của `train_local.sh`. Lệnh fit đúng công thức, vì mặc định của `lifemate.sft` chính là công thức đang dùng.
      - **Không có A30:** B16 (Colab trả phí) Anh đã chọn chưa cần. Đề xuất (3) cần Anh quyết thuê GPU, hoặc nhờ máy anh trai.
    - **Câu hỏi Codex gửi Anh:**
      - Máy anh trai đang train gì?
      - Có nâng trần API nếu pilot thầy cần hơn 6,97 USD không?
      - Nên ưu tiên public hay private, khi chưa biết bao nhiêu mẫu public thật sự **dùng** app mới?
82. **Anh duyệt hai thí nghiệm; trần API lên 80 USD; hẹn lượt `xref` lúc 23:30** (04/11; Anh lúc khoảng 14:43: "Máy anh trai Anh đang train đúng như tin nhắn hồi mấy ngày trước ... Tôi cho phép bạn vượt lên thêm 30usd nữa (cộng thêm vào) nếu thấy cần thiết. 3. Tôi ưu tiên private, nhưng public sẽ là bằng chứng tốt nhất hiện tại ... chiều nay chạy chấm lại như bạn nói, còn setup 11h30 tối nay tự train cái 8.5h").
    - **Trả lời 3 câu hỏi của Codex:**
      - **Máy anh trai** chạy gói v3 (`docs/CLOUD_TRAIN_2026-10-31.md`): 4B và 1.7B trên fit_random/fit_lao, đọc chữ chuẩn và chữ turbo chưa fine-tune, cộng các lượt `asrtrain` và `up` của 1.7B. Hai thí nghiệm hôm nay không có trong gói, nên **không trùng**.
      - **Trần API:** thêm 30 USD, tổng **80 USD**, chỉ dùng khi cần. Đã chi 43,03.
      - **Ưu tiên private;** public là bằng chứng tốt nhất hiện có.
    - **Thí nghiệm (2) chấm 4B với chữ PhoWhisper fine-tune:**
      - Unit `lifemate-q4b-phoft`, bắt đầu 14:44, code `~/zac-docker` (`9ce44ce`), script `~/zac-docker/run_q4b_phoft.sh`.
      - Dùng adapter `q4b4_fit_random` và `q4b4_fit_lao` có sẵn, chữ `asr/train_dev_{random,lao}_phoft.jsonl`, hạn 60 giây.
      - Luật ghi trước: gộp 495 dòng ≥ 47,17 và dev_lao không giảm quá 1,0.
      - Lượt gốc (chữ turbo fine-tune) chạy trước khi có bước khởi động (PR #12), nên script báo thêm điểm bỏ mẫu đầu mỗi tập.
      - Dự kiến xong khoảng 17:15.
    - **Thí nghiệm (1) prompt `xref`:**
      - **Code:** [PR #14](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/14) (nhánh `prompt-xref`, từ `q4b-laptop`) thêm `--prompt-style xref` cho `lifemate.sft` và `lifemate.infer`.
        - Tham số ID có thêm `[ID thuộc banking.accounts]`; tool đọc có thêm ` → trả về: accounts[]`.
        - Mặc định `compact` không đổi: dựng lại `sft/fit_lao.jsonl` ra đúng sha256 `96254b3b…` mà `q4b4_fit_lao` đã học.
        - Test 64/64 đạt (thêm 1 test mới).
      - **Lượt chạy:** worktree `~/zac-xref`, script `run_q4b_xref.sh`, unit `lifemate-q4b-xref`.
        - Cùng công thức và tham số train với `q4b4_fit_lao`: 254 bước, có loss dev mỗi 50 bước.
        - Chấm dev_lao bằng chữ turbo fine-tune và chữ chuẩn, rồi so với `q4b4_fit_lao` trên cùng id.
      - **Cửa 1, ghi trước:** chữ ASR ≥ +2,0; chữ chuẩn ≥ −2,0; nhóm hỏi lại (chữ ASR) ≥ −3,0. Qua thì làm tiếp fit_random → dev_random rồi quyết bằng điểm gộp.
      - **Hẹn giờ:** `lifemate-q4b-xref-kick.timer`, 23:30 ngày 04/11 (giờ máy), chỉ chạy khi cắm sạc; đợi job PhoWhisper xong trước. Dự kiến xong khoảng 07:00–07:30 ngày 05/11.
      - Huỷ: `systemctl --user disable --now lifemate-q4b-xref-kick.timer`. Dừng giữa chừng: `systemctl --user stop lifemate-q4b-xref`; chạy tiếp: `bash ~/zac-xref/start_q4b_xref.sh`.
    - **Giờ máy là giờ New York (EST, UTC−5),** khớp lời Anh ("chiều nay", "11h30 tối nay"); mọi giờ trong JOURNAL là giờ máy. Lịch thi tính theo GMT+7, sớm hơn giờ máy 12 tiếng:
      - **Hạn nộp Docker: 16/11 23:59 GMT+7 = 11:59 trưa 16/11 giờ máy.**
      - Private test phát 20/11 9:00 GMT+7 = 21:00 ngày 19/11 giờ máy; hạn nộp 23/11 23:59 GMT+7 = 11:59 ngày 23/11 giờ máy.

83. **Chấm 4B với chữ PhoWhisper fine-tune: qua luật ghi trước; đề xuất làm file nộp public** (04/11; job xong 16:06; thí nghiệm (2) của entry 82).
    - **Kết quả** (unit `lifemate-q4b-phoft`, 14:44–16:06, code `~/zac-docker` `9ce44ce`; adapter `q4b4_fit_random` / `q4b4_fit_lao`, hạn 60 giây; mốc là cùng adapter đọc chữ Whisper-turbo fine-tune):

      | Agent 4B đọc | dev_random (233) | dev_lao (262) | Gộp 495 |
      |---|---:|---:|---:|
      | Chữ Whisper-turbo fine-tune (mốc) | 54,01 | 39,20 | 46,17 |
      | **Chữ PhoWhisper fine-tune** | **55,28** | **41,30** | **47,88** |
      | Chênh (KTC 95%) | +1,27 [−3,69; +6,16] | +2,10 [−2,56; +6,79] | +1,71 [−1,68; +5,12] |

      - Mẫu tốt hơn / kém hơn: dev_random 27 / 24, dev_lao 36 / 33, gộp 63 / 57.
      - Bỏ mẫu đầu mỗi tập (lượt mốc chạy trước khi có bước khởi động): gộp 46,36 → 48,07, vẫn +1,71.
      - **Luật ghi trước** (gộp ≥ 47,17 và dev_lao không giảm quá 1,0): **đạt.** Số liệu: `~/zac-docker/lifemate/runs/q4b4_phoft_pooled_2026-11-04.json` và `compare_q4b4_phoft_vs_turboft_dev_{random,lao}.json`.
    - **Đọc:**
      - Tăng ở execute trên dev_lao (38,57 → 41,19) và hỏi lại trên dev_random (49,29 → 53,33). Ngoài phạm vi không đổi.
      - Hash đúng: dev_random 63,5 → 64,4%, dev_lao 51,5 → 55,0%. Mẫu đúng hẳn: 110 → 116 và 74 → 80.
      - Mẫu có từ 6 lượt history trở lên tăng nhiều nhất: dev_random 40,2 → 49,8; dev_lao 36,0 → 41,0.
      - **Khoảng tin cậy còn chứa 0.** Với agent 1.7B, hai ASR gần như hoà (+0,35, entry 52); với 4B thì +1,71. Có thể 4B tận dụng chữ chính xác hơn tốt hơn, nhưng vẫn có thể là nhiễu.
      - Thời gian agent gần như không đổi: trung bình 8,5 giây trên dev_random (mốc 9,0) và 8,8 trên dev_lao (mốc 7,8); chậm nhất 39,6 giây trên laptop với hạn 60. Chưa tính thời gian ASR.
    - **Cái giá của PhoWhisper:**
      - Lớn hơn: 1,55B so với 0,8B. Tổng hệ thống khoảng 5,6B, dưới trần 6B nhưng sát.
      - Chậm hơn: decoder 32 lớp so với 4 lớp. Trên T4 ở batch 8: 0,34 giây mỗi wav, so với 0,26 của turbo-ft ở batch 16. Thời gian ở batch 1 trên laptop và trên A30 chưa đo.
    - **Vướng: trên laptop không còn trọng số gốc.**
      - Adapter LoRA PhoWhisper-ft (221 MB) có ở `cloud_results/colab_leader/x/ckpt/asr_phoft/adapter`.
      - Nhưng `pytorch_model.bin` (6,17 GB) của `vinai/PhoWhisper-large` không còn trong cache Hugging Face; cache chỉ còn tokenizer và config.
      - Muốn ghép adapter để chạy public thì phải tải lại, cần Anh đồng ý (HUMAN_TODO B24).
    - **Đề xuất (B24):**
      - Tải `vinai/PhoWhisper-large` revision `b9136a44` (6,17 GB, BSD-3) và ghép adapter bằng `asr_train --merge-only`. Kiểm: chạy lại ASR dev_random, so với chữ bản Colab.
      - Chạy `predict.sh` trên public_test với `q4b4_all/final` + PhoWhisper-ft, cùng hạn 25 giây (đã tính giây ASR) như file 46,29. Vậy chỉ ASR thay đổi. ASR chạy batch 1 để đo thời gian thật.
      - Khoảng 2–2,5 giờ laptop. Bắt đầu trước khoảng 20:30 thì xong trước lượt `xref` lúc 23:30; lượt `xref` sẽ đợi job này xong.
      - **Luật cho Docker, ghi trước:** public ≥ 46,29 (không thấp hơn bản hiện tại) thì Docker đổi sang PhoWhisper-ft; thấp hơn thì giữ Whisper-turbo fine-tune. Đòi không thấp hơn vì PhoWhisper lớn hơn và chậm hơn.
      - Khi đổi, leader cần bản ghép PhoWhisper-ft (khoảng 3,1 GB fp16) để đóng Docker; Anh gửi riêng như adapter.

84. **B24: Anh cho làm file nộp public bằng PhoWhisper-ft; không cần tải gì** (04/11; Anh lúc khoảng 16:40: "Tải và chạy ngay").
    - **Đính chính entry 83:** trọng số `vinai/PhoWhisper-large` (6,17 GB) **vẫn còn trong cache** từ 30/10.
      - Cache Hugging Face trên laptop để file thật ở kho chung `~/.cache/huggingface/hub/blobs/<2 ký tự>/`; thư mục của model chỉ chứa liên kết. Lệnh `du` không đi theo liên kết, nên tưởng là mất.
      - `hf_hub_download` trả về ngay, 0 byte được tải.
    - **Chỉ ASR thay đổi so với file 46,29:**
      - File 46,29 (`runs/e2e_public_q4b_all.jsonl`) làm bằng code `~/zac-c3` `9de4e1a`, adapter `q4b4_all/final`, 4-bit, **hạn 60 giây** (không phải 25), chưa có bước khởi động.
      - Lượt mới dùng đúng cây code, adapter và cờ đó; chỉ thay chữ ASR bằng PhoWhisper-ft.
    - **Job** `lifemate-public-phoft` (bắt đầu 16:45; script `~/zac-c3/run_public_phoft.sh`; log `runs/public_phoft_2026-11-04.log`):
      1. Ghép adapter Colab của leader vào `vinai/PhoWhisper-large` `b9136a44` → `ckpt/asr_phoft/merged`.
      2. Chạy lại ASR dev_random ở batch 8 như Colab, so từng câu với bản Colab.
      3. ASR public_test ở batch 1 (đo thời gian thật) → `runs/e2e_public_phoft_asr.jsonl`.
      4. Agent → `runs/e2e_public_q4b_all_phoft.jsonl`, rồi kiểm định dạng.
      5. Tóm tắt: số dòng giống file 46,29; giây ASR + agent mỗi mẫu; số mẫu quá 25 và 30 giây, so với file 46,29.
    - Lượt `xref` 23:30 nay đợi cả job này (sửa vòng chờ trong `~/zac-xref/run_q4b_xref.sh`).
    - **Luật cho Docker** (ghi ở B24 trước khi chạy): public ≥ 46,29 thì Docker đổi sang PhoWhisper-ft; thấp hơn thì giữ Whisper-turbo fine-tune.

85. **B24 xong: file nộp public bằng PhoWhisper-ft đã sẵn sàng, chờ nộp (B25)** (04/11; job `lifemate-public-phoft` chạy 16:45–18:40).
    - **File:** `~/zac-c3/lifemate/runs/e2e_public_q4b_all_phoft.jsonl`.
      - 634 dòng, kiểm định dạng đạt (`zaic_tools --validate` 0 lỗi), sha256 `b3f86ef0c812…`.
      - Code `9de4e1a`, adapter `q4b4_all/final`, hạn 60 giây: giống file 46,29, chỉ khác ASR.
    - **Kiểm bản ghép trên laptop:** chạy lại ASR dev_random cho 779/784 câu giống hệt bản Colab, khoảng 12/11.082 từ khác. Lệch do fp16 trên hai GPU khác nhau, mức như lần ghép turbo-ft (768/784).
    - **So với file 46,29:**
      - ASR: 602/1.933 wav ra chữ giống hệt Whisper-turbo-ft.
      - Câu trả lời: 289/634 dòng giống hệt, 345 dòng khác.
      - 1.495 lời gọi tool (mốc 1.507); 48 dòng không gọi tool nào (mốc 53).
    - **Thời gian trên laptop** (RTX 4070, ASR batch 1, agent hạn 60 giây):

      | | Whisper-turbo-ft (file 46,29) | PhoWhisper-ft |
      |---|---|---|
      | ASR mỗi wav: trung bình / p95 / chậm nhất | 0,16 / 0,24 / 1,29 giây | 0,45 / 0,90 / 1,64 giây |
      | ASR mỗi mẫu (cộng các wav): trung bình / chậm nhất | 0,48 / 1,92 giây | 1,38 / 5,33 giây |
      | ASR + agent mỗi mẫu: trung bình / p95 / chậm nhất | 9,10 / 18,76 / 44,02 giây | 10,41 / 21,12 / 35,87 giây |
      | Số mẫu quá 25 / quá 30 giây | 10 / 5 | 11 / 6 |
      | Cách dừng: xong / hỏi lại / hết bước / quá số lần lỗi | 521 / 90 / 23 / 0 | 520 / 92 / 21 / 1 |

      - Các mẫu quá 25 giây gần hết là vòng lặp chạy tới `max_steps`. Trong Docker, hạn 25 giây (đã tính giây ASR) cắt các vòng này sớm hơn.
      - PhoWhisper thêm trung bình khoảng 0,9 giây mỗi mẫu, nhiều nhất khoảng 3,4 giây. Trên A30 chưa đo; leader đo khi đóng Docker.
    - **Bước tiếp (HUMAN_TODO B25):** Anh hoặc leader nộp file này, chọn cột SLM, rồi báo điểm. Claude không nộp.
      - Luật ghi trước (B24): ≥ 46,29 thì Docker đổi sang PhoWhisper-ft, và leader cần `ckpt/asr_phoft/merged` (khoảng 3,1 GB, Anh gửi riêng). Thấp hơn thì giữ Whisper-turbo-ft.
    - Laptop rảnh từ 18:40. Lượt `xref` vẫn hẹn 23:30.

86. **B25: public 51,16 với PhoWhisper-ft (+4,87 so với 46,29). Theo luật ghi trước, Docker đổi sang PhoWhisper-ft** (05/11; Anh báo lúc khoảng 00:28: "đã nộp và được: 51.16000").
    - **Kết quả:** file `e2e_public_q4b_all_phoft.jsonl` (sha256 `b3f86ef0c812…`, cột SLM) đạt 51,16; file 46,29 chỉ khác ở ASR.
    - **So với dev:** trên dev, gộp 495 dòng chỉ tăng +1,71 (khoảng tin cậy [−1,68; +5,12], entry 83). Public tăng nhiều hơn. Đây mới là một lần nộp, nên chưa giải thích chắc được vì sao.
    - **Hệ thống Docker mới:**
      - ASR: PhoWhisper-large fine-tune, 1.543.304.960 tham số. Bản ghép: `~/zac-c3/lifemate/ckpt/asr_phoft/merged` (2,9 GB), sha256 `model.safetensors` = `421a3f62f454…`.
      - LLM: Qwen3-4B-Instruct-2507, 4.022.468.096 tham số, 4-bit. Adapter `ckpt/q4b4_all/final`: 66.060.288 tham số LoRA.
      - Tổng khoảng 5,63B, dưới trần 6B (còn dư khoảng 0,37B).
    - **Code không phải đổi:** `predict.sh` nhận model ASR qua biến `ASR_MODEL`. Chỉ cần trỏ `ASR_MODEL` vào thư mục bản ghép và chép thư mục này vào image.
    - **Còn mở:**
      - Thời gian trên A30 chưa đo. Trên laptop, PhoWhisper thêm trung bình 0,9 giây mỗi mẫu, nhiều nhất khoảng 3,4 giây (entry 85). Hạn trong Docker vẫn là 25 giây, đã tính giây ASR.
      - Lượt `xref` (đang chạy từ 23:30) chấm cửa 1 bằng chữ Whisper-turbo-ft, đúng như luật đã ghi trước. Docker giờ dùng PhoWhisper-ft, nên nếu qua cửa 1 thì các bước sau chấm bằng chữ PhoWhisper-ft (mốc dev_lao 41,30, dev_random 55,28).
    - **Việc tiếp (HUMAN_TODO B26):** Anh gửi riêng thư mục bản ghép cho leader; leader đổi `ASR_MODEL` trong Docker, kiểm sha256 rồi đo thời gian trên A30.

87. **Lượt prompt `xref` không qua cửa 1; soạn tin nhắn và danh sách file cho leader đổi Docker** (05/11; Anh lúc khoảng 08:50: "Soạn tin nhắn cho leader nói về những việc leader cần check và làm. Sau đó list các file ra tôi cần gửi cho leader.").
    - **Lượt `xref` (PR #14, B23):** chạy 23:30–06:38, train 253 bước rồi chấm dev_lao. **Không qua cửa 1** (luật ghi trước: chữ ASR ≥ +2,0, chữ chuẩn ≥ −2,0, nhóm hỏi lại ≥ −3,0):

      | dev_lao, 262 mẫu | Mốc `q4b4_fit_lao` | `xref` | Chênh theo cặp [khoảng tin cậy 95%] | Tốt hơn / kém hơn |
      |---|---:|---:|---:|---:|
      | Chữ Whisper-turbo-ft | 39,20 | 38,18 | −1,02 [−5,73; +3,65] | 30 / 34 |
      | Chữ chuẩn | 53,40 | 52,72 | −0,69 [−4,79; +3,36] | 27 / 28 |
      | Nhóm hỏi lại (chữ ASR) | 39,43 | 41,06 | +1,63 | |

      - Bỏ mẫu đầu (mốc chạy trước khi có bước khởi động): 39,35 → 38,33 và 53,61 → 52,92, nên kết luận không đổi.
      - Theo luật: dừng ở đây, không chạy tiếp fit_random. Đúng như báo cáo Codex dự đoán (tăng ít, vì mô tả tham số đã ghi nguồn ID). [PR #14](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/14) không nên merge; đóng hay để là việc Anh quyết.
      - Laptop rảnh từ 06:38.
    - **Hướng dẫn cho leader:** [`docs/LEADER_DOCKER_PHOFT_2026-11-05.md`](docs/LEADER_DOCKER_PHOFT_2026-11-05.md). Trong đó có danh sách file, sha256, lệnh chạy, cách chạy thử 3 mẫu, số tham số và giấy phép.
    - **Sửa entry 86:** máy leader chỉ có GPU 4 GB (L6), không có A30. Leader chỉ chạy thử được trong Docker; thời gian trên GPU 24 GB vẫn chưa đo.
    - **File Anh gửi riêng:**
      - `ckpt/asr_phoft/merged/` (2,9 GB).
      - `ckpt/q4b4_all/final/` (263 MB; nếu đã gửi hôm 04/11 thì bỏ qua).
      - 3 file tham chiếu public (1,5 MB): chữ ASR, file nộp 51,16, trace thời gian.
      - Có lệnh `tar` gói tất cả, giữ nguyên đường dẫn.

88. **Đóng [PR #14](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/14) (prompt `xref`) mà không merge** (05/11, 09:03; Anh: "Đóng PR #14").
    - Lý do: không qua cửa 1 ghi trước (entry 87). Comment trên PR có bảng điểm dev_lao.
    - Giữ nhánh `prompt-xref` để tra lại. Bỏ nhánh này khỏi danh sách đồng bộ tài liệu.

89. **Trong lúc leader đóng Docker: Anh không phải chờ; đề xuất fine-tune lại PhoWhisper trên gần đủ train (B27)** (05/11, 09:06; Anh: "trong lúc leader xử lí thì tôi có làm gì không hay chờ leader xong").
    - **Leader không cần gì thêm từ Anh**, ngoài các file của B26.
    - **Laptop rảnh từ 06:38.** Đề xuất dùng cho việc có lợi nhất đã đo được: ASR.
      - PhoWhisper-ft hiện tại chỉ học 1.033 mẫu train, vì đã bỏ cả hai dev (495 mẫu) và 54 mẫu kiểm.
      - ASR vẫn là chỗ mất nhiều điểm nhất đã đo: với turbo-ft, chữ ASR kém chữ chuẩn 12,98 điểm gộp (báo cáo Codex mục 7).
      - Agent đã làm đúng cách này: học đủ 1.545 mẫu, public 45,39 → 46,29.
    - **Cách làm:**
      - Cùng công thức Colab (LoRA r32/a64, 3 epoch, lr 3e-4), học thêm cả 495 mẫu dev. Vẫn giữ riêng 54 mẫu kiểm cũ (210 wav), để so với bản hiện tại trên chữ cả hai bản chưa từng thấy.
      - Trên Colab T4, đỉnh bộ nhớ là 5,63 GB, nên vừa GPU 8 GB của laptop. Ước train khoảng 2–4 giờ, rồi làm file nộp public khoảng 2 giờ. 0 USD.
    - **Luật ghi trước:**
      - WER trên 54 mẫu kiểm cũ không tệ hơn bản hiện tại quá 0,5 điểm, thì mới làm file public.
      - Public ≥ 51,16 thì Docker đổi sang bản mới; leader chỉ phải thay một thư mục.
    - **Lưu ý:** bản mới đã nghe audio dev, nên các thí nghiệm agent sau này trên dev vẫn dùng chữ của PhoWhisper-ft hiện tại.
    - **Không đề xuất lúc này:**
      - Model Thinking: zero-shot khó bằng SFT, và chưa đo được trên A30.
      - Teacher API: pilot trước giảm 2,09 điểm; báo cáo Codex cũng không khuyến nghị chi ngay.
    - **Việc khác cho Anh** (không gấp): nếu anh trai đã chạy xong gói v3 thì xin 2 file kết quả (`cloud_results_*.tar.gz`, `zac_logs.tar.gz`).

90. **B27: Anh duyệt; laptop fine-tune lại PhoWhisper trên gần đủ train từ 09:18** (05/11; Anh lúc khoảng 09:10: "Chạy ngay").
    - **Job** `lifemate-asr-phoft-all` (script `~/zac-c3/run_asr_phoft_all.sh`, log `runs/asr_phoft_all_2026-11-05.log`, code `9de4e1a`):
      1. Train `ckpt/asr_phoft_all`. Công thức giống lượt Colab của leader: LoRA r32/a64/0,05, 3 epoch, lr 3e-4, warm-up 50, batch 4 × tích luỹ 4, seed 0, gốc `vinai/PhoWhisper-large` `b9136a44`.
         - Khác lượt Colab: học thêm 495 mẫu dev. Vẫn để riêng 54 mẫu kiểm cũ (`asr/phoft_val54.txt`). Phần chọn epoch lấy 2% thay vì 5%, nên còn khoảng 1.461 mẫu để học (bản hiện tại học 1.033 mẫu).
      2. Chạy cả hai bản trên 54 mẫu kiểm (210 wav, cùng cách giải mã trên laptop), rồi tính WER.
      3. Đạt luật thì làm file nộp public `runs/e2e_public_q4b_all_phoftall.jsonl`. Phía agent giống hệt file 51,16.
      4. Tóm tắt: số dòng giống file 51,16 và thời gian mỗi mẫu.
    - **Chạy thử trước** (40 mẫu, 4 bước): GPU dùng nhiều nhất 5,56 GB (cộng màn hình khoảng 1,2 GB, vẫn dưới 8 GB). Tốc độ khoảng 1,4 wav/giây, nhanh hơn T4 khoảng 1,5 lần.
    - **Dự kiến:** train khoảng 2,7 giờ (xong khoảng 12:00), file public xong khoảng 14:00–14:30.
    - **Luật** (ghi ở B27 trước khi chạy):
      - WER bản mới ≤ WER bản hiện tại + 0,5 trên 54 mẫu kiểm, thì làm file public.
      - Public ≥ 51,16 thì Docker đổi sang bản mới; thấp hơn thì giữ `ckpt/asr_phoft`.

91. **B26: Docker với PhoWhisper-ft build xong; bước agent hết VRAM trên GPU 4 GB của leader** (05/11; Anh chuyển báo cáo của leader lúc khoảng 10:20).
    - **Đã xong** (leader báo):
      - Code nhánh `q4b-laptop`, giữ nguyên code suy luận; transformers 5.21.0.
      - Hai file model khớp sha256.
      - Qwen revision `cdbee75f17c0` nằm sẵn trong cache offline; image không còn Whisper-turbo-ft.
      - Image 12,6 GB.
      - Chạy thử khi tắt mạng với `public_0002`–`public_0004`: chữ ASR khớp nguyên văn file tham chiếu.
    - **Chưa xong:** RTX 3050 4 GB nạp được Qwen 4-bit và adapter, nhưng hết VRAM ở bước warm-up của agent (thiếu 116 MiB). Vì vậy chưa có `submission_check.json`.
    - **Vì sao không bỏ warm-up để chạy tiếp:** warm-up dùng prompt hệ thống đầy đủ (luật, hồ sơ, lịch, danh mục tool) của mẫu đầu, chỉ thay câu nói bằng "Xin chào." Mẫu thật còn có thêm lịch sử và kết quả tool, nên cần ít nhất chừng ấy bộ nhớ. Bỏ warm-up thì mẫu thật cũng hết VRAM.
    - **Đề xuất (HUMAN_TODO B28):**
      - **Kiểm chính:** một lượt thuê GPU 24 GB (tốt nhất là A30), chạy đúng image.
        - Chạy 3 mẫu để có `"ok": true`.
        - Chạy đủ 634 mẫu public để đo thời gian và đếm số mẫu dừng vì hết giờ.
        - Chạy lại lần nữa để kiểm kết quả giống nhau.
        - Nên làm sau khi B27 có kết quả, để chỉ test image cuối một lần. Bản B27 cùng kiến trúc và cỡ với bản hiện tại, nên thời gian gần như không đổi.
        - Tiền của Anh hoặc leader, không tính vào trần API. Claude không thuê.
      - **Cách không tốn tiền:** Anh cài Docker và NVIDIA Container Toolkit trên laptop (cần sudo, Anh tự cài), rồi chạy image của leader trên RTX 4070 8 GB. Cách này kiểm được `"ok"` nhưng không đo được thời gian trên A30.
      - **Claude làm khi laptop rảnh** (sau B27, khoảng 14:30): chạy `predict.sh` của nhánh `q4b-laptop` với 3 mẫu trên laptop, không qua Docker. Lượt này kiểm đường code với PhoWhisper-ft và warm-up, không kiểm image.
    - **Leader (L4):** xem quy định Docker của BTC: giới hạn cỡ image, cách nộp, cách cấp GPU, thư mục dữ liệu.

92. **Anh cần dùng máy: B27 đóng băng lúc 13:38, ở bước agent làm file public** (05/11; Anh nhắn lúc 13:38).
    - **Kiểm WER đã qua:** trên 54 mẫu kiểm, PhoWhisper-ft-all 7,08 so với 7,65 của bản hiện tại (−0,57; luật: không tệ hơn quá 0,5). Chữ ASR public xong lúc 12:25 (1.933 wav).
    - **Vì sao đóng băng mà không dừng:** bước agent chạy từ 12:25, đã được 73 phút; lượt 51,16 mất khoảng 95 phút, nên còn khoảng 25 phút. File kết quả chỉ ghi khi chạy xong, nên dừng hẳn sẽ mất 73 phút đó. `systemctl --user freeze` giữ nguyên tiến độ.
    - **Khi đang đóng băng:** GPU không tính toán, nhưng job vẫn giữ khoảng 4,7 GB VRAM và RAM của nó.
      - Chạy tiếp: `systemctl --user thaw lifemate-asr-phoft-all`.
      - Nếu Anh cần GPU hoặc RAM: `systemctl --user stop lifemate-asr-phoft-all`. Chạy lại bằng `bash ~/zac-c3/start_asr_phoft_all.sh` thì chỉ làm lại bước agent (khoảng 1,5 giờ); train và chữ ASR giữ nguyên.
    - **Ảnh hưởng:** mẫu đang chạy lúc đóng băng bị tính cả thời gian đóng băng, nên có thể dừng vì hết giờ (hạn 60 giây). Nhiều nhất 1/634 mẫu khác đi; khi so với 51,16 và khi đọc số thời gian sẽ loại mẫu đó ra.

93. **B27 chạy tiếp lúc 17:45** (05/11; Anh nhắn "chạy tiếp đi").
    - Đóng băng từ 13:38 tới 17:45 (khoảng 4 giờ 7 phút). Lệnh: `systemctl --user thaw lifemate-asr-phoft-all`; GPU chạy lại ngay.
    - Bước agent còn khoảng 25 phút, nên file public dự kiến xong khoảng 18:10–18:15. Mẫu đang chạy lúc đóng băng sẽ bị loại khi so và khi đọc số thời gian (entry 92).

94. **B27 xong: file public mới bằng PhoWhisper-ft-all sẵn để nộp (B29); `predict.sh` 3 mẫu trên laptop đạt `"ok": true`** (05/11, 18:09–18:15).
    - **ASR mới:** `ckpt/asr_phoft_all/merged` (học thêm 495 mẫu dev; train xong 12:08). WER trên 54 mẫu kiểm: 7,08 so với 7,65 của bản hiện tại. sha256 `model.safetensors`: `478866317dfe91945ad3bc3fc1ed5da9d58ea8b2e66b1eb6256646afb3959d98`.
    - **Mẫu bị đóng băng:** `public_0497` đang chạy lúc đóng băng nên dừng vì hết giờ và ra rỗng (bản 51,16 có 2 lệnh gọi tool ở mẫu này). Claude chạy lại riêng mẫu này, cùng code, adapter và hạn 60 giây: ra 2 lệnh gọi trong 15,5 giây. Dòng này được ghép vào file mới.
    - **File để nộp:** `~/zac-c3/lifemate/runs/e2e_public_q4b_all_phoftall_fix0497.jsonl` (sha256 `4d7e1cf4c80f…`).
      - 634 dòng, kiểm định dạng đạt.
      - Khác file 51,16 ở 274/634 dòng. Chữ ASR giống bản cũ ở 893/1.933 wav.
      - 50 dòng rỗng (bản 51,16: 48); 1.487 lệnh gọi (bản 51,16: 1.495).
      - Thời gian trên laptop (hạn 60 giây): trung bình 10,52 giây, p95 20,60, lâu nhất 37,11 (bản 51,16: 10,41 / 21,12 / 35,87).
      - File gốc `e2e_public_q4b_all_phoftall.jsonl` (có dòng rỗng của `public_0497`) giữ lại để đối chiếu, không nộp.
    - **Kiểm `predict.sh` trên laptop** (đã hẹn ở entry 91): code nhánh `q4b-laptop` (`55ab36a`), ASR `ckpt/asr_phoft/merged`, adapter `q4b4_all/final`, 4-bit, hạn 25 giây, warm-up bật, `public_0002`–`public_0004`.
      - `"ok": true`. Chữ ASR khớp nguyên văn tham chiếu; 3/3 dòng giống hệt file 51,16.
      - Thời gian agent: 10,97 / 18,59 / 9,38 giây, cộng ASR 0,50 / 0,67 / 1,83 giây, đều dưới 25 giây.
      - Nghĩa là đường code trong image chạy đúng trên GPU 8 GB. Vẫn chưa kiểm chính image Docker (B28).
      - Kết quả lưu ở `~/zac-c3/lifemate/runs/smoke_q4b_laptop_2026-11-05/`.
    - **Luật ghi trước (B27):** public ≥ 51,16 thì Docker đổi sang `ckpt/asr_phoft_all/merged` (leader thay một thư mục 2,9 GB, cùng kiến trúc); thấp hơn thì giữ bản hiện tại.

95. **B29: public 49,65 với PhoWhisper-ft-all, thấp hơn 51,16 (−1,51). Docker giữ `ckpt/asr_phoft/merged`** (06/11; Anh báo lúc khoảng 00:45).
    - **Theo luật ghi trước (B27):** thấp hơn 51,16 thì giữ bản hiện tại. Không phải gửi leader thư mục ASR mới. Về model, image leader đã build (12,6 GB) là bản cuối.
    - **Đọc kết quả:** WER trên 54 mẫu kiểm tốt hơn 0,57, nhưng public thấp hơn 1,51. 54 mẫu (210 wav) là mẫu kiểm nhỏ, và không có nhãn public để so theo cặp. Vì vậy không biết chênh lệch này là do ASR mới kém hơn trên public hay do dao động. Luật đã quyết; không thử thêm biến thể ASR theo hướng này.
    - **Tiếp theo:** B28 không còn phải chờ: kiểm chính image hiện tại (`"ok"`, thời gian trên GPU 24 GB, chạy lại để kiểm giống nhau).
    - File `runs/e2e_public_q4b_all_phoftall_fix0497.jsonl` và `ckpt/asr_phoft_all/` giữ trên laptop để đối chiếu.

96. **Anh hỏi: train trên laptop mất bao lâu. Số đã đo trên RTX 4070** (06/11).
    - **Agent Qwen3-4B 4-bit + LoRA r32, 1 epoch, max_len 6144:**

      | Lượt | Dòng SFT | Bước | Train | Cả lượt (thêm dev loss) |
      |---|---|---|---|---|
      | `q4b4_fit_lao` | 4.051 | 254 | 318 phút | 20:48–02:11 (5 giờ 23 phút) |
      | `q4b4_fit_random` | 4.150 | 260 | 323 phút | 03:31–08:59 (5 giờ 28 phút) |
      | `q4b4_all` (đủ 1.545 mẫu) | 4.874 | 305 | 349 phút | 00:13–06:03 (5 giờ 50 phút) |

      - Khoảng 4,3 giây mỗi dòng SFT (khoảng 1,15 phút mỗi bước 16 dòng); VRAM cao nhất 5,6 GB.
      - Thêm 1.000 dòng (ví dụ dữ liệu tổng hợp) thì thêm khoảng 1,2 giờ.
    - **ASR PhoWhisper-large + LoRA r32, 3 epoch:** `asr_phoft_all` (gần đủ train, 891 bước) mất 170 phút (2 giờ 50 phút). Bản Colab T4 của leader (582 bước) mất 163 phút.
    - **Sau khi train:**
      - Làm file public: khoảng 1 giờ 45 phút (ASR 15 phút, agent khoảng 95 phút với hạn 60 giây).
      - Chấm dev_random + dev_lao bằng chữ ASR: khoảng 1 giờ 20 phút.
    - Trong lúc train, laptop vẫn dùng được nhưng chậm; job có thể đóng băng khi Anh cần máy (entry 92).

97. **Anh: "train đi nhưng nhớ lưu checkpoint". Claude chưa bật lượt nào, vì chưa có lượt train có bằng chứng tăng điểm; hỏi Anh muốn train gì** (06/11, 01:14).
    - **Checkpoint:** code train agent (`lifemate/train.py`, từ commit `9de4e1a`) có `--state-every N`, lưu `state.pt` gồm LoRA, optimizer, scheduler và RNG. Dừng bằng `systemctl stop` sẽ lưu sau bước đang chạy; `--resume` chạy tiếp đúng chỗ. Code train ASR (`asr_train.py`) chưa có chế độ này: dừng giữa chừng là train lại từ đầu.
    - **Các hướng đã xét:**
      - **Train lại agent 4B, 2 epoch:** loss dev của hai lượt 4B đã phẳng ở cuối epoch 1 (fit_random 0,0509 → 0,0503 từ bước 200 tới 260; fit_lao thấp nhất ở bước 150, rồi nhích lên 0,1074). Khó tăng điểm; tốn khoảng 11,5 giờ, và chỉ đo được bằng public.
      - **Agent học chữ PhoWhisper-ft:** PhoWhisper-ft đã học audio của fit, nên chữ nó nghe lại trên fit sạch hơn lúc thi thật. Muốn làm đúng phải có chữ k-fold (fine-tune ASR nhiều lần). Lượt chữ trộn với turbo trước đó không qua luật gộp (entry 68).
      - **Fine-tune ASR thêm:** vừa thử, public 49,65 < 51,16 (entry 95).
      - **Dữ liệu SFT nhiều vế (P1 của Codex), model Thinking, thầy API:** chưa có dữ liệu hoặc cần A30 / API, không phải việc bật được ngay.
    - **Đề xuất:** dùng laptop cho B28 (chạy thử image Docker) nếu không thuê GPU; image chưa ai chạy trọn, hạn Docker 16/11.

98. **B28: Anh chọn kiểm image Docker trên laptop; hướng dẫn cài và tin nhắn cho leader** (06/11, 02:04; Anh: "Dùng cho B28").
    - **Laptop hiện tại:** Ubuntu 26.04, chưa có Docker, chưa có NVIDIA Container Toolkit; driver 595.99; ổ đĩa còn 160 GB.
      - Kho của Ubuntu có `docker.io` 29.1.3.
      - Toolkit phải lấy từ kho apt của NVIDIA.
    - **Trên repo không có Dockerfile của leader,** nên cần leader gửi file image, đúng lệnh `docker run` và ID của image (L8).
    - **Hướng dẫn:** [`docs/B28_LAPTOP_DOCKER_2026-11-06.md`](docs/B28_LAPTOP_DOCKER_2026-11-06.md)
      - Anh cài (B30, cần sudo; Claude không cài). Tuỳ Anh có thêm mình vào nhóm `docker` để Claude chạy không cần sudo hay không.
      - Có sẵn tin nhắn cho leader ở cuối file.
    - **Claude chạy khi có image,** mỗi lượt `--network none --gpus all --memory 9g`, tổng khoảng 5 giờ:
      1. 3 mẫu để có `"ok"`;
      2. đủ 634 mẫu để đo thời gian;
      3. đủ 634 mẫu lần nữa để kiểm tái lập.
    - **Script so kết quả:** `~/zac-c3/b28_compare.py` (chỉ trên laptop, không commit).
      - So với file 51,16, với lượt `predict.sh` ngoài Docker ngày 05/11, và giữa hai lần chạy.
      - Tính thời gian và cách dừng từ trace.
      - Đã thử trên kết quả 3 mẫu ngày 05/11: 3/3 giống, `ok` true.
    - **Không đo được trên laptop:** thời gian trên A30. Băng thông bộ nhớ của RTX 4070 Laptop khoảng 256 GB/s, A30 khoảng 933 GB/s, nên số giây đo trên laptop chỉ là mức dè dặt.

99. **Leader gửi image; hướng dẫn Docker của BTC; chuẩn bị máy để chạy B28 tối nay** (06/11, 09:40). Anh: "lát nữa khoảng 11h tôi sẽ phải mang máy đi … Hãy ưu tiên làm những việc setup máy trước để tối nay chạy suôn sẻ", kèm tin nhắn của leader.
    - **Tin nhắn của leader (L8):**
      - Giữ image 05/11 (PhoWhisper-ft + `q4b4_all/final`).
      - File trên Google Drive, chỉ chia sẻ cho Anh: 12.635.573.248 byte, sha256 `190bdeeb6157…a8`, image `zaic-lifemate`.
      - **Thiếu ID của image:** tin nhắn chỉ ghi "sha256".
      - Lệnh chạy 3 mẫu trên RTX 3050 phải mount driver thủ công. Chữ ASR khớp, nhưng agent hết VRAM ở bước khởi động.
    - **Laptop lúc 09:27:** chưa có Docker. Driver 595.99.02. RAM dùng 8,1/14 GB (app của Anh đang mở). Ổ còn 160 GB. GPU rảnh, không có job nào chạy.
    - **Hướng dẫn Docker của BTC:**
      - PDF 19 trang, tạo ngày 04/11. Agent đọc web không lấy được chữ, nên Claude trích bằng `pdftotext` từ bản đã lưu.
      - Tóm tắt và bảng 9 việc còn thiếu: [`docs/BTC_DOCKER_GUIDE_2026-11-06.md`](docs/BTC_DOCKER_GUIDE_2026-11-06.md).
      - **Máy chấm:** RTX 5090 32 GB, CUDA 13.2.
      - **Giao diện:** `/code/predict.sh`; dữ liệu ở `/data`, mount chỉ-đọc; kết quả `/result/submission.jsonl`, mỗi dòng có trường `time`.
      - **Phải có thêm:** `jupyterlab` và notebook đo thời gian từng mẫu; README, `training_code/` và URL dữ liệu/model; seed cố định.
      - **Nộp:** gzip + md5, Drive chia sẻ "Anyone with the link".
      - Hướng dẫn không nhắc tới A30 hay mức 30 giây.
      - Torch trong venv laptop (`2.15.0+cu132`) có sm_120. Torch trong image chưa kiểm.
    - **Script mới trên laptop** (ở `~/zac-c3/`, không commit):
      - `b28_setup_docker.sh`: Anh chạy bằng sudo; gồm các lệnh cài của mục 1, rồi kiểm GPU trong container.
      - `b28_run.sh`: các bước `load`, `info`, `smoke`, `full1`, `full2`.
        - Bước nào đã xong thì bỏ qua; bước nào hỏng hoặc `ok` sai thì dừng.
        - Container chạy `--network none --gpus all --memory 9g`, dữ liệu mount chỉ-đọc.
        - Chạy xong thì trả quyền sở hữu file kết quả về user của Anh.
      - `b28_start.sh`: chạy trong unit riêng, chặn ngủ cả khi gập máy.
      - `b28_image_info.sh`: chạy bên trong image để in CUDA, torch, sm_120, jupyter.
    - **Thử bằng một lệnh `docker` giả** (chép kết quả 3 mẫu ngày 05/11):
      - đi đủ các bước, ghi đủ file so kết quả;
      - chạy lại thì bỏ qua bước đã xong;
      - `ok` sai thì dừng.
      - Đã sửa một lỗi: trước khi sửa, nếu lượt 3 mẫu ra `ok` sai thì lần chạy lại vẫn coi là xong.
    - **Chưa kiểm:**
      - lệnh `docker` thật: đường dẫn có dấu cách trong `--mount`, `--gpus`, `--memory`;
      - image chạy trên laptop;
      - thời gian trên RTX 5090.
    - **Việc tiếp:** B30 (Anh, trước 11:00), B31 (tối nay, khoảng 4 giờ), L9 (leader, gói nộp cuối trước 16/11).

100. **Anh hỏi: "bạn định đóng gói nộp bài bản này luôn hả và không cải tiến gì sao?"** (06/11, 09:50; file image tải được 50%.)
    - **Laptop lúc 09:47:**
      - `~/Downloads/zac_lifemate_2026-11-05.tar` đủ 12.635.573.248 byte; **sha256 khớp với số leader gửi** (09:48).
      - Docker 29.1.3 và NVIDIA Container Toolkit 1.20.1 đã cài; `/etc/docker/daemon.json` có runtime `nvidia`.
      - Nhóm `docker` chưa có thành viên, nên Claude chưa chạy được `docker`.
    - **Trả lời:**
      - Đóng gói bản 05/11 là để có sẵn một bản chạy được: image chưa chạy trọn lần nào, hạn 16/11 cố định, và gói nộp cuối còn 9 việc không phụ thuộc model (L9).
      - Có model tốt hơn thì chỉ thay thư mục adapter hoặc ASR trong image (như B26), rồi chạy lại `b28_run.sh`.
    - **Nhưng hiện chưa có cải tiến nào có bằng chứng.** Sau 51,16, mọi lượt thử đều không qua luật ghi trước:
      - prompt `xref`: entry 88;
      - PhoWhisper-ft-all: entry 95;
      - chữ trộn: entry 68;
      - pilot dữ liệu sinh: entry 61;
      - train thêm epoch: entry 97.
    - **Chỗ mất điểm (entry 78, 81):**
      - app chưa thấy: 12–15 điểm;
      - ASR: khoảng 13 điểm;
      - quyết định làm / hỏi / bỏ qua, và chọn ID.
    - **Ba hướng còn làm được trong 10 ngày (B32):**
      - (1) hỏi anh trai kết quả gói v3;
      - (2) dữ liệu sinh v2 cho app chưa thấy, sửa hai lý do pilot 1 thất bại; dưới 15 USD API, khoảng 7 giờ laptop;
      - (3) nạp bf16 trên máy chấm 32 GB; cần GPU từ 16 GB để đo.
    - **Claude đề xuất** (1) ngay, (2) nếu Anh chấp nhận rủi ro, (3) khi có GPU lớn.
    - **Lịch:** model mới phải chốt trước khoảng 13/11, để kịp đóng gói theo giao diện BTC (L9) và kiểm lại image.

101. **Kết quả gói v3 từ máy anh trai: không có adapter nào tốt hơn để thay vào image; hai lần train cùng công thức trên hai máy lệch tới 4 điểm** (06/11, 11:23–11:35; Anh gửi báo cáo `ZAIC_cloud_results_report_2026-11-06.md`, bản sao ở `cloud_results/anh_trai/`, không commit).
    - **Máy và cách chạy:**
      - 2× RTX 4090, không phải A100 như dự kiến; torch 2.15.0+cu132, transformers 5.21.0, peft 0.21.2.
      - Chạy từ 22:21 ngày 05/11 tới 01:04 ngày 06/11, không lượt nào lỗi.
      - `q4b_random_asrtrain` tự bỏ qua vì cần 4 GPU.
      - Một seed, một epoch, greedy, backend HF.
    - **Parity (chấm lại hai adapter 1.7B của laptop):** dev_random 54,56 (laptop 53,92, +0,64); dev_lao 35,21 (35,53, −0,32). Chấm cùng adapter trên máy khác chỉ lệch dưới 1 điểm, như Kaggle T4 trước đó (+0,43).
    - **4B bf16 so với 1.7B, chữ chuẩn:**
      - dev_random 54,56 → 71,31 (+16,75); dev_lao 35,21 → 51,28 (+16,07).
      - Laptop đã đo 4B 4-bit: +11,70 và +17,78 (entry 57, 58). Đội đã dùng 4B từ 02/11, nên phần này không có gì mới.
    - **4B bf16 (cloud) so với 4B 4-bit (laptop, cùng tập fit/dev), chữ chuẩn:**

      | Tập | 4-bit (laptop) | bf16 (cloud) | Chênh |
      |---|---:|---:|---:|
      | dev_random (233) | 65,61 | 71,31 | +5,70 |
      | dev_lao (262, app chưa thấy) | 53,40 | 51,28 | −2,12 |
      | Gộp 495 dòng | 59,15 | 60,71 | +1,56 |

      - **Chưa so theo cặp được:** điểm từng mẫu nằm trong `cloud_results_*.tar.gz` (722 MB), file này vẫn ở trên máy anh trai.
      - **Không tách được phần do bf16:** hai bên khác cả độ chính xác lẫn máy train.
      - **Chưa chấm trên chữ PhoWhisper-ft** (chữ của bản nộp). Cloud chỉ chấm chữ Whisper-turbo chưa fine-tune: 35,18 / 29,03. Laptop chưa có lượt 4B nào trên đúng chữ đó để so.
    - **Hai lần train cùng công thức** (cùng code, cùng file SFT, chỉ khác máy):
      - `q17b_random_up`: laptop 51,19, cloud 55,40 (+4,21).
      - `q17b_random_asrtrain`: chữ chuẩn laptop 48,55, cloud 46,59 (−1,96); chữ turbo 33,22 và 32,29.
      - Chấm cùng adapter chỉ lệch dưới 1 điểm, nên phần lớn độ lệch đến từ bước train: phép tính trên GPU khác nhau cho ra trọng số khác nhau.
      - Vậy trên tập dev 233–262 mẫu, mỗi lần train lệch khoảng 2–4 điểm. Chênh của bf16 nằm trong khoảng đó, và hai tập dev ngược chiều nhau.
    - **Agent học trên chữ ASR (`q17b_random_asrtrain`):**
      - chữ chuẩn 54,56 → 46,59 (−7,97); chữ turbo 31,69 → 32,29 (+0,60).
      - Cùng chiều với laptop (entry 48) và lượt chữ trộn (entry 68), nên bỏ.
    - **B-up (`q17b_random_up`):** so với mốc cùng máy, cloud +0,84, laptop −2,72 (entry 49). Không rõ chiều; vẫn không dùng.
    - **Tốc độ train:**
      - 4B bf16 đạt 2.778 token/giây trên một RTX 4090, gấp 3,7 lần laptop 4-bit (749); đỉnh 10,87 GB.
      - Train 4B trên đủ 1.545 mẫu mất khoảng 1,5 giờ thay vì 6 giờ.
    - **Ý nghĩa cho B32:**
      - **Hướng (1) xong:** không có adapter nào tốt hơn để thay vào image.
      - **Hướng (3), bf16: Claude không đề xuất.**
        - dev_lao là tập giống public nhất (65% mẫu public thuộc app chưa thấy), và ở đó bf16 kém 2,12.
        - Mức chênh gộp nhỏ hơn độ lệch giữa hai lần train.
        - Muốn đổi thì phải train lại bf16 trên đủ dữ liệu, build lại image không dùng 4-bit và đo lại thời gian. Laptop 8 GB không chấm được bf16.
      - **Hướng (2), dữ liệu sinh v2, vẫn mở.** Nếu làm, máy anh trai rút việc train + chấm từ khoảng 7 giờ xuống khoảng 2 giờ.
      - **Bài học cho các thử nghiệm còn lại:** một lần train hơn 1–2 điểm trên dev chưa chứng minh được gì. Luật giữ hay bỏ cần ngưỡng lớn hơn độ lệch này, hoặc phải train nhiều seed.
    - **Dữ liệu trên máy anh trai:** gói v3 có dữ liệu thi. Khi đội không cần file kết quả nữa, nhờ anh trai xoá `~/ZAIC_2026`, gói v3 và hai file kết quả (theo `docs/CLOUD_TRAIN_2026-10-31.md`, mục Tóm tắt).

102. **Anh hỏi: train tiếp trên laptop hay trên máy anh trai?** (06/11, 11:35.)
    - **Trả lời: nếu train thì dùng máy anh trai; laptop để kiểm Docker.** Nhưng hiện chỉ còn một thứ đáng train là dữ liệu sinh v2 (B32, hướng 2). Train lại công thức cũ ở máy nào cũng không thêm điểm.
    - **Vì sao chọn máy anh trai:**
      - Train nhanh gấp 3,7 lần; GPU 24 GB.
      - Có 2 GPU, nên chạy được 2 seed cùng lúc. Điều này cần, vì một lần train lệch 2–4 điểm (entry 101): pilot v2 muốn có bằng chứng thì phải so mốc với pilot, mỗi bên ít nhất 2 seed. Trên laptop, việc đó mất khoảng 28 giờ GPU.
    - **Vì sao không dùng laptop:**
      - Tối nay laptop chạy B28 khoảng 4 giờ. Sau đó còn phải chạy notebook và `predict.sh` của PR #15 trên GPU (L9).
      - Ban ngày Anh mang máy đi, nên lượt train bị dừng.
      - Mỗi lượt 4B (train + chấm) mất khoảng 7 giờ.
    - **Cách làm nếu dùng máy anh trai:**
      - Train bằng đúng công thức 4-bit đang dùng (QLoRA), để image chỉ phải thay thư mục adapter.
      - Gói v3 dùng code cũ (`8c70d4f`, chưa train 4-bit), nên Claude phải làm gói mới từ code `q4b-laptop`, kèm dữ liệu sinh.
      - Mỗi vòng đi qua Anh và anh trai: gửi gói, chạy một lệnh, gửi lại kết quả. Vì vậy cần biết anh trai cho dùng máy mấy lần trước 13/11.
      - File nộp public vẫn làm trên laptop: 4-bit, khoảng 1,5–2 giờ, cùng chữ PhoWhisper-ft với file 51,16.

103. **Anh: máy anh trai chỉ chạy được 1 lần mỗi ngày** (06/11, 11:45).
    - **Vẫn đủ cho hướng dữ liệu sinh v2.** Một lần chạy gồm được nhiều lượt trên 2 GPU: lần v3 chạy 10 lượt trong 2 giờ 43 phút. Giả định mỗi lần được khoảng 6–7 giờ; Anh báo nếu ngắn hơn.
    - **Lịch đề xuất** (chỉ cần 2 lần chạy; còn 2–3 lần dự phòng trước 13/11):
      - **06–07/11:** Claude viết bộ sinh v2, sửa hai lý do pilot 1 thất bại (entry 61). Sinh dữ liệu pilot khoảng 12 USD. Làm gói mới từ code `q4b-laptop`, train 4-bit.
      - **Lần 1, tối 07/11:** pilot trên fit_lao → dev_lao.
        - 4 lượt: mốc 4-bit 2 seed, v2 2 seed.
        - Chấm trên chữ PhoWhisper-ft và chữ chuẩn.
        - Khoảng 5–7 giờ; tốc độ 4-bit trên RTX 4090 chưa đo, gói tự đo trước khi chạy.
      - **Sáng 08/11:** đọc kết quả theo luật ghi trước. Không đạt thì dừng, giữ bản 05/11. Đạt thì sinh cho 11 app public (khoảng 13,5 USD).
      - **Lần 2, tối 08/11 hoặc 09/11:** train 4-bit trên đủ 1.545 mẫu cộng dữ liệu sinh, ra adapter mới.
      - **09–10/11:** laptop làm file public (khoảng 2 giờ), Anh nộp. Cao hơn 51,16 thì leader thay thư mục adapter.
      - **11–12/11:** chạy lại B28 trên laptop; chốt model ngày 13/11.
    - **Luật đề xuất** (ghi vào script trước khi chạy):
      - Trên dev_lao chữ PhoWhisper-ft, trung bình 2 seed của v2 hơn trung bình 2 seed của mốc ít nhất 2,0 điểm.
      - Trên chữ chuẩn, v2 không giảm quá 2,0.
      - Cả mốc lẫn v2 đều train trên máy anh trai, nên không lẫn độ lệch giữa hai máy.
    - **Chi phí API:** khoảng 25 USD cho cả hai bước. Tổng lên khoảng 68 USD, dưới trần 80.
    - **Rủi ro:** pilot 1 giảm 2,09. Mức này nằm trong độ lệch giữa các lần train (entry 101), nên v2 chưa hẳn vô vọng, nhưng cũng chưa có bằng chứng sẽ tăng.

104. **Anh: "Làm theo lịch". Gói pilot v2 cho máy anh trai đã sẵn, sớm hơn lịch một ngày** (06/11, 11:50–12:47; `docs/CLOUD_PILOT_V2_2026-11-07.md`; code [PR #16](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/16), nhánh `synth-v2`, xếp trên PR #11).
    - **Hai nguyên nhân từng nghi cho pilot 1 đều sai** (đo trên 1.283 mẫu thật của fit_lao và 280 mẫu pilot 1, không nhìn dev):
      - **Điền thừa tham số tuỳ chọn:** 0,31 mỗi lời gọi ghi, so với 0,32 ở mẫu thật. Lúc 12:00 Claude báo Anh là đã tìm ra nguyên nhân (82,6% so với 34,5% số chỗ tham số tuỳ chọn được điền). Con số đó sai: 6 app bị giấu vốn có ít tham số tuỳ chọn. Claude đã sửa lại trong tin nhắn cho Anh.
      - **90% mở đầu bằng lời gọi đọc:** mẫu thật không có lịch sử cũng 90%. Con số 59% là của cả các mẫu có lịch sử.
    - **Khác biệt thật** (mẫu thật / pilot 1): có lịch sử 64% / 0%; dùng lại ID từ lịch sử 16% / 0%; hai app 48% / 0%; không gọi tool 8% / 0%.
    - **Bộ sinh v2** (`lifemate.synth --recipe v2`):
      - Mỗi mẫu nhận một khung rút theo tỉ lệ thật: loại mẫu; lượt trước trả về đối tượng mà câu sau dùng lại (20%); đoạn hội thoại thật không liên quan đứng trước (khoảng 45%); thêm một app (40% số mẫu execute và hỏi lại).
      - Context giữ đủ app của mẫu gốc. Ví dụ mẫu đổi theo từng lần gọi API.
      - Bước kiểm loại mẫu không theo khung.
      - ID nhận theo state, vì nhiều schema không đánh dấu `x-ref` (ví dụ `loyalty.redeem.reward_id`).
      - Solver so trạng thái cuối không phân biệt hoa thường ("Họp" so với "họp").
      - Test: 31/31 (`lifemate.tests.test_synth`).
    - **Lượt thử 12 mẫu** (0,38 USD): 12/12 đạt sau hai sửa trên. Claude đọc từng mẫu.
    - **Dữ liệu pilot** (12:21–12:44, unit `lifemate-synth-v2`):
      - 6 app bị giấu, 202/289 mẫu đạt; SFT 652 dòng, 1,93 triệu token.
      - Khung so với mẫu thật: lịch sử 64,9% (thật 63,8%); dùng lại ID 14,9% (16,3%); không gọi tool 11,4% (8,1%); hai app 23,8% (48,0%); từ 3 lời gọi trở lên 15,3% (42,2%).
      - **Chi phí:** 8,97 USD. Lúc 12:20 Claude đọc nhầm số chi dồn thành giá mỗi lần gọi nên dừng unit; 3 lần gọi đang chạy dở bị mất, ước 0,39 USD, đã ghi vào sổ chi. **Tổng API cả dự án: 52,39/80 USD.**
    - **Lượt cloud** (`lifemate/cloud/arms_2026-11-07_synth_v2.txt`):
      - 4 lượt, công thức 4B 4-bit của adapter đang nộp, fit_lao → dev_lao: bản gốc và bản v2, mỗi bên seed 0 và 1.
      - Mỗi lượt chấm cả chữ chuẩn lẫn chữ PhoWhisper-ft, nạp 4-bit, hạn 60 giây.
      - Script có thêm `EXTRA_SFT`, `EVAL_ARGS`, `EVAL_LOSS`, `SMOKE_TRAIN_ARGS`, `GEN_FILES`; mặc định không đổi.
    - **Luật ghi trước** (`scripts/pilot_rule.py`): trung bình v2 trừ trung bình gốc phải ≥ +2,0 trên chữ PhoWhisper-ft và ≥ −2,0 trên chữ chuẩn.
    - **Đã kiểm trên laptop:**
      - Chạy thử ngắn đúng công thức của lượt cloud: train 4-bit 2 bước với dòng dữ liệu sinh, rồi chấm hai loại chữ.
      - Kiểm gói: 2.317 file khớp manifest; 4 file SFT dựng lại giống hệt; test đạt; `DRY_RUN` chia đúng GPU.
    - **Gói:** `~/zac_cloud_bundle_20261106_synthv2.tar.gz`, 5,5 MB, sha256 `8314687a…`; không có audio hay adapter.
      - Anh trai chạy một lệnh (trong tài liệu), khoảng 6 giờ, rồi gửi về `~/zac_v4_results.tar.gz`.
      - **Gửi được ngay tối nay**, nếu anh trai rảnh. Như vậy kết quả có sáng 07/11, sớm hơn lịch một ngày.
    - **Chưa kiểm:** tốc độ train 4-bit trên RTX 4090; quy ước của người gán nhãn với 6 app mới.

105. **Anh nhờ soạn file hướng dẫn cho AI bên máy anh trai** (06/11, 17:20): "soạn tôi 1 file md hướng dẫn để cho AI bên anh tôi đọc từ train cái gì, dùng lệnh gì, lấy file ở đâu, gửi kết quả bao gồm cái gì ở đâu".
    - **File:** `docs/BROTHER_AI_GUIDE_PILOT_V2_2026-11-07.md`.
      - Nội dung: train gì (4 lượt); yêu cầu máy; kiểm sha256 của gói; một lệnh chạy; các mốc cần thấy trong log; bảng xử lý lỗi; gửi lại `~/zac_v4_results.tar.gz` kèm báo cáo theo mẫu, gửi riêng cho Anh.
      - Quy tắc: không sửa code, không đọc `*_environment/`, không đưa dữ liệu ra ngoài, xoá các thư mục sau khi xong.
    - **Lệnh có thêm một bước:** sau 4 lượt, `scripts/pilot_rule.py` tự áp luật ghi trước, ghi vào `lifemate/runs/pilot_v2_rule.txt`. Lệnh trong `docs/CLOUD_PILOT_V2_2026-11-07.md` đã đổi theo, hai file giống nhau.
    - **Đã kiểm:**
      - Script luật chạy trên kết quả pilot 1 ra đúng −2,09 (chữ ASR) và −2,83 (chữ chuẩn) → FAIL. Lát app bị giấu / đã thấy khớp entry 61.
      - Script chạy được từ trong gói đã giải nén.
      - Cú pháp lệnh đạt (`bash -n`, cả lệnh ngoài lẫn chuỗi bên trong).
      - Bộ lọc GPU: compute capability 8.9 qua, 7.5 dừng.
    - **Gói không đổi** (sha256 `8314687a…`): `pilot_rule.py` đã có sẵn trong commit `4769d3a`.

106. **Anh đã tải gói lên một thư mục Google Drive; sửa hướng dẫn để lấy file và nộp kết quả qua thư mục đó** (06/11, 17:25). Anh gửi link thư mục và nói: "hãy sửa lại là lấy file từ drive này và cũng tải kết quả lên drive này luôn".
    - **Hướng dẫn mới:**
      - Tải gói qua trình duyệt (rồi `scp` lên máy GPU nếu là máy chủ), hoặc bằng `rclone` với `--drive-root-folder-id`. Phụ lục có cách cài `rclone` không cần sudo và cách đăng nhập trên máy không có trình duyệt.
      - Thư mục không công khai, nên `gdown` hay `wget` không tải được.
      - Kết quả (`zac_v4_results.tar.gz` và báo cáo) tải lên đúng thư mục đó. Không xoá file của Anh, không đổi quyền chia sẻ.
    - **Link không vào repo** (repo công khai):
      - Bản trong `docs/` ghi chỗ trống `<ID_THU_MUC_DRIVE>`.
      - Bản Anh gửi có sẵn link và ID: `cloud_results/anh_trai/BROTHER_AI_GUIDE_PILOT_V2_2026-11-07.md` trên laptop, ngoài git.
      - Ngoài hai chỗ link, hai bản giống hệt nhau (đã so bằng `diff`).
    - **Việc của Anh (B33):** chia sẻ thư mục cho tài khoản của anh trai với quyền "Người chỉnh sửa", giữ chế độ "Hạn chế".
    - **Chưa kiểm:**
      - Claude không mở được thư mục Drive (riêng tư), nên chưa kiểm tên file trong đó. Bên anh trai sẽ kiểm kích thước và sha256 sau khi tải.
      - Lệnh `rclone` chưa chạy thử với thư mục này.

107. **Pilot v2 trên máy anh trai: luật ghi trước KHÔNG ĐẠT; dừng hướng dữ liệu sinh, giữ bản 05/11** (08/11, 16:36–16:45; Anh: "anh tôi đã cập nhật file lên drive rồi. kiểm tra thử kết quả từ các file mới nhất"). Chi tiết: `docs/CLOUD_PILOT_V2_2026-11-07.md`, mục "Kết quả".
    - **File:** hai file mới nhất trong thư mục Drive (15:55 ngày 08/11), là báo cáo và `zac_v4_results.tar.gz` (677.567 byte, sha256 khớp báo cáo).
      - Claude đọc báo cáo trong trình xem của Drive rồi tải cả hai về `cloud_results/anh_trai/pilot_v2_2026-11-08/` (ngoài git).
      - Gói gồm 59 file thường, không có đường dẫn lạ. Giải nén vào thư mục riêng, chỉ đọc như dữ liệu.
    - **Điểm dev_lao** (chữ chuẩn / chữ PhoWhisper-ft): `base_s0` 53,73 / 40,81; `base_s1` 49,37 / 41,18; `v2_s0` 52,13 / 39,33; `v2_s1` 53,38 / 41,74.
    - **Luật** (trung bình 2 seed):
      - chữ PhoWhisper-ft 40,99 → 40,54, **−0,46** [−4,03; +3,15], cần ≥ +2,0 → **FAIL**;
      - chữ chuẩn 51,55 → 52,75, +1,20, cần ≥ −2,0 → qua.
    - **Trên 183 mẫu có app bị giấu,** đúng chỗ dữ liệu sinh nhắm tới: chữ ASR −0,98, chữ chuẩn +2,39. Không có mức tăng nào vượt nhiễu.
    - **Độ lệch giữa hai seed của cùng công thức bản gốc:** 4,36 điểm trên chữ chuẩn (53,73 so với 49,37). Khớp với độ lệch 2–4 điểm ở entry 101.
    - **Parity:** `base_s0` gần lượt laptop `q4b4_fit_lao` (53,40 / 41,30).
    - **Sự cố:** `cloud_arms.sh` bị khởi động hai lần cùng lúc.
      - Hai dòng `FAILED` là của bản chạy thứ hai.
      - `base_s0` và `v2_s1` chạy đôi song song, ghi chung một thư mục.
      - Claude kiểm lại: mọi file đủ 262 dòng, không trùng; chấm lại ra đúng từng số; dữ liệu sinh khớp sha256. Số liệu dùng được.
    - **Kết luận theo luật:** không sinh dữ liệu cho 11 app public, không có lần chạy thứ hai. Docker giữ `ckpt/q4b4_all/final` + `ckpt/asr_phoft/merged` (image 05/11). Tổng API giữ ở 52,39/80 USD.
    - **Việc còn lại** (hạn Docker 11:59 ngày 16/11, giờ máy):
      - **B28/B31 chưa chạy:** chưa có kết quả, nhóm `docker` vẫn trống.
      - **L9:** đóng gói theo giao diện BTC; PR #15 cần chạy trên GPU.
    - **Thư mục Drive mở được mà không cần đăng nhập** (Claude xem danh sách file bằng trình duyệt chưa đăng nhập). Trong thư mục có các gói chứa dữ liệu thi (255,8 MB; 5,5 MB) và file image 3,14 GB. Đề xuất Anh chuyển sang "Hạn chế", rồi xoá các gói không còn dùng (B34).

108. **Anh: "tạo cho tôi 1 bản thử nộp public". Làm file public bằng đúng cấu hình nộp cuối** (08/11, 17:50–20:00).
    - **Cách hiểu:**
      - Không có model mới: pilot v2 không đạt (entry 107).
      - File thử này dùng model 05/11 (PhoWhisper-ft + `q4b4_all`, 4-bit), chạy qua giao diện nộp cuối của BTC (PR #15, `docker/predict.sh`, commit `1f9e1e4`), hạn 25 giây, có khởi động, seed 0.
      - File 51,16 cũ chạy hạn 60 giây, không có trường `time`.
      - Nộp file này sẽ cho biết hai điều:
        - điểm của đúng cấu hình sẽ đóng gói;
        - trang chấm public có nhận dòng có `time` không.
    - **Cách chạy:**
      - Worktree mới `~/zac-pub` ở `origin/docker-submit`; venv và `ckpt/` nối tới bản trên laptop; chạy ngoài Docker.
      - Kết quả ở `lifemate/runs/pub_trial_2026-11-08/` (không commit).
    - **Chạy thử 3 mẫu** (`public_0002`–`0004`, 17:51–17:55):
      - 3/3 giống hệt file 51,16 về lời gọi tool và `state_hash`;
      - bước kiểm `ok`, dòng có `id`, `tool_calls`, `state_hash`, `time`;
      - mỗi mẫu trung bình 13,4 giây, lâu nhất 18,7 giây;
      - nạp model 13,8 giây.
    - **Đủ 634 mẫu** (unit `lifemate-pub-trial-full`, 17:55–19:59):
      - **File:** `lifemate/runs/pub_trial_2026-11-08/full/submission.jsonl` (sha256 `f6b38fdb…`).
      - **Kiểm định dạng:** 634/634 dòng, `ok`, bộ kiểm của BTC 0 lỗi schema. Mỗi dòng có `id`, `tool_calls`, `state_hash`, `time`. 48 dòng không gọi tool, bằng file 51,16.
      - **So với file 51,16:** 625/634 dòng giống hệt về lời gọi tool và `state_hash`.
        - 9 dòng khác đều do hạn 25 giây: lời gọi của file mới là phần đầu đúng của file cũ, chỉ thiếu các lời gọi cuối.
        - 4/9 dòng vẫn cùng `state_hash` (phần bị cắt chỉ là đọc hoặc hỏi lại); 5/9 dòng khác `state_hash`.
        - Ví dụ: `public_0007` và `public_0187` gọi `flights.search` 8 và 7 lần trong file cũ, file mới dừng ở 5.
        - Mất tối đa khoảng 1,4 điểm (9/634) nếu cả 9 dòng cũ đều đúng; nhiều khả năng ít hơn. Điểm public sẽ cho biết.
      - **Thời gian mỗi mẫu** (`time` = ASR + agent, trên laptop): trung bình 10,6 giây, p50 9,8, p95 21,6, lâu nhất 34,8 giây; 12 mẫu quá 25 giây, 1 mẫu quá 30 giây. `time` có cả ASR, còn hạn 25 giây chỉ tính phần agent, nên `time` có thể vượt 25 giây.
      - **Nạp model chậm (270 giây, lần chạy 3 mẫu: 6 giây):** do trần bộ nhớ 7 GB Claude đặt cho unit trên laptop. Unit chạm trần 7 GB và dùng 0,6 GB swap khi nạp model. Thời gian nạp không tính vào `time`, nên file không bị ảnh hưởng. Máy chấm của BTC không có trần này.
    - Anh hoặc leader tự nộp; Claude không nộp.
109. **Anh: "được 51.07000". Điểm public của file thử bằng cấu hình nộp cuối** (08/11, 20:25).
    - **Điểm: 51,07.** File 05/11 (hạn 60 giây, không có `time`) được 51,16, nên lệch −0,09.
      - Mức này nằm trong khoảng Claude dự đoán (thấp hơn tối đa khoảng 1,4), và khớp với việc chỉ 9/634 dòng khác: hạn 25 giây cắt các lời gọi cuối.
      - Tức 625 dòng còn lại cho điểm giống hệt; giao diện nộp cuối (PR #15) không làm sai gì khác.
    - **Trang nộp nhận dòng có trường `time`:** file có `time` vẫn được chấm bình thường.
    - **Hệ quả:**
      - Cấu hình nộp cuối đã chốt: PhoWhisper-ft + Qwen3-4B 4-bit + `q4b4_all`, hạn 25 giây, có khởi động, seed 0, chạy qua `docker/predict.sh` của PR #15.
      - Hạn 25 giây chỉ tốn 0,09 điểm. Claude không đề xuất nới hạn: máy chấm RTX 5090 nhanh hơn laptop, nên còn ít mẫu bị cắt hơn.
      - **Việc còn lại là Docker:** đưa giao diện PR #15 vào image và chạy thử trên GPU (B28/B31, L9). Hạn 11:59 ngày 16/11 theo giờ máy (EST).
      - B34 (khoá thư mục Drive, dọn dữ liệu trên máy anh trai) vẫn chờ Anh.
110. **Anh: "Đã thêm, chạy B28". B28 chưa chạy được: cần đăng nhập lại** (08/11, 20:35–20:54).
    - **Tình trạng:** `/etc/group` đã có `docker:x:118:truyen-anh-thach`. Nhưng app Claude (và systemd của user, nơi chạy các unit) mở từ trước khi thêm nhóm, nên chưa có quyền dùng `/var/run/docker.sock`.
    - **Claude sai ở 06/11:** `b28_start.sh` và `docs/B28_LAPTOP_DOCKER_2026-11-06.md` ghi "không cần đăng xuất, chạy qua `sg docker`". Ubuntu 26.04 trên laptop không có `sg` hay `newgrp`, nên cách này không dùng được.
    - **Đã sửa:**
      - `~/zac-c3/b28_start.sh` (ngoài git) bỏ `sg`. Trước khi chạy, script kiểm quyền docker ngay trong systemd của user; nếu chưa có quyền thì dừng và in lời nhắc đăng nhập lại. Đã thử: script dừng đúng như vậy.
      - `docs/B28_LAPTOP_DOCKER_2026-11-06.md` ghi rõ phải đăng xuất rồi đăng nhập lại.
      - Linger của user đang tắt, nên khi Anh đăng xuất hết, systemd của user cũng khởi động lại với nhóm mới. Khởi động lại máy là chắc nhất.
    - **Kiểm trước:** file image `~/Downloads/zac_lifemate_2026-11-05.tar` còn, đúng 12.635.573.248 byte; ổ còn trống 139 GB.
    - **Việc của Anh:** đăng xuất rồi đăng nhập lại (hoặc khởi động lại máy), cắm sạc, mở lại phiên này và nhắn "chạy B28". Claude chạy `bash ~/zac-c3/b28_start.sh all`: kiểm sha256, nạp image, `info`, 3 mẫu, rồi 634 mẫu hai lần (khoảng 4–5 giờ).
111. **Anh: "Rồi, chạy B28". B28 chạy trong Docker trên laptop** (08/11, 22:14–).
    - **Sau khi Anh khởi động lại máy:** app Claude và systemd của user đều dùng được Docker 29.1.3 (có runtime `nvidia`); máy cắm sạc; GPU RTX 4070 Laptop 8 GB.
    - **Hai lỗi nhỏ trong `~/zac-c3/b28_run.sh` (ngoài git), đã sửa rồi chạy lại; các bước đã xong được bỏ qua:**
      - Image trong file tar của leader có tên `zaic-lifemate:phoft-2026-11-05`, không phải `zaic-lifemate:latest`. Script giờ dùng tên có tag.
      - Docker 29 báo lỗi khi đọc trường `Entrypoint` mà image không có. Script giờ in cả `Config` dạng JSON.
    - **Nạp image:** file tar đúng số byte và sha256 của leader. Image `a7f7905c5423`, build 05/11 09:55, 30,3 GB khi giải nén.
    - **Trong image (`image_info.txt`):**
      - Debian 13, Python 3.12.16, torch 2.15.0+cu132 (CUDA 13.2, bằng máy chấm).
      - Danh sách arch có `sm_120`, tức chạy được trên RTX 5090.
      - transformers 5.21.0, peft 0.21.2, bitsandbytes 0.50.2.
      - Weights nằm sẵn trong image: `ckpt/asr_phoft` 2,9 GB, `ckpt/q4b4_all` 263 MB, Qwen3-4B trong `/opt/huggingface`; `HF_HUB_OFFLINE=1`.
      - **Chưa có `/code` và `jupyter`:** image 05/11 dùng giao diện cũ (`scripts/predict.sh`). Gói nộp cuối phải theo giao diện BTC (L9, PR #15).
    - **3 mẫu (`public_0002`–`0004`, 22:17–22:19, chạy với `--network none`, giới hạn 9 GB RAM):**
      - kiểm định dạng `ok`;
      - 3/3 giống hệt file 51,16 và bản chạy ngoài Docker ngày 05/11;
      - mỗi mẫu trung bình 12,7 giây, lâu nhất 17,5 giây.
      - Giờ trong container là UTC (log ghi 03:19 thay vì 22:19); không ảnh hưởng gì.
    - **Đang chạy:** `full1` (634 mẫu) từ 22:19, xong khoảng 00:30; rồi `full2` (634 mẫu lần nữa, để kiểm hai lần chạy cùng image cho cùng kết quả), xong khoảng 02:40.
112. **Anh dán prompt bàn giao của Leader. Claude đọc tài liệu trên nhánh `search-guard`** (08/11, 23:39–23:42).
    - **Cách đọc:** `git fetch origin`, rồi `git show origin/search-guard:<file>`. Không đổi nhánh, không commit trong thư mục của Anh. Đã đọc `docs/HANDOFF_2026-11-09.md`, `docs/RANKING_FINAL_WEEK_2026-11-08.md`, `docs/SYNTH_DATA_PLAN_2026-11-08.md`, `docs/LEADER_ONBOARDING_2026-11-08.md`.
    - **Leader đẩy nhánh `search-guard` (08/11, 23:04–23:35):**
      - **D5 (`SEARCH_GUARD=1`):** lớp code chạy lúc suy luận. Khi lệnh tìm kiếm có bộ lọc trả về rỗng, code tìm lại một lần với ít điều kiện hơn (tối đa 2 lần mỗi mẫu). Khi model chỉ lặp lại các lệnh đọc đã có kết quả 3 bước liền, code dừng. Mặc định tắt. Theo HANDOFF, lỗi này chạm 60/634 mẫu public.
      - **D2:** model Meta viết lý lẽ cho từng mẫu train, đặt trong khối `<think>` của dữ liệu train. Thêm `--lora-targets` cho Qwen3.5.
      - **Giai đoạn 1:** 7 lượt train (A0–A3) để so model và D2. Máy anh trai: 0 USD, khoảng 17 giờ. Thuê 4× RTX 4090: 22–40 USD, khoảng 9–10 giờ.
    - **Quy ước làm việc mới (HANDOFF §4):**
      - luật giữ/bỏ viết trước khi chạy;
      - thay đổi cần train thì mỗi bên ≥ 2 seed; ngưỡng ≥ 3 điểm trên dev_lao chữ PhoWhisper-ft;
      - so trên cùng một máy; ưu tiên thay đổi lúc suy luận;
      - phân tích trace trước khi đề xuất;
      - không train hay chi API khi chưa ghi câu hỏi, luật và chi phí;
      - public chỉ dùng cho thay đổi lúc suy luận hoặc lần kiểm cuối.
    - Theo prompt, Claude chờ Anh duyệt trước khi chạy GPU, gọi API trả phí, push hay mở PR.
    - **Claude đề xuất chạy D5 trên public bằng laptop:** giữ nguyên adapter và ASR, chỉ bật `SEARCH_GUARD=1`. Khoảng 2 giờ GPU, 0 USD. Luật ở RANKING §5: **giữ D5 nếu điểm ≥ 50,77** (51,07 − 0,3).
    - **Câu hỏi cho Anh, chưa có trả lời:**
      - giai đoạn 1 chạy ở đâu, đã bắt đầu chưa;
      - D5 đã có điểm public chưa;
      - BTC đã trả lời 3 câu hỏi chưa (cách đếm tham số bản text-only, LoRA chưa merge, máy chấm A30 hay RTX 5090);
      - L9 và B34 tới đâu.
113. **Anh: "Chờ hết B28 rồi chạy". D5 trên public xếp tự chạy sau B28** (08/11, 23:45–23:48).
    - **Thư mục làm việc riêng `~/zac-sg`** (ngoài thư mục của Anh): worktree ở `origin/search-guard` (`39f380a`). Dùng chung `.venv`, `ckpt`, `data` với repo chính qua symlink. Không commit gì ở đó.
    - **Kiểm code D5 trên CPU:**
      - khi tắt (mặc định), code D5 không đổi gì;
      - thay đổi của D2 trong agent chỉ giữ khối `<think>` không rỗng; model Instruct đang nộp không sinh khối này;
      - các test qua (chạy bằng `python -m`, vì venv không có pytest).
    - **Lệnh** `~/zac-sg/run_d5_public.sh`: giống hệt lượt thử 51,07 (`docker/predict.sh`, hạn 25 giây, có khởi động, seed 0), chỉ thêm `SEARCH_GUARD=1`. Chạy 3 mẫu, kiểm `ok`, rồi 634 mẫu.
    - **Unit `lifemate-d5-public`** (`~/zac-sg/d5_after_b28.sh`):
      - chờ unit B28 và mọi container `b28_` xong; mỗi lúc chỉ một việc dùng GPU;
      - trần bộ nhớ 8/10 GB (lượt thử 08/11 chạm trần 7 GB nên nạp model mất 270 giây);
      - chặn ngủ cả khi gập máy;
      - log: `lifemate/runs/pub_d5_2026-11-09/chain.log`.
    - **Anh hỏi file gửi anh trai mới nhất ở đâu:** `docs/BROTHER_AI_GUIDE_ARMS_2026-11-09.md` trên nhánh `origin/search-guard` (Leader đẩy lúc 23:35), chưa có trên `main`. File pilot v2 ngày 07/11 đã cũ.
114. **Anh nhờ sửa file gửi anh trai: tiếng Anh, chỉ phần cho AI bên máy anh trai, thêm link Drive để gửi kết quả** (09/11, 00:19–00:21).
    - **File:** `cloud_results/anh_trai/BROTHER_AI_GUIDE_ARMS_2026-11-09_EN.md`. Nằm ngoài git vì có link Drive riêng. Bản tiếng Việt làm lúc 23:48 đã xoá để Anh khỏi gửi nhầm.
    - Chỉ giữ phần B của bản Leader (mục 0–10 và phụ lục `rclone`); bỏ phần A (so máy anh trai với thuê GPU).
    - **Link Drive** ghi ở đầu file và ở các bước: tải gói (mục 3), gửi trước file D5 (mục 6), nộp kết quả cuối (mục 8, bằng trình duyệt hoặc `rclone`).
    - 10 khối lệnh giống từng ký tự bản Leader (so tự động).
    - **Còn thiếu:** kích thước và sha256 của gói `zac_cloud_bundle_20261109_arms.tar.gz`, đang để `<BUNDLE_SIZE>` và `<BUNDLE_SHA256>`. Gói chỉ có trên máy Leader. File dặn AI bên kia hỏi Anh hai số này trước khi chạy.
    - Trước khi tải gói lên, thư mục Drive phải ở chế độ "Hạn chế" (B34).
115. **B28 xong: chạy trong Docker cho cùng kết quả với chạy ngoài Docker. D5 trên public đang chạy** (09/11, 00:13–02:13).
    - **Lượt 1** (`full1`, 22:19–00:13):
      - kiểm định dạng `ok`, 634 dòng, 48 dòng không gọi tool (bằng file 51,16);
      - 627/634 dòng giống hệt file 51,16; 632/634 giống file thử 51,07;
      - 2 dòng khác file thử (`public_0002`, `public_0074`) đều do hạn 25 giây: lượt Docker chạy kịp và ra đúng như file 51,16, còn file thử bị cắt;
      - mỗi mẫu trung bình 10,64 giây, p95 21,6, lâu nhất 25,62; 11 mẫu quá 25 giây (`time` có cả ASR), 0 mẫu quá 30.
    - **Lượt 2** (`full2`, 00:13–02:09):
      - `ok`; 626/634 dòng giống file 51,16; **633/634 giống lượt 1**;
      - dòng khác: `public_0074`. Lượt 2 dừng ở 6 lời gọi (thiếu lệnh `banking.transfer` cuối), giống file thử; lượt 1 có đủ 7, giống file 51,16. Mẫu này chạy sát 25 giây, nên lượt này kịp, lượt kia không;
      - trung bình 10,89 giây, p95 22,25, lâu nhất 25,38; 13 mẫu quá 25 giây, 0 mẫu quá 30.
    - **Kết luận:**
      - Image 05/11 chạy đúng trên GPU, khi tắt mạng; Docker không đổi kết quả.
      - Các lượt chỉ khác nhau ở vài mẫu chạy sát 25 giây. Máy chấm RTX 5090 nhanh hơn laptop, nên ít mẫu chạm hạn hơn.
      - Thời gian trên đo bằng RTX 4070 Laptop 8 GB, chưa đo trên máy chấm.
      - B28 và B31 xong. **Còn L9:** image chưa có `/code` và `jupyter`; gói nộp cuối phải theo giao diện BTC (PR #15).
    - **D5:**
      - unit tự chạy lúc 02:09:48, ngay sau B28;
      - 3 mẫu (02:10): `ok`, nạp model 14,6 giây; cả 3 giống hệt file 51,16 (`public_0002` trong file thử bị cắt); `search_guard: true`; `search_relaxed` = 0, tức guard chưa phải can thiệp ở 3 mẫu này;
      - 634 mẫu chạy từ 02:10, xong khoảng 04:10. Khi xong Claude kiểm file, đếm số dòng guard làm khác đi, rồi báo Anh nộp (B36).
116. **D5 trên public xong: file sẵn để nộp (B36)** (09/11, 02:10–04:02).
    - **File:** `lifemate/runs/pub_d5_2026-11-09/full/submission.jsonl` (sha256 `8b625168…`), 634 dòng. Kiểm định dạng `ok`, bộ kiểm của BTC 0 lỗi schema, 634/634 dòng có `time`, 48 dòng không gọi tool (bằng file thử).
    - **Thời gian mỗi mẫu** (ASR + agent, laptop): trung bình 10,3 giây (file thử 10,6), p95 19,9, lâu nhất 25,2; 9 mẫu quá 25 giây (file thử 12), 0 mẫu quá 30. Nạp model 14,4 giây.
    - **So với file thử 51,07:** 603/634 dòng giống hệt về lời gọi tool và `state_hash`. 31 dòng khác:
      - 1 dòng (`public_0002`) do hạn 25 giây: file thử bị cắt, D5 chạy kịp và giống file 51,16.
      - 30 dòng do guard tìm lại. Cả 30 lần đều là bỏ tham số tuỳ chọn khỏi một lệnh đọc trả về rỗng (chưa lần nào phải rút gọn câu tìm). Lệnh tìm lại là lời gọi thật, nên có trong file nộp.
    - **Guard tìm lại 30 lần ở 30 mẫu:**
      - **21 lần tìm thấy kết quả.** Trong 14 mẫu, model sau đó làm thêm lệnh ghi (đặt vé, đặt xe, tạo lịch…) so với file thử. Ví dụ: `event_tickets.search` với `query` ASR nghe sai ("Sài Gòn cờ") trả về rỗng; tìm lại không có `query` ra 5 sự kiện, model chọn một sự kiện rồi đặt 3 vé và ghi lịch. File thử chỉ có lệnh tìm đầu rồi chạy hết số bước.
      - **9 lần không tìm thấy gì**, phần lớn là `train_bus_tickets.search` bỏ `type`. Nhưng có thêm một lệnh trong ngữ cảnh, nên model đi khác ở các bước sau.
    - **Guard làm mất 9 lệnh hỏi lại (`sys.ask_missing_info`) mà file thử có.** 7 mẫu thuộc nhóm tìm lại không thấy gì, 2 mẫu thuộc nhóm tìm thấy:
      - 4 mẫu (`public_0199`, `0238`, `0254`, `0314`) bị luật "lặp lệnh đọc 3 bước liền thì dừng" cắt trước khi model kịp hỏi. Tài liệu của Leader ghi luật này không đổi file nộp. Điều đó đúng với 51,16, nhưng sai khi guard đã đổi ngữ cảnh ở bước trước.
      - 5 mẫu còn lại: model làm lệnh ghi thay cho câu hỏi (đặt xe ở `public_0215`, `0364`; chuyển tiền và ghi chú ở `0281` sau khi tìm thấy người nhận; đặt vé ở `0539` sau khi tìm thấy sự kiện), hoặc dừng sau một lệnh tìm (`0579`).
      - Chưa biết bên nào đúng (không có nhãn public). Chỉ điểm public mới cho biết.
    - **Luật dừng khi lặp lệnh đọc, ở mẫu không có tìm lại:** dừng 7 mẫu; cả 7 giống hệt file thử (file thử dừng vì hết giờ 4 mẫu, hết bước 3 mẫu). Chỉ tiết kiệm thời gian, đúng như tài liệu.
    - **Dự đoán:** 31/634 dòng khác, nên điểm lệch tối đa khoảng ±4,9 so với 51,07; nhiều khả năng ít hơn nhiều. Luật viết trước: **≥ 50,77 thì giữ D5**, bật mặc định trong `docker/predict.sh` và `lifemate/submit.py` (code qua PR); thấp hơn thì bỏ.
    - **Ghi lại cho Leader, chưa đề xuất sửa:** nếu giữ D5, nên tính lại luật "lặp 3 bước" sau khi guard đã tìm lại, vì nó cắt 4 lệnh hỏi lại. Theo E4, cần xem trace trên dev trước khi đổi gì.
    - Anh hoặc leader tự nộp; Claude không nộp.
117. **Anh đã gửi gói cho anh trai train; nhờ Claude đánh giá phương án mới, chỉ ra điểm nghẽn, cách chấm kết quả và trần điểm tới 16/11** (09/11, 15:35–15:45).
    - **Đầu vào:** tài liệu và code của Leader trên `origin/search-guard` (`ff5bea4`): HANDOFF, RANKING, SYNTH_DATA_PLAN, ONBOARDING, `brother_run.sh`, `arms_rule.py`, `final_train.sh`, file nhánh `arms_2026-11-09_models_d2.txt`. Số đo mới chạy trên CPU, không train, không API, không đổi nhánh.
    - **Phân rã chỗ mất điểm (mới đo).** Nguồn: 4 lượt baseline của pilot v2 trên máy anh trai (`cloud_results/anh_trai/pilot_v2_2026-11-08/x/lifemate/runs/sft_q4b4_lao_base_s{0,1}{,_asr}`), n = 262 mẫu dev_lao, cùng công thức với nhánh đối chứng A0. Script: `~/zac-c3/analysis_2026-11-09/decomp{,2,3}.py` (chạy bằng `.venv` trong `~/zac-sg/lifemate`).
      - Chữ PhoWhisper-ft: 40,81 và 41,18, tức mất khoảng 59 điểm.
      - **Loại quyết định (ghi / hỏi lại / chỉ đọc / rỗng) đúng ở 72% mẫu.** 28% còn lại gần như 0 điểm, khoảng 27 điểm: nhãn làm mà model hỏi lại 16–27 mẫu; nhãn hỏi lại mà model làm 16–22 mẫu; nhãn làm mà model không ghi gì 19–22 mẫu.
      - **Quyết định đúng là "ghi" (146–154 mẫu) thì điểm trung bình chỉ 50,5**, khoảng 28 điểm: cùng bộ lệnh ghi nhưng sai tham số hoặc đối tượng 10–11 điểm; thiếu, thừa hoặc sai tool ghi khoảng 10 điểm; trạng thái đúng nhưng lệch call 6–7 điểm.
      - **ASR:** cùng adapter, chữ chuẩn 51,5 → PhoWhisper-ft 41,0 (−10,5). 35–42 mẫu đang đúng thì về 0; 8–12 mẫu đi chiều ngược lại.
      - **App bị giấu so với phần còn lại** (chữ ASR): 39,0–39,5 so với 44,9–45,1.
      - **Nhiễu train ở mức từng mẫu:** hai seed cùng công thức, cùng đầu vào cho kết quả khác nhau ở 42/262 mẫu (chữ ASR) và 45/262 (chữ chuẩn). Độ lệch chuẩn giữa hai lượt cùng công thức vì vậy khoảng 2,5 điểm. Hai seed cho cùng đáp án ở 151 mẫu (điểm trung bình 54,8); khác nhau ở 111 mẫu (khoảng 22).
      - **Phần D5 chạm tới trên dev_lao:** 18–23 mẫu có lệnh đọc có bộ lọc trả về rỗng, điểm trung bình 7–13, chiếm 6,4–7,6 điểm đang mất. Không mẫu nào lặp tới 8 bước (vòng lặp đọc chỉ thấy trên public).
      - **Thời gian trên 2× RTX 4090** (chỉ agent, hạn 60 giây): trung bình 6,2 giây, p95 11,7, lâu nhất 18–20; không mẫu nào quá 25.
    - **Điểm nghẽn, theo thứ tự:**
      1. **Agent 4B chưa nắm quy ước nhãn** (khi nào làm, khi nào hỏi, điền tham số nào), nhất là ở app mới. Cùng pipeline và cùng ASR, model API được 75,52 so với 51,16.
      2. **ASR:** khoảng 10 điểm trên dev; đã fine-tune, phần còn lại nằm ở tên riêng.
      3. **Tốc độ đo:** máy anh trai chạy 1 lần mỗi ngày, chốt model 13/11, nên còn khoảng 2 vòng train. Thay đổi lúc suy luận đo được nhiều vòng hơn.
      4. **Đường găng vẫn là L9** (gói Docker theo giao diện BTC).
    - **Kết quả sắp về được chấm thế nào** (`arms_rule.py`): mốc = trung bình của A0 trên máy đó và 3 lượt cũ, khoảng 41,1 (chữ PhoWhisper-ft) và 52,2 (chữ chuẩn). Một nhánh thắng khi trung bình 2 seed trên chữ PhoWhisper-ft ≥ mốc + 3,0 (khoảng 44,1) và chữ chuẩn ≥ mốc − 2,0 (khoảng 50,2). Thắng thì giai đoạn 2 tự train trên đủ 1.545 mẫu (2 seed) và làm file public. Không nhánh nào thắng thì giữ bản 05/11.
    - **Đánh giá luật** (tính từ độ lệch 2,5 điểm ở trên): chênh giữa trung bình 2 seed và mốc 4 lượt có độ lệch chuẩn khoảng 1,5 điểm. Ngưỡng +3,0 cho tỉ lệ thắng nhầm khoảng 2,5% mỗi nhánh (khoảng 7% cho cả ba). Hiệu ứng thật +3 chỉ qua được 50% số lần; +5 qua khoảng 90%; +2 qua khoảng 25%.
    - **Bốn chỗ hở Claude thấy trong phương án:**
      - Luật không xét thời gian. A2 và A3 sinh thêm khối `<think>` ở mỗi bước, dev chấm với hạn 60 giây, bản nộp chạy hạn 25 giây. Trên laptop (gần A30 hơn RTX 5090), bản hiện tại đã có p95 khoảng 22 giây và 11–13 mẫu quá 25 giây.
      - File public của giai đoạn 2 luôn bật D5 (`SEARCH_GUARD=1` mặc định trong `final_train.sh`), nên điểm public trộn hiệu ứng model với D5. Nếu D5 trượt luật 50,77 thì phải chạy lại file với D5 tắt.
      - Các nhánh chỉ chấm trên dev_lao. Khoảng 57% mẫu public dùng app đã thấy; phần này chỉ được kiểm bằng lần nộp public của giai đoạn 2, và chưa có ngưỡng viết trước cho lần nộp đó.
      - A1 và A2 đổi model gốc trong image (tải thêm khoảng 8 GB, build lại, kiểm lại như B28); chỉ A3 là thay một thư mục adapter.
    - **Đề xuất, chờ Anh và Leader duyệt (B37):**
      1. Nộp file D5 (B36) nếu chưa nộp; gửi BTC ba câu hỏi nếu chưa gửi (câu 3 về máy chấm quyết định nhánh có `<think>` có dùng được không).
      2. Chạy D5 trên dev_lao và dev_random bằng laptop (adapter `q4b4_fit_lao`, `q4b4_fit_random`, chữ PhoWhisper-ft; khoảng 1,5 giờ GPU, 0 USD). Câu hỏi: D5 tăng hay giảm điểm trên mẫu có nhãn, và luật "lặp 3 bước thì dừng" có cắt lệnh hỏi lại đúng không. Luật: giữ nguyên luật public 50,77; kết quả dev chỉ dùng để sửa luật dừng (entry 116) nếu thấy nó cắt lệnh hỏi lại đúng.
      3. Viết trước khi có kết quả ba luật bổ sung: (a) nhánh thắng phải có số mẫu vượt 25 giây trên laptop không nhiều hơn bản hiện tại quá 1% số mẫu; (b) nhánh nằm trong khoảng +1,5 tới +3,0 thì chạy thêm 2 seed ở lượt kế của máy anh trai, không loại ngay; (c) bản giai đoạn 2 chỉ thay bản 05/11 khi trung bình public 2 seed ≥ bản cùng trạng thái D5 + 1,5.
      4. Leader build và kiểm image L9 với bản 05/11 ngay, không chờ kết quả train.
    - **Kỳ vọng tới 16/11** (ước lượng của Claude, chưa đo): sàn 51 (bản 05/11, đã kiểm trong Docker); nhiều khả năng 52–55; nếu một nhánh thắng rõ và D5 giữ được: 56–58; trần khoảng 60. Xác suất có ít nhất một nhánh qua luật: khoảng 45%. Private có thể thấp hơn public vài điểm nếu có thêm app mới.
    - **Chưa làm:** không chạy GPU, không gọi API, không push. Nhật ký 112–117 và bảng HUMAN_TODO còn ở máy Anh, chờ Anh cho push lên `main`.
118. **Anh: anh trai đang train theo file hướng dẫn, khoảng 9 lượt và 25 giờ; Anh muốn làm D1 bằng key Claude (100 USD) và Meta (90 USD)** (09/11, 17:05–17:15).
    - **Đọc lại file đã gửi:** trên máy Anh chỉ có bản `cloud_results/anh_trai/BROTHER_AI_GUIDE_ARMS_2026-11-09_EN.md` (đường dẫn Anh ghi thiếu `_EN`). Bản này còn để `<BUNDLE_SIZE>` và `<BUNDLE_SHA256>`; theo HANDOFF, hai số là 251610252 byte và `dae91476a09ef90380f3dbc3cdcc872164fedced41164d8eebc2eead1367be8f`.
    - **File ghi gì:** một lệnh `brother_run.sh`, chạy lần lượt cài đặt (30–45 phút), giai đoạn 1 (7 lượt train kèm chấm, khoảng 17 giờ trên 2× RTX 4090, cùng lúc với lượt public D5), áp luật, giai đoạn 2 nếu có nhánh thắng (2 lượt train trên đủ dữ liệu, khoảng 4 giờ; 3 lượt và khoảng 8 giờ nếu có nhánh dự phòng), rồi đóng gói. **Tổng 9–10 lượt train, 22–26 giờ.** Anh nói đúng.
    - **Đối chiếu:** pilot v2 trên cùng máy mất 3 giờ 24 phút cho một lượt train kèm chấm (`cloud_arms_20261107_1926.log`: 19:26 → 22:50). GPU 0 nhận 4 trong 7 lượt, nên giai đoạn 1 ít nhất khoảng 13,6 giờ; lượt có `<think>` dài hơn.
    - **Chỗ Claude ghi sai ở entry 117:** "còn khoảng 2 vòng train" trước mốc chốt 13/11. Một đợt mất 22–26 giờ, nên sau đợt này máy anh trai chỉ còn chỗ cho khoảng một đợt nữa. Số lượt (7 ở giai đoạn 1, 2 seed ở giai đoạn 2) entry 117 ghi đúng, nhưng không ghi tổng thời gian.
    - **Đánh giá D1 với ngân sách mới:**
      - Tiền không phải nút thắt. Hai pilot dữ liệu sinh tốn 12,57 và 9,36 USD và trượt vì nhãn do LLM tự giải (lệch quy ước) và vì phép đo quá nhiễu, không vì thiếu mẫu. Sổ chi Meta trên máy Anh: 52,39 USD.
      - D1 nhắm đúng chỗ mất điểm lớn nhất (entry 117: khoảng 27 điểm ở quyết định, khoảng 28 điểm ở lệnh ghi) và là hướng duy nhất có trần cao (top cột SLM 96,66; model API cùng pipeline 75,52).
      - **Mức tăng ước lượng, chưa đo:** nếu D1 chỉ phủ 11 app mới của public và đưa app mới lên ngang app đã thấy (dev_lao 41,30 so với dev_random 55,28 trên chữ PhoWhisper-ft; 43% mẫu public gọi tool app mới) thì được tối đa khoảng +6 public. Muốn hơn thì phải sinh cho cả 57 app.
      - **Ba rủi ro:** (a) chính sách viết bằng code không tái tạo được nhãn BTC; (b) dữ liệu sinh là chữ sạch, pilot v2 tăng +2,4 ở chữ chuẩn nhưng không tăng ở chữ ASR; (c) image nộp 16/11, private chấm 20–23/11: D1 cho 11 app public chỉ giúp private ở phần app trùng.
      - HANDOFF §5 của Leader xếp D1 sau cuộc thi; RANKING xếp hạng 4, mốc dừng hết ngày 10/11. Kế hoạch của Anh đổi thứ tự này, nên cần Leader đồng ý.
    - **Đề xuất ba cửa (B38):**
      - **Cửa 0 (CPU, 0 USD, 09–10/11):** viết bộ sinh nhãn bằng code từ catalog; cho nó sinh lại nhãn của mẫu train khi biết ý định. Đi tiếp khi khớp nhãn thật ở ít nhất 80% mẫu, tính riêng cho 6 app của dev_lao (coi như chưa thấy). Dưới 60% thì dừng D1.
      - **Cửa 1 (API tối đa 5 USD, 10/11):** 50 mẫu cho 3 app public; bộ kiểm bằng code (ô được nói có trong câu, simulator xác nhận trạng thái); Anh đọc 20 câu.
      - **Cửa 2 (API tối đa 35 USD, 10–11/11):** sinh đủ cho 11 app public và 6 app dev_lao. Laptop train `fit_lao` + D1 (2 seed, khoảng 16 giờ) để đo trên dev_lao có nhãn; máy anh trai train bản đủ dữ liệu + D1 sau khi đợt hiện tại xong. Luật của Leader giữ nguyên: giữ D1 khi public trung bình 2 seed ≥ bản không D1 + 1,5.
    - **Chưa làm:** chưa viết code D1, chưa gọi API, chưa chạy GPU. Trần API trong ghi nhớ của Claude vẫn là 80 USD tổng; chờ Anh nói trần mới.
119. **Anh trả lời B36 và B38: public D5 được 52,68; Leader đồng ý D1; trần API bỏ giới hạn; bắt đầu cửa 0** (09/11, 17:20–17:25).
    - **B36 xong: file public có bật D5 được 52,68000.** Bản thử cùng cấu hình không D5: 51,07; chênh +1,61. Luật viết trước (RANKING §5): ≥ 50,77 thì giữ. **Giữ D5.** 30/634 dòng khác bản thử do guard tìm lại (entry 116), nên +1,61 tương ứng khoảng 10 mẫu từ 0 lên có điểm.
      - Việc kéo theo (code, qua PR, phần của Leader): đổi mặc định `SEARCH_GUARD` thành 1 trong `docker/predict.sh` và `lifemate/submit.py`; image L9 build từ bản có D5.
      - Lượt `pub_c0_guard` trên máy anh trai là cùng cấu hình; không cần nộp lại.
    - **B38:**
      - Leader đồng ý đưa D1 lên trước.
      - **Trần API: không giới hạn** (Anh và Leader, 09/11). Mỗi đợt gọi vẫn ghi sổ chi và có trần riêng theo E6.
      - Chưa biết model của Meta hay Anthropic viết câu nói tốt hơn: cửa 1 thử cả hai trên cùng kịch bản rồi mới chọn.
      - Khi cần key, Claude đưa lệnh để Anh tự dán key trong terminal; key không đi qua chat.
    - **Anh trai bắt đầu chạy khoảng 12:00 ngày 09/11.** Cài đặt 30–45 phút, giai đoạn 1 khoảng 17 giờ: xong khoảng 05:00–06:00 ngày 10/11. Giai đoạn 2 (nếu có nhánh thắng) thêm 4–8 giờ: xong khoảng 10:00–14:00 ngày 10/11.
    - **Anh dặn:** push nhật ký lên `main` sau mỗi lần ghi. Entry 112–119 push lúc 17:25.
    - **Cửa 0 bắt đầu 17:25.** Luật đã ghi ở entry 118: bộ sinh nhãn bằng code khớp nhãn thật ≥ 80% mẫu trên 6 app của dev_lao thì đi tiếp; dưới 60% thì dừng D1.
120. **Cửa 0 của D1: quy tắc đọc lấy ID đạt; một nửa số lệnh đọc thuộc về kịch bản** (09/11, 17:25–17:32).
    - **Code:** nhánh `d1-program-first` (tách từ `search-guard`, commit `a6274fb`, đã push; chưa mở PR). Worktree `~/zac-d1`.
      - `lifemate/lifemate/d1_policy.py`: quy tắc chỉ đọc `kind`, `x-ref`, `returns`, `required` trong catalog, không viết riêng cho app nào. ID mà lệnh ghi cần thì lấy bằng tool đọc có `returns` trỏ tới đúng collection; lệnh đọc đó chỉ mang tham số bắt buộc và `query` (tên đã lưu của đối tượng); bỏ lệnh đọc khi ID đã có trong history hoặc trong kết quả trước đó của lượt.
      - `lifemate/scripts/d1_gate0.py`: phát lại quy tắc trên 1.545 nhãn train (CPU, chỉ dùng `label.tool_calls` và `label.tool_results`, không đọc `*_environment/`). Chạy: `cd ~/zac-d1/lifemate && PYTHONPATH=. .venv/bin/python scripts/d1_gate0.py`.
    - **Cách đo:** "ý định" là những gì bộ sinh biết trước khi viết nhãn: các lệnh ghi, lệnh hỏi lại và đối tượng chúng trỏ tới. Quy tắc phải tự thêm lệnh đọc lấy ID. Lỗi quy tắc: đúng tool nhưng khác tham số; khác tool; đọc thừa; nhãn đọc lại ID mà quy tắc coi là đã biết.
    - **Kết quả** (n = 1.545 mẫu, 1.599 lệnh đọc trong nhãn):

      | Nhóm mẫu | Số mẫu | Không có lỗi quy tắc | Lệnh đọc lấy ID khớp đúng |
      |---|---:|---:|---:|
      | Tất cả | 1.545 | 1.489 (96,4%) | 693/747 (92,8%) |
      | Không dùng app bị giấu | 1.362 | 1.316 (96,6%) | 624/670 (93,1%) |
      | Dùng 1 trong 6 app của dev_lao | 183 | **173 (94,5%)** | 69/77 (89,6%) |

      - **Luật viết trước (entry 118): ≥ 80% thì đi tiếp. Đạt.**
      - 484 ID được coi là đã biết (không đọc); nhãn chỉ đọc lại 3 lần.
      - 54 lỗi tham số: `query` trong nhãn là phần người dùng nói, không phải nguyên tên đã lưu (`podcast_radio.search`, `library.search`, `news.search`: "Người gieo hạt (bản chữ lớn)" → "Người gieo hạt"); bộ lọc vị trí khi người dùng nêu địa điểm (`bike_rental.find_bikes` có `near` 11/13 lần; `smart_home.get_status` có `room` 9/101 lần). Khi sinh dữ liệu, kịch bản biết người dùng nói gì nên điền được.
      - Không có lần đọc thừa nào; không collection nào thiếu tool đọc.
    - **Giới hạn của phép đo này, phải nói rõ:**
      - Quy tắc chỉ giải thích được **mọi** lệnh đọc ở 776/1.545 mẫu (50,2%); với mẫu dùng app của dev_lao: 67/183 (36,6%).
      - **849/1.599 lệnh đọc không phải đọc lấy ID.** 131 là tra trước khi hỏi lại. 718 còn lại là điều kiện ("nếu mai mưa"), câu hỏi thông tin, hoặc tra giá trị để tính tham số (đặt báo thức một tiếng trước lịch họp → `calendar.list_events`). Tool đứng đầu: `weather.get_forecast`, `ewallet.get_balance`, `calendar.list_events`, `bill_payment.list_bills`, `gold_price.get_price`.
      - Ở nhóm này, 707/849 (83,3%) chỉ mang tham số bắt buộc và `query`; phần còn lại có bộ lọc do người dùng nêu (`gold_price.get_price{type}` 33, `calendar.list_events{date_from,date_to}` 17).
      - **Hình dạng nhãn** (thứ tự loại call): 98 dạng; 28 dạng nhiều nhất phủ 87,9% mẫu. Nhiều nhất: chỉ ghi 13,7%; đọc ID rồi ghi 8,3%; rỗng 7,2%; đọc ID rồi ghi hai lệnh 7,1%; một câu hỏi 6,3%; đọc điều kiện rồi ghi 6,2%.
      - Vậy cửa 0 chỉ chứng minh phần quy ước mà hai pilot trước làm lệch (đọc lấy ID). Phần kịch bản (đọc theo nghĩa, khi nào hỏi lại, tỉ lệ các dạng) chưa được kiểm; đó là việc của bộ sinh kịch bản và cửa 1.
    - **Việc kế (cửa 1):**
      1. Bộ sinh kịch bản cho các dạng nhiều nhất, tỉ lệ rút từ train; nhãn sinh bằng `d1_policy` và kiểm bằng simulator.
      2. Kiểm ngược trên 6 app của dev_lao: phân bố dạng nhãn của mẫu sinh so với mẫu thật (không cần GPU).
      3. Thử viết câu nói bằng cả model Meta và Anthropic trên cùng 30 kịch bản; chấm bằng bộ kiểm code (ô được nói có trong câu) và Anh đọc.
    - **Key:** `~/.zac_meta_env` đã có trên laptop (tạo 02/11). Chưa có `~/.zac_anthropic_env`; Anh tạo bằng lệnh Claude đưa (B39).
121. **Anh hỏi file dữ liệu train cho máy anh trai ở đâu, Claude tải lên Drive được không** (09/11, 18:22).
    - **File là gói** `zac_cloud_bundle_20261109_arms.tar.gz`, **chỉ nằm trên máy Leader** (`~/` của Leader). Leader tạo gói lúc 23:45 ngày 08/11 giờ New York (commit `ff5bea4`): 251.610.252 byte (240 MB), sha256 `dae91476…67be8f`. Trong gói có code, dữ liệu train (không có audio), lý lẽ D2 đủ 1.545 mẫu, transcript dev, adapter `q4b4_all` và transcript public của bản 51,16.
    - **Laptop không tự tạo được gói giống vậy:** thiếu `gen/rationale_d2all.jsonl`, file lý lẽ Leader sinh bằng API Meta (9,57 USD). Sinh lại thì tốn tiền lần nữa, và gói mới sẽ có sha256 khác với hướng dẫn. Vì vậy cả Claude lẫn Anh đều không tải được gói này từ laptop. **Leader tải lên thư mục Drive từ máy mình**, sau khi đặt thư mục ở chế độ "Hạn chế" (B34).
    - Entry 119 ghi anh trai đã bắt đầu chạy khoảng 12:00. Nếu đúng vậy thì gói đã tới máy anh ấy, không cần gửi lại.
    - **File hướng dẫn** `cloud_results/anh_trai/BROTHER_AI_GUIDE_ARMS_2026-11-09_EN.md` (ngoài git) đã điền kích thước và sha256, khớp với bản của Leader; không còn chỗ để trống. Nếu AI bên máy anh trai hỏi hai số này thì Anh gửi đúng hai số trên.
122. **Anh nhờ kiểm trên Drive đã có gói train chưa** (09/11, 18:41).
    - Claude mở thư mục Drive của đội bằng Chrome của Anh, chỉ xem, không đổi gì.
    - **Gói `zac_cloud_bundle_20261109_arms.tar.gz` đã có:** 240 MB (khớp 251.610.252 byte Leader ghi); chủ sở hữu là Leader; Leader tải lên ngày 08/11 (giờ New York); tài khoản của Anh đã mở file ngày 09/11. Drive không hiện sha256; AI bên máy anh trai kiểm sha256 sau khi tải về (mục 3 của file hướng dẫn).
    - **Cần sửa gấp (B34):** mục "Who has access" của gói ghi "Anyone on the internet with the link can edit". Tức ai có link cũng tải được, sửa được hoặc xoá được gói, mà gói có dữ liệu thi. Thư mục còn có các gói cũ và kết quả các lần chạy trước.
      - Claude mới xem quyền của gói; quyền này nhiều khả năng lấy từ thư mục, nhưng chưa xem trực tiếp quyền của thư mục.
      - Cách đổi: chuột phải thư mục → Share → General access → "Restricted", rồi chỉ thêm tài khoản của Anh và tài khoản anh trai dùng để tải. Leader là chủ thư mục. Tài khoản của Anh cũng thấy nút "Manage access", nên Anh có thể tự đổi nếu Leader không khoá quyền chia sẻ của người được mời.
      - Làm khi anh trai đã tải xong gói, hoặc thêm tài khoản của anh trai trước, để không chặn lượt đang chạy.
      - Theo B34, các gói cũ không còn cần (`zac_cloud_bundle_20261031_v3`, `zac_cloud_bundle_20261106_synthv2`) nên xoá.

123. **Anh: "Viết bộ sinh kịch bản". Bộ sinh kịch bản cho 11 app public và phép thử model viết câu nói** (09/11, 17:40–19:18; làm song song với phiên ghi entry 121–122).
    - **Anh chấp nhận cửa 0 theo cách đọc ở entry 120.** Anh đã tạo `~/.zac_anthropic_env` (B39 xong).
    - **Code, nhánh `d1-program-first`** (commit `d712df2`, đã push; chưa mở PR):
      - `lifemate/lifemate/d1_gen.py`: với mỗi app, code tự dựng state từ kho tên (không đọc `*_environment/`), chọn ý định, rồi sinh nhãn bằng `d1_policy`. Mỗi nhãn chạy thật trong bộ giả lập của public_test và bị loại nếu: sai schema, có lệnh không tác dụng, ID trong lệnh ghi chưa được lệnh đọc nào trả về, hoặc câu tìm trả về nhiều hơn một đối tượng (trừ kịch bản hỏi lại, cần từ hai trở lên).
      - Loại kịch bản: làm một việc; làm hai việc (app mới + báo thức hoặc nhắc việc); hỏi thông tin; hỏi lại (hai đối tượng cùng khớp, hoặc thiếu số tiền / số lượng / thời lượng / giờ nhắc); app chưa cài (nhãn rỗng).
      - Ngữ cảnh và history lấy từ một mẫu train (thời điểm, người dùng, app đã cài, các lượt trước), thêm app đích vào.
      - `lifemate/lifemate/d1_say.py`: model ngoài chỉ viết một câu nói từ các dòng "người dùng muốn"; có sổ chi và trần riêng cho từng model; bộ kiểm code trên câu trả về (đủ các tên phải có, không lộ chỉ dẫn, không đọc ID, 6–55 từ).
    - **11 app, 34 tool:** stocks, translator, grocery, recipes, public_transit, parking, train_bus_tickets, ecommerce, event_tickets, habit_tracker, pantry. Đã đọc mã bộ giả lập của cả 11 app (BTC cho phép dùng `zaic_tools` và catalog của public để sinh dữ liệu).
    - **1.100 kịch bản thử** (`~/zac-d1/lifemate/gen/d1_t1_scen.jsonl`, seed 1, 100 mỗi app; 20 lần bị loại khi dựng):

      | | Hỏi lại | Rỗng | Làm | Chỉ hỏi | Call mỗi mẫu | Mở đầu bằng lệnh đọc | Lệnh đọc chỉ có tham số bắt buộc + `query` |
      |---|---:|---:|---:|---:|---:|---:|---:|
      | Mẫu sinh (n = 1.100) | 11,9% | 9,8% | 68,8% | 9,5% | 2,10 | 61,8% | 99,4% |
      | Nhãn train (n = 1.545) | 14,0% | 7,2% | 70,7% | 8,0% | 2,29 | 63,7% | 89,4% |

      - Pilot 1 có 90% mẫu mở đầu bằng lệnh đọc (thật: 59%); bản này 61,8%.
      - Mẫu sinh chưa có lệnh đọc mang bộ lọc tuỳ chọn, chưa có kịch bản điều kiện ("nếu… thì…") hay tra giá trị từ app khác; đó là khoảng 15–20% mẫu train.
    - **Quy ước Claude phải đoán cho app không có nhãn** (ghi để Leader soát): `stocks` đặt lệnh thẳng bằng mã, không đọc trước; `train_bus_tickets.search` không điền `type`; `parking.find` dùng khu vực làm `near`; `grocery`/`ecommerce` tìm bằng tên người dùng nói rồi mới thêm vào giỏ; `pantry.consume` và `habit_tracker.log` đọc danh sách trước. Lượt D5 (bỏ bộ lọc tuỳ chọn thì +1,61 public) ủng hộ quy ước "đọc tối giản".
    - **Phép thử model viết câu nói** (E6: câu hỏi là model nào viết đúng nghĩa và tự nhiên nhất; luật: tỉ lệ qua bộ kiểm code, rồi Anh đọc; trần 1 USD mỗi model). Cùng 30 kịch bản, cùng prompt, cùng gợi ý cách nói:

      | Model | Qua bộ kiểm code | Số từ trung vị | Chi | Ước cho 1.000 câu |
      |---|---:|---:|---:|---:|
      | `claude-opus-5-5` (Anthropic) | 30/30 | 24 | 0,230 USD | 7,7 USD |
      | `muse-spark-1.3` (Meta) | 30/30 | 22 | 0,106 USD | 3,5 USD |
      | `muse-wonder-1.0` (Meta) | 30/30 | 24 | 0,312 USD | 10,4 USD |

      - Tổng 0,648 USD; sổ chi ở `~/zac-d1/lifemate/gen/d1_t1_say_*_usage.jsonl`. Tổng API trên máy Anh: 52,39 + 0,65 = 53,04 USD.
      - **Claude đọc tay 24 trong 30 bộ ba:** cả ba model đều viết tự nhiên. `muse-spark-1.3` có 1 câu đổi nghĩa khi tự sửa giữa câu ("nhắc mình tưới cây… à không đặt lệnh bán…": thành ra huỷ việc nhắc) và 1 câu thêm việc ("check giúp anh cổ phiếu VIC với"). `claude-opus-5-5` tự sửa đúng chỗ ("hai trăm, à không, một trăm") nhưng 2 câu thêm lời dẫn có thông tin ngoài mô tả ("hông biết còn đủ tiền hông"). `muse-wonder-1.0` không có câu sai nghĩa trong phần đã đọc, đắt nhất.
      - Bộ kiểm code không bắt được lỗi đổi nghĩa; cần thêm bước kiểm bằng model giải lại (như pilot v2) trước khi sinh số lớn.
      - Gửi đi cho model: prompt hướng dẫn, 12 câu nói train làm mẫu giọng điệu (như các đợt sinh trước), và các dòng "người dùng muốn". Không gửi history, state, nhãn hay dữ liệu public.
      - Gọi Anthropic qua SDK chính thức trong môi trường riêng `~/zac-d1/.venv-api` (không đụng `.venv` train); có bật fallback phía server cho model này.
    - **File để Anh đọc:** `lifemate/gen/d1_t1_say_compare.md` (30 kịch bản, mỗi kịch bản 3 câu; thư mục `gen/` không vào git).
    - **Chưa làm của cửa 1:** kiểm ngược trên 6 app của dev_lao (cần viết thêm 6 app cho bộ sinh; cũng là điều kiện để laptop đo có nhãn ở cửa 2); kho tên còn nhỏ (15–30 tên mỗi app); bước tạo dữ liệu train (`sft`) chưa nhận catalog của app public.

124. **Anh chọn `claude-opus-5-5`; sáu app của dev_lao; Anh dán bản giao việc mở rộng D1 sang 46 app đã thấy** (09/11, 19:30–20:25).
    - **B40:** Anh chọn `claude-opus-5-5` làm model viết câu nói chính.
    - **Sáu app của dev_lao trong bộ sinh** (library, robot_vacuum, loyalty, medication, video_meeting, home_security; catalog và bộ giả lập của train; `d1_gen build --split train --shells splits/fit_lao.txt`).
      - **Viết "mù":** chỉ đọc catalog và mã bộ giả lập, như đã làm với 11 app public, rồi commit (`f506a39`) trước khi chạy phép so. Mục đích: chấm đúng khả năng đoán quy ước ở app không có nhãn, và giữ cho lượt đo trên dev_lao không bị lộ nhãn.
      - Claude đã thấy vài mẫu của 6 app này ở entry 117 và 120 (ví dụ `medication.add`, `library.search`), nên "mù" không tuyệt đối.
    - **Phép so với nhãn thật** (`lifemate/scripts/d1_compare.py`; n = 261 call thật của 6 app; 900 kịch bản sinh):

      | Đo | Bản mù (`lao0`) | Sau khi dùng tỉ lệ đo trên app đã thấy (`lao1`) |
      |---|---:|---:|
      | Hỗn hợp bộ tham số của từng tool, trùng với thật (1 = giống hệt), tính theo tần suất call thật | 0,845 | 0,902 |
      | Tool có trong nhãn thật mà bộ sinh không gọi | 0 | 0 |

      - **Đúng ngay từ bản mù:** mọi tool; ID lấy từ đúng tool đọc; 13/20 tool có bộ tham số trùng hoàn toàn.
      - **Lệch ở bản mù:** `medication.log_taken` thiếu `time` (thật 80%, sinh 0%); `loyalty.get_points` không điền `program` (thật 58%); `robot_vacuum.start` dùng `mode` và dọn cả nhà quá nhiều (thật 89% chỉ có `rooms`); `video_meeting.create` mời người quá nhiều (thật 21%, sinh 60%).
      - **Thiếu hẳn một loại kịch bản:** ở nhãn thật, 38–62% lệnh ghi cần ID không có lệnh đọc đứng trước, vì ID đã có trong history.
    - **Hai sửa đổi, đều rút từ app đã thấy chứ không từ nhãn của 6 app:**
      - **Tỉ lệ điền tham số tuỳ chọn theo kiểu tham số**, đo trên nhãn fit_lao của 40 app không bị giấu: lệnh ghi: enum 30% (126/417), chữ tự do 11–14%, số nguyên 40%, ngày giờ 84% (162/192), mảng 2%; lệnh đọc `list_*` 1–13%, `get_*` có enum 32%. Áp cho cả 6 app dev_lao lẫn 11 app public. Riêng tỉ lệ "dọn cả nhà" của robot giữ nguyên mức đoán mù (45%), vì con số đúng chỉ biết được từ nhãn của chính app đó.
      - **Kịch bản nối tiếp (`followup`):** lệnh đọc lấy ID trở thành lượt trước trong history (câu hỏi + kết quả + câu trả lời), nhãn chỉ còn lệnh ghi. Tỉ lệ ID đến từ history ở nhãn thật: 249/1.071 (23%).
      - Sau hai sửa đổi: `log_taken` 0,20 → 0,96; `video_meeting.create` 0,62 → 0,86; `robot_vacuum.start` 0,42 → 0,67; `loyalty.get_points` vẫn 0,42 (quy tắc theo kiểu không bắt được).
    - **Bài học đưa sang 11 app public:** giảm tham số tuỳ chọn theo đúng các tỉ lệ trên (đã sửa); thêm kịch bản nối tiếp (đã thêm, 8,9% mẫu). Bộ thử mới `d1_t2`: 1.650 kịch bản; hỏi lại 12,4%, rỗng 9,8%, làm 67,1%, chỉ hỏi 10,7%.
    - **Lượt đo trên dev_lao phải dùng bản sinh không sửa theo nhãn của 6 app** (`lao1` đạt điều kiện này). Nếu sau này sửa riêng cho từng app theo nhãn thật thì dữ liệu đó không được dùng để đo trên dev_lao.
    - **Bản giao việc Anh dán: mở rộng D1 sang 46 app đã thấy.** Claude ghi nhận là việc của Anh giao, làm sau khi cửa 1 cho app public xong, trong file riêng `lifemate/lifemate/d1_seen.py`.
      - **Kiểm tiền đề trước khi làm:** bản giao việc viết "`final_state` của app mà mẫu không ghi chính là state ban đầu". **Không đúng với dữ liệu:** `final_state` chỉ chứa các app mà nhãn đã ghi (ví dụ `train_0001`: `calendar`, `sms`); 0/1.545 mẫu có `final_state` phủ hết app đã cài.
      - **Đề xuất thay thế, chờ Anh xác nhận (B41):** dùng `final_state` của app **sau** khi nhãn ghi làm state ban đầu cho kịch bản mới (đó vẫn là một state hợp lệ, đúng định dạng thật), cộng với kết quả của các lệnh đọc không tham số trong nhãn và history. Trên fit_random: 39/46 app có `final_state`; weather và gold_price chỉ có kết quả đọc; fuel_price, lottery, exchange_rate, calculator không có gì (toàn app chỉ đọc, state phải tự dựng). App ít bản nhất: news 8, home_energy 9, contacts 9, maps 10.
      - **Luật giữ/bỏ, viết trước khi train (theo bản giao việc):** train `fit_random` + dữ liệu D1 app đã thấy so với `fit_random`, chấm trên dev_random (233 mẫu), **ít nhất 2 seed mỗi bên, cùng một máy**. Giữ khi trung bình chữ PhoWhisper-ft tăng **≥ 3,0 điểm** và chữ chuẩn không giảm quá **2,0 điểm**. Đo riêng với bản 11 app public. Trước khi sinh hàng loạt cho một app: so nhãn sinh với nhãn thật của app đó bằng `d1_compare.py` (bộ tham số, lệnh đọc trước lệnh ghi, tỉ lệ loại mẫu); tool nào lệch thì sửa hoặc bỏ, báo con số. Chỉ dùng mẫu fit để lấy state và để so.
      - **Mốc dừng (theo bản giao việc):** hết ngày 11/11 chưa có dữ liệu qua bước so cho nhóm hỏi lại và 7 app đầu (bill_payment, calendar, reminders, banking, flights, chat_ott, email) thì dừng nhánh này.
      - Thứ tự làm: tình huống hỏi lại trước, rồi 7 app trên, rồi phần còn lại. Số đo nền trong bản giao việc (5,17 điểm mất ở nhóm hỏi lại trên chữ ASR…) Claude chưa tự kiểm lại.
    - **Ước chi phí, chưa chi:**
      - API viết câu nói bằng `claude-opus-5-5`: khoảng 7,7 USD mỗi 1.000 câu; kịch bản nối tiếp cần 2 câu. Bước kiểm đổi nghĩa (model giải lại) ước thêm 3–8 USD mỗi 1.000 mẫu. Public 3.300 mẫu: khoảng 35–55 USD. Bản đo dev_lao 600–900 mẫu: 8–15 USD. Nhánh app đã thấy khoảng 3.000 mẫu: 30–50 USD. **Tổng 75–120 USD** trên hai nguồn credit (190 USD).
      - GPU, trên máy anh trai (mỗi lượt train kèm chấm khoảng 3,5–4,5 giờ trên một RTX 4090; rảnh từ khoảng 14:00 ngày 10/11): đo dev_lao 2 lượt (mốc đã có 2 seed trên máy đó); đo app đã thấy 4 lượt; bản cuối trên đủ dữ liệu 2 lượt. 8 lượt trên 2 GPU: khoảng 16–18 giờ.
    - **Chưa làm:** bước kiểm đổi nghĩa; ghép câu nói vào mẫu train (kể cả lượt trước của kịch bản nối tiếp); cho `sft` nhận catalog của app public; kho tên lớn hơn; `d1_seen.py`. Chưa gọi API trong mục này.

125. **Anh sửa hai điều (giờ anh trai chạy, trần API) và duyệt các việc còn lại; đường ống D1 hoàn chỉnh; luật cho lượt đo dev_lao** (09/11, 20:30–20:58).
    - **Anh sửa:**
      - **Anh trai bắt đầu train lúc 18:30 ngày 09/11**, không phải 12:00 như entry 119 ghi. Giai đoạn 1 (cài đặt 30–45 phút + khoảng 17 giờ) xong khoảng 12:00–12:30 ngày 10/11; giai đoạn 2 nếu có nhánh thắng thêm 4–8 giờ, tức cả đợt xong khoảng 16:30–20:30 ngày 10/11.
      - **Hai trần API tách riêng, không được gộp:** Anthropic 100 USD tổng; Meta còn 81 USD (số Anh báo lúc khoảng 20:30). Entry 124 viết "tổng 75–120 USD trên 190 USD" là sai cách tính. Vượt credit của bên nào thì đội bị trừ tiền thật.
      - `lifemate/d1_say.py` giờ chặn trước mỗi lần gọi: Anthropic dừng ở 95 USD, Meta dừng ở 76 USD chi mới (để lại 5 USD mỗi bên vì sổ chi chỉ là ước tính theo token). Meta chỉ đếm các dòng ghi sau 20:25 ngày 09/11.
    - **B41: Anh đồng ý** lấy state cho app đã thấy từ `final_state` sau khi ghi và từ kết quả lệnh đọc.
    - **Đường ống D1, đã xong và chạy thử** (nhánh `d1-program-first`, commit `e6a32cb`, `86262d5`):
      1. **Kiểm đổi nghĩa** (`d1_say judge`): model `muse-spark-1.3` đọc câu nói cạnh các dòng "người dùng muốn" và loại câu thiếu việc, đổi giá trị, huỷ việc hoặc thêm việc. Thử trên 90 câu của entry 123: loại đúng 2 câu Claude đã thấy sai bằng tay, không loại câu nào khác. Chi khoảng 3,7 USD mỗi 1.000 câu (Meta).
      2. **Ghép mẫu train** (`d1_say final`): chỉ lấy kịch bản mà câu nói (và câu của lượt trước, nếu là kịch bản nối tiếp) qua cả bộ kiểm code lẫn bước kiểm nghĩa.
      3. **`sft --d1-samples`** và `D1_SAMPLES` trong `train_local.sh`: schema tool lấy từ cả catalog train lẫn public; `--drop-apps` không bỏ app mà mẫu D1 được sinh cho. Thử trên fit_lao: 4.051 dòng thật giữ nguyên, không dòng thật nào lộ tool của app bị giấu.
      4. **Kho tên** (`lifemate/d1_pools.json`, `scripts/d1_pools.py`): thêm 861 dòng tên bịa do `muse-spark-1.3` viết, code kiểm (kiểu dữ liệu, tên gọi ngắn nằm trong tên đầy đủ, không trùng); 0,28 USD (Meta).
      5. **`lifemate/d1_seen.py`, phần 1 (hỏi lại):** xem mục dưới.
    - **Dữ liệu cho lượt đo dev_lao** (`~/zac-d1/lifemate/gen/d1_lao2.jsonl`, sha256 `c2b5a1128dc9dbcb…`):
      - 660 kịch bản cho 6 app bị giấu (110 mỗi app, seed 2, bản sinh không sửa theo nhãn của 6 app); hỗn hợp bộ tham số so với nhãn thật 0,889.
      - `claude-opus-5-5` viết 691 câu (660 câu chính + 31 câu lượt trước): 678 qua bộ kiểm code; **5,33 USD (Anthropic)**.
      - `muse-spark-1.3` kiểm nghĩa 678 câu, loại 15 (đa số là câu thêm việc "check lại giùm"); **2,54 USD (Meta)**.
      - **Còn 633 mẫu** (99–109 mỗi app): làm 239, làm hai việc 174, nối tiếp 29, hỏi lại 12 + 43 (kèm việc khác), chỉ hỏi 46 + 38, app chưa cài 52.
    - **Luật cho lượt đo dev_lao, viết trước khi train (E6):**
      - **Câu hỏi:** dữ liệu D1 cho app không có nhãn (viết mà không nhìn nhãn của chúng) có nâng điểm trên app đó không.
      - **Lượt chạy:** laptop, đúng công thức `q4b4_fit_lao` (Qwen3-4B-Instruct-2507 4-bit, QLoRA r32, lr 2e-4, 1 epoch, max-len 6144), thêm `D1_SAMPLES=gen/d1_lao2.jsonl`, seed 0 rồi seed 1 (`q4b4_lao_d1_s0`, `q4b4_lao_d1_s1`); chấm dev_lao (262 mẫu) trên chữ chuẩn và chữ PhoWhisper-ft, hạn 60 giây.
      - **Mốc:** trung bình 3 lượt đã có của cùng công thức: chữ PhoWhisper-ft 41,10 (41,30; 40,81; 41,18), chữ chuẩn 52,17 (53,40; 53,73; 49,37). Lượt A0 trên máy anh trai về thì cộng vào mốc, như `arms_rule.py`.
      - **Giữ D1 cho app mới khi:** trung bình 2 seed chữ PhoWhisper-ft ≥ mốc + 3,0 (khoảng 44,1) **và** chữ chuẩn ≥ mốc − 2,0 (khoảng 50,2). Khi đó sinh dữ liệu cho 11 app public và train bản cuối.
      - **Không đạt:** dừng D1 cho app mới; bản nộp là bản 05/11 + D5, hoặc nhánh thắng của máy anh trai.
      - **Lệch so với E5:** trên laptop chỉ có 1 lượt mốc (41,30 / 53,40); hai lượt mốc kia chạy trên máy anh trai. Ba lượt đó lệch nhau 0,5 điểm trên chữ PhoWhisper-ft và 4,4 điểm trên chữ chuẩn.
      - **Chi phí:** API đã chi 5,33 USD (Anthropic) + 2,54 USD (Meta). GPU: dữ liệu train tăng từ 4.051 lên 6.072 dòng, nên mỗi seed khoảng 8 giờ train + 2,4 giờ chấm; hai seed khoảng 21 giờ, xong khoảng 19:00 ngày 10/11. Seed 0 có điểm khoảng 08:00 ngày 10/11.
    - **Nhánh app đã thấy, phần 1: tình huống hỏi lại** (`python -m lifemate.d1_seen build`; so bằng `d1_compare.py --asks --ids splits/fit_random.txt`, chỉ dùng nhãn fit_random):
      - 184 mẫu fit_random kết thúc bằng `sys.ask_missing_info`. Tám chương trình đã viết phủ **99/184 (54%)**: trùng tên trong danh bạ hoặc danh sách chat (`phone.call`, `sms.send`, `email.create_draft`, `chat_ott.send_message`), không nói số tiền (`ewallet.transfer`), không nói giờ nhắc (`reminders.create`), không nói con số (`fitness.set_goal`, `home_energy.set_alert`).
      - So với nhãn thật: hỗn hợp (tool, tham số hỏi) trùng **0,96**; lệnh tra trước khi hỏi trùng **0,94**; đứng một mình / kèm việc khác: sinh 63% / 37%, thật 60% / 40%.
      - Ở nhãn thật, hai liên hệ trùng tên mang đúng cùng một tên và chỉ khác quan hệ (8/8 mẫu đã xem); bộ sinh làm theo.
      - 85 mẫu hỏi lại chưa phủ là các chương trình lẻ (mỗi loại 2–5 mẫu), nhiều cái cần state của app.
      - Chưa sinh câu nói cho phần này (chưa chi API). Còn phải viết: 7 app mất điểm nhiều nhất với state lấy từ `final_state`, rồi các app còn lại.
    - **Tổng chi API tới 20:58:** Anthropic 5,56 / 100 USD. Meta: 3,14 USD trong 81 USD còn lại (kiểm nghĩa 2,86 + kho tên 0,28).
    - **Lượt đo đã chạy từ 20:56** (unit `lifemate-d1lao`, thư mục `~/zac-d1-job` ở commit `e6a32cb`, log `lifemate/runs/d1lao_2026-11-09.log`): 6.071 dòng train, 19,3 triệu token; máy đang cắm sạc. Dừng: `systemctl --user stop lifemate-d1lao` (train lưu tiến độ mỗi 10 bước); chạy tiếp: `bash ~/zac-d1-job/start_d1lao.sh`.

126. **Anh: "Viết tiếp 7 app". Nhánh app đã thấy, phần 2: 6 app trên state thật; đã sinh 752 mẫu** (09/11, 21:00–21:30).
    - **Code** (`lifemate/lifemate/d1_seen.py`, nhánh `d1-program-first`, commit `b675db5`): `python -m lifemate.d1_seen build --part apps`.
      - **State:** `label.final_state[app]` của chính mẫu fit làm "vỏ" (ngữ cảnh, history, thời điểm), tức state thật của app sau khi nhãn của mẫu đó ghi; không đọc `*_environment/`. Chỉ dùng mẫu fit_random.
      - **ID đã có trong history thì dùng luôn, không đọc lại** (quy ước của nhãn thật): bộ sinh nạp các giá trị trong kết quả tool của history trước khi quyết định có đọc hay không.
      - Quy ước từng tool lấy từ nhãn fit_random: `bill_payment.pay{bill_id, source}` sau `list_bills{}`; `banking.transfer` sau `get_balance{}` + `list_beneficiaries{}`; `calendar.update_event{event_id, start, end}`; `calendar.create_event` có `end` = `start` + 1 giờ ở 67% và `location` ở 21%; `chat_ott.send_message` sau `list_chats{}`; `flights.book` sau `flights.search{origin, destination, date}` với mã sân bay.
    - **Bước so với nhãn thật trước khi sinh hàng loạt** (`d1_compare.py --ids splits/fit_random.txt`; n = 837 call thật của 6 app; 480 kịch bản sinh):

      | App | Mẫu thật | Lệnh đọc đứng trước lệnh ghi chính: thật / sinh | Ghi chú |
      |---|---:|---|---|
      | bill_payment | 101 | `pay`: 94% / 93% | bộ tham số trùng 1,00 |
      | banking | 63 | `transfer` có đủ hai lệnh đọc: 94% / 87% | `list_transactions` (2 call thật) không sinh |
      | calendar | 124 | `update_event`: 86% / 95%; `cancel_event`: 79% / 84% | `create_event` trùng 0,87; `list_events` trùng 0,87 |
      | chat_ott | 96 | `send_message`: 76% / 71% | |
      | reminders | 113 | `create`: không đọc 100% / 97% | |
      | flights | 29 | `book`: 38% / 59%; `check_in`: 57% / 95% | số mẫu thật ít |

      - **Hỗn hợp bộ tham số trùng 0,965** (tính theo tần suất call thật).
      - **Bỏ sau bước so:** `email` (trả lời và lưu trữ ở nhãn thật lấy email từ history ở 8/10 mẫu, bản sinh lại liệt kê hộp thư trước ở 85–88%; soạn nháp và gửi cần danh bạ có địa chỉ email); `flights.cancel` (3 mẫu thật đều lấy vé từ history).
      - **Còn lệch, giữ nguyên:** tỉ lệ mẫu chỉ hỏi của bill_payment, calendar, chat_ott ở nhãn thật là 26–35%, bản sinh 19–23% (phần chênh là các mẫu đọc để làm điều kiện hoặc tra giá trị cho app khác, bộ sinh chưa có).
    - **Dữ liệu đã sinh** (`~/zac-d1/lifemate/gen/d1_seen_v1.jsonl`, 752 mẫu, sha256 `154d0548f2a54e67…`):

      | Phần | Kịch bản | Qua bộ kiểm code | Bị bước kiểm nghĩa loại | Còn lại | Anthropic | Meta |
      |---|---:|---:|---:|---:|---:|---:|
      | Hỏi lại (`seenask`) | 301 | 295 | 7 | 288 | 2,36 USD | 1,44 USD |
      | Sáu app (`seen7`) | 480 | 476 | 12 | 464 | 3,70 USD | 1,80 USD |

      - Số mẫu theo app: phone 96, reminders 95, chat_ott 87, sms 83, flights 80, calendar 79, bill_payment 76, banking 75, ewallet 52, email 10 (chỉ phần hỏi lại), home_energy 10, fitness 9.
      - Thử dựng dữ liệu train `fit_random` + file này: 4.150 dòng thật + 2.410 dòng D1.
    - **Tổng chi API tới 21:30:** Anthropic **11,61 / 100 USD**; Meta **6,38 USD trong 81 USD còn lại**.
    - **Luật giữ/bỏ của nhánh này đã ghi ở entry 124** (fit_random + dữ liệu này so với fit_random, dev_random, ít nhất 2 seed mỗi bên cùng máy; chữ PhoWhisper-ft ≥ +3,0, chữ chuẩn không giảm quá 2,0). **Chưa train:** cần 4 lượt (2 mốc + 2 có D1) trên cùng một máy, mỗi lượt khoảng 3,5–4,5 giờ trên một RTX 4090 hoặc 10–13 giờ trên laptop. Laptop đang bận lượt dev_lao; máy anh trai bận tới khoảng 16:30–20:30 ngày 10/11. Anh quyết chạy ở đâu (B42).
    - **Lượt đo dev_lao trên laptop** (seed 0 chạy từ 20:56): 380 bước; lúc 21:27 ở bước 15, tốc độ 589 token/giây, còn khoảng 520 phút train. Ước lại: seed 0 có điểm khoảng 09:00 ngày 10/11, seed 1 khoảng 21:00 ngày 10/11 (entry 125 ghi 19:00 cho cả hai, sớm hơn thực tế).
    - **Chưa làm:** các app còn lại trong 46 app (ngoài 6 app và phần hỏi lại); kịch bản điều kiện và tra giá trị; dữ liệu cho 11 app public (chờ điểm seed 0 của lượt dev_lao).

127. **Anh quyết B42 trong một phiên phụ; kế hoạch bản cuối và luật thay bản nộp** (09/11, 21:35–21:40).
    - **Nguồn:** tin nhắn từ một phiên Claude phụ (fork của phiên này) chuyển lời Anh, nguyên văn: "Bỏ 4 lượt đo app đã thấy." Phần kế hoạch dưới đây là đề xuất của phiên phụ mà Anh chọn theo; phiên phụ không sửa file, không chạy gì. Claude ở phiên này chưa nghe trực tiếp từ Anh, nên nêu lại hai điểm cần Anh xác nhận ở cuối mục.
    - **Quyết định:**
      1. **Bỏ 4 lượt đo nhánh app đã thấy.** `d1_seen_v1.jsonl` (752 mẫu) giữ lại, không train trong đợt này, không trộn vào bản cuối. Không viết tiếp 34 app còn lại trước 13/11. Luật ở entry 124 cho nhánh này vì vậy không được áp; hiệu quả của dữ liệu app đã thấy **chưa được đo**.
      2. **Sinh dữ liệu cho 11 app public ngay**, không chờ điểm seed 0 của lượt dev_lao. Nếu lượt dev_lao trượt luật ở entry 125 thì bỏ dữ liệu này.
      3. **Đợt GPU còn lại trên máy anh trai** (rảnh khoảng 16:30–20:30 ngày 10/11) chỉ chạy **2 lượt bản cuối**: đủ 1.545 mẫu train + dữ liệu 11 app public, seed 0 và 1, rồi làm file public (hạn 25 giây, D5 bật). Gói và file hướng dẫn do Leader đóng (công cụ đóng gói ở máy Leader).
    - **Luật thay bản nộp, viết trước khi train (E6):**
      - **Câu hỏi:** bản train thêm dữ liệu D1 của 11 app public có hơn bản đang nộp trên public không.
      - **Mốc:** 52,68 (bản 05/11 + D5, entry 119).
      - **Thay bản nộp khi:** trung bình điểm public của 2 seed **≥ 54,18** (52,68 + 1,5). Thấp hơn thì nộp bản 05/11 + D5, hoặc nhánh thắng của đợt A1–A3 nếu có.
      - **Điều kiện trước:** lượt dev_lao (entry 125) phải đạt luật của nó; trượt thì không train bản cuối với D1.
      - **Chi phí:** API ước dưới 28 USD (Anthropic) và dưới 14 USD (Meta); sổ chi trước khi chạy: Anthropic 11,61 / 100 USD, Meta 6,38 / 81 USD. GPU: 2 lượt trên 2 card của máy anh trai.
    - **Hai điểm Claude nêu để Anh xác nhận:**
      - **Thời điểm:** lượt dev_lao cho điểm seed 0 khoảng 09:00 và seed 1 khoảng 21:00 ngày 10/11. Luật của nó cần trung bình 2 seed. Nếu máy anh trai rảnh lúc 16:30–20:30 mà bắt đầu ngay thì lúc đó mới có seed 0.
      - **Số mẫu:** lượt dev_lao chỉ kiểm mật độ khoảng 105 mẫu mỗi app (633 mẫu sinh trên 1.283 mẫu thật). Claude sinh 200 kịch bản mỗi app (2.200) thay vì 300; bản cuối dùng bao nhiêu thì Anh và Leader chốt khi đóng gói.

128. **Anh: "Seed 0 đạt là chạy"** (09/11, 21:45).
    - Claude nêu ở entry 127 rằng luật của lượt dev_lao cần trung bình 2 seed, trong khi máy anh trai rảnh trước khi có seed 1. Anh quyết: **chạy 2 lượt bản cuối khi mới có seed 0, nếu seed 0 đạt.**
    - **Điều kiện bắt đầu bản cuối, sửa trước khi có kết quả nào:** `q4b4_lao_d1_s0` đạt **cả hai** ngưỡng của entry 125: chữ PhoWhisper-ft ≥ 44,1 **và** chữ chuẩn ≥ 50,2. Seed 0 không đạt thì không gửi gói, dừng D1 cho app mới.
    - **Hệ quả cần nhớ khi đọc kết quả:** một seed có độ lệch chuẩn khoảng 1,8 điểm quanh mức thật của công thức (entry 117), nên quyết định theo một seed dễ sai hơn theo hai. Seed 1 vẫn chạy tiếp trên laptop (xong khoảng 21:00 ngày 10/11) để kiểm lại; nếu trung bình 2 seed trượt luật thì ghi lại, còn luật thay bản nộp (public trung bình 2 seed ≥ 54,18) vẫn là cửa cuối.
    - **Gói cho máy anh trai:** `make_cloud_bundle.sh` chạy được trên laptop này (bản cuối không cần file lý lẽ D2), nên Claude đóng gói khi dữ liệu public xong; không cần Leader. Anh tải gói lên thư mục Drive và gửi file hướng dẫn cho anh trai.

129. **Dữ liệu D1 cho 11 app public; gói và file hướng dẫn cho 2 lượt bản cuối** (09/11, 21:40–22:35).
    - **Dữ liệu** (`~/zac-d1/lifemate/gen/`):
      - 2.200 kịch bản (200 mỗi app, seed 11, kho tên đã mở rộng: 721 tên khác nhau được nói ra). Phân bố nhãn: hỏi lại 11,6%, rỗng 10,8%, làm 66,9%, chỉ hỏi 10,8%; 1,91 call mỗi mẫu.
      - `claude-opus-5-5` viết 2.387 câu (2.200 câu chính + 187 câu lượt trước): 2.346 qua bộ kiểm code; **18,51 USD (Anthropic)**.
      - `muse-spark-1.3` kiểm nghĩa 2.346 câu, loại 21; **8,75 USD (Meta)**.
      - **`d1_pub_v1.jsonl`: 2.139 mẫu** (187–199 mỗi app; sha256 `c7b1b002ceab580c…`).
      - **`d1_pub_v1_105.jsonl`: 1.155 mẫu**, rút ngẫu nhiên 105 mỗi app (sha256 `c22b423e1ccedef6…`). Đây là mật độ mà lượt dev_lao đang đo (633 mẫu cho 6 app). **Bản cuối mặc định dùng file này**; muốn dùng cả 2.139 mẫu thì đặt `D1=gen/d1_pub_v1.jsonl`, nhưng mật độ đó chưa được đo.
      - Gợi ý cách nói "chêm từ tiếng Anh" đã sửa (bỏ "check") vì nó làm model viết thêm việc "check lại giùm".
    - **Script** (nhánh `d1-program-first`, commit `73efbab`): `final_train.sh` nhận `D1_SAMPLES`; `final_d1_run.sh` train seed 0 và 1 (mỗi seed một card) trên đủ 1.545 mẫu train + file D1, rồi làm file public (hạn 25 giây, D5 bật), đóng `~/zac_v6_results.tar.gz`.
      - Các dòng train của mẫu thật **giống từng byte** bản đang nộp: sha256 của `sft/all_q4b.jsonl`, `fit_random`, `fit_lao`, `dev_random`, `dev_lao` dựng bằng code mới đều trùng file cũ. Dòng D1 nối thêm phía sau.
      - Với file 105 mỗi app: 4.874 dòng thật + 3.707 dòng D1 = 8.581 dòng, khoảng 540 bước.
    - **Gói** (đóng trên laptop bằng `make_cloud_bundle.sh`, không cần máy Leader): `~/zac_cloud_bundle_20261110_d1final.tar.gz`, **268.666.315 byte**, sha256 `a199db3e23d6274d2fb8fc11126bc7b8c85e7a0f9a23ea67192f05d3c75f44eb`, code ở commit `73efbab`. Chứa dữ liệu thi (không audio), hai file D1, transcript public của bản 05/11.
      - Đã giải nén thử: 2.302 file khớp bảng kê, dựng được dữ liệu train từ gói; bản thử đã xoá.
      - **Gói có dữ liệu thi: chỉ đưa lên thư mục Drive của đội (đang phải ở chế độ "Hạn chế", B34).**
    - **File hướng dẫn cho AI bên máy anh trai:** `cloud_results/anh_trai/BROTHER_AI_GUIDE_D1FINAL_2026-11-10_EN.md` (tiếng Anh, ngoài git vì có link Drive, quyền 600). Khác bản trước ở mục 1: **chỉ bắt đầu khi (a) đợt cũ `~/zac_v5` đã in `XONG` và hai card rảnh, (b) Anh báo "go"**. Thời gian ước: cài đặt 20–45 phút, rồi khoảng 5 giờ train + 1 giờ làm file public, hai seed song song; tổng 6–7 giờ.
    - **Tổng chi API tới 22:35:** Anthropic **30,12 / 100 USD**; Meta **15,14 USD trong 81 USD còn lại**.
    - **Lượt dev_lao trên laptop:** 22:26 ở bước 65/380, 619 token/giây, còn khoảng 435 phút train; seed 0 có điểm khoảng 08:30 ngày 10/11.
    - **Trình tự ngày 10/11:** (1) khoảng 08:30 Claude đọc điểm seed 0 và áp điều kiện ở entry 128; (2) đạt thì Anh báo anh trai "go" khi đợt A0–A3 xong (khoảng 16:30–20:30); (3) hai file public về thì Anh nộp, áp luật 54,18 ở entry 127.

130. **Anh: "Cả 2.139 mẫu". Gói bản cuối đóng lại** (09/11, 22:38–22:42).
    - **Quyết định của Anh:** bản cuối train trên đủ 1.545 mẫu thật + **cả 2.139 mẫu** `d1_pub_v1.jsonl`, không dùng bản 105 mỗi app.
    - **Điều Claude đã nêu trước khi Anh chọn, ghi lại để đọc kết quả cho đúng:** lượt dev_lao chỉ đo mật độ khoảng 105 mẫu mỗi app (dòng D1 chiếm 33% dữ liệu train của lượt đó). Với 2.139 mẫu, dữ liệu train có 4.874 dòng thật + 6.866 dòng D1 (58% là D1); mật độ này **chưa được đo** trên dev. Cửa kiểm duy nhất cho nó là luật public 54,18 ở entry 127.
    - **Code:** `final_d1_run.sh` mặc định `D1=gen/d1_pub_v1.jsonl` (nhánh `d1-program-first`, commit `efd09f1`).
    - **Gói mới:** `~/zac_cloud_bundle_20261110_d1full.tar.gz`, **268.666.293 byte**, sha256 `d02a3c044bc8f92c539ad96d0787a9bd4c971a2da97b402eb7dd27257ca90fcc`. Giải nén thử: 2.302 file khớp bảng kê, lệnh chạy mặc định trỏ tới file 2.139 mẫu. **Gói `zac_cloud_bundle_20261110_d1final.tar.gz` (entry 129) đã xoá khỏi laptop; nếu Anh đã tải nó lên Drive thì xoá đi và tải gói mới.**
    - **File hướng dẫn** `cloud_results/anh_trai/BROTHER_AI_GUIDE_D1FINAL_2026-11-10_EN.md` đã sửa: tên gói, kích thước, sha256, dòng mốc `D1 samples: 2139 rows, sha256 c7b1b002ceab580c`, khoảng 730 bước mỗi seed, thời gian **8–9 giờ** (cài đặt 20–45 phút, train khoảng 7 giờ, file public khoảng 1 giờ; hai seed song song).
    - **Lịch:** nếu máy anh trai bắt đầu lúc 16:30–20:30 ngày 10/11 thì hai file public về khoảng 01:00–05:30 ngày 11/11.
131. **Lượt dev_lao D1 trên laptop xong (ghi bù; kết quả có lúc 15:33 ngày 10/11)** (ghi 11/11, 13:46).
    - **Điểm dev_lao (262 mẫu, hạn 60 giây)**, từ `lifemate/runs/sft_q4b4_lao_d1_s{0,1}{,_asr}_score.json`:

      | | Chữ PhoWhisper-ft | Chữ chuẩn |
      |---|---:|---:|
      | seed 0 (`q4b4_lao_d1_s0`) | 45,14 | 55,06 |
      | seed 1 (`q4b4_lao_d1_s1`) | 42,68 | 56,58 |
      | **Trung bình** | **43,91** | **55,82** |
      | Mốc 3 lượt cũ (entry 125) | 41,10 | 52,17 |
      | Ngưỡng (mốc + 3,0 / mốc − 2,0) | 44,1 | 50,2 |

    - **Theo entry 128:** seed 0 đạt cả hai ngưỡng (45,14 ≥ 44,1; 55,06 ≥ 50,2), nên bản cuối được chạy.
    - **Kiểm lại bằng 2 seed (luật gốc ở entry 125):** chữ chuẩn đạt rõ (+3,65 so với mốc). Chữ PhoWhisper-ft +2,81 so với mốc, thiếu 0,19 so với ngưỡng +3,0. Tức là trượt sát nút luật gốc, nếu chưa tính lượt A0 của máy anh trai vào mốc. Theo entry 128 thì chỉ ghi lại; cửa cuối vẫn là luật public 54,18 (entry 127).
    - Hai seed lệch nhau 2,46 điểm ở chữ ASR, gần độ lệch 2,5 đã đo ở entry 117.
    - Thời gian (agent, laptop, hạn 60 giây): trung bình khoảng 8 giây, p95 khoảng 14 giây; lâu nhất 34,1 giây (seed 1, chữ ASR).
132. **Anh: "File train từ máy anh tôi đã được đưa lên drive, kiểm tra thử kết quả"** (11/11, 13:42–13:46).
    - **Trên Drive** (Claude xem bằng Chrome của Anh, chỉ tải một file 53 KB):
      - **Chưa có file kết quả train** `zac_v5_results.tar.gz` (adapter và điểm của A0–A3; mục 8 của hướng dẫn) hay báo cáo của đợt này. Tìm theo tên trên toàn Drive cũng không thấy.
      - **Chỉ có thêm `zac_v5_d5_public.tar.gz`**: 54.359 byte, tài khoản anh trai tạo ngày 11/11; sha256 `cfdce674…`. Bên trong là file public của adapter đang nộp với D5 (`pub_c0_guard.jsonl`, mục 6 của hướng dẫn).
      - **Gói bản cuối `zac_cloud_bundle_20261110_d1full.tar.gz` không có trên Drive** (B43 chưa xong); gói vẫn nằm trên laptop.
      - Quyền của các file vẫn là "ai có link đều sửa được" (B34 chưa xong).
    - **Lịch thật của máy anh trai:** lượt D5 chạy 18:58–20:24 ngày 10/11 (giờ New York), cùng lúc với đầu giai đoạn 1 (`brother_run.sh` chạy hai việc này song song). Vậy giai đoạn 1 bắt đầu khoảng 18:30–19:00 ngày **10/11**, không phải 09/11 như entry 125 ghi. Giai đoạn 1 khoảng 17 giờ, xong khoảng 12:00 ngày 11/11; giai đoạn 2 (nếu có nhánh thắng) thêm 4–8 giờ, xong khoảng 16:00–20:00 ngày 11/11. Hai lượt bản cuối D1 (8–9 giờ) chỉ chạy sau đó: nếu bắt đầu ngay thì xong khoảng 01:00–05:00 ngày 12/11.
    - **Kiểm file D5 của máy anh trai** (giải nén ở `cloud_results/anh_trai/v5_d5_2026-11-11/x/`, ngoài git):
      - Kiểm định dạng `ok`: 634 dòng, 0 lỗi schema, 634 dòng có `time`, 48 dòng không gọi tool.
      - Cùng code với lượt laptop (`code_sha256` trùng), cùng adapter (`q4b4_all`, sha256 `6b9e347a…`), cùng torch 2.15.0, transformers 5.21.0, peft 0.21.2, cùng tham số (4-bit, hạn 25 giây, seed 0, D5 bật). Chữ ASR giống hệt từng chữ ở cả 1.933 file audio.
      - **So với file D5 của laptop (public 52,68): 581/634 dòng giống hệt.** 53 dòng khác: 8 dòng do giới hạn 25 giây (bên này là phần đầu của bên kia); **45 dòng còn lại do khác GPU** (RTX 4090 so với RTX 4070 Laptop). Phép tính 4-bit trên hai GPU lệch nhau rất nhỏ, đủ đổi lựa chọn của model ở chỗ hai token gần ngang nhau. Trên cùng laptop, hai lượt B28 chỉ khác 1/634 dòng (entry 115).
      - Thời gian trên RTX 4090 (ASR + agent): trung bình 9,5 giây (laptop 10,3), p95 18,9, lâu nhất 25,1; 5 mẫu quá 25 giây (laptop 9).
    - **Hệ quả:**
      - Máy chấm RTX 5090 cũng sẽ đổi vài chục dòng so với file 52,68. Điểm trên máy chấm có thể lệch khỏi 52,68, lên hoặc xuống; chưa đo được bao nhiêu.
      - **Luật thay bản nộp (entry 127) đang so file của máy anh trai với mốc 52,68 của laptop**, tức so khác máy (trái E5). Nộp file `pub_c0_guard.jsonl` này lên public cho mốc cùng máy: nếu nó lệch nhiều so với 52,68 thì cần tính lại mốc trước khi áp luật 54,18. Đây cũng là số đo duy nhất cho biết điểm lệch bao nhiêu khi đổi GPU (B44).
133. **Anh: "Claude tải lên" (gói bản cuối lên Drive). Claude không tải được** (11/11, 13:50–13:59).
    - **Gói đã kiểm lại:** `~/zac_cloud_bundle_20261110_d1full.tar.gz`, 268.666.293 byte, sha256 `d02a3c04…ca90fcc`, khớp file hướng dẫn `BROTHER_AI_GUIDE_D1FINAL_2026-11-10_EN.md`.
    - **Vì sao không tải được:** công cụ tải file của Claude trong Chrome chỉ nhận tối đa 10 MB mỗi lần; nút "File upload" của Drive mở hộp chọn file của hệ điều hành mà Claude không điều khiển được; laptop không có `rclone`. Claude không chia nhỏ gói, vì AI bên máy anh trai sẽ phải ghép lại và hướng dẫn phải sửa.
    - **Cách Anh tải (khoảng 1 phút thao tác):** trong Chrome trên laptop, mở thư mục ZAIC_2026 → New → File upload → bấm Ctrl+L, dán `/home/truyen-anh-thach/zac_cloud_bundle_20261110_d1full.tar.gz` → Open. Drive sẽ báo khoảng 256 MB (Drive tính MB theo 1.024; gói `…_arms` 251.610.252 byte hiện là 240 MB).
    - **Cách khác cho lần sau:** cài `rclone` (bản chính thức) và Anh cấp quyền Google Drive cho nó một lần trong trình duyệt; sau đó Claude tải file lớn bằng dòng lệnh. Cần Anh đồng ý cả việc tải `rclone` lẫn việc cấp quyền.
    - **Đính chính entry 122:** thư mục ZAIC_2026 **thuộc tài khoản của Anh** (Drive ghi "Owned by you"); gói `…_arms` bên trong thì do Leader tải lên. Vậy B34 (khoá thư mục) là việc của Anh: Manage access → thêm tài khoản anh trai dùng để tải (tài khoản đã tải file D5 lên) → General access → "Restricted". Quyền hiện tại vẫn là "Anyone on the internet with the link can edit".
134. **Anh: "Tôi đã tải lên rồi". B43 xong** (11/11, 14:03).
    - Claude kiểm trên Drive (chỉ xem): `zac_cloud_bundle_20261110_d1full.tar.gz` nằm trong thư mục ZAIC_2026; Drive hiện **256,2 MB**, khớp 268.666.293 byte (Drive tính MB theo 1.024); chủ sở hữu là tài khoản Anh; tạo ngày 11/11.
    - Drive không hiện sha256. AI bên máy anh trai kiểm sha256 `d02a3c04…ca90fcc` sau khi tải về, theo file hướng dẫn `BROTHER_AI_GUIDE_D1FINAL_2026-11-10_EN.md`.
    - **Theo hướng dẫn, anh trai chỉ bắt đầu khi (a) đợt v5 đã in `XONG` và hai card rảnh, (b) Anh báo "go".** Theo entry 132, đợt v5 xong khoảng 16:00–20:00 hôm nay; hai lượt bản cuối mất 8–9 giờ, nên xong sớm nhất khoảng 01:00–05:00 ngày 12/11.
    - Quyền của gói vẫn là "Anyone on the internet with the link can edit" (B34 chưa làm).
135. **Anh chuyển tin anh trai: đã tải lên kết quả đợt A0–A3. Claude tải về, kiểm và áp luật** (11/11, 14:50–15:00).
    - **File** (ở `cloud_results/anh_trai/v5_results_2026-11-11/`, ngoài git): `zac_v5_results.tar.gz` 461.616.514 byte, sha256 `9fc913b2…76e8`, khớp số anh trai báo; giải nén ở `x/` (không có symlink hay đường dẫn ra ngoài); báo cáo `ZAIC_arms_report_2026-11-11.md` 4.675 byte.
    - **Lịch thật:** máy 2× RTX 4090 của anh trai, bắt đầu 18:49 ngày 10/11, xong (`XONG`) 14:09 ngày 11/11. Trước đó chạy hỏng trên một máy 2× RTX 3090 (driver 570 không chạy được torch 2.15 cu132), không train gì ở đó.
    - **Sự cố và cách anh trai xử lý (khác công thức, anh trai báo rõ):** lượt đầu có 4 lượt train hỏng vì cache Hugging Face trên ổ dùng chung mất file trọng số của Qwen3-4B-Thinking và Qwen3.5 sau bước kiểm cài đặt; chạy offline nên không tải lại được. Anh trai tải lại hai model **đúng revision đã ghim** (`768f209d…` và `efe91c59…`) vào cache trên ổ cục bộ rồi chạy lại đúng lệnh resume. Không đổi code, file nhánh, seed hay tham số. **Claude thấy chấp nhận được:** trọng số cùng revision, công thức không đổi.
    - **Điểm dev_lao (262 mẫu, hạn 60 giây), Claude tính lại từ các file điểm, khớp `arms_decision.txt`:**

      | Nhánh | Model | seed 0 (chuẩn / ASR) | seed 1 (chuẩn / ASR) | Trung bình chuẩn | Trung bình ASR | Kết luận |
      |---|---|---|---|---:|---:|---|
      | A0 | Qwen3-4B-Instruct (đối chứng) | 49,86 / 40,09 | – | 49,86 | 40,09 | mốc |
      | **A1** | **Qwen3.5-4B text-only** | **63,20 / 47,44** | **60,83 / 47,29** | **62,02** | **47,36** | **THẮNG** (+7,27 so với A0, [+2,32; +12,27]) |
      | A2 | Qwen3-4B-Thinking + D2 | 50,08 / 35,25 | 45,48 / 34,17 | 47,78 | 34,71 | thua |
      | A3 | Qwen3-4B-Instruct + D2 | 44,85 / 34,15 | 41,97 / 33,80 | 43,41 | 33,97 | thua |

      - Mốc = 3 lượt cũ + A0: chữ chuẩn 51,59, chữ ASR 40,84. Thắng khi chữ ASR ≥ 43,84 và chữ chuẩn ≥ 49,59. A1 qua cả hai, hai seed sát nhau (47,44 và 47,29).
      - A0 trên máy này (40,09 / 49,86) nằm trong khoảng của 3 lượt cũ, nên máy anh trai cho kết quả ngang các máy trước.
      - **D2 (lý lẽ `<think>`) làm giảm điểm** ở cả model Instruct lẫn Thinking: −6,1 và −5,4 trên chữ ASR. Không dùng D2.
    - **Giai đoạn 2 (A1 train trên đủ 1.545 mẫu, 2 seed, mỗi seed khoảng 4 giờ 16 phút train + 1 giờ 15 phút file public):**
      - `public_f_a1_q35t_lao_s0.jsonl` và `…_s1.jsonl` (trong `x/lifemate/runs/`): 634 dòng, 0 lỗi schema, có `time`, D5 bật, hạn 25 giây, 4-bit, cùng chữ ASR của bản 51,16.
      - Thời gian trên RTX 4090 (ASR + agent): trung bình 8,5 và 8,4 giây (bản đang nộp trên cùng máy: 9,5), lâu nhất 25,05; 2 và 1 mẫu quá 25 giây.
      - Hai seed giống nhau 322/634 dòng; mỗi seed giống file 52,68 chỉ khoảng 233–247 dòng (model khác hẳn).
      - Adapter `ckpt/f_a1_q35t_lao_s{0,1}/final` nằm trong file kết quả.
    - **Luật nộp cho A1, Claude ghi trước khi có điểm public** (theo đề xuất (c) ở entry 117 và cùng ngưỡng với entry 127): A1 thay bản đang nộp khi **trung bình public 2 seed ≥ 54,18** (52,68 + 1,5) **và BTC chấp nhận cách đếm tham số bản text-only**. Nếu file mốc cùng máy (B44, `pub_c0_guard.jsonl`) lệch khỏi 52,68 quá 0,5 thì dùng điểm của nó + 1,5. Anh và Leader xác nhận luật này.
    - **Điều kiện về tham số (RANKING §2, HANDOFF):** Qwen3.5-4B text-only có 4.205.751.296 tham số (Apache-2.0); cộng PhoWhisper-large-ft 1,54B thì khoảng 5,75B, dưới trần 6B, LLM dưới 5B. Nhưng checkpoint gốc `Qwen/Qwen3.5-4B` có 6,26B. HANDOFF ghi A1 chỉ dùng được khi BTC đồng ý cách đếm. **Nhật ký chưa ghi BTC đã trả lời.**
    - **Kiểm lại luật dev_lao của D1 (entry 125) khi tính A0 vào mốc:** mốc mới 40,84 / 51,59, ngưỡng 43,84 / 49,59. D1 trung bình 2 seed 43,91 / 55,82 → **qua** (chữ ASR hơn ngưỡng 0,07). So với A1 thì D1 trên Qwen3-4B yếu hơn nhiều (chữ ASR 43,91 so với 47,36).
    - **Lượt kế tiếp cho máy anh trai (đang rảnh từ 14:09; gói `…d1full` đã trên Drive):**
      - `final_train.sh` nhận biến `MODEL` và `LORA_TARGETS`, và `final_d1_run.sh` không ghi đè hai biến này. Vậy **cùng gói đó train được Qwen3.5 + D1**, chỉ đổi lệnh chạy (thêm `MODEL`, `LORA_TARGETS` như nhánh A1, và `HF_HOME` trỏ tới cache cục bộ anh trai đã dựng).
      - Thời gian ước: dữ liệu 4.874 dòng thật + 6.866 dòng D1, gấp khoảng 2,4 lần giai đoạn 2 của A1 → khoảng 10 giờ train + 1 giờ 15 phút file public mỗi seed; hai seed song song. Bắt đầu khoảng 16:00 thì xong khoảng 03:30 ngày 12/11.
      - Bản đã đóng gói (Qwen3-4B + D1) mất 8–9 giờ.
      - Qwen3.5 + D1 chưa được đo trên dev. Luật Claude đề xuất, ghi trước: Qwen3.5 + D1 thay A1 khi trung bình public 2 seed ≥ trung bình public của A1 + 1,5.
136. **Anh hỏi bốn việc: đã có file public mới chưa, liên hệ BTC thế nào, hướng dẫn v6 nằm đâu (anh trai có 3 máy rảnh, Anh muốn chạy cả hai hướng trong lúc chờ BTC), và hạn Docker theo giờ Buffalo** (11/11, 15:40–15:51).
    - **Quyết định của Anh:** chạy **cả hai** lượt ở B46 cùng lúc, mỗi lượt một máy (B46 xong).
    - **File public mới (B45)**, gom ở `cloud_results/nop_public_2026-11-11/` (ngoài git), cả 3 đều 634 dòng, có `time`:
      1. `1_A1_qwen35_seed0.jsonl`, 2. `2_A1_qwen35_seed1.jsonl`: A1 giai đoạn 2 (entry 135).
      3. `3_C0_moc_cung_may_anh_trai.jsonl`: bản đang nộp + D5, chạy trên máy anh trai; mốc cùng máy (B44, entry 132).
      - Vòng public cho nộp tối đa 5 lần mỗi ngày.
    - **Liên hệ BTC:** trang cuộc thi `challenge.zalo.ai` chỉ ghi một kênh hỗ trợ: **email `aichallenge@zalo.me`** (mục FAQ "How do I receive technical support?" và chân trang). Facebook và LinkedIn ở chân trang là trang tuyển dụng của Zalo. Portal LifeMate có các mục Overview, Public Leaderboard, Public Submissions, Test Solution, Rule, Submission Guidance; không có diễn đàn.
    - **Thể lệ, mục Rule trên portal (Claude đọc 11/11):**
      - cả hệ thống (ASR, LLM, mọi thành phần) dưới 6B tham số; LLM dưới 5B, ngữ cảnh tối đa 16.384 token;
      - mỗi mẫu tối đa 30 giây, máy chấm 1× A30 (Docker Guide thì ghi RTX 5090; đây là câu hỏi 3 cho BTC);
      - nếu chạy lại khác kết quả đã nộp, BTC chạy image 5 lần và lấy điểm trung bình. Entry 132 cho thấy đổi GPU làm khác khoảng 7% số dòng, nên điểm private có thể được tính bằng trung bình 5 lần chạy của BTC;
      - hoà điểm thì xét F1 của tool_calls (bỏ qua hash), rồi thời gian trung bình mỗi mẫu.
    - **Số tham số khi dùng A1:** Qwen3.5-4B text-only 4.205.751.296 + LoRA 60.948.480 (adapter đang nộp: 66.060.288) + PhoWhisper-large-ft khoảng 1,54B, tổng khoảng 5,81B.
    - **Hạn theo giờ Buffalo** (EST, UTC−5; trùng giờ máy laptop). Claude quy đổi bằng `TZ=America/New_York date`; mốc GMT+7 lấy từ trang cuộc thi:

      | Mốc (GMT+7) | Giờ Buffalo |
      |---|---|
      | Khoá sửa thành viên đội: 00:00 ngày 16/11 | 12:00 trưa Chủ nhật 15/11 |
      | **Nộp Docker: 23:59 ngày 16/11** (tối đa 2 lần, lấy lần cuối; link Drive "Anyone with the link" kèm md5) | **11:59 trưa thứ Hai 16/11** |
      | Phát private test: 11:00 ngày 20/11 | 23:00 thứ Năm 19/11 |
      | Nộp kết quả private: 23:59 ngày 23/11 | 11:59 trưa thứ Hai 23/11 |
      | Công bố top 2: 02/12; xếp hạng cuối: 12/12 | |

      - **Đính chính:** mục 1.4 và entry 82 ghi private test phát 9:00 GMT+7 (21:00 ngày 19/11 giờ Buffalo). Trang cuộc thi ghi 11:00 GMT+7, tức 23:00 ngày 19/11 giờ Buffalo.
      - **Hạn thực tế của đội:** image nén khoảng 12 GB, tải lên Drive mất vài giờ, và nên giữ lần nộp thứ hai làm dự phòng. Vậy nên nộp lần đầu chậm nhất tối Chủ nhật 15/11 giờ Buffalo, và chốt model khoảng 13/11.
    - **Hướng dẫn cho máy anh trai:** `cloud_results/anh_trai/BROTHER_AI_GUIDE_V6_BOTH_2026-11-11_EN.md` (tiếng Anh, ngoài git vì có link Drive; thay file `…D1FINAL…`):
      - **Run Q:** Qwen3.5-4B text-only + D1 (2.139 mẫu), seed 0 và 1, trên máy đã chạy v5 (cache cục bộ đã có model đúng revision đã ghim); khoảng 12–13 giờ.
      - **Run I:** Qwen3-4B-Instruct + D1, đúng lượt mà gói đã đóng, trên máy thứ hai; khoảng 5–6 giờ. Máy thứ ba dự phòng.
      - Không sửa code trong gói. Hai máy dùng chung thư mục home, nên Run Q chạy một bản sao `final_d1_run.sh`, tạo bằng một lệnh `sed` chỉ đổi tên file khoá, file kết quả và tên lượt (`fd1q35_s0/1`). Claude đã thử trên laptop: đúng 9 dòng khác, cú pháp đạt. Biến `MODEL` và `LORA_TARGETS` giống nhánh A1; `final_train.sh` nhận hai biến này (giai đoạn 2 của v5 đã chạy cách này). Có bước kiểm tên model trong log 15 phút sau khi bắt đầu.
      - Mỗi lượt dùng cache model trên ổ cục bộ và chạy offline sau bước cài đặt (như v5), vì cache trên home dùng chung từng mất file trọng số. Bảng revision đã ghim và lệnh tải lại đúng revision nằm trong mục 8.
      - Máy driver 570 (2× RTX 3090) không chạy được torch 2.15.0 (10/11), nên hướng dẫn chỉ cho dùng máy driver từ 580.
      - Thời gian ước theo tốc độ đo ở v5 trên RTX 4090 (Qwen3-4B 2.927 token/giây, Qwen3.5 951 token/giây) và khoảng 36 triệu token mỗi seed (4.874 dòng thật + 6.866 dòng D1).
    - **Luật viết trước khi train (E6):**
      - **Run Q.** Câu hỏi: D1 có cộng thêm điểm cho Qwen3.5 trên public không. Luật: Run Q thay A1 khi trung bình public 2 seed ≥ trung bình public của A1 + 1,5. Chỉ áp khi BTC chấp nhận bản text-only. Chưa có số đo dev cho tổ hợp này (gói không có dữ liệu D1 của dev_lao), nên luật public là cửa duy nhất. Chi phí khoảng 25 giờ GPU trên máy anh trai, 0 USD.
      - **Run I.** Câu hỏi: D1 có giúp Qwen3-4B trên public không. Luật: thay bản 52,68 khi trung bình public 2 seed ≥ 54,18 (entry 127); nếu file mốc cùng máy C0 lệch khỏi 52,68 quá 0,5 thì dùng điểm C0 + 1,5. Dùng khi BTC không chấp nhận Qwen3.5. Chi phí khoảng 11 giờ GPU, 0 USD.
    - **Email soạn sẵn gửi BTC** (`aichallenge@zalo.me`; điền tên đội):

      > **Tiêu đề:** [ZAC 2026 – LifeMate] Hỏi về cách đếm tham số và máy chấm
      >
      > Chào Ban tổ chức Zalo AI Challenge,
      >
      > Đội <tên đội> (bảng LifeMate) xin hỏi 3 điểm trước hạn nộp Docker 16/11:
      >
      > 1. **Cách đếm tham số khi chỉ dùng phần ngôn ngữ của một model đa phương thức.** Đội muốn dùng `principled-intelligence/Qwen3.5-4B-text-only`: đây là checkpoint `Qwen/Qwen3.5-4B` (phát hành 02/2026, licence Apache-2.0) được nạp bằng `Qwen3_5ForCausalLM` rồi lưu lại, đã bỏ bộ mã hoá ảnh và các lớp MTP. Bản này có 4.205.751.296 tham số. Cộng ASR PhoWhisper-large đã fine-tune (khoảng 1,54B) và adapter LoRA thì cả hệ thống khoảng 5,81B. BTC đếm theo trọng số thực sự có trong image và được nạp khi suy luận (LLM 4,21B), hay theo checkpoint đa phương thức gốc?
      > 2. **Adapter LoRA không merge** (khoảng 61 triệu tham số) nạp kèm model gốc lúc suy luận: có tính vào tổng tham số không? Đội đang tính có.
      > 3. **Máy chấm và giới hạn thời gian.** Mục Rule ghi 1 × NVIDIA A30 và 30 giây mỗi mẫu, còn Docker Guide ghi 1 × RTX 5090 32 GB. Bản private sẽ chạy trên máy nào, và giới hạn 30 giây mỗi mẫu có tính trên đúng máy đó không?
      >
      > Cảm ơn Ban tổ chức.

---

## 8. Việc tiếp theo

- [ ] Anh và leader làm theo [`HUMAN_TODO.md`](HUMAN_TODO.md), trả lời 20 câu hỏi ngay trong file đó, rồi thảo luận với Claude để chốt kế hoạch nâng cấp.
- [ ] Review và merge PR `agent-pipeline` → `main`.
- [x] Đọc kết quả train qua đêm: dev_random 9,9 → 53,9 (2026-10-29).
- [x] Phân tích lỗi của checkpoint `q17b_fit_random`: Anh audit với Codex hỗ trợ, Claude đối chiếu (29/10, [`docs/EVAL_2026-10-29.md`](docs/EVAL_2026-10-29.md)). Việc hai người tự phân loại bằng mắt vẫn mở trong `HUMAN_TODO.md`.
- [x] Sửa `scripts/train_local.sh` để chọn được tập train và tập dev: [PR #2](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/2), chờ review.
- [x] Chấm step_100, step_200 và final trên đủ 233 mẫu; chọn final làm mốc (29/10).
- [ ] Review và merge PR #2 (người review quyết).
- [x] **Thí nghiệm B:** train `fit_lao` → chấm `dev_lao`. Final đạt 35,53; hỏi lại về tool mới được 0 điểm (29/10, EVAL mục 7).
- [x] Sửa lỗi bộ chấm khi thiếu prediction, kèm 11 test (30/10, PR #2, commit `d6208a1`).
- [x] Thiết kế D: thống kê chính sách hỏi lại, thử luật tất định, viết bộ sinh dữ liệu, chạy thử 23 mẫu (30/10, PR #3, `docs/EXPERIMENT_D.md`).
- [ ] Anh đọc tay 23 mẫu D (`lifemate/gen/review_fit_lao.md`).
- [x] D giai đoạn 1 (D v1, 77 mẫu) và giai đoạn 1b (bộ lọc v2, D-train 77 mẫu) (30/10, `docs/D_PHASE1_2026-10-30.md`, `docs/D_PHASE1B_2026-10-30.md`).
- [x] Anh quyết: giai đoạn 2 ngay với D-train 77 mẫu (khuyến nghị), hay giai đoạn 3 (nới luật) trước. *Anh chọn giai đoạn 2 (30/10).*
- [x] Giai đoạn 2 của D: xong 31/10 03:09. **D bị loại**, B-up thắng; xem `docs/D_PHASE2_2026-10-31.md` (entry 30).
- [x] **Cân lại tỉ trọng hỏi lại trên fit_random** (`q17b_random_up`, cloud; Anh bật 31/10, entry 32): dev_random không giảm quá 1 điểm thì dùng công thức B-up làm mặc định. *(31/10 20:19, laptop: giảm 2,72, không giữ; entry 49.)*
- [x] Anh quyết ưu tiên sau D: **baseline đầu-cuối** (30/10, entry 21).
- [x] **Baseline đầu-cuối** ([PR #4](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/4)): xong 31/10 (entry 31). ASR làm mất khoảng 20 điểm.
- [x] Anh quyết có nộp `lifemate/runs/e2e_public_turbo.jsonl` lên public không (Anh tự nộp). *(Leader nộp 31/10: 25,93, entry 46. Lần 2 với ASR fine-tune: 35,24, entry 53. Lần 3 với agent 4B: 45,39, entry 62.)*
- [x] **Fine-tune ASR** trên wav của fit (leader, cloud); đánh giá bằng điểm agent và độ đúng slot. *(01/11: hai Colab xong; gộp 23,99 → 33,07 với Whisper-turbo fine-tune, được chọn; entry 52.)*
- [ ] **Train agent trên chữ ASR** (`q17b_random_asrtrain`, cloud; Anh bật 31/10, entry 32; bản 4B `q4b_random_asrtrain` chỉ chạy khi có ≥ 4 GPU). *(1.7B xong 31/10 17:00 trên laptop: không đáng dùng, entry 48. Bản 4B chờ máy anh trai.)*
- [ ] **Từ báo cáo Codex (entry 24), chưa làm:**
  - [x] **Chốt chặn ID: đã đo** (entry 27). Gần như không thêm điểm (0 / 0 / +0,26), nên hạ xuống lưới an toàn: viết cùng phần sửa `agent.py:150`, không cần lượt GPU riêng.
  - [x] **Tách lệnh ghi sai theo nguyên nhân** (entry 28): mất nhiều nhất là thiếu lệnh ghi và ghi sai tool, rồi tới chọn nhầm ID và ngày giờ.
  - **Dữ liệu SFT nhiều vế và điều kiện** (P1 trong báo cáo Codex), kiểm chứng bằng ToolEnv; nhắm vào lỗi "tự dừng khi chưa làm đủ" (entry 28).
  - **Ngày giờ:** thử quy ước sáng/tối và "tuần này / tuần sau" (nhãn tuần trong bảng ngày, hoặc chuẩn hoá giờ nói). Cần train lại để đo, nên làm sau giai đoạn 2.
  - **Ngưỡng hỏi lại:** chỉnh ngưỡng xác suất chọn `ask_missing_info` lúc suy luận. Ngưỡng chỉnh trên tập dò từ fit, không chỉnh trên dev. Cần GPU, nên làm sau giai đoạn 2. *(31/10: hạ ưu tiên. Trần chỉ 1,2–1,7 điểm trên dev_lao, entry 30.)*
  - [x] **Sửa `agent.py:150`:** xem thời gian còn lại trước khi sinh mỗi bước, để bước cuối không vượt 30 giây. Làm trước khi đóng Docker. *(31/10: thêm trần cho mỗi bước; một mẫu sinh lặp "000…" hai bước liền mất 23,4 giây, entry 49.)* *(31/10 21:08: xong, [PR #9](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/9), kèm chốt chặn ID; entry 50.)*
  - **[Leader]** Thêm Qwen3-ASR-0.6B vào so sánh ASR; thử ITN tiếng Việt của NeMo (`r1.2.0`).
- [ ] Nếu duyệt: sinh đủ khoảng 230 mẫu D, chạy D-lao và D-random với số bước giữ nguyên (EXPERIMENT_D mục 8).
- [ ] Thiết kế D, ưu tiên hỏi lại với schema chưa thấy: dữ liệu đủ/thiếu slot trên schema đổi tên hoặc tổng hợp; thử kiểm tra tất định xem tham số bắt buộc có nguồn trong lời nói, history hoặc kết quả tool không, đo trên fit trước.
- [x] **4B 4-bit trên laptop, vòng dev_lao** (C6): +14,65 trên chữ ASR fine-tune, 4B thắng vòng này (02/11, entry 57).
- [x] **4B: quyết bằng điểm gộp 495 dòng** (C7): gộp 33,07 → 46,17, **chốt 4B** (02/11 10:13, entry 58).
- [x] **Pilot dữ liệu tổng hợp** cho app chưa thấy: code xong ([PR #11](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/11)); bài thử 20 mẫu chờ key Meta (HUMAN_TODO B13, entry 59–60). *(14:52 ngày 02/11: sinh xong 280 mẫu đạt, 11,55 USD; train + chấm dev_lao đang chạy, xong khoảng 22:30–23:00; entry 61.)* ***Xong 22:37: không đạt** (chữ ASR −2,09, chữ chuẩn −2,83); không dùng; entry 61.*
- [x] **4B học chữ trộn** (B15, entry 63–65): laptop từ 00:19 ngày 03/11 (dừng 00:37 vì máy khởi động lại, chạy tiếp 00:53), chấm dev_random xong khoảng 07:25. Qua cửa 1 thì chạy tiếp trên fit_lao để quyết bằng điểm gộp 495 dòng. *(07:30: **qua cửa 1**, chữ ASR +2,31, chữ chuẩn +0,43. Lượt fit_lao chạy từ 08:54, chấm dev_lao xong khoảng 15:40; entry 67.)* *(15:07: **không qua luật gộp**, chữ ASR gộp −0,69; bỏ chữ trộn; entry 68.)*
- [x] **Nộp bản API `xhigh` + bỏ tham số hiếm (APIs/Others)** (entry 79, HUMAN_TODO B21): **75,52**. Prompt cho Codex đã viết (entry 80).
- [x] **Codex phân tích sâu chiến lược cho 4B** (entry 80–81): báo cáo xong 14:38 ngày 04/11.
- [x] **Thí nghiệm theo báo cáo Codex** (entry 81–82; Anh duyệt 14:43): (2) 4B + chữ PhoWhisper fine-tune trên dev, chạy từ 14:44, xong khoảng 17:15 *(xong 16:06: **qua luật**, gộp 46,17 → 47,88; public **51,16** (+4,87), Docker đổi sang PhoWhisper-ft (B26), entry 83–86)*; (1) prompt `xref` trên fit_lao ([PR #14](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/14)), chạy 23:30–06:38 *(**không qua cửa 1**: dev_lao chữ ASR −1,02, chữ chuẩn −0,69; dừng, entry 87; PR #14 đã đóng 09:03, entry 88)*.
- [x] **Nộp file public bản Meta API (cột APIs/Others) để có mốc model mạnh** (entry 77): file xong 12:43 ngày 04/11, 6,75 USD. *(Anh nộp: **69,47**; phân tích mất điểm ở entry 78.)* Code ở [PR #13](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/13), chờ review.
- [x] **Train lại 4B chữ chuẩn trên đủ 1.545 mẫu, rồi làm file nộp public** (entry 66, 68): script sẵn; Anh chọn tự bật sau (15:11, HUMAN_TODO B17). *(16:27: Anh nhờ hẹn giờ; tự chạy lúc 00:30 ngày 04/11 khi đã cắm sạc; entry 72.)* *(04/11 00:13: Anh bảo chạy ngay; entry 74.)* *(04/11 07:34: xong; `runs/e2e_public_q4b_all.jsonl` 634 dòng, kiểm đạt; entry 75.)* *(04/11 12:21: public 46,29, hơn 45,39; Docker dùng `ckpt/q4b4_all/final`; entry 76.)*
- [x] **Sẵn sàng Docker** ([PR #12](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/12)): bước khởi động không tính giờ, `predict.sh` mặc định 4B 4-bit với hạn 25 giây. *(Claude review và merge vào `q4b-laptop` lúc 17:22 theo yêu cầu của Anh; entry 73.)* Còn đo trên GPU 24 GB (B16) và Dockerfile (leader, L6).
- [ ] **Sau khi chốt 4B:** file nộp public bằng 4B (HUMAN_TODO B11, Anh tự chạy; *Anh nộp 02/11: **45,39**, entry 62*); đo trên A30, kiểm nạp 4-bit hay bf16; thêm cờ 4-bit và bước khởi động vào `eval_ckpt.sh`, `train_local.sh`, `predict.sh` (entry 58).
- [ ] **Thí nghiệm A:** 2 epoch trên fit_random, để tách "thiếu ngân sách train" với "thiếu dữ liệu đa dạng".
- [ ] **Thí nghiệm C:** trong agent, giữ nguyên call JSON hỏng và nhắc khi gặp `done=false`; PR riêng, 12 phút đánh giá.
- [ ] **Thí nghiệm D:** thiết kế dữ liệu phản thực tế từ fit cho điều kiện và ranh giới hỏi lại; mọi nhãn phải qua kiểm tra thực thi.
- [ ] Quyết có tách lockbox khoảng 200 mẫu từ fit hay không.
- [ ] Nộp public lần đầu để kiểm chứng 3 giả định của bộ chấm (mục 6.1).
- [ ] Cloud:
  - Baseline zero-shot Qwen3-4B-Instruct-2507 (`scripts/cloud_baseline.sh`).
  - SFT 4B trên `all.jsonl`.
  - Thử nghiệm so sánh `--history tagged` và `--rename 0/2/4`.
- [ ] Phần ASR (leader):
  - Benchmark Whisper-turbo và PhoWhisper trên audio train: WER và độ đúng của số, giờ, tên. *(30/10: Claude chạy bản không fine-tune trên dev_random + dev_lao trong lượt đo đầu-cuối, `scripts/asr_quality.py`; leader dùng số liệu này làm điểm xuất phát.)*
  - Viết bộ chuẩn hoá chữ thành số (ITN).
  - Xuất `asr/<split>.jsonl` theo giao kèo; làm transcript k-fold cho SFT (`--asr-file`). *(Định dạng file đã có trong `lifemate/asr.py`, PR #4.)*
- [ ] Dữ liệu app tổng hợp: LLM mạnh sinh app, schema, simulator, câu yêu cầu và đáp án; chạy thật qua executor để kiểm chứng.
- [ ] **Cloud:** chạy gói train ([`docs/CLOUD_TRAIN_2026-10-31.md`](docs/CLOUD_TRAIN_2026-10-31.md), PR #6). Trước hết cần 2 lượt parity, rồi 4B trên fit_random và fit_lao với công thức 1.7B.
- [ ] Docker offline: dùng backend vLLM, đo thời gian trên GPU 24GB, chạy 5 lần kiểm tra tính tái lập. *(Lõi chạy offline: `scripts/predict.sh`, PR #4.)*

### Lộ trình tới hạn Docker 16/11

| Ngày | Việc |
|---|---|
| 1–3 | Bộ chấm, prompt, baseline, benchmark ASR *(đã xong phần agent)* |
| 4–9 | SFT v1, chốt và fine-tune ASR, nộp public lần đầu |
| 8–13 | Dữ liệu app tổng hợp, SFT v2, phân tích lỗi |
| 14–17 | Docker offline, đo thời gian, kiểm tra tái lập |
| 18–19 | Dự phòng |

### Câu hỏi mở

- Server chấm có so khớp chính xác tham số không fuzzy và tách token theo khoảng trắng như bộ chấm local giả định không?
- Licence của các model ASR tiếng Việt: một số dùng CC-BY-NC, có được dùng không?
- Có model LLM hoặc ASR nào tốt hơn phát hành trước 26/10/2026 không? *(Một phần đã có trong mục 6 của báo cáo Codex, entry 24; leader rà tiếp ở HUMAN_TODO 0.4.)*
