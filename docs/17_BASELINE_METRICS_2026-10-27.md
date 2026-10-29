# Baseline metrics — 2026-10-27

| Metric | Baseline | Measurement status |
|---|---:|---|
| Backend test reproducibility | 28/28 tests passed (100%) | Verified qua `scripts/check.ps1` |
| STT Transcription Latency (Whisper RTX 5060 Ti) | ~0.24s / câu nói | CUDA float16 + Silero VAD |
| LLM Local Generation Speed (Qwen 27B) | ~26.2 tokens/sec | `safe_ctx` 4096 trong VRAM |
| Diagnostic Evaluation Total Latency | 34.3s - 37.1s | Đã khắc phục lỗi timeout 120s |
| Test suite execution time | ~5.2s | Toàn bộ suite unit & integration |
| Audio File Cleanup Verification | 100% | Đã test xóa file khi reset và delete profile |
| Duplicate turn rate | Pending Phase 2 | Phase 2 Idempotency |
| Feedback parse failure | 0 trong test suite | Bổ sung error fallback |

Các số liệu trên được đo đạc trực tiếp trên môi trường thử nghiệm với phần cứng thực tế và bộ test tự động.
