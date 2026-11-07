# 08 — Backlog có dependency và acceptance

`tasks.json` giữ status/dependency. File này giữ chi tiết. Thứ tự ID là thứ tự tham khảo; chỉ chạy task đã qua dependency. Mỗi task ghi file thật sau discovery; paths dưới đây là vùng dự kiến, không cấp quyền ghi đè toàn thư mục.

Task chỉ `done` khi có bằng chứng exit gate. Code/test hoàn tất nhưng còn human review phải ghi `needs_review`, không giả `done`. Task khác không phụ thuộc approval đó vẫn tiếp tục. Agent được giao toàn bộ kế hoạch sẽ đi tiếp các task đủ điều kiện; không xin xác nhận mỗi task.

## T00 — Baseline và quyết định tích hợp

- Entry: repo đích đọc được, có chỉ dẫn hiện hành.
- Làm: pin SHA/worktree; inventory API/model/UI/provider/migration; xác định DB theo runtime; đọc hợp đồng sản phẩm cũ, ghi ADR mở rộng theo V2. Snapshot test/build hiện có, phân biệt kết quả cũ với lần chạy mới.
- Vùng: docs audit/ADR; đọc backend/android/web/config; chưa implement feature.
- Output: `docs/learning-audit/BASELINE.md`, `REUSE_MATRIX.md`, `RISK_AND_DECISIONS.md`; có test command và build blocker thật.
- Gate: mọi module được phân loại reuse/extend/new, không gọi kế hoạch upstream là hiện trạng; worktree người dùng được bảo toàn.

## T01 — App local dùng được: auth và model

- Entry: T00.
- Làm: web login/logout/expired token theo auth hiện có; model discovery thực; host Ollama mode cho OrbStack; chọn profile đúng. Giữ bảo vệ API. Không tự tải model.
- Vùng: web/API client, auth integration, config/Compose/docs; không viết lại auth thuật toán khi không cần.
- Check: missing/expired token; user A/B không xem hồ sơ nhau; profile không tồn tại không fallback; model thiếu có lỗi rõ.
- Gate: mở browser, đăng nhập, chọn hồ sơ, gửi câu Speaking và nhận output; ghi provider thật/mocked. UI dùng được, không chỉ health 200.

## T02 — Khảo sát và chọn code donor

- Entry: T00.
- Làm: pin donor SHA, license; vẽ dependencies cho marking, reader, editor, listening/player/tts, jobs; chọn phần nhỏ đủ cho 4 lesson. ADR frontend React + backend adapter, dependency inventory và nguồn imports.
- Vùng: tài liệu/import manifest/notices; không cài toàn voice extra mặc định.
- Output: `UPSTREAM_IMPORTS.md` có source SHA/path/license/consumer/delta; danh sách dependencies thực sự cần, conflict và cách xử lý.
- Gate: không có hai user DB/provider settings/active profile toàn cục; không đổi stack ngoài quyết định.

## T03 — Chốt content/evidence/API contract

- Entry: T00, T02.
- Làm: hiện thực Pydantic/domain contracts từ schemas tham khảo; pin ID/version, result/assistance/exposure; chốt API/resources/limits/error shapes. Mapping content item → competency → activity → learner evidence.
- Vùng: backend schemas, content schema, API contract docs; chưa expose raw answer keys.
- Check: schema hợp lệ/không hợp lệ; content refs/version; reject client tự báo owner/correct/mastery; API learning không trùng routes.
- Gate: fixtures cho 4 lesson có shape nhất quán, semantics trợ giúp/transfer/review không mơ hồ.

## T04 — Persistence và migration an toàn

- Entry: T03.
- Làm: reuse user/profile; thêm content refs/attempt/evidence/review/state tối thiểu; constraints/idempotency/lineage; update export/delete. Mapping donor tables theo nhu cầu.
- Vùng: models/repositories/migrations và tests.
- Check: DB mới; snapshot DB cũ có Speaking; migration lặp; restore backup trên bản sao; user/profile isolation, concurrent duplicate submit, stale draft.
- Gate: Speaking history cũ không đổi; rollback/restore có bằng chứng; không test trên DB thật.

## T05 — Content pipeline và bài draft pilot

- Entry: T03.
- Làm: manifest/validator/import idempotent; biên soạn L01–L04 theo `04_FOUR_SKILLS.md`; đủ mẫu/guided/independent/transfer/review variants. Phân tách answer key và learner payload. Workflow reviewer.
- Vùng: content/learning, validator/import tests, content-review checklist.
- Check: checksum/ID/version/refs/cycles; đáp án evidence; thiếu asset; retire/update giữ attempts; không lộ transfer answer cho Tutor.
- Gate: developer preview được với draft có nhãn rõ; chưa có reviewer thì recorded `pending_review`, không biến thành content release.

## T06 — Lesson player và web shell

- Entry: T01, T02, T04, T05.
- Làm: React frontend chọn lọc; Today/lesson steps; API auth/profile dùng chung; autosave/resume; tách Learn/Independent/Assessment; navigation Speaking cũ không mất session.
- Vùng: frontend, FastAPI static/development setup, compatibility adapters.
- Check: browser từ lần mở đầu → auth → bài → refresh/resume; keyboard/focus, loading/error, draft conflict, đổi profile không lẫn draft.
- Gate: mẫu + guided + independent chạy được từ UI với fixture; frontend build artifact được backend phục vụ đúng, không chỉ HTML skeleton.

## T07 — Tutor dạy và feedback dẫn tới tự sửa

- Entry: T03, T04, T05.
- Làm: lesson-grounded prompt; hint ladder; worked example; error/suggestion/alternative; feedback giới hạn vào objective; learner correction step; output validation/source refs.
- Vùng: services/prompts/schemas/API và UI tutor.
- Check: không biết nguồn; malformed output; timeout; thiếu model; prompt injection trong content; answer leakage; câu đúng không bị bắt buộc thay “nâng band”.
- Gate: người học có thể hiểu gợi ý, tự sửa rồi làm câu mới; retry không lặp evidence; mẫu/rewrite AI không tự thành learner answer.

## T08 — Reading learning slice

- Entry: T02, T04, T05, T06, T07.
- Làm: import normalizer/player cần thiết; câu/đoạn vừa sức; scaffold cấu trúc/phủ định/đổi ý; learner chọn evidence + diễn giải; làm bài mới; feedback và retry.
- Vùng: reading adapter/service/UI/content/tests.
- Check: marking variants/word limit theo activity; evidence span; key ẩn; autosave; profile isolation; trợ giúp → assisted.
- Gate: L02 hoàn thành từ Learn tới transfer, draft/review lưu đúng; không chỉ có màn hình làm đề.

## T09 — Listening learning slice

- Entry: T02, T04, T05, T06, T07.
- Làm: reuse audio asset đã có trước; nếu cần TTS, kiểm dependency/model; render/cache/job/player/transcript; Learn cho replay, independent ghi exposure; probe phân biệt âm-nghĩa-spelling.
- Vùng: listening adapter/media/jobs/TTS optional/UI/content/tests.
- Check: missing engine, cancelled/interrupted render, bad audio/timing, Range/auth, cache hit/version change, cleanup; server không chết vì thiếu TTS.
- Gate: L01 nghe thật trong browser, transcript đúng; thiếu asset/engine báo blocker audio, không báo test mock là đã nghe thật. Nội dung/audio chưa human review vẫn draft.

## T10 — Writing learning slice

- Entry: T02, T04, T05, T06, T07.
- Làm: editor/autosave/annotations/revision; short objective rubric; learner tự sửa; bài mới/chủ đề khác; không áp essay penalties lên bài câu/đoạn.
- Vùng: writing adapter/provider jobs/UI/content/tests.
- Check: char offsets/Unicode, valid alternative, stale save, retry submit, malformed model, không mất bài khi scorer fail, isolation.
- Gate: L03 hoàn thành mẫu → learner draft → feedback → learner revision → transfer mới; không dùng band tăng làm chứng minh học được.

## T11 — Speaking learning slice và compatibility

- Entry: T04, T05, T06, T07.
- Làm: nối lesson/activity vào session/turn hiện có; accuracy/fluency feedback timing; transcript correction và audio replay; learner tự nói ý; follow-up mới.
- Vùng: speaking API/service/web bridge/UI + compatibility tests; Android DTO chỉ đổi nếu cần và có default/version.
- Check: idempotent turns, STT lỗi, mic denied, text fallback có nhãn, timing không bịa, session cũ và Android contract.
- Gate: L04 có new-context response; text test không được gọi pronunciation assessment; micro thật phải có manual result hoặc ghi chưa kiểm.

## T12 — Evidence, review và mastery V0.1

- Entry: T04, T05, T07.
- Làm: state reducer theo policy; exposure tracking; review 2/7 ngày hoặc scheduler sẵn có; clock injection; variant selection chưa gặp; no-item fallback.
- Vùng: learning state/review services/repo/tests.
- Check: same-item retry, answer-revealed, hint-assisted, new-context transfer, delayed review, inconsistent evidence, model low confidence, clock boundaries.
- Gate: không thăng state từ completion/time/AI rewrite; replay evidence cho cùng kết quả; không tạo review trùng scheduler.

## T13 — Daily planner có giải thích

- Entry: T04, T05, T12.
- Làm: rule-based chọn prerequisite, remedial lesson, due review, new application; cân bằng 4 kỹ năng, thời lượng và lựa chọn người học; reuse adaptive cache khi phù hợp.
- Vùng: progress/adaptive services/API/UI/tests.
- Check: chưa có band/ngày thi, rảnh 10 phút, cạn content, thiếu audio, sai một lần, skill imbalance, user reschedule.
- Gate: recommendation có activity/version/evidence reason; không giao full mock mặc định, không ép đăng ký thi.

## T14 — Một đơn vị học tích hợp end-to-end

- Entry: T08, T09, T10, T11, T12, T13.
- Làm: nối L01–L04 và review; thay bề mặt/dữ kiện giữa bài để không lộ đáp án; đảm bảo history/progress theo đúng người học.
- Vùng: integration/UI/content/tests.
- Check: fresh profile → bài nghe/đọc → tự viết/nói → tự sửa → transfer → clock-advanced review; restart giữa bài; compatibility history cũ.
- Gate: thực hiện qua browser, ghi evidence từng bước và lỗi còn lại; đây là mốc feature đầu tiên, chưa phải chứng minh hiệu quả giáo dục.

## T15 — Dashboard và động lực học

- Entry: T06, T12, T13.
- Làm: Today là màn hình chính; biểu thị can-do/assistance/transfer/retention, next action; history 4 skill; assessment tách; đổi goal học/thi không xóa năng lực.
- Vùng: frontend/progress schemas/repo, docs.
- Check: thiếu evidence, delayed review chưa tới, unknown không biến thành zero, speaking vs study time, keyboard/mobile width.
- Gate: người mới hiểu hôm nay học gì/vì sao; không lấy streak/band làm tiến bộ duy nhất.

## T16 — Assessment và tính trung thực điểm AI

- Entry: T00, T03, T07.
- Làm: audit nhãn calibration đang có; tách rubric objective/band; prompt/provider/model/version trace; null/abstain; thiết kế tập human-rated và protocol đánh giá scorer, tách dữ liệu fit/evaluation.
- Vùng: scoring/prompts/schemas/calibration UI/tests/docs.
- Check: thiếu audio, input quá ít, unsupported model, malformed response, heuristic confidence, label calibrated/±0.5 khi chưa có evidence.
- Gate: learning vẫn chạy khi band chưa validated; band hiện có mang nhãn provisional phù hợp. Chưa có golden set thì report “chưa xác minh”, không fake accuracy hoặc gate deployment học tập vì thiếu band.

## T17 — Regression, security và content release candidate

- Entry: T14, T15, T16.
- Làm: complete QA matrix `09`; suite backend/frontend/migrations/media/isolation; kiểm notices/import provenance, build/runtime, content reviewer status.
- Check: baseline regression, user A/B, malicious IDs/path/content, delete/export, backup/restore, cancellation, missing provider, browser flow.
- Gate: technical release candidate có check logs; bài chưa reviewer approved không phát hành cho pilot. Không tuyên bố Android tested nếu chưa chạy.

## T18 — Pilot học tập có đo trước/sau/giữ lại

- Entry: T17 và ít nhất một unit được human-approved, người học/điều kiện pilot được chủ dự án cung cấp.
- Làm: theo protocol `09`; thu consent khi cần; baseline item A, học, item B mới, retention item C; ghi hint/time/context/attrition và phỏng vấn hiểu feedback.
- Vùng: reports và dữ liệu được phép, không public learner text/audio.
- Gate: báo cáo số thật cùng n/missing data; không bịa learner/reviewer/learning gain. Không đủ người hoặc chưa đến retention → ghi pending evidence; tiếp tục phân tích đã có.

## T19 — Bàn giao bản học tập đầu tiên

- Entry: T18, không còn blocker phát hành đã xác nhận.
- Làm: hướng dẫn run/auth/model đã có; package web/backend; release notes phạm vi 1 unit; giữ Speaking; recovery; ghi giới hạn scoring/content/hardware.
- Check: người nhận cài/chạy từ hướng dẫn, mở UI hoàn thành bài, resume, export/delete trên test profile, không có secret/DB/model trong artifact.
- Gate: một repo/app dùng được; không gọi “khóa học beginner–7.0 hoàn chỉnh”. Mở backlog unit tiếp theo từ evidence pilot.

## Mốc mở rộng sau bản đầu

Sau khi T19 đạt, thêm unit theo năng lực, mở mức khó/đối tượng theo nội dung đã duyệt, rồi mới tăng dạng IELTS/full mock. Android 4 skill, desktop packaging và teacher review portal là task/ADR mới có phạm vi riêng. Không tự kéo vào bản đầu.
