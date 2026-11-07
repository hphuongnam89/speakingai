# ADR — Learning foundation và ranh giới tin cậy

Trạng thái: thực thi phase 0–1 theo yêu cầu người dùng ngày 06/11/2026. Mở rộng hợp đồng sản phẩm Speaking v1 bằng Learning V2, giữ API/history Speaking.

## Quyết định

1. Giữ FastAPI/SQLAlchemy/migration runner và identity hiện có. Một database runtime; bảng learning thêm tăng dần.
2. React web shell được build vào backend image; root và /learn phục vụ UI, /api/v1/info giữ JSON, /speaking giữ trang Speaking cũ.
3. Web login opt-in bằng `X-Browser-Session: true`, reuse user token ký sẵn có nhưng cookie HttpOnly/SameSite=Strict. Bearer API/Android không đổi. Unsafe cookie requests bắt buộc same-origin; logout không hồi sinh session; expired session trả401.
4. Không tắt API key hoặc nhúng admin key vào JS. Sign-up vẫn chưa có xác minh email/reset password như baseline; không quảng bá là production identity hoàn chỉnh.
5. Model selection lưu theo profile, kiểm tên thực từ Ollama. Host override bỏ model-init dependency, không tự pull.
6. Content server giữ keys/hints; learner payload allowlist. Draft preview chỉ development/testing và account/profile hợp lệ; production không bật preview qua query flag.
7. Attempt autosave revision compare-and-swap; request idempotency unique; transaction rollback khi conflict. Hint/source/exposure do server xác nhận. Không tin client tự báo correct/mastered/owner.
8. Tutor chỉ local, lấy teaching steps + tối đa ba bài đã nộp của đúng attempt; không đưa independent/transfer keys hoặc hồ sơ khác vào prompt. Prompt không là security boundary: API chặn Tutor trực tiếp ở independent/transfer/review và output phải qua schema/source-ID validation.
9. Feedback không tự thăng mastery. Content human review và calibration vẫn có gate riêng.

## Threat model tối thiểu

| Boundary/asset | Abuse case | Kiểm soát |
|---|---|---|
| Browser → API/session | CSRF, expired cookie | strict same-origin writes, HttpOnly cookie, expiry, không token localStorage |
| Profile/attempt → DB | Đổi ID lấy bài người khác | owner/profile-scoped queries, 404, tests A/B |
| Submit/hint → evidence | Retry làm tăng evidence, tự khai đã đúng | request hash + DB unique/CAS, strict Pydantic, server grading |
| Content → learner/Tutor | Lộ answer key/holdout, prompt injection | learner allowlist, teaching-only context, draft gates |
| Model → UI | JSON giả, source bịa, HTML/script | schema/source validation, React escaping, không tools/SQL/HTML từ model |
| Startup/build → learner data | Copy DB/secret vào image, migration hỏng | .dockerignore theo đúng runtime data, SQLite backup/restore test |

## Giới hạn được giữ rõ

Không thể chứng minh Tutor không bao giờ hallucinate bằng prompt/schema. Schema bảo vệ hình dạng/source ref, không chứng nhận mọi nhận xét đúng; draft/review safeguards vẫn cần. Đây là app local pilot, không cấu hình deploy công khai.
