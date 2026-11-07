# Learning Edition — Baseline T00

Ngày audit: 06/11/2026. Repository: SpeakingAI. HEAD khi bắt đầu: `152b9f0a0c4d520e09001993ab174bb40eeffc99`.

Worktree đã có thay đổi chưa commit ở README/.env.example, Android network/conversation/progress, backend IELTS/progress/speech/config/adaptive/calibration/tests, Docker Compose và hai SQLite DB. Các thay đổi này được giữ; không reset/stash/commit.

## Inventory xác minh bằng code

- Backend FastAPI: `backend/app/main.py`, router đăng ký tường minh `/api/v1`.
- Identity: user/password/token ở `core/auth.py`, `api/auth.py`; profile có owner; selector profile không phải danh tính.
- Speaking: sessions/turns/conversation, Whisper STT, pronunciation, mistakes, progress, pilot.
- Provider: ModelRouter → Ollama/DeepSeek; cloud chỉ khi cấu hình/cho phép. Không mang provider store của donor sang.
- SQLAlchemy models: user/profile/session/turn/settings/progress/mistake/audio/adaptive/pilot/scoring. Migration tùy biến `app/migrations/runner.py`, chưa Alembic.
- Web cũ: `backend/web` HTML/JS/CSS; Android Kotlin client riêng.
- Trước phase: không có lesson runtime, content catalog, learning attempts hoặc React frontend trong repo đích.
- CI: backend pytest, Docker build, Android debug. Docker trước đây build với context backend; phase 1 đổi sang repo root để build React rồi copy assets vào image.

## Baseline kiểm thử mới

Lệnh từ backend: `/tmp/speakingai-venv/bin/python -m pytest tests -q`.

Kết quả trước implementation: **53 passed**, 1 warning deprecation anyio/Starlette, 1.98s. Provider stub và DB tạm theo conftest. Không phải kết quả Android hoặc nội dung sư phạm.

## Runtime/data

OrbStack context, backend bind `127.0.0.1:8000`, mount `./data:/app/data`. Native backend chạy từ backend có thể dùng `backend/data/app.db`; đây là file khác, không được dùng thay thế.

Trước cập nhật runtime, dùng SQLite `.backup` tạo `/tmp/learning-backup.LO1kGw/app.db`; integrity check `ok`, 21 sessions, 57 turns. Sau khởi động migration mới vẫn 21 sessions/57 turns trước smoke Speaking bổ sung. Backup không được commit hoặc đưa vào ZIP.

Ollama host có `qwen2.5vl:7b`, `qwen3.5:9b-nvfp4`, `ornith1.5:9b`, `gemma4:e4b-it-qat`. Đây là kết quả kiểm kê tại phiên chạy, không hardcode làm danh sách model của sản phẩm.

## Defects/limits đã nhận diện

- Production root trả JSON; web không có browser session; lỗi 401 có thể hiện thành “backend offline”.
- Model dropdown cũ hardcode tên không khớp kho model thực; selection ghi global settings.
- Selector profile không hợp lệ từng fallback về principal. Phase 0 sửa explicit invalid selector thành 404.
- Donor triển khai đã rộng hơn tài liệu July/August; inventory phải pin source thay vì đếm theo README.
- Nhãn calibration của code local chưa chứng minh bằng golden set; giữ trong backlog T16, không gọi đã calibrated.
- Chưa xác minh Android build/microphone thật trong phase này.
