import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_llm_review import evaluate
from llm_review_openai import build_review_input, validate_findings

class TestLLMReviewContract(unittest.TestCase):
    def test_review_input_contains_expected_context(self):
        x = build_review_input()
        self.assertEqual(len(x["requirements"]), 12)
        self.assertEqual(len(x["traceability"]), 12)
        self.assertFalse(x["review_contract"]["final_approval_allowed"])

    def test_perfect_prediction(self):
        gt = json.loads(
            (ROOT / "evidence" / "ground_truth_findings.json").read_text(encoding="utf-8")
        )
        metrics = evaluate(gt, gt)
        self.assertEqual(metrics["benchmark"]["hits"], 5)
        self.assertEqual(metrics["benchmark"]["misses"], 0)
        self.assertEqual(metrics["benchmark"]["recall"], 1.0)
        self.assertEqual(metrics["discovery"]["candidate_count"], 0)

    def test_one_miss_one_false_positive(self):
        gt = json.loads(
            (ROOT / "evidence" / "ground_truth_findings.json").read_text(encoding="utf-8")
        )
        pred = gt[:-1] + [{
            "type": "missing_evidence",
            "requirement_id": "RQ-09",
            "test_id": "TC-09",
        }]
        metrics = evaluate(gt, pred)
        self.assertEqual(metrics["benchmark"]["hits"], 4)
        self.assertEqual(metrics["benchmark"]["misses"], 1)
        self.assertEqual(metrics["discovery"]["candidate_count"], 1)

    def test_human_review_guardrail_is_enforced(self):
        with self.assertRaises(ValueError):
            validate_findings([{
                "type": "missing_evidence",
                "requirement_id": "RQ-10",
                "test_id": "TC-10",
                "human_review_required": False
            }])

if __name__ == "__main__":
    unittest.main()
