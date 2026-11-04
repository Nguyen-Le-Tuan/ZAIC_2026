# Chiến lược nâng điểm hệ thống 4B — 04/11/2026

## 1. Tóm tắt

- **Mục tiêu 80 public bằng SLM trước 16/11 hiện có xác suất thấp.** Từ 46,29 cần +33,71 điểm public; bản API mạnh hơn trên cùng pipeline cũng chỉ đạt 75,52 public. Đây không phải chứng minh bất khả thi, nhưng không có phép đo nào hiện tại cho thấy một thay đổi đơn lẻ đủ lớn.
- Trên 80 mẫu dev chung, 4B đạt 39,10, API `xhigh` + bỏ tham số hiếm đạt 64,75: Δ **+25,65** [95% CI +14,43; +36,90]. Phân loại một nguyên nhân chính cho mỗi mẫu cho thấy **quyết định làm/hỏi/bỏ qua** chiếm +10,59 điểm của chênh lệch; **chọn ID thực thể** +5,00. Đây là mô tả của 80 mẫu, không phải dự báo mức tăng khi sửa 4B.
- ASR làm 4B giảm **12,98 điểm** trên 495 lượt dev: chữ chuẩn 59,15 → chữ ASR 46,17 [Δ −16,57; −9,58]. Ngay cả ASR hoàn hảo, 4B hiện tại vẫn còn khoảng 20,85 điểm dưới mốc 80 nếu lấy dev làm thước tham chiếu.
- Việc nên làm đầu tiên: **(1)** một lượt 4B `fit_lao` với prompt thể hiện `x-ref` và kết quả tool đọc, giữ train/infer cùng prompt; **(2)** kiểm tốc độ A30 và thử nhỏ model Thinking trước khi dành cả đêm train; **(3)** chấm 4B với transcript PhoWhisper fine-tune đã có để xác định ASR còn tăng được không.
- Chưa nên chi tiền API để sinh lô lớn: pilot 280 mẫu synthetic làm dev_lao ASR giảm 2,09 điểm; sổ chi còn **6,97 USD** tới trần 50 USD. Luật bỏ tham số hiếm replay trên 4B cũng giảm 0,26 điểm; không bật cho Docker.

## 2. Số liệu đã kiểm lại và cách tái lập

Phân tích dùng mã `origin/api-agent` tại `1e504bd` trong worktree `~/zac-codex`, script `lifemate/scripts/codex_4b_analysis.py`; dữ liệu/run sẵn có ở `~/zac-c3` và `~/zac-docker`. Không dùng GPU, API, package mới hay đọc `*_environment/`. Lệnh đã chạy (mỗi lệnh dưới 3 giây; `CUDA_VISIBLE_DEVICES=''`):

```bash
cd ~/zac-codex/lifemate
for q in paired asr replay schema cost public; do
  CUDA_VISIBLE_DEVICES='' .venv/bin/python scripts/codex_4b_analysis.py "$q"
done
CUDA_VISIBLE_DEVICES='' .venv/bin/python -m lifemate.compare \
  ~/zac-c3/lifemate/runs/sft_q4b4_fit_lao_asrturboft \
  ~/zac-c3/lifemate/runs/sft_q4b4_fit_lao_synth_w1_asrturboft \
  --ids ~/zac-c3/lifemate/splits/dev_lao.txt
CUDA_VISIBLE_DEVICES='' .venv/bin/python scripts/loss_breakdown.py \
  /home/truyen-anh-thach/zac-c3/lifemate/runs/sft_q4b4_fit_lao_asrturboft.jsonl@/home/truyen-anh-thach/zac-docker/lifemate/runs/pilot40_dev_lao.txt \
  --root ~/zac-c3/data/train+public_test
```

`loss_breakdown.py` được chạy tương tự cho 4 tổ hợp 4B/API × dev_random/dev_lao (đúng file ID 40 tương ứng). Mọi điểm dev dưới đây lấy từ `_rows.jsonl` có thể chấm lại bằng `lifemate.scorer`; trace và dự đoán chỉ dùng trên **train**. Bootstrap theo cặp 10.000 lần, seed 0. Các file public chỉ đếm tổng hợp; 46,29 và 75,52 là điểm Anh báo từ bảng xếp hạng trong `JOURNAL.md` entries 76 và 80, **không thể chấm lại local vì public không có nhãn**.

| Kiểm tra | Kết quả | Nguồn |
|---|---:|---|
| Dev 4B chữ chuẩn: random / lao | 65,61 (n=233) / 53,40 (n=262) | `~/zac-c3/lifemate/runs/sft_q4b4_fit_{random,lao}_rows.jsonl` |
| Dev 4B chữ ASR: random / lao | 54,01 (n=233) / 39,20 (n=262) | Cùng prefix, hậu tố `_asrturboft_rows.jsonl` |
| Gộp hai lượt dev, chữ chuẩn / ASR | 59,15 / 46,17 (n=495 lượt) | Hai cặp file trên |
| Pilot 80, 4B / API `xhigh_drop` | 39,10 / 64,75 (40+40) | `_rows.jsonl` ở `~/zac-c3/lifemate/runs/` và `~/zac-docker/lifemate/runs/`; ID ở `pilot40_dev_*.txt` |
| Pilot synthetic, dev_lao ASR | 39,20 → 37,12 (n=262), Δ −2,09 [−7,22; +3,01] | `sft_q4b4_fit_lao{,_synth_w1}_asrturboft_rows.jsonl` |
| App chỉ có ở catalog public | 11; có cài ở 410/634 mẫu | `train_tools_catalog.json`, `public_test_tools_catalog.json`, `public_test.jsonl`; chỉ đếm `installed_apps` |

**Hai chỗ dễ tính sai:** `dev_random` và `dev_lao` trùng **37 ID**, nhưng mỗi lượt dùng adapter khác; phải gộp 495 cặp `(split, id)`, không ghi đè theo ID để còn 458 mẫu. Và `scripts/loss_breakdown.py` nằm dưới `lifemate/scripts/`; chạy từ `lifemate/` với venv, truyền `--root` trỏ tới `~/zac-c3/data/train+public_test`. Số brief về điểm dev và 80 mẫu khớp sau khi xử lý hai điều này.

## 3. Q1 — API hơn 4B ở đâu?

Đối chứng dùng cùng chữ Whisper-turbo fine-tune, prompt và vòng lặp agent. Metadata cho thấy 4B HF có `time_budget=60`, API có `900` và dùng luật bỏ tham số hiếm; trên 80 trace **không bên nào dừng vì hết thời gian**. Vì vậy đây là so sánh pipeline thực tế, nhưng không phải ablation thuần một biến về trọng số model.

| Tập, n | 4B | API `xhigh_drop` | Δ theo cặp, CI 95% | API thắng / 4B thắng / hòa |
|---|---:|---:|---:|---:|
| dev_random, 40 | 51,04 | 62,44 | +11,40 [−2,92; +26,08] | 12 / 7 / 21 |
| dev_lao, 40 | 27,16 | 67,06 | +39,90 [+23,79; +55,52] | 22 / 3 / 15 |
| Gộp, 80 | 39,10 | 64,75 | **+25,65 [+14,43; +36,90]** | 34 / 10 / 36 |

Trên **API minimal không bỏ tham số**, 4B lại hơn 4,25 điểm ở dev_random (51,04 so với 46,79; n=40; CI của API−4B [−18,42; +9,63]). Việc tăng effort và bỏ tham số làm đảo chiều trên 40 mẫu đó; không nên gọi mọi khác biệt là “năng lực suy luận” của model. Trong pilot `xhigh`, nhóm gold execute có n=69, ask n=9, OOS n=2; các nhóm ask/OOS quá nhỏ để suy rộng.

**Bảng phân bổ chênh lệch +25,65 điểm trên 80 mẫu.** Tôi đối chiếu 44 cặp khác điểm bằng call, tham số, hash, lý do dừng và từng bước trace, rồi gán **một nguyên nhân chính** cho mỗi cặp. Cột âm là nơi 4B hơn API; tổng cột ròng đúng bằng Δ chung. Mẫu có nhiều lỗi chỉ được tính một lần, nên đây là attribution mô tả có yếu tố phán đoán, không là lợi ích nhân quả của việc sửa riêng từng lỗi.

| Nguyên nhân chính | API thắng (mẫu; điểm/80) | 4B thắng (mẫu; điểm/80) | Ròng |
|---|---:|---:|---:|
| Quyết định làm / hỏi / bỏ qua | 11; +11,14 | 1; −0,56 | **+10,59** |
| Chọn ID thực thể từ history/kết quả đọc | 4; +5,00 | 0; 0 | **+5,00** |
| Chọn tool hoặc bước ghi | 4; +3,42 | 2; −1,56 | +1,86 |
| Bước đọc thừa / thiếu | 4; +2,97 | 0; 0 | +2,97 |
| Thời gian | 3; +2,81 | 0; 0 | +2,81 |
| Tham số khác | 5; +5,63 | 5; −3,96 | +1,67 |
| Nội dung fuzzy | 3; +1,75 | 2; −1,00 | +0,75 |
| **Tổng** | **34; +32,73** | **10; −7,08** | **+25,65** |

Ví dụ chỉ nêu ID: `train_1104` đổi từ làm sang hỏi đúng; `train_0869` đổi ID sau bước đọc; `train_1504` bỏ được một call đọc thừa. Phía 4B thắng có `train_0720` vì API thêm tham số tùy chọn và `train_0705` vì API thêm thao tác ghi làm sai hash. `loss_breakdown.py` xác nhận 4B dev_lao pilot mất 20,00 điểm ở nhóm “hash sai, F1=0” và 16,73 điểm ở “hash sai dù F1>0”; API tương ứng 2,50 và 5,58. Các nhóm loss này là chẩn đoán bổ sung, **không cộng** với bảng attribution.

Trên public chỉ so tổng hợp: file 4B có 634 dòng, 1.507 call, 53 dòng rỗng, 90 dừng hỏi; API `xhigh_drop` có 634 dòng, 1.813 call, 36 dòng rỗng, 110 dừng hỏi. Không suy nhãn hoặc quy tắc từ bất kỳ dự đoán public nào.

**Kết luận, độ chắc chắn vừa:** khác biệt lớn nhất trong pilot là quyết định hành động và theo ID, đặc biệt ở dev_lao. CI chung cho thấy hướng hơn khá rõ; bảng nguyên nhân chỉ có n=80 và nhiều lỗi đồng thời, nên không dùng các ô làm dự báo điểm tăng.

## 4. Q2 — Vì sao 4B kém khi gặp app chưa thấy?

Trong dev_lao toàn bộ, lát cắt theo **app của call gold** như script pilot cũ cho 4B ASR **34,84 trên n=183** dùng một trong sáu app giữ riêng, so với **49,31 trên n=79** còn lại; chữ chuẩn là 51,90 và 56,88. Chênh lệch giữa hai lát cắt không tự chứng minh nguyên nhân app: loại yêu cầu và độ khó cũng khác. Trên pilot 40 dev_lao, API hơn 4B cả n=26 có call gold ở app giữ riêng (+30,61) lẫn n=14 còn lại (+57,14); hai lát cắt quá nhỏ để suy kết luận app riêng.

Audit `prompt.render_tool` với catalog:

| Catalog | Tool / tham số | Metadata có trong catalog nhưng không thể hiện rõ trong prompt | Metadata đã thể hiện |
|---|---:|---|---|
| train | 147 / 246 | `x-ref`: 68 tham số; `returns` không rỗng: 70 tool | 32 enum; 6 `x-one-of`; mô tả tham số có ở 167 |
| public_test | 122 / 219 | `x-ref`: 61; `returns` không rỗng: 62 | 27 enum; 5 `x-one-of`; mô tả tham số có ở 151 |

Catalog không có trường ví dụ cho tham số. Mô tả bằng chữ **có thể** đã gợi ý ID/kết quả đọc, nên không thể khẳng định 68 `x-ref` bị mất toàn bộ thông tin. Chốt chặn ID của agent vẫn dùng metadata `x-ref`; phần thiếu là tín hiệu tường minh cho model để lập đường read→write. SFT gọi cùng `build_system`, nên mọi sửa prompt phải đồng bộ train/infer.

**Phép thử rẻ nhất để phân biệt giả thuyết:**

1. **Thông tin prompt:** thêm một đoạn ngắn cho tham số `x-ref` nêu collection tham chiếu và tóm tắt `returns` cho tool đọc; chỉ nối với tool đọc cụ thể nếu catalog cho phép xác định chắc chắn, giữ nguyên enum/`x-one-of`. Chạy inference với adapter cũ trên 40+40 để đo hiệu ứng prompt thuần, rồi train `fit_lao` với prompt mới để loại sai khác train/infer. Nếu chỉ bản đã train tăng, vấn đề là tương tác prompt–SFT.
2. **SFT học thuộc app:** so model gốc Qwen3-4B-Instruct-2507 với đúng adapter `fit_random` trên dev_random và `fit_lao` trên dev_lao, cùng prompt mới, 40 mẫu mỗi tập. Model gốc hơn riêng app giữ riêng còn SFT hơn app đã thấy là bằng chứng gợi ý học thuộc, chưa chứng minh vì recipe/prompt khác.
3. **Giới hạn năng lực:** nếu prompt đủ thông tin và SFT khớp prompt vẫn kém, nhưng API cùng transcript tốt hơn, thử model Thinking dưới 5B trong hạn thời gian. Không kết luận “4B không đủ sức” trước phép thử này.

**Kết luận, độ chắc chắn vừa cho hiện tượng, thấp cho nguyên nhân:** có khoảng trống tổng quát hóa, nhưng chưa tách được prompt, SFT và model bằng các run đã có. Ưu tiên ablation prompt một biến, tránh sửa cùng lúc chính sách hỏi lại và dữ liệu train.

## 5. Q3 — Distillation từ API có đáng làm?

Pilot `lao_w1` sinh 280/384 mẫu đạt (n=280; `~/zac-synth/lifemate/gen/`, `JOURNAL.md` entry 61), rồi train 4B: dev_lao chữ ASR **39,20 → 37,12**, Δ −2,09 [−7,22; +3,01]; chữ chuẩn **53,40 → 50,57**, Δ −2,83 [−7,93; +2,35]. Call-F1 ASR giảm 51,41 → 47,81 trong khi hash đúng tăng 51,53% → 53,44%: bộ sinh có thể tạo hành động làm đúng state nhưng không đúng **quy ước call** của nhãn. Pilot còn lệch phân bố: 90% mẫu sinh mở đầu bằng read, câu thật 59% (`JOURNAL.md` entry 61). “Solver” độc lập cũng chỉ đối chiếu state và write/ask; nó không bảo đảm điểm F1 call cao.

Đọc `lifemate.synth`: API tạo `state_json` cho mẫu tổng hợp từ catalog, mã simulator và context mẫu **fit**; `simulate()` chạy trên state ấy. Nó không lấy state từ `*_environment/`. Với mẫu train thật, `ToolEnv("train", id)` cung cấp môi trường gốc để chạy teacher. Không dùng audio, transcript hay dự đoán public làm đầu vào teacher.

**Thiết kế pilot nếu Claude/Anh muốn tiếp tục:** chọn 40 ID chỉ từ 1.087 mẫu train ngoài cả hai dev; teacher chạy trên transcript train và `ToolEnv` thật, lưu trajectory. Chỉ nhận trajectory nếu cùng hash **và** `lifemate.scorer` cho điểm 1 so với nhãn train; audit tay các call read/write/ask và các ca teacher khác nhãn. Với mẫu tổng hợp từ catalog public, tạo state giả theo `synth.py`, kiểm simulator, rồi audit thêm quy ước call với các analog trong train; không nhận chỉ vì state đúng. So SFT pilot với đối chứng nhân bản số dòng train thật và cùng số bước. Luật giữ trước: dev_lao ASR ≥+2, dev_random ≥−1, ask không giảm quá 3 điểm; không đạt thì dừng.

Sổ `~/zac-docker/lifemate/gen/*usage.jsonl` cộng **43,03/50 USD**, còn **6,97 USD**. API `xhigh` pilot dùng 1,92 USD/80 mẫu ≈0,024 USD/mẫu; 40 mẫu train ước 0,96 USD trước hao phí. Sinh synthetic `lao_w1` tốn 11,55/280 ≈0,041 USD/mẫu đạt; 100 mẫu mới khoảng 4,13 USD nếu tỷ lệ giữ như cũ. Hai con số này là **ước từ sổ cũ**, không phải báo giá bảo đảm. Đặt trần pilot 1,25 USD; chỉ mở rộng trong phần còn lại sau audit và luật giữ, vượt 50 USD tổng phải hỏi Anh. **Không khuyến nghị chi ngay:** train đã có nhãn, teacher chỉ thêm giá trị nếu tìm được trajectory đúng quy ước nhưng có ích hơn SFT hiện tại. Độ chắc chắn thấp.

## 6. Q4 — Thinking trong hạn 25 giây

[Qwen3-4B-Thinking-2507](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507) ghi 4,0B tham số, Apache-2.0, chỉ hỗ trợ thinking; [QwenLM](https://github.com/QwenLM/Qwen3) ghi phát hành mở ngày 06/08/2025, trước mốc 26/10/2026. [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) bản hybrid cũng 4,0B, Apache-2.0, có thinking bật/tắt. Ghép với ASR khoảng 0,8B trong brief thì tổng khoảng 4,8B, nằm dưới 6B theo **số tham số**, nhưng Docker và licence toàn hệ thống vẫn cần leader xác nhận. Card không chứng minh latency A30 hay điểm LifeMate.

Đo lại `e2e_public_q4b_all_trace.jsonl` (n=634, chỉ dùng **thống kê tốc độ**, không dùng dự đoán): thời gian agent+ASR trung bình 9,10 giây, p95 **18,73** trên laptop; 1.848 bước sinh trung bình 30,4 token/bước, tokenizer local cho khoảng **11,0 token/giây** ở các bước đủ dài. 25−18,73 ≈6,27 giây dư ở p95; nếu tốc độ và số bước **không đổi**, tương đương khoảng **69 token suy luận thêm/mẫu**, hay khoảng **23 token/bước** với gần 3 bước. Đây là ước bảo thủ cho laptop, **không phải số đo A30**. A30 bf16 có thể khác nhiều; model Thinking có thể tiêu hết `max_tokens` trước khi sinh `<tool_call>`.

Đề xuất preflight trên A30: 20 mẫu train không thuộc dev, `max_tokens` 128 rồi 256, ghi tổng thời gian ASR+agent, p95/max, số bước không sinh call và điểm hợp lệ; chỉ chạy 40+40 dev nếu không quá 25 giây/mẫu và call hợp lệ ≥95%. Chạy zero-shot trước; LoRA của Instruct không được coi là đã xác thực trên backbone Thinking. Nếu p95 không đạt, dừng hướng này để giữ thời gian Docker. Độ chắc chắn cao về card và phép tính laptop, **chưa biết** hiệu quả/tốc độ A30.

## 7. Q5 — ASR còn đáng đầu tư?

| So cùng adapter, cùng ID | Chữ chuẩn | Whisper-turbo-ft | Δ ASR−chuẩn, CI 95% |
|---|---:|---:|---:|
| dev_random, n=233 | 65,61 | 54,01 | −11,60 [−16,67; −6,75] |
| dev_lao, n=262 | 53,40 | 39,20 | −14,20 [−19,20; −9,27] |
| Gộp 495 lượt | 59,15 | 46,17 | **−12,98 [−16,57; −9,58]** |

Nguồn: `~/zac-c3/lifemate/runs/sft_q4b4_fit_{random,lao}{,_asrturboft}_rows.jsonl` cùng prediction JSONL; `codex_4b_analysis.py asr`. Trên dev_lao, nhóm call gold thuộc app giữ riêng n=183 mất **17,07** điểm do ASR (51,90→34,84); nhóm còn lại n=79 mất **7,57** (56,88→49,31). Đây là tương tác quan sát được, chưa chứng minh ASR tự nó tệ hơn cho app lạ.

Trong các call gold **khớp ở bản chữ chuẩn rồi mất khớp ở bản ASR**, có 73 trường hợp call/tool biến mất; trong các call cùng tên còn lại, key đổi nhiều nhất: `query` 15, `content` 11, `start` 6, `time` 5, `title` 5, `date_from`/`date_to` mỗi loại 2, ID lẻ tẻ. Đây là **số lần key trong call**, không là số mẫu hay chứng cứ trực tiếp ASR nghe sai tên riêng/số: model có thể đổi kế hoạch từ một transcript khác. Cần audit audio/transcript ở train để phân biệt lỗi nhận dạng tên riêng, số và lỗi agent suy luận.

PhoWhisper fine-tune có file transcript `asr/train_dev_{random,lao}_phoft.jsonl`, nhưng **không có rollout 4B Pho-ft cùng điều kiện**. Vì vậy chưa có số đo cho 4B để khẳng định đổi ASR thắng; các lượt 1.7B trong `JOURNAL.md` entry 52 đã chọn turbo-ft. Chấm Pho-ft trên 4B hiện tại là phép thử khoảng 2–3 giờ GPU, rẻ hơn một lượt train. Luật giữ: điểm gộp ASR ≥46,17+1,0, dev_lao không giảm >1,0 và latency A30 còn đạt. Độ chắc chắn cao về headroom 12,98, thấp về phương án ASR cụ thể.

## 8. Q6 — Luật tất định cho 4B

Replay từ **1.087 mẫu train ngoài cả hai dev** tạo 23 luật bỏ tham số tùy chọn có tần suất điền <5% và ít nhất 5 call (`lifemate.rare_params`). Lọc call của 4B đã ghi rồi phát lại trên `ToolEnv("train", id)` mới, chấm bằng `lifemate.scorer`; đây là replay trajectory tĩnh, không cho model sinh lại sau khi kết quả tool đổi.

| Tập | Mẫu/call đổi | Điểm trước → sau | Δ, CI 95% |
|---|---:|---:|---:|
| dev_random, n=233 | 4 / 4 | 54,01 → 53,80 | −0,21 [−1,29; +0,64] |
| dev_lao, n=262 | 5 / 5 | 39,20 → 38,90 | −0,31 [−1,22; +0,38] |
| Gộp, n=495 lượt | 9 / 9 | **46,17 → 45,91** | **−0,26 [−0,95; +0,28]** |

Hai mẫu tốt hơn, ba kém hơn, 490 không đổi. Trên 495 lượt không có call đọc **trùng hệt** trong prediction để khử; mọi `sys.ask_missing_info.params` của 4B đã có đúng một mục. Các luật “khử đọc trùng” và “chuẩn hóa độ dài params hỏi lại” vì thế cho Δ=0 trên run này. **Không có luật tất định đã đo nào đáng bật thêm cho 4B.** Luật thời gian/ID mới phải rút từ fit và replay trên dev trước khi đề xuất triển khai; đặc biệt không được sửa call dựa vào hash gold hoặc nhãn dev lúc suy luận. Độ chắc chắn cao cho ba phép kiểm này, chưa có bằng chứng cho luật khác.

## 9. Q7 — Ưu tiên trước 16/11

Các khoảng tăng dưới đây là **dải lập kế hoạch chủ quan trên dev gộp**, không phải số đã đo và **không cộng được** vì các lỗi chồng nhau. Giữ/bỏ dùng điểm ASR theo cặp trên cùng ID; mọi lần chạy báo CI, nhóm ask/execute và latency. Chi phí laptop lấy từ các lượt 4B trong `JOURNAL.md` (train ~5,5–6 giờ, mỗi dev ~1,2 giờ); A30 chưa đo.

| # | Đề xuất | Dải Δ dev gộp trước đo | Chi phí (GPU laptop / USD / người) | Rủi ro | Luật giữ/bỏ viết trước | Ai chạy | Phụ thuộc |
|---|---|---|---|---|---|---|---|
| 1 | Prompt `x-ref` + kết quả read, train/infer đồng bộ; chỉ một thay đổi prompt | −2 đến +5 | ~6–8 giờ/lượt fit_lao; 0 USD; ~3 giờ code/audit | Prompt dài, lệch SFT, mất ask | Qua cửa 1: dev_lao ASR ≥+2, sạch ≥−2, ask ≥−3; qua cửa 2: gộp 495 ASR ≥+1 và mỗi split ≥−2 | Claude | Mã `prompt.py`, SFT mới, GPU rảnh |
| 2 | Chấm 4B với transcript Pho-ft sẵn có | −2 đến +3 | ~2–3 giờ; 0 USD; <1 giờ | ASR khác nhưng agent không hợp | Gộp ASR ≥+1 so 46,17; dev_lao ≥−1; latency đạt | Claude | Run 4B hiện tại, file Pho-ft |
| 3 | Smoke A30 Qwen3-4B-Thinking/hybrid trước mọi train | −5 đến +8 nếu khả thi | ~1–2 giờ A30 smoke, sau đó ~6–8 giờ/lượt nếu train; 0 USD; ~2 giờ | Thinking quá thời gian, không ra call | Không thử train nếu bất kỳ mẫu >25 giây hoặc valid-call <95%; chỉ giữ nếu gộp dev ≥+2 sau SFT, không split nào <−2 | Claude/leader | A30, model hợp licence, Docker |
| 4 | Teacher pilot nhỏ, kiểm đủ hash **và** F1 call | −3 đến +5 | ~6–8 giờ nếu train; ≤6,97 USD tổng còn lại; ~4 giờ audit | Pilot trước −2,09; teacher khác quy ước | Audit ≥95% accepted đúng chính sách; dev_lao ASR ≥+2, dev_random ≥−1, ask ≥−3; không đạt thì dừng API | Claude sau khi Anh chốt chi | Kết quả #1, hạn chi API |
| 5 | Đóng Docker và đo offline A30 | 0 điểm kỳ vọng trực tiếp | 2–3 ngày cuối; 0 USD | Mất bài vì timeout/OOM/không tái lập | 0 lỗi format/hash, 5/5 chạy giống nhau, mọi mẫu <30 giây và ngân sách nội bộ ≤25 giây | Leader/Claude | Adapter và ASR cuối |

**Đánh giá khả thi:** để đạt 80 theo thước dev, 4B ASR hiện tại cần khoảng +33,83. ASR hoàn hảo theo số đo chỉ bù 12,98; phần agent còn cần khoảng +20,85. API `xhigh` hơn 4B 25,65 trên pilot nhưng chính API public chỉ 75,52, và không thể chuyển toàn bộ lợi thế ấy sang 4B bằng SFT trong vài ngày. Với 6–8 lượt GPU còn lại và 2–3 ngày Docker, tôi đánh giá **vượt 80 trước 16/11 là rất khó**; nên tối ưu theo các cổng dev đã định, không thay mục tiêu điểm thành lý do dùng nhãn public. Rủi ro lớn nhất là tổng quát hóa sang app chưa thấy cùng ASR nhiễu; rủi ro vận hành là 25 giây A30 chưa được chứng minh.

### Thí nghiệm nên chạy đêm nay

Ưu tiên **#1** vì Q1 gợi ý vấn đề read→ID và audit thấy metadata có thể bổ sung; không trộn thêm dữ liệu synthetic hoặc đổi ASR trong cùng lượt. Claude sửa `prompt.render_tool` để (i) in ngắn `x-ref` cho tham số ID và (ii) in `returns` cho tool read, có giới hạn độ dài; không đổi luật, schema hay chat template khác. Sau khi review prompt của vài mẫu **train** và kiểm `scripts/check_sft.py`, chạy với tag mới, không ghi đè run cũ:

```bash
cd ~/zac-c3/lifemate
.venv/bin/python -m lifemate.sft --fit splits/fit_lao.txt \
  --drop-apps splits/heldout_apps.json --out sft/fit_lao_xref.jsonl
.venv/bin/python -m lifemate.sft --fit splits/dev_lao.txt \
  --out sft/dev_lao_xref.jsonl
.venv/bin/python -m lifemate.train --model Qwen/Qwen3-4B-Instruct-2507 \
  --load-4bit --optim adamw8bit --max-len 6144 --data sft/fit_lao_xref.jsonl \
  --eval-data sft/dev_lao_xref.jsonl --epochs 1 \
  --out ckpt/q4b4_fit_lao_xref --state-every 10
.venv/bin/python -m lifemate.infer --split train --ids splits/dev_lao.txt \
  --text asr --asr-file asr/train_dev_lao_turboft.jsonl --backend hf \
  --model Qwen/Qwen3-4B-Instruct-2507 --load-4bit \
  --adapter ckpt/q4b4_fit_lao_xref/final --time-budget 60 \
  --out runs/sft_q4b4_fit_lao_xref_asrturboft.jsonl \
  --trace runs/sft_q4b4_fit_lao_xref_asrturboft_trace.jsonl
.venv/bin/python -m lifemate.scorer runs/sft_q4b4_fit_lao_xref_asrturboft.jsonl \
  --split train --ids splits/dev_lao.txt \
  --rows runs/sft_q4b4_fit_lao_xref_asrturboft_rows.jsonl
.venv/bin/python -m lifemate.compare \
  runs/sft_q4b4_fit_lao_asrturboft runs/sft_q4b4_fit_lao_xref_asrturboft \
  --ids splits/dev_lao.txt
```

Chấm thêm chữ chuẩn với cùng adapter trước khi qua cửa 1. Nếu đạt, lặp đúng prompt/recipe trên `fit_random` → `dev_random`, rồi mới tính gộp 495 lượt. `JOURNAL.md` entries 61 và 67–70 cho thấy cả synthetic và chữ trộn từng giảm điểm; không lặp lại chúng trong thí nghiệm này.

## 10. Câu hỏi cho Claude và Anh; giới hạn

1. Claude: A30 có lịch trống cho smoke Thinking và kiểm Docker trước 13/11 không? Máy anh trai Anh đang train model/recipe nào để tránh lặp cùng giả thuyết?
2. Anh: nếu pilot teacher đạt cổng nhưng cần hơn **6,97 USD** còn lại, Anh có muốn nâng trần API không? Không gọi API trước câu trả lời này.
3. Claude/leader: mức ưu tiên public so với private khác nhau thế nào nếu public 410/634 mẫu **cài** app mới nhưng chưa biết bao nhiêu mẫu thực sự **dùng** app đó?

Giới hạn: điểm public không có nhãn để kiểm lại; pilot API chỉ n=80, n=9 ask; attribution một nguyên nhân chính mang tính đánh giá; hai dev có 37 ID trùng nhưng adapter khác; replay Q6 không cho model sinh lại sau sửa call; chưa có 4B+Pho-ft, Qwen Thinking trên A30, hoặc kết quả của máy anh trai. Không có số đo nào chứng minh các dải Δ trong bảng ưu tiên; chúng chỉ dùng để xếp lịch thí nghiệm.
