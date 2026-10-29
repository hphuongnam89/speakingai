# Phase 2 Implementation Report — Core Conversation Reliability

**Ngày hoàn thành:** 2026-10-27  
**Ưu tiên:** P0  
**Trạng thái:** ✅ **COMPLETED & CLOSED**

---

## 1. Mục tiêu đã hoàn thành

1. **Khử trùng lặp lượt nói (Turn Idempotency):**
   - Bổ sung `client_turn_id` vào `TurnModel` và migration marker `003_turn_client_turn_id`.
   - Bổ sung `request_id` vào schema `ConversationRequest`.
   - Khi client retry (hoặc người học bấm gửi liên tiếp), backend nhận cùng `request_id` sẽ trả lại kết quả đã cache của lượt đó mà không gọi lại LLM và không tạo bản ghi trùng lặp trong database.
2. **Khóa phiên đã kết thúc (Session Finish Guard):**
   - Chặn tuyệt đối việc gửi câu trả lời hoặc gọi mô hình AI vào một session đã kết thúc (`ended_at IS NOT NULL`).
   - Trả về mã lỗi có cấu trúc `SESSION_ALREADY_FINISHED` (HTTP 400, `retryable: false`).
3. **Mã lỗi chuẩn hóa & Cơ chế phục hồi (Structured Error Codes & Recovery):**
   - Trả về mã lỗi định dạng JSON: `SESSION_NOT_FOUND`, `SESSION_ALREADY_FINISHED`.
   - Trên Frontend, loại bỏ hoàn toàn các thông báo lỗi thô hoặc `alert()`, hiển thị banner lỗi kèm nút **🔄 Thử lại (Retry)** giữ nguyên `requestId` để retry mượt mà.
4. **Quản lý trạng thái giao diện (UI State Machine):**
   - `setBusy(true)` khóa tức thì textarea, nút Ghi âm và nút Gửi.
   - Nút Gửi hiển thị rõ trạng thái `AI đang nghĩ… ⏳` để người học không bị hoang mang khi mô hình AI đang xử lý.

---

## 2. Kết quả kiểm thử tự động (Verification)

Bộ test mới [test_phase2_reliability.py](file:///c:/Users/Hp/Downloads/ielts_speaking_ai_masterplan/backend/tests/test_phase2_reliability.py) kiểm chứng 3 kịch bản:
- `test_session_already_finished_rejects_new_turn`: PASS (HTTP 400).
- `test_session_not_found_returns_structured_error`: PASS (HTTP 404).
- `test_idempotent_conversation_turn_retry`: PASS (Cùng `request_id` trả về đúng kết quả cũ, số lượng turn trong DB giữ nguyên 2).

Chạy `scripts/check.ps1`:
```text
33 passed, 1 warning in 7.38s
```
Toàn bộ 33 test unit & integration pass 100%. Cú pháp JavaScript `node -c app.js` đạt 0 lỗi.

---

## 3. Sẵn sàng cho Phase tiếp theo

Hệ thống đã đạt đầy đủ Definition of Done của Phase 2, sẵn sàng chuyển tiếp sang:
👉 **Phase 3 — Frontend quality và accessibility** (Tách module `app.js`, bàn phím điều hướng, focus trap modal, auto-scroll, contrast).
