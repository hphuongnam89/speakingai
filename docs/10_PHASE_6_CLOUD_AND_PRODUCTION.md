# Phase 6 — Cloud Fallback & Production

## Model Router
Default:
local Ollama.

Cloud fallback:
DeepSeek.

Automatic fallback is available only when `DEEPSEEK_ENABLED=true` and the
request's user settings allow cloud fallback. `local_only=true` always keeps
the request on Ollama. Requests without user-specific routing options use the
server-level routing configuration.

Fallback conditions:
- Ollama unavailable
- timeout
- model error
- user explicitly enables cloud high-quality analysis

## Production
- [x] Backend API-key authentication and production configuration validation.
- [x] HTTPS reverse-proxy configuration, explicit CORS origins, security headers, and backend loopback binding.
- [x] In-memory rate limiting for the single-worker backend deployment.
- [x] Android account access-token storage encrypted with a non-exportable Android Keystore key; API and DeepSeek signing secrets stay server-side.
- [x] Optional PostgreSQL driver/configuration and Docker deployment path.
- [x] Android release cleartext disabled; optional release signing from environment-provided keystore secrets.
- [x] Email/password account registration and sign-in with signed expiring access tokens.
- [x] Per-account session, settings, mistake, and progress scoping; Android stores the token encrypted and offers sign-in/sign-out.
- [x] Optional Sentry crash/error reporting for backend and Android; PII, request-body capture, Android screenshots, view hierarchy, and interaction breadcrumbs are disabled.
- [x] GitHub Actions build workflow for the backend container and Android debug APK.
- [x] Manual SSH deployment workflow; production host details and GitHub secrets must be configured by the operator.

### Deployment requirements
- For Docker production, set `ENVIRONMENT=production`, use separate random `API_KEY` and `AUTH_SECRET` values of at least 32 characters, and configure exact `CORS_ORIGINS` values.
- Never put the operator `API_KEY`, `AUTH_SECRET`, or DeepSeek key in the Android app; learners use individual account tokens.
- Mount TLS files at `docker/ssl/fullchain.pem` and `docker/ssl/privkey.pem`; start the proxy with `docker compose --profile proxy up -d --build`.
- The optional pronunciation sidecar is English-only and experimental; enable its profile separately. It is not calibrated for IELTS or Vietnamese learners.
- Configure the Android release keystore through `ANDROID_KEYSTORE_PATH`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, and `ANDROID_KEY_PASSWORD`. Keep these values in the CI secret store if builds are automated.

The account system is self-hosted and uses email/password without email verification or password reset. Before public launch, configure SMTP and recovery/verification flows, set `SENTRY_DSN` and the GitHub Actions variable `SENTRY_ANDROID_DSN` only after publishing the applicable privacy notice, and add the GitHub deployment secrets described in the README. Existing anonymous `default` data stays under the guest identity; newly registered accounts get isolated data rather than silently importing another user's sessions.

Never place DeepSeek API key inside Android APK.
