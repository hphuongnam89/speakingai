# Rules for AI Coding Agents

## General
1. Read all files in `/docs` before coding.
2. Work phase by phase.
3. Do not silently change architecture.
4. Do not add unnecessary frameworks.
5. Do not implement future-phase features early unless required.
6. Keep Android independent from LLM vendors.
7. Add tests for all critical backend services.
8. Run lint/tests/build before marking a task complete.
9. Update README when setup changes.
10. Never commit secrets.

## Required End-of-Task Report
Every completed task must report:
- files changed
- feature implemented
- tests run
- build result
- remaining issues
- next recommended task

## Stop Conditions
Do not continue if:
- build is broken
- migrations fail
- API contract differs from docs
- tests fail

Fix the issue first.
