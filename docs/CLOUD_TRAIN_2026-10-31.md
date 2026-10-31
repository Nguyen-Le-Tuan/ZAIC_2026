# Train và chấm trên cloud (31/10/2026)

*Anh cho phép thuê cloud (30/10, 23:58), và nhờ Claude chuẩn bị gói code cùng dữ liệu để Anh tự đẩy lên cloud train cho nhanh. Bộ công cụ ở [PR #6](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/6), nhánh `cloud-train`, chưa merge. Gói đã tạo sẵn trên máy Anh.*

*Cập nhật 31/10, sáng sớm: baseline đầu-cuối cho thấy agent đọc chữ ASR mất khoảng 20 điểm ([`E2E_BASELINE_2026-10-31.md`](E2E_BASELINE_2026-10-31.md)). Bộ công cụ có thêm lượt train agent trên chữ ASR, và mọi lượt train chấm cả trên chữ ASR. **Dùng gói mới** (zac_cloud_bundle_20261031_asr.tar.gz); gói `zac_cloud_bundle_20261031.tar.gz` cũ không còn dùng.*

*Cập nhật 31/10, 10:00: Anh chọn bộ lượt theo khuyến nghị. Các lượt đó đã bật sẵn trong **gói v3** (`zac_cloud_bundle_20261031_v3.tar.gz`); không cần sửa file danh sách lượt trên cloud. Hai gói trước (`…_20261031.tar.gz`, `…_20261031_asr.tar.gz`) không dùng nữa.*

## Tóm tắt

- **Gói đã sẵn:** `~/zac_cloud_bundle_20261031_v3.tar.gz` (256 MB, sha256 bắt đầu bằng `bfe980b32f46`, chỉ chủ máy đọc được). Tạo lúc 10:06 ngày 31/10.
  - Code ở commit `8c70d4f` của `cloud-train`. Tài liệu trong gói là bản cũ hơn; đọc bản trên `main`.
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
- **Lượt Anh đã chọn, bật sẵn** (mục "Lượt Anh đã bật" bên dưới):
  - `q17b_random_asrtrain`: 1.7B học trên chữ turbo.
  - `q17b_random_up`: công thức B-up trên fit_random.
  - `q4b_random_asrtrain`: 4B học trên chữ turbo. Chỉ chạy khi các lượt có ít nhất 4 GPU (`MIN_GPUS=4`); máy ít GPU hơn thì script tự bỏ qua và ghi vào log.

## Thuê máy gì

| Mục | Đề xuất | Lý do |
|---|---|---|
| GPU | 1 máy, **2–4 GPU từ 40 GB trở lên** (A100 80GB, H100 80GB, L40S 48GB) | Mỗi lượt dùng 1 GPU. 4 GPU thì 4 lượt mặc định chạy cùng lúc; 2 GPU thì chạy thành 2 đợt. |
| Loại GPU | **Có bf16 phần cứng: thế hệ Ampere trở lên** (A100, A10, A30, L4, L40S, H100, RTX 30/40) | T4, V100, P100 không có bf16. Đo trên Kaggle T4 (31/10): train 1.7B chỉ 157 token/giây, tức khoảng 22 giờ mỗi epoch, chậm gần 9 lần laptop; chấm 17,5 giây mỗi mẫu. |
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
scp ~/zac_cloud_bundle_20261031_v3.tar.gz <user>@<host>:~/
```

Nếu đã giải nén và cài gói `_asr` trên máy cloud, **và chưa chạy `cloud_arms.sh`**: giải nén gói v3 đè lên đúng chỗ cũ (`tar -xzf zac_cloud_bundle_20261031_v3.tar.gz` trong `~`). Chỉ hai file code đổi; venv, model đã tải và file SFT đã dựng vẫn giữ, nên không cần cài lại. Nếu lượt đã chạy rồi thì để nó chạy hết, báo Claude.

**3. Cài đặt trên cloud** (khoảng 15–30 phút, chủ yếu là tải torch và model):

```bash
tar -xzf zac_cloud_bundle_20261031_v3.tar.gz && cd ZAIC_2026
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

Cuối log có điểm của từng lượt, và file `~/ZAIC_2026/cloud_results_<máy>_<giờ>.tar.gz` (trong thư mục gốc của gói, không phải `~`) gồm `runs/` cùng các adapter mới. Với các lượt đã bật, file này khoảng 1 GB (adapter 1.7B khoảng 144 MB, 4B lớn hơn).

**5. Mang kết quả về:**

```bash
mkdir -p ~/"Zalo AI Challenge"/cloud_results && scp <user>@<host>:~/ZAIC_2026/cloud_results_*.tar.gz ~/"Zalo AI Challenge"/cloud_results/
```

Rồi báo Claude. Claude giải nén vào `lifemate/runs/` và `lifemate/ckpt/` (tên lượt mới, không trùng lượt cũ), kiểm parity rồi viết báo cáo.

**6. Tắt máy cloud** khi đã mang kết quả về.

**Khi nhờ người khác chạy giúp một lần** (ví dụ anh trai của Anh; JOURNAL entry 33, 46). Người chạy đặt gói v3 vào thư mục home rồi chạy đúng một lệnh:

```bash
cd ~ && tar -xzf zac_cloud_bundle_20261031_v3.tar.gz && cd ZAIC_2026 && nohup bash -c 'if nvidia-smi --query-gpu=compute_cap --format=csv,noheader | awk -F. "\$1<8{bad=1} END{exit bad}"; then bash lifemate/scripts/cloud_setup.sh && bash lifemate/scripts/cloud_arms.sh lifemate/cloud/arms_2026-10-31.txt; else echo "DUNG: GPU khong co bf16 (can A100, A10, L4, H100 hoac RTX 30/40), khong train"; nvidia-smi -L; fi; tar -czf ~/zac_logs.tar.gz run.log lifemate/runs/cloud_*; mv cloud_results_*.tar.gz ~/; echo "XONG $(date)"' > run.log 2>&1 &
```

- Lệnh kiểm GPU trước. Nếu có GPU không có bf16 (compute capability dưới 8.0), nó dừng ngay, không train, và vẫn để lại `~/zac_logs.tar.gz`.
- Nếu GPU đạt: cài đặt, chạy các lượt trong nền (thoát SSH vẫn chạy), rồi để lại ở `~` hai file cần gửi về: `cloud_results_*.tar.gz` và `zac_logs.tar.gz`.
- Xem tiến độ: `tail -f ~/ZAIC_2026/run.log`. Xong khi dòng cuối có `XONG`.
- *Thêm lúc 16:05 ngày 31/10, sau khi Kaggle T4 cho thấy GPU không có bf16 chậm gần 9 lần. Đã thử bằng GPU giả (A100, RTX 40: chạy; T4, máy lẫn GPU cũ: dừng).*

## Lượt mặc định và cách đọc kết quả

| Lượt | Làm gì | Đọc thế nào |
|---|---|---|
| `q17b_fit_random_cloud`, `q17b_fit_lao_cloud` | Chấm lại 2 adapter 1.7B trên cloud | Nếu giống hệt từng mẫu với bản local (53,92 / 35,53), thì số cloud và local so trực tiếp được. Nếu không, chỉ so các lượt cloud với nhau, dùng 2 lượt này làm gốc. |
| `q4b_fit_random` | 4B, fit_random → dev_random | Chữ chuẩn: so với 1.7B (53,92), `runs/compare_q4b_fit_random_vs_ref.json`. Chữ turbo: so với 1.7B trên cùng chữ (31,69), `runs/compare_q4b_fit_random_asr_vs_ref.json` |
| `q4b_fit_lao` | 4B, fit_lao → dev_lao (app chưa thấy) | Chữ chuẩn: so với B0 (35,53). Chữ turbo: so với 17,14. Tên file tương tự |

## Lượt Anh đã bật (31/10, 10:00, theo khuyến nghị)

| Số GPU cho các lượt | Lượt chạy | Ước tính thô (chưa đo trên cloud) |
|---|---|---|
| 2 | 6 lượt: 4 lượt mặc định, `q17b_random_asrtrain`, `q17b_random_up`. `q4b_random_asrtrain` tự bỏ qua | Mỗi GPU một lượt 4B và một lượt 1.7B: khoảng 2,5–3,5 giờ |
| 3 | Như 2 GPU | Gần như 2 GPU (GPU chậm nhất vẫn chạy một lượt 4B và một lượt 1.7B) |
| 4 | 7 lượt; `q4b_random_asrtrain` chạy sau `q4b_fit_random` trên GPU 2 | GPU 2 chạy hai lượt 4B: khoảng 3–4 giờ |

- `DRY_RUN=1` in ra lượt nào chạy trên GPU nào; đã kiểm với 1, 2, 3, 4 và 8 GPU.
- Nếu leader giữ riêng 1 GPU để fine-tune ASR, đặt `GPUS=<số GPU còn lại>` khi chạy `cloud_arms.sh`; các lượt dùng GPU 0 tới `GPUS−1`.
- Thứ tự dòng trong file danh sách lượt có chủ ý, đừng đổi: nhờ thứ tự đó, `q4b_random_asrtrain` chạy trên cùng GPU và sau lượt gốc `q4b_fit_random` của nó.

### Agent học trên chữ ASR

Cùng công thức với `q17b_fit_random`. Chỉ khác chữ của các lượt user trong dữ liệu SFT: lấy từ ASR có sẵn chạy trên wav train (`asr/train_all_<asr>.jsonl`), thay cho `audio_text`. ASR có sẵn chưa từng train trên các wav này, nên transcript không bị "thuộc lòng".

| Lượt | Làm gì | So với |
|---|---|---|
| `q17b_random_asrtrain` (**bật**) | 1.7B học trên chữ turbo | Chữ turbo: 31,69 (`runs/compare_<TAG>_asr_vs_ref.json`); chữ chuẩn: 53,92 |
| `q4b_random_asrtrain` (**bật nếu ≥ 4 GPU**) | 4B học trên chữ turbo | Chạy sau `q4b_fit_random` trên cùng GPU; so với 4B học trên chữ chuẩn, đọc chữ turbo |
| `q17b_random_asrtrain_pho` (tắt) | 1.7B học trên chữ PhoWhisper | Chữ PhoWhisper: 27,90. Cho biết PhoWhisper có thắng không khi agent đã quen kiểu chữ của nó |

- Mỗi lượt cho hai điểm: trên chữ chuẩn (`runs/sft_<TAG>`) và trên chữ ASR (`runs/sft_<TAG>_asr`). Cuối log `cloud_arms` in cả hai.
- Script dừng ngay nếu file ASR thiếu wav nào của tập fit, vì `sft.py` sẽ lặng lẽ dùng `audio_text` cho wav thiếu.
- Khi leader đã fine-tune ASR trên wav train, transcript dùng để train agent phải là k-fold (mỗi phần do model chưa train trên phần đó tạo ra). Bộ công cụ hiện chưa làm k-fold.

**Sau giai đoạn 2 của D** (xong 03:09, [`D_PHASE2_2026-10-31.md`](D_PHASE2_2026-10-31.md)): D bị loại. Lượt đối chứng B-up (chỉ nhân bản mẫu hỏi lại thật) tăng hỏi lại từ 7,5 lên 30,0 trên dev_lao, tổng 35,53 → 36,94 (chưa chắc).
- **Đã bật: `q17b_random_up`** (1.7B, fit_random + `gen/up_real_asks_random.jsonl`, 260 bước như `q17b_fit_random`). Đây là phép thử theo kế hoạch đặt trước: dev_random (chữ chuẩn) không giảm quá 1 điểm so với 53,92 thì dùng công thức B-up làm mặc định.
  - Lượt này nay chấm thêm trên chữ turbo, so với 31,69. Số đó chỉ để tham khảo, không thuộc luật quyết.
  - Dữ liệu (263 dòng, từ 127 mẫu hỏi lại thật) do `scripts/make_upsample.py` tạo, đã có trong gói. Script này tái tạo đúng file B-up trên fit_lao.
- **4B cùng dữ liệu B-up** (`q4b_lao_up`, `q4b_random_up`): vẫn tắt; bật sau khi `q17b_random_up` đạt.
- Các dòng còn tắt nằm cuối file danh sách lượt. Muốn bật thì bỏ dấu `#`, nhưng giữ chúng ở cuối để các lượt phía trên không đổi GPU. Sửa qua PR rồi tạo gói mới, không sửa trên cloud. Lượt D (`q4b_lao_d3`) đã bỏ khỏi file.

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
- ~~Chạy thật một lượt qua `cloud_arms.sh`~~: đã chạy thật trên laptop (31/10, 05:05–05:15), từ gói mới giải nén vào thư mục tạm: một lượt chấm 1.7B trên chữ turbo (`ASR_FILE`). Kết quả 31,69, giống hệt lượt đầu-cuối cả 233/233 dự đoán (chênh 0,00); bước so theo cặp và đóng gói kết quả (448 KB) chạy đúng.
- ~~Lượt train qua `cloud_arms.sh`~~: đã chạy thử trên laptop (31/10, 10:07–10:21), từ gói v3 giải nén vào thư mục tạm. Hai lượt 1.7B như `q17b_random_asrtrain` và `q17b_random_up`, nhưng chỉ 2 bước train và chấm 10 mẫu dev_random, nên điểm không có ý nghĩa.
  - Đủ các bước: kiểm file ASR phủ 4.252/4.252 lượt user; dựng SFT (chữ turbo 4.150 dòng; B-up 4.979 dòng, gồm 829 dòng từ mẫu hỏi lại nhân bản); train; chấm trên chữ chuẩn và chữ turbo; so theo cặp với lượt gốc; đóng gói kết quả (189 MB, có 2 adapter).
  - Lượt có `MIN_GPUS=4` được bỏ qua và ghi log.
  - **Chưa chạy một lượt train đầy đủ** và chưa train 4B nào qua `cloud_arms.sh`; lần chạy cloud đầu tiên sẽ là lần đầu.
