# 00 — Quy trình cho agent mới

## Khôi phục ngữ cảnh

- Xác định repository root từ môi trường; không hardcode đường dẫn máy tác giả.
- Đọc hướng dẫn hiện hành của repo và `README.md` của gói này.
- Xem `git status --short`, branch, HEAD, remote; phân biệt commit với thay đổi chưa commit.
- Đọc `tasks.json`, handoff gần nhất và kết quả test gần nhất nếu có.
- Chọn task có toàn bộ dependency đã đạt acceptance. Không tự đánh dấu task trước đã xong vì có file cùng tên.
- Nếu baseline khác, ghi chênh lệch và điều chỉnh mapping; giữ yêu cầu học tập và bảo toàn dữ liệu.

## Chu trình một task

1. Ghi task ID, mục tiêu, entry gate, phạm vi file và acceptance cần chứng minh.
2. Tìm implementation/caller/test/config liên quan; dùng cơ chế có sẵn.
3. Tạo thay đổi nhỏ nhưng đủ end-to-end: dữ liệu → service → API → UI → tests nếu task cần.
4. Test bằng DB tạm, fixture không có dữ liệu cá nhân, provider giả có kiểm soát.
5. Với task giao diện, mở trình duyệt và thực hiện luồng thật; HTTP 200/health không chứng minh UI sử dụng được.
6. Cập nhật task và handoff bằng kết quả thực tế, lệnh kiểm thử, lỗi còn lại.
7. Tiếp tục task đủ điều kiện tiếp theo trong phạm vi người dùng đã giao.

## Kỷ luật thay đổi

- Giữ các thay đổi người dùng đang làm; không reset, ghi đè DB, stash/drop hoặc commit hộ khi chưa được giao.
- Không merge hai lịch sử Git bằng `allow-unrelated-histories` để ghép sản phẩm.
- Ghi nguồn, SHA, license cho code/nội dung lấy từ BandReady; không copy toàn bộ rồi coi đã tích hợp.
- Không tự tắt authentication, CORS, ownership hoặc validation để UI hết báo lỗi.
- Không đưa API key, AUTH_SECRET, model weights, DB hoặc recording vào gói bàn giao/Git.
- Kiểm kê model đang có trước khi đề nghị tải; model alias local có thể khác registry.
- Giữ một backend, một hệ hồ sơ học viên và một cấu hình provider làm nguồn sự thật.
- Không tự đổi Python/FastAPI sang stack khác, hoặc đưa Electron thành điều kiện bắt buộc cho web.

## Khi bị chặn

Ghi rõ blocker, bằng chứng, bước độc lập còn làm được. Nếu thiếu human review, tiếp tục code/test với nội dung `draft`, không phát hành bài đó như nội dung đã duyệt. Nếu thiếu model/audio, dùng fixture trong test và hiện trạng thái chưa sẵn sàng ở UI; không báo đã thử AI/microphone thật.

Nếu hệ thống từ chối một thao tác, tuân theo lý do từ chối; không đạt cùng kết quả bằng đường vòng. Quyết định mở rộng phạm vi sản phẩm, phá dữ liệu hoặc gửi thông tin ra ngoài phải có quyền phù hợp.

## Báo cáo tối thiểu

`Task → kết quả → file đổi → checks đã chạy → checks chưa chạy → vấn đề còn lại → task tiếp theo`.

Mỗi agent phải đọc được handoff mà không cần biết nội dung cuộc chat trước.
