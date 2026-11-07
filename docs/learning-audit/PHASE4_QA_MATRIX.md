# Phase 4 acceptance trace

Automated tests use temporary databases, synthetic inputs and deterministic providers. Browser checks and hardware limitations are recorded separately in the handoff. A technical release candidate does not release the four draft lessons to a learner pilot.

| ID | Automated evidence (backend/tests unless noted) |
|---|---|
| Q01 | test_learning_foundation: requires login/owned profile; test_phase4_assessment: short input abstains; no validated overall shown |
| Q02 | test_learning_foundation: owner/profile isolation; test_phase1_security: owner-scoped playback; test_phase4_assessment: admin calibration boundaries |
| Q03–Q05 | test_learning_foundation: hint idempotency/assisted, repeated vs new item; test_learning_slices: transcript exposure and unseen retention |
| Q06–Q08 | test_learning_slices: policy due boundaries, insufficient items, retained variants; reducer only promotes with qualifying observations |
| Q09 | test_learning_release: cancelled Tutor preserves draft; test_phase4_assessment: malformed output is retryable; foundation Tutor source/output validation |
| Q10 | test_learning_foundation: draft resume/CAS; test_learning_slices: per-item draft/evidence reload |
| Q11 | test_learning_release: retired content only resumes for existing owner; foundation immutable version/checksum tests |
| Q12 | test_learning_slices: authenticated Range audio, hidden transcript, exposure/assisted; browser playback evidence in prior handoff |
| Q13 | test_learning_release: missing/corrupt asset fails closed; existing speech unsupported MIME/invalid session tests. Real mic denial remains manual/hardware evidence, not a claimed automated result |
| Q14 | foundation Tutor uses only teaching sources and rejects invented sources; server never puts independent/transfer keys in Tutor context |
| Q15 | test_learning_release: old SQLite migration twice + backup/restore; foundation additive metadata preservation |
| Q16 | foundation export/profile deletion; phase1 audio cleanup; reviews included in shared deletion/export path |
| Q17 | frontend/tests/api.test.mjs: 401 vs transport errors; browser cookie/origin/logout backend tests |
| Q18 | Docker staged-snapshot build/startup smoke + React route; frontend typecheck/unit/build; npm and Python advisory audits |
| Q19 | No runtime TTS job exists: static versioned checksummed WAVs. Missing/corrupt asset tests cover the deployed path; build script requires macOS say only during authoring |
| Q20 | Existing Speaking/API/full-flow regressions. Android nullable assessment DTO/report updated; build result is separate from microphone hardware evidence |

Content review: draft 4, human-approved 0, published 0. No reviewer identity, pilot participation, calibration accuracy or learning gain is invented to close technical checks.
