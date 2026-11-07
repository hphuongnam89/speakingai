# 11 — Nguồn, quyết định và giới hạn

## Nguồn code

- SpeakingAI: https://github.com/hphuongnam89/speakingai — baseline commit trong `02_BASELINE_AND_REUSE.md`, có worktree chưa commit nên HEAD không đại diện toàn trạng thái local.
- BandReady snapshot: https://github.com/Luxshan2000/ielts-prep/tree/1627d57fc8beccb8158302c04b0c62d2744b0b02
- Donor status: https://github.com/Luxshan2000/ielts-prep/blob/1627d57fc8beccb8158302c04b0c62d2744b0b02/docs/IMPLEMENTATION-STATUS.md
- Donor license: https://github.com/Luxshan2000/ielts-prep/blob/1627d57fc8beccb8158302c04b0c62d2744b0b02/LICENSE
- Donor manifest: https://github.com/Luxshan2000/ielts-prep/blob/1627d57fc8beccb8158302c04b0c62d2744b0b02/content/core-en/manifest.json

Manifest, source code, README và author status có thể khác nhau. Đếm/validate file thật ở SHA đã pin; không lặp lại số lượng từ README như kết quả test.

## Nguồn định hướng dạy học

- IES, Organizing Instruction and Study to Improve Student Learning (2007): https://ies.ed.gov/ncee/wwc/PracticeGuide/1 — spaced learning, examples xen kẽ tự giải, retrieval và explanatory questions. Đây là hướng dẫn học tập chung, không là thử nghiệm app/IELTS của dự án.
- AERO, Vary practice (cập nhật 14/05/2026 tại lần đọc): https://www.edresearch.edu.au/guides-resources/practice-guides/vary-practice — luyện đa dạng, giãn cách và vận dụng qua ngữ cảnh; tài liệu chủ yếu bối cảnh trường học, không suy ra mức tăng band người lớn.
- EEF, Teacher Feedback to Improve Pupil Learning (2021): https://educationendowmentfoundation.org.uk/education-evidence/guidance-reports/feedback — phản hồi có thể có ích hoặc không tùy thiết kế/sử dụng; tài liệu hướng tới học sinh 5–18 tuổi, không trực tiếp xác minh AI Tutor người lớn.

Các nguồn này đã được đọc trong quá trình phản biện kế hoạch. Quy tắc pilot 3/4, hai nhiệm vụ productive, review 2/7 ngày và nhóm 5–8 người là quyết định thiết kế để kiểm nghiệm, không phải ngưỡng lấy nguyên từ các nguồn trên.

## Nguồn IELTS cần xác minh khi triển khai assessment

- https://ielts.org/take-a-test/your-results/ielts-scoring-in-detail
- https://ielts.org/organisations/ielts-for-organisations/understanding-ielts-scoring/resources-for-setting-your-ielts-scores

Agent T16 phải kiểm bản chính thức đang áp dụng trước đưa band conversion/descriptors vào code. Bài học thường ngày dùng objective rubric, không ép quy đổi CEFR/nội bộ sang IELTS. Không copy rubric/content có hạn chế phân phối khi chưa kiểm điều kiện sử dụng.

## Quyết định kế hoạch đã chốt

| ID | Quyết định | Lý do |
|---|---|---|
| D01 | Học và cải thiện là mục tiêu chính | Yêu cầu người dùng |
| D02 | Giữ SpeakingAI làm repo/backend chủ | Bảo toàn Speaking, tài khoản, hồ sơ, lịch sử |
| D03 | Tái dùng chọn lọc BandReady L/R/W | Có source/player/editor/marking, giảm viết lại |
| D04 | Web React là hướng UI mới; Android giữ tương thích | Tái dùng UI donor; frontend migration theo từng slice |
| D05 | Một unit có 4 skill trước giáo trình lớn | Có mốc end-to-end đủ nhỏ để kiểm chứng |
| D06 | Learning evidence tách band | Không nhầm sửa bài/được gợi ý với năng lực độc lập |
| D07 | Nội dung draft không tự thành approved | Cần kiểm ngôn ngữ/sư phạm/audio |
| D08 | Calibration không chặn bài học đã duyệt | Learning feedback khác tuyên bố độ chính xác band |
| D09 | Ollama có sẵn được kiểm kê trước tải | Tránh kho model trùng host/container |
| D10 | Giữ auth và ownership | Ghép UI qua user login, không hạ bảo vệ API |

## Các điểm chưa quyết định

Mức vào học của cohort tiếp theo; reviewer và người học pilot cụ thể; TTS/voice có sẵn; model phù hợp cho từng objective; ngưỡng mastery sau pilot; phạm vi Android 4 skill. Agent có thể hoàn thành code, fixture và draft content trước khi các quyết định này có đủ evidence, nhưng không bịa con người/asset/kết quả.
