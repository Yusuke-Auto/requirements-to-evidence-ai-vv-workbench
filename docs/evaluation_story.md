# Evaluation Story: Why the First F1 Score Was Misleading

## v0.3 — First live LLM review

The first live reviewer run used five seeded defects as ground truth and returned ten findings.

The original evaluator used an exact key:

`finding_type + requirement_id + test_id`

That produced:

- TP = 3
- FP = 7
- FN = 2
- Precision = 0.30
- Recall = 0.60
- F1 = 0.40

This looked like poor reviewer quality, but failure analysis showed that the evaluation contract itself was flawed.

## Failure analysis

Three evaluation problems were found:

1. **Incidental `test_id` mismatch**
   - Requirement-level findings were counted as different findings when the LLM attached a test ID.
2. **Unobservable ground truth**
   - One seeded guardrail violation was not visible in the artifacts given to the reviewer.
3. **Context pointers without hydrated evidence**
   - The reviewer could see references to evidence files without seeing their contents.

## v0.4 — Corrected evaluation contract

The evaluation was changed so that:

- requirement-level findings ignore incidental `test_id`,
- only observable defects count as benchmark targets,
- referenced evidence is hydrated into reviewer context,
- the guardrail violation is represented as an explicit audit event,
- unmatched findings are sent to human/domain-expert adjudication instead of being automatically labeled false positive.

Using the same model family with the corrected context and contract:

- benchmark hits = 5 / 5
- benchmark misses = 0
- benchmark recall = 1.00
- discovery candidates = 2

This does **not** mean the model has production-grade recall. It means all five defects in this small synthetic benchmark were detected.

## v0.4.1 — Human adjudication

The two discovery findings were reviewed manually:

- `RQ-05 ambiguous_requirement` → **valid discovery**
- `RQ-09 missing_evidence` → **false positive**

The RQ-09 false positive is especially useful because the required field was actually present in the hydrated JSON artifact.

This led to the next architecture decision:

> **Use deterministic checks for structural facts and LLM review for semantic engineering judgment.**

## Resulting review boundary

```text
Structural facts
(file/field/trace/schema)
        ↓
Deterministic validation
        ↓
Semantic review
(ambiguity/conflict/rationale)
        ↓
LLM reviewer
        ↓
Human / domain-expert adjudication
        ↓
Final decision
```

The final approval state remains human-controlled.
