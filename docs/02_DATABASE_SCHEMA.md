# Database Schema

## users
- id UUID
- display_name TEXT
- target_band REAL
- native_language TEXT
- created_at DATETIME

## sessions
- id UUID
- user_id UUID
- mode TEXT
- started_at DATETIME
- ended_at DATETIME
- topic TEXT
- total_speaking_ms INTEGER
- estimated_band REAL NULL
- provider TEXT

## turns
- id UUID
- session_id UUID
- role TEXT
- transcript TEXT
- audio_path TEXT NULL
- duration_ms INTEGER
- created_at DATETIME

## evaluations
- id UUID
- turn_id UUID
- fluency_score REAL NULL
- grammar_score REAL NULL
- vocabulary_score REAL NULL
- pronunciation_score REAL NULL
- coherence_score REAL NULL
- confidence REAL
- feedback_json TEXT

## mistakes
- id UUID
- user_id UUID
- session_id UUID
- turn_id UUID
- category TEXT
- original_text TEXT
- corrected_text TEXT
- explanation TEXT
- severity INTEGER
- first_seen_at DATETIME
- last_seen_at DATETIME
- occurrence_count INTEGER
- resolved BOOLEAN

## vocabulary
- id UUID
- user_id UUID
- phrase TEXT
- meaning TEXT
- example TEXT
- level TEXT
- times_seen INTEGER
- times_used INTEGER
- mastered BOOLEAN

## daily_stats
- id UUID
- user_id UUID
- date DATE
- speaking_minutes REAL
- session_count INTEGER
- word_count INTEGER
- avg_wpm REAL
- avg_pause_ms REAL
- mistake_count INTEGER

## ielts_attempts
- id UUID
- session_id UUID
- part INTEGER
- question TEXT
- answer_turn_id UUID
- feedback_json TEXT

## user_settings
- user_id UUID
- correction_level TEXT
- local_only BOOLEAN
- cloud_fallback BOOLEAN
- preferred_model TEXT
- voice TEXT
