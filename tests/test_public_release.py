import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestPublicRelease(unittest.TestCase):
    def test_live_v04_has_no_provider_response_id(self):
        obj = json.loads((ROOT / "findings/llm_review_openai_v0.4.json").read_text(encoding="utf-8"))
        self.assertNotIn("response_id", obj)

    def test_human_final_approval_was_not_performed(self):
        obj = json.loads((ROOT / "findings/llm_review_openai_v0.4.json").read_text(encoding="utf-8"))
        self.assertFalse(obj["final_approval_performed"])

    def test_adjudication_preserves_known_false_positive(self):
        obj = json.loads((ROOT / "evidence/discovery_adjudication_v0.4.json").read_text(encoding="utf-8"))
        self.assertEqual(obj["summary"]["false_positives"], 1)

if __name__ == "__main__":
    unittest.main()
