import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_vv import evaluate_tc04, evaluate_tc07, review_requirement_rq11

class TestSyntheticAEBVV(unittest.TestCase):
    def test_tc04_brake_trigger_latency(self):
        r = evaluate_tc04()
        self.assertEqual(r["result"], "PASS")
        self.assertTrue(r["actual"]["brake_request"])
        self.assertLessEqual(r["actual"]["latency_ms"], r["expected"]["max_latency_ms"])

    def test_tc07_false_positive_suppression(self):
        r = evaluate_tc07()
        self.assertEqual(r["result"], "PASS")
        self.assertFalse(r["actual"]["trajectory_intersection"])
        self.assertFalse(r["actual"]["brake_request"])

    def test_tc11_ambiguity_detection_and_human_gate(self):
        r = review_requirement_rq11()
        self.assertEqual(r["result"], "PASS")
        finding = r["finding"]
        self.assertEqual(finding["type"], "ambiguous_requirement")
        self.assertTrue(finding["human_review_required"])
        self.assertIsNone(finding["final_disposition"])

if __name__ == "__main__":
    unittest.main()
