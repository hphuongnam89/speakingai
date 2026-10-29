# Product Contract v1

## Định vị
AI IELTS Speaking Practice Coach cho người học Band 4.5–6.5, tập trung vào phản xạ nói, mở rộng câu trả lời, sửa lỗi lặp lại và duy trì thói quen. Đây là công cụ luyện tập, không phải giám khảo IELTS chính thức.

## Core loop
`Start → Speak → Transcript → Focus feedback → Repeat → Review progress`

MVP v1 ưu tiên Daily Practice, IELTS Part 2, feedback có cấu trúc, mistake notebook và progress cơ bản. Full Mock, acoustic pronunciation scoring và cloud fallback là beta/backlog.

## Product labels bắt buộc
- **Practice feedback:** nhận xét để luyện tập, không phải điểm thi.
- **Quick diagnostic:** kiểm tra đầu vào nhanh, không phải chứng nhận trình độ.
- **Provisional transcript-based estimate:** ước lượng tạm thời dựa trên transcript/LLM.
- **Experimental pronunciation analysis:** chỉ xuất hiện khi có acoustic assessor; transcript confidence không phải pronunciation score.

## Glossary
- `speaking_time`: thời gian người học thực sự nói, lấy từ audio metrics khi có; text-only chỉ là proxy.
- `recording_duration`: tổng thời lượng file recording.
- `transcription_confidence`: độ tin cậy nhận dạng giọng nói của STT.
- `pronunciation_score`: điểm từ acoustic assessor; null khi chưa có assessor.

## Success baseline
Ghi nhận p50/p95 latency, timeout rate, transcription success rate, duplicate turn rate và feedback parse failure rate trước/sau mỗi phase. Không coi proxy text-only là speaking time thật.
