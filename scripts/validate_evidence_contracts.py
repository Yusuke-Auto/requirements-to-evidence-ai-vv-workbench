#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def main():
    contracts = json.loads((ROOT / "evidence/evidence_contracts.json").read_text(encoding="utf-8"))
    results = []
    overall = True

    for c in contracts["contracts"]:
        artifact = ROOT / c["artifact"]
        if not artifact.exists():
            results.append({
                "requirement_id": c["requirement_id"],
                "artifact": c["artifact"],
                "result": "FAIL",
                "reason": "artifact_not_found"
            })
            overall = False
            continue

        obj = json.loads(artifact.read_text(encoding="utf-8"))
        missing = [f for f in c["required_fields"] if f not in obj]
        passed = len(missing) == 0
        results.append({
            "requirement_id": c["requirement_id"],
            "artifact": c["artifact"],
            "required_fields": c["required_fields"],
            "missing_fields": missing,
            "result": "PASS" if passed else "FAIL"
        })
        overall = overall and passed

    out = {
        "validator": "deterministic_evidence_contract",
        "overall_result": "PASS" if overall else "FAIL",
        "results": results
    }
    (ROOT / "evidence/deterministic_evidence_validation.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print(f"Deterministic evidence validation: {out['overall_result']}")
    for r in results:
        print(f"{r['requirement_id']}: {r['result']} missing={r.get('missing_fields', [])}")
    return 0 if overall else 1

if __name__ == "__main__":
    raise SystemExit(main())
