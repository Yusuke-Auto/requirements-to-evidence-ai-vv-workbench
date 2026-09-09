from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]

def evaluate_tc04():
    latency_ms = 118
    max_latency_ms = 150
    actual_brake_request = True
    passed = actual_brake_request and latency_ms <= max_latency_ms
    return {
        "test_id": "TC-04",
        "requirement_id": "RQ-04",
        "scenario_id": "SC-PED-004",
        "expected": {"brake_request": True, "max_latency_ms": max_latency_ms},
        "actual": {"brake_request": actual_brake_request, "latency_ms": latency_ms},
        "result": "PASS" if passed else "FAIL",
        "evidence": ["risk_state.json", "brake_timeline.json"]
    }

def evaluate_tc07():
    trajectory_intersection = False
    actual_brake_request = False
    passed = (trajectory_intersection is False) and (actual_brake_request is False)
    return {
        "test_id": "TC-07",
        "requirement_id": "RQ-07",
        "scenario_id": "SC-PED-007",
        "expected": {"brake_request": False},
        "actual": {
            "pedestrian_detected": True,
            "trajectory_intersection": trajectory_intersection,
            "ttc_s": 0.9,
            "brake_request": actual_brake_request
        },
        "result": "PASS" if passed else "FAIL",
        "evidence": ["risk_state.json", "brake_state.json"]
    }

def review_requirement_rq11():
    text = "The system shall brake sufficiently quickly when collision risk is high."
    ambiguous_terms = ["sufficiently quickly", "high"]
    hits = [term for term in ambiguous_terms if term in text.lower()]
    finding = {
        "finding_id": "F-11-AMB",
        "type": "ambiguous_requirement",
        "severity": "high",
        "requirement_id": "RQ-11",
        "detected_terms": hits,
        "reason": "The requirement has non-measurable terms and lacks explicit trigger and timing thresholds.",
        "recommendation": "Needs Clarification",
        "final_disposition": None,
        "human_review_required": True,
        "reviewer_type": "deterministic_stub_v0.1"
    }
    return {
        "test_id": "TC-11",
        "requirement_id": "RQ-11",
        "scenario_id": "SC-REQ-011",
        "result": "PASS" if hits else "FAIL",
        "finding": finding
    }

def main():
    evidence_dir = ROOT / "evidence"
    findings_dir = ROOT / "findings"
    evidence_dir.mkdir(exist_ok=True)
    findings_dir.mkdir(exist_ok=True)

    results = [evaluate_tc04(), evaluate_tc07(), review_requirement_rq11()]

    with open(evidence_dir / "test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(findings_dir / "review_findings.json", "w", encoding="utf-8") as f:
        json.dump([results[2]["finding"]], f, indent=2)

    print("Synthetic AEB V&V v0.1")
    for r in results:
        print(f'{r["test_id"]}: {r["result"]}')
    print("Human approval gate: ENABLED")
    print("Automated final approval: DISALLOWED")

if __name__ == "__main__":
    main()
