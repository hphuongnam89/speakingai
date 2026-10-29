# Phase 0–1 implementation report

## Đã triển khai hoàn chỉnh

### 1. Phase 0 — Product contract và baseline kỹ thuật
- **Product Contract v1:** Chốt user segment (Band 4.5–6.5), core loop, glossary (`speaking_time`, `recording_duration`, `transcription_confidence`, `pronunciation_score`) và 4 nhãn bắt buộc trong `15_PRODUCT_CONTRACT_V1.md`.
- **API Spec Contract:** Cập nhật `03_API_SPEC.md` với đầy đủ Bearer token và semantics ownership.
- **Wording & Disclaimers:** Web UI đã bổ sung nhãn *Provisional Practice Estimate* và chính sách bảo mật audio 72h.
- **Cross-platform scripts:** Đồng bộ `scripts/bootstrap.ps1`, `scripts/check.ps1`, `scripts/test.ps1` tự động nhận diện cả `.venv` và `venv`.

### 2. Phase 1 — Security, ownership và privacy foundation
- **Data Model Ownership:** Thêm `owner_user_id` vào `ProfileModel`, `SessionModel`, `TurnModel`, `MistakeModel`, `DailyStatsModel`, và `AudioRecordingModel`.
- **Database Migrations:** Runner `001_owner_and_audio` và `002_resource_owner_columns` thực thi tự động và idempotent.
- **Principal vs Selector Boundary:** `get_current_principal_id()` xác thực chặt chẽ qua JWT Bearer token / API-key; `X-Profile-Id` chỉ đóng vai trò selector thuộc quyền sở hữu của principal.
- **Audio Limits & Safety:** Kiểm tra `MAX_AUDIO_BYTES` (413), `MAX_AUDIO_DURATION_MS`, content-type whitelist.
- **Audio Lifecycle & Cleanup:** 
  - `reset-all` dọn sạch cả bản ghi DB và file vật lý trên đĩa.
  - `delete_profile` tự động thu dọn sạch toàn bộ sessions, turns, mistakes, progress và các file audio liên quan của profile đó trên đĩa.
  - Background task trong `lifespan` chạy định kỳ dọn dẹp các file audio vượt quá hạn retention (72h).
- **Frontend XSS Hygiene:** Thêm hàm `escapeHtml` khử mã độc chèn trong profile name và correction items trong `app.js`.
- **Production Guard:** Chặn khởi động server production nếu cấu hình secret/CORS không an toàn.

## Validation & Test Results

- Toàn bộ 28 bài test (bao gồm IDOR profiles, IDOR sessions, IDOR mistakes, reset audio cleanup, delete profile audio cleanup) chạy qua sạch sẽ 100%:
  ```text
  28 passed, 1 warning in 5.22s
  ```
- Lệnh kiểm tra tĩnh cú pháp JavaScript `node -c backend/web/app.js` đạt 0 lỗi.
- `scripts/check.ps1` biên dịch và chạy test thành công.

## Trạng thái Phase 0 & Phase 1
- **Status:** **COMPLETED & CLOSED** theo đúng tiêu chuẩn *Definition of Done*.
- **Sẵn sàng chuyển sang:** Phase 2 (Core conversation reliability & idempotency).
