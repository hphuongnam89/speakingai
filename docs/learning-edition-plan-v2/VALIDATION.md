# Kiểm tra bộ kế hoạch

Ngày: 06/11/2026. Phạm vi: chất lượng cấu trúc tài liệu, chưa triển khai ứng dụng.

## Đã kiểm tra bằng Node.js và assert

- 5 JSON parse được.
- 20 task ID duy nhất, mọi dependency trỏ tới task tồn tại, không có chu trình.
- Mỗi task có mục chi tiết tương ứng trong `08_TASKS.md`.
- Mọi task ban đầu là `planned`, không báo feature đã hoàn thành.
- Các tài liệu bắt buộc và đường dẫn schema/example tồn tại.
- Ví dụ lesson có các trường bắt buộc, đủ 8 loại step, step IDs không trùng.
- Evidence quote của từng item mẫu nằm trong stimulus tương ứng.
- Independent và transfer dùng stimulus khác nhau.
- Ví dụ content giữ `draft`, reviewer null, license chưa gán; không tự phát hành.
- Policy có review 2/7 ngày và không promotion từ completion/AI rewrite.

Đây là kiểm tra hợp đồng cơ bản, chưa phải chạy bộ validator JSON Schema Draft 2020-12 đầy đủ. T03 phải có validator thực và negative fixtures khi biến schema thành runtime contract.

## Rà soát giới hạn

- Không chạy code donor hoặc test sản phẩm trong lượt viết kế hoạch.
- Kết quả 53 backend tests là bằng chứng từ lần chạy trước trong phiên làm việc, không phải kết quả mới của gói V2.
- Không có người học/reviewer giả, band accuracy giả hoặc nội dung được tự gán human-approved.
- Quy tắc pilot và nguồn nghiên cứu được phân biệt; chưa chứng minh learning gain.
- Gói chỉ gồm tài liệu/schema/example; không có `.env`, DB, model weights hay recording.

Khi chỉnh tài liệu, cần kiểm lại dependencies, ID/reference, ví dụ và trạng thái. Khi triển khai, ghi kết quả mới ở handoff, không sửa bản ghi này thành báo cáo test sản phẩm.
