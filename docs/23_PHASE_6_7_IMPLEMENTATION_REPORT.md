# Phase 6–7 implementation report

## Phase 6 — IELTS pedagogy và AI tutor

Đã mở rộng correction contract với `error_type`, `subtype`, `severity` và `practice_prompt`. Tutor prompt hiện áp dụng band guidance cho nhóm 4.5–5.0, 5.5–6.0 và 6.5–7.0; giới hạn tối đa ba focus errors trong một session; yêu cầu framework answer → reason → example và chống prompt injection từ learner text. Parser JSON, bullet và arrow fallback đều tạo practice prompt an toàn. Response có `session_focus`, còn `/conversation/repeat-check` kiểm tra người học thực sự nói lại câu sửa bằng similarity thay vì chỉ phát TTS.

## Phase 7 — Progress, mistake notebook và adaptive learning

Mistake notebook đã có `error_type`, `subtype`, `successful_reuse_count`, `next_review_at`, `last_reviewed_at`, `mastery_state` và `example_sentence`. Endpoint `POST /api/v1/mistakes/{id}/review` chỉ đánh dấu mastered sau ba lần reuse thành công; review thất bại đưa lỗi trở lại learning state. Session model phân biệt `actual_speaking_ms`, `audio_duration_ms`, `typing_practice_ms` và `session_duration_ms`; speech transcription cập nhật speaking/audio time bằng duration thật.

Adaptive plan hiện lấy top weaknesses từ mistake evidence, trả về `next_best_action`, `evidence_count` và cache theo principal/ngày trong `adaptive_plans`. Migration `004_mistake_learning_state`, `005_adaptive_plan_cache` và `006_time_metric_dimensions` được thêm vào migration runner.

## Validation

Đã kiểm tra tĩnh diff và JavaScript syntax. Regression tests Phase 6–7 đã được thêm tại `backend/tests/test_phase6_7_learning.py`. Chưa thể chạy pytest trong phiên này nếu Python interpreter/virtualenv không khả dụng; cần chạy `scripts/check.ps1` trên clean environment trước khi đóng phase.
