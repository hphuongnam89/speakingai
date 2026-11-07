# 10 — Mẫu bàn giao

Sao chép mẫu này vào `docs/learning-handoffs/<timestamp>-<task-id>.md` khi triển khai. Không cập nhật chính mẫu bằng dữ liệu tưởng tượng.

## Baseline

- Task ID / plan version:
- Repo root / branch / HEAD:
- Worktree changes trước task (kể cả thay đổi người dùng):
- Donor SHA / content versions đã dùng:
- Mục tiêu và acceptance IDs:

## Kết quả

- Hành vi mới quan sát được:
- Files tạo/sửa (đường dẫn thật):
- Compatibility/data impact:
- Dependency/import/license đã thêm:
- Content status / reviewer evidence:

## Kiểm thử

| Lệnh hoặc manual flow | Môi trường/DB/provider | Kết quả thật | Log/artifact |
|---|---|---|---|
| Điền sau khi chạy | temporary/live, mock/real | pass/fail/not_run | path |

- Browser UI đã mở và thực hiện đến bước nào:
- Microphone/audio/model thật đã kiểm gì:
- Migration backup/restore đã kiểm gì:
- Chưa kiểm và lý do:

## Trạng thái và tiếp nối

- `planned / in_progress / needs_review / blocked / done`:
- Acceptance chưa đạt / blocker có bằng chứng:
- Quyết định đã chốt, không cần hỏi lại:
- Task đủ điều kiện tiếp theo:
- Lệnh chạy lại thực tế, không chứa secret:
- File/code location cần mở đầu tiên:

Chỉ cập nhật task `done` sau exit gate và lưu tham chiếu handoff vào `tasks.json`. Đừng đánh dấu một phase hoàn tất từ việc một file đã tồn tại hoặc một suite mock đã pass.
