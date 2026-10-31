# Deep research đối chiếu LifeMate — 31/10/2026

## 0. Tóm tắt cho người bận

*Thứ tự dưới đây tối ưu khả năng tăng điểm **private** trước hạn Docker 16/11. Không có khoảng tăng điểm private nào đã được đo trực tiếp; mọi ước lượng trong báo cáo là giả thuyết để kiểm bằng dev. Chi phí là ước lượng lập kế hoạch, không phải thời gian GPU đã chạy.*

| Hạng | Việc và tác động cần kiểm | Chi phí / ưu tiên |
|---|---|---|
| 1 | [Bằng chứng mạnh] Khôi phục **phép đo đầu-cuối hợp lệ**; tách lỗi ASR, agent, runtime theo `dev_random` và `dev_lao`. Không có đo này thì mọi xếp hạng model dễ sai. | 0,5–1 ngày người; P0 |
| 2 | [Bằng chứng mạnh] Chốt thí nghiệm D bằng đối chứng khớp bước và báo **ask/execute/OOS**; nếu D không thắng, dùng lỗi để sửa mẫu thiếu slot thay vì mở rộng mù. | 1 ngày phân tích sau khi job được chạy hợp lệ; P0 [S5][S9][S10] |
| 3 | [Suy luận] Xây bảng **nguồn của từng tham số** từ lời nói, history, kết quả tool; chặn ID tự bịa trước lệnh ghi bằng kiểm tra dựa trên kết quả tool hiện có. Nhắm lỗi hash. | 1–2 ngày người; P0 [S14][S67] |
| 4 | [Suy luận] Cho leader so ASR theo **slot và điểm agent đầu-cuối**, thêm Qwen3-ASR-0.6B cùng hai baseline; không chọn theo WER đơn lẻ. | 1–2 ngày người + vài giờ GPU đo; P0 [S25][S54][S29][S30][S31] |
| 5 | [Bằng chứng vừa] Thử ITN tiếng Việt NeMo `r1.2.0` có kiểm lỗi ngày/số/tiền; đưa thời gian và phép tính sang code khi điều kiện rõ. | 1–2 ngày người; P0 [S20][S74] |
| 6 | [Bằng chứng vừa] Đo Qwen3-4B-Instruct-2507 trên cùng tập và cùng recipe; giữ 1.7B làm đối chứng, không suy điểm từ BFCL. | 1–2 ngày chuẩn bị + cloud GPU cần đo; P0 [S44][S45] |
| 7 | [Bằng chứng vừa] Khóa runtime A30/Docker offline, đo p50/p95/max, 5 lượt greedy, cold start, VRAM và trường hợp sát 30 giây. | 1–2 ngày người + A30; P0 [S39][S40][S41] |
| 8 | [Suy luận] Sinh **lô nhỏ** app/trajectory mới có provenance và replay; chỉ mở rộng khi `dev_lao` tăng mà không hại `dev_random`. | 2–3 ngày người + API chỉ lúc phát triển; P1 [S11][S14] |
| 9 | [Suy luận] Thử JSON/enum constrained decoding ở một backend đã pin; đo lỗi format, hash và độ trễ, không áp dụng mặc định. | 1 ngày người + A30; P1 [S18][S19] |
| 10 | [Suy luận] Thử Qwen3.5-4B hoặc Gipformer 68M như **challenger có cổng dừng sớm**; chúng có căn cứ licence/ngày/tổng tham số nhưng chưa có điểm LifeMate. | 1 ngày sàng lọc mỗi cặp; P1 [S31][S46] |

**Dừng / chưa làm.** [Bằng chứng vừa] (i) Không triển khai RL đa lượt mới trước mốc đóng băng: ToolRL/EFPL có tín hiệu nhưng tích hợp reward, rollout và kiểm reward hacking vượt đường găng hiện tại [S9][S16]. (ii) Không thêm `ask_missing_info` bằng luật mơ hồ diện rộng: luật A đã chỉ kích hoạt 0–2 mẫu trong thí nghiệm nội bộ. (iii) Không đổi sang audio-LLM end-to-end hoặc model chỉ vì tên “3B/E2B”: Gemma-4-E2B-it và Qwen2.5-Omni-3B đều dưới trần **hệ thống** 6B khi chạy một mình, nhưng cần xác nhận cách tính cấu phần LLM, tiếng Việt/tool use và (với Omni) licence [S38][S49].

**Ba rủi ro private lớn nhất.** [Bằng chứng mạnh] Một call ghi sai có thể làm hash sai và điểm mẫu về 0 (README chính thức; `docs/PIPELINE.md` mục 3.2). [Bằng chứng vừa] App chưa thấy cộng thiếu slot đã làm ask trên 23 mẫu giữ app riêng về 0 (`docs/EVAL_2026-10-29.md` mục 7); ASR có thể khuếch đại lỗi này nhưng chưa có điểm đầu-cuối. [Bằng chứng mạnh] Hai job gần nhất chưa sinh điểm do lỗi đường chạy trên `main`; Docker/A30, 30 giây và tái lập chưa được chứng minh (`lifemate/runs/phase2_d.log`, `e2e_baseline.log`, đọc 30/10). [S39][S41]

## 1. Đội đang đặt cược vào điều gì

*Phần này được viết sau khi đọc tài liệu và mã nội bộ, trước khi tra cứu nguồn bên ngoài. Số liệu nội bộ là phép đo của đội, không phải bằng chứng về private test.*

**Các giả định ngầm.** [Bằng chứng vừa] Đội chọn ASR → agent gọi tool theo vòng lặp, vì tách được lỗi nghe và lỗi quyết định; hiện mới đo agent trên `audio_text`, chưa có điểm đầu-cuối. Đường suy luận thực tế dùng một `ToolEnv` cho mỗi mẫu, kiểm schema trước `env.call`, bỏ trùng call đọc, dừng sau `ask_missing_info`; `Agent.run` chỉ kiểm đồng hồ **giữa** hai lượt generate. Nguồn: `JOURNAL.md` mục 0, 4, 6; `lifemate/lifemate/agent.py` và `infer.py` trên nhánh `e2e-baseline`.

[Bằng chứng mạnh] SFT Qwen3-1.7B LoRA r32, 1 epoch đạt 53,92 trên 233 mẫu `dev_random` có chữ chuẩn; điểm trên 233 mẫu đã train là 80,22. Với `fit_lao` không thấy 6 app, điểm `dev_lao` là 35,53 trên 262 mẫu; nhóm hỏi lại chỉ đạt 7,48 và 23 mẫu cần hỏi về tool của app giữ riêng được 0 điểm. Chênh lệch 53,92–35,53 **không** cô lập được tác động app mới vì thành phần mẫu khác nhau. Nguồn: `docs/EVAL_2026-10-29.md` mục 3 và 7; `docs/REVIEW_CLAUDE_EVAL_2026-10-29.md` mục 3.

[Bằng chứng vừa] Đội đặt cược vào việc model học chính sách nhãn từ dữ liệu phản thực tế và sau đó từ app tổng hợp. D-train có 77 mẫu, 242 dòng SFT, 25 tool đích; ba tool đứng đầu chiếm 47%. D-eval sạch sau khi bỏ một mẫu rò rỉ còn 23 cặp, model gốc hỏi đúng 0/23 ở vế thiếu thông tin. D có nhãn phát lại được qua ToolEnv, nhưng phát lại chỉ chứng minh tính hợp lệ thực thi, chưa chứng minh giống chính sách BTC. Người đọc tay chưa hoàn tất. Nguồn: `docs/D_PHASE1B_2026-10-30.md` mục 0, 4–6; `docs/baselines/d_phase1b_2026-10-30.json`; `docs/REVIEW_D_2026-10-30.md` mục 0.

**Rủi ro lớn nhất cho private.** [Suy luận] (1) Một lệnh ghi sai khiến hash sai và mất toàn bộ điểm mẫu; 46% tham số lệnh ghi lấy từ kết quả tool, 15% từ history, 15% cần tính thời gian, 11% cần tính số. (2) App/schema chưa thấy và thiếu slot có thể làm model tự điền giá trị: ở các ca C bỏ hỏi, 21/25 lần model điền một giá trị cho slot cần hỏi. (3) Chưa chứng minh pipeline ASR + agent + Docker chạy offline, tái lập và dưới 30 giây trên A30; ngay lúc đọc, lượt D dừng ở rollout với `No module named lifemate.infer`, baseline đầu-cuối dừng vì thiếu `scripts/e2e_baseline.sh` trong checkout `main`. Đây là lỗi hiện tại của workspace/job, chưa phải kết quả thí nghiệm. Nguồn: `docs/PIPELINE.md` mục 3.2; `docs/EXPERIMENT_D.md` mục 3; `lifemate/runs/phase2_d.log`, `lifemate/runs/e2e_baseline.log` (đọc 30/10/2026).

**Năm câu hỏi bên ngoài cần trả lời trước.**

1. Model nhỏ học ranh giới **hỏi / làm / bỏ qua** trên schema chưa thấy tốt hơn bằng cặp phản thực tế, cân lại dữ liệu thật, preference learning, hay guardrail nào?
2. Dữ liệu app tổng hợp cần kiểm gì ngoài khả năng replay để khớp chính sách call đọc, hỏi lại và tham số của BTC?
3. Với khoảng 6,8 giờ lời nói train, ASR nào giữ đúng số, giờ, phủ định và tên tốt nhất, và sửa transcript có cứu được điểm agent không?
4. Có model LLM/audio mới phát hành trọng số trước 26/10/2026 đáng đổi khỏi Qwen3-4B + Whisper/PhoWhisper, vừa trần tham số và 30 giây không?
5. Những kỹ thuật constrained decoding, tính toán tất định và runtime nào giảm lỗi hash hoặc nguy cơ mất trắng mà vẫn giữ được F1 call và tính tái lập?

## 2. Bản đồ hiện trạng tri thức A–L

*Các con số dưới đây giữ nguyên benchmark, cỡ model và ngôn ngữ của nguồn. Chúng **không** là dự báo điểm LifeMate. Một số card tự báo kết quả và có protocol khác nhau. “Chưa có” nghĩa là không tìm thấy phép đo đủ gần trong nguồn đã mở.*

| Trục; Q | Biết chắc và con số gần nhất | Khoảng trống đối với private |
|---|---|---|
| **A** Tool/app mới; Q6,Q15,Q17 | [Bằng chứng vừa] BFCL v4 tách multi-turn, thiếu tham số, irrelevance; Hammer dùng function masking; Gorilla/ToolBench đặt bài toán API mới. Trên ToolBench của paper 2026, menu đủ producer nâng online success 0,737→0,898, nhưng không có state hash. [S1][S2][S3][S4][S67][S68] | [Suy luận] Đội đã rename/remove/distractor, còn thiếu kiểm **mô tả schema**, đường producer→consumer và truy hồi tool chỉ khi catalog lớn. Chưa có số tăng cho model Việt <5B. |
| **B** Hỏi/làm/bỏ qua; Q4,Q5,Q13 | [Bằng chứng mạnh] Noisy ToolBench ghi nhận LLM tự bịa missing argument. When2Call và ToolSandbox đo riêng hỏi lại; τ²-bench nhấn mạnh stateful interaction. EFPL trên Qwen3-4B báo BFCL multi-turn 37,83 và When2Call F1 77,76; trong cùng bảng, GRPO-planner là 34,50 và 74,09. [S5][S6][S7][S8][S9] | [Suy luận] `ask_missing_info` LifeMate là tool call cuối, còn “cannot answer” của paper thường là trả lời bằng chữ; cần ánh xạ sang `[]` đúng chính sách. Không thể cộng mức tăng paper vào 35,53 dev_lao. |
| **C** Synthetic đúng chính sách; Q2,Q3,Q17,Q18 | [Bằng chứng vừa] APIGen kiểm format, thực thi, ngữ nghĩa; APIGen-MT thêm trajectory; ToolACE kết hợp rule/model filter; ToolWeave theo dõi nguồn tham số. ToolForge báo +21,6% trên 5 QA benchmark với **Qwen3-8B**, vượt trần bài này. [S11][S12][S13][S14][S15] | [Suy luận] Replay chứng minh call chạy được, không chứng minh BTC sẽ chọn đúng **đường đi**, bước đọc hay hỏi. Cần audit người và so phân bố/hiệu quả trên app giữ riêng. |
| **D** SFT/RL model nhỏ; Q15 | [Bằng chứng vừa] ToolRL báo +17% từ base và +15% từ SFT trên benchmark của họ với reward chi tiết; EFPL có kết quả 1.7B và 4B nhưng dùng planner/executor riêng. [S9][S16] | [Suy luận] Chưa có GPU-hour, A30 latency hoặc reward khớp hash BTC. SFT D + đối chứng khớp bước là lựa chọn gần hạn; RL là P2. |
| **E** Structured decoding; Q14 | [Bằng chứng vừa] XGrammar/vLLM hỗ trợ grammar và JSON schema; ép cú pháp không đảm bảo tool/ID/giá trị đúng. [S18][S19][S57] | [Suy luận] Cần đo format-error giảm bao nhiêu, cost/token, tác hại khi enum/ID hợp lệ nhưng giá trị đúng chưa quan sát. |
| **F** Ngày/số/ITN; Q12,Q13 | [Bằng chứng mạnh] NeMo `r1.2.0` ngày 05/06/2026 thêm **cả TN và ITN tiếng Việt** cho cardinal, ordinal, decimal, date, time, fraction, measure, money, telephone, electronic. PAL hỗ trợ ý tưởng tách phép tính ra code. [S20][S21][S74] | [Suy luận] Không thấy bằng chứng grammar xử lý đầy đủ ngày tương đối và tự sửa trong câu nói LifeMate. `vinorm` đi chiều số→lời nói; dateparser/Duckling cần test khẩu ngữ và licence. [S22][S23][S24] |
| **G** ASR Việt; Q9–Q12 | [Bằng chứng vừa] PhoWhisper có 844 giờ huấn luyện; ViMD đo phương ngữ. Card Gipformer 68M tự báo WER ViMD 7,00 và FLEURS 12,65; card BuzzASR tự báo FLEURS WER 7,26. Qwen3-ASR-0.6B hỗ trợ vi, nhưng file trọng số có **938M**, không phải 600M. [S25][S54][S28][S29][S30][S31][S32] | [Bằng chứng mạnh] WER các card khác tập chuẩn hoá, không so trực tiếp; chưa có điểm ASR→agent trên dev. Cần slot recall, điểm theo cặp và p95 latency. [S33][S34][S72] |
| **H** SLU/audio-LLM; Q6,Q15 | [Bằng chứng vừa] SLURP/STOP cho parsing từ speech ở tiếng Anh. Voxtral Mini tên 3B nhưng toàn bộ là 4,676B; Qwen2.5-Omni tên 3B nhưng toàn bộ 5,537B (<6B) và licence riêng. [S35][S36][S37][S38] | [Suy luận] Không có nguồn chứng minh audio-LLM nhỏ gọi `ToolEnv` tiếng Việt tốt hơn pipeline; cấu phần LLM và licence của Omni còn cần xác nhận. Nối tầng vẫn là mặc định hợp lý. |
| **I** A30/runtime; Q16,Q19 | [Bằng chứng mạnh] A30 là Ampere 24GB. vLLM không bảo đảm tái lập mặc định; offline có chế độ tắt V1 multiprocessing hoặc batch invariance. Greedy vẫn có thể đổi theo batch. [S39][S40][S41][S42] | [Bằng chứng mạnh] Chưa có benchmark 30 giây, VRAM, cold start, 5 lượt trên A30 của đội. Không suy latency từ thông số GPU. |
| **J** Đánh giá; Q6–Q8 | [Bằng chứng vừa] Nghiên cứu adaptive holdout giải thích vì sao dùng leaderboard lặp dễ overfit. Paper 2026 khuyên báo action-class recall/emit-rate/accuracy thay tổng điểm. [S10][S43][S73] | [Suy luận] `dev_random` và `dev_lao` khác thành phần; cần so **cùng id** theo cặp trong từng split, bootstrap theo origin/app và khoá quy tắc nộp public. |
| **K** Tiền lệ Việt; Q9,Q18 | [Bằng chứng vừa] PhoWhisper, ViMD, GigaSpeech 2 và nghiên cứu ASR Việt 2026 cho biết phương ngữ, miền và chuẩn hoá có thể đổi kết luận. VLSP 2025 báo hệ thắng có SyER 9,07 và một đội dùng Whisper Small hai giai đoạn; các số đó không đo LifeMate. [S25][S54][S28][S33][S72][S80][S81] | [Chưa kiểm chứng] Chưa tìm được writeup giải ZAC LifeMate 2026 có nguồn gốc công khai và hợp lệ; không dùng bài đăng có transcript/nhãn test. Không chuyển kết quả VLSP thành điểm hash. |
| **L** LLM nhỏ; Q15 | [Bằng chứng vừa] Card Qwen3-4B-2507 tự báo BFCL-v3 61,9; Qwen3.5-4B tự báo BFCL-v4 50,3; Granite-4.2-3B tự báo BFCL-v4 52,41. **Khác phiên bản/protocol nên không xếp hạng bằng các số này.** [S44][S46][S48] | [Suy luận] Chỉ phép đo LifeMate cùng prompt, compute, ASR và A30 mới xác nhận thay model; Granite card còn khuyên sampling `temperature=1`, xung đột yêu cầu greedy. |

### Đào sâu năm trục rủi ro đã đo

**B — quyết định mode trước giá trị.** [Bằng chứng mạnh] `dev_lao` ask 7,48 và 0/23 ở nhóm app giữ riêng là lỗi chọn hành động, không chỉ lỗi cú pháp. `docs/EXPERIMENT_D.md` cho thấy 21/25 lần bỏ hỏi model điền một giá trị. Noisy ToolBench báo cùng hiện tượng trên tác vụ khác; paper calibration 2026 khuyên tách **tool_call / ask / refuse / confirm** và theo dõi emit-rate thay vì chỉ accuracy tổng [S7][S10]. [Suy luận] Bản thử rẻ nhất là thêm báo cáo confusion mode và cặp đủ/thiếu slot, giữ execute/OOS làm rào chống “hỏi mọi thứ”. DPO hoặc EFPL chỉ sau khi SFT D có tín hiệu vì paper EFPL cũng thấy SFT-planner thuần có thể kém hơn base [S9].

**C — dữ liệu tổng hợp phải có nguồn cho mỗi tham số.** [Bằng chứng vừa] APIGen kiểm chạy API; ToolWeave khẳng định lỗi hallucination xuất phát từ tham số không do người nói hay tool trước đó cung cấp [S11][S14]. [Suy luận] Với LifeMate, mỗi tham số synthetic cần một tag `speech/history/tool_result/clock/computation/allowed_default`; giá trị thiếu nguồn phải hỏi hoặc bỏ. Người đọc tay cần xác nhận đường call/read đúng quy ước BTC trước khi dùng nhãn. Trộn lô nhỏ với mẫu thật và kiểm dev_lao; model collapse là rủi ro khi thay thế lặp dữ liệu thật, không là bằng chứng rằng lô synthetic đầu tiên sẽ hại [S17].

**D — chỉ tối ưu objective khi bộ chấm đáng tin.** [Bằng chứng vừa] ToolRL dùng reward chi tiết tên tool, tham số, giá trị; đó là gợi ý cho shaping, nhưng điểm BTC có hash gate: call ghi thừa không thể sửa bằng retry trong cùng env [S16]. [Suy luận] Trước 12/11, ưu tiên 2 epoch/4B và D được đo theo cặp. Nếu muốn RL sau cuộc thi, rollout phải dùng env train hợp lệ, một env mỗi mẫu, reward đúng hash/call và audit reward hacking.

**G — chọn ASR bằng lỗi slot và tác động agent.** [Bằng chứng mạnh] `asr.py` hiện đi qua Whisper greedy; `asr_quality.py` có kiểm slot, nhưng job đầu-cuối chưa hoàn tất. [Bằng chứng vừa] CB-Whisper cải thiện entity recall trên Anh/Trung, còn Gipformer tự báo WER tốt ở một số bộ tiếng Việt; hai nguồn không chứng minh tên app/tiền/giờ trong LifeMate [S31][S34]. [Suy luận] So transcript cùng id với `audio_text` chuẩn: lỗi phủ định, số, tiền, ngày giờ, tên app, query và history; chạy agent cùng checkpoint để lấy ∆điểm theo cặp. Dùng context bias chỉ từ `installed_apps`, enum và kết quả tool đã gọi, có danh sách âm tính để đo false positives.

**I — xác định đường găng hệ thống.** [Bằng chứng mạnh] `Agent.run` kiểm ngân sách giữa hai lời gọi generate, nên một generate chậm có thể vượt 25 giây; p95 và max quan trọng hơn throughput [S39][S41]. [Suy luận] Đo thời gian ASR, prefill, từng vòng LLM, tool, tổng; pin phiên bản vLLM, model SHA, trình điều khiển, context cap ≤16.384, batch 1 và seed. Chạy 5 lượt cùng tập sau khi cố định backend. Chỉ áp quantization khi so theo cặp chứng minh hash/F1 không giảm; A30 không có lý do chọn FP8 làm mặc định [S40][S42].

## 3. Đối chiếu pipeline của đội với tri thức ngoài

| Thành phần | Đã / đang / định làm | Khoảng cách nhìn từ nguồn | Đề xuất ngắn | Nguồn |
|---|---|---|---|---|
| ASR | [Bằng chứng mạnh] PR #4 có Whisper turbo, PhoWhisper; đầu-cuối chưa có điểm. | [Bằng chứng vừa] Model Việt mới và benchmark phương ngữ có, nhưng số WER không là điểm agent. [S25][S54][S28][S30][S31] | Đo thêm Qwen3-ASR 0.6B; giữ theo slot + ∆score. | [S25][S54][S28][S30][S31] |
| ITN | [Bằng chứng mạnh] `vinum.py` chỉ sinh dạng nói; ITN chưa nối. | [Bằng chứng mạnh] NeMo đã có grammar vi cả TN/ITN từ 06/2026. [S74] | Thử trên dev train; chặn biến đổi mơ hồ. | [S74] |
| Prompt/schema | [Bằng chứng mạnh] ChatML, schema gọn, bảng ngày, SFT khớp inference. | [Bằng chứng vừa] Tool menu nên giữ producer của ID và dependency; retrieval thuần có thể bỏ sót bước đọc. [S67][S68] | Thử mask/menu theo action path, so cùng checkpoint. | [S67][S68] |
| Dữ liệu SFT | [Bằng chứng mạnh] Rename, remove, distractor, ASR-style, gộp bước. | [Bằng chứng vừa] Function masking có tiền lệ; chưa có phép đo tách riêng từng augment hoặc schema paraphrase. [S2] | Ablation một thay đổi, giữ only nếu dev_lao tăng. | [S2] |
| Synthetic T3 | [Bằng chứng vừa] Có ý tưởng app/schema/simulator; D replay được. | [Bằng chứng vừa] Execution verification cần thêm nguồn tham số, kiểm chính sách và độ giống thật. [S11][S14] | Lô nhỏ, audit tay, mix với real, không mở rộng trước tín hiệu. | [S11][S14] |
| Hỏi lại | [Bằng chứng mạnh] Luật A bị loại; D 77 mẫu, phase2 chưa có score. | [Bằng chứng mạnh] “Tự bịa missing argument” là lỗi phổ biến; cần mode calibration. [S7][S10] | Chốt D, confusion mode và guardrail hash. | [S7][S10] |
| Decoding | [Bằng chứng mạnh] Parse JSON rồi `validate`; retry có giới hạn. | [Bằng chứng vừa] Grammar có thể loại JSON sai nhưng không sửa giá trị sai. [S18][S19] | Đo format-error và latency trước khi ép. | [S18][S19] |
| Code tất định | [Bằng chứng vừa] Định chuyển ngày/số/ID sang code. | [Bằng chứng vừa] PAL gợi ý tính bằng code; token-level ID constraint có thể sai nếu ID chưa hiện ra. [S20] | Chỉ tính khi đơn nghĩa; ID phải có provenance từ history/tool. | [S20] |
| Đánh giá | [Bằng chứng mạnh] Dev random, leave-apps-out, scorer, so theo cặp/bootstrap. | [Bằng chứng vừa] Cần báo action-class và hạn chế chọn thích nghi trên holdout. [S10][S43] | Khoá split/quy tắc; thêm provenance và CI theo origin. | [S10][S43] |
| Suy luận | [Bằng chứng mạnh] vLLM backend có sẵn; A30 chưa đo. | [Bằng chứng mạnh] vLLM không tự bảo đảm tái lập; greedy chưa đủ. [S39][S40] | Pin runtime; benchmark 5 lượt và max latency. | [S39][S40] |
| Docker | [Bằng chứng mạnh] `predict.sh` có; job hiện fail vì checkout thiếu code. | [Suy luận] Cần kiểm path, artifact, offline, driver, stdout, một env/mẫu. [S41] | Chạy dry run hợp lệ sau khi đội phục hồi checkout; đóng băng 12–13/11. | [S41] |



## 4. Đề xuất có cổng kiểm chứng

**Thang chấm.** [Suy luận] Bốn cột 1–5: tác động tiềm năng **T**, độ tin bằng chứng **B**, chi phí **C**, rủi ro thực hiện **R**; điểm tham khảo `T×B/(C×R)`, thêm **M** 0–5 nếu giảm nguy cơ mất trắng. Đây là cách chọn việc, **không phải** dự báo điểm. Ưu tiên còn phụ thuộc thứ tự đường găng. Chi phí GPU dưới đây là **ngân sách thí nghiệm đề nghị**, chưa phải dự đoán runtime; đội phải đo trên máy/cloud thật. Không có phép đo đủ tin để nêu khoảng tăng điểm private. Mọi thay đổi P0/P1 đều chạy riêng một biến chính, cùng id trên cả `dev_random` và `dev_lao`, báo ∆ theo cặp, bootstrap theo origin/app, các nhóm execute/ask/OOS, app thấy/chưa thấy, rồi mới quyết. Mỗi **lượt suy luận** tạo đúng một `ToolEnv` cho mẫu; không tìm kiếm nhánh bằng cách reset/clone env. [S10][S43]

| Mã | Ưu tiên | T / B / C / R / M | Lý do xếp |
|---|---|---|---|
| P0-1 | P0 | 5 / 5 / 2 / 2 / 5 | Mở khoá mọi quyết định và ngăn lỗi nộp. |
| P0-2 | P0 | 5 / 4 / 2 / 2 / 1 | Lỗi ask đã đo trực tiếp. |
| P0-3 | P0 | 5 / 3 / 3 / 2 / 3 | Ngăn ID tự bịa gây hash sai. |
| P0-4 | P0 | 5 / 4 / 3 / 2 / 2 | Audio là đầu vào thật nhưng chưa có điểm. |
| P0-5 | P0 | 4 / 4 / 2 / 2 / 1 | Grammar vi có sẵn; chỗ nối hẹp. |
| P0-6 | P0 | 5 / 3 / 3 / 3 / 1 | Model 4B có khả năng nâng trần, cần cloud. |
| P0-7 | P0 | 5 / 5 / 3 / 2 / 5 | Runtime là điều kiện nộp, không chỉ tối ưu điểm. |
| P1-1 | P1 | 4 / 3 / 4 / 3 / 0 | Synthetic có tiềm năng nhưng dễ lệch nhãn. |
| P1-2 | P1 | 3 / 3 / 3 / 3 / 1 | Format có thể cứu lỗi nhưng semantic còn nguyên. |
| P1-3 | P1 | 4 / 2 / 3 / 4 / 0 | Model mới cần cổng dừng sớm. |

### P0-1. Phục hồi và khóa baseline đầu-cuối

[Bằng chứng mạnh] **Giả thuyết:** đo cùng mẫu từ audio tới `state_hash` sẽ phơi bày tác động ASR và lỗi thực thi; đây là tiền đề chọn mọi thay đổi tiếp theo. Hai log hiện tại không có score: rollout D lỗi import `lifemate.infer`, e2e script không tìm thấy trong `main`. Chúng **không** cho phép suy rằng model D/ASR tốt hay xấu. Đánh giá theo mode và tính tái lập phù hợp khuyến nghị ngoài [S10][S39]. **Tác động:** mọi loại mẫu, cả app thấy/chưa thấy, trên audio; điểm tăng trực tiếp bằng 0 vì đây là phép đo, nhưng giảm quyết định sai và nguy cơ nộp lỗi. **Chi phí:** Claude 0,5–1 ngày kiểm checkout/job/path; leader 0,5 ngày đọc metric; 1–3 giờ GPU đo nếu runtime hiện có hoạt động. **Rủi ro:** lỗi môi trường, path và khác biệt code giữa `main`/`e2e-baseline`; tín hiệu trong ngày khi có pipeline hợp lệ. **Cắm vào:** `scripts/e2e_baseline.sh`, `scripts/asr_quality.py`, `lifemate/infer.py::main`, `scorer.py::score_sample`, `runinfo.py`; không sửa trong nghiên cứu này. **Phép đo:** trên hai split, cùng checkpoint agent, so `audio_text` chuẩn và từng ASR bằng cùng id, seed, prompt; lưu version/SHA, lỗi runtime, ∆score/CI và slot. **Giữ** baseline khi 100% id có JSON hợp lệ, 0 exception, 0 gọi env ngoài một instance/mẫu, có score và provenance; **bỏ và sửa đường chạy** nếu thiếu bất kỳ điều kiện nào. **Phụ thuộc:** Anh/Claude quyết phục hồi checkout hoặc chạy từ `~/zac-jobs/lifemate/` có code; leader xác nhận bản ASR. [S10][S39]

### P0-2. Chốt D và chẩn đoán mode hỏi/làm/bỏ qua

[Bằng chứng mạnh] **Giả thuyết:** cặp đủ/thiếu slot của D dạy model kiềm chế việc tự bịa, nhưng phải bảo vệ execute/OOS. Nội bộ: 77 mẫu D-train, 23 cặp D-eval sạch, 0/23 ask ở baseline; đó là tín hiệu lỗi, **chưa có kết quả can thiệp**. When2Call, EFPL và phân tích calibration độc lập ủng hộ tách lớp quyết định này [S5][S9][S10]. **Tác động:** ask trên app thấy/chưa thấy và audio sau này; có thể hại execute nếu over-ask. **Chi phí:** Claude/Anh 1 ngày tổng hợp B-D3, B-up, B-D1 và review tay; GPU bổ sung 0 nếu score được khôi phục, tối đa 2–4 giờ cloud nếu phải chạy lại. **Rủi ro:** mẫu D tập trung tool, nhãn “đúng” chỉ hợp lệ thực thi, rò rỉ origin, tự bịa giảm nhưng over-ask tăng; tín hiệu 1 ngày sau score. **Cắm vào:** `counterfactual.py::build`, `make_label`, `replay`, `split_by_origin`; `sft.py::build_all`; `train.py::main`; `askpolicy.py::ask_type`; `compare.py`/scorer. **Phép đo:** ba nhóm khớp số bước/token và cùng split train, cùng id ở `dev_random`/`dev_lao`; báo ask recall, ask precision, execute/OOS, số call thừa và điểm tổng; D-eval chỉ là stress set, không thay dev. **Giữ** D nếu ∆`dev_lao` ≥+2 điểm, ∆`dev_random` ≥−1 điểm, ask ở cả hai tăng mà execute/OOS không giảm >2 điểm; **bỏ/thu hẹp** nếu bất kỳ rào nào fail hoặc review tay thấy nhãn sai chính sách. Các ngưỡng là quyết định trước đo, không là ý nghĩa thống kê; báo CI dù điểm vượt. **Phụ thuộc:** Anh duyệt nhãn mẫu biên và chọn có thuê cloud khi cần. [S5][S9][S10]

### P0-3. Provenance tham số và chặn ID không có nguồn

[Suy luận] **Giả thuyết:** trước lệnh ghi, chỉ cho ID tham chiếu đã xuất hiện trong history hoặc kết quả tool của **cùng env**; yêu cầu thêm bước đọc nếu thiếu; thiếu slot không có default hợp lệ thì hỏi. ToolWeave theo dõi nguồn tham số và State-Path Menu giữ producer trước consumer, nhưng số tăng paper 70B/ToolBench không áp dụng trực tiếp [S14][S67]. **Tác động:** execute và ask, nhất là app chưa thấy; giảm hash sai do giá trị tự bịa. **Chi phí:** Claude 1–2 ngày, CPU phát triển; 1–2 giờ GPU đo hai split. **Rủi ro:** chặn ID hợp lệ được user nói nhưng chưa hiện trong tool result, gọi đọc thừa làm F1 giảm, over-ask; tín hiệu sau 1 ngày. **Cắm vào:** `agent.py::Agent.run` ngay trước `env.validate`/`env.call`; `prompt.py::render_results` và `history_messages` để lấy provenance; `askpolicy.py::is_xref`; không đọc thư mục môi trường. **Phép đo:** A/B cùng model, ASR, prompt, bước, time budget; chỉ bật guardrail ở một nhóm xref được định nghĩa từ schema, đo ∆score theo cặp cả hai dev, số ID không chứng thực, số read/ask thừa. **Giữ** nếu ∆`dev_lao` ≥+2, ∆`dev_random` ≥−1 và số write ID không chứng thực giảm ≥50%; **bỏ** nếu read/ask thừa làm điểm execute giảm >1 hoặc có false block ở audit tay. **Phụ thuộc:** Anh duyệt định nghĩa “ID đã thấy” và ưu tiên call đọc theo Q3/Q14. [S14][S67]

### P0-4. Chọn ASR theo slot và điểm agent

[Bằng chứng vừa] **Giả thuyết:** model có WER tốt nhất chưa chắc giữ phủ định, số và tên app tốt nhất. PhoWhisper/ViMD có bằng chứng Việt; Qwen3-ASR 0.6B hỗ trợ vi; Gipformer 68M có card benchmark Việt nhưng tự báo, tất cả khác miền LifeMate [S25][S54][S28][S29][S30][S31]. **Tác động:** cả execute/ask/OOS trên audio; không ảnh hưởng phép đo chữ chuẩn. **Chi phí:** leader 1–2 ngày tích hợp Qwen3-ASR 0.6B, 2–6 giờ GPU đo; Gipformer tối đa 0,5 ngày sàng lọc nếu dễ cắm. **Rủi ro:** Qwen “0.6B” thật 938M, latency A30, dấu câu/số khác format train; tín hiệu 1 ngày sau transcript. **Cắm vào:** `asr.py::Whisper`/`transcribe` hoặc adapter mới, `infer.py::texts_for`, `scripts/asr_quality.py::label_checks` và `predict.sh`. **Phép đo:** dùng cùng audio/id trên hai dev, so từng ASR với Whisper turbo và PhoWhisper; agent/checkpoint cố định; báo WER, entity/negation/number/time slot miss, ∆score/CI, p95 và max latency. **Giữ** ASR thay thế nếu ∆score đầu-cuối ≥+2 trên ít nhất một split, split kia ≥−1, critical-slot miss không tăng và tổng <30 giây A30; **bỏ** nếu chỉ WER tốt nhưng score không đạt rào. **Phụ thuộc:** leader chọn model tải về sau khi Anh chấp nhận licence và dung lượng; chỉ dùng audio train/dev, không pseudo-label test. [S25][S54][S29][S30][S31]

### P0-5. ITN vi và phép tính tất định có điều kiện

[Bằng chứng vừa] **Giả thuyết:** chuẩn hóa số/giờ/tiền có kiểm loại và tính thời điểm bằng code giúp model chọn đúng tham số exact-match. NeMo `r1.2.0` công bố grammar vi; PAL hỗ trợ mô hình LLM chọn phép tính rồi code tính [S20][S74]. **Tác động:** execute có số/ngày/tiền trên audio và chữ chuẩn; giảm lỗi hash, nhưng biến đổi mơ hồ có thể hại. **Chi phí:** leader 1 ngày thử ITN, Claude/Anh 0,5–1 ngày tích hợp tính toán rõ nghĩa; CPU test nhẹ, 1–2 giờ GPU đo agent. **Rủi ro:** “năm”/“lăm”, ngày tương đối, tự sửa; grammar không hiểu ngữ cảnh; tín hiệu 0,5–1 ngày. **Cắm vào:** sau `infer.py::texts_for` trước `prompt.py::build_messages`; phép tính trong `agent.py::Agent.run`/helper riêng có provenance từ `context.current_time`; `vinum.py` chỉ dùng chiều nói nếu cần đối chiếu. **Phép đo:** ba nhánh riêng—ITN, date arithmetic, cả hai—cùng ASR/checkpoint; hai dev theo cặp, báo subset số/ngày/tiền và false conversion. **Giữ** từng nhánh nếu ∆subset ≥+3, ∆tổng mỗi dev ≥−1 và 0 false conversion nghiêm trọng trong audit 50 ca bị biến đổi; **bỏ** nhánh gây đổi nghĩa. **Phụ thuộc:** leader xác nhận ngữ cảnh timezone; Anh chọn subset audit từ train/dev. [S20][S74]

### P0-6. Thử Qwen3-4B-Instruct-2507 trên cùng recipe

[Bằng chứng vừa] **Giả thuyết:** tăng năng lực model có thể giúp app chưa thấy và multi-step; card 4B báo BFCL-v3 61,9 và paper EFPL có backbone 4B, nhưng cả hai không đo LifeMate [S44][S9]. **Tác động:** execute/ask/OOS trên app thấy/chưa thấy, cả text/ASR. **Chi phí:** Anh quyết cloud; Claude 1–2 ngày port recipe, 4–12 giờ GPU cloud là **trần ngân sách thử ban đầu**, không khẳng định huấn luyện xong trong đó. **Rủi ro:** khác template, overfit, chi phí, A30 latency/VRAM; tín hiệu 1–2 ngày nếu checkpoint chạy được. **Cắm vào:** `train.py::build_model`/`main`, `sft.py::build_example`, `agent.py::VLLMBackend`, `predict.sh`; giữ prompt byte-identical giữa train/infer. **Phép đo:** 1.7B và 4B cùng fit split, cùng số epoch/token hữu hiệu, cùng augmentation/seed; đối chứng 1.7B 2 epoch nếu đủ ngân sách; so cùng id ở hai dev trên text trước, ASR sau; báo nhóm ask và p95 A30. **Giữ** 4B nếu ∆`dev_lao` ≥+3, ∆`dev_random` ≥0, không giảm ask và tổng pipeline <30 giây; **bỏ** nếu không đạt hoặc không vừa A30. **Phụ thuộc:** Anh duyệt cloud và licence; leader xác nhận ASR ghép không đẩy tổng ≥6B. [S44][S9]

### P0-7. Chứng minh Docker/A30 offline, 30 giây, tái lập

[Bằng chứng mạnh] **Giả thuyết:** ngăn crash, quá giờ, thiếu trọng số và run-to-run đổi call có giá trị lớn hơn thêm một nhánh thử model. vLLM nói rõ mặc định không bảo đảm tái lập; Thinking Machines giải thích batch invariance; A30 có 24GB nhưng không có latency LifeMate từ thông số [S39][S40][S41]. **Tác động:** mọi mẫu; giảm nguy cơ mất trắng hơn là tăng điểm kỳ vọng. **Chi phí:** Claude/leader 1–2 ngày, 2–4 giờ A30 cho profiling/5 lượt; tín hiệu trong 1 ngày sau khi có image. **Rủi ro:** batch invariance tốn tốc độ, cold start, CUDA/driver mismatch, giới hạn context. **Cắm vào:** `predict.sh`, `agent.py::VLLMBackend`/`Agent.run`, `infer.py::main`, Dockerfile do leader quản lý. **Phép đo:** một image pinned, `HF_HUB_OFFLINE=1`, không network; 5 lượt trên cùng `dev_random` và `dev_lao` audio, mỗi lượt một env/mẫu; đo id/JSON/hash/call giống hệt, p50/p95/max, OOM, VRAM, container cold start, deadline. Đối chứng backend hiện tại với chế độ reproducible và một mức batch cố định. **Giữ** chỉ nếu 0 exception/invalid/timeout, max **<30 giây/mẫu** trên A30 và 5/5 output giống hệt; **bỏ tối ưu** gây fail, quay về cấu hình đơn giản có cùng cổng pass. **Phụ thuộc:** Anh/leader bố trí A30 và chốt image, driver, số lần nộp. [S39][S40][S41]

### P1-1. Synthetic app có kiểm chính sách, bản nhỏ nhất

[Suy luận] **Giả thuyết:** app/schema chưa thấy ở train sẽ dễ hơn khi model học các **đường phụ thuộc** và cách hỏi lại trên app giả, miễn nhãn theo chính sách BTC. APIGen chứng minh giá trị của execution verification; ToolWeave cho thấy theo dõi nguồn tham số; hai nguồn không đo LifeMate [S11][S14]. **Tác động:** app chưa thấy, execute/ask; trên text trước, sau đó audio. **Chi phí:** Claude 2–3 ngày, Anh 0,5 ngày audit, tối đa 100–300 synthetic sample đầu tiên và vài giờ API lúc phát triển; 2–4 giờ GPU cloud cho SFT đối chứng. **Rủi ro:** teacher tự tạo chính sách call khác, đường đọc vô nghĩa, mẫu giả dễ nhận ra, dữ liệu train lấn real; tín hiệu 2 ngày. **Cắm vào:** `counterfactual.py::make_tasks`/`replay`/`judge_reason`, `sft.py::build_all`, `train.py`. **Phép đo:** sinh app giả **chỉ từ schema và mẫu train**, ẩn tên app dev_lao, kiểm provenance mọi tham số, audit ngẫu nhiên 50 mẫu; SFT cùng bước với đối chứng **nhân bản real** và cùng id hai dev; thêm kiểm classifier phân biệt schema thật/giả để phát hiện lệch phân bố. **Giữ** nếu audit ≥95% nhãn đúng chính sách, ∆`dev_lao` ≥+3, ∆`dev_random` ≥−1, ask không giảm; **bỏ** khi fail rào. Không sinh pseudo-label public/private test. **Phụ thuộc:** Anh duyệt nguồn dữ liệu phát triển/chi phí API; Claude xây simulator cho vài nhóm tool trước, không mở rộng 46 app một lượt. [S11][S14][S17]

### P1-2. Structured JSON/enum decoding ở backend đã pin

[Bằng chứng vừa] **Giả thuyết:** ép cú pháp và enum làm ít call invalid hơn, nhưng không sửa chọn tool/giá trị; XGrammar và vLLM cung cấp cơ chế, nên đây là phép thử hẹp [S18][S19]. **Tác động:** mọi loại mẫu có lỗi JSON/schema; giảm call bị từ chối; có thể hại free-text/ask. **Chi phí:** Claude 1 ngày, 1–2 giờ A30; tín hiệu trong ngày. **Rủi ro:** grammar phức tạp theo installed_apps, chậm, enum thiếu giá trị hợp lệ, khác phân phối output SFT. **Cắm vào:** `agent.py::VLLMBackend.generate`/`parse_tool_calls`, `prompt.py::render_tool`, `scorer.py`. **Phép đo:** baseline vs grammar chỉ ép JSON + tool name/enum chắc chắn, cùng model và prompt, cả hai dev theo cặp; đo invalid-call rate, ∆score, latency. Không ép ID ngoài tập **đã xuất hiện** mà chưa biết cơ chế đọc. **Giữ** nếu invalid giảm ≥50%, ∆mỗi dev ≥−1 và p95 tổng <25 giây để còn dư deadline; **bỏ** nếu điểm giảm >1 hoặc quá giờ. **Phụ thuộc:** Claude chọn phiên bản vLLM/XGrammar có license và hỗ trợ A30, leader pin image. [S18][S19]

### P1-3. Challenger model mới: Qwen3.5-4B hoặc Gipformer 68M

[Suy luận] **Giả thuyết:** Qwen3.5-4B có năng lực tool use mới; Gipformer 68M giải phóng bộ nhớ/thời gian ASR. Card Qwen3.5 tự báo BFCL-v4 50,3, card Gipformer có WER Việt tự báo; Granite 4.2 là đối chiếu độc lập nhưng yêu cầu sampling trong card, nên không được dùng số BFCL khác nguồn để kết luận Qwen3.5 hơn/kém [S31][S46][S48]. **Tác động:** Qwen3.5 lên toàn bộ agent; Gipformer lên audio/latency; không biết dấu ∆ private. **Chi phí:** leader/Claude mỗi cặp 0,5–1 ngày sàng lọc + 2–4 giờ GPU; tín hiệu trong ngày nếu adapter có sẵn. **Rủi ro:** Qwen3.5 yêu cầu vLLM main/nightly, 4,660B thực tế nên không ghép PhoWhisper 1,55B; Gipformer card tự báo WER trên chuẩn hóa khác, có thể bỏ sót số/tên. **Cắm vào:** Qwen3.5 tại `train.py::build_model`, `agent.py::VLLMBackend` và chat template; Gipformer tại `asr.py` adapter và `infer.py::texts_for`. **Phép đo:** hai challenger **riêng**, cùng id hai dev; model LLM so zero-shot rồi SFT cùng bước với 4B-2507, ASR so với Whisper turbo trên cùng agent; báo nhóm, slot và A30. **Giữ** nếu challenger ∆`dev_lao` ≥+3, ∆`dev_random` ≥0, latency <30 giây, 5/5 tái lập; **bỏ** sau pilot 1 ngày nếu không vượt rào. **Phụ thuộc:** Anh duyệt cloud/khối lượng thử; leader quyết có chỗ cho model trong image. [S31][S46][S48]

### P2. Để sau cuộc thi hoặc loại khỏi cấu hình nộp

[Suy luận] **RL/GRPO đa lượt** có cơ sở ToolRL/EFPL nhưng cần xây reward và rollout phù hợp hash, tránh tool call thừa; không nên chiếm lịch trước 12–13/11 [S9][S16][S60][S61]. **Audio-LLM end-to-end** cần benchmark tiếng Việt + call policy + tổng tham số; Voxtral Mini 4,676B chưa chứng minh tiếng Việt, Qwen2.5-Omni 5,537B có licence qwen-research, Gemma-4-E2B 5,123B có Apache-2.0 nhưng cả hai cần xác nhận cấu phần LLM và đo task; không xếp hạng cấu hình nộp hiện tại [S37][S38][S49]. **Model licence NC/qwen-research/gated** như xLAM, Hammer2.1, Parakeet: hỏi BTC bằng văn bản rồi mới xét, không đặt trong đường nộp hiện tại [S50][S51][S70]. **Speculative decoding** ToolSpec có thể tiết kiệm thời gian nhưng tăng độ phức tạp trước freeze, chỉ xem lại nếu profiling A30 chỉ ra decode là nút thắt [S69].

### Ma trận chín điều kiện tuân thủ cho từng đề xuất

`✓` = thiết kế đáp ứng; `Đ` = cần đo/chứng minh trên A30 hoặc artifact; `?` = cần người xác nhận; `—` = không có model mới. C1 trọng số trước 26/10; C2 licence; C3 tổng <6B và LLM <5B; C4 offline; C5 <30 giây A30; C6 greedy/tái lập; C7 không nhãn/pseudo-label test; C8 không đọc `*_environment/`; C9 một `ToolEnv` mỗi mẫu, không reset/clone. Các dấu ✓ ở C7–C9 là **điều kiện thiết kế đề xuất**, đội vẫn phải audit code nộp. [S39][S41]

| Đề xuất | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | Ghi chú |
|---|---|---|---|---|---|---|---|---|---|---|
| P0-1 baseline | ✓ | ✓ | ✓ | Đ | Đ | Đ | ✓ | ✓ | ✓ | Chọn cấu hình Qwen3-4B+Whisper turbo đã kiểm ở §6; job hiện fail. |
| P0-2 D | ✓ | ✓ | ✓ | ✓ | Đ | Đ | ✓ | ✓ | ✓ | Chỉ dùng train/fit; mỗi replay là một env mới cho mẫu train. |
| P0-3 provenance | ✓ | ✓ | ✓ | ✓ | Đ | Đ | ✓ | ✓ | ✓ | ID lấy từ history/tool trong cùng env. |
| P0-4 ASR | ✓ | ✓ | ✓ | Đ | Đ | Đ | ✓ | ✓ | ✓ | Mỗi cặp model tính tổng ở §6; Qwen3-ASR 1.7B + 4B bị loại. |
| P0-5 ITN/code | ✓ | ✓ | ✓ | ✓ | Đ | Đ | ✓ | ✓ | ✓ | NeMo Apache-2.0; không thêm model tham số. |
| P0-6 Qwen 4B | ✓ | ✓ | ✓ | Đ | Đ | Đ | ✓ | ✓ | ✓ | Cần pin 4B-2507 + ASR phù hợp. |
| P0-7 runtime | ✓ | ✓ | ✓ | Đ | Đ | Đ | ✓ | ✓ | ✓ | C4–C6 là cổng bắt buộc trước nộp. |
| P1-1 synthetic | ✓ | ✓ | ✓ | ✓ | Đ | Đ | ✓ | ✓ | ✓ | LLM ngoài chỉ lúc phát triển; kiểm license dữ liệu tạo ra. |
| P1-2 grammar | ✓ | ✓ | ✓ | ✓ | Đ | Đ | ✓ | ✓ | ✓ | Pin bản vLLM/XGrammar và kiểm latency. |
| P1-3 challenger | ✓ | ✓ | ✓ | Đ | Đ | Đ | ✓ | ✓ | ✓ | Chỉ Qwen3.5+ASR ≤1.340B; Gipformer+4B. |
| P2 licence hạn chế | ✓ | ? | Đ | ? | Đ | Đ | ✓ | ✓ | ✓ | **Không xếp hạng cấu hình nộp** trước trả lời BTC. |
| P2 audio-LLM/RL | Đ | Đ | Đ | Đ | Đ | Đ | ✓ | ✓ | ? | **Không dùng** nếu phải clone/reset env hoặc vượt trần. |

## 5. Lộ trình 31/10–16/11

*Thời gian là kế hoạch và có cổng dừng; các job lỗi trên `main` phải được đội phục hồi ở checkout có code trước khi chạy. Tôi không chạy hay sửa job. Mọi lần nộp public do Anh quyết theo `HUMAN_TODO.md`; không chọn cấu hình bằng nhãn test.*

| Mốc | Anh / Claude (agent) | Leader (ASR/Docker) | Quyết định hoặc đầu ra |
|---|---|---|---|
| 31/10–01/11 | [Bằng chứng mạnh] Kiểm hai job lỗi, lấy D score với B-D3/B-up/B-D1 nếu phục hồi hợp lệ; khóa `dev_random`, `dev_lao`, checkpoint, provenance. | Chạy baseline audio→agent hợp lệ từ checkout có code, xuất WER/slot/score; đọc lỗi path. | Anh xác nhận có A30/cloud và chọn baseline public đầu tiên **chỉ nếu** kiểm format và offline đạt. |
| 02–04/11 | [Suy luận] Review D theo cặp, thử 2 epoch, provenance ID trên 1.7B; bắt đầu 4B cloud khi được duyệt. | So Whisper turbo, PhoWhisper, Qwen3-ASR-0.6B theo slot và điểm agent; thử NeMo ITN vi. | Cổng 04/11: loại thay đổi không thắng cả hai dev theo ngưỡng §4. |
| 05–08/11 | [Suy luận] Chốt 4B và guardrail; chỉ làm synthetic lô nhỏ nếu D/4B đã có điểm tin cậy. | Tích hợp ASR thắng cuộc + ITN an toàn, đo p95 A30, bắt đầu image offline. | Anh chọn **một** cặp model/ASR và tối đa một challenger; ghi licence/SHA/tổng tham số. |
| 09–11/11 | [Suy luận] Ablation cuối: grammar hoặc synthetic, mỗi lần một biến; audit Q1/Q3 về cách chấm/call policy. | Test Docker, 5 lượt tái lập, max 30 giây, driver và cold start. | Cổng 11/11: chỉ merge nhánh thắng dev và pass system gate. |
| **12–13/11** | [Bằng chứng vừa] **Đóng băng tính năng**; khóa prompt, adapter, model SHA, seed, split, quyết định giữ/bỏ. | Pin image/runtime; chạy kiểm offline hoàn chỉnh. | Anh ký cấu hình nộp; không đổi model vì một điểm public đơn lẻ. [S39][S43] |
| 14–15/11 | [Suy luận] Chỉ sửa lỗi đóng gói/timeout có phép đo lại; tạo checksum artifact. | Rehearsal A30 từ image nộp, kiểm id/JSON, một env/mẫu, 5/5 giống. | Dành một lượt nộp Docker khi đã pass; giữ khả năng rollback về image đã pass. |
| **16/11 trước 23:59** | [Bằng chứng mạnh] Không mở thí nghiệm mới. | Kiểm artifact cuối và log nộp. | Anh quyết lần nộp cuối; luật cuộc thi lấy **lần cuối**. |

[Suy luận] **Song song hợp lệ:** leader đo ASR/ITN trong khi Claude phân tích D/4B; cùng dùng checkpoint và split đã khóa để kết quả so được. **Đường găng:** score đầu-cuối → chọn ASR + agent → A30/Docker → freeze. Nếu mốc 04/11 vẫn chưa có baseline hợp lệ, ưu tiên sửa đường chạy và Docker; hạ synthetic, grammar, challenger xuống P2. [S10][S39]

## 6. Model ứng viên và cấu hình ghép

**Cách đếm.** [Bằng chứng mạnh] Dùng **tổng** tham số checkpoint từ Hugging Face API/model card, tính cả encoder/vision/audio nếu cùng model; tên `0.6B`, `1.7B`, `E2B`, `4GB` không phải phép chứng minh tuân thủ. Ngày ở bảng là **commit đầu tiên tải trọng số**, kiểm riêng khỏi ngày paper; SHA là revision tại lúc tra 30/10/2026 và phải pin trước nộp. Với checkpoint không có bộ đếm safetensors, ghi `~` theo card/kiến trúc và cần xác minh trước chọn. Quantization đổi byte VRAM, **không đổi số tham số**. Mọi cấu hình cần đo A30 24GB, offline, greedy, 5 lượt, max <30 giây. [S27][S30][S39][S41]

### ASR

| Model | Tổng tham số; licence; ngày trọng số | Bằng chứng tiếng Việt và hạn chế | Quyết định |
|---|---|---|---|
| Whisper large-v3-turbo | 808.878M; MIT; 01/10/2024 [S27] | [Bằng chứng vừa] Baseline đang có; model đa ngôn ngữ, chưa có điểm slot LifeMate. | Đối chứng bắt buộc. |
| PhoWhisper-large | khoảng 1,55B; BSD-3; 19/12/2023 [S25][S54][S26] | [Bằng chứng vừa] Paper Việt và card; model lớn có thể tốt WER nhưng chậm; tổng với 4B vẫn <6B nếu xác minh count. | Đối chứng; cần xác minh tổng exact. |
| PhoWhisper-medium | khoảng 769M; BSD-3; 18/02/2024 [S25][S54][S77] | [Bằng chứng vừa] Phương án nhẹ hơn; chưa có slot LifeMate. | P1 nếu turbo kém và large chậm. |
| Qwen3-ASR-0.6B | **938.009M**; Apache-2.0; 28/01/2026 [S29][S30] | [Bằng chứng vừa] Card hỗ trợ Vietnamese; số trên tên thấp hơn tổng safetensors. | P0 benchmark slot/e2e. |
| Qwen3-ASR-1.7B | **2.349B**; Apache-2.0; 28/01/2026 [S75] | [Bằng chứng vừa] Card hỗ trợ vi; không ghép Qwen3-4B vì tổng >6B. | Chỉ nghiên cứu với LLM 1.7/2B, không ưu tiên. |
| Gipformer1.5-68M-RNNT | khoảng 68M; MIT; 21/08/2026 [S31] | [Bằng chứng vừa] Card tự báo WER Việt nhiều miền, ViMD 7,00; chuẩn hóa khác và code repo chưa rõ licence. | P1 sàng lọc nhanh, kiểm licence code. |
| BuzzASR Vietnamese | 1.543B; MIT; 08/09/2026 [S32] | [Bằng chứng vừa] Card tự báo FLEURS WER 7,26; một ngôn ngữ và chưa biết slot in-domain. | P1 nếu thời gian, không thay baseline theo WER. |
| NVIDIA Parakeet CTC vi | khoảng 600M; NVIDIA Open Model License/gated; 17/01/2026 [S70] | [Bằng chứng vừa] Vietnamese-English code-switch; card có A30, nhưng quyền tải/licence cần xác nhận. | Không xếp cấu hình nộp trước trả lời BTC. |

### LLM

| Model | Tổng tham số; licence; ngày trọng số | Tiếng Việt / tool calling / vLLM | Quyết định |
|---|---|---|---|
| Qwen3-1.7B | **2.032B**; Apache-2.0; 28/04/2025 [S45] | [Bằng chứng mạnh] Đội đã đo LifeMate; vLLM backend hiện có. | Đối chứng 1.7B, không suy là đủ cho private. |
| Qwen3-4B-Instruct-2507 | **4.022B**; Apache-2.0; 05/08/2025 [S44] | [Bằng chứng vừa] Card đa ngôn ngữ, BFCL-v3 61,9 tự báo; hỗ trợ vLLM ≥0.8.5. | P0 ứng viên chính; cần SFT/slot/A30. |
| Qwen3.5-4B | **4.660B**; Apache-2.0; 27/02/2026 [S46] | [Bằng chứng vừa] Card tự báo BFCL-v4 50,3; đa ngôn ngữ, **chưa có số riêng vi**; vLLM main/nightly. | P1 challenger, chỉ ghép ASR nhỏ. |
| Qwen3.5-2B | **2.274B**; Apache-2.0; 01/03/2026 [S76] | [Bằng chứng vừa] Tool calling và runtime cùng họ; tiếng Việt cần đo. | P2 trừ khi 4B quá chậm. |
| Granite-4.2-3B | **3.660B**; Apache-2.0; 07/08/2026 [S48] | [Bằng chứng vừa] Tool calling, BFCL-v4 52,41 **tự báo**; ngôn ngữ hỗ trợ không xác nhận vi; vLLM có, card khuyên sampling. | P2 vì greedy chưa chứng minh. |
| Phi-4-mini-instruct | **3.836B**; MIT; 19/02/2025 [S47] | [Bằng chứng vừa] Có tool calling; tiếng Việt và LifeMate chưa đo; vLLM cần xác minh bản. | P2. |
| SmolLM3-3B | **3.075B**; Apache-2.0; 08/07/2025 [S71] | [Bằng chứng vừa] Tiếng Việt/tool use chưa có bằng chứng gần bài; vLLM cần đo. | P2. |
| FrogNano-4B-2609 | **4.660B**; MIT; 17/09/2026 [S78] | [Bằng chứng vừa] Tool output/coding là miền chính, chưa có Việt; vLLM cần đo. | P2, ghi nhận model mới nhưng không chạy sát hạn. |
| Gemma-4-E2B-it | **5.123B toàn checkpoint**; Apache-2.0; 02/04/2026 [S49] | [Bằng chứng vừa] Có audio + function calling; **dưới 6B** nếu chạy một mình. Cấu phần text LLM có thể <5B sau trừ encoder nhưng cần BTC xác nhận cách tính; chưa có đo tiếng Việt/tool LifeMate. | P2/chưa xếp cấu hình nộp. |
| Nemotron 3.5 Bolt E4B | **~8B tổng**; OpenMDW-1.1; 23/10/2026 [S79] | [Bằng chứng mạnh] 4B là effective; tổng >6B. | **Loại** khỏi bài nộp. |
| xLAM-2-3b-fc-r; Hammer2.1-3b | **3.086B; 3.085B**; CC-BY-NC-4.0 / qwen-research; 28/03/2025; 12/12/2024 [S50][S51] | [Bằng chứng vừa] Tool-focused nhưng licence cần BTC trả lời; không có Việt LifeMate. | **Không xếp hạng** trước xác nhận. |

### Cấu hình ghép đủ căn cứ về trọng số/licence/tổng tham số

| Cặp ASR + LLM | Tổng tham số tính từ nguồn | Cổng còn thiếu | Ưu tiên |
|---|---:|---|---|
| Whisper turbo + Qwen3-4B-2507 [S27][S44] | **4.831B** | [Suy luận] A30 latency/VRAM, slot, 5 lượt, offline cần đo. | P0 baseline nộp |
| Qwen3-ASR-0.6B + Qwen3-4B-2507 [S30][S44] | **4.960B** | [Suy luận] Adapter/runtime Qwen ASR; A30 cần đo. | P0 challenger ASR |
| Gipformer 68M + Qwen3-4B-2507 [S31][S44] | **~4.090B** | [Suy luận] Xác minh code licence, slot, A30. | P1 |
| BuzzASR vi + Qwen3-4B-2507 [S32][S44] | **5.566B** | [Suy luận] Lớn/chậm; A30 cần đo. | P1 |
| Whisper turbo + Qwen3.5-4B [S27][S46] | **5.469B** | [Suy luận] vLLM main/nightly, A30, SFT, 5 lượt cần đo. | P1 |
| Qwen3-ASR-0.6B + Qwen3.5-4B [S30][S46] | **5.598B** | [Suy luận] Hai runtime cùng GPU; A30 cần đo. | P1 |
| Qwen3-ASR-1.7B + Qwen3-1.7B [S45][S75] | **4.381B** | [Suy luận] Agent 1.7B yếu trên app chưa thấy; A30 cần đo. | P2 |
| Qwen3-ASR-1.7B + Qwen3-4B-2507 [S44][S75] | **6.372B** | [Bằng chứng mạnh] Vượt tổng <6B. | **Không dùng** |
| PhoWhisper-large + Qwen3.5-4B [S26][S46] | **~6.210B** | [Bằng chứng mạnh] Vượt tổng <6B nếu count large ~1.55B. | **Không dùng** |

[Bằng chứng vừa] Việc rà riêng giai đoạn **01/06–25/10/2026** tìm thấy trọng số mới của Granite-4.2-3B, FrogNano-4B và Nemotron Bolt, cùng ASR Gipformer/Buzz. Qwen3.5-4B có trọng số từ tháng 02, chỉ được kiểm lại trong đợt rà này. Ngày paper EMNLP 24–29/10 không được dùng làm ngày trọng số của bất kỳ model nào [S9][S14][S31][S32][S46][S48][S78][S79].

## 7. Repo và thư viện có thể dùng

*Ngày cột “bảo trì” là `pushed_at` của repo công khai khi tra 30/10/2026 (UTC có thể sang 31/10); nó chỉ cho biết hoạt động, **không** chứng minh chất lượng. Repo nào ghi licence chưa rõ chỉ dùng để đọc ý tưởng, không sao chép code vào bài nộp. Model weight licence được xét riêng ở §6.*

| Repo/thư viện | Licence; bảo trì gần nhất | Dùng cho; rủi ro |
|---|---|---|
| [When2Call](https://github.com/NVIDIA/When2Call) [S64] | Apache-2.0; 29/04/2025 | [Bằng chứng vừa] Mode ask/call/cannot; dữ liệu tiếng Anh, nhãn khác `[]`. |
| [ToolSandbox](https://github.com/apple-aiml-research/ToolSandbox) [S65] | Chưa xác nhận; 11/09/2026 | [Bằng chứng vừa] Thiết kế stateful/insufficient info; không tái dùng code trước licence. |
| [ToolBench](https://github.com/OpenBMB/ToolBench) [S66] | Apache-2.0; 21/05/2025 | [Bằng chứng vừa] Tool retrieval/trajectory; quy mô API khác. |
| [NeMo text processing](https://github.com/NVIDIA/NeMo-text-processing) [S52][S74] | Apache-2.0; 29/10/2026 | [Bằng chứng mạnh] ITN vi; kiểm dependency/edge cases. |
| [dateparser](https://github.com/scrapinghub/dateparser) [S23] | BSD-3-Clause; 30/10/2026 | [Bằng chứng vừa] Parse ngày; chưa chứng minh khẩu ngữ vi. |
| [Duckling](https://github.com/facebook/duckling) [S22] | Licence chưa xác nhận từ API; 15/03/2026 | [Bằng chứng vừa] Time parsing VI_XX; có thể thiếu ngày tương đối. |
| [OpenAI Whisper](https://github.com/openai/whisper) [S53] | MIT; 31/08/2026 | [Bằng chứng mạnh] ASR baseline; thiếu ITN theo slot BTC. |
| [PhoWhisper](https://github.com/VinAIResearch/PhoWhisper) [S54] | BSD-3-Clause; 12/11/2024 | [Bằng chứng vừa] ASR Việt; model large nặng. |
| [Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR) [S62] | Apache-2.0; 26/06/2026 | [Bằng chứng vừa] Inference offline/vLLM; adapter và số tham số thật cần kiểm. |
| [Gipformer](https://github.com/ggroup-ai-lab/gipformer) [S63] | Licence code chưa rõ; 17/09/2026 | [Bằng chứng vừa] RNNT/ONNX Việt; model weight MIT nhưng code khác điều kiện. |
| [vLLM](https://github.com/vllm-project/vllm) [S55][S39] | Apache-2.0; 31/10/2026 UTC | [Bằng chứng mạnh] Backend offline; pin version và chế độ tái lập. |
| [SGLang](https://github.com/sgl-project/sglang) [S56] | Apache-2.0; 31/10/2026 UTC | [Bằng chứng vừa] Backend đối chứng; đổi engine sát hạn tốn QA. |
| [XGrammar](https://github.com/mlc-ai/xgrammar) [S57] | Apache-2.0; 29/10/2026 | [Bằng chứng vừa] JSON grammar; chỉ bảo đảm cú pháp. |
| [Outlines](https://github.com/dottxt-ai/outlines) [S58] | Apache-2.0; 21/09/2026 | [Bằng chứng vừa] Structured output; cần tích hợp backend. |
| [llguidance](https://github.com/guidance-ai/llguidance) [S59] | MIT; 29/10/2026 | [Bằng chứng vừa] Grammar nhanh; phụ thuộc phiên bản vLLM. |
| [TRL](https://github.com/huggingface/trl) [S60] | Apache-2.0; 30/10/2026 | [Bằng chứng vừa] DPO/GRPO nghiên cứu sau freeze; reward LifeMate cần kiểm. |
| [verl](https://github.com/volcengine/verl) [S61] | Apache-2.0; 30/10/2026 | [Bằng chứng vừa] RL rollout; tích hợp env và compute lớn. |

## 8. Bảy điểm phản biện lựa chọn hiện tại

1. **Nối tầng so với audio-LLM.** [Bằng chứng vừa] **Đồng ý giữ nối tầng.** SLURP/STOP chứng minh speech parsing là hướng nghiên cứu, không chứng minh gọi ToolEnv Việt với hash. Voxtral 4,676B không có bằng chứng tiếng Việt gần bài; Qwen2.5-Omni-3B có 5,537B tổng (<6B) nhưng licence qwen-research; Gemma-4-E2B 5,123B cũng <6B và có audio/function calling nhưng chưa có đo Việt/tool LifeMate. Cách BTC tính cấu phần LLM vẫn cần xác nhận. Nối tầng cho phép chọn ASR theo slot và đổi độc lập [S35][S36][S37][S38][S49]. Sẽ xét lại khi có e2e score/latency thắng theo cặp—hiện chưa có.
2. **1.7B LoRA r32 một epoch rồi 4B.** [Bằng chứng vừa] **Đồng ý dùng 1.7B làm thí nghiệm rẻ, không đồng ý coi 53,92 là mức trần.** Điểm train 80,22 so dev 53,92 và dev_lao 35,53 cho thấy generalization là vấn đề, nhưng không cô lập epoch hay cỡ model. 4B-2507 có tool-use prior trên BFCL-v3; thử 2 epoch (A) và 4B với compute/augment khớp, giữ theo dev_lao và A30, không đổi sang Granite/FrogNano chỉ vì benchmark card [S9][S44][S48][S78].
3. **Thiết kế D.** [Bằng chứng vừa] **Đồng ý cặp phản thực tế, đối chứng nhân bản và khớp bước; chưa đồng ý mở rộng từ 77 mẫu.** 25 tool đích và top3 chiếm 47%, 23 cặp eval không bảo đảm phủ app mới. When2Call/EFPL ủng hộ mode rõ ràng; ToolWeave nhắc provenance. Đối chứng rẻ hơn trước DPO là cân lại ca ask thật, thêm cặp thiếu/đủ slot ở tool ít xuất hiện, audit nhãn bằng người, rồi kiểm execute không giảm [S5][S9][S14].
4. **Chữ chuẩn trước, audio sau.** [Bằng chứng mạnh] **Đồng ý thứ tự để gỡ lỗi agent, nhưng phải chuyển sang đầu-cuối ngay.** Dùng `audio_text` giúp cô lập lỗi quyết định; điểm nộp là từ audio. Job đầu-cuối hiện fail, nên 53,92/35,53 chưa ước lượng được private. Paper/benchmark ASR Việt cho thấy WER và miền biến động; ưu tiên hồi phục baseline trước fine-tune ASR [S25][S54][S28][S33].
5. **Bộ chấm local khắt khe.** [Bằng chứng vừa] **Đồng ý dùng làm lower-bound vận hành cho exact-match**, vì README chính thức nói `x-match: fuzzy` có ngoại lệ và call rejected vẫn tính. BFCL và ToolSandbox có cách chấm riêng nên không xác nhận tokenization/case/order của BTC [S1][S6]. Một lần nộp public có mục tiêu kiểm sai khác aggregate giữa scorer/local và server, không dò nhãn test hay chỉnh ví dụ test. Q1 vẫn cần BTC xác nhận; mọi kết luận về “lower bound” là suy luận vì local có thể khác theo nhiều hướng.
6. **Moat synthetic đúng chính sách.** [Suy luận] **Đồng ý hướng dài hạn, không đồng ý làm bộ lớn trong 16 ngày.** APIGen/ToolWeave cho quy trình khả thi; replay D chỉ xác minh thực thi. Bản nhỏ nhất: 3–5 nhóm tool có read→write và ask, 100–300 mẫu train-only, provenance mọi tham số, audit 50, đối chứng nhân bản real; chỉ mở rộng nếu dev_lao thắng [S11][S14][S17].
7. **Rủi ro chưa nhìn thấy.** [Bằng chứng vừa] (a) Tên kích thước model che tổng tham số: Qwen3-ASR “0.6B” có 938M; Nemotron “E4B” có 8B tổng [S30][S79]. (b) vLLM greedy có thể không tái lập theo batch; `Agent.run` không ngắt một generate quá dài [S39][S40]. (c) Model card khác chuẩn benchmark và script WER chuẩn hóa số có thể che lỗi slot [S31][S46]. (d) Lịch đang bị lỗi checkout/job, trước mọi nghiên cứu model phải có pipeline hợp lệ. (e) `state_hash` làm call ghi thừa nguy hiểm hơn format JSON, nên ép format không đủ [S18][S19].

## 9. Câu hỏi mở và thí nghiệm nhỏ

| Câu hỏi trong PIPELINE/HUMAN_TODO | Điều chưa biết | Thí nghiệm nhỏ, kết quả cần báo |
|---|---|---|
| Q1, Q8 | [Chưa kiểm chứng] Tokenization/case/list/order của scorer local có đúng server? | [Suy luận] Một baseline public hợp lệ do Anh nộp; so **aggregate** với scorer local cùng artifact, ghi sai khác theo nhóm nhưng không đọc nhãn test. Nếu lệch, xin BTC làm rõ quy tắc chấm. [S1][S6] |
| Q2, Q3, Q17 | [Suy luận] Chính sách BTC quyết read/filter/write theo dấu hiệu nào? | Audit 50 trajectory **train** chia theo provenance tham số; viết rule từ train; kiểm lỗi trên dev_lao chưa nhìn. So lô synthetic với nhân bản real. [S11][S14] |
| Q4, Q5 | [Bằng chứng mạnh] Đội biết 0/23 ask app giữ riêng; chưa biết D thắng không. | D đối chứng khớp bước; confusion ask/execute/OOS, precision/recall và hash theo hai split; audit false ask. [S5][S9][S10] |
| Q6 | [Suy luận] Leave-apps-out đã mô phỏng private đủ chưa? | Giữ nguyên `dev_random` và `dev_lao`; thêm leave-*group*-out chỉ từ train nếu nhóm app có đủ mẫu; báo variance theo app, không thay split cũ. [S1][S43] |
| Q7 | [Bằng chứng vừa] Mỗi ngày 5 lượt public có thể làm đội overfit. | Quy tắc đặt trước: nộp khi thay đổi đã thắng cả hai dev/cổng hệ thống; tối đa một lần thăm dò kỹ thuật cho mỗi giả thuyết; không chọn ngưỡng theo điểm public lặp. [S43][S73] |
| Q9–Q11 | [Chưa kiểm chứng] Lỗi ASR nào đổi quyết định tool, history audio có đáng cải thiện? | Cùng id hai dev, thay riêng ASR lượt cuối rồi ASR history; đo slot miss, ∆score và latency. Nhóm phủ định/số/tên lấy từ nhãn train/dev, không từ test. [S25][S54][S28][S34] |
| Q12, Q13 | [Chưa kiểm chứng] ITN/tính ngày/số cứu bao nhiêu hash? | A/B NeMo ITN và helper ngày có điều kiện; audit 50 ca bị đổi; đo exact params, score subset và toàn split. [S20][S74] |
| Q14 | [Chưa kiểm chứng] Ép JSON/enum/ID có giảm call thừa hơn hại semantic? | Grammar chỉ JSON+enum chắc chắn trước; ID guardrail riêng; so invalid, ∆score, latency trên hai dev. [S18][S19] |
| Q15 | [Chưa kiểm chứng] 2 epoch 1.7B, 4B, Qwen3.5 khác nhau ra sao khi so công bằng? | Ba nhánh khớp dữ liệu/token/steps theo điều kiện train khả thi; text trước, audio sau; đo p95 A30. [S44][S45][S46] |
| Q16, Q19, Q20 | [Bằng chứng mạnh] Chưa chứng minh tái lập/30 giây/Docker. | Image pinned offline, cùng 2 dev × 5 lượt, kiểm checksum output, max latency, một env/mẫu, cold start; freeze 12–13/11. [S39][S40][S41] |
| Q18 | [Suy luận] Nhiễu lời nói nào tăng private mà không làm sai nhãn? | Chỉ sinh text train paraphrase có giữ slot/negation; ASR-style augmentation ablation theo cặp, audit provenance. TTS chỉ khi ASR slot còn là nút thắt và licence rõ. [S7][S17][S28] |

[Suy luận] **Độ phân giải của dev:** 233 và 262 mẫu không đủ để tin một mức tăng 1–2 điểm chỉ dựa vào điểm trung bình. Kết quả giữ/bỏ ở §4 là rào vận hành, không là kiểm định thống kê. Báo khoảng tin cậy bootstrap theo cặp, số mẫu đổi từ sai→đúng và đúng→sai, cụm app/origin; nếu CI phủ cả tăng và giảm đáng kể, giữ baseline an toàn. [S10][S43]

## 10. Phụ lục: truy vấn, nguồn loại và giới hạn

### Truy vấn web đã dùng (không chứa dữ liệu thi)

`BFCL v4 missing parameter multi turn leaderboard`; `Hammer function masking on-device tool use`; `When2Call ask tool cannot answer`; `APIGen-MT execution verification`; `ToolWeave parameter provenance`; `ToolRL verifiable reward`; `2026 EMNLP ask answer act planner`; `Vietnamese ASR 2026 model card release`; `Qwen3-ASR-0.6B Vietnamese`; `Gipformer 68M WER`; `NeMo text processing Vietnamese ITN release`; `vLLM reproducibility batch invariance`; `A30 FP8 support`; `2026 small LLM 4B tool calling`; `Zalo AI Challenge 2026 LifeMate public writeup`; `VLSP 2025 ASR system`. [S1][S9][S14][S16][S30][S31][S39][S74][S80]

### Nguồn đã xem nhưng không dùng làm bằng chứng chính

| Nguồn/nhóm | Lý do |
|---|---|
| Blog so sánh “best small LLM 2026” và bài Reddit xếp hạng 4B | [Bằng chứng vừa] Không có protocol LifeMate, thường trộn effective với total params; bảng model dùng card/Hub API. [S44][S46][S49] |
| `vinorm` [S24] | [Bằng chứng vừa] Hướng số→lời nói, không phải ITN cần gắn sau ASR; licence chưa xác nhận. |
| Gemma-4-E2B, Nemotron Bolt [S49][S79] | [Bằng chứng mạnh] Gemma E2B tổng 5,123B **dưới 6B** nhưng cấu phần LLM và điểm Việt/tool cần xác minh; Nemotron Bolt khoảng 8B vượt trần hệ thống. |
| Qwen2.5-Omni-3B [S38] | [Bằng chứng mạnh] Tổng 5,537B **dưới trần hệ thống 6B**; licence qwen-research cần BTC xác nhận, cấu phần LLM <5B và chất lượng tiếng Việt/tool calling chưa đủ căn cứ. |
| xLAM-2-3b, Hammer2.1-3b, Parakeet vi [S50][S51][S70] | [Bằng chứng vừa] Licence NC/qwen-research/NVIDIA gated không được tự suy là hợp lệ; không xếp hạng. |
| ToolForge 8B [S15], ToolWeave 70B [S14] | [Bằng chứng mạnh] Paper hữu ích về cách sinh dữ liệu nhưng model thí nghiệm vượt trần và benchmark khác. |
| ToolWeave repo cập nhật 27/10/2026 | [Bằng chứng vừa] Paper đã mở nhưng code repo cập nhật sau mốc rà trọng số; không đưa vào đường nộp 16/11. [S14] |
| Thảo luận/nguồn có thể chứa transcript hoặc nhãn public/private test | [Bằng chứng mạnh] Không mở và không dùng theo luật cuộc thi. Không ghi URL cụ thể để tránh lan truyền. |

### Giới hạn và điều cần xác nhận

[Bằng chứng mạnh] Báo cáo dựa trên tài liệu nội bộ đã đọc, README chính thức, mã `e2e-baseline` qua `git show` và checkout `~/zac-jobs/lifemate/` **chỉ đọc**, cùng nguồn công khai mở ngày 30/10/2026. Không đọc `*_environment/`, không chạy train/eval/ASR/GPU, không dùng nhãn test. Tôi chỉ ghi hai tệp trong `docs/research/`. `phase2_d.log` và `e2e_baseline.log` không có điểm sau lỗi path/import; mọi kết luận D/e2e vẫn treo cho tới khi đội chạy hợp lệ. Không có benchmark trên A30 hoặc Docker, nên mọi dòng liên quan hiệu năng ghi **cần đo**. Model card có số tự báo, quy trình đánh giá khác nhau; không cộng mức tăng paper vào điểm dev. [S9][S31][S39][S46]

[Chưa kiểm chứng] PDF PhoWhisper trên OpenReview chặn truy cập trực tiếp khi rà nguồn; thông tin 844 giờ và checkpoint trong báo cáo được đối chiếu qua repository chính thức của nhóm tác giả. Không dùng PDF đó làm nguồn duy nhất cho một kết luận. [S25][S54]

[Suy luận] Nguồn CSV ghi URL, loại bằng chứng, licence, ngày upload trọng số, tổng tham số và revision nơi có thể kiểm. Một vài repo ghi “licence chưa rõ” hoặc tham số `~`; chúng là đối tượng đọc/đo, chưa phải cấu hình nộp. Câu hỏi Q1 về server scorer và quyền licence hạn chế chỉ BTC trả lời được. Đội nên khóa quyết định trước khi xem điểm public tiếp theo. [S43][S73]




