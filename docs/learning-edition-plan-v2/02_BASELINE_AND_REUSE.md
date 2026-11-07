# 02 — Baseline và bản đồ tái sử dụng

## Bằng chứng tại ngày viết

| Nguồn | Snapshot | Mức xác minh |
|---|---|---|
| SpeakingAI | `hphuongnam89/speakingai`, HEAD `152b9f0a0c4d520e09001993ab174bb40eeffc99` + worktree đang sửa | Đã đọc code, trước đó chạy 53 backend tests; không thay cho baseline mới của agent |
| BandReady | `Luxshan2000/ielts-prep`, SHA `1627d57fc8beccb8158302c04b0c62d2744b0b02` | Đã đọc source/manifest; chưa chạy suite hoặc xác minh chất lượng nội dung |
| ZIP kế hoạch cũ | `bandready-learning-edition-plan.zip`, 22 Markdown | Tài liệu định hướng; không có implementation |

Clone BandReady dùng để review ở `/tmp/bandready-integration-review` trên máy tác giả là đường dẫn tạm, không phải dependency triển khai. Agent ở máy khác dùng URL và SHA; không tự cập nhật donor lên main mới nhất.

## Nguồn sự thật hiện tại

SpeakingAI: FastAPI/Pydantic/SQLAlchemy, SQLite, web HTML/CSS/JS ở `backend/web`, Android Kotlin ở `android/`. Model/router/provider nằm trong `backend/app/`. Migration tùy biến ở `backend/app/migrations/runner.py`; chưa phải Alembic.

Có `UserModel`, `ProfileModel`, `SessionModel`, `TurnModel`, `MistakeModel`, `DailyStatsModel`, `AdaptivePlanModel`, audio, pilot và calibration records. Không tạo thêm bộ learner/tutor session giống hệt chỉ vì donor gọi tên khác.

Ownership: `owner_user_id` là tài khoản; profile được chọn là tài nguyên thuộc tài khoản. Không đổi selector profile thành danh tính xác thực.

## Mapping

| Domain | Giữ SpeakingAI | Chọn từ BandReady | Công việc tích hợp |
|---|---|---|---|
| Identity | `core/auth.py`, user/profile repo | Không mang token launch và active profile toàn cục sang | Adapter auth theo request + truy vấn ownership |
| Speaking | session/turn/conversation/STT/mistake | Nội dung/cách luyện nếu phù hợp | Thêm lesson context; không thay voice pipeline đang chạy |
| Reading | API conventions, identity | `server/routes/reading.py`, `scoring/answers.py`, UI reading | Tách marking thuần, content, attempts và review khỏi giả định sidecar |
| Listening | provider settings, media ownership | `routes/listening.py`, drills/coach, `audio/tts_render.py`, player | Kiểm tra TTS dependency, cache, range request, quyền audio |
| Writing | LLM router, history ownership | `routes/writing.py`, `scoring/writing.py`, coach, editor/annotations | Adapter provider, job, draft lineage và lesson goals |
| Nội dung | Không ghi vào learner DB như history | `content/core-en/`, pack tools | Pin version, provenance, checksum, review độc lập |
| Ôn tập | mistake/progress hiện có | FSRS/grammar patterns chọn lọc | Không nhân đôi scheduler hoặc learner state |
| Curriculum | profile/placement làm đầu vào | Pattern curriculum/theory có thể tái dùng | Thiết kế chu trình dạy học theo tài liệu V2 |

Các file donor có import chéo DB/settings/jobs/providers. Không copy route rồi chỉ đổi URL. Lập dependency map trước, tách các hàm thuần trước, kiểm thử hợp đồng sau khi adapter.

## Vấn đề cần kiểm tra ở T00/T01

- Worktree có nhiều thay đổi chưa commit, gồm calibration và DB. Không ghi đè.
- Compose mount `./data:/app/data`, khác `backend/data/app.db` khi chạy Python từ backend. Xác định DB theo runtime; backup đúng file bằng SQLite backup API trước migration.
- Production `/` hiện trả JSON, development mới có web UI. Health 200 không chứng minh app dùng được.
- Web đã quan sát lỗi authentication. Giải quyết bằng đăng nhập/token theo user, không tắt API key hoặc gắn admin key vào bundle.
- Ollama host đã có alias `ornith1.5:9b`; container volume không dùng chung kho host. Kiểm kê `/api/tags` hoặc `ollama list` trước tải.
- Container backend đã từng gọi thành công Ollama host; phải thử lại sau thay đổi, không coi kết quả lịch sử là hiện trạng.
- Hàm calibration hiện có điều chỉnh bias và confidence heuristic. Chưa chứng minh sai số ±0.5 hoặc hiệu chuẩn đủ chuẩn; T16 phải kiểm tra nhãn.
- Android chưa được build/chạy trong phiên kiểm tra trước; không suy ra thiếu wrapper nghĩa là tất cả môi trường đều không build được.

## License

Donor LICENSE ghi MIT; manifest core-en ghi CC0-1.0 và ai_assisted. Khi tái sử dụng giữ notice/attribution cần thiết và ghi nguồn. Manifest/README không chứng minh đáp án hoặc bài giảng đã được kiểm duyệt độc lập. Không suy ra license code tự bao phủ model/voice/dependency.
