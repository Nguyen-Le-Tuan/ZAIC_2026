# ZAIC 2026 — LifeMate

Giải pháp Zalo AI Challenge 2026, đề LifeMate (giọng nói tiếng Việt → agent gọi tool).

**Đọc [`JOURNAL.md`](JOURNAL.md) trước:** nhật ký dự án gồm đề bài, số liệu, quyết định, trạng thái hiện tại và việc tiếp theo. Sau đó đọc [`docs/PIPELINE.md`](docs/PIPELINE.md): pipeline, moat và câu hỏi nghiên cứu.

**Quy tắc git:** tài liệu commit thẳng vào `main`; code mới phải qua Pull Request.

| Thư mục | Nội dung |
|---|---|
| `JOURNAL.md`, `docs/` | Nhật ký và tài liệu nghiên cứu. |
| `lifemate/` | Agent: prompt, vòng lặp gọi tool, bộ chấm local, sinh dữ liệu SFT, train LoRA. Xem `lifemate/README.md` *(hiện ở PR `agent-pipeline`)*. |
| `data/` | **Không commit.** Giải nén `train+public_test.zip` vào `data/` để có `data/train+public_test/{train,public_test}/`. Thể lệ cấm phát tán bộ dữ liệu. |

Hạn: Docker 16/11/2026 23:59 (GMT+7) · private test 20–23/11/2026.
