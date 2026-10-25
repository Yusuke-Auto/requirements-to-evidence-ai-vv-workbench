"""Negative verification for the public-safety check; uses synthetic credentials only."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

CHECKER = Path(__file__).resolve().parents[1] / "scripts" / "public_safety_check.py"

class PublicSafetyGateNegativeTests(unittest.TestCase):
    def run_check_with_fixture(self, relative_path):
        with tempfile.TemporaryDirectory(prefix="public-safety-test-") as temporary:
            root = Path(temporary)
            dst = root / "scripts" / "public_safety_check.py"
            dst.parent.mkdir()
            shutil.copyfile(CHECKER, dst)
            fixture = root / relative_path
            fixture.parent.mkdir(parents=True, exist_ok=True)
            marker = "sk-" + "X" * 25  # fabricated key-shaped text; NOT a credential
            fixture.write_text(marker, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(dst)], cwd=root, capture_output=True,
                text=True, check=False
            )
            self.assertNotIn(marker, result.stdout)
            self.assertNotIn(marker, result.stderr)
            return result

    def test_rejects_key_shaped_text_in_markdown(self):
        result = self.run_check_with_fixture("docs/synthetic.md")
        self.assertEqual(result.returncode, 1)
        self.assertIn("possible API secret", result.stdout)

    def test_rejects_key_shaped_text_in_dotenv(self):
        result = self.run_check_with_fixture(".env")
        self.assertEqual(result.returncode, 1)
        self.assertIn("possible API secret", result.stdout)

if __name__ == "__main__":
    unittest.main()
