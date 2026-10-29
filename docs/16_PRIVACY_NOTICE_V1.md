# Privacy Notice v1

Ứng dụng lưu profile, session, transcript, feedback và mistake notebook để cung cấp chức năng luyện tập. Recording audio chỉ được lưu trong thời gian cần thiết cho transcription/feedback hoặc đến `retention_at` đã cấu hình; file không cần giữ phải được xóa sau xử lý.

Người học phải biết khi microphone được dùng, mục đích xử lý và thời hạn lưu. Không gửi audio/transcript lên cloud nếu local-only được bật. Khi người học yêu cầu reset hoặc xóa profile, database records và audio liên quan phải được xóa cùng nhau.

Telemetry/crash reporting không được gửi request body hoặc PII. Các band/diagnostic hiển thị trong sản phẩm là estimate phục vụ luyện tập và không phải kết quả IELTS chính thức.

## Consent state
Consent cho audio là một trạng thái explicit ở client/backend contract. Nếu chưa consent, chỉ cho phép text input hoặc từ chối upload với lỗi ổn định.
