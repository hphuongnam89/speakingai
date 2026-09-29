# Phase 5 — Pronunciation Engine

Do not use transcript-only LLM scoring.

## Components
- word timestamps
- forced alignment
- phoneme alignment
- pronunciation confidence
- pitch
- rhythm
- stress
- intonation
- intelligibility

Candidate technologies to benchmark:
- whisper.cpp timestamps
- WhisperX / forced alignment
- wav2vec2 phoneme models
- Montreal Forced Aligner
- custom acoustic scorer

Output example:
```json
{
  "word": "enjoyed",
  "expected": "/ɪnˈdʒɔɪd/",
  "confidence": 0.72,
  "needs_review": true
}
```

UI:
- word-level highlighting
- listen
- record
- compare
- repeat
