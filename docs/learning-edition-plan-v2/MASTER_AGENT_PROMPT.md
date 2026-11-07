# Prompt giao việc cho AI agent

Copy phần dưới khi người dùng muốn bắt đầu triển khai. Nếu chỉ được giao review hoặc viết kế hoạch, không tự triển khai.

---

Hãy triển khai kế hoạch IELTS Learning Edition V2 trong repository SpeakingAI hiện tại, theo phạm vi người dùng đã giao.

Mục tiêu: dạy người học hiểu và dùng được tiếng Anh tốt hơn qua Listening, Reading, Writing, Speaking. Kết quả đầu tiên là một đơn vị học bốn kỹ năng với hướng dẫn, luyện tập, tự sửa, nhiệm vụ mới, lịch ôn và progress có evidence. Giữ Speaking và dữ liệu hiện có.

Tìm thư mục `docs/learning-edition-plan-v2/` ở repository hiện tại. Đọc README, 00 và 01, sau đó tài liệu liên quan task. Nếu gói nằm ngoài repo, xác định đúng đường dẫn; không giả định máy có đường dẫn `/Users/nam/...`.

Trước code: đọc hướng dẫn repo, kiểm worktree/HEAD, baseline và handoff; xem `tasks.json`. Bắt đầu T00 nếu chưa có bằng chứng hoàn thành. Nếu đã có, tiếp tục task đủ dependency đầu tiên và xác minh acceptance liên quan.

Sử dụng codebase graph nếu môi trường có; nếu không, dùng tìm kiếm code thông thường. Không cần plugin/model đặc biệt để hiểu kế hoạch.

Thực hiện thay đổi nhỏ đủ end-to-end, đọc caller/contracts/tests, tái dùng implementation và dependencies hiện có. Pin BandReady SHA từ baseline. Không import identity/settings/DB thứ hai. Không tự đổi architecture để làm mọi thứ dễ hơn.

Mỗi bài phải có objective, mẫu được giải thích, hỗ trợ giảm dần, bài mới độc lập và transfer. AI feedback phải dẫn tới learner action. Không xem AI rewrite, đáp án đã lộ, completion hoặc streak là mastery. Dùng policy pilot có version, nêu giới hạn.

Giữ auth/ownership, không đưa admin key vào web bundle. Không ghi đè DB thật hoặc thay đổi chưa commit của người dùng. Kiểm đúng DB theo runtime trước migration; test trên snapshot/DB tạm. Kiểm kê model đã có trước khi tải.

Chạy test tương ứng và browser flow khi có UI; ghi mock/real, pass/fail/not_run đúng thực tế. Không dùng test pass làm bằng chứng nội dung đúng hoặc học viên cải thiện. Human review, pilot và calibration thiếu evidence phải ghi thật, không giả kết quả để đóng task.

Sau task, cập nhật trạng thái và handoff theo `10_HANDOFF_TEMPLATE.md`; đi tiếp task đủ điều kiện trong phạm vi được giao. Chỉ hỏi khi thiếu quyết định thực sự làm đổi phạm vi, cần quyền mới hoặc không thể tiếp tục bằng lựa chọn hợp lý. Quy định công cụ/hệ thống và chỉ dẫn người dùng ưu tiên hơn prompt này.

Báo cáo ngắn: task đã hoàn thành, hành vi quan sát được, file đổi, kiểm thử, giới hạn và task tiếp theo. Không tuyên bố đã có app/giáo trình hoàn chỉnh khi mới có một phần.

---

Prompt tiếp tục một task cụ thể:

> Tiếp tục task `<ID>` trong kế hoạch V2. Đọc baseline, tasks.json và handoff gần nhất; xác minh dependencies/acceptance, thực hiện end-to-end trong phạm vi task, chạy kiểm thử và cập nhật handoff. Không làm lại phần đã được kiểm chứng nếu không có thay đổi liên quan.
