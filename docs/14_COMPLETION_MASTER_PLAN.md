# IELTS Speaking AI Coach — Completion Master Plan

**Phiên bản:** 1.0  
**Ngày:** 2026-10-27  
**Mục tiêu:** Chuyển dự án từ MVP nhiều tính năng thành sản phẩm luyện IELTS Speaking đáng tin cậy cho local pilot, sau đó mới mở rộng production.

---

## 1. Tuyên bố chiến lược

Dự án không nên tiếp tục theo hướng “thêm tính năng càng nhanh càng tốt”. Thứ tự đúng là:

```text
Reproducible → Secure → Reliable → Learnable → IELTS-correct → Measurable → Scalable
```

Sản phẩm v1 nên được định vị là:

> **AI IELTS Speaking Practice Coach cho người học Band 4.5–6.5, tập trung vào phản xạ nói, mở rộng câu trả lời, sửa lỗi lặp lại và duy trì thói quen.**

Không định vị v1 là giám khảo IELTS chính thức, không hứa hẹn band chính xác, và không gọi transcript confidence là pronunciation score.

---

## 2. Baseline hiện tại

### Đã có

- Web practice room và Android client.
- Daily practice, free talk, Fix My English, IELTS Part 1/2/3 ở mức cơ bản.
- Profile, placement test, roadmap, streak, progress, mistake notebook.
- FastAPI, SQLite/PostgreSQL configuration, repository layer, LLM provider router.
- Ollama local và DeepSeek adapter.
- Whisper STT, audio metrics, pronunciation dictionary và sidecar thử nghiệm.
- Docker, reverse proxy, healthcheck và CI backend/Android debug build.

### Chưa đạt release production

- Ownership profile/session chưa được enforce đúng; `X-Profile-Id` có thể được client tự gửi.
- Frontend có dynamic `innerHTML` với dữ liệu profile/AI chưa escape.
- Audio chưa có byte/duration limit, quota, retention và cleanup đầy đủ.
- Reset database chưa xóa audio files.
- Full Mock chưa phải flow Part 1 → Part 2 → Part 3 hoàn chỉnh.
- Part 2 chưa được backend kiểm soát 60 giây chuẩn bị/120 giây nói.
- IELTS evaluation thiếu pronunciation criterion và còn dùng duration hard-code.
- Placement chỉ là quick diagnostic nhưng UI dễ khiến người học hiểu là band chính xác.
- Progress có nhiều proxy/hard-code chưa phản ánh speaking time thật.
- Test local không chạy được vì virtualenv trỏ tới Python executable bị Access Denied.
- Chưa có frontend E2E, accessibility test, security regression hoặc load test.

---

## 3. Mục tiêu release theo tầng

### Release A — Internal Engineering Baseline

Có thể build, test và reset dữ liệu một cách lặp lại trên máy developer/CI. Chưa cần đẹp, chưa cần thêm feature.

### Release B — Local Pilot

3–5 người học có thể hoàn thành core learning loop mà không cần facilitator takeover. Dữ liệu test được kiểm soát, band được trình bày là estimate, audio có consent và cleanup.

### Release C — Trusted IELTS Practice Beta

IELTS flow đúng hơn, feedback theo band/skill, progress phản ánh dữ liệu thật, có calibration với giáo viên và regression test ổn định.

### Release D — Public Production

Có tenant isolation, retention/privacy, observability, migration, backup, release Android ký, rate limiting phân tán và quy trình incident/recovery.

---

## 4. Definition of Done chung cho mọi phase

Một phase chỉ được đóng khi có đủ:

1. Code và test được commit trong branch riêng.
2. API/schema/docs được cập nhật đồng bộ.
3. Test unit/integration liên quan chạy pass.
4. Có test cho happy path và failure path.
5. README hoặc runbook được cập nhật nếu thay đổi setup.
6. Có manual verification cho web/Android nếu phase ảnh hưởng UI.
7. Báo cáo cuối phase gồm: files changed, feature, tests, build, remaining issues, next task.
8. Không có secret, recording cá nhân hoặc runtime database nằm trong artifact release.

Nếu build/test hoặc API contract hỏng, không được chuyển phase tiếp theo.

---

# Phase 0 — Product contract và baseline kỹ thuật

**Ưu tiên:** P0  
**Thời lượng mục tiêu:** 2–3 ngày  
**Phụ thuộc:** Không có

## Mục tiêu

Chốt v1 là công cụ luyện IELTS Speaking hằng ngày, không mở rộng thêm mode trước khi core loop đáng tin cậy.

## Công việc

- Chốt user segment chính: Band 4.5–6.5.
- Chốt core loop: `Start → Speak → Transcript → Focus feedback → Repeat → Review progress`.
- Tách product labels:
  - Practice feedback.
  - Quick diagnostic.
  - Provisional transcript-based estimate.
  - Experimental pronunciation analysis.
- Viết API contract hiện hành bằng OpenAPI hoặc cập nhật `docs/03_API_SPEC.md` theo route thực tế.
- Chốt glossary: `speaking_time`, `recording_duration`, `transcription_confidence`, `pronunciation_score`.
- Ghi baseline metric hiện tại: latency, timeout, transcription success, duplicate turn, feedback parse failure.
- Sửa local environment để có thể tạo lại virtualenv từ đầu.
- Thêm script chuẩn như `scripts/bootstrap.ps1`, `scripts/test.ps1`, `scripts/check.ps1`.

## Deliverables

- Product brief v1.
- API contract v1.
- Baseline metric report.
- Local setup script.
- CI/local command parity.

## Acceptance criteria

- Developer mới có thể cài dependency và chạy healthcheck.
- Backend test command chạy được hoặc có lỗi môi trường được xử lý rõ.
- Web và Android không còn dùng wording khẳng định band/pronunciation quá mức.
- Không thêm feature mới ngoài backlog đã chốt.

---

# Phase 1 — Security, ownership và privacy foundation

**Ưu tiên:** P0  
**Thời lượng mục tiêu:** 5–7 ngày  
**Phụ thuộc:** Phase 0

## Mục tiêu

Đảm bảo user A không thể đọc, sửa, xóa dữ liệu của user/profile B và recording không tồn tại ngoài ý muốn.

## Công việc backend

- Thêm `owner_user_id` vào `profiles`.
- Liên kết sessions, turns, mistakes, progress và audio metadata với owner/profile.
- Migration bằng Alembic hoặc migration versioning tương đương; không phụ thuộc `create_all()` cho schema production.
- Viết helper `get_owned_profile()` và dùng thống nhất ở mọi endpoint.
- Không dùng `X-Profile-Id` hoặc query `profile_id` làm identity.
- Nếu vẫn hỗ trợ local multi-profile, coi profile selector là resource selector và kiểm tra ownership.
- Bảo vệ các endpoint:
  - profile list/get/create/update/delete/select;
  - reset-all;
  - placement evaluate/reset;
  - sessions/turns/mistakes/progress;
  - speech/transcribe.
- Thêm test IDOR cho user A/B.
- Không trả raw exception/provider detail cho client.

## Công việc audio/privacy

- Tạo `audio_recordings` metadata với owner, session, size, duration, content type, created_at, retention_at.
- Giới hạn upload bytes và duration.
- Validate decoded media, không tin filename/MIME từ client.
- Xóa file khi reset/delete nếu user không chọn giữ recording.
- Thêm retention cleanup job.
- Xác định rõ recording nào cần lưu và recording nào xóa sau transcription.
- Thêm privacy notice và consent state.

## Acceptance criteria

- IDOR test pass cho tất cả resource chính.
- Reset profile xóa cả DB record và audio liên quan.
- File vượt giới hạn bị từ chối trước khi inference.
- User có thể biết audio được lưu bao lâu và có cách xóa.
- Production config không chạy khi secret/CORS/rate limit không an toàn.

---

# Phase 2 — Core conversation reliability

**Ưu tiên:** P0  
**Thời lượng mục tiêu:** 4–6 ngày  
**Phụ thuộc:** Phase 1

## Mục tiêu

Biến một turn nói thành một transaction có trạng thái rõ, retry an toàn và không tạo dữ liệu trùng.

## Công việc

- Thiết kế turn state:

```text
created → uploading → transcribing → awaiting_feedback → completed
                                      ↘ failed/retryable
```

- Thêm `request_id`/idempotency key cho transcription và conversation response.
- Đảm bảo client retry sau timeout không tạo user turn hoặc assistant turn trùng.
- Tách timeout:
  - health/settings: ngắn;
  - STT: theo audio duration;
  - LLM: theo provider/model;
  - pronunciation assessor: riêng.
- Thêm error codes ổn định: `AUDIO_TOO_LARGE`, `STT_UNAVAILABLE`, `LLM_TIMEOUT`, `SESSION_NOT_FOUND`.
- Thêm server correlation ID và structured logging.
- Giới hạn request text, session ID, topic và correction level bằng schema.
- Đảm bảo conversation không gọi LLM nếu session đã finish.
- Cân nhắc transaction/outbox cho assistant response và progress event.

## Frontend/Android

- Hiển thị trạng thái: recording, uploading, transcribing, thinking, saving, retry.
- Disable control đúng lúc.
- Retry có thể tiếp tục từ state hiện tại.
- Không dùng `alert()` làm cơ chế lỗi chính.

## Acceptance criteria

- Retry cùng request ID không tạo duplicate.
- Timeout sau khi backend commit không làm mất transcript.
- Mọi lỗi đều có hành động phục hồi rõ.
- Có integration tests cho text flow, audio flow và provider timeout.

---

# Phase 3 — Frontend quality và accessibility

**Ưu tiên:** P0/P1  
**Thời lượng mục tiêu:** 4–6 ngày  
**Phụ thuộc:** Phase 2

## Mục tiêu

Làm cho web client an toàn, dễ hiểu và dùng được khi người học đang nói thay vì nhìn màn hình liên tục.

## Công việc

- Loại bỏ `innerHTML` có dữ liệu động tại các vị trí profile, roadmap, correction và AI output.
- Dùng `textContent`, DOM nodes hoặc sanitizer allowlist.
- Tách `app.js` thành module:
  - `api.js`;
  - `session.js`;
  - `recording.js`;
  - `profiles.js`;
  - `placement.js`;
  - `render.js`;
  - `progress.js`.
- Thêm focus trap, Escape close và restore focus cho modal.
- Kiểm tra keyboard navigation và screen reader labels.
- Kiểm tra contrast, font-size và color-only states.
- Thêm auto-scroll/scroll-to-latest cho conversation.
- Thêm empty/loading/error states cho mọi widget.
- Hiển thị disclaimer score ngay cạnh kết quả.
- Làm responsive tốt cho màn hình nhỏ và landscape mobile.
- Thêm ESLint/formatter hoặc static checks tối thiểu.

## Acceptance criteria

- XSS payload trong profile name, correction và roadmap chỉ hiển thị như text.
- User hoàn thành session bằng keyboard và microphone flow.
- Modal không làm mất focus.
- Không có trạng thái “đang xử lý” vô hạn nếu request fail.
- Frontend E2E test pass cho start session → send answer → correction → finish.

---

# Phase 4 — Audio/STT pipeline và pronunciation boundary

**Ưu tiên:** P0/P1  
**Thời lượng mục tiêu:** 5–7 ngày  
**Phụ thuộc:** Phase 1–3

## Mục tiêu

Đảm bảo transcript usable và phân biệt rõ recognition confidence với pronunciation assessment.

## Công việc

- Chuẩn hóa audio input/output và decoder validation.
- Preflight microphone permission và device capability.
- Giới hạn duration để tránh file quá dài.
- Ghi nhận:
  - total duration;
  - speaking duration;
  - pause duration;
  - long pause count;
  - filler count;
  - word count;
  - WPM.
- Phân biệt:
  - `transcription_confidence`;
  - `pronunciation_score`;
  - `pronunciation_not_assessed`.
- Nếu sidecar không sẵn sàng, UI không được hiển thị score giả.
- Pronunciation feedback tập trung vào intelligibility, stress và practice tips.
- Có fallback text input rõ ràng.
- Tạo audio fixtures không chứa dữ liệu cá nhân để test.

## Acceptance criteria

- Recording 20–40 giây được transcribe ổn định.
- File lỗi/không đúng codec bị từ chối có lý do.
- Permission denied có hướng dẫn recovery.
- Reset/delete dọn sạch audio.
- Pronunciation score vẫn null khi không có acoustic assessor.

---

# Phase 5 — IELTS engine đúng format

**Ưu tiên:** P0  
**Thời lượng mục tiêu:** 7–10 ngày  
**Phụ thuộc:** Phase 2 và Phase 4

## Mục tiêu

Chuyển IELTS practice từ “chat có chủ đề” thành một flow mô phỏng có state, timing và feedback đúng bản chất bài thi.

## 5.1. Part 1

- 4–5 câu hỏi theo chủ đề.
- Không sửa lỗi trong lúc interview.
- Follow-up ngắn nhưng không biến thành tutoring.
- Có coverage đủ lớn và chống lặp đề.
- Sau phần thi mới hiển thị feedback.

## 5.2. Part 2

- Backend state bắt buộc:

```text
PREPARATION_60S → SPEAKING_UP_TO_120S → COMPLETED
```

- Có cue card, 4 bullet points và planning note.
- Không correction trong 2 phút nói.
- Ghi speaking duration thật.
- Cảnh báo nếu nói quá ngắn.
- Có auto-stop hoặc server validation khi vượt thời lượng.

## 5.3. Part 3

- 4–5 câu hỏi discussion.
- Chuyển từ personal topic sang abstract/general discussion.
- Có question types: opinion, cause/effect, compare, future, problem/solution.
- Không chỉ hỏi ngẫu nhiên; cần blueprint theo topic.

## 5.4. Full Mock

Implement state machine:

```text
PART_1 → PART_2_PREP → PART_2_SPEAK → PART_3 → EVALUATION
```

- Mục tiêu 11–14 phút.
- Có transition examiner tự nhiên.
- Không cho finish sớm nếu chưa đủ phần, trừ explicit user exit.
- Lưu event/timing từng part.

## Acceptance criteria

- Có thể hoàn thành Part 1, Part 2, Part 3 độc lập.
- Full Mock thực sự chạy đủ ba phần.
- Part 2 kiểm soát được 60/120 giây ở backend.
- Feedback chỉ xuất hiện sau phần tương ứng hoàn tất.
- Không gọi Full Mock nếu flow không có đủ cue card và Part 3.

---

# Phase 6 — IELTS pedagogy và AI tutor

**Ưu tiên:** P1  
**Thời lượng mục tiêu:** 7–10 ngày  
**Phụ thuộc:** Phase 5

## Mục tiêu

Đảm bảo mỗi session không chỉ đưa ra correction mà còn tạo ra hành vi học có thể đo được.

## Công việc

- Band-specific feedback cho Band 4.5–5.0, 5.5–6.0, 6.5–7.0.
- Thêm `One Focus per Session`.
- Correction schema:

```json
{
  "error_type": "grammar",
  "subtype": "past_tense",
  "severity": "important",
  "original": "...",
  "corrected": "...",
  "explanation": "...",
  "practice_prompt": "..."
}
```

- Mỗi correction quan trọng phải có practice prompt.
- Say-it-again cần kiểm tra câu người học nói lại, không chỉ phát TTS.
- Dạy framework:
  - Part 1: answer → reason → example;
  - Part 2: opening → events → feeling → why memorable;
  - Part 3: opinion → reason → example → contrast/conclusion.
- Tạo sample answers theo Band 5/6/7.
- Tránh sửa mọi lỗi trong một lượt nói.
- Thêm self-assessment cuối session.
- Bảo vệ prompt khỏi learner text chèn chỉ thị giả mạo.

## Acceptance criteria

- User có thể hiểu vì sao câu sai và thực hành ngay.
- Mỗi session có tối đa 1–3 focus errors phù hợp level.
- Hệ thống không sửa pronunciation dựa trên transcript.
- Feedback được phân loại đúng error type trong bộ test.
- Có test cho output LLM sai format và correction fallback.

---

# Phase 7 — Progress, mistake notebook và adaptive learning

**Ưu tiên:** P1  
**Thời lượng mục tiêu:** 5–7 ngày  
**Phụ thuộc:** Phase 4–6

## Mục tiêu

Biến dữ liệu học thành hành động ôn tập, không chỉ là dashboard.

## Công việc

- Tách:
  - actual speaking time;
  - audio duration;
  - typing practice time;
  - session duration.
- Bỏ hard-code IELTS speaking minutes.
- Ghi scoring metadata và sample count.
- Hiển thị latest estimate, recent average và confidence range.
- Mistake notebook thêm:
  - error type/subtype;
  - occurrence count;
  - last seen;
  - successful reuse count;
  - next review date;
  - example sentence;
  - mastery state.
- Thêm spaced review và mini quiz.
- Adaptive plan cache theo ngày.
- Plan phải sinh từ top weaknesses có bằng chứng, không chỉ từ target band.
- Mỗi ngày trả về một next best action rõ ràng.

## Acceptance criteria

- Progress phản ánh thời lượng audio thật.
- Một lỗi chỉ được xem là resolved sau khi learner dùng đúng nhiều lần hoặc hoàn thành review.
- Adaptive plan thay đổi theo dữ liệu thật.
- Không cập nhật band quá dễ dàng chỉ từ một session.

---

# Phase 8 — Scoring calibration và quality assurance

**Ưu tiên:** P1  
**Thời lượng mục tiêu:** 1–2 tuần  
**Phụ thuộc:** Phase 5–7

## Mục tiêu

Đo độ tin cậy của AI trước khi dùng score làm thông tin chính trên product.

## Công việc

- Tạo dataset consented gồm audio/transcript đã được giáo viên IELTS chấm.
- Mỗi mẫu có bốn tiêu chí:
  - Fluency & Coherence;
  - Lexical Resource;
  - Grammatical Range & Accuracy;
  - Pronunciation.
- Chấm bởi ít nhất hai rater khi có thể.
- So sánh AI với human score.
- Tính sai lệch theo criterion và level.
- Lưu prompt/model/scoring version.
- Không trả overall IELTS score nếu pronunciation chưa được đánh giá; hoặc hiển thị provisional score rõ ràng.
- Thêm feedback flag: useful, incorrect, too harsh, too vague.
- Tạo regression set cho prompt changes.

## Acceptance criteria

- Có báo cáo calibration trước khi publicize score.
- Có ngưỡng sai lệch chấp nhận được do academic owner quyết định.
- Prompt/model change phải chạy regression set.
- Score UI hiển thị confidence và limitation.

---

# Phase 9 — Android parity và release quality

**Ưu tiên:** P1  
**Thời lượng mục tiêu:** 5–7 ngày  
**Phụ thuộc:** Phase 1–8

## Công việc

- Đồng bộ Android models với API contract mới.
- Gửi profile selector đúng ownership semantics.
- Test 401, logout, token expiry và invalid token.
- Test audio permission, background app, rotation/process death.
- Test emulator và thiết bị thật.
- Thêm release build vào CI, không chỉ debug APK.
- Kiểm tra minify/proguard, app signing và crash reporting privacy.
- Không log transcript/audio/token trong release.
- Xác nhận cleartext chỉ bật ở debug.
- Cải thiện setup URL: emulator, LAN device, production HTTPS.

## Acceptance criteria

- Android hoàn thành core loop không cần web.
- Release build assemble được với signing secrets ngoài repository.
- 401/timeout/permission errors có recovery.
- Không có API key/provider secret trong APK.

---

# Phase 10 — Pilot có kiểm soát

**Ưu tiên:** P0 trước public  
**Thời lượng mục tiêu:** 5–7 ngày quan sát + 2–3 ngày tổng hợp  
**Phụ thuộc:** Phase 1–9

## Protocol

- 3–5 learners, dùng test account/data.
- Có consent trước recording.
- Không coach learner trong khi thao tác.
- Mỗi bước ghi: completed without help, completed with help, blocked.
- Ghi nguyên văn câu learner không hiểu.
- Thu feedback về:
  - next action có rõ không;
  - correction có hữu ích không;
  - score có tạo cảm giác quá chắc chắn không;
  - có muốn quay lại không.

## Success criteria

- Mọi learner kết nối, record, xem feedback và tìm progress không cần takeover.
- Không recording nào mất im lặng.
- Permission denied có recovery.
- Learner hiểu band là estimate.
- Các feedback bị đánh dấu sai được review trước phase tiếp.
- Session completion mục tiêu tối thiểu 70%.
- Audio transcription success mục tiêu tối thiểu 90% trên test devices.

---

# Phase 11 — Production hardening

**Ưu tiên:** P0/P1  
**Thời lượng mục tiêu:** 1–2 tuần  
**Phụ thuộc:** Pilot pass

## Công việc

- PostgreSQL migration và backup/restore drill.
- Redis/distributed rate limit nếu chạy nhiều instance.
- Job queue/concurrency control cho Whisper và pronunciation.
- Observability:
  - latency p50/p95;
  - STT/LLM error rate;
  - queue depth;
  - memory/CPU;
  - storage growth;
  - request correlation.
- Generic client errors, detailed server logs.
- TLS-only production, explicit CORS, trusted proxy configuration.
- Security headers và CSP phù hợp với frontend.
- Secret rotation và incident runbook.
- Data export/delete verification.
- Load test và failover test.
- Dependency update policy và vulnerability scan.

## Go-live gate

Chỉ public khi:

- P0 security/privacy không còn mở.
- IDOR/XSS/audio deletion regression pass.
- CI backend test, frontend test và Android release build pass.
- Backup restore đã thực hiện thành công.
- Có monitoring và owner xử lý alert.
- Có privacy/retention notice.
- Có calibration report hoặc score được giới hạn rõ là provisional.

---

## 5. Dependency map

```text
Phase 0: Baseline/product contract
    ↓
Phase 1: Ownership/privacy/security
    ↓
Phase 2: Conversation reliability
    ↓
Phase 3: Frontend quality
    ↓
Phase 4: Audio/STT boundary
    ↓
Phase 5: IELTS state machine
    ↓
Phase 6: Pedagogy/tutor
    ↓
Phase 7: Progress/mistakes
    ↓
Phase 8: Calibration/QA
    ↓
Phase 9: Android parity
    ↓
Phase 10: Pilot
    ↓
Phase 11: Production hardening
```

Không nên triển khai Phase 8 scoring calibration trước Phase 5 IELTS flow và Phase 4 audio metrics. Không nên public trước Phase 1 security/privacy dù các feature IELTS đã hoàn thành.

---

## 6. Backlog ưu tiên theo impact

| ID | Hạng mục | Priority | Impact | Done khi |
|---|---|---:|---:|---|
| SEC-01 | Profile ownership | P0 | Rất cao | IDOR tests pass |
| SEC-02 | Audio deletion/retention | P0 | Rất cao | Reset/delete dọn file |
| SEC-03 | Upload limits | P0 | Cao | Abuse/size tests pass |
| SEC-04 | Frontend XSS removal | P0 | Cao | Dynamic data render an toàn |
| REL-01 | Idempotent turn flow | P0 | Cao | Retry không duplicate |
| REL-02 | Error codes/recovery | P1 | Cao | UI có hướng dẫn phục hồi |
| IELTS-01 | Part 2 backend timer | P0 | Rất cao | 60/120s enforced |
| IELTS-02 | Full Mock state machine | P0 | Rất cao | Đủ Part 1/2/3 |
| IELTS-03 | Pronunciation limitation UI | P0 | Cao | Không overclaim |
| EDU-01 | One focus per session | P1 | Cao | 1–3 target errors |
| EDU-02 | Band-specific feedback | P1 | Cao | Có rubric theo level |
| EDU-03 | Practice prompt | P1 | Cao | Learner có cơ hội dùng lại |
| DATA-01 | Actual speaking time | P1 | Cao | Không hard-code |
| DATA-02 | Spaced mistake review | P1 | Cao | Có next review/mastery |
| QA-01 | Human calibration dataset | P1 | Rất cao | Có sai lệch theo criterion |
| QA-02 | Frontend E2E/accessibility | P1 | Cao | Happy/failure paths pass |
| OPS-01 | Migration/backup/restore | P1 | Rất cao | Restore drill pass |

---

## 7. Metrics cần theo dõi sau mỗi release

### Product

- Profile creation → first completed turn.
- First turn → second session within 7 days.
- Session completion rate.
- Say-it-again completion rate.
- Mistake reuse success rate.
- D1/D7/W4 retention.

### Academic

- Feedback judged useful.
- Feedback judged incorrect.
- Recurring error reduction.
- Average answer duration.
- Part 2 completion duration.
- Part 3 answer development quality.
- Human vs AI score deviation.

### Technical

- STT success rate.
- LLM p50/p95 latency.
- Timeout/503 rate.
- Duplicate turn rate.
- Audio storage growth.
- CPU/RAM during Whisper.
- 4xx/5xx by endpoint.
- Android crash-free sessions.

---

## 8. Những việc chưa được làm sớm

Không ưu tiên các hạng mục sau trước khi P0/P1 hoàn thành:

- thêm nhiều model selector;
- thêm social/community;
- thanh toán;
- iOS;
- advanced phoneme scoring;
- thêm hàng chục mode luyện tập;
- dashboard quá nhiều biểu đồ;
- marketing claim Band 9.0;
- cloud scale lớn khi local flow chưa ổn định.

Mỗi feature mới phải trả lời được một trong ba câu hỏi:

1. Có giúp learner nói tốt hơn không?
2. Có giúp learner quay lại học đều hơn không?
3. Có giúp hệ thống đo tiến bộ đáng tin hơn không?

Nếu không, đưa vào backlog sau v1.

---

## 9. Kết luận

Dự án có nền tảng tốt và đủ tiềm năng để trở thành một sản phẩm luyện IELTS Speaking có giá trị. Nhưng bước tiếp theo không phải là mở rộng thêm feature. Bước tiếp theo là hoàn thiện tính đúng đắn của core loop:

```text
Người học nói thật
→ hệ thống ghi nhận đúng
→ AI phản hồi vừa đủ và đúng trọng tâm
→ người học thực hành lại
→ lỗi được theo dõi qua thời gian
→ progress phản ánh dữ liệu thật
```

Nếu hoàn thành theo thứ tự trên, dự án sẽ chuyển từ **MVP nhiều chức năng** thành **learning product có thể kiểm chứng, có trách nhiệm và sẵn sàng mở rộng**.
