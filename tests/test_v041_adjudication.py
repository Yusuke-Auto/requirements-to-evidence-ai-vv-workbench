import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestHumanAdjudicationV041(unittest.TestCase):
    def test_rq09_required_fields_are_present(self):
        record = json.loads(
            (ROOT / "evidence" / "decision_record.json").read_text(encoding="utf-8")
        )
        for field in ["timestamp", "requirement_id", "input_state", "trigger_reason"]:
            self.assertIn(field, record)

    def test_discovery_adjudication_is_one_valid_one_fp(self):
        adj = json.loads(
            (ROOT / "evidence" / "discovery_adjudication_v0.4.json").read_text(encoding="utf-8")
        )
        self.assertEqual(adj["summary"]["valid_discoveries"], 1)
        self.assertEqual(adj["summary"]["false_positives"], 1)
        self.assertEqual(adj["summary"]["discovery_precision"], 0.5)

if __name__ == "__main__":
    unittest.main()
