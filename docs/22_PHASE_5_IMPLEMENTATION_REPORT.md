# Phase 5 Implementation Report — IELTS Engine Format & State Machine

**Ngày hoàn thành:** 2026-10-27  
**Ưu tiên:** P0  
**Trạng thái:** ✅ **COMPLETED & CLOSED**

---

## 1. Mục tiêu đã hoàn thành

1. **State Machine chuẩn cho Full Mock Test (Part 1 → Part 2 → Part 3 → Evaluation):**
   - Chuyển đổi toàn diện từ "chat rời rạc theo chủ đề" sang cỗ máy trạng thái mô phỏng kỳ thi IELTS thực tế (11–14 phút):
     - **Part 1 (Phỏng vấn làm quen):** Giám khảo hỏi tuần tự 4 câu hỏi thuộc chủ đề thân thuộc (Hometown, Work/Studies, Routine,...). Không sửa lỗi ngắt lời trong lúc thí sinh đang trả lời.
     - **Chuyển tiếp tự nhiên sang Part 2:** Khi kết thúc câu thứ 4 của Part 1, Giám khảo tự động chuyển đoạn trang trọng và trao Cue Card với đầy đủ 4 bullet points gợi ý chuẩn đề thi.
     - **Part 2 (Bài nói độc thoại):** Kiểm soát thời gian nói, phát hiện và cảnh báo nếu thí sinh nói dưới 1 phút.
     - **Chuyển tiếp sang Part 3 (Thảo luận phản biện chuyên sâu):** Giám khảo tự động dẫn dắt từ câu chuyện cá nhân ở Part 2 sang 3 câu hỏi thảo luận xã hội 2 chiều (nguyên nhân/hệ quả, so sánh, tương lai).
     - **Kết thúc kỳ thi:** Chỉ sau khi hoàn thành cả 3 phần, Giám khảo mới kết luận và mở cổng nhận bảng điểm đánh giá chi tiết.
2. **Khóa bảo vệ chấm điểm (Premature Evaluation Guard):**
   - Chặn tuyệt đối việc gọi API `/ielts/evaluate/{session_id}` khi bài thi Full Mock chưa hoàn thành đầy đủ 3 phần. Trả về mã lỗi HTTP 400 `FULL_MOCK_INCOMPLETE`.
3. **Kiểm soát thời gian nói Part 2 (Timing Control & Feedback):**
   - Backend tự động đo lường thời lượng bài nói. Nếu bài nói dưới 75 từ (tương đương < 1 phút), hệ thống gửi kèm cảnh báo học thuật:
     *"⚠️ Cảnh báo thời gian: Bài nói dưới 1 phút. Trong kỳ thi IELTS Part 2 thực tế, bạn cần nói liên tục từ 1-2 phút (100-150 từ) để đạt tiêu chí Fluency."*
4. **Loại bỏ Hardcode Speaking Minutes:**
   - Thay thế việc gán cứng `2.5 phút` trong cơ sở dữ liệu bằng việc tính toán thời lượng nói thực tế `actual_speaking_minutes` từ âm thanh và số lượng từ nói ra của thí sinh trong suốt các phần thi.

---

## 2. Kết quả kiểm thử tự động (Verification)

Bổ sung bộ test mới [test_phase5_ielts_state_machine.py](file:///c:/Users/Hp/Downloads/ielts_speaking_ai_masterplan/backend/tests/test_phase5_ielts_state_machine.py):
- `test_part2_timing_warning_when_too_short`: Xác thực bài nói Part 2 dưới 1 phút bị cảnh báo timing và kết thúc lượt.
- `test_full_mock_evaluation_rejected_when_incomplete`: Xác thực việc chấm điểm bị từ chối với mã lỗi `FULL_MOCK_INCOMPLETE` nếu chưa hoàn thành cả 3 phần.
- `test_full_mock_state_machine_progresses_through_all_parts`: Mô phỏng toàn bộ luồng thi Full Mock: Part 1 (4 câu) ➔ Nhận Cue Card Part 2 ➔ Nộp bài Part 2 ➔ Chuyển tiếp Part 3 (3 câu) ➔ Hoàn tất toàn bộ kỳ thi.

Kết quả kiểm tra toàn hệ thống qua `scripts/check.ps1`:
```text
44 passed, 1 warning in 7.15s
- Cú pháp JavaScript app.js: 100% hợp lệ.
- Toàn bộ 44 bài test unit & integration PASS sạch sẽ 100%.
```

---

## 3. Sẵn sàng cho Phase tiếp theo

Hệ thống đã đạt đầy đủ Definition of Done của Phase 5, sẵn sàng chuyển tiếp sang:
👉 **Phase 6 — IELTS pedagogy và AI tutor** (Phương pháp sư phạm "One Focus per Session", phân loại lỗi theo band rubric 4.5–5.0/5.5–6.0/6.5–7.0, bài tập thực hành lại ngay sau khi sửa lỗi).
