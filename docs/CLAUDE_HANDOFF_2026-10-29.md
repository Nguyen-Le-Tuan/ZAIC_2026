# Prompt gửi Claude — tiếp tục LifeMate sau audit lượt train đầu tiên

Mình quay lại sau bước phân tích lỗi bạn giao. Mình đã nhờ Codex đối chiếu code, log, prediction/trace và đo lại loss. Dưới đây là kết quả audit cùng câu trả lời làm việc cho checklist HUMAN_TODO. Không coi đây là xác nhận rằng mình và leader đã tự nghe audio, hỏi BTC, review PR hoặc hoàn thành mọi checkbox.

Mục tiêu của phiên này là biến kết quả phân tích thành thí nghiệm có thể kiểm chứng, rồi chọn bước train tiếp theo dựa trên bằng chứng. Bạn hãy kiểm tra độc lập các kết luận, phản biện chỗ chưa chắc và thực hiện phần việc kỹ thuật trong phạm vi mình giao ở cuối prompt; không chỉ nhắc mình đọc lại tài liệu hoặc chờ mình phân tích lỗi lần nữa.

## 1. Đọc context và xác định trạng thái thật

Repo local: `/home/truyen-anh-thach/Zalo AI Challenge`.

Đọc theo thứ tự:
1. `JOURNAL.md`, nhất là trạng thái hiện tại, mục 6.4 và mục 8.
2. `docs/PIPELINE.md` và `HUMAN_TODO.md`.
3. `docs/TRAIN_REVIEW_2026-10-29.md` — báo cáo mới của Codex.
4. `lifemate/runs/codex_focus_51.md` — bảng phân loại 51 mẫu trọng tâm.
5. `lifemate/runs/codex_error_audit.jsonl` — 120 mẫu chưa đạt điểm 1; chỉ 51 mẫu trọng tâm có nhãn phân loại thủ công.
6. `lifemate/runs/codex_loss_audit.json`, `.log`, `.py` và các prediction/score/trace gốc `sft_q17b_fit_random*`, `zs_q17b_fit_random*`.

Các đường dẫn ở danh sách trên tính từ repo root. Audit code tại commit `da62cf9f9499d3463c38222081153b1d221541d1`; kiểm tra HEAD hiện tại trước khi áp dụng kết luận. `runs/` là artifact local, có thể không tồn tại trên clone khác. Nếu thiếu, nói rõ artifact nào thiếu và tái tạo phần có thể tái tạo từ nguồn được phép; không tự điền kết quả.

Tình trạng checklist:
- Lượt train qua đêm đã hoàn tất theo log. Không chạy lại lệnh train ở mục 1 chỉ vì checkbox cũ chưa đánh dấu.
- Phần đọc điểm và phân tích lỗi đã có audit với sự hỗ trợ của Codex; cần bạn đối chiếu, không ghi thành “hai người đã tự kiểm chứng toàn bộ”.
- Chưa có báo cáo nghe 30 audio train/20 audio public, câu trả lời mới từ BTC, trạng thái máy leader, tài khoản cloud/HF, bảng licence cập nhật, phê duyệt PR hay lịch họp đã thống nhất. Giữ những việc này là chưa xác nhận.
- Q1–Q20 bên dưới có mức độ chắc chắn khác nhau. Có câu trả lời làm việc không đồng nghĩa đã giải quyết xong câu hỏi nghiên cứu.

## 2. Thể lệ làm căn cứ cho quyết định

Nguồn: https://challenge.zalo.ai/portal/lifemate — bản nội dung và hai ảnh Description/Evaluation mình đã cung cấp. Nếu có thông báo chính thức mới, ghi rõ nguồn, ngày và chỗ thay đổi; không coi giả định của mình hay tài liệu dự án là xác nhận của BTC.

Các ràng buộc cần giữ:
- Tổng hệ thống dưới 6B tham số; LLM dưới 5B; context tối đa 16.384 token. Tính cả mọi model phụ thực sự dùng ở inference.
- Mỗi mẫu tối đa 30 giây, trên A30, CPU 16 core, RAM 64GB, offline hoàn toàn. Các số đo chỉ phần LLM trên laptop chưa đủ chứng minh đạt giới hạn toàn pipeline.
- Mỗi mẫu inference đúng một ToolEnv; không đọc/copy/parse bất kỳ file nào dưới `<split>_environment/`. Chỉ lấy dữ liệu app qua các tool được phép. Không reset/clone môi trường để thử các nhánh rồi chọn nhánh tốt nhất.
- Submission lấy mọi call thực sự đã gọi, kể cả call thất bại, và hash do môi trường trả. Không xóa call khỏi log sau khi biết nó làm giảm điểm. `env.validate()` là kiểm tra schema trước thực thi theo API BTC cung cấp.
- Gold rỗng: chỉ prediction rỗng mới được 1. Gold không rỗng: hash sai hoặc không có call khớp thì 0; còn lại tính F1. Ghép call là một-một, không xét thứ tự, nhưng thực thi/replay vẫn theo thứ tự và thứ tự có thể đổi state.
- Tham số non-fuzzy phải identical. Fuzzy dùng token-F1 > 0,6 sau lowercase và NFC; free-text fuzzy không ảnh hưởng hash theo mô tả Evaluation. Không tự áp dụng chuẩn hóa fuzzy cho mọi tham số.
- Dùng đúng catalog và phiên bản zaic_tools của split, lọc tools theo installed_apps từng mẫu. Schema thật là căn cứ; ví dụ minh họa trên trang không thay thế tên tool/argument thực tế.
- Không gán nhãn/pseudo-label public/private để train hoặc tune, kể cả nhờ model ngoài. ASR khi chạy inference là một phần pipeline; không biến transcript/kết quả test thành bộ huấn luyện hay tập nhãn để chỉnh tay theo từng mẫu.
- Synthetic có thể tạo trong phát triển theo thể lệ; các dịch vụ/model bên ngoài đó không được dùng ở inference. Kiểm ngày phát hành và licence của nguồn/model sử dụng, theo mốc trước 26/10/2026 và ngoại lệ synthetic được nêu.
- Fix seed Python/NumPy/PyTorch… và decoding xác định cho ASR/LLM. Temperature 0 tự nó chưa chứng minh tái lập toàn hệ thống.
- Hạn Docker: 16/11/2026 23:59 GMT+7, tối đa hai lần, lần cuối được xét. Phải kèm code train/infer/data theo yêu cầu, checksum và link Google Drive công khai để BTC tải. Cần đọc hướng dẫn Docker riêng trước khi chốt entrypoint/layout.
- Private phát hành 20/11 lúc 09:00, nộp kết quả trước 23/11 23:59 GMT+7, dùng giải pháp đã đóng băng. Không dành giai đoạn này cho fine-tune hoặc chỉnh heuristic theo private.

## 3. Kết quả phân tích lỗi cần bạn đối chiếu

Baseline 9,8999 → SFT 53,9163; call-F1 bỏ hash 67,1680; hash_acc theo scorer 63,0901%. Có 113 mẫu điểm 1, 20 mẫu một phần, 100 mẫu điểm 0.

Phát hiện mới quan trọng nhất: train.py mặc định `--eval-n=100`, lấy đầu file. Log dev loss 0,0234 không đo trên toàn bộ 233 mẫu dùng tính điểm.

| Tập | Loss final đo lại | Điểm rollout đã lưu |
|---|---:|---:|
| 100 mẫu đầu | 0,023435 | 68,94 |
| 133 mẫu còn lại | 0,115310 | 42,62 |
| Toàn bộ 233 | 0,068489 | 53,92 |

Phần sau có loss cao khoảng 4,92 lần. Ask_missing đạt 83,33 ở nhóm đầu nhưng 30,00 ở nhóm sau. Không được dùng loss cũ để kết luận toàn dev đã hội tụ tốt. Đồng thời chưa đủ bằng chứng kết luận overfit, underfit hay 1.7B thiếu capacity. Chưa có rollout step_100/step_200 để chọn checkpoint.

Audit ghi nhận: không trùng ID hoặc nguyên prompt đầu giữa fit/dev; 529/529 tool_results gold dev khớp khi replay; không có dev tool response gold/history bị cắt ở ngưỡng 4.000 ký tự; không có timeout/max_steps/retries stop trong rollout này. Đây là kiểm tra cụ thể, không phải bằng chứng loại trừ mọi leakage/bug.

51 execute có call khớp nhưng hash sai được phân theo sai lệch chủ yếu:
- 15 ngày giờ/số lượng/số tiền.
- 11 nhánh điều kiện hoặc hành động phụ thuộc điều kiện.
- 12 xác định đối tượng, ID, truy vấn, tham chiếu history.
- 12 tool/chuỗi hành động, thiếu/thừa việc hoặc hỏi lại.
- 1 JSON hỏng làm mất hành động.

Mỗi mẫu chỉ được tính một nhóm, có thể còn lỗi phụ; đây chưa phải ablation hay dự báo điểm cứu được.

Các mẫu tiêu biểu:
- train_0109: tool trả rain=false nhưng vẫn hủy lịch, gửi SMS báo mưa.
- train_0098: ví 185900 < hóa đơn 216000; pay trả ok=true, done=false, model vẫn gửi thông báo đã đóng.
- train_0072: giá bán 126,6 triệu < 127 triệu nhưng làm sai nhánh.
- train_0238: hẹn 14:30, xe đón trước 30 phút, nhắc trước xe 15 phút; đúng là 14:00/13:45, model sinh 13:30/13:15.
- train_1558: 16:30 + 90 phút phải 18:00, model sinh 15:45.
- train_1511, ngoài nhóm 51: chọn ID xe có thật nhưng tiền thuê vượt ngân sách. Ép “ID đã thấy” không đủ.
- train_1458: JSON fitness.set_goal chứa phép cộng chưa tính; cùng completion có phone.call hợp lệ. Agent dựng lại history từ call parse được, mất nội dung call hỏng rồi model dừng. Cần kiểm tra lỗi phục hồi này, không chỉ ép JSON.

Có 31 prediction hỏi lại nhưng chỉ 17 trùng nhóm 33 gold cần hỏi. Có 14 execute bị hỏi lại, 16 gold cần hỏi không được hỏi. Chỉ 5/233 trace có lỗi JSON/schema, gồm cả lỗi đã tự sửa thành công. Vì vậy, chỉ sửa format sẽ không giải quyết phần lớn vấn đề.

## 4. Câu trả lời làm việc cho Q1–Q20

### Q1. So khớp tham số

**Căn cứ thể lệ:** non-fuzzy identical; fuzzy lowercase + NFC rồi token-F1 > 0,6. Giữ exact comparison làm mặc định, không tự lowercase hoặc gộp whitespace non-fuzzy.

**Còn cần xác nhận:** cách token hóa/punctuation của fuzzy, optional key absent so với explicit default, thứ tự phần tử list và các chi tiết chuẩn hóa không được nói rõ. Không trộn cách canonicalize state hash với cách chấm call. Ưu tiên câu trả lời chính thức hoặc scorer BTC nếu có; không viết rằng đã xác nhận từ public score.

### Q2. Chính sách sinh nhãn

**Giả thuyết:** nhãn có nhiều quy luật/template, nhưng chưa biết được sinh bằng template, LLM hay pipeline kết hợp. Đừng biến dấu vết thống kê thành khẳng định về hệ thống nội bộ BTC.

Phân tích trên fit: signature tool sequence, tham số đọc, default/optional key, phrasing fuzzy, cách chọn đối tượng và thứ tự hành động. Tách các nhóm khác quy ước; không ép toàn bộ dữ liệu theo một luật chỉ vì nhóm đầu file tuân theo. Kiểm độ tổng quát trên dev/group holdout.

### Q3. Khi nào đọc trước ghi?

**Nguyên tắc làm việc:** đọc khi thiếu đối tượng, thuộc tính hoặc điều kiện cần thiết; dùng lại thông tin history còn hiệu lực khi đủ. Theo dõi thay đổi sau write để tránh dùng dữ liệu cũ. Không áp luật cứng “mọi write đều phải read” hoặc “history từng có thì luôn bỏ read”.

Tách hai mục tiêu: đủ thông tin thực thi đúng và khớp quy ước call của nhãn. Có mẫu cần filtered read, mẫu dùng `{}`. Cần thống kê ngoại lệ; đừng xóa filter chỉ để giống đa số. Nếu code tính nội bộ thay một phép toán, vẫn phải xem gold có chấm calculator tool hay không.

### Q4. Hỏi lại hay tự quyết?

**Nguyên tắc:** dùng context/history và tool hợp lệ để giải quyết phần có thể tra; chỉ hỏi thông tin bắt buộc không xác định được hoặc đối tượng vẫn mơ hồ. Kiểm x-one-of: có phone_number hợp lệ không nhất thiết cần contact_id. Tôn trọng lời tự sửa cuối cùng của user.

Ask đúng tool đích và params còn thiếu, dừng sau ask. Dữ liệu nên có minimal pairs đủ/thiếu slot và một/nhiều đối tượng khớp. Đo riêng hỏi thừa, bỏ hỏi, sai params; không chỉ đếm số lần hỏi.

### Q5. Ngoài phạm vi

**Đã biết từ journal:** 111 mẫu, có thiếu app, hủy/phủ định, trò chuyện, thông tin đã có. **Chưa hoàn tất:** phân loại độc lập đủ 111 mẫu và chính sách yêu cầu làm được một phần.

Không suy ra rằng một ý không hỗ trợ thì luôn bỏ toàn bộ yêu cầu, hoặc câu có từ “thôi” thì trả rỗng. Cần kiểm phủ định từng ý, tự sửa, capability thực tế của installed_apps. Chưa xác nhận phân bố public/private bằng các nhãn tự tạo.

### Q6. Dev mô phỏng private

**Giả thuyết rủi ro:** app/schema mới, history dài, ngôn ngữ/giọng khác, thay đổi ID/thứ tự entity và tổ hợp tác vụ. Public có app ngoài train là bằng chứng về nhu cầu tổng quát hóa, không chứng minh private chắc chắn có đúng loại shift nào.

Dùng random dev để đo tiến bộ cùng miền; train fit_lao riêng để đo unseen-app; bổ sung nhóm/template holdout hoặc cross-validation đủ mẫu. Đảm bảo held-out apps không rò qua gold, history, ask_missing.tool_name, distractor hoặc augmentation. Chỉ chấm checkpoint random trên dev_lao không thành unseen-app evaluation. Leave-groups-out là stress test bổ sung khi đủ dữ liệu, không mặc định là ước lượng private tốt nhất.

### Q7. Dùng quota public

**Đề xuất:** coi public là kiểm tra tích hợp bên ngoài; không cần dùng hết 5 lượt/ngày. Chỉ nộp khi có candidate xác định rõ checkpoint, config, nội bộ đã kiểm tra và mục đích đo.

Ghi lịch sử thay đổi và score; tránh chỉnh theo mẫu test hoặc tìm kiếm quá nhiều cấu hình theo leaderboard. Không ưu tiên bài rỗng/biến đổi chỉ để dò phân bố hoặc thước đo trong phiên này. Nếu cần làm rõ metric, ưu tiên hỏi BTC. Hiện chưa có public score mới để đưa vào quyết định.

### Q8. Dev và public lệch

**Chưa đo:** mức lệch thực tế. Các nguyên nhân cần phân biệt gồm ASR, schema mới, tỉ lệ tác vụ, context/history, scorer, runtime và bản zaic_tools.

Trên train-heldout, so oracle-text/ASR với cùng agent; so seen/unseen-app với protocol đúng; đo timeout và kết quả parsing; đối chiếu scorer với đặc tả. Public dùng đúng thư viện và catalog của split. Không có gold public thì không suy diễn chính xác số điểm mất do từng nguyên nhân từ một scalar leaderboard.

### Q9. Metric ASR theo thông tin quan trọng

**Chưa có kết quả nghe/benchmark.** Đề xuất ngoài WER, đo độ đúng của thông tin: số tiền, số điện thoại, ngày/giờ, khoảng thời gian, tên/đối tượng, phủ định, điều kiện và tự sửa.

Xác định facts/slots từ train transcript và context hợp lệ, phân biệt lấy trực tiếp từ lời nói với giá trị chỉ xuất hiện sau tool. Báo accuracy từng loại và tỉ lệ câu đúng toàn bộ thông tin quan trọng; nêu mẫu số, trường hợp mơ hồ. Đo thêm chênh lệch score agent oracle/ASR theo cặp. Không quy mọi lỗi chọn ID downstream thành lỗi ASR.

### Q10. Ngữ cảnh để sửa ASR

**Đề xuất:** dùng profile, thời gian, installed_apps, schema và history đã quan sát hợp lệ. Entity chỉ biết sau tool thì chỉ dùng sau thời điểm tool đó trả về; không đưa gold/final_state hoặc dữ liệu app chưa quan sát vào ASR prompt.

Hotword/contextual correction cần thử vì có thể ép nghe sai thành tên quen. Bảo toàn raw transcript để debug; đo số câu được cứu và bị làm hỏng trên heldout train. Nếu dùng model sửa riêng ở inference, tính vào giới hạn tham số và thời gian/offline.

### Q11. ASR history có thể yếu hơn không?

**Chưa có bằng chứng để chốt.** History chứa mốc thời gian, số tiền, người nhận và lời sửa đổi nên có thể quyết định hành động.

Thí nghiệm 2×2: lượt cuối/history lần lượt oracle–oracle, ASR–oracle, oracle–ASR, ASR–ASR. Cùng checkpoint, cùng samples. Chỉ chọn ASR nhẹ hơn cho history nếu lợi ích latency đáng giá so với điểm mất. Có thể cache theo file audio khi nó thực sự xuất hiện lại, không giả định cache làm biến mất toàn bộ chi phí history.

### Q12. Chuẩn hóa chữ thành số

**Đề xuất:** ASR giữ lời nói; bộ phân tích có kiểu dữ liệu xử lý số tiền, điện thoại, duration, thời gian. Giữ nguồn và biểu diễn gốc, không thay mọi chuỗi chữ-số một cách mù quáng.

LLM chọn ý định, mốc và phép toán; code tính kết quả, datetime/timezone và kiểm ràng buộc. Nếu không phân giải được mốc thì không tự bịa. So raw-ASR, ASR+ITN và LLM tự xử lý trên cùng dev; chưa khẳng định phương án nào thắng trước khi đo.

### Q13. Phần nào chuyển sang code?

**Ưu tiên thử:** tính ngày giờ/số học/so sánh có kiểu dữ liệu; validate schema; enum và provenance ID; theo dõi pending action; xử lý done=false và phục hồi lỗi.

Không hard-code theo ID mẫu, không tự chọn đối tượng chỉ bằng phép tính. Chặn ID chưa thấy không giải quyết chọn nhầm ID có thật. 15 mẫu numeric + 11 conditional trong nhóm 51 là phạm vi quan sát, không phải 26 mẫu chắc chắn sửa được. Đo ablation từng thành phần với số mẫu cứu/hỏng và delta score, hash, F1, latency.

### Q14. Ràng buộc ID/enum

**Đề xuất:** enum theo schema; ID theo loại x-ref và dữ liệu đã quan sát còn hiệu lực, gồm cả ID vừa được tạo trong lượt. Phân biệt ID với tên hiển thị, số điện thoại hoặc các lựa chọn x-one-of.

Rủi ro: danh sách thiếu do read có lọc, ID cũ bị xóa, loại ID nhầm, chặn nhầm giá trị hợp lệ, hoặc tăng latency. Không chọn đại ID hợp lệ để vượt validator. Khi thiếu thông tin, tra bằng tool hợp lệ hoặc hỏi đúng slot. So hậu kiểm với constrained decoding trước khi quyết định triển khai rộng.

### Q15. 1.7B/4B, LoRA/full FT, kế hoạch ngắn

**Ưu tiên:** chấm checkpoint hiện có trước. Sau đó so tăng compute trên 1.7B với bổ sung dữ liệu nhắm lỗi, rồi 4B LoRA trên cùng split/protocol. Báo cả compute, lượng dữ liệu và learning curve để không quy nhầm lợi ích.

Chưa ưu tiên full FT hoặc RL khi chưa có bằng chứng cần. Nếu thử kế hoạch ngắn, dùng dạng có cấu trúc, chỉ dựa trên quan sát tại thời điểm đó, không lộ kết quả tương lai/gold. Đo chất lượng và số token/latency. Không train all rồi báo dev_random là heldout; không mặc định 4B vừa ngân sách toàn hệ thống nếu chưa đếm model ASR/phụ.

### Q16. Tái lập

**Chưa chạy phép đo 5 lần vLLM.** Fix seed, greedy, pin weights/tokenizer/dependencies/config, ổn định thứ tự input và batching. Kiểm cả ASR, không chỉ LLM.

Trên môi trường triển khai, chạy 5 lần, so từng sample tool_calls, state_hash, score, timeout và latency. Nếu lệch, cô lập bước đầu khác nhau rồi kiểm kernel/backend/batching/precision. Không khẳng định temperature 0 bảo đảm bitwise reproducibility. Không nhân cơ hội thử 5 lần để chọn output tốt nhất; mục đích là đo tái lập.

### Q17. Synthetic đúng policy

**Đề xuất:** ưu tiên counterfactual từ fit: đổi số dư quanh ngưỡng, thời gian, entity/ID nhất quán, thứ tự danh sách, lời tự sửa, đủ/thiếu slot; tái sinh nhãn và kiểm thực thi/điều kiện.

Simulator đúng chỉ chứng minh chạy được và state phù hợp fixture, chưa chứng minh giống quy ước call BTC. Cần thêm policy checks cho read/ask/optional args/fuzzy text, ablation real-only/real+synthetic, kiểm trên holdout chưa dùng sinh nhãn. Schema mới có thể dùng simulator/fixture tự tạo độc lập; không đọc/copy file environment BTC để làm fixture. Giữ nguồn gốc và công thức sinh dữ liệu.

Journal có ghi đội từng nhận giải thích rằng dùng catalog/zaic_tools public để sinh dữ liệu được phép. Đây là thông tin đội đã ghi lại, không phải xác nhận mới từ lần audit. Dù dùng schema public, không dùng audio/yêu cầu/trạng thái ẩn public để tạo nhãn train/tune. Không tự áp model-generated labels lên dev rồi đưa ngược vào fit.

### Q18. Đa dạng ngôn ngữ/TTS

**Đề xuất:** ưu tiên paraphrase từ fit cho phủ định, tự sửa, tham chiếu history, nhiều ý định, phương ngữ và English xen kẽ. Kiểm semantic equivalence và cập nhật target khi thay đổi ý định thật.

Chưa có tỉ lệ tối ưu; thử ít mức trộn được xác định trước, báo learning curve thay vì chọn một tỉ lệ theo cảm tính. Text augmentation phục vụ LLM; TTS chỉ cần nếu thí nghiệm ASR cho thấy lợi ích. Kiểm chứng trên audio thật heldout, không dùng TTS để thay việc xác minh transcript của người nói. Chưa ghi rằng audio đã được đội nghe và xác nhận khớp kịch bản.

### Q19. Rủi ro triển khai

**Các kiểm tra cần có:** đủ model/tokenizer offline; đúng phiên bản zaic_tools và đường dẫn dữ liệu mount; entrypoint/output path theo hướng dẫn Docker; đủ mọi sample, UTF-8/JSONL; một env và đầy đủ call log; hash do env; tổng tham số/context; latency toàn pipeline; GPU/RAM; tái lập và integrity checksum.

30 giây phải đo cả ASR/history, agent và overhead thuộc phạm vi BTC tính. Cold-start có nằm trong hạn từng mẫu chưa rõ thì nêu là câu hỏi, chưa tự suy diễn. Agent time_budget hiện kiểm giữa các vòng chưa bảo đảm một generate không vượt deadline. Cần đo p50/p95/p99/max và timeout rate. Không catch mọi lỗi rồi im lặng xuất rỗng, không sửa hash/log để che lỗi.

### Q20. Đường găng và mốc làm việc

**Lịch đề xuất, chưa phải lịch họp đã chốt**, tất cả mốc nộp theo GMT+7:
- 29–31/10: audit, sửa evaluation, chọn checkpoint, có kết quả ASR baseline trên train-heldout; dựng Docker smoke-test sớm.
- 01–05/11: ablation agent/tính toán/dữ liệu nhắm lỗi; fit_lao; benchmark cấu hình lớn hơn nếu có tài nguyên.
- 06–10/11: tích hợp ASR và agent, đánh giá end-to-end, một số lần nộp public có mục đích rõ; không học nhãn test.
- 11–13/11: chọn candidate, đóng băng tính năng nội bộ, kiểm offline/tái lập/thời gian trên A30 nếu có.
- 14–15/11: hoàn thiện code/data/manifests/checksum, kiểm khả năng tải Docker, nộp sớm.
- 16/11: dự phòng trước 23:59 GMT+7; nếu dùng lần nộp thứ hai phải kiểm toàn bộ vì BTC xét lần cuối.
- 20–23/11: chạy giải pháp đã đóng băng với private và nộp kết quả; không fine-tune lại.

Phân công đề xuất: mình phụ trách agent/evaluation; leader phụ trách ASR/Docker; hai bên thống nhất giao diện ASR và đánh giá end-to-end. Không đợi LLM hoàn thiện mới làm Docker. Việc chưa có tài nguyên hoặc cần người xử lý phải ghi dependency, không đánh dấu đã hoàn tất.

## 5. Phần việc giao cho bạn trong phiên tới

Thực hiện theo thứ tự, giữ baseline và giới hạn phạm vi để biết thay đổi nào tạo ra hiệu quả:

1. **Kiểm tra audit.** Đọc artifact, tái tính thống kê từ file có sẵn, xem mẫu đại diện từng nhóm và các case 0098/0109/1458. Kiểm shift/mask loss, sample coverage và phần chênh lệch 100/133. Nếu phản bác, đưa ID/code/evidence cụ thể. Không cần chạy lại toàn bộ kiểm tra đã khớp nếu không có nghi vấn mới.
2. **Sửa đường đánh giá qua code branch/PR phù hợp.** Cho chọn rõ fit/dev trong script; mặc định đánh giá đủ dev hoặc ghi rõ subset được chọn. Không dùng sự tồn tại của file SFT cũ như bằng chứng nó đúng split/config: kiểm ID và metadata/manifest. Giữ nguyên file split để đối chiếu baseline. Lưu model/checkpoint, hash dữ liệu, args, seed, backend và số mẫu mỗi lần đo.
3. **Chấm checkpoint sẵn có.** Nếu step_100/step_200 tồn tại, chạy cùng protocol oracle-text trên đủ 233 mẫu, cùng backend với baseline. Có thể tái dùng final rollout đã lưu nếu weights/code/config khớp. Không ghi đè prediction/checkpoint cũ. Báo score, call-F1, hash, từng category và latency; so theo cặp. Đây là eval, chưa phải yêu cầu train một đợt mới.
4. **Chốt thí nghiệm kế tiếp bằng bằng chứng.** Đề xuất ít phương án có thể phân biệt giả thuyết; mỗi phương án có một thay đổi chính, tập đo, đối chứng, chi phí ước lượng và tiêu chí giữ/bỏ. Ưu tiên lỗi điều kiện, tham chiếu/tính toán và phục hồi hành động. Không gộp đổi model, prompt, data, decoder vào một run rồi kết luận nguyên nhân.
5. **Cập nhật context.** Ghi kết quả thật vào JOURNAL; trong HUMAN_TODO ghi các câu trả lời làm việc với trạng thái “đã xác minh / giả thuyết / chưa đo / chờ BTC”. Chỉ đánh dấu hoàn tất phần thực sự hoàn tất, không đánh dấu thay các việc nghe audio, thanh toán, hỏi BTC hoặc review của người. Giữ quy tắc tài liệu main, code qua PR; không vô tình đưa code vào main hoặc commit artifact chứa dữ liệu cuộc thi. Không tự merge thay người review.

Trong phiên này, mình giao việc đọc/kiểm chứng, sửa evaluation và chạy eval local cần thiết. Chưa yêu cầu thuê cloud, thanh toán, nộp public, upload Docker hoặc chạy một lượt train dài mới. Các việc đó phải có candidate/config và mục tiêu cụ thể để mình quyết định. Không cần hỏi lại cho các thao tác kỹ thuật nằm trong phạm vi vừa giao.

Nếu evaluation cũ đáng tin sau kiểm chứng thì đi tiếp, không dừng ở việc đưa lời khuyên chung. Nếu gặp blocker thật, ghi cụ thể thiếu file/tài nguyên/quyết định nào và hoàn thành phần độc lập còn làm được.

## 6. Kết quả mình muốn nhận cuối phiên

- Bảng đối chiếu các nhận định của Codex: đồng ý, cần sửa, chưa đủ bằng chứng.
- Bảng checkpoint so trên cùng 233 mẫu, hoặc lý do cụ thể không đo được checkpoint nào.
- Diff/PR của evaluation và kết quả kiểm chứng phù hợp.
- Quyết định đề xuất chọn checkpoint nào và thí nghiệm tiếp theo nào, với căn cứ và rủi ro.
- Danh sách việc còn cần mình/leader/BTC, tách khỏi những việc bạn đã thực hiện.

Mình muốn bạn phân biệt rõ quan sát, suy luận và kết quả can thiệp. Chưa có ablation thì không nói một bản sửa chắc chắn cứu được bao nhiêu điểm. Mục tiêu là tăng chất lượng giải pháp đóng băng và khả năng tổng quát hóa, không chỉ làm đẹp loss hay thích nghi với 233 mẫu dev đã xem kỹ.
