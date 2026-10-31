# Fine-tune ASR trên Colab (31/10/2026)

*Anh đồng ý lúc khoảng 14:40 ("Viết script ASR"). Phần ASR là của leader. Claude viết script và ô lệnh để chạy trên Colab T4, vì máy leader (RTX 3050 4 GB) không đủ, còn Kaggle của leader đang bận lượt agent. Colab **không cần xác minh số điện thoại**, nên cả Anh và leader đều dùng được Colab của mình. Code ở [PR #7](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/7) (nhánh `asr-finetune`), chưa merge.*

## Tóm tắt

- **Train gì:** Whisper-large-v3-turbo và PhoWhisper-large, bằng LoRA. Dữ liệu là 3.092 wav của 1.033 mẫu train, nhãn là `audio_text`.
  - **Loại hẳn 458 mẫu của dev_random và dev_lao.** Code kiểm từng wav, nên không wav dev nào lọt vào. Nhờ vậy, sau đó vẫn chấm được cả đường audio → ASR → agent trên hai tập dev.
  - 54 mẫu (210 wav) được giữ riêng. WER trên phần này, đo trước khi train và sau mỗi epoch, dùng để chọn epoch. Không dùng dev để chọn gì.
- **Vì sao nhãn là `audio_text` nguyên văn:** ASR học luôn kiểu chữ mà agent đã quen (viết hoa, dấu câu, cách viết số). Theo báo cáo E2E, PhoWhisper sai ít từ hơn turbo nhưng điểm agent lại thấp hơn, phần lớn vì khác kiểu chữ.
- **Vì sao LoRA:** vừa T4 16 GB ở fp16, model gốc giữ nguyên, adapter nhỏ. Sau khi gộp, số tham số không đổi (turbo 0,81B, PhoWhisper 1,55B), nên vẫn dưới trần 6B khi cộng với LLM.
- **Kết quả mỗi model** (`asr_results_<model>.tar.gz`):
  - adapter LoRA;
  - log từng bước và WER trên phần giữ riêng trước và sau khi train;
  - transcript mới của dev_random và dev_lao theo đúng định dạng của `infer.py`;
  - `asr_quality` so với turbo và PhoWhisper gốc (WER lượt cuối và history, số, giờ, từ phủ định, query).
- **Điểm agent:** Claude chấm trên laptop bằng transcript mới, so thẳng với 31,69 (dev_random) và 17,14 (dev_lao) trên cùng máy.

## Nên chạy thế nào

- **Song song trên hai tài khoản Colab** (mỗi tài khoản Google có Colab riêng): Anh chạy `MODELS="turbo"`, leader chạy `MODELS="pho"`. Mỗi bên mất khoảng 1,5–2,5 giờ.
- Một tài khoản thì để `MODELS="turbo pho"`: chạy turbo trước, mất khoảng 4–5 giờ. Mỗi model xong là gói kết quả lên Drive ngay, nên nếu phiên bị ngắt giữa chừng thì vẫn còn kết quả của model trước.
- Ước tính thô, **chưa đo trên T4**:

  | Việc | Thời gian |
  |---|---|
  | Cài môi trường | 10–20 phút |
  | Turbo: 3 epoch, nhận dạng 2 tập dev | khoảng 1,5–2 giờ |
  | PhoWhisper: 3 epoch, nhận dạng 2 tập dev | khoảng 2–2,5 giờ |

  Ô lệnh có giới hạn thời gian: nếu chưa xong 3 epoch khi phiên sắp hết, nó dừng và giữ epoch tốt nhất.

## Các bước

1. **Tải gói lên Drive.** File `~/zac_asr_bundle_20261031.tar.gz` (845 MB, trên máy Anh) gồm code, dữ liệu train kèm audio train (không có audio public) và transcript gốc. Tải lên **thư mục gốc My Drive** của tài khoản sẽ chạy. Nếu leader chạy, Anh gửi riêng file cho leader. File có dữ liệu thi: không chia sẻ thư mục, xoá khi xong.
2. Mở https://colab.research.google.com → **New notebook**. Chọn **Runtime → Change runtime type → T4 GPU → Save**.
3. **Ô thứ nhất** (Python), chạy rồi bấm cho phép truy cập Drive:
   ```python
   from google.colab import drive; drive.mount('/content/drive')
   ```
4. **Ô thứ hai:** dán toàn bộ ô lệnh bên dưới. Chỉ sửa dòng `MODELS` nếu cần, rồi chạy. **Để tab mở** tới khi xong; Colab free có thể ngắt khi lâu không tương tác.
5. Theo dõi trong ô:
   - dòng `OK: Tesla T4 ...` nghĩa là kiểm tra trước khi cài đã qua;
   - mỗi epoch in `val_wer` (epoch 0 là model gốc);
   - cuối cùng in chất lượng trên hai tập dev.
6. **Kết quả:** `My Drive/zac_out/asr_results_turbo.tar.gz` và `asr_results_pho.tar.gz`. Tải về, đặt vào `~/Zalo AI Challenge/cloud_results/` rồi báo Claude. Nếu cài lỗi thì có `zac_asr_logs.tar.gz`; gửi file đó.
7. Xoá gói và `zac_out` trên Drive khi xong.

```bash
%%bash
# ZAC 2026: fine-tune ASR (Whisper-large-v3-turbo, PhoWhisper-large) trên Colab T4 (hoặc Kaggle). Chạy SAU ô mount Drive.
# Chỉ sửa dòng MODELS nếu cần. Hướng dẫn: docs/ASR_FINETUNE_2026-10-31.md trong repo ZAIC_2026 (nhánh main).
MODELS="turbo pho"   # chạy lần lượt; mỗi model xong là gói kết quả ngay, nên phiên bị ngắt giữa chừng vẫn còn model trước
BUNDLE=zac_asr_bundle_20261031.tar.gz
START=$(date +%s); W=$HOME/zac
say() { echo "[$(date '+%H:%M:%S')] $*"; }
if [ -d /kaggle/input ]; then IN=/kaggle/input; OUT=/kaggle/working; else IN=/content/drive/MyDrive; OUT=/content/drive/MyDrive/zac_out; fi
left_min() { echo $(( 11 * 60 - ($(date +%s) - START) / 60 )); }   # phiên dừng ở 12 giờ; chừa 1 giờ

# 0. Kiểm tra trước khi cài
MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1)
[ "${MEM:-0}" -ge 15000 ] || { say "LỖI: cần GPU từ 16 GB (Colab: Runtime > Change runtime type > T4 GPU). Đang có: $(nvidia-smi -L 2>/dev/null || echo không có GPU)"; exit 1; }
curl -sfI https://huggingface.co >/dev/null || { say "LỖI: không có Internet"; exit 1; }
B=$(find "$IN" -name "$BUNDLE" 2>/dev/null | head -1)
D=$(find "$IN" -maxdepth 6 -type d -name ZAIC_2026 2>/dev/null | head -1)
[ -n "$B$D" ] || { say "LỖI: không thấy $BUNDLE trong $IN (Colab: chạy ô mount Drive trước; file phải ở thư mục gốc My Drive)"; exit 1; }
FREE=$(df -BG --output=avail "$HOME" | tail -1 | tr -dc 0-9)
[ "${FREE:-0}" -ge 30 ] || { say "LỖI: ổ chỉ còn ${FREE}G trống, cần ít nhất 30G"; exit 1; }
say "OK: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1) ${MEM} MiB; có Internet; gói ${B:-$D}; ổ trống ${FREE}G"

# 1. Giải nén và cài môi trường (khoảng 10-20 phút)
mkdir -p "$OUT" "$W" && cd "$W" || exit 1
if [ -n "$B" ]; then tar -xzf "$B"; else cp -r "$D" .; fi
cd ZAIC_2026 || exit 1
chmod -R u+w . 2>/dev/null
say "Đang cài môi trường (log: setup.log)..."
ASR_ONLY=1 bash lifemate/scripts/cloud_setup.sh > setup.log 2>&1 || { say "LỖI khi cài, 25 dòng cuối:"; tail -25 setup.log; tar -czf "$OUT/zac_asr_logs.tar.gz" setup.log; say "DỪNG: gửi zac_asr_logs.tar.gz cho Anh"; exit 0; }
cd lifemate

# 2. Mỗi model: chạy thử 3 bước, fine-tune, nhận dạng 2 tập dev, đo chất lượng, gói kết quả
for m in $MODELS; do
  case $m in
    turbo) MID=openai/whisper-large-v3-turbo; REV=(--revision 41f01f3fe87f28c78e2fbf8b568835947dd65ed9); BS=8; GA=2; EBS=16; EXTRA=() ;;
    pho) MID=vinai/PhoWhisper-large; REV=(--revision b9136a44b5f2ca664bd0b8f74baecf1715f6eeeb); BS=4; GA=4; EBS=8; EXTRA=() ;;
    tiny) MID=openai/whisper-tiny; REV=(); BS=2; GA=1; EBS=8; EXTRA=(--limit-samples 8 --max-steps 3) ;;  # chỉ để thử ô lệnh
    *) say "bỏ qua model lạ: $m"; continue ;;
  esac
  T=${m}ft; LOGS=(../setup.log)
  LEFT=$(left_min)
  [ "$LEFT" -ge 90 ] || { say "$m: chỉ còn $LEFT phút trong phiên, bỏ qua"; continue; }
  say "$m: chạy thử 3 bước (log: asr_smoke_$m.log)..."
  .venv/bin/python -m lifemate.asr_train --model $MID "${REV[@]}" --limit-samples 4 --max-steps 3 --epochs 1 --batch-size 2 \
      --grad-accum 1 --eval-batch-size 4 --no-merge --overwrite --out ckpt/_smoke_asr_$m > ../asr_smoke_$m.log 2>&1 \
      || { say "LỖI $m khi chạy thử, 20 dòng cuối:"; tail -20 ../asr_smoke_$m.log; tar -czf "$OUT/asr_results_$m.tar.gz" ../setup.log ../asr_smoke_$m.log; continue; }
  LEFT=$(( $(left_min) - 30 ))   # chừa 30 phút cho nhận dạng dev và gói kết quả
  say "$m: fine-tune, tối đa $LEFT phút (log: asr_train_$m.log)..."
  .venv/bin/python -m lifemate.asr_train --model $MID "${REV[@]}" --batch-size $BS --grad-accum $GA --eval-batch-size $EBS \
      --max-minutes $LEFT "${EXTRA[@]}" --out ckpt/asr_$T > ../asr_train_$m.log 2>&1
  grep -E '"epoch"|"done"' ../asr_train_$m.log | cut -c1-200
  FILES=(../asr_smoke_$m.log ../asr_train_$m.log)
  for f in adapter train_log.jsonl split_ids.json asr_train.meta.json; do [ -e ckpt/asr_$T/$f ] && FILES+=(ckpt/asr_$T/$f); done
  if [ -d ckpt/asr_$T/merged ]; then
    for d in dev_random dev_lao; do
      say "$m: nhận dạng $d..."
      .venv/bin/python -m lifemate.asr --split train --ids splits/$d.txt --model ckpt/asr_$T/merged --batch-size $EBS \
          --overwrite --out asr/train_${d}_$T.jsonl > ../asr_decode_${m}_$d.log 2>&1 && FILES+=(asr/train_${d}_$T.jsonl asr/train_${d}_$T.meta.json)
      base=(); for b in asr/train_${d}_turbo.jsonl asr/train_${d}_pho.jsonl; do [ -f $b ] && base+=($b); done
      .venv/bin/python scripts/asr_quality.py "${base[@]}" asr/train_${d}_$T.jsonl --ids splits/$d.txt \
          --json runs/asr_quality_${d}_$T.json > ../asr_quality_${m}_$d.log 2>&1 && FILES+=(runs/asr_quality_${d}_$T.json)
      tail -4 ../asr_quality_${m}_$d.log | cut -c1-200
      FILES+=(../asr_decode_${m}_$d.log ../asr_quality_${m}_$d.log)
    done
  else
    say "LỖI $m: không có model đã gộp, 20 dòng cuối của log:"; tail -20 ../asr_train_$m.log
  fi
  tar -czf "$OUT/asr_results_$m.tar.gz" ../setup.log "${FILES[@]}" 2>/dev/null
  say "$m: đã gói $OUT/asr_results_$m.tar.gz ($(du -h "$OUT/asr_results_$m.tar.gz" | cut -f1))"
done
say "XONG. Gửi Anh các file:"; ls -la "$OUT" | grep -E "asr_results|zac_asr_logs"
```

## Đọc kết quả

- **`val_wer`:** epoch 0 (model gốc) so với epoch tốt nhất, trên cùng máy và cùng cách giải mã. `val_wer_raw` tính cả viết hoa và dấu câu, cho biết ASR đã học kiểu chữ của `audio_text` chưa.
- **`asr_quality`** trên dev_random và dev_lao, so với turbo và PhoWhisper gốc: WER lượt cuối và history, giữ đúng số, giờ, từ phủ định, query tìm kiếm. Bản gốc được giải mã trên laptop, bản mới trên T4. Khác máy có thể làm vài câu đổi chút ít, nên chỉ coi chênh lệch lớn là chắc chắn.
- **Điểm agent:** Claude chạy `ASR_FILE=asr/train_dev_random_<model>ft.jsonl ... eval_ckpt.sh` trên laptop, so theo cặp với 31,69 và 17,14. Chọn ASR theo điểm này (luật cũ: điểm cộng gộp hai tập dev cao hơn; chênh dưới 1 điểm thì chọn model nhỏ hơn).

## Quy tắc

- Không train trên wav của dev (code kiểm từng wav). Gói không có audio public; không gán nhãn hay pseudo-label tập test.
- **k-fold khi train agent trên chữ ASR:** nếu sau này train agent trên transcript của ASR đã fine-tune, transcript của mỗi wav train phải do một model **chưa train trên wav đó** tạo ra. Nếu không, ASR "thuộc lòng" câu train và chữ đầu vào sạch hơn thực tế. Bộ công cụ chưa làm k-fold.
- Model và revision ghim: turbo `41f01f3f`, PhoWhisper `b9136a44`.

## Đã kiểm và chưa kiểm

- **Đã kiểm, chỉ trên CPU** (GPU laptop đang train agent):
  - 6 test của `asr_train` đạt, gồm test không wav dev nào lọt vào train.
  - Chạy với Whisper-tiny: chia dữ liệu, WER gốc, train, WER sau epoch, adapter, gộp, rồi `lifemate.asr` giải mã bằng model đã gộp; `--merge-only` cho ra trọng số giống hệt.
  - Gói có audio: 7.405 file, 0 khác khi kiểm; 5.036 wav train, 0 wav public, 0 file rác.
  - `cloud_setup.sh` với `ASR_ONLY=1` dừng đúng sau bước cài môi trường.
  - **Ô lệnh chạy trọn vẹn** trên CPU, với gói thật, GPU T4 giả lập và `MODELS="tiny"` (14:53–15:10): kiểm tra trước, cài môi trường, chạy thử 3 bước, fine-tune, gộp model, nhận dạng dev_random và dev_lao, `asr_quality` so với turbo và PhoWhisper gốc, gói kết quả (7,8 MB). Whisper-tiny cho WER trên 100%: chỉ dùng để thử đường chạy, không phải kết quả.
- **Chưa kiểm:**
  - Chạy trên GPU: fp16, bộ nhớ và tốc độ trên T4. Ô lệnh chạy thử 3 bước trước mỗi model để lỗi lộ ra sớm.
  - Siêu tham số (lr 3e-4, LoRA r 32, 3 epoch, SpecAugment theo mặc định của model) chưa tinh chỉnh.
