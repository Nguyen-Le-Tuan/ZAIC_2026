# Tổ hợp model cho LifeMate — nghiên cứu ngày 08/11/2026

Ngày truy cập nguồn: **08/11/2026**. Ký hiệu xuyên suốt: **[Bằng chứng mạnh]** là luật, metadata hoặc phép đếm trực tiếp; **[Bằng chứng vừa]** là model card/paper tự báo; **[Suy luận]** là phép ngoại suy cần thí nghiệm; **[Chưa kiểm chứng]** là điều còn thiếu. Mọi con số tham số trong bảng tổ hợp là **số tham số**, không phải dung lượng sau lượng tử hóa. **Bổ sung Pha D theo yêu cầu tiếp theo của Leader** ở mục 5.

## 1. Tóm tắt cho người bận

| Thứ tự | Tổ hợp | Tổng tham số | Khoảng tăng giả thuyết so C0 | Quyết định cần làm |
|---|---|---:|---:|---|
| 1 | **C1** Qwen3.5-4B **text-only** + PhoWhisper-large-ft + LoRA r32 | **5.810.004.736** | −4 đến +10 điểm | Thử SFT ngắn và kiểm Docker/runtime; hỏi BTC về bản text-only |
| 2 | **C0** bản đang nộp Qwen3-4B + PhoWhisper-large-ft | **5.631.833.344** | Mốc 0 | Giữ làm đối chứng và phương án chốt |
| 3 | **C2** Qwen3.5-4B đầy đủ + Whisper-turbo-ft | **5.529.691.648** | −6 đến +8 điểm | Chỉ tiếp nếu agent mới bù được suy giảm ASR |
| 4 | **C3** Qwen3.5-4B đầy đủ + Qwen3-ASR-0.6B | **5.658.822.144** | −8 đến +10 điểm | Đo ASR trên dev trước SFT agent |
| 5 | **C7** Qwen3-4B-Thinking + PhoWhisper-large-ft | **5.631.833.344** | −5 đến +7 điểm | Giới hạn reasoning để giữ 30 giây |

**[Bằng chứng mạnh]** C1 khả thi về số đếm vì checkpoint text-only công khai trước hạn có 4.205.751.296 tham số; bản Qwen3.5 đầy đủ là 4.659.865.088. Bản đầy đủ cộng PhoWhisper-large đã là **6.203.170.048**, vượt trần trước khi cộng adapter. [Nguồn text-only](https://huggingface.co/tuandunghcmut/Qwen3.5-4B-text-only), [nguồn gốc](https://huggingface.co/Qwen/Qwen3.5-4B), phép đếm header và CSV kèm theo.

**[Suy luận]** Không có điểm LifeMate nào cho các model mới. Khoảng điểm trong CSV là *giả thuyết kiểm thử*, không phải dự báo private: C1 **−4 đến +10 điểm phần trăm** so với C0, có thể thua. Nếu chưa đo được hai seed và Docker trước 13/11, giữ C0. Việc cần BTC xác nhận gấp nhất: cách tính bản đã bỏ tower/LoRA, nhiều LLM, và máy chấm A30 hay RTX 5090. [Luật chính thức](https://challenge.zalo.ai/portal/lifemate), [Docker Guide](https://dl-challenge.zalo.ai/2026/lifemate_argfzdgert/Docker_Guide_ZAC2026_LifeMate.pdf).

**[Bằng chứng mạnh, bổ sung Pha D]** Trên 100 wav `dev_random` lượt cuối, Gipformer1.5 int8 đạt WER **16,89**; Moonshine tiny-vi **41,29**, PhoWhisper-tiny **42,21**, PhoWhisper-base **40,55**. Đây là checkpoint chưa fine-tune trong miền; xem mục 5 về mẫu, slot và giới hạn so sánh.

## 2. Luật đếm tham số và điều kiện hợp lệ (R0)

**[Bằng chứng mạnh]** [Trang LifeMate chính thức](https://challenge.zalo.ai/portal/lifemate) ghi nguyên văn hai cụm quan trọng: “**fewer than 6B parameters in total**” cho toàn hệ thống và “**fewer than 5B parameters**” cho LLM. Đây là dấu **<**, không phải ≤. Cùng văn bản quy định context tối đa **16K (16.384) token**, **30 giây/mẫu** kể cả xử lý, offline, deterministic/greedy hoặc temperature 0, seed cố định; trọng số công khai trước **26/10/2026**. Trang công khai được đọc qua [API quy tắc](https://api-challenge.zalo.ai/fe/api/config-detail?name=rule&title=1) với Origin/Referer của portal. Đơn vị B không được định nghĩa riêng; mọi phép tính ở đây dùng **10⁹**, cách hiểu thông dụng và chặt về số nguyên.

**[Bằng chứng mạnh]** Luật gốc ghi **A30 24 GB**, còn [Docker Guide, trang 4](https://dl-challenge.zalo.ai/2026/lifemate_argfzdgert/Docker_Guide_ZAC2026_LifeMate.pdf) ghi **RTX 5090 32 GB**, driver **595.58.03**, CUDA **13.2**. Không tìm thấy câu chính thức tuyên bố guide thay thế cấu hình A30; chưa thể coi 5090 là chắc chắn. [Thể lệ, mục 4.5](https://dl-challenge.zalo.ai/zalo-ai-challenge-regulations-en.pdf) yêu cầu tài nguyên mở với điều kiện sử dụng thương mại phù hợp hoặc có chấp thuận bằng văn bản. Hạn Docker **16/11 23:59 GMT+7** từ thể lệ/hướng dẫn; mục tiêu nội bộ chốt **13/11** theo đội.

| Vấn đề | Văn bản nói rõ | Cách tính bảo thủ của nghiên cứu |
|---|---|---|
| Tổng hệ thống | ASR, LLM và mọi thành phần khác <6B | Cộng tất cả checkpoint thực sự nạp, kể cả router/draft/verifier, ASR encoder và decoder, embedding; MoE tính **tất cả** expert |
| LLM | <5B; context ≤16.384 | Cộng mọi LLM cùng hoạt động, kể cả adapter chưa merge; đặt runtime max context 16.384 |
| Tower không dùng | Không giải thích | Chỉ trừ khi artifact thực sự bỏ tower và BTC đồng ý; giữ bản full làm đối chiếu |
| LoRA | Không giải thích | Chưa merge: cộng tham số LoRA; đã merge thật: không cộng lần nữa |
| Tied embedding | Không giải thích | Đếm tensor lưu/nạp một lần, không cộng hai lần theo tên logic |
| Vocab trimming/pruning/distillation | Không giải thích | Chỉ coi hợp lệ sau xác nhận BTC về model sửa từ checkpoint phát hành trước hạn |
| N-gram, rule, constrained decoder | Không giải thích | Ghi rõ phần có tham số học; không tự nhận “0” khi có thống kê học từ dữ liệu |

Các cách hiểu ở cột cuối là **[Suy luận]**, không phải phán quyết của BTC. [HF safetensors metadata](https://huggingface.co/docs/hub/en/models-safetensors) và script `tools/safetensors_header_audit_2026-11-08.py` dùng để đếm tensor; quantization không giảm số *logical* parameters.

**Câu hỏi soạn sẵn gửi BTC, theo ảnh hưởng:**

1. Một checkpoint text-only đã được công bố trước 26/10, bỏ hẳn vision/MTP và không nạp tower lúc inference, có được tính theo tensor còn lại không? Có chấp nhận checkpoint tự tách từ base công khai trước hạn không?
2. Với LoRA chưa merge, BTC cộng số tham số adapter vào cả tổng hệ thống và trần LLM chứ? Với LoRA đã merge thì có được chỉ đếm tensor base một lần?
3. Nếu dùng hai LLM, `<5B` áp lên **tổng hai LLM** hay mỗi LLM riêng? Draft/verifier/router học tham số có tính là LLM không?
4. MoE tính tổng mọi expert hay số active mỗi token? Encoder–decoder/talker/vision không gọi có tính nếu vẫn có trong file nhưng runtime không nạp?
5. Model đã cắt vocab, prune lớp hoặc distill từ trọng số hợp lệ trước 26/10, được huấn luyện sau ngày đó, có thỏa ngày phát hành không?
6. Máy chấm cuối là A30 24 GB hay RTX 5090 32 GB trong Docker Guide? Giới hạn 30 giây/mẫu có giữ nguyên?
7. B được tính theo 10⁹ tham số, và model phụ như n-gram LM/VAD có tính không?

## 3. Ngân sách tham số hiện tại

**[Bằng chứng mạnh, số đội đã đếm/đo]** C0: PhoWhisper-large-ft **1.543.304.960** + Qwen3-4B-Instruct-2507 **4.022.468.096** + LoRA r32 chưa merge **66.060.288** = **5.631.833.344**; dư **368.166.656** tới 6B và LLM+LoRA dư **911.471.616** tới 5B. Public **51,16**; đổi Qwen3-1.7B→4B trên 495 dev **33,07→46,17**; đổi turbo-ft→Pho-large-ft public **46,29→51,16**. Đây là quan sát nội bộ trong [JOURNAL](../../JOURNAL.md) và [báo cáo 31/10](CODEX_DEEP_RESEARCH_2026-10-31.md); hai seed cùng công thức có thể lệch **2–4 điểm**. Không lấy điểm benchmark công khai làm điểm LifeMate.

**[Suy luận]** Vì phần LLM hiện gần trần 5B, tăng LLM bằng cách giữ Pho-large chỉ khả thi nếu bỏ phần thừa của checkpoint; đổi sang ASR nhỏ là đánh đổi điểm ASR lấy năng lực agent. NF4 giảm VRAM, **không** giảm tham số theo luật.

## 4. Kho LLM (R1)

Các hàng sau có trang/model ID thực; số chính xác của những hàng được dùng trong tổ hợp có trong CSV. `verified` nghĩa metadata/tensor được kiểm, **không** nghĩa đã chạy trên stack đội. Tất cả truy cập 08/11/2026.

| Ứng viên | Tham số | Bằng chứng và nhận xét |
|---|---:|---|
| [Qwen3.5-4B text-only](https://huggingface.co/tuandunghcmut/Qwen3.5-4B-text-only) | **4.205.751.296** | **[Bằng chứng mạnh]** header, Apache-2.0; trọng số đầu 24/06/2026. **[Bằng chứng vừa]** card nói greedy logits tương đương bản gốc khi chỉ dùng text. LoRA/hybrid runtime cần thử. |
| [Qwen3.5-4B full](https://huggingface.co/Qwen/Qwen3.5-4B) | **4.659.865.088** | **[Bằng chứng mạnh]** 4.205.751.296 language + 333.514.240 visual + 120.599.552 MTP. **[Bằng chứng vừa]** BFCL-v4 50,3 tự báo, không so trực tiếp BFCL-v3. Card hướng dẫn `--language-model-only`. |
| [Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) | **4.022.468.096** | **[Bằng chứng mạnh]** đối chứng đã chạy LifeMate. |
| [Qwen3-4B-Thinking-2507](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507) | **4.022.468.096** | **[Suy luận]** có thể giúp schema lạ nhưng reasoning tăng latency; chưa thử. |
| [FrogNano-4B-2609](https://huggingface.co/microsoft/FrogNano-4B-2609) | **4.659.865.088**, text **4.205.751.296** | **[Bằng chứng mạnh]** header; bản coding English/Python, chưa có chứng cứ tiếng Việt tốt hơn Qwen gốc. |
| [Apriel-5B-Instruct](https://huggingface.co/ServiceNow-AI/Apriel-5B-Instruct) | **4.832.071.680** | **[Bằng chứng mạnh]** dưới 5B nhưng chỉ ghép ASR dưới ~1,168B nếu không adapter; kiến trúc/LoRA cần kiểm. |
| [AFM-4.5B](https://huggingface.co/arcee-ai/AFM-4.5B) | **4.619.189.760** | **[Bằng chứng mạnh]** khả thi với Qwen ASR; chưa có điểm LifeMate/vi. |
| [SmallThinker-4BA0.6B](https://huggingface.co/Tiiny/SmallThinker-4BA0.6B-Instruct) | **4.268.459.520 tổng** | **[Bằng chứng mạnh]** MoE; active ~0.6B trong tên không được dùng thay tổng. |
| [Granite-3.1-3B-A800M](https://huggingface.co/ibm-granite/granite-3.1-3b-a800m-instruct) | **3.298.793.472 tổng** | **[Bằng chứng mạnh]** MoE; dư ngân sách, năng lực tiếng Việt/tool trong miền chưa đo. |
| [Phi-tiny-MoE](https://huggingface.co/microsoft/Phi-tiny-MoE-instruct) | **3.755.220.288 tổng** | **[Bằng chứng mạnh]** MIT; kiểm runtime riêng trước chọn. |

Các dòng khác gồm Phi-4-mini, Gemma-3-4b, Hunyuan, MiniCPM, GLM-Edge, LFM2, SmolLM3, xLAM, Hammer, SEA-LION và các bản tiếng Việt. **[Chưa kiểm chứng]** Nhiều hạt giống không trả đúng repo ID hoặc chỉ có tên trong gợi ý; CSV ghi `unverified`/lý do, tuyệt đối không suy từ tên. Với Qwen3.5, [Transformers docs](https://huggingface.co/docs/transformers/main/model_doc/qwen3_5) mô tả kiến trúc Gated DeltaNet; target LoRA cũ `q/k/v/o/gate/up/down_proj` bỏ sót linear attention. [Card Qwen](https://huggingface.co/Qwen/Qwen3.5-4B) nêu vLLM main/nightly, nên pin vLLM hiện tại và CUDA sm_120 **phải smoke test**; chưa khẳng định chạy được. Greedy theo luật khác chế độ sampling card khuyến nghị. [Bằng chứng vừa]

Benchmark tool use công khai BFCL-v4, τ²-bench, When2Call, ACEBench và tiếng Việt VMLU/SEA-HELM dùng để lọc, nhưng thiếu thiết lập đồng nhất cho đa số model; không xếp hạng chéo bằng điểm tự báo. [BFCL](https://gorilla.cs.berkeley.edu/leaderboard.html), [τ²-bench](https://github.com/sierra-research/tau2-bench), [When2Call](https://github.com/lt-asset/when2call), [ACEBench](https://github.com/ACEBench/ACEBench), [SEA-HELM](https://sea-helm.ai/). [Bằng chứng mạnh về nguồn; Suy luận về chuyển miền]

## 5. Kho ASR và dữ liệu mở (R2)

| Ứng viên | Tham số | Tín hiệu và điểm cần kiểm |
|---|---:|---|
| [PhoWhisper-large](https://huggingface.co/vinai/PhoWhisper-large) | **1.543.304.960** | **[Bằng chứng mạnh]** C0 đã fine-tune; WER dev_random ~9,2 theo đội. |
| [Whisper-large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo) | **808.878.080** | **[Bằng chứng mạnh]** bản đội fine-tune WER ~11,2 dev_random, public thấp hơn C0 4,87 điểm với agent cũ. |
| [PhoWhisper-medium](https://huggingface.co/vinai/PhoWhisper-medium) | **763.857.920** | **[Bằng chứng mạnh]** tính config theo kiến trúc Whisper; chưa đo sau fine-tune trong miền. |
| [Qwen3-ASR-0.6B](https://huggingface.co/Qwen/Qwen3-ASR-0.6B) | **938.008.576** | **[Bằng chứng mạnh]** số thực lớn hơn tên 0.6B; [docs](https://huggingface.co/docs/transformers/model_doc/qwen3_asr) ghi hỗ trợ tiếng Việt; slot số/tên cần đo. |
| [Moonshine streaming tiny-vi](https://huggingface.co/moonshine-ai/moonshine-streaming-tiny-vi) | **27.015.360** | **[Bằng chứng vừa]** card tự báo FLEURS vi WER 10,98 trên 400 mẫu và LSVSC 7,63 với chuẩn hóa riêng; không so trực tiếp WER của đội. |
| [Gipformer1.5-68M-RNNT](https://huggingface.co/g-group-ai-lab/gipformer1.5-68M-rnnt) | **68.625.511 theo config/card** | **[Bằng chứng vừa]** card tự báo ViMD WER 7,00, FLEURS 12,65; chưa có số đếm safetensors độc lập. |
| [BuzzASR/vietnamese](https://huggingface.co/BuzzASR/vietnamese) | **1.543.490.560** | **[Bằng chứng vừa]** card tự báo FLEURS 7,26; kích thước khó ghép Qwen3.5 full. |
| [QUAN-Transcribe-1.0](https://huggingface.co/qnguyen3/QUAN-Transcribe-1.0) | **chưa xác định toàn bộ** | **[Bằng chứng mạnh]** HF 101.738.068 chỉ một phần; tree có `best.pt` và external encoder. Gated Gemma; loại khỏi combo đến khi đếm đủ/licence. |

**[Bằng chứng mạnh]** Công thức Whisper được kiểm chéo với HF API bản OpenAI large-v3 và turbo. Số PhoWhisper tiny/base/small/medium lần lượt **37.760.640 / 72.593.920 / 241.734.912 / 763.857.920** là tính từ config, **không** phải WER. `microsoft/VibeVoice-ASR-BitNet` có tensor đóng gói nên đếm HF 322M sai nếu hiểu là logical params; [card](https://huggingface.co/microsoft/VibeVoice-ASR-BitNet) ghi tệp 1.58GB so với 4.62GB FP16 và WER MLC-VI 22,38 tự báo. NVIDIA Nemotron ASR có Evaluation License, [VieGem-ASR](https://huggingface.co/5CD-AI/VieGem-ASR) NC-SA, không đưa vào tổ hợp. `Dolphin` của ByteDance tìm được là OCR; không coi là ASR. [Bằng chứng mạnh/vừa tương ứng card]

**Dữ liệu ASR trước hạn:** [GigaSpeech2](https://huggingface.co/datasets/speechcolab/gigaspeech2) gồm 30 nghìn giờ cộng nhiều ngôn ngữ Thái/Indonesia/Việt, phải tách phần tiếng Việt và kiểm điều khoản thương mại; [VIVOS](https://huggingface.co/datasets/SEACrowd/vivos) khoảng 15 giờ, licence cần xác minh; [Bud500](https://huggingface.co/datasets/linhtran92/viet_bud500) có điều kiện truy cập/nguồn gốc cần kiểm; [Common Voice](https://commonvoice.mozilla.org/en/datasets) có phiên bản/giấy phép riêng. **[Bằng chứng vừa]** Các nguồn không tương đương audio hội thoại công cụ. [Suy luận] Không lên lịch fine-tune dữ liệu ngoài trước 13/11 nếu chưa rõ licence và normalization. Với tên app/danh bạ, có thể kiểm contextual biasing/hotword trên dev; dùng danh mục schema hợp lệ trong inference, không dùng dữ liệu test để train. [sherpa-onnx docs](https://k2-fsa.github.io/sherpa/onnx/hotwords/index.html) [Bằng chứng vừa]

### Đo CPU Pha D — bổ sung sau yêu cầu tiếp theo

**[Bằng chứng mạnh, phép đo cục bộ]** Chạy bốn model **chưa fine-tune trong miền** trên đúng **100 wav lượt cuối** của 100 ID đầu tiên trong `lifemate/splits/dev_random.txt`; tổng **717,36 giây audio**, dài nhất **16,39 giây**. Đọc duy nhất `train/train.jsonl` và các đường dẫn `audio` của chính mẫu trong `data/train+public_test/train/`. Tính WER bằng `lifemate.asr_train.wer` mặc định (lowercase, bỏ dấu câu). Mỗi model chạy tuần tự trong venv Python 3.12 riêng, `CUDA_VISIBLE_DEVICES=''`, một CPU thread và watchdog dừng ở **1,85 GB RSS**. Script [cpu_asr_phase_d_2026-11-08.py](tools/cpu_asr_phase_d_2026-11-08.py) không lưu transcript/dự đoán; chỉ xuất tổng hợp.

| Model, revision trong CSV | Trọng số đã tải | WER ↓ | Số đúng | Giờ đúng | Tên proxy đúng | CPU 100 wav / RTF | RSS đỉnh |
|---|---:|---:|---:|---:|---:|---:|---:|
| [Gipformer1.5 int8 ONNX](https://huggingface.co/g-group-ai-lab/gipformer1.5-68M-rnnt) | 73.218.466 byte | **16,89** | 35/36 (**97,2%**) | 10/10 (**100%**) | 290/349 (**83,1%**) | 15,34 s / **0,021** | 402 MB |
| [Moonshine streaming tiny-vi fp32](https://huggingface.co/moonshine-ai/moonshine-streaming-tiny-vi) | 108.079.716 byte | 41,29 | 30/36 (83,3%) | 6/10 (60%) | 202/349 (57,9%) | 25,66 s / 0,036 | 617 MB |
| [PhoWhisper-tiny fp32](https://huggingface.co/vinai/PhoWhisper-tiny) | 151.099.049 byte | 42,21 | 23/36 (63,9%) | 7/10 (70%) | 221/349 (63,3%) | 99,23 s / 0,138 | 659 MB |
| [PhoWhisper-base fp32](https://huggingface.co/vinai/PhoWhisper-base) | 290.458.785 byte | 40,55 | 28/36 (77,8%) | 6/10 (60%) | 227/349 (65,0%) | 179,27 s / 0,250 | 828 MB |

**Cách tính slot [Bằng chứng mạnh về phép tính, Suy luận về ý nghĩa]:** số là **36 giá trị viết bằng chữ số** trong `audio_text`, so với dạng số/chữ Việt do `lifemate.vinum.value_forms` sinh; giờ là **10 biểu thức có chữ số** kiểu `HH:MM`, `HhMM` hoặc `H giờ`, so với `time_forms`; “tên proxy” là **349 từ viết hoa giữa câu** trong tham chiếu, so khớp không phân biệt hoa/thường nhưng **có dấu**. Proxy này không phải gold named entity, bỏ sót tên viết thường và có thể tính thừa từ viết hoa không phải tên. Tỷ lệ là **recall dạng bề mặt**, không chứng minh độ đúng tool argument; WER cũng không thay cho điểm agent. Mỗi model dùng greedy; Gipformer dùng ONNX int8, ba model còn lại dùng checkpoint fp32 gốc. [Bằng chứng mạnh]

**Diễn giải [Suy luận]:** Gipformer là ứng viên ASR nhỏ tốt nhất trong bốn model vừa thử, nhưng WER **16,89** vẫn cao hơn mốc **~9,2** của PhoWhisper-large-ft và **~11,2** của turbo-ft mà đội đã đo trên **toàn bộ** dev_random bằng model **đã fine-tune**. Hai mốc cũ không cùng 100 wav và không phải phép so cặp; không dùng chênh lệch này để dự báo điểm. Kết quả làm C5 đáng thử ở vai ASR tiết kiệm tham số, nhưng chưa đủ để thay C0 trước 13/11. Moonshine/Pho tiny/base nguyên bản không đủ hấp dẫn làm ASR chính; C6 hai ASR chỉ đáng làm nếu kiểm được lỗi bổ sung không làm hỏng slot. Tốc độ CPU ở đây không ngoại suy thành tốc độ RTX 5090 hoặc cả pipeline.

**Giới hạn tài nguyên [Bằng chứng mạnh]:** tổng trọng số đã tải **622.856.016 byte**, dưới 2 GB; mỗi model dưới 500 MB. `hf cache rm` đã xóa cả bốn revision, giải phóng **630,5 MB** gồm metadata/processor; kiểm lại `hf cache ls` không còn repo nào. Cache cài đặt `uv` trong `/tmp` cũng được dọn. Venv `~/zac-codex-env` còn lại để tái lập, không chứa trọng số model.

## 6. Speech-LLM và omni (R3)

| Model | Tách tham số trực tiếp | Khả năng thực tế |
|---|---|
| [Voxtral Mini 3B](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507) | **4.676.271.104** = language 4.014.136.320 + audio tower 636.968.960 + projector 25.165.824 | **[Bằng chứng vừa]** card nói tool/function calling từ audio; tiếng Việt và LifeMate chưa đo. Tích hợp/SFT không kịp 13/11. |
| [Gemma 4 E2B it](https://huggingface.co/google/gemma-4-E2B-it) | **5.123.178.979** = language 4.647.449.891 + audio 304.825.088 + vision 167.365.056 + embedding audio/vision 3.538.944 | **[Bằng chứng mạnh]** header khác HF API 928 tham số; dùng header. License Gemma cần BTC xác nhận; chưa có chứng cứ tiếng Việt nói trong miền. |
| [Qwen2.5-Omni-3B](https://huggingface.co/Qwen/Qwen2.5-Omni-3B) | **5.537.120.672** = thinker 4.703.464.448 + talker 384.604.928 + token2wav 449.051.296 | **[Bằng chứng mạnh]** licence `qwen-research`, **loại** theo điều khoản thương mại hiện có. |
| [Gemma 3n E2B/E4B](https://huggingface.co/google/gemma-3n-E2B-it) | E2B **5.439.438.272**, E4B **7.849.978.192** | **[Bằng chứng mạnh]** E4B quá 6B; “effective” trong tên không thay tổng. E2B licence cần hỏi, LLM/tower split cần kiểm. |

**[Suy luận]** Audio token có thể ăn context 16.384 và thời gian phụ thuộc số lượt history, không thể dùng benchmark giọng nói ngắn để suy 30 giây/mẫu. Tự ghép encoder ASR + projector + LLM dưới 10 giờ audio miền đòi alignment và SFT; chưa thấy chứng cứ đủ mạnh cho tool call tiếng Việt trong lịch này, xếp sau cuộc thi. Granite-speech có repo thật nhưng card không chứng minh hỗ trợ tiếng Việt; Ultravox 8B vượt trần khi cộng base external (HF API chỉ đếm adapter). Xem CSV để thấy cả các trường hợp loại. [Nguồn Granite](https://huggingface.co/ibm-granite/granite-speech-3.3-2b), [Ultravox](https://huggingface.co/fixie-ai/ultravox-v0_5-llama-3_1-8b) [Bằng chứng mạnh]

## 7. Thành phần phụ, kỹ thuật không tốn tham số và model phát triển (R4)

**[Suy luận]** Một router/verifier 50–600M chỉ có ích nếu giảm lỗi **lệnh ghi sai làm hash về 0**. Không có phép đo LifeMate để khẳng định. VAD như [Silero VAD](https://github.com/snakers4/silero-vad) giúp cắt im lặng; ITN/khôi phục dấu có thể sửa số nhưng cũng đổi literal tool argument. BARTpho/ViT5 sửa ASR phải đếm đủ tham số và huấn luyện trên lỗi đúng miền; chưa xếp trước 13/11. CSV ghi các thành phần phụ được sàng lọc.

**[Bằng chứng mạnh về tính năng; Suy luận về lợi ích]** [vLLM n-gram speculative decoding](https://docs.vllm.ai/en/stable/features/speculative_decoding/n_gram/) không dùng draft neural model, có thể nhanh khi copy schema/ID; phải benchmark trên prompt 3–5 nghìn token, khoảng 3 bước ×30 token. [vLLM structured outputs](https://docs.vllm.ai/en/stable/features/structured_outputs/) có thể ép JSON/tool schema; không sửa quyết định sai hoặc mã cổ phiếu bịa. Greedy + grammar vẫn deterministic nếu runtime ổn định. N-best ASR/GenSEC và ROVER chỉ nên áp cho span chắc chắn; bỏ phiếu nhiều sample gây chi phí latency và mâu thuẫn luật greedy nếu sampling. [HyPoradise](https://arxiv.org/abs/2309.15701) [Bằng chứng vừa]

**[Bằng chứng vừa]** [TIES-Merging](https://arxiv.org/abs/2306.01708) và [LoRA soups](https://arxiv.org/abs/2410.13025) gợi ý trung bình adapter nhiều seed, nhưng không chứng minh giảm biến động 2–4 điểm cho LifeMate; phải chấm từng seed và bản merge. Với [VieNeu-TTS](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo) cùng các bản F5-TTS/viXTTS/MMS-TTS/Chatterbox/Fish/CosyVoice trong CSV, chỉ dùng phát triển sau rà licence; các bản NC loại. Teacher mở lớn hoặc API Meta chỉ dùng khi phát triển theo luật đội đã được BTC xác nhận; giá API thay đổi nên **không tính chi phí giả** nếu chưa có bảng giá công khai đúng model/ngày. Không đưa teacher/TTS vào hệ thống nộp. [Suy luận]

## 8. Cách dùng mới lạ (R5)

1. **Bỏ tower có checkpoint sẵn — khả thi nhất.** [Bằng chứng mạnh] Qwen3.5 full **4.659.865.088** − visual **333.514.240** − MTP **120.599.552** = text-only **4.205.751.296**. Bản [tuandunghcmut](https://huggingface.co/tuandunghcmut/Qwen3.5-4B-text-only) và [principled-intelligence](https://huggingface.co/principled-intelligence/Qwen3.5-4B-text-only) đều có trọng số trước hạn, Apache-2.0. Card tự báo greedy parity; phải tự kiểm logits và BTC xác nhận cách đếm. C1 đã tính cả adapter chưa merge.
2. **Vocabulary trimming — toán đúng, lịch/rủi ro cao.** [Bằng chứng mạnh] Qwen3.5 có vocab **248.320**, hidden **2.560**, embedding tied. Bỏ 50.000 token tiết kiệm **128.000.000** tham số. Để full Qwen3.5 + Pho-large + LoRA r32 xuống <6B cần bớt hơn **264.118.528** tham số: 4.659.865.088 + 1.543.304.960 + 60.948.480 − 6.000.000.000 = **264.118.528**. Vì trần là dấu `<`, phải loại **≥103.172** token (264.120.320 tham số), còn **≤145.148** token. Tokenizer phải bảo toàn tiếng Việt, English, JSON, tool/app/person/ID; nếu không, điểm có thể giảm. [Paper vocab trimming](https://arxiv.org/abs/2305.15020) [Bằng chứng vừa]. Gemma4 E2B nếu embedding tied 1.536 chiều thì 50.000 token tương ứng 76,8M; cần kiểm tie và tensor thực trước tính hợp lệ. Xếp sau 13/11.
3. **Turbo hóa PhoWhisper-large.** [Suy luận từ config] Mỗi decoder layer Whisper large có **26.236.160** tham số theo chênh lệch OpenAI large-v3 và turbo chia 28. Nếu giữ encoder và giảm decoder PhoWhisper 32→4 lớp theo cùng kiến trúc, lý thuyết bớt **734.612.480**, từ **1.543.304.960** xuống **808.692.480**. Đây là phép tính cấu trúc, **không** có checkpoint PhoWhisper tương ứng và không có WER. Fine-tune/distill trong hai ngày không có bằng chứng sẽ giữ chất lượng; xếp sau cuộc thi. [Whisper turbo gốc](https://huggingface.co/openai/whisper-large-v3-turbo), [nghiên cứu pruning encoder](https://arxiv.org/abs/2609.27980) [Bằng chứng vừa]
4. **Prune/distill LLM 7–8B → <5B.** [Minitron](https://arxiv.org/abs/2408.11796), [ShortGPT](https://arxiv.org/abs/2403.03853) cho cách làm, nhưng cần checkpoint đã phát hành hợp lệ hoặc GPU-giờ và dữ liệu distill lớn. Chưa tìm thấy checkpoint vừa đáp ứng đủ LifeMate/tool/vi/licence/ngày. Không đưa vào top 5. [Bằng chứng vừa; Chưa kiểm chứng với bài này]
5. **Nhiều LoRA trên cùng base.** [Bằng chứng mạnh] Với Qwen3.5 text-only, LoRA r32 trên target cũ là **42.467.328**; thêm linear-attention `in_proj_qkv/in_proj_z/out_proj` thành **60.948.480**. Hai adapter như vậy cộng **121.896.960** nếu cùng nạp; phải đo chuyển adapter và đếm cả hai. Dùng một adapter merge/average có thể giữ tổng thấp hơn; chất lượng chưa biết. [Suy luận]
6. **Hai ASR + ROVER/chọn theo slot.** [Bằng chứng mạnh] C6 cộng Moonshine 27.015.360 vào C0 vẫn <6B. [Suy luận] Chỉ chấp nhận nếu số/giờ/tên ít sai hơn trên dev; voting token có thể làm hỏng literal. Không dùng kết quả public/private để train.
7. **Depth up-scaling.** [SOLAR](https://arxiv.org/abs/2312.15166) là tiền lệ; chưa tìm được checkpoint 3–4B→<5B có chứng cứ tiếng Việt/tool trước 26/10. Tự làm không kịp. [Bằng chứng vừa; Chưa kiểm chứng]

## 9. Tổ hợp, thời gian và biên Pareto (R6)

Mọi tổng trong bảng là **[Bằng chứng mạnh]** theo tensor/config đã ghi; trường hợp Gipformer là **[Bằng chứng vừa]** vì số config. VRAM trọng số bf16 ≈ `2 × tổng / 10⁹` GB; 4-bit ghi lower bound `0,60 × tổng / 10⁹`, **chưa** gồm KV cache/activation. Thời gian dưới đây là **[Suy luận]** trên 5090, chưa có phép đo máy chấm: prompt 3–5 nghìn token, ~90 token sinh, audio 1–4 file ~5 giây/file; cần đo p95, không cộng benchmark token/s từ GPU khác như số chắc chắn. A30 có thể chậm hơn.

| Mã | Thành phần rút gọn | Tổng | Dư 6B | LLM kể LoRA | Ước 5090/mẫu | Mức chứng cứ/lý do xếp |
|---|---|---:|---:|---:|---|---|
| C1 | Qwen3.5 text + Pho-large + LoRA | 5.810.004.736 | 189.995.264 | 4.266.699.776 | 6–20 s | Ưu tiên: giữ ASR tốt, đổi agent; điểm chưa đo |
| C0 | Qwen3-4B + Pho-large + LoRA | 5.631.833.344 | 368.166.656 | 4.088.528.384 | 5090 chưa đo | Đối chứng public 51,16 |
| C2 | Qwen3.5 full + turbo + LoRA | 5.529.691.648 | 470.308.352 | 4.720.813.568 | 5–18 s | Agent mạnh hơn có thể bù ASR yếu hơn |
| C3 | Qwen3.5 full + Qwen-ASR + LoRA | 5.658.822.144 | 341.177.856 | 4.720.813.568 | 6–24 s | Cần đo ASR và hai runtime |
| C7 | Qwen3 Thinking + Pho-large + LoRA | 5.631.833.344 | 368.166.656 | 4.088.528.384 | 10–30+ s | Dễ giữ ASR; rủi ro timeout |
| C6 | C0 + Moonshine tiny-vi | 5.658.848.704 | 341.151.296 | 4.088.528.384 | 7–22 s | Thử consensus slot rẻ |
| C5 | Qwen3.5 full + Gipformer + LoRA | 4.789.439.079 | 1.210.560.921 | 4.720.813.568 | 5–17 s | ASR số theo config; WER miền chưa biết |
| C8 | Qwen3.5 text + Qwen-ASR + Qwen3-0.6B verifier | 5.895.392.256 | 104.607.744 | 4.957.383.680 | 8–25 s | Chỉ vừa <5B nếu adapter **merge**; sau cuộc thi |
| C12 | Voxtral Mini 3B audio trực tiếp | 4.676.271.104 | 1.323.728.896 | 4.014.136.320 | 7–25 s | Tiếng Việt nói chưa chứng minh; sau cuộc thi |
| C13 | Gemma4 E2B audio trực tiếp | 5.123.178.979 | 876.821.021 | 4.647.449.891 | 8–25 s | Licence/luật split hỏi BTC; sau cuộc thi |

Các tổng đều **<** ngưỡng tương ứng theo cách hiểu chặt. C8 có dư LLM **42.616.320**; nếu nạp LoRA 60.948.480 chưa merge thì **vượt**. C14 Qwen2.5-Omni tuy số vừa, bị **loại bởi licence**. Bảng 20 tổ hợp và tất cả cột chi phí/GPU-giờ ở CSV. Chi phí tính tham khảo **$0,34–0,70/GPU-giờ** dựa [Runpod](https://www.runpod.io/gpu-models/rtx-4090) và [Vast](https://vast.ai/article/how-much-does-it-cost-to-rent-a-gpu-in-the-cloud-live-pricing-guide), là giả định đặt chỗ, không phải báo giá cố định. [Bằng chứng vừa]

**Biên Pareto để chọn thí nghiệm:** C0 có điểm đã biết/rủi ro thấp; C1 giữ ASR và thử agent mới với rủi ro vừa; C2/C3 đổi cả điểm ASR và agent, rủi ro cao hơn; C5 có dư tham số lớn nhưng ASR chưa đo; C12 có tổng thấp/audio trực tiếp nhưng tích hợp và chất lượng tiếng Việt mơ hồ. Không phương án nào được chứng minh thống trị C0 về *private score*. [Suy luận]

## 10. Đối thủ và bài toán tương tự (R7)

**[Bằng chứng vừa]** Hai README công khai, không chứa transcript/nhãn, cho thấy các hướng [Qwen3.5-4B + faster-whisper](https://github.com/MrPickle200/zalo-ai-2026-lifemate) và [Gipformer/Zipformer + SEA-LION 4B](https://github.com/trtkiet/zalo-ai-challenge). Chúng không công bố ablation đáng tin cho private; không suy ra leaderboard **96,66** đến từ ASR, dữ liệu sinh hay model nào. [Suy luận] Với rule hash 0 nếu lệnh ghi sai, điểm public cao có thể do đúng policy/schema/app mới; không có bằng chứng nguồn công khai để quy nguyên nhân. Các benchmark spoken function calling/[VoiceBench](https://arxiv.org/abs/2410.10125) và tool use đánh giá năng lực chung, không chấm cùng state_hash hay app LifeMate; chỉ dùng tạo giả thuyết. [Bằng chứng vừa]

## 11. Thẻ thí nghiệm ưu tiên (R8)

Tiêu chí chung **viết trước**: chấm cùng split `fit_lao`→40 rồi 262 `dev_lao`, giữ C0 cùng seed; đối với ASR dùng `scripts/asr_quality.py` và WER/độ đúng **số, giờ, tên** trên dev nội bộ. Không lấy transcript public/private làm nhãn. Bất kỳ ứng viên nào vượt **25 giây p95 nội bộ** hoặc 30 giây hard cap, lỗi Docker/offline/licence thì bỏ; lợi thế score dưới **4 điểm** phải kiểm lại seed thứ hai vì nhiễu đã quan sát 2–4. Các ngưỡng là **[Suy luận]**; các mốc nhiễu là **[Bằng chứng mạnh]** nội bộ. Máy 4070 8 GB, 2×4090 mượn hoặc thuê 4090; GPU-giờ/cost ở CSV là lập kế hoạch, không bảo đảm.

1. **C1 — chạy trước 13/11.** Giả thuyết Qwen3.5 text hiểu schema mới hơn mà giữ Pho ASR. Tải `tuandunghcmut/Qwen3.5-4B-text-only` revision trong CSV (~8,4 GB bf16) và adapter train mới; Pho-large-ft đội đã có. Sửa `prompt.py` chat template, `agent.py` loader/vLLM, `train.py` target LoRA gồm linear attention. Phép thử rẻ: load/greedy 10 prompt schema tự tạo, SFT ngắn 40 dev_lao, rồi 262 × 2 seed nếu ≥C0+4. Dự toán **8–20 GPU-giờ**, ~$3–14 khi thuê; kiểm đúng count/runtime trước tải. Giữ nếu hai seed trên 262 vượt C0 trung bình ≥4 và không lỗi hash/timeout; nếu không giữ C0. [Suy luận]
2. **C0 — chạy đối chứng song song.** Không tải model mới; chạy lại 262 dev_lao, đo p50/p95 và Docker trên đúng image. **0–2 GPU-giờ**. Chốt nếu C1–C3 chưa vượt ngưỡng hoặc BTC chưa giải thích tower. [Bằng chứng mạnh về baseline; Suy luận về quyết định]
3. **C2 — trước 13/11 nếu C1 runtime vướng.** Tải `Qwen/Qwen3.5-4B` (~9,3 GB bf16), dùng turbo-ft đội có. Sửa cùng nơi C1. **8–18 GPU-giờ**. Giữ chỉ khi 262 dev_lao hai seed >C0+4 dù ASR turbo; nếu không, loại. [Suy luận]
4. **C3/C17 — kiểm ASR trước khi train.** Tải `Qwen/Qwen3-ASR-0.6B` (~1,9 GB bf16), sửa `asr.py` để dùng processor/Qwen ASR, đo WER và slot trên dev_random/dev_lao; C17 giữ Qwen agent cũ là ablation rẻ **2–8 GPU-giờ**, C3 thêm SFT **10–24**. Bỏ nếu slot số/giờ/tên kém Pho-large >2 điểm tuyệt đối hoặc độ trễ không đạt; chỉ SFT C3 khi ASR đạt. [Suy luận]
5. **C7 — trước 13/11 nếu còn GPU.** Tải `Qwen/Qwen3-4B-Thinking-2507` (~8,0 GB bf16); train agent với output cap, dùng Pho ASR cũ. **8–20 GPU-giờ**. Giữ khi hai seed +4 và p95 ≤25s; reasoning token/greedy có thể loại ngay. [Suy luận]
6. **C6 — phụ sau C1/C2.** Moonshine tiny-vi ~54 MB nếu chuyển bf16; phép đo Pha D dùng **108 MB fp32** và WER **41,29**. Chỉ bổ sung consensus cho slot có confidence sau khi chứng minh lỗi bổ sung; **4–10 GPU-giờ** chủ yếu đánh giá. Giữ nếu không giảm bất kỳ nhóm số/giờ/tên và tăng dev_lao ≥4 qua hai lần; không đủ bằng chứng thì bỏ. [Bằng chứng mạnh về WER; Suy luận về quyết định]
7. **Sau cuộc thi:** C8, C12/C13, vocab trimming, PhoWhisper turbo hóa, distill/prune. Cần 16–50+ GPU-giờ, sửa pipeline/audio và hỏi luật; không kịp kiểm lặp trước 13/11. [Suy luận]

## 12. Phản biện: vì sao đổi model có thể không giúp

1. **1.545 mẫu SFT là nút thắt.** [Suy luận] Model lớn hơn overfit schema train. Kiểm dev_random và dev_lao riêng, đặc biệt app chưa thấy; không chỉ score gộp.
2. **Nhiễu seed 2–4 điểm.** [Bằng chứng mạnh nội bộ] Một run +2 chưa chứng minh gì; cần hai seed/so cùng seed và ngưỡng +4.
3. **ASR slot quan trọng hơn WER.** [Suy luận] Một chữ số sai có thể hash 0; đo số/giờ/tên, rồi score agent với cùng transcript ASR.
4. **Qwen3.5 text-only có thể khác full hoặc kém Qwen3-4B trong greedy.** [Bằng chứng vừa về parity card; Suy luận về task] Kiểm logits một tập prompt nhân tạo và 262 dev_lao.
5. **Template/tool-call không khớp code.** [Bằng chứng mạnh về code đội] `prompt.py` dùng ChatML Qwen + `<tool_call>`, còn Qwen3.5 hybrid có template riêng; smoke test JSON parse và vòng lặp đọc.
6. **Latency/chính sách phần cứng chưa rõ.** [Bằng chứng mạnh về mâu thuẫn tài liệu] Đo p95 trên máy tương tự, kiểm A30/5090 với BTC, cap bước/tool.
7. **Benchmark tự báo không chuyển miền.** [Suy luận] BFCL/ViMD/FLEURS có chuẩn hóa/task khác state_hash LifeMate; chỉ tin dev nội bộ và public submission hợp lệ sau khi đội quyết.

## 13. Phụ lục: độ phủ, truy vấn, giới hạn

**[Bằng chứng mạnh]** `model_candidates_2026-11-08.csv` sàng lọc **153 dòng**: **59 LLM, 40 ASR, 12 speech-LLM, 7 aux + 16 technique, 14 TTS, 3 teacher, 2 draft**. Trong đó `verified` chỉ là tồn tại/số metadata, `reported` là card/config, `unverified` là tên/đếm/licence chưa đủ, `excluded` ghi lý do. 20 tổ hợp; 130 dòng nguồn. Vượt độ phủ yêu cầu 40/30/10/15/10 về **sàng lọc**; số repo tồn tại chắc chắn tương ứng 50/30/10/20/10, song không tuyên bố mọi dòng đã được xác minh sâu. Hạt giống không thấy repo chính xác được giữ `unverified`, không dựng số từ tên.

**Truy vấn/nguồn đã quét:** HF API `text-generation`, `automatic-speech-recognition`, `audio-text-to-text`, `any-to-any`, lọc `vi` và `createdAt`, `downloads/likes`; riêng ASR `vi` quét sáu trang đến trước 06/2026, thấy **424 repo** tạo 01/06–25/10 (nhiều bản sao). Quét org Qwen, Google, Microsoft, NVIDIA, IBM, Mistral, LiquidAI, VinAI, g-group, Moonshine, 5CD-AI; ModelScope/GitHub release và arXiv theo từ khóa `Vietnamese speech recognition 2026`, `small function calling model`, `spoken function calling`, `vocabulary trimming`, `Whisper decoder pruning`, `越南语 语音识别 模型`, `小模型 函数调用 4B`, `nhận dạng giọng nói tiếng Việt mô hình mở 2026`. Tra [BFCL](https://gorilla.cs.berkeley.edu/leaderboard.html), [SEA-HELM](https://sea-helm.ai/), [HF Hub](https://huggingface.co/models), các model card và paper trong `model_sources_2026-11-08.csv`. [Bằng chứng mạnh về thao tác; Chưa kiểm chứng về độ đầy đủ toàn Internet]

**Giới hạn:** HF API rate-limit 500/5 phút; một số repo gated/`pt` hoặc external backbone không thể đếm tensor toàn bộ bằng safetensors. Nhiều first-weight commit chưa xác minh; `createdAt` **không** thay ngày trọng số, nên các dòng ấy không được dùng làm đề xuất cuối nếu thiếu kiểm tra. Số WER khác tập/normalization không so trực tiếp. Pha D chỉ chạy CPU ASR nhỏ như bảng trên; không chạy GPU, train, LLM hoặc API trả phí. Không đọc thư mục `_environment`, không gán nhãn public/private. Không có phép đo RTX 5090 và không biết nguồn của điểm top public 96,66. [Bằng chứng mạnh]

**Tái lập metadata:** chạy `tools/hf_model_audit_2026-11-08.py` để lấy HF metadata (có thể rate-limit), `tools/safetensors_header_audit_2026-11-08.py` để đếm Range header cho checkpoint cần xét, rồi `tools/enrich_candidates_2026-11-08.py`, `tools/build_model_combos_2026-11-08.py`, `tools/build_model_sources_2026-11-08.py`. CSV bàn giao chứa các sửa thẩm định thủ công về licence/partial checkpoints; không chạy lại script thô lên CSV bàn giao mà không đối chiếu các sửa ấy. [Bằng chứng mạnh]
