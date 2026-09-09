import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from review_traceability import detect_findings

class TestTraceabilityReview(unittest.TestCase):
    def test_exactly_five_injected_findings_detected(self):
        findings = detect_findings()
        self.assertEqual(len(findings), 5)

    def test_required_failure_types_present(self):
        types = {f["type"] for f in detect_findings()}
        expected = {
            "ambiguous_requirement",
            "context_contradiction",
            "missing_evidence",
            "broken_trace",
            "guardrail_violation",
        }
        self.assertEqual(types, expected)

    def test_all_findings_require_human_review(self):
        self.assertTrue(all(f["human_review_required"] for f in detect_findings()))

    def test_guardrail_blocks_final_approval(self):
        f = next(x for x in detect_findings() if x["type"] == "guardrail_violation")
        self.assertTrue(f["blocked"])
        self.assertIsNone(f["final_disposition"])

if __name__ == "__main__":
    unittest.main()
