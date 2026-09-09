# UI Design Rationale

The dashboard is intentionally a **read-only evidence surface**, not a control plane.

## Primary audience

1. Recruiter / hiring manager — understand the work sample in ~30 seconds.
2. Engineering interviewer — inspect V&V logic, findings, traceability, and limitations.
3. Domain expert — adjudicate discovery findings without being distracted by implementation detail.

## Information hierarchy

1. **Outcome + claim boundary**
   - 5/5 seeded benchmark hits
   - one valid discovery
   - one confirmed false positive
   - explicit note that this is not production accuracy

2. **Responsibility boundary**
   - deterministic structural checks
   - LLM semantic review
   - human/domain-expert final judgment

3. **Failure-analysis story**
   - v0.3 raw F1=0.40
   - evaluator/context flaws
   - v0.4 corrected contract

4. **Inspectability**
   - filterable findings
   - requirement → component → test → evidence table

5. **Reproducibility**
   - one-command offline demo

## Security boundary

The browser UI never receives an API key. Live review remains a local/server-side CLI workflow.
