# Phase 10 implementation report — Controlled pilot

## Đã triển khai

- Controlled pilot API với ownership isolation:
  - `POST /api/v1/pilot/runs`
  - `POST /api/v1/pilot/runs/{id}/events`
  - `POST /api/v1/pilot/runs/{id}/feedback`
  - `GET /api/v1/pilot/runs/{id}/summary`
- Consent bắt buộc trước pilot; audio recording chỉ được phép khi `consent_audio=true`.
- Pilot event contract chỉ nhận `completed_without_help`, `completed_with_help` hoặc `blocked`.
- Feedback bắt buộc đo next action clarity, correction usefulness, score certainty và return intent.
- `DELETE /api/v1/pilot/runs/{id}` xóa pilot events/feedback/run để hỗ trợ rút consent và dọn test data.
- Pilot storage chỉ lưu metadata, không lưu audio hoặc full transcript.
- Migration `008_controlled_pilot`.
- Runbook, observer form, severity rubric và report template.
- Regression tests cho outcome contract và completion-rate calculation.

## Trạng thái acceptance criteria

Code và protocol đã sẵn sàng. Tuy nhiên pilot thực tế chưa được đánh dấu passed vì cần 3–5 learners thật, test accounts/devices và quan sát độc lập. Chưa được suy diễn completion rate, transcription success rate hoặc silent-recording-loss rate khi chưa có các run thực tế.

Trạng thái đúng hiện tại: **pilot harness ready / pilot execution pending**.

## Gate để đóng Phase 10

1. Chạy tối thiểu 3–5 learner runs theo runbook.
2. Điền toàn bộ task outcomes và feedback.
3. Đạt session completion >=70% và audio transcription success >=90%.
4. Xác nhận permission denied có recovery và không có silent recording loss.
5. Review mọi feedback flag `incorrect` trước khi chuyển Phase 11.
6. Ghi kết luận `pilot_passed` trong report template; nếu chưa đạt, ghi `pilot_blocked` và mở issue P0/P1 tương ứng.
