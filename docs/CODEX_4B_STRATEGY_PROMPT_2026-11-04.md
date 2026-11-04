# Prompt cho Codex: phân tích sâu để đưa hệ thống 4B lên điểm cao nhất

> **Cách dùng:** mở Codex trong thư mục `~/Zalo AI Challenge`, rồi gõ:
> *"Đọc và làm đúng theo `docs/CODEX_4B_STRATEGY_PROMPT_2026-11-04.md`."*
>
> Claude viết lúc 14:00 ngày 04/11/2026, theo yêu cầu của Anh. Từ đây trở xuống là chỉ dẫn cho Codex.

---

## 0. Vai trò, mục tiêu, sản phẩm

**Vai trò:** nhà phân tích dữ liệu và chiến lược, độc lập và phản biện. Bạn làm việc cùng Claude:
- **Bạn:** phân tích kết quả đã có trên CPU, rồi đề xuất thí nghiệm.
- **Claude:** chạy các job GPU và API, giữ nhật ký chung (`JOURNAL.md`, `HUMAN_TODO.md`).

Trước đây bạn đã làm một báo cáo nghiên cứu: `docs/research/CODEX_DEEP_RESEARCH_2026-10-31.md`. Lần này trọng tâm là **số liệu của chính đội**, không phải đọc tài liệu bên ngoài.

**Mục tiêu:** trả lời, bằng số đo kiểm chứng được, câu hỏi sau:

> *Với hệ thống được phép (LLM dưới 5B, cả hệ thống dưới 6B, offline, 30 giây mỗi mẫu trên A30) và 12 ngày còn lại tới hạn Docker (16/11), làm gì để điểm private test cao nhất? Đội đặt mục tiêu **trên 80 điểm public bằng SLM**, vì Anh cho rằng mức đó có khả năng đậu.*

Lý do làm lúc này:
- Cùng pipeline (cùng chữ ASR, prompt, vòng lặp agent, chốt chặn), chỉ thay model 4B bằng model API được **75,52** trên public, trong khi 4B được **46,29**.
- Chênh lệch gần 30 điểm này cho thấy phần lớn điểm đang mất nằm ở **model và cách dạy model**, không phải ở ASR hay khung vòng lặp.
- Câu hỏi là phần nào trong chênh lệch đó mà 4B có thể học lại được, và học bằng cách nào.

**Sản phẩm:**
1. **Báo cáo:** `docs/research/CODEX_4B_STRATEGY_2026-11-04.md`, viết bằng tiếng Việt (giữ thuật ngữ kỹ thuật tiếng Anh), theo cấu trúc ở mục 8.
2. **Script phân tích (nếu có):** nằm trong worktree riêng của bạn (mục 1, luật 2).

Khi xong, trả lời trong chat bằng 10–15 dòng tóm tắt kèm đường dẫn báo cáo.

---

## 1. Luật an toàn (bắt buộc)

Máy này là laptop của Anh: RTX 4070 8GB, RAM 14GB, một GPU dùng chung.

**1. Không đổi trạng thái git ở các thư mục sẵn có.** Áp dụng cho `~/Zalo AI Challenge` (Claude commit tài liệu ở đây), `~/zac-c3` (cây chạy job, đứng ở commit tách rời `9de4e1a`), `~/zac-docker` và `~/zac-synth`.
- Cấm: `checkout`, `switch`, `stash`, `reset`, `pull`, `merge`, `commit`, `add`, `push`.
- Được dùng lệnh chỉ đọc: `log`, `show`, `diff`, `branch -a`, `ls-files`.
- Ngày 30/10 từng có sự cố đổi nhánh làm mất dữ liệu đang được job dùng.

**2. Muốn viết script thì tạo worktree riêng:**
```bash
git -C ~/zac-c3 fetch -q origin
git -C ~/zac-c3 worktree add ~/zac-codex -b codex-analysis origin/api-agent
ln -s ~/zac-c3/lifemate/.venv ~/zac-codex/lifemate/.venv
mkdir -p ~/zac-codex/data && ln -s ~/zac-c3/data/train+public_test ~/zac-codex/data/train+public_test
```
- Chỉ commit trong `~/zac-codex`.
- Được push nhánh `codex-analysis` và mở **PR nháp** nhắm vào `api-agent`. Không merge PR nào.
- Mọi commit kết thúc bằng một dòng ghi rõ do Codex viết.

**3. Không dùng GPU, không gọi API.**
- Không chạy `lifemate.train`, `lifemate.infer` (trừ `--backend oracle`), `lifemate.asr`, `predict.sh`, `eval_ckpt.sh`, `train_local.sh`, và không gọi Meta API.
- Thí nghiệm cần GPU hay API: viết vào báo cáo theo mẫu ở mục 8. Claude sẽ chạy.
- Lý do: chỉ có một GPU, và tiền API là của Anh. Đã chi 43,03 trên trần 50 USD, còn khoảng 7 USD.

**4. Giới hạn tài nguyên CPU.** Phân tích CPU giữ dưới 2 GB RAM và dưới khoảng 10 phút mỗi lệnh, kèm `CUDA_VISIBLE_DEVICES=""`. Trước khi chạy lệnh nặng, xem `systemctl --user list-units 'lifemate-*'`: nếu đang có job thì để nó chạy yên.

**5. Không cài gói, không tải model hay dataset.**

**6. Dữ liệu thi** (licence cấm phát tán, và repo GitHub đang public):
- **Không bao giờ đọc** `data/train+public_test/*/*_environment/`. Luật thi cấm đọc thư mục này.
- Không dán câu nói, nhãn hay kết quả tool vào web hay dịch vụ ngoài.
- Báo cáo chỉ dùng id mẫu (`train_0201`) và ví dụ tự diễn đạt lại, không chép nguyên văn.
- Không commit `data/`, `runs/`, `sft/`, `ckpt/`, `gen/`, `asr/`.

**7. Public test không có nhãn, và cấm gán nhãn public hay private test.**
- Được so **tổng hợp** hai file nộp public (4B và API), ví dụ theo app, tool hay loại dừng, để biết nên nhìn vào đâu.
- **Không** dùng một dự đoán public nào làm dữ liệu train, ví dụ trong prompt hay luật.
- Mọi luật đề xuất phải rút ra từ train và đo trên dev.

**8. Không bịa số.** Số nào cũng phải chạy lại được, ghi rõ `n` và file nguồn. Số trong brief này cũng phải kiểm lại; nếu bạn ra số khác thì ghi cả hai.

---

## 2. Đề bài, luật chấm, ràng buộc (bản đủ: `JOURNAL.md` mục 1)

**Đầu vào và đầu ra:**
- Đầu vào: audio tiếng Việt của lượt cuối, kèm `context` (giờ, vị trí, profile, `installed_apps` với tool được phép) và `history`. Lượt user trong history chỉ có audio.
- Đầu ra mỗi mẫu: `{"id", "tool_calls", "state_hash"}`.
- Mỗi mẫu đúng **một** `zaic_tools.ToolEnv`, và mọi call đã gọi đều tính vào bài nộp.

**Luật chấm:**
- Gold rỗng: được 1 nếu nộp rỗng, ngược lại 0.
- Hash sai, hoặc không call nào khớp: 0.
- Còn lại: F1 giữa call nộp và call đáp án.
- Một call khớp khi:
  - cùng tên tool;
  - mọi tham số không fuzzy **giống hệt**;
  - tham số fuzzy có token-F1 > 0,6.
- Call thừa đều bị tính, kể cả call đọc thừa và call sai schema.

**Ràng buộc:**
- LLM **dưới 5B**; cả hệ thống dưới 6B. Cột "SLM < 6B" trên bảng xếp hạng là giới hạn cả hệ thống.
- 30 giây mỗi mẫu trên A30 24GB; Docker đặt hạn 25 giây.
- Offline, greedy, seed cố định.
- Model và dữ liệu phải công khai và phát hành **trước 26/10/2026**.

**Được và không được dùng dữ liệu nào:**
- Được dùng LLM ngoài để sinh dữ liệu tổng hợp trong lúc phát triển, kể cả từ catalog và `zaic_tools` của public_test (BTC đã xác nhận, `JOURNAL.md` mục 1.5).
- Cấm gán nhãn audio hay yêu cầu của tập test.

**Lịch:**
- Docker: hạn **16/11 23:59**, nộp tối đa 2 lần.
- Private test: 20–23/11.
- Public: tối đa 5 lần nộp mỗi ngày.

---

## 3. Hệ thống hiện tại và nơi để file

**Hệ thống (nhánh `q4b-laptop`, bản sẽ đóng Docker):**
- **ASR:** Whisper-large-v3-turbo fine-tune, đã merge: `~/zac-c3/lifemate/ckpt/asr_turboft/merged`.
- **LLM:** Qwen3-4B-Instruct-2507 nạp NF4 4-bit, cộng LoRA.
  - `ckpt/q4b4_all/final`: train trên đủ 1.545 mẫu, public 46,29. Đây là adapter Docker sẽ dùng.
  - `ckpt/q4b4_fit_random/final`: public 45,39, dev_random.
  - `ckpt/q4b4_fit_lao/final`: train không có 6 app giữ riêng, dùng để đo trên dev_lao.
- **Công thức train:** NF4, LoRA r32/α64, lr 2e-4, 1 epoch, tích luỹ gradient 16, adamw8bit, `--max-len 6144`. Dữ liệu từ `lifemate.sft` với `--rename 2 --p-remove 0.3 --p-distract 0.5 --p-lower 0.3 --history off`.
- **Prompt:** `lifemate/prompt.py`, schema rút gọn mỗi tool một dòng.
- **Vòng lặp agent:** `lifemate/agent.py`, tối đa 8 bước, có chốt chặn ID và kiểm schema trước khi gọi `env`.

**Code mới nhất:** `~/zac-docker`, nhánh `api-agent` = `q4b-laptop` + [PR #13](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/13). PR #13 thêm:
- backend API (`lifemate/api_backend.py`);
- `lifemate/rare_params.py` và `infer --drop-params`;
- `scripts/loss_breakdown.py`.

**Dữ liệu và kết quả:**

| Cái gì | Ở đâu |
|---|---|
| Dữ liệu (train, public_test, catalog) | `~/zac-c3/data/train+public_test/` (cấm `*_environment/`) |
| Tập dev | `splits/dev_random.txt` (233 mẫu, app đã thấy); `splits/dev_lao.txt` (262 mẫu, mọi mẫu dùng 6 app giữ riêng: library, robot_vacuum, loyalty, medication, video_meeting, home_security; mô phỏng 11 app mới của public). Gộp 495 dòng |
| Chữ ASR | `~/zac-c3/lifemate/asr/train_dev_{random,lao}_{turbo,turboft,pho,phoft}.jsonl`; public: `~/zac-c3/lifemate/runs/e2e_public_turboft_asr.jsonl` |
| Run dev của 4B và 1.7B | `~/zac-c3/lifemate/runs/sft_<tag>{.jsonl,_rows.jsonl,_trace.jsonl,_score.json}`. Tag chính: `q4b4_fit_random`, `q4b4_fit_random_asrturboft`, `q4b4_fit_lao`, `q4b4_fit_lao_asrturboft`. Không có hậu tố `_asr…` là chữ chuẩn `audio_text` |
| Thử API trên 80 mẫu dev | `~/zac-docker/lifemate/runs/api_spark_{min,low,min_drop,high_drop,xhigh_drop}_pilot_{dev_random,dev_lao}{.jsonl,_rows.jsonl,_trace.jsonl,_score.json}`; id: `runs/pilot40_dev_{random,lao}.txt` |
| File nộp public | 4B: `~/zac-c3/lifemate/runs/e2e_public_q4b_all.jsonl` (46,29) kèm `_trace.jsonl`. API: `~/zac-docker/lifemate/runs/e2e_public_api_spark_min.jsonl` (69,47) và `e2e_public_api_spark_xhigh_drop.jsonl` (75,52) kèm `_trace.jsonl` |
| Dữ liệu SFT | `~/zac-c3/lifemate/sft/*.jsonl` (có `.manifest.json`) |
| Dữ liệu sinh pilot (không đạt) | `~/zac-synth/lifemate/gen/` |

**File ghi từng mẫu:**
- `_rows.jsonl`: `score`, `call_f1`, `hash_ok`, `category`.
- `_trace.jsonl`: chữ đầu vào, output của model mỗi bước, kết quả tool, lý do dừng.

**Công cụ:**
- `python -m lifemate.scorer <pred> --split train --ids <ids> --rows <out>`
- `python -m lifemate.compare <run_a> <run_b> --ids <ids> --slices --json <out>`: chênh lệch theo cặp kèm khoảng tin cậy.
- `scripts/loss_breakdown.py <pred>@<ids> ...`

**Tài liệu nên đọc:**
- `JOURNAL.md` entry 52–79, nhất là 57–58 (chọn 4B), 61 (pilot dữ liệu sinh), 67–70 (chữ trộn), 77–79 (API).
- `docs/PARAM_ERRORS_2026-10-30.md`
- `docs/E2E_BASELINE_2026-10-31.md`
- `docs/ASR_FINETUNE_2026-10-31.md`
- `docs/EXPERIMENT_D.md`

---

## 4. Số liệu đã có (kiểm lại trước khi dùng)

**Điểm public:**

| Lần nộp | Hệ thống | Điểm |
|---|---|---|
| 31/10 | 1.7B, ASR chưa fine-tune | 25,93 |
| 01/11 | 1.7B, ASR fine-tune | 35,24 |
| 02/11 | 4B (fit_random) | 45,39 |
| 04/11 | 4B (đủ train) | **46,29** |
| 04/11 | API `muse-spark-1.3` `minimal`, cột APIs/Others | 69,47 |
| 04/11 | API `xhigh` + bỏ tham số hiếm, cột APIs/Others | **75,52** |
| Top cột SLM lúc Anh chụp | đội khác | 96,66; 96,58; 96,25; 95,74 |

**4B trên toàn bộ dev:**

| | Chữ chuẩn | Chữ ASR fine-tune |
|---|---|---|
| dev_random (n = 233) | 65,61 (trạng thái đúng 73,0%) | 54,01 (63,5%) |
| dev_lao (n = 262) | 53,40 (66,8%) | 39,20 (51,5%) |
| Gộp 495 | 59,15 | 46,17 |

Dev gộp dự đoán public của 4B sai lệch khoảng 1 điểm (46,17 so với 45,39 và 46,29).

**Thử API trên 80 mẫu dev** (40 mẫu mỗi tập, chữ ASR fine-tune):

| | dev_random | dev_lao | Gộp |
|---|---|---|---|
| 4B (cùng 80 mẫu) | 51,04 | 27,16 | 39,10 |
| API `minimal` | 46,79 | 53,80 | 50,29 |
| API `minimal` + bỏ tham số hiếm | 57,67 | 58,23 | 57,95 |
| API `high` + bỏ tham số hiếm | 62,85 | 62,13 | 62,49 |
| API `xhigh` + bỏ tham số hiếm | 62,44 | 67,06 | 64,75 |

**Điều đã biết:**
- **Bỏ tham số hiếm:** bỏ các tham số tuỳ chọn mà nhãn train gần như không điền, ví dụ `alarm.create.repeat` 0/193 và `smart_home.light_set.color` 0/126. Luật này giúp model API khoảng +7 điểm, nhưng không đổi gì cho 4B, vì 4B đã học quy ước này.
- **Mất điểm của 4B rải rác:** trạng thái cuối sai ở 27% mẫu ngay cả với chữ chuẩn trên app đã thấy. ASR làm mất 11,6–14,2 điểm; app chưa thấy làm mất 12–15 điểm.
- **Lỗi tham số hay gặp:** `content` và `body` (fuzzy), `time`, `query`, `from_account_id`, `program`. Ngoài ra là thiếu hoặc thừa call đọc.
- **Public có app chưa thấy:** 410/634 mẫu cài ít nhất một trong 11 app không có trong train.
- **Bản API trên public:** dev 80 mẫu 50,29 nhưng public 69,47, tức public cao hơn dev nhiều. Với 4B, public và dev gần bằng nhau. Chưa giải thích được vì sao.

**Đã thử nhưng không đạt:**
- **Dữ liệu sinh** bằng `muse-wonder-1.0` cho 6 app của dev_lao (280 mẫu): dev_lao chữ ASR 39,20 → 37,12; chữ chuẩn 53,40 → 50,57 (entry 61).
- **Train trên chữ trộn** (nửa chữ chuẩn, nửa chữ ASR): gộp chữ ASR −0,69, chữ chuẩn −1,62; câu hỏi lại giảm (entry 67–70).
- **Thí nghiệm D** (dữ liệu hỏi lại): xem `docs/EXPERIMENT_D.md` và `docs/D_PHASE2_2026-10-31.md`.

**Chưa đo:**
- Tốc độ 4B bf16 trên A30 (laptop 4-bit: trung bình 9,1 giây mỗi mẫu, p95 18,7 giây).
- Bản API trên chữ chuẩn.
- Model dưới 5B nào khác ngoài Qwen3, phát hành trước 26/10/2026.

---

## 5. Câu hỏi cần trả lời (theo thứ tự ưu tiên)

**Q1. Bản API hơn 4B ở đâu, cụ thể?**
- Dữ liệu: 80 mẫu thử, có trace của cả hai. Không tốn gì.
- Tách chênh lệch 39,10 → 64,75 theo:
  - loại mẫu (thực thi, hỏi lại, ngoài phạm vi);
  - app đã thấy hay chưa;
  - kiểu lỗi: chọn sai tool; thiếu bước đọc trước khi ghi; dùng sai ID lấy từ kết quả tool; sai thời gian; nội dung tin nhắn không đủ giống; quyết sai giữa hỏi lại và làm luôn.
- Đọc trace từng cặp mẫu thắng/thua.
- Cũng chỉ ra chỗ 4B hơn API: trên dev_random, 4B 51,04 so với API `minimal` 46,79.
- Kết quả cần có: bảng "điểm thua do mỗi nguyên nhân" mà 4B có thể lấy lại.

**Q2. Vì sao 4B kém hẳn trên app chưa thấy?** Có ba giả thuyết; hãy đề xuất cách phân biệt chúng với chi phí thấp nhất:
- (a) Prompt rút gọn làm mất thông tin. So `prompt.render_tool` với catalog: mô tả, `x-ref`, `x-one-of`, enum, ví dụ.
- (b) SFT làm model học thuộc theo từng app.
- (c) Model không đủ sức suy luận.

**Q3. Học từ "thầy" API (distillation) có làm được không, và làm thế nào?**
- Bản API `xhigh` hơn 4B khoảng 25 điểm trên dev và khoảng 29 điểm trên public.
- Đọc `lifemate/synth.py` (nhánh `synth-data`, [PR #11](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/11)) và entry 61: pilot dữ liệu sinh thất bại vì sao?
- Thiết kế cách dùng model API làm thầy, sinh lời giải (gọi qua `ToolEnv` thật) cho:
  - dữ liệu sinh từ catalog public;
  - hoặc chính các mẫu train, nếu lời giải của thầy khác nhãn mà vẫn đúng.
- Lưu ý: `ToolEnv` cần môi trường của từng mẫu. Hãy xem mẫu sinh lấy môi trường từ đâu.
- Ước số USD cần tiêu. Chỉ còn khoảng 7 USD; cần thêm thì phải hỏi Anh.
- **Không** dùng mẫu public_test làm đầu vào.

**Q4. Suy luận lúc chạy cho 4B.**
- Bản API tăng khoảng 7 điểm khi tăng mức suy nghĩ.
- Có model dưới 5B nào có chế độ suy luận (ví dụ bản Thinking của Qwen3-4B), phát hành trước 26/10/2026, licence cho phép, mà chạy kịp 25 giây trên A30 không?
- Ước số token suy luận mỗi bước dùng được.
- Ghi rõ điều nào đã kiểm qua model card, điều nào chưa kiểm.

**Q5. ASR còn đáng đầu tư không?**
- Dùng run chữ chuẩn và chữ ASR của 4B (theo từng mẫu): ASR làm hỏng những slot nào (tên riêng, số, nội dung tin nhắn, query)?
- Sửa phía ASR (ví dụ PhoWhisper fine-tune, đã có `asr/*_phoft.jsonl`) hay phía agent thì được nhiều hơn?

**Q6. Luật tất định giúp 4B.**
- Những sửa bằng code nào, đo trên dev, có thể tăng điểm cho 4B? Ví dụ: chuẩn hoá thời gian, chống gọi đọc thừa, chuẩn hoá tham số của `ask_missing_info`.
- Mỗi đề xuất phải kèm số đo chạy lại (replay) trên dev. Có thể làm như `--drop-params`: sửa call rồi chạy lại trên `ToolEnv` mới của **train**.

**Q7. Kiểm tra thực tế:** đạt từ 80 điểm public bằng SLM trước 16/11 có khả thi không? Cần kết hợp những gì, mỗi phần dự kiến tăng bao nhiêu (kèm độ bất định), và rủi ro lớn nhất là gì?

---

## 6. Ngân sách thời gian để xếp hạng đề xuất

- **Laptop:**
  - Một lượt train 4B trên khoảng 1.300 mẫu mất 5,5–6 giờ.
  - Chạy dev mất khoảng 1,2 giờ mỗi tập (262 mẫu).
  - File public mất khoảng 1,5 giờ.
  - Tức khoảng một thí nghiệm mỗi đêm, tổng cộng khoảng 6–8 lượt GPU trước 16/11, và phải chừa 2–3 ngày cho Docker.
- **Máy anh trai Anh** (2–4 A100) đã bắt đầu train, chưa rõ nội dung. Nếu đề xuất cần GPU lớn, ghi thành câu hỏi cho Anh.
- **API:** còn khoảng 7 USD trên trần 50 USD. Vượt trần phải được Anh đồng ý.

---

## 7. Cách phối hợp với Claude

- **Đề xuất thí nghiệm** theo đúng mẫu ở mục 8. Mỗi đề xuất phải có **luật giữ/bỏ ghi trước khi chạy**, ví dụ: "gộp 495 dòng chữ ASR tăng ít nhất 1,0 và không tập nào giảm quá 2,0".
- Claude đọc báo cáo, chạy các thí nghiệm GPU và API theo thứ tự Anh duyệt, rồi ghi kết quả vào `JOURNAL.md`.
- **Không sửa** `JOURNAL.md`, `HUMAN_TODO.md` hay file nào ngoài báo cáo của bạn. Claude sẽ commit báo cáo lên `main`.
- Câu hỏi cho Claude hoặc Anh: ghi ở cuối báo cáo.

---

## 8. Cấu trúc báo cáo `docs/research/CODEX_4B_STRATEGY_2026-11-04.md`

1. **Tóm tắt** (15 dòng trở xuống): câu trả lời cho Q7 và 3 việc nên làm đầu tiên.
2. **Số liệu đã kiểm lại:** lệnh đã chạy và chỗ lệch so với brief.
3. **Q1 – Q6:** mỗi câu gồm số đo (kèm `n`, file nguồn, khoảng tin cậy nếu có), kết luận, và mức chắc chắn.
4. **Bảng đề xuất**, xếp theo điểm kỳ vọng trên chi phí:

   | # | Đề xuất | Tăng kỳ vọng trên dev gộp (khoảng) | Chi phí (giờ GPU laptop / USD / giờ người) | Rủi ro | Luật giữ/bỏ ghi trước | Ai chạy | Phụ thuộc |
   |---|---|---|---|---|---|---|---|

5. **Thí nghiệm nên chạy đêm nay:** lệnh cụ thể Claude có thể chạy, hoặc thay đổi code cần làm trước.
6. **Câu hỏi cho Claude và Anh.**
7. **Giới hạn:** điều chưa kiểm, giả định.
