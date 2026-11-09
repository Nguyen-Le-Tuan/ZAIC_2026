# Prompt cho Codex: tìm model và tổ hợp model sát trần tham số nhất cho LifeMate

> **Cách dùng (Leader):** mở terminal ở `/home/nguyenletuan/Desktop/ZAIC_2026`, chạy Codex với **web search bật** và mức suy luận cao nhất mà bản Codex của bạn hỗ trợ. Ví dụ `codex --search`; nếu bản của bạn đặt tuỳ chọn ở chỗ khác thì bật trong cấu hình. Sau đó gõ:
> *"Đọc và làm đúng theo `docs/CODEX_MODEL_COMBOS_PROMPT_2026-11-08.md`. Pha D: không làm."*
> (Muốn Codex chạy thử ASR nhỏ trên CPU thì đổi thành *"Pha D: cho phép"*; xem mục 7.)
>
> Claude viết ngày 08/11/2026 theo yêu cầu của Leader. Từ đây trở xuống là chỉ dẫn cho Codex.

---

## 0. Vai trò, mục tiêu, sản phẩm

**Vai trò:** nhà nghiên cứu tìm kiếm, độc lập và phản biện, có toàn quyền tra cứu Internet. Bạn làm việc cùng Claude:
- **Bạn:** quét Internet thật rộng và thật sâu, kiểm chứng từng con số, lập các tổ hợp hợp lệ.
- **Claude:** đọc báo cáo của bạn, xếp hạng phương án, rồi chạy thí nghiệm GPU/API theo thứ tự đội duyệt.

**Câu hỏi trung tâm:**

> *Trong giới hạn của đề (toàn hệ thống dưới 6B tham số, LLM dưới 5B, context tối đa 16.384 token, offline, 30 giây mỗi mẫu trên máy chấm), **tổ hợp model nào** (ASR, LLM, model phụ, hoặc speech-LLM) và **cách dùng model nào** (kể cả những cách ít người biết) cho điểm private cao nhất, mà đội còn kịp kiểm chứng và đóng gói trước khoảng 13/11/2026?*

Leader tin rằng BTC đặt trần như vậy là có chủ đích: tồn tại những tổ hợp model với số tham số khác nhau, hoặc những cách dùng model mới lạ, mà một lần tìm kiếm hời hợt sẽ bỏ sót. **Nhiệm vụ của bạn là tìm ra chúng.** Nếu sau khi tìm kỹ mà kết luận là không có, hãy chứng minh bằng độ phủ tìm kiếm (mục 6), đừng kết luận sớm.

**Sản phẩm** (chỉ tạo file mới; mục 1, luật 1):
1. `docs/research/CODEX_MODEL_COMBOS_2026-11-08.md`: báo cáo bằng tiếng Việt, giữ thuật ngữ tiếng Anh, theo cấu trúc ở mục 8.
2. `docs/research/model_candidates_2026-11-08.csv`: mỗi dòng một model hoặc thành phần (schema ở mục 8).
3. `docs/research/model_combos_2026-11-08.csv`: mỗi dòng một tổ hợp (schema ở mục 8).
4. `docs/research/model_sources_2026-11-08.csv`: nguồn, cùng schema với `docs/research/codex_sources_2026-10-31.csv`.
5. `docs/research/CODEX_MODEL_COMBOS_progress_2026-11-08.md`: nhật ký tiến độ, **cập nhật sau mỗi pha**, để nếu phiên bị ngắt thì không mất kết quả.
6. Script tra cứu (nếu viết): `docs/research/tools/` (chỉ code, không chứa dữ liệu thi).

Khi xong, trả lời trong chat bằng 15–20 dòng tóm tắt, kèm top 5 tổ hợp và đường dẫn các file.

---

## 1. Luật an toàn (bắt buộc)

Máy này là laptop của Leader: RTX 3050 4 GB, RAM 14 GB (thường chỉ trống khoảng 3 GB), **ổ cứng chỉ còn khoảng 27 GB**.

1. **Git: không đổi trạng thái.** Nhánh hiện tại `codex/docker-phoft` có việc Docker chưa commit của Leader (`lifemate/Dockerfile`, `lifemate/.dockerignore`, `docs/DOCKER_PHOFT_SOLUTION.md`, …).
   - Cấm: `checkout`, `switch`, `stash`, `reset`, `pull`, `merge`, `rebase`, `commit`, `add`, `push`, `clean`, `restore`.
   - Được: `git fetch -q origin`, `log`, `show`, `diff`, `branch -a`, `ls-files`. Đọc file ở nhánh khác bằng `git show origin/<nhánh>:<đường dẫn>`.
   - Không sửa, không xoá file nào đang có. Chỉ tạo các file mới liệt kê ở mục 0.
2. **Không dùng GPU, không train, không chạy LLM.** Không chạy `lifemate.train`, `lifemate.infer`, `lifemate.asr`, `predict.sh`, Docker.
3. **Không tải trọng số model**, trừ Pha D khi được cho phép. Tra cứu bằng HF API, `config.json`, `*.safetensors.index.json` và model card là đủ. Lý do: ổ cứng gần đầy, và Leader đang dùng máy.
4. **Không gọi API trả phí** (Meta, OpenAI, Anthropic…). Không đăng nhập web, không đăng bài lên forum hay hỏi BTC; câu hỏi cho BTC thì soạn sẵn vào báo cáo.
5. **Dữ liệu thi** (licence cấm phát tán; repo GitHub đang public):
   - **Không bao giờ đọc** `data/train+public_test/*/*_environment/`. Luật thi cấm.
   - **Không dán** câu nói, nhãn, transcript hay kết quả tool vào ô tìm kiếm hay dịch vụ ngoài. Truy vấn web chỉ chứa tên model, tên kỹ thuật, tên benchmark.
   - Báo cáo chỉ nêu id mẫu, không chép nguyên văn dữ liệu.
   - Cấm gán nhãn public/private test. Không dùng dự đoán public làm dữ liệu train.
6. **Không bịa.** Đây là yêu cầu quan trọng nhất:
   - Mỗi model phải được kiểm là **có thật**: trang Hugging Face (hoặc ModelScope, GitHub release) trả về 200, ghi `repo_id` chính xác.
   - Số tham số phải là **số đếm thật**, không lấy từ tên model ("4B", "E2B", "0.6B" thường sai). Cách đếm ở mục 6.3.
   - Mỗi con số trong báo cáo có nguồn (URL và ngày truy cập) và nhãn bằng chứng (mục 8).
   - Danh sách gợi ý ở mục 5 do Claude viết từ trí nhớ (kiến thức của Claude dừng ở giữa năm 2026). **Có thể sai tên hoặc không tồn tại.** Kiểm từng cái; cái nào không có thì ghi "không tìm thấy", đừng đoán.

---

## 2. Đề bài và ràng buộc (bản đủ: `git show origin/main:JOURNAL.md`, mục 1)

**Bài toán:** audio tiếng Việt (lượt nói cuối, cộng audio các lượt user trong history) → agent gọi tool trên môi trường giả lập `zaic_tools.ToolEnv` → nộp `{"id", "tool_calls", "state_hash"}` mỗi mẫu.

**Chấm điểm:** gold rỗng thì nộp rỗng được 1. Ngược lại, hash trạng thái sai là 0; hash đúng thì điểm là F1 giữa call nộp và call đáp án (tham số không fuzzy phải giống hệt, fuzzy cần token-F1 > 0,6). Một lệnh ghi sai là cả mẫu về 0.

**Ràng buộc theo ghi chép của đội** (bạn phải tìm lại **nguyên văn chính thức**, xem R0):
- Toàn hệ thống (ASR + LLM + mọi thành phần khác) **dưới 6B** tham số. LLM **dưới 5B**, context tối đa **16.384** token.
- Offline hoàn toàn khi chấm, greedy hoặc temperature 0, seed cố định. Nếu kết quả không tái lập, BTC chạy 5 lần lấy trung bình.
- **Máy chấm** (theo Docker Guide của BTC, `docs/BTC_DOCKER_GUIDE_2026-11-06.md` trên `origin/main`): **RTX 5090 32 GB, driver 595.58.03, CUDA 13.2**. Luật gốc ghi A30 24 GB; hãy xác nhận bản nào là cuối cùng. **30 giây mỗi mẫu** tính cả ASR; đội đặt hạn nội bộ 25 giây.
- Model và dữ liệu phải công khai, **phát hành trước 26/10/2026**, licence cho phép.
- Được dùng LLM hoặc TTS ngoài để sinh dữ liệu **lúc phát triển** (model chỉ dùng lúc phát triển không nằm trong hệ thống nộp), kể cả từ catalog và `zaic_tools` của public_test (BTC đã xác nhận với đội). Cấm gán nhãn audio hay yêu cầu của tập test.
- Phân hạng khi bằng điểm: thời gian trung bình mỗi mẫu thấp hơn xếp trên.

**Lịch:** Docker hạn **16/11/2026 23:59 GMT+7**, nộp tối đa 2 lần, lấy lần cuối. Private test 20–23/11. Đội muốn chốt model khoảng **13/11** để còn đóng gói và kiểm lại. Vậy phương án nào cần train lại thì phải train và chấm được trong khoảng 11–13/11.

**Nguồn chính thức cần tìm và trích:** trang cuộc thi Zalo AI Challenge 2026 (đề LifeMate), thể lệ, FAQ, forum, và Docker Guide: `https://dl-challenge.zalo.ai/2026/lifemate_argfzdgert/Docker_Guide_ZAC2026_LifeMate.pdf`.

---

## 3. Hệ thống hiện tại và các con số đã đo

**Cấu hình đang nộp** (public 51,16; bản thử cấu hình nộp cuối 51,07):

| Thành phần | Model | Tham số (đếm thật) |
|---|---|---:|
| ASR | `vinai/PhoWhisper-large` (rev `b9136a44`) + LoRA đã merge | 1.543.304.960 |
| LLM | `Qwen/Qwen3-4B-Instruct-2507` (rev `cdbee75f17c0`), nạp NF4 4-bit | 4.022.468.096 |
| Adapter | LoRA r32 (chưa merge vì nạp 4-bit) | 66.060.288 |
| **Tổng** | | **5.631.833.344** |

**Ngân sách còn dư thật ra không nhiều:** dưới 6B còn **0,368B**; dưới trần LLM 5B còn 0,911B (nếu tính cả LoRA). Khi LLM đã sát 5B, phần còn lại cho ASR và mọi thành phần khác chỉ khoảng 1,0B. **Đánh đổi chính là giữa kích thước ASR và kích thước LLM**, cộng các cách "làm gọn" model để nhét được nhiều năng lực hơn vào cùng ngân sách.

**Điểm đã đo** (dev nội bộ; public thường cao hơn dev gộp khoảng 2–3 điểm):

| Hệ thống | Điểm |
|---|---:|
| Qwen3-1.7B → **Qwen3-4B** (cùng công thức, chữ ASR, gộp 495 dòng) | 33,07 → **46,17** (+13,1) |
| Cùng 4B, chữ chuẩn (không lỗi ASR) | 59,15 |
| 4B: dev_random / dev_lao (app chưa thấy), chữ chuẩn | 65,61 / 53,40 |
| 4B: dev_random / dev_lao, chữ ASR | 54,01 / 39,20 |
| Whisper-turbo-ft → PhoWhisper-large-ft (cùng agent) | public 46,29 → 51,16 |
| Cùng pipeline, agent là model API mạnh | public 75,52 |
| Top cột SLM trên bảng public (04/11) | 96,66 |

**Bài học từ các con số:**
- **Tăng dung lượng LLM là đòn bẩy lớn nhất từng đo được:** 1,7B → 4B cho +13 tới +17 điểm. Đổi ASR tốt hơn cho khoảng +2 (dev) tới +5 (public).
- ASR làm mất khoảng 13 điểm, và lỗi ASR hại app chưa thấy gấp đôi.
- 65% mẫu public có cài app không có trong train. Theo dự đoán của chính bản 51,16, 43% mẫu public có gọi tool của 11 app mới đó.
- Trace của bản 51,16 cho thấy model **kẹt vòng lặp đọc** ở app mới (gọi lại `event_tickets.search`, `stocks.get_quote` tới hết 8 bước, không gửi lệnh ghi) và **bịa mã** (mã cổ phiếu) khi không có tool tra cứu. Model nào suy luận tốt hơn trên schema lạ sẽ có lợi.
- Cùng công thức train hai lần lệch 2–4 điểm. Mọi đề xuất phải tính đến nhiễu này.

**Đã thử và không giúp** (đừng đề xuất lại y nguyên): agent học trên chữ ASR; nhân bản mẫu hỏi lại; prompt in thêm `x-ref`/`returns`; dữ liệu sinh bằng LLM (hai pilot); luật bỏ tham số hiếm; train thêm epoch; bf16 thay 4-bit (chênh trong nhiễu).

**Năng lực tính toán của đội:** laptop RTX 4070 8 GB (QLoRA 4B, khoảng 6 giờ mỗi epoch trên đủ train); máy RTX 3050 4 GB này; máy 2× RTX 4090 của người quen (1 lần chạy mỗi ngày); có thể **thuê GPU cloud** nếu đáng (bạn ước giá, đội quyết); khoảng 90 USD credit API Meta (chỉ dùng lúc phát triển).

**Code liên quan** (đọc để biết đổi model tốn công thế nào): `lifemate/lifemate/prompt.py` (ChatML Qwen, thẻ `<tool_call>`), `agent.py` (backend HF và vLLM), `train.py` (LoRA trên `q/k/v/o/gate/up/down_proj`, `AutoModelForCausalLM`), `asr.py` (`WhisperForConditionalGeneration`, greedy, từng file). Môi trường đang pin: torch 2.15.0, transformers 5.21.0, peft 0.21.2.

---

## 4. Đã có gì từ lần tra cứu trước (31/10) — kiểm lại và mở rộng, đừng làm lại từ đầu

Đọc `docs/research/CODEX_DEEP_RESEARCH_2026-10-31.md`, mục 6 và 7. Lần đó đã ghi nhận, kèm số đếm từ HF API:
- **LLM:** Qwen3.5-4B (4,660B; Apache-2.0; 27/02/2026; BFCL-v4 tự báo 50,3; cần vLLM mới); Qwen3.5-2B (2,274B); Granite-4.2-3B (3,660B); FrogNano-4B-2609 (4,660B; MIT; 17/09/2026); Phi-4-mini-instruct (3,836B); SmolLM3-3B (3,075B); Gemma-4-E2B-it (5,123B toàn checkpoint, có audio); Nemotron 3.5 Bolt E4B (khoảng 8B, loại); xLAM-2-3b-fc-r và Hammer2.1-3b (licence cần hỏi).
- **ASR:** Whisper-large-v3-turbo (808,9M); PhoWhisper-medium (khoảng 769M); Qwen3-ASR-0.6B (938,0M; Apache-2.0; 28/01/2026; có tiếng Việt); Qwen3-ASR-1.7B (2,349B); Gipformer1.5-68M-RNNT (khoảng 68M; MIT; 21/08/2026; tự báo ViMD WER 7,00); BuzzASR Vietnamese (1,543B; MIT; 08/09/2026); NVIDIA Parakeet CTC vi (khoảng 600M; licence NVIDIA, gated).
- **Tổ hợp đã tính:** ví dụ Gipformer + Qwen3-4B khoảng 4,09B; Whisper-turbo + Qwen3.5-4B 5,469B; PhoWhisper-large + Qwen3.5-4B khoảng 6,21B (vượt trần).

**Chưa ai trong đội thử Qwen3.5-4B hay bất kỳ ASR nhỏ nào.** Lần này cần: kiểm lại các số trên (nhất là Qwen3.5-4B có gồm vision tower không; nếu bỏ phần không dùng thì phần text còn bao nhiêu), quét rộng hơn nhiều, quét kỹ giai đoạn **06/2026–25/10/2026**, và tìm các **cách dùng mới** (R5).

---

## 5. Câu hỏi nghiên cứu (R0–R8), theo thứ tự ưu tiên

Mỗi câu ghi: cần tìm gì, gợi ý hạt giống (phải kiểm), và tiêu chí. Mỗi nhóm cần đủ độ phủ tối thiểu ở mục 6.4.

### R0. Luật đếm tham số và điều kiện hợp lệ (làm trước tiên)

- Trích **nguyên văn** luật về giới hạn tham số, context, ngày phát hành, licence, phần cứng chấm. Ghi "dưới" hay "không quá" 6B và 5B, và đơn vị B là 10^9 hay khác.
- Luật **đếm thế nào**: tổng tham số mọi thành phần nạp lúc suy luận? Có tính embedding không (tied embedding đếm một lần)? MoE tính tổng hay active? Encoder–decoder tính cả hai? Với speech-LLM hay omni model, phần nào là "LLM"? Tower không dùng (vision, talker) mà bỏ ra khỏi checkpoint thì có được không? LoRA đã merge thì không cộng thêm; adapter không merge thì cộng. Draft model của speculative decoding, verifier, model phân loại nhỏ có tính không? Nhiều LLM cùng lúc: trần 5B áp cho từng LLM hay tổng các LLM? n-gram LM có tính là "model" không?
- **Model đã sửa:** cắt vocab, prune lớp, nén low-rank, distill một model mở thành model nhỏ hơn: có được coi là "model mã nguồn mở phát hành trước 26/10" không, khi model gốc hợp lệ và licence cho phép sửa?
- Kết quả gồm: (a) cái gì luật nói rõ; (b) cái gì phải suy luận; (c) **danh sách câu hỏi soạn sẵn để đội gửi BTC**, xếp theo mức ảnh hưởng tới lựa chọn tổ hợp.

### R1. LLM tối đa 5B: kho ứng viên, ưu tiên dải 4,3–4,99B

Tìm mọi LLM mở (dense, MoE, hybrid Mamba/linear-attention) **tổng tham số dưới 5B**, phát hành trước 26/10/2026, có ít nhất một trong: tool calling hay function calling, hỏi lại khi thiếu thông tin, năng lực tiếng Việt, context từ 16K trở lên.

- **Hạt giống chung (kiểm từng cái):** Qwen3.5-4B (và mọi biến thể Instruct/Thinking/VL nếu có), Qwen3-4B-Thinking-2507, Qwen3.5-2B, Phi-4-mini-instruct, Phi-4-mini-flash-reasoning, Gemma-3-4b-it (đếm phần text nếu bỏ vision), các bản Gemma 4 nhỏ, Llama-3.2-3B-Instruct, Llama-3.1-Nemotron-Nano-4B-v1.1, Nemotron-Mini-4B-Instruct, Llama-3.1-Minitron-4B (Width/Depth), Hunyuan-4B-Instruct, MiniCPM3-4B và MiniCPM4/4.x bản nhỏ, GLM-Edge-4B-chat, Granite-4.0-micro / h-micro / Granite-4.2-3B, LFM2-2.6B và các bản LFM mới hơn, SmolLM3-3B, Ministral-3-3B (nếu có), Apriel-5B-Instruct, AFM-4.5B (Arcee), EXAONE-4.0-1.2B, Falcon-H1-3B, Zamba2-2.7B, Jan-v1-4B, Jan-nano, Polaris-4B, FrogNano-4B-2609, Nanbeige4-3B, Youtu-LLM-2B.
- **MoE có tổng dưới 5B** (active ít nên nhanh, chừa thời gian cho tính toán thêm lúc suy luận): SmallThinker-4BA0.6B, Phi-tiny-MoE, Granite-3.1-3B-A800M, và mọi MoE nhỏ mới.
- **Tiếng Việt:** PhoGPT-4B-Chat (VinAI), Arcee-VyLinh (3B), Vi-Qwen2-3B, SeaLLMs-v3-1.5B, Sailor2 bản nhỏ, GemSUra-2B, VinaLlama-2.7B, các bản fine-tune tiếng Việt của Qwen3/Qwen3.5-4B (tổ chức 5CD-AI, AITeamVN, ura-hcmut, VietAI, Viettel, FPT, VinAI, VNG/Zalo…), SEA-LION bản nhỏ.
- **Chuyên tool calling:** xLAM-2 (1B/3B), Hammer2.x, Arch-Function-3B / Arch-Agent-3B, Octopus, TinyAgent, ToolACE bản nhỏ, các checkpoint RL cho tool use (ToolRL, Tool-N1, Tool-Star…) cỡ dưới 5B, và model huấn luyện trên When2Call.
- **Bằng chứng cần thu:** BFCL v3/v4 (nhất là multi-turn, missing parameter, irrelevance), τ²-bench, When2Call, ACEBench và các benchmark agent khác; năng lực tiếng Việt qua VMLU, SEA-HELM, Global-MMLU (vi), MMLU-ProX (vi), INCLUDE. Ghi rõ số tự báo hay số độc lập.
- **Kỹ thuật:** lớp kiến trúc trong transformers (có chạy với transformers 5.21 không), vLLM hỗ trợ từ bản nào, tên module để gắn LoRA (code đội gắn `q/k/v/o/gate/up/down_proj`; model hybrid có thể khác), chat template có định dạng tool call riêng không.

### R2. ASR tiếng Việt: mọi cỡ, ưu tiên "nhỏ mà mạnh" và "lớn mà tốt nhất"

Lý do: ASR càng nhỏ thì càng nhiều chỗ cho LLM và thành phần phụ; ASR tốt hơn thì bớt khoảng 13 điểm đang mất.

- **Hạt giống:** PhoWhisper (tiny tới large), EraX-WoW-Turbo và các bản fine-tune Whisper tiếng Việt khác, Qwen3-ASR-0.6B/1.7B, Gipformer (mọi phiên bản), BuzzASR, NVIDIA Parakeet/Canary có tiếng Việt, ChunkFormer (`khanhld/chunkformer-large-vie`), Zipformer tiếng Việt (ví dụ `hynt/Zipformer-30M-RNNT-6000h`), VietASR (Zipformer + pretrain lớn), wav2vec2 tiếng Việt (`nguyenvulebinh/*`), w2v-BERT 2.0 fine-tune tiếng Việt, Moonshine bản tiếng Việt (nếu có), Dolphin (DataoceanAI), Meta Omnilingual ASR (các cỡ CTC và LLM-ASR), OWSM v3.1/v4 và OWSM-CTC, Fun-ASR bản đa ngôn ngữ, MMS-1b-all và SeamlessM4T-v2 (licence NC, ghi để loại cho rõ), Voxtral Mini Transcribe, và ASR từ các công ty Việt (Viettel, FPT, VinBigData, VNG/Zalo).
- **Bằng chứng:** WER trên Common Voice vi, FLEURS vi, VIVOS, VLSP2020/2021/2023, GigaSpeech2-vi, ViMD, Bud500, LSVSC; ghi cách chuẩn hoá chữ. RTF, có hỗ trợ **hotword hay contextual biasing** không (sherpa-onnx có cho transducer), fine-tune được trên 6,8 giờ audio trong miền của đội không.
- **Dữ liệu ASR mở phát hành trước 26/10/2026** để fine-tune thêm (GigaSpeech2, Bud500, VIVOS, Common Voice, VLSP, ViMD…): kích thước, licence.

### R3. Speech-LLM và omni model (audio vào, tool call ra)

- Model nhận audio trực tiếp mà **tổng dưới 6B**, phần LLM dưới 5B: Gemma-4-E2B, Gemma-3n E2B/E4B (đếm tham số thô, gồm cả per-layer embedding), Qwen2.5-Omni-3B (bỏ talker và vision thì còn bao nhiêu; licence), Voxtral Mini 3B (có function calling từ giọng nói; có tiếng Việt không?), Phi-4-multimodal, Ultravox bản nhỏ, Granite-speech bản nhỏ, MiniCPM-o bản nhỏ nếu có, LLaMA-Omni2 bản nhỏ, và mọi speech-LLM mới trong 2026.
- Với mỗi model: chất lượng hiểu tiếng Việt nói (có số đo không), độ dài token audio so với context 16K, fine-tune được không, cách đếm "LLM" theo R0.
- **Dạng lai:** encoder của một ASR + projector + LLM nhỏ (tự ghép): có công trình nào làm với dưới 10 giờ dữ liệu trong miền mà vẫn tốt không?

### R4. Thành phần phụ nhỏ, và kỹ thuật không tốn tham số

- **Thành phần phụ:** ITN tiếng Việt (NeMo-text-processing vi, các repo khác), khôi phục dấu và dấu câu, sửa lỗi ASR (BARTpho, ViT5 cỡ nhỏ), VAD (Silero…), model nhỏ làm verifier hay router cho quyết định làm / hỏi / bỏ qua, EAGLE-3 hay Medusa head cho Qwen3/Qwen3.5-4B, draft model cho speculative decoding.
- **Kỹ thuật không tốn tham số hoặc gần như không:**
  - prompt-lookup / n-gram speculative decoding trong vLLM (tool call hay chép ID và chuỗi từ context);
  - constrained decoding (XGrammar, llguidance, Outlines);
  - self-consistency hay bỏ phiếu nhiều phương án cho tool call;
  - model soup / trung bình LoRA nhiều seed, TIES/DARE merging (giảm nhiễu 2–4 điểm giữa các lần train);
  - N-best hay lattice của ASR đưa vào LLM (generative error correction: HyPoradise, GenSEC);
  - contextual biasing cho Whisper bằng prompt decoder (tên app, tên danh bạ có trong context);
  - shallow fusion với n-gram LM dựng từ catalog tool và câu train.
  
  Với mỗi kỹ thuật: bằng chứng định lượng, rủi ro tái lập (greedy, seed), hỗ trợ trong vLLM/transformers đã pin.
- **Model chỉ dùng lúc phát triển (không tính tham số):** TTS tiếng Việt để sinh audio cho dữ liệu ASR và agent (VieNeu-TTS, các bản F5-TTS tiếng Việt, viXTTS, MMS-TTS, Chatterbox đa ngôn ngữ, Fish-Speech/OpenAudio, CosyVoice…; **ghi licence**), LLM mở lớn làm teacher (Qwen3/3.5 cỡ lớn, DeepSeek…), và các model trên Meta API mà đội có credit (tìm tài liệu công khai về danh sách model và giá).

### R5. "Cách dùng mới lạ" để nhét nhiều năng lực hơn vào cùng ngân sách

Đây là phần Leader kỳ vọng nhất. Với mỗi kỹ thuật, tìm paper hoặc repo, bằng chứng chất lượng giữ được bao nhiêu, công cụ có sẵn, thời gian thực hiện, và rủi ro luật (R0):

- **Cắt vocab (vocabulary trimming):** embedding của LLM đa ngôn ngữ chiếm nhiều tham số (ví dụ vocab khoảng 150–260 nghìn × hidden 2.560). Giữ lại token cần cho tiếng Việt, tiếng Anh, JSON và tên tool có thể bớt hàng trăm triệu tham số. Từ đó: (a) đưa một model hơi trên 5B xuống dưới 5B, hoặc (b) giải phóng chỗ cho ASR lớn hơn. Tính cụ thể cho từng ứng viên R1/R3. Lưu ý tokenizer phải giữ nguyên hành vi trên văn bản trong miền.
- **Bỏ tower không dùng:** vision encoder của model VL, talker của omni model.
- **Prune có distill:** Minitron, Sheared-LLaMA, ShortGPT/LaCo (bỏ lớp). Đưa một model khoảng 7–8B về dưới 5B: có checkpoint làm sẵn không? Nếu tự làm thì tốn bao nhiêu GPU-giờ?
- **Turbo hoá PhoWhisper-large:** cắt decoder từ 32 xuống 2–4 lớp rồi fine-tune lại, như cách OpenAI làm large-v3-turbo. Giải phóng khoảng 0,7B mà vẫn giữ encoder PhoWhisper. Nén encoder low-rank (LiteASR) để bớt thêm.
- **Nhiều LoRA trên một base** (mỗi adapter chỉ vài chục triệu tham số), mỗi adapter làm một vai: quyết định, điền tham số, sửa ASR.
- **Hai ASR khác nhau rồi kết hợp** (ROVER, hoặc để LLM chọn), khi mỗi ASR đủ nhỏ.
- **Depth up-scaling** (nhân lớp, kiểu SOLAR) một model 3–4B lên sát 5B: chỉ ghi nhận nếu có checkpoint làm sẵn đã được kiểm chứng; tự làm thì quá sức trước 13/11.

### R6. Lập tổ hợp và tìm biên Pareto

Từ các ứng viên đã kiểm ở R1–R5, liệt kê **mọi tổ hợp hợp lệ đáng cân nhắc**, tính số tham số **chính xác tới hàng đơn vị** từ số đếm thật. Tối thiểu phải có:
- **C0** cấu hình hiện tại;
- LLM lớn hơn (4,5–4,99B) + ASR nhỏ;
- LLM lớn hơn + ASR cỡ vừa đã turbo hoá;
- LLM hiện tại + ASR tốt hơn hoặc hai ASR;
- LLM + ASR + model phụ (verifier, router, sửa ASR);
- speech-LLM một khối;
- MoE + tính toán thêm lúc suy luận;
- mọi tổ hợp dùng kỹ thuật R5.

Với mỗi tổ hợp, ghi:
- tổng tham số và phần LLM, dư bao nhiêu so với 6B và 5B, theo **cách hiểu chặt nhất** của luật và theo cách hiểu khác nếu có;
- VRAM ở bf16 và ở 4-bit, so với máy chấm 32 GB;
- **ước thời gian mỗi mẫu trên RTX 5090** (lập luận theo token/giây đã công bố hoặc FLOPs; đội đo: mỗi mẫu khoảng 3 bước sinh, khoảng 30 token mỗi bước, prompt 3–5 nghìn token; ASR từ 1–4 file wav, trung bình 5 giây audio). Ghi rõ đây là ước, chưa đo;
- việc phải làm: train lại agent? fine-tune ASR? sửa code (prompt template, module LoRA, backend)?
- GPU-giờ và chi phí nếu thuê cloud;
- **mức tăng điểm dự kiến (khoảng) kèm lý lẽ và mức bằng chứng**, có tính đến nhiễu 2–4 điểm giữa các lần train;
- rủi ro: luật, licence, tái lập, thời gian.

Vẽ (bằng bảng) **biên Pareto**: tham số so với năng lực dự kiến so với rủi ro.

### R7. Đối thủ và bài toán tương tự

- Các đội khác làm ZAIC 2026 LifeMate thế nào: bài viết công khai, repo GitHub, thảo luận. **Không mở hay dùng nguồn nào có thể chứa transcript hay nhãn public/private.**
- Các cuộc thi hoặc benchmark tương tự: gọi tool từ giọng nói (spoken function calling, voice agent benchmark), VLSP 2025/2026, các track ASR tiếng Việt, lời giải đoạt giải các mùa Zalo AI Challenge trước. Họ ghép ASR + LLM ra sao, dưới trần tham số nào?
- Có dấu hiệu nào cho thấy mức 96,66 trên bảng public đến từ đâu không (ASR gần hoàn hảo, dữ liệu sinh cho app mới, hay model đặc biệt)?

### R8. Thẻ thí nghiệm cho top phương án

Với **top 5–8 tổ hợp**, viết thẻ thí nghiệm theo mẫu:
- **Giả thuyết**; **cần tải gì** (repo_id, revision, dung lượng);
- **phép thử rẻ nhất** dùng code sẵn của đội. Ví dụ: WER và độ đúng slot của ASR trên dev bằng `lifemate.asr` + `scripts/asr_quality.py`; với LLM, SFT ngắn theo đúng công thức trên `fit_lao` rồi chấm 40 hoặc 262 mẫu `dev_lao`, vì đó là thước gần public nhất;
- **luật giữ/bỏ viết trước**, có tính nhiễu (ví dụ cần 2 seed, hoặc ngưỡng vượt 4 điểm);
- **máy nào chạy, bao lâu, bao nhiêu tiền**; **sửa code ở đâu**;
- **có kịp trước 13/11 không**. Cái nào không kịp thì xếp vào "sau cuộc thi" và nói rõ.

---

## 6. Cách tìm kiếm (để độ phủ thật rộng)

### 6.1 Nguồn phải quét

- **Hugging Face Hub API** (chính xác nhất, nên dùng nhiều):
  - Liệt kê: `https://huggingface.co/api/models?pipeline_tag=<tag>&filter=<tag>&sort=<downloads|likes|createdAt|trendingScore>&direction=-1&limit=100` (phân trang theo header `Link`). Pipeline tag: `text-generation`, `automatic-speech-recognition`, `audio-text-to-text`, `any-to-any`, `image-text-to-text`. Filter: `vi`, `function-calling`, `tool-use`, `conversational`. Thử thêm tham số lọc theo số tham số (giao diện web dùng `num_parameters=min:...,max:...`); kiểm xem API có nhận không.
  - Chi tiết một model: `https://huggingface.co/api/models/<repo_id>?expand[]=safetensors&expand[]=createdAt&expand[]=lastModified&expand[]=cardData&expand[]=tags&expand[]=downloads&expand[]=likes`.
  - Lịch sử commit (ngày tải trọng số đầu tiên): `https://huggingface.co/api/models/<repo_id>/commits/main`.
  - **Quét riêng theo thời gian:** mọi model ASR có tag `vi` và mọi LLM dưới 6B tạo từ 01/06/2026 tới 25/10/2026, sắp theo `createdAt`. Đây là vùng Claude không biết.
  - Collections và org: Qwen, google, microsoft, meta-llama, facebook, nvidia, ibm-granite, mistralai, LiquidAI, HuggingFaceTB, openbmb, THUDM/zai-org, tencent, baidu, internlm, LGAI-EXAONE, tiiuae, Zyphra, arcee-ai, ServiceNow-AI, Salesforce, MadeAgents, katanemo, menloresearch/janhq, PowerInfer, vinai, VietAI, 5CD-AI, AITeamVN, ura-hcmut, SeaLLMs, sail, aisingapore, nguyenvulebinh, khanhld, hynt, ggroup-ai-lab, erax-ai, Systran, k2-fsa, csukuangfj, usefulsensors, DataoceanAI, espnet.
- **ModelScope** (nhiều model Trung Quốc lên đây trước, hoặc chỉ có ở đây).
- **arXiv:** `http://export.arxiv.org/api/query?search_query=...&sortBy=submittedDate&max_results=200` với các cụm "Vietnamese speech recognition", "Vietnamese ASR", "small language model function calling", "tool calling small model", "spoken function calling", "speech LLM Vietnamese", "vocabulary trimming", "layer pruning LLM", "Whisper decoder pruning", "contextual biasing Whisper", "generative error correction ASR LLM", khoảng 2025–10/2026.
- **GitHub:** repo và awesome-list (awesome Vietnamese NLP/speech, awesome speech LLM, awesome function calling, awesome small LLM); sắp theo cập nhật gần nhất.
- **Leaderboard:** BFCL (gorilla.cs.berkeley.edu), τ²-bench, When2Call, ACEBench, Open ASR Leaderboard (cả phần đa ngôn ngữ), SEA-HELM, VMLU, các leaderboard tiếng Việt trên HF Spaces, Artificial Analysis (mục model nhỏ).
- **Cộng đồng:** r/LocalLLaMA (bài về model nhỏ mới, 06–10/2026), Hacker News, X/Twitter của các lab, blog kỹ thuật (Qwen, Google, Microsoft, NVIDIA, IBM, Liquid, Mistral, Meta FAIR), Viblo và báo công nghệ Việt (VnExpress, Genk) về model tiếng Việt mới, Zhihu cho model Trung Quốc.
- **Tra cứu nhiều thứ tiếng:** tiếng Anh, tiếng Việt ("nhận dạng giọng nói tiếng Việt mô hình mở 2026", "mô hình ngôn ngữ tiếng Việt nhỏ gọi hàm"), tiếng Trung ("越南语 语音识别 模型", "小模型 函数调用 4B", "工具调用 端侧 模型 2026").

### 6.2 Kiểm chứng từng ứng viên

1. Trang model tồn tại; ghi `repo_id` chính xác và revision (commit SHA) lúc tra.
2. **Số tham số** theo mục 6.3.
3. **Ngày phát hành:** ngày commit đầu tiên có trọng số (không lấy ngày paper). Phải trước 26/10/2026.
4. **Licence:** đọc `cardData.license` và file LICENSE. Đánh dấu NC, research-only, gated hay cần đồng ý điều khoản.
5. **Tiếng Việt:** model card có ghi không; có điểm benchmark tiếng Việt không.
6. **Tool calling:** chat template có hỗ trợ tool không; có điểm benchmark không.
7. **Chạy được với stack đội đã pin** (transformers 5.21, vLLM, CUDA 13.2 / sm_120), hay cần bản mới.

### 6.3 Đếm tham số đúng cách

- Ưu tiên `safetensors.total` và `safetensors.parameters` từ HF API (đếm theo dtype). Nếu không có: tải `model.safetensors.index.json` hoặc header của file safetensors (vài KB đầu file, dùng HTTP Range) rồi cộng shape. Cuối cùng mới tính từ `config.json` theo kiến trúc; khi đó ghi rõ là ước tính.
- Tách thành phần: LLM / vision / audio encoder / talker / embedding (ghi embedding có tied không) / LM head.
- **Quantization không đổi số tham số.** Model GPTQ/AWQ/bnb trên HF có thể bị API đếm sai (do pack nhiều số vào một), nên đếm trên bản gốc.
- Viết script nhỏ trong `docs/research/tools/` để tra hàng loạt và tái lập được.

### 6.4 Độ phủ tối thiểu (để chứng minh đã tìm kỹ)

Đã kiểm tối thiểu **40 LLM, 30 ASR, 10 speech-LLM, 15 thành phần phụ và kỹ thuật, 10 TTS**. Ghi cả các model bị loại, kèm lý do (quá trần, sau 26/10, licence, không có tiếng Việt, không tồn tại…). Báo cáo có phụ lục liệt kê truy vấn đã dùng và các nguồn đã quét.

---

## 7. Các pha và thời gian

- **Pha A** (khoảng 45 phút): R0; kiểm lại bảng ngày 31/10; viết script đếm tham số. Ghi nhật ký tiến độ.
- **Pha B** (2–3 giờ): R1–R5, quét rộng. Ghi nhật ký giữa chừng sau mỗi nhóm.
- **Pha C** (khoảng 1 giờ): R6–R8, lập tổ hợp, xếp hạng, viết báo cáo.
- **Pha D cho phép:** chạy thử ASR rất nhỏ trên CPU để có WER thật thay cho số tự báo.
  - Chỉ model ASR có trọng số **dưới 500 MB**; tối đa 4 model; tổng dung lượng tải dưới 2 GB; xoá sau khi đo.
  - Tạo venv riêng bằng `uv` ở `~/zac-codex-env` (Python 3.12); không cài gì vào hệ thống.
  - Chạy trên tối đa 100 file wav **lượt cuối** của `dev_random` (`lifemate/splits/dev_random.txt`). Đường dẫn wav lấy từ trường `audio` của mẫu, tính từ `data/train+public_test/train/`; so với trường `audio_text` của chính mẫu đó trong `train.jsonl`. Tính WER bằng hàm `wer` của `lifemate/lifemate/asr_train.py`, kèm tỉ lệ đúng số, giờ và tên (tham khảo `lifemate/scripts/asr_quality.py`). Giới hạn `CUDA_VISIBLE_DEVICES=""`, dưới 2 GB RAM.
  - Mốc so sánh đã có: PhoWhisper-large-ft WER khoảng 9,2 trên dev_random; Whisper-turbo-ft 11,2; Whisper-turbo chưa fine-tune 31,2. Nhớ rằng model chưa fine-tune trong miền thì thiệt khi so; ghi rõ.
  - Không ghi transcript hay dữ liệu vào báo cáo; chỉ ghi con số tổng hợp.

---

## 8. Cấu trúc báo cáo và schema CSV

**Nhãn bằng chứng** (gắn cho mọi khẳng định):
- `[Bằng chứng mạnh]`: tự kiểm trực tiếp (HF API, file config, phép đo của bạn);
- `[Bằng chứng vừa]`: model card hoặc paper tự báo;
- `[Suy luận]`: lập luận của bạn;
- `[Chưa kiểm chứng]`.

**Báo cáo `CODEX_MODEL_COMBOS_2026-11-08.md`:**
1. **Tóm tắt cho người bận** (tối đa 15 dòng): top 5 tổ hợp, mức tăng dự kiến, việc đội cần quyết, câu hỏi gửi BTC.
2. **Luật đếm tham số (R0):** nguyên văn, cách hiểu, câu hỏi cho BTC.
3. **Ngân sách tham số:** cấu hình hiện tại; trần nào đang bó; đánh đổi giữa ASR và LLM.
4. **Kho LLM (R1):** bảng tóm tắt các ứng viên đáng xét; danh sách đầy đủ để trong CSV.
5. **Kho ASR (R2)** và dữ liệu ASR mở.
6. **Speech-LLM (R3).**
7. **Thành phần phụ và kỹ thuật không tốn tham số (R4)**, và model chỉ dùng lúc phát triển.
8. **Cách dùng mới lạ (R5):** từng kỹ thuật kèm phép tính tham số cụ thể.
9. **Tổ hợp và biên Pareto (R6):** bảng tổ hợp, top 10 kèm lý lẽ.
10. **Đối thủ và bài toán tương tự (R7).**
11. **Thẻ thí nghiệm (R8)**, xếp theo thứ tự nên chạy; tách "kịp trước 13/11" và "sau cuộc thi".
12. **Phản biện:** 5–7 lý do vì sao đổi model có thể **không** giúp (ví dụ: SFT trên 1.545 mẫu là nút thắt chứ không phải dung lượng model; nhiễu 2–4 điểm), và cách kiểm từng lý do.
13. **Phụ lục:** truy vấn đã dùng; nguồn đã quét; model đã loại và lý do; giới hạn của báo cáo.

**`model_candidates_2026-11-08.csv`**, các cột:
`component` (llm | asr | speech_llm | aux | tts | teacher | draft | technique), `repo_id`, `revision`, `family`, `params_total`, `params_breakdown`, `params_source` (hf_api | safetensors_header | config_calc | card), `weights_first_commit`, `license`, `license_ok` (yes | no | ask_btc), `vietnamese_evidence`, `tool_calling_evidence`, `key_benchmarks`, `context_len`, `arch_class`, `transformers_ok`, `vllm_ok`, `vram_bf16_gb`, `latency_note`, `status` (verified | reported | unverified | excluded), `exclusion_reason`, `url`, `accessed`.

**`model_combos_2026-11-08.csv`**, các cột:
`combo_id`, `components`, `params_total`, `params_llm`, `headroom_6b`, `headroom_5b`, `rule_interpretation`, `vram_gb`, `latency_estimate_s`, `work_needed`, `gpu_hours`, `cost_usd`, `expected_gain`, `evidence_level`, `fits_before_13_11` (yes | no), `risks`, `rank`, `notes`.

**`model_sources_2026-11-08.csv`:** cùng các cột với `docs/research/codex_sources_2026-10-31.csv`.

---

## 9. Tài liệu nội bộ nên đọc trước (chỉ đọc phần cần)

- `git show origin/main:JOURNAL.md`: mục 1 (đề), mục 3 (phát hiện về nhãn), mục 4 (kiến trúc); entry 78, 81, 101, 107.
- `docs/research/CODEX_DEEP_RESEARCH_2026-10-31.md` mục 6–7 và `docs/research/CODEX_4B_STRATEGY_2026-11-04.md`.
- `docs/LEADER_ONBOARDING_2026-11-08.md` mục 5–6 (chỉ có ở máy này, chưa commit).
- `git show origin/main:docs/BTC_DOCKER_GUIDE_2026-11-06.md` (yêu cầu Docker, phần cứng chấm).
- Code: `lifemate/lifemate/{prompt,agent,train,asr}.py`.
