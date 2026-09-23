"""Thin AWS Lambda adapter: IoT Rule event -> pure transform -> S3 evidence object.

All validation and record shaping live in transform.py. This module only does
I/O: read the bucket name from the environment, write one JSON object to S3,
and emit one structured log line (stdout is captured by CloudWatch Logs).

Lambda handler setting: cloud_evidence.lambda_handler.handler
Required environment variable: EVIDENCE_BUCKET
"""
import json
import os

from .transform import TelemetryValidationError, evidence_object_key, telemetry_to_evidence


def _log(level, event, **fields):
    print(json.dumps({"level": level, "event": event, **fields}, sort_keys=True))


def handler(event, context, s3_client=None):
    try:
        record = telemetry_to_evidence(event)
    except TelemetryValidationError as exc:
        # Malformed input is logged and dropped, not raised: a retry cannot fix it.
        _log("ERROR", "telemetry_rejected", reason=str(exc))
        return {"status": "rejected", "reason": str(exc)}

    bucket = os.environ["EVIDENCE_BUCKET"]
    key = evidence_object_key(record)
    if s3_client is None:
        import boto3  # provided by the Lambda runtime; not needed for offline tests

        s3_client = boto3.client("s3")

    # S3 errors propagate so Lambda's async retry / IoT Rule error action can apply.
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(record, indent=2, sort_keys=True).encode("utf-8"),
        ContentType="application/json",
    )
    _log("INFO", "evidence_recorded", key=key, message_id=record["message_id"])
    return {"status": "recorded", "key": key}
