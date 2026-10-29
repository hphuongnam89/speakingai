# Phase 10 — Controlled pilot runbook

## Scope

Chạy với 3–5 learners bằng test account/data. Người quan sát không coach trong lúc learner thao tác; chỉ ghi outcome sau mỗi task. Không dùng tài khoản production và không nhập dữ liệu nhận diện cá nhân vào participant code.

## Consent gate

Trước khi bật microphone, learner phải xác nhận audio recording consent và feedback consent. Nếu audio consent bị từ chối, pilot chỉ test text path; không upload audio. Feedback consent là bắt buộc để đưa participant vào pilot summary. Consent có thể rút lại bằng cách đóng pilot run và xóa test account/data.

## Tasks

1. Kết nối backend và đăng nhập.
2. Chọn profile.
3. Tạo conversation session.
4. Cấp microphone permission và record một câu.
5. Xem transcript/correction và thực hiện say-it-again.
6. Xem IELTS provisional score, confidence và limitation.
7. Tìm progress và mistake notebook.
8. Thực hiện logout/login lại và xử lý permission denied hoặc timeout nếu được phân công.

Mỗi task gửi `POST /api/v1/pilot/runs/{run_id}/events` với một outcome: `completed_without_help`, `completed_with_help` hoặc `blocked`. Nếu learner không hiểu wording, ghi nguyên văn tối đa 500 ký tự trong `understood_quote`; không ghi audio/transcript đầy đủ.

## Feedback form

Sau task cuối, gửi một lần `POST /api/v1/pilot/runs/{run_id}/feedback`:

- `next_action_clear`: 1–5
- `correction_useful`: 1–5
- `score_too_certain`: 1–5
- `would_return`: 1–5
- `free_text`: tối đa 2.000 ký tự

## Pass criteria

- 100% learners connect, record, view feedback và find progress without takeover.
- 0 silent recording loss.
- Permission denied has recovery.
- Learners understand band is an estimate/provisional.
- Every incorrect feedback flag is reviewed before next phase.
- Completion rate >= 70%.
- Audio transcription success >= 90% on test devices.

Nếu chưa có 3–5 completed runs hoặc chưa đo được các metrics trên, trạng thái là `pilot_incomplete`, không được gọi là production-ready.
