import contextlib
import copy
import io
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cloud_evidence.lambda_handler import handler
from cloud_evidence.transform import TelemetryValidationError, telemetry_to_evidence

FIXTURE = ROOT / "cloud_evidence/fixtures/synthetic_telemetry_nominal.json"


class FakeS3:
    def __init__(self):
        self.puts = []

    def put_object(self, **kwargs):
        self.puts.append(kwargs)


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def run_handler(event, s3):
    out = io.StringIO()
    with mock.patch.dict(os.environ, {"EVIDENCE_BUCKET": "example-evidence-bucket"}):
        with contextlib.redirect_stdout(out):
            result = handler(event, None, s3_client=s3)
    return result, [json.loads(line) for line in out.getvalue().splitlines()]


class TestCloudEvidenceContract(unittest.TestCase):
    def test_nominal_telemetry_becomes_rq09_compliant_evidence(self):
        record = telemetry_to_evidence(load_fixture())

        # Reuse the repository's existing deterministic RQ-09 evidence contract.
        contracts = json.loads((ROOT / "evidence/evidence_contracts.json").read_text(encoding="utf-8"))
        rq09 = next(c for c in contracts["contracts"] if c["requirement_id"] == "RQ-09")
        self.assertEqual([f for f in rq09["required_fields"] if f not in record], [])

        self.assertTrue(record["synthetic"])
        self.assertEqual(record["evidence_status"], "RECORDED")
        self.assertFalse(record["safety_decision_made"])
        self.assertFalse(record["final_approval_performed"])
        self.assertTrue(record["human_final_approval_required"])

        s3 = FakeS3()
        result, logs = run_handler(load_fixture(), s3)
        self.assertEqual(result["status"], "recorded")
        self.assertEqual(len(s3.puts), 1)
        put = s3.puts[0]
        self.assertEqual(put["Key"], "cloud-evidence/telemetry/synthetic-bench-01/syn-telemetry-0001.json")
        self.assertEqual(json.loads(put["Body"]), record)
        self.assertEqual(logs[-1]["event"], "evidence_recorded")

    def test_malformed_telemetry_is_rejected_without_writing_evidence(self):
        malformed = copy.deepcopy(load_fixture())
        del malformed["signals"]["ttc_s"]
        with self.assertRaises(TelemetryValidationError):
            telemetry_to_evidence(malformed)

        non_synthetic = dict(load_fixture(), synthetic=False)
        with self.assertRaises(TelemetryValidationError):
            telemetry_to_evidence(non_synthetic)

        path_injection = dict(load_fixture(), device_id="../other-prefix")
        with self.assertRaises(TelemetryValidationError):
            telemetry_to_evidence(path_injection)

        s3 = FakeS3()
        result, logs = run_handler(malformed, s3)
        self.assertEqual(result, {"status": "rejected", "reason": "invalid_or_missing_signal:ttc_s"})
        self.assertEqual(s3.puts, [])
        self.assertEqual(logs[-1]["level"], "ERROR")
        self.assertEqual(logs[-1]["event"], "telemetry_rejected")

    def test_offline_demo_does_not_depend_on_cloud_extension(self):
        for script in (ROOT / "scripts").glob("*.py"):
            text = script.read_text(encoding="utf-8")
            self.assertNotIn("cloud_evidence", text, script.name)
            self.assertNotIn("boto3", text, script.name)


if __name__ == "__main__":
    unittest.main()
