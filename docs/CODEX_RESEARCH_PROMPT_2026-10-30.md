# Prompt cho Codex: deep research đối chiếu giải pháp ZAC 2026 LifeMate

> **Cách dùng:** mở Codex trong thư mục `~/Zalo AI Challenge` rồi gõ:
> *"Đọc và làm đúng theo `docs/CODEX_RESEARCH_PROMPT_2026-10-30.md`."*
> Claude viết ngày 30/10/2026, theo yêu cầu của Anh. Mọi thứ dưới đây là chỉ dẫn cho Codex.

---

## 0. Vai trò, mục tiêu, sản phẩm

**Vai trò:** nhà nghiên cứu độc lập, có tính phản biện. Bạn **không** viết code cho dự án, **không** train, **không** chạy job. Bạn đọc kỹ repo, tìm hiểu rộng các paper, kỹ thuật, model và repo công khai, rồi đối chiếu với những gì đội (Anh, leader và Claude) **đã làm, đang làm và định làm**.

**Mục tiêu:** trả lời bằng bằng chứng có trích dẫn câu hỏi sau:

> *Với ràng buộc của cuộc thi và 16 ngày còn lại, những giải pháp nào (từ nghiên cứu và thực tiễn) có triển vọng cao nhất để tăng điểm **private test**? Đội đang làm đúng, thiếu, hay sai ở đâu so với hiện trạng tri thức?*

**Sản phẩm** (chỉ ghi vào 2 file này, xem mục 9):
1. `docs/research/CODEX_DEEP_RESEARCH_2026-10-31.md`: báo cáo bằng **tiếng Việt** (giữ thuật ngữ kỹ thuật tiếng Anh), theo cấu trúc ở mục 9.
2. `docs/research/codex_sources_2026-10-31.csv`: bảng nguồn, mỗi nguồn một dòng.

Khi xong, trả lời trong chat bằng 10–15 dòng tóm tắt và đường dẫn 2 file.

---

## 1. Luật an toàn trên máy này (bắt buộc, không ngoại lệ)

Máy này là laptop của Anh (RTX 4070 8GB, RAM 14GB). **Đang chạy job dài tới khoảng 6 giờ sáng 31/10:**
- unit `lifemate-phase2-d`: 3 lượt train của thí nghiệm D;
- sau đó unit `lifemate-e2e-baseline`: lượt đo ASR → agent.

Hai job này chạy **từ chính thư mục repo này**.

1. **Không dùng git để thay đổi gì:** không `checkout`/`switch`/`stash`/`reset`/`pull`/`merge`/`commit`/`add`/`push`, không tạo branch. Đổi nhánh sẽ xoá script và dữ liệu đang được job dùng; ngày 30/10 đã xảy ra sự cố này. Được dùng lệnh git chỉ đọc: `git log`, `git show`, `git diff`, `git branch -a`, `git ls-files`.
2. **Không dùng GPU, không chạy job nặng.** Không chạy `train*.sh`, `phase2_d.sh`, `e2e_baseline.sh`, `predict.sh`, `eval_ckpt.sh`, `lifemate.infer`, `lifemate.asr`, `lifemate.train`. Nếu cần một phân tích nhỏ trên CPU, giới hạn dưới 2 phút và dưới 1GB RAM, với `CUDA_VISIBLE_DEVICES=""`. Ví dụ đếm phân bố trong `train.jsonl` bằng `python3`.
3. **Không cài gói** vào `lifemate/.venv`. Không tải model hay dataset.
4. **Chỉ ghi file vào `docs/research/`** (tạo thư mục nếu chưa có) và `/tmp`. Không sửa file nào khác.
5. **Không đụng** `lifemate/runs/`, `lifemate/ckpt/`, `lifemate/sft/`, `lifemate/gen/`, `lifemate/asr/`. Được đọc file nhỏ trong `runs/` (`*_score.json`, `compare_*.json`) để lấy số liệu.
6. **Dữ liệu thi có licence cấm phát tán, và repo GitHub đang public:**
   - Không dán câu nói, nhãn, kết quả tool hay nội dung `data/` vào công cụ tìm kiếm, web hay bất kỳ dịch vụ ngoài nào.
   - Trong báo cáo, chỉ dùng ví dụ tự đặt (diễn giải lại), không chép nguyên văn mẫu train.
   - **Không đọc** `data/train+public_test/*/*_environment/`: luật thi cấm agent đọc thư mục này, và nghiên cứu cũng không cần.
7. **Không dùng nhãn test:** nếu tìm thấy nguồn công khai nào chứa transcript hay nhãn của public/private test, **không mở tải, không dùng**; chỉ ghi vào báo cáo rằng nó tồn tại.
8. **Không bịa:**
   - Mọi khẳng định quan trọng phải có nguồn kiểm chứng được (URL, arXiv ID, model card, README repo).
   - Nếu không truy cập được web, hoặc chỉ nhớ mà chưa mở nguồn, ghi rõ **"chưa kiểm chứng"**.
   - Nếu hoàn toàn không có quyền duyệt web, dừng lại và báo, thay vì viết báo cáo từ trí nhớ.

---

## 2. Bối cảnh tóm tắt (đọc để định hướng; số liệu phải đối chiếu lại với file ở mục 3)

### 2.1 Đề bài
- **Zalo AI Challenge 2026, bài LifeMate.**
- **Đầu vào:** audio tiếng Việt của yêu cầu cuối (có thể lẫn tiếng Anh, giọng Bắc/Trung/Nam) và `context`:
  - giờ hiện tại, vị trí, profile;
  - `installed_apps`: danh sách tool được phép gọi.
- **History:** các lượt trước. Lượt user **chỉ có audio**; lượt assistant có text, tool_calls, tool_results.
- **Đầu ra mỗi mẫu:** `{"id", "tool_calls", "state_hash"}`. Agent gọi tool qua `zaic_tools.ToolEnv` (môi trường giả lập của BTC), mỗi mẫu đúng **một** env, và mọi call đã gọi đều tính.
- **Ba kiểu hành vi trong nhãn:**

  | Kiểu | Tỉ lệ ở train | Hành vi đúng |
  |---|---|---|
  | Thực thi | khoảng 79% | Gọi tool cho tới khi đạt trạng thái mong muốn |
  | Hỏi thiếu thông tin | khoảng 14% | `sys.ask_missing_info(tool_name, params)`, luôn là call cuối |
  | Ngoài phạm vi | khoảng 7% | `[]` |

- **Chấm điểm:**
  - Hash state sai thì mẫu được 0. Nếu hash đúng, điểm là F1 trên tập call.
  - Tham số `x-match: fuzzy` được so bằng token-F1 > 0,6; tham số khác phải khớp chính xác.
  - Call bị từ chối vì sai schema vẫn bị tính là call thừa.
  - Mẫu ngoài phạm vi: nộp `[]` được 1, gọi bất kỳ call nào là 0.
- **Ràng buộc:**
  - Tổng tham số toàn hệ thống (ASR + LLM + mọi thứ) **< 6B**; LLM **< 5B**; context ≤ 16.384 token.
  - **30 giây/mẫu** trên 1 GPU A30 24GB, chạy **offline**.
  - Tái lập được: greedy; nếu kết quả khác nhau giữa các lần chạy, BTC chạy 5 lần lấy trung bình.
  - Chỉ dùng model mã nguồn mở có trọng số **phát hành trước 26/10/2026**, licence cho phép.
  - Được dùng LLM hoặc TTS ngoài để sinh dữ liệu **lúc phát triển**, không được dùng lúc suy luận.
  - **Cấm gán nhãn hay pseudo-label public/private test.**
- **Dữ liệu:**
  - Train 1.545 mẫu có nhãn, có `audio_text`; public_test 634 mẫu.
  - 46 app / 147 tool ở train. **Public có 11 app không có trong train**, và private gần như chắc chắn có app mới.
  - Audio 16 kHz, trung bình 5,1 giây; train có 5.036 câu nói, tổng 6,83 giờ.
- **Lịch:**
  - Hôm nay 30/10/2026 tối.
  - **Nộp Docker 16/11/2026 23:59**, tối đa 2 lần, lấy lần cuối.
  - Private test 20–23/11.
  - Public leaderboard cho tối đa 5 lần nộp/ngày.
- **Đội:**

  | Người | Máy | Phụ trách |
  |---|---|---|
  | Anh | laptop RTX 4070 8GB | agent / LLM |
  | Leader | RTX 3050 4GB | ASR, chuẩn hoá số, Docker |
  | Claude | — | agent code (viết code, chạy đo) |
  | Codex | — | từng làm audit / review (`docs/TRAIN_REVIEW_2026-10-29.md`, `docs/REVIEW_CLAUDE_EVAL_2026-10-29.md`) |

  Ngân sách cloud không giới hạn, nhưng thuê cloud và nộp bài là Anh quyết.

### 2.2 Kiến trúc đã chốt (28/10)
- **Nối tầng:** ASR (~0,8–1,5B) → chuẩn hoá chữ thành số (ITN, chưa làm) → prompt (luật, profile, bảng ngày −7…+14, schema tool viết gọn, history kèm tool_results) → vòng lặp agent Qwen3 greedy → `env.validate()` → `env.call()`.
- **Lớp kiểm soát bằng code:**
  - validate trước khi gọi, nên call sai không lọt vào bài nộp;
  - bỏ trùng call đọc;
  - dừng ngay sau `ask_missing_info`;
  - tối đa 8 bước, khoảng 25 giây.
- **Không dùng audio-LLM end-to-end** (lý do ở JOURNAL mục 4). **Cần bạn đánh giá lại quyết định này** bằng bằng chứng mới, xem trục H ở mục 5.
- **LLM dự kiến:** Qwen3-4B-Instruct-2507 (SFT trên cloud, chưa làm). **Hiện mới chạy Qwen3-1.7B LoRA** trên máy local.

### 2.3 Số liệu hiện có (đều dùng chữ chuẩn `audio_text`, **chưa qua ASR**)

| Mốc | Train → chấm | Điểm |
|---|---|---|
| Nộp rỗng | – → train | 7,18 |
| Zero-shot Qwen3-1.7B | – → dev_random / dev_lao | 9,90 / 10,88 |
| SFT Qwen3-1.7B LoRA r32, 1 epoch | fit_random → dev_random (233 mẫu) | **53,92** (ask 49,4; execute 51,0; OOS 94,1) |
| B0, app chưa thấy | fit_lao → dev_lao (262 mẫu; 6 app giữ riêng) | **35,53** (ask 7,48; execute 39,73; OOS 71,43) |

- **Khoảng cách tổng quát hoá:** 80,2 trên mẫu đã train, so với 53,9 trên dev.
- **Điểm yếu lớn nhất đã đo:** ranh giới hỏi lại / tự làm. Ở dev_random, 30 mẫu mất 12,7 điểm. Ở dev_lao, các mẫu hỏi lại về tool của app chưa thấy được **0/23**. Khi bỏ hỏi, model thường gọi tool đích với giá trị **tự bịa** cho đúng tham số lẽ ra phải hỏi.
- **Đặc điểm nhãn đã đo** (`docs/PIPELINE.md` mục 1.2 và 3.2):
  - Tham số của lệnh ghi: 46% lấy từ kết quả tool, 15% từ history, 15% là ngày giờ phải tính, 11% là số phải tính, gần 0% chép nguyên văn lời nói.
  - Query `contacts.search` là tên lưu trong danh bạ.
  - `ask_missing_info` luôn là call cuối.
  - Lượt assistant trong history theo quy ước khác với nhãn.
- **Kiểu viết số:** `audio_text` viết số bằng chữ nhiều hơn chữ số (1.371 so với 481 câu), trong khi Whisper hay xuất chữ số.

### 2.4 Đã làm, đang làm, định làm (đối tượng để bạn đánh giá)

| Hạng mục | Trạng thái | Ở đâu |
|---|---|---|
| Bộ chấm local, phát lại đáp án ra 100, kiểm trùng id / thiếu prediction | Đã làm | `lifemate/lifemate/scorer.py`, PR #1–#2 |
| Prompt ChatML, schema gọn, bảng ngày; SFT khớp prompt suy luận từng ký tự | Đã làm | `prompt.py`, `sft.py`, `scripts/check_sft.py` |
| SFT augmentation: đổi tên app/tool, gỡ app → `[]`, app gây nhiễu (cả app public), transcript kiểu ASR (viết thường, bỏ dấu câu, p = 0,3); gộp call độc lập vào một bước | Đã làm | `sft.py`, JOURNAL 6.3 |
| LoRA SFT bằng PyTorch thuần: logits chỉ ở vị trí có loss, gradient checkpointing, r32, lr 2e-4, 1 epoch | Đã làm | `train.py`, JOURNAL 6.4 |
| Protocol đánh giá: dev_random, dev_lao (leave-apps-out), so theo cặp với bootstrap CI, provenance | Đã làm | `compare.py`, `runinfo.py`, `docs/EVAL_2026-10-29.md` |
| Thí nghiệm B: đo app chưa thấy | Đã làm | EVAL mục 7 |
| Luật tất định cho hỏi lại kiểu A (trùng tên): thử rồi **loại** vì chỉ kích hoạt 0–2 mẫu | Đã làm | `docs/EXPERIMENT_D.md` |
| **Thí nghiệm D:** dữ liệu phản thực tế cặp đủ/thiếu slot và mơ hồ/cụ thể. Câu viết lại do LLM; nhãn phát lại qua ToolEnv; bộ lọc nguồn, judge, chặn rò rỉ nhãn; D-train 77 mẫu | Đang làm. Giai đoạn 2 đang train 3 lượt so khớp số bước (B-D3, B-up đối chứng, B-D1), có tiêu chí giữ/bỏ đặt trước | `docs/EXPERIMENT_D.md`, `docs/REVIEW_D_2026-10-30.md`, `docs/D_PHASE1*.md`, `lifemate/lifemate/counterfactual.py` |
| **Baseline đầu-cuối:** ASR có sẵn (Whisper-large-v3-turbo, PhoWhisper-large; chưa fine-tune) → agent; chỉ số ASR theo slot; lệnh offline `predict.sh` | Code xong (PR #4); lượt đo đang xếp lịch | `lifemate/lifemate/asr.py`, `lifemate/scripts/asr_quality.py`, `lifemate/scripts/predict.sh`, `lifemate/scripts/e2e_baseline.sh`, JOURNAL entry 21 |
| Thí nghiệm A (2 epoch); thí nghiệm C (giữ call JSON hỏng, nhắc khi gặp `done=false`) | Định làm | EVAL mục 5.3 |
| Tầng T2: code tất định cho ngày giờ, số; ép ID phải là giá trị đã thấy; chuẩn hoá call đọc | Định làm | `docs/PIPELINE.md` mục 4 |
| Tầng T3: dữ liệu app tổng hợp đúng chính sách nhãn (LLM mạnh sinh app, schema, simulator, câu, nhãn; kiểm bằng chạy thật) | Định làm, **được coi là moat chính** | PIPELINE mục 1.3, 4 |
| Tầng T4: ASR theo slot (fine-tune trên 6,8 giờ train, ITN, gợi ý ngữ cảnh), transcript k-fold để SFT | Định làm (leader) | PIPELINE mục 4, HUMAN_TODO Q9–Q12 |
| Tầng T5: vLLM, Qwen3-4B, đo trên GPU 24GB, tái lập 5 lần, Docker offline | Định làm | PIPELINE mục 4, HUMAN_TODO Q16, Q19 |
| 20 câu hỏi nghiên cứu Q1–Q20 | Phần lớn mới là giả thuyết | `docs/PIPELINE.md` mục 5, `HUMAN_TODO.md` mục 8 |

---

## 3. Đọc gì, theo thứ tự nào (bắt buộc trước khi tìm kiếm)

Đọc kỹ; ghi lại số liệu kèm đường dẫn file để trích trong báo cáo.

1. `JOURNAL.md`: toàn bộ, đặc biệt mục 0 (trạng thái), 1 (đề và luật), 2–3 (dữ liệu, phát hiện), 4 (kiến trúc), 6 (code), 7 (nhật ký entry 1–21), 8 (việc tiếp theo).
2. `docs/PIPELINE.md`: moat, pipeline nền móng, tự đánh giá, đề án T1–T5, 20 câu hỏi.
3. `HUMAN_TODO.md`: câu trả lời làm việc cho Q1–Q20, việc của người.
4. `docs/EVAL_2026-10-29.md`, `docs/TRAIN_REVIEW_2026-10-29.md`, `docs/REVIEW_CLAUDE_EVAL_2026-10-29.md`, `docs/CLAUDE_HANDOFF_2026-10-29.md`: phân tích lỗi, protocol, các quyết định.
5. `docs/EXPERIMENT_D.md`, `docs/REVIEW_D_2026-10-30.md`, `docs/D_PHASE1_2026-10-30.md`, `docs/D_PHASE1B_2026-10-30.md`, `docs/baselines/*.json`: thí nghiệm D.
6. `data/train+public_test/README.md` và `data/train+public_test/train/zaic_tools/README.md`: luật chính thức về định dạng, tool, hash.
7. Code (đọc để biết **chỗ nào** một kỹ thuật sẽ cắm vào; không sửa):
   - `lifemate/README.md`
   - `lifemate/lifemate/prompt.py`
   - `lifemate/lifemate/agent.py`
   - `lifemate/lifemate/sft.py`
   - `lifemate/lifemate/train.py`
   - `lifemate/lifemate/scorer.py`
   - `lifemate/lifemate/askpolicy.py`
   - `lifemate/lifemate/counterfactual.py`
   - `lifemate/lifemate/asr.py`
   - `lifemate/lifemate/infer.py`
   - `lifemate/scripts/*.py`, `lifemate/scripts/*.sh`
8. Nếu đã có thì đọc thêm (job đang chạy, có thể chưa có): `lifemate/runs/phase2_d.log`, `lifemate/runs/e2e_baseline.log`, `lifemate/runs/asr_quality_*.json`, `lifemate/runs/sft_*_asr*_score.json`. Chưa có thì ghi "chưa có số liệu".
9. Muốn tự hiểu dữ liệu thì được đọc `data/train+public_test/train/train.jsonl` và các catalog để thống kê nhỏ (theo luật mục 1). Không đọc `*_environment/`.

**Sau khi đọc**, trước khi tìm kiếm, viết vào báo cáo (mục 9, phần 1) **một trang "đội đang đặt cược vào điều gì"**, gồm:
- các giả định ngầm;
- các rủi ro lớn nhất cho điểm private;
- 5 câu hỏi quan trọng nhất mà nghiên cứu bên ngoài có thể trả lời.

---

## 4. Tiêu chuẩn nguồn và trích dẫn

- **Ưu tiên nguồn gốc:** paper (arXiv, ACL Anthology, OpenReview, PMLR), model card và repo chính thức, tài liệu của thư viện. Blog hay bài review chỉ là nguồn phụ, phải ghi rõ.
- **Mỗi nguồn ghi đủ:**
  - tiêu đề, tác giả hoặc tổ chức, năm, venue (hoặc "preprint");
  - URL hoặc arXiv ID;
  - ngày truy cập;
  - với model/repo: licence, ngày phát hành trọng số, số tham số, commit/revision nếu có.
- **Phân loại bằng chứng:** [peer-reviewed] / [preprint] / [model card] / [repo] / [blog] / [chưa kiểm chứng].
- **Trích số liệu từ paper:** ghi rõ benchmark, ngôn ngữ, cỡ model, và vì sao có hoặc không chuyển giao được sang bài này (tiếng Việt, giọng nói, model < 5B, app chưa thấy, chấm bằng hash).
- **Mục tiêu tối thiểu:**
  - ≥ 40 nguồn gốc có liên quan trực tiếp; ≥ 12 repo hay thư viện dùng được;
  - mỗi đề xuất ưu tiên cao có ≥ 2 nguồn độc lập.
- **Ưu tiên công trình mới (2024–2026).** Kiến thức của Claude dừng khoảng giữa 2026, nên các model và paper từ 06/2026 tới 25/10/2026 là phần **bạn cần tìm kỹ nhất**.
- **Không trích dài:** mỗi nguồn tối đa một câu trích dưới 15 từ; còn lại diễn giải bằng lời của bạn.

---

## 5. Trục nghiên cứu (tìm rộng, rồi lọc theo mục 6–7)

Mỗi trục có các câu hỏi cần trả lời và **gợi ý điểm xuất phát**. Gợi ý có thể sai tên hoặc năm, nên **phải tự kiểm chứng**. Không dừng ở gợi ý; tìm thêm công trình liên quan, trích dẫn chéo, và repo đi kèm. Mỗi trục ghi rõ liên quan tới câu hỏi nào trong Q1–Q20.

### A. Tool calling với LLM nhỏ (< 5B) và tổng quát hoá sang tool/app chưa thấy
- Kỹ thuật nào giúp model nhỏ dùng đúng schema **chưa từng thấy**: function masking, đổi tên, viết lại mô tả, curriculum, retrieval tool, tăng đa dạng schema? Mức tăng đo được là bao nhiêu?
- So với cách đội đang làm (`--rename`, gỡ app, app gây nhiễu, leave-apps-out), còn thiếu gì?
- Điểm xuất phát:
  - Berkeley Function Calling Leaderboard (BFCL v3/v4: multi-turn, irrelevance, thiếu tham số / thiếu hàm);
  - Gorilla; ToolLLM/ToolBench; API-Bank;
  - Hammer (function masking); xLAM / APIGen / APIGen-MT; ToolACE;
  - TinyAgent (model nhỏ, tool retrieval); NexusRaven; Arch-Function; Granite function calling;
  - báo cáo kỹ thuật Qwen3 về tool use.
- Q liên quan: Q6, Q15, Q17.

### B. Khi nào hỏi lại, khi nào tự làm, khi nào từ chối (**điểm yếu số 1 của đội**)
- Hiện trạng tri thức về phát hiện thiếu tham số, mơ hồ tham chiếu (chọn 1 trong nhiều mục), và yêu cầu ngoài phạm vi:
  - dữ liệu nào, cách sinh ra sao;
  - loss hay objective nào (SFT, DPO, RL);
  - đo thế nào;
  - model nhỏ đạt được bao nhiêu.
- Đánh giá **thí nghiệm D** của đội so với các phương pháp này: thiết kế cặp phản thực tế, đối chứng nhân bản mẫu thật, so khớp compute. Có cách nào rẻ hơn hoặc mạnh hơn không, ví dụ preference pairs hỏi/không hỏi, hay reward cho việc kiềm chế?
- Điểm xuất phát:
  - When2Call (NVIDIA);
  - các hạng mục missing-parameter / irrelevance của BFCL;
  - ToolSandbox (Apple: stateful, insufficient information);
  - NoisyToolBench và "Learning to Ask" khi chỉ dẫn mơ hồ;
  - τ-bench / τ²-bench;
  - nghiên cứu clarification questions (ClarifyGPT, CLAMBER, AmbigQA);
  - abstention / selective prediction cho LLM.
- Q liên quan: Q4, Q5, Q13.

### C. Dữ liệu tổng hợp tuân theo **chính sách nhãn** của BTC (moat T3)
- Cách sinh app, schema, simulator và trajectory mà nhãn đúng **chính sách của người ra đề**, không theo "thói quen" của LLM sinh dữ liệu:
  - kiểm chứng bằng chạy thật;
  - lọc bằng LLM-judge;
  - đo độ giống thật bằng classifier thật/giả hoặc so phân bố;
  - đo tác động lên app chưa thấy.
- Sinh multi-turn kèm history.
- Kinh nghiệm thất bại: synthetic data làm hại thay vì giúp, model collapse, lệch phân bố.
- Điểm xuất phát:
  - APIGen / APIGen-MT; ToolACE; ToolFlow; BUTTON;
  - Magnet (multi-turn tool use data); Magpie;
  - các pipeline "execution-verified" synthetic data;
  - Seal-Tools; NESTFUL; ComplexFuncBench.
- Đối chiếu với `counterfactual.py`, ý tưởng app tổng hợp trong PIPELINE, và việc được dùng catalog cùng `zaic_tools` của public (JOURNAL 1.5).
- Q liên quan: Q2, Q3, Q17, Q18.

### D. Phương pháp train cho model nhỏ
- SFT recipe cho function calling: mask loss, gộp bước, số epoch, LoRA hay full fine-tune, rank, mức tăng từ 1.7B lên 4B.
- Distillation trajectory từ model lớn (được phép lúc phát triển).
- **RL với reward kiểm chứng được** (GRPO, các biến thể) trên môi trường thực thi tất định. Đội **đã có** env (`ToolEnv`) và bộ chấm, nên có thể dùng điểm thật làm reward.
  - Bằng chứng về mức tăng cho tool calling với model < 5B; chi phí GPU; rủi ro reward hacking.
  - Có khả thi trong 16 ngày không, với GPU nào, bao nhiêu giờ?
- DPO hay preference cho ranh giới hỏi/làm.
- Điểm xuất phát:
  - ToolRL ("reward is all tool learning needs");
  - Nemotron-Research-Tool-N1;
  - các paper GRPO cho agent / tool use 2025–2026;
  - DeepSeek-R1 (phương pháp RL);
  - thư viện TRL, verl, OpenRLHF (hỗ trợ multi-turn env).
- Q liên quan: Q15.

### E. Structured / constrained decoding và guardrail
- JSON schema constrained decoding, ép enum, ép ID nằm trong tập giá trị đã thấy (từ kết quả tool hoặc history).
- Tác động lên độ chính xác (có làm giảm chất lượng không?), tốc độ, tính tái lập.
- Tương thích với vLLM offline trong Docker.
- Vòng validate–retry, so với cách đội đang làm: validate trước khi gọi, trả lỗi lại cho model.
- Điểm xuất phát:
  - XGrammar; Outlines; llguidance; guided decoding của vLLM / SGLang;
  - các paper về ảnh hưởng của format restriction lên năng lực suy luận.
- Q liên quan: Q14.

### F. Thành phần tất định cho tiếng Việt (ngày giờ, số, tiền, ITN)
- Có thư viện hay grammar nào xử lý **biểu thức thời gian tiếng Việt** ("thứ tư tuần sau", "trước 3 tiếng", "tối mai", "5 giờ kém 15")? Còn **chuẩn hoá chữ thành số** ("hai triệu tám", "năm chục nghìn", "một trăm linh năm")?
- Chất lượng, licence, mức bảo trì của từng công cụ.
- Mô hình lai: LLM chọn ý định và phép tính, code tính ra kết quả (program-aided, PAL).
- Điểm xuất phát:
  - NVIDIA NeMo text processing (kiểm xem có ITN tiếng Việt không);
  - `vinorm` (text normalization, chiều ngược lại); underthesea;
  - Duckling (kiểm hỗ trợ tiếng Việt); HeidelTime; dateparser;
  - các paper ITN tiếng Việt; PAL / program-of-thought.
- Đối chiếu với `lifemate/lifemate/vinum.py` (đang chỉ sinh dạng nói từ giá trị, chưa phân tích ngược).
- Q liên quan: Q12, Q13.

### G. ASR tiếng Việt cho trợ lý giọng nói (phần của leader; đội vừa bắt đầu baseline)
- **Model ≤ khoảng 1,5B phát hành trước 26/10/2026**, có số đo trên tiếng Việt: Whisper large-v3 / turbo, PhoWhisper, wav2vec2 / XLS-R tiếng Việt, Zipformer / k2-sherpa, NeMo Parakeet / Canary (kiểm hỗ trợ tiếng Việt), SeamlessM4T, Moonshine, và mọi model mới 2026.
- **Benchmark tiếng Việt:** VLSP các năm, Common Voice vi, VIVOS, FOSD, GigaSpeech 2, ViMD (đa phương ngữ), bộ dữ liệu giọng nói trợ lý ảo hay smart home.
- **Fine-tune trên dữ liệu ít** (khoảng 6,8 giờ in-domain): LoRA hay full, tăng cường giọng hay nhiễu, TTS tổng hợp (Anh có gợi ý VieNeu, cần kiểm licence và ngày phát hành), nguy cơ quên kiến thức cũ.
- **Contextual biasing:**
  - từ ngữ cảnh hợp lệ: tên app đã cài, enum trong schema;
  - từ kết quả tool: tên trong danh bạ;
  - kỹ thuật: prompt của Whisper, hotword, TCPGen, CB-Whisper, shallow fusion.
- **Sửa lỗi ASR bằng LLM:** N-best, generative error correction như HyPoradise.
- **Làm agent bền với lỗi ASR:** train trên transcript ASR (k-fold), trên N-best, hoặc chèn nhiễu.
- **Đo theo slot thay vì WER:** slot error rate, concept error rate.
- Đối chiếu với `asr.py`, `asr_quality.py`, và lựa chọn 2 model của đội.
- Q liên quan: Q9, Q10, Q11, Q12.

### H. Hiểu ngôn ngữ nói (SLU) và audio-LLM end-to-end
- Bài học từ SLU cho trợ lý ảo: SLURP, STOP (Spoken Task Oriented Parsing), Spoken-SQuAD, DSTC (speech-aware dialogue).
- SLU tiếng Việt: PhoATIS / JointIDSF (VinAI), các challenge SLU của VLSP.
- Kiến trúc nối tầng so với end-to-end:
  - **Audio-LLM ≤ 5B** có function calling từ giọng nói: Voxtral Mini, Qwen2.5-Omni 3B, Qwen2-Audio, Phi-4-multimodal (kiểm số tham số), Kimi-Audio, Step-Audio 2 mini, và model mới 2026.
  - Năng lực tiếng Việt có được đo không?
  - Có vừa trần 6B / 5B không?
- **Kết luận cần có:** quyết định nối tầng của đội còn đúng không, với bằng chứng 2026?
- Q liên quan: Q6, Q15.

### I. Hệ thống suy luận: tốc độ, bộ nhớ, tái lập, Docker offline
- vLLM hay SGLang offline cho ASR + LLM trên một GPU 24GB: prefix caching, chia bộ nhớ, cold start.
- Ảnh hưởng của quantization (AWQ, GPTQ, FP8; kiểm A30 hỗ trợ gì) lên độ chính xác tool calling.
- **Tái lập:** non-determinism do batch, phép cộng số thực không kết hợp, và kernel batch-invariant. Điểm xuất phát: bài "Defeating Nondeterminism in LLM Inference" (Thinking Machines Lab, 2025); chế độ batch-invariant hay deterministic của vLLM.
- Kinh nghiệm đóng Docker offline cho cuộc thi AI: tải sẵn trọng số, `HF_HUB_OFFLINE`, CUDA/driver, dung lượng image.
- Q liên quan: Q16, Q19.

### J. Phương pháp đánh giá và tránh overfit leaderboard
- Leave-apps-out / leave-groups-out để mô phỏng phân bố chưa thấy; bootstrap theo cặp; số mẫu cần để phân biệt chênh lệch 1–2 điểm.
- Chiến lược dùng public leaderboard (5 lần/ngày) để dò thước đo mà không overfit; "adaptive data analysis" và reusable holdout.
- Q liên quan: Q6, Q7, Q8.

### K. Tiền lệ của cuộc thi và hệ sinh thái Việt Nam
- Lời giải các năm trước của Zalo AI Challenge và cuộc thi tương tự (VLSP, các cuộc thi agent / tool-use 2025–2026): writeup, repo. Rút ra mẹo thực chiến.
- Thảo luận công khai về ZAC 2026 LifeMate (forum, GitHub, blog). Nhắc lại luật mục 1.7: chỉ ghi nhận, không dùng nhãn test.
- Model hay dữ liệu tiếng Việt từ VinAI, FPT, Viettel, Zalo/VNG, VietAI phát hành trước 26/10/2026, có thể dùng cho ASR, LLM hoặc dữ liệu tổng hợp.

### L. LLM nhỏ phát hành tới 25/10/2026
- Lập bảng ứng viên LLM < 5B. Mỗi model ghi:
  - số tham số, licence, ngày phát hành;
  - tiếng Việt, tool calling, context;
  - benchmark tool use (BFCL hay tương đương);
  - mức hỗ trợ của vLLM.
- Gợi ý: Qwen3-1.7B / 4B (và bản 2507), Llama 3.2 1B/3B, Gemma 3 1B/4B, Phi-4-mini, SmolLM3, Granite (IBM), xLAM-2 nhỏ, Hammer2.x, các model tiếng Việt (Arcee-VyLinh, SeaLLMs, Sailor2, PhoGPT), và **mọi model mới tháng 06–10/2026**.
- **Câu cần trả lời:** có model nào đáng thay Qwen3-4B-Instruct-2507 không? Có model nào đã được train sẵn cho function calling nên SFT ít dữ liệu cũng tốt hơn không?

---

## 6. Bộ lọc tuân thủ: áp cho **mọi** model, dữ liệu, kỹ thuật được đề xuất

Đánh dấu rõ từng tiêu chí trong bảng đề xuất:

1. **Ngày phát hành trọng số < 26/10/2026.** Ghi ngày và nguồn; nếu chỉ có ngày ra paper mà không rõ ngày ra trọng số, ghi "cần hỏi BTC".
2. **Licence** cho phép dùng trong cuộc thi. Ghi riêng các model không thương mại (CC-BY-NC…) và "cần hỏi BTC".
3. **Trần tham số:** ASR + LLM + mọi thành phần < 6B, LLM < 5B. Ghi tổng với từng cấu hình đề xuất.
4. **Chạy offline**, không gọi API lúc suy luận.
5. **30 giây/mẫu trên A30.** Ước lượng thời gian nếu có số liệu; nếu không, ghi "cần đo".
6. **Tái lập** (greedy, kernel tất định).
7. **Không dùng nhãn hay transcript test** để train, không pseudo-label.
8. **Không đọc `*_environment/`** lúc suy luận. Kỹ thuật nào cần "biết state" phải lấy qua tool.
9. **Mỗi mẫu đúng một `ToolEnv`.** Kỹ thuật kiểu "thử nhiều nhánh rồi chọn" (tree search, self-consistency có gọi tool) **không** được reset hay clone env. Mọi call đã gọi đều tính, nên gọi thừa là mất điểm.

Kỹ thuật vi phạm một tiêu chí thì vẫn có thể nhắc tới, nhưng ghi rõ **"không dùng được vì …"** và không xếp hạng.

---

## 7. Khung chấm đề xuất

Mỗi đề xuất ghi đủ các mục sau:

- **Tên.**
- **Giả thuyết:** cơ chế nào làm tăng điểm.
- **Bằng chứng:** nguồn, số liệu, mức độ chuyển giao sang bài này.
- **Tác động dự kiến:**
  - lên loại mẫu nào: execute / ask / OOS;
  - lên phần nào: app đã thấy / chưa thấy, có ASR / không;
  - ước lượng khoảng điểm và nêu cách ước lượng; nếu không ước lượng được thì nói rõ.
- **Chi phí:** số ngày công kỹ sư; số giờ GPU; GPU local 8GB, cloud, hay A30.
- **Rủi ro:** hỏng hash, mất tái lập, chậm, vi phạm luật, phụ thuộc người.
- **Thời gian để có tín hiệu:** bao lâu thì biết có hiệu quả.
- **Cắm vào đâu trong code:** file, hàm; điểm nối với `prompt.py`, `agent.py`, `sft.py`, `train.py`, `counterfactual.py`, `asr.py`, `predict.sh`…
- **Thí nghiệm kiểm chứng** theo đúng phong cách của đội:
  - một thay đổi chính, so khớp compute, so theo cặp trên `dev_random` và `dev_lao`;
  - tiêu chí giữ / bỏ đặt trước;
  - chi phí của thí nghiệm.
- **Phụ thuộc:** cần Anh hoặc leader quyết gì (cloud, nộp public, licence).
- **Xếp hạng:** P0 (làm ngay), P1 (nếu kịp), P2 (sau cuộc thi / không làm). Đặt trong lịch 31/10–16/11, giả định **đóng băng tính năng khoảng 12–13/11** để còn đóng Docker và kiểm tái lập.

**Thang ưu tiên** (dùng để xếp hạng, ghi điểm từng thành phần):
- tác động × độ tin của bằng chứng ÷ (chi phí × rủi ro);
- cộng thêm cho việc **giảm rủi ro mất trắng** ở private: crash, quá giờ, sai định dạng, không tái lập.

---

## 8. Phản biện bắt buộc

Ngoài tìm giải pháp mới, **đánh giá thẳng** các lựa chọn hiện tại. Mỗi điểm nêu rõ đồng ý / không đồng ý, kèm bằng chứng:

1. Nối tầng so với audio-LLM end-to-end (mục 2.2, trục H).
2. Qwen3-1.7B LoRA để thí nghiệm, Qwen3-4B để nộp. LoRA r32 1 epoch có hợp lý không? Nên ưu tiên 2 epoch (thí nghiệm A), 4B, hay đổi model?
3. Thiết kế thí nghiệm D: dữ liệu phản thực tế cho ranh giới hỏi lại. Quy mô 77 mẫu có đủ không? Có phương án nào tốt hơn cho trục B?
4. Đánh giá bằng chữ chuẩn rồi mới thêm ASR. Thứ tự ưu tiên hiện tại (agent trước, đầu-cuối sau) có đúng không, khi hạn còn 16 ngày?
5. Bộ chấm local giả định khắt khe: tham số không fuzzy khớp chính xác, token tách theo khoảng trắng. Có tiền lệ nào về cách chấm của các benchmark tương tự?
6. Moat "dữ liệu tổng hợp đúng chính sách" (T3): có khả thi trong 16 ngày không? Nếu có thì bản nhỏ nhất đáng làm là gì?
7. Những rủi ro đội **chưa nhìn thấy**.

---

## 9. Định dạng đầu ra

### 9.1 `docs/research/CODEX_DEEP_RESEARCH_2026-10-31.md`

Văn phong:
- tiếng Việt, câu ngắn, có số liệu;
- bảng khi so sánh từ 3 thứ trở lên;
- mỗi kết luận gắn nhãn **[Bằng chứng mạnh] / [Bằng chứng vừa] / [Suy luận] / [Chưa kiểm chứng]**;
- trích dẫn dạng `[S12]`, trỏ tới dòng trong file CSV.

Cấu trúc:

0. **Tóm tắt cho người bận** (tối đa 1 trang):
   - 10 khuyến nghị xếp hạng, mỗi khuyến nghị 1–2 dòng gồm tác động, chi phí, P0/P1/P2;
   - 3 điều nên **dừng** hoặc **không làm**;
   - 3 rủi ro lớn nhất cho điểm private.
1. **Đội đang đặt cược vào điều gì** (sau khi đọc repo, trước khi tìm kiếm; xem mục 3).
2. **Bản đồ hiện trạng tri thức** theo các trục A–L. Mỗi trục gồm:
   - những gì đã biết chắc;
   - con số tốt nhất cho model nhỏ;
   - khoảng trống;
   - nguồn.
3. **Bảng đối chiếu** "đội đang làm" và "hiện trạng tri thức" theo từng thành phần: ASR, ITN, prompt/schema, dữ liệu SFT, dữ liệu tổng hợp, chính sách hỏi lại, decoding, code tất định, đánh giá, suy luận, Docker. Cột: đã làm / đang làm / định làm; hiện trạng tri thức; khoảng cách; đề xuất; nguồn.
4. **Danh sách đề xuất đầy đủ** theo khung mục 7, xếp hạng P0 → P2.
5. **Lộ trình đề xuất 31/10–16/11** cho Anh, leader và Claude. Gồm:
   - việc nào song song được;
   - mốc đóng băng;
   - việc nào cần quyết định của người.
6. **Bảng model ứng viên:**
   - ASR: tên, tham số, licence, ngày phát hành, số đo tiếng Việt, ghi chú;
   - LLM: tên, tham số, licence, ngày phát hành, tiếng Việt, tool calling, vLLM, ghi chú;
   - cấu hình ghép kèm tổng tham số.
7. **Bảng repo và thư viện dùng được:** tên, URL, licence, mức bảo trì (commit gần nhất), dùng cho việc gì, rủi ro.
8. **Phản biện** (mục 8): mỗi điểm một kết luận.
9. **Câu hỏi mở và thí nghiệm nhỏ đề xuất** để trả lời chúng, gắn với Q1–Q20.
10. **Phụ lục:** truy vấn đã dùng, nguồn đã xem nhưng loại (kèm lý do), giới hạn của báo cáo.

### 9.2 `docs/research/codex_sources_2026-10-31.csv`

Mã hoá UTF-8, có dòng tiêu đề. Các cột:

```
sid,title,authors_or_org,year,venue_or_type,url,accessed,evidence_type,axes,claims_used,license,weights_release_date,params,relevance_1to5,notes
```

- `sid` dạng `S1, S2, …`, khớp với trích dẫn trong báo cáo.
- `evidence_type`: peer-reviewed / preprint / model-card / repo / blog / unverified.
- `axes`: các trục A–L, ví dụ `B;C`.

---

## 10. Quy trình gợi ý

1. **Đọc repo** (mục 3) và viết phần 1 của báo cáo. Khoảng 15–20% thời gian.
2. **Quét rộng** theo các trục A–L. Với mỗi trục:
   - tìm survey gần nhất;
   - lần theo trích dẫn tới (forward) và lui (backward);
   - tìm repo và model card.
   Ghi nguồn vào CSV ngay khi đọc.
3. **Đào sâu** các trục có tác động lớn nhất với bài này. Dự kiến là B, C, D, G, I, nhưng hãy tự quyết dựa trên phần 1.
4. **Lọc tuân thủ** (mục 6) và **chấm đề xuất** (mục 7).
5. **Viết báo cáo, tự rà:**
   - mọi số liệu có nguồn;
   - mọi đề xuất có thí nghiệm kiểm chứng;
   - không có nội dung dữ liệu thi;
   - không vi phạm luật mục 1.
6. **Ghi dần:** báo cáo dài, nên ghi file theo từng phần trong lúc làm, để không mất kết quả nếu phiên bị ngắt.

---

## 11. Không làm

- Không sửa code, script, tài liệu hiện có; không tạo PR; không chạy git làm thay đổi trạng thái (mục 1).
- Không chạy train, eval, ASR, suy luận; không dùng GPU.
- Không đề xuất pseudo-label test, đọc `*_environment/`, reset hay clone `ToolEnv`, hay gọi API lúc suy luận.
- Không leo public leaderboard bằng cách chỉnh theo điểm public.
- Không đưa ra khuyến nghị chỉ dựa trên trí nhớ mà không ghi "chưa kiểm chứng".
- Không viết báo cáo kiểu liệt kê dàn trải: mọi thứ phải quy về **điểm private và lịch 16/11**.

---

## 12. Checklist trước khi kết thúc

- [ ] Đã đọc đủ file ở mục 3, và phần 1 của báo cáo trích đúng số liệu kèm đường dẫn.
- [ ] Có ≥ 40 nguồn gốc và ≥ 12 repo hay thư viện trong CSV; mọi `[S#]` trong báo cáo đều có dòng tương ứng.
- [ ] Mọi model đề xuất đều có ngày phát hành, licence, số tham số, và tổng tham số của cấu hình.
- [ ] Mỗi đề xuất P0/P1 có: thí nghiệm kiểm chứng, tiêu chí giữ/bỏ, chi phí, chỗ cắm vào code.
- [ ] Đã trả lời đủ 7 điểm phản biện ở mục 8.
- [ ] Không có nội dung dữ liệu thi nào bị chép hay gửi ra ngoài; chỉ ghi file trong `docs/research/`; `git status` chỉ còn thêm file trong `docs/research/`.
- [ ] Trả lời trong chat: tóm tắt 10–15 dòng và đường dẫn 2 file.
