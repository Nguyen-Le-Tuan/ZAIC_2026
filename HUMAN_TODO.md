# Việc của người — Anh và Leader

Danh sách việc trong lúc laptop của Anh train qua đêm, và sáng hôm sau. Phần cuối là 20 câu hỏi nghiên cứu, chép từ [`docs/PIPELINE.md`](docs/PIPELINE.md).

## Cách dùng file

- Mỗi việc ghi người phụ trách: **[Anh]**, **[Leader]**, **[Cả hai]** hoặc **[Claude]**.
- Xong việc nào thì đánh `[x]` và ghi kết quả ngắn ngay dưới việc đó. Commit thẳng lên `main` (tài liệu không cần PR). Leader: `git pull` trên `main` để có bản mới nhất.
- **Bản mới nhất là mục "Ngày 31/10, chiều và tối" ngay dưới đây.** Các mục từ "0." trở xuống là việc cũ (28–30/10); việc nào còn ý nghĩa đã được chép lên mục mới.
- Code: `main` đã có code của PR #1 (merge 31/10, 14:47). Code của #2 và #3 vào `main` khi [PR #8](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/8) được merge. Các lệnh chạy trong thư mục `lifemate/`.

---

## Ngày 31/10, chiều và tối: bảng điều phối

*Claude tạo lúc 15:30 ngày 31/10 và **cập nhật mỗi khi có việc hay quyết định đổi** (lần gần nhất 20:58 ngày 09/11). Bản này thay cho mục "Ngày 31/10" viết lúc sáng sớm (kế hoạch gốc: [`docs/PLAN_2026-10-31.md`](docs/PLAN_2026-10-31.md); diễn biến trong ngày: JOURNAL entry 32–44). Tóm tắt: agent đọc chữ ASR mất khoảng 20 điểm (dev_random 53,92 → 31,69; dev_lao 35,53 → 17,14), nên **fine-tune ASR là ưu tiên số 1**.*

> **Thay đổi gần nhất** (mới nhất ở trên; chi tiết trong JOURNAL):
> - **20:58 ngày 09/11:** **Laptop bắt đầu train lượt đo D1 trên dev_lao (2 seed, khoảng 21 giờ, xong khoảng 19:00 ngày 10/11). Anh để máy cắm sạc; cần dùng máy thì chạy `systemctl --user stop lifemate-d1lao` (lưu tiến độ), xong chạy lại `bash ~/zac-d1-job/start_d1lao.sh`.** Luật giữ/bỏ: chữ PhoWhisper-ft ≥ 44,1 và chữ chuẩn ≥ 50,2 (trung bình 2 seed). Hai trần API tách riêng: Anthropic 5,56/100 USD, Meta 3,14/81 USD. Máy anh trai chạy từ 18:30, giai đoạn 1 xong khoảng 12:00 ngày 10/11 (JOURNAL entry 125).
> - **20:25 ngày 09/11:** **Model viết: `claude-opus-5-5` (B40 xong).** Sáu app của dev_lao đã vào bộ sinh; viết mù rồi so với nhãn thật: tool và ID đúng hết, bộ tham số khớp 0,845 → 0,902. **Nhánh D1 cho 46 app đã thấy đã ghi luật giữ/bỏ; một tiền đề của bản giao việc sai (`final_state` không chứa app không ghi), chờ Anh xác nhận cách thay thế (B41).** (JOURNAL entry 124)
> - **19:18 ngày 09/11:** **Bộ sinh kịch bản D1 chạy cho 11 app public; thử 3 model viết câu nói xong (0,65 USD).** Anh đọc `lifemate/gen/d1_t1_say_compare.md` và chọn model viết (B40). Còn lại của cửa 1: 6 app của dev_lao, kho tên lớn hơn, bước kiểm đổi nghĩa (JOURNAL entry 123).
> - **18:41 ngày 09/11:** **Gói train đã có trên Drive** (240 MB, Leader tải lên 08/11). **B34 gấp [Anh hoặc Leader]:** gói (và nhiều khả năng cả thư mục) vẫn để "bất kỳ ai có link đều sửa được", mà trong đó có dữ liệu thi. Chuyển sang "Hạn chế" và chỉ thêm tài khoản của Anh và anh trai; làm sau khi anh trai tải xong gói, hoặc thêm tài khoản anh trai trước (JOURNAL entry 122).
> - **18:22 ngày 09/11:** **Gói train cho máy anh trai (`zac_cloud_bundle_20261109_arms.tar.gz`, 240 MB) chỉ có trên máy Leader; Leader tải lên Drive** (thư mục để "Hạn chế", B34). Laptop không tự tạo được gói này. File hướng dẫn tiếng Anh đã điền kích thước và sha256 (JOURNAL entry 121).
> - **17:32 ngày 09/11:** **Cửa 0 của D1 đạt** (mẫu dùng app của dev_lao không có lỗi quy tắc: 94,5%, ngưỡng 80%). Một nửa số lệnh đọc trong nhãn thuộc về kịch bản, chưa kiểm; đó là việc của cửa 1. Code ở nhánh `d1-program-first`. **Anh tạo file key Anthropic (B39).** (JOURNAL entry 120)
> - **17:25 ngày 09/11:** **Public có bật D5: 52,68 (+1,61 so với 51,07). Giữ D5** theo luật viết trước; Leader đổi mặc định `SEARCH_GUARD=1` và build L9 từ bản có D5. **Leader đồng ý D1; trần API bỏ giới hạn; Claude bắt đầu cửa 0 (CPU).** Máy anh trai chạy từ khoảng 12:00, giai đoạn 1 xong khoảng 05:00–06:00 ngày 10/11 (JOURNAL entry 119).
> - **17:15 ngày 09/11:** **Anh muốn làm D1 (sinh dữ liệu) bằng key Claude và Meta; chờ Anh quyết B38.** Đợt chạy trên máy anh trai gồm 9–10 lượt train, 22–26 giờ, nên trước 13/11 chỉ còn chỗ cho khoảng một đợt nữa (JOURNAL entry 118; sửa entry 117).
> - **15:45 ngày 09/11:** **Anh đã gửi gói cho anh trai chạy giai đoạn 1 (7 lượt train, kết quả khoảng 10/11).** Claude đánh giá phương án và phân rã chỗ mất điểm (JOURNAL entry 117): mất nhiều nhất ở quyết định làm / hỏi lại / dừng (khoảng 27 điểm) và ghi sai tham số hoặc tool (khoảng 28 điểm); ASR khoảng 10,5. **Chờ Anh quyết B37.** B36 (nộp file D5) vẫn chờ.
> - **04:02 ngày 09/11:** **File public có bật D5 đã xong, Anh nộp được ngay (B36):** `lifemate/runs/pub_d5_2026-11-09/full/submission.jsonl`. 634 dòng, kiểm định dạng đạt, có `time`. 603/634 dòng giống file thử 51,07; 30 dòng khác do guard tìm lại. Guard làm mất 9 lệnh hỏi lại, nên điểm có thể lên hoặc xuống. **Giữ D5 nếu điểm ≥ 50,77** (JOURNAL entry 116).
> - **02:13 ngày 09/11:** **B28 xong: image Docker 05/11 chạy đúng trên GPU, cho cùng kết quả với lúc chạy ngoài Docker** (627/634 dòng giống file 51,16; hai lượt chỉ khác 1 dòng, do hạn 25 giây). Còn L9 (image chưa có `/code`, notebook). **D5 (search guard của Leader) đang chạy trên public, xong khoảng 04:10. Anh nộp file khi Claude báo; giữ D5 nếu điểm ≥ 50,77 (B36).** File gửi anh trai bản tiếng Anh có link Drive đã xong, còn chờ Leader gửi kích thước và sha256 của gói (JOURNAL entry 112–115).
> - **22:20 ngày 08/11:** **B28 đang chạy trong Docker trên laptop.** Image của leader nạp được và chạy được trên GPU; torch trong image có hỗ trợ RTX 5090; 3 mẫu giống hệt file 51,16. Hai lượt 634 mẫu xong khoảng 02:40 ngày 09/11. **Anh để máy cắm sạc, đừng tắt máy** (gập nắp được) (B31; JOURNAL entry 111).
> - **20:54 ngày 08/11:** **Anh đã vào nhóm `docker`, nhưng phải đăng xuất rồi đăng nhập lại (hoặc khởi động lại máy) thì B28 mới chạy được.** Ubuntu 26.04 không có `sg`/`newgrp` như Claude ghi ngày 06/11 (đã sửa). Sau đó Anh mở lại phiên này, nhắn "chạy B28" (B31; JOURNAL entry 110).
> - **20:25 ngày 08/11:** **B35 xong: file public thử bằng cấu hình nộp cuối được 51,07** (file 05/11: 51,16; −0,09, đúng phần hạn 25 giây cắt 9 dòng). Trang nộp nhận trường `time`. **Cấu hình nộp cuối đã chốt; việc còn lại là Docker (B28/B31, L9), hạn 11:59 ngày 16/11.** B34 (khoá Drive) vẫn chờ Anh (JOURNAL entry 109).
> - **20:00 ngày 08/11:** **File public thử đã xong, Anh nộp được ngay (B35):** `lifemate/runs/pub_trial_2026-11-08/full/submission.jsonl`. 634 dòng, kiểm định dạng đạt, có trường `time`. 625/634 dòng giống hệt file 51,16; 9 dòng còn lại bị hạn 25 giây cắt các lời gọi cuối, nên điểm có thể thấp hơn 51,16 tối đa khoảng 1,4 (JOURNAL entry 108).
> - **17:57 ngày 08/11:** **Anh nhờ làm một file public để nộp thử.** Claude chạy đúng cấu hình nộp cuối (giao diện BTC của PR #15, hạn 25 giây, có trường `time`) trên laptop, ngoài Docker. 3 mẫu thử giống hệt file 51,16. Đủ 634 mẫu xong khoảng 20:00, rồi Anh nộp (B35; JOURNAL entry 108).
> - **16:45 ngày 08/11:** **Pilot v2 không đạt luật ghi trước:** chữ ASR −0,46 (cần +2,0), kể cả trên đúng 6 app được sinh dữ liệu (−0,98). **Dừng hướng dữ liệu sinh, Docker giữ bản 05/11.** **Việc gấp còn lại là Docker:** B28 (B31) chưa chạy, L9 (hạn 11:59 ngày 16/11). **B34 [Anh]:** thư mục Drive đang mở cho bất kỳ ai có link, trong đó có dữ liệu thi; chuyển sang "Hạn chế" và nhờ anh trai xoá dữ liệu trên máy (JOURNAL entry 107).
> - **17:25 ngày 06/11:** **Anh đã tải gói lên một thư mục Google Drive riêng; hướng dẫn đã sửa:** anh trai lấy gói từ thư mục đó và tải kết quả lên lại đúng thư mục đó. Bản có link nằm ngoài git (`cloud_results/anh_trai/BROTHER_AI_GUIDE_PILOT_V2_2026-11-07.md`); bản trong repo không ghi link. **Anh chia sẻ thư mục cho tài khoản của anh trai với quyền "Người chỉnh sửa", giữ chế độ "Hạn chế"** (B33; JOURNAL entry 106).
> - **17:20 ngày 06/11:** **File hướng dẫn cho AI bên máy anh trai đã xong:** [`docs/BROTHER_AI_GUIDE_PILOT_V2_2026-11-07.md`](docs/BROTHER_AI_GUIDE_PILOT_V2_2026-11-07.md). File nói train gì, lệnh nào, lấy file ở đâu, gửi lại gì. Lệnh nay tự áp luật ghi trước khi chạy xong. Anh gửi file này kèm gói (B33; JOURNAL entry 105).
> - **12:47 ngày 06/11:** **Gói pilot v2 cho máy anh trai đã sẵn, sớm hơn lịch một ngày.** 202 mẫu sinh cho 6 app bị giấu, theo đúng tỉ lệ của mẫu thật (lịch sử, dùng lại ID, câu không gọi tool); 4 lượt 4-bit, mỗi bên 2 seed. Đã chạy thử và kiểm gói trên laptop. Chi 9,36 USD, tổng API 52,39/80. **Anh gửi gói và lệnh cho anh trai (B33), tối nay nếu được** (JOURNAL entry 104, [`docs/CLOUD_PILOT_V2_2026-11-07.md`](docs/CLOUD_PILOT_V2_2026-11-07.md)).
> - **11:45 ngày 06/11:** Máy anh trai chỉ chạy 1 lần mỗi ngày. **Vẫn đủ: dữ liệu sinh v2 cần 2 lần chạy** (pilot 2 seed tối 07/11; train đủ dữ liệu tối 08 hoặc 09/11), chốt model 13/11, API khoảng 25 USD. **Anh duyệt B32** (JOURNAL entry 103).
> - **11:40 ngày 06/11:** Anh hỏi train ở máy nào. **Nếu train (chỉ còn hướng dữ liệu sinh v2) thì dùng máy anh trai:** nhanh gấp 3,7 lần, chạy 2 seed cùng lúc. Laptop để kiểm Docker (B31, L9). Cần biết anh trai cho dùng máy mấy lần trước 13/11 (JOURNAL entry 102).
> - **11:35 ngày 06/11:** **Kết quả gói v3 từ máy anh trai đã về (2× RTX 4090): không có adapter nào tốt hơn để thay vào image.** 4B bf16 so với 4B 4-bit đang nộp (chữ chuẩn): dev_random +5,70, dev_lao −2,12, gộp +1,56. Cùng một công thức train trên hai máy đã lệch tới 4,21 điểm, nên các mức chênh này chưa nói được gì. **B32:** hướng (1) xong; Claude không đề xuất bf16; còn hướng (2) dữ liệu sinh v2 (JOURNAL entry 101).
> - **09:50 ngày 06/11:** **Đã tải xong file image (09:47, đủ byte, sha256 khớp); Docker 29.1.3 và NVIDIA toolkit 1.20.1 đã cài; Anh chưa vào nhóm `docker`.** Anh hỏi có phải nộp luôn bản này, không cải tiến nữa không. **Trả lời: đóng gói bản này là để có sẵn một bản chạy được; có model tốt hơn thì chỉ thay một thư mục trong image.** Nhưng hiện chưa có cải tiến nào có bằng chứng; **Anh chọn hướng ở B32** (JOURNAL entry 100).
> - **09:40 ngày 06/11:** **Leader đã gửi image (L8 xong) và đã đọc hướng dẫn Docker của BTC (L4 xong).** Anh mang máy đi lúc 11:00, nên **B28 chạy tối nay (B31, khoảng 4 giờ)**. **Trước 11:00, Anh chạy `sudo bash ~/zac-c3/b28_setup_docker.sh` và tải file image từ Drive (B30).** **Theo hướng dẫn BTC, máy chấm là RTX 5090 32 GB, CUDA 13.2; gói nộp cuối phải theo giao diện `/code/predict.sh` → `/data` → `/result/submission.jsonl`, có notebook đo thời gian, trường `time`, README và code train.** Image 05/11 chưa theo giao diện này; việc mới cho leader là L9: [`docs/BTC_DOCKER_GUIDE_2026-11-06.md`](docs/BTC_DOCKER_GUIDE_2026-11-06.md) (JOURNAL entry 99).
> - **02:04 ngày 06/11:** **B28: Anh chọn kiểm image Docker trên laptop** (không thuê GPU). **Anh cài Docker + NVIDIA toolkit (B30, 15 phút)** và gửi leader tin nhắn có sẵn; **leader gửi file image và lệnh `docker run` (L8)**. Hướng dẫn: [`docs/B28_LAPTOP_DOCKER_2026-11-06.md`](docs/B28_LAPTOP_DOCKER_2026-11-06.md) (JOURNAL entry 98).
> - **00:47 ngày 06/11:** **B29 xong: public 49,65, thấp hơn 51,16. Docker giữ `ckpt/asr_phoft/merged`**; không phải gửi leader thư mục mới. Image leader đã build là bản cuối về model. **Việc còn lại cho Docker: B28** (kiểm image trên GPU 24 GB) (JOURNAL entry 95).
> - **18:15 ngày 05/11:** **B27 xong. Anh hoặc leader nộp B29:** `~/zac-c3/lifemate/runs/e2e_public_q4b_all_phoftall_fix0497.jsonl` (PhoWhisper-ft học thêm dev; WER 54 mẫu 7,65 → 7,08). ≥ 51,16 thì Docker đổi ASR. `predict.sh` 3 mẫu trên laptop đạt `"ok": true`, giống hệt file 51,16 (JOURNAL entry 94).
> - **17:45 ngày 05/11:** **B27 chạy tiếp** (đóng băng 13:38–17:45). File public dự kiến xong khoảng 18:10–18:15 (JOURNAL entry 93).
> - **13:38 ngày 05/11:** **Anh cần dùng máy: B27 đóng băng** ở bước agent làm file public (còn khoảng 25 phút). Kiểm WER đã qua (7,65 → 7,08). Chạy tiếp: `systemctl --user thaw lifemate-asr-phoft-all` (JOURNAL entry 92).
> - **10:24 ngày 05/11:** **Leader build xong Docker với PhoWhisper-ft** (12,6 GB; sha256 khớp; chữ ASR 3 mẫu khớp nguyên văn). Bước agent hết VRAM trên GPU 4 GB (thiếu 116 MiB), nên chưa có `"ok"`. **Anh quyết B28:** thuê GPU 24 GB một lượt để chạy image (JOURNAL entry 91).
> - **09:20 ngày 05/11:** **B27 xong: Anh duyệt. Laptop fine-tune lại PhoWhisper từ 09:18**, train xong khoảng 12:00. Đạt kiểm WER thì làm tiếp file public, xong khoảng 14:00–14:30 (JOURNAL entry 90).
> - **09:06 ngày 05/11:** Trong lúc leader làm B26, Anh không phải chờ. **Anh quyết B27:** cho laptop fine-tune lại PhoWhisper trên gần đủ train không (JOURNAL entry 89).
> - **08:54 ngày 05/11:** **Lượt prompt `xref` không qua cửa 1** (xong 06:38): dev_lao chữ ASR 39,20 → 38,18 (−1,02), chữ chuẩn 53,40 → 52,72 (−0,69). Dừng theo luật; [PR #14](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/14) đã đóng, không merge (Anh duyệt 09:03).
>   - **B26:** hướng dẫn cho leader ở [`docs/LEADER_DOCKER_PHOFT_2026-11-05.md`](docs/LEADER_DOCKER_PHOFT_2026-11-05.md), kèm danh sách file Anh cần gửi.
>   - Laptop rảnh từ 06:38 (JOURNAL entry 87).
> - **00:30 ngày 05/11:** **B25 xong: public 51,16 với PhoWhisper-ft (+4,87 so với 46,29). Docker đổi sang PhoWhisper-ft** theo luật ghi trước.
>   - Tổng hệ thống khoảng 5,63B, dưới trần 6B. Không phải sửa code: chỉ đổi `ASR_MODEL` trong Docker.
>   - **B26:** Anh gửi bản ghép PhoWhisper-ft (2,9 GB) cho leader; leader đổi Docker và đo thời gian trên A30.
>   - Lượt `xref` đang chạy từ 23:30, xong khoảng 07:30 (JOURNAL entry 86).
> - **18:41 ngày 04/11:** **File nộp public bằng PhoWhisper-ft đã xong (18:40). Anh hoặc leader nộp: B25.**
>   - 634 dòng, kiểm định dạng đạt. Chỉ ASR khác file 46,29; 345/634 dòng trả lời khác.
>   - ASR + agent mỗi mẫu trên laptop: trung bình 10,4 giây (mốc 9,1); 11 mẫu quá 25 giây (mốc 10).
>   - Laptop rảnh tới 23:30 (JOURNAL entry 85).
> - **16:46 ngày 04/11:** **B24 xong: Anh duyệt. Laptop đang làm file nộp public bằng PhoWhisper-ft từ 16:45, xong khoảng 18:45–19:15.**
>   - **Không phải tải gì:** model gốc vẫn còn trong cache. Cache lưu file ở kho chung nên lúc trước Claude kiểm sai.
>   - Chỉ ASR thay đổi so với file 46,29 (cùng code, adapter, hạn 60 giây). Xong thì Anh hoặc leader nộp (B25).
>   - Lượt `xref` 23:30 sẽ đợi job này xong (JOURNAL entry 84).
> - **16:10 ngày 04/11:** **4B đọc chữ PhoWhisper fine-tune qua luật ghi trước** (xong 16:06, sớm hơn dự kiến).
>   - Gộp 495 dòng 46,17 → **47,88** (+1,71, khoảng tin cậy [−1,68; +5,12]); dev_random 54,01 → 55,28; dev_lao 39,20 → 41,30.
>   - Khoảng tin cậy còn chứa 0, nên cần public để xác nhận. **Anh quyết B24:** cho tải lại model gốc PhoWhisper-large (6,17 GB) để làm file nộp public bằng PhoWhisper-ft (khoảng 2–2,5 giờ laptop).
>   - Laptop rảnh từ 16:06 tới 23:30 (JOURNAL entry 83).
> - **14:49 ngày 04/11:** **B23 xong: Anh duyệt cả hai thí nghiệm.**
>   - **Đang chạy:** chấm 4B với chữ PhoWhisper fine-tune, xong khoảng 17:15. Trong lúc chạy, laptop vẫn dùng được nhưng chậm hơn.
>   - **23:30 tối nay (giờ máy):** tự train lượt prompt `xref`, khoảng 8 giờ, xong khoảng 07:30 ngày 05/11. **Trước 23:30 cắm sạc và để máy mở.**
>   - **Trần API:** tổng 80 USD, chỉ dùng khi cần.
>   - **Hạn nộp Docker là 11:59 trưa 16/11 theo giờ máy** (máy chạy giờ New York; hạn của BTC là 23:59 GMT+7) (JOURNAL entry 82).
> - **14:40 ngày 04/11:** **Codex xong báo cáo (B22 xong)**: [`docs/research/CODEX_4B_STRATEGY_2026-11-04.md`](docs/research/CODEX_4B_STRATEGY_2026-11-04.md). Đạt 80 public trước 16/11 rất khó. 4B thua API chủ yếu ở quyết định làm/hỏi/bỏ qua và chọn ID; ASR làm mất khoảng 13 điểm. **Anh duyệt thí nghiệm (B23)** và trả lời 3 câu hỏi của Codex (JOURNAL entry 81).
> - **13:51 ngày 04/11:** **Bản API `xhigh` được 75,52** (B21 xong; `minimal` 69,47; 4B 46,29). **Prompt cho Codex đã sẵn (B22):** mở Codex trong `~/Zalo AI Challenge`, gõ *"Đọc và làm đúng theo `docs/CODEX_4B_STRATEGY_PROMPT_2026-11-04.md`."* Codex phân tích trên CPU và đề xuất thí nghiệm; Claude chạy GPU/API theo thứ tự Anh duyệt (JOURNAL entry 80).
> - **13:37 ngày 04/11:** **File public bản API mạnh nhất trong ngân sách xong (B21).** `~/zac-docker/lifemate/runs/e2e_public_api_spark_xhigh_drop.jsonl`: `muse-spark-1.3` mức suy nghĩ `xhigh`, cộng luật bỏ tham số tuỳ chọn mà nhãn train không dùng. Trên 80 mẫu dev: 64,75 (bản 69,47 trên dev là 50,29). 634 dòng, kiểm đạt. Chi 17,61 USD; **tổng API 43,03 / 50 USD** (Anh nâng trần lên 50 lúc 12:55). **Khi nộp chọn APIs/Others** (JOURNAL entry 79).
> - **12:53 ngày 04/11:** **Bản Meta API được 69,47** (B20 xong; 4B: 46,29). Phân tích: bộ chấm local vẫn khớp public, không có lỗi hệ thống nào giải thích khoảng cách tới 96. 4B mất điểm ở app chưa thấy (khoảng 12–15 điểm; 65% mẫu public có app mới), ASR (khoảng 12–14) và ghi sai khi chữ đã đúng. Model API thiếu quy ước tham số tuỳ chọn của nhãn; sửa bằng luật thì được khoảng +7 trên dev, nhưng 4B không đổi. Chờ Anh chọn hướng tiếp (JOURNAL entry 78).
> - **12:45 ngày 04/11:** **File nộp public bằng Meta API xong (B20).** `~/zac-docker/lifemate/runs/e2e_public_api_spark_min.jsonl`: 634 dòng, kiểm định dạng đạt. Cùng pipeline, chỉ thay model 4B bằng `muse-spark-1.3`. **Khi nộp chọn loại APIs/Others**, để không tính vào cột SLM. Thử trên 80 mẫu dev: API gộp 50,29, 4B 39,10 trên cùng mẫu (API hơn nhiều ở app chưa thấy, kém nhẹ ở app đã thấy). Chi 6,75 USD; **tổng API đã chi 21,15 / 30 USD**. Code: [PR #13](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/13), chờ review. Anh trai Anh đã bắt đầu train (JOURNAL entry 77).
> - **12:22 ngày 04/11:** **Điểm public lần 4: 46,29** (B19 xong; lần 3: 45,39, +0,90). Theo luật ghi trước, **Docker dùng adapter mới `ckpt/q4b4_all/final`** (263 MB). **Anh gửi riêng adapter này cho leader**; leader đóng Docker với `ADAPTER=ckpt/q4b4_all/final` (L6, JOURNAL entry 76).
> - **07:55 ngày 04/11:** **File nộp public mới xong (07:34): Anh hoặc leader nộp được rồi (B19).** `~/zac-c3/lifemate/runs/e2e_public_q4b_all.jsonl`: 634 dòng, kiểm định dạng đạt, sha256 `483fecf54c75…`. Adapter train trên đủ 1.545 mẫu (loss cuối 0,016). Khác bản 45,39 ở 357/634 dòng. Điểm từ 44,39 trở lên thì Docker dùng adapter mới; thấp hơn thì giữ adapter cũ. **Laptop rảnh, gập máy được** (JOURNAL entry 75).
> - **00:15 ngày 04/11:** **Laptop đang train lại 4B trên đủ 1.545 mẫu từ 00:13** (Anh bảo chạy ngay; Claude tắt hẹn giờ 00:30 để khỏi chạy hai lần). Train xong khoảng 06:35; **file nộp public xong khoảng 08:20–08:45** (`runs/e2e_public_q4b_all.jsonl`). Cắm sạc, không gập máy, không khởi động lại (JOURNAL entry 74).
> - **17:23 ngày 03/11:** **B18 xong: Claude review và merge [PR #12](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/12)** vào `q4b-laptop` theo yêu cầu của Anh (17:22). Không có lỗi chặn; test 63/63 đạt. Leader đóng Docker từ nhánh `q4b-laptop` (L6). Lượt 00:30 không bị ảnh hưởng (JOURNAL entry 73).
> - **16:27 ngày 03/11:** **Lượt train lại trên đủ 1.545 mẫu đã hẹn tự chạy lúc 00:30 ngày 04/11** (B17 xong), xong khoảng 08:30–09:00. Chỉ chạy khi đã cắm sạc: lúc 00:30 mà máy chạy pin thì nó chờ tới khi cắm sạc; máy ngủ thì chờ tới khi mở. Tối nay mang máy đi thoải mái. **Mở [PR #12](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/12)**: bước khởi động trước mẫu đầu (mẫu đầu 110 → 13 giây), `predict.sh` mặc định 4B 4-bit, hạn 25 giây (B18, JOURNAL entry 72).
> - **15:27 ngày 03/11:** **Chấm xong hết lượt chữ trộn; laptop rảnh từ 15:27.** dev_lao chữ chuẩn 53,40 → 49,97; gộp 495 dòng: chữ ASR −0,69, chữ chuẩn −1,62; luật in FAIL như đã báo. Anh bật B17 khi tiện (JOURNAL entry 70).
> - **15:11 ngày 03/11:** **B17: Anh chọn tự bật sau.** Claude không bật. Khi muốn chạy: `bash ~/zac-c3/start_q4b_all.sh` (khoảng 8 giờ laptop, dừng và chạy tiếp được). Laptop rảnh sau khoảng 15:30 (JOURNAL entry 69).
> - **15:07 ngày 03/11:** **Chữ trộn không qua luật gộp.** dev_lao chữ ASR fine-tune 39,20 → 35,85 (−3,35); gộp 495 dòng 46,17 → 45,49 (−0,69, cần +1,0). Bỏ chữ trộn. **Claude đã chuẩn bị train lại 4B trên đủ 1.545 mẫu rồi làm file nộp public (khoảng 8 giờ laptop); chờ Anh bật ở B17.** Laptop còn chấm chữ chuẩn tới khoảng 15:30 (JOURNAL entry 68).
> - **08:56 ngày 03/11:** **Lượt chữ trộn qua cửa 1 trên dev_random:** chữ ASR fine-tune 54,01 → **56,32** (+2,31), chữ chuẩn 65,61 → 66,05 (+0,43). Khoảng tin cậy còn chứa 0, và mẫu hỏi lại giảm ở cả hai loại chữ (33 mẫu), cần theo dõi. **Laptop chạy cùng cách trộn trên fit_lao từ 08:54, chấm dev_lao xong khoảng 15:40**, rồi quyết bằng điểm gộp 495 dòng. Cần mang máy đi thì dùng lệnh ở dòng Laptop (JOURNAL entry 67).
> - **00:54 ngày 03/11:** **Laptop khởi động lại lúc 00:37** (lệnh khởi động lại thường, không phải crash), nên lượt chữ trộn dừng ở bước 10. **Đã chạy tiếp từ 00:53**, chỉ mất vài phút train; **chấm xong khoảng 07:25**. Đừng khởi động lại hay tắt máy tới khi xong; cần dừng thì dùng lệnh ở dòng Laptop. **B16: Anh chọn chưa cần Colab trả phí** (JOURNAL entry 65).
> - **00:22 ngày 03/11:** **Laptop train 4B học chữ trộn từ 00:19** (B15 xong: Anh chọn chạy đêm nay). Một nửa mẫu fit_random học trên chữ Whisper-turbo, nửa kia trên chữ chuẩn. **Chấm dev_random xong khoảng 07:05.** Giữ nếu chữ ASR fine-tune tăng ít nhất 1,0 so với 54,01 và chữ chuẩn không giảm quá 2,0 so với 65,61; qua thì chạy tiếp trên fit_lao. **Cắm sạc, không gập máy, tắt bớt app nặng** (RAM còn khoảng 2,8 GB). **Colab:** bản miễn phí là GPU T4, chậm gần 9 lần laptop khi train (đã đo ở Kaggle), nên không dùng. Bản trả phí (L4/A100) chưa cần cho train; có ích cho việc đo bf16 và thời gian (B16, không gấp) (JOURNAL entry 64).
> - **22:44 ngày 02/11:** **Anh hỏi chiến lược để nộp public thêm.** Claude đề xuất theo thứ tự: (1) 4B học trên chữ trộn (nửa chữ chuẩn, nửa chữ ASR), khoảng 6,7 giờ laptop, chấm trên dev_random; (2) train lại công thức thắng trên đủ 1.545 mẫu train rồi nộp public; (3) chuẩn bị Docker. **Anh chọn B15** (JOURNAL entry 63).
> - **22:39 ngày 02/11:** **Chấm xong: pilot không đạt cả hai loại chữ.** Chữ chuẩn 53,40 → 50,57 (−2,83 [−7,93; +2,35]); chữ ASR 39,20 → 37,12. Giảm cả ở app mà dữ liệu sinh nhắm tới. → Không dùng dữ liệu sinh này, không sinh cho 11 app public, giữ chi ở 12,57 USD. **B14 không cần làm nữa.** GPU laptop rảnh, gập máy được (JOURNAL entry 61).
> - **22:17 ngày 02/11:** **Pilot dữ liệu sinh không đạt.** Train 4B trên fit_lao + 280 mẫu sinh xong 21:15. Chấm dev_lao chữ ASR fine-tune: 39,20 → **37,12** (−2,09, khoảng tin cậy 95% [−7,22; +3,01]). Luật đặt trước cần tăng ít nhất 2,0, nên **không giữ** dữ liệu sinh ở dạng này và **chưa sinh cho 11 app public** (đã chi 12,57 / 30 USD). App bị giấu −0,96, app đã thấy −4,69. Chữ chuẩn đang chấm, xong khoảng 22:40 (JOURNAL entry 61).
> - **15:47 ngày 02/11:** **Điểm public lần 3: 45,39** (Anh nộp `e2e_public_q4b.jsonl`, agent 4B; B11 xong). Tăng 10,15 so với 35,24; dev gộp dự đoán tăng 13,11, khoảng tin cậy +8,94 đến +17,32, nên vẫn khớp. Lần này public thấp hơn dev gộp 0,78 điểm (hai lần trước cao hơn khoảng 2 điểm); một lần như vậy vẫn là nhiễu. Train pilot vẫn đang chạy, xong khoảng 23:00 (JOURNAL entry 62).
> - **14:54 ngày 02/11:** **File nộp public 4B xong (B11): Anh nộp được rồi.** `~/zac-c3/lifemate/runs/e2e_public_q4b.jsonl`: 634 dòng, kiểm định dạng đạt (0 lỗi), sha256 `2fc287ffa729…`. Trên laptop mỗi mẫu trung bình 9,1 giây, p95 17,9 giây; 2 mẫu quá 30 giây vì chạy hết 8 bước, nên bản Docker phải đặt hạn dưới 30 giây. **Pilot sinh xong: 280/384 mẫu đạt, 11,55 USD.** Giọng văn gần câu thật ("giùm" 10% so với 12%, dài 20,6 so với 22,5 từ). **Tổng đã chi: 12,57 / 30 USD.** **Train pilot tự bật lúc 14:52**, xong khoảng 22:30–23:00; cắm sạc, không gập máy. Luật: giữ nếu dev_lao chữ ASR tăng ít nhất 2,0 điểm so với 39,20 (JOURNAL entry 61).
> - **13:48 ngày 02/11:** **Anh chọn "Tự bật khi xong":** Claude cài lệnh chờ. Khi file nộp public (B11) và pilot sinh đều xong, train pilot tự bật (nếu có ít nhất 100 mẫu đạt), khoảng 7,5 giờ, tức xong khoảng 22:30–23:00 nếu bật lúc 15:00. Dừng giữa chừng: `systemctl --user stop lifemate-q4b-synth`. Giá thật của `muse-wonder-1.0` khoảng 0,095 USD mỗi lần sinh (ước 0,078), nên pilot khoảng 10–11 USD; phần 11 app public sẽ cần ít mẫu hơn mỗi app, hoặc hỏi Anh nếu vượt 30 USD.
> - **13:40 ngày 02/11:** **Anh nâng trần chi tiêu lên 30 USD** "để thoải mái và tăng chất lượng". **Anh đang chạy file nộp public (B11) từ 13:10**, xong khoảng 14:45–15:00; GPU bận tới lúc đó. Claude thử model mạnh hơn `muse-wonder-1.0` trên 8 mẫu: câu và kịch bản phong phú hơn (có câu nhiều việc, làm phần đủ thông tin rồi mới hỏi phần thiếu), giá gấp 2,3 lần; 8/8 đạt. → **Pilot sinh bằng `muse-wonder-1.0`, đang chạy** (6 app × 64 mẫu, khoảng 9 USD, xong khoảng 14:55). Script train + chấm pilot đã sẵn: `bash ~/zac-synth/start_q4b_lao_synth.sh` (khoảng 7,5 giờ GPU). Dự tính: pilot khoảng 9 USD + 11 app public khoảng 16,5 USD, tổng khoảng 26,5 USD. **Tổng đã chi: 0,9 USD** (JOURNAL entry 60).
> - **13:20 ngày 02/11:** **Bài thử sinh dữ liệu đạt điều kiện đầu.** Lượt t20: 14/20 mẫu qua mọi bước kiểm (0,37 USD). Claude sửa bộ kiểm (loại nhầm câu chỉ hỏi thông tin; hỏng vì dấu `}` thừa) và giọng văn (95% câu có "giùm", câu thật chỉ 12%), thêm trần tổng 10 USD vào code. Lượt t12 trên code đã sửa: 9/12 đạt (0,19 USD), câu đa dạng hơn hẳn. **Tổng đã chi: 0,55 USD.** **Anh chấm B14:** đọc `lifemate/gen/synth_review_t12_t20.md` (23 câu), đánh T/K từng câu (JOURNAL entry 60).
> - **13:12 ngày 02/11:** **Bài thử 20 mẫu đang chạy** (B13 xong: Anh lưu key; tự chạy từ 13:10). **Trần chi tiêu Anh đặt: tổng dưới khoảng 10 USD cho việc sinh dữ liệu; vượt mức phải hỏi Anh.** Về VieNeu (TTS tiếng Việt chạy local): nó đọc chữ thành audio, không tự viết câu và đáp án, nên **không thay được Meta mà bổ sung cho ASR**. Đáng thử sau: trên dev_lao, lỗi ASR làm 4B mất 17,1 điểm ở mẫu dùng app chưa thấy, so với 7,6 ở mẫu dùng app đã thấy. Cần kiểm licence của checkpoint VieNeu trước (JOURNAL entry 60).
> - **12:35 ngày 02/11:** **Bộ sinh dữ liệu đã viết xong ([PR #11](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/11), 14 test CPU đạt); bài thử 20 mẫu chờ key Meta (B13).** Anh chọn "Viết và thử 20 mẫu". Model `muse-spark-1.3` của Meta (gói Standard, Meta không dùng nội dung để train), trần 3 USD. Claude đã cài lệnh chờ: **Anh tạo file key là bài thử tự chạy**, khoảng 10–20 phút, rồi Claude báo tỉ lệ mẫu đạt và gửi file mẫu để Anh đọc (JOURNAL entry 60).
> - **12:20 ngày 02/11:** **Credit Claude API chưa dùng được** (tài khoản chưa đủ 7 ngày), nên pilot B12 có thể **dùng model chữ của Meta thay thế**. Meta Model API có model chữ (Muse Spark, Muse Wonder), không chỉ model chuyển giọng nói thành chữ; nguồn tin nói credit tính cho cả nền tảng. Anh cần kiểm trên trang Meta là 100 USD dùng được cho Muse Spark hoặc Muse Wonder, và đọc điều khoản về việc dùng đầu ra để train model khác (JOURNAL entry 59).
> - **12:15 ngày 02/11:** **Anh tự chạy file nộp public bằng 4B (B11):** `bash ~/zac-c3/start_public_q4b.sh`, khoảng 1,5–2 giờ; đã thử 2 mẫu public, chạy đúng. **Ý tưởng sinh dữ liệu bằng Claude API: luật cho phép, và có chỗ đáng làm.** 11 app của public_test không có trong train (410/634 mẫu public có cài ít nhất một app này), và 4B trên app chưa thấy (dev_lao) kém app đã thấy khoảng 15 điểm. Claude đề xuất pilot trên 6 app của dev_lao trước, khoảng 10–20 USD; **Anh quyết B12.** Credit Meta (chuyển giọng nói thành chữ) gần như không dùng được: không được gán nhãn audio test, và audio train đã có nhãn (JOURNAL entry 59).
> - **10:20 ngày 02/11:** **Chốt 4B làm model agent (C7 xong).** Điểm gộp 495 dòng trên chữ Whisper-turbo fine-tune: 1.7B 33,07 → 4B **46,17**, +13,11 [+8,94; +17,32]. Riêng dev_random: 42,64 → **54,01** (+11,37 [+5,35; +17,45]); chữ chuẩn 53,92 → **65,61**. Luật đặt trước cần hơn ít nhất 1 điểm và dev_random không kém, nên 4B được chọn. Không mẫu nào chạy quá 25 giây mà có điểm, nên hạn giờ không làm đổi kết quả. Mẫu đầu tiên của một lượt chấm chạy 110 giây vì model vừa nạp; cần chạy khởi động trước khi tính giờ. **Laptop rảnh từ 10:13, gập máy được.** **Anh quyết B11:** làm file nộp public bằng 4B trên laptop (khoảng 1,5–2 giờ GPU). **Leader (L6):** Docker giờ chạy 4B (khoảng 8 GB ở bf16) cùng Whisper-turbo fine-tune; thời gian trên A30 chưa đo (JOURNAL entry 58).
> - **03:40 ngày 02/11:** **4B thắng rõ trên dev_lao (C6 xong).** Chữ ASR fine-tune: 1.7B 24,55 → 4B **39,20**, +14,65 [+8,79; +20,49] (tốt hơn ở 78 mẫu, kém hơn ở 30). Chữ chuẩn: 35,62 → **53,40**, +17,78 [+11,74; +23,61]. Tăng ở cả mẫu cần làm (execute) lẫn mẫu hỏi lại. Hai bên chạy cùng code suy luận, cùng 262 mẫu; chỉ khác model. Laptop 4-bit: trung bình 7,8 giây mỗi mẫu, chậm nhất 27,9 giây (1 mẫu quá 25 giây, mẫu đó vốn 0 điểm). Theo luật đặt trước, **laptop đang chạy lượt kế tiếp: 4B trên fit_random → dev_random (C7, từ 03:30, dự kiến xong khoảng 10:00)**, rồi quyết bằng điểm gộp 495 dòng. Phải mang máy đi trước khi xong thì dừng bằng `systemctl --user stop lifemate-q4b-random` (đợi 1–3 phút cho lưu xong rồi gập); về chạy `bash ~/zac-c3/start_q4b_random.sh` là tiếp từ chỗ dừng. **Leader (L6):** nếu C7 chốt 4B, Docker sẽ chạy 4B (khoảng 8 GB ở bf16) cùng Whisper-turbo; thời gian trên A30 chưa đo (JOURNAL entry 57).
> - **20:55 ngày 01/11:** **Lượt 4B chạy lại từ 20:47** (B10 xong: Anh bấm "Chạy tiếp 4B"). 711 token/giây, như lúc sáng. **Dự kiến train xong khoảng 01:30, chấm xong khoảng 03:00 sáng 02/11.** Để máy cắm sạc, không gập, tránh app nặng GPU. Cần mang máy đi thì dừng bằng `systemctl --user stop lifemate-q4b-lao`, đợi 1–3 phút cho lưu xong rồi gập; chạy lại `bash ~/zac-c3/start_q4b.sh` là tiếp từ chỗ dừng.
> - **10:40 ngày 01/11:** **Lượt 4B tạm dừng; GPU laptop rảnh, gập máy được.** Anh phải mang máy đi học lúc 11:00, mà code cũ không lưu được giữa chừng, nên Claude dừng lượt lúc 10:13 (bước 35/254, phải chạy lại từ đầu). Đã thêm **lưu trạng thái mỗi 10 bước và khi dừng, rồi chạy tiếp** (PR #10, đã thử trên GPU). **Khi về và cắm sạc (B10):** chạy `bash ~/zac-c3/start_q4b.sh` hoặc nhắn Claude. Cần khoảng 7,5 giờ GPU, chia nhiều buổi được; dừng bất cứ lúc nào bằng `systemctl --user stop lifemate-q4b-lao` (mất 1–3 phút để lưu).
> - **09:30 ngày 01/11:** **Laptop đang train Qwen3-4B bản 4-bit** (B9 xong: Anh đồng ý tải; tải 8 GB mất 64 giây). Cùng công thức với mốc 1.7B trên fit_lao, chấm trên dev_lao bằng chữ ASR fine-tune và chữ chuẩn. **Từ 09:27, dự kiến xong khoảng 16:30–17:00.** **Cắm sạc, không gập máy, tránh video, game hay app nặng GPU** (VRAM chỉ dư khoảng 0,4 GB). Luật đặt trước: 4B thắng nếu hơn 1.7B ít nhất 1 điểm trên dev_lao chữ ASR fine-tune (mốc 24,55). Code thêm optimizer 8-bit: [PR #10](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/10) (JOURNAL entry 55).
> - **08:25 ngày 01/11:** **Bắt đầu phần agent.** Đo lại trên dev: mẫu nhiều vế **không phải chỗ mất điểm chính**. Model làm thiếu lệnh ghi ở 11/183 (dev_random) và 29/214 (dev_lao) mẫu execute; còn mẫu chỉ có 1 lệnh ghi cũng sai gần một nửa (JOURNAL entry 54). Claude đề xuất thử **4B 4-bit ngay trên laptop** trước: **cần Anh đồng ý tải Qwen3-4B (khoảng 8 GB), mục B9.**
> - **08:11 ngày 01/11:** **Điểm public lần 2: 35,24** (Anh nộp `lifemate/runs/e2e_public_turboft.jsonl`; B8 xong). Tăng 9,31 so với 25,93, gần đúng mức tăng trên dev gộp (+9,08). Cả hai lần, public cao hơn dev gộp khoảng 2 điểm (25,93 so với 23,99; 35,24 so với 33,07), nên tiếp tục chọn trên dev được (mục F). Việc lớn tiếp theo là agent: ASR giờ chỉ làm mất 11 điểm, agent mất khoảng 56 ngay trên chữ chuẩn.
> - **01:35 ngày 01/11:** **File nộp public mới đã sẵn sàng (B8: Anh hoặc leader nộp):** `lifemate/runs/e2e_public_turboft.jsonl` (634 dòng, 0 lỗi định dạng, sha256 bắt đầu `f87c8e1fc863`). Whisper-turbo fine-tune và agent `q17b_fit_random`, đúng agent của lần nộp 25,93, nên chỉ ASR thay đổi. Trên laptop: ASR 0,48 giây và cả mẫu 3,0 giây trung bình, chậm nhất 11,7 giây; không mẫu nào quá 25 giây. Trên dev, đổi ASR này tăng điểm gộp 23,99 → 33,07, nên public có thể lên quanh 33–35 (ước lượng thô từ lần 25,93). Ghép adapter trên laptop khớp bản Colab 768/784 câu (khác 24/11.084 từ, sai số fp16 giữa hai GPU). **GPU laptop rảnh từ 01:29.**
> - **01:05 ngày 01/11:** **C3 xong: fine-tune ASR thêm khoảng 9 điểm.** Điểm gộp 495 dòng (dev_random + dev_lao): Whisper-turbo fine-tune **33,07**, PhoWhisper fine-tune **33,41**, turbo chưa fine-tune 23,99, chữ chuẩn 44,23. dev_random 31,69 → 42,64 (turbo-ft) / 43,04 (Pho-ft); dev_lao 17,14 → 24,55 / 24,85. Hai model fine-tune cách nhau 0,35 điểm [−2,89; +3,61], dưới 1 điểm, nên theo luật đặt trước **chọn Whisper-turbo fine-tune** (0,8B, nhanh hơn, chừa chỗ cho agent 4B). ASR giờ chỉ còn làm mất 11 điểm, so với 20 điểm trước đây (JOURNAL entry 52). **GPU laptop đang làm file nộp public mới bằng ASR này (C5, từ 00:54, khoảng 45 phút).** Anh hoặc leader tự nộp khi file xong.
> - **00:05 ngày 01/11:** **Kết quả hai Colab đã về** (B2, L3 xong; máy anh trai vẫn chờ). WER lượt cuối trên dev_random: Whisper-turbo 31,2 → **11,2** sau fine-tune; PhoWhisper 25,9 → **9,2**. Không lẫn dev: train chỉ đọc `train`, bỏ toàn bộ 458 mẫu của hai tập dev. **Claude đang chấm agent trên GPU laptop (C3, 5 lượt, 00:02 tới khoảng 01:00)**: luật chọn ASR đã ghi trước khi chạy. Anh và leader: xoá gói dữ liệu và thư mục `zac_out` trên Drive (mục D).
> - **21:21:** Anh dừng phiên hôm nay, chờ kết quả Colab. **Đã chốt thứ tự phiên sau:** (1) chấm ASR fine-tune từ hai Colab và chọn ASR (C3, C5); (2) chuyển sang agent: kết quả 4B nếu máy anh trai chạy xong, rồi dữ liệu SFT nhiều vế và điều kiện (JOURNAL entry 51).
> - **21:08:** **C4 xong: [PR #9](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/9)**, chờ review. Mỗi mẫu có hạn chót cứng, tính cả thời gian ASR; chốt chặn ID chạy trong agent. Chạy lại: dev_random và chữ turbo giống hệt từng dòng (53,92 và 31,69); dev_lao 35,53 → 35,62 (4 call sai bị chặn, 1 mẫu tốt hơn, 0 mẫu kém); mẫu `train_0830` dừng đúng 15,0 giây khi cho ngân sách 15 giây. Theo luật đặt trước: nhận cả hai, chốt chặn bật mặc định (JOURNAL entry 50). **GPU laptop rảnh từ 21:05**, chờ Colab cho C3. Leader dựng Docker (L6) nên lấy từ nhánh `time-budget`.
> - **20:33:** Anh chọn "Làm C4 ngay". Code xong trên nhánh `time-budget` (15 test CPU đạt). **GPU laptop chạy 4 lượt kiểm C4 từ 20:32 tới khoảng 21:15.** Nếu kết quả Colab về trong lúc đó, C3 chạy ngay sau.
> - **20:22:** Laptop xong lượt (2) B-up lúc 20:19. Đọc chữ chuẩn 51,19 so với 53,92 (−2,72 [−8,08; +2,52]); đọc chữ turbo 29,06 so với 31,69 (−2,64). Giảm quá 1 điểm nên theo luật đặt trước **không giữ B-up**; công thức agent mặc định vẫn là SFT thường `q17b_fit_random` (JOURNAL entry 49). B-up hỏi lại đúng hơn (49 → 69) nhưng hỏi thừa ở mẫu cần làm (14 → 22 mẫu). **GPU laptop đã rảnh**; C3 chạy ngay khi `asr_results_*` từ Colab về. Một mẫu sinh lặp "000…" mất 23,4 giây, nên C4 thêm trần cho mỗi bước.
> - **17:01:** Laptop xong lượt (1) lúc 17:00. Agent học trên chữ turbo: đọc chữ turbo 33,22 so với 31,69 (+1,5, chưa chắc), nhưng đọc chữ chuẩn 48,55 so với 53,92 (−5,4, kém thật). → Giữ agent học trên `audio_text`, dồn sức cho fine-tune ASR (JOURNAL entry 48). Lượt (2) chạy tới khoảng 20:00. Khuyến nghị không chạy lượt agent học trên chữ PhoWhisper.
> - **16:12:** Anh đã gửi gói và lệnh cho anh trai (B4 xong), đang chờ phản hồi. **Colab vẫn làm ngay** (B2 cho Anh, L3 cho leader). Việc fine-tune ASR không gửi cho anh trai: anh trai chỉ chạy một lần, lần đó dành cho các lượt agent (nhất là 4B), và máy chưa rõ GPU gì. Đã chốt chuyện dữ liệu: BTC cho phép.
> - **16:05:** Kaggle xong mà không train, vì T4 chậm gần 9 lần (JOURNAL entry 46). Public lần đầu **25,93**. Thêm nguyên tắc chọn model (mục F). Lệnh cho anh trai thêm bước kiểm GPU có bf16.
> - **15:30:** Tạo bảng này.

### A. Đang chạy: chỉ chờ, không cần làm gì

| Máy | Ai lo | Đang chạy gì | Xong khoảng | Kết quả |
|---|---|---|---|---|
| Laptop của Anh (RTX 4070) | Claude theo dõi | **04/11: chấm 4B với chữ PhoWhisper fine-tune 14:44–16:06 (qua luật); 16:45–18:40 làm file nộp public bằng PhoWhisper-ft (B24; public 51,16, B25); 23:30 ngày 04/11 – 06:38 ngày 05/11 lượt prompt `xref` (không qua cửa 1). Từ 09:18 ngày 05/11 fine-tune lại PhoWhisper trên gần đủ train (B27); kiểm WER qua; đóng băng 13:38–17:45 vì Anh cần dùng máy; file public xong 18:09 (B29). Rảnh từ 18:14.** Trước đó: rảnh từ 07:34 ngày 04/11. Lượt train lại trên đủ 1.545 mẫu (00:13–06:03) và file nộp public (06:03–07:34) đã xong (B19). Lượt chữ trộn trên fit_lao (08:54–15:27) không qua luật gộp. Lượt chữ trộn trên fit_random (00:19–07:30, dừng 00:37–00:53 vì máy khởi động lại) qua cửa 1: chữ ASR +2,31, chữ chuẩn +0,43. Trước đó GPU rảnh từ 10:13 ngày 02/11. C7 (4B trên fit_random) xong 10:13: **chốt 4B**. C6 (4B trên fit_lao) xong 03:28: 4B thắng rõ. Lượt sáng 01/11 (09:27–10:13) đã bỏ. File nộp public mới đã xong (C5). C3 xong lúc 00:53 (5 lượt chấm, entry 52). Trước đó: 4 lượt kiểm C4 xong lúc 21:05. Hai lượt train đã xong: **(1)** `q17b_random_asrtrain` (học trên chữ turbo): xong 17:00, không đáng dùng (C1). **(2)** `q17b_random_up` (công thức B-up): xong 20:19, không giữ (C2) | Đã xong | Nằm sẵn trên laptop (`lifemate/runs/`), không cần gửi |
| Kaggle của leader (T4 x2) | Leader | **Xong khoảng 15:50, không train:** T4 chỉ 157 token/giây (khoảng 22,5 giờ mỗi epoch), nên ô lệnh tự bỏ qua. Chấm lại adapter laptop trên T4: 54,35 so với 53,92 (+0,43; 228/233 mẫu giống hệt) | Đã xong | Đã giải nén ở `cloud_results/kaggle/` |
| Máy Google của anh trai Anh | Anh trai | Gói v3 (4B và 1.7B) với lệnh có kiểm GPU bf16. **Anh đã gửi (16:12), đang chờ phản hồi** *(04/11 12:25: Anh báo anh trai đã bắt đầu train.)* *(06/11 11:23: xong; máy là 2× RTX 4090, chạy 22:21–01:04; báo cáo ở `cloud_results/anh_trai/`; không có adapter tốt hơn, JOURNAL entry 101.)* *(06/11 12:47: gói pilot v2 sẵn, chờ Anh gửi (B33); chạy 1 lần mỗi ngày.)* *(08/11: pilot v2 chạy xong 19:22 ngày 07/11 – 02:36 ngày 08/11, luật FAIL; không còn việc cho máy này; dọn dữ liệu, B34.)* | 3–5 giờ sau khi anh trai chạy (2–4 GPU A100) | `~/cloud_results_*.tar.gz`, `~/zac_logs.tar.gz` (máy anh trai) |

- **Laptop:**
  - Chấm 4B với chữ PhoWhisper fine-tune xong 16:06 (qua luật).
  - File nộp public bằng PhoWhisper-ft xong 18:40 (B24); public 51,16 (B25).
  - Lượt `xref` chạy 23:30–06:38, không qua cửa 1 (dev_lao chữ ASR −1,02).
  - **09:18 ngày 05/11:** fine-tune lại PhoWhisper (B27). Train xong 12:08; kiểm WER qua (7,65 → 7,08); chữ ASR public xong 12:25.
  - 13:38–17:45 đóng băng vì Anh cần dùng máy. **File public xong 18:09** (B29); chạy lại riêng `public_0497` lúc 18:10.
  - 18:12–18:14: `predict.sh` 3 mẫu (nhánh `q4b-laptop`, không Docker) đạt `"ok": true`.
  - **Rảnh từ 18:14 ngày 05/11.** Anh mang máy đi từ 11:00 tới tối 06/11. **Tối nay chạy thử image Docker (B28, B31), khoảng 4 giờ:** 3 mẫu, rồi đủ 634 mẫu hai lần, bằng `~/zac-c3/b28_run.sh` (đã thử bằng lệnh `docker` giả).
- **Bài học từ Kaggle:** train agent cần GPU có bf16 phần cứng (A100, A10, A30, L4, H100, RTX 30/40). T4, V100, P100 chậm gần 9 lần, nên không dùng để train agent. Colab T4 vẫn fine-tune ASR được, vì Whisper chạy fp16.

### B. Việc tiếp theo, làm theo thứ tự

**Anh:**
- [ ] **B1.** (2 phút) Gửi leader file `lifemate/runs/e2e_public_turbo.jsonl` (634 dòng, khoảng 180 KB; đã kiểm định dạng), để leader nộp public ở L1.
- [x] **B2.** (15 phút thao tác, máy chạy 1,5–2 giờ) **Colab: fine-tune ASR Whisper-turbo** theo [`docs/ASR_FINETUNE_2026-10-31.md`](docs/ASR_FINETUNE_2026-10-31.md).
  - Tải `~/zac_asr_bundle_20261031.tar.gz` (845 MB) lên thư mục gốc My Drive.
  - Mở Colab, chọn T4 GPU, chạy ô mount Drive, rồi dán ô lệnh và đổi `MODELS="turbo"`.
  - **Để tab mở.** Kết quả: `My Drive/zac_out/asr_results_turbo.tar.gz`.
  - *Chưa làm (16:12). Vẫn làm, không chờ anh trai: Colab T4 fine-tune ASR được bình thường (Whisper chạy fp16), và có kết quả trước hoặc ngay sau buổi 18:00.*
  - ***Xong (00:05 ngày 01/11, Anh báo):*** train 158 phút trên T4, 3 epoch. WER trên phần kiểm giữ lại của train 33,7 → 9,0. Trên dev_random, WER lượt cuối 31,2 → 11,2; dev_lao 31,2 → 14,4. Đã giải nén ở `cloud_results/colab_anh/x/`.
- [ ] **B3.** (2 phút) Chia sẻ riêng file gói ASR (chỉ cho leader), để leader chạy phần PhoWhisper ở L3.
- [x] **B4.** *(Anh đã gửi lúc 16:12; đang chờ phản hồi.)* **Gửi anh trai** đúng 2 thứ:
  - file `~/zac_cloud_bundle_20261031_v3.tar.gz` (256 MB, sha256 bắt đầu `bfe980b32f46`);
  - lệnh một dòng **bản mới, có kiểm GPU** trong [`docs/CLOUD_TRAIN_2026-10-31.md`](docs/CLOUD_TRAIN_2026-10-31.md), mục "Khi nhờ người khác chạy giúp một lần".

  Kèm 3 lời dặn:
  - **Máy phải có GPU NVIDIA có bf16** (A100, A10, A30, L4, H100, RTX 30/40), Linux, Internet, ổ trống từ 100 GB. Máy T4, V100, P100 hay TPU thì đừng chạy; lệnh cũng tự dừng nếu GPU không đạt.
  - Xong thì gửi lại 2 file `~/cloud_results_*.tar.gz` và `~/zac_logs.tar.gz`.
  - Gửi xong thì xoá `~/ZAIC_2026`, gói và 2 file đó.

  Máy là GPU gì, bắt đầu chạy lúc nào (điền khi anh trai trả lời): …
  - Nếu máy là T4, V100, P100 hay TPU: 4B chỉ còn cách thuê GPU có bf16 (mục E).
  - Nếu máy có GPU mạnh và anh trai sẵn lòng chạy thêm một lần: Claude làm gói fine-tune ASR riêng cho máy đó (trên A100 chưa tới 1 giờ).
- [ ] **B5.** (45–60 phút, trong lúc Colab chạy) Nghe 18 câu Whisper-turbo nghe sai nhiều nhất, cùng leader nếu được. Danh sách id ở mục "Mất điểm ở đâu" của [`docs/E2E_BASELINE_2026-10-31.md`](docs/E2E_BASELINE_2026-10-31.md). Ghi lại tiếng ồn, giọng, tốc độ nói, từ lạ.
- [ ] **B6.** Review [PR #8](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/8) cùng leader rồi merge. Sau đó đổi nhánh đích của #4 sang `main`. Từ đó merge từ dưới lên (#4 → #5 → #6 → #7 → #9 → #10), mỗi lần đổi đích PR kế tiếp sang `main` trước khi merge.
- [x] **B8.** (5 phút) **Nộp public** `lifemate/runs/e2e_public_turboft.jsonl`, tự nộp hoặc gửi leader nộp. Claude không nộp.
  - File: 634 dòng, khoảng 195 KB, đã qua `zaic_tools --validate` (0 lỗi). Chỉ khác lần nộp 25,93 ở ASR (Whisper-turbo fine-tune).
  - ***Xong (Anh báo lúc 08:11 ngày 01/11): 35,24.*** Lần trước 25,93, tức tăng 9,31; dev gộp dự đoán tăng 9,08 (JOURNAL entry 53).
- [x] **B9.** (1 phút) **Quyết: tải Qwen3-4B-Instruct-2507 về laptop để thử train 4B 4-bit?** Khoảng 8 GB, licence Apache-2.0, từ Hugging Face (`Qwen/Qwen3-4B-Instruct-2507`). Claude đề xuất có (JOURNAL entry 54).
  - Nếu có: Claude chạy thử 15 phút để đo VRAM và tốc độ. Nếu một epoch dưới khoảng 8 giờ, train fit_lao → dev_lao qua đêm; khi đó cắm sạc và không gập máy.
  - Nếu không: GPU laptop chạy thí nghiệm A (1.7B, 2 epoch, khoảng 5,5 giờ) trước.
  - ***Xong (Anh chọn "Có, tải 4B", 08:5x):*** đã tải (rev `cdbee75f`), đang train (C6).
- [x] **B10.** Khi về và cắm sạc: chạy lượt 4B tiếp, bằng `bash ~/zac-c3/start_q4b.sh` trong terminal hoặc nhắn Claude "chạy tiếp 4B".
  - Cần khoảng 7,5 giờ GPU (train 6,2 giờ, chấm 1,3 giờ), chia nhiều buổi được: lưu mỗi 10 bước (khoảng 12 phút).
  - ***Xong (20:47, Anh bấm "Chạy tiếp 4B"):*** lượt chạy lại từ đầu, đang train (C6).
  - Dừng bất cứ lúc nào: `systemctl --user stop lifemate-q4b-lao`. Lệnh chờ bước đang chạy xong rồi lưu, mất 1–3 phút; đợi xong mới gập máy. Chạy lại `bash ~/zac-c3/start_q4b.sh` là tiếp từ chỗ dừng.
- [x] **B11.** *(12:10 ngày 02/11, Anh chọn tự chạy sau. 14:42: chạy xong, kiểm định dạng đạt. ***Xong (15:47): Anh nộp, được 45,39.***)* **Chạy file nộp public bằng 4B trên laptop, rồi nộp.** Agent 4B `q4b4_fit_random` nạp 4-bit, dùng lại chữ Whisper-turbo fine-tune của lần nộp 35,24, nên chỉ agent thay đổi. Khoảng 1,5–2 giờ GPU; cắm sạc, không gập máy trong lúc chạy. Anh hoặc leader tự nộp; Claude không nộp. Dev gộp tăng 33,07 → 46,17; hai lần trước public cao hơn dev gộp khoảng 2 điểm, nhưng đó chỉ là ước lượng thô.
  - Chạy: `bash ~/zac-c3/start_public_q4b.sh`. Lệnh chạy nền, đóng terminal được; cắm sạc, không gập máy tới khi xong.
  - Xem tiến độ: `tail -f ~/zac-c3/lifemate/runs/e2e_public_q4b_2026-11-02.log`. Xong khi log có dòng `done: 634 lines, ok=True`.
  - Dừng: `systemctl --user stop lifemate-public-q4b`. Chạy lại thì làm lại từ mẫu đầu.
  - File nộp: `~/zac-c3/lifemate/runs/e2e_public_q4b.jsonl`. Claude đã thử 2 mẫu public: chạy đúng, đúng định dạng.
  - Nộp xong thì báo điểm để Claude ghi.
  - *(14:54 ngày 02/11) File xong: 634 dòng, 0 lỗi định dạng, sha256 `2fc287ffa729…`. Còn: Anh hoặc leader nộp file này và báo điểm.*
- [x] **B12.** *(Xong 22:39: pilot chạy hết, không đạt luật, dừng hướng này.)* (5 phút) **Quyết: pilot sinh dữ liệu tổng hợp bằng Claude API?** (JOURNAL entry 59)
  - Pilot: sinh khoảng 300–600 mẫu cho 6 app bị giấu của dev_lao, kiểm từng mẫu bằng cách chạy thật trong `zaic_tools`, train lại 4B trên fit_lao + mẫu sinh, chấm dev_lao. Luật đặt trước: tăng ít nhất 2 điểm trên chữ ASR fine-tune (mốc 39,20) thì sinh tiếp cho 11 app của public.
  - Chi phí pilot ước khoảng 10–20 USD (Claude Opus 5.5 qua Batch API, giảm 50%). Script sẽ có trần tiền cứng; Claude không chi vượt mức Anh duyệt.
  - Anh tự đặt API key trên laptop (Claude không cần thấy key): tạo file `~/.zac_anthropic_env` chứa dòng `export ANTHROPIC_API_KEY=...`, rồi `chmod 600 ~/.zac_anthropic_env`. Không dán key vào chat, không commit.
  - Gói Claude Max và credit API là hai thứ riêng: script chỉ dùng được credit trên Console (platform.claude.com).
  - ***12:35 ngày 02/11: Anh chọn "Viết và thử 20 mẫu" (với model của Meta).*** Code xong: [PR #11](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/11). Bài thử: 5 app của dev_lao × 4 mẫu, `~/zac-synth/run_synth_t20.sh`. **Luật đặt trước để sang pilot:** ít nhất 8/20 mẫu qua mọi bước kiểm, và Anh thấy ít nhất 4/5 câu được nhận là tự nhiên. Không đạt thì sửa prompt một lần (hoặc dùng `muse-wonder-1.0`) và thử lại 20 mẫu; vẫn không đạt thì dừng.
  - ***13:12 ngày 02/11: Trần chi tiêu (Anh đặt):*** tổng mọi lần gọi API sinh dữ liệu (Meta, sau này Anthropic) dưới khoảng 10 USD; lượt nào làm tổng vượt mức thì Claude hỏi Anh trước.
  - *(12:20 ngày 02/11)* Credit Claude chưa dùng được (chưa đủ 7 ngày). **Phương án thay: model chữ của Meta** (Muse Spark rẻ nhất, Muse Wonder mạnh hơn), gọi qua API kiểu OpenAI của Meta. Trước hết thử 20 mẫu: đếm tỉ lệ mẫu qua bộ lọc, Anh đọc vài mẫu xem tiếng Việt có tự nhiên không. Key Meta đặt trong `~/.zac_meta_env` (chmod 600), như key Claude. Bộ sinh viết để đổi nhà cung cấp được, khi credit Claude có thì dùng thêm.
- [x] **B13.** *(Xong 13:10: Anh lưu key; bài thử tự chạy.)* **Đặt key Meta trên laptop** để chạy bài thử 20 mẫu (B12). Trong terminal, thay `DÁN_KEY_VÀO_ĐÂY` bằng key:
  - `printf 'export META_API_KEY=%s\n' 'DÁN_KEY_VÀO_ĐÂY' > ~/.zac_meta_env && chmod 600 ~/.zac_meta_env`
  - Không dán key vào chat. Tạo xong file là bài thử tự chạy (lệnh chờ của Claude), trần 3 USD.
  - Sau đó đọc file `~/zac-synth/lifemate/gen/synth_t20_show.txt` và chấm: trong 5 câu được nhận, mấy câu nghe tự nhiên như người Việt nói thật.
- [x] **B14.** *(Không cần nữa (22:39): pilot không đạt trên điểm chấm, nên kết quả chấm độ tự nhiên không đổi quyết định.)* (10 phút) **Chấm độ tự nhiên của câu sinh** (điều kiện thứ hai để sang pilot): mở `lifemate/gen/synth_review_t12_t20.md`, đánh **T** (tự nhiên) hoặc **K** (không) cho từng câu, ghi chú nếu đáp án sai ý câu nói. Chú ý nhất 9 câu đầu (bản t12 đang dùng). Đạt khi ít nhất 4/5 câu là T. Báo Claude số T/K.
  - Nếu đạt: pilot khoảng 380 mẫu đạt cho 6 app của dev_lao, khoảng 8 USD (tổng vẫn dưới 10 USD), rồi train 4B trên fit_lao + mẫu sinh trên laptop (khoảng 7 giờ) và chấm dev_lao (khoảng 1,2 giờ).
  - Sinh cho 11 app của public sau pilot sẽ làm tổng vượt 10 USD; khi đó Claude hỏi Anh trước.
  - *(13:40 ngày 02/11) Anh nâng trần lên 30 USD; chưa báo kết quả chấm. Claude sinh pilot ngay (chỉ dùng API, không cần GPU) bằng `muse-wonder-1.0`. Phần train vẫn chờ GPU rảnh (sau B11). Nếu Anh chấm thấy dưới 4/5 câu tự nhiên thì báo để Claude dừng trước khi train.*
  - *(13:48 ngày 02/11) Anh chọn "Tự bật khi xong": train pilot tự bật khi B11 và pilot sinh xong.*
  - *(14:54 ngày 02/11) Pilot sinh xong 280 mẫu đạt; train đã bật lúc 14:52. Kết quả chấm vẫn có ích: nếu dưới 4/5 câu tự nhiên thì báo để Claude dừng train, hoặc bỏ kết quả pilot.*
- [x] **B27. (09:06 ngày 05/11)** *Anh duyệt lúc khoảng 09:10 ngày 05/11 ("Chạy ngay"); job chạy từ 09:18, xong 18:09 (đóng băng 13:38–17:45). WER qua (7,65 → 7,08); file public sẵn (B29).* (1 phút) **Cho laptop fine-tune lại PhoWhisper trên gần đủ train?**
  - **Vì sao:** bản hiện tại (public 51,16) chỉ học 1.033 mẫu. Bản mới học thêm 495 mẫu dev, như cách agent học đủ 1.545 mẫu (public 45,39 → 46,29). ASR vẫn là chỗ mất nhiều điểm nhất đã đo.
  - **Claude làm:** cùng công thức Colab, giữ riêng 54 mẫu kiểm cũ để so WER với bản hiện tại. Đạt thì làm file nộp public. Laptop khoảng 4–6 giờ, vẫn dùng máy được nhưng chậm hơn. 0 USD.
  - **Luật ghi trước:** WER trên 54 mẫu kiểm không tệ hơn quá 0,5 điểm thì làm file public. Public ≥ 51,16 thì Docker đổi sang bản mới (leader thay một thư mục); thấp hơn thì giữ bản hiện tại.
- [x] **B29. (18:15 ngày 05/11)** *Anh nộp, được **49,65** (báo lúc khoảng 00:45 ngày 06/11); thấp hơn 51,16 nên Docker giữ `ckpt/asr_phoft/merged`.* (5 phút) **Nộp file public bằng PhoWhisper-ft-all** `~/zac-c3/lifemate/runs/e2e_public_q4b_all_phoftall_fix0497.jsonl` (sha256 `4d7e1cf4c80f…`; cột SLM). Báo lại điểm cho Claude.
  - **Khác file 51,16 ở đâu:** chỉ ASR (PhoWhisper-ft học thêm 495 mẫu dev). Cùng code, adapter `q4b4_all/final` và hạn 60 giây. 274/634 dòng trả lời khác. WER trên 54 mẫu kiểm: 7,65 → 7,08.
  - **Lưu ý:** nộp file `_fix0497`, không nộp `e2e_public_q4b_all_phoftall.jsonl`. File kia có dòng `public_0497` rỗng vì mẫu này đang chạy lúc đóng băng 13:38; Claude đã chạy lại riêng mẫu đó (JOURNAL entry 94).
  - **Luật ghi trước (B27):** ≥ 51,16 thì Docker đổi sang `ckpt/asr_phoft_all/merged`: Anh gửi leader thư mục này (2,9 GB, 6 file; sha256 `model.safetensors`: `478866317dfe91945ad3bc3fc1ed5da9d58ea8b2e66b1eb6256646afb3959d98`), leader thay thư mục `ckpt/asr_phoft/merged` trong image. Thấp hơn thì giữ bản hiện tại.
- [ ] **B30. (02:04 ngày 06/11; cập nhật 09:40)** (15 phút, cần sudo; **làm trước 11:00**) **Cài Docker và NVIDIA Container Toolkit trên laptop, rồi tải file image.**
  - **Cài:** `sudo bash ~/zac-c3/b28_setup_docker.sh`. Script chạy đúng các lệnh ở mục 1 của [`docs/B28_LAPTOP_DOCKER_2026-11-06.md`](docs/B28_LAPTOP_DOCKER_2026-11-06.md), rồi kiểm GPU trong container. Dòng cuối phải là `B28 SETUP OK`.
  - **Tải:** mở link Drive leader gửi trong Chrome (đăng nhập tài khoản Google mà leader đã chia sẻ file), bấm Tải xuống rồi "Vẫn tải xuống", lưu vào `~/Downloads/zac_lifemate_2026-11-05.tar` (12.635.573.248 byte). File chia sẻ riêng, phải đăng nhập mới tải được, nên Claude không tải hộ.
  - **Tuỳ Anh:** `sudo usermod -aG docker $USER` để Claude chạy `docker` không cần sudo. Nhóm này có quyền tương đương root. Không thêm thì tối nay Anh tự chạy một lệnh sudo (B31).
  - Xong thì báo Claude. Nếu còn kịp trước 11:00, Claude kiểm sha256, nạp image và chạy 3 mẫu.
- [x] **B32. (09:50 ngày 06/11)** *(11:50: Anh chọn (2), "Làm theo lịch"; train trên máy anh trai; JOURNAL entry 104.)* (5 phút quyết) **Trong 10 ngày còn lại, thử cải tiến model theo hướng nào?** Bản 05/11 vẫn đóng gói trước. Có model tốt hơn thì chỉ thay thư mục adapter hoặc ASR trong image, chạy lại B28, và phải chốt trước khoảng 13/11 để kịp L9.
  - **Đã thử sau 51,16 và không qua luật ghi trước:**
    - prompt `xref`: dev_lao chữ ASR −1,02;
    - PhoWhisper-ft-all: public 49,65;
    - chữ trộn trên fit_lao: gộp −0,69;
    - dữ liệu sinh pilot 1: dev_lao −2,09;
    - train thêm epoch: loss dev đã phẳng.
  - **Chỗ mất điểm lớn nhất (đã đo):**
    - app chưa thấy: 65% mẫu public; 4B kém 12–15 điểm;
    - ASR: khoảng 13 điểm;
    - quyết định làm / hỏi / bỏ qua, và chọn ID.
  - **(1) Hỏi anh trai kết quả gói v3** (4B train trên A100, bắt đầu từ 04/11). Không tốn tiền; Anh chỉ cần nhắn.
    - *(11:35 ngày 06/11) Xong (máy thật là 2× RTX 4090). Không có adapter nào tốt hơn để thay:*
      - *4B bf16 so với 4B 4-bit đang nộp, chữ chuẩn: dev_random 65,61 → 71,31; dev_lao 53,40 → 51,28; gộp 59,15 → 60,71;*
      - *cùng công thức train trên hai máy lệch tới 4,21 điểm, lớn hơn các mức chênh trên;*
      - *agent học trên chữ ASR: chữ chuẩn −7,97, bỏ (JOURNAL entry 101).*
  - **(2) Dữ liệu sinh v2 cho app chưa thấy:**
    - Sửa hai lý do pilot 1 thất bại: call lệch quy ước của nhãn, và 90% mẫu mở đầu bằng call đọc.
    - Chi phí: Claude viết khoảng 1 ngày; API dưới 15 USD (còn 36,97 trong trần 80); laptop train + chấm khoảng 7 giờ, chạy ban đêm.
    - Qua pilot thì sinh cho 11 app public, train lại, nộp public, rồi thay vào Docker.
    - Rủi ro cao: pilot 1 làm giảm điểm.
  - **(3) Nạp model ở bf16 thay vì 4-bit:**
    - Máy chấm có 32 GB, nên không còn bắt buộc 4-bit.
    - Adapter được train trên nền 4-bit, nên điểm có thể tăng hoặc giảm chút ít; tốc độ thì nhanh hơn.
    - Cần GPU từ 16 GB để đo (1–2 giờ); laptop 8 GB không làm được.
  - **Claude đề xuất:** làm (1) ngay hôm nay; làm (2) nếu Anh chấp nhận rủi ro và chi phí; làm (3) chỉ khi có GPU lớn, ví dụ máy anh trai.
  - *(11:35 ngày 06/11) **Claude đề xuất mới:** không làm (3), vì trên dev_lao (tập giống public nhất) bf16 kém 2,12. Còn hai lựa chọn:*
    - *giữ bản 05/11 và dồn sức vào đóng gói (B31, L9);*
    - *làm (2). Nếu anh trai cho dùng máy thêm, mỗi vòng train + chấm còn khoảng 2 giờ thay vì 7 giờ.*
  - *(11:45) Máy anh trai 1 lần mỗi ngày: vẫn đủ. Cần 2 lần chạy, lịch và luật ở JOURNAL entry 103. Anh báo nếu mỗi lần bị giới hạn giờ (giả định 6–7 giờ trên 2 GPU).*
  - *(11:40) Nếu làm (2): train trên máy anh trai, dùng đúng công thức 4-bit, mỗi bên 2 seed. Claude làm gói mới từ code `q4b-laptop`. Anh hỏi anh trai: trước 13/11 cho dùng máy mấy lần (JOURNAL entry 102).*
- [x] **B33. (12:47 ngày 06/11)** *(08/11 15:55: anh trai đã chạy và tải kết quả lên Drive; luật FAIL, chữ ASR −0,46; JOURNAL entry 107.)* (5 phút) **[Anh] Gửi anh trai gói pilot v2 và lệnh chạy; tối nay nếu anh trai rảnh.**
  - **Gói:** `~/zac_cloud_bundle_20261106_synthv2.tar.gz` (5.752.327 byte, sha256 `8314687a327301d30410549489644494250067d5522548d3b49c4accc5c0c6a3`). *(17:25: Anh đã tải lên thư mục Drive riêng.)*
  - **Thư mục Drive:** chia sẻ cho tài khoản Google của anh trai với quyền "Người chỉnh sửa", để anh trai tải kết quả lên được. Giữ chế độ "Hạn chế", không bật "Bất kỳ ai có đường liên kết": gói có dữ liệu thi.
  - **Hướng dẫn:** gửi anh trai bản có sẵn link, `~/Zalo AI Challenge/cloud_results/anh_trai/BROTHER_AI_GUIDE_PILOT_V2_2026-11-07.md` (ngoài git; có thể tải lên cùng thư mục Drive). File có:
    - cách tải gói từ Drive (trình duyệt hoặc `rclone`);
    - lệnh chạy, khoảng 6 giờ;
    - cách kiểm và cách xử lý lỗi;
    - mẫu báo cáo và cách tải kết quả lên.
  - **Anh trai tải lên cùng thư mục Drive:** `zac_v4_results.tar.gz` và báo cáo `ZAIC_pilot_v2_report_<ngày>.md`. Anh tải cả hai về `~/Zalo AI Challenge/cloud_results/anh_trai/` rồi báo Claude.
  - **Sau đó:**
    - Claude áp luật ghi trước. Đạt thì sinh dữ liệu cho 11 app public (khoảng 15 USD) và chuẩn bị lần chạy 2: train bản cuối trên đủ 1.545 mẫu.
    - Không đạt thì dừng, giữ bản 05/11.
- [x] **B41. (20:25 ngày 09/11)** *(20:58: Anh đồng ý; JOURNAL entry 125.)* (3 phút; JOURNAL entry 124) **[Anh] Xác nhận cách lấy state cho nhánh D1 của 46 app đã thấy.**
  - Bản giao việc ghi: `final_state` của app mà mẫu không ghi là state ban đầu. Dữ liệu không như vậy: `final_state` chỉ có app mà nhãn đã ghi.
  - **Claude đề xuất:** dùng `final_state` sau khi ghi làm state ban đầu cho kịch bản mới, cộng kết quả các lệnh đọc không tham số. Phủ 39/46 app; 4 app chỉ đọc (fuel_price, lottery, exchange_rate, calculator) phải tự dựng state.
  - Anh trả lời: đồng ý, hoặc cách khác.
- [x] **B40. (19:18 ngày 09/11)** *(20:25: Anh chọn `claude-opus-5-5`; JOURNAL entry 124.)* (15 phút; JOURNAL entry 123) **[Anh, có thể cùng Leader] Đọc 30 kịch bản × 3 câu và chọn model viết câu nói.**
  - **File:** `lifemate/gen/d1_t1_say_compare.md`. Mỗi kịch bản có dòng "muốn" (điều người dùng cần) và ba câu do ba model viết.
  - **Chấm ba điều:** câu có tự nhiên như người nói thật không; có nói đủ và đúng mọi con số, ngày giờ, tên không; có thêm việc hay thông tin ngoài dòng "muốn" không.
  - **Claude đề xuất:** `claude-opus-5-5` làm model chính (khoảng 7,7 USD mỗi 1.000 câu); có thể trộn `muse-spark-1.3` (3,5 USD) cho đa dạng, nhưng không cho nó viết câu tự sửa giữa chừng.
  - Báo Claude: model chọn, và những câu Anh thấy sai để sửa prompt.
- [x] **B39. (17:32 ngày 09/11)** *(19:18: Anh đã tạo `~/.zac_anthropic_env`.)* (2 phút; JOURNAL entry 120) **[Anh] Tạo file key Anthropic để Claude thử model viết câu nói (cửa 1).**
  - Chạy trong terminal, dán key khi được hỏi (key không hiện lên màn hình, không dán vào chat):
    `read -rs -p "Anthropic API key: " K; echo; printf 'export ANTHROPIC_API_KEY=%s\n' "$K" > ~/.zac_anthropic_env; chmod 600 ~/.zac_anthropic_env; unset K`
  - Key Meta đã có ở `~/.zac_meta_env` (tạo 02/11). Nếu Anh muốn dùng key Meta mới (90 USD) thì chạy lại lệnh tương tự với `META_API_KEY` và `~/.zac_meta_env`.
  - Cửa 1 chi tối đa 5 USD cho cả hai nhà cung cấp.
- [x] **B38. (17:15 ngày 09/11)** *(17:25: Anh duyệt; Leader đồng ý; trần API bỏ giới hạn; anh trai chạy từ khoảng 12:00; JOURNAL entry 119.)* (5 phút đọc; JOURNAL entry 118) **[Anh, bàn với Leader] Duyệt D1 theo ba cửa.**
  - **Cửa 0** (CPU, 0 USD): code tự sinh lại nhãn train từ catalog; khớp ≥ 80% thì đi tiếp, dưới 60% thì dừng D1.
  - **Cửa 1** (API tối đa 5 USD): 50 mẫu cho 3 app public; Anh đọc 20 câu.
  - **Cửa 2** (API tối đa 35 USD): sinh đủ; laptop đo trên dev_lao (2 seed, khoảng 16 giờ), máy anh trai train bản cuối sau đợt hiện tại.
  - **Anh trả lời:** trần API mới là bao nhiêu (ghi nhớ hiện tại: 80 USD tổng, đã chi 52,39); Leader có đồng ý đưa D1 lên trước không; anh trai bắt đầu chạy lúc mấy giờ.
- [ ] **B37. (15:45 ngày 09/11)** (5 phút đọc; JOURNAL entry 117) **[Anh, bàn với Leader] Quyết hai việc trong lúc chờ máy anh trai.**
  - **Việc 1: chạy D5 trên dev có nhãn bằng laptop.** Khoảng 1,5 giờ GPU, 0 USD; laptop đang rảnh.
    - Câu hỏi: D5 tăng hay giảm điểm trên 495 mẫu có nhãn; luật "lặp 3 bước thì dừng" có cắt lệnh hỏi lại đúng không.
    - Kết quả không đổi luật public 50,77; chỉ dùng để sửa luật dừng nếu cần.
  - **Việc 2: gửi Leader ba luật bổ sung, viết trước khi có kết quả train.**
    - Nhánh thắng không được làm số mẫu vượt 25 giây trên laptop tăng quá 1% số mẫu.
    - Nhánh nằm trong khoảng +1,5 tới +3,0 thì chạy thêm 2 seed, không loại ngay.
    - Bản giai đoạn 2 chỉ thay bản 05/11 khi trung bình public 2 seed ≥ bản cùng trạng thái D5 + 1,5.
  - **Kèm theo:** cho Claude push nhật ký 112–117 lên `main` hay chưa.
- [x] **B36. (02:13 ngày 09/11)** *(17:25: Anh nộp, được **52,68**; bản thử 51,07; +1,61; giữ D5; JOURNAL entry 119.)* (2 phút) **[Anh hoặc leader] Nộp file public có bật D5 (search guard).**
  - **File:** `lifemate/runs/pub_d5_2026-11-09/full/submission.jsonl`. Chỉ khác lượt thử 51,07 ở chỗ bật `SEARCH_GUARD=1`.
  - **Luật viết trước (RANKING §5 của Leader):** điểm ≥ 50,77 (51,07 − 0,3) thì giữ D5 và bật mặc định trong `docker/predict.sh` và `lifemate/submit.py`; thấp hơn thì bỏ.
  - Ghi điểm vào đây và báo Claude.
- [x] **B35. (17:57 ngày 08/11)** *(20:25: Anh nộp, được 51,07; file 05/11 51,16; trang nhận trường `time`; JOURNAL entry 109.)* (2 phút, sau khi Claude báo file xong) **[Anh hoặc leader] Nộp thử file public làm bằng cấu hình nộp cuối.**
  - **File (xong 19:59, kiểm đạt):** `lifemate/runs/pub_trial_2026-11-08/full/submission.jsonl`, 634 dòng, có trường `time`.
  - **Ghi lại hai điều:**
    - trang nộp có nhận dòng có trường `time` không;
    - điểm so với 51,16. 625/634 dòng giống hệt file 51,16; 9 dòng bị hạn 25 giây cắt các lời gọi cuối, nên điểm có thể thấp hơn tối đa khoảng 1,4.
  - **Điểm thấp hơn 51,16 quá 1,4 thì báo Claude:** khi đó có chỗ khác ngoài hạn 25 giây.
- [ ] **B34. (16:45 ngày 08/11)** *(18:41 ngày 09/11: chưa làm. Gói train mới cũng nằm trong thư mục, quyền của gói vẫn là "ai có link đều sửa được". Leader là chủ thư mục; tài khoản của Anh cũng có nút "Manage access" nên có thể tự đổi; JOURNAL entry 122.)* (5 phút) **[Anh] Khoá thư mục Drive và dọn dữ liệu trên máy anh trai.**
  - **Thư mục Drive `ZAIC_2026`:** đang xem được mà không cần đăng nhập, tức chế độ "Bất kỳ ai có đường liên kết". Trong đó có hai gói chứa dữ liệu thi có licence (`zac_cloud_bundle_20261031_v3.tar.gz`, `zac_cloud_bundle_20261106_synthv2.tar.gz`) và file image `gui_leader_phoft_2026-11-05.tar` (3,14 GB).
    - Chuyển thư mục sang "Hạn chế": Chia sẻ → Quyền truy cập chung → Hạn chế.
    - Xoá hai gói, vì pilot đã xong và không có lần chạy 2.
    - Giữ file image nếu leader còn cần, nhưng chỉ chia sẻ cho người trong đội.
  - **Máy anh trai:** nhờ xoá `~/zac_v4`, `~/ZAIC_2026`, các file `zac_cloud_bundle_*.tar.gz`, `cloud_results_*.tar.gz`, `zac_logs.tar.gz`, `zac_v4_results.tar.gz` (theo mục 8 của file hướng dẫn).
- [x] **B31. (09:40 ngày 06/11)** *(02:09 ngày 09/11: xong. 3 mẫu và hai lượt 634 mẫu đều `ok`; lượt 1 giống file 51,16 ở 627/634 dòng; hai lượt khác nhau 1 dòng, do hạn 25 giây; lâu nhất 25,6 giây mỗi mẫu; JOURNAL entry 115.)* (2 phút; máy chạy khoảng 4 giờ) **Tối nay, khi mở lại laptop: cắm sạc, tắt bớt app nặng, báo Claude.**
  - **(22:20 ngày 08/11) Đang chạy từ 22:14, xong khoảng 02:40 ngày 09/11. Anh để máy cắm sạc, đừng tắt máy; gập nắp được.** 3 mẫu đã đạt.
  - Khi đó Claude chạy `bash ~/zac-c3/b28_start.sh all`. Lệnh này chạy trong một unit riêng, chặn ngủ cả khi gập máy, và tự dừng nếu chưa có quyền docker.
  - Nếu chưa vào nhóm, Anh chạy `sudo systemd-inhibit --what=sleep:idle:handle-lid-switch --why=B28 bash /home/truyen-anh-thach/zac-c3/b28_run.sh all` và để nguyên terminal.
  - **Thứ tự chạy:**
    1. kiểm số byte và sha256, rồi nạp image;
    2. `info`: ID image, CUDA, torch có sm_120 cho RTX 5090 không;
    3. 3 mẫu;
    4. đủ 634 mẫu hai lần.
  - Bước nào đã xong thì bỏ qua; bước nào hỏng hoặc `ok` không đúng thì dừng.
  - Claude báo Anh và leader:
    - có `"ok"` không;
    - thời gian mỗi mẫu;
    - số dòng khác giữa hai lần chạy;
    - số dòng khác file 51,16;
    - ID image.
- [x] **B28. (10:24 ngày 05/11)** *Anh chọn dùng laptop lúc khoảng 01:15 ngày 06/11 (không thuê GPU); việc tiếp theo ở B30 và L8. Laptop không đo được thời gian trên A30.* (1 phút quyết; thuê khoảng 2–3 giờ) **Thuê một GPU 24 GB (tốt nhất A30) để chạy đúng image Docker?**
  - **Vì sao:** máy leader 4 GB không chạy nổi bước agent. Chưa ai chạy image trọn từ đầu tới cuối, và thời gian trên GPU giống máy chấm chưa đo. Đây là rủi ro mất bài lớn nhất còn lại.
  - **Làm gì:** leader đẩy image lên registry riêng, chạy trên máy thuê:
    - 3 mẫu để có `"ok": true`;
    - đủ 634 mẫu public để đo thời gian mỗi mẫu và đếm số mẫu dừng vì hết giờ;
    - chạy lại lần nữa để kiểm kết quả giống nhau.
  - **Khi nào:** sau khi B27 có kết quả (tối 05/11 hoặc 06/11), để chỉ test image cuối một lần.
  - *(00:47 ngày 06/11) ASR đã chốt (B29: 49,65, giữ bản hiện tại), nên image leader đã build là bản cuối về model. **Làm được ngay.***
  - *(18:15 ngày 05/11) B27 đã có kết quả; chờ điểm B29 để chốt ASR rồi test image cuối. `predict.sh` 3 mẫu trên laptop (không Docker) đạt `"ok": true`, nên đường code đã đúng; B28 chỉ còn kiểm chính image và đo thời gian.*
  - **Tiền:** của Anh hoặc leader, không tính vào trần API. Claude không thuê.
  - **Nếu không thuê:** Anh tự cài Docker + NVIDIA Container Toolkit trên laptop (cần sudo) rồi chạy image trên RTX 4070. Cách này kiểm được `"ok"` nhưng không đo được thời gian trên A30.
- [ ] **B26. (00:30 ngày 05/11; cập nhật 10:24)** *Leader làm xong phần build (10:20 ngày 05/11): sha256 khớp; image 12,6 GB, không có Whisper-turbo-ft; chữ ASR 3 mẫu khớp tham chiếu. Còn thiếu `"ok"` vì GPU 4 GB hết VRAM ở bước agent (B28).* (Anh 10 phút, leader khoảng 1–2 giờ) **Đổi ASR trong Docker sang PhoWhisper-ft.** Hướng dẫn đầy đủ: [`docs/LEADER_DOCKER_PHOFT_2026-11-05.md`](docs/LEADER_DOCKER_PHOFT_2026-11-05.md).
  - **Anh gửi riêng cho leader** (trong `~/zac-c3/lifemate/`; có lệnh `tar` gói tất cả trong hướng dẫn):
    - `ckpt/asr_phoft/merged/` (2,9 GB): đúng bản cho ra 51,16.
    - `ckpt/q4b4_all/final/` (263 MB), nếu chưa gửi hôm 04/11.
    - `runs/e2e_public_phoft_asr.jsonl`, `runs/e2e_public_q4b_all_phoft.jsonl`, `runs/e2e_public_q4b_all_phoft_trace.jsonl` (1,5 MB, để so).
  - **Leader:**
    - Kiểm sha256 của hai file model.
    - Chép vào image, đặt `ASR_MODEL=ckpt/asr_phoft/merged`. Code (nhánh `q4b-laptop`) và các biến khác giữ nguyên: adapter `q4b4_all/final`, 4-bit, `TIME_BUDGET` 25.
    - Chạy thử 3 mẫu trong Docker khi tắt mạng.
  - **Còn mở:** máy leader chỉ có GPU 4 GB, không chạy nổi bước agent (thiếu 116 MiB ở warm-up), nên chưa có `"ok"` và chưa đo thời gian trên GPU 24 GB (B28). Trên laptop, PhoWhisper thêm trung bình 0,9 giây mỗi mẫu, nhiều nhất khoảng 3,4 giây.
  - **Tổng tham số:** ASR 1,543B + Qwen3-4B 4,022B + LoRA 0,066B = khoảng 5,63B, dưới trần 6B.
- [x] **B25. (18:41 ngày 04/11)** *Anh nộp, được **51,16** (báo lúc khoảng 00:28 ngày 05/11); hơn 46,29 nên Docker đổi sang PhoWhisper-ft (B26).* (5 phút) **Nộp file public bằng PhoWhisper-ft** `~/zac-c3/lifemate/runs/e2e_public_q4b_all_phoft.jsonl` (634 dòng, kiểm định dạng đạt, sha256 `b3f86ef0c812…`), **chọn cột SLM**, rồi báo điểm cho Claude. Anh hoặc leader nộp; Claude không nộp.
  - **Khác file 46,29 ở đâu:** chỉ ASR (PhoWhisper-large fine-tune thay cho Whisper-turbo fine-tune). Cùng code, adapter `q4b4_all/final` và hạn giờ. 345/634 dòng trả lời khác.
  - **Luật ghi trước (B24):** ≥ 46,29 thì Docker đổi sang PhoWhisper-ft; thấp hơn thì giữ Whisper-turbo-ft.
  - **Nếu đổi:** Anh gửi riêng cho leader `~/zac-c3/lifemate/ckpt/asr_phoft/merged` (khoảng 3,1 GB). Leader đo thời gian trên A30: trên laptop PhoWhisper thêm trung bình 0,9 giây mỗi mẫu, nhiều nhất khoảng 3,4 giây.
- [x] **B24. (16:10 ngày 04/11)** *Anh duyệt lúc khoảng 16:40 ngày 04/11. Không phải tải: model gốc vẫn còn trong cache (Claude kiểm sai lúc 16:10). Job chạy từ 16:45.* (1 phút) **Cho tải lại model gốc PhoWhisper-large để làm file nộp public bằng PhoWhisper-ft?**
  - **Vì sao:** 4B đọc chữ PhoWhisper fine-tune qua luật ghi trước trên dev (gộp +1,71; dev_lao +2,10), nhưng khoảng tin cậy còn chứa 0. Public là bằng chứng tốt nhất hiện có.
  - **Cần tải:** `pytorch_model.bin` của `vinai/PhoWhisper-large` (revision `b9136a44`, 6,17 GB, licence BSD-3) từ Hugging Face. File này không còn trong cache của laptop; adapter fine-tune (221 MB) thì có sẵn.
  - **Claude làm:** ghép adapter, kiểm chữ dev khớp bản Colab, rồi chạy `predict.sh` trên public_test với `q4b4_all/final`, cùng hạn 25 giây như file 46,29 (chỉ ASR thay đổi). Khoảng 2–2,5 giờ laptop, xong trước lượt `xref` lúc 23:30. 0 USD.
  - **Luật cho Docker, ghi trước:** public ≥ 46,29 thì Docker đổi sang PhoWhisper-ft; thấp hơn thì giữ Whisper-turbo fine-tune.
  - Nếu đổi: tổng hệ thống khoảng 5,6B (dưới trần 6B); leader cần bản ghép PhoWhisper-ft (khoảng 3,1 GB), Anh gửi riêng.
- [x] **B23. (14:40 ngày 04/11)** *Anh duyệt cả hai lúc 14:43 ngày 04/11: PhoWhisper chiều nay, `xref` tự chạy lúc 23:30. Trả lời Codex: anh trai chạy gói v3 (không trùng), trần API thêm 30 USD (tổng 80) khi cần, ưu tiên private.* (2 phút) **Duyệt thí nghiệm GPU theo báo cáo Codex.** Claude đề xuất:
  - **Chiều nay:** chấm 4B hiện tại với chữ PhoWhisper fine-tune trên dev_random và dev_lao. Khoảng 2,4 giờ GPU, không sửa code, 0 USD. Giữ nếu gộp 495 dòng ≥ 47,17 và dev_lao không giảm quá 1,0.
  - **Đêm nay:** train lại fit_lao với prompt có thêm `x-ref` và `returns`, rồi chấm dev_lao bằng cả chữ ASR lẫn chữ chuẩn. Khoảng 8,5 giờ, 0 USD. Qua cửa 1 nếu dev_lao chữ ASR ≥ +2, chữ chuẩn ≥ −2 và nhóm hỏi lại ≥ −3. Dự kiến tăng ít (mô tả tham số đã ghi nguồn ID).
  - Kèm 3 câu hỏi của Codex: máy anh trai đang train gì; có nâng trần API nếu cần không; ưu tiên public hay private.
- [x] **B22. (13:51 ngày 04/11)** *Anh giao, Codex xong lúc khoảng 14:38 ngày 04/11.* (2 phút giao, Codex chạy khoảng 1–3 giờ) **Giao việc cho Codex:** mở Codex trong `~/Zalo AI Challenge`, gõ *"Đọc và làm đúng theo `docs/CODEX_4B_STRATEGY_PROMPT_2026-11-04.md`."* Codex chỉ phân tích trên CPU, không dùng GPU hay API, viết báo cáo `docs/research/CODEX_4B_STRATEGY_2026-11-04.md`. Xong thì báo Claude để Claude đọc, commit và đề xuất thí nghiệm cho Anh duyệt.
- [x] **B21. (13:37 ngày 04/11)** *Anh nộp loại APIs/Others: **75,52** (báo lúc khoảng 13:45 ngày 04/11).* (5 phút) **Nộp file public bản API `xhigh`** `~/zac-docker/lifemate/runs/e2e_public_api_spark_xhigh_drop.jsonl` (634 dòng, kiểm định dạng đạt, sha256 `99b2ff9b6656…`), **chọn loại APIs/Others**, rồi báo điểm cho Claude. Sau đó Claude viết prompt cho Codex.
- [x] **B20. (12:45 ngày 04/11)** *Anh nộp loại APIs/Others: **69,47** (báo lúc khoảng 12:50 ngày 04/11).* (5 phút) **Nộp file public bản Meta API** `~/zac-docker/lifemate/runs/e2e_public_api_spark_min.jsonl` (634 dòng, kiểm định dạng đạt, sha256 `0d264ca094e8…`), **chọn loại APIs/Others**, rồi báo điểm cho Claude. Điểm này cho biết pipeline hiện tại (ASR fine-tune, prompt, vòng lặp agent) đạt tới đâu khi model mạnh hơn 4B. Docker vẫn dùng 4B. Nếu trang thi giới hạn số lần nộp mỗi ngày, cân nhắc trước khi nộp.
- [x] **B19. (07:55 ngày 04/11)** *Anh nộp, điểm **46,29** (báo lúc 12:21 ngày 04/11); hơn 45,39 nên Docker dùng `ckpt/q4b4_all/final`.* (5 phút) **Nộp file public mới** `~/zac-c3/lifemate/runs/e2e_public_q4b_all.jsonl` (634 dòng, kiểm định dạng đạt, sha256 `483fecf54c75…`) và báo điểm cho Claude. Adapter mới học trên đủ 1.545 mẫu; bản 45,39 học trên 1.312 mẫu. Luật ghi trước: điểm từ 44,39 trở lên thì Docker dùng `ckpt/q4b4_all/final`; thấp hơn thì giữ `ckpt/q4b4_fit_random/final` (JOURNAL entry 75). Claude không nộp.
- [x] **B18. (16:27 ngày 03/11)** *Anh nhờ Claude tự review và merge; review đạt, đã merge vào `q4b-laptop` lúc 17:22 (commit `a2615ee`).* (15 phút) **Review [PR #12](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/12)** (cùng leader, trước khi đóng Docker): bước khởi động không tính giờ; `predict.sh` mặc định Qwen3-4B 4-bit, hạn 25 giây; thêm `LOAD_4BIT`, `TIME_BUDGET` vào `eval_ckpt.sh`, `train_local.sh`. Đã thử trên GPU: file nộp giống hệt bản 45,39 trên 3 mẫu public. Ban đầu ghi "Claude không merge"; Anh cho phép merge riêng PR này lúc 17:22.
- [x] **B17. (15:07 ngày 03/11)** *Anh chọn tự bật sau (15:11 ngày 03/11); 16:27: Anh nhờ hẹn giờ, Claude hẹn tự chạy lúc 00:30 ngày 04/11 (chỉ khi đã cắm sạc). 00:13 ngày 04/11: Anh bảo chạy ngay; Claude bật và tắt hẹn giờ. Huỷ: `systemctl --user disable --now lifemate-q4b-all-kick.timer`.* (1 phút) **Bật train lại 4B trên đủ 1.545 mẫu rồi làm file nộp public?** Chữ trộn không qua luật gộp (JOURNAL entry 68), nên theo kế hoạch: train lại bản 4B hiện tại (bản cho 45,39) trên đủ dữ liệu train. Laptop bận khoảng 8 giờ: train 6,3 giờ, file nộp 1,7 giờ. Bật khoảng 15:30 thì xong khoảng 23:30. Dừng và chạy tiếp được nếu cần mang máy đi. Trả lời Claude, hoặc tự bật: `bash ~/zac-c3/start_q4b_all.sh`.
- [x] **B16. (00:22 ngày 03/11)** *Anh chọn chưa cần (00:52 ngày 03/11).* (5 phút) **Có dùng Colab trả phí (L4 hoặc A100) để đo bf16 và thời gian không?** Laptop 8 GB không nạp được 4B ở bf16. Trên GPU 24 GB, Claude so điểm khi nạp bf16 với 4-bit và đo giây mỗi mẫu, khoảng 1–2 giờ GPU. Tiền của Anh, không tính vào trần 30 USD API. Colab miễn phí (T4) không làm được việc này (JOURNAL entry 64).
- [x] **B15. (22:44 ngày 02/11)** *Anh chọn chạy đêm nay (00:16 ngày 03/11); laptop chạy từ 00:19.* (2 phút) **Chọn thí nghiệm tiếp theo trên laptop** (JOURNAL entry 63). Claude đề xuất: 4B học trên chữ trộn (một nửa `audio_text`, một nửa chữ Whisper-turbo), train trên fit_random, chấm dev_random; khoảng 6,7 giờ, cắm sạc, không gập máy. Giữ nếu chữ ASR fine-tune tăng ít nhất 1,0 so với 54,01 và chữ chuẩn không giảm quá 2,0. Sau đó train lại trên đủ train để nộp public.
- [ ] **B7.** (tuỳ chọn) Xác minh số điện thoại cho tài khoản Kaggle của Anh (thêm khoảng 30 giờ GPU/tuần). Lưu bằng chứng BTC cho phép nhờ anh trai train vào mục 4.

**Leader:**
- [x] **L1.** (5 phút, **trước 18:00**) **Nộp public** file `e2e_public_turbo.jsonl` Anh gửi ở B1. Đây là mốc public đầu tiên; theo hai tập dev, điểm dự đoán khoảng 17–32. Ghi điểm và giờ nộp: … Claude không nộp.
  - ***Điểm: 25,9300*** (Anh báo lúc 16:05). Nằm giữa dev_random 31,69 và dev_lao 17,14, gần số gộp 23,99, nên dev local dự đoán public khá sát (JOURNAL entry 46).
- [x] **L2.** Kaggle: xong khoảng 15:50; leader đã gửi kết quả (đã giải nén ở `cloud_results/kaggle/`). **Xoá dataset và notebook trên Kaggle** nếu chưa xoá. Không cần chạy lại lượt agent trên Kaggle (T4 quá chậm).
- [x] **L3.** (15 phút thao tác, máy chạy 2–2,5 giờ) **Colab: fine-tune ASR PhoWhisper** trên Colab của leader.
  - Bấm "Tạo bản sao" file gói Anh chia sẻ ở B3. Tên kiểu "Bản sao của ..." vẫn dùng được.
  - Mở Colab, chọn T4 GPU, chạy ô mount Drive, rồi dán ô lệnh và đổi `MODELS="pho"`. **Để tab mở.**
  - Kết quả: `My Drive/zac_out/asr_results_pho.tar.gz`. Colab và Kaggle chạy song song được.
  - ***Xong (00:05 ngày 01/11, Anh báo):*** train 163 phút trên T4, 3 epoch. WER trên phần kiểm giữ lại của train 23,7 → 7,7. Trên dev_random, WER lượt cuối 25,9 → 9,2; dev_lao 26,9 → 12,9. Đã giải nén ở `cloud_results/colab_leader/x/`.
- [x] **L4.** *(Leader báo sáng 06/11; Claude tóm tắt lúc 09:40 ở [`docs/BTC_DOCKER_GUIDE_2026-11-06.md`](docs/BTC_DOCKER_GUIDE_2026-11-06.md). Máy chấm: RTX 5090 32 GB, driver 595.58.03, CUDA 13.2. Giao diện nộp cuối khác image 05/11, xem L9. Hướng dẫn không ghi giới hạn 30 giây hay A30. Q1 và bảng xếp hạng chưa có tin.)* (20 phút) Forum BTC: hướng dẫn Docker, máy chấm, Q1 (so khớp tham số). Xem bảng xếp hạng public: điểm cao nhất, số đội. Ghi vào mục 4.
- [ ] **L5.** (cùng B5) Nghe 18 câu ASR sai cùng Anh. Lập danh sách "cụm từ nguy hiểm" (số, giờ, tên người, từ phủ định, tự sửa giữa câu).
- [ ] **L6.** (1–2 giờ) Bản Docker đầu tiên quanh `lifemate/scripts/predict.sh`, lấy từ nhánh `time-budget` ([PR #9](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/9)) để có giới hạn thời gian mỗi mẫu (tính cả ASR). *(16:27 ngày 03/11, cập nhật 17:22: nên lấy từ nhánh `q4b-laptop`, đã có PR #12 sau khi merge ([PR #12](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/12)), có thêm 4B 4-bit, hạn 25 giây và bước khởi động; lệnh mẫu ở đầu `predict.sh`.)* Dựng trên máy leader; GPU 4 GB không chạy nổi cả ASR lẫn LLM, nên chạy thử 1–2 mẫu bằng CPU. Hạn Docker là 16/11. *(12:22 ngày 04/11: dùng adapter `ckpt/q4b4_all/final` (public 46,29), Anh gửi riêng; truyền `ADAPTER=ckpt/q4b4_all/final`.)*
- [x] **L8. (02:04 ngày 06/11)** *(Leader gửi sáng 06/11: file trên Drive, chỉ chia sẻ cho Anh; 12.635.573.248 byte; sha256 `190bdeeb6157…`; image `zaic-lifemate`; lệnh chạy 3 mẫu. **Thiếu ID của image** (tin nhắn chỉ ghi "sha256"); Claude ghi ID sau khi nạp và gửi lại leader để so.)* (30 phút + thời gian tải lên) **Gửi Anh image Docker đã build ngày 05/11** để chạy thử trên laptop (B28), theo mục 2 của [`docs/B28_LAPTOP_DOCKER_2026-11-06.md`](docs/B28_LAPTOP_DOCKER_2026-11-06.md):
  - file `docker save` (khoảng 12–13 GB) kèm `sha256sum`, gửi riêng qua Google Drive;
  - đúng lệnh `docker run` đã dùng để chạy 3 mẫu khi tắt mạng (mount dữ liệu, chỗ ghi kết quả, biến môi trường);
  - tên, tag và ID của image.
- [ ] **L9. (09:40 ngày 06/11)** (khoảng 1 ngày; **trước 11:59 ngày 16/11**) **Gói nộp cuối theo hướng dẫn BTC.** Image 05/11 chỉ để kiểm nội bộ. Bảng 9 việc còn thiếu ở cuối [`docs/BTC_DOCKER_GUIDE_2026-11-06.md`](docs/BTC_DOCKER_GUIDE_2026-11-06.md). Chính là:
  - `/code/predict.sh` đọc `/data/<split>`, ghi `/result/submission.jsonl`, tham số đặt sẵn, không dùng biến môi trường;
  - trường `time` (mili giây) trên mỗi dòng; in thời gian nạp model và predict ra stdout;
  - base image CUDA 13.2, torch có sm_120 (RTX 5090);
  - `jupyterlab`, `start_jupyter.sh`, `predict_notebook.ipynb` chạy từng mẫu, ra `/result/jupyter_submission.jsonl` cùng điểm với `submission.jsonl`;
  - seed cố định;
  - `README.md` và `training_code/`, kèm URL tải dữ liệu và model. **Anh và leader quyết:** dữ liệu train là của BTC, `gen/` sinh từ train, repo đang public;
  - khi nộp: `docker save | gzip`, `md5sum`, Drive "Anyone with the link".
  - *(10:07 ngày 06/11) Phần code đã có ở [PR #15](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/15) (nhánh `docker-submit` → `q4b-laptop`, chưa merge): script bọc `/code/predict.sh`, notebook đo thời gian, `start_jupyter.sh`, trường `time`, seed cố định. Test CPU đạt; chưa chạy trên GPU, nên chưa kiểm notebook có cùng điểm với `predict.sh` không. Anh hoặc leader review trước khi merge.*
- [ ] **L7.** Review PR #8 cùng Anh (B6). Sau đó tới #4 (ASR, predict), #6 (cloud), #7 (fine-tune ASR), #9 (giới hạn 30 giây, chốt chặn ID; nên xem trước khi đóng Docker) khi tới lượt. #12 (sẵn sàng Docker) đã merge vào `q4b-laptop` lúc 17:22 (B18).

**Claude** (Anh không cần nhắc):
- [x] **C1.** Khoảng 16:50: đọc kết quả lượt (1) trên laptop. So theo cặp với 53,92 (chữ chuẩn) và 31,69 (chữ turbo), báo trong chat, ghi JOURNAL.
  - ***Xong 17:01:*** đọc chữ turbo 33,22 so với 31,69 (+1,52 [−3,58; +6,62]); đọc chữ chuẩn 48,55 so với 53,92 (**−5,37 [−10,75; −0,05]**). → Không dùng công thức này; giữ agent học trên `audio_text`, ưu tiên fine-tune ASR (JOURNAL entry 48).
- [x] **C2.** Khoảng 20:00: đọc lượt (2) B-up. Luật đặt trước: dev_random không giảm quá 1 điểm thì giữ công thức B-up.
  - ***Xong 20:22:*** đọc chữ chuẩn 51,19 so với 53,92 (**−2,72** [−8,08; +2,52]); đọc chữ turbo 29,06 so với 31,69 (−2,64 [−6,58; +1,35]). Giảm quá 1 điểm → **không giữ B-up**. Hỏi lại tăng 49,4 → 69,1 nhưng execute giảm 51,0 → 44,0, vì hỏi thừa ở 22 mẫu cần làm (mốc: 14). Không dò thêm tỉ lệ nhân bản trên dev_random (mục F) (JOURNAL entry 49).
- [x] **C3.** Khi `asr_results_*` về (GPU laptop rảnh từ 21:05): chấm agent bằng transcript ASR mới trên laptop, so thẳng với 31,69 và 17,14. Khoảng 10 phút cho mỗi model trên mỗi tập dev.
  - *Đang chạy (00:05 ngày 01/11):* 5 lượt trên code `time-budget` (chốt chặn ID bật): hai ASR fine-tune trên hai tập dev, cộng một lượt chữ turbo trên dev_lao với cùng code để so cho công bằng. **Luật đặt trước:** so điểm gộp 495 dòng của hai tập dev; model nào cao hơn thì thắng, cách nhau dưới 1 điểm thì chọn Whisper-turbo (nhỏ và nhanh hơn). Nếu người thắng kém hơn trên dev_lao quá 1 điểm thì không tự chọn mà báo đội quyết.
  - ***Xong 01:05 ngày 01/11:*** Điểm gộp 495 dòng (dev_random + dev_lao): Whisper-turbo fine-tune **33,07**, PhoWhisper fine-tune **33,41**, turbo chưa fine-tune 23,99, chữ chuẩn 44,23. So với turbo chưa fine-tune: turbo-ft +9,08 [+5,42; +12,84], Pho-ft +9,42 [+5,73; +13,25]. Pho-ft so với turbo-ft: +0,35 [−2,89; +3,61] (dev_random +0,40, dev_lao +0,30). → **Chọn Whisper-turbo fine-tune.** Chốt chặn ID chặn 1 call (turbo-ft) và 7 call (Pho-ft) trên dev_lao, đều là ID bịa (JOURNAL entry 52).
- [x] **C4.** Trong lúc chờ (chỉ dùng CPU): PR sửa `agent.py:150` cho giới hạn 30 giây mỗi mẫu (tính cả thời gian ASR), kèm chốt chặn ID làm lưới an toàn. Thêm trần thời gian và trần token cho mỗi bước: lượt B-up có mẫu `train_0830` sinh lặp "000…" hai bước liền, mỗi bước tới trần 512 token, mất 23,4 giây. *Đang làm (20:33).*
  - ***Xong 21:08:*** [PR #9](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/9) (xếp chồng lên #7), chờ review. dev_random giống hệt 233/233 dòng (53,92); chữ turbo giống hệt 233/233 (31,69); dev_lao 35,62 so với 35,53 (+0,10 [0,00; +0,29]; 4 call sai bị chặn, tốt 1, kém 0); `train_0830` với ngân sách 15 giây dừng ở 15,01 giây (code cũ: 23,4). Luật đặt trước: nhận phần thời gian, **chốt chặn bật mặc định** (JOURNAL entry 50).
- [ ] **C5.** *(Phần file nộp public xong 01:35 ngày 01/11: `lifemate/runs/e2e_public_turboft.jsonl`, Anh đã nộp ở B8: 35,24. Phần gộp kết quả máy anh trai chờ tới khi có.)* Khi kết quả từ các máy đã về: viết **`docs/RESULTS_2026-10-31.md`** gộp tất cả (laptop, Kaggle, Colab, anh trai). Từ đó chọn ASR, chọn công thức agent cho vòng sau, và chuẩn bị file nộp public mới bằng ASR đã fine-tune.
- [x] **C6.** *(Chạy 20:47 ngày 01/11 – 03:28 ngày 02/11. Lượt đầu 09:27–10:13 đã bỏ vì máy phải mang đi học.)* Train Qwen3-4B 4-bit trên fit_lao bằng laptop, rồi chấm dev_lao (chữ ASR fine-tune, rồi chữ chuẩn). Khoảng 16:30–17:00: áp luật đặt trước (JOURNAL entry 55) và báo trong chat.
  - 4B hơn ít nhất 1 điểm trên dev_lao chữ ASR fine-tune → lượt tiếp trên laptop: 4B trên fit_random / dev_random, rồi quyết bằng điểm gộp 495 dòng như C3.
  - Kém hơn mức đó → giữ 1.7B. Nếu riêng chữ chuẩn hơn từ 3 điểm trở lên thì báo để đội quyết.
  - ***Xong 03:28 ngày 02/11:*** chữ ASR fine-tune 24,55 → **39,20** (+14,65 [+8,79; +20,49]; tốt 78, kém 30, giống 154). Chữ chuẩn 35,62 → **53,40** (+17,78 [+11,74; +23,61]). → **4B thắng vòng này**, chạy C7. Hỏi lại 11,1 → 39,4; execute 25,1 → 38,6; ngoài phạm vi 85,7 → 57,1 (chỉ 7 mẫu, kém ở 2). Laptop 4-bit: trung bình 7,8 giây, p95 14,1, chậm nhất 27,9; 1 mẫu quá 25 giây, mẫu đó vốn 0 điểm nên hạn 25 giây cũng không đổi điểm (JOURNAL entry 57).
- [x] **C7.** *(Chạy 03:30–10:13 ngày 02/11.)* Train 4B 4-bit trên fit_random (cùng công thức), chấm dev_random bằng chữ ASR fine-tune rồi chữ chuẩn, rồi tính điểm gộp 495 dòng. **Luật đặt trước** (ghi trong `~/zac-c3/run_q4b_random.sh` trước khi chạy):
  - Số chính: điểm gộp 495 dòng trên chữ ASR fine-tune, 4B so với 1.7B (gộp 33,07).
  - Hơn ít nhất 1,0 điểm → 4B thành model agent. Việc tiếp: đo trên A30, kiểm nạp 4-bit hay bf16, rồi làm file nộp public.
  - Kém hơn mức đó → giữ 1.7B (nhỏ và nhanh hơn).
  - Riêng dev_random mà 4B kém 1.7B quá 1 điểm thì không tự chọn, báo đội quyết.
  - Báo thêm: chữ chuẩn trên dev_random (so với 53,92) và gộp, số giây mỗi mẫu, số mẫu quá 25 giây.
  - ***Xong 10:13 ngày 02/11:*** gộp 495 dòng chữ ASR fine-tune 33,07 → **46,17** (+13,11 [+8,94; +17,32]; tốt 127, kém 53). dev_random 42,64 → **54,01** (+11,37 [+5,35; +17,45]). Chữ chuẩn: dev_random 53,92 → **65,61** (+11,70), gộp 44,23 → **59,15** (+14,92). → **Chốt 4B làm model agent.** Laptop 4-bit: dev_random trung bình 9,0 giây, p95 17,4. 4 mẫu quá 25 giây, đều 0 điểm; mẫu đầu lượt chấm mất 110 giây vì model vừa nạp (cùng mẫu đó, lượt sau chỉ 13 giây) (JOURNAL entry 58).

### C. Mốc giờ (ước tính)

| Giờ | Việc |
|---|---|
| Ngay sau 16:12 | Anh bắt đầu Colab turbo (B2); leader bắt đầu Colab PhoWhisper (L3) |
| Trước 18:00 | Leader nộp public (L1) |
| ~~16:50~~ 17:00 | Laptop xong lượt (1); Claude đã báo (C1) |
| 18:00–18:30 | Colab turbo xong; PhoWhisper khoảng 18:30–19:00 |
| **18:00** | **Họp**: điểm public, lượt (1), WER của ASR fine-tune (nếu đã có), tình hình máy anh trai |
| ~~20:00~~ 20:19 | Laptop xong lượt (2); Claude đã báo (C2): không giữ B-up |
| 20:32–21:05 | Claude chạy 4 lượt kiểm C4 trên GPU laptop, rồi mở PR #9 (C4 xong) |
| Khi Colab gửi về | Claude chấm agent với transcript ASR mới (C3), khoảng 10 phút mỗi model trên mỗi tập dev |
| 00:02–00:53 ngày 01/11 | Claude chạy C3 trên GPU laptop (5 lượt): chọn Whisper-turbo fine-tune |
| 00:54–01:29 ngày 01/11 | Claude làm file nộp public mới (C5); Anh hoặc leader nộp (B8) |
| 08:11 ngày 01/11 | Anh báo điểm public lần 2: 35,24 (B8 xong) |
| 08:25 ngày 01/11 | Bắt đầu phần agent: đo lại chỗ mất điểm; chờ Anh quyết tải 4B (B9) |
| ~~09:27–khoảng 17:00~~ 09:27–10:13 ngày 01/11 | Laptop train 4B 4-bit (C6): dừng vì máy mang đi học; chạy lại khi Anh về (B10) |
| 20:47 ngày 01/11 – 03:28 ngày 02/11 | Laptop train và chấm 4B 4-bit (C6): 4B thắng rõ trên dev_lao |
| 03:30–10:13 ngày 02/11 | Laptop train và chấm 4B trên fit_random / dev_random (C7): chốt 4B |
| 13:10–14:51 ngày 02/11 | Laptop làm file nộp public bằng 4B (B11); Anh hoặc leader nộp |
| 15:47 ngày 02/11 | Anh báo điểm public lần 3: 45,39 (B11 xong) |
| 13:38–14:45 ngày 02/11 | Pilot sinh 280 mẫu đạt bằng API Meta (11,55 USD) |
| 14:52 – khoảng 23:00 ngày 02/11 | Laptop train 4B pilot trên fit_lao + mẫu sinh, rồi chấm dev_lao |
| 00:19–07:30 ngày 03/11 | Laptop train 4B học chữ trộn trên fit_random, rồi chấm dev_random (B15); dừng 00:37–00:53 vì máy khởi động lại; qua cửa 1 |
| 08:54–15:27 ngày 03/11 | Laptop train cùng cách trộn trên fit_lao, rồi chấm dev_lao; không qua luật gộp (chữ ASR −0,69) |
| 00:13 – 07:34 ngày 04/11 | Laptop train lại 4B trên đủ 1.545 mẫu (xong 06:03), rồi làm file nộp public (xong 07:34); Anh bảo chạy ngay thay cho hẹn giờ 00:30 (B17). Nộp: B19 |
| 14:44–16:06 ngày 04/11 | Laptop chấm 4B với chữ PhoWhisper fine-tune trên dev_random và dev_lao (B23): qua luật, gộp 46,17 → 47,88 |
| 16:45–18:40 ngày 04/11 | Laptop ghép PhoWhisper-ft, kiểm chữ dev (779/784 câu giống Colab), làm file nộp public bằng PhoWhisper-ft (B24). Anh hoặc leader nộp (B25) |
| 23:30 ngày 04/11 – 06:38 ngày 05/11 | Laptop tự train lượt prompt `xref` trên fit_lao rồi chấm dev_lao ([PR #14](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/14), B23): không qua cửa 1 |
| 09:18 – 18:14 ngày 05/11 | Laptop fine-tune lại PhoWhisper trên gần đủ train, kiểm WER trên 54 mẫu (qua), làm file public (B27; đóng băng 13:38–17:45 vì Anh cần dùng máy); `predict.sh` 3 mẫu đạt `"ok"`. Anh hoặc leader nộp (B29) |
| Trước 11:00 ngày 06/11 | Anh cài Docker và tải file image (B30); kịp thì Claude nạp image và chạy 3 mẫu |
| Tối 06/11, khi Anh mở lại máy (B31) | Laptop chạy thử image Docker (B28): 3 mẫu để có `"ok"`, rồi đủ 634 mẫu hai lần (khoảng 4 giờ) |
| Trước 11:59 ngày 16/11 | Gói nộp cuối theo giao diện BTC (L9) |
| **11:59 ngày 16/11 (giờ máy)** | **Hạn nộp Docker** (23:59 GMT+7) |
| Nếu Anh duyệt B12 | Claude viết bộ sinh dữ liệu (khoảng nửa ngày), sinh pilot qua Batch API, train 4B khoảng 6 giờ, chấm khoảng 1 giờ |
| ~~22:00–01:15~~ | Kaggle đã xong lúc 15:50 (không train) |

### D. Khi máy xong: gửi kết quả một lần

1. Trên laptop của Anh, tạo thư mục riêng cho từng nguồn, để các file cùng tên không đè lên nhau:
   ```bash
   mkdir -p ~/"Zalo AI Challenge"/cloud_results/{kaggle,colab_anh,colab_leader,anh_trai}
   ```
2. Đặt file vào đúng thư mục:

   | Nguồn | File | Thư mục |
   |---|---|---|
   | Colab của Anh | `asr_results_turbo.tar.gz` (trong `My Drive/zac_out`) | `cloud_results/colab_anh/`: **đã có** (01/11, 00:00) |
   | Colab của leader | `asr_results_pho.tar.gz` | `cloud_results/colab_leader/`: **đã có** (01/11, 00:00) |
   | Kaggle của leader | `cloud_results_*.tar.gz` (tab Output) | `cloud_results/kaggle/`: **đã có** (16:05) |
   | Máy anh trai | `zac_logs.tar.gz` và `cloud_results_*.tar.gz` (trong `~`) | `cloud_results/anh_trai/` |
   | Laptop của Anh | Không cần làm gì | |

3. Nhắn Claude **một lần**: "Kết quả đã về", kèm nguồn nào có. Có nguồn nào trước 18:00 thì gửi trước cũng được. Claude giải nén vào chỗ riêng, không đè lên kết quả cũ.
4. Sau khi gửi, xoá bản trên các máy ngoài, vì có dữ liệu thi:
   - Kaggle: dataset và notebook.
   - Drive: gói và thư mục `zac_out`.
   - Máy anh trai: `~/ZAIC_2026`, gói và các file kết quả.
5. Các file này không bao giờ lên git: `cloud_results/` và `*.tar.gz` đã nằm trong `.gitignore`. File `zac_logs.tar.gz` ở thư mục gốc repo là của lần chạy Kaggle bị lỗi lúc 14:05; xoá được.

### E. Quyết định và việc đã xong hôm nay

- [x] Bật lượt cloud theo khuyến nghị (Anh, 10:00). Gói v3 có sẵn các lượt đã bật; lượt 4B học trên chữ ASR chỉ chạy khi có từ 4 GPU.
- [x] Nhờ anh trai train trên máy Google; Anh báo đã được cho phép (10:29).
- [x] Chạy 2 lượt 1.7B dự phòng trên laptop (Anh, 13:46).
- [x] Kaggle chạy `ARMS="pho asr"` (Anh, 13:58). Lỗi lần đầu (14:05: Kaggle bỏ file rác khi giải nén) đã sửa trong ô lệnh.
- [x] Viết script fine-tune ASR (Anh, khoảng 14:40): [PR #7](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/7), hướng dẫn Colab, gói có audio.
- [x] PR #1 merge vào `main` (Anh, 14:47). PR #2 và #3 được merge vào nhánh nền (leader, 14:47–14:48), nên Claude mở [PR #8](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/8) để đưa chúng vào `main`.
- [x] Leader nộp public: **25,9300** (file `e2e_public_turbo.jsonl`).
- [x] Anh nộp public lần 2: **35,24** (file `e2e_public_turboft.jsonl`, ASR fine-tune; 08:11 ngày 01/11).
- [x] Anh nộp public lần 3: **45,39** (file `e2e_public_q4b.jsonl`, agent 4B 4-bit; 15:47 ngày 02/11).
- [x] Anh gửi gói v3 và lệnh có kiểm GPU cho anh trai (16:12). Fine-tune ASR vẫn chạy trên Colab, không gửi anh trai.
- [x] Dữ liệu: Anh đã hỏi BTC, được phép nhờ anh trai chạy. Không cần nhắc lại.
- [x] B-up trên fit_random: **không giữ**, theo luật đặt trước (Claude áp luật lúc 20:22; JOURNAL entry 49). Agent mặc định vẫn là SFT thường.
- [ ] **Còn mở:**
  - lượt agent học trên chữ PhoWhisper: Kaggle không kịp; laptop đã rảnh từ 20:19, chạy mất khoảng 3 giờ. **Claude khuyến nghị không chạy** (lượt cùng hướng vừa không đáng dùng, JOURNAL entry 48); Anh quyết.
  - ~~nộp public (L1)~~ xong: 25,93, rồi 35,24 với ASR fine-tune;
  - merge PR #8 (B6);
  - **sau ASR, bước lớn tiếp theo là agent** (JOURNAL entry 51): ASR hoàn hảo chỉ đưa điểm gộp lên khoảng 44, vì agent đọc chữ chuẩn vẫn mất khoảng 56 điểm. Claude đề xuất: kết quả 4B, rồi dữ liệu SFT nhiều vế và điều kiện. **Anh đồng ý (21:21).**
  - có thuê GPU từ 24 GB cho 2 lượt 4B không, nếu máy anh trai không train được (B4). Gói v3 và [`docs/CLOUD_TRAIN_2026-10-31.md`](docs/CLOUD_TRAIN_2026-10-31.md) đã sẵn.

### F. Nguyên tắc chọn mô hình (Anh nêu 31/10, sau điểm public 25,93)

Không đổi tổng quát hoá lấy điểm public. Cụ thể:
1. **Chọn trên dev, không trên public.** Model, công thức train và ASR được chọn bằng dev_random và dev_lao, so theo cặp có khoảng tin cậy 95%, với luật đặt trước khi chạy.
2. **Coi trọng dev_lao (app chưa thấy).** Tập private có thể có app mới. Thay đổi nào làm dev_lao giảm rõ thì không nhận, kể cả khi dev_random tăng.
3. **Public chỉ để kiểm,** không để chỉnh. Mỗi lần nộp phải là một mốc có lý do: bộ máy mới, ASR mới, model mới. Không thử nhiều biến thể để chọn bản có điểm public cao nhất.
4. **Không train trên public, không pseudo-label public hay private,** không nghe để gán nhãn.
5. **Mỗi lần nộp ghi lại:** file, model, ASR, điểm dev dự đoán, điểm public. Hôm nay: `e2e_public_turbo.jsonl`, dev dự đoán 17–32 (gộp 23,99), public 25,93.
   - 01/11: `e2e_public_turboft.jsonl` (Whisper-turbo fine-tune, agent `q17b_fit_random`), dev dự đoán 25–43 (gộp 33,07), public 35,24.
   - 02/11: `e2e_public_q4b.jsonl` (Whisper-turbo fine-tune, agent `q4b4_fit_random` nạp 4-bit), dev 39–54 (gộp 46,17), public 45,39.
   - 04/11: `e2e_public_q4b_all.jsonl` (Whisper-turbo fine-tune, agent `q4b4_all` học đủ 1.545 mẫu nên không có điểm dev riêng), public 46,29.
   - 05/11: `e2e_public_q4b_all_phoft.jsonl` (PhoWhisper-large fine-tune, agent `q4b4_all`), dev với adapter fit 41–55 (gộp 47,88), public 51,16.
   - 05/11: `e2e_public_q4b_all_phoftall_fix0497.jsonl` (PhoWhisper-large fine-tune học thêm 495 mẫu dev, agent `q4b4_all`; WER 54 mẫu kiểm 7,65 → 7,08), public 49,65: giữ bản 51,16.

## 0. Tối 30/10, trong lúc máy Anh chạy (tới khoảng 6 giờ sáng 31/10), làm trên máy leader

**Máy Anh:** chỉ đọc file. Không đổi nhánh, không commit trong thư mục repo, không mở ứng dụng nặng. Máy đang chạy giai đoạn 2 của D, rồi tới lượt đo đầu-cuối.

**Ghi kết quả ở đâu:**
- Câu trả lời và ghi chú: `HUMAN_TODO.md` trên `main`. Sửa trên GitHub web, hoặc trong clone của leader ở nhánh `main`.
- Góp ý code: comment trên [PR #4](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/4); Claude sửa.
- Không commit `data/`, `gen/`, `asr/`, `runs/`.

Các việc dưới đây xếp theo mức có ích cho các quyết định sáng 31/10.

- [ ] **[Leader] 0.1 Dựng môi trường** (khoảng 15 phút). Dùng nhánh `e2e-baseline`: có đủ code của PR #1–#4 và tài liệu mới nhất. Chạy được 2 bộ test trên máy thứ hai cũng là một lần tập dượt cho Docker.
  ```bash
  git clone https://github.com/Nguyen-Le-Tuan/ZAIC_2026.git && cd ZAIC_2026 && git checkout e2e-baseline
  mkdir -p data && unzip -q /đường/dẫn/tới/train+public_test.zip -x '__MACOSX/*' -d data   # phải ra data/train+public_test/
  cd lifemate && uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
  .venv/bin/python -m lifemate.tests.test_asr && .venv/bin/python -m lifemate.tests.test_scorer
  ```
- [ ] **[Cả hai] 0.2 Nghe audio train** (45–60 phút). Làm theo mục 3 (30 mẫu ngẫu nhiên), **cộng 3 câu Whisper-turbo nghe sai** trong lần thử: `train_0003`, `train_0019`, `train_0025`. Đó là 3 wav đầu của dev_random; nếu không có `aplay` thì mở bằng trình phát bất kỳ.
  - **Câu cần trả lời:** `audio_text` là kịch bản người nói đọc theo, hay transcript thật? Người nói có đọc lệch không? Ví dụ `train_0019`:
    - `audio_text`: "Chị ơi, giúp tôi đặt phòng khách sạn ở Đà Lạt với nhé"
    - ASR: "Giờ tôi cần đặt phòng các sản ở Đà Lạt nữa nha"

    Nếu người nói đọc lệch kịch bản, WER đo sáng mai sẽ phạt oan ASR, và nhãn để fine-tune ASR phải xử lý khác.
  - Ghi vào bảng ghi chú ở mục 3.
- [ ] **[Leader] 0.3 Danh sách "cụm từ nguy hiểm" cho ASR** (khoảng 20 phút; mục 3, Q9). Viết từ những gì vừa nghe.
  - Đối chiếu với danh sách từ phủ định mà `lifemate/scripts/asr_quality.py` đang đo: `NEG = ["đừng", "không", "chưa", "thôi", "khỏi", "hủy", "bỏ"]`.
  - Thiếu biến thể nào (ví dụ "hông", "hổng", "thôi khỏi", "khỏi cần", "à không" khi tự sửa) thì comment trên PR #4.
- [ ] **[Leader] 0.4 Rà model ASR và LLM mới** phát hành từ 06/2026 tới 25/10/2026 (khoảng 30 phút; mục 5).
  - Ghi tên, số tham số, licence, ngày phát hành, revision trên Hugging Face.
  - Nếu có ASR tiếng Việt tốt hơn PhoWhisper, Claude thêm nó vào danh sách `MODELS` của `lifemate/scripts/e2e_baseline.sh`. Lần chạy lại chỉ đo model mới; các bước đã xong được bỏ qua.
- [ ] **[Leader] 0.5 Forum và câu hỏi cho BTC** (khoảng 20 phút; mục 4).
  - Ưu tiên: hướng dẫn Docker; CUDA và driver của máy chấm; giới hạn dung lượng image.
  - 30 giây mỗi mẫu có tính thời gian nạp model không.
  - Chấm có phân biệt chữ hoa/thường không.

  Các câu trả lời này quyết định cách đóng Docker quanh `lifemate/scripts/predict.sh`.
- [ ] **[Leader] 0.6 Review PR #4** (khoảng 30 phút). Đây là phần của leader (ASR, Docker), nên cần đồng ý với 2 giao kèo trước khi đóng Docker:
  - Định dạng file ASR (`lifemate/lifemate/asr.py`).
  - Giao diện biến môi trường của `lifemate/scripts/predict.sh` (`SPLIT`, `DATA`, `ASR_MODEL`, `LLM`, `ADAPTER`, `OUT`).

  Đọc thêm `lifemate/scripts/asr_quality.py` và `lifemate/scripts/check_submission.py`.
- [ ] **[Cả hai] 0.7 Chuẩn bị quyết định nộp public sáng mai** (khoảng 15 phút).
  - Chốt quy tắc dùng 5 lượt nộp mỗi ngày (Q7, mục 8).
  - Ghi trước con số nào sẽ coi là "khớp" với dev nội bộ. Lần nộp đầu dùng để lấy mốc điểm và kiểm các giả định của bộ chấm (Q1, Q8), không phải để leo bảng.
- [x] **[Anh] 0.9 Deep research bằng Codex.** Mở Codex trong thư mục repo trên máy Anh, gõ: *"Đọc và làm đúng theo `docs/CODEX_RESEARCH_PROMPT_2026-10-30.md`."*
  - Prompt cấm Codex đụng git, GPU và job đang chạy.
  - Codex sẽ ghi kết quả vào `docs/research/`. Sáng mai cả đội và Claude đọc, đối chiếu, rồi mới đưa lên `main`.
  - *Xong 30/10, 21:23.* Claude đã kiểm nguồn và kiểm không có dữ liệu thi; Anh đồng ý đưa lên `main` (JOURNAL entry 24). **[Leader]** đọc mục 0, 4 (P0-4, P0-5, P0-7) và 6 của báo cáo.
- [ ] **[Leader] 0.8 (tuỳ chọn, cần GPU)** Chạy Whisper-turbo trên chính các câu vừa nghe, để so bằng tai.
  - RTX 3050 4GB đủ cho turbo fp16 (1,6GB). PhoWhisper-large (3,1GB fp16) có thể không vừa.
  - Lệnh mẫu, với `ids_listen.txt` là danh sách id đã nghe:
    ```bash
    .venv/bin/python -m lifemate.asr --split train --ids ids_listen.txt --batch-size 1 --out asr/train_listen_turbo.jsonl
    ```
  - Lần đầu sẽ tải model 1,6GB.
  - **Chỉ chạy trên train.** Transcript của public_test chỉ được tạo bên trong `predict.sh` để nộp bài, không đem ra nghe, sửa hay dùng làm nhãn.

## 1. Ngay bây giờ (15 phút đầu)

- [x] **[Anh]** Mở terminal, paste lệnh train (lấy ở `JOURNAL.md`, mục "Lệnh chạy train qua đêm"). *Đã chạy 28/10 23:52 → 29/10 02:40, không lỗi (theo log). Không chạy lại.*
  ```bash
  cd ~/"Zalo AI Challenge/lifemate" && mkdir -p runs && { nohup systemd-inhibit --what=sleep:idle:handle-lid-switch --why="LifeMate training" bash scripts/train_local.sh > runs/overnight.log 2>&1 & } && sleep 5 && tail -f runs/overnight.log
  ```
- [ ] **[Anh]** Khoảng 10–15 phút sau, kiểm tra log:
  - Dòng `{"n": 233, ...}` của baseline zero-shot đã xuất hiện.
  - Khi bắt đầu train: `peak_gb` dưới khoảng 6,3 và `tok_s` khoảng 1.400.
  - Ghi `eta_min` (số phút còn lại) vào đây: …
- [ ] **[Anh]** Cắm sạc. Không mở game, video hay ứng dụng nặng GPU, vì VRAM chỉ còn dư khoảng 0,9GB.
- [ ] **[Leader]** Chuẩn bị máy của mình để chạy được code:
  ```bash
  git clone https://github.com/Nguyen-Le-Tuan/ZAIC_2026.git && cd ZAIC_2026 && git checkout agent-pipeline
  mkdir -p data && unzip -q /đường/dẫn/tới/train+public_test.zip -x '__MACOSX/*' -d data   # phải ra data/train+public_test/
  command -v uv || curl -LsSf https://astral.sh/uv/install.sh | sh
  cd lifemate && uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
  ```

## 2. Hiểu bài và hiểu code (khoảng 1 giờ)

- [ ] **[Cả hai]** Đọc `JOURNAL.md` (mục 0–4) và `docs/PIPELINE.md` (mục 1–4).
- [ ] **[Cả hai]** Đọc README gốc của BTC: `data/train+public_test/README.md` và `data/train+public_test/train/zaic_tools/README.md`. **Ghi lại mọi chỗ khác với `JOURNAL.md`**, vì Claude có thể đã hiểu sai.
- [ ] **[Cả hai]** Xem tận mắt prompt mà model nhìn thấy cho mẫu `train_0001`, rồi đối chiếu với lời giải ở `docs/PIPELINE.md` mục 2.4:
  ```bash
  cd lifemate && .venv/bin/python -c "
  from lifemate.data import *; from lifemate.prompt import *
  cat=load_catalog('train'); s=[x for x in load_split('train') if x['id']=='train_0001'][0]
  h=[t['audio_text'] for t in s['history'] if t['role']=='user']
  print(to_chatml(build_messages(s,s['audio_text'],h,catalog_tools(cat),{a['id']:a for a in cat['apps']})))" | less
  ```
- [ ] **[Cả hai]** Tự chạy lại kiểm chứng "phát lại đáp án phải ra 100" (chỉ dùng CPU, khoảng 1 phút):
  ```bash
  cd lifemate && .venv/bin/python -m lifemate.infer --split train --text oracle --backend oracle --out runs/oracle_train.jsonl \
    && .venv/bin/python -m lifemate.scorer runs/oracle_train.jsonl --split train
  ```
- [ ] **[Cả hai]** Review [PR #1](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/1) theo thứ tự `prompt.py` → `agent.py` → `scorer.py` → `sft.py` → `train.py`.
  - Comment trên GitHub mọi chỗ chưa hiểu hoặc nghi là sai.
  - **Mục tiêu:** mỗi người tự giải thích lại được vòng lặp agent bằng lời của mình.
- [ ] **[Cả hai]** Tự kiểm tra lại bằng tay một phát hiện của Claude. Ví dụ đọc 10 mẫu có `contacts.search` để xác nhận "query là tên lưu trong danh bạ, không phải lời người nói" (`JOURNAL.md`, phát hiện 13). Kết luận: đúng / sai / có ngoại lệ: …

## 3. Nghe audio: việc chỉ người làm được (khoảng 1 giờ)

- [ ] **[Cả hai]** Nghe 30 mẫu train ngẫu nhiên và so với `audio_text`.
  - Bước 1, tạo danh sách:
    ```bash
    cd lifemate && .venv/bin/python -c "
    import random; from lifemate.data import *
    random.seed(1); S=load_split('train')
    for s in random.sample(S,30): print(DEFAULT_ROOT/'train'/s['audio'], '|', s['context']['user_profile'].get('city'), '|', s['audio_text'])" > runs/listen_train.txt
    ```
  - Bước 2, nghe lần lượt (bấm Enter để sang mẫu sau):
    ```bash
    cd lifemate && while IFS='|' read -r f city text; do echo "== [$city]$text"; aplay -q "${f% }"; read -rp "   Enter để nghe tiếp " _ </dev/tty; done < runs/listen_train.txt
    ```
  - Ghi vào bảng ghi chú bên dưới. Câu cần trả lời: **`audio_text` là kịch bản người nói đọc theo, hay transcript thật của audio? Người nói có đọc lệch kịch bản không?** Câu trả lời quyết định nhãn dùng để train ASR.
- [ ] **[Cả hai]** Nghe 20 mẫu public để hiểu phân bố. **Chỉ nghe, không ghi transcript, không dùng để train**, vì thể lệ cấm gán nhãn tập test. Ghi lại khác biệt so với train.
  ```bash
  cd lifemate && .venv/bin/python -c "
  import random; from lifemate.data import *
  random.seed(2); S=load_split('public_test')
  for s in random.sample(S,20): print(DEFAULT_ROOT/'public_test'/s['audio'], '|', s['context']['user_profile'].get('city'), '|', ', '.join(s['context']['installed_apps']))" > runs/listen_public.txt
  while IFS='|' read -r f city apps; do echo "== [$city] app:$apps"; aplay -q "${f% }"; read -rp "   Enter để nghe tiếp " _ </dev/tty; done < runs/listen_public.txt
  ```
- [ ] **[Leader]** Từ những gì đã nghe, lập danh sách **"cụm từ nguy hiểm" cho ASR**: số tiền, giờ, ngày, tên người, từ phủ định ("đừng", "thôi khỏi"), tự sửa giữa câu. Đây là đầu vào cho Q9.

**Bảng ghi chú khi nghe** (mỗi mẫu một dòng):

| id | Giọng (Bắc/Trung/Nam) | Giọng nam/nữ, tuổi ước lượng | Nhiễu nền | Cách đọc số, giờ | Từ tiếng Anh | Audio lệch transcript? | Ghi chú |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## 4. Làm việc với BTC và cộng đồng

- [ ] **[Leader]** Đọc forum và kênh hỏi đáp của cuộc thi. Tìm hướng dẫn đóng gói Docker (BTC nói sẽ có tài liệu riêng) và các thông báo thay đổi dữ liệu.
- [ ] **[Leader]** Hỏi BTC những chỗ luật chưa rõ:
  1. Tham số không fuzzy được so khớp có phân biệt chữ hoa/thường và khoảng trắng không? List (ví dụ `params` của `sys.ask_missing_info`) có xét thứ tự không?
  2. "Token" trong token-F1 được tách theo khoảng trắng, hay có bỏ dấu câu trước?
  3. Giới hạn 30 giây mỗi mẫu có tính cả thời gian nạp model lúc khởi động không?
  4. Khi nào có hướng dẫn Docker? Máy chấm dùng phiên bản CUDA và driver nào? Image có giới hạn dung lượng không?
  5. Private test có dùng bản `zaic_tools` và catalog mới, tức là có app mới không?
  6. Mốc "phát hành trước 26/10/2026" tính theo ngày công bố trọng số model hay ngày công bố paper?
- [ ] **[Leader]** Xem bảng xếp hạng public: điểm cao nhất hiện tại, số đội tham gia. Ghi vào đây: …
- [ ] **[Leader]** *Quyết định:* có dùng 1 lượt nộp public hôm nay cho **bài nộp rỗng** không?
  - Mục đích: đo tỉ lệ mẫu ngoài phạm vi của public. Điểm nhận được = 100 × tỉ lệ đó; train là 7,18.
  - Đây là một lần dò để hiểu dữ liệu, không phải để leo bảng xếp hạng.
  - File nộp: `lifemate/runs/public_empty.jsonl` (đã có sẵn trên máy của Anh), hoặc tạo lại bằng:
    ```bash
    cd data/train+public_test && python3 -c "
    import json,sys; sys.path.insert(0,'public_test'); from zaic_tools import ToolEnv
    with open('public_test/public_test.jsonl',encoding='utf-8') as f, open('../../lifemate/runs/public_empty.jsonl','w',encoding='utf-8') as o:
        for l in f:
            i=json.loads(l)['id']; e=ToolEnv('public_test',i,root='.')
            o.write(json.dumps({'id':i,'tool_calls':[],'state_hash':e.get_state_hash()})+'\n')"
    PYTHONPATH=public_test python3 -m zaic_tools --split public_test --root . --validate ../../lifemate/runs/public_empty.jsonl
    ```
  - Kết quả (ghi thêm vào Q6): …
  - *29/10:* handoff của Anh đề xuất **không ưu tiên** nộp bài rỗng trong giai đoạn này (xem Q7). Leader chưa quyết; chưa nộp.

## 5. Chuẩn bị tài nguyên

- [ ] **[Anh hoặc Leader]** Chọn nhà cung cấp GPU cloud, tạo tài khoản và nạp tiền. Claude không làm các việc thanh toán. Cần 2 loại máy:
  - 1 máy A100 hoặc H100 80GB để train.
  - 1 máy 24GB (A30 nếu thuê được, không thì L4 hoặc A10) để đo thời gian giống máy chấm.
- [ ] **[Anh]** Tạo Hugging Face token (quyền read) để tải model nhanh hơn, không bị giới hạn lượt tải.
- [ ] **[Leader]** Rà Hugging Face tìm LLM dưới 5B và ASR tiếng Việt phát hành từ 06/2026 tới 25/10/2026. Kiến thức của Claude dừng ở giữa năm 2026 nên không biết các model này. Ghi tên, số tham số, licence, ngày phát hành.
- [ ] **[Leader]** Lập bảng licence các model ứng viên: Qwen3 (Apache-2.0), Whisper (MIT), PhoWhisper (BSD-3) và các model khác. Đánh dấu model nào dùng licence không thương mại (CC-BY-NC).

## 6. Tổ chức đội

- [ ] **[Cả hai]** Thống nhất quy trình review PR: ai review, trong bao lâu, tiêu chí để merge (ví dụ: kiểm chứng phát lại đáp án vẫn ra 100, điểm dev không giảm).
- [ ] **[Cả hai]** Đặt lịch họp ngắn hằng ngày và chốt mốc đóng băng tính năng (xem Q20).

## 7. Sáng mai, khi train xong

- [x] **[Anh]** Xem 2 file điểm: `lifemate/runs/zs_q17b_fit_random_score.json` (trước khi train) và `lifemate/runs/sft_q17b_fit_random_score.json` (sau khi train). *29/10: Anh đã đọc và dán kết quả vào chat (9,9 → 53,9).*
- [ ] **[Cả hai]** **Tự phân tích lỗi trước khi hỏi Claude.** In 15 mẫu sai, rồi tự phân nhóm nguyên nhân bằng mắt (sai ID, sai giờ, thiếu bước đọc, gọi thừa, hỏi lại sai lúc, gọi tool ở mẫu ngoài phạm vi…). Sau đó mới so với phân tích của Claude.
  ```bash
  cd lifemate && TAG=q17b_fit_random && .venv/bin/python -c "
  import json; from lifemate.data import *
  tag='$TAG'; rows=load_jsonl(f'runs/sft_{tag}_rows.jsonl'); pred={r['id']:r for r in load_jsonl(f'runs/sft_{tag}.jsonl')}
  S={s['id']:s for s in load_split('train')}
  for r in [r for r in rows if r['score']<1][:15]:
      s=S[r['id']]; print('=====',r['id'],r['category'],'| điểm',round(r['score'],2),'| hash đúng' if r['hash_ok'] else '| HASH SAI'); print('  NÓI   :',s['audio_text'])
      for c in s['label']['tool_calls']: print('  ĐÁP ÁN:',json.dumps(c,ensure_ascii=False))
      for c in pred[r['id']]['tool_calls']: print('  MODEL :',json.dumps(c,ensure_ascii=False))
  " | less
  ```
  - *29/10:* Anh đã audit lỗi với Codex hỗ trợ ([`docs/TRAIN_REVIEW_2026-10-29.md`](docs/TRAIN_REVIEW_2026-10-29.md)), Claude đã đối chiếu ([`docs/EVAL_2026-10-29.md`](docs/EVAL_2026-10-29.md)). Chưa ghi nhận việc hai người tự phân loại toàn bộ bằng mắt, nên việc này vẫn để mở.
- [ ] **[Anh]** *(30/10)* Đọc tay 23 mẫu thí nghiệm D trong `lifemate/gen/review_fit_lao.md` (chỉ có trên máy Anh). Đánh dấu `[x]` mẫu hợp lý, ghi lý do mẫu sai. Xem [`docs/EXPERIMENT_D.md`](docs/EXPERIMENT_D.md) mục 6.
  - *31/10: không còn cần.* D bị loại ở giai đoạn 2 ([`docs/D_PHASE2_2026-10-31.md`](docs/D_PHASE2_2026-10-31.md)). Anh quyết bỏ việc này hay vẫn đọc để lưu.
- [ ] **[Anh]** *(30/10)* Quyết có sinh đủ khoảng 230 mẫu D và chạy hai lượt D-lao, D-random hay không (EXPERIMENT_D mục 8).
  - *Cập nhật sau review 30/10:* kế hoạch đã đổi thành 4 giai đoạn có cổng chặn và có đối chứng "nhân bản mẫu hỏi lại thật" ([`docs/REVIEW_D_2026-10-30.md`](docs/REVIEW_D_2026-10-30.md) mục 5). Việc cần quyết bây giờ là **duyệt giai đoạn 1**.
- [ ] **[Anh hoặc Leader]** *(30/10)* Đọc tay 30 nhãn D của giai đoạn 1 (R8 trong review): nhãn có đúng cách BTC sẽ gán không, nhất là các nhãn không có tiền lệ.
  - *Đã sẵn sàng:* `lifemate/gen/review_v1_30.md`, gồm 30 mẫu ngẫu nhiên của D v1 (14 C, 16 B-vague). Đây là cổng còn mở của giai đoạn 1; cần ≥ 27/30 mẫu hợp lý.
- [x] **[Anh]** *(30/10)* Chọn bước tiếp theo của D: giai đoạn 1b rồi giai đoạn 2 có nhánh liều lượng (khuyến nghị), hay giai đoạn 2 ngay ([`docs/D_PHASE1_2026-10-30.md`](docs/D_PHASE1_2026-10-30.md) mục 5).
  - *Anh đã chọn trong chat (30/10):* "Làm giai đoạn 1b". Kết quả ở [`docs/D_PHASE1B_2026-10-30.md`](docs/D_PHASE1B_2026-10-30.md): D-train 77 mẫu; tỉ lệ người viết phải bỏ 27% (C 0%, B-vague 53%), cổng ≤ 15% vẫn không đạt.
- [x] **[Anh]** *(30/10)* Chọn bước tiếp theo sau giai đoạn 1b: giai đoạn 2 ngay với D-train 77 mẫu (khuyến nghị), hay giai đoạn 3 (nới luật để có thêm tool) trước ([`docs/D_PHASE1B_2026-10-30.md`](docs/D_PHASE1B_2026-10-30.md) mục 6). Giai đoạn 2 tốn khoảng 3 × 3,3 giờ GPU trên máy Anh.
  - *Anh đã chọn trong chat (30/10):* "Train giai đoạn 2". Đang chạy từ 18:17 trong unit `lifemate-phase2-d`, dự kiến khoảng 9 giờ.
- [ ] **[Anh]** *(30/10)* Trong khoảng 9 giờ train giai đoạn 2, cộng khoảng 2–2,5 giờ đo đầu-cuối ngay sau đó (tới khoảng 6 giờ sáng 31/10):
  - Giữ máy cắm điện; không gập nắp, vì unit chỉ chặn idle-sleep.
  - Hạn chế mở ứng dụng nặng (ngày 29/10 systemd-oomd đã từng kill app vì thiếu RAM).
  - **Không đổi nhánh git trong thư mục repo, và không commit từ thư mục đó.** Ngày 30/10 lúc 20:03, việc đổi sang `main` rồi đổi lại đã xoá `lifemate/gen/` trên máy. Claude đã khôi phục (JOURNAL entry 21). Muốn sửa tài liệu trên `main` thì dùng một git worktree riêng.
- [x] **[Anh]** *(30/10)* Chọn ưu tiên sau D. *Anh đã chọn trong chat:* "Ưu tiên đầu-cuối", và "Claude làm ASR baseline với 2 model" (Whisper-large-v3-turbo, PhoWhisper-large, không fine-tune). Code ở [PR #4](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/4); lượt đo chạy sau giai đoạn 2 (JOURNAL entry 21).
- [x] **[Anh]** *(30/10)* **Repo đang public.**
  - Commit `1bbd05a` đã đưa `lifemate/gen/` lên `main`. Thư mục này chứa lời nói, nhãn và kết quả tool chép từ train, trong khi README dữ liệu cấm phát tán.
  - Claude đã gỡ khỏi `main` (`4e908be`, Anh chọn "Gỡ khỏi main"), nhưng **bản cũ vẫn xem được trong lịch sử git**.
  - Quyết: chuyển repo sang private (GitHub → Settings → General → Danger Zone → Change visibility), hoặc viết lại lịch sử. Viết lại lịch sử thì leader phải đồng bộ lại.
  - Muốn chia sẻ file `gen/` cho leader thì gửi riêng, không qua repo.
  - *Anh đã chọn trong chat (30/10):* **giữ public**, không viết lại lịch sử.
- [ ] **[Anh]** *(sáng 31/10)* Khi có `docs/E2E_BASELINE_2026-10-31.md`, quyết có nộp `lifemate/runs/e2e_public_<asr>.jsonl` lên public không. File đã qua `check_submission.py`. Anh tự nộp trên trang thi; Claude không nộp. Mục đích: lấy mốc điểm public đầu tiên và kiểm các giả định của bộ chấm local (Q1, Q7, Q8).
- [ ] **[Leader]** *(30/10)* Claude đã dựng bước ASR baseline (`lifemate/asr.py`, PR #4) với 2 model chưa fine-tune.
  - Xem số liệu sáng 31/10: WER; số, tiền, giờ còn giữ được; từ phủ định; query tìm kiếm. Dùng chúng để quyết hướng fine-tune ASR và chuẩn hoá số (Q9, Q12).
  - Thử nhanh 3 câu trên CPU: Whisper-turbo nghe kém ("huỷ lịch" → "bị dịch").
  - `audio_text` viết số bằng chữ nhiều hơn chữ số (1.371 so với 481 câu).
- [ ] **[Leader]** Khi BTC có hướng dẫn Docker: đóng image quanh `lifemate/scripts/predict.sh` (một lệnh offline từ thư mục dữ liệu ra `submission.jsonl` đã kiểm).
- [ ] **[Anh hoặc Leader]** *(30/10)* Đọc tay 24 mẫu mới của giai đoạn 1b trong `lifemate/gen/review_1b.md` (chỉ có trên máy Anh). Chú ý: 7/8 câu B-vague được viết bằng cách bỏ hẳn người nhận, và 3 mẫu `banking.transfer.amount` không có tiền lệ hỏi thật.
  - *31/10: không còn cần.* D bị loại ở giai đoạn 2 ([`docs/D_PHASE2_2026-10-31.md`](docs/D_PHASE2_2026-10-31.md)). Anh quyết bỏ việc này hay vẫn đọc để lưu.
- [ ] **[Anh]** *(30/10)* Giữ nguyên các file `lifemate/gen/*_fit_lao.jsonl`, `lifemate/gen/*_v1*` và `lifemate/gen/*_1b*` (mốc so sánh, hash ghi trong `docs/baselines/`). Không xoá, không train trên nguồn của CS-pilot-23 hay D-eval-24.
  - *Ghi chú 30/10:* D-eval-24 có 1 mẫu rò rỉ nhãn (`train_1140#d1`). Tập vẫn giữ nguyên để so được với mốc; báo cáo kèm kết quả trên D-eval-23 (bỏ mẫu này).
- [x] **[Anh]** Mở chat với Claude: *29/10, kèm [`docs/CLAUDE_HANDOFF_2026-10-29.md`](docs/CLAUDE_HANDOFF_2026-10-29.md).* *"Đọc `JOURNAL.md`, `docs/PIPELINE.md` và `HUMAN_TODO.md`. Đây là kết quả train và câu trả lời của đội…"*

---

## 8. Hai mươi câu hỏi nghiên cứu

Chép từ [`docs/PIPELINE.md`](docs/PIPELINE.md) mục 5. **Ghi câu trả lời ở đây**, không ghi bên `PIPELINE.md`, để chỉ có một nơi lưu câu trả lời. Người phụ trách chỉ là gợi ý; ai có ý tưởng thì cứ viết thêm.

Ngày 29/10 đã điền câu trả lời làm việc, lấy từ handoff của Anh (soạn với Codex hỗ trợ). Mỗi câu ghi một trong bốn trạng thái: **đã xác minh**, **giả thuyết**, **chưa đo**, **chờ BTC**. Chưa câu nào được đánh dấu xong, vì có câu trả lời làm việc không có nghĩa là câu hỏi nghiên cứu đã giải quyết.

### A. Hiểu thước đo và chính sách sinh nhãn

- [ ] **[Leader]** **Q1. Server so khớp tham số không fuzzy thế nào: có phân biệt chữ hoa không, có gộp khoảng trắng không, list có xét thứ tự không?**
  - *Vì sao:* quyết định có cần viết hoa query, sắp xếp list `params` của `ask_missing` hay không.
  - *Gợi ý:* thiết kế 1–2 lần nộp public **dùng để dò thước đo**, không phải để tối ưu. Ví dụ nộp cùng một bài nhưng viết thường toàn bộ query của call đọc, rồi so điểm.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chờ BTC.**
    - Theo thể lệ: tham số non-fuzzy phải giống hệt; fuzzy được hạ chữ thường và chuẩn hoá NFC rồi so token-F1 > 0,6. Mặc định giữ so khớp chính xác, không tự hạ chữ thường hay gộp khoảng trắng.
    - Chưa rõ: cách tách token và xử lý dấu câu của fuzzy; tham số tuỳ chọn để trống so với ghi rõ giá trị mặc định (ví dụ `train_1474` thêm `days: "daily"` nên bộ chấm local cho 0 điểm dù hash đúng); thứ tự phần tử trong list.
    - Ưu tiên hỏi BTC; không coi điểm public là xác nhận.
- [ ] **[Cả hai]** **Q2. BTC sinh đáp án như thế nào: bằng template, bằng LLM, hay bằng một simulator chạy chính sách cố định? Tìm thêm dấu vết** (ngoài chuyện query dùng tên trong danh bạ).
  - *Vì sao:* biết cách nhãn được sinh thì tái tạo được chính sách cho app mới.
  - *Gợi ý:* so sánh nhiều mẫu cùng kiểu yêu cầu; xem tham số fuzzy được viết theo văn phong nào; xem thứ tự các call.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết.**
    - Nhãn có nhiều quy luật, nhưng chưa biết sinh bằng template, LLM hay pipeline kết hợp.
    - **Đã xác minh (Claude đo 29/10):** id của train đi theo từng lô có đặc điểm khác nhau. Lô id 1501+ có trung bình 7,0 lượt user trong history (96% mẫu có history). Lô id 1–300 có 12,2 app cài và 3,1 call đáp án mỗi mẫu. Các lô khác khoảng 8–9 app và khoảng 2 call.
    - Hướng làm: phân tích quy ước theo lô và nhóm trên fit; không ép một luật cho mọi lô.
- [ ] **[Cả hai]** **Q3. Viết thành luật: khi nào đáp án gọi call đọc trước lệnh ghi, khi nào đọc kèm bộ lọc, khi nào bỏ qua bước đọc?**
  - *Vì sao:* call đọc chiếm phần lớn F1, và luật tổng quát dùng được cho app mới.
  - *Gợi ý:* thống kê theo từng cặp (call đọc, lệnh ghi); đã biết 113/126 lần bật đèn có `get_status` trước, và 11 lần còn lại đều do đã có trong history.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết.**
    - Nguyên tắc làm việc: đọc khi thiếu đối tượng, thuộc tính hoặc điều kiện; dùng lại thông tin trong history nếu còn hiệu lực; theo dõi thay đổi sau mỗi lệnh ghi.
    - Tách hai mục tiêu: đủ thông tin để thực thi đúng, và khớp quy ước call của đáp án.
    - Cần thống kê các ngoại lệ (đọc có bộ lọc so với đọc `{}`) trên fit.
- [ ] **[Cả hai]** **Q4. Ranh giới giữa hỏi lại, tự quyết và bỏ qua: các "tín hiệu" nào dẫn tới `ask_missing_info`?**
  - *Vì sao:* 14% mẫu là hỏi lại, và danh sách `params` phải khớp chính xác.
  - *Gợi ý:* đọc 217 mẫu hỏi lại, phân nhóm: trùng tên, thiếu giờ, thiếu số tiền, yêu cầu mơ hồ ("hạ xuống chút")… Rút ra danh sách kiểm tra.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết (nguyên tắc); đã xác minh (quy mô lỗi trên dev_random).**
    - Nguyên tắc: chỉ hỏi khi thông tin bắt buộc không tra được hoặc đối tượng còn mơ hồ. Với x-one-of, có số điện thoại thì không cần `contact_id`. Tôn trọng lời tự sửa cuối cùng của người dùng.
    - **Claude đo (29/10):** 14 mẫu execute bị hỏi thừa và 16 mẫu cần hỏi lại không hỏi, tổng 30 mẫu, mất 12,7 điểm. Đây là nhóm hành vi mất điểm lớn nhất; 22/30 mẫu nằm ngoài nhóm 51.
    - Hướng làm: cặp mẫu gần giống nhau (đủ/thiếu slot, một/nhiều đối tượng) sinh từ fit. Đo riêng hỏi thừa, bỏ hỏi và sai `params`.
    - **Thêm 30/10 (đã xác minh, [EXPERIMENT_D](docs/EXPERIMENT_D.md) mục 2–3):**
      - Nhãn hỏi lại có 3 kiểu: A trùng tên khi tra cứu, B chọn mơ hồ ID, C thiếu slot.
      - Model đã làm tốt kiểu A; bỏ hỏi chủ yếu ở B và C, nhất là với tool mới.
- [ ] **[Cả hai]** **Q5. Phân loại 111 mẫu ngoài phạm vi theo nguyên nhân. Có mẫu "làm được một phần" không, và đáp án xử lý ra sao?**
  - *Vì sao:* gọi dù chỉ một call ở mẫu ngoài phạm vi là mất trắng; còn yêu cầu nhiều ý mà chỉ một ý làm được thì cách xử lý chưa rõ.
  - *Gợi ý:* lọc các mẫu có nhiều ý định mà thiếu một app; xem đáp án làm phần còn lại hay trả `[]`.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chưa đo.**
    - Đã biết 111 mẫu gồm thiếu app, huỷ hoặc phủ định, trò chuyện, và thông tin đã có sẵn.
    - Chưa phân loại đủ 111 mẫu, chưa rõ chính sách khi yêu cầu chỉ làm được một phần.
    - Không suy luật từ từ khoá (ví dụ có chữ "thôi" thì trả rỗng).

### B. Tổng quát hoá và tín hiệu đánh giá

- [ ] **[Cả hai]** **Q6. Private test có thể khác public ở những điểm nào** (app mới, phân bố loại mẫu, giọng nói, độ dài history)? **Bộ dev nào mô phỏng private tốt nhất?** Leave-apps-out đã đủ chưa, hay cần leave-groups-out?
  - *Gợi ý:* so phân bố của public với train (app đã cài, độ dài history, thành phố); đặt giả định "xấu nhất hợp lý".
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết.**
    - Rủi ro chính: app/schema mới, history dài, giọng nói, thứ tự entity, tổ hợp tác vụ.
    - Tập đo: dev_random đo tiến bộ trong cùng miền; fit_lao → dev_lao đo app chưa thấy (chưa chạy).
    - **Claude đo (29/10):** điểm giảm theo lô id (68 → 35) và theo history (59,8 khi không có history → 33,1 khi từ 6 lượt). Từ nay báo điểm kèm lát cắt.
    - Vì dev_random đã bị phân tích kỹ, nên giữ riêng một tập kiểm tra kín (lockbox). Xem [docs/EVAL_2026-10-29.md](docs/EVAL_2026-10-29.md).
    - **Thí nghiệm B (chiều 29/10):**
      - fit_lao → dev_lao đạt 35,53 điểm (zero-shot 10,88).
      - Trong cùng các mẫu, lời gọi thực hiện vào app mới không kém app đã thấy, nhưng hỏi lại về tool mới được 0/23.
      - Lockbox chỉ dùng được cho model train lại từ model gốc, theo review của Codex.
      - Chi tiết ở EVAL mục 7.
- [ ] **[Leader]** **Q7. Dùng 5 lần nộp public mỗi ngày vào việc gì để không overfit?** Đặt quy tắc cho đội, ví dụ "chỉ nộp khi dev nội bộ tăng ít nhất X điểm" hoặc "dành một lần nộp mỗi ngày để dò thước đo hoặc đo ASR".
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết (đề xuất của Anh; leader chưa chốt).**
    - Coi public là kiểm tra tích hợp. Chỉ nộp khi có candidate rõ checkpoint, config và mục đích đo; ghi lịch sử nộp.
    - Không dùng bài nộp rỗng để dò phân bố trong giai đoạn này; hỏi BTC về metric.
- [ ] **[Cả hai]** **Q8. Nếu điểm dev nội bộ và điểm public lệch nhau, những nguyên nhân nào có thể giải thích, và kiểm tra từng nguyên nhân thế nào?** Ví dụ: ASR thật so với text chuẩn, app mới, khác biệt của bộ chấm, phiên bản `zaic_tools`.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chưa đo.**
    - Nguồn có thể gây lệch: ASR, schema mới, tỉ lệ loại tác vụ, history, bộ chấm, runtime, phiên bản `zaic_tools`.
    - Cách đo trên phần train giữ riêng: so oracle với ASR trên cùng agent; seen với unseen app theo đúng protocol; timeout và lỗi parse.

### C. ASR

- [ ] **[Leader]** **Q9. Lỗi ASR nào thực sự làm mất điểm? Định nghĩa "tỉ lệ lỗi slot" thay cho WER thế nào?**
  - *Gợi ý:* từ bảng ở mục 3.2, lấy các tham số của lệnh ghi có nguồn là ngày giờ hoặc số, tìm cụm từ tương ứng trong `audio_text` (ví dụ "muộn 1 tiếng", "hai triệu tám"), rồi đo ASR nghe đúng các cụm đó bao nhiêu phần trăm. Đừng quên từ phủ định: "đừng", "thôi khỏi".
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chưa đo** (chưa có báo cáo nghe audio hay benchmark ASR).
    - Ngoài WER, đo độ đúng theo loại thông tin: số tiền, số điện thoại, ngày giờ, khoảng thời gian, tên, phủ định, điều kiện, tự sửa. Báo cả tỉ lệ câu đúng toàn bộ thông tin quan trọng.
    - Đo chênh lệch điểm agent giữa oracle và ASR theo cặp.
- [ ] **[Leader]** **Q10. Có dùng được ngữ cảnh hợp lệ để sửa ASR không?** Ví dụ tên app đã cài, enum trong schema, tên kênh, và sau khi agent đọc danh bạ thì sửa lại tên người.
  - *Lưu ý:* chỉ được dùng dữ liệu lấy qua tool, không được đọc `state.json`.
  - *Gợi ý:* Whisper có `initial_prompt` hoặc hotword; hoặc sửa ở lớp sau, khi so khớp với kết quả tool.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết, chưa đo.**
    - Dùng profile, thời gian, installed_apps, schema và history. Entity chỉ biết sau một lần gọi tool thì chỉ dùng sau khi tool đó trả về.
    - Giữ transcript gốc để debug; đo số câu được sửa đúng và số câu bị làm hỏng.
    - Nếu dùng model sửa riêng lúc inference, model đó tính vào giới hạn tham số và thời gian.
- [ ] **[Leader]** **Q11. Lượt user trong history có cần ASR chất lượng cao không, hay model nhỏ, nhanh là đủ?**
  - *Gợi ý:* trên train, thay transcript history bằng ASR kém hơn (hoặc cố tình làm nhiễu) rồi đo điểm agent giảm bao nhiêu.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chưa đo.**
    - Thí nghiệm 2×2: lượt cuối và history, mỗi phần dùng oracle hoặc ASR; cùng checkpoint, cùng mẫu.
- [ ] **[Leader]** **Q12. Chuẩn hoá chữ thành số đặt ở đâu: ASR xuất thẳng chữ số, một bộ quy tắc riêng, hay để LLM tự hiểu?**
  - *Vì sao:* 11% tham số của lệnh ghi là số phải tính.
  - *Gợi ý:* thử cả 3 cách trên các mẫu có `amount`, `time`, `phone`.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chưa đo.**
    - Đề xuất: ASR giữ nguyên lời nói; một bộ phân tích có kiểu xử lý số tiền, điện thoại, khoảng thời gian, giờ. LLM chọn ý định, mốc và phép toán; code tính kết quả.
    - So ba cách (raw ASR, ASR + ITN, để LLM tự xử lý) trên cùng tập dev.

### D. Agent và mô hình

- [ ] **[Anh]** **Q13. Phần nào nên chuyển từ LLM sang code tất định, và mỗi phần cứu được bao nhiêu điểm?**
  - *Gợi ý:* dùng mục 3.2 làm khung; với từng nhóm (ngày giờ, số, ID, quy ước call đọc), ước lượng số mẫu bị ảnh hưởng × xác suất LLM làm sai.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết (chưa có ablation).**
    - Ưu tiên thử: tính ngày giờ, số học và so sánh có kiểu; validate; enum và nguồn gốc ID; theo dõi việc còn dở; xử lý `done=false`; phục hồi lỗi JSON.
    - **Claude đo (29/10), đây là trần trên dev_random, không phải điểm cứu chắc chắn:**
      - `done=false` chỉ xuất hiện ở 7/233 rollout, tối đa khoảng 3,0 điểm.
      - Lỗi JSON/schema có ở 5 trace, 1 trace tự sửa được.
      - Nhóm số/giờ 15 mẫu, tối đa 6,4 điểm; nhóm điều kiện 11 mẫu, tối đa 4,7 điểm.
    - **Thêm 30/10:** luật tất định "ID lấy từ lần tra ≥ 2 mục trùng tên thì hỏi lại" không báo nhầm lần nào trên fit, nhưng phát lại trên rollout chỉ kích hoạt 0–1 mẫu, nên không đưa vào agent ([EXPERIMENT_D](docs/EXPERIMENT_D.md) mục 4).
- [ ] **[Anh]** **Q14. Có nên ép model chỉ được sinh ID đã xuất hiện trong kết quả tool hoặc history, và chỉ sinh enum hợp lệ** (constrained decoding)? Rủi ro là gì?
  - *Ví dụ rủi ro:* chặn nhầm ID hợp lệ được tạo trong lượt; làm chậm suy luận.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết.**
    - Enum theo schema. ID theo x-ref và dữ liệu đã thấy còn hiệu lực, kể cả ID vừa tạo trong lượt.
    - Ràng buộc này không đủ: `train_1511` chọn một ID có thật nhưng sai xe.
    - So hậu kiểm với constrained decoding trước khi áp dụng rộng.
- [ ] **[Anh]** **Q15. Đánh đổi giữa model 4B và 1.7B, LoRA và full fine-tune, có thêm một dòng "kế hoạch ngắn" trước khi gọi tool hay không — trong giới hạn 30 giây và 16K token. Thí nghiệm nào trả lời rẻ nhất?**
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: đã xác minh (checkpoint 1.7B); giả thuyết (4B, full fine-tune, kế hoạch ngắn).**
    - **Claude đo (29/10) trên đủ 233 mẫu dev:** step_100 38,95 → step_200 52,47 → final 53,92. Final và step_200 không phân biệt được.
    - Final đạt 80,2 trên 233 mẫu đã train so với 53,9 trên dev.
    - Thí nghiệm kế tiếp (A: 2 epoch; E: 4B cùng protocol) ở [docs/EVAL_2026-10-29.md](docs/EVAL_2026-10-29.md) mục 5. Chưa ưu tiên full fine-tune hay RL.
- [ ] **[Anh]** **Q16. vLLM có cho kết quả giống hệt nhau qua 5 lần chạy không (greedy, batch 1, cùng GPU)? Nếu không, khử khác biệt bằng cách nào?**
  - *Vì sao:* nếu lần chạy lại của BTC khác kết quả đã nộp, họ lấy trung bình 5 lần, có thể tụt điểm.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: chưa đo (vLLM, A30, có ASR); đã xác minh (HF greedy trên RTX 4070, chỉ agent).**
    - **Claude đo (29/10):** chạy lại checkpoint final cho cùng lời gọi, cùng hash và cùng output thô ở 233/233 mẫu.
    - Chưa chứng minh tái lập với vLLM, trên A30, hay khi có ASR. Vẫn cần 5 lần chạy trên môi trường triển khai.

### E. Dữ liệu

- [ ] **[Anh]** **Q17. Làm sao để dữ liệu tổng hợp tuân theo chính sách của BTC chứ không theo "thói quen" của LLM sinh dữ liệu? Kiểm chứng độ "giống thật" ra sao?**
  - *Gợi ý:* (a) chỉ train trên dữ liệu tổng hợp rồi đo trên train thật; (b) huấn luyện một bộ phân loại thật/giả; (c) so phân bố số call, tỉ lệ hỏi lại, tỉ lệ ngoài phạm vi.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết.**
    - Ưu tiên dữ liệu phản thực tế sinh từ fit: đổi số dư quanh ngưỡng, giờ, entity/ID, thứ tự danh sách, lời tự sửa, đủ/thiếu slot. Sinh lại nhãn rồi kiểm bằng thực thi.
    - Cần thêm: kiểm tra theo chính sách (đọc, hỏi, tham số tuỳ chọn, văn phong fuzzy); ablation chỉ dữ liệu thật so với thật + tổng hợp; kiểm trên tập giữ riêng chưa dùng để sinh nhãn.
    - Không đọc file environment của BTC để làm fixture.
    - **Thêm 30/10:** bộ sinh cặp đủ/thiếu từ fit đã có ([PR #3](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/3)).
      - Mọi nhãn phát lại qua ToolEnv; câu qua 7 kiểm tra; loại nguồn từ dev.
      - Chạy thử ra 23 mẫu; chưa có người đọc tay, chưa train.
- [ ] **[Anh]** **Q18. Đa dạng hoá ngôn ngữ nói thế nào và theo tỉ lệ bao nhiêu?** Gồm phương ngữ, tự sửa giữa câu ("5 giờ, à không, 5 rưỡi"), phủ định, nhiều ý định trong một câu, từ tiếng Anh xen vào. Cần TTS cho ASR hay chỉ cần text cho LLM?
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết.**
    - Paraphrase từ fit: phủ định, tự sửa, tham chiếu history, nhiều ý trong một câu, phương ngữ, từ tiếng Anh xen vào.
    - Thử vài mức trộn định trước và báo learning curve. Chỉ dùng TTS nếu thí nghiệm ASR cho thấy cần.
    - Đội chưa nghe audio để xác nhận audio khớp kịch bản.
    - **Thêm 30/10 (việc của Leader):** Anh gợi ý VieNeu (TTS tiếng Việt, https://www.vieneu.io/) để tạo audio tăng cường cho ASR. Trang chưa ghi licence, kích thước model hay khả năng chạy offline; cần kiểm theo thể lệ (ngày phát hành, licence, chỉ dùng lúc phát triển) trước khi dùng.

### F. Kỹ thuật và quản trị rủi ro

- [ ] **[Leader]** **Q19. Liệt kê các kịch bản khiến bài nộp private về 0 hoặc mất nhiều điểm, và cách phòng cho từng kịch bản.**
  - *Ví dụ:* Docker cố tải model khi không có mạng; dùng sai bản `zaic_tools`; tràn bộ nhớ ở mẫu dài; quá 30 giây; đường dẫn `/data` sai; mã hoá UTF-8.
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết (danh sách kiểm tra); chờ BTC (hướng dẫn Docker; cold-start có tính vào 30 giây không).**
    - Cần kiểm: model và tokenizer có sẵn offline, đúng phiên bản `zaic_tools`, entrypoint, đủ mẫu, UTF-8, một ToolEnv mỗi mẫu, tổng tham số, latency toàn pipeline (p50/p95/max), tính tái lập, checksum.
    - `time_budget` của agent hiện chỉ kiểm giữa các vòng, chưa chặn một lần generate chạy quá hạn.
- [ ] **[Cả hai]** **Q20. Trong 19 ngày còn lại, đâu là đường găng (critical path)? Việc nào hai người làm song song được? Mốc "đóng băng tính năng" đặt ở ngày nào?**
  - **Trả lời của đội** (bản làm việc 29/10, chi tiết ở [handoff](docs/CLAUDE_HANDOFF_2026-10-29.md) mục 4; Claude đối chiếu): **Trạng thái: giả thuyết (lịch đề xuất, chưa họp chốt).**
    - 29–31/10: audit, sửa đánh giá, chọn checkpoint, baseline ASR, Docker smoke test.
    - 01–05/11: ablation, fit_lao, cấu hình lớn hơn.
    - 06–10/11: tích hợp ASR, đánh giá end-to-end.
    - 11–13/11: đóng băng tính năng.
    - 14–15/11: hoàn thiện, nộp sớm.
    - 16/11: dự phòng.
    - 20–23/11: chạy bản đã đóng băng trên private.
