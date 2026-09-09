import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / "docs" / "dashboard.html").read_text(encoding="utf-8")

    def test_dashboard_exists_and_has_core_metrics(self):
        self.assertIn("5/5", self.text)
        self.assertIn("Benchmark recall", self.text)
        self.assertIn("False positive", self.text)

    def test_dashboard_explains_claim_boundary(self):
        self.assertIn("not</strong> a production-accuracy", self.text)

    def test_dashboard_is_read_only_no_api_key_input(self):
        self.assertNotIn('type="password"', self.text)
        self.assertNotIn("OPENAI_API_KEY", self.text)

    def test_dashboard_contains_human_boundary(self):
        self.assertIn("Human adjudication &amp; approval", self.text)

if __name__ == "__main__":
    unittest.main()
