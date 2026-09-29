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

4. **Kiểm tra hoạt động**:
   - Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
   - Chạy test full flow hội thoại:
     ```bash
     .\venv\Scripts\python tests/test_full_flow.py
     ```

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

## 🎙️ 7. Tính năng Phase 5: Phân tích phát âm & Luyện âm chuyên sâu (Pronunciation Engine)

- **Nguyên tắc chất lượng**: Phân tích phát âm trực tiếp từ tín hiệu âm học và nhận dạng tiếng nói, không phán đoán phát âm mù chỉ qua văn bản chữ.
- **Chấm điểm chi tiết từng từ (Word-Level Confidence & Timestamps)**:
  - Đo độ tin cậy âm học (0.0 – 1.0) cho từng từ được nói ra.
  - Tự động gắn nhãn `needs_review: true` khi từ có độ tự tin thấp (< 0.80) hoặc gặp lỗi phát âm âm cuối, phụ âm đôi.
- **Từ điển ngữ âm & Phiên âm quốc tế IPA chuẩn**:
  - Tra cứu và sinh phiên âm IPA chuẩn xác (ví dụ: `enjoyed` $\rightarrow$ `/ɪnˈdʒɔɪd/`, `technology` $\rightarrow$ `/tɛkˈnɒlədʒi/`).
  - Bẻ từ theo âm tiết (Syllable breakdown) và đánh dấu trọng âm chính (`en - JOYED`, `tech - NOL - o - gy`).
  - Đưa ra lời khuyên âm học cụ thể (Phonetic Feedback Tip).
- **Phân tích nhịp điệu & ngắt nghỉ (Rhythm Metrics)**:
  - Tốc độ phát âm (WPM).
  - Đếm số lần ngắt nghỉ bất thường (`pause_count`) và tỷ lệ thời gian im lặng (`pause_duration_ratio`).
  - Điểm nhịp điệu tổng thể (`rhythm_consistency_score`).
- **Giao diện Android tương tác 1 chạm (Interactive Pronunciation Drill)**:
  - **Tô màu từ trực quan**: Các từ cần chú ý được hiển thị màu hổ phách/cam kèm biểu tượng cảnh báo `⚠️`.
  - **Hộp thoại luyện âm (Pronunciation Drill Dialog)**:
    - Bấm vào từ bất kỳ trên bóng hội thoại để mở bảng phân tích ngữ âm chi tiết.
    - Nút **"🔊 Listen"**: Nghe AI đọc mẫu chuẩn chậm và rõ ràng.
    - Nút **"🎙️ Practice"**: Luyện nói lại từ và nhận ngay điểm số tức thì kèm phân loại (Excellent / Good / Needs Practice) và câu mẫu ứng dụng.
- **Endpoints Backend**:
  - `POST /api/v1/pronunciation/analyze`: Phân tích phát âm chi tiết cho đoạn nói.
  - `GET /api/v1/pronunciation/dictionary/{word}`: Tra cứu phiên âm IPA, âm tiết, trọng âm và mẹo phát âm của từ.
  - `POST /api/v1/pronunciation/drill`: Chấm điểm bài luyện phát âm từng từ/cụm từ.




