# v0.4 Discovery Adjudication

## Result

The v0.4 live run returned 7 findings:
- 5/5 seeded benchmark defects were detected.
- 2 additional findings entered Discovery review.

## Discovery 1 — RQ-05 ambiguity: VALID

Requirement:

> During automatic braking, maintain the brake request until collision risk is cleared.

The phrase **collision risk is cleared** is not operationally defined. `brake_timeline.json`
contains `risk_cleared_at_ms`, but that only records *when* clearance was declared; it does
not define *what measurable criterion* constitutes clearance.

Decision: **VALID_DISCOVERY**

## Discovery 2 — RQ-09 missing requirement ID: FALSE POSITIVE

RQ-09 requires:
- timestamp
- requirement ID
- input state
- trigger reason

`decision_record.json` contains all four fields, including `requirement_id: RQ-09`.

Decision: **FALSE_POSITIVE**

This is an important reviewer failure: the LLM had the hydrated artifact but misread it.

## Architecture lesson

Use a **deterministic-first, LLM-second** review boundary:

1. Deterministic checks handle structural facts:
   - file exists
   - required JSON field exists
   - trace link exists
   - schema/version consistency
2. LLM handles semantic review:
   - ambiguous wording
   - conflicting intent
   - engineering-quality concerns
   - cross-artifact rationale
3. Human/domain expert adjudicates:
   - open-ended discoveries
   - exceptions
   - final approval

This reduces avoidable false positives while preserving the LLM's useful semantic discovery capability.
