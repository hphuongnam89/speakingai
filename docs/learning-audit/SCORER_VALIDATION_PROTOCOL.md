# Assessment validation protocol — Phase 4

Status: **unverified**. No human-rated dataset, approved rater agreement report or held-out accuracy result has been supplied. No runtime sample-count threshold enables calibrated wording or a numeric uncertainty interval.

## Runtime boundary

`assessment-0.4` / `ielts-transcript-0.4` accepts only finite half-band criterion values in [1,9], validates shape/types, and abstains on malformed output. Fewer than 40 learner words returns insufficient_evidence without calling a model or finishing the session. This is a preview sufficiency rule, not an IELTS requirement or validation result.

The evaluator receives transcript only: temporal fluency, pronunciation and overall band stay null. Lexical/grammar estimates, when available, remain provisional. Provider/model IDs come from router metadata rather than generated text. Missing provenance abstains. Confidence stays null and uncertainty is unverified. A voice recording elsewhere in the database does not mean the evaluator heard it.

Historical reports remain stored unchanged. Their prior calibrated/overall claims are not re-presented as validated evidence. Invalid output is not cached; successful evaluation uses a compare-and-swap so retries do not double-count daily activity. Typed practice does not create estimated speaking minutes.

## Human-rated dataset to obtain

Each consented sample needs a stable anonymous sample key, participant-group key (kept private), task/objective/version, original modality, audio-quality limitations, rubric version, rater pseudonyms/qualifications, individual criterion ratings, adjudication status and consent/retention scope. Do not put learner transcripts/audio in Git or CI logs.

For reproducibility retain actual provider/model digest, prompt/scoring versions, decoding options and raw model output in the approved private evaluation workspace. Administrative sample upload is disabled without the configured admin key, requires consent, rejects invalid/non-finite scores and conflicting reuse of a sample key. It stores evidence; it does not train or certify the scorer.

## Split and evaluation

1. Freeze the objective/rubric and adjudication process before looking at model error. Collect independent human ratings; report disagreement and missing evidence instead of assuming a single rater is ground truth.
2. Split by participant and related task/variant groups into fit and evaluation sets. Keep original sample IDs and a split manifest so repeated recordings, paraphrases, siblings of an item and prompt examples cannot leak across the split.
3. Use only the fit set for any bias correction, model/prompt selection or threshold choice. Freeze the resulting model/prompt/correction artifact and its checksum.
4. Run the untouched evaluation set once with the frozen artifact. Report n and missing/abstained cases by criterion, task, modality, input quality and relevant skill ranges. Include MAE, signed error, error distribution and observed within-0.5/within-1 rates where meaningful, plus human disagreement. These rates are measured results, not promises.
5. Any uncertainty interval needs an explicit held-out coverage method and observed coverage; do not infer ±0.5 or confidence from sample count, model self-confidence or in-sample fit. Selection changes require a fresh evaluation split or an explicitly documented repeated-selection correction.
6. A human reviewer approves the report, limits, source authority, data lineage and allowed wording. Only a separately reviewed implementation may consume that artifact. The current runtime deliberately has no automatic promotion to calibrated.

## Current evidence record

Human samples verified: **0**. Fit/evaluation results: **not measured**. Audio-aware pronunciation/fluency validation: **not measured**. Learning activity objective feedback and competency policy remain independent of IELTS band validation, so learning is available while assessment abstains.
