# Three-Minute Walkthrough

## 0:00–0:30 — Problem

Engineering artifacts are often fragmented across requirements, tests, and evidence.
An LLM can help review them, but the LLM's own findings must also be verified.

## 0:30–1:10 — Synthetic case

Show:

- 12 synthetic AEB-like requirements,
- Requirement → Component → Test → Evidence trace,
- five intentionally seeded defects,
- human approval boundary.

Key point: the repository does not claim real vehicle or regulatory compliance.

## 1:10–1:50 — Reviewer evaluation

Show the evolution:

- v0.3 raw exact-match evaluation: F1 = 0.40,
- failure analysis found flaws in the evaluator/context,
- v0.4 corrected evaluation: 5/5 observable benchmark defects detected,
- two discovery findings sent to human adjudication.

## 1:50–2:30 — Human adjudication

Show:

- RQ-05 ambiguity → valid new finding,
- RQ-09 missing evidence → false positive.

Key point: the LLM misread a hydrated JSON artifact.

## 2:30–3:00 — Architecture decision

Explain the final boundary:

- deterministic validation for structural facts,
- LLM review for semantic quality,
- human/domain expert for open-ended findings and final approval.

Close with the limitation:
this is a small synthetic benchmark and not a production-quality accuracy claim.
