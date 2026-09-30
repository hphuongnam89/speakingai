# Phase 5 — Pronunciation Engine

Do not use transcript-only LLM scoring.

## Current implementation status
- Recorded-turn transcription responses include Whisper word timestamps and recognition probabilities.
- Recognition confidence is surfaced only as transcript uncertainty; it is not presented as pronunciation accuracy or an IELTS band.
- The drill provides IPA and practice guidance without a numeric score.
- An optional OpenPronounce 0.3.0 sidecar scores recorded English audio against its transcript and returns possible phoneme differences. Its raw score is experimental, never an IELTS band.
- IELTS pronunciation band scoring and calibration on Vietnamese learners remain unimplemented.

## Implemented
- Whisper word timestamps and recognition probabilities (recognition uncertainty only).
- IPA lookup with syllables and lexical stress hints.
- Optional OpenPronounce experimental score and possible phoneme differences for English recordings.

## Not implemented / not calibrated
- IELTS pronunciation band scoring.
- Calibration for Vietnamese learners or independent human-rating validation.
- Forced alignment as an acoustic reference for each expected word.
- Pitch, rhythm, stress, intonation, and intelligibility scoring.
- Scored single-word drill recordings.

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
