# Việc của người — Anh và Leader

Danh sách việc trong lúc laptop của Anh train qua đêm, và sáng hôm sau. Phần cuối là 20 câu hỏi nghiên cứu, chép từ [`docs/PIPELINE.md`](docs/PIPELINE.md).

## Cách dùng file

- Mỗi việc ghi người phụ trách: **[Anh]**, **[Leader]** hoặc **[Cả hai]**.
- Xong việc nào thì đánh dấu `[x]` và ghi kết quả ngắn ngay dưới việc đó. Commit thẳng lên `main` (tài liệu không cần PR).
- **Laptop của Anh đang train, nên không chạy gì dùng GPU trên máy này.** Mọi lệnh dưới đây chỉ dùng CPU.
- Các lệnh chạy trong thư mục `lifemate/`, trên nhánh `agent-pipeline` (code chưa vào `main`, đang nằm ở [PR #1](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/1)).
- Mọi lệnh trong file đã được Claude chạy thử trên máy của Anh ngày 2026-10-28.

---

## 1. Ngay bây giờ (15 phút đầu)

- [ ] **[Anh]** Mở terminal, paste lệnh train (lấy ở `JOURNAL.md`, mục "Lệnh chạy train qua đêm"):
  ```bash
  cd ~/"Zalo AI Challenge/lifemate" && mkdir -p runs && { nohup systemd-inhibit --what=sleep:idle:handle-lid-switch --why="LifeMate training" bash scripts/train_local.sh > runs/overnight.log 2>&1 & } && sleep 5 && tail -f runs/overnight.log
  ```
- [ ] **[Anh]** Khoảng 10–15 phút sau, kiểm tra log:
  - Dòng `{"n": 233, ...}` của baseline zero-shot đã xuất hiện.
  - Khi bắt đầu train: `peak_gb` dưới khoảng 6,3 và `tok_s` khoảng 1.400.
  - Ghi `eta_min` (số phút còn lại) vào đây: …
- [ ] **[Anh]** Cắm sạc. Không mở game, video hay ứng dụng nặng GPU, vì VRAM chỉ còn dư khoảng 0,9GB.
- [ ] **[Leader]** Chuẩn bị máy của mình để chạy được code:
  ```bash
  git clone https://github.com/Nguyen-Le-Tuan/ZAIC_2026.git && cd ZAIC_2026 && git checkout agent-pipeline
  mkdir -p data && unzip -q /đường/dẫn/tới/train+public_test.zip -x '__MACOSX/*' -d data   # phải ra data/train+public_test/
  command -v uv || curl -LsSf https://astral.sh/uv/install.sh | sh
  cd lifemate && uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
  ```

## 2. Hiểu bài và hiểu code (khoảng 1 giờ)

- [ ] **[Cả hai]** Đọc `JOURNAL.md` (mục 0–4) và `docs/PIPELINE.md` (mục 1–4).
- [ ] **[Cả hai]** Đọc README gốc của BTC: `data/train+public_test/README.md` và `data/train+public_test/train/zaic_tools/README.md`. **Ghi lại mọi chỗ khác với `JOURNAL.md`**, vì Claude có thể đã hiểu sai.
- [ ] **[Cả hai]** Xem tận mắt prompt mà model nhìn thấy cho mẫu `train_0001`, rồi đối chiếu với lời giải ở `docs/PIPELINE.md` mục 2.4:
  ```bash
  cd lifemate && .venv/bin/python -c "
  from lifemate.data import *; from lifemate.prompt import *
  cat=load_catalog('train'); s=[x for x in load_split('train') if x['id']=='train_0001'][0]
  h=[t['audio_text'] for t in s['history'] if t['role']=='user']
  print(to_chatml(build_messages(s,s['audio_text'],h,catalog_tools(cat),{a['id']:a for a in cat['apps']})))" | less
  ```
- [ ] **[Cả hai]** Tự chạy lại kiểm chứng "phát lại đáp án phải ra 100" (chỉ dùng CPU, khoảng 1 phút):
  ```bash
  cd lifemate && .venv/bin/python -m lifemate.infer --split train --text oracle --backend oracle --out runs/oracle_train.jsonl \
    && .venv/bin/python -m lifemate.scorer runs/oracle_train.jsonl --split train
  ```
- [ ] **[Cả hai]** Review [PR #1](https://github.com/Nguyen-Le-Tuan/ZAIC_2026/pull/1) theo thứ tự `prompt.py` → `agent.py` → `scorer.py` → `sft.py` → `train.py`.
  - Comment trên GitHub mọi chỗ chưa hiểu hoặc nghi là sai.
  - **Mục tiêu:** mỗi người tự giải thích lại được vòng lặp agent bằng lời của mình.
- [ ] **[Cả hai]** Tự kiểm tra lại bằng tay một phát hiện của Claude. Ví dụ đọc 10 mẫu có `contacts.search` để xác nhận "query là tên lưu trong danh bạ, không phải lời người nói" (`JOURNAL.md`, phát hiện 13). Kết luận: đúng / sai / có ngoại lệ: …

## 3. Nghe audio: việc chỉ người làm được (khoảng 1 giờ)

- [ ] **[Cả hai]** Nghe 30 mẫu train ngẫu nhiên và so với `audio_text`.
  - Bước 1, tạo danh sách:
    ```bash
    cd lifemate && .venv/bin/python -c "
    import random; from lifemate.data import *
    random.seed(1); S=load_split('train')
    for s in random.sample(S,30): print(DEFAULT_ROOT/'train'/s['audio'], '|', s['context']['user_profile'].get('city'), '|', s['audio_text'])" > runs/listen_train.txt
    ```
  - Bước 2, nghe lần lượt (bấm Enter để sang mẫu sau):
    ```bash
    cd lifemate && while IFS='|' read -r f city text; do echo "== [$city]$text"; aplay -q "${f% }"; read -rp "   Enter để nghe tiếp " _ </dev/tty; done < runs/listen_train.txt
    ```
  - Ghi vào bảng ghi chú bên dưới. Câu cần trả lời: **`audio_text` là kịch bản người nói đọc theo, hay transcript thật của audio? Người nói có đọc lệch kịch bản không?** Câu trả lời quyết định nhãn dùng để train ASR.
- [ ] **[Cả hai]** Nghe 20 mẫu public để hiểu phân bố. **Chỉ nghe, không ghi transcript, không dùng để train**, vì thể lệ cấm gán nhãn tập test. Ghi lại khác biệt so với train.
  ```bash
  cd lifemate && .venv/bin/python -c "
  import random; from lifemate.data import *
  random.seed(2); S=load_split('public_test')
  for s in random.sample(S,20): print(DEFAULT_ROOT/'public_test'/s['audio'], '|', s['context']['user_profile'].get('city'), '|', ', '.join(s['context']['installed_apps']))" > runs/listen_public.txt
  while IFS='|' read -r f city apps; do echo "== [$city] app:$apps"; aplay -q "${f% }"; read -rp "   Enter để nghe tiếp " _ </dev/tty; done < runs/listen_public.txt
  ```
- [ ] **[Leader]** Từ những gì đã nghe, lập danh sách **"cụm từ nguy hiểm" cho ASR**: số tiền, giờ, ngày, tên người, từ phủ định ("đừng", "thôi khỏi"), tự sửa giữa câu. Đây là đầu vào cho Q9.

**Bảng ghi chú khi nghe** (mỗi mẫu một dòng):

| id | Giọng (Bắc/Trung/Nam) | Giọng nam/nữ, tuổi ước lượng | Nhiễu nền | Cách đọc số, giờ | Từ tiếng Anh | Audio lệch transcript? | Ghi chú |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## 4. Làm việc với BTC và cộng đồng

- [ ] **[Leader]** Đọc forum và kênh hỏi đáp của cuộc thi. Tìm hướng dẫn đóng gói Docker (BTC nói sẽ có tài liệu riêng) và các thông báo thay đổi dữ liệu.
- [ ] **[Leader]** Hỏi BTC những chỗ luật chưa rõ:
  1. Tham số không fuzzy được so khớp có phân biệt chữ hoa/thường và khoảng trắng không? List (ví dụ `params` của `sys.ask_missing_info`) có xét thứ tự không?
  2. "Token" trong token-F1 được tách theo khoảng trắng, hay có bỏ dấu câu trước?
  3. Giới hạn 30 giây mỗi mẫu có tính cả thời gian nạp model lúc khởi động không?
  4. Khi nào có hướng dẫn Docker? Máy chấm dùng phiên bản CUDA và driver nào? Image có giới hạn dung lượng không?
  5. Private test có dùng bản `zaic_tools` và catalog mới, tức là có app mới không?
  6. Mốc "phát hành trước 26/10/2026" tính theo ngày công bố trọng số model hay ngày công bố paper?
- [ ] **[Leader]** Xem bảng xếp hạng public: điểm cao nhất hiện tại, số đội tham gia. Ghi vào đây: …
- [ ] **[Leader]** *Quyết định:* có dùng 1 lượt nộp public hôm nay cho **bài nộp rỗng** không?
  - Mục đích: đo tỉ lệ mẫu ngoài phạm vi của public. Điểm nhận được = 100 × tỉ lệ đó; train là 7,18.
  - Đây là một lần dò để hiểu dữ liệu, không phải để leo bảng xếp hạng.
  - File nộp: `lifemate/runs/public_empty.jsonl` (đã có sẵn trên máy của Anh), hoặc tạo lại bằng:
    ```bash
    cd data/train+public_test && python3 -c "
    import json,sys; sys.path.insert(0,'public_test'); from zaic_tools import ToolEnv
    with open('public_test/public_test.jsonl',encoding='utf-8') as f, open('../../lifemate/runs/public_empty.jsonl','w',encoding='utf-8') as o:
        for l in f:
            i=json.loads(l)['id']; e=ToolEnv('public_test',i,root='.')
            o.write(json.dumps({'id':i,'tool_calls':[],'state_hash':e.get_state_hash()})+'\n')"
    PYTHONPATH=public_test python3 -m zaic_tools --split public_test --root . --validate ../../lifemate/runs/public_empty.jsonl
    ```
  - Kết quả (ghi thêm vào Q6): …

## 5. Chuẩn bị tài nguyên

- [ ] **[Anh hoặc Leader]** Chọn nhà cung cấp GPU cloud, tạo tài khoản và nạp tiền. Claude không làm các việc thanh toán. Cần 2 loại máy:
  - 1 máy A100 hoặc H100 80GB để train.
  - 1 máy 24GB (A30 nếu thuê được, không thì L4 hoặc A10) để đo thời gian giống máy chấm.
- [ ] **[Anh]** Tạo Hugging Face token (quyền read) để tải model nhanh hơn, không bị giới hạn lượt tải.
- [ ] **[Leader]** Rà Hugging Face tìm LLM dưới 5B và ASR tiếng Việt phát hành từ 06/2026 tới 25/10/2026. Kiến thức của Claude dừng ở giữa năm 2026 nên không biết các model này. Ghi tên, số tham số, licence, ngày phát hành.
- [ ] **[Leader]** Lập bảng licence các model ứng viên: Qwen3 (Apache-2.0), Whisper (MIT), PhoWhisper (BSD-3) và các model khác. Đánh dấu model nào dùng licence không thương mại (CC-BY-NC).

## 6. Tổ chức đội

- [ ] **[Cả hai]** Thống nhất quy trình review PR: ai review, trong bao lâu, tiêu chí để merge (ví dụ: kiểm chứng phát lại đáp án vẫn ra 100, điểm dev không giảm).
- [ ] **[Cả hai]** Đặt lịch họp ngắn hằng ngày và chốt mốc đóng băng tính năng (xem Q20).

## 7. Sáng mai, khi train xong

- [ ] **[Anh]** Xem 2 file điểm: `lifemate/runs/zs_q17b_fit_random_score.json` (trước khi train) và `lifemate/runs/sft_q17b_fit_random_score.json` (sau khi train).
- [ ] **[Cả hai]** **Tự phân tích lỗi trước khi hỏi Claude.** In 15 mẫu sai, rồi tự phân nhóm nguyên nhân bằng mắt (sai ID, sai giờ, thiếu bước đọc, gọi thừa, hỏi lại sai lúc, gọi tool ở mẫu ngoài phạm vi…). Sau đó mới so với phân tích của Claude.
  ```bash
  cd lifemate && TAG=q17b_fit_random && .venv/bin/python -c "
  import json; from lifemate.data import *
  tag='$TAG'; rows=load_jsonl(f'runs/sft_{tag}_rows.jsonl'); pred={r['id']:r for r in load_jsonl(f'runs/sft_{tag}.jsonl')}
  S={s['id']:s for s in load_split('train')}
  for r in [r for r in rows if r['score']<1][:15]:
      s=S[r['id']]; print('=====',r['id'],r['category'],'| điểm',round(r['score'],2),'| hash đúng' if r['hash_ok'] else '| HASH SAI'); print('  NÓI   :',s['audio_text'])
      for c in s['label']['tool_calls']: print('  ĐÁP ÁN:',json.dumps(c,ensure_ascii=False))
      for c in pred[r['id']]['tool_calls']: print('  MODEL :',json.dumps(c,ensure_ascii=False))
  " | less
  ```
- [ ] **[Anh]** Mở chat với Claude: *"Đọc `JOURNAL.md`, `docs/PIPELINE.md` và `HUMAN_TODO.md`. Đây là kết quả train và câu trả lời của đội…"*

---

## 8. Hai mươi câu hỏi nghiên cứu

Chép từ [`docs/PIPELINE.md`](docs/PIPELINE.md) mục 5. **Ghi câu trả lời ở đây**, không ghi bên `PIPELINE.md`, để chỉ có một nơi lưu câu trả lời. Người phụ trách chỉ là gợi ý; ai có ý tưởng thì cứ viết thêm.

### A. Hiểu thước đo và chính sách sinh nhãn

- [ ] **[Leader]** **Q1. Server so khớp tham số không fuzzy thế nào: có phân biệt chữ hoa không, có gộp khoảng trắng không, list có xét thứ tự không?**
  - *Vì sao:* quyết định có cần viết hoa query, sắp xếp list `params` của `ask_missing` hay không.
  - *Gợi ý:* thiết kế 1–2 lần nộp public **dùng để dò thước đo**, không phải để tối ưu. Ví dụ nộp cùng một bài nhưng viết thường toàn bộ query của call đọc, rồi so điểm.
  - **Trả lời của đội:**
- [ ] **[Cả hai]** **Q2. BTC sinh đáp án như thế nào: bằng template, bằng LLM, hay bằng một simulator chạy chính sách cố định? Tìm thêm dấu vết** (ngoài chuyện query dùng tên trong danh bạ).
  - *Vì sao:* biết cách nhãn được sinh thì tái tạo được chính sách cho app mới.
  - *Gợi ý:* so sánh nhiều mẫu cùng kiểu yêu cầu; xem tham số fuzzy được viết theo văn phong nào; xem thứ tự các call.
  - **Trả lời của đội:**
- [ ] **[Cả hai]** **Q3. Viết thành luật: khi nào đáp án gọi call đọc trước lệnh ghi, khi nào đọc kèm bộ lọc, khi nào bỏ qua bước đọc?**
  - *Vì sao:* call đọc chiếm phần lớn F1, và luật tổng quát dùng được cho app mới.
  - *Gợi ý:* thống kê theo từng cặp (call đọc, lệnh ghi); đã biết 113/126 lần bật đèn có `get_status` trước, và 11 lần còn lại đều do đã có trong history.
  - **Trả lời của đội:**
- [ ] **[Cả hai]** **Q4. Ranh giới giữa hỏi lại, tự quyết và bỏ qua: các "tín hiệu" nào dẫn tới `ask_missing_info`?**
  - *Vì sao:* 14% mẫu là hỏi lại, và danh sách `params` phải khớp chính xác.
  - *Gợi ý:* đọc 217 mẫu hỏi lại, phân nhóm: trùng tên, thiếu giờ, thiếu số tiền, yêu cầu mơ hồ ("hạ xuống chút")… Rút ra danh sách kiểm tra.
  - **Trả lời của đội:**
- [ ] **[Cả hai]** **Q5. Phân loại 111 mẫu ngoài phạm vi theo nguyên nhân. Có mẫu "làm được một phần" không, và đáp án xử lý ra sao?**
  - *Vì sao:* gọi dù chỉ một call ở mẫu ngoài phạm vi là mất trắng; còn yêu cầu nhiều ý mà chỉ một ý làm được thì cách xử lý chưa rõ.
  - *Gợi ý:* lọc các mẫu có nhiều ý định mà thiếu một app; xem đáp án làm phần còn lại hay trả `[]`.
  - **Trả lời của đội:**

### B. Tổng quát hoá và tín hiệu đánh giá

- [ ] **[Cả hai]** **Q6. Private test có thể khác public ở những điểm nào** (app mới, phân bố loại mẫu, giọng nói, độ dài history)? **Bộ dev nào mô phỏng private tốt nhất?** Leave-apps-out đã đủ chưa, hay cần leave-groups-out?
  - *Gợi ý:* so phân bố của public với train (app đã cài, độ dài history, thành phố); đặt giả định "xấu nhất hợp lý".
  - **Trả lời của đội:**
- [ ] **[Leader]** **Q7. Dùng 5 lần nộp public mỗi ngày vào việc gì để không overfit?** Đặt quy tắc cho đội, ví dụ "chỉ nộp khi dev nội bộ tăng ít nhất X điểm" hoặc "dành một lần nộp mỗi ngày để dò thước đo hoặc đo ASR".
  - **Trả lời của đội:**
- [ ] **[Cả hai]** **Q8. Nếu điểm dev nội bộ và điểm public lệch nhau, những nguyên nhân nào có thể giải thích, và kiểm tra từng nguyên nhân thế nào?** Ví dụ: ASR thật so với text chuẩn, app mới, khác biệt của bộ chấm, phiên bản `zaic_tools`.
  - **Trả lời của đội:**

### C. ASR

- [ ] **[Leader]** **Q9. Lỗi ASR nào thực sự làm mất điểm? Định nghĩa "tỉ lệ lỗi slot" thay cho WER thế nào?**
  - *Gợi ý:* từ bảng ở mục 3.2, lấy các tham số của lệnh ghi có nguồn là ngày giờ hoặc số, tìm cụm từ tương ứng trong `audio_text` (ví dụ "muộn 1 tiếng", "hai triệu tám"), rồi đo ASR nghe đúng các cụm đó bao nhiêu phần trăm. Đừng quên từ phủ định: "đừng", "thôi khỏi".
  - **Trả lời của đội:**
- [ ] **[Leader]** **Q10. Có dùng được ngữ cảnh hợp lệ để sửa ASR không?** Ví dụ tên app đã cài, enum trong schema, tên kênh, và sau khi agent đọc danh bạ thì sửa lại tên người.
  - *Lưu ý:* chỉ được dùng dữ liệu lấy qua tool, không được đọc `state.json`.
  - *Gợi ý:* Whisper có `initial_prompt` hoặc hotword; hoặc sửa ở lớp sau, khi so khớp với kết quả tool.
  - **Trả lời của đội:**
- [ ] **[Leader]** **Q11. Lượt user trong history có cần ASR chất lượng cao không, hay model nhỏ, nhanh là đủ?**
  - *Gợi ý:* trên train, thay transcript history bằng ASR kém hơn (hoặc cố tình làm nhiễu) rồi đo điểm agent giảm bao nhiêu.
  - **Trả lời của đội:**
- [ ] **[Leader]** **Q12. Chuẩn hoá chữ thành số đặt ở đâu: ASR xuất thẳng chữ số, một bộ quy tắc riêng, hay để LLM tự hiểu?**
  - *Vì sao:* 11% tham số của lệnh ghi là số phải tính.
  - *Gợi ý:* thử cả 3 cách trên các mẫu có `amount`, `time`, `phone`.
  - **Trả lời của đội:**

### D. Agent và mô hình

- [ ] **[Anh]** **Q13. Phần nào nên chuyển từ LLM sang code tất định, và mỗi phần cứu được bao nhiêu điểm?**
  - *Gợi ý:* dùng mục 3.2 làm khung; với từng nhóm (ngày giờ, số, ID, quy ước call đọc), ước lượng số mẫu bị ảnh hưởng × xác suất LLM làm sai.
  - **Trả lời của đội:**
- [ ] **[Anh]** **Q14. Có nên ép model chỉ được sinh ID đã xuất hiện trong kết quả tool hoặc history, và chỉ sinh enum hợp lệ** (constrained decoding)? Rủi ro là gì?
  - *Ví dụ rủi ro:* chặn nhầm ID hợp lệ được tạo trong lượt; làm chậm suy luận.
  - **Trả lời của đội:**
- [ ] **[Anh]** **Q15. Đánh đổi giữa model 4B và 1.7B, LoRA và full fine-tune, có thêm một dòng "kế hoạch ngắn" trước khi gọi tool hay không — trong giới hạn 30 giây và 16K token. Thí nghiệm nào trả lời rẻ nhất?**
  - **Trả lời của đội:**
- [ ] **[Anh]** **Q16. vLLM có cho kết quả giống hệt nhau qua 5 lần chạy không (greedy, batch 1, cùng GPU)? Nếu không, khử khác biệt bằng cách nào?**
  - *Vì sao:* nếu lần chạy lại của BTC khác kết quả đã nộp, họ lấy trung bình 5 lần, có thể tụt điểm.
  - **Trả lời của đội:**

### E. Dữ liệu

- [ ] **[Anh]** **Q17. Làm sao để dữ liệu tổng hợp tuân theo chính sách của BTC chứ không theo "thói quen" của LLM sinh dữ liệu? Kiểm chứng độ "giống thật" ra sao?**
  - *Gợi ý:* (a) chỉ train trên dữ liệu tổng hợp rồi đo trên train thật; (b) huấn luyện một bộ phân loại thật/giả; (c) so phân bố số call, tỉ lệ hỏi lại, tỉ lệ ngoài phạm vi.
  - **Trả lời của đội:**
- [ ] **[Anh]** **Q18. Đa dạng hoá ngôn ngữ nói thế nào và theo tỉ lệ bao nhiêu?** Gồm phương ngữ, tự sửa giữa câu ("5 giờ, à không, 5 rưỡi"), phủ định, nhiều ý định trong một câu, từ tiếng Anh xen vào. Cần TTS cho ASR hay chỉ cần text cho LLM?
  - **Trả lời của đội:**

### F. Kỹ thuật và quản trị rủi ro

- [ ] **[Leader]** **Q19. Liệt kê các kịch bản khiến bài nộp private về 0 hoặc mất nhiều điểm, và cách phòng cho từng kịch bản.**
  - *Ví dụ:* Docker cố tải model khi không có mạng; dùng sai bản `zaic_tools`; tràn bộ nhớ ở mẫu dài; quá 30 giây; đường dẫn `/data` sai; mã hoá UTF-8.
  - **Trả lời của đội:**
- [ ] **[Cả hai]** **Q20. Trong 19 ngày còn lại, đâu là đường găng (critical path)? Việc nào hai người làm song song được? Mốc "đóng băng tính năng" đặt ở ngày nào?**
  - **Trả lời của đội:**
