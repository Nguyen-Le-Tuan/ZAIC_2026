# Train và chấm trên cloud (31/10/2026)

*Anh cho phép thuê cloud (30/10, 23:58), và nhờ Claude chuẩn bị gói code cùng dữ liệu để Anh tự đẩy lên cloud train cho nhanh. Bộ công cụ ở [PR #6](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/6), nhánh `cloud-train`, chưa merge. Gói đã tạo sẵn trên máy Anh.*

*Cập nhật 31/10, sáng sớm: baseline đầu-cuối cho thấy agent đọc chữ ASR mất khoảng 20 điểm ([`E2E_BASELINE_2026-10-31.md`](E2E_BASELINE_2026-10-31.md)). Bộ công cụ có thêm lượt train agent trên chữ ASR, và mọi lượt train chấm cả trên chữ ASR. **Dùng gói mới** (zac_cloud_bundle_20261031_asr.tar.gz); gói `zac_cloud_bundle_20261031.tar.gz` cũ không còn dùng.*

## Tóm tắt

- **Gói đã sẵn:** `~/zac_cloud_bundle_20261031_asr.tar.gz` (256 MB, sha256 bắt đầu bằng `3a3fb94822a9`, chỉ chủ máy đọc được). Tạo lúc 05:05 ngày 31/10.
  - Code ở commit `f34defa` của `cloud-train`. Tài liệu trong gói là bản cũ hơn; đọc bản trên `main`.
  - Dữ liệu train và public_test, **không có audio**.
  - `gen/`, hai adapter 1.7B, và các lượt gốc để so sánh: hai lượt chữ chuẩn, bốn lượt chữ ASR.
  - `asr/train_*`: transcript turbo và PhoWhisper của toàn bộ 5.036 wav train (chỉ train; public không có).
  - **Gói có dữ liệu thi có licence:** chỉ tải lên máy thuê của đội, không đưa lên git hay drive chia sẻ, và xoá khi trả máy.
- **Cách làm:** cloud chạy **đúng đường train và chấm của máy local**: `train_local.sh` và `eval_ckpt.sh`, backend HF, greedy, cùng file SFT, cùng phiên bản thư viện. Nhờ vậy số trên cloud so được với 53,92 và 35,53.
  - **Đã kiểm trên máy local:** 4 file SFT dựng lại từ gói giống hệt từng byte bản local.
- **Lượt mặc định** (`lifemate/cloud/arms_2026-10-31.txt`):
  - Chấm lại 2 adapter 1.7B để kiểm parity.
  - Qwen3-4B-Instruct-2507 train với đúng công thức của 1.7B, trên fit_random → dev_random và fit_lao → dev_lao. Chấm trên cả chữ chuẩn lẫn chữ turbo.
  - Câu cần trả lời: model 4B hơn 1.7B bao nhiêu khi mọi thứ khác giữ nguyên, trên chữ chuẩn và trên chữ ASR.
- **Lượt tuỳ chọn, chờ Anh bật** (mục "Lượt train trên chữ ASR" bên dưới): agent học trên chữ ASR, công thức B-up trên fit_random.

## Thuê máy gì

| Mục | Đề xuất | Lý do |
|---|---|---|
| GPU | 1 máy, **2–4 GPU từ 40 GB trở lên** (A100 80GB, H100 80GB, L40S 48GB) | Mỗi lượt dùng 1 GPU. 4 GPU thì 4 lượt mặc định chạy cùng lúc; 2 GPU thì chạy thành 2 đợt. |
| Ổ đĩa | ≥ 100 GB; ≥ 150 GB nếu leader dùng chung để fine-tune ASR | Model gốc khoảng 12 GB, venv khoảng 10 GB, checkpoint, log; gói có audio thêm 1,1 GB, cộng checkpoint ASR. |
| Hệ điều hành | Linux, driver NVIDIA ≥ 550 | Script tự chọn bản CUDA của torch hợp với driver. |
| A30 | Chưa cần | A30 dùng để đo thời gian và Docker sau này (việc của leader, P0-5 trong báo cáo Codex). |

- Một GPU 24 GB có thể đủ cho 4B LoRA, nhưng chưa đo. Smoke test ghi lại đỉnh bộ nhớ.
- Chỉ có 1 GPU vẫn chạy được, các lượt chạy lần lượt.

## Thời gian (ước tính thô, chưa đo trên cloud)

- **Một epoch** xử lý khoảng 12,7 triệu token. Số này đo trên máy local: khoảng 1,4 nghìn token/giây trong khoảng 2,5 giờ.
  - Smoke test ghi tốc độ thật vào `runs/cloud_setup.json`, kèm số giờ ước tính cho một epoch.
  - Ví dụ: 5 nghìn token/giây thì khoảng 0,7 giờ; 10 nghìn token/giây thì khoảng 0,35 giờ.
- **Chấm một lượt** (233–262 mẫu, mỗi mẫu một lần sinh): trên máy local, 1.7B mất khoảng 10–11 phút. 4B sẽ chậm hơn 1.7B, nhưng GPU lớn nhanh hơn 4070.
- `train.py` chạy batch 1 cộng gradient accumulation 16, nên không tận dụng hết GPU lớn. Như vậy vẫn đủ dùng.
  - Muốn tăng tốc thêm (batch lớn hơn, chấm bằng vLLM) thì cần PR riêng và kiểm parity lại, vì sẽ đổi cách chạy.

## Các bước

**1. Trên máy Anh.** Gói đã tạo sẵn. Chỉ cần tạo lại khi đổi code, hoặc khi cần audio cho leader:

```bash
git -C ~/"Zalo AI Challenge" fetch origin
git -C ~/"Zalo AI Challenge" worktree add --detach ~/zac-cloud origin/cloud-train   # lần đầu
SRC=~/"Zalo AI Challenge" bash ~/zac-cloud/lifemate/scripts/make_cloud_bundle.sh
SRC=~/"Zalo AI Challenge" WITH_AUDIO=1 bash ~/zac-cloud/lifemate/scripts/make_cloud_bundle.sh   # thêm 1,1 GB audio
```

Gói luôn lấy code ở commit hiện tại của `~/zac-cloud`. Muốn có transcript ASR trong gói thì `lifemate/asr/train_*` phải có sẵn trên máy (đã có). Muốn lấy code mới hơn thì chạy `git -C ~/zac-cloud checkout --detach origin/cloud-train` trước.

**2. Tải lên máy cloud:**

```bash
scp ~/zac_cloud_bundle_20261031_asr.tar.gz <user>@<host>:~/
```

**3. Cài đặt trên cloud** (khoảng 15–30 phút, chủ yếu là tải torch và model):

```bash
tar -xzf zac_cloud_bundle_20261031_asr.tar.gz && cd ZAIC_2026
bash lifemate/scripts/cloud_setup.sh 2>&1 | tee setup.log
```

Cần thấy ba điều:
- `0 differ`: gói còn nguyên.
- `same as local` 4 lần: file SFT giống hệt bản local.
- `runs/cloud_setup.json` có tốc độ (tok/s) của cả 1.7B và 4B.

Nếu báo không dùng được GPU, đặt `TORCH_INDEX_URL=https://download.pytorch.org/whl/cu128` (hoặc bản CUDA hợp với driver) rồi chạy lại.

**4. Chạy các lượt** (trong `tmux`, để mất kết nối SSH không làm dừng job):

```bash
tmux new -s arms
DRY_RUN=1 bash lifemate/scripts/cloud_arms.sh lifemate/cloud/arms_2026-10-31.txt   # xem lượt nào chạy trên GPU nào
bash lifemate/scripts/cloud_arms.sh lifemate/cloud/arms_2026-10-31.txt 2>&1 | tee arms.log
```

Cuối log có điểm của từng lượt, và file `~/cloud_results_<máy>_<giờ>.tar.gz` gồm `runs/` cùng các adapter mới.

**5. Mang kết quả về:**

```bash
mkdir -p ~/"Zalo AI Challenge"/cloud_results && scp <user>@<host>:~/cloud_results_*.tar.gz ~/"Zalo AI Challenge"/cloud_results/
```

Rồi báo Claude. Claude giải nén vào `lifemate/runs/` và `lifemate/ckpt/` (tên lượt mới, không trùng lượt cũ), kiểm parity rồi viết báo cáo.

**6. Tắt máy cloud** khi đã mang kết quả về.

## Lượt mặc định và cách đọc kết quả

| Lượt | Làm gì | Đọc thế nào |
|---|---|---|
| `q17b_fit_random_cloud`, `q17b_fit_lao_cloud` | Chấm lại 2 adapter 1.7B trên cloud | Nếu giống hệt từng mẫu với bản local (53,92 / 35,53), thì số cloud và local so trực tiếp được. Nếu không, chỉ so các lượt cloud với nhau, dùng 2 lượt này làm gốc. |
| `q4b_fit_random` | 4B, fit_random → dev_random | Chữ chuẩn: so với 1.7B (53,92), `runs/compare_q4b_fit_random_vs_ref.json`. Chữ turbo: so với 1.7B trên cùng chữ (31,69), `runs/compare_q4b_fit_random_asr_vs_ref.json` |
| `q4b_fit_lao` | 4B, fit_lao → dev_lao (app chưa thấy) | Chữ chuẩn: so với B0 (35,53). Chữ turbo: so với 17,14. Tên file tương tự |

## Lượt train trên chữ ASR (tuỳ chọn, chờ Anh bật)

Cùng công thức với `q17b_fit_random`. Chỉ khác chữ của các lượt user trong dữ liệu SFT: lấy từ ASR có sẵn chạy trên wav train (`asr/train_all_<asr>.jsonl`), thay cho `audio_text`. ASR có sẵn chưa từng train trên các wav này, nên transcript không bị "thuộc lòng".

| Lượt | Làm gì | So với |
|---|---|---|
| `q17b_random_asrtrain` | 1.7B học trên chữ turbo | Chữ turbo: 31,69 (`runs/compare_<TAG>_asr_vs_ref.json`); chữ chuẩn: 53,92 |
| `q17b_random_asrtrain_pho` | 1.7B học trên chữ PhoWhisper | Chữ PhoWhisper: 27,90. Cho biết PhoWhisper có thắng không khi agent đã quen kiểu chữ của nó |
| `q4b_random_asrtrain` | 4B học trên chữ turbo | Chạy sau `q4b_fit_random` trên cùng GPU; so với 4B học trên chữ chuẩn, đọc chữ turbo |

- Mỗi lượt cho hai điểm: trên chữ chuẩn (`runs/sft_<TAG>`) và trên chữ ASR (`runs/sft_<TAG>_asr`). Cuối log `cloud_arms` in cả hai.
- Script dừng ngay nếu file ASR thiếu wav nào của tập fit, vì `sft.py` sẽ lặng lẽ dùng `audio_text` cho wav thiếu.
- Khi leader đã fine-tune ASR trên wav train, transcript dùng để train agent phải là k-fold (mỗi phần do model chưa train trên phần đó tạo ra). Bộ công cụ hiện chưa làm k-fold.

**Sau giai đoạn 2 của D** (xong 03:09, [`D_PHASE2_2026-10-31.md`](D_PHASE2_2026-10-31.md)): D bị loại. Lượt đối chứng B-up (chỉ nhân bản mẫu hỏi lại thật) tăng hỏi lại từ 7,5 lên 30,0 trên dev_lao, tổng 35,53 → 36,94 (chưa chắc).
- **Nên bật trước: `q17b_random_up`** (1.7B, fit_random + `gen/up_real_asks_random.jsonl`, 260 bước như `q17b_fit_random`). Đây là phép thử theo kế hoạch đặt trước: dev_random không giảm quá 1 điểm so với 53,92 thì dùng công thức B-up làm mặc định.
  - Dữ liệu (263 dòng, từ 127 mẫu hỏi lại thật) do `scripts/make_upsample.py` tạo, đã có trong gói. Script này tái tạo đúng file B-up trên fit_lao.
- **4B cùng dữ liệu B-up** (`q4b_lao_up`, `q4b_random_up`): bật cùng lúc nếu đủ GPU, hoặc sau khi `q17b_random_up` đạt.
- Các dòng này đang được ghi chú tắt sẵn trong file danh sách lượt. Bỏ dấu `#` trước dòng đó sau khi Anh quyết. Lượt D (`q4b_lao_d3`) không cần bật nữa.

## Quy tắc

- **Chỉ train trên train;** không dùng public_test để train hay chỉnh. Cloud cũng không chạy ASR trên public_test.
- **Model:** Qwen3-4B-Instruct-2507, revision `cdbee75f`, Apache-2.0, repo tạo ngày 05/08/2025, tức trước mốc 26/10/2026. Đếm tham số:
  - LLM 4,02B, dưới trần 5B.
  - Cộng Whisper-turbo (0,81B) được khoảng 4,83B, dưới trần 6B.
  - Cộng PhoWhisper-large (1,55B) được khoảng 5,57B, vẫn dưới 6B.
- **Không sửa code trên cloud.** Cần sửa thì sửa qua PR, rồi tạo gói mới.
- **Kết quả mang về** để trong `lifemate/runs/` và `lifemate/ckpt/`. Hai thư mục này bị git bỏ qua; không commit.

## Chưa kiểm

- **Cài torch 2.15.0 và tải model trên máy thuê thật.**
  - Script thử bản PyPI trước, rồi tới các bản CUDA 13.0, 12.8, 12.6.
  - Máy local dùng bản CUDA 13.2 (driver 595).
- **Smoke test của 4B:** máy local 8 GB không nạp nổi 4B bf16.
- **Parity giữa hai máy:** GPU và CUDA khác nhau có thể làm vài output greedy khác đi. Hai lượt chấm lại 1.7B sẽ cho biết.
- ~~Chạy thật một lượt qua `cloud_arms.sh`~~: đã chạy thật trên laptop (31/10, 05:05–05:15), từ gói mới giải nén vào thư mục tạm: một lượt chấm 1.7B trên chữ turbo (`ASR_FILE`). Kết quả 31,69, giống hệt lượt đầu-cuối cả 233/233 dự đoán (chênh 0,00); bước so theo cặp và đóng gói kết quả (448 KB) chạy đúng. Chưa chạy thật lượt train nào qua `cloud_arms.sh`.
- **Lượt train trên chữ ASR:** mới kiểm phần dựng dữ liệu SFT trên máy local (dữ liệu SFT của fit_random dựng từ chữ turbo: đúng 4.150 dòng, cùng phần đáp án và cùng cách tăng cường như bản chữ chuẩn; chỉ chữ của người nói khác); chưa train thật lượt nào.
