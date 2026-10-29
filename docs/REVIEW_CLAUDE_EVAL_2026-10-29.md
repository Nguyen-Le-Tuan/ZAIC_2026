# Review phiên Claude — evaluation protocol, 29/10/2026

Phạm vi: review code PR #2 ở HEAD `19ffe95bb026a5d0af728c23ac94e2f24a7beeeb`, tài liệu và artifact sẵn có. Chỉ kiểm tra CPU/read-only; không train, không chạy lại inference/loss GPU, không merge hay gửi comment GitHub. Người dùng cần tắt máy đi học; không khởi chạy A/B/C/D/E trong phiên này.

## Kết luận

Phiên Claude tạo ra tiến bộ hữu ích và các kết quả checkpoint được kiểm tra lại là đúng. Giữ final làm baseline hợp lý. Không cần train B ngay. Cần sửa một thiếu sót của cơ chế chấm mẫu thiếu và làm rõ thiết kế thí nghiệm/lockbox trước các lượt train mới.

## Bằng chứng được kiểm tra độc lập

Tính lại bằng scorer từ prediction thực tế và gold oracle đã lưu, không chỉ đọc file score:

| Run | N prediction duy nhất | Score |
|---|---:|---:|
| step_100 | 233 | 38,95054159 |
| step_200 | 233 | 52,46678929 |
| final cũ | 233 | 53,91626256 |
| final rerun | 233 | 53,91626256 |
| final probe-fit | 233 | 80,22072348 |

- Final cũ/rerun giống toàn bộ prediction ở 233/233 mẫu; output thô từng bước cũng giống 233/233. Có thể sử dụng kết quả này làm bằng chứng ổn định trên cấu hình HF/máy hiện tại. Không suy rộng sang ASR/vLLM/A30.
- Artifact full-dev loss đủ 233 dòng: step_100 0,079796689; step_200 0,069772234; final 0,068489255. Phiên review này đọc/kiểm artifact, không đo GPU lại.
- Probe-fit gồm toàn ID thuộc fit_random, đúng là tập đã train, không phải heldout.
- Trace mới có đúng 7 rollout chứa `done=false` ở cấp kết quả tool, không nhầm với trường `item.done=false` của reminder.
- train_0098: pay ở bước 1 (đánh số từ 0), sms ở bước 2. Model đã nhận kết quả thanh toán thất bại trước khi sinh SMS. Claude sửa chi tiết này đúng; không dùng 0098 làm bằng chứng lỗi batching.
- Journal hệ thống xác nhận lúc 08:26:59 theo giờ log: systemd-oomd kill scope của Claude, memory usage 6,6G, vì pressure ở user cgroup vượt ngưỡng. Con số này là cả scope, không phải riêng một tiến trình evaluation. Đo một lần khác 1,25GB không đủ loại trừ mọi đóng góp của evaluation trong lần bị kill.
- PR #2 mở, base agent-pipeline, head khớp checkout. Không có status checks trả về từ GitHub tại thời điểm review; các kiểm chứng mô tả là kiểm chứng local. JOURNAL/HUMAN_TODO/EVAL local không khác origin/main hiện có.
- Không thấy process LifeMate train/infer/eval hoặc unit train/eval đang chạy lúc kiểm tra.

## Phát hiện cần xử lý

### 1. [P2] Cơ chế “thiếu prediction tính 0” còn sai với gold rỗng

Vị trí tích hợp mới: `lifemate/scripts/eval_ckpt.sh:32-33`; nguyên nhân trong code scorer đã tồn tại: `lifemate/lifemate/scorer.py:120-124`.

Script nói dùng `--ids` thì mẫu thiếu prediction sẽ được tính 0. Nhưng scorer tạo prediction mặc định là `tool_calls=[]`, `state_hash=None`; nếu gold cũng rỗng, score_sample trả 1, call-F1 và hash_ok cũng được coi là đúng.

Đã tái hiện chỉ bằng CPU:

```python
from lifemate.scorer import evaluate
print(evaluate({}, {"missing_oos": {"tool_calls": [], "state_hash": "hash"}}, {}))
# score = 100.0, call_f1 = 100.0, hash_acc = 100.0
```

Mẫu vắng mặt khác với một dòng prediction thực sự nộp danh sách call rỗng. Cần phân biệt hai trường hợp: hoặc từ chối file thiếu ID ở wrapper, hoặc explicit score 0 cho ID bị thiếu theo protocol local. Đồng thời kiểm unknown/duplicate IDs để mẫu số không im lặng thay đổi. Thêm regression test cho missing execute, missing out-of-scope và explicit empty hợp lệ.

Đây là thiếu sót của scorer cũ mà cơ chế mới đang dựa vào, không phải bằng chứng Claude làm hỏng score hiện tại. Cả năm run đã kiểm đều đủ 233 prediction duy nhất nên lỗi này không thay đổi các điểm trong bảng.

### 2. Lockbox lấy từ fit không độc lập với checkpoint hiện tại

Vị trí: `docs/EVAL_2026-10-29.md:181-192`. Đề xuất bỏ khoảng 200 mẫu khỏi fit của các thí nghiệm mới có thể dùng được, nhưng cần thêm điều kiện bắt buộc:

- Chốt lockbox và loại toàn bộ ví dụ/augmentation dẫn xuất của nó khỏi tập huấn luyện cho mọi candidate được đánh giá trên lockbox.
- Train lại baseline và candidate từ base model chưa SFT trên lockbox; không warm-start từ final hiện tại đã học các mẫu này.
- Không dùng final 53,92 hoặc A train trên fit cũ làm đối chứng trên lockbox rồi gọi chênh lệch là generalization gain.
- Theo dõi lineage của dữ liệu synthetic; nếu có thể, chia theo nhóm gần trùng/template trước khi augment.

Không có thao tác chia file nào khiến checkpoint cũ “quên” dữ liệu đã học. Nhận xét này bổ sung điều kiện còn thiếu trong đề xuất của Claude, không phủ nhận việc có thể lập một holdout mới cho các model train lại đúng protocol.

Nếu chưa sẵn sàng train lại baseline, tiếp tục gọi dev_random là tập phát triển đã được phân tích, dùng cross-validation/holdout cho thí nghiệm tương lai; không đổi tên một phần fit thành “kiểm tra kín” rồi sử dụng với model cũ.

### 3. Thí nghiệm B cần cách diễn giải thận trọng hơn

Vị trí: bảng mục 5.3, dòng B. Chạy fit_lao → dev_lao là phép đo cần thiết. Nhưng ngưỡng “thấp hơn dev_random >=15 điểm thì ưu tiên app synthetic hơn mọi thứ khác” chưa đủ căn cứ: hai tập khác mẫu, cơ cấu app/task/history và độ khó. Chênh lệch đó không tách riêng hiệu ứng unseen-app.

Nên ghi rõ B đo hiệu năng trên protocol held-out-app này; kèm zero-shot cùng dev_lao và lát cắt, chưa tuyên bố mức giảm nhân quả do app mới. Nếu cần so seen/unseen để quyết định đầu tư lớn, thiết kế các fold/control thích hợp với tập đánh giá chung hoặc tương xứng và train sạch khỏi các mẫu đánh giá.

Kiểm tra mới: **225/262 ID của dev_lao nằm trong fit_random cũ**. Vì thế không dùng final hiện tại chấm dev_lao rồi gọi đó là đối chứng seen-app sạch; kết quả ấy bị nhiễm do đã train trên mẫu đánh giá. Claude hiện mới đề nghị final/dev_random làm tham chiếu, không báo đã chạy phép đối chứng nhiễm này; con số trên là cảnh báo cụ thể cho thiết kế tiếp theo.

## Những diễn giải nên hạ mức khẳng định

- **80,22 train vs 53,92 dev:** bằng chứng rõ về khoảng cách hiệu năng trên hai tập hiện có. Chưa tách được memorization, khó khăn về history, chất lượng dữ liệu hay capacity. Không đủ để kết luận history dài “không phải nút thắt”: model có thể nhớ trường hợp đã train mà vẫn suy luận kém với history mới. Không bị cắt vì giới hạn token chỉ loại trừ truncation.
- **Final vs step_200:** giữ final làm baseline, nhưng “chưa có bằng chứng khác biệt rõ” không đồng nghĩa “đã chứng minh tương đương”.
- **A 2 epoch:** kéo dài tổng steps cũng thay đổi cosine schedule và warmup tuyệt đối theo code hiện tại. Có thể đánh giá cả cấu hình train 2 epoch như một phương án thực dụng; không tuyên bố đã cô lập duy nhất số lần nhìn dữ liệu. Nên thay “H1/H2 đúng” bằng “kết quả ủng hộ giả thuyết…”.
- **Ranh giới hỏi lại 12,7 điểm, done=false 3 điểm:** là điểm đang mất trên nhóm có biểu hiện đó và trần thô theo phạm vi nhóm, không phải uplift đã chứng minh. Lỗi hỏi lại có thể do sai retrieval/history trước đó; chỉ tăng xu hướng hỏi lại sẽ làm nhóm hỏi thừa nặng hơn. Các nhóm chồng lấn, không cộng lợi ích.
- **Giới hạn RAM/systemd:** tách unit giúp cô lập vòng đời và giới hạn tài nguyên, không bảo đảm tuyệt đối các app khác không bị oomd kill khi toàn máy còn áp lực. Không suy từ RSS/cgroup ở một lượt chạy mới ra nguyên nhân duy nhất của lượt cũ. Dù vậy, không có bằng chứng hiện tại yêu cầu chạy thêm test RAM trước khi người dùng tắt máy.

## Đề nghị quyết định hôm nay

1. Không chạy B hoặc bất kỳ train/eval GPU nào lúc này; không lên lịch tự chạy thay người dùng.
2. Giữ final, giữ toàn bộ artifact; không cần chạy lại checkpoint để xác minh thêm các điểm vừa đối chiếu.
3. Chưa merge PR #2 trước khi sửa/kiểm regression cho missing prediction. Sau đó review theo thứ tự PR #1 và PR #2 phụ thuộc, không merge vượt PR nền.
4. Phiên tới có thể sửa scorer/evaluation và thiết kế protocol bằng CPU trước. B là phép đo hữu ích khi người dùng sẵn sàng, không phải việc bắt buộc phải train ngay hôm nay.

## Nội dung ngắn gửi lại Claude

> Mình chưa chạy B/A hay bất kỳ train/eval GPU nào vì cần tắt máy đi học. Giữ final làm baseline. Codex đã tính lại điểm từ prediction và xác nhận rerun 233/233. Trước lượt train mới, xử lý lỗi missing prediction của mẫu ngoài phạm vi đang bị scorer cho 1; bổ sung test explicit-empty khác missing-ID. Làm rõ lockbox: mọi model so trên lockbox phải train lại mà không từng học các mẫu/augmentation đó; không dùng checkpoint final cũ làm đối chứng sạch. B đo held-out-app nhưng chênh với dev_random không cô lập tác động app mới; bỏ quyết định cứng dựa riêng vào ngưỡng -15 điểm. dev_lao hiện có 225/262 mẫu thuộc fit_random cũ, nên không dùng final cũ trên dev_lao làm control sạch. Chỉ sửa/kiểm CPU và cập nhật kế hoạch; chờ mình quay lại rồi quyết định chạy train. Chi tiết ở docs/REVIEW_CLAUDE_EVAL_2026-10-29.md.
