# 06 — Kiến trúc tích hợp

## Quyết định mặc định của kế hoạch

Một repository SpeakingAI, một FastAPI backend, một nguồn identity/profile/provider, một learner database. Web là kênh triển khai bốn kỹ năng đầu tiên; Android hiện có giữ tương thích. Electron không bắt buộc.

Giao diện learning dự kiến dùng React/TypeScript của BandReady có chọn lọc trong `frontend/`, vì có editor/player/component cần tái dùng. Đây là phạm vi kiến trúc được đề xuất trong kế hoạch, chưa phải migration đã hoàn tất. T02 ghi dependency graph/cost và ADR trước import. Nếu gặp blocker thực tế, ghi phương án thay thế cụ thể, không tự thay cả backend.

## Phân lớp

```text
React learning UI / Speaking UI hiện có / Android hiện có
                  ↓ API auth + profile selector
FastAPI: learning routes + reading/listening/writing adapters + Speaking routes
                  ↓ domain services + job/media/provider contracts
SQLAlchemy: learner data có ownership | versioned content catalog
                  ↓
SQLite + managed media | Ollama host / STT / TTS đã cấu hình
```

Tất cả giao diện phải dùng cùng auth/profile context và progress source. Trong giai đoạn chuyển đổi có thể còn trang Speaking cũ; không gọi release “giao diện thống nhất” cho đến khi navigation/profile/history giữa các màn hình hoạt động và không phải đăng nhập lại. Không dùng iframe ghép hai app độc lập làm kiến trúc cuối.

## Vị trí đề xuất

- Giữ `backend/app/api/`, `schemas/`, `models/`, `repositories/`, `services/` theo conventions hiện tại.
- Learning mới: `api/learning.py`, `schemas/learning.py`, `models/learning.py`, `repositories/learning_repo.py`, `services/learning/` nếu đủ nhiều logic.
- Reading/listening/writing tách module khi cần, dùng cùng database/session/auth dependencies.
- Content versioned ở `content/learning/`; manifest và pipeline import rõ ràng.
- Tái dùng React modules/components qua `frontend/`; không lấy electron/main/preload/auto-update vào web bundle.
- Ghi `THIRD_PARTY_NOTICES.md` và upstream import manifest có URL/SHA/license/files/delta.

Các vị trí mới là đề xuất; T02/T03 chốt tên một lần, cập nhật API/test/import manifest cùng nhau. Không tạo wrapper mỗi khi một hàm thuần có thể tái dùng trực tiếp.

## Hợp đồng tích hợp donor

| Phụ thuộc donor | Cách thay |
|---|---|
| `require_auth`, token mỗi lần chạy sidecar | Auth hiện có; token người dùng và ownership theo request |
| `current_profile_id` từ settings toàn cục | Profile thuộc account trong request context; không có active user toàn cục |
| Settings/provider tự lưu của donor | Một cấu hình provider của SpeakingAI; không copy API keys |
| Donor DB engine/Base/migrations | Map model cần dùng vào SQLAlchemy/migration hiện có |
| Inference/render dài | Job có status/progress/cancel, kiểm owner cả job và artifact |
| Media ticket, audio Range | Adapter phù hợp auth web; không để raw token trong URL/log |
| Router/screen auto-discovery | Theo conventions repo đích; không giả định auto-discovery đã tồn tại |

Listening render phải có dependency inventory. Giữ lazy/optional import cho TTS để thiếu engine không làm toàn backend chết. Audio asset đã có được dùng trước. Không kéo toàn Pipecat/torch cho Reading/Writing chỉ vì donor có voice extra.

## Local runtime

Ưu tiên OrbStack chạy backend và Ollama native host đã có model. T01 kiểm container gọi được host endpoint; cấu hình qua env, không hardcode URL cho mọi môi trường. `/api/tags`/list để lấy tên thực, không tự sửa alias theo registry.

Compose hiện có model-init dependency. Agent phải cung cấp chế độ host rõ ràng, không vô tình chạy init/pull lại; thay đổi cấu hình bằng patch/override được ghi trong repo nếu được giao triển khai. Tải model mới chỉ khi thiếu thật và đã giải thích dung lượng/nhu cầu theo quyền hiện hành.

Frontend gọi backend đã xác thực; không chuyển `API_KEY_ENABLED=false` làm cách sửa lỗi UI. Production frontend có static assets/build đúng route, không chỉ JSON `/`. Backend container build context hiện là `backend`; T06/T19 phải xử lý đường dẫn build artifacts nếu frontend ở root.

## Compatibility và performance

- Không đổi shape các API Android/Speaking đang dùng nếu không có version/adapter tương thích.
- Dashboard mới tách speaking time, listening time, reading/writing activity; không cộng tất cả thành speaking minutes.
- Một worker và job manager in-process có thể dùng cho pilot, nhưng phải báo job bị interrupted khi restart; không báo succeeded khi chưa có output.
- Không thêm Redis/vector DB/microservices khi chưa có nhu cầu đo được.
- Auth/model/media errors có trạng thái rõ và retry có kiểm soát; save draft trước inference.
- Local/cloud consent theo chức năng; Tutor không tự gửi toàn bộ DB hoặc audio lên cloud.
