# Human Review Gate

Allowed automated actions:
- flag ambiguity,
- flag missing evidence,
- flag missing trace,
- compare expected vs actual result,
- recommend review priority.

Disallowed automated actions:
- set Requirement = Verified,
- set Test = Approved,
- waive a safety-relevant finding,
- silently rewrite an engineering requirement.

Final states are human-controlled:
- Verified
- Rejected
- Needs Clarification
