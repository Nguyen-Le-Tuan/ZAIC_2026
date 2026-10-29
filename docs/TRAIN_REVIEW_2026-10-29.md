# Đánh giá lượt train đầu tiên — 29/10/2026

Phạm vi: phân tích yêu cầu tại mục 7 của `HUMAN_TODO.md` và kết quả trong mục 6.4 của `JOURNAL.md`. Không thực hiện các TODO khác, không sửa pipeline, không train thêm. Báo cáo dựa trên code tại commit `da62cf9f9499d3463c38222081153b1d221541d1`, log, 233 prediction/trace và dữ liệu train hợp lệ; bổ sung một lượt đo loss bằng checkpoint đã có. Không đọc trực tiếp file environment, không phân tích/gán nhãn mẫu test.

## Kết luận

Lượt train thành công về vận hành và tạo ra tiến bộ đáng kể. Tuy nhiên, model chưa đáng tin ở việc chuyển từ thông tin quan sát được sang quyết định hành động: chọn nhánh, xác định đối tượng, tính toán và phân biệt lúc cần hỏi lại. Đây là bottleneck rộng hơn lỗi sinh JSON hoặc chép ID.

Phát hiện mới quan trọng nhất là **loss đang báo chỉ thuộc 100 mẫu đầu của dev, có kết quả tốt hơn nhiều so với 133 mẫu còn lại**. Tôi đo lại được loss 0,023435 trên 100 mẫu đầu, khớp log 0,0234; loss trên 133 mẫu sau là 0,115310; toàn bộ 233 mẫu là 0,068489. Không nên dùng đường loss hiện có để kết luận model đã học tốt toàn bộ dev hoặc đã đến trần năng lực.

Ưu tiên tiếp theo: sửa cách đo/chọn checkpoint; thử nghiệm có kiểm soát cho tính toán, điều kiện và phân giải history; kiểm soát kết quả thực thi và lỗi phục hồi. Chưa có bằng chứng để kết luận tăng epoch, tăng rank hay đổi sang 4B tự nó sẽ giải quyết vấn đề.

## Context tôi hiểu từ công việc của Anh và Claude

- Bài LifeMate biến audio tiếng Việt và history thành chuỗi tool call. State hash đóng vai trò cổng chấm điểm; khớp nhiều lời gọi vẫn có thể nhận 0 nếu trạng thái cuối sai.
- Kiến trúc dự kiến ASR → chuẩn hóa → Qwen3 agent → ToolEnv. Lượt hiện tại mới đo phần agent bằng transcript chuẩn; chưa đo ASR.
- Có 1.545 mẫu train; random split dùng 1.312 mẫu fit và 233 mẫu dev. Public có app ngoài train, nên khả năng hiểu schema mới là yêu cầu quan trọng. Chưa có phép đo leave-apps-out hợp lệ cho checkpoint này.
- 4.150 dòng SFT là các biến thể của 1.312 mẫu gốc, không phải 4.150 tình huống độc lập. Rename, distractor, lowercase và remove-app tăng độ đa dạng bề mặt, nhưng chưa trực tiếp tạo các cặp thay đổi số dư/giờ/ID/điều kiện có đáp án tương ứng.
- Đội có hai người; máy local 4070 Laptop 8GB dùng cho agent; hướng model 4B/cloud và ASR là công việc tiếp theo. Code đang ở nhánh `agent-pipeline`; tôi chỉ tạo báo cáo và dữ liệu audit local.

## 1. Điều đã kiểm chứng

| Kiểm tra | Kết quả |
|---|---:|
| Tính lại điểm từ prediction và oracle replay đã lưu | 53,9163, khớp log |
| Điểm zero-shot cùng dev | 9,8999 |
| Mức tăng | +44,0164 điểm |
| Mẫu đúng hoàn toàn / một phần / 0 điểm | 113 / 20 / 100 |
| Trùng ID giữa SFT fit và dev | 0 |
| Trùng nguyên prompt đầu vào SFT fit/dev | 0 |
| Kết quả tool gold phát lại qua ToolEnv | 529/529 khớp |
| Mẫu bị bỏ vì quá dài khi train | 0 theo log |
| Tool response gold/history của dev bị cắt ở 4.000 ký tự | 0 |
| Trace có lỗi JSON/schema | 5/233 |
| Dừng do timeout/max_steps/retries | 0/233 |

Các kiểm tra này không chứng minh không có mọi loại leakage hoặc bug; chúng loại trừ một số nghi vấn cụ thể. Chưa kiểm tra toàn diện trùng template/ngữ nghĩa giữa fit và dev. Có 1 dev có lời nói cuối trùng fit, nhưng không trùng toàn prompt.

Bootstrap 10.000 lần ở cấp mẫu, seed 0: khoảng 95% cho điểm SFT khoảng 47,80–60,20; cho chênh lệch SFT–zero-shot theo cặp khoảng +37,70–+50,41. Đây chỉ là bất định lấy mẫu dưới giả định các mẫu độc lập; các template gần nhau có thể khiến khoảng này lạc quan. Nó không phải khoảng dự đoán điểm private.

## 2. Sai lệch của phép đo dev loss

`lifemate/train.py` đặt `--eval-n=100` tại dòng 101, nạp dev với `limit=a.eval_n` tại dòng 131. `load_examples()` lấy đầu file, không lấy ngẫu nhiên. File dev đi theo thứ tự dữ liệu; mẫu thứ 100 là `train_0720`.

Đo mới bằng checkpoint final, adapter chưa merge, bf16/SDPA, eval mode, cùng công thức shifted token cross-entropy với mask của code train:

| Tập đo | N | Token có loss | Loss/token | Accuracy token khi có tiền tố gold | Điểm rollout đã lưu |
|---|---:|---:|---:|---:|---:|
| 100 mẫu đầu | 100 | 9.436 | 0,023435 | 99,35% | 68,94 |
| 133 mẫu còn lại | 133 | 9.080 | 0,115310 | 96,96% | 42,62 |
| Toàn dev | 233 | 18.516 | 0,068489 | 98,18% | 53,92 |

Loss của phần còn lại cao gấp khoảng 4,92 lần. Chênh lệch điểm không chỉ do tỉ lệ loại mẫu:

| Loại | 100 mẫu đầu | 133 mẫu sau |
|---|---:|---:|
| Execute | 64,99 (83 mẫu) | 39,38 (100 mẫu) |
| Ask missing | 83,33 (12 mẫu) | 30,00 (21 mẫu) |
| Ngoài phạm vi | 100,00 (5 mẫu) | 91,67 (12 mẫu) |

History trung bình dài 3,24 lượt ở nhóm đầu và 5,85 ở nhóm sau. Đây là tương quan, chưa chứng minh history dài là nguyên nhân; nhóm sau còn có ngôn ngữ, đối tượng và yêu cầu phức tạp khác.

**Diễn giải loss:** code chỉ tính loss trên token assistant, nên không có bằng chứng loss bị pha loãng bởi hàng nghìn token prompt đã mask. Nhưng trong token assistant vẫn có nhiều dấu JSON, tên khóa và đoạn định dạng dễ đoán. Loss dùng tiền tố và kết quả tool gold, trong khi rollout phải đi tiếp từ quyết định của chính model. Vì thế token accuracy 98,18% không tương đương task success 98,18%. Chỉ 102/233 mẫu không có bất kỳ lỗi argmax token nào dưới teacher forcing. Con số này cũng không phải trần điểm rollout: khác câu chữ vẫn có thể được chấm đúng, và hai chế độ có ngữ cảnh khác nhau.

Chưa đủ bằng chứng kết luận overfit: loss 100 mẫu tăng từ 0,0233 lên 0,0234 quá nhỏ; chưa có điểm rollout của step 100/200 để so với final. Cũng chưa đủ bằng chứng kết luận underfit hay rank 32 thiếu năng lực.

## 3. Điểm mất nằm ở đâu?

| Loại | N | Điểm |
|---|---:|---:|
| Execute | 183 | 51,00 |
| Ask missing | 33 | 49,39 |
| Ngoài phạm vi | 17 | 94,12 |

Trong 216 mẫu gold không rỗng, **85 mẫu sai hash**: 73 execute và 12 ask_missing. Riêng 85 mẫu này mất 36,48 điểm trên thang 100 toàn dev. Ngoài ra, 14 mẫu gold không rỗng có hash đúng nhưng không call nào khớp; 20 mẫu đúng một phần; 1 mẫu ngoài phạm vi bị gọi tool.

Call-F1 bỏ hash là 67,17, cao hơn điểm chính 13,25. Đây là phép đo phản thực tế khi bỏ cổng hash với nguyên prediction hiện tại, **không phải** số điểm hứa hẹn sửa được, cũng không phải trần điểm sau khi sửa lời gọi.

### Phân loại 51 mẫu ưu tiên của Claude

Tôi đọc cặp gold/prediction của các mẫu lỗi và phân 51 mẫu execute có call khớp nhưng hash sai theo **sai lệch quan sát chủ yếu**. Mỗi mẫu được gán một nhóm để tránh cộng trùng. Đây là taxonomy mô tả; ablation mới chứng minh được từng nguyên nhân và số điểm cứu được.

| Sai lệch chủ yếu | Mẫu | Ví dụ |
|---|---:|---|
| Giá trị ngày giờ, số lượng, số tiền | 15 | 0238, 0278, 0517, 1558 |
| Nhánh điều kiện/so sánh hoặc hành động phụ thuộc điều kiện | 11 | 0072, 0098, 0109, 0860 |
| Xác định đối tượng, lấy ID, tìm kiếm và tham chiếu history | 12 | 0003, 0748, 1006, 1246 |
| Chọn tool/chuỗi hành động, bỏ/thừa việc hoặc hỏi lại | 12 | 0472, 0701, 0969, 1716 |
| JSON hỏng làm mất hành động | 1 | 1458 |

Danh sách đủ 51 ID và ghi chú nằm tại `lifemate/runs/codex_focus_51.md`. File `codex_error_audit.jsonl` chứa 120 mẫu chưa đạt điểm 1, kèm gold, prediction, khác biệt và trace. Chỉ 51 mẫu ưu tiên có nhãn phân loại thủ công; không giả định các mẫu khác đã có taxonomy hoàn chỉnh.

### A. Điều kiện bị bỏ qua dù dữ liệu cần thiết đã có

- `train_0072`: giá bán 126,6 triệu, điều kiện lớn hơn 127 triệu là sai; model vẫn làm nhánh nhắc đi bán vàng thay vì chuyển tiền.
- `train_0109`: tool trả `rain=false`; model vẫn hủy lịch và gửi SMS báo mưa.
- `train_0098`: số dư 185.900, hóa đơn 216.000; model chọn ví. Executor trả `ok=true, done=false`, giải thích không đủ số dư. Model vẫn gửi thông báo đã thanh toán.
- `train_0213`: thanh toán đúng bằng ví nhưng thêm nhắc nạp ví thuộc nhánh khác, thiếu SMS cần gửi.

Các ví dụ này phản bác cách hiểu rằng vấn đề chỉ là bịa ID. Có trường hợp ID và số tiền đều đúng, nhưng quan hệ điều kiện sai. Hướng thử: biểu diễn điều kiện ngắn, có kiểu dữ liệu; code tính so sánh sau khi model chọn đúng biến; ghi rõ hành động nào phụ thuộc điều kiện. Code so sánh đúng vẫn vô ích nếu model lấy sai hóa đơn hoặc biến đầu vào.

### B. Thời gian, phép tính và tham chiếu bị trộn

- `train_0238`: hẹn 14:30, đón trước 30 phút phải 14:00, nhắc trước xe 15 phút phải 13:45. Model sinh 13:30 và 13:15.
- `train_0278`: báo thức còn lại 07:30, dời thêm 30 phút phải 08:00; model sinh 08:30.
- `train_1558`: thợ đến 16:30, sửa 90 phút, nhắc lúc 18:00; model sinh 15:45.
- `train_1511` (ngoài nhóm 51): thuê 4,5 giờ, ngân sách dưới 100.000, chọn xe đắt nhất thỏa điều kiện. Model chọn xe 30.000/giờ = 135.000; gold là xe 20.000/giờ = 90.000. ID model chọn là ID thật, nên ràng buộc “ID đã thấy” không đủ.
- `train_0134`: danh sách thành viên trả về có ba người, đích là ba suất; model trừ thêm một thành hai. Cần hiểu ngữ nghĩa danh sách, không chỉ cộng/trừ đúng.

Bảng ngày hiện tại hỗ trợ tra lịch nhưng không thay thế được việc chọn mốc, chuỗi phụ thuộc hoặc phép tính. Một bộ xử lý tất định cần nhận biểu thức có cấu trúc và nguồn của từng giá trị; không nên xây regex hậu xử lý sửa ngày/ID dựa trên gold dev.

### C. Ranh giới hỏi lại chưa được học vững

Dự đoán có ask_missing 31 mẫu, khá gần 33 mẫu gold, nhưng độ giao nhau chỉ **17 mẫu**. Có **14 execute bị hỏi lại**, còn **16/33 mẫu cần hỏi không được hỏi** (15 thực thi, 1 rỗng). Trong 17 mẫu có hỏi đúng loại hành vi, vẫn có sai tool_name/params hoặc call phụ.

Ví dụ `train_0969` có thể gọi bằng số điện thoại nhưng model hỏi contact_id; `train_1409` người dùng tự sửa từ lưu trữ sang xóa nhưng model vẫn hỏi action; `train_1728` gold thiếu số bước cần hỏi, model tự chọn 3.000.

Cần các cặp gần giống nhau: đủ/thiếu một slot; một/nhiều đối tượng; số điện thoại trực tiếp/contact_id; người dùng đã xác định lại đối tượng/chưa xác định. Không nên tăng xu hướng hỏi lại một cách đồng loạt, vì hiện cả hỏi thiếu lẫn hỏi thừa đều phổ biến.

### D. Quy ước của nhãn và bộ chấm là một nguồn mất điểm riêng

`train_0465`: thêm `location` vào weather khiến call không khớp và điểm 0 dù hash đúng. `train_1474`: thêm `days="daily"` vào medication cũng khiến điểm 0 dù state tương đương. `train_0892`: thời gian nhắc đúng, nhưng nội dung ngắn không qua token-F1 theo bộ chấm local.

Không nên kết luận mọi mẫu hash đúng là thực hiện tốt: read-only có thể trả sai dữ liệu mà state không đổi. Ngược lại, không phải mọi mẫu 0 điểm đều thể hiện thất bại ngữ nghĩa hoàn toàn. Cần theo dõi cả đúng tác vụ, đúng state và khớp quy ước call; giữ sự bất định về cách chấm chính thức.

Đặc biệt, phát hiện query tên đầy đủ không biết trước không chứng minh “không thể có điểm”. Ví dụ `train_0003` tìm “Cô Mai” trả rỗng; một lượt tìm rộng hợp lệ có thể cứu thực thi với chi phí thêm call. Chưa đo chính sách tìm lại này; chưa thể gọi đó là trần tuyệt đối hoặc hứa mức tăng.

## 4. Hạn chế trong agent và dữ liệu SFT liên quan trực tiếp

1. **Thành công schema không phải thành công tác vụ.** `Agent.run` ghi lỗi validate/parse, nhưng không có xử lý bắt buộc cho `done=false`; cũng không duy trì danh sách việc chưa hoàn thành. Dừng khi model không sinh call không đảm bảo yêu cầu đã xong. Trường hợp 0098 cho thấy rủi ro thực tế.
2. **Các call trong cùng completion được thực hiện trước khi model thấy kết quả từng call.** Khi một lệnh thất bại, các hành động phụ thuộc đã được lên kế hoạch có thể vẫn chạy. Nên tách hành động độc lập với hành động cần xác nhận thành công của lệnh trước; không nhất thiết bỏ batching hoàn toàn.
3. **Lỗi JSON hỗn hợp có thể mất thông tin phục hồi.** 1458 sinh `fitness.set_goal` với biểu thức chưa tính trong JSON, đồng thời sinh `phone.call` hợp lệ. Parser chỉ giữ call điện thoại; ở dòng 183 agent dựng lại assistant message từ các call parse được. Model nhận lỗi JSON không gắn rõ hành động gốc rồi trả “Đã xong”, bỏ mục tiêu bước. Nên giữ thông tin hành động lỗi và trạng thái chờ sửa. Trường hợp 1563 chỉ có một call hỏng thì model tự sửa thành công. Không nên suy rộng rằng cả 5 lỗi JSON/schema đều gây mất điểm.
4. **Augmentation hiện tại không nhắm thẳng vào lỗi nổi bật.** 2.624/4.150 dòng chứa rename (~63,2%); có 214 dòng remove. Chưa có augmentation phản thực tế thay đổi số dư quanh ngưỡng, mưa/không mưa, ID nhất quán trong history/kết quả/target, thứ tự entity hoặc giờ hẹn và tái sinh nhãn đúng.
5. **Schema rút gọn bỏ một số thông tin.** `render_tool` không trình bày `returns`, `_param_str` không trình bày `x-ref`. Có thể làm khó hiểu quan hệ tool–ID ở app mới, nhưng lượt này chưa có ablation để quy lỗi hoặc ước lượng lợi ích. Đây là giả thuyết phụ, không kết luận chính.

Train dùng quỹ đạo gold; sau sai lầm, rollout quan sát phân bố khác, như tìm không ra người hoặc trả tiền thất bại. Đây phù hợp cơ chế lệch phân bố trong học bắt chước tuần tự. Công trình [Ross, Gordon & Bagnell, AISTATS 2011](https://proceedings.mlr.press/v15/ross11a.html) là cơ sở cho việc thu thập và dạy phục hồi trên trạng thái do policy tạo ra. Điều đó không chứng minh exposure bias giải thích toàn bộ lỗi ở đây, và không buộc phải chuyển ngay sang RL/DAgger đầy đủ. Có thể bắt đầu bằng ít ví dụ phục hồi được kiểm chứng, sinh từ **fit**, không đưa các nhãn dev vừa phân tích vào train.

## 5. Đánh giá các kết luận trước của Claude

| Kết luận trước | Đánh giá sau audit |
|---|---|
| SFT tăng mạnh, chạy train không lỗi | Đồng ý; tính lại điểm khớp. |
| Ưu tiên 51 execute có call đúng nhưng hash sai | Đồng ý, nhưng cần phân loại rộng hơn ID/ngày giờ. |
| Dev loss 0,023 mà điểm 54 | Cần đính chính: hai số dùng hai tập mẫu khác nhau; loss toàn dev là 0,0685. |
| Không chọn checkpoint theo loss | Nên chọn chính bằng rollout score, nhưng vẫn giữ loss toàn dev để chẩn đoán; không bỏ loss. |
| Tốc độ đã đủ | Mới chứng minh agent oracle-text trên 233 mẫu và 4070 chạy nhanh. Chưa bao gồm ASR/history audio, A30, app mới, backend vLLM, thời gian cold start. |
| 53,9 là trần của private | Là tham chiếu oracle-text trên dev_random, không phải cận trên toán học cho tập private khác phân bố. Có lý do kỳ vọng ASR/app mới làm khó hơn, chưa định lượng được. |
| Ép ID đã xuất hiện sẽ xử lý lỗi chọn ID | Chặn được ID bịa, không chặn chọn nhầm ID thật hoặc chọn trước khi đủ thông tin. |
| Tăng model/train thêm là bước hiển nhiên | Chưa đủ dữ liệu chọn; cần baseline đối chứng và checkpoint rollout. |

## 6. Trình tự thí nghiệm đề xuất

Chỉ là kế hoạch đánh giá tiếp theo; chưa chạy train hoặc sửa pipeline trong phiên audit này.

| Ưu tiên | Thí nghiệm cụ thể | Câu hỏi và tiêu chí |
|---|---|---|
| P0 | Đo loss toàn 233; rollout step_100, step_200, final với cùng cấu hình | Checkpoint nào thực sự tốt? So sánh theo cặp, cùng runtime/seed; báo score/hash/F1 theo loại. Full-dev final loss đã đo xong. |
| P1 | Thêm cơ chế pending action, xác nhận `done=false`, phục hồi JSON; giữ nguyên model | Tách phần mất điểm do orchestration khỏi năng lực model. Không đổi nhiều tầng cùng lúc. |
| P1 | Ablation tính toán có kiểu dữ liệu và kiểm điều kiện | Kiểm đúng nguồn dữ liệu/mốc giờ trước khi tính; so lỗi mới xuất hiện với lỗi được cứu. Con số 15+11 của nhóm 51 không phải điểm tăng đảm bảo. |
| P1 | Bộ đối chứng phản thực tế từ fit: đổi ID, đảo danh sách, số dư trước/sau ngưỡng, đủ/thiếu slot, sửa mốc giờ | Policy đổi hành động đúng khi điều kiện đổi, và giữ kết quả ngữ nghĩa khi chỉ đổi ID/thứ tự? Kiểm simulator và nhãn sau mọi biến đổi. |
| P2 | Cùng 1.7B: train thêm epoch đối chứng với thêm dữ liệu có mục tiêu; so bằng score | Tách lợi ích thêm compute khỏi lợi ích dữ liệu. Giữ checkpoint hiện tại và ghi rõ budget. |
| P2 | 4B trên cùng fit/dev và protocol, cùng báo cáo learning curve | Kiểm năng lực model có phải nút thắt; không train all rồi chấm dev đã xuất hiện trong train. |
| P2 | Train fit_lao và chấm dev_lao độc lập | Đo schema/app chưa thấy; không dùng checkpoint random hiện tại rồi gọi kết quả là unseen-app. |

Để tránh tự tối ưu quá mức 233 mẫu đã phân tích sâu, các ví dụ huấn luyện/biến đổi phải lấy từ fit và cần một tập kiểm tra độc lập hoặc cross-validation theo nhóm/template phù hợp. Không chọn ngưỡng, regex hay danh sách ID theo đáp án dev. Thành công trên random dev chưa đủ chứng minh khả năng private.

Đừng tăng learning rate/rank chỉ vì score còn thấp; đừng thêm thật nhiều rename mà không đo; đừng triển khai RL phức tạp trước khi kiểm chứng các nguyên nhân đơn giản. Ưu tiên hệ thống đo đúng và các thí nghiệm phân biệt được giả thuyết.

## Artifact và giới hạn

- `lifemate/runs/codex_loss_audit.json`: loss, token count, lỗi token theo từng dev sample.
- `lifemate/runs/codex_loss_audit.log`: log đo lại.
- `lifemate/runs/codex_loss_audit.py`: script đo lại final loss; chạy với `PYTHONPATH=lifemate` từ repo bằng venv hiện tại.
- `lifemate/runs/codex_error_audit.jsonl`: 120 mẫu lỗi, bao gồm dữ liệu train; giữ local.
- `lifemate/runs/codex_focus_51.md`: phân loại thủ công 51 mẫu trọng tâm.
- `lifemate/runs/codex_error_audit.py`: tái tạo bảng và kiểm tra đủ 51 ID, tính lại score.

Chưa chạy ablation can thiệp, checkpoint rollout trung gian, ASR, model 4B, leave-apps-out hay public submission. Chưa chứng minh mức tăng điểm của bất kỳ đề xuất nào. Các file TODO, code pipeline, checkpoint và prediction cũ giữ nguyên; báo cáo chưa commit/push.
