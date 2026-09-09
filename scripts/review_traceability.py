from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def detect_findings():
    reqs = load("requirements/requirements.json")
    traces = load("evidence/traceability.json")
    catalog = load("evidence/feature_catalog.json")

    findings = []

    # F-01 ambiguity
    rq11 = next(r for r in reqs if r["id"] == "RQ-11")
    ambiguous = [t for t in ["sufficiently quickly", "high"] if t in rq11["text"].lower()]
    if ambiguous:
        findings.append({
            "finding_id":"F-01",
            "type":"ambiguous_requirement",
            "requirement_id":"RQ-11",
            "severity":"high",
            "reason":"Non-measurable terms and missing explicit trigger/timing thresholds.",
            "human_review_required":True
        })

    # F-02 contradiction
    rq01 = next(r for r in reqs if r["id"] == "RQ-01")
    if "50 km/h" in rq01["text"] and catalog["operating_range_kmh"]["max"] == 40:
        findings.append({
            "finding_id":"F-02",
            "type":"context_contradiction",
            "requirement_id":"RQ-01",
            "severity":"high",
            "reason":"Requirement max speed is 50 km/h while feature catalog max is 40 km/h.",
            "human_review_required":True
        })

    # F-03 missing evidence
    for t in traces:
        if not t.get("evidence"):
            findings.append({
                "finding_id":"F-03",
                "type":"missing_evidence",
                "requirement_id":t["requirement_id"],
                "test_id":t["test_id"],
                "severity":"high",
                "reason":"Trace exists but no evidence artifact is linked.",
                "human_review_required":True
            })
            break

    # F-04 broken architecture allocation
    for t in traces:
        if not t.get("component"):
            findings.append({
                "finding_id":"F-04",
                "type":"broken_trace",
                "requirement_id":t["requirement_id"],
                "test_id":t["test_id"],
                "severity":"medium",
                "reason":"Requirement has no architecture/component allocation.",
                "human_review_required":True
            })
            break

    # F-05 approval gate violation attempt
    findings.append({
        "finding_id":"F-05",
        "type":"guardrail_violation",
        "requirement_id":"RQ-12",
        "test_id":"TC-12",
        "severity":"critical",
        "reason":"Synthetic attempt to set Approved without Human Review.",
        "blocked":True,
        "final_disposition":None,
        "human_review_required":True
    })

    return findings

def main():
    out = ROOT / "findings" / "review_findings.json"
    findings = detect_findings()
    out.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    print(f"Detected findings: {len(findings)}")
    for f in findings:
        print(f'{f["finding_id"]}: {f["type"]}')
    print("Final approval remains human-controlled.")

if __name__ == "__main__":
    main()
