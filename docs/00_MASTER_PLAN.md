# IELTS Speaking AI Coach — Master Plan

## 1. Product Goal
Build an Android-first AI speaking coach for daily English speaking practice and IELTS Speaking preparation toward Band 7.0.

The product must prioritize:
- Daily speaking habit
- Real-time conversation
- IELTS Speaking Part 1/2/3
- Grammar, vocabulary, fluency and pronunciation feedback
- Personal mistake memory
- Low operating cost
- Local-first AI
- Cloud fallback only when needed

## 2. Primary User Flow
1. User opens app.
2. Chooses Daily Practice / IELTS / Free Talk / Fix My English.
3. App records speech.
4. Speech is transcribed.
5. Audio metrics are extracted.
6. AI analyzes the response.
7. AI replies naturally.
8. App gives corrections after the user finishes.
9. User repeats corrected sentence when appropriate.
10. Progress and mistakes are saved.

## 3. Product Principles
- Speaking first, screen second.
- Do not interrupt unnecessarily.
- Do not let LLM estimate pronunciation only from transcript.
- Do not claim official IELTS scoring.
- Save recurring mistakes.
- Prefer local inference.
- Model providers must be swappable.
- Android app must not directly depend on Ollama APIs.

## 4. Core Modes
### Daily Practice
5–15 minute guided daily speaking sessions.

### IELTS Practice
Part 1, Part 2 and Part 3 practice.

### Mock Examiner
11–14 minute simulated IELTS Speaking test.

### Fix My English
User speaks freely; app corrects important mistakes and asks for repetition.

### Free Talk
Natural conversation with minimal UI interaction.

## 5. MVP Scope
The MVP must contain:
- Android app
- Audio recording
- Whisper transcription
- AI conversation
- TTS
- Session history
- Grammar/vocabulary corrections
- Basic fluency metrics
- IELTS practice mode
- Progress page
- Mistake memory
- Local Ollama support
- DeepSeek fallback adapter

Out of MVP:
- Advanced phoneme scoring
- Social features
- Payments
- Teacher marketplace
- Full cloud synchronization
- iOS

## 6. Tech Stack
### Android
- Kotlin
- Jetpack Compose
- MVVM + Clean Architecture
- Coroutines / Flow
- Room
- DataStore
- Retrofit / OkHttp
- Android AudioRecord
- Android TTS initially

### Local AI Server
- Python 3.12+
- FastAPI
- Pydantic
- SQLite initially
- Ollama
- whisper.cpp or faster-whisper server
- Model router

### Models
Primary local:
- Qwen3.5 9B via Ollama

Benchmark alternative:
- Ornith 1.5 9B

Cloud fallback:
- DeepSeek

## 7. Success Metrics
MVP:
- Median AI response latency < 5 sec on local LAN
- Daily session completion > 70%
- User can complete 10-minute conversation without touching keyboard
- Transcription usable for normal English speech
- All sessions persisted
- AI corrections explain the error and offer a better sentence
- Model provider can be changed without Android code changes

## 8. Repository Structure
```text
ielts-speaking-ai/
├── android/
├── backend/
├── docs/
├── prompts/
├── models/
├── scripts/
├── tests/
├── docker/
├── .env.example
├── docker-compose.yml
└── README.md
```

## 9. Development Order
1. Backend skeleton
2. Android skeleton
3. Record audio
4. STT
5. LLM gateway
6. TTS
7. Conversation loop
8. Mistake extraction
9. IELTS engine
10. Progress analytics
11. DeepSeek fallback
12. Performance and QA

## 10. Definition of Done
The first production candidate is complete when a user can:
- Install APK
- Configure local server IP
- Start Daily Practice
- Speak naturally
- Receive AI voice responses
- Review transcript and corrections
- Complete IELTS Part 1/2/3 practice
- See progress history
- Continue using local AI without paid API
