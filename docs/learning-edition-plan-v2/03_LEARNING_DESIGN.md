# 03 — Thiết kế dạy học và tiến bộ

## Đơn vị thiết kế

Thiết kế theo năng lực quan sát được. “Học Reading” quá rộng. “Sau đoạn 100 từ, chỉ ra câu nào diễn đạt quyết định cuối cùng và giải thích được dấu hiệu đổi ý” có thể dạy và kiểm tra.

Mỗi competency có ID/version, can-do statement, prerequisites, dạng ngữ liệu, lỗi thường gặp, phương pháp quan sát và giới hạn suy luận. Không gắn một band number cho mọi kiến thức nền.

## Chu trình một bài

| Bước | Người học làm gì | App/AI làm gì | Evidence |
|---|---|---|---|
| Mục tiêu/khởi động | Hiểu mục tiêu, thử câu ngắn nếu cần | Kết nối kiến thức cũ, chọn mức phù hợp | Chẩn đoán riêng, chưa quy kết mastery |
| Học nghĩa | Nghe/đọc ví dụ có ngữ cảnh | Giải thích vừa đủ, làm mẫu suy nghĩ | Exposure |
| Luyện có hướng dẫn | Trả lời từng phần | Hint tăng dần, giải thích khi cần | Assisted practice + hint log |
| Tự thực hiện | Làm nhiệm vụ mới không có gợi ý nội dung | Giảm hỗ trợ, chưa lộ mẫu/đáp án | Independent performance |
| Phản hồi/tự sửa | Sửa, ghi âm lại hoặc giải thích lại | Chọn lỗi trọng tâm, chỉ evidence | Correction uptake; không tính như lần độc lập mới |
| Vận dụng | Xử lý ngữ liệu/chủ đề khác | Giữ cùng mục tiêu, thay dữ kiện/bề mặt | Transfer evidence |
| Ôn lại | Nhớ và dùng lại sau khoảng thời gian | Lên lịch, kiểm tra bài chưa gặp | Delayed retention |

Khả năng truy cập không bị coi là hint: phóng chữ, keyboard, chỉ dẫn cách bấm không hạ independence. Transcript/audio mẫu, đáp án, gợi ý nghĩa và model answer có thể làm thay đổi điều đang đo; lưu rõ loại trợ giúp.

## Chẩn đoán nguyên nhân

Không suy ra nguyên nhân chỉ từ đúng/sai. Lưu `hypothesis`, `confirmed`, `unknown`, `not_assessable`, evidence và độ chắc chắn định tính.

Ví dụ nghe “Thursday” sai:

- Kiểm tra người học có hiểu từ viết không → phân biệt thiếu nghĩa từ với vấn đề nghe.
- Cho nghe cụm khác có từ đó → kiểm tra nhận diện âm/từ.
- Cho giải thích nội dung đoạn → phân biệt hiểu sai ý với chỉ sai spelling.
- Nếu mic/audio kém hoặc STT sai, đánh dấu chất lượng đầu vào, cho sửa transcript; không kết luận năng lực ngôn ngữ thấp.

Không bắt người học trả lời mọi probe. Dùng probe ngắn khi cần thay đổi cách dạy; nếu đủ evidence thì dạy ngay.

## Giảm trợ giúp

Hint 0 = không có trợ giúp nội dung; 1 = hướng chú ý; 2 = nhắc chiến lược/khái niệm; 3 = hướng dẫn từng bước; 4 = đáp án/mẫu hoàn chỉnh.

Khi người học bế tắc: tăng hỗ trợ hoặc trở về prerequisite. Khi làm được: rút bớt hỗ trợ và đổi ví dụ. Không kéo dài hội thoại gợi mở khi người học thiếu kiến thức chưa được dạy.

## Mastery policy V0.1 — quy tắc sản phẩm để thử nghiệm

Tách `exposure`, `assisted_performance`, `independent_performance`, `transfer`, `retention` trong evidence. State tối thiểu:

`not_started → learning → practicing → provisionally_mastered → needs_review`.

Chưa dùng nhãn “mastered” trong bản pilot vì số mẫu nhỏ chưa chứng minh độ tin cậy. Mỗi state có reason và evidence IDs.

Đề xuất cấu hình pilot cho objective chấm xác định: 4 item mới không hỗ trợ, ít nhất 3 đúng và không mắc lỗi nghiêm trọng đã định nghĩa trước → `provisionally_mastered`. Với nói/viết: 2 nhiệm vụ mới được rubric của objective xác nhận, ít nhất một nhiệm vụ đổi ngữ cảnh, không thiếu bằng chứng quan trọng. Model không đủ tin cậy → giữ `practicing`, không ép ra số.

Đây là cấu hình V0.1, không là chuẩn khoa học hay quy đổi IELTS. Lưu policy version; review theo pilot, không áp ngưỡng trắc nghiệm cho nói/viết.

Lịch pilot: kiểm tra retention sau 2 ngày rồi 7 ngày nếu đạt; nếu không đạt thì dạy lại với ví dụ khác và lùi state có reason. Học viên đổi lịch được. Dùng clock giả trong test; không chờ ngày thật để chạy CI. Nếu dùng FSRS đã có cho từ vựng thì không đồng thời chạy lịch 2/7 cho cùng card.

## Không làm sai phép đo

- Sửa lại chính câu vừa được giải không phải transfer.
- Re-submit cùng attempt không tạo evidence mới.
- Nhớ đáp án của đề cũ không được tính là câu độc lập chưa gặp.
- Nếu đã xem mẫu/đáp án, server ghi exposure và hạ cấp bài kiểm tra tương ứng.
- Không coi tự tin của model là xác suất đúng đã hiệu chuẩn.
- Nội dung kiểm tra độc lập/transfer được tách khỏi nguồn retrieval của Tutor cho đến khi hoàn tất.

## Lộ trình dài hạn

| Giai đoạn | Kết quả trọng tâm | Nhánh thi |
|---|---|---|
| Foundations | Hiểu/tạo câu ngắn, âm-từ-nghĩa, vốn từ dùng được | Chưa cần band/mock |
| Everyday comprehension | Hiểu đoạn quen thuộc, tóm tắt, giải thích và hỏi lại | Làm quen khi có nhu cầu |
| Connected language | Theo dõi lập luận, viết/nói đoạn có phát triển ý | Bài IELTS từng phần khi phù hợp |
| Flexible use | Suy luận, lựa chọn diễn đạt, dùng được ngữ cảnh mới | Tăng hoạt động theo mục tiêu thi |
| Exam readiness | Giữ chất lượng khi có giới hạn thời gian | Mock định kỳ, phân tích rồi quay về học |

Đây là bản đồ tổ chức nội dung, không phải quy đổi CEFR↔IELTS. Mỗi kỹ năng có thể ở giai đoạn khác nhau; tránh khóa cả người học theo kỹ năng thấp nhất.
