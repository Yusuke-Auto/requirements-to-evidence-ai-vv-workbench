# Problem Statement

Engineering teams often have fragmented links between requirements, tests, and evidence.
This synthetic case demonstrates a minimal traceable V&V loop for an AEB-like feature.

## Core question

Can a reviewer determine, from machine-readable artifacts, whether:
1. a requirement has a corresponding test,
2. the test produced evidence,
3. a negative case is handled correctly,
4. ambiguous requirements are surfaced,
5. human approval remains mandatory?

## Success criteria

- Normal requirement trace is inspectable.
- The three v0.1 cases execute automatically.
- A false-positive-oriented test is included.
- An ambiguous requirement produces a finding.
- No automated reviewer can assign final `Verified` / `Approved` state.
