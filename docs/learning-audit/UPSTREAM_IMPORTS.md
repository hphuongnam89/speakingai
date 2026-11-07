# Upstream inventory T02

Nguồn: https://github.com/Luxshan2000/ielts-prep/tree/1627d57fc8beccb8158302c04b0c62d2744b0b02

## Candidate map

| Candidate | Dependencies chính | Consumer dự kiến |
|---|---|---|
| sidecar/bandready/scoring/answers.py | Normalization/answer rules, helper functions | Reading/Listening marking T08/T09 |
| server/routes/reading.py | donor models/session, require_auth/current_profile_id, scoring, jobs/settings | Reading adapter; không mount nguyên router |
| server/routes/listening.py | models, tts_render, jobs, media tickets, normalizer | Listening adapter T09 |
| audio/tts_render.py | TTS config/engine, media cache, timing/stitch, DB link | Optional local render sau inventory voice/model |
| server/routes/writing.py và scoring/writing.py | models, scorer/rubric, settings/providers, jobs, coach | Writing adapter T10 |
| app/src/features/reading, listening, writing | React feature routing, API client/token contract, stores, UI kit | Player/editor có chọn lọc phase 2 |
| content/core-en/manifest.json | JSONL schema/checksum/pack pipeline | Ngữ liệu candidate; không tự coi đã review độc lập |

## Đã lấy gì vào phase 1

Không copy code/content BandReady vào runtime ở phase này. Đã dùng inventory để chốt boundaries, dependencies và tránh nhập cả sidecar/Electron. Lesson drafts và React lesson shell hiện tại được viết mới cho flow dạy học. Vì chưa copy đoạn code/substantial content donor, không giả đã hoàn tất integration L/R/W.

Khi T08–T10 import: ghi mỗi source path, SHA/checksum, destination, patch delta, test ported và MIT notice. Core-en manifest ghi CC0-1.0/ai_assisted; kiểm nội dung/version thực và điều kiện asset/voice riêng trước release.

## Hợp đồng cần thay khi import

- donor launch token → user session/bearer hiện có;
- current_profile_id global settings → request-owned profile;
- donor Base/engine/migrations → canonical learning DB;
- provider configuration → SpeakingAI router/settings;
- jobs/media tickets → ownership-aware adapters;
- exam lockdown → Learn có hỗ trợ, independent ghi trợ giúp.
