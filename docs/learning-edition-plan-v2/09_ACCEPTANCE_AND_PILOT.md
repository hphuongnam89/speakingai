# 09 — Kiểm thử, nghiệm thu và pilot

## Ba mức bằng chứng

1. Technical: contract/test/build/runtime hoạt động.
2. Pedagogical: objective, mẫu, giải thích, trợ giúp, bài mới và đáp án/audio được reviewer có chuyên môn kiểm tra.
3. Learning: người học thực làm tốt hơn trên bài mới, giữ được sau thời gian, giảm trợ giúp. Phải có dữ liệu thật.

Test pass không tự chứng minh mức 2/3. Agent không được tự xưng giáo viên đã đào tạo học viên band 9 hoặc tạo learner result giả để đạt gate.

## Lệnh baseline

T00 xác minh interpreter/venv/project scripts trước chạy. Backend từ thư mục `backend`: `<python đã xác minh> -m pytest tests -q`. Suite hiện dùng DB tạm/provider stub; phải đọc fixture để chắc không ghi DB thật. Python 3.12/3.13 từng được dùng; không tự dùng Python 3.14 rồi nới pins để cài được.

Frontend mới: sau khi package.json thực sự được tạo, chạy package-manager lock install/check/typecheck/unit/build theo script thật. Không ghi `pnpm test passed` khi chưa có frontend hoặc chưa chạy. E2E browser kiểm ở origin thật của app. Android chỉ chạy bằng toolchain/wrapper được xác minh.

Nếu lệnh fail: xem đoạn lỗi cuối và follow-up mục tiêu; không dump toàn log. Nếu mạng/quyền bị hạn chế, dùng cơ chế quyền công cụ; không báo “test fail” khi thực ra chưa chạy được test.

## Matrix acceptance bắt buộc

| ID | Tình huống | Kỳ vọng |
|---|---|---|
| Q01 | Learner mới, chưa có band/ngày thi | Vào học được, không ép mock hoặc band giả |
| Q02 | User B đưa profile/attempt/media/job của A | Không đọc/sửa/nộp/tải được |
| Q03 | Nhấn hint rồi làm đúng | Evidence assisted; server biết hint/exposure |
| Q04 | Xem đáp án rồi nộp lại hoặc retry key | Không được independent credit, không cộng evidence hai lần |
| Q05 | Câu mới cùng objective, không gợi ý | Independent evidence có đúng item/content version |
| Q06 | Hoàn thành hết trang nhưng bài mới sai | Không tự thăng mastery |
| Q07 | Sửa chính bài đã được AI chữa | Lưu revision/uptake; không tính transfer mới |
| Q08 | Học lại sau 2/7 ngày qua clock giả | Due đúng policy, chọn item chưa gặp, cạn item báo insufficient |
| Q09 | Model mất kết nối/malformed/cancel | Draft còn, lỗi rõ, không bịa result/band/state |
| Q10 | Đóng/mở giữa bài, autosave stale | Resume đúng hồ sơ, không đè bản mới bằng bản cũ |
| Q11 | Update/retire content | Attempt cũ vẫn đọc đúng stimulus/answer/rubric version |
| Q12 | Learn Listening có transcript/replay | Dùng được và ghi hỗ trợ; không dùng exam lockdown cho Learn |
| Q13 | Audio thiếu/sai/mic bị từ chối | Có fallback có nhãn, không kết luận yếu kỹ năng từ lỗi thiết bị |
| Q14 | Tutor gặp prompt injection/answer-key request | Không thực thi instructions của content, không lộ holdout answer |
| Q15 | Chạy migrations trên new/old snapshot | Giữ history, idempotent, restore thử được |
| Q16 | Export/delete một hồ sơ | Bao phủ records/media mới, không xóa hồ sơ khác |
| Q17 | 401 từ API nhưng server online | UI yêu cầu login, không báo backend offline chung chung |
| Q18 | Build/deploy local | `/` trả UI đúng, assets và API hoạt động, không secret trong bundle |
| Q19 | TTS render restart/cache/version đổi | Job interrupted có lý do; cache đúng asset/version; không hỏng lesson khác |
| Q20 | Speaking/Android contract cũ | Session/history/routes tiếp tục hoạt động; phần chưa test được ghi rõ |

Tên test cụ thể do agent tạo theo conventions repo, có thể là `test_learning_ownership.py`, `test_learning_evidence.py`, `test_learning_migrations.py`; các tên này là đề xuất. Trace matrix Qxx → test file/test name/log.

## Content review checklist

- Người học đúng mức đầu vào có hiểu mục tiêu/instruction không?
- Mẫu có giải thích cách hiểu/cách làm và vì sao không?
- Có nhiều đáp án hợp lệ không; answer key có chấp nhận không?
- Passage/audio có đủ evidence cho lời giải không?
- Nghe có khớp transcript, thời điểm, tên/số/cách đọc không?
- Hint có phù hợp và giảm được không; item độc lập có bị lộ từ mẫu không?
- Independent/transfer/retention có đổi dữ kiện/ngữ cảnh mà vẫn cùng objective không?
- Rubric nói/viết có mô tả hành vi quan sát được, không “hay hơn” mơ hồ không?
- AI suggestions có bị gọi nhầm là grammar errors không?
- Source/license/version/reviewer rõ không?

## Pilot khả thi cho bản đầu

Đề xuất nhóm 5–8 người đúng mức mục tiêu để kiểm usability/khả năng dạy học; đây là lựa chọn vận hành, không đủ để khẳng định hiệu quả phổ quát. Học viên/reviewer phải có thật, do chủ dự án cung cấp hoặc cho phép tuyển; agent không tự liên hệ người khác.

1. Chốt objective và rubric trước thu kết quả. Nội dung/unit phải qua human review.
2. Baseline dùng set A chưa dạy; ghi trợ giúp, kinh nghiệm, thời lượng và chất lượng thiết bị.
3. Học L01–L04; log những gì thực sự xem/nhận trợ giúp.
4. Post-check dùng set B khác dữ kiện/ngữ cảnh, cùng objective/độ khó dự kiến.
5. Retention dùng set C sau 7 ngày, chưa gặp; ghi cả việc ôn và hỗ trợ trong khoảng chờ.
6. Người chấm nói/viết dùng rubric objective; ẩn pre/post khi khả thi. Với mẫu quan trọng có reviewer thứ hai và ghi cách xử lý bất đồng.
7. Phỏng vấn ngắn: hiểu feedback không, tự sửa thế nào, tại sao chọn đáp án, bài mới có quá khó không.

## Báo cáo pilot

Mỗi learner có pseudonym, baseline/post/retention, item set/version, rubric, hints/exposure, số cơ hội dùng năng lực, lỗi, thời gian, missing data và lý do. Không public recording/bài viết/identity chưa được phép.

Báo cả người bỏ dở, không chỉ người tiến bộ. Tách sửa bài cũ khỏi bài mới. Không dùng confidence model hay band AI để xác nhận hiệu quả của chính Tutor/scorer đó.

Nếu không có đối chứng và độ khó item chưa được cân bằng chắc chắn, chỉ báo thay đổi quan sát được, không kết luận app gây ra mức tăng band. T18 có thể `in_progress/needs_review` khi chờ retention; không rút ngắn thời gian rồi báo delayed learning đã đạt.

## Gate phát hành

- Q01–Q20 có trạng thái pass/fail/not_run cùng lý do; blocker quan trọng đã xử lý.
- Một unit đã được người thật review và chạy browser end-to-end.
- Dữ liệu pilot hỗ trợ hướng chỉnh tiếp; không có lỗi nội dung nghiêm trọng chưa xử lý.
- Scorer chưa calibration vẫn được dùng cho feedback với giới hạn rõ, không gắn nhãn calibrated hoặc sai số được đảm bảo.
- Không gọi bản một unit là toàn bộ giáo trình 4 kỹ năng; report đúng platform/hardware đã thử.
