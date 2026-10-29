# Phase 8–9 implementation report

## Phase 8 — Scoring calibration và QA

IELTS evaluation hiện trả score status provisional, confidence, confidence range, limitation, scoring version, model id và prompt version. Pronunciation luôn là `null` nếu không có acoustic assessment; transcript không được dùng để suy ra pronunciation score. Parser có fallback confidence thấp cho output sai format. Đã thêm `evaluation_feedback` với các flag `useful`, `incorrect`, `too_harsh`, `too_vague`, cùng calibration sample storage và template consented JSONL. Protocol yêu cầu human raters, bốn criterion, provenance và release gate trước khi publicize score.

## Phase 9 — Android parity và release quality

Android API models đã đồng bộ evaluation confidence/limitation, correction taxonomy, mistake review, profile selector, repeat-check và evaluation feedback. OkHttp gửi Bearer token cùng `X-Profile-Id`; HTTP 401 xóa token trong memory để UI có thể đưa người dùng về login. Release build đã dùng environment-only signing, minify, cleartext=false và logging NONE; debug mới cho phép cleartext. Thêm checklist/script `scripts/check-android.ps1` và release contract về permission, timeout, rotation, process death, logout và privacy logging.

## Validation

Đã kiểm tra tĩnh các file, migration chain và JavaScript syntax. Đã thêm `backend/tests/test_phase8_9_contracts.py`. Không thể chạy compile/pytest hoặc Gradle trong phiên này nếu runtime/wrapper tương ứng không khả dụng; cần chạy `scripts/check.ps1` và `scripts/check-android.ps1` trên clean environment có Python và Gradle wrapper.
