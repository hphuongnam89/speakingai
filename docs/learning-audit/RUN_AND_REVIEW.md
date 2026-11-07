# Chạy và kiểm duyệt bản phase 0–1

Cập nhật 07/11/2026: audio/player/recorder, review 2/7, Today và objective feedback đã có trong preview 0.2. Xem [bàn giao Phase 2–3](../learning-handoffs/2026-11-07-phase-2-3.md) cho trạng thái mới; phần dưới ghi lại thao tác baseline 0–1. Nội dung vẫn draft; microphone thật và human review chưa xác minh.

## OrbStack + Ollama host đã có model

Từ repository root:

```sh
docker context show
ollama list
docker compose -f docker-compose.yml -f compose.host-ollama.yml up -d --build backend
```

Nếu môi trường dùng RTK, chạy qua `rtk proxy` theo quy định local. Host override xóa dependency model-init; không cần khởi động Ollama container hoặc pull lại model. Backend dùng `host.docker.internal:11434`, giữ API authentication. Không in nội dung `.env`.

`.env` cần API_KEY và AUTH_SECRET ngẫu nhiên theo README hiện có. Để preview draft local, đặt ENVIRONMENT=development; production không cho preview. Không đổi API_KEY_ENABLED thành false để làm login hoạt động.

Mở http://localhost:8000/learn . Tạo tài khoản của bạn/đăng nhập, tạo/chọn hồ sơ. Bật **Xem bài nháp để thử luồng học (chưa kiểm duyệt)**. Chọn bài, làm guided task, xin hint, nộp, chuyển independent, thử câu mới. Reload → mở lại bài để resume đúng step/draft/feedback. Speaking cũ ở http://localhost:8000/speaking dùng chung browser session.

Một account/profile QA local đã được tạo để kiểm luồng trong phiên phát triển; không phải hồ sơ người học thật. Không commit mật khẩu/token QA. Lịch sử default từ phiên chưa đăng nhập vẫn còn DB, không tự chuyển ownership sang account mới.

## Native development

```sh
cd frontend
npm ci --ignore-scripts
npm run typecheck
npm test
npm run build
```

Build ghi assets vào `backend/web/learning` (gitignored). Sau đó chạy backend bằng virtualenv theo README; xác định đúng DATABASE_URL trước khi chạy để không trỏ nhầm DB. Container build từ root với `backend/Dockerfile` tự build frontend.

Kiểm content từ backend:

```sh
python -m app.services.learning_content
python -m pytest tests -q
```

Không dùng Python hệ thống thiếu dependency thay cho venv rồi kết luận app lỗi. Runtime đã thử bằng Python3.12 trong image và tests Python3.13; Android chưa được build/chạy trong phase này.

## Human review queue

| Lesson | Nội dung đã có | Còn cần người duyệt |
|---|---|---|
| reading-change 0.1.0 | Mẫu, guided, 4 independent, 4 transfer, feedback/self-repair steps | Độ khó, đáp án/evidence, hướng dẫn tiếng Việt |
| listening-change 0.1.0 | Script/mẫu, 4 independent, 4 transfer | Audio chưa render/duyệt; không đánh giá nghe từ script preview |
| writing-change 0.1.0 | Mẫu, guided, 2 independent, 2 transfer | Rubric/giải thích và tính phù hợp sơ cấp |
| speaking-change 0.1.0 | Mẫu, guided, 2 independent, 2 transfer | Recording/drills chưa nối; bản nền tảng chỉ gõ thử |

Tất cả giữ draft, ai_assisted=true, reviewer=null, license chưa gán. Không có bằng chứng human approval hoặc learning gain. Sau review: tăng content version, ghi source/license/reviewer/date thật, update checksum manifest bằng tooling/authoring workflow. Import không cho sửa payload của cùng version đã lưu.

## Kiểm tra lỗi thường gặp

- 401: đăng nhập lại; không gọi là backend offline.
- 404 profile: chọn hồ sơ thuộc account, không tự fallback sang hồ sơ khác.
- 409 draft: tải trạng thái mới, đối chiếu nội dung đang gõ trước khi lưu tiếp.
- Không thấy bài: released catalog đang trống vì chưa human-review; local bật preview.
- Không thấy model: kiểm Ollama host đang chạy và tags thực tế; không đoán tên/pull tự động.
- Tutor502/503: giữ draft, thử lại/đổi model đã cài; output không hợp schema/source không được hiện như thành công.

## Rà soát trước bàn giao

Correctness: identity/profile isolation, optimistic save, retry idempotency và giữ version đã có regression tests. Architecture: một identity/provider/DB, giữ Speaking và phạm vi T08+ riêng. Security: cookie HttpOnly/Strict + origin check; không secret trong client; content/model output là dữ liệu. Performance: catalog/history/event có giới hạn; submit/Tutor giới hạn text/token/timeout. Content quality: draft không bị gọi approved/mastered.

Không commit, merge hoặc push trong lượt triển khai này. Các thay đổi người dùng trước task được giữ nguyên.
