"""Contract checks for the checked-in agent policy (not OS sandbox enforcement)."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class AgentBaselineContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))

    def test_interactive_permission_mode_and_no_bypass(self):
        p = self.policy["permissions"]
        self.assertEqual(p["defaultMode"], "default")
        self.assertTrue(p["blockReadsOutsideWorkingDirectories"])
        self.assertEqual(p["disableBypassPermissionsMode"], "disable")
        self.assertEqual(p["disableAutoMode"], "disable")
        self.assertFalse(p.get("allow"), "No blanket auto-approved tools allowed")

    def test_secret_files_denied_by_builtin_tools(self):
        deny = set(self.policy["permissions"]["deny"])
        for operation in ("Read", "Edit"):
            for filename in (".env", ".env.*", "secrets/**", "~/.ssh/**", "~/.aws/**"):
                with self.subTest(operation=operation,filename=filename):
                    self.assertIn(f"{operation}({filename})", deny)

    def test_sandbox_credential_scrub_declared(self):
        c = self.policy["sandbox"]["credentials"]
        denied = {x["name"] for x in c["envVars"] if x["mode"] == "deny"}
        self.assertTrue({"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GITHUB_TOKEN", "AWS_SECRET_ACCESS_KEY"} <= denied)
        self.assertIn({"path":"~/.ssh","mode":"deny"},c["files"])

    def test_ci_token_requested_read_only(self):
        workflow = (ROOT / ".github" / "workflows" / "verify.yml").read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read",workflow)
        self.assertIn("persist-credentials: false",workflow)
        self.assertNotIn("contents: write",workflow)

if __name__ == "__main__":
    unittest.main()
