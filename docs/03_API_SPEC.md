# REST API Specification

Base:
`/api/v1`

## Contract rules v1

- `Authorization: Bearer <access_token>` identifies the principal. `X-Profile-Id` and `profile_id` are resource selectors only and are accepted only when the selected profile belongs to that principal.
- Profile/session/mistake/progress/audio routes return `404` for resources outside the principal rather than leaking existence.
- Band values are provisional practice estimates, not official IELTS results. `pronunciation_score` is `null` unless an acoustic assessor produced it; STT confidence is a separate field.
- Audio uploads are bounded by `MAX_AUDIO_BYTES` and `MAX_AUDIO_DURATION_MS`, receive a retention deadline, and are removed by reset/delete/retention cleanup.
- Conversation corrections include `error_type`, `subtype`, `severity` and `practice_prompt`; `/conversation/repeat-check` verifies say-it-again reuse.
- Mistake review uses `/mistakes/{id}/review` and requires repeated successful reuse before `mastery_state=mastered`. `/progress/adaptive-plan` is evidence-based and cached per principal/day.
- IELTS evaluation is always provisional until calibration is accepted; it returns `confidence`, `confidence_range`, `limitation`, `scoring_version`, `model_id` and `prompt_version`. Evaluation feedback accepts `useful`, `incorrect`, `too_harsh` or `too_vague`.
- Controlled pilot endpoints are `/pilot/runs`, `/pilot/runs/{id}/events`, `/pilot/runs/{id}/feedback`, `/pilot/runs/{id}/summary` and `DELETE /pilot/runs/{id}`; pilot metadata excludes audio and full transcripts and is ownership-scoped.

## Health
GET `/health`

Response:
```json
{"status":"ok"}
```

## Session
POST `/sessions`

Request:
```json
{
  "mode": "daily",
  "topic": null
}
```

GET `/sessions/{session_id}`

POST `/sessions/{session_id}/finish`

## Speech
POST `/speech/transcribe`

Multipart:
- audio
- session_id
- turn_id

Response:
```json
{
  "text": "I enjoy working from home.",
  "duration_ms": 5200,
  "metrics": {
    "wpm": 115,
    "long_pauses": 1
  }
}
```

## Conversation
POST `/conversation/respond`

Request:
```json
{
  "session_id": "...",
  "user_text": "...",
  "mode": "daily"
}
```

Response:
```json
{
  "reply": "...",
  "corrections": [],
  "focus": [],
  "tts_text": "..."
}
```

## Evaluate
POST `/evaluate/turn`

Response:
```json
{
  "fluency": 6.0,
  "grammar": 5.5,
  "vocabulary": 6.0,
  "coherence": 6.0,
  "pronunciation": null,
  "feedback": []
}
```

Pronunciation must remain null unless audio-based pronunciation analysis is available.

## IELTS
POST `/ielts/start`

Request:
```json
{"part":1}
```

POST `/ielts/answer`

POST `/ielts/next`

POST `/ielts/finish`

## Mistakes
GET `/mistakes`
GET `/mistakes/frequent`
POST `/mistakes/{id}/resolve`

## Progress
GET `/progress/daily`
GET `/progress/weekly`
GET `/progress/summary`

## Models
GET `/models`

Response:
```json
{
  "active": "qwen3.5:9b",
  "available": [
    "qwen3.5:9b",
    "ornith1.5:9b"
  ]
}
```

POST `/models/select`

## Settings
GET `/settings`
PUT `/settings`
