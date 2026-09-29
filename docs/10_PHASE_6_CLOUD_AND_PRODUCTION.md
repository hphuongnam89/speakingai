# Phase 6 — Cloud Fallback & Production

## Model Router
Default:
local Ollama.

Cloud fallback:
DeepSeek.

Fallback conditions:
- Ollama unavailable
- timeout
- model error
- user explicitly enables cloud high-quality analysis

## Production
- backend auth
- HTTPS
- rate limiting
- encrypted secrets
- optional Supabase/PostgreSQL
- account synchronization
- remote access
- crash analytics
- APK signing
- CI/CD

Never place DeepSeek API key inside Android APK.
