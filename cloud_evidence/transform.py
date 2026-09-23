"""Pure telemetry -> evidence transformation.

No AWS, network, clock, or filesystem access: the same input always yields the
same evidence record, so it can be contract-tested offline.

The produced record is evidence capture only. It records what synthetic
telemetry reported; it does not make or approve any safety decision.
"""
from datetime import datetime
import re

SCHEMA_VERSION = "1.0"
CLAIM_BOUNDARY = (
    "Synthetic public work sample; not production telemetry, safety evidence, "
    "or compliance evidence."
)

_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_REQUIRED_SIGNALS = {
    "vehicle_speed_kph": (int, float),
    "ttc_s": (int, float),
    "brake_request": (bool,),
}


class TelemetryValidationError(ValueError):
    """Raised when a telemetry message violates the synthetic telemetry contract."""


def _require_safe_id(msg, key):
    value = msg.get(key)
    if not isinstance(value, str) or not _SAFE_ID.match(value):
        raise TelemetryValidationError(f"invalid_or_missing_field:{key}")
    return value


def _require_utc_timestamp(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise TelemetryValidationError("invalid_or_missing_field:timestamp")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        raise TelemetryValidationError("invalid_or_missing_field:timestamp") from None
    return value


def _require_signals(value):
    if not isinstance(value, dict):
        raise TelemetryValidationError("invalid_or_missing_field:signals")
    signals = {}
    for name, types in _REQUIRED_SIGNALS.items():
        v = value.get(name)
        # bool is a subclass of int; reject it for numeric signals.
        if not isinstance(v, types) or (bool not in types and isinstance(v, bool)):
            raise TelemetryValidationError(f"invalid_or_missing_signal:{name}")
        signals[name] = v
    if signals["vehicle_speed_kph"] < 0 or signals["ttc_s"] < 0:
        raise TelemetryValidationError("signal_out_of_range")
    return signals


def telemetry_to_evidence(msg):
    """Validate one synthetic telemetry message and return an evidence record.

    Raises TelemetryValidationError for malformed or non-synthetic input.
    """
    if not isinstance(msg, dict):
        raise TelemetryValidationError("message_not_object")
    if msg.get("schema_version") != SCHEMA_VERSION:
        raise TelemetryValidationError("unsupported_schema_version")
    # Claim boundary: this path only ever accepts explicitly synthetic data.
    if msg.get("synthetic") is not True:
        raise TelemetryValidationError("non_synthetic_telemetry_rejected")

    message_id = _require_safe_id(msg, "message_id")
    device_id = _require_safe_id(msg, "device_id")
    scenario_id = _require_safe_id(msg, "scenario_id")
    requirement_id = _require_safe_id(msg, "requirement_id")
    timestamp = _require_utc_timestamp(msg.get("timestamp"))
    signals = _require_signals(msg.get("signals"))

    return {
        "record_type": "cloud_telemetry_evidence",
        "schema_version": SCHEMA_VERSION,
        "synthetic": True,
        "message_id": message_id,
        "device_id": device_id,
        "scenario_id": scenario_id,
        # RQ-09 evidence-contract fields:
        "timestamp": timestamp,
        "requirement_id": requirement_id,
        "input_state": signals,
        "trigger_reason": "synthetic telemetry received via MQTT",
        # Evidence capture only; judgment stays offline and human-controlled.
        "evidence_status": "RECORDED",
        "safety_decision_made": False,
        "final_approval_performed": False,
        "human_final_approval_required": True,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def evidence_object_key(record, prefix="cloud-evidence/telemetry"):
    """Deterministic S3 key, so a retried delivery overwrites instead of duplicating."""
    return f"{prefix}/{record['device_id']}/{record['message_id']}.json"
