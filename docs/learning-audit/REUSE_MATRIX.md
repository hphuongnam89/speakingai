# T02 — Reuse/extend/new

| Domain | Quyết định | Implementation/consumer |
|---|---|---|
| Account/profile/password | Reuse + browser session extension | core/auth, api/auth, React và Speaking dùng cùng cookie hoặc bearer Android |
| Profile ownership | Extend strict invalid-ID handling | learning dependency và explicit selector 404 |
| LLM/STT/Speaking | Reuse | ModelRouter/OllamaProvider/conversation; thêm format schema có chọn lọc |
| Content | New versioned authoring catalog | Pydantic Lesson + manifest/checksum/import immutable |
| Learning attempts/evidence | New | learning models/service/API, không tạo user/profile thứ hai |
| Learn UI | New minimal React shell | frontend; giữ Speaking route /speaking |
| Donor L/R/W engines | Audit now, selective import at T08–T10 | không copy routes/scorer/DB/provider trong phase 1 |
| Mastery/SRS/daily planner | T12–T13 | foundation chỉ ghi evidence; chưa promotion/schedule tự động |
| Pronunciation/recording lesson | T11 | phase 1 nói rõ gõ thử không đo phát âm |

Schemas/API của V2 là đề xuất. Contracts runtime canonical ở `backend/app/schemas/learning.py`; `docs/learning-audit/IMPLEMENTATION_CONTRACT.md` ghi mapping thực tế. Không giả mọi API đề xuất đã tồn tại.

## Dependencies frontend thực thêm

React/ReactDOM 19.3.1, TypeScript 7.0.2, esbuild 0.28.2, type declarations React 19.3.0. Lockfile npm là nguồn cài đặt. `.npmrc` tắt lifecycle scripts. Cài `npm ci --ignore-scripts`; build dùng esbuild optional platform binary đã có trong dependency tree.

Không import Vite/Electron/Pipecat/Torch/Kokoro để xây lesson shell. Các player/editor đặc thù của donor được xem xét ở phase 2; dùng lesson shell mới vì donor chủ yếu cung cấp màn hình practice, không có đúng flow dạy học V2.

Audit npm mới: 0 vulnerabilities ở thời điểm kiểm. Chưa audit lại toàn bộ dependency Python cũ trong phạm vi phase 0–1; không tuyên bố toàn stack không có advisory.
