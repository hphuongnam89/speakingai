# System Architecture

## High-Level Architecture
```text
Android App
    |
    | HTTPS / LAN
    v
FastAPI AI Gateway
    |
    +-- Session Service
    +-- STT Service
    +-- Audio Metrics Service
    +-- Speaking Evaluation Service
    +-- IELTS Engine
    +-- Prompt Engine
    +-- Student Memory Service
    +-- Model Router
            |
            +-- Ollama
            |    +-- qwen3.5:9b
            |    +-- ornith1.5:9b
            |
            +-- DeepSeek API
```

## Android Modules
```text
android/app
android/core/network
android/core/database
android/core/audio
android/core/designsystem
android/feature/home
android/feature/daily
android/feature/conversation
android/feature/ielts
android/feature/result
android/feature/mistakes
android/feature/progress
android/feature/settings
```

## Backend Modules
```text
backend/app/
├── main.py
├── api/
├── core/
├── models/
├── schemas/
├── services/
│   ├── stt/
│   ├── llm/
│   ├── tts/
│   ├── evaluation/
│   ├── ielts/
│   ├── memory/
│   └── analytics/
├── repositories/
└── prompts/
```

## Model Router
The Android client must call the backend only.

Example provider interface:
```python
class LLMProvider:
    async def chat(self, messages, options): ...
```

Implementations:
- OllamaProvider
- DeepSeekProvider

Routing rules:
1. Use Ollama by default.
2. Use cloud only if explicitly enabled.
3. Fall back to DeepSeek after local timeout/error.
4. Never expose provider-specific response formats to Android.

## STT Strategy
MVP:
- Server-side Whisper.

Later:
- optional on-device whisper.cpp.

STT output:
```json
{
  "text": "...",
  "language": "en",
  "duration_ms": 15420,
  "segments": [],
  "words": []
}
```

## Audio Analysis
MVP metrics:
- total duration
- speaking duration
- silence duration
- words per minute
- mean pause
- long pause count
- filler count
- repetition count

Advanced:
- pitch
- stress
- rhythm
- phoneme confidence
- intelligibility

## Conversation State
Store:
- mode
- topic
- current IELTS part
- turn count
- transcript
- corrections
- detected weaknesses
- vocabulary introduced
- target skill

## Security
- Local server should bind to LAN only by default.
- Do not expose Ollama directly to internet.
- DeepSeek API key exists only on backend.
- Android stores no third-party API secret.
