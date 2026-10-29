# Audit toàn diện IELTS Speaking AI Coach

**Ngày audit:** 2026-10-27  
**Vai trò đánh giá:** Product Manager + Full-stack Engineer  
**Phạm vi:** Product proposition, UX/UI web, Android client, FastAPI backend, auth, tenant isolation, database, audio/STT, LLM routing, Docker/CI, testing và production readiness.

## 1. Executive summary

Đây là một MVP có độ hoàn thiện chức năng khá tốt: đã có practice room, hồ sơ học viên, placement test, conversation coach, IELTS flow, mistake notebook, progress/adaptive plan, STT Whisper, pronunciation caveat và Android client. Kiến trúc tách lớp tương đối rõ: API → repository → service/provider, có Docker, CI và một số guard production.

Tuy nhiên, sản phẩm hiện phù hợp nhất với **local pilot / single-machine beta**, chưa phù hợp để mở public production. Rủi ro lớn nhất không nằm ở thiếu tính năng mà ở **ranh giới dữ liệu và độ tin cậy**:

1. JWT đã tồn tại nhưng profile vẫn được chọn bằng header `X-Profile-Id` do client tự gửi; nhiều profile endpoint không kiểm tra ownership.
2. Frontend render dữ liệu profile và AI bằng `innerHTML` chưa escape, tạo bề mặt XSS.
3. Audio được lưu lâu dài trong filesystem; `reset-all` chỉ xóa record database, không xóa audio.
4. Upload chưa có giới hạn byte/stream, MIME sniffing hay quota; một request có thể kích hoạt lưu file, Whisper và pronunciation sidecar tốn CPU/RAM.
5. Scoring IELTS hiện là ước lượng từ transcript/LLM; progress còn dùng nhiều số xấp xỉ/hard-code. Nếu không làm rõ UX và calibration, người học có thể hiểu nhầm là điểm thật.
6. Test suite không chạy được trên máy hiện tại vì virtualenv trỏ tới Python executable bị Access Denied. CI có test nhưng local reproducibility đang hỏng.

**Đánh giá tổng thể:** 6.5/10 cho MVP local pilot; 4.5/10 cho production public hiện tại.

## 2. Đánh giá product manager

### 2.1. Giá trị sản phẩm và định vị

**Điểm mạnh**

- Problem rõ: người học cần luyện nói thường xuyên, nhận feedback ngay và theo dõi tiến bộ.
- Khác biệt có tiềm năng: local AI/Ollama, dữ liệu riêng tư trên máy, feedback theo lịch sử lỗi, placement và roadmap cá nhân hóa.
- Core learning loop đã hiện diện: chọn chủ đề → nói/gõ → transcript → AI feedback → say-it-again → lưu lỗi/progress.
- IELTS mode, Part 2 cue card, band estimate và pronunciation caveat giúp sản phẩm có hướng chuyên biệt hơn chatbot hội thoại chung.
- Nội dung UI tạo cảm giác nhẹ nhàng, không phán xét; điều này phù hợp với hành vi luyện nói của người học thiếu tự tin.

**Điểm yếu**

- Định vị đang kéo về nhiều hướng: daily practice, IELTS coach, free talk, Fix My English, local AI platform, pronunciation engine. MVP nên chọn một “wedge” chính thay vì truyền thông đồng thời mọi thứ.
- Local AI là lợi thế riêng tư nhưng cũng là friction lớn: người dùng phải cài Ollama/model nặng, chờ model load và chấp nhận latency dài. Đây là rào cản activation, không chỉ là vấn đề kỹ thuật.
- “Band 9.0 chuyên sâu”, “chuẩn IELTS”, “nhận diện siêu chuẩn xác” trong UI dễ tạo kỳ vọng vượt quá khả năng hiện tại, trong khi tài liệu đã thừa nhận score/pronunciation chỉ là practice estimate.
- Chưa thấy cơ chế đo feedback quality, learner correction acceptance, retention hoặc learning outcome. Hiện sản phẩm có nhiều feature nhưng chưa có bằng chứng feature nào tạo tiến bộ thực.

### 2.2. Funnel và trải nghiệm người dùng

**Activation hiện tại**

- Người dùng có thể vào web và tạo profile, nhưng trải nghiệm phụ thuộc backend + Ollama + model local.
- Placement test được đưa lên khá sớm, phù hợp cho personalization, nhưng cần cho phép “skip and try first” để giảm friction.
- Trạng thái AI/Whisper được hiển thị, nhưng trường hợp model chưa sẵn sàng vẫn có thể khiến user không biết phải làm gì tiếp theo ngoài retry.

**Core session**

- Luồng text input có tính khả dụng tốt và có fallback khi microphone không dùng được.
- Microphone/recording, transcript, correction và say-it-again là các điểm giá trị cao nhất nên được ưu tiên ổn định hơn các widget roadmap.
- Cần trạng thái rõ cho: uploading, transcribing, evaluating, AI timeout, retry không tạo duplicate turn, mất mạng, permission denied và session expired.
- Web có `max-height: 450px` cho conversation; với session dài, người dùng dễ mất context nếu không có pagination/auto-scroll/summary.

**Retention**

- Streak, daily minutes, roadmap và mistake notebook là nền tảng retention tốt.
- Nên thêm “next best action” duy nhất sau mỗi turn/session, thay vì nhiều CTA cạnh tranh.
- Adaptive plan nên được cache theo ngày; hiện mỗi lần gọi có thể kích hoạt LLM mới, làm tăng latency/cost và cho kết quả không ổn định.

### 2.3. MVP scope đề xuất

**MVP nên chốt:** Daily speaking + IELTS Part 2 + feedback có cấu trúc + mistake notebook + progress cơ bản.

**Hoãn hoặc đặt beta:** full mock orchestration, pronunciation scoring acoustic, nhiều model selector, roadmap “AI tính lại”, cloud fallback tự động.

Lý do: độ tin cậy của transcript/feedback và recovery quan trọng hơn số lượng mode. Với một sản phẩm giáo dục, feedback sai hoặc quá tự tin gây hại niềm tin nhiều hơn việc thiếu một tính năng.

### 2.4. KPI product nên bổ sung

- Activation: tỷ lệ tạo profile → hoàn tất turn đầu tiên trong 5 phút.
- Core loop completion: tỷ lệ turn có transcript + feedback + say-it-again.
- Audio success rate: recording → transcription thành công; phân theo thiết bị/model.
- Feedback trust: tỷ lệ feedback bị learner đánh dấu “không đúng/không hữu ích”.
- Retention: D1/D7/W4 active learners, sessions/learner/week.
- Learning outcome: lỗi lặp lại giảm theo tuần, WPM và speaking duration hợp lệ.
- Reliability: p50/p95 latency của STT, LLM; timeout/503 rate; duplicate turn rate.
- Cost/resource: CPU/RAM/model load time nếu bật cloud fallback hoặc pronunciation sidecar.

## 3. Đánh giá frontend

### 3.1. Điểm tốt

- HTML/CSS có hierarchy rõ, responsive breakpoint cơ bản và giao diện nhất quán.
- Có `aria-live`, label cho form, `role="alert"`, `role="status"`, focus styling và các nút semantic cơ bản.
- JS dùng DOM API ở nhiều nơi, tránh framework overhead cho local MVP; state tập trung giúp đọc flow dễ hơn.
- Có timeout request, error banner và fallback text input.
- Android có credential store mã hóa bằng Android Keystore; debug/release cleartext được phân biệt.

### 3.2. Vấn đề cần sửa

**P0 — XSS trong dynamic rendering**

Các đoạn sau dùng `innerHTML` với dữ liệu có thể bắt nguồn từ profile user hoặc output AI:

- `backend/web/app.js:325`: `p.name` được chèn vào profile card.
- `backend/web/app.js:590`, `884`: `phase.phase_name`, `target_band`.
- `backend/web/app.js:868-871`: `rm.feasibility` và dữ liệu roadmap.
- `backend/web/app.js:974`: `c.original`, `c.corrected`, `c.explanation` từ LLM/user transcript.

Thay bằng `textContent` + DOM nodes; nếu bắt buộc HTML, dùng sanitizer allowlist. Không nên dựa vào security headers để giải quyết DOM XSS.

**P1 — Accessibility chưa đủ**

- Modal có `role="dialog"` nhưng chưa thấy focus trap, restore focus, đóng bằng Escape và đảm bảo heading/label đầy đủ.
- `alert()` được dùng cho thành công/lỗi, gây ngắt trải nghiệm và không nhất quán.
- Nhiều biểu tượng emoji/visual status thiếu accessible name hoặc phụ thuộc màu.
- Cần kiểm tra contrast thực tế của chữ nhỏ, màu muted và focus state.

**P1 — State/recovery**

- `api()` dùng timeout chung 180 giây; nên tách timeout theo health/settings, STT và LLM.
- Retry cần idempotency key hoặc client turn state để tránh gửi trùng khi timeout sau khi backend đã commit.
- Cần disable toàn bộ control liên quan trong lúc start/finish session, không chỉ nút record.
- Cần hiển thị rõ “AI đang suy nghĩ”, “đang chuyển giọng nói thành chữ” và “đang lưu”.

**P2 — Maintainability**

- `app.js` khoảng 1.400 dòng, nhiều responsibility: API, state, recording, placement, modal, rendering. Nên tách thành modules `api`, `session`, `profiles`, `placement`, `render`, `audio`.
- Không có bundler/type checking/lint/formatter cho web client.
- Cache-busting thủ công `?v=7.2/7.3` dễ quên cập nhật.

## 4. Đánh giá backend

### 4.1. Điểm tốt

- FastAPI route grouping và Pydantic schemas tương đối rõ.
- Có repository layer, model router và provider abstraction.
- Production config có các guard: API key, auth secret, CORS explicit, rate limit, DeepSeek key.
- Password hash PBKDF2-HMAC-SHA256 với salt và constant-time compare.
- JWT ký HMAC, có `iat`/`exp`, không nhét provider secret vào client.
- Docker chạy non-root, healthcheck, reverse proxy TLS và CI backend tests.
- Pronunciation service có disclaimer đúng: Whisper confidence không phải pronunciation score và score thử nghiệm không phải IELTS band.

### 4.2. Rủi ro nghiêm trọng

#### P0 — Broken access control / tenant isolation

`backend/app/core/auth.py:get_current_user_id()` ưu tiên `X-Profile-Id` hoặc query `profile_id` do client tự gửi. Trong khi đó:

- `backend/app/api/profiles.py` không lọc profile theo authenticated user.
- `reset-all`, get/update/delete/select profile chỉ cần API key/JWT hợp lệ, không cần ownership.
- `placement/evaluate` nhận `profile_id` trong body và lookup trực tiếp.
- Profile hiện không có `user_id`/account ownership field.

Hệ quả: nếu API public được expose và một account token bị dùng, caller có thể đọc/sửa/xóa profile và dữ liệu của profile khác. JWT có mặt nhưng chưa thực sự bảo vệ domain object.

**Cách sửa:**

- Thêm `owner_user_id` vào `profiles`, migrate dữ liệu local thành owner `default`.
- Resolve principal từ JWT, không dùng header client làm identity.
- `X-Profile-Id` chỉ là selected resource, phải query `profile.owner_user_id == request.state.user_id`.
- Tách rõ local single-device mode và authenticated cloud mode; không dùng cùng semantics mơ hồ.
- Viết regression tests cho IDOR: user A không đọc/update/delete profile/session/mistake của user B.

#### P0 — Audio privacy/lifecycle

`/speech/transcribe` lưu file vào `AUDIO_DIR/session_id` nhưng không có:

- byte limit trước khi ghi;
- kiểm tra MIME/content thực tế;
- quota per user/session;
- retention/TTL;
- endpoint xóa/export dữ liệu;
- xóa file sau khi transcription nếu không cần lưu.

Đặc biệt `POST /profiles/reset-all` xóa database rows nhưng không xóa `backend/data/audio`. Đây là data retention bug và có thể để lại recording nhạy cảm sau khi user yêu cầu reset.

**Cách sửa:** stream có giới hạn kích thước, allowlist codec sau decode, đặt quota, lưu metadata, background cleanup, cascade delete audio khi reset/delete session/profile, và công khai retention policy.

#### P0 — Unbounded expensive work / abuse

Một upload hợp lệ có thể kích hoạt Whisper rồi gọi pronunciation assessor. Không có giới hạn duration/size tại application layer. Rate limit hiện in-memory theo IP và chỉ ổn định với một process; không phù hợp khi scale nhiều worker/instance.

**Cách sửa:** giới hạn file bytes và duration, giới hạn concurrency cho Whisper, job queue cho inference, Redis/distributed rate limit, timeout riêng cho assessor, circuit breaker và metrics.

#### P1 — CORS và proxy trust

Local `.env` có `CORS_ORIGINS="*"`, còn `main.py` đặt `allow_credentials=True`. Production validator chặn wildcard, nhưng dev server vẫn dễ bị chạy với cấu hình rộng. Rate limiter tin `X-Real-IP`; nếu service bị expose trực tiếp không qua trusted proxy, client có thể spoof IP.

**Cách sửa:** không bật credentials cùng wildcard; chỉ trust forwarded headers từ reverse proxy đã xác định; validate origin theo environment.

#### P1 — Database migration

`Base.metadata.create_all()` cộng với vài `ALTER TABLE` thủ công chỉ phù hợp schema additive nhỏ. Không có Alembic/versioned migrations. Production PostgreSQL/SQLite lâu dài sẽ khó rollback, audit và deploy an toàn.

#### P1 — Error handling và leakage

Một số provider route trả `str(e)` trong HTTP detail, ví dụ router LLM. Điều này có thể lộ endpoint nội bộ, model/path/network detail cho client. Nên log đầy đủ ở server với request id, trả lỗi generic + error code cho client.

#### P1 — Transaction/idempotency

Conversation flow commit user turn, gọi LLM, commit assistant turn và progress ở các bước khác nhau. Nếu provider timeout sau khi đã xử lý hoặc client retry, duplicate/partial state có thể xảy ra. Cần request id/idempotency key và state machine cho turn.

## 5. Độ tin cậy dữ liệu và scoring

- Progress text input tính speaking minutes bằng `words / 110`, tối thiểu 0.25 phút; đây là proxy không phải speaking time thực.
- IELTS evaluation ghi cố định `speaking_minutes=2.5`, bất kể session thực tế.
- Full IELTS flow chưa thể hiện timer server-side; client timer có thể bị bỏ qua hoặc lệch.
- Scoring LLM transcript-based không có calibration dataset, confidence interval hay human benchmark.
- Pronunciation được caveat tốt trong service, nhưng UI vẫn dùng wording mạnh về “chuẩn IELTS/siêu chuẩn xác” cho Whisper.

**Khuyến nghị:** hiển thị rõ `Practice estimate`, lưu `scoring_version`, prompt/model metadata, transcript/audio provenance, và benchmark với bộ câu trả lời đã được human-rated trước khi dùng score làm KPI chính.

## 6. Android client

### Điểm tốt

- Có auth register/login và gửi Bearer token.
- Token được mã hóa bằng Android Keystore, không hard-code API key.
- Release chặn cleartext, debug cho local HTTP.
- CI có build debug APK và Java/Kotlin version tương đối rõ.

### Cần kiểm tra/sửa

- Default URL `http://10.0.2.2:8000/` chỉ dành cho emulator; cần UX setup rõ cho device thật và production URL.
- Build hiện có debug CI nhưng chưa thấy release assemble/signing verification trong CI; cần test minify/proguard và signed release artifact.
- `logging-interceptor` chỉ BASIC khi debug là chấp nhận được, nhưng cần audit để chắc chắn không log transcript/audio/token trong các interceptor khác.
- Cần contract tests giữa Retrofit models và OpenAPI/Pydantic; hiện API spec docs không hoàn toàn khớp route thật, ví dụ API spec ghi `/conversation/respond` nhưng schema response thực tế dùng `message`, `repeat_prompt`, metadata.
- Cần test offline/reconnect, permission denial, rotation/process death, large audio, 401 refresh/logout và model unavailable.

## 7. Testing và delivery

### Hiện trạng

- Có nhiều backend tests và deterministic model stub, đây là nền tốt.
- CI chạy backend tests và Android debug build.
- Local test trong audit **không chạy được** vì `backend/venv/Scripts/python.exe` trỏ tới `C:\Users\Hp\AppData\Local\Programs\Python\Python313\python.exe` bị Access Denied; không kết luận là test pass/fail.
- Chưa có frontend unit/e2e, accessibility scan, security regression hoặc load test.

### Bộ test tối thiểu trước pilot rộng

1. API contract test cho mọi route chính.
2. IDOR/tenant isolation tests.
3. Upload size/type/duration/quota tests.
4. Reset/delete phải xóa cả DB record và audio.
5. Duplicate retry/idempotency tests.
6. LLM timeout/fallback/provider error tests.
7. XSS payload tests cho profile name, correction, roadmap và AI output.
8. Playwright/Cypress happy path: profile → record → transcript → feedback → progress.
9. Android instrumentation/manual matrix: emulator, device thật, denied permission, mất mạng, app background.
10. Load test cho STT/LLM concurrency và memory.

## 8. Priority roadmap

### P0 — Chặn release production

- Sửa ownership/tenant isolation bằng `owner_user_id` và bỏ trust identity từ `X-Profile-Id`.
- Xóa/retention audio đúng với reset/delete; thêm endpoint data deletion/export.
- Giới hạn upload bytes/duration/concurrency và thêm cleanup.
- Loại bỏ dynamic `innerHTML` hoặc sanitize toàn bộ dữ liệu.
- Thêm regression tests cho IDOR, XSS, reset audio và duplicate turn.
- Làm cho local test environment reproducible: recreate venv từ lock/requirements và chạy CI parity.

### P1 — Sẵn sàng pilot có kiểm soát

- Chuẩn hóa API spec/OpenAPI và Android contract.
- Thêm loading/retry/error state, idempotency key và request correlation id.
- Tách modules frontend; thêm lint/format/type checks.
- Thêm database migration tool và backup/restore procedure.
- Cache adaptive plan theo ngày; ghi scoring/model/prompt version.
- Làm rõ disclaimer trên UI, thay wording overclaim về accuracy.

### P2 — Tăng retention và chất lượng học

- Event analytics privacy-safe và dashboard funnel.
- Feedback “hữu ích/không đúng”, learner correction acceptance.
- SRS cho mistake notebook, next best action sau mỗi session.
- Calibration score bằng human-rated dataset.
- Benchmark model latency/quality và quyết định local-first hay managed cloud theo phân khúc.

## 9. Go/no-go

**Có thể pilot nội bộ:** Có, nếu chỉ dùng local/single-machine, test accounts, không expose Internet, và giải thích rõ score là estimate.

**Mở public production ngay:** Không.

**Điều kiện tối thiểu để go public:** hoàn thành toàn bộ P0; có test IDOR/XSS/audio deletion; có privacy/retention policy; có release Android được ký và kiểm thử; có quan sát latency/error/resource; và chứng minh core loop hoạt động ổn định trên 3–5 người học không cần facilitator.

## 10. Kết luận

Nền tảng hiện có “độ rộng feature” tốt hơn mức MVP thông thường và có hướng khác biệt hợp lý ở local AI + personalized learning. Việc cần làm tiếp theo không phải thêm nhiều mode mới, mà là biến hệ thống từ **demo chức năng** thành **sản phẩm đáng tin**: bảo vệ dữ liệu đúng, feedback không overclaim, audio có lifecycle, retry không tạo dữ liệu bẩn, và đo được người học có thực sự tiến bộ hay không.
