# Traceability Matrix

| Req | Component | Test | Evidence | Note |
|---|---|---|---|---|
| RQ-01 | Risk Assessor | TC-01 | monitoring_state.json | Catalog contradiction intentionally injected |
| RQ-02 | Perception Adapter | TC-02 | track_timeline.json | nominal |
| RQ-03 | AEB Supervisor | TC-03 | warning_timeline.json | nominal |
| RQ-04 | AEB Supervisor | TC-04 | test_results.json | implemented |
| RQ-05 | Brake Interface | TC-05 | brake_timeline.json | nominal |
| RQ-06 | AEB Supervisor | TC-06 | override_state.json | nominal |
| RQ-07 | Risk Assessor | TC-07 | test_results.json | implemented negative test |
| RQ-08 | Perception Adapter | TC-08 | degraded_state.json | nominal |
| RQ-09 | Evidence Logger | TC-09 | decision_record.json | nominal |
| RQ-10 | Evidence Logger | TC-10 | **MISSING** | intentional defect |
| RQ-11 | AEB Supervisor | TC-11 | review_findings.json | intentional ambiguity |
| RQ-12 | **MISSING** | TC-12 | approval_audit.json | intentional broken trace |
