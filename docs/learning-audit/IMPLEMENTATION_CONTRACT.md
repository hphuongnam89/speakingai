# Canonical implementation contracts — phase 0–1

## Bổ sung Phase 2–3 (07/11/2026)

Runtime v0.2 bổ sung `GET /learning/media/{lesson_id}/{version}/{step_id}` (auth, Range, checksum), `POST /learning/attempts/{id}/exposure` (transcript/replay), `POST /learning/attempts/{id}/speaking-session` (idempotent bridge), `POST /learning/attempts/{id}/feedback` (objective-only, source/quote verified), `GET /learning/reviews`, `POST /learning/reviews/{id}/reschedule`, `GET /learning/today?minutes=10&preview=true`. Planner/competency payload nằm trong Today. Chi tiết bằng chứng/giới hạn ở `../learning-handoffs/2026-11-07-phase-2-3.md`; các đoạn dưới giữ lại mô tả baseline 0–1.

DraftUpdate thêm item_id/evidence optional; SubmitRequest thêm evidence/turn_id optional. Observation lưu learner text, source modality/turn, selected evidence, policy. API không nhận mastery/grade từ client. Content version 0.1 vẫn đọc được; catalog mặc định dùng pack 0.2. Review mới dùng item_id nội bộ `__competency__` với unique owner/profile/lesson/version; same-item retry không là retention. Auto-created review table additive, migration marker 010. Original/Self-repair giữ observation riêng.

Source schemas: `backend/app/schemas/learning.py`. Các JSON Schema trong gói V2 là tài liệu thiết kế; runtime dùng Pydantic strict extra-forbid. Content thực ở `backend/content/learning` và manifest checksums.

## API đã có

| Endpoint | Contract |
|---|---|
| POST /auth/login, /auth/register | API token cũ; browser opt-in cookie bằng header, Origin cùng host |
| GET /auth/session; POST /auth/logout | session status; logout xóa cookie, token API cũ giữ expiry riêng |
| GET /models; POST /models/select | installed_models/selected_model, selection theo profile, không download |
| GET /learning/units | Catalog released; preview=true chỉ dev/testing |
| GET /learning/lessons/{id}?version=... | Chỉ learner-safe steps/items, không key/hints |
| POST /learning/attempts | lesson_id/version/request_id; profile từ header+owner context |
| GET /learning/attempts; GET /learning/attempts/{id} | History/resume đúng owner+profile |
| PATCH /learning/attempts/{id} | step_id/draft/expected_revision; stale →409; tổng draft bị giới hạn |
| POST /learning/attempts/{id}/submit | request_id/step_id/item_id/text; unknown item→422; idempotent |
| POST /learning/attempts/{id}/hints | Server ghi hint level/exposure, retry không tăng mức lần hai |
| POST /learning/attempts/{id}/tutor | Teaching/self-repair context, JSON/source refs validated, local-only |
| GET /learning/export | Export attempts/observations của hồ sơ hiện tại; có giới hạn thông báo rõ |

Những route daily planner/competency/mastery/review trong kế hoạch chưa thuộc phase này. Submit bài nói/viết lưu `unknown`, không invent score; Tutor có thể hỗ trợ học nhưng không tự nâng level.

## Persistence

`learning_lessons` PK(id,version), checksum immutable; `learning_attempts` owner/profile, lesson version, draft(s), revision, create key unique; `learning_events` action/request hash/result unique theo attempt; `learning_observations` learner response + result/assistance/content/competency/policy refs.

Create_all bổ sung tables; migration marker 009 và additive columns hỗ trợ nâng bản nền tảng. Profile delete/reset-all xóa learning data theo owner/profile. Export không lộ key của item chưa nộp.

## Concurrency và grading giới hạn

CAS serialize mutation trong attempt, unique event chống replay. Xung đột trả409 và giữ draft; client serializes autosave/navigation/actions. Cùng request key nhưng body khác →409. Re-submit cùng item với key mới được ghi assisted, không biến đáp án đã lộ thành independent.

Marking foundation chỉ chấp nhận answer text normalization đơn giản ở những item có answer xác định; normalizer chuyên biệt donor là T08/T09. Productive rubric/microphone/audio-render chưa được tích hợp. UI phải ghi rõ giới hạn này.

## Tutor structured outputs

Ollama format nhận JSON schema từ `TutorFeedback.model_json_schema()` theo tài liệu chính thức: https://docs.ollama.com/capabilities/structured-outputs . Validate lại ở server; unknown source/malformed response không trả thành feedback thành công. Không dùng format constraint thay cho content review.
