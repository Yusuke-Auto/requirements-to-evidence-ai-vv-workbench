# Limitations

This repository is a synthetic engineering work sample, not a production AEB system.

## What the results do not prove

The reported `5/5` benchmark result does **not** establish:

- general LLM reviewer accuracy,
- production recall or precision,
- regulatory compliance,
- functional-safety compliance,
- OEM or NCAP conformance,
- robustness across models, prompts, domains, or larger datasets,
- validity of the synthetic AEB thresholds for a real vehicle.

## Known limitations

1. **Small benchmark**
   - Only five seeded defects are used in the current benchmark.
2. **Single synthetic domain**
   - The current example is an AEB-like pedestrian scenario.
3. **Single-run evidence**
   - The live LLM result is one observed run, not a statistical performance study.
4. **Human adjudication dependency**
   - Open-ended discoveries still require domain-expert review.
5. **LLM false positive remains**
   - In v0.4, the reviewer incorrectly claimed that `RQ-09` evidence lacked `requirement_id`.
6. **No production toolchain integration**
   - No claim is made for live integration with OEM requirements tools, vehicle networks, HIL benches, or safety processes.

## Intended next validation

A stronger evaluation would add:

- a larger expert-labeled corpus,
- repeated runs and model/version tracking,
- inter-rater agreement between domain experts,
- per-finding-type precision/recall,
- latency and human-review effort,
- comparison of Human-only vs Human+LLM workflows,
- regression tests for previously observed model failures.
