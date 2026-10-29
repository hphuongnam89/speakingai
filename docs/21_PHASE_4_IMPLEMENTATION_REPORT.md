# Phase 4 Implementation Report — Audio/STT Pipeline & Pronunciation Boundary

**Ngày hoàn thành:** 2026-10-27  
**Ưu tiên:** P0/P1  
**Trạng thái:** ✅ **COMPLETED & CLOSED**

---

## 1. Mục tiêu đã hoàn thành

1. **Phân định ranh giới học thuật chuẩn xác (Pronunciation Boundary Enforcement):**
   - Phân biệt rõ rệt giữa:
     - `recognition_confidence`: Tỷ lệ phần trăm độ tin cậy nhận diện chính tả của mô hình Whisper STT (dùng để phát hiện câu nghe không rõ).
     - `pronunciation_score`: Điểm âm học chấm phát âm (chỉ có khi kết nối mô hình acoustic assessor chuyên sâu). Khi không có assessor, trường này luôn được trả về là `None` để không đánh lừa người học.
     - `disclaimer`: Tuyên bố miễn trừ trách nhiệm học thuật: *"Whisper confidence is not pronunciation accuracy. The optional OpenPronounce score is experimental, English-focused, and is not an IELTS result."*
   - Trên Frontend [app.js](file:///c:/Users/Hp/Downloads/ielts_speaking_ai_masterplan/backend/web/app.js), sửa nhãn hiển thị thành `🎯 Nhận diện chữ: ...% tin cậy (STT Confidence)`, chấm dứt việc gán nhãn sai là "Điểm phát âm".
2. **Chuẩn hóa Metrics Audio thời lượng thật:**
   - [WhisperService](file:///c:/Users/Hp/Downloads/ielts_speaking_ai_masterplan/backend/app/services/stt/whisper_service.py) tính toán chính xác:
     - `total_duration_ms`: Tổng thời lượng file ghi âm.
     - `speaking_duration_ms`: Thời gian người học thực sự phát âm (loại bỏ các khoảng im lặng).
     - `wpm`: Tốc độ nói tính theo `speaking_duration` thật.
     - `long_pauses`: Số khoảng ngập ngừng ngắc ngứ kéo dài > 1.5 giây.
     - `filler_count`: Số lượng từ đệm (`um`, `uh`, `like`, `you know`).
3. **Kiểm soát & Bảo vệ Microphone (Mic Preflight & Error Recovery):**
   - Bắt và xử lý chuyên sâu các mã lỗi thiết bị:
     - `NotAllowedError` / `PermissionDeniedError`: Hiển thị hướng dẫn mở quyền Micro tại biểu tượng ổ khóa 🔒 của trình duyệt.
     - `NotFoundError`: Hướng dẫn kiểm tra giắc cắm hoặc tai nghe micro.
   - Loại bỏ hoàn toàn các thông báo `alert()` thô, tích hợp chỉ dẫn phục hồi trực tiếp trên thanh trạng thái.
4. **Kiểm tra Fail-Fast Content Type & Giới hạn tải lên:**
   - Trong [speech.py](file:///c:/Users/Hp/Downloads/ielts_speaking_ai_masterplan/backend/app/api/speech.py), kiểm tra Content-Type ngay lập tức (Fail-Fast HTTP 415), kiểm tra giới hạn dung lượng `MAX_AUDIO_BYTES` (HTTP 413) và giới hạn độ dài `MAX_AUDIO_DURATION_MS` (HTTP 413).

---

## 2. Kết quả kiểm thử tự động (Verification)

Bổ sung bộ test mới [test_phase4_audio_pipeline.py](file:///c:/Users/Hp/Downloads/ielts_speaking_ai_masterplan/backend/tests/test_phase4_audio_pipeline.py):
- `test_pronunciation_boundary_confidence_vs_score`: Kiểm tra `recognition_confidence` hợp lệ, `pronunciation_score` trả về `None` khi không có acoustic assessor, và cờ `needs_review` hoạt động đúng.
- `test_audio_metrics_calculation`: Kiểm tra độ chính xác của `speaking_duration_ms`, `long_pauses`, `filler_count` và `wpm`.
- `test_audio_upload_unsupported_content_type_rejected`: Kiểm tra chặn file không hợp lệ trả về HTTP 415.
- `test_audio_upload_invalid_session_rejected`: Kiểm tra tên session sai định dạng trả về HTTP 400.

Chạy `scripts/check.ps1`:
```text
41 passed, 1 warning in 12.06s
- Toàn bộ 41 bài test unit, integration, frontend & audio pipeline PASS sạch sẽ 100%.
- Cú pháp JavaScript app.js: 100% không lỗi.
```

---

## 3. Sẵn sàng cho Phase tiếp theo

Hệ thống đã đạt đầy đủ Definition of Done của Phase 4, sẵn sàng chuyển tiếp sang:
👉 **Phase 5 — IELTS engine đúng format** (Xây dựng State Machine chuẩn cho Part 1, Part 2 quản lý 60s chuẩn bị / 120s nói ở Backend, Part 3 tư duy phản biện 2 chiều, và luồng Full Mock 11–14 phút hoàn chỉnh).
