# IELTS Speaking AI Coach — Pilot Checklist

Use this short protocol with 3–5 English learners before inviting a wider group. The pilot checks whether learners can complete the core learning loop; it does not validate IELTS score accuracy.

## Before the session

- Build and install the Android debug app, then connect it to a reachable backend.
- Start the backend and confirm `GET /api/v1/health` returns `200`.
- For a real AI session, start Ollama and confirm the configured model is listed by `GET /api/v1/models`.
- Tell the learner that AI feedback and band estimates are practice guidance, not official IELTS scores.
- Get consent before recording. Use test accounts/data and remove recordings or account data after the pilot when no longer needed.

## Ask each learner to try

1. Open Settings and connect the app to the backend.
2. Start a daily speaking session and record a short answer (20–40 seconds).
3. Read the transcript and AI reply. Find one correction and explain in their own words how they would improve the sentence.
4. Use “Say it again” to practise the corrected sentence.
5. Start IELTS Part 2, review the cue card, prepare an answer, and complete the speaking turn.
6. Open the progress screen and find the activity from the session.
7. If comfortable, deny microphone permission once and recover; then retry after granting permission.

Do not coach the learner through the interface. Note where they hesitate, misread a result, or ask what to do next.

## Record observations

For each step, record **completed without help**, **completed with help**, or **blocked**, plus the learner's exact words when something is unclear.

Ask these questions at the end:

- Was it clear what to do after each answer?
- Which feedback item was most useful? Which one felt wrong or confusing?
- Did the AI estimate seem more certain than it should?
- Would you use this again? What would you change first?

## Pilot exit criteria

- Every learner can connect, record, view feedback, and find progress without the facilitator taking control.
- No recording is silently lost; errors show an actionable recovery step.
- Learners understand that band scores are estimates and transcript-based data is not pronunciation scoring.
- Review every blocked task and any feedback judged incorrect before wider release.

Keep pilot notes free of passwords, access tokens, and identifiable audio/transcripts unless the learner explicitly consents to that storage.
