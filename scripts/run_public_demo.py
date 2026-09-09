#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def run(cmd, label):
    print(f"\n[{label}]")
    proc = subprocess.run(cmd, cwd=ROOT)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)

def main():
    run([sys.executable, "scripts/run_vv.py"], "1/5 Synthetic V&V")
    run([sys.executable, "scripts/review_traceability.py"], "2/5 Deterministic seeded-defect review")
    run([sys.executable, "scripts/validate_evidence_contracts.py"], "3/5 Structural evidence validation")
    run([
        sys.executable,
        "scripts/evaluate_llm_review.py",
        "--prediction", "findings/llm_review_openai_v0.4.json",
        "--output", "evidence/release_evaluation.json",
    ], "4/5 Re-evaluate saved live LLM findings")
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], "5/5 Regression tests")

    evaluation = json.loads((ROOT / "evidence/release_evaluation.json").read_text(encoding="utf-8"))
    adjudication = json.loads((ROOT / "evidence/discovery_adjudication_v0.4.json").read_text(encoding="utf-8"))

    summary = {
        "benchmark": evaluation["benchmark"],
        "human_adjudication": adjudication["summary"],
        "final_approval_performed": False,
        "claim_boundary": "Small synthetic work sample; not production accuracy or compliance evidence."
    }
    (ROOT / "evidence/release_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\n=== Public demo summary ===")
    print(
        f"Benchmark: {evaluation['benchmark']['hits']}/"
        f"{evaluation['benchmark']['observable_targets']} known defects detected"
    )
    print(
        f"Discovery: {adjudication['summary']['valid_discoveries']} valid / "
        f"{adjudication['summary']['false_positives']} false positive"
    )
    print("Human final approval: required")
    print("Saved: evidence/release_summary.json")

    run([sys.executable, "scripts/build_dashboard.py"], "6/6 Build static review dashboard")
    print("Dashboard: docs/dashboard.html")

if __name__ == "__main__":
    main()
