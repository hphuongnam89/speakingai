# Phase 8 calibration protocol

Không được publicize overall IELTS score như kết quả chính thức khi chưa có calibration dataset consented. Mỗi mẫu cần transcript/audio được phép dùng, level, tối đa hai human raters khi có thể, bốn criterion FC/LR/GRA/Pronunciation và AI provenance gồm model, prompt và scoring version.

Release gate mặc định: báo cáo sai lệch theo criterion và level; academic owner quyết định ngưỡng chấp nhận. Trong lúc chưa có đủ mẫu, API luôn trả `score_status=provisional`, `confidence_range`, `limitation` và disclaimer. Pronunciation để `null` nếu chỉ có transcript.

Feedback flags được lưu bằng `POST /api/v1/ielts/evaluate/{session_id}/feedback` với một trong `useful`, `incorrect`, `too_harsh`, `too_vague`. Mọi prompt/model change phải chạy regression set trước khi phát hành.
