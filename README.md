# IELTS Speaking AI Coach

Ứng dụng luyện nói tiếng Anh và luyện thi IELTS Speaking với AI Coach chạy Local (Ollama) và Cloud fallback.

---

## 🛠️ 1. Khởi động Backend (FastAPI + Ollama)

### Yêu cầu
- Python 3.12+ (hoặc Python 3.13)
- Ollama với model `ornith-1.5:9b` (hoặc `gpt-oss:20b`)

### Các bước chạy
1. **Kiểm tra Ollama**:
   ```bash
   ollama list
   # Đảm bảo đã có model: ornith-1.5:9b
   ```

2. **Cài đặt thư viện Python**:
   ```bash
   cd backend
   py -3.13 -m venv venv
   .\venv\Scripts\pip install -r requirements.txt
   ```

3. **Chạy máy chủ Backend**:
   ```bash
   .\venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   Backend gửi `num_ctx=4096` và `think=false` cho coach Ornith để tránh dùng
   context mặc định quá lớn hoặc chờ model suy luận dài. Timeout là 120 giây;
   giới hạn trả lời mặc định 1024 token, đủ cho sửa lỗi và báo cáo IELTS.
   Có thể chỉnh qua `OLLAMA_CONTEXT_LENGTH`, `OLLAMA_THINK`, `OLLAMA_TIMEOUT`
   và `OLLAMA_MAX_OUTPUT_TOKENS` trong `backend/.env`.
   Khi chạy nhiều ứng dụng AI cùng máy, tránh cấu hình Ollama mặc định
   131072 token × 4 lượt song song vì có thể chiếm hết RAM/VRAM.

4. **Kiểm tra hoạt động**:
   - Giao diện web luyện nói: [http://localhost:8000](http://localhost:8000) — bắt đầu buổi trò chuyện hoặc IELTS Part 2, gõ câu trả lời hay cho phép microphone để ghi âm.
   - Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
   - Chạy bộ test backend (không cần bật Ollama; test dùng model giả ổn định và database tạm):
     ```bash
     .\venv\Scripts\python -m pytest tests -q
     ```
   - Muốn thử câu trả lời AI thật, khởi động Ollama và kiểm tra hội thoại qua app/API sau khi bộ test hợp đồng chạy qua.

---

## 📱 2. Khởi động ứng dụng Android (Jetpack Compose)

### Yêu cầu
- **Android Studio** (Koala / Ladybug hoặc mới hơn)
- **JDK 17** hoặc **JDK 21**
- Thiết bị thật hoặc Android Emulator (API 26+)

### Các bước mở và chạy app
1. Mở **Android Studio** $\rightarrow$ chọn **Open** $\rightarrow$ trỏ tới thư mục `android/`.
2. Chờ Android Studio đồng bộ Gradle (**Sync Project with Gradle Files**).
3. Cắm thiết bị Android hoặc bật máy ảo Android Emulator.
4. Bấm nút **Run (Shift + F10)** để cài và mở ứng dụng.

### Cấu hình kết nối Backend trên App:
- **Nếu chạy trên Android Emulator**:
  - Mở app $\rightarrow$ bấm biểu tượng **Settings (⚙️)** góc trên bên phải.
  - Chọn preset: `http://10.0.2.2:8000/` $\rightarrow$ bấm **Test Connection** (sẽ hiện `Connected (ornith-1.5:9b)` màu xanh).
- **Nếu chạy trên điện thoại thật cắm dây / cùng Wifi**:
  - Nhập địa chỉ IP máy tính trong mạng LAN (ví dụ: `http://192.168.1.15:8000/`) $\rightarrow$ bấm **Test Connection**.

### Triển khai production bằng Docker
- Sao chép `.env.example` thành `.env`, đặt `ENVIRONMENT=production`, tạo `API_KEY` và `AUTH_SECRET` bằng hai secret ngẫu nhiên riêng biệt (mỗi secret tối thiểu 32 ký tự), rồi thay `CORS_ORIGINS` bằng đúng origin được phép.
- Cấu hình chứng chỉ TLS tại `docker/ssl/fullchain.pem` và `docker/ssl/privkey.pem`, sau đó bật Nginx TLS bằng profile `proxy`:
  ```bash
  docker compose --profile proxy up -d --build
  ```
- Nếu cần chấm phát âm thử nghiệm bằng mô hình tiếng Anh, cấu hình `PRONUNCIATION_ASSESSOR_URL=http://pronunciation-assessor:9000` rồi bật thêm profile `pronunciation` (ví dụ: `docker compose --profile proxy --profile pronunciation up -d --build`). Mô hình tải về khi chạy lần đầu và cần dung lượng/CPU đáng kể.
- Với Android release, cấu hình ký bằng `ANDROID_KEYSTORE_PATH`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`. Người học đăng nhập bằng tài khoản; không đưa `API_KEY` hoặc `AUTH_SECRET` vào APK. Bản release chặn HTTP không mã hóa.
- Trong Settings, người học có thể tạo tài khoản/đăng nhập để đồng bộ phiên học, sổ tay lỗi và tiến trình giữa thiết bị. Tài khoản hiện chưa có xác minh email hoặc khôi phục mật khẩu; dùng trên hệ thống production cần cấu hình quy trình này trước khi mở đăng ký công khai.
- GitHub Actions tự build backend image và Android debug APK khi push/PR lên `main`. Deploy thủ công cần tạo GitHub Actions secrets `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_PATH`, `DEPLOY_SSH_KEY`, `DEPLOY_KNOWN_HOSTS`; máy chủ phải có checkout repo, file `.env`, Docker Compose, chứng chỉ TLS và quyền pull repo.
- Có thể bật crash reporting trên backend bằng `SENTRY_DSN` và trên Android bằng GitHub Actions variable `SENTRY_ANDROID_DSN`. Cả hai tắt PII; Android cũng tắt screenshot, view hierarchy và breadcrumb tương tác. Cần công bố thông báo quyền riêng tư phù hợp trước khi bật gửi telemetry.

## 🧪 3. Kiểm thử người học

Sau khi cài Android debug app và kết nối backend, dùng [pilot checklist](docs/13_PILOT_TEST_CHECKLIST.md) để quan sát 3–5 người học hoàn thành một lượt luyện. Backend CI dùng model giả cho kết quả ổn định; pilot kiểm tra phản hồi AI thật và trải nghiệm trên thiết bị.

---

## 🎯 3. Tính năng Phase 1 Core MVP

- **Lựa chọn chế độ**: Daily Practice, IELTS Speaking, Free Talk, Fix My English.
- **Nhập/Nói theo chủ đề**: Gợi ý các chủ đề quen thuộc (Travel, Hometown, Work & Study...).
- **Thu âm giọng nói**: Nút Micro lớn với hiệu ứng xung nhịp khi đang ghi âm.
- **Chuyển ngữ & Trò chuyện**: AI lắng nghe, phản hồi tự nhiên và gợi mở câu hỏi tiếp theo.
- **Phát hiện & Sửa lỗi ngữ pháp tức thì**: Thẻ sửa lỗi trực quan (hiển thị câu sai màu đỏ, câu sửa màu xanh kèm giải thích ngắn gọn).
- **Phát âm AI (Text-To-Speech)**: Tự động đọc câu trả lời của AI Coach qua giọng nói trên thiết bị.
- **Lưu trữ lịch sử**: Toàn bộ phiên học và lượt thoại được ghi nhận vào SQLite `backend/data/app.db`.

---

## 🎓 4. Tính năng Phase 2 AI Tutor (Gia sư AI)

- **Cấu hình mức độ sửa lỗi (Correction Level)**:
  - `Important (Khuyên dùng)`: Sửa các lỗi ngữ pháp và từ vựng quan trọng.
  - `Aggressive (Nghiêm ngặt)`: Bắt lỗi chi tiết từ giới từ, chia thì, cấu trúc vụng.
  - `None (Tự do)`: Chỉ đàm thoại trôi chảy, không sửa lỗi.
- **Luồng luyện nói lại "Say-it-again"**: Thẻ gợi ý câu nói chuẩn để học viên bấm nghe lại qua TTS và thực hành nhắc lại ngay lập tức.
- **Sổ tay lỗi sai (Mistake Notebook)**:
  - Tự động thống kê các lỗi ngữ pháp/từ vựng học viên mắc phải.
  - Tự động tăng đếm số lần lặp lại (`occurrence_count`) khi mắc lại lỗi cũ.
  - Phân loại tab: **Top lỗi hay lặp lại** và **Tất cả lỗi đã mắc**.
  - Tính năng đánh dấu "Đã hiểu/Khắc phục" (Mark as Resolved).

---

## 🏆 5. Tính năng Phase 3 IELTS Speaking Engine (Phòng thi IELTS & Chấm điểm Band)

- **4 Chế độ thi IELTS chuyên biệt**:
  - **Part 1 (Introduction & Interview)**: Hỏi đáp nhanh 4-5 câu hỏi cá nhân theo chuẩn đề thi thật.
  - **Part 2 (Long Turn / Cue Card)**: Thẻ chủ đề với 4 gợi ý, đếm ngược **60 giây chuẩn bị** và **120 giây nói liên tục** (không ngắt lời/không sửa lỗi trong lúc nói).
  - **Part 3 (Two-way Discussion)**: Giám khảo AI hỏi thảo luận chuyên sâu, phản biện học thuật từ chủ đề Part 2.
  - **Full Mock Test**: Mô phỏng toàn diện buổi thi thật 11–14 phút qua cả 3 phần.
- **Hệ thống chấm điểm Band Score AI (Ollama Evaluator)**:
  - Ước lượng Band điểm theo 3 tiêu chí chính thức: **Fluency & Coherence**, **Lexical Resource**, **Grammatical Range & Accuracy**.
  - Bảng điểm chi tiết: Điểm tổng (Overall Band Score từ 1.0 đến 9.0), nhận xét từng tiêu chí, danh sách điểm mạnh (Strengths) và điểm cần cải thiện (Areas for Improvement).
    - **Gợi ý nâng Band từ vựng (Vocabulary Upgrades)**: Bảng đối chiếu từ câu nói của thí sinh sang cách diễn đạt Band 7.5+ học thuật.
  - Lưu ý bảo chứng chuẩn: *"Estimated score — not an official IELTS result."*

---

## 📈 6. Tính năng Phase 4: Tiến trình & Lộ trình thích ứng (Progress & Adaptive Learning)

- **Theo dõi chỉ số chuyên sâu (KPI Tracking)**:
  - **Chuỗi ngày học liên tục (Streak 🔥)**: Tự động tính toán số ngày duy trì luyện tập liên tục.
  - **Thời lượng luyện nói (Speaking Time)**: Tổng số phút nói thực tế tích lũy qua các buổi học.
  - **Tốc độ nói trung bình (WPM - Words Per Minute)**: Thước đo chỉ số lưu loát và tự tin.
  - **Ước lượng Band hiện tại**: Cập nhật điểm ước tính mới nhất từ các bài thi thử IELTS.
- **Biểu đồ hoạt động tuần (7-Day Activity Chart)**:
  - Trực quan hóa số phút luyện nói trong 7 ngày gần nhất ngay trên giao diện Android.
  - Thống kê chi tiết số lượt phiên và số lỗi phát sinh theo từng ngày.
- **Lộ trình cá nhân hóa hàng ngày do AI tạo (AI Adaptive Daily Plan)**:
  - AI phân tích cơ sở dữ liệu các lỗi sai thường gặp nhất (`frequent_mistakes`) và các chủ đề vừa luyện.
  - Tự động sinh ra:
    - **Mục tiêu trọng tâm hôm nay (Today's Objective)**.
    - **Điểm yếu cần khắc phục (Weaknesses to Conquer)**.
    - **Mẫu câu thử thách cần áp dụng (Challenge Phrases to Master)**.
    - **Chủ đề khuyến nghị (Recommended Topic)**.
  - **Nút "Bắt đầu luyện tập ngay"**: Nhấn một chạm để tự động mở phòng luyện nói với chủ đề đề xuất.
- **Endpoints Backend**:
  - `GET /api/v1/progress/summary`: Trả về tổng quan KPI, streak, thời lượng, WPM, band điểm.
  - `GET /api/v1/progress/weekly`: Thống kê chi tiết 7 ngày liên tiếp.
  - `GET /api/v1/progress/adaptive-plan`: AI Ollama phân tích lỗi sai và đề xuất lộ trình luyện tập hôm nay.

---

## 🎙️ 7. Tính năng Phase 5: Phát âm

- **Đã có**: Whisper trả về timestamp và confidence nhận dạng cho từng từ; app dùng dữ liệu này để đánh dấu transcript có thể chưa chính xác. Đây không phải điểm phát âm.
- **Tra cứu IPA**: Từ điển cung cấp phiên âm, âm tiết, trọng âm và gợi ý luyện tập.
- **Chấm phát âm thử nghiệm (tùy chọn)**: Profile Docker `pronunciation` bật OpenPronounce để trả điểm âm thanh và lỗi âm vị tiếng Anh. Điểm này chưa được hiệu chuẩn cho IELTS hoặc người Việt, có thể báo lỗi sai và không phải band IELTS; nếu sidecar không bật/không sẵn sàng, API chỉ trả dữ liệu nhận dạng.
- **Bài luyện**: Hướng dẫn luyện tập chưa chấm âm thanh từng từ.
- **Endpoints Backend**:
  - `POST /api/v1/pronunciation/analyze`: Tổng hợp confidence/timestamp nếu có; transcript đơn thuần không tạo điểm phát âm.
  - `GET /api/v1/pronunciation/dictionary/{word}`: Tra cứu phiên âm IPA, âm tiết, trọng âm và mẹo phát âm.
  - `POST /api/v1/pronunciation/drill`: Trả về hướng dẫn luyện tập, chưa chấm điểm âm thanh.
