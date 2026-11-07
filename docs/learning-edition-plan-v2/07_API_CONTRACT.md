# 07 — Hợp đồng API và sự kiện

Đây là API đề xuất để agent thống nhất trước khi code. T03 đối chiếu OpenAPI/routes thật để tránh trùng. Giữ prefix `/api/v1`, conventions Pydantic/error của repo đích và compatibility Speaking.

## Auth và ownership

API learning luôn đi qua auth hiện có. Profile selector chỉ chọn tài nguyên trong account đã xác thực. Không tin owner/profile từ JSON body. Trả 404 khi truy cập attempt/observation/job/media không thuộc người dùng; kiểm tra cả GET và mutation.

Web dùng đăng nhập người dùng sẵn có qua `/auth/...` sau khi xác minh path/schema. Không nhúng backend admin API key, static donor dev-token hoặc AUTH_SECRET trong bundle. Missing/expired token có UI đăng nhập; không hiển thị “mất kết nối” cho mọi lỗi 401.

## Các tài nguyên

| Method/path đề xuất | Kết quả và bất biến |
|---|---|
| GET `/learning/today` | Activity/review IDs, objective, duration estimate, reason codes và evidence refs |
| GET `/learning/units` | Danh mục theo level/goal; mặc định chỉ released content |
| GET `/learning/lessons/{id}?version=...` | Learner-safe steps; không answer key/transfer solution |
| POST `/learning/attempts` | Pin lesson version + activity; ID do server sinh; khóa replay submit |
| GET `/learning/attempts/{id}` | Resume step/draft và assistance đã ghi, đúng owner/profile |
| PATCH `/learning/attempts/{id}` | Autosave có revision/version; stale edit trả conflict, không mất bản nháp |
| POST `/learning/attempts/{id}/hints` | Server cấp hint và ghi loại/mức/exposure trước trả nội dung |
| POST `/learning/attempts/{id}/submit` | Validate item/response/mode/exposure; synchronous hoặc job 202 |
| POST `/learning/attempts/{id}/revisions` | Bản sửa có parent ID; không tự thành independent evidence |
| GET `/learning/competencies` | State/reason/policy/evidence quality; band riêng nếu assessment có |
| GET `/learning/reviews` | Due reviews và trạng thái thiếu item; không generate đáp án tin cậy giả |
| POST `/learning/reviews/{id}/reschedule` | Đổi lịch, giữ lịch sử, kiểm thời gian hợp lệ |

Không tạo `/jobs` hoặc scheduler mới nếu adapter của dự án đã đáp ứng. Chốt ở T03. Learning activity có thể trỏ tới reading/listening/writing attempt chuyên biệt; phải có canonical ID/mapping, không nộp cùng câu vào hai nơi rồi cộng evidence hai lần.

## Submit body tối thiểu

```json
{
  "request_id": "client-generated-retry-key",
  "item_id": "reading-change-01",
  "item_version": "1.0.0",
  "response": {"text": "The meeting is on Thursday."},
  "expected_revision": 2
}
```

Đây là ví dụ, không phải endpoint đã chạy. `request_id` được scope theo owner + attempt + action. Retry cùng key/body trả cùng kết quả; cùng key/body khác trả 409. Enforce uniqueness bằng DB/transaction, không chỉ client.

Server lấy competency/mode/assistance/content version từ attempt đã pin; không cho client tự khai `correct`, `independent`, `mastered` hay confidence. Validate text size/media limits bằng cơ chế hiện có, thêm giới hạn cụ thể ở T03.

## Feedback response

```json
{
  "attempt_id": "server-id",
  "result": "needs_revision",
  "objective_feedback": [{
    "competency_id": "reading.follow_change",
    "claim_type": "error",
    "evidence_refs": ["stimulus:s1:span:25-60"],
    "explanation": "Người viết đã sửa lại lịch hẹn ở câu sau.",
    "next_action": "Hãy chỉ ra ngày cuối cùng và cụm từ báo đổi ý."
  }],
  "assistance": {"max_hint_level": 1, "answer_revealed": false},
  "learning_evidence_status": "assisted",
  "assessment_band": null
}
```

Vị trí evidence phải được xác minh với stimulus/response version. Sai/malformed LLM output: trả trạng thái unavailable/needs_review có lý do; không tự cho điểm hoặc giữ band mặc định.

## Sự kiện nội bộ

`lesson_viewed`, `hint_requested`, `answer_submitted`, `feedback_viewed`, `revision_submitted`, `transfer_completed`, `review_completed`.

Chỉ `answer_submitted` đã chấm hợp lệ mới có thể sinh performance evidence; xem feedback/lesson là exposure. Duplicate processing không nhân đôi observation. Persist event liên quan và state trong transaction hoặc có cơ chế retry idempotent tương đương; không cần message broker cho bản đầu.

## Job/media

Job: queued/running/succeeded/failed/cancelled/interrupted; có owner, attempt ID, progress, lỗi và artifact refs. Cancelled/failed không thêm competency evidence. Restart không làm mất draft. Media download kiểm quyền, hỗ trợ Range khi player cần và không cho arbitrary filesystem path.
