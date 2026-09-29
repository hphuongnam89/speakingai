# REST API Specification

Base:
`/api/v1`

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
