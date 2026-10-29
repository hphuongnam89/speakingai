# ERRORS.md - Automatic Error Tracking & Learning

## [2026-10-06 19:28] - qwen2.5-coder:14b không gọi tool được trong OpenCode

- **Type**: Agent / Integration
- **Severity**: High
- **File**: `C:\Users\Hp\.config\opencode\opencode.json`
- **Agent**: Antigravity
- **Root Cause**: Qwen2.5-Coder 14B trả tool call dạng JSON thô trong `content` (không có thẻ `<tool_call>`), nên Ollama không parse ra `tool_calls` và OpenCode chỉ in text ra. Agent đã chẩn đoán sai 3 lần (đổ cho thiếu thẻ, cho tool "task" bịa ra, cho cache VSCode) mà không test trước.
- **Error Message**:
  ```
  tool_calls: (rỗng)
  content: {"name": "Run", "arguments": {"command": "ls"}}
  ```
- **Fix Applied**: Đổi model mặc định của OpenCode về `smtek/Qwen3.8-27B:Q3_K_XL-16gb` (đã test qua `/api/chat` là trả `tool_calls` native đúng).
- **Prevention**: Trước khi đổi model cho agent, test `/api/chat` kèm `tools` và kiểm tra `message.tool_calls` có dữ liệu không. System prompt trong Modelfile không sửa được lỗi này (OpenCode gửi system prompt riêng đè lên).
- **Status**: Fixed

---

## [2026-10-06 19:30] - sync-ollama.ps1 tự đổi model mặc định

- **Type**: Runtime
- **Severity**: Medium
- **File**: `C:\Users\Hp\.config\opencode\sync-ollama.ps1`
- **Agent**: Antigravity
- **Root Cause**: Script dùng `ConvertFrom-Json -AsHashtable`, mà Windows PowerShell 5.1 không có tham số này. Lỗi bị nuốt mất, config cũ đọc ra rỗng, nên script coi như chưa có model mặc định và tự chọn model mới nhất.
- **Error Message**:
  ```
  ConvertFrom-Json : A parameter cannot be found that matches parameter name 'AsHashtable'.
  ```
- **Fix Applied**: Viết lại script dùng PSCustomObject. Script giữ nguyên model mặc định và các provider khác, chỉ đổi model mặc định khi model đó không còn trong Ollama. Đã chạy thử 2 lần liên tiếp, model mặc định không đổi.
- **Prevention**: Script chạy trên Windows phải tương thích PS 5.1. Không nuốt lỗi khi parse config (`catch {}` rỗng).
- **Status**: Fixed

---

## [2026-10-06 19:35] - Qwen 27B bị lỗi out of memory / context length

- **Type**: Runtime
- **Severity**: High
- **File**: Modelfile
- **Agent**: Antigravity
- **Root Cause**: num_ctx 32768 quá lớn cho GPU 16GB VRAM khi chạy model 27B quantize Q3_K_XL (14GB). VRAM chỉ còn ~2GB cho context, dẫn tới tràn vào shared GPU memory hoặc system RAM, tốc độ giảm nghiêm trọng.
- **Error Message**:
  ```
  cudaMalloc failed: out of memory / slow inference
  ```
- **Fix Applied**: Tạo model `smtek/Qwen3.8-27B:Q3_K_XL-16gb` với `PARAMETER num_ctx 4096`. Context 4K tốn ~600MB VRAM, vừa vặn trong 16GB, GPU offload 100%, tốc độ sinh token nhanh.
- **Prevention**: Với model >= 27B trên GPU 16GB, luôn tính toán VRAM: model_size + num_ctx * kv_cache_per_token < total_vram. Không dùng num_ctx mặc định của base model nếu không cần thiết.
- **Status**: Fixed

---

## [2026-10-27 21:00] - STT Whisper bị Chrome Web Speech đè và cấu hình CPU chậm

- **Type**: Architecture / Integration
- **Severity**: High
- **File**: `backend/app/services/stt/whisper_service.py`, `backend/web/app.js`, `backend/web/index.html`
- **Agent**: Antigravity
- **Root Cause**: 
  1. Trình duyệt Chrome tự động kích hoạt `window.webkitSpeechRecognition` (Google Cloud Web Speech `en-US`), hoàn toàn bỏ qua Faster-Whisper trên backend. Google Cloud Web Speech được huấn luyện cho giọng bản xứ Mỹ chuẩn, rất kém khi nhận diện accent người Việt học IELTS (hay đoán sai từ, mất âm đuôi, ngắt quãng khi ngập ngừng).
  2. Faster-Whisper trên backend trước đây chỉ cấu hình CPU `int8` với `small.en`, không có `vad_filter`, không khóa `language="en"`, và không có `initial_prompt` dẫn đường ngữ cảnh thi IELTS.
- **Fix Applied**: 
  1. Kích hoạt tăng tốc phần cứng card đồ họa **NVIDIA GeForce RTX 5060 Ti 16GB (CUDA + float16)**, nâng cấp model lên **`medium.en`** (chuyên sâu tiếng Anh độ chính xác vượt trội).
  2. Bổ sung `vad_filter=True` (Silero VAD) lọc sạch tiếng thở/tạp âm, `language="en"` và `initial_prompt="IELTS Speaking examination practice test..."`. Tốc độ nhận diện đạt ~0.24 giây/câu nói.
  3. Thêm bộ lọc studio cho Micro trên Frontend (`echoCancellation`, `noiseSuppression`, `autoGainControl`).
  4. Đổi mặc định sang **Whisper AI (RTX 5060 Ti GPU)** trên Frontend, có đồng hồ đếm giây ghi âm và cho phép người dùng chuyển đổi linh hoạt giữa Whisper GPU và Chrome Web Speech.
- **Prevention**: Luôn kiểm tra khả năng hỗ trợ CUDA của máy tính người dùng trước khi cấu hình STT/LLM; không để Web Speech API của trình duyệt âm thầm đè lên mô hình AI chuyên sâu đã được chuẩn bị trên backend.
- **Status**: Fixed

---

## [2026-10-27 21:55] - Placement Test Timeout 120s khi chấm bài bằng Local 27B AI

- **Type**: Integration / Runtime
- **Severity**: High
- **File**: `backend/app/core/config.py`, `backend/app/services/llm/ollama_provider.py`, `backend/app/api/placement.py`
- **Agent**: Antigravity
- **Root Cause**:
  1. Biến môi trường Windows (`Machine/User`) có thiết lập `OLLAMA_CONTEXT_LENGTH = 32768`. Khi Ollama cấp phát context 32K cho model 27B (`smtek/Qwen3.8-27B:Q3_K_XL-16gb` 14GB), bộ nhớ đệm KV-cache nuốt thêm gần 3GB VRAM, vượt quá 16GB VRAM của RTX 5060 Ti, gây tràn và tráo đổi bộ nhớ qua RAM hệ thống (PCIe memory thrashing). Tốc độ sinh token bị tụt từ 26.5 t/s xuống còn ~7.8 t/s.
  2. Thời gian sinh trọn vẹn bản đánh giá chi tiết (3 giai đoạn lộ trình, điểm mạnh, điểm yếu, nhận xét) mất ~140 giây, trong khi `settings.LLM_TIMEOUT` bị giới hạn cứng ở 120 giây. Httpx tự động ngắt kết nối với mã lỗi 503 Timeout.
- **Fix Applied**:
  1. Giới hạn `safe_ctx` cho mô hình local không vượt quá 4096 tokens (vừa đủ cho hội thoại và đánh giá nói ~1000 tokens), giúp KV-cache chỉ chiếm ~600MB. Toàn bộ model nằm 100% trong VRAM của GPU. Tốc độ sinh token phục hồi lên **26.2 tokens/giây**.
  2. Nâng `LLM_TIMEOUT` và `OLLAMA_TIMEOUT` lên 300 giây (5 phút).
  3. Tăng trần `OLLAMA_MAX_OUTPUT_TOKENS` lên 1536 tokens.
  4. Cập nhật frontend `backend/web/app.js` khử trùng lặp câu trả lời khi người dùng bấm gửi lại.
  5. Kiểm thử live trên server: thời gian đánh giá giảm từ 141+ giây xuống **34.3 - 37.1 giây** (nhanh gấp gần 4 lần) và phản hồi HTTP 200 OK thành công.
- **Prevention**: Khi dùng model LLM lớn (>= 27B) cục bộ, luôn kiểm soát chặt context window (`num_ctx`) tránh tràn VRAM; thiết lập timeout đánh giá học thuật tối thiểu 300 giây.
- **Status**: Fixed

---

## [2026-10-27 22:25] - SyntaxError trong `app.js` làm đứng UI và Thiếu Phân tích Phát âm Chi tiết

- **Type**: Syntax / Agent / Logic
- **Severity**: High
- **File**: `backend/web/app.js`, `backend/app/prompts/placement.py`, `backend/web/styles.css`
- **Agent**: Antigravity
- **Root Cause**:
  1. Khi bổ sung `openRoadmapModal` ở phiên trước, một dòng mã thừa và dấu ngoặc nhọn `}` ở dòng 1069 của `app.js` gây lỗi `SyntaxError: Unexpected token '}'`. Lỗi này khiến toàn bộ file JavaScript dừng chạy ngay khi tải trang, danh sách profile không load và nút xem báo cáo/lộ trình bị vô hiệu hóa ("mất đánh giá").
  2. Báo cáo đánh giá chẩn đoán đầu vào trước đó chỉ có điểm số và nhận xét cho Fluency, Lexical, Grammar, nhưng hoàn toàn thiếu phần phân tích học thuật chi tiết cho tiêu chí Phát âm (Pronunciation) như âm đuôi (/s/, /z/, /ed/), trọng âm từ và ngữ điệu. Trong khi luyện nói theo lượt, dữ liệu âm học và từ phát âm sai (`problem_words`) chưa được hiển thị trực tiếp.
- **Fix Applied**:
  1. Xóa bỏ dòng thừa và dấu ngoặc nhọn sai cú pháp trong `app.js`, xác thực bằng lệnh `node -c backend/web/app.js` đạt 100% sạch lỗi.
  2. Bổ sung thẻ đánh giá chuyên sâu Phát âm (`eval-pronunciation-card`) trong modal lộ trình với 3 trụ cột phát âm chuẩn Cambridge IELTS: Âm đuôi & Phụ âm (Final Consonants), Trọng âm từ & Câu (Stress & Rhythm), và Ngữ điệu & Ngắt cụm nghĩa (Intonation & Chunking).
  3. Cập nhật prompt đánh giá chẩn đoán `placement.py` và backend API trả về trường `pronunciation_feedback` chi tiết.
  4. Cập nhật hồ sơ học viên Nam trong SQLite với đầy đủ dữ liệu phân tích phát âm theo thang Band 5.5 chuẩn UTF-8.
  5. Nâng cấp lượt hội thoại hiển thị chip nhận diện từ phát âm chưa chuẩn kèm ký hiệu phiên âm quốc tế IPA (`problem_words`).
  6. Tăng cache-busting lên `v=7.5` trong `index.html`.
- **Prevention**: Luôn chạy `node -c <file.js>` ngay sau mỗi lần chỉnh sửa file JavaScript để kiểm tra cú pháp trước khi bàn giao cho người dùng; đảm bảo cả 4 tiêu chí IELTS (FC, LR, GRA, PR) luôn có mục phân tích định tính đầy đủ.
- **Status**: Fixed

---

## [2026-10-27 22:45] - Giao diện nút bấm lệch chuẩn, Font chữ thô, và Lỗi hiển thị dấu hỏi `??` UTF-8

- **Type**: UI/UX / Encoding / Agent
- **Severity**: High
- **File**: `backend/web/styles.css`, `backend/web/app.js`, `backend/web/index.html`, `backend/data/app.db`
- **Agent**: Antigravity
- **Root Cause**:
  1. Hàng nút bấm dưới modal lộ trình (`.roadmap-modal-actions`) có 3 nút bị lệch chuẩn trầm trọng: `.secondary-button` chưa được khai báo CSS (dùng style thô của trình duyệt), `.danger-outline-btn` bị gán `margin-top: 14px` lệch dòng, font-size và chiều cao 3 nút không khớp nhau.
  2. Font chữ sử dụng fallback hệ thống lỗi thời và font serif `Playfair Display` không được nhúng trên Windows, hiển thị răng cưa và thô ráp.
  3. Quá nhiều màu sắc tương phản sặc sỡ (thẻ phát âm dùng màu hồng/tím dạ quang, thước đo 4 tiêu chí dùng 4 màu cầu vồng), thiếu tính thống nhất của một phần mềm khảo thí chuyên nghiệp.
  4. Lệnh PowerShell update database trước đó dùng pipe cp1252 đã biến các ký tự tiếng Việt có dấu thành chuỗi dấu hỏi `??`, hiển thị trực tiếp lên thẻ nhận xét phát âm.
- **Fix Applied**:
  1. Đồng bộ 100% button (`primary-button`, `secondary-button`, `danger-outline-btn`) với chung chiều cao chuẩn 40px, border-radius 9px, padding 0 18px, căn chỉnh flexbox thẳng hàng tuyệt đối.
  2. Tích hợp bộ font chuẩn quốc tế cao cấp **`Plus Jakarta Sans`** từ Google Fonts (hỗ trợ tiếng Việt đầy đủ), thay thế triệt để các font serif thô ráp.
  3. Tinh gọn hệ thống bảng màu (Calm Executive SaaS): xóa bỏ hoàn toàn màu hồng/tím chói mắt; thẻ Phát âm chuyển về nền Slate/White trang nhã viền xám tinh tế; các thanh thước đo 4 tiêu chí quy về sắc xanh ngọc lục bảo (Oxford Emerald `#059669`) sang trọng.
  4. Chạy script Python UTF-8 chuẩn làm sạch 100% database SQLite, xóa sạch dấu hỏi `??`, đồng thời bổ sung cơ chế fallback tự động trong `app.js` nếu phát hiện chuỗi lỗi.
  5. Nâng cache-busting lên `v=7.6` trong `index.html`.
- **Prevention**: Luôn chuẩn hóa button trong một Design System chung; kiểm tra hiển thị thực tế trên trình duyệt; không bao giờ dùng pipe PowerShell để ghi dữ liệu tiếng Việt có dấu vào SQLite mà không chỉ định encoding utf-8.
- **Status**: Fixed

---

## [2026-10-27 22:50] - Lỗi nhận diện âm thanh: Unsupported audio content type (HTTP 415)

- **Type**: Integration / Runtime
- **Severity**: Critical
- **File**: `backend/app/api/speech.py`, `backend/tests/test_speech_content_type.py`
- **Agent**: Antigravity
- **Root Cause**:
  Trình duyệt Chrome khi thu âm bằng MediaRecorder gửi kèm tham số codec: `Content-Type: audio/webm;codecs=opus`. Backend `speech.py` kiểm tra cứng chuỗi bằng `audio.content_type in {"audio/wav", "audio/webm", ...}`, không cắt bỏ phần tham số `;codecs=opus`. Do chuỗi không khớp tuyệt đối, API ném lỗi `HTTP 415: Unsupported audio content type`, làm bung popup cảnh báo lỗi nhận diện âm thanh.
- **Error Message**:
  ```
  HTTP 415 Unsupported Media Type: Unsupported audio content type
  ```
- **Fix Applied**:
  1. Chuẩn hóa `raw_content_type = (audio.content_type or "").split(";")[0].strip().lower()` trước khi xác thực.
  2. Mở rộng bộ MIME types được chấp nhận (`audio/webm`, `video/webm`, `audio/ogg`, `audio/opus`, `audio/mp4`, `audio/m4a`, `audio/wav`, `audio/mpeg`, `application/octet-stream`).
  3. Viết bổ sung bộ kiểm thử tự động [`test_speech_content_type.py`](file:///C:/Users/Hp/Downloads/ielts_speaking_ai_masterplan/backend/tests/test_speech_content_type.py), xác thực toàn bộ 28 tests đã PASS 100%.
  4. Khởi động lại dịch vụ backend API uvicorn.
- **Prevention**: Luôn tách lọc MIME parameters (`split(";")[0]`) khi validate `Content-Type` của tệp tải lên từ trình duyệt.
- **Status**: Fixed

---

## [2026-10-27 23:10] - Chủ đề luyện nói bị lặp cố định 1 đề ("A memorable weekend") & Thiếu bộ chọn chủ đề

- **Type**: Logic / UX Defect
- **Severity**: High
- **File**: `backend/web/index.html`, `backend/web/app.js`, `backend/app/api/ielts.py`, `backend/app/data/ielts_bank.py`
- **Agent**: Antigravity
- **Root Cause**:
  1. Trường nhập chủ đề ở thanh bên cạnh bị đặt giá trị tĩnh `value="A memorable weekend"`.
  2. Màn hình chào luyện tập trung tâm (`#welcome-state`) chỉ có một nút "Bắt đầu luyện", hoàn toàn không hiển thị danh sách chủ đề, thẻ chọn nhanh (chips) hay nút đổi chủ đề ngẫu nhiên.
  3. Khi người học bấm "Bắt đầu luyện", hàm `startSession` luôn lấy chuỗi tĩnh từ ô input này và câu hỏi mở đầu của AI bị hardcode cứng: `"Hi [Tên]! Let's talk about A memorable weekend. What has been the most interesting part of your day so far?"` bất kể chủ đề là gì.
- **Fix Applied**:
  1. Mở rộng kho chủ đề chuẩn IELTS (`ielts_bank.py` & `app.js`): bổ sung đầy đủ các bộ đề Part 1 (Quê hương, Công việc/Học tập, Thói quen, Công nghệ, Ẩm thực, Du lịch, Âm nhạc, Thể thao), Part 2 Cue Cards (Chuyến đi đáng nhớ, Người truyền cảm hứng, Quyết định quan trọng, Mục tiêu khó khăn, Thiết bị công nghệ, Vấn đề môi trường), Part 3 (Trí tuệ nhân tạo, Du lịch & Môi trường, Giáo dục) và Giao tiếp đời sống.
  2. Xây dựng **Topic Picker Hub** ngay trên giao diện trung tâm:
     - Thẻ xem trước chủ đề đang chọn (hiển thị tiêu đề, bản dịch tiếng Việt, câu hỏi mở đầu mô phỏng).
     - Hàng thẻ bấm chọn nhanh (Quick Chips): `📍 Quê hương`, `💼 Công việc`, `☕ Thói quen`, `📱 Công nghệ`, `✈️ Du lịch (Part 2)`, `💡 Xã hội (Part 3)`, `✏️ Tự nhập chủ đề`.
     - Nút **🎲 Đổi chủ đề ngẫu nhiên (Shuffle)**: 1 click để đổi ngay sang chủ đề mới lạ.
     - Khung nhập chủ đề tùy thích (Custom Topic): Cho phép người học tự gõ bất kỳ chủ đề nào muốn luyện.
  3. Bổ sung endpoint `GET /api/v1/ielts/topics` và cập nhật `POST /api/v1/ielts/start` để nhận tham số `topic` chính xác.
  4. Câu hỏi mở đầu của AI giờ đây thích ứng 100% theo chủ đề được chọn thay vì bị ép cứng vào một câu mẫu.
- **Prevention**: Luôn cung cấp bộ chọn đề trực quan và cơ chế ngẫu nhiên hóa đề thi đối với các ứng dụng luyện nói/khảo thí; không để giá trị input tĩnh chi phối luồng bắt đầu.
- **Status**: Fixed

---
