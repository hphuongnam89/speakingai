# 05 — Nội dung, dữ liệu và version

## Content contract

Đơn vị học → lesson → ordered step → activity → item/rubric → evidence. Tham khảo cấu trúc ở `schemas/lesson.schema.json` và `examples/lesson-reading-draft.json`; đây là ví dụ draft để thử hợp đồng, chưa phải bài đã duyệt.

Lesson cần: ID/version/status, skill, can-do objective, competency IDs, prerequisites, explanation, mẫu có hướng dẫn, guided task, independent task, transfer task, source/reviewer/license, thời lượng gợi ý.

Item cần: ID/version, competency, stimulus/media version, mode, mục tiêu chấm, lời giải có evidence, nhóm biến thể và exposure rule. Lưu đáp án ở server/content authoring; learner payload không có answer key hay rubric answer có thể làm lộ bài độc lập.

## Quy trình nội dung

`draft → validated → pending_review → approved → published → retired`.

Validator kiểm: schema, IDs/reference, prerequisites không vòng, asset tồn tại/checksum, đáp án có evidence, không vô tình trùng độc lập/transfer với mẫu, provenance/license. Các check tự động không thay human review ngôn ngữ/sư phạm/audio.

Reviewer người thật phải ghi ID/tên vai trò, ngày, phiên bản và checklist. Agent không được tự điền danh tính hoặc gán `approved` vì nội dung có vẻ đúng. Thiếu reviewer: cho preview có nhãn draft trong môi trường dev, không đưa vào lộ trình mặc định phát hành.

Các quy tắc `approved/published` là workflow nội dung được người dùng giao; không tự publish ra website/service ngoài phạm vi.

## Chuẩn một đơn vị pilot

- 4 lesson L01–L04 theo `04_FOUR_SKILLS.md`.
- Mỗi lesson có ít nhất một worked example, một guided activity, một independent activity và một transfer activity.
- Với objective chấm xác định, chuẩn bị đủ item mới để chạy policy V0.1; thiếu item thì ghi insufficient evidence, không lặp lại câu đã lộ để đủ số.
- Có variant chưa gặp cho review 2/7 ngày; nếu cạn item thì hiện lý do và yêu cầu bổ sung.
- Content inventory báo riêng authoring count, validated count, human-approved count và released count.

## Tái dùng ngân hàng BandReady

Giữ donor content ID/version/source khi import hoặc bảng mapping rõ ràng. Đề thi dài chỉ là nguồn ngữ liệu nếu phù hợp độ khó, license và review. Không gọi việc chia một đề thành bốn đoạn là hoàn thành giáo trình.

Không chỉnh generated pack trực tiếp nếu upstream quy định nguồn staging/build/merge. Lưu bản upstream pin và patch/delta của dự án; import idempotent và không làm mất learner history.

## Mô hình dữ liệu đề xuất, phải đối chiếu T00/T03

| Dữ liệu | Quyết định |
|---|---|
| Tài khoản/hồ sơ | Tái dùng user/profile hiện có; không tạo learner identity song song |
| Speaking session/turn/mistake/audio | Giữ lịch sử, thêm liên kết learning activity nếu cần |
| Content/catalog | Versioned lesson, activity, item, asset; tách khỏi learner attempts |
| Learning attempt | account owner, profile, lesson/activity/content version, status, draft, timestamps |
| Answer/evidence | attempt/item version, input modality, assistance, exposure, result, scorer/method, evidence refs |
| Competency state | profile + competency, state, evidence IDs, policy version, next_review_at |
| Plan/review | Sử dụng adaptive cache hiện có nếu phù hợp; thêm liên kết activity/evidence có schema |
| Writing/listening/reading | Giữ đặc trưng domain, nối cùng activity/attempt ownership; không ép mọi thứ vào transcript Speaking |

Gợi ý tên `learning_attempts`, `learning_observations`, `learner_competencies`, `learning_reviews`; chưa phải tên bảng đã tồn tại. Chỉ tạo bảng sau mapping reuse/extend/new. Chỉ số tổng hợp có thể tính lại từ evidence, không sửa lịch sử cũ để hợp policy mới.

## Tính toàn vẹn

- Owner từ auth context, profile phải thuộc owner. Chọn profile không hợp lệ trả 404/403 nhất quán; không âm thầm chuyển sang profile khác ở API learning.
- Observation tự sinh ID ở server, content/attempt refs xác minh bằng DB. `owner_user_id`, scorer, hint, exposure không tin trực tiếp từ client.
- Schema observation ở gói mô tả record nội bộ; không dùng làm request body để client tự báo “đã đạt”.
- Unique submission key/idempotency; cùng response retry không cộng điểm/ôn/evidence lần hai.
- Sửa câu trả lời tạo revision có lineage; independent test đã lộ đáp án không lấy lại nhãn unassisted.
- Timestamps UTC; lịch hiển thị theo timezone người dùng. Clock injectable trong test.
- Lưu đúng content version cho attempt; update pack không thay câu hỏi/đáp án của attempt cũ.
- Media ID do server quản lý; kiểm owner, MIME, size/duration và path traversal.
- Deletion/export bao phủ dữ liệu mới, media và quan hệ; không chỉ xóa dòng profile.

## Migration

Tái dùng migration runner hiện có cho thay đổi tăng dần của bản đầu. Không mang Alembic version table của donor sang DB đang dùng. Nếu cần đổi công cụ migration, ghi ADR riêng và có baseline/rollback test.

Trước migration DB thật: xác định đúng file runtime, dùng SQLite backup API/consistent snapshot, kiểm restore trên bản sao; không copy file đang ghi rồi coi backup an toàn. Kiểm thử DB mới và bản sao DB cũ có history; không làm migration test trên DB học viên.
